# Fantasy-bridge experiment protocol (FB) — written before any fantasy outcome model was fit

**Version:** 1.0, 2026-11-13. This file is committed to the public repository before any downstream (fantasy-category) model was fit or scored. Later changes are recorded as dated amendments at the end and never replace earlier text.
**Status of the evidence:** exploratory extension of Paper ID 18. It is *not* a pre-registered confirmatory trial:
- the 2015–2025 seasons were analysed in the original study;
- the 2026 season was inspected on 2026-11-12 for the six original targets.
**What was already seen:** the six-target forecasts (E1 nested admission; E2 frozen 2026 predictions) and their accuracy.
**What was not seen:** any relation between those forecasts and fantasy categories. No fantasy-category model has been estimated in this project before this protocol.

## 1. Question
Do out-of-time forecasts of the six original targets add information about next-season **fantasy scoring outcomes**, beyond a direct, history-aware fantasy baseline that a careful public-data manager could build? The six targets are next-season wOBA, FIP, baserunning run-value rate, fielding run-value rate, hitter bWAR per 600 PA, and pitcher bWAR per 200 IP.

This is a downstream test, separate from the original metric-to-target admission. It answers "does a better *target* forecast carry *fantasy* information?" It does not answer "is the metric predictive of the target?"

## 2. Data
- **Fantasy outcomes.** MLB Stats API season totals already used by the study:
  - `data/raw/mlb_hitting_2015_2025.parquet` and `data/raw/mlb_pitching_2015_2025.parquet`;
  - for 2026: `sloan2027/holdout2026/raw_2026/mlb_{hitting,pitching}_2026.parquet`, fetched 2026-11-12 06:49 UTC.
  - Each table has one row per player-season, summed across teams (verified: no duplicate `mlbam_id`, `season` keys).
  - Innings are taken from integer `outs`: IP = outs/3. The text field `inningsPitched` uses ".1/.2" notation and is never used in arithmetic.
- **Upstream forecasts.** Ridge forecasts of each target, built with the study's own code (`sloan2027/experiments/lib_nested.py`) and its nested admission output.

## 3. Forecast-date player pools
For outcome season **T**, the pool contains only information available before T:

| Pool | Rule (season T−1) | Source of rule |
|---|---|---|
| Hitters | ≥ 150 PA in T−1 | wOBA study year-t eligibility (canonical) |
| Pitchers | IP ≥ 80 (starters) / ≥ 30 (relievers) in T−1; 25 / 10 in 2020 | FIP study year-t eligibility (`_ip_threshold`) |

- Players are **not** filtered on season-T participation.
- A pool player with no season-T MLB record has zero counting statistics in T. That is a real fantasy outcome: a drafted player who is injured, demoted or released scores nothing.
- Rookies and players below the thresholds are outside the pool. This limits the conclusions to established major leaguers. It is reported, not hidden.

Outcome seasons:
- **Primary:** T = 2021–2025 (five outer years). These match the E1 nested design, which produced nested admission windows for them.
- **Exploratory:** T = 2026. The upstream test-row forecasts are the frozen 2026 predictions (commit `f8023bf`, sha256 `af61b2b8…`).

## 4. Outcomes (season T)
| Category | Definition | Form | Evaluation population and weight |
|---|---|---|---|
| R, HR, RBI, SB | season totals | production (count) | all pool hitters, equal weight; non-returners = 0 |
| AVG | H / AB | rate | pool hitters with AB ≥ 100 in T; weight AB |
| W, SV, K | season totals | production (count) | all pool pitchers, equal weight; non-returners = 0 |
| ERA | 9·ER / IP | rate | pool pitchers with IP ≥ 20 in T; weight IP |
| WHIP | (BB + H) / IP | rate | pool pitchers with IP ≥ 20 in T; weight IP |
| Hitter points / pitcher points | Yahoo default H2H-points weights, exactly as recorded from Yahoo's help page in `scoring_conventions.md` | production | all pool players; non-returners = 0 |
| Hitter roto value / pitcher roto value | §6 z-score value from realized totals | production | all pool players |

Rules applied to every model:
- **2020 proration.** Counting outcomes and counting features from the 60-game 2020 season are multiplied by 162/60. Ratio statistics are not prorated.
- **Points fallback.** If the Yahoo points weights cannot be verified, ESPN's verified default weights are used instead. If neither can be verified, the points outcomes are skipped. Weights are never chosen by the analyst.
- **Ratio populations.** The AB/IP floors condition on realized playing time. This is an evaluation filter, identical for every model compared, never a feature. Results for AVG/ERA/WHIP are therefore "conditional on playing".

## 5. Models
**Estimator.** Ridge regression on standardized features, with training-median imputation:
- α is tuned over {0.01, 0.1, 1, 10, 100, 1000} on inner chronological folds inside the training seasons only;
- the inner folds are the `inner_folds` rule in `lib_nested.py`.

**Training rows for window T.** Pool rows with outcome season 2018 … T−1 (feature seasons 2017 … T−2).

**Direct fantasy baseline (BF).** Features from seasons ≤ T−1 only:
- **Hitters:**
  - PA_t, PA_{t−1} (0 if absent), G_t, age, age²;
  - for each of R, HR, RBI, SB: the per-PA rate in t and a PA-weighted two-year rate;
  - AVG_t and a two-year AB-weighted AVG;
  - BB% and K% in t.
- **Pitchers:**
  - IP_t, IP_{t−1} (0 if absent), G_t, GS_t, GS share, age, age²;
  - W_t, SV_t, save opportunities_t, holds_t;
  - K per IP in t and a two-year IP-weighted K per IP;
  - ERA_t, WHIP_t, and two-year IP-weighted ERA and WHIP.
- **Never used as features:** future PA/IP, or any season-T quantity.

**Upstream forecasts F_k.**
- **ADM:** the nested-admission ridge forecast of target k, using the window-T selected set S_T from `results/nested/admission/{study}_T{T}_default_meta.json`.
- **B0:** the history-only target baseline forecast.
- **Chronological refits.** Each row's forecast for feature season f comes from an upstream ridge (α = 1, canonical weights) trained on that study's canonical sample rows with feature season ≤ f−1. Feature season f predicts outcome season f+1, so training outcomes are ≤ f.
  - For test rows (f = T−1) this is exactly the E1 outer-year model.
  - S_T was chosen using outcomes ≤ T−1, so the training rows see a feature set chosen with in-window information. No season-T information enters.
- **Missing forecasts.** Fielding forecasts exist only for players meeting the fielding study's year-t rule (≥ 200 defensive innings in t). Every linkage involving the fielding forecast is evaluated on the subset that has one, with baseline and augmented models compared on that identical subset.

**Comparisons per outcome** (identical rows, identical training seasons):
1. BF versus BF + F_k(ADM), one target at a time. Hitter targets: wOBA, baserunning, fielding, hitter WAR. Pitcher targets: FIP, pitcher WAR.
2. BF versus BF + all available ADM upstream forecasts jointly.
3. BF + F_k(B0) versus BF + F_k(ADM). Does the metric-admitted target forecast carry more fantasy information than the history-only target forecast?
4. **Direct-metric secondary set.** BF versus BF + the raw season-t metric:
   - sprint speed → SB;
   - xwOBA (two-year) → AVG, HR, R, RBI;
   - Barrel% → HR;
   - Stuff+ → K, ERA, WHIP;
   - K% → K;
   - K-BB% → ERA, WHIP.

## 6. Roto value (Level 3, illustrative)
**Format.** Primary: 12-team 5×5 rotisserie, using Yahoo's default categories as recorded in `scoring_conventions.md`.

**Category value for season T.**
- Counting category: value = (x − μ)/σ.
  - Hitter ratio category: the AVG contribution is H − AB·AVĜ.
  - Pitcher ratio categories: the ERA contribution is IP·ERÂ/9 − ER; the WHIP contribution is IP·WHIP^ − (BB + H).
  - Here AVĜ, ERÂ and WHIP^ are the pooled training-season ratios.
  - μ and σ are each category's mean and SD over the realized **training-season** pools (seasons ≤ T−1), so they are known on draft day and identical for every model.
- Value = sum of the five category z-scores. Hitters and pitchers are valued separately.
- No positional adjustment. That is a stated limitation.

**Predicted totals.**
- R, HR, RBI, SB, W, SV, K come from production models.
- H = predicted AVG × predicted AB.
- ER = predicted ERA × predicted IP / 9; BB + H = predicted WHIP × predicted IP.
- AB and IP get their own production models: the same BF, outcome = AB or IP in T, non-returners = 0.

**Draft policy (illustrative).** Pick the top k by predicted value: k = 156 hitters and 108 pitchers (12 teams × 13 hitters / 9 pitchers). Sensitivity: k ∈ {50, 100, 156/108, 195/135 (15 teams)}.

**Decision metrics.**
- Realized value captured by the top-k set.
- Spearman ρ between predicted and realized value.
- Top-k overlap with the realized top-k.

**Models compared.** "Baseline" uses BF in every category model. "Augmented" uses BF + all ADM upstream forecasts in every category model. The points-league version replaces value with total points.

These are clearly labeled what-if backtests. There is no average draft position (ADP), position eligibility, snake order, in-season management, or league simulation, so they are not evidence that anyone wins leagues.

## 7. Evaluation and uncertainty
- **Primary metric.** ΔRMSE% = 100·(RMSE_aug − RMSE_base)/RMSE_base, pooled over T = 2021–2025, on identical rows. Negative means the augmented model is better. MAE is also reported. Effects are also given in outcome units (HR, SB, ERA points, …).
- **Uncertainty.**
  - Paired player-cluster bootstrap: B = 2,000, seed 42, resampling players across all outer years. This is `paired_cluster_bootstrap` logic from `lib_nested.py`.
  - Two-sided bootstrap p = 2·min(P(Δ ≥ 0), P(Δ ≤ 0)), floored at 1/(B+1).
- **Season sensitivity.** Per-year ΔRMSE, number of years improved (of 5), and a season-block bootstrap that resamples the five outer years. Five seasons give coarse intervals, and they are reported as such.
- **Primary family** (8 pre-specified linkages, Holm-adjusted):
  1. wOBA → AVG
  2. wOBA → HR
  3. FIP → ERA
  4. FIP → WHIP
  5. baserunning → SB
  6. fielding → hitter roto value (boundary case; a null result is expected and informative)
  7. hitter WAR → hitter roto value
  8. pitcher WAR → pitcher roto value
- **Everything else** (the full target × category matrix, the B0-versus-ADM contrasts, direct-metric tests, points, joint models): exploratory, with Benjamini–Hochberg q-values within each family.
- **Verdicts.**
  - "Adds information": the 95% CI is entirely below 0 and the Holm/BH-adjusted p < 0.05.
  - "Harmful": the CI is entirely above 0.
  - Otherwise: "no detectable gain". Nulls and harms are reported with the same prominence as gains.

## 8. Leakage guards and tests
- Every feature for outcome season T comes from seasons ≤ T−1.
- Upstream and downstream fits use training seasons only. Downstream tuning uses inner chronological folds.
- Unit tests:
  - (a) Perturbing season-T outcomes leaves every season-T forecast unchanged.
  - (b) Upstream test-row forecasts equal the E1 `ADM|ridge` predictions for rows in the canonical outcome-observed sample.
  - (c) Ratio categories are aggregated from components (H/AB, ER/IP, (BB+H)/IP), never by averaging player rates.
  - (d) IP is computed from outs.

## 9. Cohort and selection reporting
For each T, report:
- pool size;
- share of players with any season-T appearance;
- share meeting each original study's t+1 rule;
- zero-outcome share;
- AB/IP floor pass rates;
- the rookie/sub-threshold exclusions as a stated limitation.

## 10. Skipped by design
- **External projections.** Archived third-party preseason projections (Steamer, ZiPS, ATC, THE BAT X) are not in the study data. FanGraphs terms restrict scraping, so they are not used. The direct baseline is the study's own.
- **Level 4 (2027 forecasts).** It needs 2026 Statcast feature panels, which were not built. Only 2026 outcome tables were fetched. It is skipped and stated as such.

## Amendments
(none yet)
