#!/usr/bin/env python3
"""Load the default flat file and plot bare Twiss and closed orbit."""

from __future__ import annotations

from common import init_ptc, output_dir, plot_bare_twiss_closed_orbit, write_dict_csv, write_json


def main() -> None:
    out = output_dir("01_plot_bare_twiss_closed_orbit")
    ptc = init_ptc()
    rows = ptc.all_node_twiss_orbit()
    tunes = ptc.tunes()
    chroma = ptc.chromaticities()
    plot_bare_twiss_closed_orbit(out / "bare_twiss_closed_orbit.png", rows, tunes, chroma)
    write_dict_csv(out / "bare_twiss_closed_orbit.csv", rows)
    write_json(out / "summary.json", {"lattice": str(ptc.lattice), "machine": ptc.machine_summary(), "tunes": tunes, "chromaticities": chroma})


if __name__ == "__main__":
    main()
