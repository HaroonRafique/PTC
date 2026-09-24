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
from pyptc import read_madx_error_table


DEFAULT_OUTPUT_DIR = MADX_DIR / "outputs" / "cscan"


def run_case(output_dir: Path, component: str, convention: str, flip: bool, args: argparse.Namespace) -> dict:
    convention_tag = "m" if convention == "madx" else "r"
    case_name = f"{component.lower()}_{convention_tag}{'f' if flip else ''}"
    case_dir = output_dir / case_name
    convention_text = "MAD-X convention, same signed values" if convention == "madx" else "raw PyPTC convention, same signed values"
    if flip:
        convention_text = f"MAD-X convention; PyPTC {component} signs deliberately reversed"
    affected = sum(getattr(record, component.lower()) != 0.0 for record in read_madx_error_table(args.madx_error_table, nonzero=True))
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
        "--skip-linear-optics",
        "--case-label",
        f"cscan diagnostic: {component}; {affected} affected elements; {convention_text}",
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
    labels = [f"{row['component']}\n{'MAD-X' if row['convention'] == 'madx' else 'raw'}{' / flip' if row['pyptc_flip'] else ''}" for row in rows]
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


def write_manifest(path: Path, rows: list[dict], error_table: Path) -> None:
    """Explain the scan conventions and retain all signed source values."""
    records = read_madx_error_table(error_table, nonzero=True)
    lines = [
        "# Misalignment component/sign scan", "",
        "Each case retains only the named component from the corrected Apr-2026 error table.",
        "`m` uses the same signed MAD-X convention in PyPTC; `r` uses raw PyPTC values;",
        "`mf` deliberately reverses that component in PyPTC only and is a convention diagnostic, not a like-for-like comparison.", "",
        "| Directory | Component | PyPTC convention | PyPTC component sign |", "| --- | --- | --- | --- |",
    ]
    for row in rows:
        sign = "reversed (diagnostic)" if row["pyptc_flip"] else "same as MAD-X"
        lines.append(f"| `{row['case']}` | {row['component']} | {row['convention']} | {sign} |")
    for component in MISALIGNMENT_COMPONENTS:
        entries = [(record.name, getattr(record, component.lower())) for record in records if getattr(record, component.lower()) != 0.0]
        unit = "mm" if component in {"DX", "DY", "DS"} else "mrad"
        scale = 1e3
        lines.extend(["", f"## {component} signed source values [{unit}]", "", "| Element | Value |", "| --- | ---: |"])
        lines.extend(f"| {name} | {scale * value:+.6f} |" for name, value in entries)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> dict:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    selected = tuple(args.components or MISALIGNMENT_COMPONENTS)
    for component in selected:
        for convention, flip in (("madx", False), ("raw", False), ("madx", True)):
            if args.summary_only:
                tag = "m" if convention == "madx" else "r"
                case_name = f"{component.lower()}_{tag}{'f' if flip else ''}"
                result = json.loads((output_dir / case_name / "summary.json").read_text(encoding="utf-8"))
                result.update(case=case_name, component=component, convention=convention, pyptc_flip=flip)
                rows.append(result)
            else:
                rows.append(run_case(output_dir, component, convention, flip, args))

    write_summary_csv(output_dir / "component_scan_summary.csv", rows)
    plot_summary(output_dir / "component_scan_summary.png", rows)
    write_manifest(output_dir / "component_scan_manifest.md", rows, args.madx_error_table)
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
    parser.add_argument("--components", nargs="+", choices=MISALIGNMENT_COMPONENTS, help="Limit regeneration to named components.")
    parser.add_argument("--summary-only", action="store_true", help="Rebuild aggregate labels and manifest from existing case summaries.")
    args = parser.parse_args()
    print(json.dumps(run(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
