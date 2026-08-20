#!/usr/bin/env python3
"""Track a 1000-particle PyParticleBunch bunch and plot separate dashboards."""

from __future__ import annotations

from common import init_ptc, make_standard_bunch, output_dir, write_array_csv, write_diagnostic_outputs, write_json


def main() -> None:
    out = output_dir("02_track_bunch_dashboard")
    ptc = init_ptc()
    bunch = make_standard_bunch(ptc, particles=1000)
    diagnostics = ptc.particle_diagnostics(bunch, turns=64, min_tune_turns=8)
    outputs = write_diagnostic_outputs(out, diagnostics)
    write_array_csv(out / "bunch_initial.csv", bunch, "x,xp,y,yp,z,dE")
    write_json(out / "summary.json", {"lattice": str(ptc.lattice), "particles": 1000, "tune_turns": 64, "outputs": outputs})


if __name__ == "__main__":
    main()
