"""
streamlit_app_h4.py — H4 Contaminant Transport Simulator Dashboard

Animated particle-tracking plume: advection + dispersion + retardation +
decay, driven by live sliders. Designed for immediate visual legibility —
the parameter sliders visibly reshape the plume in real time.

See docs/adr-001-transport-architecture.md for the particle-tracking design
rationale and the known mass-balance limitation.
"""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from sim.flow_field_source import build_velocity_field
from sim.particle_tracker import ParticleTracker
from sim.source_terms import seed_point_source

st.set_page_config(page_title="H4 — Contaminant Transport Simulator", layout="wide")

st.title("Contaminant Transport Simulator")
st.caption(
    "Particle-tracking simulation of advection, dispersion, retardation, "
    "and decay in a groundwater flow field."
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.header("Flow Field")
grad = st.sidebar.slider("Hydraulic gradient", 0.0001, 0.01, 0.001, 0.0001,
                          format="%.4f")
direction = st.sidebar.slider("Flow direction (deg)", 0, 360, 0)
K = st.sidebar.slider("Hydraulic conductivity K (m/day)", 0.1, 50.0, 10.0, 0.1)

st.sidebar.header("Pumping Well (optional)")
use_well = st.sidebar.checkbox("Add pumping well", value=False)
well_x = st.sidebar.slider("Well x", 0, 1000, 700, disabled=not use_well)
well_y = st.sidebar.slider("Well y", 0, 1000, 500, disabled=not use_well)
pumping_rate = st.sidebar.slider("Pumping rate (m3/day)", -500, 500, 200,
                                   disabled=not use_well)

st.sidebar.header("Source")
source_x = st.sidebar.slider("Source x", 0, 1000, 100)
source_y = st.sidebar.slider("Source y", 0, 1000, 500)
n_particles = st.sidebar.slider("Number of particles", 50, 500, 200, 50)

st.sidebar.header("Transport Parameters")
porosity = st.sidebar.slider("Porosity", 0.1, 0.5, 0.3, 0.01)
alpha_l = st.sidebar.slider("Longitudinal dispersivity", 1.0, 50.0, 15.0, 1.0)
alpha_t = st.sidebar.slider("Transverse dispersivity", 0.1, 10.0, 1.5, 0.1)
retardation = st.sidebar.slider("Retardation factor R", 1.0, 10.0, 1.0, 0.1)
decay_rate = st.sidebar.slider("Decay rate (per day)", 0.0, 0.02, 0.0, 0.001,
                                 format="%.3f")

st.sidebar.header("Simulation")
n_steps = st.sidebar.slider("Number of timesteps", 10, 200, 80, 10)
dt = st.sidebar.slider("Timestep (days)", 0.5, 10.0, 2.0, 0.5)

# ---------------------------------------------------------------------------
# Build flow field + run simulation
# ---------------------------------------------------------------------------
vf = build_velocity_field(
    x_min=0, x_max=1000, y_min=0, y_max=1000, n=80,
    gradient_magnitude=grad, direction_deg=direction, K=K,
    well_xy=(well_x, well_y) if use_well else None,
    pumping_rate=pumping_rate if use_well else 0.0,
)

rng = np.random.default_rng(42)
tracker = ParticleTracker(
    vf, porosity=porosity, alpha_l=alpha_l, alpha_t=alpha_t,
    retardation_factor=retardation, decay_rate=decay_rate, rng=rng,
)
x0, y0 = seed_point_source(source_x, source_y, n_particles, jitter=5, rng=rng)
traj = tracker.run(x0, y0, n_steps=n_steps, dt=dt)

# ---------------------------------------------------------------------------
# Time slider + plot
# ---------------------------------------------------------------------------
t_idx = st.slider("Time step", 0, n_steps, n_steps, key="time_slider")

fig, ax = plt.subplots(figsize=(9, 8))

# Flow field background (streamlines via quiver for context)
step = 8
ax.quiver(
    vf["x_grid"][::step, ::step], vf["y_grid"][::step, ::step],
    vf["qx"][::step, ::step], vf["qy"][::step, ::step],
    color="lightsteelblue", alpha=0.6, width=0.002,
)

active = traj["active"][t_idx]
x_t = traj["x"][t_idx][active]
y_t = traj["y"][t_idx][active]

ax.scatter(x_t, y_t, c="crimson", s=12, alpha=0.7, label="Active particles")

if use_well:
    ax.scatter([well_x], [well_y], c="black", marker="^", s=150,
               label="Pumping well", zorder=5)

ax.scatter([source_x], [source_y], c="darkgreen", marker="*", s=200,
           label="Source", zorder=5)

ax.set_xlim(0, 1000)
ax.set_ylim(0, 1000)
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.set_aspect("equal")
ax.legend(loc="upper right")
ax.set_title(f"Plume at t = {t_idx * dt:.1f} days")

st.pyplot(fig)

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
st.divider()
n_survived = active.sum()
col1, col2, col3 = st.columns(3)
col1.metric("Particles remaining", f"{n_survived} / {n_particles}")
col2.metric("Mass fraction remaining", f"{100 * n_survived / n_particles:.1f}%")
if n_survived > 0:
    centroid_x = x_t.mean()
    col3.metric("Plume centroid (x)", f"{centroid_x:.0f} m")
else:
    col3.metric("Plume centroid (x)", "n/a")

with st.expander("About this model"):
    st.markdown(
        "- **Advection**: particles move along the local Darcy velocity, "
        "corrected for retardation.\n"
        "- **Dispersion**: random-walk step scaled to longitudinal/"
        "transverse dispersivity — this is what makes the plume spread.\n"
        "- **Retardation**: sorption slows the contaminant's apparent "
        "velocity relative to the water (R >= 1).\n"
        "- **Decay**: first-order kinetics; each particle has a per-step "
        "survival probability. Try toggling this against R to see how "
        "sorption and degradation interact.\n\n"
        "**Known limitation:** particle tracking trades exact mass-balance "
        "accounting for visual clarity — see ADR-001 for details."
    )