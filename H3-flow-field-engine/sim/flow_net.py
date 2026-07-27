"""
flow_net.py — H3 Flow Field Engine

Derives streamlines from an interpolated head grid, orthogonal to the
equipotential lines (head contours), via the stream function psi.

ASSUMPTION BOUNDARY (see ADR-001):
This derivation is valid strictly under homogeneous, isotropic K. For
heterogeneous/layered aquifers, true flow-net orthogonality breaks down and
a full 2D PDE solve (div(K grad h) = 0) would be required instead. This
module does NOT attempt that — heterogeneous support is explicitly deferred.
Callers must set `homogeneous=True` to acknowledge the assumption; passing
False raises NotImplementedError rather than silently producing an
inaccurate flow net.
"""

import numpy as np


def compute_stream_function(head_grid, dx, dy, K=1.0, homogeneous=True):
    """
    Compute the stream function psi from a head grid, under the
    homogeneous/isotropic assumption.

    For 2D steady flow with K constant, the relationship between head h and
    stream function psi (Cauchy-Riemann conjugate pair) gives:
        d(psi)/dy = -K * dh/dx
        d(psi)/dx =  K * dh/dy

    psi is recovered by integrating these gradients across the grid.

    Parameters
    ----------
    head_grid : 2D array
        Interpolated head values.
    dx, dy : float
        Grid spacing in x and y.
    K : float
        Hydraulic conductivity (homogeneous, isotropic).
    homogeneous : bool
        Must be True. Explicit acknowledgment of the ADR-001 assumption
        boundary — heterogeneous K-fields are not supported here.

    Returns
    -------
    psi : 2D array, same shape as head_grid
    """
    if not homogeneous:
        raise NotImplementedError(
            "Heterogeneous K-field flow nets require a full 2D PDE solve "
            "(div(K grad h) = 0), which this module does not implement. "
            "See ADR-001 assumption boundary. Pass homogeneous=True to "
            "proceed with the isotropic approximation, or use it only as "
            "an approximate overlay with the dashboard flagged accordingly."
        )

    dh_dy, dh_dx = np.gradient(head_grid, dy, dx)

    # Integrate d(psi)/dx = K * dh/dy along x (rows), then adjust with y-integration
    psi = np.zeros_like(head_grid)
    psi_dx = K * dh_dy  # d(psi)/dx
    psi[:, 1:] = np.cumsum(psi_dx[:, 1:] * dx, axis=1) + psi[:, [0]]

    return psi


def compute_darcy_velocity(head_grid, dx, dy, K=1.0):
    """
    Darcy flux/velocity field: q = -K * grad(h).

    Returns
    -------
    qx, qy : 2D arrays, same shape as head_grid
        Specific discharge components.
    """
    dh_dy, dh_dx = np.gradient(head_grid, dy, dx)
    qx = -K * dh_dx
    qy = -K * dh_dy
    return qx, qy


def trace_streamline(qx, qy, x_grid, y_grid, start_xy, n_steps=200, step_size=None):
    """
    Trace a single streamline from a starting point by following the
    Darcy velocity field (simple forward-Euler integration).

    Parameters
    ----------
    qx, qy : 2D arrays
        Velocity field components (from compute_darcy_velocity).
    x_grid, y_grid : 2D arrays
        Coordinate grids matching qx/qy shape.
    start_xy : tuple(float, float)
        Starting (x, y) coordinate for the streamline.
    n_steps : int
        Number of integration steps.
    step_size : float or None
        Step length. Defaults to ~1/200th of the grid's x-extent.

    Returns
    -------
    path_x, path_y : 1D arrays of streamline coordinates
    """
    x_1d = x_grid[0, :]
    y_1d = y_grid[:, 0]

    if step_size is None:
        step_size = (x_1d.max() - x_1d.min()) / 200.0

    path = [start_xy]
    x, y = start_xy

    for _ in range(n_steps):
        vx = _bilinear_sample(qx, x_1d, y_1d, x, y)
        vy = _bilinear_sample(qy, x_1d, y_1d, x, y)
        speed = np.hypot(vx, vy)
        if speed < 1e-12:
            break
        x += step_size * vx / speed
        y += step_size * vy / speed
        if not (x_1d.min() <= x <= x_1d.max() and y_1d.min() <= y <= y_1d.max()):
            break
        path.append((x, y))

    path = np.array(path)
    return path[:, 0], path[:, 1]


def _bilinear_sample(field, x_1d, y_1d, x, y):
    """Bilinear interpolation of a gridded field at point (x, y)."""
    ix = np.clip(np.searchsorted(x_1d, x) - 1, 0, len(x_1d) - 2)
    iy = np.clip(np.searchsorted(y_1d, y) - 1, 0, len(y_1d) - 2)

    x0, x1 = x_1d[ix], x_1d[ix + 1]
    y0, y1 = y_1d[iy], y_1d[iy + 1]

    tx = (x - x0) / (x1 - x0) if x1 != x0 else 0.0
    ty = (y - y0) / (y1 - y0) if y1 != y0 else 0.0

    f00 = field[iy, ix]
    f10 = field[iy, ix + 1]
    f01 = field[iy + 1, ix]
    f11 = field[iy + 1, ix + 1]

    return (
        f00 * (1 - tx) * (1 - ty)
        + f10 * tx * (1 - ty)
        + f01 * (1 - tx) * ty
        + f11 * tx * ty
    )