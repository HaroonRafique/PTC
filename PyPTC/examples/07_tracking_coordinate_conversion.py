#!/usr/bin/env python3
"""Show how PyPTC maps a Python energy offset to PTC momentum deviation.

The example tracks particles with total-energy offsets corresponding to a
small, symmetric scan in relative momentum deviation. It compares tune slopes
from the tracking helper with the chromaticity API for the default ISIS RCS
lattice. This is a coordinate-conversion example, not a benchmark acceptance
test.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np

from common import init_ptc, output_dir, require_matplotlib, write_json


DELTAS = np.asarray([-1.0e-4, -5.0e-5, 0.0, 5.0e-5, 1.0e-4], dtype=float)
TRACKING_TURNS = 8192
TRANSVERSE_AMPLITUDE_M = 1.0e-3


def sha256(path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def energy_offset_for_delta(delta: float, p0c: float, beta0: float) -> float:
    """Return total-energy offset for a requested relative momentum offset."""

    e0 = p0c / beta0
    mass_squared = max(0.0, e0 * e0 - p0c * p0c)
    momentum = p0c * (1.0 + float(delta))
    return float(np.sqrt(mass_squared + momentum * momentum) - e0)


def central_slope(rows: list[dict[str, float | int | bool]], plane: str, step: float) -> float:
    lower = next(row for row in rows if np.isclose(row["delta_requested"], -step, rtol=0.0, atol=1.0e-15))
    upper = next(row for row in rows if np.isclose(row["delta_requested"], step, rtol=0.0, atol=1.0e-15))
    return float((upper[f"q{plane}"] - lower[f"q{plane}"]) / (2.0 * step))


def write_scan_csv(path: Path, rows: list[dict[str, float | int | bool]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def plot_results(path, rows: list[dict[str, float | int | bool]], chromaticities: dict[str, float]) -> None:
    plt = require_matplotlib(path.parent)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)
    delta = np.asarray([float(row["delta_requested"]) for row in rows])
    q0 = {"x": float(rows[2]["qx"]), "y": float(rows[2]["qy"])}
    for axis, plane, api_key in ((axes[0], "x", "chromx"), (axes[1], "y", "chromy")):
        delta_units = delta / 1.0e-4
        tune_shift = np.asarray([float(row[f"q{plane}"]) for row in rows]) - q0[plane]
        axis.scatter(delta_units, tune_shift, color="tab:blue", label="tracked with PyPTC helper")
        axis.plot(delta_units, float(chromaticities[api_key]) * delta, "--", color="tab:orange", label="chromaticity API linear prediction")
        axis.axhline(0.0, color="black", linewidth=0.7)
        axis.set_xlabel(r"requested relative momentum deviation, delta [$10^{-4}$]")
        axis.set_ylabel(f"fractional Q{plane} shift from zero-offset particle")
        axis.set_title(f"Horizontal tune" if plane == "x" else "Vertical tune")
        axis.grid(True, alpha=0.25)
        axis.legend(fontsize=8)
    fig.suptitle(f"Tracking coordinate conversion ({TRACKING_TURNS} turns per particle)")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    out = output_dir("07_tracking_coordinate_conversion")
    ptc = init_ptc()
    p0c = ptc.scalar("ptc_get_p0c_")
    beta0 = ptc.scalar("ptc_get_beta0_")
    chromaticities = ptc.chromaticities()
    energy_offsets = np.asarray([energy_offset_for_delta(delta, p0c, beta0) for delta in DELTAS])
    bunch = np.column_stack(
        (
            np.full(DELTAS.size, TRANSVERSE_AMPLITUDE_M),
            np.zeros(DELTAS.size),
            np.full(DELTAS.size, TRANSVERSE_AMPLITUDE_M),
            np.zeros(DELTAS.size),
            np.zeros(DELTAS.size),
            energy_offsets,
        )
    )
    diagnostics = ptc.particle_diagnostics(
        bunch,
        turns=TRACKING_TURNS,
        min_tune_turns=TRACKING_TURNS,
    )

    rows: list[dict[str, float | int | bool]] = []
    for delta, d_e, diagnostic in zip(DELTAS, energy_offsets, diagnostics):
        rows.append(
            {
                "delta_requested": float(delta),
                "dE_gev": float(d_e),
                "qx": float(diagnostic["qx"]),
                "qy": float(diagnostic["qy"]),
                "completed_turns": int(diagnostic["completed_turns"]),
                "lost": bool(diagnostic["lost"]),
            }
        )

    slopes = {
        f"central_step_{step:g}": {
            "dqx_d_delta": central_slope(rows, "x", step),
            "dqy_d_delta": central_slope(rows, "y", step),
        }
        for step in (5.0e-5, 1.0e-4)
    }
    write_scan_csv(out / "coordinate_scan.csv", rows)
    plot_results(out / "coordinate_scan.png", rows, chromaticities)
    write_json(
        out / "summary.json",
        {
            "lattice": str(ptc.lattice),
            "lattice_sha256": sha256(ptc.lattice),
            "library_sha256": sha256(ptc.library),
            "example_sha256": sha256(Path(__file__).resolve()),
            "pyptc_core_sha256": sha256(Path(__file__).resolve().parents[1] / "pyptc" / "core.py"),
            "machine": ptc.machine_summary(),
            "p0c_gev": p0c,
            "beta0": beta0,
            "coordinate_contract": {
                "python_input": "x, xp, y, yp, z, dE; dE is total-energy deviation in GeV",
                "ptc_fifth_coordinate": "delta = p/p0 - 1",
                "energy_conversion": "dE = sqrt(m^2 + (p0c*(1+delta))^2) - p0c/beta0",
                "longitudinal_conversion": "L = -z/beta0",
            },
            "tracking_turns_per_particle": TRACKING_TURNS,
            "chromaticities_from_api_per_delta": chromaticities,
            "tracking_central_slopes_per_delta": slopes,
            "scope": "coordinate-conversion example; not an acceptance or tolerance test",
            "outputs": ["coordinate_scan.csv", "coordinate_scan.png"],
        },
    )
    print(f"Wrote coordinate-conversion example to {out}")


if __name__ == "__main__":
    main()
