#!/usr/bin/env python3
"""Compare MAD-X and PyPTC closed orbits for the same simplified-lattice errors."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

MADX_DIR = Path(__file__).resolve().parent
PYPTC_DIR = MADX_DIR.parents[1]
REPO_ROOT = PYPTC_DIR.parent
if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))

from generate_flat_file import DEFAULT_MADX, LATTICES, copytree_contents, generate
from pyptc import DEFAULT_LIBRARY, PTC


DEFAULT_OUTPUT_DIR = MADX_DIR / "outputs" / "simplified_closed_orbit_comparison"
DEFAULT_ERROR_TABLE = MADX_DIR / "reference_errors" / "jan26_survey_corrected.tfs"
MISALIGNMENT_COMPONENTS = ("DX", "DY", "DS", "DTHETA", "DPHI", "DPSI")


def require_matplotlib(output_dir: Path):
    os.environ.setdefault("MPLCONFIGDIR", str(output_dir / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def parse_tfs(path: Path) -> dict[str, np.ndarray | list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    columns = None
    data_start = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("*"):
            columns = stripped.lstrip("*").split()
        elif stripped.startswith("$") and columns is not None:
            data_start = index + 1
            break
    if columns is None or data_start is None:
        raise ValueError(f"Could not parse TFS table: {path}")

    values: dict[str, list[float] | list[str]] = {column.lower(): [] for column in columns}
    string_columns: set[str] = set()
    for line in lines[data_start:]:
        stripped = line.strip()
        if not stripped or stripped.startswith(("@", "*", "$", "!")):
            continue
        parts = stripped.split()
        if len(parts) < len(columns):
            continue
        for column, token in zip(columns, parts):
            key = column.lower()
            if key in {"name", "keyword"}:
                values[key].append(token.strip('"'))
                string_columns.add(key)
            else:
                try:
                    values[key].append(float(token.replace("D", "E").replace("d", "e")))
                except ValueError:
                    values[key].append(token.strip('"'))
                    string_columns.add(key)

    parsed: dict[str, np.ndarray | list[str]] = {}
    for key, value in values.items():
        parsed[key] = value if key in string_columns else np.asarray(value, dtype=float)
    return parsed


def write_csv(path: Path, header: str, data: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(path, data, delimiter=",", header=header, comments="")


def component_set(values: list[str] | None) -> set[str]:
    if not values:
        return set()
    out = {value.upper() for value in values}
    invalid = sorted(out.difference(MISALIGNMENT_COMPONENTS))
    if invalid:
        raise ValueError(f"Unknown misalignment components: {invalid}")
    return out


def write_filtered_error_table(source: Path, destination: Path, keep: set[str], flip: set[str] | None = None) -> Path:
    flip = flip or set()
    lines = source.read_text(encoding="utf-8").splitlines()
    columns: list[str] | None = None
    data_start: int | None = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("*"):
            columns = stripped.lstrip("*").split()
        elif stripped.startswith("$") and columns is not None:
            data_start = index + 1
            break
    if columns is None or data_start is None:
        raise ValueError(f"Could not parse TFS error table: {source}")

    component_indices = {component: columns.index(component) for component in MISALIGNMENT_COMPONENTS if component in columns}
    missing = sorted(set(MISALIGNMENT_COMPONENTS).difference(component_indices))
    if missing:
        raise ValueError(f"Error table {source} is missing components: {missing}")

    output_lines = lines[:data_start]
    for line in lines[data_start:]:
        stripped = line.strip()
        if not stripped or stripped.startswith(("@", "*", "$", "!")):
            output_lines.append(line)
            continue
        parts = stripped.split()
        if len(parts) < len(columns):
            output_lines.append(line)
            continue
        for component, col_index in component_indices.items():
            value = float(parts[col_index].replace("D", "E").replace("d", "e"))
            if component not in keep:
                value = 0.0
            elif component in flip:
                value = -value
            parts[col_index] = f"{value:.12e}"
        output_lines.append(" ".join(parts))

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    return destination


def write_madx_compare_script(path: Path, error_table_name: str) -> None:
    path.write_text(
        f"""TITLE, "MAD-X closed orbit comparison for PyPTC";
CALL, FILE = "ISIS_Lattice/ISIS.injected_beam";
CALL, FILE = "ISIS_Lattice/ISIS.elements";
CALL, FILE = "ISIS_Lattice/ISIS.strength";
CALL, FILE = "ISIS_Lattice/ISIS.sequence";

USE, SEQUENCE=synchrotron;
SELECT, FLAG=TWISS, CLEAR;
SELECT, FLAG=TWISS, COLUMN=name, s, x, px, y, py, betx, bety, alfx, alfy, dx, dpx, dy, dpy, mux, muy;
TWISS, SAVE, FILE="madx_bare_twiss.tfs";

EOPTION, ADD=false;
READMYTABLE, FILE="ErrorTables/{error_table_name}", TABLE=efield;
SETERR, TABLE=efield;
ESAVE, FILE="madx_applied_errors.tfs";

SELECT, FLAG=TWISS, CLEAR;
SELECT, FLAG=TWISS, COLUMN=name, s, x, px, y, py, betx, bety, alfx, alfy, dx, dpx, dy, dpy, mux, muy;
TWISS, SAVE, FILE="madx_misaligned_twiss.tfs";
STOP;
""",
        encoding="utf-8",
    )


def run_madx_closed_orbits(args: argparse.Namespace, output_dir: Path, error_table: Path) -> dict[str, Path]:
    lattice_dir = LATTICES[args.lattice].resolve()
    madx_dir = output_dir / "madx_twiss"
    madx_dir.mkdir(parents=True, exist_ok=True)
    copytree_contents(lattice_dir, madx_dir / "ISIS_Lattice")
    (madx_dir / "ErrorTables").mkdir(parents=True, exist_ok=True)
    shutil.copy2(error_table, madx_dir / "ErrorTables" / error_table.name)
    script = madx_dir / "Compare_Closed_Orbits.madx"
    write_madx_compare_script(script, error_table.name)

    with script.open("r", encoding="utf-8") as input_file:
        result = subprocess.run(
            [str(args.madx.resolve())],
            stdin=input_file,
            cwd=madx_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    (madx_dir / "madx_closed_orbit.log").write_text(result.stdout, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"MAD-X closed-orbit run failed; see {madx_dir / 'madx_closed_orbit.log'}")

    paths = {
        "bare": madx_dir / "madx_bare_twiss.tfs",
        "misaligned": madx_dir / "madx_misaligned_twiss.tfs",
        "applied_errors": madx_dir / "madx_applied_errors.tfs",
        "log": madx_dir / "madx_closed_orbit.log",
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise RuntimeError(f"MAD-X did not produce expected comparison outputs: {missing}")
    return paths


def run_pyptc_closed_orbits(args: argparse.Namespace, flat_file: Path, error_table: Path) -> tuple[np.ndarray, np.ndarray]:
    if not args.library.exists():
        raise FileNotFoundError(f"PyPTC shared library not found; run bash PyPTC/build/build_ptc.sh first: {args.library}")
    ptc = PTC(args.library)
    ptc.init_lattice(flat_file)
    bare_rows = ptc.all_node_twiss_orbit()
    if args.pyptc_convention == "madx":
        ptc.apply_madx_error_table(error_table, nonzero=False)
    elif args.pyptc_convention == "raw":
        records = []
        from pyptc import read_madx_error_table

        records = read_madx_error_table(error_table, nonzero=False)
        ptc.apply_misalignments(records, madx_convention=False)
    else:
        raise ValueError(f"Unknown PyPTC convention: {args.pyptc_convention}")
    ptc.update_twiss()
    misaligned_rows = ptc.all_node_twiss_orbit()
    return rows_to_orbit_array(bare_rows), rows_to_orbit_array(misaligned_rows)


def rows_to_orbit_array(rows: list[dict[str, float | int]]) -> np.ndarray:
    s = np.cumsum([float(row["length"]) for row in rows])
    return np.column_stack(
        [
            s,
            [float(row["orbitx"]) for row in rows],
            [float(row["orbitpx"]) for row in rows],
            [float(row["orbity"]) for row in rows],
            [float(row["orbitpy"]) for row in rows],
        ]
    )


def tfs_to_orbit_array(table: dict[str, np.ndarray | list[str]]) -> np.ndarray:
    return np.column_stack([table["s"], table["x"], table["px"], table["y"], table["py"]])


def interpolate_to(s_target: np.ndarray, source: np.ndarray) -> np.ndarray:
    order = np.argsort(source[:, 0])
    s = source[order, 0]
    values = source[order, 1:]
    unique_s, unique_index = np.unique(s, return_index=True)
    unique_values = values[unique_index]
    return np.column_stack([np.interp(s_target, unique_s, unique_values[:, col]) for col in range(unique_values.shape[1])])


def plot_comparison(path: Path, madx_bare: np.ndarray, madx_misaligned: np.ndarray, pyptc_bare: np.ndarray, pyptc_misaligned: np.ndarray) -> np.ndarray:
    plt = require_matplotlib(path.parent)
    pyptc_on_madx_bare = interpolate_to(madx_bare[:, 0], pyptc_bare)
    pyptc_on_madx_misaligned = interpolate_to(madx_misaligned[:, 0], pyptc_misaligned)
    residual = pyptc_on_madx_misaligned - madx_misaligned[:, 1:]
    comparison = np.column_stack([madx_misaligned[:, 0], madx_bare[:, 1], madx_misaligned[:, 1], pyptc_on_madx_bare[:, 0], pyptc_on_madx_misaligned[:, 0], madx_bare[:, 3], madx_misaligned[:, 3], pyptc_on_madx_bare[:, 2], pyptc_on_madx_misaligned[:, 2], residual[:, 0], residual[:, 2]])

    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    axes[0].plot(madx_bare[:, 0], madx_bare[:, 1] * 1.0e3, label="MAD-X bare x")
    axes[0].plot(madx_misaligned[:, 0], madx_misaligned[:, 1] * 1.0e3, label="MAD-X misaligned x")
    axes[0].plot(pyptc_bare[:, 0], pyptc_bare[:, 1] * 1.0e3, "--", label="PyPTC bare x")
    axes[0].plot(pyptc_misaligned[:, 0], pyptc_misaligned[:, 1] * 1.0e3, "--", label="PyPTC misaligned x")
    axes[0].set_ylabel("x orbit [mm]")
    axes[0].legend(loc="upper right", ncol=2)

    axes[1].plot(madx_bare[:, 0], madx_bare[:, 3] * 1.0e3, label="MAD-X bare y")
    axes[1].plot(madx_misaligned[:, 0], madx_misaligned[:, 3] * 1.0e3, label="MAD-X misaligned y")
    axes[1].plot(pyptc_bare[:, 0], pyptc_bare[:, 3] * 1.0e3, "--", label="PyPTC bare y")
    axes[1].plot(pyptc_misaligned[:, 0], pyptc_misaligned[:, 3] * 1.0e3, "--", label="PyPTC misaligned y")
    axes[1].set_ylabel("y orbit [mm]")
    axes[1].legend(loc="upper right", ncol=2)

    axes[2].plot(madx_misaligned[:, 0], residual[:, 0] * 1.0e3, label="PyPTC - MAD-X x")
    axes[2].plot(madx_misaligned[:, 0], residual[:, 2] * 1.0e3, label="PyPTC - MAD-X y")
    axes[2].set_xlabel("s [m]")
    axes[2].set_ylabel("residual [mm]")
    axes[2].legend(loc="upper right")
    for ax in axes:
        ax.grid(which="both", ls=":", lw=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return comparison


def run(args: argparse.Namespace) -> dict:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if not args.madx.exists():
        raise FileNotFoundError(f"MAD-X binary not found: {args.madx}")
    if not os.access(args.madx, os.X_OK):
        raise PermissionError(f"MAD-X binary is not executable: {args.madx}")
    if not args.madx_error_table.exists():
        raise FileNotFoundError(f"MAD-X error table not found: {args.madx_error_table}")
    keep_components = component_set(args.components) or set(MISALIGNMENT_COMPONENTS)
    pyptc_flip_components = component_set(args.pyptc_flip_components)

    if args.flat_file is not None:
        flat_file = args.flat_file.resolve()
    else:
        flat_output_dir = output_dir / "flat_file"
        generate_args = argparse.Namespace(lattice=args.lattice, madx=args.madx, output_dir=flat_output_dir)
        flat_summary = generate(generate_args)
        flat_file = Path(flat_summary["flat_file"])

    table_dir = output_dir / "error_tables"
    madx_error_table = write_filtered_error_table(args.madx_error_table, table_dir / "madx_errors.tfs", keep_components)
    pyptc_error_table = write_filtered_error_table(
        args.madx_error_table,
        table_dir / "pyptc_errors.tfs",
        keep_components,
        flip=pyptc_flip_components,
    )

    if args.madx_reference_twiss is not None:
        if not args.madx_reference_twiss.exists():
            raise FileNotFoundError(f"MAD-X reference Twiss not found: {args.madx_reference_twiss}")
        madx_misaligned = tfs_to_orbit_array(parse_tfs(args.madx_reference_twiss))
        madx_bare = madx_misaligned.copy()
        madx_bare[:, 1:] = 0.0
        madx_paths = {"reference": args.madx_reference_twiss.resolve()}
    else:
        madx_paths = run_madx_closed_orbits(args, output_dir, madx_error_table)
        madx_bare = tfs_to_orbit_array(parse_tfs(madx_paths["bare"]))
        madx_misaligned = tfs_to_orbit_array(parse_tfs(madx_paths["misaligned"]))
    pyptc_bare, pyptc_misaligned = run_pyptc_closed_orbits(args, flat_file, pyptc_error_table)

    write_csv(output_dir / "madx_bare_closed_orbit.csv", "s,x,px,y,py", madx_bare)
    write_csv(output_dir / "madx_misaligned_closed_orbit.csv", "s,x,px,y,py", madx_misaligned)
    write_csv(output_dir / "pyptc_bare_closed_orbit.csv", "s,x,px,y,py", pyptc_bare)
    write_csv(output_dir / "pyptc_misaligned_closed_orbit.csv", "s,x,px,y,py", pyptc_misaligned)
    comparison = plot_comparison(output_dir / "madx_vs_pyptc_closed_orbit_comparison.png", madx_bare, madx_misaligned, pyptc_bare, pyptc_misaligned)
    write_csv(
        output_dir / "madx_vs_pyptc_closed_orbit_comparison.csv",
        "s,madx_bare_x,madx_misaligned_x,pyptc_bare_x_interp,pyptc_misaligned_x_interp,madx_bare_y,madx_misaligned_y,pyptc_bare_y_interp,pyptc_misaligned_y_interp,pyptc_minus_madx_x,pyptc_minus_madx_y",
        comparison,
    )

    summary = {
        "flat_file": str(flat_file),
        "madx_error_table": str(args.madx_error_table.resolve()),
        "madx_reference_twiss": str(args.madx_reference_twiss.resolve()) if args.madx_reference_twiss is not None else None,
        "madx_filtered_error_table": str(madx_error_table),
        "pyptc_filtered_error_table": str(pyptc_error_table),
        "components": sorted(keep_components),
        "pyptc_convention": args.pyptc_convention,
        "pyptc_flip_components": sorted(pyptc_flip_components),
        "madx_bare_max_x_m": float(np.max(np.abs(madx_bare[:, 1]))),
        "madx_bare_max_y_m": float(np.max(np.abs(madx_bare[:, 3]))),
        "madx_misaligned_max_x_m": float(np.max(np.abs(madx_misaligned[:, 1]))),
        "madx_misaligned_max_y_m": float(np.max(np.abs(madx_misaligned[:, 3]))),
        "pyptc_bare_max_x_m": float(np.max(np.abs(pyptc_bare[:, 1]))),
        "pyptc_bare_max_y_m": float(np.max(np.abs(pyptc_bare[:, 3]))),
        "pyptc_misaligned_max_x_m": float(np.max(np.abs(pyptc_misaligned[:, 1]))),
        "pyptc_misaligned_max_y_m": float(np.max(np.abs(pyptc_misaligned[:, 3]))),
        "residual_max_x_m": float(np.max(np.abs(comparison[:, 9]))),
        "residual_max_y_m": float(np.max(np.abs(comparison[:, 10]))),
        "comparison_png": str(output_dir / "madx_vs_pyptc_closed_orbit_comparison.png"),
    }
    if args.response_threshold > 0.0 and summary["pyptc_misaligned_max_x_m"] <= args.response_threshold and summary["pyptc_misaligned_max_y_m"] <= args.response_threshold:
        raise AssertionError("PyPTC misaligned orbit response is below threshold")
    if args.response_threshold > 0.0 and summary["madx_misaligned_max_x_m"] <= args.response_threshold and summary["madx_misaligned_max_y_m"] <= args.response_threshold:
        raise AssertionError("MAD-X misaligned orbit response is below threshold")
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lattice", choices=sorted(LATTICES), default="simplified")
    parser.add_argument("--madx", type=Path, default=DEFAULT_MADX)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--flat-file", type=Path)
    parser.add_argument("--madx-error-table", type=Path, default=DEFAULT_ERROR_TABLE)
    parser.add_argument("--madx-reference-twiss", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--response-threshold", type=float, default=1.0e-4)
    parser.add_argument("--components", nargs="+", choices=MISALIGNMENT_COMPONENTS)
    parser.add_argument("--pyptc-convention", choices=("madx", "raw"), default="madx")
    parser.add_argument("--pyptc-flip-components", nargs="+", choices=MISALIGNMENT_COMPONENTS)
    args = parser.parse_args()
    print(json.dumps(run(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
