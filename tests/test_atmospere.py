from pathlib import Path

import pytest

from src.utils.atmosphere import Atmosphere

DATA_PATH = Path(__file__).resolve().parents[1] / "src" / "data"


@pytest.fixture
def init_atmosphere() -> Atmosphere:
    return Atmosphere()


def test_constants(init_atmosphere: Atmosphere) -> None:
    assert init_atmosphere.rho0 == pytest.approx(1.225)
    assert init_atmosphere.p0 == pytest.approx(101325)
    assert init_atmosphere.T0 == pytest.approx(288.15)
    assert init_atmosphere.L == pytest.approx(-0.0065)
    assert init_atmosphere.R == pytest.approx(287.05)
    assert init_atmosphere.g == pytest.approx(9.81)


def test_pressure_at_sea_level(init_atmosphere: Atmosphere) -> None:
    pressure = init_atmosphere.pressure(0)
    assert pressure == pytest.approx(101325, abs=1)


def test_pressure_at_5000m(init_atmosphere: Atmosphere) -> None:
    pressure = init_atmosphere.pressure(5000)
    assert pressure == pytest.approx(54010, rel=0.01)


def test_density_at_sea_level(init_atmosphere: Atmosphere) -> None:
    density = init_atmosphere.rho(0)
    assert density == pytest.approx(1.225, abs=0.01)


def test_density_at_5000m(init_atmosphere: Atmosphere) -> None:
    density = init_atmosphere.rho(5000)
    assert density == pytest.approx(0.736, abs=0.01)


def test_density_at_15000m(init_atmosphere: Atmosphere) -> None:
    density = init_atmosphere.rho(15000)
    assert density == pytest.approx(0.193, abs=0.01)


def test_pressure_at_15000m(init_atmosphere: Atmosphere) -> None:
    pressure = init_atmosphere.pressure(15000)
    assert pressure == pytest.approx(12040, rel=0.01)


def test_pressure_at_20000m(init_atmosphere: Atmosphere) -> None:
    pressure = init_atmosphere.pressure(20000)
    assert pressure == pytest.approx(5474, rel=0.01)


def test_density_at_20000m(init_atmosphere: Atmosphere) -> None:
    density = init_atmosphere.rho(20000)
    assert density == pytest.approx(0.0889, abs=0.01)


def test_pressure_and_density_decrease_with_height(init_atmosphere: Atmosphere) -> None:
    pressure_0 = init_atmosphere.pressure(0)
    pressure_5000 = init_atmosphere.pressure(5000)
    density_0 = init_atmosphere.rho(0)
    density_5000 = init_atmosphere.rho(5000)

    assert pressure_5000 < pressure_0
    assert density_5000 < density_0


def test_negative_height_raises_error(init_atmosphere: Atmosphere) -> None:
    with pytest.raises(ValueError, match="Height cannot be negative"):
        init_atmosphere.rho(-100)
    with pytest.raises(ValueError, match="Height cannot be negative"):
        init_atmosphere.pressure(-100)


def test_height_above_20000m_raises_error(init_atmosphere: Atmosphere) -> None:
    with pytest.raises(
        ValueError, match="Density calculation only valid up to 20,000 m"
    ):
        init_atmosphere.rho(25000)
    with pytest.raises(
        ValueError, match="Pressure calculation only valid up to 20,000 m"
    ):
        init_atmosphere.pressure(25000)


def test_ideal_gas_law_consistency(init_atmosphere: Atmosphere) -> None:
    height = 15000
    pressure = init_atmosphere.pressure(height)
    density = init_atmosphere.rho(height)
    temperature = (
        init_atmosphere.T0 + init_atmosphere.L * 11000
    )  # temperature at 11,000 m

    expected = pressure / (init_atmosphere.R * temperature)

    assert density == pytest.approx(expected, abs=0.01)


def test_continuity_at_11000m(init_atmosphere: Atmosphere) -> None:
    pressure_below = init_atmosphere.pressure(10999)
    pressure_above = init_atmosphere.pressure(11001)
    density_below = init_atmosphere.rho(10999)
    density_above = init_atmosphere.rho(11001)

    assert pressure_below == pytest.approx(pressure_above, abs=10)
    assert density_below == pytest.approx(density_above, abs=0.01)
