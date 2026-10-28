#!/usr/bin/env python3
"""Run a provenance-recorded first PyPTC vs MAD-X optics diagnostic."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ITERATION_DIR = Path(__file__).resolve().parent
STEP_DIR = ITERATION_DIR.parent
if __name__ == "__main__":
    venv_root = STEP_DIR / ".venv"
    venv_python = venv_root / "bin" / "python"
    if venv_python.is_file() and Path(sys.prefix).resolve() != venv_root.resolve():
        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve())])

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent.parent / ".mplconfig"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = STEP_DIR.parents[1]
ADMISSION_BASIS = STEP_DIR / "admission_basis-accepted-attempt-20261027T082315Z"
ACCEPTED_ATTEMPT_ID = "attempt-20261027T082315Z"
OUTPUT_ROOT = REPO_ROOT / "test_outputs" / "benchmark-pyptc-linear-optics-against-madx"
SKILL_PATH = Path("/home/hr/Repositories/isis-modelling-agents/skills/machine-integration/benchmark-code-against-isis-rcs-optics/SKILL.md")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_tfs(path: Path) -> tuple[dict[str, str], list[str], list[dict[str, str]]]:
    headers: dict[str, str] = {}
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("@"):
            parts = stripped.split(maxsplit=3)
            if len(parts) == 4:
                headers[parts[1].upper()] = parts[3].strip().strip('"')
        elif stripped.startswith("*"):
            columns = stripped[1:].split()
        elif stripped.startswith('"') and columns:
            values = stripped.split()
            if len(values) == len(columns):
                rows.append(dict(zip(columns, (item.strip('"') for item in values))))
    if not rows:
        raise RuntimeError(f"No MAD-X TWISS rows parsed from {path}")
    return headers, columns, rows


def madx_recipe(input_dir: Path, tfs_path: Path) -> str:
    ordered = ("ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence")
    lines = ['TITLE, "PyPTC independent linear-optics benchmark";']
    for filename in ordered:
        lines.append(f'CALL, FILE="{(input_dir / filename).resolve()}";')
    lines += [
        "a1 := 0.0;",
        "b1 := 0.0;",
        "kqtd := 0.0;",
        "kqtf := 0.0;",
    ]
    lines += [
        "USE, SEQUENCE=synchrotron;",
        "VALUE, a1;",
        "VALUE, b1;",
        "VALUE, kqtd;",
        "VALUE, kqtf;",
    ]
    for family in ("kqtd", "kqtf"):
        lines.extend(f"VALUE, {family}_{index};" for index in range(10))
    lines += [
        "SELECT, FLAG=TWISS, CLEAR;",
        "SELECT, FLAG=TWISS, COLUMN=name, s, x, px, y, py, betx, bety, alfx, alfy, dx, dpx, dy, dpy, mux, muy;",
        f'TWISS, CHROM, SAVE, FILE="{tfs_path.resolve()}";',
    ]
    return "\n".join(lines) + "\n"


def run_madx(run_dir: Path) -> tuple[Path, dict[str, Any], dict[str, str], list[dict[str, str]]]:
    basis_inputs = ADMISSION_BASIS / "snapshot_inputs"
    madx_dir = run_dir / "madx"
    madx_dir.mkdir(parents=True, exist_ok=True)
    binary = REPO_ROOT / "workflows" / "madx" / "bin" / "madx-linux64_v5_02_00"
    accepted = json.loads((ADMISSION_BASIS / "result.json").read_text(encoding="utf-8"))
    expected_binary_hash = accepted["reference"]["madx_binary_sha256"]
    if not binary.is_file() or sha256(binary) != expected_binary_hash:
        raise RuntimeError("Pinned MAD-X 5.02.00 executable is missing or its digest differs from accepted admission")
    twiss_path = madx_dir / "reference_twiss.tfs"
    recipe_path = madx_dir / "benchmark_recipe.madx"
    log_path = madx_dir / "madx.log"
    recipe_path.write_text(madx_recipe(basis_inputs, twiss_path), encoding="utf-8")
    with recipe_path.open("r", encoding="utf-8") as recipe, log_path.open("w", encoding="utf-8") as log:
        completed = subprocess.run([str(binary)], cwd=madx_dir, stdin=recipe, stdout=log, stderr=subprocess.STDOUT, text=True)
    if completed.returncode != 0 or not twiss_path.is_file():
        raise RuntimeError(f"Pinned MAD-X calculation failed (return code {completed.returncode}); see {log_path}")
    headers, columns, rows = parse_tfs(twiss_path)
    effective: dict[str, float] = {}
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    for name in ("a1", "b1", "kqtd", "kqtf", *(f"kqtd_{i}" for i in range(10)), *(f"kqtf_{i}" for i in range(10))):
        matches = re.findall(rf"(?im)^\s*{re.escape(name)}\s*=\s*([-+0-9.eEdD]+)", log_text)
        if not matches:
            raise RuntimeError(f"MAD-X log did not report effective value for {name}")
        effective[name] = float(matches[-1].replace("D", "E").replace("d", "e"))
    if any(abs(value) > 1e-12 for value in effective.values()):
        raise RuntimeError(f"MAD-X effective harmonic/trim settings are not all zero: {effective}")
    gamma = float(headers["GAMMA"])
    beta0 = float(np.sqrt(1.0 - gamma ** -2))
    warning_lines = [line.strip() for line in log_text.splitlines() if re.search(r"\bwarning:", line, re.IGNORECASE)]
    summary = {
        "madx_version": headers.get("ORIGIN", "unknown"),
        "reference_mode": "fresh run using the exact MAD-X binary pinned by accepted admission",
        "recalculated_in_this_attempt": True,
        "sequence": headers.get("SEQUENCE", "unknown"),
        "binary_path": str(binary),
        "binary_sha256": sha256(binary),
        "reference_file": str(twiss_path.relative_to(run_dir)),
        "reference_sha256": sha256(twiss_path),
        "recipe_file": str(recipe_path.relative_to(run_dir)),
        "recipe_sha256": sha256(recipe_path),
        "log_file": str(log_path.relative_to(run_dir)),
        "log_sha256": sha256(log_path),
        "ordered_inputs": json.loads((ADMISSION_BASIS / "reference_evidence" / "source_manifest.json").read_text(encoding="utf-8"))["input_files"],
        "harmonic_settings": {"a1": 0.0, "b1": 0.0},
        "trim_settings": {"kqtd": 0.0, "kqtf": 0.0},
        "effective_madx_values": effective,
        "twiss_chrom_option": True,
        "twiss_nominal_deltap": 0.0,
        "chromaticity_native_definition": "dQ/dDELTAP for MAD-X 5.02.00",
        "chromaticity_method": "MAD-X TWISS, CHROM at nominal DELTAP=0 with internal +1e-6 step",
        "reference_gamma": gamma,
        "reference_beta0": beta0,
        "dispersion_normalization": "multiply MAD-X DX, DPX, DY, DPY by beta0 derived from this TWISS GAMMA header",
        "twiss_columns": columns,
        "twiss_rows": len(rows),
        "twiss_headers": headers,
        "warnings": {
            "implicit_element_redefinitions_ignored": sum("implicit element re-definition ignored" in line.lower() for line in warning_lines),
            "warning_lines": warning_lines,
        },
    }
    return twiss_path, summary, headers, rows


def run_pyptc(run_dir: Path, flat_file: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    sys.path.insert(0, str(REPO_ROOT))
    from pyptc.core import PTC

    library = REPO_ROOT / "build_pyptc" / "libpyptc.so"
    ptc = PTC(library)
    runtime_log = run_dir / "pyptc" / "pyptc_runtime.log"
    sys.stdout.flush()
    sys.stderr.flush()
    old_stdout, old_stderr = os.dup(1), os.dup(2)
    with runtime_log.open("w", encoding="utf-8") as native_log:
        try:
            os.dup2(native_log.fileno(), 1)
            os.dup2(native_log.fileno(), 2)
            ptc.init_lattice(flat_file)
            summary = ptc.machine_summary()
            tunes = ptc.tunes()
            chromaticities = ptc.chromaticities()
            rows = ptc.all_node_twiss_orbit()
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            os.dup2(old_stdout, 1)
            os.dup2(old_stderr, 2)
            os.close(old_stdout)
            os.close(old_stderr)
    s_exit = np.cumsum([float(row["length"]) for row in rows])
    cumulative_mux = np.cumsum([float(row["mux"]) for row in rows])
    cumulative_muy = np.cumsum([float(row["muy"]) for row in rows])
    for row, s, mux, muy in zip(rows, s_exit, cumulative_mux, cumulative_muy):
        row["s_exit_m"] = float(s)
        row["mux_cumulative"] = float(mux)
        row["muy_cumulative"] = float(muy)
        row["sampling_location"] = "node exit, verified in pinned source"
    result = {
        "library_path": str(library),
        "library_sha256": sha256(library),
        "api_level": ptc.api_level(),
        "machine_summary": summary,
        "tunes": tunes,
        "chromaticities_native": chromaticities,
        "profile_rows": len(rows),
        "profile_sampling": "one all_node_twiss_orbit row per exposed orbit node; pinned source confirms optics are queried after orbit-node tracking; s is cumulative node length",
        "phase_sampling": "node_phase_advances returns per-node increments; cumulative unwrapped sums compared with MAD-X MUX/MUY",
        "sampling_source_evidence": {
            "source_revision": "324c1a6e0389137c4f93658621089f9e01159827",
            "files": {
                "Sq_orbit_ptc.f90": {"sha256": "14258663c4813e37a50f8dca01ed25aa8b2fbdb964b182f42c70637dbe790f3a", "lines": "1310-1321, 1412-1435"},
                "ptcinterface.f90": {"sha256": "3e1da18115e7e8e31c6f52c69fbe8fc83e7ff432ff159e650a2bec7883042b0c", "lines": "157-169"},
            },
            "finding": "The API converts zero-based row indices to one-based orbit nodes. Twiss values are stored after ORBIT_TRACK_NODE; each orbit node length is the preceding interval.",
        },
        "flat_file": str(flat_file),
        "flat_file_sha256": sha256(flat_file),
        "circumference_from_sum_node_lengths_m": float(s_exit[-1]) if len(s_exit) else 0.0,
        "runtime_log": str(runtime_log.relative_to(run_dir)),
        "runtime_log_sha256": sha256(runtime_log),
        "warnings": {
            "no_nonzero_cavity_frequency_messages": sum("COULD NOT LOCALIZE NON 0.0_dp CAVITY FREQUENCY" in line for line in runtime_log.read_text(encoding="utf-8", errors="replace").splitlines()),
            "dlmax_exceeds_lmax_messages": sum("DLMAX > LMAX" in line for line in runtime_log.read_text(encoding="utf-8", errors="replace").splitlines()),
            "orbit_warning_11_present": "ORBIT_WARNING           11" in runtime_log.read_text(encoding="utf-8", errors="replace"),
        },
    }
    with (run_dir / "pyptc" / "profile_raw.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return result, rows


def scalar_comparisons(target: dict[str, Any], madx_headers: dict[str, str]) -> list[dict[str, Any]]:
    ref_qx = float(madx_headers["Q1"])
    ref_qy = float(madx_headers["Q2"])
    ref_circ = float(madx_headers["LENGTH"])
    tgt = target["tunes"]
    machine = target["machine_summary"]
    comparisons = []
    for name, reference, target_value, units, note in (
        ("fractional_tune_x", ref_qx % 1.0, float(tgt["qx"]), "tune units", "MAD-X fractional part compared with PyPTC fractional tune"),
        ("fractional_tune_y", ref_qy % 1.0, float(tgt["qy"]), "tune units", "MAD-X fractional part compared with PyPTC fractional tune"),
        ("circumference", ref_circ, float(machine["circumference_m"]), "m", "MAD-X LENGTH header compared with PyPTC machine summary"),
    ):
        comparisons.append({
            "observable": name,
            "reference": reference,
            "target": target_value,
            "signed_target_minus_reference": target_value - reference,
            "units": units,
            "classification": "pending-tolerance",
            "tolerance": None,
            "note": note,
        })
    for plane, madx_key, ptc_key in (("x", "DQ1", "chromx"), ("y", "DQ2", "chromy")):
        comparisons.append({
            "observable": f"chromaticity_{plane}",
            "reference_native": float(madx_headers[madx_key]),
            "target_native": float(target["chromaticities_native"][ptc_key]),
            "signed_native_difference": float(target["chromaticities_native"][ptc_key]) - float(madx_headers[madx_key]),
            "units": "native MAD-X/PyPTC convention unresolved",
            "classification": "blocked",
            "tolerance": None,
            "note": "Skill requires matched momentum derivative definition; native conventions/methods have not been reconciled in this iteration.",
        })
    return comparisons


def mapping_diagnostic(reference_rows: list[dict[str, str]], target_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    mad_s = np.array([float(row["S"]) for row in reference_rows], dtype=float)
    records: list[dict[str, Any]] = []
    tolerance_m = 1e-9
    exact_unique = 0
    for target in target_rows:
        s = float(target["s_exit_m"])
        residuals = np.abs(mad_s - s)
        candidates = np.flatnonzero(residuals <= tolerance_m)
        exact_unique += int(len(candidates) == 1)
        nearest = int(np.argmin(residuals))
        records.append({
            "pyptc_node_index": int(target["node_index"]),
            "pyptc_candidate_s_exit_m": s,
            "madx_nearest_row_index": nearest,
            "madx_nearest_name": reference_rows[nearest]["NAME"],
            "madx_nearest_s_m": float(mad_s[nearest]),
            "nearest_signed_position_residual_m": float(mad_s[nearest] - s),
            "madx_rows_within_exact_position_tolerance": int(len(candidates)),
            "mapping_classification": "blocked-unverified-element-identity-and-boundary-semantics",
        })
    mapping = {
        "status": "blocked",
        "reason": "Direct MAD-X samples do not cover every PyPTC node exit; installing markers inside thick elements causes MAD-X negative-drift failures. No split/interpolation rule is yet verified, and PyPTC records lack source element/occurrence identities.",
        "position_tolerance_m": tolerance_m,
        "pyptc_profile_rows": len(target_rows),
        "madx_twiss_rows": len(reference_rows),
        "unique_exact_position_matches": exact_unique,
        "fraction_of_target_rows_with_unique_exact_s_match": exact_unique / len(target_rows) if target_rows else 0.0,
        "maximum_nearest_position_residual_m": max(abs(float(row["nearest_signed_position_residual_m"])) for row in records) if records else None,
        "interpolation_used": False,
        "profile_differences_computed": False,
        "marker_insertion_experiment": {
            "attempt_id": "attempt-20261027T143138Z",
            "recipe": "test_outputs/benchmark-pyptc-linear-optics-against-madx/attempt-20261027T143138Z/madx/reference_twiss.madx",
            "recipe_sha256": "4bb768ecbaa2b8ff9c90814671aac6c58bb4e63ce69bc8fc89cf5ffaf5ebedce",
            "log": "test_outputs/benchmark-pyptc-linear-optics-against-madx/attempt-20261027T143138Z/madx/reference_twiss.log",
            "log_sha256": "bf3869f4dae80a9f109ce67f5d476eb696c6e38e8718e64f7f50865ec8cab7eb",
            "fatal": "negative drift between PYPTC_NODE_0007 and SP0_QD, length -0.2596 m",
            "interpretation": "Installing markers at PyPTC node positions inside a thick MAD-X quadrupole is not a valid mapping without an authorized, model-preserving split/interpolation method.",
        },
    }
    return records, mapping


def make_diagnostic_plot(run_dir: Path, reference_rows: list[dict[str, str]], mapping_rows: list[dict[str, Any]]) -> dict[str, Any]:
    ref_s = np.array([float(row["S"]) for row in reference_rows])
    beta_x = np.array([float(row["BETX"]) for row in reference_rows])
    beta_y = np.array([float(row["BETY"]) for row in reference_rows])
    target_s = np.array([float(row["pyptc_candidate_s_exit_m"]) for row in mapping_rows])
    offsets = np.array([float(row["nearest_signed_position_residual_m"]) for row in mapping_rows])
    fig, axes = plt.subplots(3, 1, figsize=(13, 9), constrained_layout=True)
    axes[0].plot(ref_s, beta_x, marker=".", linestyle="none", label="MAD-X native beta_x")
    axes[0].set_ylabel("beta_x [m]")
    axes[0].legend(loc="best")
    axes[1].plot(ref_s, beta_y, marker=".", linestyle="none", label="MAD-X native beta_y")
    axes[1].set_ylabel("beta_y [m]")
    axes[1].legend(loc="best")
    axes[2].plot(target_s, offsets, marker=".", linestyle="none", label="nearest MAD-X s minus target node exit s")
    axes[2].axhline(0.0, color="black", linewidth=0.7)
    axes[2].set_ylabel("nearest position residual [m]")
    axes[2].set_xlabel("PyPTC cumulative node-length coordinate [m]")
    axes[2].legend(loc="best")
    fig.suptitle("Iteration 0001 diagnostic — profile alignment blocked; no optics residuals shown")
    path = run_dir / "plots" / "mapping_diagnostic.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return {"case": "nominal", "artifact": str(path.relative_to(run_dir)), "sha256": sha256(path), "panel_groups": ["MAD-X native beta_x and beta_y", "nearest-s mapping diagnostic"], "not_a_comparison_plot": True, "sampled_point_count": len(mapping_rows), "raster": {"width_px": 1950, "height_px": 1350, "dpi": 150}, "mapping": "nearest-s diagnostics only; no samples aligned"}


def run() -> Path:
    if not ADMISSION_BASIS.is_dir():
        raise FileNotFoundError(f"Accepted admission basis is missing: {ADMISSION_BASIS}")
    result_path = ADMISSION_BASIS / "result.json"
    accepted_result = json.loads(result_path.read_text(encoding="utf-8"))
    if accepted_result.get("outcome") != "admitted-snapshot" or accepted_result.get("attempt_id") != ACCEPTED_ATTEMPT_ID:
        raise RuntimeError("The pinned admission basis is not the accepted snapshot result expected by this campaign")
    if accepted_result.get("recipe", {}).get("settings", {}).get("a1") != 0.0 or accepted_result.get("recipe", {}).get("settings", {}).get("b1") != 0.0:
        raise RuntimeError("Admission basis does not have the required zero harmonic settings")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    run_id = "attempt-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if (OUTPUT_ROOT / run_id).exists():
        suffix = 1
        while (OUTPUT_ROOT / f"{run_id}-{suffix:02d}").exists():
            suffix += 1
        run_id = f"{run_id}-{suffix:02d}"
    run_dir = OUTPUT_ROOT / run_id
    run_dir.mkdir()
    (run_dir / "pyptc").mkdir()
    run_class = os.environ.get("PYPTC_BENCHMARK_RUN_CLASS", "user-run")
    skill_hash = sha256(SKILL_PATH) if SKILL_PATH.is_file() else None
    git_revision = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    skill_repo = SKILL_PATH.parents[3]
    skill_revision = subprocess.run(["git", "-C", str(skill_repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    target_flat = ADMISSION_BASIS / "madx_work" / "PTC-PyORBIT_flat_file.flt"

    manifest: dict[str, Any] = {
        "attempt_id": run_id,
        "attempt_class": run_class,
        "workflow": "fresh PyPTC linear-optics benchmark attempt against MAD-X",
        "iteration": "0001",
        "skill_path": str(SKILL_PATH),
        "skill_sha256": skill_hash,
        "skill_repository_revision": skill_revision,
        "runner_sha256": sha256(Path(__file__).resolve()),
        "requirements_sha256": sha256(ITERATION_DIR / "requirements.txt"),
        "target_repository_revision": git_revision,
        "target_source_revision_from_admission": accepted_result["target"]["repository_commit"],
        "target_api_definition_sha256_from_admission": accepted_result["target"]["api_definition_sha256"],
        "accepted_admission_attempt": ACCEPTED_ATTEMPT_ID,
        "admission_scope": "user-accepted snapshot admission only; no optics or benchmark acceptance",
        "admission_basis_bundle_path": str(ADMISSION_BASIS.relative_to(REPO_ROOT)),
        "admission_basis_result_sha256": sha256(result_path),
        "admission_madx_binary_sha256": accepted_result["reference"]["madx_binary_sha256"],
        "admission_madx_version": accepted_result["reference"]["madx_version"],
        "admission_madx_twiss_sha256": accepted_result["reference"]["reference_output_sha256"],
        "target_flat_file_sha256": sha256(target_flat),
        "runtime": {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "matplotlib": matplotlib.__version__},
        "output_directory": str(run_dir),
        "effective_recipe_delta_from_admission": "machine state unchanged from accepted admission; measurement adds TWISS,CHROM and requests profile columns; no resplitting policy change",
    }
    try:
        target_info, target_rows = run_pyptc(run_dir, target_flat)
        twiss_path, madx_info, madx_headers, madx_rows = run_madx(run_dir)
        (run_dir / "madx" / "profile_raw.tfs").write_bytes(twiss_path.read_bytes())
        beta0 = float(madx_info["reference_beta0"])
        normalized_reference_rows = []
        for row in madx_rows:
            normalized = dict(row)
            for column in ("DX", "DPX", "DY", "DPY"):
                if column in normalized:
                    normalized[column] = float(normalized[column]) * beta0
            normalized_reference_rows.append(normalized)
        with (run_dir / "madx" / "profile_common_convention.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(normalized_reference_rows[0].keys()))
            writer.writeheader()
            writer.writerows(normalized_reference_rows)
        scalar_rows = scalar_comparisons(target_info, madx_headers)
        with (run_dir / "scalar_comparisons.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=sorted({key for row in scalar_rows for key in row}))
            writer.writeheader()
            writer.writerows(scalar_rows)
        mapping_rows, mapping = mapping_diagnostic(madx_rows, target_rows)
        with (run_dir / "mapping_diagnostic.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(mapping_rows[0].keys()))
            writer.writeheader()
            writer.writerows(mapping_rows)
        plot_info = make_diagnostic_plot(run_dir, madx_rows, mapping_rows)
        capabilities = [
            {"observable": name, "reference": ref, "target": tgt, "classification": classification, "reason": reason}
            for name, ref, tgt, classification, reason in (
                ("closed orbit", "MAD-X TWISS x/px/y/py", "PyPTC all-node orbit", "blocked", "profile boundary map is not verified"),
                ("fractional tunes", "MAD-X Q1/Q2 modulo integer", "PyPTC tunes()", "pending-tolerance", "scalar definitions are provisionally comparable; no reviewed tolerance"),
                ("beta x/y", "MAD-X BETX/BETY", "PyPTC all_node_twiss_orbit", "blocked", "profile boundary map is not verified"),
                ("alpha x/y", "MAD-X ALFX/ALFY", "PyPTC all_node_twiss_orbit", "blocked", "profile boundary map is not verified"),
                ("dispersion and derivatives", "MAD-X DX/DPX/DY/DPY", "PyPTC ETAX/ETAPX/ETAY/ETAPY", "blocked", "profile boundary map and dispersion normalization are not verified"),
                ("phase advance", "MAD-X MUX/MUY", "PyPTC node_phase_advances", "blocked", "phase origin, unwrapping and boundary map are not verified"),
                ("circumference", "MAD-X LENGTH header", "PyPTC machine_summary", "pending-tolerance", "scalar definitions provisionally comparable; no reviewed tolerance"),
                ("chromaticity", "MAD-X DQ1/DQ2 headers", "PyPTC chromaticities()", "blocked", "native coordinate and estimator conventions require reconciliation"),
                ("bounded single-particle tracking", "MAD-X tracking API", "PyPTC tracking API", "blocked", "not run because the required profile mapping and comparison prerequisites are unresolved"),
                ("corrector/error response", "MAD-X perturbation", "PyPTC public perturbation API", "unbenchmarked", "no named perturbation case was authorized in iteration 0001"),
            )
        ]
        write_json(run_dir / "capability_matrix.json", capabilities)
        manifest["madx"] = madx_info
        manifest["pyptc"] = target_info
        manifest["profile_mapping"] = mapping
        manifest["reference_profile_limitations"] = {
            "available_columns": madx_info["twiss_columns"],
            "missing_required_columns": [column for column in ("DX", "DPX", "DY", "DPY", "MUX", "MUY") if column not in madx_info["twiss_columns"]],
            "reason": "This attempt reruns the pinned MAD-X 5.02.00 binary and requests the required profile columns explicitly.",
        }
        manifest["warning_summary"] = {
            "madx": madx_info["warnings"],
            "pyptc": target_info["warnings"],
            "classification_basis": "Prior local admission feedback classified the 302 MAD-X implicit element re-definitions as ignored and identified the PyPTC no-RF and DLMAX/LMAX messages; raw logs are retained for reassessment.",
        }
        manifest["scalar_comparisons"] = scalar_rows
        manifest["plot_manifest"] = [plot_info]
        manifest["nonclaims"] = [
            "No optics-profile agreement claim: boundary/element map is blocked.",
            "No tolerance-based acceptance claim; no observable-specific tolerance was supplied.",
            "No chromaticity agreement claim; native definitions are unreconciled.",
            "No bounded tracking, perturbation, long-term stability, collective-effects, or nonlinear claim.",
            "The accepted admission record is snapshot-scoped and is not benchmark acceptance.",
        ]
        write_json(run_dir / "manifest.json", manifest)
        result = {
            "attempt_id": run_id,
            "attempt_class": run_class,
            "outcome": "blocked-profile-mapping",
            "technical_status": "diagnostic records completed; profile comparison blocked before interpretation",
            "report": "report.md",
            "manifest": "manifest.json",
            "scalar_comparisons": "scalar_comparisons.csv",
            "capability_matrix": "capability_matrix.json",
            "profile_mapping": "mapping_diagnostic.csv",
            "plot_manifest": manifest["plot_manifest"],
        }
        write_json(run_dir / "result.json", result)
        report = [
            f"# PyPTC linear-optics benchmark attempt {run_id}",
            "",
            f"**Outcome:** `{result['outcome']}`.",
            "",
            "## Scope and basis",
            "",
            f"This {run_class} run uses the user-accepted snapshot admission `{ACCEPTED_ATTEMPT_ID}`. Its scope is snapshot admission only; it does not establish optics agreement. The accepted bundle is copied under the benchmark step as immutable provenance. The five ordered reference inputs, 2023 strength overlay, `synchrotron` sequence, zero harmonic variables and zero trim-quadrupole settings are retained.",
            "",
            "## Run records",
            "",
            f"MAD-X {madx_info['madx_version']} was rerun with the exact binary pinned by accepted admission and produced {madx_info['twiss_rows']} TWISS rows. PyPTC API level {target_info['api_level']} produced {target_info['profile_rows']} node records, with node lengths summing to {target_info['circumference_from_sum_node_lengths_m']:.12f} m. PyPTC library SHA-256: `{target_info['library_sha256']}`.",
            "",
            f"The generated MAD-X TWISS columns are `{', '.join(madx_info['twiss_columns'])}`. The pinned local MAD-X binary SHA-256 is `{madx_info['binary_sha256']}`; the recipe enables `CHROM` and records `DELTAP=0`.",
            "",
            f"MAD-X `GAMMA={madx_info['reference_gamma']:.12g}` gives `beta0={beta0:.12g}`. The `profile_common_convention.csv` record multiplies `DX`, `DPX`, `DY`, and `DPY` by this beta as required for the ISIS RCS comparison. MAD-X chromaticity is recorded natively as `dQ/dDELTAP`; PyPTC's corresponding normal-form derivative coordinate remains unverified, so no chromaticity comparison is accepted.",
            "",
            f"The exact raw records and commands are retained in `madx/`, `pyptc/`, and `manifest.json`. MAD-X reported {madx_info['warnings']['implicit_element_redefinitions_ignored']} `implicit element re-definition ignored` warnings. PyPTC again reports the no-RF cavity-frequency message and `DLMAX > LMAX 0.5144 > 0.5 m` (`ORBIT_WARNING 11`); these are classified in `manifest.json` and the raw logs remain available. This benchmark does not alter the split policy.",
            "",
            "## Result and limitation",
            "",
            f"The profile map is **blocked**: {mapping['unique_exact_position_matches']} of {mapping['pyptc_profile_rows']} PyPTC node exits have a unique exact MAD-X `s` match at the diagnostic `1e-9 m` position threshold. The largest nearest-position residual is {mapping['maximum_nearest_position_residual_m']:.6g} m. {mapping['reason']} Nearest-s positions are retained only for diagnosis; no profile residuals or interpolation were computed.",
            "",
            "Tune and circumference differences are retained as `pending-tolerance`; no acceptance thresholds were supplied. Chromaticity remains blocked pending convention reconciliation. Tracking is blocked because profile mapping prerequisites are unresolved. Perturbation coverage is unbenchmarked because no named perturbation case was authorized.",
            "",
            "The single PNG is a mapping diagnostic, not the skill's completed optics comparison composite. This attempt is not technically complete and is not eligible for a publication completion record.",
            "",
            "## Files",
            "",
            "- `scalar_comparisons.csv` — scalar values and signed target-minus-reference differences.",
            "- `mapping_diagnostic.csv` — per-node nearest-s candidate evidence; not an alignment.",
            "- `capability_matrix.json` — current comparability classification.",
            "- `plots/mapping_diagnostic.png` — mapping-only diagnostic figure.",
            "- `manifest.json` and `result.json` — provenance and canonical outcome.",
        ]
        (run_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        print(f"{result['outcome']}: {run_dir}")
        return run_dir
    except Exception as exc:
        manifest["failure"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        write_json(run_dir / "manifest.json", manifest)
        write_json(run_dir / "result.json", {"attempt_id": run_id, "attempt_class": run_class, "outcome": "failed", "error": str(exc)})
        (run_dir / "report.md").write_text(f"# PyPTC linear-optics benchmark attempt {run_id}\n\n**Outcome:** failed before diagnostic completion.\n\n```text\n{traceback.format_exc()}\n```\n", encoding="utf-8")
        print(f"failed: {exc}\nReport: {run_dir / 'report.md'}", file=sys.stderr)
        raise


if __name__ == "__main__":
    run()
