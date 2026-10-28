#!/usr/bin/env python3
"""Internal independent-process worker for bounded PyPTC tracking evidence."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

mode, repo_arg, flat_arg, library_arg, initial_json, turns_text, summary_arg, history_arg = sys.argv[1:]
repo_root, flat_file, library = map(Path, (repo_arg, flat_arg, library_arg))
summary_path, history_path = Path(summary_arg), Path(history_arg)
sys.path.insert(0, str(repo_root))
from pyptc import PTC

initial = json.loads(initial_json)
if isinstance(initial, list):
    initial = dict(zip(("x_m", "xp_rad", "y_m", "yp_rad", "z_m", "dE_gev"), initial))
turns = int(turns_text)
ptc = PTC(library)
ptc.init_lattice(flat_file)
if mode == "history":
    initial_row = {"turn": 0.0, **initial}
    snapshots = ptc.track_bunch(np.asarray([[initial[key] for key in ("x_m", "xp_rad", "y_m", "yp_rad", "z_m", "dE_gev")]], dtype=float), turns=turns, record_turns=True)
    rows = [initial_row]
    for turn, snapshot in enumerate(snapshots, start=1):
        values = np.asarray(snapshot[0], dtype=float)
        rows.append({"turn": float(turn), "x_m": float(values[0]), "xp_rad": float(values[1]), "y_m": float(values[2]), "yp_rad": float(values[3]), "z_m": float(values[4]), "dE_gev": float(values[5])})
    with history_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "status": "complete" if len(rows) == turns + 1 else "blocked-incomplete-history",
        "recorded_samples": len(rows),
        "requested_turns": turns,
        "finite": bool(np.isfinite(np.asarray([[value for key, value in row.items() if key != "turn"] for row in rows], dtype=float)).all()),
        "history_file": history_path.name,
    }
elif mode == "loss":
    ptc_coordinates = [initial["x_m"], initial["xp_rad"], initial["y_m"], initial["yp_rad"], 0.0, 0.0]
    final, loss = ptc.track_particle_ptc_with_loss(ptc_coordinates, turns=turns)
    summary = {
        "status": "complete" if np.isfinite(final).all() else "blocked-nonfinite",
        "final_ptc_coordinates": [float(value) for value in final],
        "finite": bool(np.isfinite(final).all()),
        "loss": loss,
        "requested_turns": turns,
    }
else:
    raise SystemExit(f"unknown internal tracking mode: {mode}")
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
