#!/usr/bin/env python3
"""Focused checks for the PyPTC aperture table readers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

PYPTC_DIR = Path(__file__).resolve().parents[1]
if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))

from pyptc import read_jvt_design_aperture, read_madx_aperture_file, read_madx_aperture_tfs


class ApertureParserTests(unittest.TestCase):
    def test_madx_assignment_reader_uses_rectangular_half_apertures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ISIS.aperture"
            path.write_text(
                "sp0_d0_00, APERTYPE=RECTANGLE, APERTURE={0.085, 0.062};\n"
                "sp0_qf_01, APERTYPE=RECTANGLE, APERTURE={8.1e-2, 6.0e-2};\n",
                encoding="utf-8",
            )
            records = read_madx_aperture_file(path)
        self.assertEqual([record.name for record in records], ["SP0_D0_00", "SP0_QF_01"])
        self.assertEqual(records[0].half_x, 0.085)
        self.assertEqual(records[0].half_y, 0.062)

    def test_madx_tfs_reader_extracts_aper_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "madx_aperture.tfs"
            path.write_text(
                '@ NAME %s "APERTURE"\n'
                "* NAME S APER_1 APER_2\n"
                "$ %s %le %le %le\n"
                '"SP0_D0_00" 0.1 0.085 0.062\n',
                encoding="utf-8",
            )
            records = read_madx_aperture_tfs(path)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].name, "SP0_D0_00")
        self.assertEqual(records[0].s, 0.1)

    def test_jvt_reader_converts_mm_to_m(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jvt.csv"
            path.write_text(
                "Element,Dist_Datum_D,Semi_Ap_H,Semi_Ap_V\n"
                "STT,0.0,87.959014,57.090587\n",
                encoding="utf-8",
            )
            records = read_jvt_design_aperture(path)
        self.assertEqual(len(records), 1)
        self.assertAlmostEqual(records[0].half_x, 0.087959014)
        self.assertAlmostEqual(records[0].half_y, 0.057090587)


if __name__ == "__main__":
    unittest.main()
