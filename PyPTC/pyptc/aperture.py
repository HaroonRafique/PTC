"""Aperture and loss convenience functions for PyPTC."""

from .lattice import not_exposed


def set_aperture(ptc, *args, **kwargs):
    return ptc.set_aperture(*args, **kwargs)


def disable_aperture(ptc, *args, **kwargs):
    return ptc.disable_aperture(*args, **kwargs)


def absolute_aperture(ptc):
    return ptc.absolute_aperture()


def set_absolute_aperture(ptc, value):
    return ptc.set_absolute_aperture(value)


def track_bunch_with_losses(ptc, *args, **kwargs):
    return ptc.track_bunch_with_losses(*args, **kwargs)


def normalized_aperture_scan(*_args, **_kwargs):
    raise not_exposed("Normalized aperture scan")


def tune_smear_tracking(*_args, **_kwargs):
    raise not_exposed("PTC tune-smear tracking")
