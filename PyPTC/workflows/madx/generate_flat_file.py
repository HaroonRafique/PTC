#!/usr/bin/env python3
"""Generate an ISIS RCS PTC flat file with the bundled MAD-X binaries."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


MADX_DIR = Path(__file__).resolve().parent
PYPTC_DIR = MADX_DIR.parents[1]
DEFAULT_OUTPUT_DIR = MADX_DIR / "outputs" / "simplified"
MADX_BINARIES = {
    "5_02_00": MADX_DIR / "bin" / "madx-linux64_v5_02_00",
    "5_05_02": MADX_DIR / "bin" / "madx-linux64_v5_05_02",
    "5_06_01": MADX_DIR / "bin" / "madx-linux64-v5_06_01",
}
DEFAULT_MADX_VERSION = "5_02_00"
DEFAULT_MADX = MADX_BINARIES[DEFAULT_MADX_VERSION]
LATTICES = {
    "simplified": MADX_DIR / "lattices" / "00_Simplified_Lattice",
}
REQUIRED_LATTICE_FILES = (
    "ISIS.injected_beam",
    "ISIS.elements",
    "ISIS.strength",
    "ISIS.sequence",
)
REQUIRED_PTC_SCRIPTS = ("resplit.ptc", "print_flat_file.ptc")


def copytree_contents(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def prepare_run_dir(lattice_dir: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    copytree_contents(lattice_dir, output_dir / "ISIS_Lattice")
    copytree_contents(MADX_DIR / "ptc_scripts", output_dir / "PTC_Scripts")
    shutil.copy2(MADX_DIR / "scripts" / "Create_PTC_flat_file.madx", output_dir / "Create_PTC_flat_file.madx")
    return output_dir / "Create_PTC_flat_file.madx"


def validate_inputs(madx: Path, lattice_dir: Path) -> None:
    if not madx.exists():
        raise FileNotFoundError(f"MAD-X binary not found: {madx}")
    if not madx.is_file():
        raise FileNotFoundError(f"MAD-X path is not a file: {madx}")
    if not os.access(madx, os.X_OK):
        raise PermissionError(f"MAD-X binary is not executable: {madx}")
    if not lattice_dir.exists():
        raise FileNotFoundError(f"Lattice directory not found: {lattice_dir}")
    missing_lattice = [name for name in REQUIRED_LATTICE_FILES if not (lattice_dir / name).exists()]
    if missing_lattice:
        raise FileNotFoundError(f"Missing lattice files in {lattice_dir}: {missing_lattice}")
    missing_scripts = [name for name in REQUIRED_PTC_SCRIPTS if not (MADX_DIR / "ptc_scripts" / name).exists()]
    if missing_scripts:
        raise FileNotFoundError(f"Missing PTC scripts in {MADX_DIR / 'ptc_scripts'}: {missing_scripts}")


def run_madx(madx: Path, script: Path, output_dir: Path) -> subprocess.CompletedProcess[str]:
    with script.open("r", encoding="utf-8") as input_file:
        result = subprocess.run(
            [str(madx)],
            stdin=input_file,
            cwd=output_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    (output_dir / "madx.log").write_text(result.stdout, encoding="utf-8")
    return result


def generate(args: argparse.Namespace) -> dict:
    lattice_dir = LATTICES[args.lattice].resolve()
    madx = args.madx.resolve()
    output_dir = args.output_dir.resolve()
    validate_inputs(madx, lattice_dir)
    script = prepare_run_dir(lattice_dir, output_dir)
    result = run_madx(madx, script, output_dir)
    flat_file = output_dir / "PTC-PyORBIT_flat_file.flt"
    twiss_file = output_dir / "optimised_flat_file.tfs"
    if result.returncode != 0:
        raise RuntimeError(f"MAD-X failed with status {result.returncode}; see {output_dir / 'madx.log'}")
    if not flat_file.exists() or flat_file.stat().st_size == 0:
        raise RuntimeError(f"MAD-X did not produce a non-empty flat file: {flat_file}")
    summary = {
        "lattice": args.lattice,
        "lattice_dir": str(lattice_dir),
        "madx": str(madx),
        "output_dir": str(output_dir),
        "flat_file": str(flat_file),
        "twiss_file": str(twiss_file) if twiss_file.exists() else None,
        "log": str(output_dir / "madx.log"),
        "returncode": result.returncode,
    }
    (output_dir / "generation_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lattice", choices=sorted(LATTICES), default="simplified")
    parser.add_argument("--madx-version", choices=sorted(MADX_BINARIES), default=DEFAULT_MADX_VERSION)
    parser.add_argument("--madx", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    if args.madx is None:
        args.madx = MADX_BINARIES[args.madx_version]
    try:
        print(json.dumps(generate(args), indent=2, sort_keys=True))
    except Exception as exc:
        print(f"generate_flat_file.py: {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
