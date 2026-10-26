#!/usr/bin/env python3
"""Run the isolated PyPTC admission check against a pinned ISIS RCS input."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STEP_DIR = Path(__file__).resolve().parent
PYPTC_DIR = STEP_DIR.parents[1]
REPO_ROOT = PYPTC_DIR.parent
DEFAULT_REFERENCE_REPO = Path("/home/hr/Repositories/isis_2024")
REFERENCE_COMMIT = "1bada6a2ab94edd426c52b7e97a5d335926e0646"
REFERENCE_PREFIX = "Lattice_Files/00_Simplified_Lattice"
REFERENCE_FILES = (
    "ISIS.injected_beam",
    "ISIS.elements",
    "ISIS.strength",
    "2023.strength",
    "ISIS.sequence",
)
DEFAULT_MADX = PYPTC_DIR / "workflows" / "madx" / "bin" / "madx-linux64_v5_02_00"
PTC_SCRIPTS_DIR = PYPTC_DIR / "workflows" / "madx" / "ptc_scripts"
TARGET_SOURCE_FILES = (
    PYPTC_DIR / "pyptc" / "core.py",
    PYPTC_DIR / "build" / "build_ptc.sh",
    PYPTC_DIR / "fortran" / "pyptc_api.f90",
)
AUTHORIZED_RECIPE = {
    "authorization_source": "user-approved admission recipe in the 2026-10-26 session",
    "reference_mode": "clean-checkout",
    "lattice_variant": "00_Simplified_Lattice with 2023.strength overlay",
    "selected_sequence": "synchrotron",
    "include_order": [
        "ISIS.injected_beam",
        "ISIS.elements",
        "ISIS.strength",
        "2023.strength",
        "ISIS.sequence",
    ],
    "machine_settings": {"a1": 0.0, "b1": 0.0, "kqtd": 0.0, "kqtf": 0.0},
    "permitted_reference_calculation": "one MAD-X TWISS calculation for synchrotron structural/reference-particle evidence",
}
PROTON_MASS_GEV = 0.9382720813
EXPECTED_PC_GEV = 0.37033168
P0_ABS_TOLERANCE_GEV_C = 2.0e-7
KINETIC_ABS_TOLERANCE_GEV = 2.0e-6
MASS_ABS_TOLERANCE_GEV = 2.0e-6
ZERO_ABS_TOLERANCE = 1.0e-12


class AdmissionBlocked(RuntimeError):
    """A precondition prevented an admission run."""


class AdmissionFailed(RuntimeError):
    """A requested reference or PyPTC operation failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_text(repository: Path, *arguments: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        raise AdmissionBlocked(f"Could not inspect reference repository {repository}: {detail.strip()}") from exc
    return completed.stdout.strip()


def materialize_reference_inputs(reference_repo: Path, destination: Path) -> dict[str, dict[str, str]]:
    """Copy the exact tracked input closure from the pinned Git tree."""

    if not reference_repo.is_dir():
        raise AdmissionBlocked(
            f"ISIS reference repository not found: {reference_repo}. "
            "Set ISIS_REFERENCE_REPO or pass --reference-repo to the pinned checkout."
        )
    resolved_commit = git_text(reference_repo, "rev-parse", f"{REFERENCE_COMMIT}^{{commit}}")
    if resolved_commit != REFERENCE_COMMIT:
        raise AdmissionBlocked(f"Pinned ISIS revision resolved unexpectedly: {resolved_commit}")

    input_dir = destination / "reference_inputs"
    input_dir.mkdir(parents=True, exist_ok=False)
    manifest: dict[str, dict[str, str]] = {}
    for filename in REFERENCE_FILES:
        logical_name = f"{REFERENCE_PREFIX}/{filename}"
        try:
            raw = subprocess.run(
                ["git", "-C", str(reference_repo), "show", f"{REFERENCE_COMMIT}:{logical_name}"],
                check=True,
                capture_output=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            raise AdmissionBlocked(f"Pinned input is unavailable: {logical_name}") from exc
        output_path = input_dir / filename
        output_path.write_bytes(raw)
        manifest[logical_name] = {
            "materialized_path": str(output_path.relative_to(destination)),
            "sha256": sha256_bytes(raw),
        }
    return manifest


def parse_numeric_assignment(text: str, name: str) -> float | None:
    match = re.search(
        rf"(?im)^\s*{re.escape(name)}\s*(?::=|=)\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][-+]?\d+)?)\s*;",
        text,
    )
    if not match:
        return None
    return float(match.group(1).replace("D", "E").replace("d", "e"))


def validate_strength_inputs(input_dir: Path) -> dict[str, Any]:
    base_text = (input_dir / "ISIS.strength").read_text(encoding="utf-8")
    overlay_text = (input_dir / "2023.strength").read_text(encoding="utf-8")
    trim_values = {
        name: parse_numeric_assignment(base_text, name)
        for name in ("kqtd", "kqtf")
    }
    if any(value is None or abs(value) > ZERO_ABS_TOLERANCE for value in trim_values.values()):
        raise AdmissionBlocked(f"Pinned base strength input does not set both trim quads to zero: {trim_values}")

    overlay_trim_values = {
        name: parse_numeric_assignment(overlay_text, name)
        for name in ("kqtd", "kqtf")
    }
    if any(value is not None and abs(value) > ZERO_ABS_TOLERANCE for value in overlay_trim_values.values()):
        raise AdmissionBlocked(f"2023 strength overlay changes a trim quadrupole: {overlay_trim_values}")

    harmonic_names = (
        "D7SIN", "D7COS", "D8SIN", "D8COS", "F8SIN", "F8COS", "F9SIN", "F9COS",
    )
    harmonic_values = {name: parse_numeric_assignment(base_text, name) for name in harmonic_names}
    if any(value is None or abs(value) > ZERO_ABS_TOLERANCE for value in harmonic_values.values()):
        raise AdmissionBlocked(f"Pinned base strength input has missing or nonzero harmonic amplitudes: {harmonic_values}")
    return {
        "base_trim_strengths": trim_values,
        "overlay_trim_assignments": overlay_trim_values,
        "base_harmonic_amplitudes": harmonic_values,
        "recipe_harmonic_amplitudes": {"a1": 0.0, "b1": 0.0},
    }


def madx_script() -> str:
    """Return the exact authorized minimal reference and conversion recipe."""

    return '''TITLE, "PyPTC ISIS RCS admission";
CALL, FILE = "../reference_inputs/ISIS.injected_beam";
CALL, FILE = "../reference_inputs/ISIS.elements";
CALL, FILE = "../reference_inputs/ISIS.strength";
CALL, FILE = "../reference_inputs/2023.strength";
CALL, FILE = "../reference_inputs/ISIS.sequence";

a1 := 0.0;
b1 := 0.0;
kqtd := 0.0;
kqtf := 0.0;
USE, SEQUENCE=synchrotron;
VALUE, a1;
VALUE, b1;
VALUE, kqtd;
VALUE, kqtf;
VALUE, kqtd_0;
VALUE, kqtd_1;
VALUE, kqtd_2;
VALUE, kqtd_3;
VALUE, kqtd_4;
VALUE, kqtd_5;
VALUE, kqtd_6;
VALUE, kqtd_7;
VALUE, kqtd_8;
VALUE, kqtd_9;
VALUE, kqtf_0;
VALUE, kqtf_1;
VALUE, kqtf_2;
VALUE, kqtf_3;
VALUE, kqtf_4;
VALUE, kqtf_5;
VALUE, kqtf_6;
VALUE, kqtf_7;
VALUE, kqtf_8;
VALUE, kqtf_9;
SELECT, FLAG=TWISS, CLEAR;
SELECT, FLAG=TWISS, COLUMN=name, s, x, px, y, py, betx, bety, alfx, alfy;
TWISS, SAVE, FILE="reference_twiss.tfs";

propagation_method = 2;
order_of_integrator = 6;
integration_steps_per_element = 5;
map_order = 5;
ptc_create_universe;
ptc_create_layout,time=true, model=propagation_method, exact=true, method=order_of_integrator, nst=integration_steps_per_element;
ptc_script, file="PTC_Scripts/resplit.ptc";
ptc_script, file="PTC_Scripts/print_flat_file.ptc";
ptc_end;
'''


def parse_madx_value_log(log_text: str, name: str) -> float | None:
    matches = re.findall(
        rf"(?im)^\s*{re.escape(name)}\s*=\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][-+]?\d+)?)\s*;\s*$",
        log_text,
    )
    if not matches:
        return None
    return float(matches[-1].replace("D", "E").replace("d", "e"))


def validate_effective_madx_strengths(log_text: str) -> dict[str, float]:
    names = ["a1", "b1", "kqtd", "kqtf"]
    names += [f"kqtd_{index}" for index in range(10)]
    names += [f"kqtf_{index}" for index in range(10)]
    values = {name: parse_madx_value_log(log_text, name) for name in names}
    missing = [name for name, value in values.items() if value is None]
    nonzero = {name: value for name, value in values.items() if value is not None and abs(value) > ZERO_ABS_TOLERANCE}
    if missing or nonzero:
        raise AdmissionFailed(f"Effective harmonic/trim settings are not proven zero; missing={missing}, nonzero={nonzero}")
    return {name: float(value) for name, value in values.items() if value is not None}


def parse_tfs_headers(path: Path) -> dict[str, float | str]:
    headers: dict[str, float | str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("@"):
            continue
        parts = line.split(maxsplit=3)
        if len(parts) != 4:
            continue
        key, raw = parts[1].lower(), parts[3].strip().strip('"')
        try:
            headers[key] = float(raw.replace("D", "E").replace("d", "e"))
        except ValueError:
            headers[key] = raw
    return headers


def next_attempt_id(output_root: Path) -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = f"attempt-{now}"
    if not (output_root / base).exists():
        return base
    index = 2
    while (output_root / f"{base}-{index:02d}").exists():
        index += 1
    return f"{base}-{index:02d}"


def source_revision() -> str:
    return git_text(REPO_ROOT, "rev-parse", "HEAD")


def target_file_hashes() -> dict[str, str]:
    return {str(path.relative_to(REPO_ROOT)): sha256_file(path) for path in TARGET_SOURCE_FILES if path.is_file()}


def run_madx(madx: Path, work_dir: Path, script: str) -> tuple[subprocess.CompletedProcess[str], Path]:
    if not madx.is_file() or not os.access(madx, os.X_OK):
        raise AdmissionBlocked(f"MAD-X executable is unavailable or not executable: {madx}")
    for name in ("resplit.ptc", "print_flat_file.ptc"):
        source = PTC_SCRIPTS_DIR / name
        if not source.is_file():
            raise AdmissionBlocked(f"Required PyPTC flat-file support script is missing: {source}")
        shutil.copy2(source, work_dir / "PTC_Scripts" / name)
    script_path = work_dir / "admission_recipe.madx"
    script_path.write_text(script, encoding="utf-8")
    try:
        with script_path.open("r", encoding="utf-8") as input_stream:
            completed = subprocess.run(
                [str(madx)],
                cwd=work_dir,
                stdin=input_stream,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=180,
                check=False,
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdmissionFailed(f"MAD-X could not complete the authorized recipe: {exc}") from exc
    log_path = work_dir / "madx.log"
    log_path.write_text(completed.stdout, encoding="utf-8")
    flat_file = work_dir / "PTC-PyORBIT_flat_file.flt"
    twiss_file = work_dir / "reference_twiss.tfs"
    if completed.returncode != 0 or not flat_file.is_file() or not twiss_file.is_file():
        raise AdmissionFailed(
            f"MAD-X recipe failed or omitted an expected output (return code {completed.returncode}); see {log_path}"
        )
    return completed, log_path


def load_pyptc(library: Path):
    if not library.is_file():
        raise AdmissionBlocked(f"PyPTC shared library is missing: {library}. Run bash build/build_ptc.sh first.")
    sys.path.insert(0, str(PYPTC_DIR))
    try:
        from pyptc import PTC, read_flatfile_fibres
    except Exception as exc:
        raise AdmissionBlocked(f"Could not import the documented PyPTC Python API: {exc}") from exc
    return PTC(library), read_flatfile_fibres


def check_reference_particle(ptc, headers: dict[str, float | str]) -> dict[str, Any]:
    summary = ptc.machine_summary()
    p0c = ptc.scalar("ptc_get_p0c_")
    beta0 = ptc.scalar("ptc_get_beta0_")
    kinetic = ptc.scalar("ptc_get_kinetic_")
    gamma = 1.0 / math.sqrt(1.0 - beta0 * beta0) if 0.0 < beta0 < 1.0 else math.nan
    derived_mass = p0c / (beta0 * gamma) if gamma and math.isfinite(gamma) and beta0 > 0 else math.nan
    expected_kinetic = math.sqrt(EXPECTED_PC_GEV**2 + PROTON_MASS_GEV**2) - PROTON_MASS_GEV
    madx_pc = headers.get("pc")
    madx_mass = headers.get("mass")
    checks = {
        "unit_charge": summary["charge"] == 1,
        "pinned_momentum_within_flat_file_rounding": abs(p0c - EXPECTED_PC_GEV) <= P0_ABS_TOLERANCE_GEV_C,
        "kinetic_energy_consistent_with_proton": math.isclose(
            kinetic, expected_kinetic, rel_tol=0.0, abs_tol=KINETIC_ABS_TOLERANCE_GEV
        ),
        "derived_rest_mass_is_proton": math.isclose(
            derived_mass, PROTON_MASS_GEV, rel_tol=0.0, abs_tol=MASS_ABS_TOLERANCE_GEV
        ),
    }
    if isinstance(madx_mass, float):
        checks["madx_mass_header_is_proton"] = math.isclose(
            madx_mass, PROTON_MASS_GEV, rel_tol=0.0, abs_tol=MASS_ABS_TOLERANCE_GEV
        )
    if isinstance(madx_pc, float):
        checks["madx_momentum_header_matches_input"] = abs(madx_pc - EXPECTED_PC_GEV) <= P0_ABS_TOLERANCE_GEV_C
    result = {
        "species": "proton",
        "charge": summary["charge"],
        "reference_pc_gev_c": p0c,
        "input_pc_gev_c": EXPECTED_PC_GEV,
        "beta0": beta0,
        "gamma0": gamma,
        "derived_rest_mass_gev": derived_mass,
        "ptc_machine_summary_mass_raw": summary["mass_gev"],
        "kinetic_energy_gev": kinetic,
        "expected_proton_kinetic_energy_gev": expected_kinetic,
        "madx_twiss_mass_header_gev": madx_mass,
        "madx_twiss_pc_header_gev_c": madx_pc,
        "tolerances": {
            "flat_file_momentum_abs_gev_c": P0_ABS_TOLERANCE_GEV_C,
            "kinetic_energy_abs_gev": KINETIC_ABS_TOLERANCE_GEV,
            "derived_mass_abs_gev": MASS_ABS_TOLERANCE_GEV,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return result


def write_report(result: dict[str, Any], report_path: Path) -> None:
    provenance = result["provenance"]
    machine = result.get("machine", {})
    smoke = result.get("smoke_test", {})
    reference = provenance["reference"]
    target = provenance["target"]
    lines = [
        "# PyPTC ISIS RCS admission report",
        "",
        f"- Attempt: `{result['attempt_id']}`",
        f"- Technical outcome: **{result['outcome']}**",
        f"- Review disposition: **{result['review_disposition']}**",
        f"- Reference mode: `{reference['mode']}`",
        f"- ISIS source revision: `{reference['revision']}`",
        f"- Lattice variant and sequence: `{reference['lattice_variant']}` / `{reference['sequence']}`",
        f"- Recipe authorization: {reference['recipe']['authorization_source']}",
        f"- Executed include order: `{ ' → '.join(reference['recipe']['include_order']) }`",
        f"- PyPTC revision: `{target['revision']}`",
        f"- PyPTC library: `{target['library_path']}`",
        "",
        "## Checks",
        "",
        f"- Input harmonic and trim checks: `{result.get('strength_checks', {})}`",
        f"- Effective MAD-X harmonic and trim checks: `{result.get('effective_strengths', {})}`",
        f"- PyPTC machine structure: `{machine}`",
        f"- Reference particle: `{result.get('reference_particle', {})}`",
        f"- One-turn zero-offset smoke: `{smoke}`",
        "",
        "## Evidence files",
        "",
        f"- Canonical result: `{result['files']['result']}`",
        f"- Provenance manifest: `{result['files']['manifest']}`",
        f"- MAD-X log: `{result['files'].get('madx_log', 'unavailable')}`",
        f"- Reference TWISS table: `{result['files'].get('reference_twiss', 'unavailable')}`",
        f"- Generated PTC flat file: `{result['files'].get('flat_file', 'unavailable')}`",
        "",
        "## Nonclaims",
        "",
        "This admission check does not demonstrate target/reference orbit agreement, tunes, Twiss agreement, dispersion, chromaticity, long-term stability, collective-effects validity, or benchmark agreement. Technical success is pending separate human review.",
        "",
    ]
    if result.get("failure"):
        lines.extend(["## Blocker or failure", "", result["failure"], ""])
    report_path.write_text("\n".join(lines), encoding="utf-8")


def build_provenance(args, attempt_dir: Path) -> dict[str, Any]:
    reference_repo = args.reference_repo.resolve()
    target_revision = source_revision()
    target_files = target_file_hashes()
    madx_path = args.madx.resolve()
    library_path = args.library.resolve()
    return {
        "effective_command": [
            sys.executable,
            str(Path(__file__).resolve()),
            "--reference-repo", str(reference_repo),
            "--library", str(library_path),
            "--output-root", str(args.output_root.resolve()),
        ],
        "seed": "not_applicable: deterministic single-particle input",
        "reference": {
            "repository_url": "https://gitlab.stfc.ac.uk/isis_accelerator_models/isis_2024",
            "resolved_repository_path": str(reference_repo),
            "mode": "clean-checkout",
            "revision": REFERENCE_COMMIT,
            "lattice_variant": "00_Simplified_Lattice with 2023.strength overlay",
            "sequence": "synchrotron",
            "recipe": AUTHORIZED_RECIPE,
            "materialization": "tracked files read with git show from the pinned commit; working-tree files are ignored",
        },
        "target": {
            "repository_url": "https://github.com/HaroonRafique/PTC",
            "revision": target_revision,
            "pyptc_source_hashes": target_files,
            "api_reference_only": {
                "repository_url": "https://github.com/HaroonRafique/PTC",
                "revision": "021b3ed865ab04a5e10a1c7c3adbea9850133912",
                "use": "read-only API/build documentation reference; no separate checkout source is compiled, executed, or directly bound",
            },
            "library_path": str(library_path),
            "library_sha256": sha256_file(library_path) if library_path.is_file() else None,
            "build_command": ["bash", str(PYPTC_DIR / "build" / "build_ptc.sh")],
        },
        "admission_workflow": {
            "runner_path": str(Path(__file__).resolve()),
            "runner_sha256": sha256_file(Path(__file__).resolve()),
            "unit_test_path": str(STEP_DIR / "tests" / "test_admission_harness.py"),
            "unit_test_sha256": sha256_file(STEP_DIR / "tests" / "test_admission_harness.py"),
            "setup_script_path": str(STEP_DIR / "setup.sh"),
            "setup_script_sha256": sha256_file(STEP_DIR / "setup.sh"),
            "requirements_path": str(STEP_DIR / "requirements.txt"),
            "requirements_sha256": sha256_file(STEP_DIR / "requirements.txt"),
        },
        "runtime": {
            "python": sys.version,
            "numpy": importlib.metadata.version("numpy"),
            "matplotlib": importlib.metadata.version("matplotlib"),
            "madx_path": str(madx_path),
            "madx_sha256": sha256_file(madx_path) if madx_path.is_file() else None,
            "madx_version": "recorded from the retained MAD-X log",
            "pyptc_package_version": "source checkout; revision and source hashes recorded above",
        },
        "attempt_directory": str(attempt_dir.resolve()),
        "output_root": str(args.output_root.resolve()),
    }


def run_admission(args) -> tuple[dict[str, Any], Path, Path]:
    args.output_root.mkdir(parents=True, exist_ok=True)
    attempt_id = args.attempt_id or next_attempt_id(args.output_root)
    attempt_dir = args.output_root / attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=False)
    work_dir = attempt_dir / "madx_work"
    work_dir.mkdir()
    (work_dir / "PTC_Scripts").mkdir()
    report_path = attempt_dir / "report.md"
    result_path = attempt_dir / "result.json"
    manifest_path = attempt_dir / "manifest.json"
    files: dict[str, str] = {
        "report": str(report_path.resolve()),
        "result": str(result_path.resolve()),
        "manifest": str(manifest_path.resolve()),
    }
    provenance = build_provenance(args, attempt_dir)
    result: dict[str, Any] = {
        "schema_version": 1,
        "attempt_id": attempt_id,
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "outcome": "blocked",
        "review_disposition": "awaiting review",
        "failure": None,
        "provenance": provenance,
        "files": files,
        "strength_checks": {},
        "effective_strengths": {},
        "machine": {},
        "reference_particle": {},
        "smoke_test": {},
        "nonclaims": [
            "orbit agreement", "tune agreement", "Twiss agreement", "dispersion agreement",
            "chromaticity agreement", "long-term stability", "collective-effects validity", "benchmark agreement",
        ],
    }
    try:
        input_hashes = materialize_reference_inputs(args.reference_repo.resolve(), attempt_dir)
        result["provenance"]["reference"]["inputs"] = input_hashes
        input_dir = attempt_dir / "reference_inputs"
        result["strength_checks"] = validate_strength_inputs(input_dir)
        recipe = madx_script()
        recipe_path = work_dir / "admission_recipe.madx"
        recipe_path.write_text(recipe, encoding="utf-8")
        result["provenance"]["reference"]["recipe"]["script_sha256"] = sha256_file(recipe_path)
        result["provenance"]["reference"]["recipe"]["ptc_support_scripts"] = {
            name: {"source": str(PTC_SCRIPTS_DIR / name), "sha256": sha256_file(PTC_SCRIPTS_DIR / name)}
            for name in ("resplit.ptc", "print_flat_file.ptc")
        }
        madx_log = work_dir / "madx.log"
        flat_file = work_dir / "PTC-PyORBIT_flat_file.flt"
        twiss_file = work_dir / "reference_twiss.tfs"
        files.update({
            "madx_log": str(madx_log.resolve()),
            "madx_recipe": str((work_dir / "admission_recipe.madx").resolve()),
            "reference_twiss": str(twiss_file.resolve()),
            "flat_file": str(flat_file.resolve()),
            "madx_side_file": str((work_dir / "Maxwellian_bend_for_ptc.txt").resolve()),
        })
        madx_completed, madx_log = run_madx(args.madx.resolve(), work_dir, recipe)
        result["provenance"]["runtime"]["madx_version"] = next(
            (line.strip() for line in madx_completed.stdout.splitlines() if "MAD-X" in line or "MAD-X" in line.upper()),
            "version string unavailable in log; executable SHA-256 recorded",
        )
        result["effective_strengths"] = validate_effective_madx_strengths(madx_completed.stdout)
        (work_dir / "madx.log").write_text(madx_completed.stdout, encoding="utf-8")
        ptc, read_flatfile_fibres = load_pyptc(args.library.resolve())
        ptc.init_lattice(flat_file)
        summary = ptc.machine_summary()
        fibres = read_flatfile_fibres(flat_file)
        # The TFS header provides the reference circumference when available.
        twiss_headers = parse_tfs_headers(twiss_file)
        length_ref = twiss_headers.get("length")
        if not isinstance(length_ref, float):
            sequence_text = (input_dir / "ISIS.sequence").read_text(encoding="utf-8")
            sequence_match = re.search(r"(?is)synchrotron\s*:\s*sequence\s*,.*?\bl\s*=\s*([-+\d.eEdD]+)", sequence_text)
            if sequence_match:
                length_ref = float(sequence_match.group(1).replace("D", "E").replace("d", "e"))
        if summary["n_nodes"] <= 0 or summary["circumference_m"] <= 0 or not fibres:
            raise AdmissionFailed(f"PyPTC returned invalid structural lattice data: {summary}")
        if isinstance(length_ref, float) and not math.isclose(summary["circumference_m"], length_ref, rel_tol=0.0, abs_tol=1.0e-5):
            raise AdmissionFailed(
                f"PyPTC circumference differs from the pinned reference sequence: {summary['circumference_m']} vs {length_ref} m"
            )
        machine_summary = dict(summary)
        raw_mass = machine_summary.pop("mass_gev", None)
        result["machine"] = {
            **machine_summary,
            "machine_summary_mass_raw_amu": raw_mass,
            "flat_file_fibre_records": len(fibres),
            "reference_circumference_m": length_ref,
            "flat_file_sha256": sha256_file(flat_file),
        }
        result["reference_particle"] = check_reference_particle(ptc, twiss_headers)
        start = [0.0] * 6
        final, loss = ptc.track_particle_ptc_with_loss(start, turns=1)
        if final.shape != (6,) or not all(math.isfinite(float(value)) for value in final):
            raise AdmissionFailed(f"One-turn smoke particle returned invalid coordinates: {final.tolist()}")
        if loss["lost"]:
            raise AdmissionFailed(f"Zero-offset one-turn smoke particle was lost: {loss}")
        result["smoke_test"] = {
            "initial_coordinates": start,
            "coordinate_order": ["x_m", "px", "y_m", "py", "delta_p_over_p", "ct_m"],
            "turns": 1,
            "final_coordinates": [float(value) for value in final],
            "all_finite": True,
            "loss": loss,
            "loss_policy": "the zero-offset reference particle must complete one ring turn without reported loss",
        }
        result["outcome"] = "admitted"
    except AdmissionBlocked as exc:
        result["outcome"] = "blocked"
        result["failure"] = str(exc)
    except Exception as exc:
        result["outcome"] = "failed"
        result["failure"] = f"{type(exc).__name__}: {exc}"

    # Digest stable run artefacts before writing the report and final records.
    artifact_hashes = {}
    for key, value in files.items():
        path = Path(value)
        if key not in {"report", "result", "manifest"} and path.is_file():
            artifact_hashes[key] = sha256_file(path)
    result["files"]["sha256"] = artifact_hashes
    write_report(result, report_path)
    manifest = {
        "schema_version": 1,
        "attempt_id": attempt_id,
        "outcome": result["outcome"],
        "review_disposition": result["review_disposition"],
        "provenance": result["provenance"],
        "files": result["files"],
        "failure": result["failure"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result, report_path, result_path


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference-repo",
        type=Path,
        default=Path(os.environ.get("ISIS_REFERENCE_REPO", DEFAULT_REFERENCE_REPO)),
        help="local Git checkout containing the pinned isis_2024 revision",
    )
    parser.add_argument("--library", type=Path, default=PYPTC_DIR / "build_pyptc" / "libpyptc.so")
    parser.add_argument("--madx", type=Path, default=DEFAULT_MADX)
    parser.add_argument("--output-root", type=Path, default=PYPTC_DIR / "test_outputs" / "admit-code-to-isis-rcs")
    parser.add_argument("--attempt-id", help="explicit unused attempt directory name")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.attempt_id and (Path(args.attempt_id).name != args.attempt_id or args.attempt_id in {".", ".."}):
        print("--attempt-id must be a single directory name", file=sys.stderr)
        return 2
    try:
        result, report, canonical_result = run_admission(args)
    except FileExistsError as exc:
        print(f"Admission attempt directory already exists: {exc}", file=sys.stderr)
        return 2
    print(f"Technical outcome: {result['outcome']}")
    print(f"Report: {report}")
    print(f"Canonical result: {canonical_result}")
    print(f"Provenance manifest: {report.parent / 'manifest.json'}")
    return 0 if result["outcome"] == "admitted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
