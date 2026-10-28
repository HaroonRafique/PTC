#!/usr/bin/env python3
"""Run one fresh, provenance-recorded PyPTC/MAD-X skill application."""

from __future__ import annotations

import csv
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

STEP_DIR = Path(__file__).resolve().parents[2]
ITERATION_DIR = STEP_DIR / "scripts/python/iteration_0003"
SKILL_SNAPSHOT_DIR = STEP_DIR / "iteration-0004"
REPO_ROOT = STEP_DIR.parents[1]
ADMISSION_ID = "attempt-20261027T194128Z"
ADMISSION_BASIS = STEP_DIR / f"admission_basis-accepted-{ADMISSION_ID}"
PINNED_SKILL_REVISION = "f5293a3754dc8c4e9a6a4ba987603924b91949f3+working-tree"
PINNED_SKILL_SHA256 = "b6819ee834b1d3d114216ffd4bae4b52e87715e5baa4525f03394bde5241ae0b"
ITERATION = "0004"


def campaign_case_catalog() -> list[dict[str, Any]]:
    """Inventory all cross-referenced cases and assess them for this target.

    The Xsuite inventory is used only to enumerate candidates. Each candidate
    is separately assessed against the PyPTC workflow and its current
    application evidence; the cross-reference does not establish equivalence.
    """
    cases: list[dict[str, Any]] = [{
        "case_id": "nominal",
        "family": "nominal",
        "source_identity": "accepted admission basis and its hash-pinned recipe",
        "disposition": "included",
        "reason": "The accepted base recipe is available and the nominal reference/target path is implemented.",
        "evidence": ["accepted admission basis", "iteration-0004 nominal workflow"],
        "reference_application_status": "base-recipe; executed by nominal workflow",
        "target_application_status": "base-recipe; executed by nominal workflow",
        "execution_status": "planned",
    }]
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
                "family": "corrector-response",
                "source_identity": f"Xsuite attempt-029 candidate {element}, {plane}, {polarity}; cross-reference only",
                "disposition": "included",
                "reason": "The accepted MAD-X source model defines this corrector kick as a strength variable; a case-local strength input and freshly generated PTC flat file provide an isolated reference/target state.",
                "evidence": ["Xsuite attempt-029 candidate inventory", "accepted ISIS.elements and ISIS.strength source definitions", "case-local MAD-X recipe and flat-file regeneration"],
                "reference_application_status": "planned; case-local MAD-X recipe",
                "target_application_status": "planned; fresh PyPTC load of case-local flat file",
                "execution_status": "planned",
            })
    cases.append({
        "case_id": "field_sp0_qf_k1_plus_0p1pct",
        "kind": "field-error",
        "element": "sp0_qf",
        "attribute": "k1",
        "relative_delta": 1.0e-3,
        "family": "field-strength-response",
        "source_identity": "Xsuite attempt-029 candidate SP0_QF K1 perturbation; cross-reference only",
        "disposition": "included",
        "reason": "A case-local MAD-X instance-strength override can generate a fresh PTC flat file for PyPTC and a matching MAD-X TWISS reference.",
        "evidence": ["Xsuite attempt-029 candidate inventory", "accepted ISIS.sequence places SP0_QF as a named instance", "case-local MAD-X recipe and flat-file regeneration"],
        "reference_application_status": "planned; instance-specific MAD-X recipe",
        "target_application_status": "planned; fresh PyPTC load of case-local flat file",
        "execution_status": "planned",
    })
    for component, value in (("dx", "DX"), ("dy", "DY"), ("ds", "DS"), ("dphi", "DPHI"), ("dtheta", "DTHETA"), ("dpsi", "DPSI")):
        cases.append({
            "case_id": f"sp0_qf_{component}",
            "kind": "misalignment",
            "element": "SP0_QF",
            "component": value,
            "value": 1.0e-3,
            "units": "m" if value in {"DX", "DY", "DS"} else "rad",
            "family": "misalignment-response",
            "source_identity": f"Xsuite attempt-029 candidate SP0_QF {value} transform; cross-reference only",
            "disposition": "included",
            "reason": "The isolated component is applied through a case-local MAD-X EFIELD table; MAD-X SETERR and PyPTC apply_madx_error_table consume the same table in the documented MAD-X convention from fresh nominal states.",
            "evidence": ["Xsuite attempt-029 candidate inventory", "PyPTC PTC.apply_madx_error_table MAD-X convention API", "existing PyPTC MAD-X/PyPTC closed-orbit comparison workflow"],
            "reference_application_status": "planned; fresh MAD-X READMYTABLE/SETERR from case-local table",
            "target_application_status": "planned; fresh PyPTC apply_madx_error_table from same table",
            "execution_status": "planned",
        })
    for case_id in ("survey_error_table", "survey_error_table_verified_intersection"):
        if case_id == "survey_error_table":
            reason = (
                "PyPTC now applies MAD-X alignment and integrated normal/skew magnetic multipole fields through "
                "apply_madx_error_table. The pinned local Apr 2026 EFIELD table has no nonzero unsupported fields. "
                "The exact Xsuite attempt-029 table is not archived here, so this executes the PyPTC survey-table "
                "candidate without asserting byte-for-byte equivalence to that external candidate."
            )
            evidence = [
                "PyPTC EFIELD API investigation steps/benchmark-pyptc-linear-optics-against-madx/investigations/0001-efield-api.md",
                "pyptc/error_table.py supports alignment and K0L..K20L/K0SL..K20SL fields and rejects nonzero unsupported fields",
                "pinned workflows/madx/reference_errors/apr_2026_survey_corrected.tfs hash and field audit",
            ]
            target_status = "planned; fresh PyPTC apply_madx_error_table from the unchanged full survey table"
            disposition = "included"
        else:
            reason = "The verified intersection retains the six alignment components supported by PyPTC's MAD-X error-table reader; the case-local table is derived from the pinned PyPTC survey table and shared by both fresh engines."
            evidence = ["Xsuite attempt-029 candidate inventory; six-component verified intersection", "PyPTC error_table.py supports these six MAD-X EALIGN fields", "case-local filtered table hash and PyPTC example API path"]
            target_status = "planned; fresh PyPTC apply_madx_error_table over the six-component intersection"
            disposition = "included"
        cases.append({
            "case_id": case_id,
            "kind": "survey-error-table",
            "family": "survey-error-table",
            "source_identity": f"Xsuite attempt-029 candidate {case_id}; source table not adopted as PyPTC input",
            "disposition": disposition,
            "reason": reason,
            "evidence": evidence,
            "reference_application_status": "not-run",
            "target_application_status": target_status,
            "execution_status": "deferred" if disposition != "included" else "planned",
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
            "disposition": case["disposition"],
            "execution_status": case["execution_status"],
            "reason": case["reason"],
            "evidence": case["evidence"],
            "reference_application_status": case["reference_application_status"],
            "target_application_status": case["target_application_status"],
            "plot_status": "not-produced",
        })
    inventory = {
        "source": "Xsuite ISIS RCS attempt-029 case inventory, used as a planning cross-reference only",
        "source_inventory": "Xsuite ISIS RCS campaign-case-inventory.json",
        "source_inventory_sha256": "c19abadada9efd8bd336ef4e0c587c82e464e2d714e8f13018c05389d493c67c",
        "pinned_skill_revision": PINNED_SKILL_REVISION,
        "pinned_skill_sha256": PINNED_SKILL_SHA256,
        "case_count": len(cases),
        "dispositions": {key: [case["case_id"] for case in cases if case["disposition"] == key] for key in ("included", "not-applicable", "unsupported", "blocked")},
        "executed_case_ids": [],
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
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.patches import Patch

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
    # The accepted admission library remains preserved as evidence, but the
    # optics candidate must use the current PyPTC build so API additions under
    # test are present. scripts/shell/setup-benchmark.sh builds this library.
    library = REPO_ROOT / "build_pyptc/libpyptc.so"
    for required in (snapshot, flat_file, library):
        if not required.exists():
            raise FileNotFoundError(f"Required accepted admission evidence is missing: {required}")
    return accepted, snapshot, flat_file, library


def verify_inputs(accepted: dict[str, Any], snapshot: Path, flat_file: Path, library: Path) -> dict[str, Any]:
    """Verify admission inputs and identify the current PyPTC candidate build."""
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
    sys.path.insert(0, str(REPO_ROOT))
    from pyptc import PTC

    candidate_ptc = PTC(library)
    api_level = candidate_ptc.api_level()
    if api_level < 5:
        raise RuntimeError(f"Current PyPTC EFIELD API level 5 is required; build reports API level {api_level}")
    return {
        "ordered_input_hashes": actual,
        "flat_file_sha256": optics.sha256(flat_file),
        "library_sha256": optics.sha256(library),
        "accepted_admission_library_sha256": accepted["target"]["library_sha256"],
        "candidate_api_level": api_level,
        "candidate_library_path": str(library),
        "candidate_source_revision": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout.strip(),
        "accepted_source_lattice_revision": accepted["reference"]["source_revision"],
        "accepted_madx_binary_sha256": accepted["reference"].get("madx_binary_sha256", accepted["reference"].get("binary_sha256")),
    }


def materialize_case_input(snapshot: Path, case: dict[str, Any], case_dir: Path) -> Path:
    """Create an isolated source-input copy and apply one declared strength change."""
    case_input = case_dir / "input_snapshot"
    case_input.mkdir(parents=True, exist_ok=True)
    for name in ("ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence"):
        shutil.copy2(snapshot / name, case_input / name)
    if case.get("kind") == "corrector":
        source = case_input / "ISIS.strength"
        variable = str(case["strength_variable"])
        text = source.read_text(encoding="utf-8")
        pattern = re.compile(rf"(?im)^(\s*{re.escape(variable)}\s*:=\s*)[^;]+;")
        text, count = pattern.subn(rf"\g<1>{float(case['kick_rad']):.17g};", text)
        if count != 1:
            raise RuntimeError(f"Expected one {variable} assignment in {source}, found {count}")
        source.write_text(text, encoding="utf-8")
        case["applied_input_override"] = {
            "file": "ISIS.strength", "variable": variable,
            "value_rad": float(case["kick_rad"]), "assignment_count": count,
        }
    elif case.get("kind") == "field-error":
        case["applied_input_override"] = {
            "file": "reference_recipe.madx",
            "expression": "sp0_qf->k1 := sp0_qf->k1 * (1 + relative_delta)",
            "relative_delta": float(case["relative_delta"]),
        }
    elif case.get("kind") in {"misalignment", "survey-error-table"}:
        source_table = REPO_ROOT / "workflows/madx/reference_errors/apr_2026_survey_corrected.tfs"
        if not source_table.is_file():
            raise FileNotFoundError(f"Pinned campaign survey table is missing: {source_table}")
        destination = case_dir / "case_error_table.tfs"
        audit = materialize_case_error_table(case, source_table, destination)
        case["error_table_path"] = "case_error_table.tfs"
        case["error_table_sha256"] = optics.sha256(destination)
        case["error_table_source"] = {
            "path": str(source_table.relative_to(REPO_ROOT)),
            "sha256": optics.sha256(source_table),
        }
        case["error_table_application_audit"] = audit
    else:
        raise ValueError(f"No source mutation implementation for case {case['case_id']}")
    return case_input


def materialize_case_error_table(case: dict[str, Any], source: Path, destination: Path) -> dict[str, Any]:
    """Create either an unchanged full EFIELD table or a filtered alignment case."""
    if case.get("case_id") == "survey_error_table":
        # Keep every source column and row byte-for-byte for the full-table
        # case. The public API performs the definitive unsupported-field guard.
        sys.path.insert(0, str(REPO_ROOT))
        from pyptc.error_table import read_madx_error_table

        records = read_madx_error_table(source, nonzero=True)
        unsupported = [
            {"name": record.name, "field": field, "value": value}
            for record in records
            for field, value in record.unsupported
        ]
        if unsupported:
            raise ValueError(f"Pinned full EFIELD table has nonzero unsupported fields: {unsupported}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return {
            "source_sha256": optics.sha256(source),
            "destination_sha256": optics.sha256(destination),
            "source_type": "EFIELD",
            "preserved_source_verbatim": source.read_bytes() == destination.read_bytes(),
            "selected_element": "all source rows",
            "selected_row_count": len(records),
            "nonzero_supported_record_count": len(records),
            "nonzero_unsupported_fields": unsupported,
            "retained_components": "all source columns",
        }
    lines = source.read_text(encoding="utf-8").splitlines()
    columns: list[str] | None = None
    data_start: int | None = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("*"):
            columns = stripped.lstrip("*").split()
        elif stripped.startswith("$") and columns is not None:
            data_start = index + 1
            break
    if columns is None or data_start is None:
        raise RuntimeError(f"Survey error table is missing TFS columns: {source}")
    component_names = {"DX", "DY", "DS", "DPHI", "DTHETA", "DPSI"}
    keep_all_alignment = case.get("case_id") == "survey_error_table_verified_intersection"
    requested_component = str(case.get("component", "")).upper()
    element = str(case.get("element", "SP0_QF")).upper()
    if not keep_all_alignment and requested_component not in component_names:
        raise RuntimeError(f"Unsupported isolated EFIELD component for {case['case_id']}: {requested_component}")
    output = list(lines[:data_start])
    selected_rows = 0
    zeroed_fields: set[str] = set()
    for line in lines[data_start:]:
        stripped = line.strip()
        if not stripped or stripped.startswith(("@", "*", "$", "!")):
            output.append(line)
            continue
        spans = list(re.finditer(r"\S+", line))
        if len(spans) < len(columns):
            output.append(line)
            continue
        values = [match.group(0) for match in spans]
        name_index = columns.index("NAME")
        row_name = values[name_index].strip('"').split(":", 1)[0].upper()
        selected = row_name == element
        if selected:
            selected_rows += 1
        replacements: list[tuple[int, int, str]] = []
        for column_index, column in enumerate(columns):
            if column == "NAME":
                continue
            preserve = keep_all_alignment and column in component_names
            preserve = preserve or (not keep_all_alignment and selected and column == requested_component)
            if not preserve:
                value = float(values[column_index].replace("D", "E").replace("d", "e"))
                if value != 0.0:
                    zeroed_fields.add(column)
                replacements.append((spans[column_index].start(), spans[column_index].end(), "0.000000000000"))
            elif not keep_all_alignment and selected and column == requested_component:
                replacements.append((spans[column_index].start(), spans[column_index].end(), f"{float(case['value']):.12e}"))
        for start, end, replacement in reversed(replacements):
            line = line[:start] + replacement + line[end:]
        output.append(line)
    if not keep_all_alignment and selected_rows != 1:
        raise RuntimeError(f"Expected one {element} row in {source}, found {selected_rows}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(output) + "\n", encoding="utf-8")
    return {
        "source_sha256": optics.sha256(source),
        "source_type": "EFIELD",
        "retained_components": sorted(component_names if keep_all_alignment else {requested_component}),
        "zeroed_nonzero_columns": sorted(zeroed_fields),
        "selected_element": "all source rows" if keep_all_alignment else element,
        "selected_row_count": selected_rows,
        "destination_sha256": optics.sha256(destination),
    }


def run_madx_case_model(
    case: dict[str, Any],
    case_input: Path,
    case_dir: Path,
    accepted: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str], list[dict[str, str]], Path]:
    """Run case-local MAD-X TWISS and PTC flat-file generation from fresh inputs."""
    reference_dir = case_dir / "reference"
    reference_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir = reference_dir / "PTC_Scripts"
    scripts_dir.mkdir(exist_ok=True)
    basis_scripts = ADMISSION_BASIS / "madx_work/PTC_Scripts"
    shutil.copy2(basis_scripts / "resplit.ptc", scripts_dir / "resplit.ptc")
    print_script = (basis_scripts / "print_flat_file.ptc").read_text(encoding="utf-8")
    print_script = print_script.replace("PTC-PyORBIT_flat_file.flt", "case_flat_file.flt")
    (scripts_dir / "print_flat_file.ptc").write_text(print_script, encoding="utf-8")
    maxwellian = ADMISSION_BASIS / "madx_work/Maxwellian_bend_for_ptc.txt"
    if maxwellian.is_file():
        shutil.copy2(maxwellian, reference_dir / maxwellian.name)
    error_table = case_dir / str(case["error_table_path"]) if case.get("error_table_path") else None
    if error_table is not None:
        shutil.copy2(error_table, reference_dir / "case_error_table.tfs")
    tfs_path = reference_dir / "twiss.tfs"
    flat_file = reference_dir / "case_flat_file.flt"
    lines = [f'TITLE, "PyPTC case {case["case_id"]}";']
    for name in ("ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence"):
        lines.append(f'CALL, FILE="{(case_input / name).resolve()}";')
    lines.extend(("a1 := 0.0;", "b1 := 0.0;", "kqtd := 0.0;", "kqtf := 0.0;"))
    lines.extend(f"kqtd_{index} := 0.0;" for index in range(10))
    lines.extend(f"kqtf_{index} := 0.0;" for index in range(10))
    lines.append("USE, SEQUENCE=synchrotron;")
    if case.get("kind") == "field-error":
        lines.append(f"{case['element']}->{case['attribute']} := {case['element']}->{case['attribute']} * (1 + {float(case['relative_delta']):.17g});")
    lines.extend((
        "VALUE, a1;", "VALUE, b1;", "VALUE, kqtd;", "VALUE, kqtf;",
    ))
    lines.extend(f"VALUE, kqtd_{index};" for index in range(10))
    lines.extend(f"VALUE, kqtf_{index};" for index in range(10))
    if case.get("kind") == "field-error":
        lines.append(f"VALUE, {case['element']}->{case['attribute']};")
    lines.extend(("propagation_method=2; order_of_integrator=6; integration_steps_per_element=5;",))
    if error_table is None:
        lines.extend((
            "SELECT, FLAG=TWISS, CLEAR;",
            "SELECT, FLAG=TWISS, COLUMN=name, keyword, s, x, px, y, py, betx, bety, alfx, alfy, dx, dpx, dy, dpy, mux, muy;",
            f'TWISS, CHROM, SAVE, FILE="{tfs_path.resolve()}";',
        ))
    lines.extend((
        "ptc_create_universe;",
        "ptc_create_layout,time=true,model=propagation_method,exact=true,method=order_of_integrator,nst=integration_steps_per_element;",
        'ptc_script, file="PTC_Scripts/resplit.ptc";',
        'ptc_script, file="PTC_Scripts/print_flat_file.ptc";',
        "ptc_end;",
    ))
    if error_table is not None:
        lines.extend((
            "EOPTION, ADD=false;",
            'READMYTABLE, FILE="case_error_table.tfs", TABLE=efield;',
            "SETERR, TABLE=efield;",
            'ESAVE, FILE="applied_error_table.tfs";',
            "SELECT, FLAG=TWISS, CLEAR;",
            "SELECT, FLAG=TWISS, COLUMN=name, keyword, s, x, px, y, py, betx, bety, alfx, alfy, dx, dpx, dy, dpy, mux, muy;",
            f'TWISS, CHROM, SAVE, FILE="{tfs_path.resolve()}";',
        ))
    recipe_path = reference_dir / "reference_recipe.madx"
    recipe_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    binary = REPO_ROOT / "workflows/madx/bin/madx-linux64_v5_02_00"
    expected_hash = accepted["reference"].get("madx_binary_sha256", accepted["reference"].get("binary_sha256"))
    if not binary.is_file() or optics.sha256(binary) != expected_hash:
        raise RuntimeError("Pinned MAD-X 5.02.00 binary is absent or has a different SHA-256")
    log_path = reference_dir / "madx.log"
    with recipe_path.open(encoding="utf-8") as recipe, log_path.open("w", encoding="utf-8") as log:
        completed = subprocess.run([str(binary)], cwd=reference_dir, stdin=recipe, stdout=log, stderr=subprocess.STDOUT, text=True, check=False)
    if completed.returncode != 0 or not tfs_path.is_file() or not flat_file.is_file():
        raise RuntimeError(f"MAD-X case build failed for {case['case_id']} (exit {completed.returncode}); see {log_path}")
    headers, _columns, rows = optics.parse_tfs(tfs_path)
    info = {
        "command": [str(binary)], "binary_sha256": optics.sha256(binary),
        "recipe": str(recipe_path.relative_to(case_dir)), "recipe_sha256": optics.sha256(recipe_path),
        "log": str(log_path.relative_to(case_dir)), "log_sha256": optics.sha256(log_path),
        "tfs_sha256": optics.sha256(tfs_path), "flat_file": str(flat_file.relative_to(case_dir)),
        "flat_file_sha256": optics.sha256(flat_file),
        "input_hashes": {path.name: optics.sha256(path) for path in case_input.iterdir() if path.is_file()},
        "case_override": case.get("applied_input_override"),
        "error_table": str(error_table.relative_to(case_dir)) if error_table is not None else None,
        "error_table_sha256": optics.sha256(error_table) if error_table is not None else None,
        "applied_error_table_sha256": optics.sha256(reference_dir / "applied_error_table.tfs") if (reference_dir / "applied_error_table.tfs").is_file() else None,
        "rows": len(rows),
    }
    optics.write_json(case_dir / "reference/case_model.json", info)
    return info, headers, rows, flat_file


def run_harness_checks(run_dir: Path) -> dict[str, Any]:
    """Run the fresh iteration's independent deterministic fixtures."""
    log_path = run_dir / "harness-tests.log"
    command = [sys.executable, "-m", "unittest", "discover", "-s", str(STEP_DIR / "tests"), "-v"]
    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    log_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    return {
        "argv": command,
        "cwd": str(REPO_ROOT),
        "log": str(log_path.relative_to(run_dir)),
        "returncode": completed.returncode,
        "sha256": optics.sha256(log_path),
    }


def profile_capabilities(
    mapping_status: str,
    tracking_status: str,
    response_case_count: int = 0,
    unsupported_cases: list[str] | None = None,
    efield_case_status: str = "not-assessed",
) -> list[dict[str, Any]]:
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
        {"observable": "corrector, field-strength, isolated misalignment, and verified-intersection responses", "classification": "pending-tolerance" if response_case_count else "blocked", "reason": f"{response_case_count} case-specific fresh-state response records are available; tolerances and minimum meaningful-response floors remain unreviewed" if response_case_count else "no case-specific response records are available"},
        {"observable": "full EFIELD survey-table response", "classification": "unsupported" if unsupported_cases else efield_case_status, "reason": f"unexecuted unsupported full-table cases: {unsupported_cases}" if unsupported_cases else ("full-table nominal-subtracted response is retained; tolerance remains unreviewed" if efield_case_status == "pending-tolerance" else "full-table case has not completed in this run")},
    ]


def write_skill_composite(
    path: Path,
    aligned: list[dict[str, Any]],
    scalar_rows: list[dict[str, Any]],
    family_map: dict[str, str],
    family_summary: dict[str, Any],
    effective_recipe: str,
    mapping_summary: dict[str, Any],
    tracking_records: list[dict[str, Any]],
    case_id: str = "nominal",
    response_rows: list[dict[str, Any]] | None = None,
    scalar_response_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Render 3300x1600-pixel strips and stitch them into one case PNG."""
    if not aligned:
        raise ValueError("Cannot render a case composite without mapped profile samples")

    profile_fields = optics.PROFILE_FIELDS
    profile_titles = optics.PROFILE_TITLES
    family_colors = optics.FAMILY_COLORS
    sample_s = np.asarray([float(row["target_s_m"]) for row in aligned])
    reference_s = np.asarray([float(row["reference_s_m"]) for row in aligned])
    strips: list[Image.Image] = []
    panel_groups: list[dict[str, Any]] = []

    def render_strip(group_name: str, draw) -> None:
        figure = plt.figure(figsize=(8.25, 4.0), dpi=400)
        draw(figure)
        figure.subplots_adjust(left=0.10, right=0.98, top=0.84, bottom=0.15)
        buffer = io.BytesIO()
        figure.savefig(buffer, format="png", dpi=400)
        plt.close(figure)
        buffer.seek(0)
        with Image.open(buffer) as image_data:
            strip = image_data.convert("RGB")
        if strip.size != (3300, 1600):
            raise RuntimeError(f"Unexpected strip raster size {strip.size} for {group_name}")
        strips.append(strip)

    def magnet_strip(figure) -> None:
        axis = figure.add_subplot(111)
        for index, row in enumerate(aligned):
            start = 0.0 if index == 0 else float(aligned[index - 1]["reference_s_m"])
            end = float(row["reference_s_m"])
            name = str(row["element_name"])
            family = family_map.get(name, "unmapped")
            axis.axvspan(start, max(end, start + 1.0e-6), color=family_colors.get(family, family_colors["unmapped"]), linewidth=0)
        axis.set_xlim(float(reference_s[0]), float(reference_s[-1]))
        axis.set_yticks([])
        axis.set_xlabel("s [m]")
        axis.set_title(f"{case_id} magnet-family map — source classification from admitted ISIS lattice")
        axis.legend(handles=[Patch(facecolor=color, label=name) for name, color in family_colors.items() if name in set(family_map.values())], ncol=6, loc="upper center")

    render_strip("magnet_family_map", magnet_strip)
    panel_groups.append({"group": "magnet_family_map", "source": family_summary["source_files"], "classification": family_summary["rule"]})

    def working_point_strip(figure) -> None:
        axis = figure.add_subplot(111)
        axis.axis("off")
        by_name = {row["observable"]: row for row in scalar_rows}
        table_rows = [["Observable", "MAD-X", "PyPTC", "Target − reference", "Units / status"]]
        for label, key in (
            ("Bare horizontal tune", "bare_horizontal_tune"),
            ("Bare vertical tune", "bare_vertical_tune"),
            ("Bare horizontal chromaticity", "bare_horizontal_chromaticity"),
            ("Bare vertical chromaticity", "bare_vertical_chromaticity"),
        ):
            row = by_name[key]
            if "reference" in row:
                table_rows.append([label, f"{row['reference']:.9g}", f"{row['target']:.9g}", f"{row['signed_target_minus_reference']:+.4g}", row["units"]])
            else:
                table_rows.append([label, f"{row.get('reference_native'):.9g}", f"{row.get('target_native'):.9g}", f"{row.get('signed_native_difference'):+.4g}", "native; conversion blocked"])
        circumference = by_name["circumference"]
        table_rows.append(["Circumference", f"{circumference['reference']:.9g}", f"{circumference['target']:.9g}", f"{circumference['signed_target_minus_reference']:+.4g}", "m"])
        table = axis.table(cellText=table_rows[1:], colLabels=table_rows[0], colWidths=[0.27, 0.14, 0.14, 0.18, 0.27], cellLoc="center", bbox=[0.02, 0.22, 0.96, 0.65])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        axis.text(0.02, 0.13, f"Recipe: {effective_recipe}; mapped boundaries={mapping_summary['mapped_boundaries']}; mapping={mapping_summary['status']}; no physics acceptance.", transform=axis.transAxes, fontsize=7, va="center")
        axis.set_title("Bare working-point table")

    render_strip("bare_working_point", working_point_strip)
    panel_groups.append({"group": "bare_working_point", "data": f"cases/{case_id}/scalar_comparisons.csv", "recipe": effective_recipe, "mapping": mapping_summary["status"]})

    if scalar_response_rows:
        def draw_scalar_responses(figure) -> None:
            axis = figure.add_subplot(111)
            axis.axis("off")
            headers = ["Observable", "MAD-X response", "PyPTC response", "Response residual", "Units/status"]
            cells = [[
                row["observable"], f"{float(row['reference_response']):+.5g}",
                f"{float(row['target_response']):+.5g}",
                "blocked" if row["response_residual"] is None else f"{float(row['response_residual']):+.5g}",
                row["units"],
            ] for row in scalar_response_rows]
            table = axis.table(cellText=cells, colLabels=headers, colWidths=[0.23, 0.18, 0.18, 0.18, 0.23], cellLoc="center", bbox=[0.01, 0.13, 0.98, 0.78])
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            axis.set_title(f"{case_id} nominal-subtracted scalar responses; chromaticity remains native and blocked")
        render_strip("nominal_subtracted_scalar_responses", draw_scalar_responses)
        panel_groups.append({"group": "nominal_subtracted_scalar_responses", "data": f"cases/{case_id}/scalar_response_metrics.csv", "classification": "tune/circumference differences pending tolerance; native chromaticity responses blocked"})

    overview_fields = ("betx", "bety", "dx", "dy", "x", "y")
    for observable in overview_fields:
        unit = profile_fields[observable][2]
        title = profile_titles[observable]

        def draw_overview(figure, field=observable, field_unit=unit, field_title=title) -> None:
            axis = figure.add_subplot(111)
            ref = np.asarray([float(row[f"reference_{field}"]) for row in aligned])
            target = np.asarray([float(row[f"target_{field}"]) for row in aligned])
            axis.plot(reference_s, ref, linestyle="none", marker=".", markersize=2.5, label="MAD-X reference")
            axis.plot(sample_s, target, linestyle="none", marker="x", markersize=2.5, label="PyPTC target")
            axis.set_title(f"{case_id} overview: {field_title}")
            axis.set_xlabel("verified mapped s [m]")
            axis.set_ylabel(f"[{field_unit}]")
            axis.grid(alpha=0.2)
            axis.legend(loc="best")

        render_strip(f"nominal_overview_{observable}", draw_overview)
        panel_groups.append({"group": f"case_overview_{observable}", "observable": observable, "units": unit, "data": f"cases/{case_id}/aligned_profiles.csv", "mapping": mapping_summary["status"], "series": ["MAD-X reference", "PyPTC target"]})

    for observable, (_target_field, _reference_field, unit) in profile_fields.items():
        title = profile_titles[observable]

        def draw_profile(figure, field=observable, field_unit=unit, field_title=title) -> None:
            grid = figure.add_gridspec(2, 1, height_ratios=(2, 1), hspace=0.12)
            overlay = figure.add_subplot(grid[0])
            residual = figure.add_subplot(grid[1], sharex=overlay)
            reference = np.asarray([float(row[f"reference_{field}"]) for row in aligned])
            target = np.asarray([float(row[f"target_{field}"]) for row in aligned])
            overlay.plot(reference_s, reference, linestyle="none", marker=".", markersize=2.2, label="MAD-X reference")
            overlay.plot(sample_s, target, linestyle="none", marker="x", markersize=2.2, label="PyPTC target")
            overlay.set_title(f"{field_title} overlay — {field_unit}")
            overlay.set_ylabel(f"[{field_unit}]")
            overlay.grid(alpha=0.2)
            overlay.legend(loc="best")
            overlay.tick_params(axis="x", labelbottom=False)
            residual.plot(sample_s, target - reference, linestyle="none", marker=".", markersize=2.0, color="#7b3294")
            residual.axhline(0.0, color="black", linewidth=0.6)
            residual.set_xlabel("verified mapped s [m]")
            residual.set_ylabel(f"target−ref\n[{field_unit}]")
            residual.grid(alpha=0.2)

        render_strip(f"profile_{observable}", draw_profile)
        panel_groups.append({"group": f"profile_{observable}", "observable": observable, "units": unit, "data": f"cases/{case_id}/aligned_profiles.csv", "mapping": mapping_summary["status"], "signed_residual": "PyPTC target - MAD-X reference", "scaling": "independent overlay and residual axes"})

    if response_rows:
        def draw_responses(figure) -> None:
            grid = figure.add_gridspec(2, 1, hspace=0.5)
            for index, plane in enumerate(("x", "y")):
                axis = figure.add_subplot(grid[index])
                axis.plot([float(row["reference_s_m"]) for row in response_rows], [float(row[f"reference_response_{plane}"]) for row in response_rows], marker=".", linestyle="none", label="MAD-X response")
                axis.plot([float(row["target_s_m"]) for row in response_rows], [float(row[f"target_response_{plane}"]) for row in response_rows], marker="x", linestyle="none", label="PyPTC response")
                axis.set_title(f"{case_id} nominal-subtracted orbit response {plane}")
                axis.set_xlabel("verified mapped s [m]")
                axis.set_ylabel("response [m]")
                axis.grid(alpha=0.2)
                axis.legend(loc="best")
        render_strip("nominal_subtracted_orbit_response", draw_responses)
        panel_groups.append({"group": "nominal_subtracted_orbit_response", "data": f"cases/{case_id}/response_profiles.csv", "observable": "x/y orbit", "definition": "perturbed minus nominal separately for MAD-X and PyPTC"})

    if tracking_records:
        def draw_tracking(figure) -> None:
            grid = figure.add_gridspec(2, 1, hspace=0.55)
            for index, observable in enumerate(("x", "y")):
                axis = figure.add_subplot(grid[index])
                rows = [row for row in tracking_records if row["observable"] == observable]
                axis.plot([int(row["turn"]) for row in rows], [float(row["reference"]) for row in rows], marker=".", linestyle="none", label="MAD-X reference")
                axis.plot([int(row["turn"]) for row in rows], [float(row["target"]) for row in rows], marker="x", linestyle="none", label="PyPTC target")
                axis.set_title(f"Bounded tracking coordinate {observable} versus turn")
                axis.set_xlabel("" if index == 0 else "turn")
                axis.set_ylabel("position [m]")
                axis.grid(alpha=0.2)
                axis.legend(loc="best")
                if index == 0:
                    axis.tick_params(axis="x", labelbottom=False)

        render_strip("tracking_coordinates_vs_turn", draw_tracking)
        panel_groups.append({"group": "tracking_coordinates_vs_turn", "data": f"cases/{case_id}/turn_comparisons.csv", "units": "m", "observation_point": "sequence start", "phase_space_plot_status": "unavailable; retained comparison table contains x/y but no momentum coordinates"})

    path.parent.mkdir(parents=True, exist_ok=True)
    width = 3300
    height = 1600 * len(strips)
    composite = Image.new("RGB", (width, height), "white")
    for index, strip in enumerate(strips):
        composite.paste(strip, (0, index * 1600))
    composite.save(path, format="PNG")
    composite.close()
    for strip in strips:
        strip.close()
    return {
        "case": case_id,
        "artifact": str(path),
        "sha256": optics.sha256(path),
        "case_file_count": 1,
        "strip_count": len(panel_groups),
        "strip_dimensions_px": [3300, 1600],
        "raster_dimensions_px": [width, height],
        "dpi": 400,
        "sample_count": len(aligned),
        "panel_groups": panel_groups,
        "visually_inspected_at_normal_size": False,
    }


def nominal_subtracted_responses(
    nominal_aligned: list[dict[str, Any]],
    perturbed_aligned: list[dict[str, Any]],
    case_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Join independently aligned profiles and calculate engine-specific responses."""
    def key(row: dict[str, Any]) -> tuple[str, int, int]:
        return (str(row["element_name"]), int(row["element_occurrence"]), int(row["fibre_index"]))

    nominal_by_key = {key(row): row for row in nominal_aligned}
    response_rows: list[dict[str, Any]] = []
    for perturbed in perturbed_aligned:
        identity = key(perturbed)
        if identity not in nominal_by_key:
            raise RuntimeError(f"Case {case_id} mapping has no nominal boundary for {identity}")
        nominal = nominal_by_key[identity]
        row: dict[str, Any] = {
            "case_id": case_id,
            "element_name": identity[0],
            "occurrence": identity[1],
            "fibre_index": identity[2],
            "reference_s_m": float(perturbed["reference_s_m"]),
            "target_s_m": float(perturbed["target_s_m"]),
        }
        for observable in optics.PROFILE_FIELDS:
            for engine in ("reference", "target"):
                field = f"{engine}_{observable}"
                row[f"nominal_{field}"] = float(nominal[field])
                row[f"perturbed_{field}"] = float(perturbed[field])
                row[f"{engine}_response_{observable}"] = float(perturbed[field]) - float(nominal[field])
            row[f"response_residual_{observable}"] = row[f"target_response_{observable}"] - row[f"reference_response_{observable}"]
        response_rows.append(row)
    metrics: list[dict[str, Any]] = []
    for observable, (_target, _reference, units) in optics.PROFILE_FIELDS.items():
        reference = np.asarray([row[f"reference_response_{observable}"] for row in response_rows], dtype=float)
        target = np.asarray([row[f"target_response_{observable}"] for row in response_rows], dtype=float)
        residual = target - reference
        metrics.append({
            "case_id": case_id,
            "observable": observable,
            "units": units,
            "response_definition": "perturbed minus nominal, with each engine subtracted independently after verified element-exit mapping",
            "sample_count": int(len(residual)),
            "reference_response_rms": float(np.sqrt(np.mean(reference ** 2))),
            "target_response_rms": float(np.sqrt(np.mean(target ** 2))),
            "maximum_absolute_response_residual": float(np.max(np.abs(residual))),
            "rms_response_residual": float(np.sqrt(np.mean(residual ** 2))),
            "minimum_meaningful_response": None,
            "agreement_tolerance": None,
            "classification": "pending-tolerance; response floors not reviewed",
        })
    return response_rows, metrics


def nominal_subtracted_scalar_responses(
    nominal_rows: list[dict[str, Any]],
    perturbed_rows: list[dict[str, Any]],
    case_id: str,
) -> list[dict[str, Any]]:
    """Calculate per-engine scalar responses without converting native chromaticity."""
    nominal_by_name = {str(row["observable"]): row for row in nominal_rows}
    out: list[dict[str, Any]] = []
    for perturbed in perturbed_rows:
        observable = str(perturbed["observable"])
        nominal = nominal_by_name.get(observable)
        if nominal is None:
            continue
        if "reference" in nominal and "reference" in perturbed:
            reference_nominal = float(nominal["reference"])
            reference_perturbed = float(perturbed["reference"])
            target_nominal = float(nominal["target"])
            target_perturbed = float(perturbed["target"])
            units = str(perturbed["units"])
            classification = "pending-tolerance"
        elif "reference_native" in nominal and "reference_native" in perturbed:
            reference_nominal = float(nominal["reference_native"])
            reference_perturbed = float(perturbed["reference_native"])
            target_nominal = float(nominal["target_native"])
            target_perturbed = float(perturbed["target_native"])
            units = "native derivative response; cross-code coordinate unresolved"
            classification = "blocked; native chromaticity coordinate unresolved"
        else:
            continue
        reference_response = reference_perturbed - reference_nominal
        target_response = target_perturbed - target_nominal
        residual = target_response - reference_response if classification == "pending-tolerance" else None
        out.append({
            "case_id": case_id,
            "observable": observable,
            "units": units,
            "reference_nominal": reference_nominal,
            "reference_perturbed": reference_perturbed,
            "reference_response": reference_response,
            "target_nominal": target_nominal,
            "target_perturbed": target_perturbed,
            "target_response": target_response,
            "response_residual": residual,
            "classification": classification,
        })
    return out


def run_perturbation_case(
    case: dict[str, Any],
    snapshot: Path,
    library: Path,
    accepted: dict[str, Any],
    run_dir: Path,
    nominal_aligned: list[dict[str, Any]],
    nominal_scalar_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run one included case in isolated MAD-X and PyPTC processes and save its plot."""
    case_id = str(case["case_id"])
    case_dir = run_dir / "cases" / case_id
    try:
        case_input = materialize_case_input(snapshot, case, case_dir)
        optics.write_json(case_dir / "case.json", case)
        madx_info, headers, reference_rows, case_flat_file = run_madx_case_model(case, case_input, case_dir, accepted)
        target_dir = case_dir / "target"
        error_table = case_dir / str(case["error_table_path"]) if case.get("error_table_path") else None
        target_info, target_rows, fibres, node_groups = optics.run_pyptc_optics(REPO_ROOT, case_flat_file, library, target_dir, error_table=error_table)
        mapping_rows, mapping_summary = optics.build_verified_boundary_map(reference_rows, target_rows, fibres, node_groups)
        optics.write_csv(case_dir / "boundary_map.csv", mapping_rows)
        beta0 = float(np.sqrt(1.0 - float(headers["GAMMA"]) ** -2))
        aligned, profile_metrics = optics.align_profiles(mapping_rows, reference_rows, target_rows, beta0) if mapping_summary["status"] == "verified" else ([], [])
        optics.write_csv(case_dir / "aligned_profiles.csv", aligned)
        optics.write_csv(case_dir / "profile_residual_metrics.csv", profile_metrics)
        scalar_rows, chromaticity_info = optics.scalar_comparisons(headers, target_info, mapping_summary)
        optics.write_csv(case_dir / "scalar_comparisons.csv", scalar_rows)
        response_rows, response_metrics = nominal_subtracted_responses(nominal_aligned, aligned, case_id) if mapping_summary["status"] == "verified" else ([], [])
        optics.write_csv(case_dir / "response_profiles.csv", response_rows)
        optics.write_csv(case_dir / "response_metrics.csv", response_metrics)
        scalar_response_rows = nominal_subtracted_scalar_responses(nominal_scalar_rows, scalar_rows, case_id)
        optics.write_csv(case_dir / "scalar_response_metrics.csv", scalar_response_rows)
        family_map, family_summary = optics.classify_source_families(case_input, [str(row["element_name"]) for row in mapping_rows], reference_rows)
        optics.write_json(case_dir / "profile_mapping.json", mapping_summary)
        optics.write_json(case_dir / "magnet_family_classification.json", {"families": family_map, **family_summary})
        plot_info = None
        if mapping_summary["status"] == "verified":
            plot_path = run_dir / "plots/cases" / f"{case_id}.png"
            plot_info = write_skill_composite(
                plot_path, aligned, scalar_rows, family_map, family_summary,
                f"{case_id}; accepted overlay, zero harmonics/trims; synchrotron",
                mapping_summary, [], case_id=case_id, response_rows=response_rows,
                scalar_response_rows=scalar_response_rows,
            )
        status = {
            "case_id": case_id,
            "disposition": "included",
            "execution_status": "completed" if mapping_summary["status"] == "verified" else "executed-blocked-profile-mapping",
            "reason": None if mapping_summary["status"] == "verified" else "Both engines ran, but the case-specific element-exit mapping did not verify.",
            "reference_application_status": "executed; case-local MAD-X input and TWISS retained",
            "target_application_status": "executed; fresh PyPTC load of the case-local generated flat file",
            "plot_status": "produced" if plot_info else "not-produced; no verified mapping",
            "plot_path": f"plots/cases/{case_id}.png" if plot_info else None,
            "response_metrics": f"cases/{case_id}/response_metrics.csv",
            "scalar_response_metrics": f"cases/{case_id}/scalar_response_metrics.csv",
            "reference_model": madx_info,
            "target_model": {"flat_file": target_info["flat_file"], "flat_file_sha256": target_info["flat_file_sha256"], "executed_api_calls": target_info["executed_api_calls"], "error_table": target_info.get("error_table"), "applied_error_records": target_info.get("applied_error_records")},
            "chromaticity": chromaticity_info,
        }
        optics.write_json(case_dir / "case_status.json", status)
        return {"status": status, "plot": plot_info}
    except Exception as error:
        status = {
            "case_id": case_id,
            "disposition": "included",
            "execution_status": "failed",
            "reason": f"Case-specific execution failed: {type(error).__name__}: {error}",
            "reference_application_status": "see case-local MAD-X files if created",
            "target_application_status": "see case-local PyPTC files if created",
            "plot_status": "not-produced; case execution failed",
        }
        optics.write_json(case_dir / "case_status.json", status)
        return {"status": status, "plot": None}


def summarize_case_response_residuals(run_dir: Path, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize response residuals by perturbation family and observable."""
    records: list[dict[str, Any]] = []
    for case in cases:
        path = run_dir / "cases" / case["case_id"] / "response_metrics.csv"
        if case["disposition"] != "included" or not path.is_file():
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                records.append({**row, "family": case["family"]})
    summary: list[dict[str, Any]] = []
    families = sorted({str(row["family"]) for row in records})
    observables = sorted({str(row["observable"]) for row in records})
    for family in families:
        for observable in observables:
            members = [row for row in records if row["family"] == family and row["observable"] == observable]
            if not members:
                continue
            worst = max(members, key=lambda row: float(row["maximum_absolute_response_residual"]))
            summary.append({
                "family": family,
                "observable": observable,
                "units": worst["units"],
                "case_count": len({row["case_id"] for row in members}),
                "maximum_absolute_response_residual": max(float(row["maximum_absolute_response_residual"]) for row in members),
                "worst_case_id": worst["case_id"],
                "worst_case_rms_response_residual": float(worst["rms_response_residual"]),
                "classification": "pending-tolerance; response floors not reviewed",
            })
    optics.write_csv(run_dir / "response_summary.csv", summary)
    return summary


def summarize_scalar_response_residuals(run_dir: Path, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize comparable scalar response residuals, excluding blocked native chromaticity."""
    records: list[dict[str, Any]] = []
    for case in cases:
        path = run_dir / "cases" / case["case_id"] / "scalar_response_metrics.csv"
        if case["disposition"] != "included" or not path.is_file():
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row["response_residual"]:
                    records.append({**row, "family": case["family"]})
    summary: list[dict[str, Any]] = []
    for family in sorted({str(row["family"]) for row in records}):
        for observable in sorted({str(row["observable"]) for row in records}):
            members = [row for row in records if row["family"] == family and row["observable"] == observable]
            if not members:
                continue
            worst = max(members, key=lambda row: abs(float(row["response_residual"])))
            summary.append({
                "family": family,
                "observable": observable,
                "units": worst["units"],
                "case_count": len({row["case_id"] for row in members}),
                "maximum_absolute_response_residual": abs(float(worst["response_residual"])),
                "worst_case_id": worst["case_id"],
                "classification": "pending-tolerance",
            })
    optics.write_csv(run_dir / "scalar_response_summary.csv", summary)
    return summary


def run_attempt() -> Path:
    """Execute the fresh nominal optics application and write its evidence bundle."""
    accepted, snapshot, flat_file, library = load_admission_basis()
    provenance = verify_inputs(accepted, snapshot, flat_file, library)
    skill_file = SKILL_SNAPSHOT_DIR / "SKILL.md"
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
        "skill": {"name": "benchmark-code-against-isis-rcs-optics", "revision": PINNED_SKILL_REVISION, "base_commit": "f5293a3754dc8c4e9a6a4ba987603924b91949f3", "source_worktree_modified": True, "sha256": PINNED_SKILL_SHA256, "snapshot": str(skill_file.relative_to(STEP_DIR))},
        "target_repository": {"head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout.strip(), "worktree_status": subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout.splitlines()},
        "accepted_admission": {"attempt_id": ADMISSION_ID, "review_disposition": "accepted", "scope": "snapshot admission only; its original API-4 library remains preserved as admission evidence", "bundle_path": str(ADMISSION_BASIS.relative_to(STEP_DIR)), "result_sha256": optics.sha256(ADMISSION_BASIS / "result.json"), "report_sha256": optics.sha256(ADMISSION_BASIS / "report.md")},
        "target_code_under_test": {"source_revision": provenance["candidate_source_revision"], "api_level": provenance["candidate_api_level"], "library_path": str(library), "library_sha256": provenance["library_sha256"], "build_script": "build/build_ptc.sh"},
        "identities": provenance,
        "recipe": {"variant": "00_Simplified_Lattice with 2023.strength overlay", "sequence": "synchrotron", "reference_mode": "case-local working-copy snapshots", "ordered_inputs": ["ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence"], "a1": 0.0, "b1": 0.0, "kqtd": 0.0, "kqtf": 0.0, "all_individual_trim_variables": 0.0, "resplitting": "nominal uses accepted flat file; supported perturbations regenerate case-local flat files with the accepted resplit scripts", "tracking_mode": tracking_mode, "perturbation_cases": case_inventory["dispositions"]["included"][1:]},
        "campaign_case_inventory": {"path": "campaign_case_inventory.json", "case_count": case_inventory["case_count"], "dispositions": case_inventory["dispositions"]},
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
            plot_info = write_skill_composite(
                run_dir / "plots/cases/nominal.png", aligned, scalar_rows,
                family_map, family_summary,
                "accepted 2023.strength overlay; zero harmonics/trims; synchrotron",
                mapping_summary, tracking_records,
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
        case_inventory["cases"][0]["reference_application_status"] = "accepted base recipe executed; see cases/nominal/reference/"
        case_inventory["cases"][0]["target_application_status"] = "accepted base recipe executed; see cases/nominal/target/"

        plot_manifest_cases = {}
        if plot_info is not None:
            plot_manifest_cases["nominal"] = {"path": "plots/cases/nominal.png", **plot_info}
        case_run_summaries = []
        for case in case_inventory["cases"][1:]:
            if case["disposition"] != "included":
                continue
            result_for_case = run_perturbation_case(case, snapshot, library, accepted, run_dir, aligned, scalar_rows)
            case_run_summaries.append(result_for_case["status"])
            case["execution_status"] = result_for_case["status"]["execution_status"]
            case["reference_application_status"] = result_for_case["status"]["reference_application_status"]
            case["target_application_status"] = result_for_case["status"]["target_application_status"]
            case["plot_status"] = result_for_case["status"]["plot_status"]
            optics.write_json(run_dir / "cases" / case["case_id"] / "case.json", case)
            if result_for_case["plot"] is not None:
                plot_manifest_cases[case["case_id"]] = {"path": f"plots/cases/{case['case_id']}.png", **result_for_case["plot"]}
        case_inventory["executed_case_ids"] = ["nominal"] + [
            row["case_id"] for row in case_run_summaries
            if row["execution_status"].startswith("completed") or row["execution_status"].startswith("executed-")
        ]
        case_inventory["execution_summary"] = {
            "executed_case_ids": case_inventory["executed_case_ids"],
            "completed_case_ids": [row["case_id"] for row in case_run_summaries if row["execution_status"] == "completed"],
            "failed_case_ids": [row["case_id"] for row in case_run_summaries if row["execution_status"] == "failed"],
            "blocked_candidate_ids": case_inventory["dispositions"]["blocked"],
            "unsupported_candidate_ids": case_inventory["dispositions"]["unsupported"],
            "not_applicable_candidate_ids": case_inventory["dispositions"]["not-applicable"],
            "unexecuted_candidate_ids": [
                case["case_id"] for case in case_inventory["cases"]
                if case["disposition"] in {"blocked", "unsupported", "not-applicable"}
            ],
        }
        optics.write_json(run_dir / "campaign_case_inventory.json", case_inventory)
        efield_case = next(case for case in case_inventory["cases"] if case["case_id"] == "survey_error_table")
        efield_case_status = "pending-tolerance" if efield_case.get("execution_status") == "completed" else "blocked"
        capabilities = profile_capabilities(
            mapping_summary["status"], tracking_status,
            response_case_count=len(case_inventory["execution_summary"]["completed_case_ids"]),
            unsupported_cases=case_inventory["execution_summary"]["unsupported_candidate_ids"],
            efield_case_status=efield_case_status,
        )
        optics.write_json(run_dir / "cases/nominal/capability_matrix.json", capabilities)
        optics.write_json(run_dir / "plot-manifest.json", {
            "case_plot_count": len(plot_manifest_cases),
            "cases": plot_manifest_cases,
            "executed_case_ids": case_inventory["executed_case_ids"],
        })
        response_summary = summarize_case_response_residuals(run_dir, case_inventory["cases"])
        scalar_response_summary = summarize_scalar_response_residuals(run_dir, case_inventory["cases"])

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
            "response_summary": {"path": "response_summary.csv", "rows": len(response_summary)},
            "scalar_response_summary": {"path": "scalar_response_summary.csv", "rows": len(scalar_response_summary)},
            "scalar_comparisons": scalar_rows,
            "capability_matrix": "cases/nominal/capability_matrix.json",
            "plot_manifest": "plot-manifest.json",
            "magnet_family_classification": family_summary,
            "tolerance_policy": "No observable-specific tolerance has been reviewed for this PyPTC campaign; all completed differences are pending-tolerance.",
            "tracking": tracking_summary,
            "case_execution": {
                "nominal": nominal_case_status["execution_status"],
                "included_perturbations": case_inventory["execution_summary"],
                "unexecuted_candidates": case_inventory["execution_summary"]["unexecuted_candidate_ids"],
                "rule": "every included case is executed from fresh case-local inputs; blocked candidates retain candidate-specific technical evidence",
            },
        })
        failed_cases = case_inventory["execution_summary"]["failed_case_ids"]
        missing_case_plots = [
            case["case_id"] for case in case_inventory["cases"]
            if case["disposition"] == "included" and case.get("plot_status") != "produced"
        ]
        if mapping_summary["status"] != "verified":
            outcome = "blocked-profile-mapping"
        elif failed_cases or missing_case_plots:
            outcome = "incomplete-perturbation-execution"
        elif case_inventory["execution_summary"]["unexecuted_candidate_ids"]:
            outcome = "incomplete-perturbation-coverage"
        elif tracking_status != "complete":
            outcome = "blocked-bounded-tracking"
        else:
            outcome = "incomplete-chromaticity-and-plot-review"
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
            "executed_case_ids": case_inventory["executed_case_ids"],
            "completed_perturbation_cases": len(case_inventory["execution_summary"]["completed_case_ids"]),
            "failed_perturbation_cases": failed_cases,
            "non_nominal_cases_blocked": len(case_inventory["dispositions"]["blocked"]),
            "non_nominal_cases_unsupported": len(case_inventory["dispositions"]["unsupported"]),
            "unexecuted_candidate_ids": case_inventory["execution_summary"]["unexecuted_candidate_ids"],
            "response_summary": "response_summary.csv",
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
            f"This run uses the user-accepted admission snapshot `{ADMISSION_ID}`. Its accepted scope is snapshot admission only. The five accepted source inputs and flat file, and the MAD-X 5.02.00 binary, are reused by digest. PyPTC is rebuilt from current repository source at API level {provenance['candidate_api_level']} so the EFIELD API under test is available; its source revision and library digest are recorded separately. The effective recipe uses the five pinned inputs in admission order, the 2023 strength overlay, `synchrotron`, `a1=b1=0`, all trim variables zero, and the accepted flat file without resplitting for nominal optics.",
            "",
            "## Sampling and profile comparison",
            "",
            f"MAD-X returned {len(reference_rows)} named TWISS rows; PyPTC returned {len(target_rows)} orbit-node Twiss rows and {len(node_groups)} printer groups. The mapping status is `{mapping_summary['status']}` with {mapping_summary['mapped_boundaries']} matched element exits at a position tolerance of {optics.POSITION_TOLERANCE_M:g} m. Mapping method and every row identity are retained in `boundary_map.csv`.",
            "",
            f"Reference dispersion columns were multiplied by this run's beta0={beta0:.12g}, derived from the MAD-X TWISS GAMMA header. {len(profile_metrics)} profile residual summaries are retained. All remain `pending-tolerance`; no agreement or physics claim is made.",
            "",
            "## Chromaticity, tracking, and limitations",
            "",
            f"The machine-readable inventory assesses all {case_inventory['case_count']} candidates from the Xsuite attempt-029 cross-reference separately for PyPTC; the list is not treated as automatic case equivalence. {len(case_inventory['executed_case_ids'])} cases executed and were plotted: {', '.join(case_inventory['executed_case_ids'])}. Corrector, field-strength, isolated misalignment, verified-intersection, and full EFIELD survey-table cases use fresh case-local inputs and independent MAD-X/PyPTC application paths. Per-engine nominal-subtracted profile and scalar responses are retained. The full local survey table is applied unchanged; its exact source and all-field audit are retained with the case. The exact Xsuite attempt-029 EFIELD table remains unavailable, so its candidate is not claimed as byte-for-byte equivalent. Unexecuted candidates: {', '.join(case_inventory['execution_summary']['unexecuted_candidate_ids']) or 'none'}. Response tolerances remain pending review.",
            "",
            f"MAD-X 5.02.00 reports `DQ1/DQ2` as `dQ/dDELTAP`, equivalent to `dQ/d(delta_p)` with factor 1. The PyPTC native values are retained, but the public wrapper does not establish their derivative coordinate, so the cross-code chromaticity comparison is `blocked`: {chromaticity_info['planes']}.",
            "",
            f"Profile response residual envelopes are summarized by family and observable in `response_summary.csv`; scalar response envelopes are in `scalar_response_summary.csv`, and per-case data remain in each case's `response_metrics.csv` and `scalar_response_metrics.csv`. Corrector and field response tolerances and minimum meaningful-response floors have not been reviewed, so comparable response results are `pending-tolerance`. Chromaticity scalar responses remain native and blocked because the derivative coordinates are unresolved. Bounded tracking status is `{tracking_status}`. Requested mode: `{tracking_mode}`; the primary route is thick MAD-X `PTC_TRACK` against the PyPTC thick-lattice workflow. Both use the PTC tracking engine, so this is not an independent tracking-engine validation. The optional thin route is reference-only and separately classified because the ten-slice `MAKETHIN` diagnostic is unvalidated and no matching PyPTC thin control is established. Reference: `{reference_tracking.get('status')}`; target: `{target_tracking.get('status')}`. The plan uses {optics.TRACK_TURNS} turns from {optics.TRACK_INITIAL}; see `tracking_summary.json` for complete counts and the reason if blocked. No target-only or partial record is presented as a cross-code comparison. No nonlinear, long-term, collective-effects, clean-checkout admission, or production claim is made.",
            "",
            "MAD-X and PyPTC runtime warnings are retained in `reference/madx.log` and `target/pyptc_runtime.log`. They are observations, not silently discarded or interpreted as resolved.",
            "",
            "## Evidence files",
            "",
            "- `cases/<case-id>/` — isolated reference and target data, boundary map, aligned profiles, residuals, scalar results, and nominal-subtracted response records for each executed case.",
            "- `campaign_case_inventory.json` and `cases/<case-id>/{case.json,case_status.json}` — candidate identities, skill-valid dispositions, evidence-backed reasons, and per-engine application statuses.",
            "- `response_summary.csv` — maximum response residual by family and observable, with the worst-case ID; each case also retains detailed response values and residuals.",
            "- `scalar_response_summary.csv` — tune and circumference response residuals; native chromaticity responses remain blocked.",
            "- `plots/cases/<case-id>.png` — one composite for every included case with verified mapping; `plot-manifest.json` links executed cases to their PNGs.",
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
