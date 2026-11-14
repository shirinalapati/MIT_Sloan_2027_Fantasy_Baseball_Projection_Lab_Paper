# Public projection systems: disclosed methods, timing, access and use rights

Prepared for Sloan 2027 Paper 18 (fantasy framing). All pages were accessed on **2026-11-13**. Source IDs refer to `research_sources.md`.

**Legend**
- **Disclosed:** stated by the provider or system author.
- **Third-party:** an evaluation by someone else.
- **NOT VERIFIED:** no provider statement was found on the pages fetched.
- Quotes are 25 words or fewer and were copied from fetched text. Everything else is paraphrase.
- Nothing here is legal advice. Section 9 records what the terms say.

---

## Summary table

| System | Developer | Regression to the mean | Aging | Statcast / pitch-level inputs | Playing time (PT) | Blending | When published | Free on FanGraphs? |
|---|---|---|---|---|---|---|---|---|
| Steamer | Jared Cross, Dash Davidson, Peter Rosenbloom | Yes; regression tied to "reliability" (S51) | NOT VERIFIED | NOT VERIFIED | Own PT; Steamer600 rescales to 600 PA (S39) | No | 2027 preseason was live by 2026-11-13 (S40); updated daily (S39) | Current season yes; history members-only (S40); free history downloads on steamerprojections.com (S51) |
| ZiPS | Dan Szymborski | Not described as a separate step; baselines plus a comparable-player ensemble (S41) | Cohort-based (S41) | Statcast added after validation (S41) | Assumes full-time role; ZiPS DC uses RosterResource PT (S39, S41) | No | Team-by-team rollout from mid-November; full set by late January (S39, S41) | Current yes; history (2010-) members-only (S40) |
| ATC | Ariel Cohen | Inherited from inputs; not separately described | Inherited; NOT VERIFIED | Inherited | Modeled separately; manual edits (S42) | Weighted average of systems, weights per statistic (S42) | Weekly preseason; "ATC DC" in season (S39) | Current yes |
| THE BAT / THE BAT X | Derek Carty | Yes (S43) | Yes, position-specific curves (S43) | THE BAT X: launch angle, EV variants, barrels, sprint speed; pitcher stuff model (S43) | NOT VERIFIED | THE BAT X blends THE BAT with Statcast-based THE BATcast (S43) | Updated daily (S39) | Current yes; also sold via RotoGrinders (S43) |
| OOPSY | Jordan Rosenblum | Yes, by stat noise and by player type (S44) | Own curves (S44) | Revised Stuff+, velocity; barrel rate, swing speed (S44) | From FanGraphs Depth Charts (S44) | No (defense taken from Steamer) | Debuted 2025; daily in season (S39) | Current yes |
| FanGraphs Depth Charts | FanGraphs | Inherited from inputs | Inherited | Inherited | FanGraphs staff via RosterResource (S39) | 50/50 Steamer and ZiPS (S39) | Daily (S39) | Yes |
| Marcel | Tom Tango | 1,200 PA of league average (S46) | Linear around age 29 (S46) | None | 0.5 / 0.1 weights + 200 PA (S46) | No | Archive 2001-2012 (S46); Baseball-Reference publishes Marcels (S46) | Not on FanGraphs |

---

## 1. Steamer

- **Who.** Jared Cross, Peter Rosenbloom and Dash Davidson; on FanGraphs since 2012 (S39). The Steamer site's About page profiles the same three people (S51).
- **Method, disclosed (very little).**
  - A 2015 ESPN survey of projectors (S32) says Steamer uses weighted averages but "its exact formula isn't publicly shared."
  - The Steamer glossary (S51) says: "1 - reliability is the amount of regression towards the mean." So regression is used, and its size depends on each statistic's reliability.
  - The glossary also notes park and defense adjustments in pitcher projection fields.
  - No Steamer statement was found on aging curves, Statcast or pitch-tracking inputs, or how playing time is set: **NOT VERIFIED**. The MLB.com glossary entry on Steamer returned HTTP 406.
- **Playing time and variants.**
  - Steamer publishes its own PT.
  - "Steamer600" rescales every position player to 600 PA (450 for catchers), starters to 200 IP and relievers to 65 IP (S39).
  - Depth Charts replaces Steamer's PT with RosterResource PT (S39).
  - Platoon, starter/reliever split, context-neutral and percentile (wOBA and RA9) versions are for FanGraphs members only (S40, S51).
- **Timing.** Updated daily before and during the season (S39). On 2026-11-13 the FanGraphs projections page already read "2027 Projections - Steamer", updated that day (S40). We did not check which other systems had 2027 projections live on that date.
- **Access and use.**
  - The current season is free on FanGraphs (S40).
  - FanGraphs offers historical full-season Steamer back to 2012 as "Members Exclusive Data" (S40).
  - The Steamer site says: "If you'd like to download historical pre-season Steamer projections, you can do so for free!" (S51). Page 1 of 2 lists hitters for 2017-2024 and pitchers for 2018-2024; page 2 was not opened.
  - Organizations can buy API access (S51).
  - No license text on redistribution was found. The site shows only a copyright line (S51).

## 2. ZiPS

- **Who.** Dan Szymborski; on FanGraphs since 2010 (S39).
- **Method, disclosed (S41, 2026-11-10, "The 2027 ZiPS Projections Are Almost Here").**
  - Uses several years of stats, with recent seasons weighted more.
  - Builds player baselines adjusted for park, league and quality of competition.
  - Uses internal "z" stats: zBABIP, zHR, zBB, zSO.
  - Finds a large cohort of similar players by Mahalanobis distance and builds an ensemble model from those comparables to project future production. This cohort step is how aging enters; no separate aging-curve step is described.
  - Hitting projections are offense-only.
  - Statcast data was added in recent years, only after its predictive value was confirmed.
  - Uses basic injury information. The author says he makes no manual adjustments.
  - Publishes percentile ranges.
  - Basic ZiPS assumes full-time major-league roles and is not a playing-time forecast. The team articles take PT from FanGraphs Depth Charts.
- **Older disclosure (S32, 2015).** Weighted averages of the previous four seasons, PECOTA-like comparables for aging, and deliberately generous PT.
- **Variant.** ZiPS DC is ZiPS prorated to RosterResource PT (S39).
- **Timing.** The 2027 team-by-team rollout started the day after the 2026-11-10 announcement (S41). The full 2026 set was on FanGraphs by 2026-01-28 (S39). ZiPS updates daily in season (S39).
- **Access.** The current season is free. Historical ZiPS back to 2010 is members-only (S40).
- **Third-party.** Rosenblum's 2025 review (S45) found ZiPS the best standalone system for 2025 hitters.

## 3. ATC (Average Total Cost)

- **Who.** Ariel Cohen; on FanGraphs since 2017 (S39).
- **Method, disclosed (S42).**
  - A weighted average of other projection systems, with "a different weight for each statistic for which it projects" (2017).
  - Weights come from each system's past accuracy.
  - Inputs named in 2017: ZiPS, Steamer, FanGraphs Fans, other freely available projections, and the prior three MLB seasons.
  - From 2020: rates are modeled per unit of playing time. PT is aggregated separately in the same way, and rates are then scaled to it. Manual edits are mostly to PT.
  - In a 2017 comment, the author said no single system gets more than about one-third weight in a category.
  - Regression and aging are inherited from the input systems and are not described separately (NOT VERIFIED).
- **Timing.** Updated weekly before the season, then published as "ATC DC" in season with daily PT updates (S39).
- **Third-party and self-evaluation.**
  - FantasyPros' 2025 study ranked ATC 2nd overall (S47).
  - Cohen's own auction-simulation comparisons rank ATC first in 2023 and over six seasons (S48). This is the system author evaluating his own system.

## 4. THE BAT and THE BAT X

- **Who.** Derek Carty. THE BAT has been on FanGraphs since 2018 (S39).
- **THE BAT, disclosed (S43, 2019).**
  - Regression toward the mean, weighting of multiple seasons, aging curves (position-specific in the season-long version) and minor-league translations.
  - "Backwards" adjustments remove the context of past stats.
  - "Forward" adjustments add parks, weather and opponents.
  - The season-long version includes exit velocity.
- **THE BAT X for hitters, disclosed (S43, 2020-06-11).**
  - Blends THE BAT with THE BATcast, a Statcast-based model: "THE BAT X combines the best of both worlds."
  - More than 150 Statcast variables were evaluated. Named inputs include max exit velocity, the average of the top 5% of exit velocities, share of balls over 100 mph, barrel rate and sprint speed.
  - Models whether a hitter's change in approach tends to stick.
  - Some inputs are kept proprietary.
  - Backtests are asserted but no error metrics are published.
- **THE BAT X for pitchers, disclosed (S43, 2026-02-19).**
  - Adds THE BATcast stuff model, built from about 4,000 candidate variables: velocity, movement, spin, seam-shifted wake, approach angles, tunneling and others.
  - Predicts K, BB, HR and BABIP, then blends these with the results-based THE BAT.
  - Described by the author as a "black box". No accuracy figures are given.
- **Playing time.** Not described in these articles: NOT VERIFIED.
- **Timing and access.**
  - Both versions are updated daily on FanGraphs (S39). The current season is free there.
  - They are also sold through the RotoGrinders marketplace, "for one reasonable price" with a seasonal option (S43; no dollar amount stated).
- **Third-party.**
  - FantasyPros 2025 ranked THE BAT 3rd overall and best among original (non-aggregate) systems. THE BAT X appears only in the hitting breakdown (S47).
  - Rosenblum's review (S45) found THE BAT X 2nd among veteran hitters.

## 5. OOPSY

- **Who.** Jordan Rosenblum. Introduced 2025-01-15 (S44); debuted for the 2025 season (S39).
- **Method, disclosed (S44).**
  - Starts from Marcel.
  - Adds run-environment adjustments, its own aging curves, Davenport-inspired major-league equivalencies, minor- and major-league park effects and recency weights.
  - Regression to the mean is stronger for noisier stats. Players regress to different means depending on their estimated chance of reaching the majors.
  - Pitcher inputs: revised Stuff+, velocity, K%, BB% and GB%. The author says "the traditional statistics continue to weigh heavily in the pitching projections".
  - Hitter inputs: K%, BB%, HR%, barrel rate per batted ball and Baseball Savant swing speed.
  - Excludes amateur, foreign-league and minor-league Statcast data.
  - Defensive value comes from Steamer. Playing time comes from FanGraphs Depth Charts.
- **Timing.** Performance projections are updated as needed before the season and daily during it. PT updates daily (S39).
- **Self and third-party.**
  - The author's 2025 review (S45) scored each system by PA- or BF-weighted RMSE of wOBA, after rescaling to a common league average. OOPSY ranked 2nd among standalone systems for both hitters and pitchers, and a composite was best.
  - FantasyPros 2025 ranked OOPSY 8th of 13 overall (S47).

## 6. FanGraphs Depth Charts

- **Method, disclosed.** "a 50/50 blend of Steamer and ZiPS prorated to our RosterResource playing time projections", updated daily before and during the season (S39, 2026-01-28).
- **How PT and injuries are handled.**
  - FanGraphs staff divide each team's playing time.
  - "If a player gets hurt, we dock their expected playing time."
  - Before ZiPS came out each year, Steamer alone was used (S39, Library page from 2016; may be outdated).
- **Third-party.**
  - FantasyPros 2025 ranked Depth Charts 4th overall (S47).
  - In Zimmerman's review of 2024 playing time (S33), Depth Charts' PA RMSE was 168.8. The average of all systems scored 145.7.

## 7. Marcel, the naive benchmark

- **Purpose, disclosed.** Tango calls it "the most basic forecasting system you can have, that uses as little intelligence as possible" (S46).
- **Method, disclosed (S46: Marcel page and "The 2004 Marcels" post of 2004-03-10).**
  - Three MLB seasons weighted 5/4/3, most recent heaviest.
  - Regression: each player's league average is added "at a total of 1200 PA" (2 x 600 PA).
  - Projected PA: "Determine the projected PA = 0.5 * 2004PA + 0.1 * 2003PA + 200." This is the 2004 worked example as written.
  - Age adjustment around age 29: 0.006 per year under 29 and 0.003 per year over 29. The post's sign error is corrected in comment #20 to (29 - age).
  - Results are rebaselined to the league environment.
  - Players with no MLB history get league mean over 200 PA, 60 IP for a starter or 25 IP for a reliever.
  - Pitcher-specific season weights were seen only in secondary snippets in this pass: NOT VERIFIED.
- **Publication.** Tango's page archives forecasts for 2001-2012. Baseball-Reference publishes Marcels and says its implementation used Jeff Sackmann's code as a reference (S46).
- **Third-party.** In S33's second test (160 hitters, 2024), Baseball-Reference's Marcels had the best PA RMSE (142.2). Zimmerman wrote: "The Marcels projection at Baseball-Reference.com crushed the competition by just using a three-year weight average."
- **For Paper 18.** Marcel is fully specified, so it can be recomputed from the study's own 2015-2025 data. That makes it a legitimate and license-free naive benchmark and a floor for the history-aware baseline.

---

## 8. What the independent accuracy evidence does and does not show

| Study | What is scored | Main result | Caveat |
|---|---|---|---|
| FantasyPros 2025 (S47) | z-scored errors in R, HR, RBI, SB, AVG and AB; W, SV, K, ERA, WHIP and IP | 1 Zeile consensus (equal-weight average), 2 ATC, 3 THE BAT, 4 Depth Charts, 7 Steamer, 8 OOPSY, 9 ZiPS DC | Errors are relative to the set of systems tested; pool size not stated |
| Rosenblum 2025 (S45) | PA/BF-weighted RMSE of wOBA | ZiPS best for hitters, Steamer best for pitchers, composite best overall | Author-run evaluation; RMSEs shown only in images |
| Zimmerman 2024 PT review (S33) | RMSE of plate appearances | Marcel best; all systems over-project top hitters; adding injured-list information did not help | One season; about 160 hitters |
| Cohen 2023 game-theory test (S48) | Simulated auction profit against NFBC average auction values | ATC first; no system made a profit on the full player pool in 2023 | Run by ATC's author; market-relative measure |

None of these studies scores the six Paper 18 targets. They also do not agree on what "accuracy" means (category z-errors, wOBA RMSE, PA RMSE, auction profit). This supports the paper's "different jobs" framing.

---

## 9. Terms of use: scraping and redistributing projections

- **FanGraphs Terms of Service (S49; page updated 2026-11-12).**
  - Section 17: "You agree not to access the Service by any means other than through the interface that is provided by Fangraphs". It also bars users from distributing or creating "derivative works based on the Service".
  - Section 6 restricts "unauthorized reproduction, publication, further distribution or public exhibition of the materials".
  - Section 11 bars commercial exploitation of "any portion of the Service".
  - The terms have no clause specific to projections. "Data Export" is labeled "[Members Only]" (S40).
  - FanGraphs' robots.txt disallows only some legacy and test paths (S49). That is a crawler instruction, not a license, and it does not override the Terms.
- **Sports Reference (S50; relevant because the study's bWAR comes from Baseball-Reference).**
  - Automated access is prohibited "without our express written permission".
  - Aggressive spidering is blocked.
  - Some licensed data "completely preclude any redistribution".
  - Site content may not be used "for purposes of training, fine-tuning, prompting, or instructing artificial intelligence models" without permission.
  - **Flag this for the paper's provenance and data statement.**
- **Steamer site (S51).** Free historical pre-season downloads and a paid API for organizations. No redistribution license text was found.
- **Practical reading (not legal advice).** Scraping FanGraphs projection tables would appear to conflict with Section 17. Posting raw projections in a replication bundle would appear to conflict with Sections 6, 11 and 17 unless FanGraphs grants written permission. Publishing derived error statistics computed from lawfully obtained files is the conservative route.

## 10. Can archived preseason projections be obtained lawfully for backtesting?

| Source | Systems and years verified | Access | Notes |
|---|---|---|---|
| FanGraphs "Historical Preseason Projections" (S40) | ZiPS 2010-2026; Steamer 2012-2026 | FanGraphs membership ("Members Exclusive Data"); export members-only | Viewing and export fall under the FanGraphs ToS; no redistribution |
| steamerprojections.com (S51) | Pre-season Steamer: hitters 2017-2024, pitchers 2018-2024 (page 1 of 2) | Free download, per the site | File format and license not stated |
| Tango's Marcel archive (S46) | Marcel forecasts 2001-2012 | Public web page | License not stated (NOT VERIFIED) |
| Self-computed Marcel | Any season with the study's data | Method is public (S46) | Preferred naive benchmark |
| ATC, THE BAT / THE BAT X, OOPSY, Depth Charts archives | None found | NOT VERIFIED | No public archive located |

**Answer.** Yes, in part. Archived Steamer (free from its site) and ZiPS/Steamer (FanGraphs membership) can be obtained for internal backtesting. Marcel can be regenerated exactly. We found no public archive of the aggregate or Statcast-heavy systems (ATC, THE BAT X, OOPSY, Depth Charts) and no terms that allow redistributing any raw projection file.

## 11. Implications for Paper 18

1. All seven systems use the core idea behind the paper's history-aware baseline: weight recent seasons more, regress toward a mean and adjust for age. The newer systems add Statcast or pitch-quality inputs: ZiPS after validation, THE BAT X, and OOPSY's Stuff+, barrel rate and swing speed. A metric that adds nothing beyond a strong history baseline in the study is therefore plausibly already priced into these systems.
2. Playing time is handled outside the rate models in most systems: RosterResource for ZiPS DC, OOPSY and Depth Charts, and manual edits for ATC. The study has no depth charts or injury reports, so any fantasy test must treat PA and IP forecasts separately and openly (see H8 in `hypotheses.md`).
3. The evaluations in section 8 disagree on what counts as accuracy. The paper can say it evaluates rate targets separately from fantasy categories, rather than claiming one "best projection".
