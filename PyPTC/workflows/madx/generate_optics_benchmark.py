#!/usr/bin/env python3
"""Generate the tracked MAD-X/PyPTC optics, orbit, and aperture benchmark set."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

MADX_DIR = Path(__file__).resolve().parent
PYPTC_DIR = MADX_DIR.parents[1]
if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))

from compare_madx_pyptc_closed_orbits import DEFAULT_ERROR_TABLE, DEFAULT_LIBRARY, DEFAULT_MADX


DEFAULT_OUTPUT_DIR = PYPTC_DIR / "test_outputs" / "madx_optics_benchmark"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--madx", type=Path, default=DEFAULT_MADX)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--madx-error-table", type=Path, default=DEFAULT_ERROR_TABLE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    output = args.output_dir.resolve()
    optics_dir = output / "optics"
    aperture_dir = output / "aperture"
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable, str(MADX_DIR / "compare_madx_pyptc_closed_orbits.py"),
            "--madx", str(args.madx), "--library", str(args.library),
            "--madx-error-table", str(args.madx_error_table), "--output-dir", str(optics_dir),
            "--response-threshold", "0.0",
            "--case-label", "Slide benchmark: bare lattice and Apr-2026 corrected full error table",
        ],
        cwd=PYPTC_DIR,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(MADX_DIR / "compare_isis_apertures.py"), "--madx", str(args.madx), "--library", str(args.library), "--output-dir", str(aperture_dir)],
        cwd=PYPTC_DIR,
        check=True,
    )
    optics = json.loads((optics_dir / "summary.json").read_text(encoding="utf-8"))
    aperture = json.loads((aperture_dir / "summary.json").read_text(encoding="utf-8"))
    summary = {
        "description": "MAD-X/PyPTC slide benchmark: bare and full-error-table optics/orbits plus aperture state.",
        "optics": optics,
        "aperture": aperture,
    }
    (output / "benchmark_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
