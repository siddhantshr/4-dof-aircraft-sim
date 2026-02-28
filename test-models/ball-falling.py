import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

"""
consider a tennis ball thrown from ground at a speed of 20m/s directly upwards
"""

RHO = 1.22  # (ISA)
ACCELERATION_GRAVITY = 9.81
PI = 3.141
DIAMETER = 6.5 * 0.01
MASS = 60 * 0.001
CD = 0.6

ALPHA = (PI * (DIAMETER**2) * RHO * CD) / (8 * MASS)


def equation(t, Y):
    x, v = Y
    return [v, -ACCELERATION_GRAVITY - ALPHA * abs(v) * v]


def hit_ground(t, Y):
    return Y[0]  # We want to find when height (x) is zero


hit_ground.terminal = True  # Stop the integration when this event occurs
hit_ground.direction = -1  # We are only interested in when the ball is falling down

t = np.linspace(0, 6, 1000)
v0 = 20
x0 = 0
sol = solve_ivp(equation, t_span=(0, max(t)), y0=[x0, v0], t_eval=t, events=hit_ground)

# plt x and v vs t
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(sol.t, sol.y[0], label="Height (m)")
plt.title("Height vs Time")
plt.xlabel("Time (s)")
plt.ylabel("Height (m)")
plt.grid()
plt.legend()
plt.subplot(2, 1, 2)
plt.plot(sol.t, sol.y[1], label="Velocity (m/s)", color="orange")
plt.title("Velocity vs Time")
plt.xlabel("Time (s)")
plt.ylabel("Velocity (m/s)")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()
