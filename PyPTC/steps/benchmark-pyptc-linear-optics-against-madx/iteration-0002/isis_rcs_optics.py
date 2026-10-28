"""User-facing ISIS RCS optics actions for the PyPTC/MAD-X benchmark.

The public helpers in this module resolve the accepted machine state, calculate
MAD-X and PyPTC records, align element-exit samples by identity and occurrence,
and write the nominal case's composite review plot. MAD-X and PyPTC records are
kept in campaign-local output directories; this module does not alter lattice
strengths or the accepted resplitting policy.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Rectangle


POSITION_TOLERANCE_M = 1.0e-9
TRACK_TURNS = 64
TRACK_INITIAL = {"x_m": 1.0e-3, "xp_rad": 0.0, "y_m": 1.0e-3, "yp_rad": 0.0, "z_m": 0.0, "dE_gev": 0.0}
PROFILE_FIELDS = {
    "x": ("X", "orbitx", "m"),
    "px": ("PX", "orbitpx", "rad"),
    "y": ("Y", "orbity", "m"),
    "py": ("PY", "orbitpy", "rad"),
    "betx": ("BETX", "betax", "m"),
    "bety": ("BETY", "betay", "m"),
    "alfx": ("ALFX", "alphax", "1"),
    "alfy": ("ALFY", "alphay", "1"),
    "dx": ("DX", "etax", "m"),
    "dpx": ("DPX", "etapx", "1"),
    "dy": ("DY", "etay", "m"),
    "dpy": ("DPY", "etapy", "1"),
    "mux": ("MUX", "mux", "turns"),
    "muy": ("MUY", "muy", "turns"),
}
PROFILE_TITLES = {
    "x": "Horizontal orbit",
    "px": "Horizontal slope",
    "y": "Vertical orbit",
    "py": "Vertical slope",
    "betx": "Horizontal beta",
    "bety": "Vertical beta",
    "alfx": "Horizontal alpha",
    "alfy": "Vertical alpha",
    "dx": "Horizontal dispersion",
    "dpx": "Horizontal dispersion derivative",
    "dy": "Vertical dispersion",
    "dpy": "Vertical dispersion derivative",
    "mux": "Horizontal phase advance",
    "muy": "Vertical phase advance",
}
FAMILY_COLORS = {
    "main dipoles": "#f0cf45",
    "main quadrupoles": "#176b3a",
    "trim quadrupoles": "#d62728",
    "drifts": "#f4f4ef",
    "other bends": "#8c6bb1",
    "other elements": "#4c9daf",
    "unmapped": "#bdbdbd",
}


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of a file, reading it in bounded chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    """Write stable, indented JSON to a campaign artifact path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write dictionaries with a stable union of keys as a CSV artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_tfs(path: Path) -> tuple[dict[str, str], list[str], list[dict[str, str]]]:
    """Parse MAD-X TFS headers, column names, and element rows."""
    headers: dict[str, str] = {}
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("@"):
            parts = shlex.split(stripped)
            if len(parts) >= 4:
                headers[parts[1].upper()] = parts[3]
        elif stripped.startswith("*"):
            columns = stripped[1:].split()
        elif stripped.startswith('"') and columns:
            values = shlex.split(stripped)
            if len(values) == len(columns):
                rows.append(dict(zip(columns, values)))
    if not rows or "NAME" not in columns or "S" not in columns:
        raise RuntimeError(f"TFS file has no named element rows: {path}")
    return headers, columns, rows


def make_reference_recipe(input_dir: Path, tfs_path: Path) -> str:
    """Return the unperturbed MAD-X recipe matching accepted admission inputs."""
    ordered_inputs = (
        "ISIS.injected_beam",
        "ISIS.elements",
        "ISIS.strength",
        "2023.strength",
        "ISIS.sequence",
    )
    lines = ['TITLE, "PyPTC iteration 0002 optics benchmark";']
    lines.extend(f'CALL, FILE="{(input_dir / name).resolve()}";' for name in ordered_inputs)
    lines.extend((
        "a1 := 0.0;",
        "b1 := 0.0;",
        "kqtd := 0.0;",
        "kqtf := 0.0;",
    ))
    lines.extend(f"kqtd_{index} := 0.0;" for index in range(10))
    lines.extend(f"kqtf_{index} := 0.0;" for index in range(10))
    lines.extend((
        "USE, SEQUENCE=synchrotron;",
        "VALUE, a1;",
        "VALUE, b1;",
        "VALUE, kqtd;",
        "VALUE, kqtf;",
    ))
    lines.extend(f"VALUE, kqtd_{index};" for index in range(10))
    lines.extend(f"VALUE, kqtf_{index};" for index in range(10))
    lines.extend((
        "SELECT, FLAG=TWISS, CLEAR;",
        "SELECT, FLAG=TWISS, COLUMN=name, keyword, s, x, px, y, py, betx, bety, alfx, alfy, dx, dpx, dy, dpy, mux, muy;",
        f'TWISS, CHROM, SAVE, FILE="{tfs_path.resolve()}";',
    ))
    return "\n".join(lines) + "\n"


def run_madx_reference(
    repo_root: Path,
    input_dir: Path,
    reference_dir: Path,
    accepted_result: dict[str, Any],
) -> tuple[Path, dict[str, Any], dict[str, str], list[dict[str, str]]]:
    """Run pinned MAD-X on the accepted input closure and retain TFS and log."""
    reference_dir.mkdir(parents=True, exist_ok=True)
    binary = repo_root / "workflows/madx/bin/madx-linux64_v5_02_00"
    expected_hash = accepted_result["reference"].get("madx_binary_sha256", accepted_result["reference"].get("binary_sha256"))
    if not binary.is_file() or sha256(binary) != expected_hash:
        raise RuntimeError("Pinned MAD-X 5.02.00 binary is absent or has a different SHA-256")
    tfs_path = reference_dir / "twiss.tfs"
    recipe_path = reference_dir / "reference_recipe.madx"
    log_path = reference_dir / "madx.log"
    recipe_path.write_text(make_reference_recipe(input_dir, tfs_path), encoding="utf-8")
    with recipe_path.open("r", encoding="utf-8") as recipe, log_path.open("w", encoding="utf-8") as log:
        completed = subprocess.run(
            [str(binary)], cwd=reference_dir, stdin=recipe, stdout=log,
            stderr=subprocess.STDOUT, text=True, check=False,
        )
    if completed.returncode != 0 or not tfs_path.is_file():
        raise RuntimeError(f"MAD-X failed with exit code {completed.returncode}; inspect {log_path}")
    headers, columns, rows = parse_tfs(tfs_path)
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    effective: dict[str, float] = {}
    for variable in ("a1", "b1", "kqtd", "kqtf", *(f"kqtd_{i}" for i in range(10)), *(f"kqtf_{i}" for i in range(10))):
        matches = re.findall(rf"(?im)^\s*{re.escape(variable)}\s*=\s*([-+0-9.eEdD]+)", log_text)
        if not matches:
            raise RuntimeError(f"MAD-X log has no effective-value record for {variable}")
        effective[variable] = float(matches[-1].replace("D", "E").replace("d", "e"))
    if any(abs(value) > 1.0e-12 for value in effective.values()):
        raise RuntimeError(f"Effective harmonics/trims are not all zero: {effective}")
    gamma = float(headers["GAMMA"])
    beta0 = float(np.sqrt(1.0 - gamma ** -2))
    warnings = [line.strip() for line in log_text.splitlines() if re.search(r"\bwarning:", line, re.IGNORECASE)]
    summary = {
        "version": headers.get("ORIGIN", "unknown"),
        "command": [str(binary)],
        "working_directory": str(reference_dir),
        "binary_path": str(binary),
        "binary_sha256": sha256(binary),
        "recipe": recipe_path.name,
        "recipe_sha256": sha256(recipe_path),
        "log": log_path.name,
        "log_sha256": sha256(log_path),
        "tfs": tfs_path.name,
        "tfs_sha256": sha256(tfs_path),
        "ordered_inputs": [name for name in ("ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence")],
        "effective_harmonic_and_trim_settings": effective,
        "sequence": headers.get("SEQUENCE", "synchrotron"),
        "twiss_option": "TWISS, CHROM at nominal DELTAP=0",
        "chromaticity_native_definition": "MAD-X 5.02.00 DQ1/DQ2 = dQ/dDELTAP",
        "chromaticity_finite_difference_step": 1.0e-6,
        "reference_gamma": gamma,
        "beta0_from_this_TWISS": beta0,
        "dispersion_conversion": "MAD-X DX, DPX, DY, DPY multiplied by beta0 from this TWISS GAMMA",
        "columns": columns,
        "rows": len(rows),
        "headers": headers,
        "warnings": warnings,
        "ignored_implicit_redefinitions": sum("implicit element re-definition ignored" in line.lower() for line in warnings),
    }
    return tfs_path, summary, headers, rows


def parse_madx_tracking(path: Path) -> list[dict[str, Any]]:
    """Parse the MAD-X one-particle observation file into turn rows."""
    columns: list[str] = []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("*"):
            columns = stripped[1:].split()
        elif stripped.startswith(("@", "$")) or not columns or not stripped:
            continue
        else:
            values = shlex.split(stripped)
            if len(values) != len(columns):
                continue
            record = dict(zip(columns, values))
            try:
                rows.append({key.upper(): float(value.replace("D", "E").replace("d", "e")) for key, value in record.items()})
            except ValueError:
                continue
    if not rows:
        raise RuntimeError(f"MAD-X tracking file contains no records: {path}")
    return rows


def run_madx_tracking(
    repo_root: Path,
    input_dir: Path,
    tracking_dir: Path,
    accepted_result: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run a bounded MAD-X reference track with a recorded thin-lens recipe."""
    tracking_dir.mkdir(parents=True, exist_ok=True)
    binary = repo_root / "workflows/madx/bin/madx-linux64_v5_02_00"
    expected_hash = accepted_result["reference"].get("madx_binary_sha256", accepted_result["reference"].get("binary_sha256"))
    if not binary.is_file() or sha256(binary) != expected_hash:
        return {"status": "blocked-reference-engine-identity", "reason": "Pinned MAD-X executable is absent or hash-mismatched."}, []
    recipe_path = tracking_dir / "tracking_recipe.madx"
    track_file_base = tracking_dir / "track"
    lines = ['TITLE, "Bounded nominal tracking cross-check";']
    ordered_inputs = ("ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence")
    lines.extend(f'CALL, FILE="{(input_dir / name).resolve()}";' for name in ordered_inputs)
    lines.extend(("a1 := 0.0;", "b1 := 0.0;", "kqtd := 0.0;", "kqtf := 0.0;"))
    lines.extend(f"kqtd_{i} := 0.0;" for i in range(10))
    lines.extend(f"kqtf_{i} := 0.0;" for i in range(10))
    lines.extend((
        "MAKETHIN, SEQUENCE=synchrotron, STYLE=TEAPOT;",
        "USE, SEQUENCE=synchrotron;",
        f'TRACK, ONEPASS, DUMP, FILE="{track_file_base}";',
        f"START, X={TRACK_INITIAL['x_m']}, PX={TRACK_INITIAL['xp_rad']}, Y={TRACK_INITIAL['y_m']}, PY={TRACK_INITIAL['yp_rad']}, T={TRACK_INITIAL['z_m']}, PT={TRACK_INITIAL['dE_gev']};",
        f"RUN, TURNS={TRACK_TURNS};",
        "ENDTRACK;",
    ))
    recipe_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log_path = tracking_dir / "madx_tracking.log"
    command = [str(binary)]
    with recipe_path.open("r", encoding="utf-8") as recipe, log_path.open("w", encoding="utf-8") as log:
        completed = subprocess.run(command, cwd=tracking_dir, stdin=recipe, stdout=log, stderr=subprocess.STDOUT, text=True, check=False)
    candidates = sorted(tracking_dir.glob("track.obs*.p0001"))
    base_summary = {
        "command": command,
        "working_directory": str(tracking_dir),
        "binary_sha256": sha256(binary),
        "recipe": recipe_path.name,
        "recipe_sha256": sha256(recipe_path),
        "log": log_path.name,
        "log_sha256": sha256(log_path),
        "integration_recipe": "MAD-X 5.02.00 MAKETHIN STYLE=TEAPOT; TRACK ONEPASS DUMP",
        "observation_point": "sequence start, the automatic DUMP observation when no OBSERVE command is given",
        "initial_coordinates": TRACK_INITIAL,
        "requested_turns": TRACK_TURNS,
        "track_files": [path.name for path in candidates],
        "returncode": completed.returncode,
    }
    if completed.returncode != 0 or not candidates:
        return {**base_summary, "status": "blocked-reference-engine-setup-failure", "reason": "MAD-X did not produce its one-particle DUMP observation file; inspect the retained recipe and log."}, []
    try:
        rows = parse_madx_tracking(candidates[0])
    except Exception as error:
        return {**base_summary, "status": "blocked-reference-record-parse", "reason": str(error)}, []
    expected_samples = TRACK_TURNS + 1
    turn_key = "TURN" if "TURN" in rows[0] else None
    turns = sorted({int(round(row[turn_key])) for row in rows}) if turn_key else []
    finite = all(np.isfinite(value) for row in rows for value in row.values())
    complete = len(rows) == expected_samples and turns and turns[0] == 0 and turns[-1] == TRACK_TURNS and finite
    return {
        **base_summary,
        "status": "complete" if complete else "blocked-reference-nonfinite" if not finite else "blocked-reference-record-truncated",
        "retained_samples": len(rows),
        "sample_count_convention": "includes initial turn-0 row and one row per completed turn",
        "turn_values": turns,
        "expected_samples": expected_samples,
        "finite": finite,
        "reason": None if complete else "MAD-X observations are non-finite." if not finite else "MAD-X observation record does not contain the declared initial-plus-completed-turn sample count.",
    }, rows


def run_pyptc_tracking(
    repo_root: Path,
    flat_file: Path,
    library: Path,
    tracking_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, float]]]:
    """Run independent PyPTC history and loss workers from the same fresh state."""
    tracking_dir.mkdir(parents=True, exist_ok=True)
    history_dir = tracking_dir / "history"
    loss_dir = tracking_dir / "loss_check"
    history_dir.mkdir()
    loss_dir.mkdir()
    from pyptc.lattice import read_flatfile_fibres

    fibres = read_flatfile_fibres(flat_file)
    marker_text = "SETORBITMARKER\n" + str(len(set(fibre.name for fibre in fibres))) + "\n" + "\n".join(dict.fromkeys(fibre.name for fibre in fibres)) + "\nreturn\n"
    maxwellian = flat_file.parent / "Maxwellian_bend_for_ptc.txt"
    for work_dir in (history_dir, loss_dir):
        (work_dir / "pre_orbit_set.txt").write_text(marker_text, encoding="utf-8")
        if maxwellian.is_file():
            shutil.copy2(maxwellian, work_dir / maxwellian.name)
    worker = Path(__file__).with_name("ptc_tracking_worker.py")
    initial = [TRACK_INITIAL["x_m"], TRACK_INITIAL["xp_rad"], TRACK_INITIAL["y_m"], TRACK_INITIAL["yp_rad"], TRACK_INITIAL["z_m"], TRACK_INITIAL["dE_gev"]]
    mode_summaries: dict[str, Any] = {}
    for mode, work_dir in (("history", history_dir), ("loss", loss_dir)):
        summary_path = work_dir / "tracking_summary.json"
        history_path = work_dir / "turn_history.csv"
        command = [sys.executable, str(worker), mode, str(repo_root), str(flat_file), str(library), json.dumps(initial), str(TRACK_TURNS), str(summary_path), str(history_path)]
        log_path = work_dir / "pyptc_tracking.log"
        with log_path.open("w", encoding="utf-8") as log:
            completed = subprocess.run(command, cwd=work_dir, stdout=log, stderr=subprocess.STDOUT, text=True, check=False)
        if completed.returncode != 0 or not summary_path.is_file():
            mode_summaries[mode] = {"status": "blocked-target-runtime-failure", "returncode": completed.returncode, "log": str(log_path.relative_to(tracking_dir)), "sha256": sha256(log_path)}
            continue
        mode_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        mode_summary.update({"command": command, "working_directory": str(work_dir), "log": str(log_path.relative_to(tracking_dir)), "log_sha256": sha256(log_path)})
        mode_summaries[mode] = mode_summary
    history_rows: list[dict[str, float]] = []
    history_path = history_dir / "turn_history.csv"
    if history_path.is_file():
        with history_path.open(newline="", encoding="utf-8") as handle:
            history_rows = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(handle)]
    count_ok = len(history_rows) == TRACK_TURNS + 1 and bool(history_rows) and int(history_rows[-1]["turn"]) == TRACK_TURNS
    finite = all(np.isfinite(value) for row in history_rows for value in row.values())
    loss_summary = mode_summaries.get("loss", {})
    history_summary = mode_summaries.get("history", {})
    loss_record = loss_summary.get("loss", {})
    loss_free = loss_summary.get("status") == "complete" and not bool(loss_record.get("lost", True))
    status = "complete" if count_ok and finite and loss_free else "blocked"
    summary = {
        "status": status,
        "modes": mode_summaries,
        "initial_conditions": TRACK_INITIAL,
        "coordinate_convention": "PyPTC track_bunch public rows [x, xp, y, yp, z, dE]; target start point is the ring sequence start and offsets are relative to the accepted reference particle",
        "observation_point": "sequence start after each complete traversal; one initial row plus one row per completed turn",
        "requested_turns": TRACK_TURNS,
        "retained_samples": len(history_rows),
        "expected_samples": TRACK_TURNS + 1,
        "sample_count_convention": "includes initial turn-0 row",
        "finite": finite,
        "loss_free": loss_free,
        "loss": loss_record,
        "reason": None if status == "complete" else "Target tracking workers did not provide a complete, finite, loss-free turn history and loss check.",
    }
    return summary, history_rows


def compare_turn_histories(
    reference_summary: dict[str, Any],
    reference_rows: list[dict[str, Any]],
    target_summary: dict[str, Any],
    target_rows: list[dict[str, float]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compare synchronized transverse coordinates only after validating both records."""
    if reference_summary.get("status") != "complete" or target_summary.get("status") != "complete":
        return [], {"status": "blocked", "reason": "Reference and target must both retain the complete declared sample count before comparison."}
    expected = TRACK_TURNS + 1
    if len(reference_rows) != expected or len(target_rows) != expected:
        return [], {"status": "blocked", "reason": "Reference/target turn histories have different or incomplete lengths."}
    columns = (("X", "x", "m"), ("Y", "y", "m"))
    records: list[dict[str, Any]] = []
    metrics = []
    for turn, (reference, target) in enumerate(zip(reference_rows, target_rows)):
        for reference_key, target_key, unit in columns:
            ref_value = float(reference[reference_key])
            target_value = float(target[target_key])
            records.append({"turn": turn, "observation_point": "sequence start", "observable": target_key, "reference": ref_value, "target": target_value, "signed_target_minus_reference": target_value - ref_value, "units": unit})
    for _, target_key, unit in columns:
        differences = np.asarray([row["signed_target_minus_reference"] for row in records if row["observable"] == target_key])
        metrics.append({"observable": f"tracking_{target_key}", "units": unit, "sample_count": len(differences), "maximum_absolute_residual": float(np.max(np.abs(differences))), "rms_residual": float(np.sqrt(np.mean(differences ** 2))), "tolerance": None, "classification": "pending-tolerance", "note": "64-turn coarse comparison; integration recipes differ and coordinate synchronization requires human review"})
    return records, {"status": "pending-tolerance", "sample_count": expected, "sample_count_convention": "turn-0 initial state plus one sample at the sequence start after each completed turn", "metrics": metrics}


def make_orbit_marker_file(fibres: list[Any], path: Path) -> list[str]:
    """Write PTC's documented pre-orbit named-exit selection file."""
    names = list(dict.fromkeys(record.name for record in fibres))
    path.write_text("SETORBITMARKER\n" + str(len(names)) + "\n" + "\n".join(names) + "\nreturn\n", encoding="utf-8")
    return names


def parse_ptc_orbit_nodes(path: Path) -> list[dict[str, Any]]:
    """Parse PRINTORBITNODES groups and preserve node, fibre, side and s data."""
    groups: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        node_match = re.match(r"\s*Node Number\s+(\d+)", line)
        if node_match:
            current = {"node_index": int(node_match.group(1)), "integration_records": []}
            groups.append(current)
            continue
        if current is None:
            continue
        values = line.split()
        if len(values) >= 4:
            try:
                s_value = float(values[0].replace("D", "E"))
                fibre_position = int(values[-2])
                cas = int(values[-1])
            except ValueError:
                continue
            current["integration_records"].append({
                "s_m": s_value,
                "fibre_name": values[1],
                "fibre_position": fibre_position,
                "cas": cas,
            })
    for group in groups:
        if group["integration_records"]:
            group["terminal_record"] = group["integration_records"][-1]
    if not groups:
        raise RuntimeError(f"No PTC orbit-node groups found in {path}")
    return groups


def run_pyptc_optics(
    repo_root: Path,
    flat_file: Path,
    library: Path,
    target_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[Any], list[dict[str, Any]]]:
    """Load admitted PyPTC in a private directory and return all-node records."""
    sys.path.insert(0, str(repo_root))
    from pyptc.lattice import read_flatfile_fibres

    target_dir.mkdir(parents=True, exist_ok=True)
    fibres = read_flatfile_fibres(flat_file)
    make_orbit_marker_file(fibres, target_dir / "pre_orbit_set.txt")
    maxwellian = flat_file.parent / "Maxwellian_bend_for_ptc.txt"
    if maxwellian.is_file():
        (target_dir / maxwellian.name).write_bytes(maxwellian.read_bytes())
    printer = target_dir / "print_orbit_nodes.ptc"
    printer.write_text("PRINTORBITNODES\nreturn\n", encoding="utf-8")
    node_dump = target_dir / "def_orbit_node.txt"
    runtime_log = target_dir / "pyptc_runtime.log"
    summary_path = target_dir / "pyptc_api_summary.json"
    worker = Path(__file__).with_name("ptc_optics_worker.py")
    command = [sys.executable, str(worker), str(repo_root), str(flat_file), str(library), str(printer), str(summary_path), str(target_dir / "node_twiss_raw.csv")]
    with runtime_log.open("w", encoding="utf-8") as native_log:
        completed = subprocess.run(command, cwd=target_dir, stdout=native_log, stderr=subprocess.STDOUT, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"Isolated PyPTC optics worker failed with exit code {completed.returncode}; inspect {runtime_log}")
    if not summary_path.is_file():
        raise RuntimeError("PyPTC optics worker returned without an API summary")
    api_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    with (target_dir / "node_twiss_raw.csv").open(newline="", encoding="utf-8") as handle:
        profile: list[dict[str, Any]] = []
        for raw in csv.DictReader(handle):
            profile.append({key: (int(value) if key == "node_index" else float(value) if key not in {"sampling_location"} else value) for key, value in raw.items()})
    if not node_dump.is_file():
        raise RuntimeError("PTC PRINTORBITNODES did not create def_orbit_node.txt")
    groups = parse_ptc_orbit_nodes(node_dump)
    longitudinal = np.asarray([float(row["s_exit_m"]) for row in profile])
    runtime_text = runtime_log.read_text(encoding="utf-8", errors="replace")
    summary = {
        **api_summary,
        "library": str(library),
        "library_sha256": sha256(library),
        "profile_rows": len(profile),
        "profile_sampling": "PTC all-node rows are stored after ORBIT_TRACK_NODE; row length is the preceding interval",
        "phase_sampling": "node_phase_advances is cumulative phase at node exits; use returned values without a second cumulative sum",
        "flat_file": str(flat_file),
        "flat_file_sha256": sha256(flat_file),
        "pre_orbit_file": "pre_orbit_set.txt",
        "pre_orbit_sha256": sha256(target_dir / "pre_orbit_set.txt"),
        "orbit_node_dump": node_dump.name,
        "orbit_node_dump_sha256": sha256(node_dump),
        "runtime_log": runtime_log.name,
        "runtime_log_sha256": sha256(runtime_log),
        "circumference_from_node_lengths_m": float(longitudinal[-1]) if len(longitudinal) else 0.0,
        "warnings": {
            "cavity_frequency_messages": runtime_text.count("COULD NOT LOCALIZE NON 0.0_dp CAVITY FREQUENCY"),
            "dlmax_lmax_messages": runtime_text.count("DLMAX > LMAX"),
            "orbit_warning_11_present": "ORBIT_WARNING           11" in runtime_text,
        },
    }
    return summary, profile, fibres, groups


def build_verified_boundary_map(
    reference_rows: list[dict[str, str]],
    target_rows: list[dict[str, Any]],
    fibres: list[Any],
    node_groups: list[dict[str, Any]],
    position_tolerance_m: float = POSITION_TOLERANCE_M,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Map the two element-exit tables by identity, occurrence, fibre and s."""
    if len(reference_rows) != len(fibres):
        raise ValueError(f"Reference has {len(reference_rows)} rows for {len(fibres)} flat-file fibres")
    if len(target_rows) != len(node_groups):
        raise ValueError(f"PyPTC has {len(target_rows)} profile rows for {len(node_groups)} printed node groups")
    occurrence: Counter[str] = Counter()
    reference_by_identity: dict[tuple[str, int], tuple[int, dict[str, str]]] = {}
    for index, row in enumerate(reference_rows):
        name = row["NAME"].upper()
        occurrence[name] += 1
        reference_by_identity[(name, occurrence[name])] = (index, row)

    expected_by_fibre: dict[int, dict[str, Any]] = {}
    running_s = 0.0
    for fibre in fibres:
        running_s += float(fibre.length)
        expected_by_fibre[int(fibre.index)] = {
            "name": str(fibre.name).upper(),
            "occurrence": sum(1 for previous in fibres if previous.index <= fibre.index and previous.name.upper() == fibre.name.upper()),
            "s_m": running_s,
        }

    target_candidates: dict[int, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for group in node_groups:
        terminal = group.get("terminal_record")
        if terminal is None:
            continue
        target_candidates[int(terminal["fibre_position"])].append((group, terminal))

    map_by_fibre: dict[int, tuple[dict[str, Any], dict[str, Any]]] = {}
    failures: list[str] = []
    for fibre_index, expected in expected_by_fibre.items():
        candidates = [
            (group, terminal) for group, terminal in target_candidates.get(fibre_index, [])
            if terminal["fibre_name"].upper() == expected["name"]
            and abs(float(terminal["s_m"]) - expected["s_m"]) <= position_tolerance_m
        ]
        if len(candidates) != 1:
            failures.append(f"fibre {fibre_index} {expected['name']} has {len(candidates)} matching PTC exit groups")
        else:
            map_by_fibre[fibre_index] = candidates[0]

    records: list[dict[str, Any]] = []
    reference_seen: set[int] = set()
    target_seen: set[int] = set()
    for fibre in fibres:
        fibre_index = int(fibre.index)
        expected = expected_by_fibre[fibre_index]
        identity = (expected["name"], int(expected["occurrence"]))
        reference_match = reference_by_identity.get(identity)
        target_match = map_by_fibre.get(fibre_index)
        if reference_match is None or target_match is None:
            failures.append(f"missing side for element identity {identity}")
            continue
        reference_index, reference = reference_match
        group, terminal = target_match
        node_index = int(group["node_index"])
        target_seen.add(node_index)
        reference_seen.add(reference_index)
        ref_s = float(reference["S"])
        ptc_s = float(target_rows[node_index]["s_exit_m"])
        ref_vs_flat = ref_s - expected["s_m"]
        ptc_vs_flat = ptc_s - expected["s_m"]
        if abs(ref_vs_flat) > position_tolerance_m:
            failures.append(f"MAD-X row {reference_index} is not at fibre {fibre_index}'s exit")
        if abs(ptc_vs_flat) > position_tolerance_m or abs(float(terminal["s_m"]) - expected["s_m"]) > position_tolerance_m:
            failures.append(f"PyPTC row {node_index} is not at fibre {fibre_index}'s exit")
        records.append({
            "fibre_index": fibre_index,
            "element_name": str(fibre.name),
            "element_occurrence": int(expected["occurrence"]),
            "reference_row_index": reference_index,
            "reference_name": reference["NAME"],
            "reference_sampling_location": "element exit from sequence REFER=exit",
            "reference_s_m": ref_s,
            "target_node_index": node_index,
            "target_name": terminal["fibre_name"],
            "target_fibre_position": int(terminal["fibre_position"]),
            "target_cas": int(terminal["cas"]),
            "target_sampling_location": "named fibre exit; final integration record in PRINTORBITNODES group",
            "target_s_m": ptc_s,
            "position_residual_target_minus_reference_m": ptc_s - ref_s,
            "position_residual_reference_minus_flat_end_m": ref_vs_flat,
            "position_residual_target_minus_flat_end_m": ptc_vs_flat,
            "mapping_classification": "mapped" if not failures else "mapped-candidate",
        })
    if len(reference_seen) != len(reference_rows):
        failures.append(f"mapped {len(reference_seen)} of {len(reference_rows)} MAD-X rows")
    if len(target_seen) != len(fibres):
        failures.append(f"mapped {len(target_seen)} of {len(fibres)} named PTC fibre exits")
    status = "verified" if not failures and len(records) == len(reference_rows) == len(fibres) else "blocked"
    for record in records:
        record["mapping_classification"] = "mapped" if status == "verified" else "candidate-only; overall map blocked"
    return records, {
        "status": status,
        "method": "join by flat-file fibre index, exact element name and occurrence, then verify MAD-X and PyPTC physical exit s against the flat-file cumulative end",
        "position_tolerance_m": position_tolerance_m,
        "reference_rows": len(reference_rows),
        "target_node_rows": len(target_rows),
        "flat_file_fibres": len(fibres),
        "mapped_boundaries": len(records),
        "unique_reference_rows_mapped": len(reference_seen),
        "unique_target_nodes_mapped": len(target_seen),
        "failures": failures,
        "periodic_endpoint_included": bool(records and abs(float(records[-1]["reference_s_m"]) - float(reference_rows[-1]["S"])) <= position_tolerance_m),
        "zero_length_elements_preserved_by_identity": True,
    }


def align_profiles(
    boundary_map: list[dict[str, Any]],
    reference_rows: list[dict[str, str]],
    target_rows: list[dict[str, Any]],
    beta0: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return aligned, converted profile rows and per-observable residual metrics."""
    aligned: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    if not boundary_map:
        return aligned, metrics
    for mapping in boundary_map:
        ref = reference_rows[int(mapping["reference_row_index"])]
        target = target_rows[int(mapping["target_node_index"])]
        row: dict[str, Any] = {**mapping}
        for observable, (reference_key, target_key, _unit) in PROFILE_FIELDS.items():
            ref_value = float(ref[reference_key])
            if observable in ("dx", "dpx", "dy", "dpy"):
                ref_value *= beta0
            target_value = float(target[target_key])
            row[f"reference_{observable}"] = ref_value
            row[f"target_{observable}"] = target_value
            row[f"target_minus_reference_{observable}"] = target_value - ref_value
        aligned.append(row)
    for observable, (_, _, unit) in PROFILE_FIELDS.items():
        residuals = np.asarray([float(row[f"target_minus_reference_{observable}"]) for row in aligned])
        metrics.append({
            "observable": observable,
            "units": unit,
            "definition": "target minus reference at verified element exits; MAD-X dispersion and derivatives multiplied by run-specific beta0",
            "sample_count": int(len(residuals)),
            "signed_mean": float(np.mean(residuals)),
            "maximum_absolute_residual": float(np.max(np.abs(residuals))),
            "rms_residual": float(np.sqrt(np.mean(residuals ** 2))),
            "tolerance": None,
            "tolerance_source": None,
            "acceptance_owner": "pending user review",
            "classification": "pending-tolerance",
        })
    return aligned, metrics


def classify_source_families(
    input_dir: Path,
    names: Iterable[str],
    reference_rows: list[dict[str, str]] | None = None,
) -> tuple[dict[str, str], dict[str, Any]]:
    """Classify plotted magnet families from the admitted element/sequence files."""
    definitions: dict[str, tuple[str, str]] = {}
    section = "other elements"
    for line in (input_dir / "ISIS.elements").read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip().startswith("!"):
            comment = line.strip(" !-").lower()
            if "trim quadrupole" in comment:
                section = "trim quadrupoles"
            elif "main quadrupole" in comment:
                section = "main quadrupoles"
            elif "main dipole" in comment:
                section = "main dipoles"
            elif "drift" in comment:
                section = "drifts"
            continue
        match = re.match(r"\s*([A-Za-z0-9_$]+)\s*:\s*([A-Za-z0-9_$]+)\s*,", line)
        if match:
            definitions[match.group(1).lower()] = (match.group(2).lower(), section)
    placements: dict[str, str] = {}
    for line in (input_dir / "ISIS.sequence").read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"\s*([A-Za-z0-9_$]+)\s*:\s*([A-Za-z0-9_$]+)\s*,\s*at\s*=", line, re.IGNORECASE)
        if match:
            placements[match.group(1).lower()] = match.group(2).lower()

    reference_keyword = {
        str(row["NAME"]).lower(): str(row.get("KEYWORD", "")).lower()
        for row in (reference_rows or [])
    }

    def family_for(name: str) -> str:
        placement = placements.get(name.lower())
        if placement is None:
            keyword = reference_keyword.get(name.lower(), "")
            if keyword == "drift":
                return "drifts"
            if keyword == "marker":
                return "other elements"
            return "unmapped"
        visited: set[str] = set()
        current = placement
        inherited_section = "other elements"
        while current in definitions and current not in visited:
            visited.add(current)
            element_type, declared_section = definitions[current]
            if declared_section != "other elements":
                inherited_section = declared_section
            if element_type == "drift":
                return "drifts"
            if element_type == "sbend":
                return "main dipoles"
            if element_type == "rbend":
                return "other bends"
            if element_type == "quadrupole":
                if inherited_section == "trim quadrupoles" or current in {"qtd", "qtf"}:
                    return "trim quadrupoles"
                return "main quadrupoles"
            current = element_type
        return "other elements"

    family_map = {name: family_for(name) for name in names}
    return family_map, {
        "source_files": ["snapshot_inputs/ISIS.elements", "snapshot_inputs/ISIS.sequence"],
        "rule": "sequence placement resolves through ISIS.elements declarations; drift type=drifts, sbend=main dipoles, quadrupole declarations in the source TRIM QUADRUPOLES section=trim quadrupoles, remaining quadrupoles=main quadrupoles, rbend=other bends. MAD-X-generated gaps use their TWISS KEYWORD (DRIFT); sequence start markers use KEYWORD=MARKER.",
        "family_counts": dict(Counter(family_map.values())),
        "unmapped_names": [name for name, family in family_map.items() if family == "unmapped"],
    }


def scalar_comparisons(
    reference_headers: dict[str, str],
    target_summary: dict[str, Any],
    mapping_summary: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compare scalar working-point values and explicitly classify chromaticity."""
    machine = target_summary["machine_summary"]
    target_tunes = target_summary["tunes"]
    rows: list[dict[str, Any]] = []
    for name, reference, target, unit in (
        ("bare_horizontal_tune", float(reference_headers["Q1"]) % 1.0, float(target_tunes["qx"]), "tune units"),
        ("bare_vertical_tune", float(reference_headers["Q2"]) % 1.0, float(target_tunes["qy"]), "tune units"),
        ("circumference", float(reference_headers["LENGTH"]), float(machine["circumference_m"]), "m"),
    ):
        rows.append({
            "observable": name, "reference": reference, "target": target,
            "signed_target_minus_reference": target - reference, "units": unit,
            "tolerance": None, "tolerance_source": None,
            "classification": "pending-tolerance", "acceptance_owner": "pending user review",
        })
    if "DQ1" in reference_headers and "DQ2" in reference_headers:
        reference_chromaticity = {"x": float(reference_headers["DQ1"]), "y": float(reference_headers["DQ2"])}
    else:
        reference_chromaticity = {"x": None, "y": None}
    target_chromaticity = target_summary["chromaticities_native"]
    chromaticity = {}
    for plane, key in (("x", "chromx"), ("y", "chromy")):
        ref_value = reference_chromaticity[plane]
        target_value = float(target_chromaticity[key])
        chromaticity[plane] = {
            "reference_native": ref_value,
            "reference_definition": "MAD-X 5.02.00 dQ/dDELTAP" if ref_value is not None else "missing",
            "target_native": target_value,
            "target_definition": "PTC lattice_GET_CHROM coordinate not established by the public PyPTC API",
            "converted_dQ_d_delta_p": None,
            "signed_difference": None if ref_value is None else target_value - ref_value,
            "classification": "blocked",
            "reason": "the target native derivative coordinate and tune estimator are undocumented here; converting or equating it to dQ/d(delta_p) would be an unsupported inference",
            "tolerance": None,
        }
        rows.append({
            "observable": f"bare_{'horizontal' if plane == 'x' else 'vertical'}_chromaticity",
            "reference_native": ref_value,
            "target_native": target_value,
            "signed_native_difference": None if ref_value is None else target_value - ref_value,
            "units": "native derivatives; conversion to dQ/d(delta_p) unresolved",
            "converted_reference_dQ_d_delta_p": ref_value,
            "converted_target_dQ_d_delta_p": None,
            "tolerance": None,
            "classification": "blocked",
            "acceptance_owner": "pending convention review",
        })
    return rows, {
        "reference_gamma": float(reference_headers.get("GAMMA", "nan")),
        "reference_native_definition": "MAD-X 5.02.00 DQ1/DQ2=dQ/dDELTAP, DELTAP=(p-p0)/p0; conversion factor 1",
        "target_native_values": target_chromaticity,
        "planes": chromaticity,
        "classification": "blocked",
    }


def write_case_composite(
    path: Path,
    aligned: list[dict[str, Any]],
    scalar_rows: list[dict[str, Any]],
    family_map: dict[str, str],
    family_summary: dict[str, Any],
    effective_recipe: str,
    mapping_summary: dict[str, Any],
    raster_dpi: int = 150,
) -> dict[str, Any]:
    """Create one nominal case file with overview, working point and residual panels."""
    if not aligned:
        raise ValueError("Cannot plot a nominal composite without mapped profile samples")
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 7})
    profile_names = list(PROFILE_FIELDS)
    figure = plt.figure(figsize=(21, 46), constrained_layout=False)
    layout = figure.add_gridspec(12, 2, height_ratios=[0.65, 1.65, 1.65, 1.65, 1.35] + [4.1] * 7, hspace=0.55, wspace=0.28)
    s_ref = np.asarray([float(row["reference_s_m"]) for row in aligned])
    s_target = np.asarray([float(row["target_s_m"]) for row in aligned])

    strip = figure.add_subplot(layout[0, :])
    for index, row in enumerate(aligned):
        start_s = 0.0 if index == 0 else float(aligned[index - 1]["reference_s_m"])
        end_s = float(row["reference_s_m"])
        family = family_map.get(str(row["element_name"]), "unmapped")
        strip.add_patch(Rectangle((start_s, 0), max(end_s - start_s, 1.0e-6), 1, color=FAMILY_COLORS.get(family, FAMILY_COLORS["unmapped"]), linewidth=0))
    strip.set_xlim(float(s_ref[0]), float(s_ref[-1]))
    strip.set_ylim(0, 1)
    strip.set_yticks([])
    strip.set_title("Magnet-family strip — classification from admitted ISIS.elements and ISIS.sequence")
    strip.set_xlabel("s [m]")
    strip.legend(handles=[Patch(facecolor=color, label=name) for name, color in FAMILY_COLORS.items() if name in set(family_map.values())], loc="upper center", ncol=7, bbox_to_anchor=(0.5, 1.02), frameon=False)

    overview_names = ("betx", "bety", "dx", "dy", "x", "y")
    for index, observable in enumerate(overview_names):
        axis = figure.add_subplot(layout[1 + index // 2, index % 2])
        title = PROFILE_TITLES[observable]
        unit = PROFILE_FIELDS[observable][2]
        reference_values = np.asarray([float(row[f"reference_{observable}"]) for row in aligned])
        target_values = np.asarray([float(row[f"target_{observable}"]) for row in aligned])
        axis.plot(s_ref, reference_values, linestyle="none", marker=".", markersize=2.4, label="MAD-X reference")
        axis.plot(s_target, target_values, linestyle="none", marker="x", markersize=2.6, label="PyPTC target")
        axis.set_title(title)
        axis.set_ylabel(f"[{unit}]")
        if index >= 4:
            axis.set_xlabel("mapped s [m]")
        axis.grid(alpha=0.2)
        if index == 0:
            axis.legend(loc="best")

    working_point = figure.add_subplot(layout[4, :])
    working_point.axis("off")
    scalar_by_name = {row["observable"]: row for row in scalar_rows}
    chrom_status = "blocked: target derivative coordinate unresolved"
    chrom_rows = [scalar_by_name.get("bare_horizontal_chromaticity", {}), scalar_by_name.get("bare_vertical_chromaticity", {})]
    chrom = [
        f"Bare {plane} chromaticity: MAD-X native={row.get('reference_native')}; PyPTC native={row.get('target_native')}; difference={row.get('signed_native_difference')}; dQ/d(delta_p) conversion blocked"
        for plane, row in zip(("horizontal", "vertical"), chrom_rows)
    ]
    lines = [
        "Nominal working point — overview only; all scalar tolerances pending user review",
        f"Bare horizontal tune: MAD-X={scalar_by_name['bare_horizontal_tune']['reference']:.9g}, PyPTC={scalar_by_name['bare_horizontal_tune']['target']:.9g}, signed difference={scalar_by_name['bare_horizontal_tune']['signed_target_minus_reference']:+.3g}",
        f"Bare vertical tune: MAD-X={scalar_by_name['bare_vertical_tune']['reference']:.9g}, PyPTC={scalar_by_name['bare_vertical_tune']['target']:.9g}, signed difference={scalar_by_name['bare_vertical_tune']['signed_target_minus_reference']:+.3g}",
        *chrom,
        f"Circumference: MAD-X={scalar_by_name['circumference']['reference']:.12g} m, PyPTC={scalar_by_name['circumference']['target']:.12g} m, signed difference={scalar_by_name['circumference']['signed_target_minus_reference']:+.3g} m",
        f"Recipe: {effective_recipe}; mapped element exits={len(aligned)}; mapping={mapping_summary['status']}; chromaticity={chrom_status}",
    ]
    working_point.text(0.01, 0.97, "\n".join(lines), va="top", ha="left", family="monospace", fontsize=8)
    working_point.set_title("Bare working point and reviewed-state context")

    for profile_index, observable in enumerate(profile_names):
        group_grid = layout[5 + profile_index // 2, profile_index % 2].subgridspec(2, 1, height_ratios=[2, 1], hspace=0.06)
        overlay = figure.add_subplot(group_grid[0, 0])
        residual_axis = figure.add_subplot(group_grid[1, 0], sharex=overlay)
        unit = PROFILE_FIELDS[observable][2]
        reference_values = np.asarray([float(row[f"reference_{observable}"]) for row in aligned])
        target_values = np.asarray([float(row[f"target_{observable}"]) for row in aligned])
        residuals = target_values - reference_values
        overlay.plot(s_ref, reference_values, linestyle="none", marker=".", markersize=2.2, label="MAD-X reference")
        overlay.plot(s_target, target_values, linestyle="none", marker="x", markersize=2.2, label="PyPTC target")
        overlay.set_title(f"{PROFILE_TITLES[observable]} — {unit}")
        overlay.set_ylabel(f"[{unit}]")
        overlay.tick_params(axis="x", labelbottom=False)
        overlay.grid(alpha=0.2)
        if profile_index == 0:
            overlay.legend(loc="best")
        residual_axis.plot(s_target, residuals, linestyle="none", marker=".", markersize=2.0, color="#7b3294")
        residual_axis.axhline(0.0, color="black", linewidth=0.6)
        residual_axis.set_ylabel("resid.")
        residual_axis.set_xlabel("mapped s [m]")
        residual_axis.grid(alpha=0.2)

    figure.suptitle("ISIS RCS nominal linear-optics comparison — profile agreement pending tolerance review", fontsize=13, y=0.995)
    figure.subplots_adjust(left=0.075, right=0.985, top=0.975, bottom=0.035)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=raster_dpi)
    plt.close(figure)
    return {
        "case": "nominal",
        "artifact": str(path),
        "sha256": sha256(path),
        "case_file_count": 1,
        "panel_groups": [
            {"group": "magnet_family_strip", "source": family_summary["source_files"], "classification": family_summary["rule"]},
            {"group": "nominal_master_twiss_orbit_overview", "observables": list(overview_names), "effective_recipe": effective_recipe, "mapping": mapping_summary["status"]},
            {"group": "bare_working_point", "observables": ["bare_horizontal_tune", "bare_vertical_tune", "bare_horizontal_chromaticity", "bare_vertical_chromaticity", "circumference"]},
            *[{
                "group": f"profile_{observable}",
                "observable": observable,
                "units": PROFILE_FIELDS[observable][2],
                "reference_target_overlay": True,
                "signed_residual_direction": "PyPTC - MAD-X",
                "residual_panel_fraction": 0.5,
                "sample_count": len(aligned),
                "mapping": mapping_summary["status"],
                "aligned_data": "aligned_profiles.csv",
            } for observable in profile_names],
        ],
        "sample_count": len(aligned),
        "mapping": mapping_summary["status"],
        "raster": {"width_px": int(21 * raster_dpi), "height_px": int(46 * raster_dpi), "dpi": raster_dpi},
        "marker_style": "visible distinct markers, no connecting lines",
        "visual_readability_review": "pending normal-view inspection",
    }


def converted_chromaticity_from_madx(dq_d_delta_p: float, beta0: float, native_coordinate: str) -> tuple[float | None, float]:
    """Convert supported MAD-X native derivative to dQ/d(delta_p)."""
    if native_coordinate == "DELTAP":
        return dq_d_delta_p, 1.0
    if native_coordinate == "PT":
        return beta0 * dq_d_delta_p, beta0
    return None, float("nan")


def summarize_perturbation_coverage() -> dict[str, Any]:
    """Describe the iteration's nominal-only scope; no perturbation was declared."""
    return {"status": "unbenchmarked", "declared_cases": [], "reason": "No corrector, error, misalignment, or error-table case was authorized for iteration 0002."}

