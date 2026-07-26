"""
Theis (1935) solution for transient radial groundwater flow to a
fully-penetrating well in a confined, homogeneous, isotropic aquifer
of infinite areal extent.

    s(r, t) = Q / (4 * pi * T) * W(u)
    u = r^2 * S / (4 * T * t)

where:
    s  = drawdown (m)
    Q  = pumping rate (m^3/day)
    T  = transmissivity (m^2/day)
    S  = storativity (dimensionless)
    r  = radial distance from pumping well (m)
    t  = time since pumping start (days)
    W(u) = well function = exponential integral E1(u)

This module also performs the inverse problem: given observed
drawdown-vs-time data at a known distance, estimate T and S by
nonlinear least-squares curve fitting (the same class of problem
PEST solves for full numerical models, done here analytically for
a single aquifer test).
"""

import numpy as np
from scipy.special import exp1
from scipy.optimize import curve_fit


def well_function(u):
    """W(u), the Theis well function (exponential integral E1)."""
    return exp1(u)


def theis_drawdown(t, T, S, Q, r):
    """
    Drawdown at distance r and time(s) t for given aquifer
    properties T (transmissivity) and S (storativity).

    t : array-like, time since pumping start (days)
    T : transmissivity (m^2/day)
    S : storativity (-)
    Q : pumping rate (m^3/day)
    r : distance from pumping well (m)
    """
    t = np.asarray(t, dtype=float)
    u = (r ** 2 * S) / (4.0 * T * t)
    return (Q / (4.0 * np.pi * T)) * well_function(u)


def generate_synthetic_observations(T_true, S_true, Q, r, t, noise_std=0.02, seed=42):
    """
    Simulate a field pumping test: 'true' aquifer properties produce
    drawdown at times t, with measurement noise added, the way real
    field data would look before calibration.
    """
    rng = np.random.default_rng(seed)
    s_true = theis_drawdown(t, T_true, S_true, Q, r)
    noise = rng.normal(0, noise_std, size=s_true.shape)
    return np.clip(s_true + noise, a_min=0, a_max=None)


def fit_aquifer_properties(t, s_observed, Q, r, T_guess=100.0, S_guess=1e-4):
    """
    Estimate T and S from observed drawdown data via nonlinear
    least-squares curve fitting against the Theis solution.

    Returns (T_fit, S_fit, covariance_matrix).
    """
    def model(t, T, S):
        return theis_drawdown(t, T, S, Q, r)

    popt, pcov = curve_fit(
        model, t, s_observed,
        p0=[T_guess, S_guess],
        bounds=([1e-3, 1e-8], [1e6, 1.0]),
        maxfev=10000
    )
    return popt[0], popt[1], pcov


if __name__ == "__main__":
    # Quick self-test / demonstration
    Q = 500.0          # m^3/day pumping rate
    r = 30.0            # m, observation well distance
    T_true, S_true = 250.0, 2.5e-4

    t = np.logspace(-2, 1, 25)  # 0.01 to 10 days
    s_obs = generate_synthetic_observations(T_true, S_true, Q, r, t)

    T_fit, S_fit, cov = fit_aquifer_properties(t, s_obs, Q, r)

    print(f"True:  T={T_true:.2f} m2/day, S={S_true:.2e}")
    print(f"Fit:   T={T_fit:.2f} m2/day, S={S_fit:.2e}")
    print(f"Error: T={abs(T_fit-T_true)/T_true*100:.1f}%, S={abs(S_fit-S_true)/S_true*100:.1f}%")