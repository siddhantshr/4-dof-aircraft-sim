"""
Main entry point for the Boeing 737 Simulator,
handles initilization, main loop, and rendering of the PFD.
"""

import sys
from pathlib import Path

import pygame  # type: ignore

from src.exceptions.exceptions import (
    GroundContactError,
    StallError,
    StructureDeformationError,
    SupersonicFlowError,
)
from src.models.aircraft import Aircraft
from src.utils.pfd import (
    AI_H,
    AI_Y,
    BG,
    CYAN,
    FPS,
    PHYSICS_DT,
    RED,
    SPD_X,
    H,
    S,
    W,
    apply_user_input,
    draw_ai,
    draw_alt_tape,
    draw_annunciations,
    draw_hdg_tape,
    draw_speed_tape,
    draw_vs_tape,
    font,
    txt,
    update_state_from_aircraft,
)

PARENT_PATH = Path(__file__).resolve().parent


def main() -> None:
    """Main function to run the Boeing 737 Simulator, initializing the Pygame
    environment, creating the Aircraft instance, and entering the main simulation loop.
    """
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Boeing 737 PFD  –  4-DOF Dynamic")
    clock = pygame.time.Clock()

    b737 = Aircraft(initial_state=[70, 0, 0, 0.1, 1000, 0])
    b737.initialize_config(
        PARENT_PATH, "data/737-midspan-airfoil.csv", "data/configuration.yaml"
    )

    physics_accumulator = 0.0
    status_message = ""

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        frame_dt = min(clock.tick(FPS) / 1000.0, 0.05)
        physics_accumulator += frame_dt

        apply_user_input(b737, frame_dt)

        try:
            while physics_accumulator >= PHYSICS_DT:
                b737.update_state(PHYSICS_DT)
                physics_accumulator -= PHYSICS_DT
                if b737.state.height <= 0:
                    raise GroundContactError(b737.state.height)
            status_message = ""
        except (
            StallError,
            SupersonicFlowError,
            GroundContactError,
            StructureDeformationError,
        ) as exc:
            status_message = str(exc)
            physics_accumulator = 0.0

        update_state_from_aircraft(b737)

        screen.fill(BG)
        draw_ai(screen, S["pitch_deg"])
        draw_speed_tape(screen, S["tas_kt"])
        draw_alt_tape(screen, S["altitude_ft"])
        draw_vs_tape(screen, S["vs_fpm"])
        draw_hdg_tape(screen, S["hdg_mag"])
        draw_annunciations(screen)

        f_status = font(18, bold=True)
        txt(
            screen,
            f"THR {S.get('throttle', 0.0):.2f}",
            (SPD_X, AI_Y + AI_H + 70),
            f_status,
            CYAN,
        )
        txt(
            screen,
            f"ELEV {S.get('elevator_deg', 0.0):+.1f} deg",
            (SPD_X, AI_Y + AI_H + 92),
            f_status,
            CYAN,
        )
        txt(
            screen,
            f"MACH {S.get('mach', 0.0):.2f}",
            (SPD_X, AI_Y + AI_H + 114),
            f_status,
            CYAN,
        )
        txt(
            screen,
            f"AOA {S.get('aoa', 0.0):+.1f} deg",
            (SPD_X, AI_Y + AI_H + 136),
            f_status,
            CYAN,
        )

        if status_message:
            txt(
                screen,
                status_message,
                (W // 2, H - 30),
                font(18, bold=True),
                RED,
                anchor="midtop",
            )

        pygame.display.flip()


if __name__ == "__main__":
    main()
