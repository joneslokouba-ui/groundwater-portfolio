# Case Study: Aquifer Pumping Test Analysis & Type-Curve Fitting

## Problem
Given time-drawdown data from a single observation well during a
constant-rate pumping test, estimate the aquifer's transmissivity (T)
and storativity (S) — the two properties that govern how groundwater
flows toward a well and how far its influence extends. This is the
foundational inverse problem behind every aquifer characterization,
mine dewatering assessment, and water-supply permitting study.

## Approach
1. Implemented the Theis (1935) analytical solution for transient radial
   flow to a fully-penetrating well in a confined, homogeneous, isotropic
   aquifer (see ADR-001 for why analytical over numerical for this piece).
2. Generated synthetic field data by simulating a "true" aquifer with
   known T and S, then adding realistic measurement noise — the same
   validation approach used before trusting a calibration method on
   real field data.
3. Estimated T and S from the noisy data via nonlinear least-squares
   curve fitting (`scipy.optimize.curve_fit`) against the Theis solution.
4. Built an interactive Streamlit dashboard so a reviewer can vary
   pumping rate, observation distance, true aquifer properties, and
   noise level, and immediately see how well the calibration recovers
   the true parameters — a live demonstration of calibration robustness
   under different field conditions.

## Result
Under typical field-realistic noise levels (2 cm measurement noise),
the fitted parameters recover the true transmissivity and storativity
to within roughly 1-5%, matching what would be an acceptable
calibration fit in a real aquifer test report.

## What a Client or Regulator Would Need to See
- Log-log type-curve match (observed vs. fitted) — the standard visual
  QA check for pumping test analysis.
- Distance-drawdown profile — used to predict impacts at other
  locations (e.g., nearby wells, dewatering radius of influence).
- Explicit statement of the aquifer assumptions (confined, homogeneous,
  isotropic, infinite extent) and their limitations — the same
  disclosure a calibration report would include before regulatory
  submission.

## Honest Scope Note
This is a single-well analytical demonstration, not a full 3D numerical
model. It demonstrates the calibration methodology and Python/dashboard
skills directly relevant to modern hydrogeology practice, alongside —
not as a replacement for — hands-on FEFLOW/MODFLOW/HydroGeoSphere
project experience.