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
from pathlib import Path
from typing import Any

STEP_DIR = Path(__file__).resolve().parents[2]
ITERATION_DIR = STEP_DIR / "iteration-0003"
REPO_ROOT = STEP_DIR.parents[1]
ADMISSION_ID = "attempt-20261027T194128Z"
ADMISSION_BASIS = STEP_DIR / f"admission_basis-accepted-{ADMISSION_ID}"
PINNED_SKILL_REVISION = "f5293a3754dc8c4e9a6a4ba987603924b91949f3"
PINNED_SKILL_SHA256 = "2c720d050d5c26cff6abcb619c503cfae309d8b29ba8434042bfe3e435fa3f26"
ITERATION = "0003"


def campaign_case_catalog() -> list[dict[str, Any]]:
    """Return the explicit Xsuite attempt-029 case cross-reference.

    This catalog makes every requested scenario visible in the run bundle.
    It deliberately does not claim that a case has executed: the current
    PyPTC workflow only calculates the nominal case, and perturbation
    application must be implemented and verified before any case is promoted.
    """
    cases: list[dict[str, Any]] = [{"case_id": "nominal", "kind": "nominal", "execution_status": "implemented-nominal-path"}]
    correctors = (
        ("sp0_r0hd1", "horizontal", "r0hd1_kick"),
        ("sp0_r0vd1", "vertical", "r0vd1_kick"),
        ("sp2_r2hd1", "horizontal", "r2hd1_kick"),
        ("sp2_r2vd1", "vertical", "r2vd1_kick"),
        ("sp3_r3hd1", "horizontal", "r3hd1_kick"),
        ("sp3_r3vd1", "vertical", "r3vd1_kick"),
        ("sp4_r4hd1", "horizontal", "r4hd1_kick"),
        ("sp4_r4vd1", "vertical", "r4vd1_kick"),
        ("sp5_r5hd1", "horizontal", "r5hd1_kick"),
        ("sp5_r5vd1", "vertical", "r5vd1_kick"),
        ("sp7_r7hd1", "horizontal", "r7hd1_kick"),
        ("sp7_r7vd1", "vertical", "r7vd1_kick"),
        ("sp9_r9hd1", "horizontal", "r9hd1_kick"),
        ("sp9_r9vd1", "vertical", "r9vd1_kick"),
    )
    for element, plane, variable in correctors:
        for polarity, sign in (("plus", 1), ("minus", -1)):
            cases.append({
                "case_id": f"corrector_{element}_{polarity}_1mrad",
                "kind": "corrector",
                "element": element,
                "plane": plane,
                "strength_variable": variable,
                "kick_rad": sign * 1.0e-3,
                "execution_status": "blocked-not-implemented",
                "blocked_reason": "The current attempt workflow has no per-case corrector-strength path and no verified application audit.",
            })
    cases.append({
        "case_id": "field_sp0_qf_k1_plus_0p1pct",
        "kind": "field-error",
        "element": "sp0_qf",
        "attribute": "k1",
        "relative_delta": 1.0e-3,
        "execution_status": "blocked-not-implemented",
        "blocked_reason": "The current attempt workflow has no per-case quadrupole-strength path and no verified application audit.",
    })
    for component, value in (("dx", "DX"), ("dy", "DY"), ("ds", "DS"), ("dphi", "DPHI"), ("dtheta", "DTHETA"), ("dpsi", "DPSI")):
        cases.append({
            "case_id": f"sp0_qf_{component}",
            "kind": "misalignment",
            "element": "SP0_QF",
            "component": value,
            "value": 1.0e-3,
            "units": "m" if value in {"DX", "DY", "DS"} else "rad",
            "execution_status": "blocked-not-implemented",
            "blocked_reason": "The PyPTC API exposes misalignment setters, but this benchmark workflow has not yet paired fresh-state MAD-X and PyPTC case application, semantic checks, response metrics, and plots.",
        })
    for case_id in ("survey_error_table", "survey_error_table_verified_intersection"):
        cases.append({
            "case_id": case_id,
            "kind": "survey-error-table",
            "execution_status": "blocked-not-implemented",
            "blocked_reason": "The current attempt workflow has not pinned local table inputs or implemented per-engine component classification and verified-intersection response evidence.",
        })
    if len(cases) != 38 or len({case["case_id"] for case in cases}) != 38:
        raise RuntimeError("Campaign case catalog must contain exactly 38 unique cases")
    return cases


def write_case_catalog(run_dir: Path) -> dict[str, Any]:
    """Persist every declared case and an explicit current execution status."""
    cases = campaign_case_catalog()
    for case in cases:
        case_dir = run_dir / "cases" / case["case_id"]
        case_dir.mkdir(parents=True, exist_ok=True)
        optics.write_json(case_dir / "case.json", case)
        optics.write_json(case_dir / "case_status.json", {
            "case_id": case["case_id"],
            "execution_status": case["execution_status"],
            "reason": case.get("blocked_reason"),
            "plot_status": "not-produced",
        })
    inventory = {
        "source": "Xsuite ISIS RCS attempt-029 case inventory",
        "source_inventory": "campaign-case-inventory.json",
        "source_inventory_sha256": "c19abadada9efd8bd336ef4e0c587c82e464e2d714e8f13018c05389d493c67c",
        "pinned_skill_revision": PINNED_SKILL_REVISION,
        "pinned_skill_sha256": PINNED_SKILL_SHA256,
        "case_count": len(cases),
        "implemented_nominal_path": [case["case_id"] for case in cases if case["execution_status"] == "implemented-nominal-path"],
        "blocked_not_implemented": [case["case_id"] for case in cases if case["execution_status"] == "blocked-not-implemented"],
        "cases": cases,
    }
    optics.write_json(run_dir / "campaign_case_inventory.json", inventory)
    return inventory

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
        {"observable": "corrector and error response", "classification": "unbenchmarked", "reason": "37 perturbation cases are declared in the campaign inventory but are not implemented in this iteration"},
    ]


def run_attempt() -> Path:
    """Execute the fresh nominal optics application and write its evidence bundle."""
    accepted, snapshot, flat_file, library = load_admission_basis()
    provenance = verify_inputs(accepted, snapshot, flat_file, library)
    skill_file = ITERATION_DIR / "SKILL.md"
    if optics.sha256(skill_file) != PINNED_SKILL_SHA256:
        raise RuntimeError("Local skill snapshot hash differs from the iteration's pinned skill revision")
    run_dir = Path(os.environ["PYPTC_BENCHMARK_RUN_DIR"]).resolve()
    output_id = os.environ["PYPTC_BENCHMARK_ATTEMPT_ID"]
    if not run_dir.is_dir() or run_dir.parent != (STEP_DIR / "runs").resolve() or run_dir.name != output_id:
        raise RuntimeError("Shell orchestrator supplied an invalid attempt bundle path")
    run_class = os.environ.get("PYPTC_BENCHMARK_RUN_CLASS", "user-run")
    tracking_mode = os.environ.get("PYPTC_BENCHMARK_TRACKING_MODE", "thick").strip().lower()
    if tracking_mode not in {"thick", "both"}:
        raise RuntimeError("PYPTC_BENCHMARK_TRACKING_MODE must be 'thick' or 'both'")
    case_inventory = write_case_catalog(run_dir)
    manifest: dict[str, Any] = {
        "attempt_id": output_id,
        "attempt_class": run_class,
        "iteration": ITERATION,
        "skill": {"name": "benchmark-code-against-isis-rcs-optics", "revision": PINNED_SKILL_REVISION, "sha256": PINNED_SKILL_SHA256, "snapshot": str(skill_file.relative_to(STEP_DIR))},
        "target_repository": {"head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout.strip(), "worktree_status": subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout.splitlines()},
        "accepted_admission": {"attempt_id": ADMISSION_ID, "review_disposition": "accepted", "scope": "snapshot admission only", "bundle_path": str(ADMISSION_BASIS.relative_to(STEP_DIR)), "result_sha256": optics.sha256(ADMISSION_BASIS / "result.json"), "report_sha256": optics.sha256(ADMISSION_BASIS / "report.md")},
        "identities": provenance,
        "recipe": {"variant": "00_Simplified_Lattice with 2023.strength overlay", "sequence": "synchrotron", "reference_mode": "working-copy-snapshot", "ordered_inputs": ["ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence"], "a1": 0.0, "b1": 0.0, "kqtd": 0.0, "kqtf": 0.0, "all_individual_trim_variables": 0.0, "resplitting": "accepted flat file reused byte-for-byte; no split-policy change", "tracking_mode": tracking_mode, "perturbation_cases": case_inventory["blocked_not_implemented"]},
        "campaign_case_inventory": {"path": "campaign_case_inventory.json", "case_count": case_inventory["case_count"], "implemented_nominal_path": case_inventory["implemented_nominal_path"], "blocked_not_implemented": case_inventory["blocked_not_implemented"]},
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
        case_dir = run_dir / "cases/nominal"
        reference_dir = case_dir / "reference"
        target_dir = case_dir / "target"
        tfs_path, madx_info, headers, reference_rows = optics.run_madx_reference(REPO_ROOT, snapshot, reference_dir, accepted)
        target_info, target_rows, fibres, node_groups = optics.run_pyptc_optics(REPO_ROOT, flat_file, library, target_dir)
        mapping_rows, mapping_summary = optics.build_verified_boundary_map(reference_rows, target_rows, fibres, node_groups)
        optics.write_csv(case_dir / "boundary_map.csv", mapping_rows)
        gamma = float(headers["GAMMA"])
        beta0 = float(np.sqrt(1.0 - gamma ** -2))
        aligned, profile_metrics = optics.align_profiles(mapping_rows, reference_rows, target_rows, beta0) if mapping_summary["status"] == "verified" else ([], [])
        optics.write_csv(case_dir / "aligned_profiles.csv", aligned)
        optics.write_csv(case_dir / "profile_residual_metrics.csv", profile_metrics)
        scalar_rows, chromaticity_info = optics.scalar_comparisons(headers, target_info, mapping_summary)
        optics.write_csv(case_dir / "scalar_comparisons.csv", scalar_rows)
        reference_tracking, reference_turns = optics.run_madx_tracking(REPO_ROOT, snapshot, reference_dir / "tracking/thick", accepted, "thick") if mapping_summary["status"] == "verified" else ({"status": "blocked-prerequisite", "reason": "profile mapping is not verified"}, [])
        target_tracking: dict[str, Any] = {"status": "blocked-not-run", "reason": "profile mapping is not verified"}
        target_turns: list[dict[str, float]] = []
        tracking_records: list[dict[str, Any]] = []
        tracking_metrics: dict[str, Any] = {"status": "blocked", "reason": "both engines must produce complete records"}
        thin_tracking: dict[str, Any] = {"status": "not-requested", "target_status": "not-run; PyPTC thin-lens control is not established"}
        if mapping_summary["status"] == "verified":
            target_tracking, target_turns = optics.run_pyptc_tracking(REPO_ROOT, flat_file, library, target_dir / "tracking")
            tracking_records, tracking_metrics = optics.compare_turn_histories(reference_tracking, reference_turns, target_tracking, target_turns)
            if tracking_mode == "both":
                thin_info, thin_turns = optics.run_madx_tracking(REPO_ROOT, snapshot, reference_dir / "tracking/thin", accepted, "thin")
                if thin_turns:
                    optics.write_csv(reference_dir / "tracking/thin/thin_turn_history.csv", thin_turns)
                thin_tracking = {"reference": thin_info, "target_status": "unavailable; no verified matching PyPTC thin-lens control is exposed in this workflow", "comparison_status": "not-compared", "reason": "Thin tracking is a reference-only diagnostic until both the slicing policy and a matching target control are validated."}
        else:
            thin_tracking = {"status": "blocked-prerequisite", "reason": "profile mapping is not verified", "target_status": "not-run"}
        if reference_turns:
            optics.write_csv(reference_dir / "tracking/thick/reference_turn_history.csv", reference_turns)
        if target_turns:
            optics.write_csv(target_dir / "tracking/target_turn_history.csv", target_turns)
        if tracking_records:
            optics.write_csv(case_dir / "turn_comparisons.csv", tracking_records)
        tracking_status = "complete" if reference_tracking.get("status") == "complete" and target_tracking.get("status") == "complete" and tracking_metrics.get("status") == "pending-tolerance" else "blocked"
        tracking_summary = {"status": tracking_status, "primary_mode": "thick", "requested_mode": tracking_mode, "reference": reference_tracking, "reference_engine_relationship": "MAD-X PTC_TRACK and PyPTC use the PTC tracking engine; this is not an independent tracking-engine validation.", "target": target_tracking, "comparison": tracking_metrics, "thin_mode": thin_tracking, "tune_estimator": {"method": "not used", "reason": "no precision tune-from-tracking claim is made"}}
        optics.write_json(case_dir / "tracking_summary.json", tracking_summary)
        family_map, family_summary = optics.classify_source_families(snapshot, [str(row["element_name"]) for row in mapping_rows], reference_rows)
        optics.write_json(case_dir / "magnet_family_classification.json", {"families": family_map, **family_summary})
        optics.write_json(case_dir / "profile_mapping.json", mapping_summary)
        capabilities = profile_capabilities(mapping_summary["status"], tracking_status)
        optics.write_json(case_dir / "capability_matrix.json", capabilities)

        plot_info = None
        if mapping_summary["status"] == "verified":
            plot_info = optics.write_case_composite(
                run_dir / "plots/cases/nominal.png", aligned, scalar_rows,
                family_map, family_summary,
                "accepted 2023.strength overlay; zero harmonics/trims; synchrotron",
                mapping_summary,
            )
            optics.write_json(run_dir / "plot-manifest.json", {"case_plot_count": 1, "cases": {"nominal": {"path": "plots/cases/nominal.png", **plot_info}}})
        else:
            optics.write_json(run_dir / "plot-manifest.json", {"case_plot_count": 0, "cases": {}, "reason": "No verified mapping; profile overlays and residuals were not computed."})

        nominal_case_status = {
            "case_id": "nominal",
            "execution_status": "completed" if mapping_summary["status"] == "verified" else "executed-blocked-profile-mapping",
            "reason": None if mapping_summary["status"] == "verified" else "The nominal case ran but its element-exit mapping was not verified.",
            "plot_status": "produced" if plot_info is not None else "not-produced; profile mapping was not verified",
            "plot_path": "plots/cases/nominal.png" if plot_info is not None else None,
        }
        optics.write_json(run_dir / "cases/nominal/case_status.json", nominal_case_status)
        case_inventory["executed_case_ids"] = ["nominal"]
        case_inventory["cases"][0]["execution_status"] = nominal_case_status["execution_status"]
        case_inventory["cases"][0]["plot_status"] = nominal_case_status["plot_status"]
        optics.write_json(run_dir / "campaign_case_inventory.json", case_inventory)

        manifest.update({
            "madx": madx_info,
            "pyptc": target_info,
            "commands": {
                "harness_checks": tests,
                "madx": {"argv": madx_info["command"], "cwd": madx_info["working_directory"], "log": "cases/nominal/reference/madx.log"},
                "pyptc": {"python": sys.executable, "cwd": str(target_dir), "api_calls": target_info["executed_api_calls"], "runtime_log": "cases/nominal/target/pyptc_runtime.log"},
            },
            "profile_mapping": mapping_summary,
            "chromaticity": chromaticity_info,
            "profile_metrics": profile_metrics,
            "scalar_comparisons": scalar_rows,
            "capability_matrix": "cases/nominal/capability_matrix.json",
            "plot_manifest": "plot-manifest.json",
            "magnet_family_classification": family_summary,
            "tolerance_policy": "No observable-specific tolerance has been reviewed for this PyPTC campaign; all completed differences are pending-tolerance.",
            "tracking": tracking_summary,
            "case_execution": {"nominal": "executed by existing path", "non_nominal": "explicitly listed as blocked-not-implemented in campaign_case_inventory.json"},
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
            "boundary_map": "cases/nominal/boundary_map.csv",
            "aligned_profiles": "cases/nominal/aligned_profiles.csv",
            "profile_metrics": "cases/nominal/profile_residual_metrics.csv",
            "scalar_comparisons": "cases/nominal/scalar_comparisons.csv",
            "capability_matrix": "cases/nominal/capability_matrix.json",
            "plot_manifest": "plot-manifest.json",
            "declared_case_count": case_inventory["case_count"],
            "nominal_case_executed": True,
            "non_nominal_cases_blocked": len(case_inventory["blocked_not_implemented"]),
            "campaign_case_inventory": "campaign_case_inventory.json",
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
            f"The campaign inventory contains {case_inventory['case_count']} cases cross-referenced from Xsuite attempt 029. This workflow executes nominal only; the other {len(case_inventory['blocked_not_implemented'])} cases are individually recorded as `blocked-not-implemented` with the missing implementation or evidence specified in `campaign_case_inventory.json` and each `cases/<case-id>/case_status.json`. They have no fabricated results or plots. Therefore this attempt is not ready to claim the requested multi-case benchmark; the smoke run verifies inventory/provenance handling and the existing nominal path only.",
            "",
            f"MAD-X 5.02.00 reports `DQ1/DQ2` as `dQ/dDELTAP`, equivalent to `dQ/d(delta_p)` with factor 1. The PyPTC native values are retained, but the public wrapper does not establish their derivative coordinate, so the cross-code chromaticity comparison is `blocked`: {chromaticity_info['planes']}.",
            "",
            f"Bounded tracking status is `{tracking_status}`. Requested mode: `{tracking_mode}`; the primary route is thick MAD-X `PTC_TRACK` against the PyPTC thick-lattice workflow. Both use the PTC tracking engine, so this is not an independent tracking-engine validation. The optional thin route is reference-only and separately classified because the ten-slice `MAKETHIN` diagnostic is unvalidated and no matching PyPTC thin control is established. Reference: `{reference_tracking.get('status')}`; target: `{target_tracking.get('status')}`. The plan uses {optics.TRACK_TURNS} turns from {optics.TRACK_INITIAL}; see `tracking_summary.json` for complete counts and the reason if blocked. No target-only or partial record is presented as a cross-code comparison. No perturbation, nonlinear, long-term, collective-effects, clean-checkout admission, or production claim is made.",
            "",
            "MAD-X and PyPTC runtime warnings are retained in `reference/madx.log` and `target/pyptc_runtime.log`. They are observations, not silently discarded or interpreted as resolved.",
            "",
            "## Evidence files",
            "",
            "- `cases/nominal/` — reference and target data, boundary map, aligned profiles, residuals, scalar results, and tracking records.",
            "- `campaign_case_inventory.json` and `cases/<case-id>/{case.json,case_status.json}` — all 38 declared case identities and explicit execution status.",
            "- `plots/cases/nominal.png` — nominal case composite when mapping is verified; `plot-manifest.json` links each case to its PNG.",
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
        raise SystemExit("benchmark_pyptc.py is an internal workflow module; invoke scripts/shell/benchmark-pyptc-attempt.sh")
    run_attempt()
