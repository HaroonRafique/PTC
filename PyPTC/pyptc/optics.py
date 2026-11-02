"""Optics convenience functions for PyPTC."""

import numpy as np

from .lattice import not_exposed


def exact_tunes(ptc):
    return ptc.tunes()


def chromaticity(ptc):
    return ptc.chromaticities()


def one_turn_map(ptc, step: float = 1e-6) -> dict:
    """Estimate the transverse one-turn Jacobian about the closed orbit.

    PyPTC currently exposes tracking but no native linear-map accessor. This
    uses centered finite differences in the PTC ``(x, px, y, py)`` coordinates.
    The returned matrix is diagnostic and should be checked for step
    convergence and symplecticity before cross-code interpretation.
    """
    if not np.isfinite(step) or step <= 0:
        raise ValueError("step must be a positive finite value")
    orbit = ptc.node_twiss_orbit(0)
    center = np.array([orbit["orbitx"], orbit["orbitpx"], orbit["orbity"], orbit["orbitpy"]], dtype=float)
    base = np.array([*center, 0.0, 0.0], dtype=float)
    columns = []
    for index in range(4):
        plus = base.copy(); plus[index] += step
        minus = base.copy(); minus[index] -= step
        plus_out, plus_info = ptc.track_particle_ptc_with_loss(plus, turns=1)
        minus_out, minus_info = ptc.track_particle_ptc_with_loss(minus, turns=1)
        if plus_info["lost"] or minus_info["lost"]:
            raise RuntimeError(f"finite-difference probe lost at coordinate {index}")
        columns.append((plus_out[:4] - minus_out[:4]) / (2.0 * step))
    matrix = np.column_stack(columns)
    j2 = np.array([[0.0, 1.0], [-1.0, 0.0]])
    j = np.zeros((4, 4)); j[:2, :2] = j2; j[2:, 2:] = j2
    return {
        "matrix": matrix,
        "coordinate_order": ["x", "px", "y", "py"],
        "reference_orbit": center,
        "finite_difference_step": float(step),
        "method": "centered finite-difference of one-turn PTC tracking",
        "symplectic_residual_frobenius": float(np.linalg.norm(matrix.T @ j @ matrix - j)),
    }


def normal_form(*_args, **_kwargs):
    raise not_exposed("Normal-form access")
