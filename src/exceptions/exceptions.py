class StructureDeformationError(Exception):
    """Raised when structural deformation exceeds allowable limits."""

    def __init__(
        self, deformation: float, allowable: float, component: str = "structure"
    ) -> None:

        self.deformation = deformation
        self.allowable = allowable
        self.component = component

        super().__init__(
            f"{component} deformation exceeded allowable limit: "
            f"{deformation:.6f} > {allowable:.6f}"
        )


class SupersonicFlowError(Exception):
    """Raised when the flow exceeds the supersonic limit (M > 1.0)."""

    def __init__(self, mach: float) -> None:
        self.mach = mach
        super().__init__(
            f"Supersonic flow detected: Mach {mach:.2f} exceeds the limit of 1.0"
        )


class CriticalMachWarning(Warning):
    """Warning raised when the Mach number approaches the critical Mach number."""

    def __init__(self, mach: float) -> None:
        self.mach = mach
        super().__init__(
            f"Critical Mach number approaching: Mach {mach:.2f} exceeds 0.7"
        )


class StallError(Exception):
    """Raised when the angle of attack exceeds the stall angle."""

    def __init__(self, alpha: float, stall_angle: float) -> None:
        self.alpha = alpha
        self.stall_angle = stall_angle
        super().__init__(
            "Stall condition detected: Angle of attack "
            f"{alpha:.2f}° exceeds stall angle {stall_angle:.2f}°"
        )


class GroundContactError(Exception):
    """Raised when the aircraft makes contact with the ground."""

    def __init__(self, height: float) -> None:
        self.height = height
        super().__init__(
            "Ground contact detected: Aircraft altitude "
            f"{height:.2f} m is at or below ground level."
        )
