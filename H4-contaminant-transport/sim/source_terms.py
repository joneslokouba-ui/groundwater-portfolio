"""
source_terms.py — H4 Contaminant Transport Simulator

Utilities for seeding particles at a contaminant source. Supports a point
source (e.g. a spill or leaking tank) and a small-area source (e.g. a
source zone with some spatial extent).
"""

import numpy as np


def seed_point_source(x0, y0, n_particles, jitter=0.0, rng=None):
    """
    Seed particles at (or tightly clustered around) a single point source.

    Parameters
    ----------
    x0, y0 : float
        Source coordinates.
    n_particles : int
        Number of particles to seed.
    jitter : float
        Optional small random spatial spread around the point (e.g. to
        represent source-zone uncertainty), same units as x0/y0.
    rng : np.random.Generator or None

    Returns
    -------
    x, y : 1D arrays of length n_particles
    """
    rng = rng or np.random.default_rng()
    x = np.full(n_particles, x0, dtype=float)
    y = np.full(n_particles, y0, dtype=float)
    if jitter > 0:
        x += rng.normal(0, jitter, n_particles)
        y += rng.normal(0, jitter, n_particles)
    return x, y


def seed_area_source(x_min, x_max, y_min, y_max, n_particles, rng=None):
    """
    Seed particles uniformly within a rectangular source-zone footprint.

    Returns
    -------
    x, y : 1D arrays of length n_particles
    """
    rng = rng or np.random.default_rng()
    x = rng.uniform(x_min, x_max, n_particles)
    y = rng.uniform(y_min, y_max, n_particles)
    return x, y


def seed_continuous_release(x0, y0, n_particles_per_step, n_steps, jitter=0.0, rng=None):
    """
    Seed particles for a continuous-release scenario: a batch of new
    particles introduced at every timestep rather than all at once.

    Returns
    -------
    release_schedule : list of length n_steps, each element a tuple (x, y)
        of arrays for particles released at that timestep.
    """
    rng = rng or np.random.default_rng()
    schedule = []
    for _ in range(n_steps):
        x, y = seed_point_source(x0, y0, n_particles_per_step, jitter=jitter, rng=rng)
        schedule.append((x, y))
    return schedule