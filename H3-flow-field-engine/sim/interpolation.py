"""
interpolation.py — H3 Flow Field Engine

Interpolates sparse well-head observations onto a regular grid.
Default method: Inverse Distance Weighting (IDW).
Optional method: Kriging (via pykrige, if installed) for uncertainty
quantification.

See docs/adr-001-flow-field-architecture.md for design rationale.
"""

import numpy as np


def idw_interpolate(well_x, well_y, well_h, grid_x, grid_y, power=2, eps=1e-9):
    """
    Inverse Distance Weighting interpolation of head observations onto a grid.

    Parameters
    ----------
    well_x, well_y, well_h : array-like
        Well coordinates and observed heads. Same length.
    grid_x, grid_y : 2D arrays (meshgrid)
        Target grid coordinates.
    power : float
        IDW distance-decay exponent. Higher = more local influence.
    eps : float
        Small value to avoid division by zero at well locations.

    Returns
    -------
    head_grid : 2D array, same shape as grid_x/grid_y
    """
    well_x = np.asarray(well_x, dtype=float)
    well_y = np.asarray(well_y, dtype=float)
    well_h = np.asarray(well_h, dtype=float)

    if not (len(well_x) == len(well_y) == len(well_h)):
        raise ValueError("well_x, well_y, well_h must be the same length")
    if len(well_x) < 2:
        raise ValueError("IDW requires at least 2 well observations")

    gx = grid_x.ravel()
    gy = grid_y.ravel()

    # distances: (n_grid_points, n_wells)
    dx = gx[:, None] - well_x[None, :]
    dy = gy[:, None] - well_y[None, :]
    dist = np.sqrt(dx**2 + dy**2) + eps

    weights = 1.0 / (dist**power)
    weights_sum = weights.sum(axis=1)

    head_flat = (weights * well_h[None, :]).sum(axis=1) / weights_sum

    return head_flat.reshape(grid_x.shape)


def kriging_interpolate(well_x, well_y, well_h, grid_x, grid_y):
    """
    Ordinary kriging interpolation, providing both the head estimate and
    kriging variance (uncertainty surface).

    Requires pykrige. Raises ImportError with a clear message if unavailable
    so the caller can fall back to IDW.

    Returns
    -------
    head_grid, variance_grid : 2D arrays, same shape as grid_x
    """
    try:
        from pykrige.ok import OrdinaryKriging
    except ImportError as e:
        raise ImportError(
            "kriging_interpolate requires pykrige. "
            "Install with: pip install pykrige "
            "(and add 'pykrige' to requirements.txt). "
            "Falling back to idw_interpolate is recommended if unavailable."
        ) from e

    ok = OrdinaryKriging(
        well_x, well_y, well_h,
        variogram_model="linear",
        verbose=False,
        enable_plotting=False,
    )
    x_1d = grid_x[0, :]
    y_1d = grid_y[:, 0]
    head_grid, variance_grid = ok.execute("grid", x_1d, y_1d)

    return np.asarray(head_grid), np.asarray(variance_grid)


def make_grid(x_min, x_max, y_min, y_max, n=100):
    """Convenience helper: build a regular meshgrid for interpolation targets."""
    x = np.linspace(x_min, x_max, n)
    y = np.linspace(y_min, y_max, n)
    return np.meshgrid(x, y)