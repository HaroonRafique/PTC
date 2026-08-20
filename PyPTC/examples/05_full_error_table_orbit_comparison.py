#!/usr/bin/env python3
"""Apply the full Jan26 error table and compare PyPTC orbit with MAD-X Twiss."""

from __future__ import annotations

import subprocess
import sys

from common import (
    LATEST_SURVEY_REFERENCE_ERROR_TABLE,
    MADX_DIR,
    SURVEY_TO_LATTICE_MADX_TWISS,
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
    records = read_madx_error_table(LATEST_SURVEY_REFERENCE_ERROR_TABLE, nonzero=False)
    applied = ptc.apply_madx_error_table(LATEST_SURVEY_REFERENCE_ERROR_TABLE, nonzero=False)
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
            str(LATEST_SURVEY_REFERENCE_ERROR_TABLE),
            "--flat-file",
            str(ensure_default_lattice()),
            "--madx-reference-twiss",
            str(SURVEY_TO_LATTICE_MADX_TWISS),
            "--output-dir",
            str(comparison_dir),
            "--response-threshold",
            "0.0",
        ],
        check=True,
    )
    copy_madx_comparison_outputs(comparison_dir, out)
    write_json(
        out / "summary.json",
        {
            "lattice": str(ptc.lattice),
            "madx_error_table": str(LATEST_SURVEY_REFERENCE_ERROR_TABLE),
            "madx_reference_twiss": str(SURVEY_TO_LATTICE_MADX_TWISS),
            "records": len(records),
            "applied": len(applied),
            "max_abs_delta_x_m": float(abs(orbit[:, 3]).max()),
            "max_abs_delta_y_m": float(abs(orbit[:, 6]).max()),
        },
    )


if __name__ == "__main__":
    main()
