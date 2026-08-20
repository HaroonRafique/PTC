#!/usr/bin/env python3
"""Add rectangular apertures, track bunches, and plot aperture/loss diagnostics."""

from __future__ import annotations

from common import (
    MADX_DIR,
    apply_matching_madx_apertures,
    init_ptc,
    make_standard_bunch,
    output_dir,
    plot_aperture_at_peak,
    plot_aperture_vs_design,
    plot_loss_map,
    read_jvt_design_aperture,
    run_loss_map,
    write_array_csv,
    write_diagnostic_outputs,
    write_json,
)


def main() -> None:
    out = output_dir("03_track_bunch_with_apertures")
    ptc = init_ptc()
    aperture_file = MADX_DIR / "lattices" / "02_Aperture_Lattice" / "ISIS.aperture"
    design_file = MADX_DIR / "reference_apertures" / "jvt_synch_aperture.csv"
    applied, skipped = apply_matching_madx_apertures(ptc, aperture_file)
    aperture_rows = ptc.all_fibre_apertures()
    design = read_jvt_design_aperture(design_file)
    plot_aperture_vs_design(out / "aperture_vs_design.png", aperture_rows, design)

    bunch = make_standard_bunch(ptc, particles=1000)
    diagnostics = ptc.particle_diagnostics(bunch, turns=64, min_tune_turns=8)
    dashboard_outputs = write_diagnostic_outputs(out, diagnostics)

    loss_table, peak_node, positions_at_peak = run_loss_map(ptc, aperture=0.005, count=81)
    plot_loss_map(out / "loss_map.png", loss_table, ptc.all_node_twiss_orbit())
    plot_aperture_at_peak(out / "aperture_at_peak_loss_node.png", loss_table, positions_at_peak, peak_node, aperture=0.005)
    write_array_csv(out / "loss_map.csv", loss_table, "particle,x0,xp0,y0,yp0,pt0,ct0,lost,lost_turn,lost_pos,x,xp,y,yp,pt,ct")
    write_array_csv(out / "aperture_peak_node_positions.csv", positions_at_peak, "x,xp,y,yp,pt,ct")
    write_json(
        out / "summary.json",
        {
            "lattice": str(ptc.lattice),
            "applied_apertures": len(applied),
            "skipped_apertures": len(skipped),
            "particles": 1000,
            "peak_loss_node": peak_node,
            "lost_particles": int((loss_table[:, 7] > 0).sum()),
            "outputs": dashboard_outputs,
        },
    )


if __name__ == "__main__":
    main()
