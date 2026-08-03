# Groundwater Portfolio

A set of applied hydrogeology / groundwater modelling tools, built to
demonstrate the translation of classical hydrogeology methods into
interactive, deployable software — bridging a background in petroleum
geology and groundwater hydrogeology consulting with modern AI/ML
engineering practice.

Each module follows an architecture-first process: an ADR (Architecture
Decision Record) and Mermaid pipeline diagram are written before any code,
the simulation core is validated against known analytical solutions or
synthetic ground-truth data, and only then is the Streamlit dashboard
built on top.

## Modules

| Module | Description | Status |
|---|---|---|
| [H1 — Aquifer Pumping Test Analysis](./H1-aquifer-pumping-test) | Theis analytical solution for transient well-test drawdown analysis | Deployed |
| [H2 — Document Assistant](./H2-document-assistant) | Hybrid vector + keyword RAG assistant over remediation/geochemistry notes (α·VectorSim + (1−α)·KeywordScore) | In progress |
| [H3 — Flow Field Engine](./H3-flow-field-engine) | Potentiometric surfaces, flow nets, and Darcy flux from interpolated well-head observations | Deployed |
| [H4 — Contaminant Transport Simulator](./H4-contaminant-transport) | Particle-tracking advection-dispersion-retardation-decay simulation, riding H3's flow field | Deployed |
| [H5 — Integrated Groundwater Modelling Toolchain](./H5-integrated-toolchain) | Workflow proficiency showcase covering Leapfrog, FEFLOW, HydroGeoSphere, Visual MODFLOW Flex + PEST, and Surfer, connected by a Python/Streamlit automation layer; anchored to real SAGD water balance (Grizzly Oilsands) and TCE remediation (CRA) project work | Deployed |

## Running locally

Each module is self-contained with its own `requirements.txt`:

```bash
cd H3-flow-field-engine
pip install -r requirements.txt
streamlit run streamlit_app_h3.py
```

## Deployment

Each module is deployed independently to Streamlit Cloud. When configuring
a deployment, point the app's **Advanced settings → Python dependencies
file** at the module-specific `requirements.txt` (e.g.
`H3-flow-field-engine/requirements.txt`), not a root-level file.

## Design notes

- Every module's `docs/` folder contains an ADR stating the module's key
  assumptions and known limitations explicitly, rather than leaving them
  implicit.
- Simulation cores are validated against synthetic data with known ground
  truth before any dashboard code is written.
- `sim/__init__.py` is present in modules with a `sim/` package (H2–H4) to
  avoid Streamlit Cloud import path issues. H5 is intentionally
  self-contained in a single app file — see
  `H5-integrated-toolchain/docs/adr-h5-integrated-toolchain.md` for the
  reasoning, since it's a workflow/proficiency showcase rather than a
  from-scratch numerical simulation like H1–H4.