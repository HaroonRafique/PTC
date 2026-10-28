#!/usr/bin/env python3
"""Bounded PyPTC off-momentum tune scan for chromaticity-coordinate audit."""

from __future__ import annotations

import csv
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from pyptc import PTC


BASIS = ROOT / "steps/benchmark-pyptc-linear-optics-against-madx/admission_basis-accepted-attempt-20261027T194128Z"
FLAT = BASIS / "madx_work/PTC-PyORBIT_flat_file.flt"
LIBRARY = ROOT / "build_pyptc/libpyptc.so"
OUTPUT = ROOT / "test_outputs/benchmark-chromaticity-coordinate-units"
PROTON_MASS_GEV = 0.9382720813
DELTAP_VALUES = (-1.0e-4, -5.0e-5, 0.0, 5.0e-5, 1.0e-4)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def momentum_to_pt(deltap: float, p0c: float) -> tuple[float, float]:
    p = p0c * (1.0 + deltap)
    e0 = math.sqrt(p0c * p0c + PROTON_MASS_GEV * PROTON_MASS_GEV)
    e = math.sqrt(p * p + PROTON_MASS_GEV * PROTON_MASS_GEV)
    delta_e = e - e0
    return delta_e, delta_e / p0c


def run_one(deltap: float, turns: int, amplitude_m: float) -> dict[str, float | int | bool]:
    ptc = PTC(LIBRARY)
    ptc.init_lattice(FLAT)
    p0c = ptc.scalar("ptc_get_p0c_")
    beta0 = ptc.scalar("ptc_get_beta0_")
    delta_e, pt = momentum_to_pt(deltap, p0c)
    particle = np.asarray([[amplitude_m, 0.0, amplitude_m, 0.0, 0.0, delta_e]])
    record = ptc.particle_diagnostics(particle, turns=turns, min_tune_turns=turns)[0]
    return {
        "deltap": deltap,
        "pt": pt,
        "delta_e_gev": delta_e,
        "p0c_gev": p0c,
        "beta0": beta0,
        "qx_reference": ptc.tunes()["qx"],
        "qy_reference": ptc.tunes()["qy"],
        "chromx_native": ptc.chromaticities()["chromx"],
        "chromy_native": ptc.chromaticities()["chromy"],
        "qx_tracking": float(record["qx"]),
        "qy_tracking": float(record["qy"]),
        "completed_turns": int(record["completed_turns"]),
        "lost": bool(record["lost"]),
        "tune_valid": bool(record["valid_tune"]),
    }


def central_slope(records: list[dict[str, float | int | bool]], plane: str, delta_step: float, coordinate: str) -> float:
    minus = next(r for r in records if math.isclose(float(r["deltap"]), -delta_step, rel_tol=1e-9, abs_tol=1e-15))
    plus = next(r for r in records if math.isclose(float(r["deltap"]), delta_step, rel_tol=1e-9, abs_tol=1e-15))
    delta_coordinate = float(plus[coordinate]) - float(minus[coordinate])
    return (float(plus[f"q{plane}_tracking"]) - float(minus[f"q{plane}_tracking"])) / delta_coordinate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--turns", type=int, default=4096)
    parser.add_argument("--amplitude-m", type=float, default=1.0e-3)
    parser.add_argument("--tag", default="initial")
    args = parser.parse_args()
    if args.turns < 256 or args.amplitude_m <= 0:
        parser.error("--turns must be >=256 and --amplitude-m must be positive")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = [run_one(delta, args.turns, args.amplitude_m) for delta in DELTAP_VALUES]
    suffix = f"_{args.tag}"
    with (OUTPUT / f"pyptc_off_momentum_tunes{suffix}.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    beta0 = float(records[2]["beta0"])
    slopes: dict[str, dict[str, float]] = {}
    for step in (5.0e-5, 1.0e-4):
        key = f"step_{step:g}"
        slopes[key] = {}
        for plane in ("x", "y"):
            slope_delta = central_slope(records, plane, step, "deltap")
            slope_pt = central_slope(records, plane, step, "pt")
            native = float(records[2][f"chrom{plane}_native"])
            slopes[key][plane] = {
                "central_dq_d_deltap_from_tracking": slope_delta,
                "central_dq_d_pt_from_tracking": slope_pt,
                "native_lattice_get_chrom": native,
                "native_minus_tracking_dq_d_pt": native - slope_pt,
                "beta0_times_native": beta0 * native,
                "beta0_conversion_factor_at_reference": beta0,
            }
    result = {
        "purpose": "identify PyPTC lattice_GET_CHROM's independent variable by comparison with tune slopes from off-momentum tracking",
        "reference_basis": "accepted snapshot attempt-20261027T194128Z; nominal accepted flat file and current API-5 build",
        "inputs": {
            "flat_file": str(FLAT.relative_to(ROOT)),
            "flat_file_sha256": digest(FLAT),
            "library": str(LIBRARY.relative_to(ROOT)),
            "library_sha256": digest(LIBRARY),
            "python_api_source": "pyptc/core.py",
            "python_api_source_sha256": digest(ROOT / "pyptc/core.py"),
            "chromaticity_wrapper": "fortran/pyptc_api.f90:pyptc_get_chromaticities calls lattice_GET_CHROM",
            "reference_coordinate_source": "../source/So_fitting.f90:lattice_GET_CHROM extracts DHDJ V(1:2) coefficient 00001",
            "species": "proton",
            "reference_p0c_gev": float(records[2]["p0c_gev"]),
            "reference_beta0": beta0,
            "tracking_initial_transverse_offset_m": 1.0e-3,
            "turns_per_particle": args.turns,
            "deltap_values": list(DELTAP_VALUES),
            "pt_definition": "(sqrt((p0c*(1+deltap))^2 + m^2) - sqrt(p0c^2 + m^2)) / p0c",
        },
        "records": records,
        "central_slope_comparisons": slopes,
    }
    result["inputs"]["tracking_initial_transverse_offset_m"] = args.amplitude_m
    result["inputs"]["turns_per_particle"] = args.turns
    result["inputs"]["run_tag"] = args.tag
    (OUTPUT / f"pyptc_coordinate_scan{suffix}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
