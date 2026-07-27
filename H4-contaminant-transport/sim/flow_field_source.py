"""
flow_field_source.py — H4 Contaminant Transport Simulator

Self-contained synthetic velocity field generator, used so H4 can run and
deploy independently without importing H3's interpolation pipeline across
module folders (see folder-tree discussion — modules are kept self-contained
for now; a future `shared/` package could unify this with H3's actual
build_velocity_field output).

Provides a uniform regional flow field, optionally perturbed by a pumping
well (radial drawdown), which is enough to drive realistic-looking
advection-dispersion demos without needing real well data.
"""

import numpy as np


def make_grid(x_min, x_max, y_min, y_max, n=100):
    x = np.linspace(x_min, x_max, n)
    y = np.linspace(y_min, y_max, n)
    return np.meshgrid(x, y)


def uniform_flow_field(grid_x, grid_y, gradient_magnitude=0.001, direction_deg=0.0, K=10.0):
    """
    Uniform regional flow field: constant hydraulic gradient in a given
    direction, converted to Darcy flux via q = K * i.

    Parameters
    ----------
    gradient_magnitude : float
        Hydraulic gradient (dimensionless, e.g. 0.001 = 1 m drop per 1000 m).
    direction_deg : float
        Flow direction, degrees counterclockwise from +x axis.
    K : float
        Hydraulic conductivity.

    Returns
    -------
    qx, qy : 2D arrays, same shape as grid_x
    """
    theta = np.radians(direction_deg)
    i_x = gradient_magnitude * np.cos(theta)
    i_y = gradient_magnitude * np.sin(theta)
    qx = np.full_like(grid_x, K * i_x, dtype=float)
    qy = np.full_like(grid_y, K * i_y, dtype=float)
    return qx, qy


def add_pumping_well(qx, qy, grid_x, grid_y, well_xy, pumping_rate, K=10.0, b=10.0, eps=1e-6):
    """
    Superimpose radial flow from a pumping well onto an existing flux field
    (simple superposition, homogeneous confined aquifer assumption).

    Parameters
    ----------
    pumping_rate : float
        Positive = extraction (radially inward), negative = injection
        (radially outward). Volumetric rate (e.g. m^3/day).
    b : float
        Aquifer thickness (for confined aquifer Q -> flux conversion).

    Returns
    -------
    qx_new, qy_new : 2D arrays with the well's radial component added
    """
    dx = grid_x - well_xy[0]
    dy = grid_y - well_xy[1]
    r2 = dx**2 + dy**2 + eps
    r = np.sqrt(r2)

    # Radial specific discharge from a well: q_r = -Q / (2*pi*r*b), directed
    # toward the well for extraction (pumping_rate > 0)
    q_r = -pumping_rate / (2 * np.pi * r * b)

    qx_well = q_r * (dx / r)
    qy_well = q_r * (dy / r)

    return qx + qx_well, qy + qy_well


def build_velocity_field(
    x_min, x_max, y_min, y_max, n=80,
    gradient_magnitude=0.001, direction_deg=0.0, K=10.0,
    well_xy=None, pumping_rate=0.0, aquifer_thickness=10.0,
):
    """
    Convenience wrapper: build a full synthetic velocity field dict in the
    same shape H3's build_velocity_field produces, so H4's particle tracker
    (which expects qx, qy, x_grid, y_grid) works unmodified regardless of
    which module produced the field.
    """
    grid_x, grid_y = make_grid(x_min, x_max, y_min, y_max, n=n)
    qx, qy = uniform_flow_field(grid_x, grid_y, gradient_magnitude, direction_deg, K)

    if well_xy is not None and pumping_rate != 0.0:
        qx, qy = add_pumping_well(qx, qy, grid_x, grid_y, well_xy,
                                    pumping_rate, K=K, b=aquifer_thickness)

    magnitude = np.hypot(qx, qy)

    return {
        "qx": qx, "qy": qy, "magnitude": magnitude,
        "x_grid": grid_x, "y_grid": grid_y, "K": K,
    }