"""
particle_tracker.py — H4 Contaminant Transport Simulator

Core random-walk particle tracking engine. Rides a velocity field produced
by H3 (sim/darcy_flux.build_velocity_field) and evolves particle positions
over time under four mechanisms:

    - Advection    : displacement along the local Darcy velocity
    - Dispersion   : random-walk step scaled to dispersivity (longitudinal
                      and transverse components, relative to local flow
                      direction)
    - Retardation  : velocity multiplier 1/R (sorption slows the plume
                      relative to the water itself)
    - Decay        : per-step survival probability (first-order kinetics)

See docs/adr-001-transport-architecture.md for the rationale behind
choosing particle tracking over a grid-based ADE solver, and the known
mass-balance limitation.
"""

import numpy as np


def _bilinear_sample(field, x_1d, y_1d, x, y):
    """Bilinear interpolation of a gridded field at arrays of points (x, y)."""
    ix = np.clip(np.searchsorted(x_1d, x) - 1, 0, len(x_1d) - 2)
    iy = np.clip(np.searchsorted(y_1d, y) - 1, 0, len(y_1d) - 2)

    x0, x1 = x_1d[ix], x_1d[ix + 1]
    y0, y1 = y_1d[iy], y_1d[iy + 1]

    with np.errstate(invalid="ignore", divide="ignore"):
        tx = np.where(x1 != x0, (x - x0) / (x1 - x0), 0.0)
        ty = np.where(y1 != y0, (y - y0) / (y1 - y0), 0.0)

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


class ParticleTracker:
    """
    Random-walk particle tracking simulator for contaminant transport.

    Parameters
    ----------
    velocity_field : dict
        Output of H3's darcy_flux.build_velocity_field: must contain
        'qx', 'qy', 'x_grid', 'y_grid'.
    porosity : float
        Effective porosity (converts Darcy/specific discharge to
        seepage/linear velocity: v = q / n). Typical sand/gravel: 0.2-0.35.
    alpha_l, alpha_t : float
        Longitudinal and transverse dispersivity (length units, same as
        grid coordinates). Random-walk step std dev is scaled to these.
    retardation_factor : float
        R >= 1. Contaminant velocity = seepage velocity / R.
    decay_rate : float
        First-order decay constant (per unit time). 0 = conservative,
        no decay. Survival probability per step = exp(-decay_rate * dt).
    rng : np.random.Generator or None
    """

    def __init__(
        self,
        velocity_field,
        porosity=0.3,
        alpha_l=10.0,
        alpha_t=1.0,
        retardation_factor=1.0,
        decay_rate=0.0,
        rng=None,
    ):
        self.qx = velocity_field["qx"]
        self.qy = velocity_field["qy"]
        self.x_grid = velocity_field["x_grid"]
        self.y_grid = velocity_field["y_grid"]
        self.x_1d = self.x_grid[0, :]
        self.y_1d = self.y_grid[:, 0]

        if porosity <= 0:
            raise ValueError("porosity must be > 0")
        if retardation_factor < 1.0:
            raise ValueError("retardation_factor must be >= 1.0")

        self.porosity = porosity
        self.alpha_l = alpha_l
        self.alpha_t = alpha_t
        self.R = retardation_factor
        self.decay_rate = decay_rate
        self.rng = rng or np.random.default_rng()

    def _sample_velocity(self, x, y):
        """Seepage (linear) velocity at particle positions, corrected for R."""
        qx = _bilinear_sample(self.qx, self.x_1d, self.y_1d, x, y)
        qy = _bilinear_sample(self.qy, self.x_1d, self.y_1d, x, y)
        vx = qx / self.porosity / self.R
        vy = qy / self.porosity / self.R
        return vx, vy

    def step(self, x, y, active, dt):
        """
        Advance all active particles by one timestep.

        Parameters
        ----------
        x, y : 1D arrays
            Current particle positions.
        active : 1D bool array
            Which particles are still active (alive and in-bounds).
        dt : float
            Timestep length.

        Returns
        -------
        x_new, y_new, active_new : updated arrays
        """
        x_new = x.copy()
        y_new = y.copy()
        active_new = active.copy()

        idx = np.where(active)[0]
        if len(idx) == 0:
            return x_new, y_new, active_new

        vx, vy = self._sample_velocity(x[idx], y[idx])
        speed = np.hypot(vx, vy)
        speed_safe = np.where(speed < 1e-12, 1.0, speed)

        # Unit vectors along (longitudinal) and perpendicular (transverse) to flow
        ux = vx / speed_safe
        uy = vy / speed_safe
        tx = -uy
        ty = ux

        # Advection displacement
        adv_x = vx * dt
        adv_y = vy * dt

        # Dispersion: random-walk step, std dev scaled to dispersivity and speed
        # (Fickian dispersion coefficient D = alpha * v; step std ~ sqrt(2*D*dt))
        d_l = np.sqrt(np.maximum(2 * self.alpha_l * speed * dt, 0.0))
        d_t = np.sqrt(np.maximum(2 * self.alpha_t * speed * dt, 0.0))

        rand_l = self.rng.normal(0, 1, len(idx)) * d_l
        rand_t = self.rng.normal(0, 1, len(idx)) * d_t

        disp_x = rand_l * ux + rand_t * tx
        disp_y = rand_l * uy + rand_t * ty

        x_new[idx] = x[idx] + adv_x + disp_x
        y_new[idx] = y[idx] + adv_y + disp_y

        # Decay: survival probability per step
        if self.decay_rate > 0:
            survive_prob = np.exp(-self.decay_rate * dt)
            survives = self.rng.uniform(0, 1, len(idx)) < survive_prob
            active_new[idx[~survives]] = False

        # Deactivate particles that leave the grid bounds
        out_of_bounds = (
            (x_new[idx] < self.x_1d.min()) | (x_new[idx] > self.x_1d.max()) |
            (y_new[idx] < self.y_1d.min()) | (y_new[idx] > self.y_1d.max())
        )
        active_new[idx[out_of_bounds]] = False

        return x_new, y_new, active_new

    def run(self, x0, y0, n_steps, dt):
        """
        Run the full simulation from initial particle positions.

        Parameters
        ----------
        x0, y0 : 1D arrays
            Initial particle positions.
        n_steps : int
            Number of timesteps to simulate.
        dt : float
            Timestep length.

        Returns
        -------
        trajectory : dict
            'x': array of shape (n_steps+1, n_particles)
            'y': array of shape (n_steps+1, n_particles)
            'active': array of shape (n_steps+1, n_particles), bool
        """
        n_particles = len(x0)
        x_hist = np.zeros((n_steps + 1, n_particles))
        y_hist = np.zeros((n_steps + 1, n_particles))
        active_hist = np.zeros((n_steps + 1, n_particles), dtype=bool)

        x_hist[0] = x0
        y_hist[0] = y0
        active_hist[0] = True

        for t in range(n_steps):
            x_hist[t + 1], y_hist[t + 1], active_hist[t + 1] = self.step(
                x_hist[t], y_hist[t], active_hist[t], dt
            )

        return {"x": x_hist, "y": y_hist, "active": active_hist}