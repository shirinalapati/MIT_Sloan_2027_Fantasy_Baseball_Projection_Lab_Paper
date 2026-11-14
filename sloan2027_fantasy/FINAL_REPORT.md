# FINAL REPORT: Sloan 2027 Paper 18, fantasy revision (prepared 2026-11-13)

Every number below comes from a committed artifact. Intervals are 95% paired player-cluster bootstrap intervals. ΔRMSE is a percentage of the reference model's RMSE, and negative favors the first-named model.

**Status:**
- not submitted;
- not emailed;
- the app is not deployed;
- commits pushed only to the new repository `MIT_Sloan_2027_Fantasy_Baseball_Projection_Lab_Paper`, which the author designated for this work;
- the original Projection-Signal-Lab repository and site are untouched (873/873 baseline files byte-identical).

## 1. Answers to the five required questions
**(a) Why these six outcomes?**
- They cover four components: hitting (wOBA), the pitcher's own run prevention (FIP), baserunning, and fielding.
- They add two aggregates (hitter and pitcher bWAR rates), so the study can ask whether a metric's usefulness depends on the job.
- Defense is the deliberate boundary case: real value that fantasy scoring ignores.
- WAR is the aggregate stress test.
- The targets were chosen before the fantasy framing and are kept unchanged. None is a fantasy category. See manuscript Section 2 and Table 1.

**(b) Which target forecasts add out-of-time fantasy information beyond reasonable baselines?**
- **Robust:** only the FIP forecast. It improves ERA forecasts (−1.17% [−1.77, −0.59], Holm p = 0.008) and WHIP forecasts (−1.30% [−2.02, −0.57]) beyond a fantasy-category history model.
- **Not robust, not detected, or boundary:**
  - wOBA → HR: −1.02% [−2.16, +0.03]; improved in 5 of 5 seasons but not significant;
  - wOBA → AVG: null;
  - baserunning → SB: null;
  - fielding → value: null, as a boundary case should be;
  - hitter WAR → value: −0.46%, not robust to multiplicity;
  - pitcher WAR → value: null.
- **Secondary findings:**
  - raw sprint speed improves SB forecasts (−0.71% [−1.13, −0.27]);
  - Barrel% (−1.62%) and xwOBA (−1.18%) improve HR forecasts;
  - WAR forecasts mostly carry playing time (hitter WAR → AB −1.52%).
- **2026 (exploratory):** directions largely agree, but no primary linkage has an interval excluding zero.
- **Decisions:** rank agreement improves by about 0.02 Spearman, but the picks are not detectably better (illustrative backtest).

**(c) Where do popular fantasy beliefs agree or disagree with the evidence?**
- **Agree:**
  - judge pitchers by FIP-type skill, though only by about 1%;
  - expected stats and Barrel% for home runs;
  - sprint speed for steals;
  - WAR is not fantasy value;
  - defense matters at most through playing time (no signal detected).
- **Qualify or disagree:**
  - "buy low on xwOBA under-performers" is weaker than "sell high on over-performers";
  - Stuff+ adds nothing to K, ERA or WHIP beyond category history, and fails for unusual deliveries;
  - K-BB% is informative but redundant once a model has the history;
  - "more Statcast inputs always help" is false: 0 of 900 placebos were admitted, broad models lose or tie, and most links are null;
  - better skill forecasts did not change the top of an illustrative draft.
- See Table 2 in the manuscript.

**(d) What can the app actually do today?** See Section 6 below. In short: it explores every audited result. It does not run live models or forecast 2027.

**(e) What remains unvalidated and why?**
- **No prospective test.** 2026 was frozen in the workflow but evaluated after the season.
- **Fantasy evidence is exploratory.** The seasons were not new, though the protocol was pushed first.
- **No ADP- or position-aware draft evaluation and no league simulation.** There is no lawful source of archived ADP or projections in the study.
- **No 2027 forecasts.** 2026 feature panels were not built.
- **Admission not re-run inside non-linear models** (E4-B).
- **Rookies excluded.**
- **Role labels are human-specified.**

## 2. Experiments
### Executed
| ID | What | Result |
|---|---|---|
| Phase 1 re-verification | 71 tests; 55 of 55 reproduction checks; 873/873 hashes; leakage audit | All pass (2026-11-13) |
| FB L0 | Forecast-date pools that keep non-returners | 1,845 hitter-seasons and 2,115 pitcher-seasons (2021–25); 2–9% of hitters and 9–14% of pitchers produced nothing the next season |
| FB L1 | Association of target forecasts with fantasy categories | e.g. wOBA forecast ~ HR ρ = 0.64; association only |
| FB L2 | Incremental out-of-time fantasy information | 8 primary (Holm), 140 pooled comparisons; 46 add information, 1 harmful |
| FB L3 | Illustrative draft backtest | Δρ ≈ +0.02; picks not detectably better |
| FB-G | ERA nested admission (protocol amendment 1) | ERA-specific selection −5.1% vs baseline; reusing FIP's selections −5.6%; no difference between them; beats all-metric ridge; ties elastic net |

### Reused from the November reanalysis
All re-verified:
- E1 nested admission;
- E2 frozen 2026 check;
- E3 leakage;
- E4-A (model families);
- E5/E6 gates;
- E7 multiplicity;
- E8–E10 robustness and placebo;
- E11/E12 player analysis.

### Not run
- E4-B (selection inside non-linear models).
- Level 4 (2027 forecasts).
- External projection baselines: archived projections are members-only or terms-restricted.

## 3. Deviations and discovered problems
- **Placement of the points-scoring weights.** The Yahoo weights were transcribed from Yahoo's help page *after* the first fit of the non-points outcomes, but before any points model was run. The protocol fixed the weights to Yahoo's, so this involved no analyst choice.
- **BH adjustment of secondary families.** Adding the points outcomes slightly changed the BH q-values of other secondary rows. The primary family is unchanged.
- **The single harmful comparison** (admitted hitter-WAR forecast for AVG) also recurred in 2026.
- **Earlier reanalysis problems** are documented, not "fixed":
  - selection on evaluation years (≤ 0.53% optimism);
  - FIP selective/kitchen rows differ (1,699 vs 1,866);
  - outcome-observed populations.

## 4. Data rights and provenance (author decisions flagged)
- **Not committed:** raw MLBAM and Sports Reference tables and player-season panels. Rebuild scripts and SHA-256 manifests are provided instead.
- **Curated player examples in the app:** 420 player-seasons (the study's forecasts plus public season outcomes). **Author decision:** keep, shrink, or remove before any public deployment.
- **Sports Reference automated access.** Sports Reference's data-use page asks for written permission for automated access; the WAR files were downloaded programmatically (2026-08-20; 2026-11-12). **Author decision:** seek permission, or describe the rebuild as a manual download.
- **Anonymity.** The repository URL contains the author's username, and a preprint is public. The blind DOCX has no name, affiliation or links. Named copies are local only, and an organizer email draft exists locally (unsent).

## 5. Paper
- `paper/sloan_2027_fantasy_revised.docx` (blind):
  - official template; Cambria;
  - 5 numbered equations, 7 figures, 7 tables, 74 references;
  - schema-valid;
  - 238 logged values in `claims_to_evidence.csv`.
- `paper/sloan_2027_fantasy_revised_proof.pdf`: 28 pages, LibreOffice 26.8.2 with Caladea. **Word itself was not available; the author must check the file in Word.**
- Mandatory section **"Why These Six Prediction Targets?"** is Section 2.
- The **referee self-review** is in `audits/referee_self_review.md`; resolutions are listed in Section 7 below.

## 6. App
See `app/README.md`. Test and build results are recorded at the end of this report once verified.

## 7. Referee self-review resolutions
Pending; appended after the review completes.

## 8. Remaining author decisions before December 1
1. Check the DOCX in Microsoft Word, then read the whole paper.
2. Answer the anonymity, open-data and subtitle questions, optionally by sending the local email draft.
3. Decide the data-rights questions (Sports Reference permission; the curated player casebook).
4. Optionally approve a Vercel deployment of the app.
5. Submit via the form (Paper ID 18) by **Dec 1, 8:59 p.m. Pacific**.
