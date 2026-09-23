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
DEFAULT_ERROR_TABLE = MADX_DIR / "reference_errors" / "apr_2026_survey_corrected.tfs"
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
    headers: dict[str, float | str] = {}
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("@"):
            parts = stripped.split(maxsplit=3)
            if len(parts) == 4:
                token = parts[3].strip('"')
                try:
                    headers[parts[1].lower()] = float(token.replace("D", "E").replace("d", "e"))
                except ValueError:
                    headers[parts[1].lower()] = token
        elif stripped.startswith("*"):
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
    parsed.update(headers)
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


def run_pyptc_linear_rows(args: argparse.Namespace, flat_file: Path, error_table: Path) -> tuple[list[dict[str, float | int]], list[dict[str, float | int]]]:
    ptc = PTC(args.library)
    ptc.init_lattice(flat_file)
    bare_rows = ptc.all_node_twiss_orbit()
    ptc.apply_madx_error_table(error_table, nonzero=False)
    ptc.update_twiss()
    return bare_rows, ptc.all_node_twiss_orbit()


def run_pyptc_scalar_optics(args: argparse.Namespace, flat_file: Path, error_table: Path) -> tuple[dict[str, float], dict[str, float]]:
    ptc = PTC(args.library)
    ptc.init_lattice(flat_file)
    bare = ptc.tunes() | ptc.chromaticities()
    ptc.apply_madx_error_table(error_table, nonzero=False)
    ptc.update_twiss()
    return bare, ptc.tunes() | ptc.chromaticities()


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


def compare_series(madx_s: np.ndarray, madx_values: np.ndarray, pyptc_series: np.ndarray) -> np.ndarray:
    """Return s, MAD-X, interpolated PyPTC, and PyPTC-minus-MAD-X values."""
    pyptc_values = interpolate_to(np.asarray(madx_s, dtype=float), np.asarray(pyptc_series, dtype=float))[:, 0]
    madx_values = np.asarray(madx_values, dtype=float)
    return np.column_stack([madx_s, madx_values, pyptc_values, pyptc_values - madx_values])


LINEAR_COLUMNS = ("betx", "bety", "alfx", "alfy", "dx", "dpx", "dy", "dpy", "mux", "muy", "x", "px", "y", "py")


def rows_to_linear_table(rows: list[dict[str, float | int]]) -> dict[str, np.ndarray]:
    s = np.cumsum([float(row["length"]) for row in rows])
    names = {"betx": "betax", "bety": "betay", "alfx": "alphax", "alfy": "alphay", "dx": "etax", "dpx": "etapx", "dy": "etay", "dpy": "etapy", "mux": "mux", "muy": "muy", "x": "orbitx", "px": "orbitpx", "y": "orbity", "py": "orbitpy"}
    return {name: np.column_stack([s, [float(row[names[name]]) for row in rows]]) for name in LINEAR_COLUMNS}


def plot_linear_optics(path: Path, madx: dict[str, np.ndarray | list[str]], pyptc_rows: list[dict[str, float | int]]) -> np.ndarray:
    """Plot all common node/TWISS linear quantities and return long-form residual data."""
    plt = require_matplotlib(path.parent)
    pyptc = rows_to_linear_table(pyptc_rows)
    panels = (("betx", "bety"), ("alfx", "alfy"), ("dx", "dpx"), ("dy", "dpy"), ("mux", "muy"), ("x", "px"), ("y", "py"))
    fig, axes = plt.subplots(len(panels), 2, figsize=(13, 20), sharex=True)
    records = []
    for row_axes, pair in zip(axes, panels):
        for axis, name in zip(row_axes, pair):
            values = np.asarray(madx[name], dtype=float)
            compared = compare_series(np.asarray(madx["s"], dtype=float), values, pyptc[name])
            scale = 1.0e3 if name in {"x", "y"} else 1.0
            axis.plot(compared[:, 0], compared[:, 1] * scale, label=f"MAD-X {name}")
            axis.plot(compared[:, 0], compared[:, 2] * scale, "--", label=f"PyPTC {name}")
            axis.set_ylabel(f"{name}{' [mm]' if scale != 1.0 else ''}")
            axis.grid(which="both", ls=":", lw=0.5)
            axis.legend(loc="best", fontsize=8)
            records.extend(np.column_stack([np.full(len(compared), LINEAR_COLUMNS.index(name)), compared]).tolist())
    axes[-1, 0].set_xlabel("s [m]"); axes[-1, 1].set_xlabel("s [m]")
    fig.tight_layout(); fig.savefig(path, dpi=170); plt.close(fig)
    return np.asarray(records, dtype=float)


def plot_scalar_optics(path: Path, madx_bare: dict[str, np.ndarray | list[str]], madx_error: dict[str, np.ndarray | list[str]], pyptc_bare: dict[str, float], pyptc_error: dict[str, float]) -> dict[str, dict[str, float]]:
    plt = require_matplotlib(path.parent)
    sources = (("bare", madx_bare, pyptc_bare), ("jan26", madx_error, pyptc_error))
    mapping = (("qx", "q1"), ("qy", "q2"), ("chromx", "dq1"), ("chromy", "dq2"))
    result = {case: {name: float(table[key]) for name, key in mapping} | {f"pyptc_{name}": float(values[name]) for name, _ in mapping} for case, table, values in sources}
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for axis, (case, _table, _values) in zip(axes, sources):
        data = result[case]
        names = [name for name, _ in mapping]
        x = np.arange(len(names))
        axis.bar(x - 0.18, [data[name] for name in names], 0.36, label="MAD-X")
        axis.bar(x + 0.18, [data[f"pyptc_{name}"] for name in names], 0.36, label="PyPTC")
        axis.set_title(case); axis.set_xticks(x, names); axis.grid(axis="y", ls=":", lw=0.5); axis.legend()
    fig.tight_layout(); fig.savefig(path, dpi=170); plt.close(fig)
    return result


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


def plot_distorted_reference_comparison(path: Path, madx_distorted: np.ndarray, pyptc_distorted: np.ndarray) -> np.ndarray:
    plt = require_matplotlib(path.parent)
    pyptc_on_madx = interpolate_to(madx_distorted[:, 0], pyptc_distorted)
    residual = pyptc_on_madx - madx_distorted[:, 1:]
    comparison = np.column_stack(
        [
            madx_distorted[:, 0],
            madx_distorted[:, 1],
            pyptc_on_madx[:, 0],
            madx_distorted[:, 3],
            pyptc_on_madx[:, 2],
            residual[:, 0],
            residual[:, 2],
        ]
    )

    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    axes[0].plot(madx_distorted[:, 0], madx_distorted[:, 1] * 1.0e3, label="MAD-X latest survey corrected x")
    axes[0].plot(pyptc_distorted[:, 0], pyptc_distorted[:, 1] * 1.0e3, "--", label="PyPTC latest survey corrected x")
    axes[0].set_ylabel("x orbit [mm]")
    axes[0].legend(loc="upper right")

    axes[1].plot(madx_distorted[:, 0], madx_distorted[:, 3] * 1.0e3, label="MAD-X latest survey corrected y")
    axes[1].plot(pyptc_distorted[:, 0], pyptc_distorted[:, 3] * 1.0e3, "--", label="PyPTC latest survey corrected y")
    axes[1].set_ylabel("y orbit [mm]")
    axes[1].legend(loc="upper right")

    axes[2].plot(madx_distorted[:, 0], residual[:, 0] * 1.0e3, label="PyPTC - MAD-X x")
    axes[2].plot(madx_distorted[:, 0], residual[:, 2] * 1.0e3, label="PyPTC - MAD-X y")
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
    needs_madx = args.flat_file is None or args.madx_reference_twiss is None
    if needs_madx:
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
        madx_distorted = tfs_to_orbit_array(parse_tfs(args.madx_reference_twiss))
        madx_paths = {"reference": args.madx_reference_twiss.resolve()}
        pyptc_bare, pyptc_distorted = run_pyptc_closed_orbits(args, flat_file, pyptc_error_table)

        write_csv(output_dir / "madx_distorted_closed_orbit.csv", "s,x,px,y,py", madx_distorted)
        write_csv(output_dir / "pyptc_distorted_closed_orbit.csv", "s,x,px,y,py", pyptc_distorted)
        write_csv(output_dir / "pyptc_bare_closed_orbit.csv", "s,x,px,y,py", pyptc_bare)
        comparison = plot_distorted_reference_comparison(output_dir / "madx_vs_pyptc_closed_orbit_comparison.png", madx_distorted, pyptc_distorted)
        write_csv(
            output_dir / "madx_vs_pyptc_closed_orbit_comparison.csv",
            "s,madx_distorted_x,pyptc_distorted_x_interp,madx_distorted_y,pyptc_distorted_y_interp,pyptc_minus_madx_x,pyptc_minus_madx_y",
            comparison,
        )

        summary = {
            "flat_file": str(flat_file),
            "madx_error_table": str(args.madx_error_table.resolve()),
            "madx_reference_twiss": str(args.madx_reference_twiss.resolve()),
            "madx_distorted_source": str(args.madx_reference_twiss.resolve()),
            "pyptc_filtered_error_table": str(pyptc_error_table),
            "components": sorted(keep_components),
            "pyptc_convention": args.pyptc_convention,
            "pyptc_flip_components": sorted(pyptc_flip_components),
            "madx_distorted_max_x_m": float(np.max(np.abs(madx_distorted[:, 1]))),
            "madx_distorted_max_y_m": float(np.max(np.abs(madx_distorted[:, 3]))),
            "pyptc_bare_max_x_m": float(np.max(np.abs(pyptc_bare[:, 1]))),
            "pyptc_bare_max_y_m": float(np.max(np.abs(pyptc_bare[:, 3]))),
            "pyptc_distorted_max_x_m": float(np.max(np.abs(pyptc_distorted[:, 1]))),
            "pyptc_distorted_max_y_m": float(np.max(np.abs(pyptc_distorted[:, 3]))),
            "residual_max_x_m": float(np.max(np.abs(comparison[:, 5]))),
            "residual_max_y_m": float(np.max(np.abs(comparison[:, 6]))),
            "comparison_png": str(output_dir / "madx_vs_pyptc_closed_orbit_comparison.png"),
        }
        if args.response_threshold > 0.0 and summary["pyptc_distorted_max_x_m"] <= args.response_threshold and summary["pyptc_distorted_max_y_m"] <= args.response_threshold:
            raise AssertionError("PyPTC distorted orbit response is below threshold")
        if args.response_threshold > 0.0 and summary["madx_distorted_max_x_m"] <= args.response_threshold and summary["madx_distorted_max_y_m"] <= args.response_threshold:
            raise AssertionError("MAD-X distorted orbit response is below threshold")
        (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return summary
    else:
        madx_paths = run_madx_closed_orbits(args, output_dir, madx_error_table)
        madx_bare_table = parse_tfs(madx_paths["bare"])
        madx_misaligned_table = parse_tfs(madx_paths["misaligned"])
        madx_bare = tfs_to_orbit_array(madx_bare_table)
        madx_misaligned = tfs_to_orbit_array(madx_misaligned_table)
    pyptc_bare, pyptc_misaligned = run_pyptc_closed_orbits(args, flat_file, pyptc_error_table)

    if args.distorted_only:
        write_csv(output_dir / "madx_distorted_closed_orbit.csv", "s,x,px,y,py", madx_misaligned)
        write_csv(output_dir / "pyptc_distorted_closed_orbit.csv", "s,x,px,y,py", pyptc_misaligned)
        comparison = plot_distorted_reference_comparison(output_dir / "madx_vs_pyptc_closed_orbit_comparison.png", madx_misaligned, pyptc_misaligned)
        write_csv(
            output_dir / "madx_vs_pyptc_closed_orbit_comparison.csv",
            "s,madx_distorted_x,pyptc_distorted_x_interp,madx_distorted_y,pyptc_distorted_y_interp,pyptc_minus_madx_x,pyptc_minus_madx_y",
            comparison,
        )
        summary = {
            "flat_file": str(flat_file),
            "madx_error_table": str(args.madx_error_table.resolve()),
            "madx_filtered_error_table": str(madx_error_table),
            "pyptc_filtered_error_table": str(pyptc_error_table),
            "components": sorted(keep_components),
            "pyptc_convention": args.pyptc_convention,
            "pyptc_flip_components": sorted(pyptc_flip_components),
            "madx_reference_twiss": None,
            "madx_distorted_max_x_m": float(np.max(np.abs(madx_misaligned[:, 1]))),
            "madx_distorted_max_y_m": float(np.max(np.abs(madx_misaligned[:, 3]))),
            "pyptc_distorted_max_x_m": float(np.max(np.abs(pyptc_misaligned[:, 1]))),
            "pyptc_distorted_max_y_m": float(np.max(np.abs(pyptc_misaligned[:, 3]))),
            "residual_max_x_m": float(np.max(np.abs(comparison[:, 5]))),
            "residual_max_y_m": float(np.max(np.abs(comparison[:, 6]))),
            "comparison_png": str(output_dir / "madx_vs_pyptc_closed_orbit_comparison.png"),
        }
        if args.response_threshold > 0.0 and summary["pyptc_distorted_max_x_m"] <= args.response_threshold and summary["pyptc_distorted_max_y_m"] <= args.response_threshold:
            raise AssertionError("PyPTC distorted orbit response is below threshold")
        if args.response_threshold > 0.0 and summary["madx_distorted_max_x_m"] <= args.response_threshold and summary["madx_distorted_max_y_m"] <= args.response_threshold:
            raise AssertionError("MAD-X distorted orbit response is below threshold")
        (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return summary

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
    pyptc_bare_rows, pyptc_misaligned_rows = run_pyptc_linear_rows(args, flat_file, pyptc_error_table)
    pyptc_bare_scalars, pyptc_misaligned_scalars = run_pyptc_scalar_optics(args, flat_file, pyptc_error_table)
    bare_linear = plot_linear_optics(output_dir / "madx_vs_pyptc_linear_optics_bare.png", madx_bare_table, pyptc_bare_rows)
    misaligned_linear = plot_linear_optics(output_dir / "madx_vs_pyptc_linear_optics_jan26.png", madx_misaligned_table, pyptc_misaligned_rows)
    write_csv(output_dir / "madx_vs_pyptc_linear_optics_bare.csv", "quantity_index,s,madx,pyptc,pyptc_minus_madx", bare_linear)
    write_csv(output_dir / "madx_vs_pyptc_linear_optics_jan26.csv", "quantity_index,s,madx,pyptc,pyptc_minus_madx", misaligned_linear)
    scalar_optics = plot_scalar_optics(output_dir / "madx_vs_pyptc_scalar_optics.png", madx_bare_table, madx_misaligned_table, pyptc_bare_scalars, pyptc_misaligned_scalars)

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
        "linear_optics_bare_png": str(output_dir / "madx_vs_pyptc_linear_optics_bare.png"),
        "linear_optics_jan26_png": str(output_dir / "madx_vs_pyptc_linear_optics_jan26.png"),
        "scalar_optics": scalar_optics,
        "scalar_optics_png": str(output_dir / "madx_vs_pyptc_scalar_optics.png"),
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
    parser.add_argument("--distorted-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
