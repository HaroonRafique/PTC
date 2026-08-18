#!/usr/bin/env python3
"""Compare ISIS RCS design, MAD-X, and queried PyPTC rectangular apertures."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np

MADX_DIR = Path(__file__).resolve().parent
PYPTC_DIR = MADX_DIR.parents[1]
if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))

from generate_flat_file import DEFAULT_MADX, generate
from pyptc import (
    DEFAULT_LIBRARY,
    PTC,
    normalize_aperture_name,
    read_flatfile_fibres,
    read_jvt_design_aperture,
    read_madx_aperture_file,
    read_madx_aperture_tfs,
)


DEFAULT_OUTPUT_DIR = MADX_DIR / "outputs" / "aperture_comparison"
DEFAULT_DESIGN_APERTURE = MADX_DIR / "reference_apertures" / "jvt_synch_aperture.csv"
APERTURE_LATTICE_DIR = MADX_DIR / "lattices" / "02_Aperture_Lattice"
APERTURE_ASSIGNMENT_FILE = APERTURE_LATTICE_DIR / "ISIS.aperture"


def require_matplotlib(output_dir: Path):
    os.environ.setdefault("MPLCONFIGDIR", str(output_dir / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def write_records_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def aperture_rows(records) -> list[dict[str, object]]:
    return [
        {
            "name": record.name,
            "s": "" if record.s is None else record.s,
            "half_x_m": record.half_x,
            "half_y_m": record.half_y,
        }
        for record in records
    ]


def apply_and_query_ptc(library: Path, flat_file: Path) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    ptc = PTC(library)
    ptc.init_lattice(flat_file)

    fibre_index_by_name: dict[str, list[int]] = {}
    for fibre in read_flatfile_fibres(flat_file):
        fibre_index_by_name.setdefault(normalize_aperture_name(fibre.name), []).append(fibre.index)

    assignment_records = read_madx_aperture_file(APERTURE_ASSIGNMENT_FILE)
    missing: list[dict[str, object]] = []
    applied = 0
    for record in assignment_records:
        fibre_indices = fibre_index_by_name.get(normalize_aperture_name(record.name), [])
        if not fibre_indices:
            missing.append({"name": record.name, "reason": "No matching PTC fibre"})
            continue
        for fibre_index in fibre_indices:
            ptc.set_aperture(fibre_index, kind=2, x=record.half_x, y=record.half_y)
            applied += 1

    queried = ptc.all_fibre_apertures()
    drift_probe = probe_drift_aperture(ptc, flat_file)
    summary = {
        "assignment_records": len(assignment_records),
        "applied_fibre_apertures": applied,
        "queried_fibre_apertures": len(queried),
        "missing_records": len(missing),
        "drift_probe": drift_probe,
    }
    return queried, missing, summary


def probe_drift_aperture(ptc: PTC, flat_file: Path) -> dict[str, object]:
    for fibre in read_flatfile_fibres(flat_file):
        name = fibre.name.upper()
        if "_D" not in name or "_DIP" in name or fibre.length <= 0.0:
            continue
        ptc.set_aperture(fibre.index, kind=2, x=1.0e-6, y=1.0e-6)
        queried = ptc.get_aperture(fibre.index)
        ptc.set_absolute_aperture(1.0)
        _coords, loss = ptc.track_particle_ptc_with_loss([2.0e-6, 0.0, 0.0, 0.0, 0.0, 0.0], turns=1)
        return {
            "fibre_index": fibre.index,
            "name": fibre.name,
            "length_m": fibre.length,
            "stored": queried is not None
            and queried["kind"] == 2
            and abs(float(queried["x"]) - 1.0e-6) < 1.0e-15
            and abs(float(queried["y"]) - 1.0e-6) < 1.0e-15,
            **loss,
        }
    return {"stored": False, "reason": "No drift-like fibre found"}


def plot_overlay(path: Path, design, madx, pyptc_rows: list[dict[str, object]]) -> None:
    plt = require_matplotlib(path.parent)
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    series = [
        ("Design JVT", np.asarray([r.s for r in design], dtype=float), np.asarray([r.half_x for r in design]), np.asarray([r.half_y for r in design]), "-"),
        ("MAD-X APERTURE", np.asarray([r.s for r in madx], dtype=float), np.asarray([r.half_x for r in madx]), np.asarray([r.half_y for r in madx]), "--"),
        (
            "PyPTC queried",
            np.asarray([float(r["s"]) for r in pyptc_rows], dtype=float),
            np.asarray([float(r["x"]) for r in pyptc_rows], dtype=float),
            np.asarray([float(r["y"]) for r in pyptc_rows], dtype=float),
            ":",
        ),
    ]

    for label, s, half_x, half_y, linestyle in series:
        mask_x = np.isfinite(s) & np.isfinite(half_x) & (half_x > 0.0)
        mask_y = np.isfinite(s) & np.isfinite(half_y) & (half_y > 0.0)
        axes[0].plot(s[mask_x], half_x[mask_x] * 1000.0, linestyle=linestyle, label=label)
        axes[1].plot(s[mask_y], half_y[mask_y] * 1000.0, linestyle=linestyle, label=label)

    axes[0].set_ylabel("Horizontal half aperture [mm]")
    axes[1].set_ylabel("Vertical half aperture [mm]")
    axes[1].set_xlabel("s [m]")
    for axis in axes:
        axis.grid(True, alpha=0.25)
        axis.legend(loc="best")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--madx", type=Path, default=DEFAULT_MADX)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--design-aperture", type=Path, default=DEFAULT_DESIGN_APERTURE)
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    generation_args = argparse.Namespace(lattice="aperture", madx=args.madx, output_dir=output_dir / "flat_file")
    generation = generate(generation_args)

    flat_file = Path(generation["flat_file"])
    madx_aperture_file = Path(generation["madx_aperture_file"])
    design = read_jvt_design_aperture(args.design_aperture)
    madx = read_madx_aperture_tfs(madx_aperture_file)
    pyptc_rows, missing_rows, summary = apply_and_query_ptc(args.library, flat_file)

    design_csv = output_dir / "design_aperture.csv"
    madx_csv = output_dir / "madx_aperture.csv"
    pyptc_csv = output_dir / "pyptc_apertures.csv"
    missing_csv = output_dir / "missing_pyptc_apertures.csv"
    plot_path = output_dir / "isis_rcs_aperture_overlay.png"

    write_records_csv(design_csv, aperture_rows(design), ["name", "s", "half_x_m", "half_y_m"])
    write_records_csv(madx_csv, aperture_rows(madx), ["name", "s", "half_x_m", "half_y_m"])
    write_records_csv(pyptc_csv, pyptc_rows, ["fibre_index", "name", "s_start", "s_end", "s", "kind", "r1", "r2", "x", "y", "dx", "dy"])
    write_records_csv(missing_csv, missing_rows, ["name", "reason"])
    plot_overlay(plot_path, design, madx, pyptc_rows)

    summary.update(
        {
            "flat_file": str(flat_file),
            "madx_aperture_file": str(madx_aperture_file),
            "design_csv": str(design_csv),
            "madx_csv": str(madx_csv),
            "pyptc_csv": str(pyptc_csv),
            "missing_csv": str(missing_csv),
            "plot": str(plot_path),
        }
    )
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
