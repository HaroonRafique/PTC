#!/usr/bin/env python3
"""Compare PyPTC chromaticity with default-state and DELTA-state tracking.

Each --mode run must use a fresh Python process because the PTC library keeps
its lattice and internal state in module-level Fortran storage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
STEP = ROOT / "steps/benchmark-pyptc-linear-optics-against-madx"
BASIS = STEP / "admission_basis-accepted-attempt-20261027T194128Z"
FLAT = BASIS / "madx_work/PTC-PyORBIT_flat_file.flt"
LIBRARY = ROOT / "build_pyptc/libpyptc.so"
OUTPUT = ROOT / "test_outputs/benchmark-chromaticity-coordinate-units"
SOURCE = Path(__file__).resolve()
DELTAP_VALUES = (-1.0e-4, -5.0e-5, 0.0, 5.0e-5, 1.0e-4)
PROTON_MASS_GEV = 0.9382720813

sys.path.insert(0, str(ROOT))
from pyptc import PTC  # noqa: E402


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def energy_offset(deltap: float, p0c: float) -> float:
    p = p0c * (1.0 + deltap)
    e0 = math.sqrt(p0c * p0c + PROTON_MASS_GEV**2)
    e = math.sqrt(p * p + PROTON_MASS_GEV**2)
    return e - e0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("default", "api_delta"), required=True)
    parser.add_argument("--turns", type=int, default=8192)
    args = parser.parse_args()
    if args.turns < 256:
        parser.error("--turns must be >=256")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    state_script = OUTPUT / "set_delta_state.ptc"
    if args.mode == "api_delta":
        # Match lattice_GET_CHROM's state construction: it adds NOCAVITY,
        # DELTA and ONLY_4D before generating the normal form.
        state_script.write_text(
            "+NOCAVITY\n+DELTA\n+ONLY_4D\nSETORBITSTATE\nSTOP\n",
            encoding="utf-8",
        )

    ptc = PTC(LIBRARY)
    ptc.init_lattice(FLAT)
    if args.mode == "api_delta":
        ptc.run_script(state_script)

    p0c = ptc.scalar("ptc_get_p0c_")
    beta0 = ptc.scalar("ptc_get_beta0_")
    rows = []
    for deltap in DELTAP_VALUES:
        # The default PTC state uses momentum deviation delta in x5. This
        # control intentionally supplies energy-derived PT, reproducing the
        # old diagnostic's mistaken coordinate assumption. api_delta passes
        # DELTAP directly and uses lattice_GET_CHROM's explicit state.
        d_e = energy_offset(deltap, p0c) if args.mode == "default" else deltap * p0c
        bunch = np.asarray([[1.0e-3, 0.0, 1.0e-3, 0.0, 0.0, d_e]])
        row = ptc.particle_diagnostics(bunch, turns=args.turns, min_tune_turns=args.turns)[0]
        rows.append({
            "deltap_label": deltap,
            "input_dE_gev": d_e,
            "input_x5": d_e / p0c,
            "qx": float(row["qx"]),
            "qy": float(row["qy"]),
            "completed_turns": int(row["completed_turns"]),
            "lost": bool(row["lost"]),
        })

    slopes = {}
    for step in (5.0e-5, 1.0e-4):
        lo = next(row for row in rows if row["deltap_label"] == -step)
        hi = next(row for row in rows if row["deltap_label"] == step)
        slopes[f"step_{step:g}"] = {
            "dqx_d_deltap_label": (hi["qx"] - lo["qx"]) / (2.0 * step),
            "dqy_d_deltap_label": (hi["qy"] - lo["qy"]) / (2.0 * step),
        }

    result = {
        "mode": args.mode,
        "turns": args.turns,
        "basis_flat_file_sha256": digest(FLAT),
        "library_sha256": digest(LIBRARY),
        "script_sha256": digest(SOURCE),
        "python_api_sha256": digest(ROOT / "pyptc/core.py"),
        "fortran_api_sha256": digest(ROOT / "fortran/pyptc_api.f90"),
        "ptc_source_sha256": digest(ROOT.parent / "source/So_fitting.f90"),
        "p0c_gev": p0c,
        "beta0": beta0,
        "state_script_sha256": digest(state_script) if args.mode == "api_delta" else None,
        "chromaticity_api": ptc.chromaticities(),
        "rows": rows,
        "central_slopes": slopes,
        "state_interpretation": (
            "explicit NOCAVITY+DELTA+ONLY_4D state, matching lattice_GET_CHROM; x5 is DELTAP"
            if args.mode == "api_delta" else
            "default PTC state; x5 is DELTAP, but input was incorrectly formed as PT=dE/p0c"
        ),
    }
    out = OUTPUT / f"pyptc_state_scan_{args.mode}.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
