# ADR-001: Groundwater Flow Field Engine Architecture

## Status
Accepted

## Context
Need to map groundwater flow through aquifers using three classic hydrogeology
tools — potentiometric surfaces, flow nets, and Darcy flux vectors — in a way
that is (a) numerically defensible, (b) fast enough for an interactive
Streamlit dashboard, and (c) transparent about its assumptions so it holds up
under technical scrutiny in an interview setting.

## Decision
Build a steady-state 2D flow field from sparse well-head observations via
spatial interpolation, then derive flow nets and Darcy flux directly from the
interpolated head grid using finite-difference gradients.

## Pipeline
1. **Input:** well locations + observed heads (x, y, h)
2. **Interpolation:** IDW (default, fast) with kriging as an optional upgrade
   path (adds uncertainty quantification — kriging variance surface)
3. **Potentiometric surface:** contour the interpolated head grid directly
4. **Flow net:**
   - Equipotentials = head contours (already have these)
   - Streamlines = orthogonal family, derived from the stream function ψ,
     conjugate to head under the Cauchy-Riemann relations
   - Computed via numerical differentiation of the head grid
5. **Darcy flux:** q = -K·∇h, computed cell-by-cell via finite-difference
   gradient of the head grid

## Key Assumption Boundary (explicit, load-bearing)
Streamline orthogonality via the stream-function approach is only strictly
valid under **homogeneous, isotropic** K-field conditions. Under layered or
heterogeneous K, true flow nets require solving the full 2D flow PDE
(∇·(K∇h) = 0) rather than differentiating a stream function.

**v1 scope:** homogeneous/isotropic only, with heterogeneous K-field support
explicitly deferred to a future revision and flagged in the dashboard UI
(toggle disabled or labeled "approximate" for heterogeneous cases). This
mirrors the authority-tier boundary discipline used in Module 8 (Vigil) —
scope limitations are a designed feature, not an oversight.

## Consequences
- Fast, transparent, no black-box PDE solver — every step is inspectable
- Correct for the common textbook case (homogeneous aquifer), which is also
  the case most interview questions target
- Heterogeneous case is a known, documented limitation rather than a silent
  inaccuracy
- H3's velocity field output (q vectors) becomes the direct input to H4
  (contaminant transport) — no re-derivation needed downstream

## Downstream Dependency
H4 (Contaminant Transport Simulator) consumes H3's velocity field as-is.
Any change to H3's grid resolution or coordinate convention must be
coordinated with H4.