# ADR-001: Contaminant Transport Simulator Architecture

## Status
Accepted

## Context
H3 produces a velocity field (Darcy flux) from head observations. Need to
simulate contaminant fate and transport riding that field, covering the
mechanisms that make transport genuinely hard: advection, dispersion,
retardation (sorption), and decay — while producing a result compelling
enough for a live Streamlit dashboard audience that wants to *see* the
physics, not read about it.

## Decision
**Particle tracking (random walk)**, chosen over a grid-based
advection-dispersion-reaction (ADE) finite-difference solver.

## Rationale
1. **Numerical stability** — grid-based ADE solvers are sensitive to
   Peclet/Courant number constraints; particle tracking has no equivalent
   grid-stability tuning requirement.
2. **Direct physical mapping** — each transport mechanism maps to one
   inspectable operation per particle per timestep:
   - Advection: displacement along H3's local velocity vector
   - Dispersion: random-walk step drawn from a distribution scaled to the
     dispersivity coefficient (longitudinal/transverse components separable)
   - Retardation: velocity multiplier (1/R) per particle
   - Decay: per-step survival probability (first-order kinetics), with a
     Monod-kinetics option as a stretch goal tied to H2's bioremediation notes
3. **Dashboard payoff** — a particle swarm visibly spreading, thinning, and
   decaying as it migrates is immediately legible without narration. Sliders
   for dispersivity/retardation/decay reshape the plume live — the
   interaction itself is the explanation.
4. **Portfolio consistency** — keeps H4 in the same "physically transparent,
   no black-box solver" lineage as H1 (Theis) and H3 (finite-difference
   gradients), rather than introducing an opaque matrix solve.

## Known Limitation (deferred, documented)
Particle tracking is noisier for exact mass-balance accounting and requires
sufficient particle counts for stable concentration estimates. A grid-based
mass-balance check is deferred to a v2 revision. Flagged explicitly here
rather than left implicit — same pattern as H3's heterogeneity boundary.

## Pipeline
H3 velocity field → seed particles at source term → per-timestep update
(advect + disperse + retard + decay) → particle positions over time →
Streamlit animated dashboard (time slider, flow-net overlay, live parameter
sliders, homogeneous-vs-layered comparison view)

## Consequences
- No PDE solver dependency; pure numpy vectorized particle updates
- Visual-first design trades some quantitative rigor (mass balance) for
  interpretability and dashboard impact — an explicit, documented trade-off
- Directly extensible to tie decay-rate scenarios to H2's biostimulation/
  bioaugmentation notes (toggle decay rate presets sourced from H2's RAG)