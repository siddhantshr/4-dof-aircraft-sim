"""
This module contains functions for drawing the Primary Flight Display (PFD)
elements on the screen, such as the attitude indicator, speed tape,
altitude tape, vertical speed tape, and heading tape. It also includes a
function to apply user input to the aircraft controls and a function
to update the display state based on the current aircraft state.

tas, gs displayed in knots; alt in feet; vs in fpm; hdg in degrees; baro in inches Hg
"""

import math

import pygame  # type: ignore
from typing import Any

from src.models.aircraft import Aircraft

# CONSTANTS
W, H = 840, 720
FPS = 60
PHYSICS_DT = 0.02

THROTTLE_RATE = 0.35
ELEVATOR_RATE = 25.0
MAX_ELEVATOR_DEFLECTION = 20.0

KTS_PER_MPS = 1.94384
FT_PER_M = 3.28084
FPM_PER_MPS = 196.8504

BLACK = (0, 0, 0)
BG = (22, 22, 26)
SKY = (28, 140, 210)
GROUND = (115, 65, 15)
WHITE = (255, 255, 255)
MAGENTA = (255, 0, 255)
GREEN = (0, 210, 0)
CYAN = (0, 210, 210)
YELLOW = (255, 215, 0)
AMBER = (255, 160, 0)
TAPE_BG = (18, 18, 20)
TAPE_BDR = (70, 70, 75)
DARK = (40, 40, 45)
RED = (200, 30, 30)
LGRAY = (160, 160, 165)

S = dict(
    pitch_deg=2.5,
    altitude_ft=1400,
    tas_kt=175,
    gs_kt=181,
    vs_fpm=-820,
    hdg_mag=320,
    baro_in=29.92,
    vref_kt=152,
    flap=30,
    sel_spd=175,
    sel_alt=3000,
    cmd=False,
    mach=0.0,
)

AI_X, AI_Y = 205, 90  # top-left of AI window
AI_W, AI_H = 370, 370
AI_CX = AI_X + AI_W // 2
AI_CY = AI_Y + AI_H // 2
PX_DEG = 27  # pixels per pitch degree

SPD_X, SPD_W = 35, 110  # speed tape  (left)
ALT_X, ALT_W = 580, 115  # altitude tape (right)
VS_X, VS_W = 700, 55  # VS tape (far right)
TAPE_Y = AI_Y
TAPE_H = AI_H


def font(size: int, bold: bool = False) -> Any:
    """Helper function to create a pygame font object.

    Args:
        size (int): Font size in points.
        bold (bool): Whether the font should be bold. Default is False.

    Returns:
        pygame.font.Font: A pygame Font object with the specified size and weight.

    Raises:
        pygame.error: If the font cannot be loaded.
    """
    return pygame.font.SysFont("monospace", size, bold=bold)


def txt(
    surf: Any,
    text: str,
    pos: tuple[float, float],
    fnt: Any,
    colour: tuple[int, int, int],
    anchor: str = "topleft",
) -> None:
    """Helper function to render text on a pygame surface with specified font and color.

    Args:
        surf (pygame.Surface): The surface to render the text on.
        text (str): The text to render.
        pos (tuple[float, float]): The position to place the text, as
        (x, y) coordinates.
        fnt (pygame.font.Font): The font object to use for rendering the text.
        colour (tuple[int, int, int]): The color of the text, as an RGB tuple.
        anchor (str): The anchor point for positioning the text.
                      Options include 'topleft', 'topright', 'midtop', 'center',
                      etc. Default is 'topleft'.

    Returns:
        None

    Raises:
        pygame.error: If the font cannot be rendered or if the surface is invalid.
    """
    img = fnt.render(str(text), True, colour)
    r = img.get_rect(**{anchor: pos})
    surf.blit(img, r)


def clamp(value: float, lower: float, upper: float) -> float:
    """Clamps a value between a lower and upper bound."""
    return max(lower, min(upper, value))


def apply_user_input(aircraft: Aircraft, dt: float) -> None:
    """Applies user input from the keyboard to
    control the aircraft's throttle and elevator."""
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        aircraft.controls.throttle = clamp(
            aircraft.controls.throttle + THROTTLE_RATE * dt, 0.0, 1.0
        )
    if keys[pygame.K_s]:
        aircraft.controls.throttle = clamp(
            aircraft.controls.throttle - THROTTLE_RATE * dt, 0.0, 1.0
        )

    if keys[pygame.K_UP]:
        aircraft.controls.elevator_deflection = clamp(
            aircraft.controls.elevator_deflection - ELEVATOR_RATE * dt,
            -MAX_ELEVATOR_DEFLECTION,
            MAX_ELEVATOR_DEFLECTION,
        )
    if keys[pygame.K_DOWN]:
        aircraft.controls.elevator_deflection = clamp(
            aircraft.controls.elevator_deflection + ELEVATOR_RATE * dt,
            -MAX_ELEVATOR_DEFLECTION,
            MAX_ELEVATOR_DEFLECTION,
        )


def draw_ai(surf: pygame.Surface, pitch_deg: float) -> None:
    """Draws the attitude indicator (AI) on the
    given surface based on the current pitch angle.

    Args:
        surf (pygame.Surface): The surface to draw the AI on.
        pitch_deg (float): The current pitch angle in degrees.

    Returns:
        None

    Raises:
        pygame.error: If there is an error drawing on the surface.
    """
    ai_rect = pygame.Rect(AI_X, AI_Y, AI_W, AI_H)

    offset = pitch_deg * PX_DEG

    surf.set_clip(ai_rect)

    surf.fill(SKY, ai_rect)

    hor_y = AI_CY + offset
    if hor_y < AI_Y + AI_H:
        ground_top = max(AI_Y, int(hor_y))
        ground_rect = pygame.Rect(AI_X, ground_top, AI_W, AI_Y + AI_H - ground_top)
        surf.fill(GROUND, ground_rect)

    if AI_Y <= hor_y <= AI_Y + AI_H:
        pygame.draw.line(surf, WHITE, (AI_X, int(hor_y)), (AI_X + AI_W, int(hor_y)), 2)

    f_pitch = font(17)
    for deg in range(-30, 31, 5):
        if deg == 0:
            continue
        y = int(AI_CY + offset - deg * PX_DEG)
        if not (AI_Y + 10 < y < AI_Y + AI_H - 10):
            continue
        is_ten = deg % 10 == 0
        half_w = 80 if is_ten else 46
        pygame.draw.line(surf, WHITE, (AI_CX - half_w, y), (AI_CX - 12, y), 2)
        pygame.draw.line(surf, WHITE, (AI_CX + 12, y), (AI_CX + half_w, y), 2)
        if is_ten:
            label = str(abs(deg))
            txt(surf, label, (AI_CX - half_w - 28, y - 9), f_pitch, WHITE)
            txt(surf, label, (AI_CX + half_w + 4, y - 9), f_pitch, WHITE)

    surf.set_clip(None)

    pygame.draw.rect(surf, DARK, ai_rect, 5)

    cx, cy = AI_CX, AI_CY
    pygame.draw.rect(surf, WHITE, (cx - 94, cy - 5, 62, 10))
    pygame.draw.rect(surf, BLACK, (cx - 94, cy - 5, 62, 10), 1)
    pygame.draw.rect(surf, WHITE, (cx + 32, cy - 5, 62, 10))
    pygame.draw.rect(surf, BLACK, (cx + 32, cy - 5, 62, 10), 1)
    pygame.draw.rect(surf, WHITE, (cx - 8, cy - 8, 16, 16))
    pygame.draw.rect(surf, BLACK, (cx - 8, cy - 8, 16, 16), 1)
    pygame.draw.rect(surf, WHITE, (cx - 2, cy + 8, 4, 16))

    if S["cmd"]:
        f_cmd = font(32, bold=True)
        txt(surf, "CMD", (AI_CX, AI_Y + 10), f_cmd, GREEN, anchor="midtop")


def draw_speed_tape(surf: pygame.Surface, tas: float) -> None:
    """Draws the speed tape on the given surface based on the current true airspeed.

    Args:
        surf (pygame.Surface): The surface to draw the speed tape on.
        tas (float): The current true airspeed in knots.

    Returns:
        None

    Raises:
        pygame.error: If there is an error drawing on the surface.
    """
    rect = pygame.Rect(SPD_X, TAPE_Y, SPD_W, TAPE_H)
    pygame.draw.rect(surf, TAPE_BG, rect)
    pygame.draw.rect(surf, TAPE_BDR, rect, 2)

    surf.set_clip(rect)

    f_tick = font(18)
    px_per_kt = TAPE_H / 80  # 80 kt visible range

    for spd in range(0, 400, 10):
        dy = (tas - spd) * px_per_kt
        y = int(TAPE_Y + TAPE_H // 2 + dy)
        if not (TAPE_Y <= y <= TAPE_Y + TAPE_H):
            continue
        pygame.draw.line(
            surf, WHITE, (SPD_X + SPD_W - 18, y), (SPD_X + SPD_W - 2, y), 2
        )
        if spd % 20 == 0:
            txt(
                surf,
                str(spd),
                (SPD_X + SPD_W - 22, y - 9),
                f_tick,
                WHITE,
                anchor="topright",
            )

    # vref tick
    vref = S["vref_kt"]
    vy = int(TAPE_Y + TAPE_H // 2 + (tas - vref) * px_per_kt)
    if TAPE_Y <= vy <= TAPE_Y + TAPE_H:
        pygame.draw.line(surf, GREEN, (SPD_X + SPD_W - 22, vy), (SPD_X + SPD_W, vy), 3)

    surf.set_clip(None)

    # speed window
    win_h = 46
    win_rect = pygame.Rect(
        SPD_X - 2, TAPE_Y + TAPE_H // 2 - win_h // 2, SPD_W + 4, win_h
    )
    pygame.draw.rect(surf, BLACK, win_rect)
    pygame.draw.rect(surf, WHITE, win_rect, 2)
    f_spd = font(30, bold=True)
    txt(
        surf,
        str(int(tas)),
        (win_rect.centerx, win_rect.centery),
        f_spd,
        WHITE,
        anchor="center",
    )

    # selected speed bug (magenta triangle on right edge)
    sel = S["sel_spd"]
    sy = int(TAPE_Y + TAPE_H // 2 + (tas - sel) * px_per_kt)
    if TAPE_Y <= sy <= TAPE_Y + TAPE_H:
        pts = [
            (SPD_X + SPD_W, sy),
            (SPD_X + SPD_W + 14, sy - 10),
            (SPD_X + SPD_W + 14, sy + 10),
        ]
        pygame.draw.polygon(surf, MAGENTA, pts)

    # selected speed label above tape
    f_lbl = font(22, bold=True)
    txt(surf, str(S["sel_spd"]), (SPD_X, TAPE_Y - 30), f_lbl, MAGENTA)

    # GS below tape
    f_gs = font(22, bold=True)
    txt(surf, f"GS {S['gs_kt']}", (SPD_X, TAPE_Y + TAPE_H + 8), f_gs, GREEN)

    # VREF labels
    f_ref = font(17)
    txt(
        surf,
        f"{S['flap']}/{S['vref_kt']}",
        (SPD_X + 4, TAPE_Y + TAPE_H - 76),
        f_ref,
        GREEN,
    )
    txt(surf, f"VREF {S['vref_kt']}", (SPD_X + 4, TAPE_Y + TAPE_H - 54), f_ref, GREEN)


def draw_alt_tape(surf: pygame.Surface, alt: float) -> None:
    """Draws the altitude tape on the given surface based on
    the current altitude.

    Args:
        surf (pygame.Surface): The surface to draw the altitude tape on.
        alt (float): The current altitude in feet.

    Returns:
        None

    Raises:
        pygame.error: If there is an error drawing on the surface.
    """
    rect = pygame.Rect(ALT_X, TAPE_Y, ALT_W, TAPE_H)
    pygame.draw.rect(surf, TAPE_BG, rect)
    pygame.draw.rect(surf, TAPE_BDR, rect, 2)

    surf.set_clip(rect)

    f_tick = font(18)
    px_per_ft = TAPE_H / 1000  # 1000 ft visible range

    for a in range(-500, 8000, 100):
        dy = (a - alt) * px_per_ft
        y = int(TAPE_Y + TAPE_H // 2 - dy)
        if not (TAPE_Y <= y <= TAPE_Y + TAPE_H):
            continue
        pygame.draw.line(surf, WHITE, (ALT_X + 2, y), (ALT_X + 20, y), 2)
        if a % 500 == 0 and a >= 0:
            txt(surf, str(a), (ALT_X + 24, y - 9), f_tick, WHITE)

    # selected alt line
    sel = S["sel_alt"]
    sel_dy = (sel - alt) * px_per_ft
    sel_y = int(TAPE_Y + TAPE_H // 2 - sel_dy)
    if TAPE_Y <= sel_y <= TAPE_Y + TAPE_H:
        pygame.draw.line(
            surf, MAGENTA, (ALT_X + 2, sel_y), (ALT_X + ALT_W - 2, sel_y), 2
        )
        f_sm = font(16)
        txt(surf, str(sel), (ALT_X + 24, sel_y - 18), f_sm, MAGENTA)

    surf.set_clip(None)

    # altitude window
    win_h = 46
    win_rect = pygame.Rect(
        ALT_X - 2, TAPE_Y + TAPE_H // 2 - win_h // 2, ALT_W + 4, win_h
    )
    pygame.draw.rect(surf, BLACK, win_rect)
    pygame.draw.rect(surf, WHITE, win_rect, 2)

    # split display: big thousands + smaller hundreds
    thousands = int(alt) // 1000
    hundreds = int(alt) % 1000
    f_big = font(30, bold=True)
    f_mid = font(21, bold=True)
    if thousands > 0:
        t_img = f_big.render(str(thousands), True, WHITE)
        h_img = f_mid.render(f"{hundreds:03d}", True, WHITE)
        surf.blit(t_img, (win_rect.x + 6, win_rect.centery - t_img.get_height() // 2))
        surf.blit(
            h_img,
            (
                win_rect.right - h_img.get_width() - 4,
                win_rect.centery - h_img.get_height() // 2,
            ),
        )
    else:
        txt(
            surf,
            str(int(alt)),
            (win_rect.centerx, win_rect.centery),
            f_big,
            WHITE,
            anchor="center",
        )

    # selected alt above tape
    f_sel = font(22, bold=True)
    txt(
        surf,
        str(S["sel_alt"]),
        (ALT_X + ALT_W // 2, TAPE_Y - 30),
        f_sel,
        MAGENTA,
        anchor="midtop",
    )

    # baro below tape
    f_baro = font(20, bold=True)
    txt(surf, f"{S['baro_in']:.2f} IN.", (ALT_X, TAPE_Y + TAPE_H + 8), f_baro, GREEN)


def vs_to_y(v: float) -> int:
    """Map VS (fpm) to a y pixel on the VS tape."""
    mid = TAPE_Y + TAPE_H // 2
    half = TAPE_H // 2 - 24  # usable half-height
    if abs(v) <= 2000:
        return int(mid - (v / 2000) * half * 0.8)
    sign = 1 if v > 0 else -1
    base = (v / 2000) * half * 0.8
    extra = sign * (abs(v) - 2000) / 4000 * half * 0.2
    return int(mid - base - extra)


def draw_vs_tape(surf: pygame.Surface, vs: float) -> None:
    """Draws the vertical speed tape on the
    given surface based on the current vertical speed.

    Args:
        surf (pygame.Surface): The surface to draw the vertical speed tape on.
        vs (float): The current vertical speed in feet per minute.

    Returns:
        None
    """
    rect = pygame.Rect(VS_X, TAPE_Y, VS_W, TAPE_H)
    pygame.draw.rect(surf, TAPE_BG, rect)
    pygame.draw.rect(surf, TAPE_BDR, rect, 2)

    f_vs = font(16)
    marks = [6000, 2000, 1000, 0, -1000, -2000, -6000]
    for v in marks:
        y = vs_to_y(v)
        if not (TAPE_Y <= y <= TAPE_Y + TAPE_H):
            continue
        pygame.draw.line(surf, WHITE, (VS_X + 2, y), (VS_X + 14, y), 2)
        label = str(abs(v) // 1000) if v != 0 else "0"
        col = WHITE if v != 0 else LGRAY
        txt(surf, label, (VS_X + 16, y - 8), f_vs, col)

    # pointer
    py = vs_to_y(vs)
    py = max(TAPE_Y + 4, min(TAPE_Y + TAPE_H - 4, py))
    pts = [(VS_X + 2, py), (VS_X + 18, py - 8), (VS_X + 18, py + 8)]
    pygame.draw.polygon(surf, GREEN, pts)

    # numeric readout
    if abs(vs) > 200:
        f_v2 = font(17, bold=True)
        yt = py - 22 if vs > 0 else py + 6
        txt(
            surf,
            str(abs(int(vs))),
            (VS_X + VS_W // 2, yt),
            f_v2,
            GREEN,
            anchor="midtop",
        )


def draw_hdg_tape(
    surf: pygame.Surface, hdg: float
) -> None:  # this is static since only 4dof ;(
    """Draws the heading tape on the given surface based on the current
    magnetic heading.

    Args:
        surf (pygame.Surface): The surface to draw the heading tape on.
        hdg (float): The current magnetic heading in degrees.

    Returns:
        None

    Raises:
        pygame.error: If there is an error drawing on the surface.
    """
    tape_x = AI_X
    tape_y = AI_Y + AI_H + 8
    tape_w = AI_W
    tape_h = 52

    rect = pygame.Rect(tape_x, tape_y, tape_w, tape_h)
    pygame.draw.rect(surf, TAPE_BG, rect)
    pygame.draw.rect(surf, TAPE_BDR, rect, 2)

    surf.set_clip(rect)

    px_per_deg = tape_w / 40  # 40 degrees visible
    cx = tape_x + tape_w // 2
    f_hdg = font(17)

    for dh in range(-22, 23):
        h = int(hdg + dh) % 360
        x = int(cx + dh * px_per_deg)
        if h % 10 == 0:
            pygame.draw.line(surf, WHITE, (x, tape_y + 2), (x, tape_y + 16), 2)
            if h % 30 == 0:
                label = f"{h:03d}"[:-1]
                txt(surf, label, (x, tape_y + 20), f_hdg, WHITE, anchor="midtop")
        else:
            pygame.draw.line(surf, WHITE, (x, tape_y + 2), (x, tape_y + 9), 1)

    surf.set_clip(None)

    # centre tick (fixed)
    pygame.draw.line(surf, WHITE, (cx, tape_y - 6), (cx, tape_y + 2), 2)

    # heading readout box at bottom of tape
    win_w, win_h = 60, 28
    win_rect = pygame.Rect(cx - win_w // 2, tape_y + tape_h - win_h - 2, win_w, win_h)
    pygame.draw.rect(surf, BLACK, win_rect)
    pygame.draw.rect(surf, WHITE, win_rect, 2)
    f_h2 = font(20, bold=True)
    txt(
        surf,
        f"{int(hdg):03d}",
        (win_rect.centerx, win_rect.centery),
        f_h2,
        WHITE,
        anchor="center",
    )

    # MAG label
    txt(
        surf,
        "MAG",
        (tape_x + tape_w // 2, tape_y + tape_h + 4),
        font(17),
        GREEN,
        anchor="midtop",
    )

    # selected heading
    f_sh = font(22, bold=True)
    txt(
        surf,
        f"{S['hdg_mag']:03d} H",
        (tape_x + tape_w // 2, tape_y + tape_h + 26),
        f_sh,
        MAGENTA,
        anchor="midtop",
    )


def draw_annunciations(surf: pygame.Surface) -> None:
    """Draws any annunciations (warnings, cautions, advisories)
    on the given surface based on the current state.

    Args:
        surf (pygame.Surface): The surface to draw the annunciations on.

    Returns:
        None

    Raises:
        pygame.error: If there is an error drawing on the surface.
    """
    f = font(22, bold=True)
    f2 = font(18)
    cx = AI_CX
    x0 = AI_X
    x1 = AI_X + AI_W

    # three mode boxes
    txt(surf, "FMC SPD", (x0 + 4, 30), f, GREEN, anchor="midleft")
    txt(surf, "LNAV", (cx, 30), f, GREEN, anchor="center")
    txt(surf, "VNAV PTH", (x1 - 4, 30), f, GREEN, anchor="midright")

    sep1 = x0 + AI_W // 3
    sep2 = x0 + 2 * AI_W // 3
    pygame.draw.line(surf, LGRAY, (sep1, 14), (sep1, 48), 1)
    pygame.draw.line(surf, LGRAY, (sep2, 14), (sep2, 48), 1)

    # left info block
    txt(surf, "IPOS/104°", (AI_X + 10, AI_Y + 14), f2, WHITE)
    txt(surf, "DME  ---", (AI_X + 10, AI_Y + 33), f2, WHITE)
    txt(surf, "LNAV/VNAV", (AI_X + 10, AI_Y + 57), f2, WHITE)


def update_state_from_aircraft(aircraft: Aircraft) -> None:
    """Updates the display state dictionary S based on the current state of
    the aircraft.

    Args:
        aircraft (Aircraft): The aircraft object containing the current
        state of the simulation.

    Returns:
        None

    Raises:
        AttributeError: If the aircraft object does not have the required attributes.
    """
    v = (aircraft.state.u**2 + aircraft.state.w**2) ** 0.5
    mach = v / math.sqrt(
        1.4
        * aircraft.atmosphere.R
        * (aircraft.atmosphere.T0 + aircraft.atmosphere.L * aircraft.state.height)
    )
    tas_kt = v * KTS_PER_MPS
    alt_ft = aircraft.state.height * FT_PER_M
    vs_mps = aircraft.state.u * math.sin(
        aircraft.state.theta
    ) - aircraft.state.w * math.cos(aircraft.state.theta)
    vs_fpm = vs_mps * FPM_PER_MPS

    S["tas_kt"] = max(0.0, tas_kt)
    S["altitude_ft"] = max(0.0, alt_ft)
    S["vs_fpm"] = vs_fpm
    S["pitch_deg"] = math.degrees(aircraft.state.theta)
    S["gs_kt"] = int(tas_kt)
    S["throttle"] = aircraft.controls.throttle
    S["elevator_deg"] = aircraft.controls.elevator_deflection
    S["mach"] = mach
    S["aoa"] = math.degrees(math.atan2(aircraft.state.w, aircraft.state.u))
