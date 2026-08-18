"""PyParticleBunch integration for PyPTC."""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path

import numpy as np


DEFAULT_PYPARTICLEBUNCH_SRC = Path("/home/hr/Codes/pyparticlebunch/src")


def pyparticlebunch_source() -> Path:
    return Path(os.environ.get("PYPARTICLEBUNCH_SRC", str(DEFAULT_PYPARTICLEBUNCH_SRC))).resolve()


def ensure_pyparticlebunch_path() -> Path:
    source = pyparticlebunch_source()
    if not source.exists():
        raise FileNotFoundError(f"PyParticleBunch source directory not found: {source}")
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))
    return source


def generate_matched_gaussian_4d(
    *,
    n: int,
    emittance_x: float,
    emittance_y: float,
    alpha_x: float,
    beta_x: float,
    alpha_y: float,
    beta_y: float,
    x_limit: float = 5.0,
    y_limit: float = 5.0,
    seed: int | None = None,
) -> np.ndarray:
    """Generate an N x 6 bunch array using the existing PyParticleBunch repo."""

    ensure_pyparticlebunch_path()
    from pyparticlebunch import ParticleBunch

    if seed is not None:
        np.random.seed(int(seed))
        random.seed(int(seed))

    bunch = ParticleBunch.MatchedGaussian_4D(
        n=int(n),
        emittance_x=float(emittance_x),
        emittance_y=float(emittance_y),
        alpha_x=float(alpha_x),
        beta_x=float(beta_x),
        alpha_y=float(alpha_y),
        beta_y=float(beta_y),
        x_limit=float(x_limit),
        y_limit=float(y_limit),
    )
    return bunch.to_numpy()
