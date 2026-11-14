# Fantasy scoring conventions: verified platform defaults

Prepared for Sloan 2027 Paper 18 ("One Metric, Different Jobs"), fantasy reframing.
Every page below was accessed on **2026-11-13**. Source IDs (S01...) refer to `research_sources.md`.

**Rules used in this file**
- An exact number appears only if it was read on a page fetched on 2026-11-13.
- "NOT VERIFIED (could not access)" means the page would not load or render.
- "NOT VERIFIED" alone means the page loaded but did not state the value.
- Lines marked **[our arithmetic]** are derived by us from verified tables. They are not platform statements.

---

## 0. Quick reference

| Platform / product | Default format | Teams | Active lineup | Categories (roto / H2H-cats) | Points system |
|---|---|---|---|---|---|
| Yahoo (S01, S02) | H2H Points for newly created leagues (confirmed) | Max 10 (public), 12 (public prize, private) | 22 active (C, 1B, 2B, 3B, SS, 3 OF, 2 Util, 2 SP, 2 RP, 4 P) + 5 BN + 4 IL | R, HR, RBI, SB, AVG / W, SV, K, ERA, WHIP | See section 1.4 |
| ESPN standard (S03, S04, S05) | Several formats offered; no single default stated on fetched pages | 10 (S04) | 16 starters + 3 bench (+ up to 3 IL) | R, HR, RBI, SB, AVG / K, W, SV, HD, ERA, WHIP (5x6) | See section 2.2 (wins value conflicts) |
| NFBC Main Event (S06) | 5x5 rotisserie, league plus overall contest | 15 | 23 active + 7 reserve = 30 | R, HR, RBI, SB, AVG / K, W, SV, ERA, WHIP | None |
| FanGraphs Auction Calculator (S09, S10) | Live tool NOT VERIFIED (could not access) | 12 (documented 2022) | 2 C in default (documented 2022); full roster NOT VERIFIED | Hitting cats in 2022 example: AVG, R, HR, RBI, SB; pitching NOT VERIFIED | Points mode with presets exists |
| CBS free leagues (S07) | Roto (3 variants) and weekly H2H points | 10 | H2H 16; Roto 23 | 5x5: AVG, HR, RBI, SB, R / ERA, W, SV, WHIP, K | See section 5 |

---

## 1. Yahoo

### 1.1 Do newly created 2026 leagues default to H2H points? CONFIRMED.
- The 2026 Yahoo guide (S02, Yahoo Sports Fantasy Staff, published 2026-02-10) says: "Default scoring in all newly-created leagues will be Head-to-Head Points".
- The same article says: "This will be the standard across all new leagues, but private-league commissioners can change their scoring settings".
- The Yahoo Help page (S01) says: "The default Private League scoring type selected is Head-to-Head Points".
- Scope note: S01 gives separate settings blocks for Public H2H Points, Public H2H Categories and Public Rotisserie, so a public-league player picks a format queue. S02 also says public leagues still offer H2H Categories and Rotisserie.
- Neither page gives a reason for the change (S02 was checked for one).

### 1.2 Default league settings (S01; page shows no "last updated" date; its settings refer to the 2026 season)

| Setting | Value read on S01 |
|---|---|
| Max teams | Public 10; Public Prize 12; Private 12 |
| Roster positions (all league types) | C, 1B, 2B, 3B, SS, OF, OF, OF, Util, Util, SP, SP, RP, RP, P, P, P, P, BN x5, IL x4 (27 slots) |
| Draft | Live Standard Draft (S02: snake, 23 rounds by default) |
| Max acquisitions per week (H2H formats) | 6 |
| Minimum innings per team per week (H2H formats) | 20 |
| Playoffs (H2H formats) | 6 teams, weeks 24-26, ending September 27 (2026) |
| Rotisserie caps | Public: 162 games per position slot / 1,400 IP; Private: no games maximum / 1,400 IP |
| Scoring window (Roto, Season Points) | March 25, 2026 (if drafted before then) to September 27, 2026 |
| Trade end date | August 6, 2026 |

S02 describes the same 22-starter, 5-bench, 4-IL layout "in a 10-team league".

### 1.3 Default categories (S01): H2H Categories, H2H One Win, Rotisserie
- Batting: Runs, Home Runs, RBI, Stolen Bases, Batting Average.
- Pitching: Wins, Saves, Strikeouts, ERA, WHIP.

### 1.4 Default H2H Points (and Season Points) weights (S01; identical in S02 and in the S08 comparison table)

| Batters | Points | Pitchers | Points |
|---|---|---|---|
| Single (1B) | 2.6 | Win (W) | 8 |
| Double (2B) | 5.2 | Save (SV) | 8 |
| Triple (3B) | 7.8 | Strikeout (K) | 3 |
| Home run (HR) | 10.4 | Earned run (ER) | -3 |
| Run (R) | 1.9 | Out recorded | 1 |
| RBI | 1.9 | Walk allowed (BB) | -1.3 |
| Walk (BB) | 2.6 | Hit allowed (H) | -1.3 |
| Stolen base (SB) | 4.2 | Hit batter (HBP) | -1.3 |
| Hit by pitch (HBP) | 2.6 | | |

There is no batter strikeout penalty, caught-stealing penalty, loss penalty, hold credit or quality-start credit in the Yahoo default.

### 1.5 What the Yahoo weights imply [our arithmetic]
- Batting points = 2.6 x (total bases + BB + HBP) + 1.9 x (R + RBI) + 4.2 x SB, because 5.2, 7.8 and 10.4 are exactly 2, 3 and 4 times 2.6.
- Outs made by a batter cost nothing, so extra plate appearances can only add points. This makes playing time mechanically important (relevant to H8 in `hypotheses.md`).
- A pitcher strikeout that records an out earns 3 + 1 = 4 points. An inning earns 3 points from outs. A walk, hit or hit batter costs 1.3 points each.

### 1.6 Coverage by the study's variables [our check]
- Batters: all inputs are present. Singles = H - 2B - 3B - HR.
- Pitchers: outs = innings converted from the .1/.2 notation to thirds. **Hit batters allowed are not in the study's pitcher variable list**, so Yahoo pitcher points can be computed only without the -1.3 HBP term. Document this as a known omission.

---

## 2. ESPN

### 2.1 Default categories
- S03 (ESPN Fan Support, "Standard Scoring for Public Baseball leagues", updated 2026-11-09 20:12) lists these for Most Categories, Each Category and Rotisserie leagues: batting R, HR, RBI, SB, AVG; pitching K, W, SV, HD (holds), ERA, WHIP.
- S04 (Tristan H. Cockcroft, ESPN, 2026-01-27) says: "ESPN's standard for Roto is 5x6, adding holds to the 5x5 categories above." It says H2H Each Category uses the same 11 categories.
- A companion support page ("Scoring Formats", updated 2026-11-09 19:34; listed with S03) says standard leagues offer five formats. It calls Rotisserie and H2H Each Category the most commonly used. It does not name one default.

### 2.2 Default points weights: three sources agree except on wins

| Stat | S03 support page (updated 2026-11-09) | S04 ESPN primer (2026-01-27) | S08 FantasyPros table (2026-01-24) |
|---|---|---|---|
| Batting: R | 1 | 1 | 1 |
| Batting: total bases (TB) | 1 per base | 1 per base | 1B 1, 2B 2, 3B 3, HR 4 |
| Batting: RBI | 1 | 1 | 1 |
| Batting: BB | 1 | 1 | 1 |
| Batting: strikeout | -1 | -1 | -1 |
| Batting: SB | 1 | 1 | 1 |
| Pitching: IP | 3 | 3 | 3 |
| Pitching: H allowed | -1 | -1 | -1 |
| Pitching: ER | -2 | -2 | -2 |
| Pitching: holds | 2 | 2 | 2 (placement in table inferred) |
| Pitching: BB allowed | -1 | -1 | -1 |
| Pitching: K | 1 | 1 | 1 |
| **Pitching: W** | **5** | **2** | **5** |
| Pitching: L | -2 | -2 | -2 |
| Pitching: SV | 5 | 5 | 5 |

**Conflict on wins (unresolved).** S05 (ESPN, 2023-01-19) says of newly created standard leagues: "Wins, previously worth five points, will now be worth two apiece". S04 (2026) also lists 2. S03 (support page, updated 2026-11-09) and S08 list 5. S03 is titled for **public** leagues, while S04 and S05 describe ESPN "standard" leagues. Which value a newly created private league gets today is NOT VERIFIED. **Recommendation:** report ESPN points results for W = 2 and W = 5.

### 2.3 League size and roster
- S04: "with 10 teams of 16 starters and three bench players apiece", plus up to three injured-list spots.
- S05 (2023 change, still described as current by S04's 16-starter count): one each of C, 1B, 2B, 3B, SS, three OF and one DH/utility, plus seven pitchers. Rosters are 19 players with three bench spots.
- S04's own position sentence lists "three outfielders and three pitchers", which does not add up to 16. We rely on S05 for position counts. Status: partially verified.

### 2.4 Coverage by the study's variables [our check]
- Batters: TB is derivable. The batter strikeout count is needed; use raw K if stored, otherwise K% x PA. Fully computable.
- Pitchers: **losses are not in the study's pitcher variable list.** Holds are present. ESPN pitcher points can be computed only without the L term, and W must be run at both 2 and 5.

---

## 3. NFBC Main Event (S06)

Source: NFBC rules page for the Main Event (`nfc.shgn.com/rules/2813`). On 2026-11-13 it showed the **2027** season, with scoring periods from Wednesday 3/24/2027 to Sunday 9/26/2027.

| Item | Value read on page |
|---|---|
| Entry fee | $1,800 single entry |
| Teams per league | 15 |
| Draft | Snake, 30 rounds; draft order by "Kentucky Derby Style" preferences |
| Active roster (23) | C 2, 1B 1, 2B 1, SS 1, 3B 1, OF 5, CI 1, MI 1, UT 1, P 9 |
| Reserves | 7 (30 total; the NFBC FAQ also says "The maximum roster limit at all times is 30, with 23 players always active.") |
| Categories (roto) | Runs, Home Runs, RBI, Stolen Bases, Batting Average, Strikeouts, Wins, Saves, ERA, WHIP |
| Standings | League standings plus "a roto style overall competition" across all Main Event teams |
| Lineups | Weekly, with Monday locks; reserve hitters may be swapped in on Fridays |
| Innings minimum | 950 IP; a team below it gets 1 point in ERA and in WHIP |
| Prizes | League: $7,500 / $3,700 / $1,800; Overall: $200,000 / $50,000 / $30,000 |

**Conflict on in-season acquisitions (unresolved).** The 2027 rules page says "There are no free agent pickups in Main Event Leagues." It also bans trades. The NFBC FAQ, however, describes an imaginary $1,000 FAAB budget spread over 27 weeks for NFBC leagues. A FanGraphs study (Zimmerman, 2018-07-21, listed in S06) analyzed Main Event FAAB bids against a $1,000 budget. The 2027 Online Championship page also says "NO FREE AGENT ACQUISITIONS", so the 2027 pages may be an unfinished template. Treat the 2027 FAAB rule as NOT VERIFIED. Categories, teams and roster are consistent across sources.

---

## 4. FanGraphs Auction Calculator (S09, S10, S55)

### 4.1 Live tool: NOT VERIFIED (could not access)
On 2026-11-13, `https://www.fangraphs.com/fantasy-tools/auction-calculator/` rendered only tab names and an empty table ("Loading..."). The settings are drawn by JavaScript, and an automated request for the page script returned a bot-check page. No current default could be read.

### 4.2 Most recent documented defaults
- Lucas Kelly (FanGraphs, 2022-02-07; S09) describes a "12-team, 2 catcher league (the default settings of the calculator)".
- In the same article, the worked example uses Steamer projections. Its calculator link carries `dollars=260`, and a $1 minimum bid is added to every player. Experimental Mode is off by default.
- That example's hitting categories are AVG, RBI, R, SB and HR. Its hitter pool is 14 batters per team plus 6 hitter bench spots, about 240 hitters for 12 teams.
- **NOT VERIFIED for 2026/2027:** default pitching categories, full roster and bench counts, default hitter/pitcher dollar split, and the current default projection system.

### 4.3 How value and replacement level are computed (as documented)
1. **Category scores.** Each category gets a z-score: the player's projection minus the player-pool mean, divided by the pool's standard deviation. The calculator chooses the pool by an optimization (S09).
2. **Total.** PTS is the sum of the category z-scores (S09).
3. **Replacement level by position.** aPOS is a positional adjustment set from the last rosterable player at each position. In effect it sets replacement level per position (S09). An Ottoneu forum poster described aPOS as "a positional replacement level proxy" (S55, community reading, 2016).
4. **Dollars.** Dollars = PTS + aPOS + the $1 minimum bid (S09). David Appelman described the method as "pretty similar to the Last Player Picked methodology" (S10, 2015).
5. **Bench equals replacement.** Johnson (S10, 2016) says bench slots act as replacement level; bench players are treated as worth about $1 or less regardless of position.
6. **Other documented options (S10):**
   - An experimental mode fills in replacement-level stats for players with incomplete playing time. Kelly (S09) says this applies to hitters projected under 600 PA.
   - A minimum-innings setting assumes 150 IP per starting pitcher and 50 IP per reliever.
   - A relief-pitcher value adjustment exists because holds are not projected.
   - A Points mode has Ottoneu presets. A total-bases category was added for points leagues, and quality starts are folded into wins in some setups.
7. Ariel Cohen's projection comparisons (S48) use his own z-score calculator with NFBC Main Event settings ($260 budget). Those are not FanGraphs defaults.

---

## 5. CBS (S07)

Source: "2026 CBSSports.com Free Fantasy Baseball Leagues Terms" (CBS Sports). The page has no publication date. It covers the 2026 season (March 25 to September 27, 2026); the footer reads "© 2004-2025". The points table on the page is flattened, so we matched our column reading against the S08 table, and the two agree. S08 does not list the CS value.

- **League size:** 10 teams. H2H leagues have two divisions of five.
- **H2H roster:** 21 players drafted; 16 active (C 1, 1B 1, 2B 1, 3B 1, SS 1, OF 3, U 1, SP 5, RP 2); 2 IL spots.
- **Roto roster:** 29 players drafted; 23 active (C 2, 1B, 2B, 3B, SS, OF 5, MI, CI, U, P 9); 2 IL spots. Roto leagues require at least 5 active pitchers. A first-place team in a category earns 10 points and last place earns 1.
- **Roto category sets:**
  - Traditional: AVG, RBI, HR, SB; ERA, W, SV, WHIP.
  - 5x5: Traditional plus R and K.
  - Roto-Plus: OBP, SLG, R, RBI; W, SV, ERA, WHIP.
- **Default H2H points:**

| Batting | Points | Pitching | Points |
|---|---|---|---|
| Single | 1 | Inning pitched | 3 |
| Double | 2 | Strikeout | 0.5 |
| Triple | 3 | Win | 7 |
| Home run | 4 | Loss | -5 |
| RBI | 1 | Save | 7 |
| Run | 1 | Quality start | 3 |
| Walk | 1 | Earned run | -1 |
| Stolen base | 2 | Hit allowed | -1 |
| Strikeout | -0.5 | Walk allowed | -1 |
| Caught stealing | -1 | Hit batter | -1 |
| Hit by pitch | 1 | | |

**Coverage by the study's variables [our check].** Quality starts (game-level), losses and pitcher hit batters are not in the study's pitcher variables, so CBS pitcher points can only be computed in part. CBS batter points can be computed in full, since CS is available.

---

## 6. Cross-platform facts that matter for Paper 18

1. **None of the six study targets is a scoring category.** None of wOBA, FIP, baserunning run value, fielding run value, hitter bWAR/600 PA or pitcher bWAR/200 IP appears on any platform list above (S01, S03, S06, S07).
2. **Pitcher strikeouts are worth very different amounts relative to an inning (3 points on all three platforms)** [our arithmetic]:
   - Yahoo: 3 per K.
   - ESPN: 1 per K.
   - CBS: 0.5 per K.

   So strikeout skill (K%, K-BB%, Stuff+) should matter far more for Yahoo points than for CBS points.
3. **Batter strikeouts** cost 0 on Yahoo, -1 on ESPN and -0.5 on CBS [our arithmetic from the tables].
4. **A stolen base**, measured in singles, is worth about 1.6 singles on Yahoo (4.2 / 2.6), 1 on ESPN and 2 on CBS. In 5x5 roto, SB is 1 of 10 categories [our arithmetic].
5. **Holds** score only in ESPN defaults (points and the 5x6 categories).
6. **Recommended reporting set for the fantasy experiment:**
   - (a) Yahoo default 5x5 roto, 10- and 12-team.
   - (b) Yahoo default H2H points, without the pitcher HBP term.
   - (c) ESPN points with W = 2 and W = 5, without the L term.
   - (d) CBS points as a partial sensitivity (no QS, L or pitcher HBP).
   - (e) NFBC-style 15-team 5x5 roto with 23 active players and a 950 IP minimum.
