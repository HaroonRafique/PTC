#!/usr/bin/env python3
"""Run one fresh, provenance-recorded PyPTC/MAD-X skill application."""

from __future__ import annotations

import csv
import json
import os
import platform
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ITERATION_DIR = Path(__file__).resolve().parent
STEP_DIR = ITERATION_DIR.parent
REPO_ROOT = STEP_DIR.parents[1]
OUTPUT_ROOT = REPO_ROOT / "test_outputs/benchmark-pyptc-linear-optics-against-madx"
ADMISSION_ID = "attempt-20261027T194128Z"
ADMISSION_BASIS = STEP_DIR / f"admission_basis-accepted-{ADMISSION_ID}"
PINNED_SKILL_REVISION = "f5293a3754dc8c4e9a6a4ba987603924b91949f3"
PINNED_SKILL_SHA256 = "2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26"

if __name__ == "__main__":
    venv_root = STEP_DIR / ".venv"
    venv_python = venv_root / "bin/python"
    if venv_python.is_file() and Path(sys.prefix).resolve() != venv_root.resolve():
        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve())])
os.environ.setdefault("MPLCONFIGDIR", str(STEP_DIR / ".mplconfig"))

import numpy as np

sys.path.insert(0, str(ITERATION_DIR))
import isis_rcs_optics as optics


def load_admission_basis() -> tuple[dict[str, Any], Path, Path, Path]:
    """Validate the user-accepted admission record and return its input paths."""
    result_path = ADMISSION_BASIS / "result.json"
    if not result_path.is_file():
        raise FileNotFoundError(f"Accepted admission basis is missing: {result_path}")
    accepted = json.loads(result_path.read_text(encoding="utf-8"))
    if accepted.get("attempt_id") != ADMISSION_ID or accepted.get("outcome") != "admitted-snapshot":
        raise RuntimeError("Pinned admission bundle is not the expected admitted-snapshot attempt")
    ledger_path = REPO_ROOT / "steps/admit-code-to-isis-rcs/review_ledger.csv"
    with ledger_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    disposition = next((row for row in rows if row["attempt_id"] == ADMISSION_ID), None)
    if disposition is None or disposition["disposition"] != "accepted" or disposition["acceptance_scope"] != "snapshot admission only":
        raise RuntimeError("Admission ledger does not confirm accepted snapshot scope for this bundle")
    snapshot = ADMISSION_BASIS / "snapshot_inputs"
    flat_file = ADMISSION_BASIS / "madx_work/PTC-PyORBIT_flat_file.flt"
    library = ADMISSION_BASIS / "bootstrap/libpyptc.so"
    for required in (snapshot, flat_file, library):
        if not required.exists():
            raise FileNotFoundError(f"Required accepted admission evidence is missing: {required}")
    return accepted, snapshot, flat_file, library


def verify_inputs(accepted: dict[str, Any], snapshot: Path, flat_file: Path, library: Path) -> dict[str, Any]:
    """Verify the five input and target-library hashes against admission evidence."""
    input_hashes = accepted["reference"]["input_hashes"]
    files = {
        "ISIS.injected_beam": snapshot / "ISIS.injected_beam",
        "ISIS.elements": snapshot / "ISIS.elements",
        "ISIS.strength": snapshot / "ISIS.strength",
        "2023.strength": snapshot / "2023.strength",
        "ISIS.sequence": snapshot / "ISIS.sequence",
    }
    actual = {name: optics.sha256(path) for name, path in files.items()}
    expected = {name.rsplit("/", 1)[-1]: digest for name, digest in input_hashes.items()}
    if actual != expected:
        raise RuntimeError(f"Admission source input hashes changed: expected {expected}, got {actual}")
    expected_flat = accepted["reference"]["flat_file_sha256"]
    if optics.sha256(flat_file) != expected_flat:
        raise RuntimeError("Accepted PTC flat-file digest no longer matches admission")
    expected_library = accepted["target"]["library_sha256"]
    if optics.sha256(library) != expected_library:
        raise RuntimeError("Accepted PyPTC library digest no longer matches admission")
    return {
        "ordered_input_hashes": actual,
        "flat_file_sha256": optics.sha256(flat_file),
        "library_sha256": optics.sha256(library),
        "accepted_target_source_revision": accepted["target"]["repository_commit"],
        "accepted_source_lattice_revision": accepted["reference"]["source_revision"],
        "accepted_madx_binary_sha256": accepted["reference"].get("madx_binary_sha256", accepted["reference"].get("binary_sha256")),
    }


def run_harness_checks(run_dir: Path) -> dict[str, Any]:
    """Run the fresh iteration's independent deterministic fixtures."""
    log_path = run_dir / "harness-tests.log"
    command = [sys.executable, "-m", "unittest", "discover", "-s", str(ITERATION_DIR / "tests"), "-v"]
    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    log_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    return {
        "argv": command,
        "cwd": str(REPO_ROOT),
        "log": str(log_path.relative_to(run_dir)),
        "returncode": completed.returncode,
        "sha256": optics.sha256(log_path),
    }


def profile_capabilities(mapping_status: str, tracking_status: str) -> list[dict[str, Any]]:
    """Return observables and their evidence status for this nominal case."""
    profile_state = "pending-tolerance" if mapping_status == "verified" else "blocked"
    return [
        {"observable": "reference orbit x/px/y/py", "classification": profile_state, "reason": "named MAD-X/PyPTC element-exit rows are mapped by name, occurrence, fibre index and s" if profile_state == "pending-tolerance" else "element-exit map not verified"},
        {"observable": "beta x/y", "classification": profile_state, "reason": "mapped profile values retained; no reviewed tolerance" if profile_state == "pending-tolerance" else "element-exit map not verified"},
        {"observable": "alpha x/y", "classification": profile_state, "reason": "mapped profile values retained; no reviewed tolerance" if profile_state == "pending-tolerance" else "element-exit map not verified"},
        {"observable": "dispersion and derivatives", "classification": profile_state, "reason": "MAD-X run-specific beta0 normalization recorded; no reviewed tolerance" if profile_state == "pending-tolerance" else "element-exit map not verified"},
        {"observable": "phase advance", "classification": profile_state, "reason": "element-exit phase values and phase origin retained; no reviewed tolerance" if profile_state == "pending-tolerance" else "element-exit map not verified"},
        {"observable": "fractional tunes", "classification": "pending-tolerance", "reason": "scalar values and signed differences retained; no reviewed tolerance"},
        {"observable": "circumference", "classification": "pending-tolerance", "reason": "scalar values and signed differences retained; no reviewed tolerance"},
        {"observable": "chromaticity", "classification": "blocked", "reason": "PyPTC lattice_GET_CHROM derivative coordinate is not documented by the public wrapper; no conversion is inferred"},
        {"observable": "bounded single-particle tracking", "classification": "pending-tolerance" if tracking_status == "complete" else "blocked", "reason": "complete matched records retained; no reviewed tolerance" if tracking_status == "complete" else "the reference and target did not both produce complete compatible records"},
        {"observable": "corrector and error response", "classification": "unbenchmarked", "reason": "no perturbation case was authorized for this nominal-only iteration"},
    ]


def run_attempt() -> Path:
    """Execute the fresh nominal optics application and write its evidence bundle."""
    accepted, snapshot, flat_file, library = load_admission_basis()
    provenance = verify_inputs(accepted, snapshot, flat_file, library)
    skill_file = ITERATION_DIR / "SKILL.md"
    if optics.sha256(skill_file) != PINNED_SKILL_SHA256:
        raise RuntimeError("Local skill snapshot hash differs from the iteration's pinned skill revision")
    output_id = "attempt-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if (OUTPUT_ROOT / output_id).exists():
        raise FileExistsError(f"Attempt directory already exists: {OUTPUT_ROOT / output_id}")
    run_dir = OUTPUT_ROOT / output_id
    run_dir.mkdir(parents=True)
    run_class = os.environ.get("PYPTC_BENCHMARK_RUN_CLASS", "user-run")
    manifest: dict[str, Any] = {
        "attempt_id": output_id,
        "attempt_class": run_class,
        "iteration": "0002",
        "skill": {"name": "benchmark-code-against-isis-rcs-optics", "revision": PINNED_SKILL_REVISION, "sha256": PINNED_SKILL_SHA256, "snapshot": str(skill_file.relative_to(STEP_DIR))},
        "target_repository": {"head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout.strip(), "worktree_status": subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout.splitlines()},
        "accepted_admission": {"attempt_id": ADMISSION_ID, "review_disposition": "accepted", "scope": "snapshot admission only", "bundle_path": str(ADMISSION_BASIS.relative_to(STEP_DIR)), "result_sha256": optics.sha256(ADMISSION_BASIS / "result.json"), "report_sha256": optics.sha256(ADMISSION_BASIS / "report.md")},
        "identities": provenance,
        "recipe": {"variant": "00_Simplified_Lattice with 2023.strength overlay", "sequence": "synchrotron", "reference_mode": "working-copy-snapshot", "ordered_inputs": ["ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence"], "a1": 0.0, "b1": 0.0, "kqtd": 0.0, "kqtf": 0.0, "all_individual_trim_variables": 0.0, "resplitting": "accepted flat file reused byte-for-byte; no split-policy change", "perturbation_cases": []},
        "runtime": {"python": sys.version, "platform": platform.platform()},
        "output_directory": str(run_dir),
        "commands": {},
        "nonclaims": ["No clean-checkout admission claim.", "No tolerance-based or physics acceptance claim.", "No chromaticity agreement claim until target derivative coordinate is established.", "No bounded tracking, perturbation, nonlinear, or production claim unless separately completed in this attempt."],
    }
    try:
        tests = run_harness_checks(run_dir)
        manifest["harness_checks"] = tests
        if tests["returncode"] != 0:
            raise RuntimeError("Fresh deterministic harness checks failed; see harness-tests.log")
        reference_dir = run_dir / "reference"
        target_dir = run_dir / "target"
        case_dir = run_dir / "case_nominal"
        tfs_path, madx_info, headers, reference_rows = optics.run_madx_reference(REPO_ROOT, snapshot, reference_dir, accepted)
        target_info, target_rows, fibres, node_groups = optics.run_pyptc_optics(REPO_ROOT, flat_file, library, target_dir)
        mapping_rows, mapping_summary = optics.build_verified_boundary_map(reference_rows, target_rows, fibres, node_groups)
        optics.write_csv(run_dir / "boundary_map.csv", mapping_rows)
        gamma = float(headers["GAMMA"])
        beta0 = float(np.sqrt(1.0 - gamma ** -2))
        aligned, profile_metrics = optics.align_profiles(mapping_rows, reference_rows, target_rows, beta0) if mapping_summary["status"] == "verified" else ([], [])
        optics.write_csv(run_dir / "aligned_profiles.csv", aligned)
        optics.write_csv(run_dir / "profile_residual_metrics.csv", profile_metrics)
        scalar_rows, chromaticity_info = optics.scalar_comparisons(headers, target_info, mapping_summary)
        optics.write_csv(run_dir / "scalar_comparisons.csv", scalar_rows)
        reference_tracking, reference_turns = optics.run_madx_tracking(REPO_ROOT, snapshot, run_dir / "reference/tracking", accepted) if mapping_summary["status"] == "verified" else ({"status": "blocked-prerequisite", "reason": "profile mapping is not verified"}, [])
        target_tracking: dict[str, Any] = {"status": "blocked-not-run", "reason": "profile mapping is not verified"}
        target_turns: list[dict[str, float]] = []
        tracking_records: list[dict[str, Any]] = []
        tracking_metrics: dict[str, Any] = {"status": "blocked", "reason": "both engines must produce complete records"}
        if mapping_summary["status"] == "verified":
            target_tracking, target_turns = optics.run_pyptc_tracking(REPO_ROOT, flat_file, library, run_dir / "target/tracking")
            tracking_records, tracking_metrics = optics.compare_turn_histories(reference_tracking, reference_turns, target_tracking, target_turns)
        if reference_turns:
            optics.write_csv(run_dir / "reference/tracking/reference_turn_history.csv", reference_turns)
        if target_turns:
            optics.write_csv(run_dir / "target/tracking/target_turn_history.csv", target_turns)
        if tracking_records:
            optics.write_csv(run_dir / "turn_comparisons.csv", tracking_records)
        tracking_status = "complete" if reference_tracking.get("status") == "complete" and target_tracking.get("status") == "complete" and tracking_metrics.get("status") == "pending-tolerance" else "blocked"
        tracking_summary = {"status": tracking_status, "reference": reference_tracking, "target": target_tracking, "comparison": tracking_metrics, "tune_estimator": {"method": "not used", "reason": "no precision tune-from-tracking claim is made"}}
        optics.write_json(run_dir / "tracking_summary.json", tracking_summary)
        family_map, family_summary = optics.classify_source_families(snapshot, [str(row["element_name"]) for row in mapping_rows], reference_rows)
        optics.write_json(run_dir / "magnet_family_classification.json", {"families": family_map, **family_summary})
        optics.write_json(run_dir / "profile_mapping.json", mapping_summary)
        capabilities = profile_capabilities(mapping_summary["status"], tracking_status)
        optics.write_json(run_dir / "capability_matrix.json", capabilities)

        plot_info = None
        if mapping_summary["status"] == "verified":
            plot_info = optics.write_case_composite(
                case_dir / "nominal_optics_composite.png", aligned, scalar_rows,
                family_map, family_summary,
                "accepted 2023.strength overlay; zero harmonics/trims; synchrotron",
                mapping_summary,
            )
            optics.write_json(run_dir / "plot_manifest.json", {"case_plot_count": 1, "plots": [plot_info]})
        else:
            optics.write_json(run_dir / "plot_manifest.json", {"case_plot_count": 0, "plots": [], "reason": "No verified mapping; profile overlays and residuals were not computed."})

        manifest.update({
            "madx": madx_info,
            "pyptc": target_info,
            "commands": {
                "harness_checks": tests,
                "madx": {"argv": madx_info["command"], "cwd": madx_info["working_directory"], "log": "reference/madx.log"},
                "pyptc": {"python": sys.executable, "cwd": str(target_dir), "api_calls": target_info["executed_api_calls"], "runtime_log": "target/pyptc_runtime.log"},
            },
            "profile_mapping": mapping_summary,
            "chromaticity": chromaticity_info,
            "profile_metrics": profile_metrics,
            "scalar_comparisons": scalar_rows,
            "capability_matrix": "capability_matrix.json",
            "plot_manifest": "plot_manifest.json",
            "magnet_family_classification": family_summary,
            "tolerance_policy": "No observable-specific tolerance has been reviewed for this PyPTC campaign; all completed differences are pending-tolerance.",
            "tracking": tracking_summary,
        })
        outcome = "blocked-profile-mapping" if mapping_summary["status"] != "verified" else "blocked-bounded-tracking" if tracking_status != "complete" else "incomplete-chromaticity-and-plot-review"
        manifest["outcome"] = outcome
        optics.write_json(run_dir / "manifest.json", manifest)
        result = {
            "attempt_id": output_id,
            "attempt_class": run_class,
            "outcome": outcome,
            "technical_status": "fresh user-facing workflow ran; benchmark is incomplete under the pinned skill",
            "report": "report.md",
            "manifest": "manifest.json",
            "boundary_map": "boundary_map.csv",
            "aligned_profiles": "aligned_profiles.csv",
            "profile_metrics": "profile_residual_metrics.csv",
            "scalar_comparisons": "scalar_comparisons.csv",
            "capability_matrix": "capability_matrix.json",
            "plot_manifest": "plot_manifest.json",
        }
        optics.write_json(run_dir / "result.json", result)
        report = [
            f"# PyPTC/MAD-X linear-optics attempt {output_id}",
            "",
            f"**Outcome:** `{outcome}`. **Run class:** `{run_class}`.",
            "",
            "## Accepted basis and recipe",
            "",
            f"This run uses the user-accepted admission snapshot `{ADMISSION_ID}`. Its accepted scope is snapshot admission only. The exact accepted PyPTC shared library and MAD-X 5.02.00 binary were reused by digest. The effective recipe uses the five pinned inputs in admission order, the 2023 strength overlay, `synchrotron`, `a1=b1=0`, all trim variables zero, and the accepted flat file without resplitting.",
            "",
            "## Sampling and profile comparison",
            "",
            f"MAD-X returned {len(reference_rows)} named TWISS rows; PyPTC returned {len(target_rows)} orbit-node Twiss rows and {len(node_groups)} printer groups. The mapping status is `{mapping_summary['status']}` with {mapping_summary['mapped_boundaries']} matched element exits at a position tolerance of {optics.POSITION_TOLERANCE_M:g} m. Mapping method and every row identity are retained in `boundary_map.csv`.",
            "",
            f"Reference dispersion columns were multiplied by this run's beta0={beta0:.12g}, derived from the MAD-X TWISS GAMMA header. {len(profile_metrics)} profile residual summaries are retained. All remain `pending-tolerance`; no agreement or physics claim is made.",
            "",
            "## Chromaticity, tracking, and limitations",
            "",
            f"MAD-X 5.02.00 reports `DQ1/DQ2` as `dQ/dDELTAP`, equivalent to `dQ/d(delta_p)` with factor 1. The PyPTC native values are retained, but the public wrapper does not establish their derivative coordinate, so the cross-code chromaticity comparison is `blocked`: {chromaticity_info['planes']}.",
            "",
            f"Bounded tracking status is `{tracking_status}`. Reference: `{reference_tracking.get('status')}`; target: `{target_tracking.get('status')}`. The plan uses {optics.TRACK_TURNS} turns from {optics.TRACK_INITIAL}; see `tracking_summary.json` for complete counts and the reason if blocked. No target-only or partial record is presented as a cross-code comparison. No perturbation, nonlinear, long-term, collective-effects, clean-checkout admission, or production claim is made.",
            "",
            "MAD-X and PyPTC runtime warnings are retained in `reference/madx.log` and `target/pyptc_runtime.log`. They are observations, not silently discarded or interpreted as resolved.",
            "",
            "## Evidence files",
            "",
            "- `boundary_map.csv` and `profile_mapping.json` — identity and position evidence.",
            "- `aligned_profiles.csv` and `profile_residual_metrics.csv` — data and signed residual summaries, when mapping is verified.",
            "- `scalar_comparisons.csv` and `capability_matrix.json` — scalar results and scope.",
            "- `case_nominal/nominal_optics_composite.png` and `plot_manifest.json` — one nominal case composite when mapping is verified.",
            "- `manifest.json`, `result.json`, and `harness-tests.log` — provenance, canonical status, and harness checks.",
        ]
        (run_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
        print(f"{outcome}: {run_dir}")
        return run_dir
    except Exception as error:
        manifest["failure"] = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}
        manifest["outcome"] = "failed"
        optics.write_json(run_dir / "manifest.json", manifest)
        optics.write_json(run_dir / "result.json", {"attempt_id": output_id, "attempt_class": run_class, "outcome": "failed", "error": str(error)})
        (run_dir / "report.md").write_text(f"# PyPTC/MAD-X linear-optics attempt {output_id}\n\n**Outcome:** failed.\n\n```text\n{traceback.format_exc()}\n```\n", encoding="utf-8")
        print(f"failed: {error}\nReport: {run_dir / 'report.md'}", file=sys.stderr)
        raise


if __name__ == "__main__":
    if len(sys.argv) != 1:
        raise SystemExit("run_benchmark.py accepts no arguments; configure only documented environment variables")
    run_attempt()
