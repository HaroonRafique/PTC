import numpy as np
import pytest

from pyptc.optics import one_turn_map


class LinearMapPTC:
    def __init__(self, matrix):
        self.matrix = matrix

    def node_twiss_orbit(self, _index):
        return {"orbitx": 1e-3, "orbitpx": 2e-4, "orbity": -3e-4, "orbitpy": 1e-4}

    def track_particle_ptc_with_loss(self, coordinates, turns=1):
        assert turns == 1
        values = np.asarray(coordinates, dtype=float).copy()
        values[:4] = self.matrix @ values[:4]
        return values, {"lost": False}


def test_one_turn_map_recovers_coupled_linear_matrix():
    matrix = np.array([[1.0, 0.2, 0.1, 0.0], [0, 1, 0, 0.05],
                       [0.0, 0.0, 1.0, 0.3], [0.02, 0.0, 0.0, 1.0]])
    result = one_turn_map(LinearMapPTC(matrix), step=1e-6)
    np.testing.assert_allclose(result["matrix"], matrix, atol=1e-10)
    assert result["coordinate_order"] == ["x", "px", "y", "py"]
    assert result["method"].startswith("centered finite-difference")


@pytest.mark.parametrize("step", [0.0, -1.0, float("nan")])
def test_one_turn_map_rejects_invalid_step(step):
    with pytest.raises(ValueError, match="step"):
        one_turn_map(LinearMapPTC(np.eye(4)), step=step)
