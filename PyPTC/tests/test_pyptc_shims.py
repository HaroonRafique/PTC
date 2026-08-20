#!/usr/bin/env python3
"""Smoke tests for the first PyPTC shim layer.

The test writes diagnostic PNGs so failures can be inspected visually:

  python3 PyPTC/tests/test_pyptc_shims.py --output-dir PyPTC/test_outputs/shims
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

PYPTC_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PYPTC_DIR.parent
if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))

from pyptc import (
    DEFAULT_LATTICE,
    DEFAULT_LIBRARY,
    LATEST_SURVEY_REFERENCE_ERROR_TABLE,
    PTC,
    ensure_default_lattice,
    generate_matched_gaussian_4d,
    read_madx_error_table,
    resolve_fibre_index,
)


def require_matplotlib(output_dir: Path):
    os.environ.setdefault("MPLCONFIGDIR", str(output_dir / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def write_array_csv(path: Path, array: np.ndarray, header: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(path, np.asarray(array, dtype=float), delimiter=",", header=header, comments="")


def plot_optics(path: Path, rows: list[dict[str, float | int]], tunes: dict, chroma: dict) -> None:
    plt = require_matplotlib(path.parent)
    s = np.cumsum([float(row["length"]) for row in rows])
    betax = np.array([float(row["betax"]) for row in rows])
    betay = np.array([float(row["betay"]) for row in rows])
    alphax = np.array([float(row["alphax"]) for row in rows])
    alphay = np.array([float(row["alphay"]) for row in rows])
    etax = np.array([float(row["etax"]) for row in rows])
    etapx = np.array([float(row["etapx"]) for row in rows])
    etay = np.array([float(row["etay"]) for row in rows])
    etapy = np.array([float(row["etapy"]) for row in rows])
    orbitx = np.array([float(row["orbitx"]) for row in rows])
    orbitpx = np.array([float(row["orbitpx"]) for row in rows])
    orbity = np.array([float(row["orbity"]) for row in rows])
    orbitpy = np.array([float(row["orbitpy"]) for row in rows])

    fig, axes = plt.subplots(4, 1, figsize=(11, 11), sharex=True)
    axes[0].plot(s, betax, label="betax")
    axes[0].plot(s, betay, label="betay")
    axes[0].set_ylabel("beta [m]")
    axes[0].legend(loc="upper right")
    axes[0].set_title(
        f"Tunes qx={tunes['qx']:.6g}, qy={tunes['qy']:.6g}; "
        f"chroma x={chroma['chromx']:.6g}, y={chroma['chromy']:.6g}"
    )
    axes[1].plot(s, alphax, label="alphax")
    axes[1].plot(s, alphay, label="alphay")
    axes[1].set_ylabel("alpha [-]")
    axes[1].legend(loc="upper right")
    axes[2].plot(s, etax, label="etax")
    axes[2].plot(s, etapx, label="etapx")
    axes[2].plot(s, etay, label="etay")
    axes[2].plot(s, etapy, label="etapy")
    axes[2].set_ylabel("dispersion")
    axes[2].legend(loc="upper right", ncol=4)
    axes[3].plot(s, orbitx * 1.0e3, label="orbit x [mm]")
    axes[3].plot(s, orbity * 1.0e3, label="orbit y [mm]")
    axes[3].plot(s, orbitpx * 1.0e3, label="orbit px [mrad]")
    axes[3].plot(s, orbitpy * 1.0e3, label="orbit py [mrad]")
    axes[3].set_xlabel("s over PTC/ORBIT nodes [m]")
    axes[3].set_ylabel("closed orbit")
    axes[3].legend(loc="upper right", ncol=4)
    for ax in axes:
        ax.grid(which="both", ls=":", lw=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_madx_error_table(path: Path, records) -> None:
    plt = require_matplotlib(path.parent)
    names = [record.name for record in records]
    x = np.arange(len(records))
    dx = np.array([record.dx for record in records])
    dy = np.array([record.dy for record in records])
    ds = np.array([record.ds for record in records])
    dtheta = np.array([record.dtheta for record in records])
    dphi = np.array([record.dphi for record in records])
    dpsi = np.array([record.dpsi for record in records])

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    axes[0].bar(x - 0.25, dx * 1.0e3, width=0.25, label="DX")
    axes[0].bar(x, dy * 1.0e3, width=0.25, label="DY")
    axes[0].bar(x + 0.25, ds * 1.0e3, width=0.25, label="DS")
    axes[0].set_ylabel("translation [mm]")
    axes[0].legend(loc="upper right", ncol=3)
    axes[0].grid(True, alpha=0.25)
    axes[1].bar(x - 0.25, dtheta * 1.0e3, width=0.25, label="DTHETA")
    axes[1].bar(x, dphi * 1.0e3, width=0.25, label="DPHI")
    axes[1].bar(x + 0.25, dpsi * 1.0e3, width=0.25, label="DPSI")
    axes[1].set_ylabel("rotation [mrad]")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(names, rotation=90, fontsize=7)
    axes[1].legend(loc="upper right", ncol=3)
    axes[1].grid(True, alpha=0.25)
    axes[1].set_xlabel("MAD-X error table element")
    fig.suptitle("MAD-X EFIELD table misalignments")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def run_madx_error_table_case(args: argparse.Namespace) -> dict:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if not args.madx_error_table.exists():
        raise FileNotFoundError(f"MAD-X error table not found: {args.madx_error_table}")

    records = read_madx_error_table(args.madx_error_table, nonzero=False)
    assert records
    plot_madx_error_table(output_dir / "06_madx_error_table_misalignments.png", records)
    error_table_rows = np.array(
        [[record.dx, record.dy, record.ds, record.dtheta, record.dphi, record.dpsi] for record in records],
        dtype=float,
    )
    write_array_csv(output_dir / "madx_error_table_misalignments.csv", error_table_rows, "dx,dy,ds,dtheta,dphi,dpsi")

    ptc = PTC(args.library)
    ptc.init_lattice(args.lattice)
    bare_rows = ptc.all_node_twiss_orbit()
    applied_errors = ptc.apply_madx_error_table(args.madx_error_table, nonzero=False)
    ptc.update_twiss()
    table_rows = ptc.all_node_twiss_orbit()
    full_table_orbit = plot_orbit_response(output_dir / "pyptc_bare_vs_jan26_error_table_generated_lattice.png", bare_rows, table_rows)
    max_delta_x = float(np.max(np.abs(full_table_orbit[:, 5])))
    max_delta_y = float(np.max(np.abs(full_table_orbit[:, 6])))
    assert max_delta_x > 1.0e-4 or max_delta_y > 1.0e-4
    if len(records) == 38 and len(applied_errors) != 38:
        raise AssertionError(
            "Jan26 error table resolved to "
            f"{len(applied_errors)} fibre applications for {len(records)} records; "
            "this usually means the legacy sliced readiness lattice was used instead "
            "of the generated simplified lattice."
        )
    write_array_csv(
        output_dir / "pyptc_bare_vs_jan26_error_table_generated_lattice.csv",
        full_table_orbit,
        "s,bare_orbitx,error_table_orbitx,bare_orbity,error_table_orbity,delta_orbitx,delta_orbity",
    )

    applied_rows = np.array(
        [
            [
                record.fibre_index,
                record.occurrence,
                record.dx,
                record.dy,
                record.ds,
                record.dtheta,
                record.dphi,
                record.dpsi,
            ]
            for record in applied_errors
        ],
        dtype=float,
    )
    write_array_csv(
        output_dir / "applied_madx_error_table.csv",
        applied_rows,
        "fibre_index,occurrence,dx,dy,ds,dtheta,dphi,dpsi",
    )

    return {
        "table": str(args.madx_error_table.resolve()),
        "records": len(records),
        "applied": len(applied_errors),
        "max_abs_dx_m": float(max(abs(record.dx) for record in records)),
        "max_abs_dy_m": float(max(abs(record.dy) for record in records)),
        "max_abs_rotation_rad": float(max(max(abs(record.dtheta), abs(record.dphi), abs(record.dpsi)) for record in records)),
        "max_orbit_delta_x_m": max_delta_x,
        "max_orbit_delta_y_m": max_delta_y,
        "orbit_png": "pyptc_bare_vs_jan26_error_table_generated_lattice.png",
    }


def run_madx_error_table_case_subprocess(args: argparse.Namespace) -> dict:
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "_run_madx_error_table_case",
        "--library",
        str(args.library),
        "--lattice",
        str(args.lattice),
        "--output-dir",
        str(args.output_dir),
        "--madx-error-table",
        str(args.madx_error_table),
    ]
    subprocess.run(cmd, check=True, cwd=PYPTC_DIR)
    return json.loads((args.output_dir / "madx_error_table_summary.json").read_text(encoding="utf-8"))


def run_madx_pyptc_comparison_artifact(args: argparse.Namespace, output_dir: Path) -> dict:
    comparison_dir = output_dir / "madx_pyptc_closed_orbit_comparison"
    cmd = [
        sys.executable,
        str(PYPTC_DIR / "workflows" / "madx" / "compare_madx_pyptc_closed_orbits.py"),
        "--library",
        str(args.library),
        "--madx-error-table",
        str(args.madx_error_table),
        "--output-dir",
        str(comparison_dir),
        "--response-threshold",
        "0.0",
    ]
    subprocess.run(cmd, check=True, cwd=PYPTC_DIR)
    summary = json.loads((comparison_dir / "summary.json").read_text(encoding="utf-8"))
    shutil.copy2(
        comparison_dir / "madx_vs_pyptc_closed_orbit_comparison.png",
        output_dir / "07_madx_vs_pyptc_closed_orbit_comparison.png",
    )
    shutil.copy2(
        comparison_dir / "madx_vs_pyptc_closed_orbit_comparison.csv",
        output_dir / "07_madx_vs_pyptc_closed_orbit_comparison.csv",
    )
    return summary


def plot_orbit_response(path: Path, bare: list[dict[str, float | int]], edited: list[dict[str, float | int]]) -> np.ndarray:
    plt = require_matplotlib(path.parent)
    s = np.cumsum([float(row["length"]) for row in bare])
    bare_x = np.array([float(row["orbitx"]) for row in bare])
    bare_y = np.array([float(row["orbity"]) for row in bare])
    edited_x = np.array([float(row["orbitx"]) for row in edited])
    edited_y = np.array([float(row["orbity"]) for row in edited])

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    axes[0].plot(s, bare_x * 1.0e3, label="bare x")
    axes[0].plot(s, edited_x * 1.0e3, label="misaligned x")
    axes[0].set_ylabel("x closed orbit [mm]")
    axes[0].legend(loc="upper right")
    axes[1].plot(s, bare_y * 1.0e3, label="bare y")
    axes[1].plot(s, edited_y * 1.0e3, label="misaligned y")
    axes[1].set_xlabel("s over PTC/ORBIT nodes [m]")
    axes[1].set_ylabel("y closed orbit [mm]")
    axes[1].legend(loc="upper right")
    for ax in axes:
        ax.grid(which="both", ls=":", lw=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return np.column_stack([s, bare_x, edited_x, bare_y, edited_y, edited_x - bare_x, edited_y - bare_y])


def action_from_twiss(bunch: np.ndarray, twiss: dict[str, float | int], plane: str) -> np.ndarray:
    if plane == "x":
        coord = bunch[:, 0]
        angle = bunch[:, 1]
        alpha = float(twiss["alphax"])
        beta = float(twiss["betax"])
    elif plane == "y":
        coord = bunch[:, 2]
        angle = bunch[:, 3]
        alpha = float(twiss["alphay"])
        beta = float(twiss["betay"])
    else:
        raise ValueError(f"Unknown plane: {plane}")
    gamma = (1.0 + alpha**2) / beta
    return 0.5 * (gamma * coord**2 + 2.0 * alpha * coord * angle + beta * angle**2)


def phase_from_twiss(bunch: np.ndarray, twiss: dict[str, float | int], plane: str) -> np.ndarray:
    if plane == "x":
        coord = bunch[:, 0]
        angle = bunch[:, 1]
        alpha = float(twiss["alphax"])
        beta = float(twiss["betax"])
    elif plane == "y":
        coord = bunch[:, 2]
        angle = bunch[:, 3]
        alpha = float(twiss["alphay"])
        beta = float(twiss["betay"])
    else:
        raise ValueError(f"Unknown plane: {plane}")
    u = coord / np.sqrt(beta)
    up = alpha * coord / np.sqrt(beta) + np.sqrt(beta) * angle
    return np.mod(np.arctan2(up, u) / (2.0 * np.pi), 1.0)


def padded_limits(*arrays: np.ndarray, factor: float = 1.05) -> tuple[float, float]:
    values = np.concatenate([np.asarray(array, dtype=float).ravel() for array in arrays])
    vmin = float(np.min(values))
    vmax = float(np.max(values))
    if np.isclose(vmin, vmax):
        delta = abs(vmin) * 0.05 + 1.0e-12
        return vmin - delta, vmax + delta
    center = 0.5 * (vmin + vmax)
    half = 0.5 * (vmax - vmin) * factor
    return center - half, center + half


def heatmap(ax, x_data: np.ndarray, y_data: np.ndarray, x_label: str, y_label: str, title: str, xlims=None, ylims=None, bins: int = 96):
    if xlims is None:
        xlims = padded_limits(x_data)
    if ylims is None:
        ylims = padded_limits(y_data)
    ax.hist2d(x_data, y_data, bins=bins, range=[xlims, ylims])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(which="both", ls=":", lw=0.4, alpha=0.7)


def plot_bunch_dashboard(
    path: Path,
    initial: np.ndarray,
    final: np.ndarray,
    losses: list[dict],
    twiss: dict[str, float | int],
    tunes: dict[str, float],
) -> None:
    plt = require_matplotlib(path.parent)
    lost = np.array([bool(info["lost"]) for info in losses], dtype=bool)

    jx = action_from_twiss(final, twiss, "x")
    jy = action_from_twiss(final, twiss, "y")
    x_phase = phase_from_twiss(final, twiss, "x")
    y_phase = phase_from_twiss(final, twiss, "y")
    qx = np.full(final.shape[0], tunes["qx"])
    qy = np.full(final.shape[0], tunes["qy"])

    xlims_mm = padded_limits(initial[:, 0] * 1.0e3, final[:, 0] * 1.0e3)
    xp_lims_mrad = padded_limits(initial[:, 1] * 1.0e3, final[:, 1] * 1.0e3)
    ylims_mm = padded_limits(initial[:, 2] * 1.0e3, final[:, 2] * 1.0e3)
    yp_lims_mrad = padded_limits(initial[:, 3] * 1.0e3, final[:, 3] * 1.0e3)
    z_lims = padded_limits(initial[:, 4], final[:, 4])
    de_lims_mev = padded_limits(initial[:, 5] * 1.0e3, final[:, 5] * 1.0e3)

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle("PyPTC Bunch Dashboard: before/after standalone PTC tracking", fontsize=16)

    heatmap(axes[0, 0], qx, qy, "qx", "qy", "tune footprint", xlims=(0.0, 1.0), ylims=(0.0, 1.0))
    axes[0, 0].scatter([tunes["qx"]], [tunes["qy"]], s=30, c="red", marker="+")
    heatmap(axes[0, 1], qx, jx, "qx", "Jx", "horizontal tune vs action", xlims=(0.0, 1.0))
    heatmap(
        axes[0, 2],
        final[:, 0] * 1.0e3,
        final[:, 1] * 1.0e3,
        "x [mm]",
        "xp [mrad]",
        "horizontal phase space",
        xlims=xlims_mm,
        ylims=xp_lims_mrad,
    )
    axes[0, 2].scatter(initial[:, 0] * 1.0e3, initial[:, 1] * 1.0e3, s=4, c="white", alpha=0.35)
    heatmap(
        axes[0, 3],
        final[:, 0] * 1.0e3,
        final[:, 2] * 1.0e3,
        "x [mm]",
        "y [mm]",
        "real space",
        xlims=xlims_mm,
        ylims=ylims_mm,
    )
    axes[0, 3].scatter(initial[:, 0] * 1.0e3, initial[:, 2] * 1.0e3, s=4, c="white", alpha=0.35)

    heatmap(axes[1, 0], qx, qy, "qx", "qy", "tune footprint zoom", xlims=(0.25, 0.45), ylims=(0.45, 0.85))
    axes[1, 0].scatter([tunes["qx"]], [tunes["qy"]], s=30, c="red", marker="+")
    heatmap(axes[1, 1], qy, jy, "qy", "Jy", "vertical tune vs action", xlims=(0.0, 1.0))
    heatmap(
        axes[1, 2],
        final[:, 2] * 1.0e3,
        final[:, 3] * 1.0e3,
        "y [mm]",
        "yp [mrad]",
        "vertical phase space",
        xlims=ylims_mm,
        ylims=yp_lims_mrad,
    )
    axes[1, 2].scatter(initial[:, 2] * 1.0e3, initial[:, 3] * 1.0e3, s=4, c="white", alpha=0.35)
    heatmap(
        axes[1, 3],
        final[:, 4],
        final[:, 5] * 1.0e3,
        "z [m]",
        "dE [MeV]",
        "longitudinal phase space",
        xlims=z_lims,
        ylims=de_lims_mev,
    )
    axes[1, 3].scatter(initial[:, 4], initial[:, 5] * 1.0e3, s=4, c="white", alpha=0.35)

    if lost.any():
        fig.text(0.01, 0.01, f"Lost particles in tracked bunch: {int(lost.sum())}", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_loss_map(path: Path, loss_table: np.ndarray, node_rows: list[dict[str, float | int]]) -> None:
    plt = require_matplotlib(path.parent)
    s_nodes = np.cumsum([float(row["length"]) for row in node_rows])
    loss_positions = loss_table[loss_table[:, 2] > 0, 2].astype(int)
    counts = np.zeros_like(s_nodes)
    for pos in loss_positions:
        if 1 <= pos <= len(counts):
            counts[pos - 1] += 1

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(s_nodes, counts, where="mid", label="loss count")
    ax.set_xlabel("s over PTC/ORBIT nodes [m]")
    ax.set_ylabel("lost particles")
    ax.set_title("Aperture loss map")
    ax.grid(which="both", ls=":", lw=0.5)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def track_ptc_to_node(ptc: PTC, coords: np.ndarray, node_pos: int) -> np.ndarray:
    tracked = np.asarray(coords, dtype=float).copy()
    for node_index in range(max(0, node_pos)):
        tracked = ptc.track_particle_ptc(node_index, tracked)
    return tracked


def aperture_boundary_xy(half_x: float, half_y: float) -> tuple[np.ndarray, np.ndarray]:
    x = np.array([-half_x, half_x, half_x, -half_x, -half_x])
    y = np.array([-half_y, -half_y, half_y, half_y, -half_y])
    return x * 1.0e3, y * 1.0e3


def plot_aperture_at_peak_loss(
    path: Path,
    peak_node: int,
    half_x: float,
    half_y: float,
    loss_table: np.ndarray,
    node_rows: list[dict[str, float | int]],
    positions_at_peak: np.ndarray,
) -> None:
    plt = require_matplotlib(path.parent)
    s_nodes = np.cumsum([float(row["length"]) for row in node_rows])
    peak_s = float(s_nodes[peak_node - 1]) if 1 <= peak_node <= len(s_nodes) else float("nan")
    reached = loss_table[:, 2] == 0
    reached |= loss_table[:, 2] >= peak_node
    lost_here = loss_table[:, 2] == peak_node
    inside_at_peak = (np.abs(positions_at_peak[:, 0]) <= half_x) & (np.abs(positions_at_peak[:, 2]) <= half_y)
    survived_here = reached & ~lost_here & inside_at_peak
    bx, by = aperture_boundary_xy(half_x, half_y)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    axes[0].plot(bx, by, color="black", lw=1.5, label="rectangular aperture")
    axes[0].scatter(
        positions_at_peak[survived_here, 0] * 1.0e3,
        positions_at_peak[survived_here, 2] * 1.0e3,
        s=18,
        alpha=0.7,
        label="reached / survived",
    )
    axes[0].scatter(
        positions_at_peak[lost_here, 0] * 1.0e3,
        positions_at_peak[lost_here, 2] * 1.0e3,
        s=28,
        alpha=0.9,
        label="lost at peak node",
    )
    axes[0].set_xlabel("x [mm]")
    axes[0].set_ylabel("y [mm]")
    axes[0].set_title(f"x-y at node {peak_node}, s={peak_s:.3f} m")
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].grid(which="both", ls=":", lw=0.5)
    axes[0].legend(loc="best")

    axes[1].scatter(
        positions_at_peak[survived_here, 0] * 1.0e3,
        positions_at_peak[survived_here, 1] * 1.0e3,
        s=18,
        alpha=0.7,
        label="reached / survived",
    )
    axes[1].scatter(
        positions_at_peak[lost_here, 0] * 1.0e3,
        positions_at_peak[lost_here, 1] * 1.0e3,
        s=28,
        alpha=0.9,
        label="lost at peak node",
    )
    axes[1].set_xlabel("x [mm]")
    axes[1].set_ylabel("xp [mrad]")
    axes[1].set_title("horizontal phase space at peak-loss node")
    axes[1].grid(which="both", ls=":", lw=0.5)
    axes[1].legend(loc="best")
    axes[2].scatter(
        positions_at_peak[survived_here, 2] * 1.0e3,
        positions_at_peak[survived_here, 3] * 1.0e3,
        s=18,
        alpha=0.7,
        label="reached / survived",
    )
    axes[2].scatter(
        positions_at_peak[lost_here, 2] * 1.0e3,
        positions_at_peak[lost_here, 3] * 1.0e3,
        s=28,
        alpha=0.9,
        label="lost at peak node",
    )
    axes[2].set_xlabel("y [mm]")
    axes[2].set_ylabel("yp [mrad]")
    axes[2].set_title("vertical phase space at peak-loss node")
    axes[2].grid(which="both", ls=":", lw=0.5)
    axes[2].legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def run(args: argparse.Namespace) -> dict:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for old_png in output_dir.glob("*.png"):
        old_png.unlink()

    ptc = PTC(args.library)
    ptc.init_lattice(args.lattice)

    assert ptc.api_level() >= 2
    summary = ptc.machine_summary()
    assert int(summary["n_nodes"]) > 0

    tunes = ptc.tunes()
    chroma = ptc.chromaticities()
    assert np.isfinite([*tunes.values(), *chroma.values()]).all()

    fibre_index = resolve_fibre_index(args.lattice, args.element, args.occurrence)
    bare_rows = ptc.all_node_twiss_orbit()
    plot_optics(output_dir / "01_ptc_twiss_orbit_tunes_chroma.png", bare_rows, tunes, chroma)

    twiss0 = ptc.node_twiss_orbit(0)
    bunch = generate_matched_gaussian_4d(
        n=args.particles,
        emittance_x=args.emit_x,
        emittance_y=args.emit_y,
        alpha_x=float(twiss0["alphax"]),
        beta_x=float(twiss0["betax"]),
        alpha_y=float(twiss0["alphay"]),
        beta_y=float(twiss0["betay"]),
        x_limit=args.limit,
        y_limit=args.limit,
        seed=args.seed,
    )
    final_bunch, losses = ptc.track_bunch_with_losses(bunch, turns=args.turns)
    assert final_bunch.shape == bunch.shape
    plot_bunch_dashboard(
        output_dir / "03_bunch_dashboard_before_after_tracking.png",
        bunch,
        final_bunch,
        losses,
        twiss0,
        tunes,
    )

    ptc.set_misalignment(fibre_index, dx=args.dx)
    ptc.update_twiss()
    misaligned_rows = ptc.all_node_twiss_orbit()
    orbit_response = plot_orbit_response(
        output_dir / "02_closed_orbits_bare_vs_misaligned.png",
        bare_rows,
        misaligned_rows,
    )
    assert np.max(np.abs(orbit_response[:, 5])) > 0.0

    original_absolute_aperture = ptc.absolute_aperture()
    ptc.set_aperture(fibre_index, kind=2, x=args.loss_map_aperture, y=args.loss_map_aperture)
    ptc.set_absolute_aperture(args.loss_map_aperture)
    loss_rows = []
    initial_loss_coords = []
    for x0 in np.linspace(-0.95 * args.loss_map_aperture, 0.95 * args.loss_map_aperture, args.loss_map_particles):
        coords, info = ptc.track_particle_ptc_with_loss([x0, 0.0, 0.0, 0.0, 0.0, 0.0], turns=1)
        initial_loss_coords.append([x0, 0.0, 0.0, 0.0, 0.0, 0.0])
        loss_rows.append([x0, int(info["lost"]), int(info["lost_pos"]), int(info["lost_turn"]), *coords.tolist()])
    ptc.set_absolute_aperture(original_absolute_aperture)
    loss_table = np.asarray(loss_rows, dtype=float)
    assert np.any(loss_table[:, 1] > 0)
    plot_loss_map(output_dir / "04_aperture_loss_map.png", loss_table, misaligned_rows)
    lost_positions = loss_table[loss_table[:, 2] > 0, 2].astype(int)
    unique_positions, unique_counts = np.unique(lost_positions, return_counts=True)
    peak_loss_node = int(unique_positions[np.argmax(unique_counts)])
    ptc.set_absolute_aperture(1.0)
    positions_at_peak = np.array([track_ptc_to_node(ptc, np.asarray(coords, dtype=float), peak_loss_node) for coords in initial_loss_coords])
    ptc.set_absolute_aperture(original_absolute_aperture)
    plot_aperture_at_peak_loss(
        output_dir / "05_aperture_at_peak_loss_node.png",
        peak_loss_node,
        args.loss_map_aperture,
        args.loss_map_aperture,
        loss_table,
        misaligned_rows,
        positions_at_peak,
    )

    ptc.set_acceleration(False)
    ptc.set_acceleration(True)
    ptc.set_ramping(False)
    ptc.set_ramping(True)
    ptc.set_modulation(False)
    ptc.set_modulation(True)
    ptc.set_cavity(False)
    ptc.set_cavity(True)
    ptc.store_orbit_state()
    ptc.use_orbit_state()
    ptc.set_orbit_time(0.0)
    ptc.configure_ac_magnet(fibre_index, dc=1.0, amplitude=0.0, phase_turns=0.0, d_ac=0.0, bn=[0.0], an=[0.0])

    madx_error_table_summary = run_madx_error_table_case_subprocess(args)
    madx_pyptc_comparison_summary = run_madx_pyptc_comparison_artifact(args, output_dir)

    write_array_csv(output_dir / "initial_bunch.csv", bunch, "x,xp,y,yp,z,dE")
    write_array_csv(output_dir / "final_bunch.csv", final_bunch, "x,xp,y,yp,z,dE")
    write_array_csv(output_dir / "closed_orbit_response.csv", orbit_response, "s,bare_orbitx,misaligned_orbitx,bare_orbity,misaligned_orbity,delta_orbitx,delta_orbity")
    write_array_csv(output_dir / "loss_map.csv", loss_table, "initial_x,lost,lost_pos,lost_turn,final_x,final_xp,final_y,final_yp,final_pt,final_ct")
    write_array_csv(output_dir / "aperture_peak_node_positions.csv", positions_at_peak, "x,xp,y,yp,pt,ct")

    pngs = sorted(path.name for path in output_dir.glob("*.png"))
    required_pngs = {
        "01_ptc_twiss_orbit_tunes_chroma.png",
        "02_closed_orbits_bare_vs_misaligned.png",
        "03_bunch_dashboard_before_after_tracking.png",
        "04_aperture_loss_map.png",
        "05_aperture_at_peak_loss_node.png",
        "06_madx_error_table_misalignments.png",
        "07_madx_vs_pyptc_closed_orbit_comparison.png",
        "pyptc_bare_vs_jan26_error_table_generated_lattice.png",
    }
    missing_pngs = sorted(required_pngs.difference(pngs))
    assert not missing_pngs, f"Missing required PNG test outputs: {missing_pngs}"

    result = {
        "library": str(args.library.resolve()),
        "lattice": str(args.lattice.resolve()),
        "machine": summary,
        "tunes": tunes,
        "chromaticities": chroma,
        "misalignment": {"element": args.element, "occurrence": args.occurrence, "fibre_index": fibre_index, "dx_m": args.dx},
        "tracking": {"particles": args.particles, "turns": args.turns, "lost_in_bunch": sum(bool(info["lost"]) for info in losses)},
        "madx_error_table": madx_error_table_summary,
        "madx_pyptc_closed_orbit_comparison": madx_pyptc_comparison_summary,
        "loss_map": {
            "absolute_aperture_m": args.loss_map_aperture,
            "particles": args.loss_map_particles,
            "lost": int(np.sum(loss_table[:, 1] > 0)),
            "loss_positions": sorted({int(pos) for pos in loss_table[:, 2] if pos > 0}),
            "peak_loss_node": peak_loss_node,
        },
        "png_files": pngs,
    }
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "_run_madx_error_table_case":
        parser = argparse.ArgumentParser()
        parser.add_argument("_command")
        parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
        parser.add_argument("--lattice", type=Path, default=DEFAULT_LATTICE)
        parser.add_argument("--output-dir", type=Path, required=True)
        parser.add_argument("--madx-error-table", type=Path, required=True)
        args = parser.parse_args()
        args.library = args.library.resolve()
        args.output_dir = args.output_dir.resolve()
        args.madx_error_table = args.madx_error_table.resolve()
        args.lattice = ensure_default_lattice() if args.lattice == DEFAULT_LATTICE else args.lattice.resolve()
        os.chdir(PYPTC_DIR)
        result = run_madx_error_table_case(args)
        (args.output_dir / "madx_error_table_summary.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--lattice", type=Path, default=DEFAULT_LATTICE)
    parser.add_argument("--output-dir", type=Path, default=PYPTC_DIR / "test_outputs" / "shims")
    parser.add_argument("--element", default="SP0_QF")
    parser.add_argument("--occurrence", type=int, default=1)
    parser.add_argument("--dx", type=float, default=0.003)
    parser.add_argument("--particles", type=int, default=32)
    parser.add_argument("--turns", type=int, default=1)
    parser.add_argument("--emit-x", type=float, default=1.0e-6)
    parser.add_argument("--emit-y", type=float, default=1.0e-6)
    parser.add_argument("--limit", type=float, default=5.0)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--loss-map-aperture", type=float, default=0.005)
    parser.add_argument("--loss-map-particles", type=int, default=81)
    parser.add_argument("--madx-error-table", type=Path, default=LATEST_SURVEY_REFERENCE_ERROR_TABLE)
    args = parser.parse_args()
    args.library = args.library.resolve()
    args.output_dir = args.output_dir.resolve()
    args.madx_error_table = args.madx_error_table.resolve()
    args.lattice = ensure_default_lattice() if args.lattice == DEFAULT_LATTICE else args.lattice.resolve()
    os.chdir(PYPTC_DIR)

    result = run(args)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
