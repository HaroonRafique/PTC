#!/usr/bin/env python3
"""Focused checks for per-particle tune diagnostic helpers."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

PYPTC_DIR = Path(__file__).resolve().parents[1]
if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))

from pyptc import PTC, tune_summary, write_diagnostic_csv, write_tune_csv


class ParticleDiagnosticHelperTests(unittest.TestCase):
    def test_phase_tune_chooses_direction_near_reference(self) -> None:
        tune, phase0, phase_final = PTC._phase_tune([0.1, 0.8, 0.5, 0.2], reference_tune=0.3)
        self.assertAlmostEqual(tune, 0.3)
        self.assertAlmostEqual(phase0, 0.1)
        self.assertAlmostEqual(phase_final, -0.8)

    def test_tune_summary_uses_only_valid_survivors_for_statistics(self) -> None:
        rows = [
            {"qx": 0.31, "qy": 0.72, "survived": True, "lost": False, "valid_tune": True},
            {"qx": 0.33, "qy": 0.70, "survived": True, "lost": False, "valid_tune": True},
            {"qx": 0.40, "qy": 0.60, "survived": False, "lost": True, "valid_tune": True},
            {"qx": math.nan, "qy": math.nan, "survived": False, "lost": True, "valid_tune": False},
        ]
        summary = tune_summary(rows)
        self.assertEqual(summary["particles"], 4)
        self.assertEqual(summary["survived"], 2)
        self.assertEqual(summary["lost"], 2)
        self.assertEqual(summary["valid_tunes"], 3)
        self.assertEqual(summary["valid_survivor_tunes"], 2)
        self.assertEqual(summary["valid_lost_tunes"], 1)
        self.assertAlmostEqual(summary["qx_mean"], 0.32)
        self.assertAlmostEqual(summary["qy_mean"], 0.71)

    def test_csv_writers_include_diagnostic_and_tune_columns(self) -> None:
        rows = [
            {
                "particle": 0,
                "x": 1.0e-3,
                "qx": 0.31,
                "qy": 0.72,
                "jx": 1.0e-6,
                "jy": 2.0e-6,
                "survived": True,
                "lost": False,
                "lost_turn": 0,
                "lost_pos": 0,
                "completed_turns": 32,
                "valid_tune": True,
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            diagnostic_path = Path(tmp) / "bunch_diagnostics.csv"
            tune_path = Path(tmp) / "tune_footprint.csv"
            write_diagnostic_csv(diagnostic_path, rows)
            write_tune_csv(tune_path, rows)
            diagnostic_text = diagnostic_path.read_text(encoding="utf-8")
            tune_text = tune_path.read_text(encoding="utf-8")
        self.assertIn("x0,xp0,y0", diagnostic_text)
        self.assertIn("qx,qy,survived,lost", diagnostic_text)
        self.assertIn("particle,qx,qy,jx,jy,survived", tune_text)


if __name__ == "__main__":
    unittest.main()
