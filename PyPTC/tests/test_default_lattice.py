#!/usr/bin/env python3
"""Checks for the canonical PyPTC test lattice default."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PYPTC_DIR = Path(__file__).resolve().parents[1]
if str(PYPTC_DIR) not in sys.path:
    sys.path.insert(0, str(PYPTC_DIR))

from pyptc import DEFAULT_LATTICE, DEFAULT_SIMPLIFIED_LATTICE, LEGACY_READINESS_LATTICE, ensure_default_lattice, read_flatfile_fibres


class DefaultLatticeTests(unittest.TestCase):
    def test_default_lattice_is_generated_simplified_lattice(self) -> None:
        self.assertEqual(DEFAULT_LATTICE, DEFAULT_SIMPLIFIED_LATTICE)
        self.assertNotEqual(DEFAULT_LATTICE, LEGACY_READINESS_LATTICE)

    def test_default_lattice_has_simplified_fibre_count(self) -> None:
        lattice = ensure_default_lattice()
        self.assertEqual(len(read_flatfile_fibres(lattice)), 586)


if __name__ == "__main__":
    unittest.main()
