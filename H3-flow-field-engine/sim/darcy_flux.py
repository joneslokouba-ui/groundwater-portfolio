"""
darcy_flux.py — H3 Flow Field Engine

Utility functions built on top of flow_net.compute_darcy_velocity for
dashboard display: flux magnitude, direction, and a convenience wrapper
that packages qx/qy into a downstream-ready dict for H4.
"""

import numpy as np

from .flow_net import compute_darcy_velocity


def flux_magnitude(qx, qy):
    """Specific discharge magnitude at each grid point."""
    return np.hypot(qx, qy)


def flux_direction_deg(qx, qy):
    """Flow direction in degrees, measured counterclockwise from +x axis."""
    return np.degrees(np.arctan2(qy, qx))


def build_velocity_field(head_grid, dx, dy, K=1.0, x_grid=None, y_grid=None):
    """
    Compute the full Darcy velocity field and package it for downstream use
    (H4 particle tracker expects this shape).

    Returns
    -------
    dict with keys: qx, qy, magnitude, direction_deg, x_grid, y_grid, K, dx, dy
    """
    qx, qy = compute_darcy_velocity(head_grid, dx, dy, K=K)

    return {
        "qx": qx,
        "qy": qy,
        "magnitude": flux_magnitude(qx, qy),
        "direction_deg": flux_direction_deg(qx, qy),
        "x_grid": x_grid,
        "y_grid": y_grid,
        "K": K,
        "dx": dx,
        "dy": dy,
    }