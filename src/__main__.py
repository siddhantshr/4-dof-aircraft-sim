from src.models.aircraft import Aircraft
from pathlib import Path

PARENT_PATH = Path(__file__).resolve().parent

"""
we are keeping everthing in SI units, we are not using lbs, ft, knots, etc.

1 ft = 1/3.281 m
1 lb = 0.453592 kg
1 knot = 0.514444 m/s

We are only going to see low speed aerodynamics, so we are not going to worry about
compressibility, shock waves etc. M < 0.3 i.e. Vtas < 0.3*sqrt(gamma*R*T)
"""

LENGTH_CONVERSION = 1/3.281
MASS_CONVERSION = 0.453592
VELOCITY_CONVERSION = 0.514444

def main():
    # we are keeping everthing in SI units, we are not using lbs, ft, knots, etc. 
    # mass = [oew, payload, fuel_mass]
    # initial_state = [height, tas, pitch_angle, pitch_rate]
    b737 = Aircraft(
        mass=[41412, 16000, 10000],
        thrust=120000,
        initial_state=[10_000*LENGTH_CONVERSION, 70, 0.1, 0],
    )
    b737.initialize_airfoil(PARENT_PATH, "data/737-midspan-airfoil.csv", "data/geometries.json", "data/drag-polar.csv")

    # for attribute, value in b737.__dict__.items():
    #     print(f"{attribute}: {value}")

    # for attribute, value in b737.airfoil.__dict__.items():
    #     print(f"{attribute}: {value}")

    # for attribute, value in b737.atmosphere.__dict__.items():
    #     print(f"{attribute}: {value}")



if __name__ == "__main__":
    main()
