# 4 DOF Aircraft Simulator (Boeing 737)

## Description

- Purpose: Simulate the flight dynamics of a Boeing 737 using real aerodynamic data and flight dynamics equations and
    display the result to a PFD (Primary Flight Display) style interface.

- Scope: Focuses on 4 degrees of freedom (longitudinal directional dynamics)

- Key Features:
    - Nonlinear 6-state longitudinal flight dynamics model using body-axis velocities, pitch angle, and pitch rate.

$$state = [u, w, q, θ, h, x]^T$$

    - Aerodynamic forces and moments derived from real Boeing 737 airfoil data (Cl, Cd, Cm) as functions of angle of attack.
    - Forces and moments modelled as stability-derivative based functions.
    - Realistic atmospheric model for air density and speed of sound variations with altitude.
    - PFD-style display showing airspeed, altitude, vertical speed, and pitch angle.
    - Control inputs for throttle and elevator deflection to influence the aircraft's state.
    - Modelled compressible flow effects at high speeds (Mach > 0.3) using Prandtl-Glauert correction.
    - Modelled wave drag at transonic speeds using a simplified approximation:

$$\Delta C_{D,wave} = k \cdot (M - M_{crit})^m$$

        where $M_{crit}$ is the critical Mach number and $k, m$ are empirically derived constants.
    - Aircraft inertia estimation using radius of gyration approximations based on typical commercial airliner mass distributions.

$$I_{yy} = m \cdot (r_g L)^2$$

        where $r_g$ is the radius of gyration as a fraction of the aircraft length $L$.
    - Foundation for future extensions to include lateral-directional dynamics, control surface deflections, more detailed aerodynamic modeling, autopilot systems, post stall behavior, structural deformation effects, and more advanced rendering of the PFD.
    - Accurate kinematics integration using Runge-Kutta-Fehlberg method for improved stability and accuracy over simple Euler integration.

## Quick Start

### Requirements

- Python environment from `requirements.txt`
- Pygame for the simulator UI

### Install

```bash
pip install -r requirements.txt
```

### Run

```bash
python -m src
```

## Controls

- `W` / `S`: throttle up / down
- `Up` / `Down`: elevator deflection up / down
- `Esc`: exit the simulator

## Project Structure

- `src/__main__.py` — application entry point and simulator loop
- `src/models/aircraft.py` — aircraft dynamics, state, and controls
- `src/models/airfoil.py` — airfoil coefficient extraction and fitting
- `src/utils/atmosphere.py` — ISA atmosphere model
- `src/utils/pfd.py` — PFD rendering and keyboard input handling
- `src/exceptions/exceptions.py` — custom errors and warnings
- `src/data/` — aircraft configuration and aerodynamic data
- `test-models/` — example or exploratory model scripts

## Data Sources

### Drag Polar Coefficients

[Aircraft Drag Polar Estimation Based on a Stochastic Hierarchical Model](https://www.sesarju.eu/sites/default/files/documents/sid/2018/papers/SIDs_2018_paper_75.pdf) by Junzi Sun, Jacco M. Hoekstra, and Joost Ellerbroek.

### $C_L$ vs. angle of attack data

[BOEING 737 MIDSPAN AIRFOIL (b737b-il) Xfoil prediction polar at RE=1,000,000 Ncrit=9](http://airfoiltools.com/polar/details?polar=xf-b737b-il-1000000)

## Model Notes

- The simulator currently models longitudinal motion only.
- Compressibility corrections are applied for higher Mach numbers.
- Moments are based on the available airfoil and configuration data.
- The state is managed through `AircraftState` and the control inputs through `Controls`.

## Development

- Formatting: `black`
- Import sorting: `isort`
- Linting: `flake8`

## Limitations

- No lateral-directional model yet.
- No full autopilot system yet.
- No structural or aeroelastic deformation model yet.
- Rendering is PFD-focused rather than full 3D visualization.

## Future Work

- Add lateral-directional dynamics
- Add flap/slat and other control-surface effects
- Add autopilot and flight directors
- Improve stall and post-stall modeling
- Add structural and failure limits
- Expand rendering beyond the PFD

## License

See the [LICENSE](LICENSE) file for details.