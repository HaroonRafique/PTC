"""Contracts for the slide-ready MAD-X/PyPTC benchmark artifacts."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np

PYPTC_DIR = Path(__file__).resolve().parents[1]
if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))
MADX_DIR = PYPTC_DIR / "workflows" / "madx"
if str(MADX_DIR) not in sys.path:
    sys.path.insert(0, str(MADX_DIR))

from compare_isis_apertures import aperture_residual_rows
from compare_madx_pyptc_closed_orbits import LINEAR_COLUMNS, LINEAR_TOPICS, residual_metrics


class MadxOpticsBenchmarkTests(unittest.TestCase):
    def test_topics_cover_every_shared_node_quantity_once(self) -> None:
        quantities = tuple(quantity for topic in LINEAR_TOPICS.values() for quantity in topic)
        self.assertEqual(set(quantities), set(LINEAR_COLUMNS))
        self.assertEqual(len(quantities), len(LINEAR_COLUMNS))

    def test_residual_metrics_keep_native_values(self) -> None:
        records = np.asarray([[0, 0.0, 1.0, 1.1, 0.1], [0, 1.0, 2.0, 1.8, -0.2]])
        metrics = residual_metrics(records)
        self.assertAlmostEqual(metrics["betx"]["max_abs"], 0.2)
        self.assertAlmostEqual(metrics["betx"]["rms"], np.sqrt(0.025))

    def test_aperture_residuals_interpolate_madx_at_pyptc_positions(self) -> None:
        class Record:
            def __init__(self, s, half_x, half_y):
                self.s, self.half_x, self.half_y = s, half_x, half_y

        rows = aperture_residual_rows(
            [Record(0.0, 1.0, 2.0), Record(2.0, 3.0, 6.0)],
            [{"s": 1.0, "x": 2.2, "y": 4.1}],
        )
        np.testing.assert_allclose(rows, [[1.0, 2.0, 2.2, 4.0, 4.1]])

    def test_committed_baseline_has_complete_provenance(self) -> None:
        root = PYPTC_DIR / "test_outputs" / "madx_optics_benchmark"
        summary = json.loads((root / "benchmark_summary.json").read_text(encoding="utf-8"))
        optics = summary["optics"]
        self.assertEqual(set(optics["linear_optics"]), set(LINEAR_TOPICS))
        self.assertEqual(summary["aperture"]["missing_records"], 0)
        manifest = (root / "optics" / "case_manifest.md").read_text(encoding="utf-8")
        self.assertIn("Error-table SHA-256", manifest)
        self.assertIn("| Element | Occurrence | Fibre |", manifest)
        self.assertGreaterEqual(manifest.count("| SP"), 38)


if __name__ == "__main__":
    unittest.main()
