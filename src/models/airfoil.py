"""
This module defines the Airfoil class, which encapsulates the aerodynamic
properties of the airfoil used in the Boeing 737 simulator. It includes
methods to extract airfoil properties from configuration files and perform
a least squares fit to determine the lift curve slope. The Airfoil class
is used by the Aircraft class to calculate lift and drag forces based on the
current state of the aircraft.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import yaml


class Airfoil:  # for lift and drag
    """Airfoil class to store aerodynamic properties of the airfoil,
    such as lift and drag coefficients, geometric properties, etc.

    Args:
        alpha0 (float): zero lift angle of attack in degrees
        cl_slope (float): lift curve slope (per degree)
        cd0 (float): zero lift drag coefficient
        k (float): induced drag factor
        stall_angle (float): angle of attack for stall in degrees
        oswald_efficiency (float): Oswald efficiency factor
        cm0 (float): pitching moment coefficient at zero lift
        chord_length (float): chord length of the wing in meters
        wing_area (float): wing area in square meters
        wing_span (float): wing span in meters
    """

    def __init__(
        self,
        alpha0: float = None,
        cl_slope: float = None,
        cd0: float = None,
        k: float = None,
        stall_angle: float = None,
        negative_stall_angle: float = None,
        oswald_efficiency: float = None,
        cm0: float = None,
        chord_length: float = None,
        wing_area: float = None,
        wing_span: float = None,
    ) -> None:
        self.alpha0 = alpha0
        self.cl_slope = cl_slope  # lift curve slope (per degree)
        self.cd0 = cd0
        self.k = k
        self.stall_angle = stall_angle
        self.negative_stall_angle = negative_stall_angle
        self.oswald_efficiency = oswald_efficiency
        self.cm0 = cm0
        self.chord_length = chord_length
        self.wing_area = wing_area
        self.wing_span = wing_span
        self.aspect_ratio = (
            wing_span**2 / wing_area if wing_area and wing_span else None
        )
        self.cma = None
        self.cmde = None
        self.cmq = None

    def extract_airfoil(
        self, PARENT_PATH: Path, airfoil_file: str, config_file: str
    ) -> None:
        """Extracts airfoil properties from the given files.

        Args:
            PARENT_PATH (Path): parent path to the data files
            airfoil_file (str): filename of the airfoil data (CSV)
            config_file (str): filename of the configuration data (YAML)

        Returns:
            None

        Raises:
            FileNotFoundError: If any of the specified files are not found.
            ValueError: If the data in the files is not in the expected format.
        """

        with open(PARENT_PATH / config_file, "r") as f:
            # ----------------------- GEOMETRIC PROPERTIES -----------------------
            config = yaml.safe_load(f)
            self.chord_length = float(
                config["B737"]["geometry"]["mean_aerodynamic_chord"]
            )
            self.wing_span = float(config["B737"]["geometry"]["wing_span"])
            self.wing_area = float(config["B737"]["geometry"]["wing_area"])
            self.aspect_ratio = self.wing_span**2 / self.wing_area

            # ------------------------ DRAG POLAR COEFFICIENTS ------------------------
            self.oswald_efficiency = float(config["B737"]["coefficients"]["e"])
            self.k = float(config["B737"]["coefficients"]["k"])
            self.cd0 = float(config["B737"]["coefficients"]["cd0"])

            # ---------------------- MOMENT COEFFICIENTS ----------------------
            self.cma = float(config["B737"]["moments"]["cma"])
            self.cmde = float(config["B737"]["moments"]["cmde"])
            self.cmq = float(config["B737"]["moments"]["cmq"])
            self.cm0 = float(config["B737"]["moments"]["cm0"])

        # ---------------------- LIFT COEFFICIENTS ----------------------

        df = pd.read_csv(PARENT_PATH / airfoil_file)
        df.columns = df.columns.str.strip()

        self.stall_angle = df.iloc[df["cl"].idxmax()][
            "alpha"
        ]  # angle of attack for stall
        self.negative_stall_angle = df.iloc[df["cl"].idxmin()]["alpha"]
        data_points = []
        linear_limit = 6
        for _, row in df.iterrows():
            if abs(row["alpha"]) < linear_limit:
                data_points.append((row["alpha"], row["cl"], row["cm"]))

        # performing least square fit to find cl_slope A.T@A@x = A.T@b
        A = np.array([[1, point[0]] for point in data_points])
        b = np.array([point[1] for point in data_points])
        c, cl_2d_slope = np.linalg.lstsq(A, b, rcond=None)[0]
        cl_2d_slope *= (
            180.0 / np.pi
        )  # converting to per radian (our slope is cl per degree)

        # applying finite wing correction to cl slope
        self.cl_slope = (
            cl_2d_slope
            / (1 + cl_2d_slope / (np.pi * self.aspect_ratio * self.oswald_efficiency))
            * np.pi
            / 180.0
        )  # converting back to per degree

        # alpha0 from our least square fit, where cl = 0 i.e alpha0 = -intercept/slope
        self.alpha0 = -c / self.cl_slope  # in degrees
