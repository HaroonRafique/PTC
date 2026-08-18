#!/usr/bin/env python3
"""Run bare vs single-magnet-misaligned standalone PTC tracking."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

PYPTC_DIR = Path(__file__).resolve().parents[1]
ROOT = PYPTC_DIR.parent
if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))

from flatfile_misalign import apply_single_misalignment
from ptc import DEFAULT_LATTICE, DEFAULT_LIBRARY, PTC
from pyptc import generate_matched_gaussian_4d, pyparticlebunch_source


DEFAULT_OUTPUT = PYPTC_DIR / "artifacts" / "outputs" / "misalignment_experiment"


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_array_csv(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(path, np.asarray(array, dtype=float), delimiter=",", header="x,xp,y,yp,z,dE", comments="")


def plot_results(output_dir: Path) -> None:
    try:
        os.environ.setdefault("MPLCONFIGDIR", str(output_dir / ".matplotlib"))
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    orbit = np.genfromtxt(output_dir / "orbit_difference_nodes.csv", delimiter=",", names=True)
    if orbit.size:
        s = np.cumsum(orbit["length"])
        plt.figure(figsize=(8, 4))
        plt.plot(s, orbit["delta_orbitx"], label="dx closed orbit")
        plt.plot(s, orbit["delta_orbity"], label="dy closed orbit")
        plt.xlabel("s over PTC/ORBIT nodes [m]")
        plt.ylabel("closed orbit difference [m]")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "closed_orbit_difference.png", dpi=160)
        plt.close()

    initial = np.genfromtxt(output_dir / "bare_bunch_initial.csv", delimiter=",", names=True)
    bare = np.genfromtxt(output_dir / "bare_bunch_final.csv", delimiter=",", names=True)
    mis = np.genfromtxt(output_dir / "misaligned_bunch_final.csv", delimiter=",", names=True)
    if initial.size and bare.size and mis.size:
        plt.figure(figsize=(6, 5))
        plt.scatter(initial["x"], initial["xp"], s=8, alpha=0.5, label="initial")
        plt.scatter(bare["x"], bare["xp"], s=8, alpha=0.5, label="bare final")
        plt.scatter(mis["x"], mis["xp"], s=8, alpha=0.5, label="misaligned final")
        plt.xlabel("x [m]")
        plt.ylabel("xp")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "bunch_x_xp_comparison.png", dpi=160)
        plt.close()


def make_bunch(args: argparse.Namespace, twiss0: dict[str, float | int]) -> np.ndarray:
    return generate_matched_gaussian_4d(
        n=args.particles,
        emittance_x=args.emit_x,
        emittance_y=args.emit_y,
        alpha_x=float(twiss0["alphax"]),
        beta_x=float(twiss0["betax"]),
        alpha_y=float(twiss0["alphay"]),
        beta_y=float(twiss0["betay"]),
        x_limit=args.limit,
        y_limit=args.limit,
        seed=args.seed,
    )


def run_case(lattice: Path, library: Path, initial_bunch: Path, output_dir: Path, turns: int) -> dict[str, object]:
    ptc = PTC(library)
    ptc.init_lattice(lattice)
    summary = ptc.machine_summary()
    orbit_rows = ptc.all_node_twiss_orbit()
    bunch0 = load_bunch_csv(initial_bunch)
    final = ptc.track_bunch(bunch0, turns=turns)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "orbit_nodes.csv", orbit_rows)
    write_array_csv(output_dir / "bunch_final.csv", final)
    return {"summary": summary, "orbit_rows": orbit_rows, "final_bunch": np.asarray(final).tolist()}


def load_bunch_csv(path: Path) -> np.ndarray:
    bunch = np.loadtxt(path, delimiter=",", skiprows=1)
    if bunch.ndim == 1:
        bunch = bunch.reshape(1, 6)
    return np.asarray(bunch, dtype=float)


def run_case_subprocess(case_name: str, lattice: Path, library: Path, initial_bunch: Path, output_dir: Path, turns: int) -> dict:
    case_dir = output_dir / "_cases" / case_name
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "_run_case",
        "--lattice",
        str(lattice),
        "--library",
        str(library),
        "--initial-bunch",
        str(initial_bunch),
        "--output-dir",
        str(case_dir),
        "--turns",
        str(turns),
    ]
    env = os.environ.copy()
    subprocess.run(cmd, check=True, cwd=PYPTC_DIR, env=env)
    return json.loads((case_dir / "case_summary.json").read_text(encoding="utf-8"))


def compare_orbits(bare_rows: list[dict], mis_rows: list[dict]) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    for bare, mis in zip(bare_rows, mis_rows):
        rows.append(
            {
                "node_index": int(bare["node_index"]),
                "length": float(bare["length"]),
                "bare_orbitx": float(bare["orbitx"]),
                "bare_orbitpx": float(bare["orbitpx"]),
                "bare_orbity": float(bare["orbity"]),
                "bare_orbitpy": float(bare["orbitpy"]),
                "misaligned_orbitx": float(mis["orbitx"]),
                "misaligned_orbitpx": float(mis["orbitpx"]),
                "misaligned_orbity": float(mis["orbity"]),
                "misaligned_orbitpy": float(mis["orbitpy"]),
                "delta_orbitx": float(mis["orbitx"]) - float(bare["orbitx"]),
                "delta_orbitpx": float(mis["orbitpx"]) - float(bare["orbitpx"]),
                "delta_orbity": float(mis["orbity"]) - float(bare["orbity"]),
                "delta_orbitpy": float(mis["orbitpy"]) - float(bare["orbitpy"]),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    case_parser = subparsers.add_parser("_run_case")
    case_parser.add_argument("--lattice", type=Path, required=True)
    case_parser.add_argument("--library", type=Path, required=True)
    case_parser.add_argument("--initial-bunch", type=Path, required=True)
    case_parser.add_argument("--output-dir", type=Path, required=True)
    case_parser.add_argument("--turns", type=int, required=True)

    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--lattice", type=Path, default=DEFAULT_LATTICE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--element", default="SP0_QF")
    parser.add_argument("--occurrence", type=int, default=1)
    parser.add_argument("--dx", type=float, default=0.003)
    parser.add_argument("--dy", type=float, default=0.0)
    parser.add_argument("--ds", type=float, default=0.0)
    parser.add_argument("--particles", type=int, default=100)
    parser.add_argument("--turns", type=int, default=1)
    parser.add_argument("--emit-x", type=float, default=1.0e-6)
    parser.add_argument("--emit-y", type=float, default=1.0e-6)
    parser.add_argument("--limit", type=float, default=5.0)
    parser.add_argument("--seed", type=int, default=12345)

    args = parser.parse_args()

    args.library = args.library.resolve()
    args.lattice = args.lattice.resolve()
    args.output_dir = args.output_dir.resolve()
    if hasattr(args, "initial_bunch"):
        args.initial_bunch = args.initial_bunch.resolve()

    if args.command == "_run_case":
        result = run_case(args.lattice, args.library, args.initial_bunch, args.output_dir, args.turns)
        slim = {
            "summary": result["summary"],
            "orbit_rows": result["orbit_rows"],
        }
        (args.output_dir / "case_summary.json").write_text(
            json.dumps(slim, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)
    lattice_dir = args.output_dir / "lattices"
    mis_lattice = lattice_dir / f"{args.element}_occ{args.occurrence}_dx{args.dx:g}.flt"
    applied = apply_single_misalignment(
        args.lattice,
        mis_lattice,
        args.element,
        dx=args.dx,
        dy=args.dy,
        ds=args.ds,
        occurrence=args.occurrence,
    )

    probe = PTC(args.library)
    probe.init_lattice(args.lattice)
    bare_summary = probe.machine_summary()
    twiss0 = probe.node_twiss_orbit(0)

    initial_bunch = make_bunch(args, twiss0)
    initial_path = args.output_dir / "bare_bunch_initial.csv"
    write_array_csv(initial_path, initial_bunch)

    bare_case = run_case_subprocess("bare", args.lattice, args.library, initial_path, args.output_dir, args.turns)
    mis_case = run_case_subprocess("misaligned", mis_lattice, args.library, initial_path, args.output_dir, args.turns)

    bare_orbit = bare_case["orbit_rows"]
    mis_orbit = mis_case["orbit_rows"]
    orbit_diff = compare_orbits(bare_orbit, mis_orbit)
    write_csv(args.output_dir / "bare_orbit_nodes.csv", bare_orbit)
    write_csv(args.output_dir / "misaligned_orbit_nodes.csv", mis_orbit)
    write_csv(args.output_dir / "orbit_difference_nodes.csv", orbit_diff)

    bare_final = load_bunch_csv(args.output_dir / "_cases" / "bare" / "bunch_final.csv")
    mis_final = load_bunch_csv(args.output_dir / "_cases" / "misaligned" / "bunch_final.csv")
    write_array_csv(args.output_dir / "bare_bunch_final.csv", bare_final)
    write_array_csv(args.output_dir / "misaligned_bunch_final.csv", mis_final)

    max_dx = max(abs(float(row["delta_orbitx"])) for row in orbit_diff) if orbit_diff else 0.0
    max_dy = max(abs(float(row["delta_orbity"])) for row in orbit_diff) if orbit_diff else 0.0
    bunch_delta = np.asarray(mis_final) - np.asarray(bare_final)
    rms_final_delta = np.sqrt(np.mean(bunch_delta**2, axis=0)).tolist()
    summary = {
        "bare_lattice": str(args.lattice),
        "misaligned_lattice": str(mis_lattice),
        "library": str(args.library),
        "pyparticlebunch_source": str(pyparticlebunch_source()),
        "machine": bare_summary,
        "misalignment": {
            "element": applied.element,
            "occurrence": applied.occurrence,
            "dx_m": applied.dx,
            "dy_m": applied.dy,
            "ds_m": applied.ds,
        },
        "particles": args.particles,
        "turns": args.turns,
        "max_abs_delta_orbitx_m": max_dx,
        "max_abs_delta_orbity_m": max_dy,
        "rms_final_bunch_delta_x_xp_y_yp_z_dE": rms_final_delta,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    plot_results(args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
