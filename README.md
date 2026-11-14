# Fantasy Projection Lab — MIT Sloan SSAC 2027, Baseball track (Paper ID 18)

**One Metric, Different Jobs: Target-Specific Feature Admission for Major League Baseball Player Projection**, revised for the full-paper stage with a fantasy-baseball application.

The paper asks which public baseball metrics deserve to change a next-season forecast, and for which target. The same statistic can do different jobs: sprint speed improves baserunning forecasts and adds nothing to wOBA. The revision also tests whether forecasts of the study's six targets carry information about real fantasy categories.

This repository extends the original study in [Projection-Signal-Lab](https://github.com/shirinalapati/Projection-Signal-Lab). That repository, and its research companion site, are unchanged.

## What is here
| Path | Contents |
|---|---|
| `sloan2027_fantasy/paper/` | Revised manuscript: blind DOCX in the official SSAC template, a 28-page proof PDF, the builder scripts, a claims-to-evidence log (every printed value with its source), verified references, metric definitions, and an original-versus-revised claims table |
| `sloan2027_fantasy/fantasy/` | The fantasy bridge. It contains: the protocol (pushed before any fantasy model was fit); scoring conventions and projection-system research (55 dated sources); the practice audit and hypotheses; all results (`results_by_target_category.csv`, `by_year.csv`, `paired_uncertainty.csv`, `level1_correlations.csv`, `ranking_value_sensitivity.csv`); the ERA generalization check; a summary and negative findings |
| `sloan2027_fantasy/experiments/` | `fb01`–`fb05`, `fbg_era_admission.py`, `export_app_data.py` |
| `sloan2027_fantasy/figures/` | Figures 1–7 (PNG/PDF/SVG) with the data behind each |
| `sloan2027_fantasy/tests/` | Leakage, ratio-category and result-integrity tests |
| `sloan2027_fantasy/00_…04_*.md` | Inventory and preservation; Meredith Wills / Phil Birnbaum feedback crosswalk; referee issue tracker; experiment decisions; manuscript plan |
| `sloan2027_fantasy/FINAL_REPORT.md`, `REVIEWER_PACKET.md` | Status report and a short packet for reviewers |
| `app/` | **Fantasy Projection Lab** web app (Vite + React + TypeScript). Static and evidence-first, built from the audited JSON in `app/public/data/` |
| `vercel.json` | Zero-configuration Vercel deployment of `app/` (not deployed) |

## Main results (details, intervals and caveats in the paper)
- **The original study reproduces exactly:** 55 of 55 checks, re-run 2026-11-13.
- **Nested selection lift:** with the selection repeated inside each training window, admitted metrics lowered out-of-time RMSE against a history-only baseline for 5 of 6 targets (1.0–7.5%). Hitter WAR was the exception.
- **Selective versus broad models depends on the comparison:**
  - selective beats an all-metric ridge model for wOBA and FIP;
  - it ties a tuned elastic net;
  - it loses for both WAR targets;
  - it lost for FIP in the 2026 check, which was frozen in the workflow.
- **Fantasy bridge (exploratory):**
  - the FIP forecast improves ERA and WHIP forecasts by about 1% beyond category history;
  - wOBA, baserunning, fielding and WAR forecasts show no multiplicity-robust gain for their pre-specified categories;
  - raw sprint speed helps stolen-base forecasts, and Barrel% and xwOBA help home-run forecasts;
  - in an illustrative draft backtest, the picks were not detectably better.
- **ERA (new target):** the procedure selects a sensible metric set, but re-selecting for ERA adds nothing beyond reusing FIP's selections.

## Reproduce
See [REPRODUCING.md](REPRODUCING.md). The research code needs a local Projection-Signal-Lab checkout with rebuilt data panels (`PSL_ROOT`). MLB Advanced Media and Sports Reference data are not redistributed.

## Run the app
```bash
cd app && npm ci && npm run dev      # local development
npm test && npm run build            # unit/integration tests, data validation, production build
```
See `app/README.md` for end-to-end tests and the Vercel steps. The app has **not** been deployed.

## Status
- Nothing has been submitted to the conference.
- Nothing has been emailed.
- The app has not been deployed.
- The submission (Google form, Paper ID 18) is due **December 1, 2026, 8:59 p.m. Pacific**, and requires the author's sign-in.

## Data and rights
- Raw tables and player-season panels from MLB Advanced Media (Baseball Savant, MLB Stats API) and Sports Reference (Baseball-Reference) are **not** included. Their terms restrict redistribution, and Sports Reference asks for written permission for automated access.
- The repository includes:
  - code that rebuilds every dataset;
  - SHA-256 manifests;
  - aggregate results;
  - a curated set of player examples (the study's own forecasts plus public season outcomes) used in the paper and app.
