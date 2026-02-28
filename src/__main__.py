import json
from pathlib import Path

import numpy as np

# import matplotlib.pyplot as plt
# from scipy.integrate import solve_ivp
import pandas as pd

PARENT_PATH = Path(__file__).resolve().parent.parent


class Airfoil:  # for lift and drag
    def __init__(
        self,
        alpha0=None,
        cl_slope=None,
        cd0=None,
        k=None,
        stall_angle=None,
        oswald_efficiency=None,
        cm0=None,
        chord_length=None,
        wing_area=None,
        wing_span=None,
    ) -> None:
        self.alpha0 = alpha0
        self.cl_slope = cl_slope
        self.cd0 = cd0
        self.k = k
        self.stall_angle = stall_angle
        self.oswald_efficiency = oswald_efficiency
        self.cm0 = cm0
        self.chord_length = chord_length
        self.wing_area = wing_area
        self.wing_span = wing_span
        self.aspect_ratio = (
            wing_span**2 / wing_area if wing_area and wing_span else None
        )

    def extract_airfoil(self) -> None:
        # ----------------------- GEOMETRIC PROPERTIES -----------------------

        with open(PARENT_PATH / "data" / "geometries.json", "r") as f:
            geometries = json.load(f)
            self.chord_length = geometries["c"]
            self.wing_span = geometries["b"]
            self.wing_area = geometries["S"]
            self.aspect_ratio = self.wing_span**2 / self.wing_area

        # ------------------------ DRAG POLAR COEFFICIENTS ------------------------

        df = pd.read_csv(PARENT_PATH / "data" / "drag-polar.csv")
        df.columns = df.columns.str.strip()

        row = df[df["Aircraft"] == "B737"].iloc[0]
        self.cd0 = row["CD0_clean"]
        self.k = row["k"]
        self.oswald_efficiency = row["e"]

        # ---------------------- LIFT COEFFICIENTS ----------------------

        df = pd.read_csv(PARENT_PATH / "data" / "737-midspan-airfoil.csv")
        df.columns = df.columns.str.strip()

        self.stall_angle = df.iloc[df["cl"].idxmax()][
            "alpha"
        ]  # angle of attack for stall
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
        self.alpha0 = -c / self.cl_slope

        # ----------------------- PITCHING MOMENT COEFFICIENTS -----------------------

        self.cm0 = sum([x[2] for x in data_points]) / len(
            data_points
        )  # average of cm values in linear region


class Aircraft:
    def __init__(self, mass, area, cd, thrust, airfoil, initial_state) -> None:
        self.mass = mass
        self.area = area
        self.cd = cd
        self.thrust = thrust
        self.airfoil = airfoil
        self.height = initial_state[0]
        self.velocity = initial_state[1]
        self.pitch_angle = initial_state[2]
        self.pitch_rate = initial_state[3]

    def state(self) -> list:
        return [self.height, self.velocity, self.pitch_angle, self.pitch_rate]


if __name__ == "__main__":
    airfoil = Airfoil()
    airfoil.extract_airfoil()

    # print all the properties of the airfoil
    print("Airfoil Properties:")
    for attr, value in vars(airfoil).items():
        print(f"  {attr}: {value}")
