#!/usr/bin/env python3
"""Bounded probe of PTC's pre_orbit_set/SETORBITMARKER sampling support.

Run this script with the probe output directory as the process working
directory. PTC reads ``pre_orbit_set.txt`` relative to that directory during
``ptc_init``. All generated files therefore stay in the selected test output.
"""

from __future__ import annotations

import csv
import json
import shlex
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from pyptc import DEFAULT_LIBRARY, PTC
from pyptc.lattice import read_flatfile_fibres


BASIS = REPO_ROOT / "steps/benchmark-pyptc-linear-optics-against-madx/admission_basis-accepted-attempt-20261027T082315Z"
FLAT_FILE = BASIS / "madx_work/PTC-PyORBIT_flat_file.flt"
MADX_TFS = REPO_ROOT / "test_outputs/benchmark-pyptc-linear-optics-against-madx/attempt-20261027T145757Z/madx/reference_twiss.tfs"
EXACT_TOLERANCE_M = 1.0e-9


def read_tfs_name_s(path: Path) -> list[tuple[str, float]]:
    columns: list[str] | None = None
    result: list[tuple[str, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("* "):
            columns = shlex.split(line[2:])
            continue
        if columns is None or line.startswith(("@", "$", "#")) or not line.strip():
            continue
        row = dict(zip(columns, shlex.split(line)))
        result.append((row["NAME"], float(row["S"])))
    return result


def read_orbit_node_ends(path: Path) -> list[tuple[int, float, str, int, int]]:
    """Read the final printed integration-node identity for each orbit node."""
    groups: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("Node Number"):
            if current is not None:
                groups.append(current)
            current = {"node": int(stripped.split()[-1]), "records": []}
            continue
        if current is None:
            continue
        parts = stripped.split()
        if len(parts) == 4:
            try:
                record = (float(parts[0]), parts[1], int(parts[2]), int(parts[3]))
            except ValueError:
                continue
            current["records"].append(record)  # type: ignore[union-attr]
    if current is not None:
        groups.append(current)
    ends = []
    for group in groups:
        records = group["records"]
        if records:
            s, name, fibre_index, case = records[-1]  # type: ignore[index]
            ends.append((int(group["node"]), float(s), str(name), int(fibre_index), int(case)))
    return ends


def main() -> None:
    work = Path.cwd()
    fibres = read_flatfile_fibres(FLAT_FILE)
    marker_names = list(dict.fromkeys(fibre.name for fibre in fibres))
    pre_orbit = work / "pre_orbit_set.txt"
    pre_orbit.write_text(
        "SETORBITMARKER\n" + str(len(marker_names)) + "\n" + "".join(f"{name}\n" for name in marker_names) + "return\n",
        encoding="utf-8",
    )

    ptc = PTC(DEFAULT_LIBRARY)
    ptc.init_lattice(FLAT_FILE)
    rows = ptc.all_node_twiss_orbit()
    running_s = 0.0
    for row in rows:
        running_s += float(row["length"])
        row["s_exit_m"] = running_s

    profile_path = work / "pyptc_marked_nodes.csv"
    with profile_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    command_path = work / "print_orbit_nodes.ptc"
    command_path.write_text("PRINTORBITNODES\nreturn\n", encoding="utf-8")
    ptc.run_script(command_path)

    madx_rows = read_tfs_name_s(MADX_TFS)
    madx_s = [s for _, s in madx_rows]
    node_ends = read_orbit_node_ends(work / "def_orbit_node.txt")
    fibre_end_s = 0.0
    boundary_matches = 0
    boundary_misses = []
    for fibre in fibres:
        fibre_end_s += fibre.length
        if any(
            name == fibre.name and abs(s - fibre_end_s) <= EXACT_TOLERANCE_M
            for _node_index, s, name, fibre_index, _case in node_ends
            if fibre_index == fibre.index
        ):
            boundary_matches += 1
        else:
            boundary_misses.append({"fibre_index": fibre.index, "name": fibre.name, "s_m": fibre_end_s})
    matched_positions = {
        s for _, s in madx_rows if any(abs(float(row["s_exit_m"]) - s) <= EXACT_TOLERANCE_M for row in rows)
    }
    per_ref_position = Counter(round(s / EXACT_TOLERANCE_M) for _, s in madx_rows)
    summary = {
        "probe": "PTC SETORBITMARKER on every distinct flat-file fibre name before ORBIT layout creation",
        "flat_file_fibres": len(fibres),
        "unique_marker_names": len(marker_names),
        "ptc_orbit_nodes": len(rows),
        "pyptc_circumference_m": running_s,
        "pyptc_tunes": ptc.tunes(),
        "madx_twiss_rows": len(madx_rows),
        "madx_distinct_s_positions": len({round(s / EXACT_TOLERANCE_M) for s in madx_s}),
        "madx_distinct_s_positions_with_a_ptc_sample": len(matched_positions),
        "flat_file_fibre_end_matches_by_name_position_and_s": boundary_matches,
        "flat_file_fibre_end_match_misses": boundary_misses,
        "exact_position_tolerance_m": EXACT_TOLERANCE_M,
        "ptc_node_rows_at_duplicate_reference_positions": sum(
            sum(abs(float(row["s_exit_m"]) - s) <= EXACT_TOLERANCE_M for row in rows) > 1
            for s, count in ((s, c) for s, c in Counter(madx_s).items() if c > 1)
        ),
        "written_files": ["pre_orbit_set.txt", "pyptc_marked_nodes.csv", "print_orbit_nodes.ptc", "def_orbit_node.txt"],
    }
    (work / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
