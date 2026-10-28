#!/usr/bin/env python3
"""Compare PyPTC and MAD-X application of a complete MAD-X EFIELD table.

The example writes a self-contained, repeatable record under
``test_outputs/06_madx_efield_api``. It covers the checked-in ISIS survey table
and a synthetic normal/skew multipole table so the field API is exercised even
though the ISIS survey's multipole columns are zero.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

PYPTC_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PYPTC_DIR.parent
os.environ.setdefault("MPLCONFIGDIR", str(PYPTC_DIR / "test_outputs" / "06_madx_efield_api" / ".matplotlib"))
if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))
if str(PYPTC_DIR / "workflows" / "madx") not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR / "workflows" / "madx"))
if str(PYPTC_DIR / "steps" / "benchmark-pyptc-linear-optics-against-madx" / "iteration-0003") not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR / "steps" / "benchmark-pyptc-linear-optics-against-madx" / "iteration-0003"))

from generate_flat_file import DEFAULT_MADX, generate
from isis_rcs_optics import align_profiles, build_verified_boundary_map, run_pyptc_optics
from pyptc import DEFAULT_LIBRARY, PTC, read_madx_error_table


DEFAULT_OUTPUT = PYPTC_DIR / "test_outputs" / "06_madx_efield_api"
SOURCE_TABLE = PYPTC_DIR / "workflows" / "madx" / "reference_errors" / "apr_2026_survey_corrected.tfs"
CASE_FIELD_VALUES = {"K1L": 2.0e-4, "K1SL": -1.0e-4}
REQUIRED_TWISS_COLUMNS = ("NAME", "S", "X", "Y", "BETX", "BETY")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_tfs(path: Path) -> tuple[dict[str, float | str], list[str], list[dict[str, str]]]:
    headers: dict[str, float | str] = {}
    columns: list[str] = []
    rows: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("@"):
            parts = shlex.split(stripped)
            if len(parts) >= 4:
                try:
                    headers[parts[1].upper()] = float(parts[3].replace("D", "E").replace("d", "e"))
                except ValueError:
                    headers[parts[1].upper()] = parts[3]
        elif stripped.startswith("*"):
            columns = stripped[1:].split()
        elif stripped.startswith('"') and columns:
            values = shlex.split(stripped)
            if len(values) == len(columns):
                rows.append(dict(zip(columns, values)))
    if not rows:
        raise RuntimeError(f"No named rows found in TFS file {path}")
    missing = sorted(set(REQUIRED_TWISS_COLUMNS) - set(columns)) if "TWISS" in path.name.upper() else []
    if missing:
        raise RuntimeError(f"TFS file {path} is missing columns {missing}")
    return headers, columns, rows


def make_field_only_table(source: Path, destination: Path) -> Path:
    lines = source.read_text(encoding="utf-8").splitlines()
    columns: list[str] = []
    names: list[str] = []
    rendered: list[str] = []
    target_found = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("*"):
            columns = stripped[1:].split()
            rendered.append(line)
            continue
        if stripped.startswith("$") or not stripped.startswith('"'):
            rendered.append(line)
            continue
        values = shlex.split(stripped)
        if len(values) != len(columns):
            raise ValueError(f"Malformed EFIELD row while making fixture: {line}")
        row = dict(zip(columns, values))
        name = row["NAME"].split(":")[0]
        for column in columns:
            if column != "NAME":
                row[column] = "0"
        if name.upper() == "SP0_QF":
            row.update(CASE_FIELD_VALUES)
            target_found = True
        names.append(name)
        rendered.append(
            " ".join(
                f'"{row[column]}"' if column == "NAME" else f"{float(row[column]):.16g}"
                for column in columns
            )
        )
    if not target_found:
        raise ValueError("Synthetic MAD-X EFIELD fixture could not find SP0_QF")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(rendered) + "\n", encoding="utf-8")
    return destination


def make_unsupported_fixture(source: Path, destination: Path) -> Path:
    lines = source.read_text(encoding="utf-8").splitlines()
    columns: list[str] = []
    rendered: list[str] = []
    found = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("*"):
            columns = stripped[1:].split()
            rendered.append(line)
            continue
        if stripped.startswith("$") or not stripped.startswith('"'):
            rendered.append(line)
            continue
        values = shlex.split(stripped)
        row = dict(zip(columns, values))
        if row.get("NAME", "").split(":")[0].upper() == "SP0_QF":
            row["MREX"] = "1e-4"
            found = True
        rendered.append(" ".join(
            f'"{row[column]}"' if column == "NAME" else f"{float(row[column]):.16g}"
            for column in columns
        ))
    if not found or "MREX" not in columns:
        raise ValueError("Could not construct unsupported-field guard fixture")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(rendered) + "\n", encoding="utf-8")
    return destination


def run_madx_case(case_dir: Path, input_dir: Path, table: Path, madx: Path) -> tuple[Path, Path, dict]:
    reference = case_dir / "reference"
    reference.mkdir(parents=True, exist_ok=True)
    lattice_input = reference / "ISIS_Lattice"
    if not lattice_input.exists():
        shutil.copytree(input_dir, lattice_input)
    local_table = reference / "efield.tfs"
    shutil.copy2(table, local_table)
    bare_twiss_path = reference / "bare_twiss.tfs"
    twiss_path = reference / "twiss.tfs"
    recipe = reference / "recipe.madx"
    recipe.write_text(
        "\n".join(
            [
                'TITLE, "PyPTC full EFIELD side-by-side example";',
                *(f'CALL, FILE="ISIS_Lattice/{name}";' for name in (
                    "ISIS.injected_beam", "ISIS.elements", "ISIS.strength", "2023.strength", "ISIS.sequence"
                )),
                "USE, SEQUENCE=synchrotron;",
                "SELECT, FLAG=TWISS, CLEAR;",
                "SELECT, FLAG=TWISS, COLUMN=name, keyword, s, x, px, y, py, betx, bety, alfx, alfy, dx, dpx, dy, dpy, mux, muy;",
                f'TWISS, CHROM, SAVE, FILE="{bare_twiss_path.name}";',
                "EOPTION, ADD=false;",
                'READMYTABLE, FILE="efield.tfs", TABLE=efield;',
                "SETERR, TABLE=efield;",
                'ESAVE, FILE="applied_efield.tfs";',
                "SELECT, FLAG=TWISS, CLEAR;",
                "SELECT, FLAG=TWISS, COLUMN=name, keyword, s, x, px, y, py, betx, bety, alfx, alfy, dx, dpx, dy, dpy, mux, muy;",
                f'TWISS, CHROM, SAVE, FILE="{twiss_path.name}";',
                "STOP;",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    log = reference / "madx.log"
    with recipe.open("r", encoding="utf-8") as stream, log.open("w", encoding="utf-8") as output:
        completed = subprocess.run([str(madx)], cwd=reference, stdin=stream, stdout=output,
                                   stderr=subprocess.STDOUT, text=True, check=False)
    if completed.returncode != 0 or not twiss_path.is_file():
        raise RuntimeError(f"MAD-X failed for {case_dir.name}; inspect {log}")
    bare_headers, _, bare_rows = parse_tfs(bare_twiss_path)
    headers, _, rows = parse_tfs(twiss_path)
    return bare_twiss_path, twiss_path, {
        "bare_headers": bare_headers,
        "headers": headers,
        "bare_rows": bare_rows,
        "rows": rows,
        "log": str(log),
        "recipe": str(recipe),
    }


def write_plot(path: Path, response_rows: list[dict], title: str) -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(path.parent / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s = np.asarray([float(row["reference_s_m"]) for row in response_rows])
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True)
    for ax, key, label, scale in (
        (axes[0, 0], "betx", r"$\Delta\beta_x$ [m]", 1.0),
        (axes[0, 1], "bety", r"$\Delta\beta_y$ [m]", 1.0),
        (axes[1, 0], "x", r"$\Delta x$ response [mm]", 1.0e3),
        (axes[1, 1], "y", r"$\Delta y$ response [mm]", 1.0e3),
    ):
        ax.plot(s, [float(row[f"madx_delta_{key}"]) * scale for row in response_rows], label="MAD-X")
        ax.plot(s, [float(row[f"pyptc_delta_{key}"]) * scale for row in response_rows], "--", label="PyPTC")
        ax.set_ylabel(label)
        ax.grid(True, linestyle=":", linewidth=0.6)
        ax.legend()
    for ax in axes[-1, :]:
        ax.set_xlabel("s [m]")
    fig.suptitle(title)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run_case(case_id: str, table: Path, base_flat_file: Path, input_dir: Path, output_dir: Path,
             madx: Path, library: Path) -> dict:
    case_dir = output_dir / "cases" / case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    bare_twiss_path, twiss_path, reference_result = run_madx_case(case_dir, input_dir, table, madx)
    bare_headers, _, bare_reference_rows = parse_tfs(bare_twiss_path)
    headers, _, reference_rows = parse_tfs(twiss_path)
    bare_target_summary, bare_target_rows, fibres, bare_node_groups = run_pyptc_optics(
        PYPTC_DIR, base_flat_file, library, case_dir / "target_bare", None
    )
    target_summary, target_rows, _, node_groups = run_pyptc_optics(
        PYPTC_DIR, base_flat_file, library, case_dir / "target_efield", table
    )
    bare_boundary_map, bare_boundary_summary = build_verified_boundary_map(
        bare_reference_rows, bare_target_rows, fibres, bare_node_groups
    )
    boundary_map, boundary_summary = build_verified_boundary_map(reference_rows, target_rows, fibres, node_groups)
    for label, mapping in (("bare", bare_boundary_summary), ("efield", boundary_summary)):
        if mapping["status"] != "verified":
            raise RuntimeError(f"MAD-X/PyPTC {label} boundary map is not verified: {mapping['failures'][:5]}")
    beta0 = float(np.sqrt(1.0 - float(headers["GAMMA"]) ** -2))
    bare_aligned, _ = align_profiles(bare_boundary_map, bare_reference_rows, bare_target_rows, beta0)
    aligned, _ = align_profiles(boundary_map, reference_rows, target_rows, beta0)
    if len(bare_aligned) != len(aligned):
        raise RuntimeError("Bare and EFIELD profile maps have different exit counts")
    response_rows = []
    response_metrics = []
    for base, changed in zip(bare_aligned, aligned):
        response = {"reference_s_m": changed["reference_s_m"], "element_name": changed["element_name"]}
        for observable in ("x", "y", "betx", "bety"):
            madx_delta = float(changed[f"reference_{observable}"]) - float(base[f"reference_{observable}"])
            pyptc_delta = float(changed[f"target_{observable}"]) - float(base[f"target_{observable}"])
            response[f"madx_delta_{observable}"] = madx_delta
            response[f"pyptc_delta_{observable}"] = pyptc_delta
            response[f"pyptc_minus_madx_delta_{observable}"] = pyptc_delta - madx_delta
        response_rows.append(response)
    for observable in ("x", "y", "betx", "bety"):
        residuals = np.asarray([row[f"pyptc_minus_madx_delta_{observable}"] for row in response_rows])
        response_metrics.append({
            "observable": observable,
            "sample_count": int(len(residuals)),
            "maximum_absolute_response_residual": float(np.max(np.abs(residuals))),
            "rms_response_residual": float(np.sqrt(np.mean(residuals ** 2))),
            "classification": "pending-tolerance",
            "tolerance": None,
        })
    target_scalars = target_summary["tunes"]
    with (case_dir / "aligned_profiles.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["name", "s_m", "madx_delta_x", "pyptc_delta_x", "madx_delta_y", "pyptc_delta_y",
                  "madx_delta_betx", "pyptc_delta_betx", "madx_delta_bety", "pyptc_delta_bety"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in response_rows:
            writer.writerow({"name": row["element_name"], "s_m": row["reference_s_m"],
                             **{key: row[key] for key in fields if key.startswith(("madx_delta_", "pyptc_delta_"))}})
    plot_path = case_dir / "madx_pyptc_efield_comparison.png"
    write_plot(plot_path, response_rows, f"{case_id}: MAD-X SETERR and PyPTC EFIELD API response")

    q1 = float(headers["Q1"]) % 1.0
    q2 = float(headers["Q2"]) % 1.0
    bare_q1 = float(bare_headers["Q1"]) % 1.0
    bare_q2 = float(bare_headers["Q2"]) % 1.0
    target_bare_scalars = bare_target_summary["tunes"]
    madx_delta_qx = ((q1 - bare_q1 + 0.5) % 1.0) - 0.5
    madx_delta_qy = ((q2 - bare_q2 + 0.5) % 1.0) - 0.5
    pyptc_delta_qx = ((target_scalars["qx"] - target_bare_scalars["qx"] + 0.5) % 1.0) - 0.5
    pyptc_delta_qy = ((target_scalars["qy"] - target_bare_scalars["qy"] + 0.5) % 1.0) - 0.5
    qx_residual = ((pyptc_delta_qx - madx_delta_qx + 0.5) % 1.0) - 0.5
    qy_residual = ((pyptc_delta_qy - madx_delta_qy + 0.5) % 1.0) - 0.5
    parsed = read_madx_error_table(table, nonzero=True)
    applied_fields = [
        {"name": row.name, "knl_nonzero": {str(i): v for i, v in enumerate(row.knl) if v != 0.0},
         "ksl_nonzero": {str(i): v for i, v in enumerate(row.ksl) if v != 0.0},
         "misalignment": row.as_kwargs()}
        for row in parsed
    ]
    summary = {
        "case_id": case_id,
        "table": str(table.resolve()),
        "table_sha256": sha256(table),
        "madx_twiss": str(twiss_path),
        "ptc_flat_file": str(base_flat_file),
        "flat_file_sha256": sha256(base_flat_file),
        "reference_rows": len(reference_rows),
        "target_rows": len(target_rows),
        "mapped_element_exits": boundary_summary["mapped_boundaries"],
        "boundary_map": boundary_summary,
        "bare_boundary_map": bare_boundary_summary,
        "profile_response_metrics": response_metrics,
        "madx_tune_response": {"qx": madx_delta_qx, "qy": madx_delta_qy},
        "pyptc_tune_response": {"qx": pyptc_delta_qx, "qy": pyptc_delta_qy},
        "madx_tunes_fractional": {"qx": q1, "qy": q2},
        "pyptc_tunes_fractional": {"qx": target_scalars["qx"], "qy": target_scalars["qy"]},
        "tune_residuals_wrapped": {"qx": qx_residual, "qy": qy_residual},
        "applied_table_rows": applied_fields,
        "plot": str(plot_path),
        "aligned_profiles": str(case_dir / "aligned_profiles.csv"),
        "madx_log": reference_result["log"],
    }
    (case_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--madx", type=Path, default=DEFAULT_MADX)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in (args.madx, args.library, SOURCE_TABLE):
        if not path.is_file():
            raise FileNotFoundError(path)

    lattice_source = PYPTC_DIR / "workflows" / "madx" / "lattices" / "00_Simplified_Lattice"
    reference_lattice = output_dir / "inputs" / "ISIS_Lattice"
    if reference_lattice.exists():
        shutil.rmtree(reference_lattice)
    shutil.copytree(lattice_source, reference_lattice)
    flatfile_dir = output_dir / "inputs" / "flatfile_generation"
    generated = generate(argparse.Namespace(lattice="simplified", madx=args.madx, output_dir=flatfile_dir))
    flat_file = Path(generated["flat_file"])
    field_table = make_field_only_table(SOURCE_TABLE, output_dir / "inputs" / "synthetic_normal_skew.tfs")
    unsupported_table = make_unsupported_fixture(
        field_table, output_dir / "inputs" / "unsupported_nonzero_mrex.tfs"
    )
    try:
        PTC(args.library).apply_madx_error_table(unsupported_table)
    except ValueError as exc:
        unsupported_guard = {"status": "rejected-as-designed", "message": str(exc)}
    else:
        raise RuntimeError("PyPTC failed to reject the unsupported nonzero MREX fixture")
    cases = [
        run_case("isis_apr_2026_survey", SOURCE_TABLE, flat_file, reference_lattice, output_dir, args.madx, args.library),
        run_case("synthetic_normal_skew", field_table, flat_file, reference_lattice, output_dir, args.madx, args.library),
    ]
    result = {
        "status": "completed",
        "madx_binary": str(args.madx.resolve()),
        "madx_binary_sha256": sha256(args.madx.resolve()),
        "pyptc_library": str(args.library.resolve()),
        "pyptc_library_sha256": sha256(args.library.resolve()),
        "source_table_sha256": sha256(SOURCE_TABLE),
        "generated_flat_file": str(flat_file),
        "generated_flat_file_sha256": sha256(flat_file),
        "unsupported_fixture": str(unsupported_table),
        "unsupported_fixture_sha256": sha256(unsupported_table),
        "unsupported_field_guard": unsupported_guard,
        "cases": cases,
        "scope": "alignment plus integrated normal/skew magnetic K_nL/K_nSL errors; other nonzero EFIELD columns are rejected by the Python API",
    }
    result_path = output_dir / "result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# PyPTC MAD-X EFIELD API side-by-side example",
        "",
        "This is a reproducible test/example, not a tolerance-based acceptance.",
        "The MAD-X path uses `READMYTABLE` and `SETERR`; PyPTC uses the public `apply_madx_error_table` API.",
        "Each engine reads the same table and uses a fresh lattice state.",
        "",
        f"- MAD-X: `{args.madx.resolve()}` (SHA-256 `{result['madx_binary_sha256']}`)",
        f"- PyPTC library SHA-256: `{result['pyptc_library_sha256']}`",
        f"- Source survey table SHA-256: `{result['source_table_sha256']}`",
        f"- Generated PTC flat file SHA-256: `{result['generated_flat_file_sha256']}`",
        f"- Unsupported nonzero EFIELD guard: `{unsupported_guard['status']}` (`{unsupported_guard['message']}`)",
        "",
        "## Cases",
        "",
    ]
    for case in cases:
        tune = case["tune_residuals_wrapped"]
        report.extend([
            f"### `{case['case_id']}`",
            "",
            f"- Mapped exits: {case['mapped_element_exits']}",
            f"- Wrapped tune residuals: Qx `{tune['qx']:.6g}`, Qy `{tune['qy']:.6g}`",
            f"- Plot: `{Path(case['plot']).relative_to(output_dir)}`",
            f"- Aligned values: `{Path(case['aligned_profiles']).relative_to(output_dir)}`",
            "",
        ])
    report.extend([
        "## Scope and limits",
        "",
        "The API applies DX/DY/DS/DPHI/DTHETA/DPSI and integrated magnetic K0L..K20L/K0SL..K20SL.",
        "Nonzero EFIELD fields outside that set fail before any lattice mutation. The example does not claim support for monitor readout/scaling, RF multipole phases, or RF frequency/harmonic/lag errors.",
        "The checked-in survey table has zero multipole columns; the synthetic case exercises normal and skew field errors.",
        "",
    ])
    (output_dir / "report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote EFIELD side-by-side example to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
