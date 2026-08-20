#!/usr/bin/env python3
"""Apply the full Jan26 error table and compare PyPTC orbit with MAD-X Twiss."""

from __future__ import annotations

import subprocess
import sys
import json

from common import (
    MADX_DIR,
    SURVEY_TO_LATTICE_JAN26_CORRECTED_ERROR_TABLE,
    copy_madx_comparison_outputs,
    ensure_default_lattice,
    init_ptc,
    orbit_response_rows,
    output_dir,
    plot_orbit_response,
    read_madx_error_table,
    write_array_csv,
    write_json,
)


def main() -> None:
    out = output_dir("05_full_error_table_orbit_comparison")
    ptc = init_ptc()
    bare_rows = ptc.all_node_twiss_orbit()
    error_table = SURVEY_TO_LATTICE_JAN26_CORRECTED_ERROR_TABLE
    records = read_madx_error_table(error_table, nonzero=False)
    applied = ptc.apply_madx_error_table(error_table, nonzero=False)
    if len(records) == 38 and len(applied) != 38:
        raise RuntimeError(f"Jan26 table produced {len(applied)} applications for {len(records)} records")
    ptc.update_twiss()
    edited_rows = ptc.all_node_twiss_orbit()
    orbit = orbit_response_rows(bare_rows, edited_rows)
    plot_orbit_response(out / "full_error_table_pyptc_orbit.png", orbit, labels=("bare", "Jan26 full error table"))
    write_array_csv(out / "full_error_table_pyptc_orbit.csv", orbit, "s,bare_x,error_x,delta_x,bare_y,error_y,delta_y")

    comparison_dir = out / "madx_pyptc_closed_orbit_comparison"
    subprocess.run(
        [
            sys.executable,
            str(MADX_DIR / "compare_madx_pyptc_closed_orbits.py"),
            "--madx-error-table",
            str(error_table),
            "--flat-file",
            str(ensure_default_lattice()),
            "--output-dir",
            str(comparison_dir),
            "--response-threshold",
            "0.0",
            "--distorted-only",
        ],
        check=True,
    )
    copy_madx_comparison_outputs(comparison_dir, out)
    comparison_summary = json.loads((comparison_dir / "summary.json").read_text(encoding="utf-8"))
    write_json(
        out / "summary.json",
        {
            "lattice": str(ptc.lattice),
            "madx_error_table": str(error_table),
            "records": len(records),
            "applied": len(applied),
            "max_abs_delta_x_m": float(abs(orbit[:, 3]).max()),
            "max_abs_delta_y_m": float(abs(orbit[:, 6]).max()),
            "comparison": comparison_summary,
        },
    )


if __name__ == "__main__":
    main()
