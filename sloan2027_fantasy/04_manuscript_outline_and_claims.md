# 04 — Manuscript outline and claims plan (written after the evidence review, before the final text)

## Title
- **Kept:** "One Metric, Different Jobs: Target-Specific Feature Admission for Major League Baseball Player Projection". This is the accepted title for Paper ID 18.
- **Proposed subtitle, for the author to decide (not applied):** "…, with a Test of What Carries Over to Fantasy Baseball".
  - The fantasy framing is an application context, not a change of the research question.
  - Whether a subtitle is acceptable at the full-paper stage is an organizer question. It is included in the optional email draft.

## Claim hierarchy used throughout (master prompt §I3)
| Tier | Label in the paper | Examples |
|---|---|---|
| A | Historical record (accepted abstract) | the abstract's ΔRMSE values (Appendix A) |
| B | Reproduced original analysis | 402/208/163; 27/110/44/27 verdicts; all published RMSEs (55/55) |
| C | Nested out-of-time evidence (2021–2025) | selected vs baseline for 5 of 6 targets; kitchen-sink comparisons |
| D | 2026 frozen-in-workflow check (exploratory) | FIP reversal; directional replications whose intervals include 0 |
| E | Fantasy link by association only | Level 1 Spearman correlations |
| F | Fantasy link by out-of-time incremental lift | FIP forecast → ERA/WHIP; sprint speed → SB; Barrel% → HR |
| G | Fantasy decision value (illustrative backtest) | rank agreement +0.02; top-k picks not detectably better |
| H | Aspiration / app feature | value-lab calculator; no 2027 forecasts |

## Section plan
1. **Introduction: the fantasy manager's question.**
   - "Describes a player" versus "improves next season's forecast".
   - Public users see dozens of metrics (Statcast leaderboards; FanGraphs, Yahoo and ESPN tools).
   - Contributions (falsifiable, numbered) and non-claims: not a front-office tool, not a new projection system, no 2027 leaderboard.
2. **Why These Six Prediction Targets?** (mandatory standalone section)
   - Table 1, six rows: measure, unit/denominator, why used, hypothesized fantasy link, what it does not establish.
   - Component (4) versus aggregate (2) logic; defense as the boundary case.
   - The targets were chosen before the fantasy framing.
   - bWAR versus fWAR.
   - Box 1: wOBA, xwOBA, FIP, bWAR defined (verified sources).
3. **What fantasy managers already use.**
   - Formats: Yahoo default 5×5 categories; points-league defaults.
   - Projection systems: Steamer, ZiPS, ATC, THE BAT X, Marcel.
   - Popular metrics and debates.
   - Table 2: conventional-wisdom audit (belief → what we test → result).
   - Prior academic work and novelty limits.
4. **Data, populations and timing.**
   - Sources, eligibility, and outcome-observed versus forecast-date pools (attrition table).
   - Rights.
5. **How a metric earns admission.**
   - Equations 1–3 (weighted RMSE, ΔRMSE, gates); Equation 4 (nested windows).
   - Figure 1.
   - Taxonomy with human/statistical basis (Table 3).
   - Four meanings of "unstable" (Table 4).
   - K% versus K-BB%.
6. **Results I: six-target evidence.**
   - Reproduction.
   - Figure 4 classification map.
   - Figure 3 model comparison.
   - Figure 7 year by year.
   - Flagship contrasts (Table 5).
   - Gates and thresholds; placebo; multiplicity.
   - Original versus revised claims.
7. **Results II: player stories in baseball units.**
   - Figure 2 (Rogers, Wheeler; deciles).
   - Sprint speed; xwOBA gap cohorts.
   - Share improved/worsened.
8. **Results III: from performance forecasts to fantasy categories.**
   - Level 0 pools.
   - Level 1 association.
   - Level 2 (Figure 5; primary 8; direct metrics; admitted vs history forecasts).
   - 2026 exploratory.
   - Level 3 (Figure 6).
9. **A new target: ERA.** Generalization check (Amendment 1).
10. **Discussion.**
    - What a public reader should do.
    - Where fantasy wisdom agrees or disagrees.
    - Target and model conditionality.
    - Why defense and WAR behave as they do.
    - Front-office boundary; public-data compression.
    - Alternative explanations.
    - A closing paragraph, no recap section.
11. **Limitations and future work.**
12. **References; appendices:**
    - A: accepted abstract and revision diff;
    - B: gate definitions and reason codes;
    - C: reproducibility and data rights;
    - D: full fantasy matrix.

## Claims that will NOT appear
- "The six targets are fantasy categories."
- "Fantasy players will win more."
- "MLB organizations can deploy this as-is."
- "The 2026 holdout was prospective."
- "The framework handles any metric and any target."
- "Selective models beat broad models" without qualification.
- Conversions of FIP or WAR changes into fantasy points or runs saved.

## Figures (all from `figures/make_figures.py`; data in `figures/data/`)
1. Decision flow, with human versus statistical steps and the sprint-speed two-target example.
2. Player stories (Stuff+ → FIP): Rogers, Wheeler, deciles, share improved.
3. Six-target model comparison: nested 2021–2025 and 2026.
4. Classification map with reason codes.
5. Fantasy linkage matrix.
6. Illustrative draft backtest.
7. Year by year, 2021–2026.
