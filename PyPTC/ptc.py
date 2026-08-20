"""Backward-compatible import surface for early PyPTC scripts."""

from pyptc.core import DEFAULT_LATTICE, DEFAULT_LIBRARY, DEFAULT_SIMPLIFIED_LATTICE, LEGACY_READINESS_LATTICE, PTC, ensure_default_lattice

__all__ = [
    "DEFAULT_LATTICE",
    "DEFAULT_LIBRARY",
    "DEFAULT_SIMPLIFIED_LATTICE",
    "LEGACY_READINESS_LATTICE",
    "PTC",
    "ensure_default_lattice",
]
