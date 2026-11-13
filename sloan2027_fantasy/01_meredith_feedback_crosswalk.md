# 01 — Meredith Wills and Phil Birnbaum feedback crosswalk

**Sources.** Master prompt §C summarizes the 2026-11-12 meeting and Meredith's margin comments; §C3 summarizes Phil Birnbaum's feedback. No transcript or screenshot file was found on disk, so nothing is attributed beyond those summaries. Phil said he is not qualified to judge the technical details (author's pre-meeting brief), so nothing here implies he endorsed the methods.

Section numbers refer to the revised manuscript `paper/sloan_2027_fantasy_revised.docx`.

## Meredith: what to keep
| Comment | Where it is honoured |
|---|---|
| "Solid methodology… the key will be the writing itself, along with visualizations." | Methods kept unchanged (§5). Seven evidence figures, each tied to a claim (Figs 1–7). The paper is rewritten from the evidence up; it is not an edit of the prior draft. |
| Keep the 2015–2025 study and the six targets ("the prediction targets themselves are great"). | Same six targets, definitions, denominators and eligibility (§2, Table 1). No target dropped or replaced. Fantasy categories are added downstream (§8), not substituted. |
| "All fantasy is doing is creating context." | Fantasy is the application frame (§1, §3) and a separate downstream test (§8). The core admission results (§6) are unchanged in method. |
| A real web app matters for a normal fan. | New app (`app/`), separate from the original companion: metric→target explorer, fantasy linkage explorer, casebook, model comparison, illustrative value lab, methods page. |

## Meredith: requirements (C2 1–12)
| # | Requirement | Paper | Experiment / data | Figure / table | App |
|---|---|---|---|---|---|
| 1 | Define "unstable" operationally. | §5.4 "Four things called unstable": feature reliability r (reported, never gates); lift consistency (share of folds, gates); coefficient drift (sign changes, gates); interval uncertainty. Each has units, measurement, an example, and whether it gates. | `artifacts/admission_*` columns `reliability_pearson`, `folds_improved`, `coef_sign_changes`, CIs | Table 4 (definitions) | Methods page; explorer shows all four for every pair |
| 2 | Remove business-style abstractions. | §1, §5: "diagnostic", "context", "signal", "target-specific", "forecast" defined with baseball examples (Box 1, glossary). "Diagnostic" is stated as a human label. | `engine.decide_verdict` | Box 1 | Verdict-basis line on every card |
| 3 | Graphics critical, not decorative. | Each figure carries one argument: Fig 1 flow, Fig 2 player stories, Fig 3 six-target comparison, Fig 4 classification map, Fig 5 fantasy linkage, Fig 6 draft backtest, Fig 7 year by year. | `figures/make_figures.py` | Figs 1–7 | Same charts, interactive, with table views |
| 4 | Be precise about what the model does. | Results always name the target, comparison, era, population and what the stat cannot see (§6–§8). No "model works" sentences. | — | Captions state population, years, CI | Metadata block on every result |
| 5 | Justify each target. | **§2 "Why These Six Prediction Targets?"**: a six-row table plus a per-target rationale; component vs aggregate logic; defense as boundary; fantasy link plausible vs proven. | Table 1 from `artifacts` + `fantasy/target_category_map.csv` | Table 1 | Methods page; target cards |
| 6 | Research actual fantasy practice. | §3: formats, projection systems, popular metrics, community debates, with sources. Conventional-wisdom audit (Table 2). | `fantasy/research_sources.md`, `practice_audit.csv`, `hypotheses.md`, `scoring_conventions.md`, `projection_systems.md` | Table 2 | Sources page |
| 7 | Front-office limitation. | §1 and §10.4: public single-number metrics are not a substitute for team tracking systems. No claim that teams need these labels. | — | — | Caveat on Methods page |
| 8 | Public-data and dimensionality limits (Barrel%, WAR assumptions, bWAR vs fWAR). | §4.4, §10.5, §11 | `paper/metric_definitions_sources.md` | Table 1 notes | Methods page |
| 9 | Discussion rather than a repetitive conclusion. | §10 Discussion: decisions, alternative explanations, agreement and disagreement with fantasy practice, boundaries, future work. No recap section; one closing paragraph. | — | — | — |
| 10 | Length proportional to the argument. | No 8-page cap. A reviewer-friendly packet for Meredith and Billy (`REVIEWER_PACKET.md`). | — | — | — |
| 11 | 2027 projections vs year-to-year selection. | The research question is which metrics carry next-season information. No 2027 leaderboard. Level 4 is skipped: 2026 feature panels were not built. | protocol §10 | — | App states that no 2027 forecasts are published |
| 12 | Explain wOBA, xwOBA and FIP. | Box 1 and §2: what each measures, its construction, and what it cannot see (verified definitions). | `paper/metric_definitions_sources.md` | Box 1 | Glossary |

Meredith's written comments (paraphrased in the prompt):
- "more specifics": numbers in baseball units throughout;
- "weasel words": §1 rewritten with concrete examples;
- "visualizations will be critical": Figs 1–7;
- "forecasting is non-specific": every claim names the target and season;
- "may need a discussion rather than a recap": §10;
- "single-number metrics are for fans… fantasy… front offices insufficient": §1, §3, §10.4.

## Phil Birnbaum (C3)
| Request | Where |
|---|---|
| Baseball units, not RMSE decimals | §6–§7 state changes in wOBA points, FIP units, runs per 100 times on base. §8 states fantasy effects in HR, SB, ERA and WHIP units. No FIP→ERA→fantasy-points conversion. |
| Named players, both directions | §7 and Fig 2: forecast without and with the metric, the observed value, the error change, and what was known at forecast time. Includes the largest Stuff+ adjustments that **worsened** forecasts (e.g., a low-arm-slot reliever whose low Stuff+ raised his FIP forecast every year while he kept outperforming it). |
| Tell a baseball story | §7: why Stuff+ is tempting, why two-year FIP already carries most of it, and why an unusual delivery breaks a pitch-quality model. Sprint speed: why speed belongs in baserunning forecasts but not in wOBA. |
| K% vs K-BB% | §5.5 and §7.3: K% is admitted for FIP. K-BB% is Diagnostic (redundant given the baseline and K%). FIP itself is built from K, BB and HR, so the distinction is explained. |
| Don't oversell small RMSE changes | Every effect is reported with an interval, the share of players improved and worsened, and per-year values. |
