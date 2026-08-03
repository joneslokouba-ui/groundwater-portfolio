"""
H5: Integrated Groundwater Modelling Toolchain
------------------------------------------------
Workflow proficiency showcase covering Leapfrog, FEFLOW, HydroGeoSphere,
Visual MODFLOW Flex + PEST, and Surfer, connected by a Python/Streamlit
automation layer.

Structure (see docs/adr-h5-integrated-toolchain.md):
  Tab 1 - Thread 1: Predictive / Design case study (static content)
  Tab 2 - Thread 2: Site Characterization / Remediation case study (static content)
  Tab 3 - Toolchain cheat sheet (static reference table)
  Tab 4 - Interactive demo: IDW-based "Surfer-style" contouring + PEST-style
          residual summary, built on synthetic or uploaded monitoring data

NOTE ON REUSE: The IDW interpolation routine below is a self-contained
version for portability. When this file is placed in the actual repo
alongside H3-flow-field-engine, replace `idw_interpolate()` with an import
from `H3-flow-field-engine/sim/interpolation.py` to keep the codebase DRY,
per ADR-H5.
"""

import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="H5: Integrated Toolchain", page_icon="🧰", layout="wide")

# ----------------------------------------------------------------------------
# Shared: IDW interpolation (placeholder for H3's sim/interpolation.py import)
# ----------------------------------------------------------------------------


def idw_interpolate(x, y, z, grid_x, grid_y, power=2, eps=1e-9):
    """Inverse-distance-weighted interpolation onto a regular grid.

    x, y, z: 1D arrays of sample point coordinates and values
    grid_x, grid_y: 2D meshgrid arrays to interpolate onto
    """
    gx = grid_x.ravel()
    gy = grid_y.ravel()
    zi = np.zeros_like(gx, dtype=float)

    for i in range(len(gx)):
        dist = np.sqrt((x - gx[i]) ** 2 + (y - gy[i]) ** 2)
        if np.any(dist < eps):
            zi[i] = z[np.argmin(dist)]
        else:
            weights = 1.0 / (dist**power)
            zi[i] = np.sum(weights * z) / np.sum(weights)

    return zi.reshape(grid_x.shape)


# ----------------------------------------------------------------------------
# Synthetic sample data (used if no CSV is uploaded)
# ----------------------------------------------------------------------------


def make_synthetic_monitoring_data(n_wells=12, seed=42):
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 500, n_wells)
    y = rng.uniform(0, 500, n_wells)

    # Synthetic plume: concentration decays from a source near (150, 300)
    source_x, source_y = 150, 300
    dist_from_source = np.sqrt((x - source_x) ** 2 + (y - source_y) ** 2)
    concentration_baseline = 800 * np.exp(-dist_from_source / 120) + rng.normal(0, 15, n_wells)
    concentration_baseline = np.clip(concentration_baseline, 0, None)

    dates = pd.date_range("2023-01-01", periods=6, freq="QE")
    rows = []
    for well_id in range(n_wells):
        for t_idx, date in enumerate(dates):
            attenuation = np.exp(-0.15 * t_idx)  # gradual plume shrinkage
            conc = concentration_baseline[well_id] * attenuation + rng.normal(0, 5)
            rows.append(
                {
                    "well_id": f"MW-{well_id + 1:02d}",
                    "x": x[well_id],
                    "y": y[well_id],
                    "date": date,
                    "concentration_ppb": max(0, conc),
                }
            )
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# Page header
# ----------------------------------------------------------------------------

st.title("🧰 H5: Integrated Groundwater Modelling Toolchain")
st.caption(
    "Workflow proficiency across Leapfrog, FEFLOW, HydroGeoSphere, "
    "Visual MODFLOW Flex + PEST, and Surfer — connected by a Python automation layer."
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🛢️ Thread 1: Predictive/Design",
        "🧪 Thread 2: Remediation",
        "📋 Toolchain Cheat Sheet",
        "📈 Interactive Demo",
    ]
)

# ----------------------------------------------------------------------------
# TAB 1 — Predictive / Design case study
# ----------------------------------------------------------------------------
with tab1:
    st.header("Thread 1 — Predictive / Design Modelling")

    st.markdown(
        """
    **Context:** SAGD water balance modelling and monitoring at Grizzly Oilsands,
    tracking groundwater usage and recharge contributions from nearby surface water
    bodies (lakes, swamps).

    This thread follows a design-stage workflow: build a geological model, simulate
    flow and transport against it, then calibrate the model against observed field data.
    """
    )

    st.subheader("Workflow")
    st.markdown(
        """
    1. **Leapfrog** — 3D geological/hydrostratigraphic model built from borehole and
       geophysical data. Implicit modelling handles complex, sparse-data geology better
       than explicit surface-fitting approaches.
    2. **FEFLOW / HydroGeoSphere** — numerical saturated/unsaturated flow (and
       surface-water coupling, where relevant) simulation run against the Leapfrog model.
    3. **Visual MODFLOW Flex + PEST** — model calibration against observed heads/flows,
       with PEST providing automated parameter estimation and uncertainty quantification.
    """
    )

    with st.expander("Real project anchor — SAGD water balance, Grizzly Oilsands"):
        st.markdown(
            """
        - **Project type:** SAGD water balance monitoring
        - **Your role:** Led water balance modelling and reporting
        - **Key outcome:** Monitored groundwater usage and recharge contributions from
          nearby surface water bodies (lakes, swamps), informing site water management
          decisions
        """
        )

    st.info(
        "Figures for this thread are illustrative/reconstructed unless real project "
        "outputs are confirmed as shareable (non-confidential)."
    )

# ----------------------------------------------------------------------------
# TAB 2 — Site Characterization / Remediation case study
# ----------------------------------------------------------------------------
with tab2:
    st.header("Thread 2 — Site Characterization / Remediation")

    st.markdown(
        """
    **Context:** Chlorinated solvent (trichloroethylene) plume delineation and
    remediation performance tracking as Project Contaminant Hydrogeologist at
    Conestoga-Rovers & Associates (CRA), evaluating and comparing two in-situ
    remediation technologies.
    """
    )

    st.subheader("Workflow")
    st.markdown(
        """
    1. **Monitoring well network** — groundwater sampling data (concentration, water
       levels) collected over multiple sampling events.
    2. **Surfer** — contouring of dissolved-phase concentration isopleths; plume
       delineation; pre/post-remediation comparison maps.
    3. **Remediation performance tracking** — visualizing plume shrinkage/attenuation
       trends over time, supporting regulatory reporting for in-situ permanganate
       oxidation projects.
    """
    )

    with st.expander("Real project anchor — chlorinated solvent remediation (CRA)"):
        st.markdown(
            """
        - **Project type:** Trichloroethylene (TCE) plume remediation — comparative
          evaluation of two in-situ technologies
        - **Your role:** Project Contaminant Hydrogeologist. Monitored the influence of,
          and evaluated, in-situ potassium permanganate oxidation to degrade chlorinated
          solvents; also monitored and compared granular iron as a second treatment
        - **Key outcome:**
            - **Potassium permanganate:** 87% plume reduction over ~5 months — most
              effective at the deeper source of contamination
            - **Granular iron:** 53% plume reduction over ~8 months — most effective at
              the shallow source of contamination
        """
        )

    st.info(
        "The Interactive Demo tab (Tab 4) reproduces the *style* of Surfer's isopleth "
        "contouring in Python for automation purposes — it is not a Surfer output."
    )

# ----------------------------------------------------------------------------
# TAB 3 — Toolchain cheat sheet
# ----------------------------------------------------------------------------
with tab3:
    st.header("Toolchain Cheat Sheet")
    st.caption("Interview-ready reference — confirm/edit the 'Real Project Anchor' column.")

    cheat_sheet = pd.DataFrame(
        [
            {
                "Tool": "Leapfrog",
                "Core Use": "3D geological/hydrostratigraphic modelling",
                "When You'd Choose It": "Complex geology, sparse borehole data, implicit modelling needed",
                "Real Project Anchor": "SAGD water balance, Grizzly Oilsands",
            },
            {
                "Tool": "FEFLOW",
                "Core Use": "Saturated/unsaturated flow & transport (finite element)",
                "When You'd Choose It": "Complex geometry, variable-density or thermal problems",
                "Real Project Anchor": "SAGD water balance, Grizzly Oilsands",
            },
            {
                "Tool": "HydroGeoSphere",
                "Core Use": "Fully-integrated surface-subsurface flow",
                "When You'd Choose It": "Surface water/groundwater interaction is significant",
                "Real Project Anchor": "SAGD recharge from adjacent lakes/swamps, Grizzly Oilsands",
            },
            {
                "Tool": "Visual MODFLOW Flex",
                "Core Use": "Finite-difference flow modelling, industry-standard GUI",
                "When You'd Choose It": "Regulatory-familiar deliverable, MODFLOW family required",
                "Real Project Anchor": "SAGD water balance, Grizzly Oilsands",
            },
            {
                "Tool": "PEST",
                "Core Use": "Automated calibration / parameter estimation",
                "When You'd Choose It": "Any model needing defensible calibration & uncertainty",
                "Real Project Anchor": "SAGD water balance calibration, Grizzly Oilsands",
            },
            {
                "Tool": "Surfer",
                "Core Use": "2D contouring / gridding",
                "When You'd Choose It": "Plume delineation, concentration isopleths, presentation maps",
                "Real Project Anchor": "TCE plume delineation, potassium permanganate vs. granular iron (CRA)",
            },
            {
                "Tool": "Python / Streamlit",
                "Core Use": "Automation, QA/QC, dashboarding",
                "When You'd Choose It": "Repetitive processing, making static outputs explorable",
                "Real Project Anchor": "Connective layer across all of the above",
            },
        ]
    )

    st.dataframe(cheat_sheet, use_container_width=True, hide_index=True)

    st.download_button(
        "Download cheat sheet as CSV",
        cheat_sheet.to_csv(index=False).encode("utf-8"),
        file_name="h5_toolchain_cheat_sheet.csv",
        mime="text/csv",
    )

# ----------------------------------------------------------------------------
# TAB 4 — Interactive demo
# ----------------------------------------------------------------------------
with tab4:
    st.header("Interactive Demo: Monitoring Data → Contour + Trend Automation")
    st.caption(
        "Reuses H3's IDW interpolation approach to auto-generate a 'Surfer-style' "
        "isopleth map and trend plots from monitoring well data."
    )

    data_source = st.radio(
        "Data source", ["Use synthetic sample data", "Upload monitoring well CSV"], horizontal=True
    )

    if data_source == "Upload monitoring well CSV":
        st.caption("Expected columns: well_id, x, y, date, concentration_ppb")
        uploaded = st.file_uploader("Upload CSV", type="csv")
        if uploaded is not None:
            df = pd.read_csv(uploaded, parse_dates=["date"])
        else:
            st.warning("No file uploaded yet — showing synthetic data below.")
            df = make_synthetic_monitoring_data()
    else:
        df = make_synthetic_monitoring_data()

    st.subheader("Monitoring data")
    st.dataframe(df, use_container_width=True, height=200)

    dates_available = sorted(df["date"].unique())
    selected_date = st.select_slider(
        "Sampling event",
        options=dates_available,
        value=dates_available[-1],
        format_func=lambda d: pd.Timestamp(d).strftime("%Y-%m-%d"),
    )

    snapshot = df[df["date"] == selected_date].copy()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Isopleth map (IDW contour, Surfer-style)")
        x = snapshot["x"].to_numpy()
        y = snapshot["y"].to_numpy()
        z = snapshot["concentration_ppb"].to_numpy()

        grid_res = 80
        gx, gy = np.meshgrid(
            np.linspace(x.min() - 20, x.max() + 20, grid_res),
            np.linspace(y.min() - 20, y.max() + 20, grid_res),
        )
        gz = idw_interpolate(x, y, z, gx, gy, power=2)

        fig, ax = plt.subplots(figsize=(6, 5))
        contour = ax.contourf(gx, gy, gz, levels=15, cmap="YlOrRd")
        ax.scatter(x, y, c="black", s=25, zorder=5, label="Monitoring wells")
        for _, row in snapshot.iterrows():
            ax.annotate(row["well_id"], (row["x"], row["y"]), fontsize=7, xytext=(3, 3), textcoords="offset points")
        fig.colorbar(contour, ax=ax, label="Concentration (ppb)")
        ax.set_xlabel("Easting (m)")
        ax.set_ylabel("Northing (m)")
        ax.set_title(f"Concentration isopleths — {pd.Timestamp(selected_date).strftime('%Y-%m-%d')}")
        ax.legend(loc="upper right", fontsize=8)
        st.pyplot(fig)

        st.caption(
            "Illustrative reproduction of Surfer-style contouring — not a Surfer output. "
            "IDW power = 2."
        )

    with col2:
        st.subheader("Concentration trend by well")
        pivot = df.pivot_table(index="date", columns="well_id", values="concentration_ppb")

        fig2, ax2 = plt.subplots(figsize=(6, 5))
        pivot.plot(ax=ax2, marker="o", legend=False)
        ax2.set_xlabel("Sampling event")
        ax2.set_ylabel("Concentration (ppb)")
        ax2.set_title("Attenuation trend across all wells")
        st.pyplot(fig2)

        overall_reduction = (
            1 - pivot.iloc[-1].mean() / pivot.iloc[0].mean()
        ) * 100 if pivot.iloc[0].mean() > 0 else 0
        st.metric("Mean concentration reduction (first → latest event)", f"{overall_reduction:.1f}%")

        st.caption(
            "**Real-world benchmark (CRA, TCE remediation):** potassium permanganate "
            "achieved 87% plume reduction in ~5 months at a deeper contaminant source; "
            "granular iron achieved 53% reduction in ~8 months at a shallow source. "
            "This synthetic dataset is illustrative of the trend-tracking workflow only."
        )

    st.divider()

    st.subheader("PEST-style residual summary (synthetic)")
    st.caption(
        "Illustrative PEST-style calibration residual summary. In a real workflow this "
        "would ingest PEST's .rei/.res output files rather than synthetic data."
    )

    rng = np.random.default_rng(7)
    n_obs = 20
    observed = rng.normal(50, 10, n_obs)
    simulated = observed + rng.normal(0, 2.5, n_obs)
    residuals = observed - simulated

    resid_df = pd.DataFrame(
        {
            "observation_id": [f"OBS-{i+1:02d}" for i in range(n_obs)],
            "observed": observed,
            "simulated": simulated,
            "residual": residuals,
        }
    )

    rcol1, rcol2 = st.columns([1, 1])
    with rcol1:
        fig3, ax3 = plt.subplots(figsize=(5, 4))
        ax3.scatter(resid_df["observed"], resid_df["simulated"], alpha=0.7)
        lims = [resid_df[["observed", "simulated"]].min().min(), resid_df[["observed", "simulated"]].max().max()]
        ax3.plot(lims, lims, "k--", linewidth=1, label="1:1 line")
        ax3.set_xlabel("Observed")
        ax3.set_ylabel("Simulated")
        ax3.set_title("Observed vs. simulated (synthetic)")
        ax3.legend()
        st.pyplot(fig3)

    with rcol2:
        st.dataframe(resid_df.style.format({"observed": "{:.2f}", "simulated": "{:.2f}", "residual": "{:.2f}"}), height=350)

    rmse = float(np.sqrt(np.mean(residuals**2)))
    st.metric("RMSE (synthetic)", f"{rmse:.2f}")