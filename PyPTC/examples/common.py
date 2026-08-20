"""Shared utilities for user-facing PyPTC examples."""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import numpy as np

PYPTC_DIR = Path(__file__).resolve().parents[1]
ROOT = PYPTC_DIR.parent
OUTPUT_ROOT = PYPTC_DIR / "test_outputs"
MADX_DIR = PYPTC_DIR / "workflows" / "madx"
SURVEY_TO_LATTICE_MADX_TWISS = Path("/home/hr/Repositories/survey_to_lattice/03_Standalone/synchrotron_madx_twiss.tfs")

if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))

from pyptc import (  # noqa: E402
    DEFAULT_LATTICE,
    DEFAULT_LIBRARY,
    LATEST_SURVEY_REFERENCE_ERROR_TABLE,
    PTC,
    ensure_default_lattice,
    generate_matched_gaussian_4d,
    read_jvt_design_aperture,
    read_madx_error_table,
    tune_summary,
    write_diagnostic_csv,
    write_tune_csv,
)
from pyptc.aperture import read_madx_aperture_file  # noqa: E402
from pyptc.lattice import read_flatfile_fibres, resolve_fibre_index  # noqa: E402
from scripts.flatfile_misalign import apply_single_misalignment  # noqa: E402


def chdir_repo() -> None:
    os.chdir(PYPTC_DIR)


def output_dir(name: str) -> Path:
    path = OUTPUT_ROOT / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_array_csv(path: Path, array: np.ndarray, header: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(path, np.asarray(array, dtype=float), delimiter=",", header=header, comments="")


def write_dict_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def require_matplotlib(output: Path):
    os.environ.setdefault("MPLCONFIGDIR", str(output / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def init_ptc(lattice: Path | None = None, library: Path | None = None) -> PTC:
    chdir_repo()
    ptc = PTC(library or DEFAULT_LIBRARY)
    ptc.init_lattice(lattice or ensure_default_lattice())
    return ptc


def s_positions(rows: list[dict[str, object]]) -> np.ndarray:
    return np.cumsum([float(row["length"]) for row in rows])


def padded_limits(*arrays: np.ndarray, factor: float = 1.08) -> tuple[float, float]:
    values = np.concatenate([np.asarray(array, dtype=float).ravel() for array in arrays])
    values = values[np.isfinite(values)]
    if values.size == 0:
        return -1.0, 1.0
    vmin = float(np.min(values))
    vmax = float(np.max(values))
    if np.isclose(vmin, vmax):
        pad = abs(vmin) * 0.05 + 1.0e-6
        return vmin - pad, vmax + pad
    center = 0.5 * (vmin + vmax)
    half = 0.5 * (vmax - vmin) * factor
    return center - half, center + half


def make_standard_bunch(ptc: PTC, particles: int = 1000, seed: int = 12345, limit: float = 5.0) -> np.ndarray:
    twiss0 = ptc.node_twiss_orbit(0)
    return generate_matched_gaussian_4d(
        n=particles,
        emittance_x=1.0e-6,
        emittance_y=1.0e-6,
        alpha_x=float(twiss0["alphax"]),
        beta_x=float(twiss0["betax"]),
        alpha_y=float(twiss0["alphay"]),
        beta_y=float(twiss0["betay"]),
        x_limit=limit,
        y_limit=limit,
        seed=seed,
    )


def diagnostic_arrays(rows: list[dict[str, object]], stage: str) -> dict[str, np.ndarray]:
    suffix = "0" if stage == "initial" else ""

    def values(key: str) -> np.ndarray:
        return np.asarray([float(row.get(key, float("nan"))) for row in rows], dtype=float)

    return {
        "x": values(f"x{suffix}") * 1.0e3,
        "xp": values(f"xp{suffix}") * 1.0e3,
        "y": values(f"y{suffix}") * 1.0e3,
        "yp": values(f"yp{suffix}") * 1.0e3,
        "z": values(f"z{suffix}"),
        "dE": values(f"dE{suffix}") * 1.0e3,
        "jx": values(f"jx{suffix}"),
        "jy": values(f"jy{suffix}"),
        "qx": values("qx"),
        "qy": values("qy"),
        "lost": np.asarray([bool(row.get("lost", False)) for row in rows], dtype=bool),
        "survived": np.asarray([bool(row.get("survived", False)) for row in rows], dtype=bool),
        "valid": np.asarray([bool(row.get("valid_tune", False)) for row in rows], dtype=bool),
    }


def dashboard_limits(rows: list[dict[str, object]]) -> dict[str, tuple[float, float]]:
    initial = diagnostic_arrays(rows, "initial")
    final = diagnostic_arrays(rows, "final")
    valid = final["valid"] & np.isfinite(final["qx"]) & np.isfinite(final["qy"])
    return {
        "x": padded_limits(initial["x"], final["x"]),
        "xp": padded_limits(initial["xp"], final["xp"]),
        "y": padded_limits(initial["y"], final["y"]),
        "yp": padded_limits(initial["yp"], final["yp"]),
        "z": padded_limits(initial["z"], final["z"]),
        "dE": padded_limits(initial["dE"], final["dE"]),
        "qx": padded_limits(final["qx"][valid]) if valid.any() else (0.0, 1.0),
        "qy": padded_limits(final["qy"][valid]) if valid.any() else (0.0, 1.0),
        "jx": padded_limits(initial["jx"], final["jx"]),
        "jy": padded_limits(initial["jy"], final["jy"]),
    }


def plot_bunch_dashboard(path: Path, rows: list[dict[str, object]], stage: str, limits: dict[str, tuple[float, float]]) -> None:
    plt = require_matplotlib(path.parent)
    data = diagnostic_arrays(rows, stage)
    valid = data["valid"] & np.isfinite(data["qx"]) & np.isfinite(data["qy"])
    survived = valid & data["survived"]
    lost = valid & data["lost"]
    phase_survived = data["survived"] if stage == "final" else np.ones_like(data["survived"], dtype=bool)
    phase_lost = data["lost"] if stage == "final" else np.zeros_like(data["lost"], dtype=bool)

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle(f"{stage.title()} 1000-particle PyPTC bunch dashboard")

    axes[0, 0].scatter(data["qx"][survived], data["qy"][survived], s=10, alpha=0.7, label="survived")
    axes[0, 0].scatter(data["qx"][lost], data["qy"][lost], s=22, marker="x", alpha=0.9, label="lost")
    axes[0, 0].set_xlabel("qx")
    axes[0, 0].set_ylabel("qy")
    axes[0, 0].set_xlim(*limits["qx"])
    axes[0, 0].set_ylim(*limits["qy"])
    axes[0, 0].legend(loc="best")

    axes[0, 1].scatter(data["jx"][survived], data["qx"][survived], s=10, alpha=0.7)
    axes[0, 1].scatter(data["jx"][lost], data["qx"][lost], s=22, marker="x", alpha=0.9)
    axes[0, 1].set_xlabel("Jx")
    axes[0, 1].set_ylabel("qx")
    axes[0, 1].set_xlim(*limits["jx"])
    axes[0, 1].set_ylim(*limits["qx"])

    axes[0, 2].scatter(data["jy"][survived], data["qy"][survived], s=10, alpha=0.7)
    axes[0, 2].scatter(data["jy"][lost], data["qy"][lost], s=22, marker="x", alpha=0.9)
    axes[0, 2].set_xlabel("Jy")
    axes[0, 2].set_ylabel("qy")
    axes[0, 2].set_xlim(*limits["jy"])
    axes[0, 2].set_ylim(*limits["qy"])

    axes[1, 0].scatter(data["x"][phase_survived], data["xp"][phase_survived], s=8, alpha=0.65, label="particles")
    axes[1, 0].scatter(data["x"][phase_lost], data["xp"][phase_lost], s=20, marker="x", alpha=0.9, label="lost")
    axes[1, 0].set_xlabel("x [mm]")
    axes[1, 0].set_ylabel("xp [mrad]")
    axes[1, 0].set_xlim(*limits["x"])
    axes[1, 0].set_ylim(*limits["xp"])
    axes[1, 0].legend(loc="best")

    axes[1, 1].scatter(data["y"][phase_survived], data["yp"][phase_survived], s=8, alpha=0.65, label="particles")
    axes[1, 1].scatter(data["y"][phase_lost], data["yp"][phase_lost], s=20, marker="x", alpha=0.9, label="lost")
    axes[1, 1].set_xlabel("y [mm]")
    axes[1, 1].set_ylabel("yp [mrad]")
    axes[1, 1].set_xlim(*limits["y"])
    axes[1, 1].set_ylim(*limits["yp"])
    axes[1, 1].legend(loc="best")

    axes[1, 2].scatter(data["z"][phase_survived], data["dE"][phase_survived], s=8, alpha=0.65, label="particles")
    axes[1, 2].scatter(data["z"][phase_lost], data["dE"][phase_lost], s=20, marker="x", alpha=0.9, label="lost")
    axes[1, 2].set_xlabel("z [m]")
    axes[1, 2].set_ylabel("dE [MeV]")
    axes[1, 2].set_xlim(*limits["z"])
    axes[1, 2].set_ylim(*limits["dE"])
    axes[1, 2].legend(loc="best")

    for axis in axes.ravel():
        axis.grid(which="both", ls=":", lw=0.5, alpha=0.7)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def write_diagnostic_outputs(output: Path, rows: list[dict[str, object]], prefix: str = "bunch") -> dict[str, object]:
    diagnostics_csv = output / f"{prefix}_diagnostics.csv"
    tune_csv = output / f"{prefix}_tune_action.csv"
    write_diagnostic_csv(diagnostics_csv, rows)
    write_tune_csv(tune_csv, rows)
    limits = dashboard_limits(rows)
    initial_png = output / "bunch_initial_dashboard.png"
    final_png = output / "bunch_final_dashboard.png"
    plot_bunch_dashboard(initial_png, rows, "initial", limits)
    plot_bunch_dashboard(final_png, rows, "final", limits)
    return {
        "diagnostics_csv": str(diagnostics_csv),
        "tune_csv": str(tune_csv),
        "initial_dashboard": str(initial_png),
        "final_dashboard": str(final_png),
        "summary": tune_summary(rows),
    }


def plot_bare_twiss_closed_orbit(path: Path, rows: list[dict[str, object]], tunes: dict, chroma: dict) -> None:
    plt = require_matplotlib(path.parent)
    s = s_positions(rows)
    betax = np.asarray([float(row["betax"]) for row in rows])
    betay = np.asarray([float(row["betay"]) for row in rows])
    etax = np.asarray([float(row["etax"]) for row in rows])
    orbitx = np.asarray([float(row["orbitx"]) for row in rows]) * 1.0e3
    orbity = np.asarray([float(row["orbity"]) for row in rows]) * 1.0e3

    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    axes[0].plot(s, betax, label="betax")
    axes[0].plot(s, betay, label="betay")
    axes[0].set_ylabel("beta [m]")
    axes[0].legend(loc="upper right")
    axes[0].set_title(
        f"bare tunes qx={tunes['qx']:.6f}, qy={tunes['qy']:.6f}; "
        f"chromaticities x={chroma['chromx']:.4g}, y={chroma['chromy']:.4g}"
    )
    axes[1].plot(s, etax, label="etax")
    axes[1].set_ylabel("dispersion x [m]")
    axes[1].legend(loc="upper right")
    axes[2].plot(s, orbitx, label="x")
    axes[2].plot(s, orbity, label="y")
    axes[2].set_ylabel("closed orbit [mm]")
    axes[2].set_xlabel("s over PTC/ORBIT nodes [m]")
    axes[2].legend(loc="upper right")
    for axis in axes:
        axis.grid(which="both", ls=":", lw=0.5, alpha=0.7)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def orbit_response_rows(bare: list[dict[str, object]], edited: list[dict[str, object]]) -> np.ndarray:
    s = s_positions(bare)
    bare_x = np.asarray([float(row["orbitx"]) for row in bare])
    bare_y = np.asarray([float(row["orbity"]) for row in bare])
    edited_x = np.asarray([float(row["orbitx"]) for row in edited])
    edited_y = np.asarray([float(row["orbity"]) for row in edited])
    return np.column_stack([s, bare_x, edited_x, edited_x - bare_x, bare_y, edited_y, edited_y - bare_y])


def plot_orbit_response(path: Path, orbit: np.ndarray, labels: tuple[str, str] = ("bare", "edited")) -> None:
    plt = require_matplotlib(path.parent)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axes[0].plot(orbit[:, 0], orbit[:, 1] * 1.0e3, label=f"{labels[0]} x")
    axes[0].plot(orbit[:, 0], orbit[:, 2] * 1.0e3, label=f"{labels[1]} x")
    axes[0].set_ylabel("x closed orbit [mm]")
    axes[0].legend(loc="upper right")
    axes[1].plot(orbit[:, 0], orbit[:, 4] * 1.0e3, label=f"{labels[0]} y")
    axes[1].plot(orbit[:, 0], orbit[:, 5] * 1.0e3, label=f"{labels[1]} y")
    axes[1].set_xlabel("s over PTC/ORBIT nodes [m]")
    axes[1].set_ylabel("y closed orbit [mm]")
    axes[1].legend(loc="upper right")
    for axis in axes:
        axis.grid(which="both", ls=":", lw=0.5, alpha=0.7)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def plot_aperture_vs_design(path: Path, pyptc_rows: list[dict[str, object]], design_records: Iterable[object]) -> None:
    plt = require_matplotlib(path.parent)
    design = list(design_records)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    if pyptc_rows:
        s = np.asarray([float(row["s"]) for row in pyptc_rows])
        axes[0].scatter(s, [float(row["x"]) * 1.0e3 for row in pyptc_rows], s=10, label="PyPTC half x")
        axes[1].scatter(s, [float(row["y"]) * 1.0e3 for row in pyptc_rows], s=10, label="PyPTC half y")
    if design:
        ds = np.asarray([float(record.s) for record in design if record.s is not None])
        dx = np.asarray([float(record.half_x) * 1.0e3 for record in design if record.s is not None])
        dy = np.asarray([float(record.half_y) * 1.0e3 for record in design if record.s is not None])
        axes[0].scatter(ds, dx, s=14, alpha=0.6, marker="x", label="design half x")
        axes[1].scatter(ds, dy, s=14, alpha=0.6, marker="x", label="design half y")
    axes[0].set_ylabel("horizontal half aperture [mm]")
    axes[1].set_ylabel("vertical half aperture [mm]")
    axes[1].set_xlabel("s [m]")
    for axis in axes:
        axis.grid(which="both", ls=":", lw=0.5, alpha=0.7)
        axis.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def apply_matching_madx_apertures(ptc: PTC, aperture_file: Path) -> tuple[list[object], list[object]]:
    fibre_names = {fibre.name.upper() for fibre in read_flatfile_fibres(ptc.lattice)}
    records = read_madx_aperture_file(aperture_file)
    matched = [record for record in records if record.name.upper() in fibre_names]
    skipped = [record for record in records if record.name.upper() not in fibre_names]
    return ptc.apply_rectangular_apertures(matched), skipped


def make_losable_bunch(count: int = 81, limit: float = 0.005) -> np.ndarray:
    rows = []
    for x0 in np.linspace(-1.5 * limit, 1.5 * limit, count):
        rows.append([x0, 0.0, 0.0, 0.0, 0.0, 0.0])
    return np.asarray(rows, dtype=float)


def track_to_node(ptc: PTC, coords: np.ndarray, node_pos: int) -> np.ndarray:
    tracked = np.asarray(coords, dtype=float).copy()
    for node_index in range(max(0, node_pos)):
        tracked = ptc.track_particle_ptc(node_index, tracked)
    return tracked


def run_loss_map(ptc: PTC, aperture: float = 0.005, count: int = 81) -> tuple[np.ndarray, int, np.ndarray]:
    original = ptc.absolute_aperture()
    ptc.set_absolute_aperture(aperture)
    bunch = make_losable_bunch(count=count, limit=aperture)
    rows = []
    for particle, coords in enumerate(bunch):
        tracked, info = ptc.track_particle_ptc_with_loss(coords, turns=1)
        rows.append([particle, *coords.tolist(), int(info["lost"]), int(info["lost_turn"]), int(info["lost_pos"]), *tracked.tolist()])
    loss_table = np.asarray(rows, dtype=float)
    ptc.set_absolute_aperture(1.0)
    lost_positions = loss_table[loss_table[:, 8] > 0, 8].astype(int)
    if lost_positions.size:
        unique, counts = np.unique(lost_positions, return_counts=True)
        peak_node = int(unique[np.argmax(counts)])
    else:
        peak_node = 1
    positions_at_peak = np.asarray([track_to_node(ptc, coords, peak_node) for coords in bunch])
    ptc.set_absolute_aperture(original)
    return loss_table, peak_node, positions_at_peak


def plot_loss_map(path: Path, loss_table: np.ndarray, node_rows: list[dict[str, object]]) -> None:
    plt = require_matplotlib(path.parent)
    s = s_positions(node_rows)
    counts = np.zeros_like(s)
    for pos in loss_table[loss_table[:, 8] > 0, 8].astype(int):
        if 1 <= pos <= len(counts):
            counts[pos - 1] += 1
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.step(s, counts, where="mid")
    ax.set_xlabel("s over PTC/ORBIT nodes [m]")
    ax.set_ylabel("lost particles")
    ax.set_title("loss map for deliberately losable bunch")
    ax.grid(which="both", ls=":", lw=0.5, alpha=0.7)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def plot_aperture_at_peak(path: Path, loss_table: np.ndarray, positions: np.ndarray, peak_node: int, aperture: float) -> None:
    plt = require_matplotlib(path.parent)
    lost_here = loss_table[:, 8].astype(int) == peak_node
    survived = ~lost_here
    boundary_x = np.asarray([-aperture, aperture, aperture, -aperture, -aperture]) * 1.0e3
    boundary_y = np.asarray([-aperture, -aperture, aperture, aperture, -aperture]) * 1.0e3
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].plot(boundary_x, boundary_y, color="black", lw=1.5)
    axes[0].scatter(positions[survived, 0] * 1.0e3, positions[survived, 2] * 1.0e3, s=14, label="survived")
    axes[0].scatter(positions[lost_here, 0] * 1.0e3, positions[lost_here, 2] * 1.0e3, s=24, marker="x", label="lost")
    axes[0].set_xlabel("x [mm]")
    axes[0].set_ylabel("y [mm]")
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].set_title(f"aperture at node {peak_node}")
    axes[1].scatter(positions[survived, 0] * 1.0e3, positions[survived, 1] * 1.0e3, s=14, label="survived")
    axes[1].scatter(positions[lost_here, 0] * 1.0e3, positions[lost_here, 1] * 1.0e3, s=24, marker="x", label="lost")
    axes[1].set_xlabel("x [mm]")
    axes[1].set_ylabel("xp [mrad]")
    axes[2].scatter(positions[survived, 2] * 1.0e3, positions[survived, 3] * 1.0e3, s=14, label="survived")
    axes[2].scatter(positions[lost_here, 2] * 1.0e3, positions[lost_here, 3] * 1.0e3, s=24, marker="x", label="lost")
    axes[2].set_xlabel("y [mm]")
    axes[2].set_ylabel("yp [mrad]")
    for axis in axes:
        axis.grid(which="both", ls=":", lw=0.5, alpha=0.7)
        axis.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def generate_flat_file(output: Path) -> dict:
    chdir_repo()
    subprocess.run(
        [
            sys.executable,
            str(MADX_DIR / "generate_flat_file.py"),
            "--output-dir",
            str(DEFAULT_LATTICE.parent),
        ],
        cwd=PYPTC_DIR,
        check=True,
    )
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "flat_file": str(ensure_default_lattice()),
        "fibres": len(read_flatfile_fibres(ensure_default_lattice())),
    }
    write_json(output / "summary.json", manifest)
    return manifest


def copy_madx_comparison_outputs(source_dir: Path, output: Path) -> None:
    shutil.copy2(source_dir / "madx_vs_pyptc_closed_orbit_comparison.png", output / "madx_vs_pyptc_closed_orbit_comparison.png")
    shutil.copy2(source_dir / "madx_vs_pyptc_closed_orbit_comparison.csv", output / "madx_vs_pyptc_closed_orbit_comparison.csv")
