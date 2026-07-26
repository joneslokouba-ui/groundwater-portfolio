# ADR-001: Analytical (Theis) Solution vs. Proprietary Numerical Software

## Context
This portfolio needs a hydrogeology mini-project that is (a) technically
credible to a hiring manager who knows FEFLOW/MODFLOW/HydroGeoSphere,
(b) fully reproducible without a paid software license, and (c) shareable
publicly (e.g., on Streamlit Cloud, GitHub) without licensing restrictions.

## Decision
Use the Theis (1935) analytical solution for transient radial flow to a
well in a confined aquifer, implemented in Python (NumPy/SciPy), rather
than building a MODFLOW/FEFLOW numerical model for this particular
demonstration piece.

## Alternatives Considered
- **MODFLOW via FloPy**: open-source Python interface to MODFLOW 6.
  Rejected for *this* piece only because it requires downloading and
  managing a compiled MODFLOW executable, adding a deployment dependency
  that complicates a lightweight, publicly-shareable Streamlit app. This
  remains the right choice for a *numerical* case study in this same
  portfolio (see `02-numerical-models/modflow/`).
- **Proprietary FEFLOW/HydroGeoSphere outputs**: not usable in a public
  portfolio piece due to licensing — these remain described qualitatively
  in project case studies rather than reproduced as live code.

## Consequences
- This project demonstrates the same core competency proprietary software
  automates — parameter estimation from field drawdown data — using
  transparent, auditable, open-source math.
- The inverse-problem method here (`scipy.optimize.curve_fit`) is the same
  *class* of nonlinear least-squares calibration PEST performs for full
  numerical models, just applied analytically to a single-well test
  instead of a gridded numerical domain.
- Limitation to disclose honestly in interviews: this is a simplified,
  ideal-aquifer case (confined, homogeneous, isotropic, infinite extent).
  Real projects typically require boundary corrections, leaky/unconfined
  aquifer variants, or a full numerical model — this piece demonstrates
  the underlying calibration methodology, not a substitute for full
  numerical modelling experience.