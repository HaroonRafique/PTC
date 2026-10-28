#!/usr/bin/env python3
"""Run MAD-X TWISS at the PyPTC diagnostic's matched delta_p offsets."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STEP = ROOT / "steps/benchmark-pyptc-linear-optics-against-madx"
BASIS = STEP / "admission_basis-accepted-attempt-20261027T194128Z"
NOMINAL_RECIPE = STEP / "runs/attempt-019/cases/nominal/reference/reference_recipe.madx"
MADX = ROOT / "workflows/madx/bin/madx-linux64_v5_02_00"
OUTPUT = ROOT / "test_outputs/benchmark-chromaticity-coordinate-units/madx"
DELTAP_VALUES = (-1.0e-4, -5.0e-5, 0.0, 5.0e-5, 1.0e-4)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_headers(path: Path) -> dict[str, float]:
    result: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("@"):
            parts = line.split()
            if len(parts) >= 4:
                try:
                    result[parts[1].upper()] = float(parts[3].replace("D", "E"))
                except ValueError:
                    pass
    return result


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    original = NOMINAL_RECIPE.read_text(encoding="utf-8")
    prefix = re.sub(r"TWISS,\s*CHROM,\s*SAVE,\s*FILE=.*?;\s*$", "", original, flags=re.I | re.S)
    if prefix == original:
        raise RuntimeError("Could not remove the nominal final TWISS command from the retained MAD-X recipe")
    rows: list[dict[str, float | int | str]] = []
    for deltap in DELTAP_VALUES:
        case_dir = OUTPUT / f"deltap_{deltap:+.0e}".replace("+", "plus_").replace("-", "minus_")
        case_dir.mkdir(parents=True, exist_ok=True)
        twiss_path = case_dir / "twiss.tfs"
        recipe_path = case_dir / "recipe.madx"
        log_path = case_dir / "madx.log"
        recipe_path.write_text(
            prefix + f'\nTWISS, DELTAP={deltap:.16g}, SAVE, FILE="{twiss_path}";\nSTOP;\n',
            encoding="utf-8",
        )
        completed = subprocess.run([str(MADX), str(recipe_path)], cwd=case_dir, text=True, capture_output=True, check=False)
        log_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
        if completed.returncode != 0 or not twiss_path.is_file():
            raise RuntimeError(f"MAD-X scan failed at DELTAP={deltap}; see {log_path}")
        headers = parse_headers(twiss_path)
        rows.append({
            "deltap": deltap,
            "qx_full": headers["Q1"],
            "qy_full": headers["Q2"],
            "qx_fractional": headers["Q1"] % 1.0,
            "qy_fractional": headers["Q2"] % 1.0,
            "madx_gamma": headers["GAMMA"],
            "twiss_sha256": digest(twiss_path),
            "recipe_sha256": digest(recipe_path),
            "log_sha256": digest(log_path),
            "returncode": completed.returncode,
        })
    with (OUTPUT / "madx_off_momentum_tunes.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    slopes = {}
    for step in (5.0e-5, 1.0e-4):
        minus = next(r for r in rows if r["deltap"] == -step)
        plus = next(r for r in rows if r["deltap"] == step)
        slopes[f"step_{step:g}"] = {
            "dqx_d_deltap": (float(plus["qx_fractional"]) - float(minus["qx_fractional"])) / (2 * step),
            "dqy_d_deltap": (float(plus["qy_fractional"]) - float(minus["qy_fractional"])) / (2 * step),
        }
    summary = {
        "binary": str(MADX.relative_to(ROOT)),
        "binary_sha256": digest(MADX),
        "nominal_recipe": str(NOMINAL_RECIPE.relative_to(ROOT)),
        "nominal_recipe_sha256": digest(NOMINAL_RECIPE),
        "accepted_snapshot_inputs": {
            name: digest(BASIS / "snapshot_inputs" / name)
            for name in ("ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence")
        },
        "twiss_option": "TWISS, DELTAP=<offset>, SAVE; no CHROM option, read Q1/Q2 from each matched physical momentum offset",
        "deltap_values": list(DELTAP_VALUES),
        "rows": rows,
        "central_slopes_dq_d_deltap": slopes,
        "madx_5_02_chromaticity_header_values_from_attempt_019": {"dqx_d_deltap": -4.745390843, "dqy_d_deltap": -4.806168146},
    }
    (OUTPUT / "madx_tune_scan.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
