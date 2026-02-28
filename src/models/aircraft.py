from src.utils.atmosphere import Atmosphere
from src.models.airfoil import Airfoil

class Aircraft:
    def __init__(self, mass, thrust, initial_state) -> None:
        self.oew = mass[0]
        self.payload = mass[1]
        self.fuel_mass = mass[2]
        self.m = self.oew + self.payload + self.fuel_mass
        self.thrust = thrust
        self.height = initial_state[0]
        self.tas = initial_state[1]
        self.pitch_angle = initial_state[2]
        self.pitch_rate = initial_state[3]
        self.airfoil = Airfoil()
        self.atmosphere = Atmosphere()

    # def warn(self, message):
    #     print(f"\033[91m{message}\033[0m")

    # def check_low_speed_aerodynamics(self):
    #     mach = self.tas * np.sqrt(1.4 * self.atmosphere.R * (self.atmosphere.T0 + self.atmosphere.L * self.height))
    #     if mach > 0.3:
    #         self.warn(f"High Mach number detected: {mach}")

    def initialize_airfoil(self, PARENT_PATH, airfoil_file, geometry_file, drag_polar_file) -> None:
        self.airfoil.extract_airfoil(PARENT_PATH, airfoil_file, geometry_file, drag_polar_file)

    def state(self) -> list:
        return [self.height, self.tas, self.pitch_angle, self.pitch_rate]
    
