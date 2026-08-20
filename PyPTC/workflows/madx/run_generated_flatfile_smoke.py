#!/usr/bin/env python3
"""Run repeatable PyPTC smoke plots against a freshly generated MAD-X flat file."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


MADX_DIR = Path(__file__).resolve().parent
PYPTC_DIR = MADX_DIR.parents[1]
REPO_ROOT = PYPTC_DIR.parent
DEFAULT_OUTPUT_DIR = MADX_DIR / "outputs" / "simplified"
DEFAULT_LIBRARY = PYPTC_DIR / "artifacts" / "build-pyptc" / "libpyptc.so"
DEFAULT_ERROR_TABLE = MADX_DIR / "reference_errors" / "jan26_survey_corrected.tfs"


def run_command(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def require_generated_flat_file(output_dir: Path, regenerate: bool) -> Path:
    flat_file = output_dir / "PTC-PyORBIT_flat_file.flt"
    if regenerate or not flat_file.exists():
        run_command(
            [
                sys.executable,
                str(MADX_DIR / "generate_flat_file.py"),
                "--output-dir",
                str(output_dir),
            ],
            REPO_ROOT,
        )
    if not flat_file.exists() or flat_file.stat().st_size == 0:
        raise RuntimeError(f"Generated flat file is missing or empty: {flat_file}")
    return flat_file


def run_pyptc_smoke(args: argparse.Namespace, flat_file: Path, output_dir: Path) -> dict:
    if not args.library.exists():
        raise FileNotFoundError(f"PyPTC shared library not found; run bash PyPTC/build/build_ptc.sh first: {args.library}")
    if not args.madx_error_table.exists():
        raise FileNotFoundError(f"Reference MAD-X error table not found: {args.madx_error_table}")

    smoke_dir = output_dir / "pyptc_smoke"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            sys.executable,
            str(PYPTC_DIR / "tests" / "test_pyptc_shims.py"),
            "--library",
            str(args.library),
            "--lattice",
            str(flat_file),
            "--output-dir",
            str(smoke_dir),
            "--particles",
            str(args.particles),
            "--turns",
            str(args.turns),
            "--loss-map-particles",
            str(args.loss_map_particles),
            "--madx-error-table",
            str(args.madx_error_table),
        ],
        PYPTC_DIR,
    )
    return json.loads((smoke_dir / "summary.json").read_text(encoding="utf-8"))


def validate_orbits(smoke_dir: Path, bare_threshold: float, response_threshold: float) -> dict:
    orbit_csv = smoke_dir / "pyptc_bare_vs_jan26_error_table_generated_lattice.csv"
    if not orbit_csv.exists():
        raise FileNotFoundError(f"Expected orbit comparison CSV was not produced: {orbit_csv}")
    data = np.loadtxt(orbit_csv, delimiter=",", skiprows=1)
    max_bare_x = float(np.max(np.abs(data[:, 1])))
    max_bare_y = float(np.max(np.abs(data[:, 3])))
    max_delta_x = float(np.max(np.abs(data[:, 5])))
    max_delta_y = float(np.max(np.abs(data[:, 6])))
    max_bare = max(max_bare_x, max_bare_y)
    max_delta = max(max_delta_x, max_delta_y)
    if max_bare >= bare_threshold:
        raise AssertionError(f"Bare orbit max {max_bare:.6e} m exceeds threshold {bare_threshold:.6e} m")
    if max_delta <= response_threshold:
        raise AssertionError(f"Misaligned orbit response {max_delta:.6e} m is below threshold {response_threshold:.6e} m")
    return {
        "max_bare_x_m": max_bare_x,
        "max_bare_y_m": max_bare_y,
        "max_delta_x_m": max_delta_x,
        "max_delta_y_m": max_delta_y,
    }


def run(args: argparse.Namespace) -> dict:
    output_dir = args.output_dir.resolve()
    flat_file = require_generated_flat_file(output_dir, regenerate=not args.no_regenerate)
    smoke_summary = run_pyptc_smoke(args, flat_file, output_dir)
    orbit_summary = validate_orbits(output_dir / "pyptc_smoke", args.bare_orbit_threshold, args.response_threshold)
    result = {
        "flat_file": str(flat_file),
        "output_dir": str(output_dir),
        "pyptc_smoke_dir": str(output_dir / "pyptc_smoke"),
        "orbit_validation": orbit_summary,
        "pyptc_summary": smoke_summary,
    }
    (output_dir / "repeatable_smoke_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--madx-error-table", type=Path, default=DEFAULT_ERROR_TABLE)
    parser.add_argument("--particles", type=int, default=12)
    parser.add_argument("--turns", type=int, default=1)
    parser.add_argument("--loss-map-particles", type=int, default=21)
    parser.add_argument("--bare-orbit-threshold", type=float, default=3.0e-10)
    parser.add_argument("--response-threshold", type=float, default=1.0e-4)
    parser.add_argument("--no-regenerate", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
