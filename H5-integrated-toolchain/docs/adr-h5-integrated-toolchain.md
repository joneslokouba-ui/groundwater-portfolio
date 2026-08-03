# ADR-H5: Integrated Groundwater Modelling Toolchain

## Status
Proposed

## Context

H1–H4 demonstrate that core hydrogeology numerical methods (Theis analysis, HybridRAG document retrieval, flow-field interpolation, particle-tracking transport) can be built natively in Python and deployed as interactive Streamlit tools. That portfolio proves algorithmic and engineering capability.

It does not, on its own, demonstrate fluency with the licensed, GUI-based industry-standard toolchain that most hydrogeology and mining-water consulting work is actually built on: Leapfrog (geological modelling), FEFLOW and HydroGeoSphere (numerical flow/transport simulation), Visual MODFLOW Flex with PEST (calibration), and Surfer (contouring/plume delineation).

These tools are licensed desktop GUI applications with no public API. They cannot be embedded in a Streamlit app the way H1–H4's algorithms can. PEST is the partial exception: its calibration workflow is script/file-driven and can be meaningfully reproduced in Python.

The risk of omitting this toolchain from the portfolio is that a reviewer or interviewer may read H1–H4 as "the candidate can code, but has never touched the tools our projects actually run on." The risk of trying to fully recreate the licensed GUIs in Python is overclaiming proprietary-software experience the candidate does not have.

## Decision

Add H5 as a **workflow proficiency showcase**, structurally distinct from H1–H4:

1. **Two case-study threads**, each documenting a real project workflow through the relevant tool(s), with per-tool descriptions (what it's for, when to choose it, a real project anchor):
   - **Thread 1 — Predictive/Design**: Leapfrog → FEFLOW/HydroGeoSphere → Visual MODFLOW Flex/PEST, anchored to SAGD/oil-sands water balance or mine dewatering work.
   - **Thread 2 — Site Characterization/Remediation**: monitoring data → Surfer contouring → remediation tracking, anchored to chlorinated-solvent plume delineation and in-situ permanganate oxidation work (Waterloo Hydrogeologic / CRA background).

2. **One genuinely interactive component**: a PEST-style calibration/data-digestion demo built in Python, reusing H3's IDW interpolation logic (`sim/interpolation.py`) rather than duplicating it. This is the only part of H5 that runs live in the browser — everything else is documented case-study content plus a static toolchain cheat-sheet table.

3. **No attempt to simulate Leapfrog, FEFLOW, HydroGeoSphere, Visual MODFLOW Flex, or Surfer output algorithmically.** Where illustrative figures are needed, they are clearly labelled as reconstructed/illustrative, not live tool output.

## Consequences

**Positive:**
- Closes the credibility gap between "can code numerical methods" (H1–H4) and "knows the commercial toolchain a consulting employer actually runs" (H5).
- Cheat-sheet table (Tab 3) is directly reusable as interview prep material, independent of the deployed app.
- Reuses existing H3 interpolation code rather than duplicating logic, keeping the codebase DRY.

**Negative / risks:**
- H5 has less "wow factor" than H1–H4 since most of it is static content, not live simulation. Mitigated by keeping the interactive demo tab genuinely functional rather than decorative.
- Requires the candidate to supply real project details (real project lines, confirm which figures can use real vs. illustrative data) before the module is complete — this is a content dependency, not a code dependency.
- Two-thread structure adds navigation complexity vs. H1–H4's single-purpose pages; mitigated by tab-based layout matching the existing app's navigation pattern.

## Alternatives considered

- **Full simulation of each tool's core algorithm in Python** (e.g. building a mini finite-element solver to stand in for FEFLOW): rejected — this would overstate the depth of the demo relative to actual licensed-software experience, and duplicates effort already covered by H1–H4's from-scratch numerical work.
- **Skipping H5 entirely, relying on CV/cover letter to cover toolchain experience**: rejected — a live portfolio artifact carries more weight in interviews than a CV line, and gives the candidate a structured reference to speak from.