from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyptc.error_table import read_madx_error_table


class MadxEfieldReaderTests(unittest.TestCase):
    def read_table(self, row: str, columns: str = "NAME DX DY DS DPHI DTHETA DPSI K0L K1L K1SL MREX"):
        type_codes = " ".join(["%s"] + ["%le"] * (len(columns.split()) - 1))
        text = f"* {columns}\n$ {type_codes}\n{row}\n"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "efield.tfs"
            path.write_text(text, encoding="utf-8")
            return read_madx_error_table(path, nonzero=False)

    def test_parses_integrated_normal_skew_and_alignment_errors(self):
        record = self.read_table('"QF" 1e-3 0 0 0 0 0 0 2e-4 -3e-5 0')
        self.assertEqual(len(record), 1)
        row = record[0]
        self.assertEqual(row.name, "QF")
        self.assertEqual(row.dx, 1e-3)
        self.assertEqual(row.knl[0], 0.0)
        self.assertEqual(row.knl[1], 2e-4)
        self.assertEqual(row.ksl[1], -3e-5)
        self.assertTrue(row.has_misalignment())
        self.assertTrue(row.has_multipole_error())
        self.assertFalse(row.unsupported)

    def test_retains_nonzero_unsupported_fields_for_explicit_rejection(self):
        record = self.read_table('"BPM" 0 0 0 0 0 0 0 0 0 1.5e-4')[0]
        self.assertEqual(record.unsupported, (("MREX", 1.5e-4),))
        self.assertTrue(record.has_error())

    def test_nonzero_filter_keeps_field_only_rows(self):
        text = "* NAME DX DY DS DPHI DTHETA DPSI K1L K1SL\n$ %s %le %le %le %le %le %le %le %le\n\"QF\" 0 0 0 0 0 0 2e-4 0\n"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "efield.tfs"
            path.write_text(text, encoding="utf-8")
            record = read_madx_error_table(path)
        self.assertEqual(len(record), 1)
        self.assertEqual(record[0].knl[1], 2e-4)


if __name__ == "__main__":
    unittest.main()
