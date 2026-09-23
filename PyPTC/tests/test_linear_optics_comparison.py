"""Focused contracts for MAD-X/PyPTC linear-optics comparison helpers."""

from __future__ import annotations

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

from pyptc import DEFAULT_LIBRARY, PTC, ensure_default_lattice
from workflows.madx.compare_madx_pyptc_closed_orbits import compare_series


class LinearOpticsComparisonTests(unittest.TestCase):
    def test_node_phase_advances_cover_the_lattice_and_end_at_the_tunes(self) -> None:
        ptc = PTC(DEFAULT_LIBRARY)
        ptc.init_lattice(ensure_default_lattice())

        phases = ptc.node_phase_advances()
        self.assertEqual(phases.shape, (ptc.machine_summary()["n_nodes"], 2))
        self.assertTrue(np.isfinite(phases).all())
        self.assertGreater(np.ptp(phases[:, 0]), 0.1)
        self.assertGreater(np.ptp(phases[:, 1]), 0.1)
        self.assertGreater(phases[-1, 0], 0.0)
        self.assertGreater(phases[-1, 1], 0.0)

    def test_compare_series_interpolates_pyptc_onto_madx_positions(self) -> None:
        madx_s = np.asarray([0.0, 0.5, 1.0])
        madx_values = np.asarray([1.0, 2.0, 3.0])
        pyptc = np.asarray([[0.0, 1.0], [1.0, 5.0]])

        compared = compare_series(madx_s, madx_values, pyptc)

        np.testing.assert_allclose(compared[:, 0], madx_s)
        np.testing.assert_allclose(compared[:, 1], madx_values)
        np.testing.assert_allclose(compared[:, 2], [1.0, 3.0, 5.0])
        np.testing.assert_allclose(compared[:, 3], [0.0, 1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
