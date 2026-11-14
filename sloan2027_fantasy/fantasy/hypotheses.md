# Falsifiable hypotheses drawn from the practice audit

Prepared for Sloan 2027 Paper 18 (fantasy framing). Source IDs refer to `research_sources.md`; belief IDs (B01 to B14) refer to `practice_audit.csv`. Prepared 2026-11-13.

Each hypothesis is labeled by where its premise comes from:
- **Published claim:** someone actually publishes the view; the source is cited.
- **Straw man:** a stronger or simpler version we did *not* find published. It is stated only so the paper does not attack it by accident.

---

## 0. Shared evaluation protocol (applies to every hypothesis)

### 0.1 Out-of-time design
- Expanding window. For each target season *t+1* from 2017 to 2025, fit every model only on player-seasons whose target year is at most *t*, then predict *t+1*.
- Statcast and other inputs come from seasons up to *t* only.
- Treat 2020 in one of two ways and show both: drop it as a target season, or keep per-PA/per-IP rates with a 2020 flag.

### 0.2 History-aware baseline (B)
- Use the paper's existing strong baseline.
- At minimum, include a Marcel replica built from the study data (S46):
  - Weights 5/4/3 over three seasons.
  - Regression to the league mean equal to 1,200 PA for hitters; for pitchers, use an innings-based analogue chosen on pre-period data only.
  - Age adjustment around age 29.
  - Marcel's playing-time rule (0.5 x last season's PA + 0.1 x the season before + 200).
- The method is public, so it is license-free.

### 0.3 Challenger (B+X)
- The same model plus candidate metric X, using a multi-year weighted average of X.

### 0.4 Identical players
- Every paired comparison uses exactly the same player-season rows: the intersection of rows where both models can produce a forecast.

### 0.5 Losses
- Rate targets (wOBA, ERA, WHIP, AVG, K%): squared error weighted by realized next-season PA or IP. As a sensitivity check, weight by forecast PA or IP to avoid any look-ahead in the weights.
- Counting stats and fantasy values: unweighted squared error.

### 0.6 Paired test
- For each player-season i, compute d_i = (error under B)^2 - (error under B+X)^2.
- H0: mean(d) <= 0.
- Inference:
  - A player-clustered bootstrap that resamples players with all their seasons (10,000 resamples).
  - A Diebold-Mariano-type statistic with season blocks.
  - A leave-one-season-out check.
- Report the MSE skill score, 1 - MSE(B+X)/MSE(B), with a 95% interval.

### 0.7 Decision rules (pre-register before running)
- "Support" requires the lower 95% bound of the skill score to be above 0 **and** skill of at least a pre-set minimum. We suggest 1% MSE reduction; the authors should fix this number in advance.
- Use Holm correction within each family of metrics x outcomes.

### 0.8 Two-stage fantasy chain (for the separate fantasy experiment)
- Stage A: does metric X improve the forecast of study target T (for example, xwOBA for wOBA)?
- Stage B: does the forecast of T add OOT information about fantasy outcome F (for example, AVG, R, RBI, HR, SB, W, SV, K, ERA, WHIP, or points) beyond a baseline forecast of F itself (a Marcel of F plus a PA/IP forecast)?
- Report Stage B for both versions of the T forecast, with and without X.

### 0.9 Fantasy outcome definitions (from `scoring_conventions.md`)
- **5x5 roto value:** Yahoo default categories. Ratio categories enter as volume-weighted contributions:
  - AVG: H - lgAVG x AB
  - ERA: lgERA x IP / 9 - ER
  - WHIP: lgWHIP x IP - (BB + H)
- Z-scores are computed within a 10- or 12-team Yahoo-default rostered pool. An NFBC 15-team version is a sensitivity check.
- **Points:**
  - Yahoo H2H points, computed exactly for batters and without the pitcher HBP term.
  - ESPN points with W = 2 and W = 5, without losses.
  - CBS points as a partial sensitivity (no QS, L or pitcher HBP).

### 0.10 Why incremental, shrinkage-based tests (peer-reviewed background)
- Shrinking toward population means across players and seasons improves hitting forecasts (S53).
- Many hitting metrics carry real but heavily overlapping signal (S54). A metric can look predictive on its own and still add nothing beyond history, which is why every comparison here is incremental.
- Fantasy outcomes keep an irreducible element of chance even when skill dominates (S52). Expect modest skill scores.

### 0.11 Data the study does not have
- No ADP, archived projections, injury reports, depth charts or lineup slots.
- Pitcher losses, quality starts and hit batters allowed are not in the variable list.
- The study's Stuff+ is an in-house expanding-window model, not FanGraphs Stuff+.

---

## H1. xwOBA improves wOBA forecasts, and the gain shrinks as it passes into fantasy hitting categories (B01, B13)

- **Community viewpoint (published claim).**
  - MLB's glossary: "xwOBA is more indicative of a player's skill than regular wOBA, as xwOBA removes defense from the equation." (S11)
  - Szymborski: xStats "can be a crucial part of a predictive model" (S12).
  - Counterviews: Dunbar finds expected stats "are not more predictive of future success than actual stats" (S16). Chamberlain calls xwOBA weak as an in-season predictor (S14).
  - The "buy-low on positive x-gap" practice appears in fantasy columns. Melchior (S15) shows the gap only partly closes.
- **Straw man (not found published):** "xwOBA alone forecasts next season better than any history-based projection."
- **Hypothesis.**
  - (a) Adding multi-year xwOBA to B gives positive OOT skill for next-season wOBA.
  - (b) Feeding the improved wOBA forecast into Stage B gives a **smaller relative skill gain** for next-season AVG, R, RBI, Yahoo points and 5x5 roto value than it gave for wOBA.
- **Measurable comparison.**
  - Stage A: skill of B+xwOBA vs B for wOBA in season t+1.
  - Stage B: skill of [F-baseline + wOBA forecast with xwOBA] vs [F-baseline + wOBA forecast without xwOBA] for each fantasy outcome F.
  - Secondary: B + (wOBA - xwOBA) vs B + xwOBA, to test whether the "luck gap" carries information beyond the xwOBA level.
- **Required data:** PA, AB, H, 2B, 3B, HR, BB, HBP, R, RBI, SB, AVG, wOBA, xwOBA, xBA, xSLG, sprint speed, age.
- **Test:** protocol section 0. Holm correction across the six fantasy outcomes.
- **Supports:**
  - (a) Lower bound of wOBA skill above 0 (replicating the direction in S12).
  - (b) Skill for fantasy outcomes smaller than wOBA skill (a paired bootstrap of the difference in skill excludes 0).
- **Refutes:**
  - (a) No wOBA gain, which would favor S16 over S12.
  - (b) Fantasy gains as large as the wOBA gain. That would mean the metric's value passes through to fantasy in full.

## H2. Statcast power metrics add HR information mainly for hitters with short MLB histories (B02)

- **Community viewpoint (published claim).**
  - Barrel rate and fly-ball/line-drive EV are among the most stable power indicators (S17: year-to-year r .80 and .82).
  - THE BAT X uses max EV, top-5% EV, barrels and similar inputs (S43).
  - Counterview: an EV-gap screen alone did not find breakouts, while EV95 plus a contact gain did (S18).
- **Straw man:** "Any rise in max EV means a power breakout."
- **Hypothesis.** Adding Barrel%, max EV and hard-hit% to B improves OOT forecasts of next-season HR/PA and HR count. The gain is concentrated among hitters with at most one prior qualifying MLB season and is near zero for hitters with three or more.
- **Measurable comparison:** skill of B+{Barrel%, max EV, hard-hit%} vs B for HR/PA (PA-weighted) and HR count, stratified by history length (1, 2, 3+ prior seasons). Repeat for ISO and wOBA as a link to the main study.
- **Required data:** HR, PA, Barrel%, exit velocity, max EV, hard-hit%, launch angle, sweet-spot%, ISO, age.
- **Test:** protocol; test the interaction (skill difference between strata) with a paired bootstrap.
- **Supports:** positive skill overall, with skill in the 1-season stratum larger than in the 3+ stratum.
- **Refutes:** no skill in any stratum, or equal skill across strata (which would suggest the metrics add information even with long histories).

## H3. ERA estimators improve ERA forecasts more than WHIP forecasts or IP-weighted fantasy ratio value (B03, B04, B13)

- **Community viewpoint (published claim).**
  - FanGraphs Library: xFIP "has one of the highest correlations with future ERA of all the pitching metrics" and SIERA is "only slightly more predictive than xFIP" (S19).
  - Swartz: SIERA has the lowest next-year ERA RMSE (S20).
  - Richards and Sauceda report modest next-ERA R2, at most about .22 (S21, S22).
  - For WHIP, prior WHIP is stickier and K-BB% does best (S22).
- **Straw man:** "ERA-estimator gaps reliably predict which pitchers will win you ERA and WHIP."
- **Hypothesis.**
  - (a) SIERA (and separately xFIP and FIP) added to a Marcel ERA baseline gives positive OOT skill for next-season ERA.
  - (b) The relative skill is smaller for WHIP than for ERA.
  - (c) Skill is smaller again for IP-weighted fantasy contributions (ERA runs saved; WHIP baserunners saved), because innings uncertainty dilutes it.
- **Measurable comparison:** skill of B+SIERA, B+xFIP and B+FIP vs B for ERA (IP-weighted), WHIP (IP-weighted) and the two volume-weighted fantasy contributions.
- **Required data:** ERA, ER, IP, WHIP, BB, H, FIP, xFIP, SIERA, K%, BB%, GB%, HR%, BABIP, age.
- **Test:** protocol. Compare skills across outcomes with a paired bootstrap on identical pitchers.
- **Supports:** ERA skill above 0; WHIP skill below ERA skill; fantasy-contribution skill below rate skill.
- **Refutes:** no ERA skill, or WHIP and fantasy skill at least as large as ERA skill.

## H4. K-BB% matches SIERA for ERA, beats it for WHIP, and the in-house Stuff+ adds information mainly for strikeouts (B05, B06)

- **Community viewpoint (published claim).**
  - K-BB% beat SIERA for next-season ERA R2 (.224 vs .204; S21) and led for WHIP (.294; S22).
  - S16 concludes that strikeout-to-walk ratio is the leading predictive pitcher metric (paraphrase).
  - Stuff+ becomes reliable after about 80 pitches (paraphrase), and Pitching+ "out-predicts any current projection system for relievers" (S23).
  - Counterview: Stuff+ is "a poor predictor of ERA, worse than FIP" for team-switchers (S24).
- **Straw man:** "Stuff+ alone tells you who will have a good ERA next year."
- **Hypothesis.**
  - (a) As a single addition to B, K-BB% is at least as skillful as SIERA for next-season ERA and more skillful for WHIP.
  - (b) Adding in-house Stuff+ to B+K-BB% improves next-season K% and fantasy K forecasts but not ERA or WHIP.
  - (c) If team IDs can be added, Stuff+'s ERA skill is lower for team-changers.
- **Measurable comparison:**
  - Head-to-head: B+K-BB% vs B+SIERA (paired d_i on identical pitchers).
  - Increment: B+K-BB%+Stuff+ vs B+K-BB% for K%, K (with an IP forecast), ERA and WHIP.
- **Required data:** K, K%, BB%, K-BB%, SIERA, xFIP, FIP, ERA, WHIP, IP, GS, in-house Stuff+, velocity, whiff rate, CSW; team ID (needed for part c and not in the listed variables).
- **Test:** protocol. Part (a) is a two-sided paired test; parts (b) and (c) are one-sided.
- **Supports:** K-BB% not worse than SIERA for ERA (equivalence margin pre-set) and better for WHIP; Stuff+ increment above 0 for K% but about 0 for ERA and WHIP.
- **Refutes:** SIERA clearly beats K-BB% for both outcomes, or Stuff+ adds ERA/WHIP skill comparable to its K% skill.

## H5. Sprint speed adds little to SB forecasts once attempt history and opportunities are known (B07)

- **Community viewpoint (published claim).**
  - "not everyone who can run fast should run fast". Sprint speed correlates more with attempts per opportunity (r = .598) than with success rate (r = .298) (S27).
  - Collette stresses reads, manager intent and opportunities after the 2023 rules (S28).
  - The rules raised steals: 0.51 to 0.72 SB per team-game from 2022 to 2023 (S26).
  - THE BAT X includes sprint speed (S43).
- **Straw man:** "Sprint speed alone predicts stolen bases."
- **Hypothesis.**
  - (a) Once B includes Marcel SB, the prior attempt rate (SB+CS)/(1B+BB+HBP), OBP and a PA forecast, adding sprint speed gives OOT skill for next-season SB below the pre-set minimum.
  - (b) Exceptions: sprint speed adds skill for players with few prior opportunities, and for forecasts of 2023 made from 2022 (the regime break).
  - (c) The main study's forecast of baserunning run value adds SB information beyond B.
- **Measurable comparison:** skill of B+sprint speed vs B for SB count and SB per opportunity. Interactions with opportunity tercile and with a 2023 indicator. Skill of B + baserunning-run-value forecast vs B.
- **Required data:** SB, CS, H, 2B, 3B, HR, BB, HBP, PA, OBP, sprint speed, age, season; baserunning run component.
- **Test:** protocol. Report pre-2023 and post-2023 target seasons separately as well.
- **Supports:** overall skill below the minimum, with significant skill in the low-opportunity group and/or the 2023 transition.
- **Refutes:** substantial overall skill from sprint speed beyond attempt history. That would mean speed carries information that analysts say attempts already capture.

## H6. A WAR forecast adds no fantasy information beyond wOBA and playing-time forecasts (B08)

- **Community viewpoint (published claim).** WAR "clearly does not provide a good indicator of power or speed on its own" but "still has a place in fantasy baseball" (S30). Baseball-Reference WAR includes fielding, positional adjustment and replacement runs (S29), none of which score in fantasy (S01, S03, S06, S07).
- **Straw man:** "WAR is a good one-number fantasy ranking."
- **Hypothesis.**
  - (a) For hitters, adding the hitter bWAR/600 forecast (and separately its fielding and positional components) to [5x5-value baseline + wOBA forecast + PA forecast] gives OOT skill of about 0 for next-season 5x5 roto value and Yahoo points.
  - (b) The same holds for pitcher bWAR/200 against a [W, SV, K, ERA, WHIP baseline + IP forecast].
- **Measurable comparison:** skill of the augmented model vs the model without the WAR forecast, for roto z-sum, Yahoo points and each category.
- **Required data:** bWAR and its components; PA; IP; wOBA; position; all category stats.
- **Test:** protocol. Use an equivalence test (two one-sided tests) against a pre-set negligible-skill margin.
- **Supports:** skill inside the equivalence margin, especially for the fielding and positional components.
- **Refutes:** positive skill beyond the margin. Check with H7 whether it operates only through PA.

## H7. Prior fielding value predicts next-season playing time, and that is its only fantasy channel (B09)

- **Community viewpoint (published claim).** "the most often forgotten about reason players lose playing time is poor defense" (S31). We found no published quantitative test.
- **Straw man:** "Good defenders are better fantasy players."
- **Hypothesis.**
  - (a) Prior fielding run value (per game and total) improves OOT forecasts of next-season PA beyond Marcel PA, age, the wOBA forecast and position.
  - (b) Once forecast PA is included, fielding adds about 0 to forecasts of next-season R, HR, RBI, SB and points.
- **Measurable comparison:** skill of B_PA + fielding vs B_PA for PA, then skill of [F-baseline + PA forecast] + fielding vs [F-baseline + PA forecast] for each fantasy F.
- **Required data:** PA, G, fielding runs, position, age, wOBA, R, HR, RBI, SB.
- **Test:** protocol; part (b) uses an equivalence test.
- **Supports:** (a) positive PA skill and (b) fantasy skill inside the equivalence margin.
- **Refutes:** no PA skill, or fielding still adds fantasy skill after conditioning on PA.

## H8. Playing-time error dominates fantasy forecast error and swamps rate-metric gains (B10)

- **Community viewpoint (published claim).**
  - Zola (via ESPN) calls playing time "probably more responsible for differences of opinions than skills analysis" (S32).
  - Zimmerman: "all projections overproject the top hitters by a wide margin." Marcel had the best PA RMSE (S33).
  - Projection systems handle PT outside the rate model (S39, S41, S42, S44).
- **Straw man:** "Only playing time matters."
- **Hypothesis.**
  - (a) For next-season fantasy value (roto z-sum and Yahoo points), giving the model the actual PA or IP (oracle) reduces OOT MSE more than giving it the actual per-PA or per-IP rates.
  - (b) The fantasy-MSE gains from the best rate metrics in H1 to H5 are at least an order of magnitude smaller than the gain from the PA oracle.
- **Measurable comparison.** MSE of fantasy value under four set-ups:
  - forecast rate x forecast PA (B)
  - forecast rate x actual PA (PA oracle)
  - actual rate x forecast PA (rate oracle)
  - metric-improved rate x forecast PA

  Also compare Marcel PA with a constant-PA forecast, to measure realistic PT skill.
- **Required data:** PA, AB, IP, G, GS, all category stats, age. No injury data, so PA history is the health proxy, as in S33.
- **Test:** paired MSE differences under the protocol. Report the ratio (B - PA oracle) / (B - metric-improved) with a bootstrap interval.
- **Supports:** PA-oracle reduction larger than rate-oracle reduction, and a ratio of 10 or more.
- **Refutes:** rate-oracle reduction at least as large as the PA oracle, or metric gains comparable to PT gains.

## H9. Unweighted ratio scoring overstates the fantasy value of rate-metric gains (B11)

- **Community viewpoint (published claim).**
  - Z-scores "do not address the issue of opportunity" (S34).
  - "Batting average and WHIP are the two most tightly bunched categories" (S35).
  - Z-score tools "have challenges handling ratios" (S36).
- **Straw man (described and rebutted in S35, never found advocated):** "Ignore the ratio categories."
- **Hypothesis.**
  - (a) In simulated leagues built from realized seasons, volume-weighted AVG/ERA/WHIP contributions explain more variation in team standings points than unweighted rate z-scores.
  - (b) A metric's forecast gain for AVG, ERA or WHIP (from H1, H3, H4) is smaller when scored in volume-weighted units than in unweighted rate units.
- **Measurable comparison.**
  - Simulated 10- and 12-team Yahoo-default leagues and 15-team NFBC-style leagues. Fill rosters from realized player-seasons using random draws and value-based drafts.
  - Compare the R2 of standings points on summed player contributions under each scoring.
  - Compare skill scores of the same metric under each scoring.
- **Required data:** AB, H, PA, IP, ER, pitcher BB and H; roster settings from S01 and S06.
- **Test:** the difference in R2 across 1,000 simulated leagues (bootstrap interval); paired skill differences on identical players.
- **Supports:** higher R2 for volume-weighted contributions, and smaller weighted skill.
- **Refutes:** no R2 difference, or equal skill under both scorings.

## H10. The fantasy value of a metric depends on the scoring format (B12)

- **Community viewpoint (published claim).** Points primers say relievers lose most of their value in points leagues: 12 relievers versus 40 starters reached 350+ points in 2025 (S08). The platform tables (S01, S03, S07) give:
  - Pitcher K worth 3, 1 or 0.5 points.
  - Batter K penalties of 0, -1 or -0.5.
  - SB worth 4.2, 1 or 2.
- **Straw man:** "One ranking works for every league."
- **Hypothesis.**
  - (a) Hitter K% adds more OOT skill for ESPN and CBS points (which penalize batter strikeouts) than for Yahoo points (which do not).
  - (b) Sprint speed and the baserunning forecast add more skill for 5x5 roto value than for any points format.
  - (c) Pitcher K-BB% and in-house Stuff+ add more skill for Yahoo points (K = 3) than for CBS points (K = 0.5).
- **Measurable comparison:** for each metric, skill vs B under each format's fantasy outcome. Paired bootstrap of the skill differences between formats on identical players.
- **Required data:** all category stats, holds, CS, HBP (batters), K% (batters), sprint speed, K-BB%, Stuff+. Pitcher L, QS and HBP are missing, so ESPN and CBS pitcher points are partial and must be flagged.
- **Test:** protocol, plus format-difference contrasts with Holm correction.
- **Supports:** the predicted sign of each format difference, with intervals excluding 0.
- **Refutes:** no format differences, or reversed signs.

---

## Published claims vs straw men at a glance

| H | Claim people actually publish (source) | Straw man we did not find published | What we test |
|---|---|---|---|
| H1 | x-stats track skill and help in a blend (S11, S12); counterviews S13 to S16 | xwOBA alone beats projections | xwOBA beyond a history baseline, and whether the gain reaches fantasy categories |
| H2 | Barrel% and EV are stable power signals (S17); EV screens alone fail (S18) | Any max-EV jump means a breakout | Incremental HR skill by length of history |
| H3 | SIERA/xFIP beat ERA for next ERA (S19 to S22) | Estimator gaps reliably win ERA and WHIP | ERA vs WHIP vs IP-weighted fantasy value |
| H4 | K-BB% is the best simple indicator (S21, S22); Stuff+ stabilizes fast (S23); Stuff+ fails for team-switchers (S24) | Stuff+ alone predicts ERA | Head-to-head and incremental skill |
| H5 | Speed is necessary but not sufficient; attempts and intent matter (S27, S28) | Speed alone predicts SB | Speed beyond attempt history; 2023 regime |
| H6 | WAR is not fantasy value (S30) | WAR is a good fantasy ranking | Equivalence test of the WAR forecast's increment |
| H7 | Defense matters through playing time (S31) | Good defenders are better fantasy players | Fielding to PA, then to fantasy |
| H8 | Playing time drives value and disagreement (S32, S33) | Only playing time matters | Oracle decomposition |
| H9 | Ratios need volume weighting (S34 to S36) | Ignore ratio categories | Weighted vs unweighted scoring |
| H10 | Formats value players differently (S08; S01, S03, S07) | One ranking fits all | Metric skill by format |

## Beliefs not testable with the study data (keep as discussion only)

- **Averaging third-party projections beats any single system (B14; S45, S47).** Needs archived projections. Steamer's free historical pre-season files (S51) could make a Steamer-only extension possible.
- **Within-season stabilization of Stuff+ and Location+ (S23).** Needs pitch-level, within-season data.
- **Team or manager green light for steals (S28).** Needs team and manager context.
- **How injuries and depth charts shape playing time (S33, S39).** Needs injury reports and depth charts.
- **Lineup slot and team context for R and RBI.** Needs lineup data.
