"""Reusable plotting helpers for PyPTC diagnostics."""

from __future__ import annotations

import csv
import math
import os
from pathlib import Path
from typing import Iterable

import numpy as np


DIAGNOSTIC_COLUMNS = [
    "particle",
    "x0",
    "xp0",
    "y0",
    "yp0",
    "z0",
    "dE0",
    "x",
    "xp",
    "y",
    "yp",
    "z",
    "dE",
    "jx0",
    "jy0",
    "jx",
    "jy",
    "phase_x0",
    "phase_y0",
    "phase_x_final",
    "phase_y_final",
    "qx",
    "qy",
    "survived",
    "lost",
    "lost_turn",
    "lost_pos",
    "completed_turns",
    "valid_tune",
]


def require_matplotlib(output_dir: Path):
    os.environ.setdefault("MPLCONFIGDIR", str(output_dir / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def write_diagnostic_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(DIAGNOSTIC_COLUMNS)
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_tune_csv(path: Path, rows: list[dict[str, object]]) -> None:
    columns = ["particle", "qx", "qy", "jx", "jy", "survived", "lost", "lost_turn", "lost_pos", "completed_turns", "valid_tune"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _bool_array(rows: list[dict[str, object]], key: str) -> np.ndarray:
    return np.asarray([bool(row.get(key, False)) for row in rows], dtype=bool)


def _float_array(rows: list[dict[str, object]], key: str) -> np.ndarray:
    values = []
    for row in rows:
        try:
            values.append(float(row.get(key, float("nan"))))
        except (TypeError, ValueError):
            values.append(float("nan"))
    return np.asarray(values, dtype=float)


def finite_tune_mask(rows: list[dict[str, object]]) -> np.ndarray:
    qx = _float_array(rows, "qx")
    qy = _float_array(rows, "qy")
    return _bool_array(rows, "valid_tune") & np.isfinite(qx) & np.isfinite(qy)


def tune_summary(rows: list[dict[str, object]]) -> dict[str, float | int]:
    valid = finite_tune_mask(rows)
    survived = _bool_array(rows, "survived")
    lost = _bool_array(rows, "lost")
    stat_mask = valid & survived
    qx = _float_array(rows, "qx")
    qy = _float_array(rows, "qy")
    summary: dict[str, float | int] = {
        "particles": len(rows),
        "survived": int(survived.sum()),
        "lost": int(lost.sum()),
        "valid_tunes": int(valid.sum()),
        "valid_survivor_tunes": int(stat_mask.sum()),
        "valid_lost_tunes": int((valid & lost).sum()),
    }
    if stat_mask.any():
        summary.update(
            {
                "qx_mean": float(np.mean(qx[stat_mask])),
                "qy_mean": float(np.mean(qy[stat_mask])),
                "qx_std": float(np.std(qx[stat_mask])),
                "qy_std": float(np.std(qy[stat_mask])),
            }
        )
    else:
        summary.update({"qx_mean": math.nan, "qy_mean": math.nan, "qx_std": math.nan, "qy_std": math.nan})
    return summary


def _padded_limits(*arrays: np.ndarray, factor: float = 1.08) -> tuple[float, float]:
    finite = [np.asarray(array, dtype=float).ravel() for array in arrays]
    values = np.concatenate(finite) if finite else np.asarray([], dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return 0.0, 1.0
    vmin = float(np.min(values))
    vmax = float(np.max(values))
    if np.isclose(vmin, vmax):
        delta = abs(vmin) * 0.05 + 1.0e-6
        return vmin - delta, vmax + delta
    center = 0.5 * (vmin + vmax)
    half = 0.5 * (vmax - vmin) * factor
    return center - half, center + half


def _save_formats(fig, path_base: Path, formats: Iterable[str]) -> list[str]:
    path_base.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for fmt in formats:
        fmt = fmt.strip().lstrip(".").lower()
        if not fmt:
            continue
        path = path_base.with_suffix(f".{fmt}")
        fig.savefig(path, dpi=170)
        written.append(str(path))
    return written


def plot_tune_footprints(output_base: Path, rows: list[dict[str, object]], formats: Iterable[str] = ("png",)) -> list[str]:
    plt = require_matplotlib(output_base.parent)
    qx = _float_array(rows, "qx")
    qy = _float_array(rows, "qy")
    valid = finite_tune_mask(rows)
    survived = _bool_array(rows, "survived")
    lost = _bool_array(rows, "lost")
    survivor_mask = valid & survived
    lost_mask = valid & lost

    xlims = _padded_limits(qx[valid])
    ylims = _padded_limits(qy[valid])
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharex=True, sharey=True)
    axes[0].scatter(qx[survivor_mask], qy[survivor_mask], s=14, alpha=0.75, label="survived")
    axes[0].set_title("surviving particles")
    axes[1].scatter(qx[survivor_mask], qy[survivor_mask], s=14, alpha=0.65, label="survived")
    axes[1].scatter(qx[lost_mask], qy[lost_mask], s=24, alpha=0.9, marker="x", label="lost")
    axes[1].set_title("survival-aware")
    for axis in axes:
        axis.set_xlabel("qx")
        axis.set_ylabel("qy")
        axis.set_xlim(*xlims)
        axis.set_ylim(*ylims)
        axis.grid(which="both", ls=":", lw=0.5, alpha=0.7)
        axis.legend(loc="best")
    fig.tight_layout()
    written = _save_formats(fig, output_base, formats)
    plt.close(fig)
    return written


def plot_tune_vs_action(output_base: Path, rows: list[dict[str, object]], formats: Iterable[str] = ("png",)) -> list[str]:
    plt = require_matplotlib(output_base.parent)
    qx = _float_array(rows, "qx")
    qy = _float_array(rows, "qy")
    jx = _float_array(rows, "jx")
    jy = _float_array(rows, "jy")
    valid = finite_tune_mask(rows)
    survived = _bool_array(rows, "survived")
    lost = _bool_array(rows, "lost")

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    for axis, tune, action, tune_label, action_label in (
        (axes[0], qx, jx, "qx", "Jx"),
        (axes[1], qy, jy, "qy", "Jy"),
    ):
        survivor_mask = valid & survived & np.isfinite(action)
        lost_mask = valid & lost & np.isfinite(action)
        axis.scatter(action[survivor_mask], tune[survivor_mask], s=14, alpha=0.75, label="survived")
        axis.scatter(action[lost_mask], tune[lost_mask], s=24, alpha=0.9, marker="x", label="lost")
        axis.set_xlabel(action_label)
        axis.set_ylabel(tune_label)
        axis.grid(which="both", ls=":", lw=0.5, alpha=0.7)
        axis.legend(loc="best")
    fig.tight_layout()
    written = _save_formats(fig, output_base, formats)
    plt.close(fig)
    return written


def plot_diagnostic_dashboard(output_base: Path, rows: list[dict[str, object]], formats: Iterable[str] = ("png",)) -> list[str]:
    plt = require_matplotlib(output_base.parent)
    x0 = _float_array(rows, "x0") * 1.0e3
    xp0 = _float_array(rows, "xp0") * 1.0e3
    y0 = _float_array(rows, "y0") * 1.0e3
    yp0 = _float_array(rows, "yp0") * 1.0e3
    x = _float_array(rows, "x") * 1.0e3
    xp = _float_array(rows, "xp") * 1.0e3
    y = _float_array(rows, "y") * 1.0e3
    yp = _float_array(rows, "yp") * 1.0e3
    qx = _float_array(rows, "qx")
    qy = _float_array(rows, "qy")
    jx = _float_array(rows, "jx")
    jy = _float_array(rows, "jy")
    valid = finite_tune_mask(rows)
    survived = _bool_array(rows, "survived")
    lost = _bool_array(rows, "lost")

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes[0, 0].scatter(qx[valid & survived], qy[valid & survived], s=12, alpha=0.7, label="survived")
    axes[0, 0].scatter(qx[valid & lost], qy[valid & lost], s=22, alpha=0.9, marker="x", label="lost")
    axes[0, 0].set_xlabel("qx")
    axes[0, 0].set_ylabel("qy")
    axes[0, 0].legend(loc="best")

    axes[0, 1].scatter(jx[valid & survived], qx[valid & survived], s=12, alpha=0.7)
    axes[0, 1].scatter(jx[valid & lost], qx[valid & lost], s=22, alpha=0.9, marker="x")
    axes[0, 1].set_xlabel("Jx")
    axes[0, 1].set_ylabel("qx")

    axes[0, 2].scatter(jy[valid & survived], qy[valid & survived], s=12, alpha=0.7)
    axes[0, 2].scatter(jy[valid & lost], qy[valid & lost], s=22, alpha=0.9, marker="x")
    axes[0, 2].set_xlabel("Jy")
    axes[0, 2].set_ylabel("qy")

    axes[1, 0].scatter(x0, xp0, s=8, alpha=0.35, label="initial")
    axes[1, 0].scatter(x[survived], xp[survived], s=10, alpha=0.65, label="final survived")
    axes[1, 0].scatter(x[lost], xp[lost], s=18, alpha=0.9, marker="x", label="lost")
    axes[1, 0].set_xlabel("x [mm]")
    axes[1, 0].set_ylabel("xp [mrad]")
    axes[1, 0].legend(loc="best")

    axes[1, 1].scatter(y0, yp0, s=8, alpha=0.35, label="initial")
    axes[1, 1].scatter(y[survived], yp[survived], s=10, alpha=0.65, label="final survived")
    axes[1, 1].scatter(y[lost], yp[lost], s=18, alpha=0.9, marker="x", label="lost")
    axes[1, 1].set_xlabel("y [mm]")
    axes[1, 1].set_ylabel("yp [mrad]")
    axes[1, 1].legend(loc="best")

    axes[1, 2].scatter(x[survived], y[survived], s=10, alpha=0.65, label="survived")
    axes[1, 2].scatter(x[lost], y[lost], s=18, alpha=0.9, marker="x", label="lost")
    axes[1, 2].set_xlabel("x [mm]")
    axes[1, 2].set_ylabel("y [mm]")
    axes[1, 2].legend(loc="best")

    for axis in axes.ravel():
        axis.grid(which="both", ls=":", lw=0.5, alpha=0.7)
    fig.tight_layout()
    written = _save_formats(fig, output_base, formats)
    plt.close(fig)
    return written
