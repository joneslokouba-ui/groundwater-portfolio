"""
streamlit_app_h3.py — H3 Flow Field Engine Dashboard

Interactive visualization of potentiometric surfaces, flow nets, and Darcy
flux for a synthetic (editable) well-head dataset.

See docs/adr-001-flow-field-architecture.md for the homogeneous/isotropic
assumption boundary that governs the flow-net overlay.
"""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from sim.interpolation import idw_interpolate, make_grid
from sim.flow_net import trace_streamline
from sim.darcy_flux import build_velocity_field

st.set_page_config(page_title="H3 — Groundwater Flow Field Engine", layout="wide")

st.title("Groundwater Flow Field Engine")
st.caption(
    "Potentiometric surface, flow net, and Darcy flux — derived from "
    "interpolated well-head observations."
)

# ---------------------------------------------------------------------------
# Sidebar: well data + parameters
# ---------------------------------------------------------------------------
st.sidebar.header("Well Observations")
st.sidebar.caption("Edit the default 5-well synthetic dataset, or use as-is.")

default_wells = {
    "x": [0, 1000, 0, 1000, 500],
    "y": [0, 0, 1000, 1000, 500],
    "h": [100.0, 90.0, 100.0, 90.0, 95.0],
}

n_wells = st.sidebar.number_input("Number of wells", min_value=3, max_value=20,
                                    value=len(default_wells["x"]))

well_x, well_y, well_h = [], [], []
for i in range(n_wells):
    st.sidebar.markdown(f"**Well {i+1}**")
    dx = default_wells["x"][i] if i < len(default_wells["x"]) else 500.0
    dy = default_wells["y"][i] if i < len(default_wells["y"]) else 500.0
    dh = default_wells["h"][i] if i < len(default_wells["h"]) else 95.0
    c1, c2, c3 = st.sidebar.columns(3)
    x_val = c1.number_input(f"x{i}", value=float(dx), key=f"x{i}", label_visibility="collapsed")
    y_val = c2.number_input(f"y{i}", value=float(dy), key=f"y{i}", label_visibility="collapsed")
    h_val = c3.number_input(f"h{i}", value=float(dh), key=f"h{i}", label_visibility="collapsed")
    well_x.append(x_val)
    well_y.append(y_val)
    well_h.append(h_val)

st.sidebar.header("Aquifer Parameters")
K = st.sidebar.slider("Hydraulic conductivity K (m/day)", 0.1, 50.0, 10.0, 0.1)
homogeneous = st.sidebar.checkbox(
    "Homogeneous / isotropic aquifer", value=True,
    help="Flow-net streamlines are only physically valid under this assumption. "
         "See ADR-001."
)

st.sidebar.header("Grid & Display")
grid_n = st.sidebar.slider("Grid resolution", 20, 150, 60)
n_streamlines = st.sidebar.slider("Number of streamlines", 3, 20, 8)
idw_power = st.sidebar.slider("IDW power", 1, 4, 2)

# ---------------------------------------------------------------------------
# Compute
# ---------------------------------------------------------------------------
x_min, x_max = min(well_x) - 100, max(well_x) + 100
y_min, y_max = min(well_y) - 100, max(well_y) + 100

grid_x, grid_y = make_grid(x_min, x_max, y_min, y_max, n=grid_n)
head_grid = idw_interpolate(well_x, well_y, well_h, grid_x, grid_y, power=idw_power)

dx = grid_x[0, 1] - grid_x[0, 0]
dy = grid_y[1, 0] - grid_y[0, 0]
vf = build_velocity_field(head_grid, dx, dy, K=K, x_grid=grid_x, y_grid=grid_y)

if not homogeneous:
    st.warning(
        "Heterogeneous aquifer selected — flow-net streamlines below are "
        "shown as an **approximation only**. True heterogeneous flow nets "
        "require a full 2D PDE solve, which this module does not implement "
        "(see ADR-001). Contours and flux vectors remain valid; streamline "
        "orthogonality does not."
    )

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 8))

# Potentiometric surface
contour = ax.contour(grid_x, grid_y, head_grid, levels=15, cmap="viridis")
ax.clabel(contour, inline=True, fontsize=7, fmt="%.1f")

# Darcy flux quiver (subsampled for clarity)
step = max(grid_n // 15, 1)
ax.quiver(
    grid_x[::step, ::step], grid_y[::step, ::step],
    vf["qx"][::step, ::step], vf["qy"][::step, ::step],
    color="darkorange", alpha=0.7, scale=None, width=0.003,
)

# Streamlines, seeded along the left edge
seed_y = np.linspace(y_min + 50, y_max - 50, n_streamlines)
for sy in seed_y:
    px, py = trace_streamline(vf["qx"], vf["qy"], grid_x, grid_y,
                               start_xy=(x_min + 10, sy), n_steps=300)
    ax.plot(px, py, color="steelblue", linewidth=1.2, alpha=0.8)

# Wells
ax.scatter(well_x, well_y, color="red", zorder=5, s=60, edgecolor="black")
for wx, wy, wh in zip(well_x, well_y, well_h):
    ax.annotate(f"{wh:.1f}", (wx, wy), textcoords="offset points",
                xytext=(6, 6), fontsize=8, color="black")

ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.set_title("Potentiometric Surface + Flow Net + Darcy Flux")
ax.set_aspect("equal")

st.pyplot(fig)

st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("Head range", f"{head_grid.min():.1f} – {head_grid.max():.1f} m")
col2.metric("Mean flux magnitude", f"{vf['magnitude'].mean():.4f} m/day")
col3.metric("Max flux magnitude", f"{vf['magnitude'].max():.4f} m/day")

with st.expander("About this model"):
    st.markdown(
        "- **Equipotentials** (contour lines): interpolated head surface "
        "from well observations (IDW).\n"
        "- **Streamlines** (blue): traced along the Darcy velocity field, "
        "orthogonal to equipotentials under the homogeneous/isotropic "
        "assumption.\n"
        "- **Flux vectors** (orange arrows): q = -K∇h at each grid point.\n\n"
        "This velocity field is the direct input to **H4: Contaminant "
        "Transport Simulator**."
    )