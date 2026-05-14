from pathlib import Path
from typing import Callable

import numpy as np
import pytest  # type: ignore
from numpy.typing import NDArray

from src.exceptions.exceptions import (
    CriticalMachWarning,
    GroundContactError,
    StallError,
    SupersonicFlowError,
)
from src.models.aircraft import Aircraft, AircraftState, Controls

DATA_PATH = Path(__file__).resolve().parents[1] / "src" / "data"


@pytest.fixture  # type: ignore[untyped-decorator]
def initialized_aircraft() -> Aircraft:
    aircraft = Aircraft([120.0, 0.0, 0.0, 0.0, 2000.0, 0.0])
    aircraft.initialize_config(
        DATA_PATH,
        "737-midspan-airfoil.csv",
        "configuration.yaml",
    )
    return aircraft


def test_aircraft_state_creation() -> None:
    state = AircraftState(100.0, 5.0, 0.1, 0.2, 1000.0, 0.0)
    assert state.u == 100.0
    assert state.height == 1000.0


def test_controls_creation() -> None:
    controls = Controls(0.5, -5.0)
    assert controls.throttle == 0.5
    assert controls.elevator_deflection == -5.0


def test_aircraft_init_from_list() -> None:
    aircraft = Aircraft([100.0, 5.0, 0.1, 0.2, 1000.0, 0.0])
    assert aircraft.state.u == 100.0
    assert aircraft.state.height == 1000.0


def test_aircraft_init_from_state() -> None:
    state = AircraftState(100.0, 5.0, 0.1, 0.2, 1000.0, 0.0)
    aircraft = Aircraft(state)
    assert aircraft.state is state


def test_initialize_config_populates_aircraft_and_airfoil(
    initialized_aircraft: Aircraft,
) -> None:
    aircraft = initialized_aircraft
    assert aircraft.m is not None
    assert aircraft.thrust0 is not None
    assert aircraft.radius_of_gyration_yy is not None
    assert aircraft.L is not None
    assert aircraft.airfoil.wing_area is not None
    assert aircraft.m > 0
    assert aircraft.thrust0 > 0
    assert aircraft.radius_of_gyration_yy > 0
    assert aircraft.L > 0
    assert aircraft.airfoil.wing_area > 0
    assert aircraft.airfoil.cl_slope is not None
    assert aircraft.airfoil.stall_angle is not None


def test_iyy_calculation() -> None:
    aircraft = Aircraft([100.0, 5.0, 0.1, 0.2, 1000.0, 0.0])
    aircraft.m = 50000.0
    aircraft.radius_of_gyration_yy = 0.3
    aircraft.L = 10.0
    expected_iyy = 50000.0 * (0.3 * 10.0) ** 2
    assert aircraft.iyy == expected_iyy


def test_maximum_thrust_scales_with_density(initialized_aircraft: Aircraft) -> None:
    sea_level = initialized_aircraft.maximum_thrust_available(0.0)
    high_altitude = initialized_aircraft.maximum_thrust_available(10000.0)
    assert sea_level == pytest.approx(initialized_aircraft.thrust0, rel=0.001)
    assert high_altitude < sea_level


def test_maximum_thrust_negative_height_raises(initialized_aircraft: Aircraft) -> None:
    with pytest.raises(ValueError, match="Height cannot be negative"):
        initialized_aircraft.maximum_thrust_available(-1.0)


def test_derivatives_nominal_case_returns_six_finite_values(
    initialized_aircraft: Aircraft,
) -> None:
    state = [130.0, 3.0, 0.01, 0.02, 1800.0, 100.0]
    derivs = initialized_aircraft.derivatives(0.0, np.array(state))
    assert len(derivs) == 6
    assert np.all(np.isfinite(derivs))


def test_derivatives_ground_contact_raises(initialized_aircraft: Aircraft) -> None:
    with pytest.raises(GroundContactError):
        initialized_aircraft.derivatives(
            0.0, np.array([100.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        )


def test_derivatives_stall_raises(initialized_aircraft: Aircraft) -> None:
    with pytest.raises(StallError):
        initialized_aircraft.derivatives(
            0.0, np.array([10.0, 30.0, 0.0, 0.0, 2000.0, 0.0])
        )


def test_derivatives_supersonic_raises(initialized_aircraft: Aircraft) -> None:
    with pytest.raises(SupersonicFlowError):
        initialized_aircraft.derivatives(
            0.0, np.array([400.0, 0.0, 0.0, 0.0, 2000.0, 0.0])
        )


def test_derivatives_warns_on_critical_mach(initialized_aircraft: Aircraft) -> None:
    with pytest.warns(CriticalMachWarning):
        initialized_aircraft.derivatives(
            0.0, np.array([245.0, 0.0, 0.0, 0.0, 2000.0, 0.0])
        )


def test_update_state_updates_state_from_integrator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    aircraft = Aircraft([100.0, 0.0, 0.0, 0.0, 1000.0, 0.0])

    class DummySolution:  # mocking
        def __init__(self) -> None:
            self.y = np.array(
                [[101.0], [1.0], [0.02], [0.03], [1005.0], [20.0]],
                dtype=float,
            )

    def fake_solve_ivp(
        fun: Callable[[float, NDArray[np.float64]], NDArray[np.float64]],
        t_span: tuple[float, float],
        y0: NDArray[np.float64],
        method: str,
        t_eval: list[float],
    ) -> DummySolution:
        assert callable(fun)
        assert t_span == (0, 0.5)
        np.testing.assert_array_equal(y0, [100.0, 0.0, 0.0, 0.0, 1000.0, 0.0])
        assert method == "RK45"
        assert t_eval == [0.5]
        return DummySolution()

    monkeypatch.setattr("src.models.aircraft.solve_ivp", fake_solve_ivp)

    aircraft.update_state(0.5)

    assert aircraft.state == AircraftState(
        u=101.0,
        w=1.0,
        q=0.02,
        theta=0.03,
        height=1005.0,
        x=20.0,
    )
