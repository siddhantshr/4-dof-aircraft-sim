from pathlib import Path

import pytest

from src.models.aircraft import Aircraft

DATA_PATH = Path(__file__).resolve().parents[1] / "src" / "data"


@pytest.fixture
def initialized_aircraft() -> Aircraft:
    aircraft = Aircraft([120.0, 0.0, 0.0, 0.0, 2000.0, 0.0])
    aircraft.initialize_config(
        DATA_PATH,
        "737-midspan-airfoil.csv",
        "configuration.yaml",
    )
    return aircraft


def test_airfoil_properties(initialized_aircraft: Aircraft) -> None:
    airfoil = initialized_aircraft.airfoil
    assert airfoil.alpha0 is not None
    assert airfoil.cl_slope > 0
    assert airfoil.cd0 > 0
    assert airfoil.k > 0
    assert airfoil.stall_angle > 0
    assert airfoil.negative_stall_angle < 0
    assert airfoil.oswald_efficiency > 0
    assert airfoil.cm0 is not None
    assert airfoil.chord_length > 0
    assert airfoil.wing_area > 0
    assert airfoil.wing_span > 0
    assert airfoil.aspect_ratio > 0
    assert airfoil.cma is not None
    assert airfoil.cmde is not None
    assert airfoil.cmq is not None
