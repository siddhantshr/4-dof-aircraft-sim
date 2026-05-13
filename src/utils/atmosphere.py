"""
This module contains the Atmosphere class to calculate atmospheric
properties using the International Standard Atmosphere (ISA) model
"""

import numpy as np


class Atmosphere:
    """Atmosphere class to calculate atmospheric
    properties such as pressure and density based on ISA"""

    def __init__(self):
        self.rho0 = 1.225
        self.p0 = 101325
        self.T0 = 288.15
        self.L = -0.0065
        self.R = 287.05
        self.g = 9.81

    def pressure(self, height):
        """Calculates the atmospheric pressure at a given
        height using the International Standard Atmosphere (ISA) model."""
        if height < 11000:  # troposphere
            return self.p0 * (1 + self.L * height / self.T0) ** (
                -self.g / (self.R * self.L)
            )
        else:  # stratosphere
            P11K = self.p0 * (1 + self.L * 11000 / self.T0) ** (
                -self.g / (self.R * self.L)
            )
            T11K = self.T0 + self.L * 11000

            return P11K * np.exp(-self.g * (height - 11000) / (self.R * T11K))

    def rho(self, height):
        """Calculates the atmospheric density at a given
        height using the International Standard Atmosphere (ISA) model."""
        return self.pressure(height) / (self.R * (self.T0 + self.L * height))
