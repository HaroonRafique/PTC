"""Optics convenience functions for PyPTC."""

from .lattice import not_exposed


def exact_tunes(ptc):
    return ptc.tunes()


def chromaticity(ptc):
    return ptc.chromaticities()


def one_turn_map(*_args, **_kwargs):
    raise not_exposed("One-turn map access")


def normal_form(*_args, **_kwargs):
    raise not_exposed("Normal-form access")
