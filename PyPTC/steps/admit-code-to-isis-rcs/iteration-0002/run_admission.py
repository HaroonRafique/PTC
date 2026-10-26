#!/usr/bin/env python3
"""Fresh admission harness generated from the current shared skill revision."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.metadata
import json
import math
import os
import re
import shutil
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ITERATION_DIR = Path(__file__).resolve().parent
STEP_DIR = ITERATION_DIR.parent
REPO_ROOT = STEP_DIR.parents[1]
SNAPSHOT_DIR = STEP_DIR / "reference_snapshot"
PINNED_SKILL_COMMIT = "85a897a47b55951552226221dcdbc3b83a8daf71"
PINNED_SKILL_SHA256 = "ca7457645d0fe9049e7b55c50fc3b035b4db771bdb5984c6ab662cbe3cfbf35f"
PINNED_REFERENCE_COMMIT = "1bada6a2ab94edd426c52b7e97a5d335926e0646"
REFERENCE_NAMES = ("ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence")
HARMONIC_NAMES = ("D7SIN", "D7COS", "D8SIN", "D8COS", "F8SIN", "F8COS", "F9SIN", "F9COS")
ZERO_TOL = 1e-12
PC_TOL_GEV_C = 2e-7
KE_TOL_GEV = 2e-6
LENGTH_TOL_M = 1e-6
AUTHORIZED_RECIPE = {
    "authorization_source": "user instructions on 2026-10-26; recipe recorded in step README and feedback 0001",
    "reference_mode": "working-copy-snapshot",
    "variant": "00_Simplified_Lattice with 2023.strength overlay",
    "sequence": "synchrotron",
    "include_order": list(REFERENCE_NAMES),
    "settings": {"a1": 0.0, "b1": 0.0, "kqtd": 0.0, "kqtf": 0.0},
    "reference_calculation": "one MAD-X TWISS calculation",
    "wrapper": "attempt-local admission_recipe.madx",
    "ptc_support_scripts": ["resplit.ptc", "print_flat_file.ptc"],
}


class AdmissionBlocked(RuntimeError):
    """A required identity or precondition was not established."""


class AdmissionFailed(RuntimeError):
    """A requested bootstrap, reference, or target operation failed."""


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def run(command: list[str], *, cwd: Path, timeout: int = 300,
        stdin_path: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        if stdin_path is None:
            return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, timeout=timeout, check=False)
        with stdin_path.open("r", encoding="utf-8") as recipe_input:
            return subprocess.run(command, cwd=cwd, stdin=recipe_input, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdmissionFailed(f"Command could not complete: {command}: {exc}") from exc


def parse_assignments(text: str) -> dict[str, float]:
    pattern = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*(?::=|=)\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][-+]?\d+)?)\s*;", re.M)
    return {m.group(1).lower(): float(m.group(2).replace("D", "E").replace("d", "e")) for m in pattern.finditer(text)}


def validate_snapshot(snapshot: Path) -> dict[str, Any]:
    manifest_path = snapshot / "source_manifest.json"
    if not snapshot.is_dir() or not manifest_path.is_file():
        raise AdmissionBlocked(f"Authorized local reference snapshot is missing at {snapshot}; materialize the documented five-file snapshot first.")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("reference_mode") != "working-copy-snapshot" or not manifest.get("snapshot_authorization"):
        raise AdmissionBlocked("The files-only reference snapshot lacks explicit snapshot authorization.")
    if manifest.get("reference_source", {}).get("materialized_revision") != PINNED_REFERENCE_COMMIT:
        raise AdmissionBlocked("Reference snapshot does not match the approved source revision.")
    if manifest.get("files_copied") != len(REFERENCE_NAMES) or manifest.get("nested_git_metadata_copied") is not False:
        raise AdmissionBlocked("Reference snapshot boundary is not the approved files-only closure.")
    status_file = snapshot / manifest["reference_source"]["checkout_status_evidence"]
    if not status_file.is_file():
        raise AdmissionBlocked("Reference snapshot is missing its source checkout status evidence.")
    if sha_file(status_file) != manifest["reference_source"]["checkout_status_sha256"]:
        raise AdmissionBlocked("Source checkout status evidence hash does not match its manifest.")
    files = {}
    for name in REFERENCE_NAMES:
        logical = f"Lattice_Files/00_Simplified_Lattice/{name}"
        item = manifest.get("input_files", {}).get(logical)
        if not item or item.get("local_path") != name:
            raise AdmissionBlocked(f"Required reference input is missing from the snapshot manifest: {logical}")
        path = snapshot / name
        if not path.is_file():
            raise AdmissionBlocked(f"Required reference input is missing from the local snapshot: {logical}")
        if sha_file(path) != item["sha256"]:
            raise AdmissionBlocked(f"Reference input does not match its recorded hash: {logical}")
        files[name] = path
    return {"manifest": manifest, "status_file": status_file, "files": files}


def validate_recipe(recipe: dict[str, Any]) -> None:
    if recipe != AUTHORIZED_RECIPE:
        raise AdmissionBlocked("Proposed reference recipe differs from the explicitly authorized recipe.")


def clean_checkout_gate(status_text: str, revision: str, expected_revision: str) -> None:
    entries = [line for line in status_text.splitlines() if line and not line.startswith("#")]
    if revision != expected_revision or entries:
        raise AdmissionBlocked(f"Clean-checkout reference gate failed: revision={revision}; dirty_entries={len(entries)}")


def normalized_tfs_fingerprint(path: Path) -> str:
    stable_text = "\n".join(
        line for line in path.read_text(errors="replace").splitlines()
        if not re.match(r"^@\s+(TIME|DATE)\b", line)
    ) + "\n"
    return sha_bytes(stable_text.encode())


@contextmanager
def capture_native_stdout(path: Path):
    """Capture Python and native-library writes to file descriptor 1."""
    sys.stdout.flush()
    libc = ctypes.CDLL(None)
    libc.fflush(None)
    saved_stdout = os.dup(1)
    with path.open("wb") as capture:
        os.dup2(capture.fileno(), 1)
        try:
            yield
        finally:
            sys.stdout.flush()
            libc.fflush(None)
            os.dup2(saved_stdout, 1)
            os.close(saved_stdout)


def classify_runtime_warnings(madx_log: str, pyptc_log: str) -> dict[str, Any]:
    madx_lines = [line.strip() for line in madx_log.splitlines()
                  if re.match(r"^\s*\+*\s*(?:WARN(?:ING)?|ERROR)\s*:", line, re.I)]
    categories: dict[str, int] = {}
    for line in madx_lines:
        match = re.search(r"warning:\s*([^:]+)", line, re.I)
        label = match.group(1).strip() if match else line.strip()
        categories[label] = categories.get(label, 0) + 1
    target_lines = [line.strip() for line in pyptc_log.splitlines()
                    if re.search(r"ORBIT_WARNING|DLMAX\s*>\s*LMAX|COULD NOT LOCALIZE|\bWARN(?:ING)?\b|\bERROR\b", line, re.I)]
    return {
        "madx": {"line_count": len(madx_lines), "categories": categories,
                 "examples": list(dict.fromkeys(madx_lines))[:8]},
        "pyptc": {"line_count": len(target_lines), "relevant": list(dict.fromkeys(target_lines))},
    }


def validate_strengths(files: dict[str, Path]) -> dict[str, Any]:
    base = parse_assignments(files["ISIS.strength"].read_text(errors="replace"))
    overlay = parse_assignments(files["2023.strength"].read_text(errors="replace"))
    for name in ("kqtd", "kqtf", *HARMONIC_NAMES):
        value = base.get(name.lower())
        if value is None or abs(value) > ZERO_TOL:
            raise AdmissionBlocked(f"Pinned base input must explicitly set {name}=0; got {value!r}.")
    for name in ("kqtd", "kqtf", *HARMONIC_NAMES, "a1", "b1"):
        value = overlay.get(name.lower())
        if value is not None and abs(value) > ZERO_TOL:
            raise AdmissionBlocked(f"Approved overlay contains an unauthorized nonzero {name} assignment.")
    return {"base_zero_assignments": {n: base[n.lower()] for n in ("kqtd", "kqtf", *HARMONIC_NAMES)},
            "overlay_relevant_assignments": {n: v for n, v in overlay.items() if n.lower() in {x.lower() for x in (*HARMONIC_NAMES, "kqtd", "kqtf", "a1", "b1")}}}


def madx_recipe() -> str:
    calls = "\n".join(f'CALL, FILE="../snapshot_inputs/{name}";' for name in REFERENCE_NAMES)
    return f'''TITLE, "PyPTC admission snapshot";
{calls}
a1 := 0.0;
b1 := 0.0;
kqtd := 0.0;
kqtf := 0.0;
USE, SEQUENCE=synchrotron;
VALUE, a1;
VALUE, b1;
VALUE, kqtd;
VALUE, kqtf;
''' + "\n".join(f"VALUE, {family}_{i};" for family in ("kqtd", "kqtf") for i in range(10)) + '''
SELECT, FLAG=TWISS, CLEAR;
SELECT, FLAG=TWISS, COLUMN=name, s, x, px, y, py, betx, bety, alfx, alfy;
TWISS, SAVE, FILE="reference_twiss.tfs";
propagation_method = 2;
order_of_integrator = 6;
integration_steps_per_element = 5;
ptc_create_universe;
ptc_create_layout,time=true, model=propagation_method, exact=true, method=order_of_integrator, nst=integration_steps_per_element;
ptc_script, file="PTC_Scripts/resplit.ptc";
ptc_script, file="PTC_Scripts/print_flat_file.ptc";
ptc_end;
'''


def parse_value(log: str, name: str) -> float | None:
    hits = re.findall(rf"(?im)^\s*{re.escape(name)}\s*=\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][-+]?\d+)?)\s*;\s*$", log)
    return float(hits[-1].replace("D", "E").replace("d", "e")) if hits else None


def parse_tfs_headers(path: Path) -> dict[str, float | str]:
    result: dict[str, float | str] = {}
    for line in path.read_text(errors="replace").splitlines():
        if not line.startswith("@"):
            continue
        parts = line.split(maxsplit=3)
        if len(parts) != 4:
            continue
        raw = parts[3].strip().strip('"')
        try:
            result[parts[1].upper()] = float(raw.replace("D", "E").replace("d", "e"))
        except ValueError:
            result[parts[1].upper()] = raw
    return result


def next_attempt(root: Path) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = f"attempt-{stamp}"
    index = 2
    while (root / candidate).exists():
        candidate = f"attempt-{stamp}-{index:02d}"
        index += 1
    return candidate


def record_api(trace_path: Path, name: str, function, *args):
    value = function(*args)
    with trace_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"call": name, "arguments": [str(x) for x in args], "return": value}, default=str) + "\n")
    return value


def record_stage(event_path: Path, stage: str, state: str, **detail: Any) -> None:
    with event_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"utc": datetime.now(timezone.utc).isoformat(),
                                 "stage": stage, "state": state, **detail}, sort_keys=True) + "\n")


def run_target_api(library: Path, flat_file: Path, runtime_log: Path, trace_path: Path) -> dict[str, Any]:
    sys.path.insert(0, str(REPO_ROOT))
    from pyptc import PTC, read_flatfile_fibres

    calls = []
    with capture_native_stdout(runtime_log):
        ptc = PTC(library)
        record_api(trace_path, "PTC.init_lattice", ptc.init_lattice, flat_file)
        calls.append(f"PTC.init_lattice({flat_file.relative_to(runtime_log.parent)})")
        structure = record_api(trace_path, "PTC.machine_summary", ptc.machine_summary)
        calls.append("PTC.machine_summary()")
        fibres = read_flatfile_fibres(flat_file)
        record_api(trace_path, "pyptc.read_flatfile_fibres", lambda: {"count": len(fibres), "first": fibres[0].name if fibres else None})
        calls.append("pyptc.read_flatfile_fibres(flat_file)")
        symbols = {"p0c_gev_c": "ptc_get_p0c_", "beta0": "ptc_get_beta0_", "kinetic_gev": "ptc_get_kinetic_"}
        scalars = {key: record_api(trace_path, f"PTC.scalar({symbol})", ptc.scalar, symbol)
                   for key, symbol in symbols.items()}
        calls.extend(f"PTC.scalar({symbol})" for symbol in symbols.values())
        initial = [0.0] * 6
        final, loss = record_api(trace_path, "PTC.track_particle_ptc_with_loss", ptc.track_particle_ptc_with_loss, initial, 1)
        calls.append("PTC.track_particle_ptc_with_loss([0,0,0,0,0,0], turns=1)")
    return {"calls": calls, "structure": structure, "fibres": fibres,
            "scalars": scalars, "initial_coordinates": initial,
            "final_coordinates": [float(value) for value in final], "loss": loss}


def write_incomplete_bundle(args: argparse.Namespace, error: Exception) -> None:
    out = args.output_root.resolve() / str(args.attempt_id)
    if not out.is_dir() or (out / "result.json").exists():
        return
    events_path = out / "events.jsonl"
    events = [json.loads(line) for line in events_path.read_text().splitlines()] if events_path.exists() else []
    started = {item["stage"] for item in events if item["state"] == "started"}
    reference_called = "madx-reference" in started
    target_called = bool(started & {"pyptc-bootstrap", "pyptc-admission"})
    outcome = "blocked" if isinstance(error, AdmissionBlocked) else "failed"
    reason = str(error)
    snapshot_manifest = out / "reference_evidence/source_manifest.json"
    source = json.loads(snapshot_manifest.read_text()) if snapshot_manifest.exists() else {}
    reference_source = source.get("reference_source", {})
    build_log = out / "bootstrap/build.log"
    bootstrap_log = out / "bootstrap/bootstrap.log"
    library = args.library.resolve()
    result = {
        "attempt_id": args.attempt_id, "outcome": outcome, "review_disposition": "awaiting review",
        "attempt_class": "agent-run diagnostic; not a user-run skill-test result",
        "effective_command": " ".join([sys.executable, *sys.argv]),
        "seed": None, "ledger": "steps/admit-code-to-isis-rcs/review_ledger.csv",
        "report": "report.md", "canonical_result": "result.json", "manifest": "manifest.json",
        "snapshot_scope": "Any evidence in this bundle is limited to the authorized pinned input snapshot; it is not a clean-checkout result or a reviewed acceptance.",
        "reason_incomplete": reason,
        "reference_engine_invoked": reference_called, "target_engine_invoked": target_called,
        "reference": {"mode": "working-copy-snapshot", "snapshot_manifest": "reference_evidence/source_manifest.json",
                      "status_evidence": "reference_evidence/source_checkout_status.porcelain-v2.txt",
                      "status_sha256": reference_source.get("checkout_status_sha256"),
                      "source_revision": reference_source.get("materialized_revision"),
                      "observed_checkout_revision": reference_source.get("checkout_revision_at_copy"),
                      "dirty_entry_count": reference_source.get("checkout_status_entry_count"),
                      "variant": AUTHORIZED_RECIPE["variant"], "sequence": AUTHORIZED_RECIPE["sequence"],
                      "include_order": AUTHORIZED_RECIPE["include_order"],
                      "reference_calculation": AUTHORIZED_RECIPE["reference_calculation"]},
        "target": {"build_log": str(build_log.relative_to(out)) if build_log.is_file() else None,
                   "build_log_sha256": sha_file(build_log) if build_log.is_file() else None,
                   "bootstrap_log": str(bootstrap_log.relative_to(out)) if bootstrap_log.is_file() else None,
                   "bootstrap_log_sha256": sha_file(bootstrap_log) if bootstrap_log.is_file() else None,
                   "library": str(library), "library_sha256": sha_file(library) if library.is_file() else None},
        "nonclaims": ["No admission acceptance, optics, or benchmark claim is made."],
    }
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (out / "manifest.json").write_text(json.dumps({**result, "events": "events.jsonl"}, indent=2, sort_keys=True) + "\n")
    (out / "report.md").write_text(
        f"# PyPTC ISIS RCS admission {args.attempt_id}\n\n"
        f"- Outcome: **{outcome}**; review disposition: **awaiting review**.\n"
        f"- Reference mode: `working-copy-snapshot`; source revision: `{result['reference']['source_revision']}`.\n"
        f"- Scope: {result['snapshot_scope']}\n"
        f"- Pre-run dirty-state evidence: `{result['reference']['status_evidence']}` (SHA-256 `{result['reference']['status_sha256']}`; {result['reference']['dirty_entry_count']} entries).\n"
        f"- Approved recipe (not executed): `{result['reference']['variant']}`, sequence `{result['reference']['sequence']}`, include order `{result['reference']['include_order']}`; permitted calculation: {result['reference']['reference_calculation']}.\n"
        f"- Bootstrap log: `{result['target']['bootstrap_log']}` (SHA-256 `{result['target']['bootstrap_log_sha256']}`).\n"
        f"- Reference engine invoked: `{reference_called}`; PyPTC invoked: `{target_called}`.\n"
        f"- Ledger: `{result['ledger']}`.\n\n## Incomplete evidence\n\n{reason}\n\n"
        "No admission acceptance, optics, or benchmark claim is made.\n", encoding="utf-8")


def render_report(result: dict[str, Any]) -> str:
    ref = result["reference"]
    target = result["target"]
    smoke = result.get("smoke")
    warnings = result.get("warning_summary", {})
    calls = result.get("executed_calls", [])
    recipe = result["recipe"]
    lines = [
        f"# PyPTC ISIS RCS admission {result['attempt_id']}", "",
        f"- Technical outcome: **{result['outcome']}**; external review disposition: **awaiting review**.",
        f"- Reference mode: `{ref['mode']}`; snapshot source revision: `{ref['source_revision']}`.",
        f"- Shared skill: `{result['skill']['commit']}`; SHA-256 `{result['skill']['sha256']}`.",
        f"- Snapshot source checkout revision/state: `{ref['observed_checkout_revision']}`, dirty with {ref['dirty_entry_count']} entries; full status: `{ref['status_evidence']}` (SHA-256 `{ref['status_sha256']}`).",
        f"- Input selection: {ref.get('snapshot_content_source', 'not recorded')}; dirty working-tree file contents were not used.",
        "- Snapshot boundary: only the five listed direct lattice inputs are passed to MAD-X; the source checkout's unrelated files were not copied.",
        f"- Target-code commit: `{target.get('repository_commit')}`; runtime: Python `{target.get('runtime')}`, NumPy `{target.get('numpy')}`.",
        f"- Target source: `{target.get('official_source')}`; install/build method: `{target.get('installation_method')}`.",
        f"- Loaded shared library SHA-256: `{target.get('library_sha256')}`; API definition: `{target.get('api_definition')}`.",
        f"- Bootstrap: {target.get('bootstrap_kind')}; loaded API level `{target.get('bootstrap', {}).get('api_level')}` without an ISIS lattice.",
        f"- Variant/sequence: `{recipe['variant']}` / `{recipe['sequence']}`.",
        f"- Approved recipe authorization: {recipe['authorization_source']}.",
        f"- Include order: `{' → '.join(recipe['include_order'])}`.",
        f"- Machine settings: `a1=b1=kqtd=kqtf=0`; permitted reference calculation: {recipe['reference_calculation']}.",
        f"- Reviewed ledger: `{result['ledger']}` (awaiting review).",
        f"- Effective command: `{result['effective_command']}`", "",
        f"- Bootstrap evidence: `{result['target'].get('bootstrap_log', 'not recorded')}`.",
        f"- Reference output table: `{ref.get('reference_output', 'not produced')}` (SHA-256 `{ref.get('reference_output_sha256', 'not available')}`).",
        f"- MAD-X runtime: `{ref.get('madx_version')}`; executable SHA-256 `{ref.get('madx_binary_sha256')}`.",
        f"- Attempt-local input snapshot: `{ref.get('snapshot_input_path')}`; logical input names and hashes are in the result and manifest.",
        f"- Harness checks: {result.get('harness_validation', {}).get('tests_run', 0)} passed; log `{result.get('harness_validation', {}).get('log_path')}` (SHA-256 `{result.get('harness_validation', {}).get('log_sha256')}`).",
        "", "## Executed PyPTC calls", "",
        "The actual calls and returned values are recorded in `pyptc_api_trace.jsonl`.",
    ]
    lines += [f"- `{call}`" for call in calls]
    lines += ["", "## Structural and reference-particle checks", ""]
    lines.append(json.dumps(target.get("structure", {}), sort_keys=True))
    lines.append(json.dumps(target.get("reference_particle", {}), sort_keys=True))
    lines += ["", "## Minimal smoke", ""]
    lines.append(json.dumps(smoke, sort_keys=True))
    lines += ["", "## Runtime warning summary", ""]
    madx_warnings = warnings.get("madx", {})
    pyptc_warnings = warnings.get("pyptc", {})
    lines.append(f"MAD-X: {madx_warnings.get('line_count', 0)} warning/error lines; raw log `{warnings.get('madx_log_path')}` (SHA-256 `{warnings.get('madx_log_sha256')}`).")
    lines.append(f"PyPTC: {pyptc_warnings.get('line_count', 0)} relevant runtime warning lines; raw log `{warnings.get('pyptc_log_path')}` (SHA-256 `{warnings.get('pyptc_log_sha256')}`).")
    lines.append(f"Disposition: {warnings.get('disposition', 'not assessed')}")
    for category, count in madx_warnings.get("categories", {}).items():
        lines.append(f"- MAD-X category ({count}): {category}")
    for warning in pyptc_warnings.get("relevant", []):
        lines.append(f"- Unresolved PyPTC runtime warning for review: {warning}")
    lines += ["", "## Nonclaims", "", result.get("snapshot_scope", "This is snapshot-scoped admission evidence only; it is not a clean-checkout result."),
              "It does not validate closed orbit, tunes, Twiss agreement, dispersion, long-term tracking, collective effects, or benchmark agreement. The technical result is pending external review; it is not reviewed acceptance.", ""]
    if result.get("reason_incomplete"):
        lines += ["## Incomplete evidence", "", result["reason_incomplete"], ""]
    return "\n".join(lines)


def execute(args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    attempt_id = args.attempt_id or next_attempt(output_root)
    out = output_root / attempt_id
    if out.exists() and any(out.iterdir()):
        raise AdmissionBlocked(f"Refusing to overwrite an existing attempt bundle: {out}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "bootstrap").mkdir(exist_ok=True)
    (out / "madx_work" / "PTC_Scripts").mkdir(parents=True)
    (out / "snapshot_inputs").mkdir()
    (out / "reference_evidence").mkdir()
    implementation = out / "implementation"
    implementation.mkdir()
    runner_copy = implementation / "run_admission.py"
    shutil.copy2(Path(__file__).resolve(), runner_copy)
    test_source = ITERATION_DIR / "tests/test_admission.py"
    test_copy = implementation / "test_admission.py"
    if test_source.is_file():
        shutil.copy2(test_source, test_copy)
    runner_hash = sha_file(runner_copy)
    events = out / "events.jsonl"

    snapshot = validate_snapshot(args.snapshot_dir.resolve())
    source_manifest = snapshot["manifest"]
    source_status = snapshot["status_file"]
    shutil.copy2(source_status, out / "reference_evidence" / source_status.name)
    shutil.copy2(args.snapshot_dir / "source_manifest.json", out / "reference_evidence" / "source_manifest.json")
    input_hashes = {}
    for name, source in snapshot["files"].items():
        destination = out / "snapshot_inputs" / name
        shutil.copy2(source, destination)
        input_hashes[f"Lattice_Files/00_Simplified_Lattice/{name}"] = sha_file(destination)
    record_stage(events, "snapshot-copy", "complete", input_count=len(input_hashes))
    test_command = [sys.executable, "-m", "unittest", "discover", "-s", str(ITERATION_DIR / "tests"), "-v"]
    record_stage(events, "harness-tests", "started", command=test_command)
    test_run = run(test_command, cwd=REPO_ROOT)
    test_log = out / "harness-tests.log"
    test_log.write_text(test_run.stdout, encoding="utf-8")
    if test_run.returncode != 0:
        raise AdmissionFailed(f"Fresh harness tests failed; see {test_log}")
    test_match = re.search(r"Ran\s+(\d+)\s+tests?", test_run.stdout)
    test_count = int(test_match.group(1)) if test_match else None
    record_stage(events, "harness-tests", "complete", returncode=test_run.returncode, tests_run=test_count,
                 log_sha256=sha_file(test_log))
    strength_evidence = validate_strengths({name: out / "snapshot_inputs" / name for name in REFERENCE_NAMES})
    validate_recipe(AUTHORIZED_RECIPE)

    build_log = out / "bootstrap" / "build.log"
    build_command = ["bash", "build/build_ptc.sh"]
    record_stage(events, "pyptc-build", "started", command=build_command)
    build = run(build_command, cwd=REPO_ROOT, timeout=900)
    build_log.write_text(build.stdout, encoding="utf-8")
    if build.returncode != 0:
        raise AdmissionFailed(f"PyPTC build failed; see {build_log}")
    record_stage(events, "pyptc-build", "complete", returncode=build.returncode)
    library = args.library.resolve()
    if not library.is_file():
        raise AdmissionBlocked(f"PyPTC library not found: {library}")
    bootstrap_code = "import json,sys; sys.path.insert(0,sys.argv[1]); from pyptc import PTC; p=PTC(sys.argv[2]); print(json.dumps({'library':p.library.resolve().as_posix(),'api_level':p.api_level()}))"
    bootstrap_command = [sys.executable, "-c", bootstrap_code, str(REPO_ROOT), str(library)]
    record_stage(events, "pyptc-bootstrap", "started", command=bootstrap_command)
    bootstrap = run(bootstrap_command, cwd=REPO_ROOT)
    (out / "bootstrap" / "bootstrap.py-command.txt").write_text(" ".join(bootstrap_command) + "\n")
    (out / "bootstrap" / "bootstrap.log").write_text(bootstrap.stdout, encoding="utf-8")
    if bootstrap.returncode != 0:
        raise AdmissionFailed(f"PyPTC library-load/API-level bootstrap failed; see {out / 'bootstrap/bootstrap.log'}")
    record_stage(events, "pyptc-bootstrap", "complete", returncode=bootstrap.returncode)
    try:
        bootstrap_value = json.loads(bootstrap.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        raise AdmissionFailed("PyPTC bootstrap did not return its library/API identity.") from exc

    madx = args.madx.resolve()
    if not madx.is_file() or not os.access(madx, os.X_OK):
        raise AdmissionBlocked(f"MAD-X executable unavailable or not executable: {madx}")
    work = out / "madx_work"
    support_hashes = {}
    for name in AUTHORIZED_RECIPE["ptc_support_scripts"]:
        support = REPO_ROOT / "workflows/madx/ptc_scripts" / name
        if not support.is_file():
            raise AdmissionBlocked(f"Authorized PTC support script missing: {support}")
        shutil.copy2(support, work / "PTC_Scripts" / name)
        support_hashes[name] = sha_file(work / "PTC_Scripts" / name)
    recipe_path = work / "admission_recipe.madx"
    recipe_text = madx_recipe()
    recipe_path.write_text(recipe_text, encoding="utf-8")
    if len(re.findall(r"(?im)^\s*TWISS\s*,", recipe_text)) != 1:
        raise AdmissionBlocked("Generated recipe does not contain exactly one TWISS calculation.")
    madx_command = [str(madx)]
    record_stage(events, "madx-reference", "started", command=madx_command, recipe_sha256=sha_file(recipe_path))
    madx_run = run(madx_command, cwd=work, timeout=180, stdin_path=recipe_path)
    log_path = work / "madx.log"
    log_path.write_text(madx_run.stdout, encoding="utf-8")
    record_stage(events, "madx-reference", "complete", returncode=madx_run.returncode, log_sha256=sha_file(log_path))
    flat_file = work / "PTC-PyORBIT_flat_file.flt"
    twiss_file = work / "reference_twiss.tfs"
    if madx_run.returncode != 0 or not flat_file.is_file() or not twiss_file.is_file():
        raise AdmissionFailed(f"MAD-X failed or omitted required outputs; inspect {log_path}")
    madx_version_match = re.search(r"MAD-X\s+([0-9.]+)", madx_run.stdout)
    madx_version = madx_version_match.group(1) if madx_version_match else "version not found in log"
    effective = {name: parse_value(madx_run.stdout, name) for name in ("a1", "b1", "kqtd", "kqtf", *(f"kqtd_{i}" for i in range(10)), *(f"kqtf_{i}" for i in range(10)))}
    if any(value is None or abs(value) > ZERO_TOL for value in effective.values()):
        raise AdmissionFailed(f"Effective harmonic/trim zero state not proven: {effective}")

    headers = parse_tfs_headers(twiss_file)
    record_stage(events, "pyptc-admission", "started", api_definition_sha256=sha_file(REPO_ROOT / "pyptc/core.py"))
    trace = out / "pyptc_api_trace.jsonl"
    target_runtime_log = out / "pyptc_runtime.log"
    api_run = run_target_api(library, flat_file, target_runtime_log, trace)
    calls = api_run["calls"]
    structure = api_run["structure"]
    fibres = api_run["fibres"]
    scalars = api_run["scalars"]
    record_stage(events, "pyptc-admission", "complete", runtime_log_sha256=sha_file(target_runtime_log))
    pc_ref = float(headers["PC"])
    mass_ref = float(headers["MASS"])
    gamma_expected = math.sqrt(1.0 + (pc_ref / mass_ref) ** 2)
    beta_expected = pc_ref / (mass_ref * gamma_expected)
    kinetic_expected = math.sqrt(pc_ref * pc_ref + mass_ref * mass_ref) - mass_ref
    reference_particle = {
        "madx_pc_gev_c": pc_ref, "pyptc_p0c_gev_c": scalars["p0c_gev_c"],
        "p0c_difference_gev_c": scalars["p0c_gev_c"] - pc_ref,
        "p0c_tolerance_gev_c": PC_TOL_GEV_C,
        "madx_mass_gev": mass_ref, "pyptc_beta0": scalars["beta0"], "derived_beta0": beta_expected,
        "madx_kinetic_gev": kinetic_expected, "pyptc_kinetic_gev": scalars["kinetic_gev"],
        "kinetic_tolerance_gev": KE_TOL_GEV,
        "mass_summary_raw_value": structure.get("mass_gev"),
        "mass_summary_units": "not assumed; API field is not used as a consistency authority",
    }
    if abs(reference_particle["p0c_difference_gev_c"]) > PC_TOL_GEV_C:
        raise AdmissionFailed("PyPTC reference momentum differs from MAD-X beyond the recorded flat-file tolerance.")
    if abs(scalars["beta0"] - beta_expected) > 2e-6 or abs(scalars["kinetic_gev"] - kinetic_expected) > KE_TOL_GEV:
        raise AdmissionFailed("Reference-particle beta or kinetic energy is inconsistent with MAD-X TWISS headers.")
    circumference_ref = float(headers.get("LENGTH", math.nan))
    if not math.isfinite(circumference_ref) or abs(float(structure["circumference_m"]) - circumference_ref) > LENGTH_TOL_M:
        raise AdmissionFailed("PyPTC circumference does not match the approved MAD-X reference table.")
    if not fibres or int(structure["n_nodes"]) <= 0:
        raise AdmissionFailed("PyPTC did not expose a nonempty loaded lattice structure.")
    final_coords = api_run["final_coordinates"]
    loss = api_run["loss"]
    smoke_coords = api_run["initial_coordinates"]
    finite = all(math.isfinite(float(value)) for value in final_coords)
    smoke = {"initial_coordinates": smoke_coords, "final_coordinates": final_coords,
             "coordinate_order": "PyPTC six-coordinate API order; all components initialized to zero",
             "turns": 1, "loss": loss,
             "loss_policy": "any reported loss fails the one-turn smoke; all final coordinates must be finite",
             "finite": finite, "pass": finite and not loss["lost"]}
    if not smoke["pass"]:
        raise AdmissionFailed("One-turn zero-offset smoke produced non-finite coordinates or particle loss.")
    record_stage(events, "pyptc-admission", "complete", smoke_passed=True)

    raw_tfs_hash = sha_file(twiss_file)
    normalized_hash = normalized_tfs_fingerprint(twiss_file)
    (out / "reference_twiss.normalized.sha256").write_text(normalized_hash + "  TFS with @TIME/@DATE headers removed\n")
    warning_summary = classify_runtime_warnings(madx_run.stdout, target_runtime_log.read_text(errors="replace"))
    warning_summary.update({
        "madx_log_path": str(log_path.relative_to(out)),
        "madx_log_sha256": sha_file(log_path),
        "pyptc_log_path": str(target_runtime_log.relative_to(out)),
        "pyptc_log_sha256": sha_file(target_runtime_log),
        "disposition": "MAD-X reports repeated element definitions as ignored; these are counted and retained. PyPTC runtime warnings remain unresolved for review. Structural and reference-particle checks passed, but warning interpretation remains pending external review.",
    })
    result = {
        "attempt_id": attempt_id, "attempt_class": "agent-run diagnostic; not a user-run skill-test result",
        "outcome": "admitted-snapshot", "review_disposition": "awaiting review",
        "effective_command": " ".join([sys.executable, *sys.argv]),
        "seed": None, "ledger": "steps/admit-code-to-isis-rcs/review_ledger.csv",
        "report": "report.md", "canonical_result": "result.json", "manifest": "manifest.json",
        "output_path": str(out.resolve()),
        "snapshot_scope": (f"This technical outcome applies only to the five hash-identified reference inputs copied from {source_manifest['reference_source']['materialized_revision']}. It is not a clean-checkout result and does not describe the dirty source working tree at {source_manifest['reference_source']['checkout_revision_at_copy']}."),
        "harness_validation": {"command": test_command, "outcome": "passed", "tests_run": test_count,
                               "log_path": str(test_log.relative_to(out)), "log_sha256": sha_file(test_log),
                               "runner_sha256": runner_hash, "test_script_sha256": sha_file(test_copy)},
        "skill": {"name": "admit-code-to-isis-rcs", "commit": PINNED_SKILL_COMMIT, "sha256": PINNED_SKILL_SHA256},
        "runner": {"path": "implementation/run_admission.py", "sha256": runner_hash},
        "target": {"repository_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, check=True).stdout.strip(),
                   "official_source": subprocess.run(["git", "config", "--get", "remote.origin.url"], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, check=True).stdout.strip(),
                   "version_identity": "exact Git commit; no separate release tag asserted",
                   "installation_method": "bash build/build_ptc.sh builds build_pyptc/libpyptc.so",
                   "supported_interface": "public pyptc Python package using its ctypes wrapper",
                   "runtime": sys.version, "numpy": importlib.metadata.version("numpy"), "bootstrap": bootstrap_value,
                   "build_command": build_command, "bootstrap_command": bootstrap_command, "build_log": str(build_log.relative_to(out)),
                   "build_log_sha256": sha_file(build_log), "bootstrap_log_sha256": sha_file(out / "bootstrap/bootstrap.log"),
                   "bootstrap_log": str((out / "bootstrap/bootstrap.log").relative_to(out)),
                   "runtime_log": str(target_runtime_log.relative_to(out)),
                   "runtime_log_sha256": sha_file(target_runtime_log),
                   "api_trace": str(trace.relative_to(out)), "api_trace_sha256": sha_file(trace),
                   "api_definition": "pyptc/core.py: PTC.__init__, PTC.api_level, PTC.init_lattice, machine_summary, scalar, track_particle_ptc_with_loss",
                   "bootstrap_kind": "locally constructed no-lattice library-load and API-level readback",
                   "api_definition_sha256": sha_file(REPO_ROOT / "pyptc/core.py"),
                   "library": str(library), "library_sha256": sha_file(library),
                   "structure": {**structure, "flat_file_fibre_count": len(fibres)}, "reference_particle": reference_particle},
        "reference": {"mode": "working-copy-snapshot", "snapshot_content_source": "pinned Git commit tree",
                      "source_repository": source_manifest["reference_source"]["repository"],
                      "snapshot_source_path": str(args.snapshot_dir.resolve()),
                      "snapshot_input_path": "snapshot_inputs/", "source_revision": source_manifest["reference_source"]["materialized_revision"],
                      "observed_checkout_revision": source_manifest["reference_source"]["checkout_revision_at_copy"],
                      "dirty_entry_count": source_manifest["reference_source"]["checkout_status_entry_count"],
                      "status_evidence": "reference_evidence/source_checkout_status.porcelain-v2.txt",
                      "status_sha256": source_manifest["reference_source"]["checkout_status_sha256"],
                      "snapshot_manifest": "reference_evidence/source_manifest.json",
                      "snapshot_manifest_sha256": sha_file(out / "reference_evidence/source_manifest.json"),
                      "source_checkout_path": source_manifest["reference_source"]["local_checkout_observed"],
                      "input_hashes": input_hashes,
                      "variant": AUTHORIZED_RECIPE["variant"], "sequence": AUTHORIZED_RECIPE["sequence"],
                      "machine_settings": {**AUTHORIZED_RECIPE["settings"], "effective_madx": effective},
                      "reference_command": madx_command, "recipe_path": str(recipe_path.relative_to(out)),
                      "madx_version": madx_version, "madx_binary": str(args.madx.resolve()),
                      "madx_binary_sha256": sha_file(args.madx.resolve()),
                      "ptc_support_script_hashes": support_hashes,
                      "recipe_sha256": sha_file(recipe_path), "flat_file": str(flat_file.relative_to(out)),
                      "flat_file_sha256": sha_file(flat_file), "reference_output": str(twiss_file.relative_to(out)),
                      "reference_output_sha256": raw_tfs_hash, "normalized_fingerprint_sha256": normalized_hash,
                      "normalized_fingerprint_method": "SHA-256 of TFS text after removing @TIME and @DATE header rows",
                      "reference_engine_invoked": True, "target_engine_invoked": True},
        "recipe": AUTHORIZED_RECIPE, "strength_evidence": strength_evidence,
        "executed_calls": calls, "smoke": smoke, "warning_summary": warning_summary,
        "nonclaims": ["No orbit, tunes, Twiss agreement, dispersion, long-term stability, collective-effects, or benchmark validation."],
    }
    (out / "warning_summary.json").write_text(json.dumps(warning_summary, indent=2) + "\n")
    manifest = {**result,
                "reference_input_paths": {f"Lattice_Files/00_Simplified_Lattice/{name}": str((out / "snapshot_inputs" / name).relative_to(out)) for name in REFERENCE_NAMES},
                "target_source_hashes": {rel: sha_file(REPO_ROOT / rel) for rel in ("pyptc/core.py", "pyptc/lattice.py", "build/build_ptc.sh")},
                "commands": {"effective_admission": result["effective_command"], "madx": madx_command, "pyptc_bootstrap": bootstrap_command},
                "events": "events.jsonl"}
    (out / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (out / "report.md").write_text(render_report(result), encoding="utf-8")
    return result, out


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-dir", type=Path, default=SNAPSHOT_DIR)
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "test_outputs/admit-code-to-isis-rcs")
    parser.add_argument("--library", type=Path, default=REPO_ROOT / "build_pyptc/libpyptc.so")
    parser.add_argument("--madx", type=Path, default=REPO_ROOT / "workflows/madx/bin/madx-linux64_v5_02_00")
    parser.add_argument("--attempt-id")
    return parser


def cli(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    args.output_root = args.output_root.resolve()
    args.output_root.mkdir(parents=True, exist_ok=True)
    if args.attempt_id is None:
        args.attempt_id = next_attempt(args.output_root)
    try:
        result, output = execute(args)
    except AdmissionBlocked as exc:
        write_incomplete_bundle(args, exc)
        print(f"blocked: {exc}", file=sys.stderr)
        out = args.output_root / str(args.attempt_id)
        if (out / "report.md").exists(): print(f"Report: {out / 'report.md'}")
        if (out / "result.json").exists(): print(f"Canonical result: {out / 'result.json'}")
        return 2
    except (AdmissionFailed, OSError, ValueError, KeyError, json.JSONDecodeError,
            subprocess.CalledProcessError) as exc:
        write_incomplete_bundle(args, exc)
        print(f"failed: {exc}", file=sys.stderr)
        out = args.output_root / str(args.attempt_id)
        if (out / "report.md").exists(): print(f"Report: {out / 'report.md'}")
        if (out / "result.json").exists(): print(f"Canonical result: {out / 'result.json'}")
        return 1
    print(f"Technical outcome: {result['outcome']}")
    print(f"Report: {output / 'report.md'}")
    print(f"Canonical result: {output / 'result.json'}")
    print(f"Manifest: {output / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
