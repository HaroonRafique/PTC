#!/usr/bin/env python3
"""Add a single deterministic misalignment and plot the orbit response."""

from __future__ import annotations

from common import (
    DEFAULT_LATTICE,
    apply_single_misalignment,
    ensure_default_lattice,
    init_ptc,
    orbit_response_rows,
    output_dir,
    plot_orbit_response,
    write_array_csv,
    write_json,
)


def main() -> None:
    out = output_dir("04_single_element_misalignment")
    lattice = ensure_default_lattice()
    misaligned_lattice = out / "SP0_QF_occ1_dx0.003.flt"
    applied = apply_single_misalignment(lattice, misaligned_lattice, "SP0_QF", occurrence=1, dx=0.003)

    bare = init_ptc(DEFAULT_LATTICE)
    bare_rows = bare.all_node_twiss_orbit()
    edited = init_ptc(misaligned_lattice)
    edited_rows = edited.all_node_twiss_orbit()
    orbit = orbit_response_rows(bare_rows, edited_rows)
    plot_orbit_response(out / "single_element_orbit_response.png", orbit, labels=("bare", "SP0_QF dx=3 mm"))
    write_array_csv(out / "single_element_orbit_response.csv", orbit, "s,bare_x,misaligned_x,delta_x,bare_y,misaligned_y,delta_y")
    write_json(out / "summary.json", {"lattice": str(lattice), "misaligned_lattice": str(misaligned_lattice), "applied": applied.__dict__})


if __name__ == "__main__":
    main()
