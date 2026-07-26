# Groundwater Modelling Portfolio

A structured, architecture-first portfolio for hydrogeology and groundwater modelling
work — mirroring the same discipline used in the AI/ML engineering portfolio
(ADR → model design → calibration → visualization → case study), adapted for
hydrogeological modelling.

## Structure

- **00-adrs/** — Architecture/Approach Decision Records. One markdown file per project
  documenting *why* a modelling approach, boundary condition, or software choice was made —
  not just what the model shows. This is what makes the portfolio read as engineering
  judgment, not just software output.
- **01-conceptual-models/** — Conceptual hydrogeological models: geology, hydrostratigraphy,
  recharge/discharge zones, before any numerical model is built.
- **02-numerical-models/** — Actual model files and build notes, organized by platform:
  - `feeflow/`
  - `modflow/`
  - `hydrogeosphere/`
- **03-calibration-validation/** — Calibration reports, PEST runs, residual analysis,
  sensitivity analysis, validation against observed heads/flows.
- **04-visualization-dashboards/** — Streamlit (or similar) dashboards that make model
  outputs interactive: head contours, drawdown over time, particle tracking, water
  balance charts. This is the differentiator most groundwater modellers don't build —
  worth featuring prominently.
- **05-case-studies/** — Full narrative write-ups per project: problem, approach, result,
  what a client or regulator needed to see. These are the pieces you'd actually link in
  a resume or cover letter.
- **06-reports-templates/** — Reusable report structures (calibration report template,
  model documentation template) so each new project starts from a consistent format.

## Mini Project #1: Aquifer Pumping Test Analysis (ready to deploy)

A working Theis-solution pumping test analysis tool, following the
same architecture-first pattern as the AI/ML portfolio:

- `00-adrs/001-theis-solution-vs-proprietary-software.md` — why analytical, not numerical, for this piece
- `03-calibration-validation/theis_solution.py` — core solution + curve-fitting calibration (tested, recovers true T/S within ~1-5%)
- `04-visualization-dashboards/streamlit_app.py` — interactive dashboard
- `05-case-studies/case-study-01-pumping-test-analysis.md` — full write-up

**To deploy on Streamlit Cloud (same pattern as Modules 1-8):**
1. Move/copy `requirements.txt` to the repo root (Streamlit Cloud needs it there, per your established practice).
2. Add `sim/__init__.py` if you restructure this into a `sim/` package, per your standing convention.
3. Point Streamlit Cloud's entry file at `04-visualization-dashboards/streamlit_app.py`.
4. Use all-hyphens in any new ADR filenames, per your standing convention.

Run locally first with: `streamlit run 04-visualization-dashboards/streamlit_app.py`

## Notes

- Populate each software-specific numerical-models folder only with what you have
  genuine hands-on project history for — don't backfill software you haven't
  actually used on a real project.
- If a refresher is needed on any platform before publishing a case study, note that
  honestly in the ADR rather than presenting rusty familiarity as current fluency.