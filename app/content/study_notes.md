# Study notes for the app (source text — keep wording faithful)

## Original accepted abstract (historical record, preserved verbatim; later analyses qualify some claims)

**Title:** One Metric, Different Jobs: Target-Specific Feature Admission for Major League Baseball Player Projection

**Introduction**

Baseball organizations have access to hundreds of traditional, tracking-derived, and process metrics, but a metric that explains player performance does not necessarily improve a future projection. This study asks when a candidate metric should be allowed to change a next-season forecast and when it is better treated as diagnostic or contextual information. The question is important for baseball decision systems because redundant, unstable, or sparsely available inputs can add complexity without improving out-of-sample accuracy.

**Methods**

Using MLB player-season data from 2015–2025, I evaluated candidate features for next-season wOBA, FIP, baserunning run-value rate, fielding run-value rate, hitter WAR rate, and pitcher WAR rate. A registry of 402 fields produced 208 feature-target admission evaluations across 163 unique metrics under component-specific eligibility. Each target used a strong history-aware ridge-regression baseline. Headline results came from seven expanding-window temporal folds with outcomes from 2019–2025, so training data always preceded the feature and outcome seasons. Candidate features were evaluated for incremental out-of-time RMSE improvement, temporal stability, redundancy, coverage, subgroup robustness, and target dependence. Selective admitted-feature models were also compared with broader “kitchen-sink” models.

**Results**

Feature usefulness was strongly target-specific. Two-year xwOBA improved next-season wOBA RMSE by 0.00093 beyond a baseline already containing two-year wOBA and improved all seven folds. Exit velocity also improved future wOBA and hitter WAR. Stuff+ improved next-season FIP RMSE by 0.00730 beyond a two-year FIP baseline, with five of seven folds improving. Sprint speed was highly stable year to year (r ≈ 0.92) but provided essentially no incremental value for future wOBA (ΔRMSE ≈ +0.00003); for baserunning, the same metric improved RMSE by 0.0599 in all seven folds. Selective models outperformed kitchen-sink alternatives for wOBA and FIP, while the broader model performed better for hitter WAR.

**Conclusion**

Baseball metrics should not be classified as universally “predictive” or “non-predictive.” Their role depends on the target, the information already in the model, and whether they contribute repeatable future signal under realistic temporal validation. For baseball operations, this framework provides a reproducible way to decide which metrics should change a projection, which should explain it, and which should remain contextual.

## What changed after stronger validation (show next to the abstract)
- Exit velocity → hitter WAR is no longer supported: nested 2021–25 −0.57% [−1.19, +0.05]; 2026 +0.72% [−0.49, +1.82].
- Stuff+ → FIP is small: pooled 2019–25 −0.48% [−0.92, −0.03]. Holm-adjusted p = 0.018, but BH q = 0.062 across all 208 tests.
- "Selective beats kitchen-sink" holds only against an all-feature ridge model, for wOBA and FIP historically.
  - A tuned elastic net ties it.
  - Broad models win for both WAR targets.
  - In 2026 the all-feature ridge was better for FIP: kitchen minus selected −3.78% [−7.26, −0.10].
- Sprint speed's target dependence replicated:
  - baserunning 2021–25 −4.75% [−6.16, −3.30]; 2026 −3.30% [−6.68, +0.09];
  - wOBA ≈ 0 throughout (2026 −0.16% [−0.48, +0.16]).

## Verdict roles: how each is decided
- **Projection**: statistical. All of these must hold:
  - out-of-time RMSE improves by at least 0.5% of the baseline RMSE;
  - at least 3 folds;
  - the 95% CI is below zero, or at least 60% of folds improve;
  - not redundant with simpler features;
  - the coefficient changes sign fewer than 2 times;
  - no harm in most large subgroups;
  - coverage at least 70%.
- **Diagnostic**: failed the Projection test, AND the metric catalog marks it as an interpretable process metric. That flag is a human, domain-based label, not something the algorithm discovered.
- **Exclude**: failed the Projection test and is not flagged as a process metric. It means "no conditional value for this target given this baseline", not "useless".
- **Context**: assigned from a human-specified role (park/environment, age, playing time), whatever its predictive value.
- **Augmented Projection / Insufficient Evidence**: defined, but never triggered in the 208 evaluations. 207 of the 208 had 7 folds; arm angle × FIP had 4, because arm angle is available only from 2020.
- A metric–target pair that was never evaluated shows **Not evaluated**, never a verdict.

## Four different things called "unstable"
1. **Feature reliability**: the metric's own year-to-year correlation (Pearson r). It is reported, and listed as a reason in Diagnostic text, but it never blocks or grants admission. A stable metric can still add nothing (sprint speed for wOBA).
2. **Lift consistency**: the share of the out-of-time folds (7 for 207 of the 208 evaluations) in which adding the metric lowered RMSE. It is part of the Projection test (at least 60%, or a CI below zero).
3. **Coefficient drift**: the number of sign changes of the metric's coefficient across folds. Two or more blocks Projection.
4. **Uncertainty**: the width of the bootstrap interval. It is separate from all three above. The canonical point estimate is the mean of the fold-level changes, while the interval comes from a pooled bootstrap of paired errors. Because the two estimate slightly different quantities, 7 of the 208 point estimates fall just outside their own interval.

## Caveats the app must keep visible
- **2026 check.** The 2026 forecasts were frozen in the workflow (committed 2026-11-12 before the 2026 tables were downloaded). The design is still retrospective: the season had already been played. Several 2026 intervals include zero, so those results are directional.
- **Who is in the sample.** Historical evaluation populations require the player to meet playing-time rules in the next season too. In 2026:
  - 24% of 2025-eligible hitters and 34% of 2025-eligible pitchers did not meet those rules;
  - injured, demoted and released players are mostly outside the evaluated populations.
- **Fantasy bridge.** The fantasy pools include non-returners (scored as zero). The fantasy-bridge results are exploratory: the protocol was written before fitting, but the seasons are not new.
- **Not fantasy categories.** None of the six targets is a standard fantasy category. wOBA, FIP and WAR are not scored in standard 5×5 or points leagues.
- **Front offices.** This is public data compressed into single-number metrics. It is not a substitute for team-proprietary tracking models.
- **Stuff+.** The study's Stuff+ is its own expanding-window expected-whiff model, not FanGraphs' Stuff+.
- **WAR.** Both WAR targets are Baseball-Reference WAR (bWAR), not FanGraphs fWAR.
- **No 2027 forecasts.** No 2027 player forecasts are published: 2026 feature panels were not built.

## Data rights
MLB Stats API and Baseball Savant data are © MLB Advanced Media; Baseball-Reference WAR is © Sports Reference. Their terms restrict redistribution. The app shows:
- aggregate research results;
- a curated set of player examples (forecasts are the study's own; observed values are public season statistics).

It does not ship the underlying data panels. The repositories contain code that rebuilds every dataset from the original sources.
