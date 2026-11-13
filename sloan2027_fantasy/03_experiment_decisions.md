# 03 — Experiment decisions: kept, reused, repaired, new

**Principle (master prompt §F3).** Reproduce and clarify the existing six-target evidence rather than re-running the 2015–2025 pipeline because of the fantasy framing. Fantasy analysis is additive and separate, and its protocol was written before fitting.

## Kept and reused as-is
These were re-verified on 2026-11-13. Each item lists its evidence status.

| Experiment | Source (`research/sloan-2027` @ `04fddeb`) | Why kept | Evidence status |
|---|---|---|---|
| Canonical 208 evaluations, original verdicts | `artifacts/admission_*` (commit `17da742`) | Historical record. Reproduced exactly (55/55 checks). | Reproduced original analysis |
| E1 nested chronological admission + outer predictions (19 model variants, identical rows) | `results/nested/*` | Removes selection on evaluation years. Main evidence for the six targets. | Stronger nested evidence |
| E1 inner-2017 sensitivity | `results/nested/*_inner2017*` | Checks sensitivity to the inner-fold start | Sensitivity |
| E2 frozen-in-workflow 2026 check | `results/holdout2026/*` | Out-of-period check; frozen before download | 2026 exploratory (directional) |
| E3 leakage audit + regression tests | `audits/leakage_audit*`; `tests/test_temporal_leakage.py` | Guards against future data | Reproduced (tests pass) |
| E4-A ridge-selected sets in tuned ridge, elastic net, LightGBM, random forest | within E1 | Model dependence of the lift | Stronger nested evidence |
| E5/E6 comparators, gate ablations, thresholds, admission α | `results/gates/*` | Which gates change error vs labels | Sensitivity |
| E7 multiplicity (208 cluster bootstraps, BH, Holm) | `results/multiplicity/*` | Exploratory error-rate context | Exploratory relative to prior exposure |
| E8 eligibility, prospective-cohort and strata variants | `results/robustness/*` | Population sensitivity | Sensitivity |
| E9 alternative targets (transfer of selections) | `e8_e9_e11.py` | Labeled **transfer only**; superseded for generalization by FB-G | Sensitivity only |
| E10 placebo features (0/900 admitted) | `results/placebo/*` | Negative control | Reproduced control |
| E11/E12 player cohorts, cases, unit translation | `results/players/*` | Phil's baseball-unit and player-story request | Reproduced; cases curated for the app |

## Repaired or relabeled (no numbers changed)
- "Prospective t-only cohort" is renamed **outcome-observed returners** (M2).
- "Only two gates work" now reads: **only the materiality threshold and family step materially changed out-of-time error; other gates can change labels** (M6).
- **Diagnostic / Context** are described as human-specified labels applied after a statistical test (M4).
- Single-feature contrasts on outer years 2021–2025 are labeled "outer years 2021–2025 (single-feature)", not "nested". The metric was fixed in advance, not selected inside the window.

## Not run, or skipped (stated in the paper)
- **E4-B:** re-running admission inside each non-linear estimator. Skipped for time; the paper makes no estimator-general selection claim.
- **Level 4: 2027 fantasy forecasts.** These would need 2026 Statcast feature panels, which were not built. No 2027 leaderboard is published.
- **Archived third-party projections** (Steamer, ZiPS, ATC, THE BAT X) as baselines. They are not in the study data, and FanGraphs terms restrict scraping. The fantasy baseline is the study's own direct model.
- **The author's K%-target study** in the main checkout. It comes from the Phillies trial branch and was excluded per the author's instruction.

## New experiments (this repository)
| ID | Question | Pre-analysis record | Run | Status label |
|---|---|---|---|---|
| FB L0 | What fantasy outcomes and pools exist, and how much attrition is there? | Protocol v1.0, commit `8819791` (pushed before fitting) | 2026-11-13 | Descriptive |
| FB L1 | Are out-of-time target forecasts associated with next-season fantasy categories? | Protocol §7 | 2026-11-13 | Association only |
| FB L2 | Do the target forecasts add out-of-time information beyond a direct fantasy baseline? 8 primary linkages (Holm) plus the full matrix (BH). | Protocol §5–§7 | 2026-11-13 | Exploratory fantasy linkage. 2021–2025 primary; 2026 exploratory. |
| FB L3 | Do they change an illustrative top-k draft policy? | Protocol §6 | 2026-11-13 | Illustrative what-if backtest |
| FB-G | Can the procedure select features for a new target (next-season ERA), and does that beat reusing FIP's selections? | Protocol Amendment 1, commit `b482448` (pushed before running) | 2026-11-13 | New-target generalization check (nested 2021–2025) |

**Time budget.** Every new model fit runs in minutes on an 11-core M3 Pro:
- upstream forecasts: 3 s;
- fantasy bridge: 2 min 19 s;
- draft backtest: 17 s;
- ERA admission: a few minutes.

**Integrity checks:**
- Upstream test-row forecasts reproduce the E1 and frozen-2026 predictions (max |diff| ≤ 1.8×10⁻¹⁵).
- 8 fantasy-bridge tests pass, including "future outcomes cannot change forecasts".

## What counts as confirmatory
Nothing in this revision is confirmatory in the strict sense:
- the 2015–2025 seasons were analysed before;
- 2026 was inspected on 2026-11-12.

The fantasy bridge is the cleanest new evidence. Its fantasy outcomes had never been modeled in this project, and its protocol was publicly time-stamped before fitting. It is still labeled exploratory.
