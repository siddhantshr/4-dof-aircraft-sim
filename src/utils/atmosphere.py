"""
This module contains the Atmosphere class to calculate atmospheric
properties using the International Standard Atmosphere (ISA) model
"""

import numpy as np


class Atmosphere:
    """Atmosphere class to calculate atmospheric
    properties such as pressure and density based on ISA"""

    def __init__(self) -> None:
        self.rho0: float = 1.225
        self.p0: float = 101325
        self.T0: float = 288.15
        self.L: float = -0.0065
        self.R: float = 287.05
        self.g: float = 9.81

    def pressure(self, height: float) -> float:
        """Calculates the atmospheric pressure at a given
        height using the International Standard Atmosphere (ISA) model."""
        if height < 0:
            raise ValueError("Height cannot be negative")
        if height > 20000:
            raise ValueError("Pressure calculation only valid up to 20,000 m")

        if height < 11000:  # troposphere
            return float(
                self.p0
                * (1 + self.L * height / self.T0) ** (-self.g / (self.R * self.L))
            )
        P11K = float(
            self.p0 * (1 + self.L * 11000 / self.T0) ** (-self.g / (self.R * self.L))
        )
        T11K = float(self.T0 + self.L * 11000)

        return float(P11K * np.exp(-self.g * (height - 11000) / (self.R * T11K)))

    def rho(self, height: float) -> float:
        """Calculates the atmospheric density at a given
        height using the International Standard Atmosphere (ISA) model."""
        if height < 0:
            raise ValueError("Height cannot be negative")
        if height > 20000:
            raise ValueError("Density calculation only valid up to 20,000 m")

        if height < 11000:  # troposphere
            return float(self.pressure(height) / (self.R * (self.T0 + self.L * height)))
        return float(self.pressure(height) / (self.R * (self.T0 + self.L * 11000)))
