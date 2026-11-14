# Metric definitions and sources

**Accessed:** every page below was fetched on **2026-11-13**. The HTML was converted to text, and each quotation was copied from that text. Quotations are 25 words or fewer; all other wording is paraphrase.

**Citation IDs** (e.g., [I1], [B3]) refer to `references_verified.md`.

**"Does not capture / assumes"** lines are tagged:
- **[Source]:** stated on the cited page.
- **[Inference]:** my reading of the definition, not stated by the source.

---

## 1. wOBA (weighted on-base average)

**Sources:**
- FanGraphs Library, "wOBA" (Slowinski, 2010) [I1]: https://library.fangraphs.com/offense/woba/
- MLB Glossary [I14]: https://www.mlb.com/glossary/advanced-stats/weighted-on-base-average

**Definition**
- FanGraphs: "Weighted On-Base Average combines all the different aspects of hitting into one metric, weighting each of them in proportion to their actual run value."
- MLB: "wOBA is a version of on-base percentage that accounts for how a player reached base".

**Linear weights**
- "Exactly how much to weigh each of the components of wOBA was determined using linear weights." [I1]
- "These weights change on a yearly basis" [I1].
- Example weights (FanGraphs, 2013 season): wOBA = (0.690·uBB + 0.722·HBP + 0.888·1B + 1.271·2B + 1.616·3B + 2.101·HR) / (AB + BB − IBB + SF + HBP).
- MLB gives the same structure with "factor" weights over (AB + unintentional BB + SF + HBP).

**Scale to OBP:** "League average wOBA is always scaled to league average OBP" [I1]. FanGraphs converts wOBA to runs with wRAA = ((wOBA − lgwOBA) / wOBA scale) × PA.

**Does not capture / assumes**
- [Source, I1] wOBA "is context-neutral" (base-out state and score are ignored).
- [Source, I1] FanGraphs wOBA "is not adjusted for park effects".
- [Source, I1] Stolen bases and caught stealing are excluded: wOBA "only accounts for a player's production at the plate".

---

## 2. xwOBA (expected wOBA)

**Sources:**
- MLB Glossary [B3]: https://www.mlb.com/glossary/statcast/expected-woba
- Baseball Savant expected-statistics page [H4]: https://baseballsavant.mlb.com/leaderboard/expected_statistics
- Savant CSV documentation [H7]: https://baseballsavant.mlb.com/csv-docs

**Inputs:** "Expected Weighted On-base Average (xwOBA) is formulated using exit velocity, launch angle and, on certain types of batted balls, Sprint Speed." [B3]

**Computation**
1. **Per batted ball:** "every batted ball is given a single, double, triple and home run probability based on the results of comparable batted balls" [B3]. The comparison set covers balls since Statcast went league-wide in 2015.
   - "For the majority of batted balls, this is achieved using only exit velocity and launch angle." [B3]
   - "As of 2019, "topped" or "weakly hit" balls also incorporate a batter's seasonal Sprint Speed." [B3]
   - Statcast Search exposes the per-ball value as `estimated_woba_using_speedangle`, documented as "Estimated wOBA based on launch angle and exit velocity." [H7]
2. **Weighting:** the hit-type probabilities are valued with the same seasonal wOBA weights (factors) as standard wOBA [B3].
3. **Non-batted-ball events:** strikeouts, walks, and HBP are not modeled. xwOBA uses "a player's real-world data used for factors such as walks, strikeouts and times hit by a pitch" [B3]. Savant's wording: "By accumulating the expected outcomes of each batted ball with actual strikeouts, walks and hit by pitches" [H4].
   - [Inference] As in the wOBA formula, a strikeout adds zero to the numerator and one plate appearance to the denominator.
4. **Pitchers:** the same calculation gives expected xwOBA against [B3].

**Does not capture / assumes**
- [Source, H4] By design, "Expected Outcome stats help to remove defense and ballpark from the equation".
- [Inference] Batted-ball direction (spray or pull angle) is not among the listed inputs, so balls with the same exit velocity and launch angle get the same value wherever they are hit.
- [Inference] Sprint speed enters only for topped or weakly hit balls.
- [Inference] Because K, BB, and HBP are actual counts, xwOBA differs from wOBA only on batted balls.

---

## 3. FIP, xFIP, SIERA

### FIP (fielding independent pitching)

**Sources:**
- FanGraphs Library, "FIP" [I2]: https://library.fangraphs.com/pitching/fip/
- MLB Glossary [I15]: https://www.mlb.com/glossary/advanced-stats/fielding-independent-pitching

**Formula [I2]:** FIP = ((13·HR) + (3·(BB + HBP)) − (2·K)) / IP + constant
- "The constant is solely to bring FIP onto an ERA scale and is generally around 3.10."
- FIP constant = lgERA − (((13·lgHR) + (3·(lgBB + lgHBP)) − (2·lgK)) / lgIP)
- "The individual weights for home runs, walks/HBP, and strikeouts are based on the relative values of those actions with respect to run prevention."
- MLB gives the same formula. It says FIP "focuses solely on the events a pitcher has the most control over -- strikeouts, walks, hit-by-pitches and home runs".

**Does not capture / assumes**
- [Source, I2] FIP assumes the pitcher "were to have experienced league average results on balls in play and league average timing".
- [Source, I2] "FIP tells you about a subset of a pitcher's results."
- [Source, I2] "FIP is not league or park adjusted"; FIP- is the adjusted version.

### xFIP (expected FIP)

**Sources:**
- FanGraphs Library, "xFIP" [I3]: https://library.fangraphs.com/pitching/xfip/
- MLB Glossary [I16]: https://www.mlb.com/glossary/advanced-stats/expected-fielding-independent-pitching

**Definition [I3]:** developed "by Dave Studeman from The Hardball Times". It "replaces a pitcher's home run total with an estimate of how many home runs they should have allowed given the number of fly balls".

**Formula [I3]:** xFIP = ((13·(fly balls × lgHR/FB%)) + (3·(BB + HBP)) − (2·K)) / IP + constant. The constant is the same as FIP's.

**Caution:** the MLB Glossary prints "Fly balls / league average rate of HR per fly ball x 13". That divides where FanGraphs multiplies. Use FanGraphs' formula.

**Does not capture / assumes**
- [Source, I3] "xFIP may overestimate or underestimate a player's true talent level by assuming a league average HR/FB ratio."
- [Source, I3] "xFIP is not park or league adjusted."
- [Source, I3] "xFIP only dates back to 2002, the first year we have reliable HR/FB% data."

### SIERA (skill-interactive ERA)

**Sources:**
- FanGraphs Library, "SIERA" (2011) [I4]: https://library.fangraphs.com/pitching/siera/
- MLB Glossary [I17]: https://www.mlb.com/glossary/advanced-stats/skill-interactive-earned-run-average

**Definition**
- FanGraphs: "SIERA doesn't ignore balls in play, but attempts to explain why certain pitchers are more successful at limiting hits and preventing runs."
- MLB: "unlike a stat such as xFIP, SIERA considers balls in play and adjusts for the type of ball in play".

**Formula as printed by MLB [I17]:** 6.145 − 16.986(SO/PA) + 11.434(BB/PA) − 1.858((GB−FB−PU)/PA) + 7.653((SO/PA)²) +/− 6.664(((GB−FB−PU)/PA)²) + 10.130(SO/PA)((GB−FB−PU)/PA) − 5.195(BB/PA)((GB−FB−PU)/PA).
- The sign printed as "+/−" is ambiguous. Check it against Matt Swartz's formula, which FanGraphs links, before computing SIERA yourself.

**Does not capture / assumes**
- [Source, I4] "SIERA is technically a backward-looking ERA estimator and not a forward-looking projection system"
- [Source, I4] FanGraphs states that "SIERA is park-adjusted".
- [Inference] SIERA depends on batted-ball type classifications (GB, FB, PU), so it inherits their classification error.

---

## 4. K%, BB%, K−BB%

**Sources:**
- FanGraphs Library, "K% and BB%" for batters [I5]: https://library.fangraphs.com/offense/rate-stats/
- FanGraphs Library, "Strikeout and walk rates" for pitchers [I6]: https://library.fangraphs.com/pitching/rate-stats/
- MLB Glossary [I18], [I19]: https://www.mlb.com/glossary/advanced-stats/strikeout-rate and https://www.mlb.com/glossary/advanced-stats/walk-rate
- FanGraphs Stuff+ primer [B6]
- FanGraphs Library, "Sample size" [I11]: https://library.fangraphs.com/principles/sample-size/

**Batters [I5]:** K% = K / PA; BB% = BB / PA.

**Pitchers**
- [I6]: K% = strikeouts / batters faced; BB% = walks / batters faced.
- MLB defines K% as "total strikeouts divided by total batters faced" and BB% as "total walks divided by total batters faced".
- Why rates per batter rather than per nine innings: "worse pitchers will often face more batters per inning than better pitchers" [I6].

**Historical note [I5]:** "In the past, FanGraphs carried K% as K/AB." Then: "In 2011, K% was changed to K/PA."

**K−BB%:** strikeout rate minus walk rate, K% − BB%, on the same denominator.
- FanGraphs primer: "Strikeout minus walk rate is powerful as a rest-of-season predictor" [B6].
- [I6]: "The larger the spread between strikeout and walk rate, the more effective the pitcher."
- No FanGraphs Library or MLB Glossary page defining K−BB% on its own was found. The definition rests on these two statements.

**Reliability**
- Batters [I5]: "You don't need more than about 60 PA for K% or 120 PA for BB% before the numbers start to become meaningful".
- Pitchers: the sample-size page [I11] lists Carleton's cut points of 70 BF for K rate and 170 BF for BB rate.

**Does not capture / assumes**
- [Source, I5] "K% and BB% are not park, league, or context adjusted."
- [Source, I6] The pitching rates are not park-, league-, or season-adjusted either.
- [Inference] Neither page says whether intentional walks are included in BB. Check your data source's convention, because this changes BB% and K−BB% slightly.

---

## 5. Barrel and hard-hit rate

**Sources:**
- MLB Glossary "Barrel" [H1]: https://www.mlb.com/glossary/statcast/barrel
- MLB Glossary "Hard-hit rate" [H2]: https://www.mlb.com/glossary/statcast/hard-hit-rate

### Barrel [H1]

A barrel is a batted ball whose comparable balls (by exit velocity and launch angle) have produced at least a .500 batting average and a 1.500 slugging percentage since 2015 (paraphrase).
- "To be Barreled, a batted ball requires an exit velocity of at least 98 mph."
- At 98 mph, launch angles of 26–30° qualify; at 99 mph, 25–31°; at 100 mph, 24–33°.
- Each further mph widens the band by 2–3°, until 116 mph, where 8–50° qualifies.
- In 2016, barrels hit .822 with a 2.386 slugging percentage.

### Hard-hit rate [H2]

- "Statcast defines a 'hard-hit ball' as one hit with an exit velocity of 95 mph or higher".
- The rate is "the percentage of batted balls that were hit at 95 mph or more".

**Does not capture / assumes**
- [Inference] Hard-hit rate uses exit velocity only, so a 95 mph ground ball counts the same as a 95 mph line drive.
- [Inference] Barrel is a binary zone that ignores spray direction.
- [Inference] Rates can be computed per batted ball or per plate appearance. State which one is used.

---

## 6. Sprint speed

**Sources:**
- MLB Glossary [B4]: https://www.mlb.com/glossary/statcast/sprint-speed
- Savant sprint-speed leaderboard [H5]: https://baseballsavant.mlb.com/leaderboard/sprint_speed

**Definition**
- Savant quotes the definition as "feet per second in a player's fastest one-second window" [H5].
- MLB: sprint speed is measured as "how many feet per second a player runs in his fastest one-second window" [B4].
- Introduced in 2017. In 2018 it was updated to include top home-to-first times [B4].

**Qualifying runs [B4, H5]**
- Runs of two or more bases on non-homers, excluding a runner starting at second base when an extra-base hit occurs.
- Home-to-first runs on "topped" or "weakly hit" balls.
- "The best of these runs, approximately two-thirds, are averaged for a player's seasonal average." [B4]

**Scale [H5]**
- "The Major League average on a "competitive" play is 27 ft/sec".
- Competitive range is roughly 23 ft/s (poor) to 30 ft/s (elite).
- A "Bolt" is any run at or above 30 ft/s.
- Leaderboard listing requires at least 10 competitive runs.

**Does not capture / assumes**
- [Source, B4] "Approximately seven full-effort strides can be captured over the course of a one-second window". The metric rewards sustained top speed.
- [Inference] It does not measure acceleration, reaction time, or baserunning decisions.
- [Inference] Only the best runs are kept, which reduces the effect of effort but excludes most plays.

---

## 7. Outs Above Average (OAA)

**Sources:**
- MLB Glossary [H3]: https://www.mlb.com/glossary/statcast/outs-above-average
- Savant OAA leaderboard [H6]: https://baseballsavant.mlb.com/leaderboard/outs_above_average

**Definition**
- MLB: "Outs Above Average (OAA) is a range-based metric of skill that shows how many outs a player has saved."
- Savant: OAA is "the cumulative effect of all individual plays a fielder has been credited or debited with".
- Example: a play with a 25% out probability earns +0.75 if made and −0.25 if missed.

**Computation [H3]**
- **Outfielders:** based on Catch Probability, which uses the distance to the ball, the time available, and the direction of travel.
- **Infielders:** uses the distance to the intercept point, the time to get there, and the distance to the base the runner is heading to. On force plays, the runner's average sprint speed is used.
- "Prior to 2020, OAA was an outfield-only metric."
- Runs: "Runs Prevented is the position-based translation from outs saved to runs saved." [H6]

**Does not capture / assumes**
- [Source, H6] Statcast's overall Fielding Run Value combines "various metrics like OAA, blocking, framing, etc.", so OAA alone excludes catcher defense.
- [Source, I13] FanGraphs treats the arm component of Fielding Run Value as separate from OAA.
- [Source, H6] First basemen qualify at a lower threshold (one attempt per every other team game).
- [Inference] OAA exists only for the Statcast era; FanGraphs applies Statcast Fielding Runs Prevented from 2016 onward [I12]. The glossary's "Prior to 2020" describes when infield OAA was introduced, not necessarily the first season of infield data. Check Savant for the earliest infield season before using OAA as a feature.

---

## 8. Baseball-Reference WAR (bWAR, also rWAR)

**Sources:**
- B-Ref position-player WAR page [I23]: https://www.baseball-reference.com/about/war_explained_position.shtml
- B-Ref pitcher WAR page [I24]: https://www.baseball-reference.com/about/war_explained_pitch.shtml
- WAR download glossary [I25]: https://www.baseball-reference.com/about/war_explained_glossary.shtml
- Player-page column tooltips [I27]
- WAR explained [I22]
- Sports Reference blog WAR updates [I28–I32]

**Structure:** "WAR for position players has six components" [I23]:
1. Batting runs
2. Baserunning runs
3. Runs from grounding into double plays in DP situations
4. Fielding runs
5. Positional adjustment runs
6. Replacement-level runs

The first five are measured relative to league average.

### Rbat (batting runs) [I23]

- "For batting runs we use a linear weights system based on Tom Tango's wOBA (weighted on-base average) framework".
- Weights are league-season specific, and pitchers are excluded from league averages.
- Strikeouts are separated from other outs, and reached-on-error (ROE) runs are included: "ROE runs are now rolled into the batting runs".
- SB and CS runs are computed in wRAA, then "we subtract them out from the batting total and add them into the baserunning total".

### Rbaser (baserunning runs)

The B-Ref methodology page calls this "Rbr"; player pages label it "Rbaser". The download file column is `runs_br`.

- **Tooltip [I27]:** "Number of runs better or worse than average the player was for all baserunning events. SB, CS, PB, WP, Defensive Indifference."
- **Methodology [I23]:** it combines (a) SB and CS runs and (b) non-steal baserunning, such as "1st to 3rd on singles, outs on the bases, tagging up on fly balls, scoring from third on a ground ball".
- **Tracked events [I23]** include advances on hits, fly balls, and infield grounders. They also include "advances on defensive indifference, passed balls, wild pitches, balks, and pickoff errors", plus pickoff outs not scored as caught stealing.
- **Run values [I23]:** bases gained relative to league are worth "generally around .20 runs/base"; outs added cost "generally around .48 runs/out".
- **Coverage:** non-SB baserunning is estimated for the play-by-play era (the page says 1931 to the present).
- **Download glossary [I25]:** `runs_br` is "baserunning runs, includes SB and CS runs".

### Double plays are not in Rbaser

They are a separate component, Rdp (`runs_dp`).
- **Tooltip [I27]:** Rdp is the number of runs better or worse than average "at avoiding grounding into double plays".
- **Formula [I23]:** R_gidp = .44 × (GIDP_OPPS_player × GIDP_RATE_lg − GIDP_player).
- A GIDP opportunity is an infield ground ball with a runner on first, fewer than two outs, at least one out recorded, and no hit.
- **Implication for the paper:** a target built from `runs_br` alone excludes GIDP avoidance.

### Rfield (fielding runs)

- **Tooltip [I27]:** "Fielding of balls in play, turning double plays, outfield arms and catcher defense are all included."
- **Sources by era**
  - 2003 onward: Defensive Runs Saved. The tooltip reads "We use Baseball Info Solutions Defensive Runs Saved when available". B-Ref "switched to using Baseball Info Solutions Defensive Runs Saved for seasons since its introduction in 2003, and TZR for previous seasons" [I23].
  - Before 2003: Sean Smith's Total Zone Rating (TZR). From 1953 to 2002, TZR uses play-by-play; before 1953 it is estimated from other data [I23].
  - Negro League seasons: Defensive Regression Analysis (Humphreys), divided by 1.75 [I23].
  - Leagues with no fielding data get 0.
- **Framing**
  - The tooltip says "we do not use BIS catcher framing runs".
  - The methodology page's list of DRS factors still includes "Catcher handling of the pitching staff via things like pitch framing and pitch calling".
  - Treat framing as excluded, per the tooltip. [Inference: the methodology page appears out of date on this point.]
- **Recent changes (no switch to Statcast OAA found)**
  - Before the 2021 season, B-Ref updated DRS "with new figures from Sports Info Solutions that incorporate more accurate hit timing data" [I29].
  - The 2022 update fixed how those figures fed the pitcher defense adjustment [I29].
  - In March 2025: "SIS has provided us with an update to figures from 2015 through 2024" [I31].
  - The 2024 and 2026 updates changed park factors, Retrosheet data, and player identifications, not the fielding source [I30, I32].
  - The 2019 update added openers and three-year park factors, and expanded catcher defense for 1890–1952 [I28].
- **Data vintage:** `runs_field` for 2015–2024 changed in March 2025. Park factors are recomputed each spring. Record the download date of the war_daily files.

### Rpos (positional adjustment)

Tooltip [I27]: "Positions like C, SS, and 2B get a bonus. Positions like 1B, DH, LF get a penalty."

### Rrep (replacement runs)

- Tooltip [I27]: "Number of runs an average player is better than a replacement player. Replacement is set for a .294 team winning percentage."
- This gives 30 × 162 × (.500 − .294) = 1,000 WAR per season [I23].

### Pitcher bWAR [I24]

- **Base:** "our pitching WAR calculation requires only overall Runs Allowed (both earned and unearned) and Innings Pitched."
- **Expected runs:** expected runs (xRA) are based on the opposing offenses faced, neutralized for park.
- **Defense adjustment:**
  - The team's defensive runs saved is allocated by the pitcher's share of balls in play: xRA_def = (BIP_pitcher)/(BIP_team) × TeamDefensiveRunsSaved.
  - The team figure uses "Baseball Info Solutions' Runs Saved from 2003 on and Total Zone before 2003".
- **Other adjustments**
  - Starter and reliever averages differ ("for recent years we set this difference league-wide at .1125 runs/game").
  - The park factor is pitcher-specific, weighted by appearances in each park [I22]. B-Ref uses "a three-year average for park factors when computing pitching WAR" [I29].
  - Leverage applies to relievers only [I22].

**Does not capture / assumes**
- [Source, I24] B-Ref measures "the value of the recorded performance--not its repeatability". Sequencing and balls in play stay charged to the pitcher, apart from the team-level defense adjustment.
- [Source, I22] "you should not take any full-season difference between two players of less than one to two wins to be definitive".
- [Inference] The pitcher defense adjustment assumes team-average defense behind every ball in play.

---

## 9. bWAR versus fWAR

**Sources:**
- FanGraphs "WAR for pitchers" [I8]
- FanGraphs "WAR for position players" [I9]
- FanGraphs "fWAR, rWAR, and WARP" [I10]
- FanGraphs WAR updates [I12, I13]
- MLB Glossary WAR [I21]
- B-Ref [I22, I26]

**Pitchers**
- FanGraphs: "FanGraphs' main WAR for pitchers is based on FIP with infield flies counted as strikeouts." [I8]
  - ifFIP = ((13·HR) + (3·(BB + HBP)) − (2·(K + IFFB))) / IP + ifFIP constant.
  - ifFIP is rescaled to RA9 and divided by a FIP-based park factor. Runs per win are pitcher-specific.
  - Replacement level is 0.03 wins per game for relievers and 0.12 for starters. A reliever leverage multiplier is (1 + gmLI)/2.
  - RA9-WAR is offered as an alternative [I8].
- Baseball-Reference: FanGraphs describes B-Ref's approach this way: "Baseball-Reference uses a pitcher's runs allowed and then adjusts that value based on the overall quality of their defense that year." [I10]
- MLB: "fWAR uses FIP in determining pitcher WAR, while bWAR uses RA9" [I21].

**Shared scale:** both sites use a .294 replacement level (1,000 WAR per season). B-Ref adopted it in March 2013 "after deciding with FanGraphs.com to set a single replacement level between our sites" [I22]. FanGraphs splits WAR 57% to position players and 43% to pitchers [I8].

**Position players**
- **Batting:** FanGraphs uses wOBA/wRAA [I9]. B-Ref uses its modified wRAA.
- **Baserunning**
  - The FanGraphs Library gives BsR = UBR + wSB + wGDP [I9].
  - Since April 2024, retroactive to 2016: "Ultimate Base Running and Weighted Grounded into Double Play Runs have been replaced with Statcast's baserunning metric (labeled XBR)" [I13].
  - B-Ref keeps Rdp separate from Rbaser.
- **Fielding**
  - FanGraphs used UZR from 2002 and Total Zone before that [I10]. In 2022: "Retroactive to the 2016 season, we have swapped out the Range component of UZR for the Statcast metric Fielding Runs Prevented" [I12].
  - In 2024, FanGraphs replaced the arm, catcher-throwing, and blocking inputs with Statcast Fielding Run Value components and removed UZR double-play runs. All retroactive to 2016 [I13].
  - B-Ref uses DRS from 2003 and TZR before that.
- **Note:** B-Ref's comparison chart [I26] still lists fWAR fielding as UZR after 2002, which is out of date.

**Does not capture / assumes**
- [Source, I10] "Positional player WAR values typically only differ dramatically when the various systems disagree about a player's defense."
- [Source, I10] For pitchers, the two differ by design: FIP ignores balls in play and sequencing, while B-Ref "starts with runs allowed and works backwards."

---

## 10. FanGraphs Stuff+, Location+, Pitching+

**Sources:**
- FanGraphs Library primer (McGrattan, 2023-03-10) [B6]: https://library.fangraphs.com/pitching/stuff-location-and-pitching-primer/
- Launch post (Appelman, 2023-03-10) [H8]: https://blogs.fangraphs.com/pitchingbot-and-stuff-pitch-modeling-are-now-on-fangraphs/

**Who built it [B6]:** "Eno Sarris and Max Bay created Pitching+". Sarris and McGrattan maintain the model.

**Stuff+ [B6]**
- "Stuff+ looks only at the physical characteristics of a pitch."
- "Important features include, but are not limited to, release point, velocity, vertical and horizontal movement, and spin rate."
- Secondary pitches are judged relative to the pitcher's primary fastball. The model also includes "axis differential" (seam-shifted wake).
- "Stuff+ was trained against run values". It uses a decision-tree-based model.

**Location+ [B6]:** "Location+ is a count- and pitch type-adjusted judge of a pitcher's ability to put pitches in the right place." It uses no physical characteristics.

**Pitching+ [B6]**
- "The overall model, Pitching+, is not just a weighted average of Stuff+ and Location+".
- It is a third model that uses physical characteristics, location, count, and batter handedness.

**Scale and reliability [B6]**
- "10 points of Stuff+, Location+ and Pitching+ is a standard deviation on the pitch level".
- Location+ is centered at 100 for each pitch type. Stuff+ averages differ by pitch type (four-seamers 99.2, sliders 110.8 in the primer's table).
- "Stuff+ becomes reliable 80 pitches into the season". Location+ takes about 400 pitches.

**Not the same as Driveline's Stuff+ [B5]**
- Driveline's model "filters out plate locations (thus characteristics of command which is measured in a separate metric)".
- On Driveline's scale, "100" means league average "relative to other pitches thrown in that pitch type bucket".
- Name the model explicitly when citing Stuff+.

**Does not capture / assumes**
- [Source, B6] Stuff+ excludes location and command.
- [Source, B5] Driveline: "Stuff+ isn't concerned with command nor targeting strategy".
- [Source, B6] Release point matters, which "suggests that Stuff+ includes some deception".
- [Source, B6] Training on run values builds in an assumption that pitchers have some control over contact quality.
- [Inference] Values depend on the model version and are not comparable across providers.

---

## 11. wRC+ (weighted runs created plus)

**Sources:**
- FanGraphs Library, "wRC and wRC+" [I7]: https://library.fangraphs.com/offense/wrc/
- MLB Glossary [I20]: https://www.mlb.com/glossary/advanced-stats/weighted-runs-created-plus

**Definition**
- [I7]: "League average for position players is 100, and every point above 100 is a percentage point above league average."
- [I7]: wRC+ "is park and league-adjusted".
- MLB: "A wRC+ of 100 means a league-average hitter".

**Formulas [I7]**
- wRC = (((wOBA − lgwOBA)/wOBA scale) + lgR/PA) × PA
- wRC+ = (((wRAA/PA + lgR/PA) + (lgR/PA − PF × lgR/PA)) / (AL or NL wRC/PA, excluding pitchers)) × 100

**Does not capture / assumes**
- [Source, I7] wRC and wRC+: "Neither adjusts for position".
- [Source, I7] Both are context-neutral.
- [Source, I7, I1] wRC+ inherits wOBA's exclusion of baserunning.

---

## Appendix: "stabilization" as used for K%, BB%, and similar rates

**Source:** FanGraphs Library "Sample size" [I11], which summarizes Carleton [D8–D10].

- Carleton's cut point is the sample size at which "the correlation between that sample and another sample of the same size is 0.7" (R² ≈ .49).
- The page cautions: "A statistic doesn't stabilize, it becomes more stable."
- Cut points for batters: K rate 60 PA, BB rate 120 PA, HR rate 170 PA, OBP 460 PA, BABIP 820 BIP.
- Cut points for pitchers: K rate 70 BF, BB rate 170 BF, BABIP 2,000 BIP.
