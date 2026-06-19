#!/usr/bin/env python3
"""Functional standalone PTC lattice smoke test.

This test uses the Fortran entry points directly through ctypes. It does not
exercise the PyORBIT3 Bunch wrapper, because that wrapper requires PyORBIT3.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path

import numpy as np

from smoke_load_ptc import configure_signatures, load_library, verify_symbols


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def readiness_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def default_library_path() -> Path:
    return repo_root() / "build-standalone" / "libptc_orbit.so"


def default_output_dir() -> Path:
    return readiness_dir() / "outputs" / "PTC_standalone_outputs"


def call_ptc_init(lib, ptc_input: Path) -> None:
    encoded = str(ptc_input.resolve()).encode()
    lib.ptc_init_(encoded, len(encoded))


def get_ini_params(lib) -> dict[str, float | int]:
    n_nodes = np.ctypeslib.as_ctypes(np.array([0], dtype=np.int32))
    n_harm = np.ctypeslib.as_ctypes(np.array([0], dtype=np.int32))
    l_ring = np.ctypeslib.as_ctypes(np.array([0.0], dtype=np.float64))
    gamma_t = np.ctypeslib.as_ctypes(np.array([0.0], dtype=np.float64))
    lib.ptc_get_ini_params_(n_nodes, n_harm, l_ring, gamma_t)
    return {
        "n_nodes": int(n_nodes[0]),
        "n_harm": int(n_harm[0]),
        "l_ring": float(l_ring[0]),
        "gamma_t": float(gamma_t[0]),
    }


def get_syncpart(lib) -> dict[str, float | int]:
    mass = np.ctypeslib.as_ctypes(np.array([0.0], dtype=np.float64))
    charge = np.ctypeslib.as_ctypes(np.array([0], dtype=np.int32))
    kinetic = np.ctypeslib.as_ctypes(np.array([0.0], dtype=np.float64))
    lib.ptc_get_syncpart_(mass, charge, kinetic)
    return {
        "mass": float(mass[0]),
        "charge": int(charge[0]),
        "kinetic_energy": float(kinetic[0]),
    }


def get_twiss_init(lib) -> dict[str, float]:
    values = [np.ctypeslib.as_ctypes(np.array([0.0], dtype=np.float64)) for _ in range(12)]
    lib.ptc_get_twiss_init_(*values)
    names = (
        "betax",
        "betay",
        "alphax",
        "alphay",
        "etax",
        "etapx",
        "etay",
        "etapy",
        "orbitx",
        "orbitpx",
        "orbity",
        "orbitpy",
    )
    return {name: float(value[0]) for name, value in zip(names, values)}


def get_node_info(lib, node_index: int) -> dict[str, float | int]:
    idx = np.ctypeslib.as_ctypes(np.array([node_index], dtype=np.int32))
    values = [np.ctypeslib.as_ctypes(np.array([0.0], dtype=np.float64)) for _ in range(13)]
    lib.ptc_get_twiss_for_node_(idx, *values)
    names = (
        "length",
        "betax",
        "betay",
        "alphax",
        "alphay",
        "etax",
        "etapx",
        "etay",
        "etapy",
        "orbitx",
        "orbitpx",
        "orbity",
        "orbitpy",
    )
    data: dict[str, float | int] = {"node_index": node_index}
    data.update({name: float(value[0]) for name, value in zip(names, values)})
    return data


def make_particles(count: int) -> list[list[float]]:
    particles: list[list[float]] = []
    for i in range(count):
        angle = 2.0 * math.pi * i / max(count, 1)
        particles.append(
            [
                1.0e-4 * math.cos(angle),
                1.0e-5 * math.sin(angle),
                1.0e-4 * math.sin(angle),
                -1.0e-5 * math.cos(angle),
                0.0,
                0.0,
            ]
        )
    return particles


def track_particle(lib, node_index: int, particle: list[float]) -> list[float]:
    idx = np.ctypeslib.as_ctypes(np.array([node_index], dtype=np.int32))
    values = [np.ctypeslib.as_ctypes(np.array([value], dtype=np.float64)) for value in particle]
    lib.ptc_synchronous_set_(idx)
    lib.ptc_track_particle_(idx, *values)
    lib.ptc_synchronous_after_(idx)
    return [float(value[0]) for value in values]


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_node_csv(path: Path, rows: list[dict[str, float | int]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_particle_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    fieldnames = ["particle", "stage", "node_index", "x", "xp", "y", "yp", "pt", "ct"]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_outputs(output_dir: Path, node_rows: list[dict[str, float | int]], particle_rows: list[dict[str, float | int | str]]) -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(output_dir / "matplotlib-cache"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if node_rows:
        s = np.cumsum([float(row["length"]) for row in node_rows])
        betax = [float(row["betax"]) for row in node_rows]
        betay = [float(row["betay"]) for row in node_rows]
        plt.figure(figsize=(8, 4))
        plt.plot(s, betax, label="betax")
        plt.plot(s, betay, label="betay")
        plt.xlabel("s over sampled nodes")
        plt.ylabel("Twiss beta")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "sampled_twiss_beta.png", dpi=160)
        plt.close()

    initial = [row for row in particle_rows if row["stage"] == "initial"]
    final = [row for row in particle_rows if row["stage"] == "final"]
    if initial and final:
        plt.figure(figsize=(5, 5))
        plt.scatter([float(row["x"]) for row in initial], [float(row["y"]) for row in initial], label="initial")
        plt.scatter([float(row["x"]) for row in final], [float(row["y"]) for row in final], label="final")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "particle_xy_initial_final.png", dpi=160)
        plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, default=default_library_path())
    parser.add_argument("--ptc-input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=default_output_dir())
    parser.add_argument("--sample-nodes", type=int, default=80)
    parser.add_argument("--track-nodes", type=int, default=20)
    parser.add_argument("--particles", type=int, default=8)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    lib = load_library(args.library)
    verify_symbols(lib)
    configure_signatures(lib)
    call_ptc_init(lib, args.ptc_input)

    ini_params = get_ini_params(lib)
    syncpart = get_syncpart(lib)
    twiss_init = get_twiss_init(lib)

    n_nodes = int(ini_params["n_nodes"])
    sample_count = min(max(args.sample_nodes, 0), n_nodes)
    node_rows = [get_node_info(lib, index) for index in range(sample_count)]
    write_node_csv(args.output_dir / "sampled_nodes.csv", node_rows)

    particles = make_particles(args.particles)
    track_count = min(max(args.track_nodes, 0), n_nodes)
    particle_rows: list[dict[str, float | int | str]] = []
    for particle_index, particle in enumerate(particles):
        current = particle
        particle_rows.append(dict(zip(["x", "xp", "y", "yp", "pt", "ct"], current)) | {"particle": particle_index, "stage": "initial", "node_index": -1})
        for node_index in range(track_count):
            current = track_particle(lib, node_index, current)
        particle_rows.append(dict(zip(["x", "xp", "y", "yp", "pt", "ct"], current)) | {"particle": particle_index, "stage": "final", "node_index": track_count - 1})
    write_particle_csv(args.output_dir / "particles_initial_final.csv", particle_rows)

    summary = {
        "library": str(args.library),
        "ptc_input": str(args.ptc_input),
        "ini_params": ini_params,
        "syncpart": syncpart,
        "twiss_init": twiss_init,
        "sampled_nodes": sample_count,
        "tracked_nodes": track_count,
        "particles": args.particles,
        "note": "Direct ctypes PTC smoke test; not PyORBIT3 Bunch tracking.",
    }
    write_json(args.output_dir / "summary.json", summary)
    plot_outputs(args.output_dir, node_rows, particle_rows)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
