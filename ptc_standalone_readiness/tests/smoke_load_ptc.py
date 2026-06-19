#!/usr/bin/env python3
"""Standalone smoke checks for the PTC Fortran shared library.

This script intentionally does not import or require PyORBIT3. The PyORBIT3
wrapper sources in interface/ need PyORBIT3 headers and runtime types, so this
repo can only prove that the Fortran shared object is buildable, loadable, and
exports the entry points expected by the later merge.
"""

from __future__ import annotations

import argparse
import ctypes
from pathlib import Path


EXPECTED_SYMBOLS = (
    "ptc_init_",
    "ptc_script_",
    "ptc_get_twiss_init_",
    "ptc_get_ini_params_",
    "ptc_get_syncpart_",
    "ptc_get_twiss_for_node_",
    "ptc_get_task_type_",
    "ptc_get_omega_",
    "ptc_get_p0c_",
    "ptc_get_beta0_",
    "ptc_get_kinetic_",
    "ptc_read_accel_table_",
    "ptc_synchronous_set_",
    "ptc_synchronous_after_",
    "ptc_track_particle_",
    "ptc_update_twiss_",
)


def default_library_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "build-standalone" / "libptc_orbit.so"


def load_library(path: Path) -> ctypes.CDLL:
    if not path.exists():
        raise SystemExit(f"PTC shared library not found: {path}")
    return ctypes.CDLL(str(path))


def configure_signatures(lib: ctypes.CDLL) -> None:
    c_double_p = ctypes.POINTER(ctypes.c_double)
    c_int_p = ctypes.POINTER(ctypes.c_int)

    lib.ptc_init_.argtypes = [ctypes.c_char_p, ctypes.c_int]
    lib.ptc_init_.restype = None
    lib.ptc_script_.argtypes = [ctypes.c_char_p, ctypes.c_int]
    lib.ptc_script_.restype = None
    lib.ptc_read_accel_table_.argtypes = [ctypes.c_char_p, ctypes.c_int]
    lib.ptc_read_accel_table_.restype = None

    lib.ptc_get_ini_params_.argtypes = [c_int_p, c_int_p, c_double_p, c_double_p]
    lib.ptc_get_ini_params_.restype = None
    lib.ptc_get_syncpart_.argtypes = [c_double_p, c_int_p, c_double_p]
    lib.ptc_get_syncpart_.restype = None
    lib.ptc_get_twiss_init_.argtypes = [c_double_p] * 12
    lib.ptc_get_twiss_init_.restype = None
    lib.ptc_get_twiss_for_node_.argtypes = [c_int_p] + [c_double_p] * 13
    lib.ptc_get_twiss_for_node_.restype = None

    lib.ptc_get_task_type_.argtypes = [c_int_p, c_int_p]
    lib.ptc_get_task_type_.restype = None
    lib.ptc_get_omega_.argtypes = [c_double_p]
    lib.ptc_get_omega_.restype = None
    lib.ptc_get_p0c_.argtypes = [c_double_p]
    lib.ptc_get_p0c_.restype = None
    lib.ptc_get_beta0_.argtypes = [c_double_p]
    lib.ptc_get_beta0_.restype = None
    lib.ptc_get_kinetic_.argtypes = [c_double_p]
    lib.ptc_get_kinetic_.restype = None
    lib.ptc_synchronous_set_.argtypes = [c_int_p]
    lib.ptc_synchronous_set_.restype = None
    lib.ptc_synchronous_after_.argtypes = [c_int_p]
    lib.ptc_synchronous_after_.restype = None
    lib.ptc_track_particle_.argtypes = [c_int_p] + [c_double_p] * 6
    lib.ptc_track_particle_.restype = None
    lib.ptc_update_twiss_.argtypes = []
    lib.ptc_update_twiss_.restype = None


def verify_symbols(lib: ctypes.CDLL) -> None:
    missing = [name for name in EXPECTED_SYMBOLS if not hasattr(lib, name)]
    if missing:
        raise SystemExit("Missing expected PTC symbols: " + ", ".join(missing))


def call_ptc_init_if_requested(lib: ctypes.CDLL, ptc_input: Path | None) -> None:
    if ptc_input is None:
        return
    if not ptc_input.exists():
        raise SystemExit(f"PTC input file not found: {ptc_input}")
    encoded = str(ptc_input).encode()
    lib.ptc_init_(encoded, len(encoded))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--library",
        type=Path,
        default=default_library_path(),
        help="Path to libptc_orbit.so.",
    )
    parser.add_argument(
        "--ptc-input",
        type=Path,
        help="Optional real PTC input file. If provided, ptc_init_ is called.",
    )
    args = parser.parse_args()

    lib = load_library(args.library)
    verify_symbols(lib)
    configure_signatures(lib)
    call_ptc_init_if_requested(lib, args.ptc_input)
    print(f"PTC smoke check passed: loaded {args.library}")
    print(f"Verified {len(EXPECTED_SYMBOLS)} exported PTC symbols.")
    if args.ptc_input is None:
        print("No PTC input supplied; skipped functional ptc_init_ call.")


if __name__ == "__main__":
    main()
