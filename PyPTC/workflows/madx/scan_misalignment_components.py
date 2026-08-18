#!/usr/bin/env python3
"""Scan MAD-X vs PyPTC closed-orbit agreement by misalignment component."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

from compare_madx_pyptc_closed_orbits import (
    DEFAULT_ERROR_TABLE,
    DEFAULT_LIBRARY,
    DEFAULT_MADX,
    MADX_DIR,
    MISALIGNMENT_COMPONENTS,
    REPO_ROOT,
    require_matplotlib,
)


DEFAULT_OUTPUT_DIR = MADX_DIR / "outputs" / "cscan"


def run_case(output_dir: Path, component: str, convention: str, flip: bool, args: argparse.Namespace) -> dict:
    convention_tag = "m" if convention == "madx" else "r"
    case_name = f"{component.lower()}_{convention_tag}{'f' if flip else ''}"
    case_dir = output_dir / case_name
    command = [
        sys.executable,
        str(MADX_DIR / "compare_madx_pyptc_closed_orbits.py"),
        "--madx",
        str(args.madx),
        "--library",
        str(args.library),
        "--madx-error-table",
        str(args.madx_error_table),
        "--output-dir",
        str(case_dir),
        "--components",
        component,
        "--pyptc-convention",
        convention,
        "--response-threshold",
        "0.0",
    ]
    if flip:
        command.extend(["--pyptc-flip-components", component])
    subprocess.run(command, cwd=REPO_ROOT, check=True)
    result = json.loads((case_dir / "summary.json").read_text(encoding="utf-8"))
    result["case"] = case_name
    result["component"] = component
    result["convention"] = convention
    result["pyptc_flip"] = flip
    return result


def write_summary_csv(path: Path, rows: list[dict]) -> None:
    header = (
        "case,component,convention,pyptc_flip,"
        "madx_x_mm,madx_y_mm,pyptc_x_mm,pyptc_y_mm,residual_x_mm,residual_y_mm"
    )
    data = []
    for row in rows:
        data.append(
            [
                row["case"],
                row["component"],
                row["convention"],
                int(row["pyptc_flip"]),
                1.0e3 * row["madx_misaligned_max_x_m"],
                1.0e3 * row["madx_misaligned_max_y_m"],
                1.0e3 * row["pyptc_misaligned_max_x_m"],
                1.0e3 * row["pyptc_misaligned_max_y_m"],
                1.0e3 * row["residual_max_x_m"],
                1.0e3 * row["residual_max_y_m"],
            ]
        )
    with path.open("w", encoding="utf-8") as stream:
        stream.write(header + "\n")
        for row in data:
            stream.write(",".join(str(value) for value in row) + "\n")


def plot_summary(path: Path, rows: list[dict]) -> None:
    plt = require_matplotlib(path.parent)
    labels = [row["case"] for row in rows]
    x = np.arange(len(rows))
    residual_x = np.array([1.0e3 * row["residual_max_x_m"] for row in rows])
    residual_y = np.array([1.0e3 * row["residual_max_y_m"] for row in rows])
    pyptc_x = np.array([1.0e3 * row["pyptc_misaligned_max_x_m"] for row in rows])
    pyptc_y = np.array([1.0e3 * row["pyptc_misaligned_max_y_m"] for row in rows])
    madx_x = np.array([1.0e3 * row["madx_misaligned_max_x_m"] for row in rows])
    madx_y = np.array([1.0e3 * row["madx_misaligned_max_y_m"] for row in rows])

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    width = 0.2
    axes[0].bar(x - 1.5 * width, madx_x, width=width, label="MAD-X x")
    axes[0].bar(x - 0.5 * width, pyptc_x, width=width, label="PyPTC x")
    axes[0].bar(x + 0.5 * width, madx_y, width=width, label="MAD-X y")
    axes[0].bar(x + 1.5 * width, pyptc_y, width=width, label="PyPTC y")
    axes[0].set_ylabel("max closed orbit [mm]")
    axes[0].legend(loc="upper right", ncol=4)
    axes[0].grid(axis="y", ls=":", lw=0.5)

    axes[1].bar(x - width / 2.0, residual_x, width=width, label="x residual")
    axes[1].bar(x + width / 2.0, residual_y, width=width, label="y residual")
    axes[1].set_ylabel("max interpolated residual [mm]")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=90, fontsize=8)
    axes[1].legend(loc="upper right")
    axes[1].grid(axis="y", ls=":", lw=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def run(args: argparse.Namespace) -> dict:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for component in MISALIGNMENT_COMPONENTS:
        rows.append(run_case(output_dir, component, "madx", False, args))
        rows.append(run_case(output_dir, component, "raw", False, args))
        rows.append(run_case(output_dir, component, "madx", True, args))

    write_summary_csv(output_dir / "component_scan_summary.csv", rows)
    plot_summary(output_dir / "component_scan_summary.png", rows)
    best = {}
    for component in MISALIGNMENT_COMPONENTS:
        candidates = [row for row in rows if row["component"] == component]
        best[component] = min(candidates, key=lambda row: row["residual_max_x_m"] + row["residual_max_y_m"])
    summary = {
        "error_table": str(args.madx_error_table.resolve()),
        "output_dir": str(output_dir),
        "best_by_component": best,
        "rows": rows,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--madx", type=Path, default=DEFAULT_MADX)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--madx-error-table", type=Path, default=DEFAULT_ERROR_TABLE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    print(json.dumps(run(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
