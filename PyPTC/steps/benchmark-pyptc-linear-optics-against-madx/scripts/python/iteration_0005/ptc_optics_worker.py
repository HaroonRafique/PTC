#!/usr/bin/env python3
"""Internal isolated-process adapter for one accepted PyPTC optics load."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

arguments = sys.argv[1:]
if len(arguments) not in {6, 7}:
    raise SystemExit("internal worker expects repo, flat file, library, printer, summary, node CSV, and optional MAD-X error table")
repo_root, flat_file, library, printer, summary_path, node_csv = map(Path, arguments[:6])
error_table = Path(arguments[6]).resolve() if len(arguments) == 7 else None
sys.path.insert(0, str(repo_root))
from pyptc import PTC

from isis_rcs_optics import sha256, write_csv

flat_file = flat_file.resolve()
library = library.resolve()
printer = printer.resolve()
summary_path = summary_path.resolve()
node_csv = node_csv.resolve()
ptc = PTC(library)
ptc.init_lattice(flat_file)
api_calls = ["PTC(library)", "PTC.init_lattice(case_flat_file)"]
applied_errors = []
if error_table is not None:
    applied_errors = ptc.apply_madx_error_table(error_table, nonzero=True)
    ptc.update_twiss()
    api_calls.extend(["PTC.apply_madx_error_table(case_error_table, nonzero=True)", "PTC.update_twiss()"])
machine = ptc.machine_summary()
tunes = ptc.tunes()
chromaticities_native = ptc.chromaticities()
profile = ptc.all_node_twiss_orbit()
longitudinal = np.cumsum([float(row["length"]) for row in profile])
for row, s_value in zip(profile, longitudinal):
    row["s_exit_m"] = float(s_value)
    row["sampling_location"] = "orbit-node exit; verified from PTC integration-node printer"
ptc.run_script(printer)
write_csv(node_csv, profile)
summary = {
    "executed_api_calls": [*api_calls, "PTC.machine_summary()", "PTC.tunes()", "PTC.chromaticities()", "PTC.all_node_twiss_orbit()", "PTC.run_script(PRINTORBITNODES)"],
    "error_table": str(error_table) if error_table else None,
    "applied_error_records": [record.__dict__ for record in applied_errors],
    "python_api_source": "pyptc/core.py",
    "python_api_source_sha256": sha256(repo_root / "pyptc/core.py"),
    "api_level": ptc.api_level(),
    "machine_summary": machine,
    "tunes": tunes,
    "chromaticities_native": chromaticities_native,
    "circumference_from_node_lengths_m": float(longitudinal[-1]) if len(longitudinal) else 0.0,
}
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
