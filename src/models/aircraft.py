"""
This module defines the Aircraft class, which represents the state
and dynamics of a Boeing 737. The Aircraft class includes
methods to initialize the aircraft configuration, calculate
the maximum thrust available at a given altitude, compute the
derivatives of the state variables based on the current state
and control inputs, and update the state using numerical integration.
The Aircraft class interacts with the Airfoil class to determine
aerodynamic forces and with the Atmosphere class to calculate
atmospheric properties.
"""

from dataclasses import dataclass
from pathlib import Path
from warnings import warn

import numpy as np
from scipy.integrate import solve_ivp
from yaml import safe_load

from src.exceptions.exceptions import (
    CriticalMachWarning,
    GroundContactError,
    StallError,
    SupersonicFlowError,
)
from src.models.airfoil import Airfoil
from src.utils.atmosphere import Atmosphere


@dataclass
class AircraftState:
    """Dataclass to represent the state of the aircraft."""

    u: float  # Body X-velocity (m/s)
    w: float  # Body Z-velocity (m/s)
    q: float  # Pitch rate (rad/s)
    theta: float  # Pitch angle (rad)
    height: float  # Altitude (m)
    x: float  # X-position (m)


@dataclass
class Controls:
    """Dataclass to represent the control inputs for the aircraft."""

    throttle: float  # Throttle setting (0 to 1)
    elevator_deflection: float  # Elevator deflection in degrees


class Aircraft:
    """Aircraft class to represent the state and dynamics of the Boeing 737.

    Args:
        initial_state (list): Initial state of the aircraft [u, w, q, theta, height, x]
    """

    def __init__(self, initial_state: list | AircraftState) -> None:
        self.oew = None
        self.payload = None
        self.fuel_mass = None
        self.m = None
        self.thrust0 = None
        # accept either an AircraftState or a list/tuple of values
        if isinstance(initial_state, AircraftState):
            self.state = initial_state
        else:
            self.state = AircraftState(
                u=initial_state[0],
                w=initial_state[1],
                q=initial_state[2],
                theta=initial_state[3],
                height=initial_state[4],
                x=initial_state[5],
            )
        self.airfoil = Airfoil()
        self.atmosphere = Atmosphere()

        self.radius_of_gyration_yy = None
        # Estimated radius of gyration in the y-axis as a fraction of the length
        self.L = None  # Length of the aircraft in meters

        # Controls held in a dataclass
        self.controls = Controls(throttle=1.0, elevator_deflection=0.0)

        self.mcrit = None
        self.curve_exponent = None
        self.drag_severity_multiplier = None

    def initialize_config(
        self, PARENT_PATH: Path, airfoil_file: str, config_file: str
    ) -> None:
        """Initializes the airfoil properties by extracting data from the given files.

        Args:
            PARENT_PATH (Path): The parent path to the data files.
            airfoil_file (str): The filename of the airfoil data (CSV).
            config_file (str): The filename of the configuration data (YAML).

        Returns:
            None

        Raises:
            FileNotFoundError: If any of the specified files are not found.
            ValueError: If the data in the files is not in the expected format.
        """
        with open(PARENT_PATH / config_file, "r") as file:
            config = safe_load(file)
            self.oew = float(config["B737"]["mass"]["oew"])
            self.payload = float(config["B737"]["mass"]["payload"])
            self.fuel_mass = float(config["B737"]["mass"]["fuel_mass"])
            self.m = self.oew + self.payload + self.fuel_mass
            self.thrust0 = float(config["B737"]["thrust"]["thrust0"])
            self.radius_of_gyration_yy = float(
                config["B737"]["geometry"]["radius_of_gyration_yy"]
            )
            self.L = float(config["B737"]["geometry"]["length"])
            self.drag_severity_multiplier = float(
                config["B737"]["wave_drag"]["severity_multiplier"]
            )
            self.mcrit = float(config["B737"]["wave_drag"]["mcrit"])
            self.curve_exponent = float(config["B737"]["wave_drag"]["curve_exponent"])
        self.airfoil.extract_airfoil(PARENT_PATH, airfoil_file, config_file)

    @property
    def iyy(self) -> float:
        """Calculates the moment of inertia about the y-axis (pitch axis).

        Returns:
            float: Moment of inertia about the y-axis (kg·m²)
        """
        # iyy = iyy(dry) + iyy(fuel) + iyy(payload) i.e. iyy(dry) + int dm r^2
        # lets estimate simply using Roskam's estimation
        return self.m * (self.radius_of_gyration_yy * self.L) ** 2

    def print_state(self) -> None:
        """Prints the current state of the aircraft as a neat colored table."""
        v = np.sqrt(self.state.u**2 + self.state.w**2)
        alpha = np.arctan2(self.state.w, self.state.u)
        mach = v / np.sqrt(
            1.4
            * self.atmosphere.R
            * (self.atmosphere.T0 + self.atmosphere.L * self.state.height)
        )

        # ANSI color codes
        HEADER = "\033[95m"
        BLUE = "\033[94m"
        CYAN = "\033[96m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

        print(f"\n{HEADER}{BOLD}{'='*70}{RESET}")
        print(f"{HEADER}{BOLD}{'AIRCRAFT STATE':^70}{RESET}")
        print(f"{HEADER}{BOLD}{'='*70}{RESET}\n")

        state_vars = [
            ("Body X-velocity (u)", f"{self.state.u:.2f}", "m/s", CYAN),
            ("Body Z-velocity (w)", f"{self.state.w:.2f}", "m/s", CYAN),
            ("Pitch rate (q)", f"{self.state.q:.4f}", "rad/s", BLUE),
            ("Pitch angle (θ)", f"{np.degrees(self.state.theta):.2f}", "°", BLUE),
            ("Height", f"{self.state.height:.2f}", "m", GREEN),
            ("X-position", f"{self.state.x:.2f}", "m", GREEN),
        ]

        derived_vars = [
            ("True Airspeed (V)", f"{v:.2f}", "m/s", YELLOW),
            ("Angle of Attack (α)", f"{np.degrees(alpha):.2f}", "°", YELLOW),
            ("Mach Number", f"{mach:.4f}", "-", RED if mach > 0.7 else YELLOW),
        ]

        print(f"{BOLD}Primary State Variables:{RESET}")
        for name, value, unit, color in state_vars:
            print(f"  {color}{name:.<35} {value:>10} {unit}{RESET}")

        print(f"\n{BOLD}Derived Variables:{RESET}")
        for name, value, unit, color in derived_vars:
            print(f"  {color}{name:.<35} {value:>10} {unit}{RESET}")

        print(f"\n{HEADER}{BOLD}{'='*70}{RESET}\n")

    def maximum_thrust_available(self, height: float) -> float:
        """Calculates the maximum thrust available at a given height.

        Args:
            height (float): Altitude in meters.

        Returns:
            float: Maximum thrust available at the given height.

        Raises:
            ValueError: If the height is negative.
        """
        if height < 0:
            raise ValueError("Height cannot be negative.")
        return self.thrust0 * self.atmosphere.rho(height) / self.atmosphere.rho0

    def derivatives(self, t: float, state: list) -> list:
        """Calculates the derivatives of the aircraft state variables.

        Args:
            t (float): Time.
            state (list): Current state of the aircraft [u, w, q, theta, height, x].

        Returns:
            list: Derivatives of the state variables respectively.

        Raises:
            StallError: If the angle of attack exceeds the stall angle.
            SupersonicFlowError: If the Mach number exceeds 1.0.
        """
        u, w, q, theta, height, x = state

        if height <= 0:
            raise GroundContactError(height)

        qbar = 0.5 * self.atmosphere.rho(height) * (u**2 + w**2)
        alpha = np.arctan2(w, u)  # Angle of attack in radians
        if (
            np.degrees(alpha) > self.airfoil.stall_angle
            or np.degrees(alpha) < self.airfoil.negative_stall_angle
        ):
            raise StallError(np.degrees(alpha), self.airfoil.stall_angle)
        v = np.sqrt(u**2 + w**2)  # True airspeed
        mach = v / np.sqrt(
            1.4 * self.atmosphere.R * (self.atmosphere.T0 + self.atmosphere.L * height)
        )
        if mach >= 1.0:
            raise SupersonicFlowError(mach)
        beta = np.sqrt(1 - mach**2)

        cL = self.airfoil.cl_slope * (
            np.degrees(alpha) - self.airfoil.alpha0
        )  # cl_slope is in per degree
        if mach > 0.3:
            cL /= beta
        cD = (
            self.airfoil.cd0 if mach < 0.3 else self.airfoil.cd0 / beta**2
        ) + self.airfoil.k * (cL**2)
        # use controls dataclass for control inputs
        cM = (
            self.airfoil.cm0
            + self.airfoil.cma * alpha
            + self.airfoil.cmde * np.radians(self.controls.elevator_deflection)
            + self.airfoil.cmq * (q * self.airfoil.chord_length / (2 * max(v, 1e-6)))
        )

        if mach > 0.7:
            warn(CriticalMachWarning(mach))
            # delta_cd = k(M-Mcrit)^m
            cD += (
                self.drag_severity_multiplier
                * (mach - self.mcrit) ** self.curve_exponent
            )

        T = self.controls.throttle * self.maximum_thrust_available(height)
        L = qbar * self.airfoil.wing_area * cL
        D = qbar * self.airfoil.wing_area * cD
        M = qbar * self.airfoil.wing_area * self.airfoil.chord_length * cM

        u_dot = (
            (T - D * np.cos(alpha) + L * np.sin(alpha)) / self.m
            - self.atmosphere.g * np.sin(theta)
            - q * w
        )
        w_dot = (
            (0 - D * np.sin(alpha) - L * np.cos(alpha)) / self.m
            + self.atmosphere.g * np.cos(theta)
            + q * u
        )
        q_dot = M / self.iyy
        theta_dot = q
        height_dot = u * np.sin(theta) - w * np.cos(theta)
        x_dot = u * np.cos(theta) + w * np.sin(theta)

        return [u_dot, w_dot, q_dot, theta_dot, height_dot, x_dot]

    def update_state(self, delta_t: float) -> None:
        """Updates the current aircraft state.

        Args:
            dt (float): Time step for the update.

        Returns:
            None

        Raises:
            ValueError: If delta_t is not positive.
        """
        y0 = [
            self.state.u,
            self.state.w,
            self.state.q,
            self.state.theta,
            self.state.height,
            self.state.x,
        ]
        sol = solve_ivp(
            self.derivatives,
            t_span=(0, delta_t),
            y0=y0,
            method="RK45",
            t_eval=[delta_t],
        )
        u, w, q, theta, height, x = sol.y[:, -1]
        self.state = AircraftState(u=u, w=w, q=q, theta=theta, height=height, x=x)
