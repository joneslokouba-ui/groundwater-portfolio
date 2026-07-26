import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "03-calibration-validation"))

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from theis_solution import (
    theis_drawdown,
    generate_synthetic_observations,
    fit_aquifer_properties,
)

st.set_page_config(page_title="Aquifer Pumping Test Analysis", layout="wide")

st.title("Aquifer Pumping Test Analysis — Theis Type-Curve Fitting")
st.caption(
    "Analytical groundwater modelling tool: simulates a confined-aquifer pumping "
    "test, then estimates transmissivity (T) and storativity (S) from the "
    "drawdown data via nonlinear least-squares curve fitting — the same class "
    "of inverse problem PEST solves for full numerical models, shown here for "
    "a single-well analytical case."
)

# ---------------- Sidebar: test setup ----------------
st.sidebar.header("Pumping Test Setup")
Q = st.sidebar.number_input("Pumping rate, Q (m³/day)", 10.0, 5000.0, 500.0, step=10.0)
r = st.sidebar.number_input("Observation distance, r (m)", 1.0, 500.0, 30.0, step=1.0)

st.sidebar.header("'True' Aquifer Properties (synthetic field data)")
T_true = st.sidebar.slider("Transmissivity, T (m²/day)", 10.0, 1000.0, 250.0)
S_true = st.sidebar.select_slider(
    "Storativity, S (–)",
    options=[1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2],
    value=2.5e-4 if 2.5e-4 in [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2] else 1e-4,
)
noise = st.sidebar.slider("Measurement noise (m)", 0.0, 0.2, 0.02)

t = np.logspace(-2, 1, 30)
s_obs = generate_synthetic_observations(T_true, S_true, Q, r, t, noise_std=noise)

# ---------------- Calibration ----------------
T_fit, S_fit, cov = fit_aquifer_properties(t, s_obs, Q, r)
t_smooth = np.logspace(-2, 1, 200)
s_fit_smooth = theis_drawdown(t_smooth, T_fit, S_fit, Q, r)

col1, col2, col3 = st.columns(3)
col1.metric("Fitted Transmissivity (T)", f"{T_fit:.1f} m²/day",
            f"{(T_fit-T_true)/T_true*100:+.1f}% vs. true")
col2.metric("Fitted Storativity (S)", f"{S_fit:.2e}",
            f"{(S_fit-S_true)/S_true*100:+.1f}% vs. true")
col3.metric("Observation wells", "1", f"r = {r:.0f} m")

# ---------------- Type-curve plot ----------------
st.subheader("Type-Curve Match: Observed Drawdown vs. Fitted Theis Curve")
fig, ax = plt.subplots(figsize=(8, 5))
ax.loglog(t, s_obs, "o", label="Synthetic field observations", color="#1f3864")
ax.loglog(t_smooth, s_fit_smooth, "-", label="Fitted Theis curve", color="#c0392b")
ax.set_xlabel("Time since pumping start (days)")
ax.set_ylabel("Drawdown (m)")
ax.set_title("Log-Log Type-Curve Match")
ax.legend()
ax.grid(True, which="both", alpha=0.3)
st.pyplot(fig)

# ---------------- Distance-drawdown plot ----------------
st.subheader("Distance-Drawdown Profile at End of Test")
distances = np.linspace(2, 200, 100)
t_end = t.max()
s_profile_true = theis_drawdown(t_end, T_true, S_true, Q, distances)
s_profile_fit = theis_drawdown(t_end, T_fit, S_fit, Q, distances)

fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.plot(distances, s_profile_true, label="True aquifer response", color="#1f3864")
ax2.plot(distances, s_profile_fit, "--", label="Fitted model", color="#c0392b")
ax2.axvline(r, color="gray", linestyle=":", label=f"Obs. well (r={r:.0f} m)")
ax2.set_xlabel("Distance from pumping well (m)")
ax2.set_ylabel(f"Drawdown at t = {t_end:.1f} days (m)")
ax2.legend()
ax2.grid(alpha=0.3)
st.pyplot(fig2)

# ---------------- Raw data table ----------------
with st.expander("Raw observation data"):
    st.dataframe(pd.DataFrame({"time_days": t, "drawdown_m": s_obs}))

st.caption(
    "Methodology note: this tool uses the Theis (1935) analytical solution for "
    "a confined, homogeneous, isotropic, infinite aquifer. Real field "
    "conditions (leaky/unconfined aquifers, boundaries, partial penetration) "
    "would require the appropriate analytical correction or a full numerical "
    "model (MODFLOW / FEFLOW / HydroGeoSphere) calibrated with PEST."
)