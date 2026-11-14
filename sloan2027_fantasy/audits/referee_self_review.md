# Referee self-review: "One Metric, Different Jobs" (Paper ID 18, Baseball track)

**Manuscript reviewed:** `sloan2027_fantasy/paper/sloan_2027_fantasy_revised_proof.pdf` (blind proof, 28 pp., built 2026-11-13 16:48 PST), compared against the named proof, the accepted abstract (`app/content/study_notes.md`), the fantasy-bridge protocol (`sloan2027_fantasy/fantasy/experiment_protocol.md`), the claims ledger (`paper/claims_to_evidence.csv`), every `fantasy/*.csv`, every `figures/data/*.csv`, and the six-target artifacts in the PSL worktree (`/Users/Shirin/Future_Predictor/.worktrees/sloan-2027/sloan2027/...`, abbreviated `PSL/sloan2027/...` below).

**Stance:** skeptical MIT Sloan SSAC 2027 referee. Page numbers refer to the blind proof. No file other than this report was modified, and git was not run. Where I say "my re-analysis", I used the project's own prediction files; the method is in the final section so the author can check it.

---

## 1. Summary assessment

The paper asks a good question: which public metrics should change a next-season forecast once a model knows a player's history, and does that matter for fantasy categories? It does several things most Sloan submissions do not:

- it reruns the selection inside each training window (nested validation);
- it scores broad regularized competitors on identical rows;
- it pre-specifies a fantasy test with Holm-adjusted primary linkages;
- it keeps a claims ledger and a 2026 frozen-in-workflow check;
- it reports its own failures (hitter WAR, exit velocity → WAR, the 2026 FIP reversal).

The fantasy framing, the front-office caveat (§10.4) and the public-data compression section (§10.5) answer the earlier feedback well.

The manuscript is still not ready. Several statements are factually wrong when checked against the project's own outputs:

- §5.4: the K%/K-BB% mechanism;
- §6.5: which ablations changed error;
- §10.6: what the baseline contains;
- the Figure 4 caption, and the FIP pattern described in §6.3.

Material weaknesses of the canonical pipeline that the project's own audits mark "must be disclosed" are missing from the paper. The headline "admitted metrics" gains are partly three-year target history, not new public metrics. Season-level uncertainty is understated, and at the season level the primary verdicts flip. Several Discussion recommendations rest on analyses the paper never ran.

Most of these can be fixed with existing outputs plus a few targeted reruns before the 2026-12-01 deadline.

| Criterion | Score (1–5) | Reasons |
|---|---|---|
| Novelty | **3** | The ingredients (incremental validity, nested time-ordered validation) are established, and the paper rightly claims only the combination. The genuinely new piece is the pre-specified two-stage test: target forecast → fantasy category. Its main findings mostly confirm existing practice: FIP-type skill helps ERA/WHIP by about 1%; WAR mostly signals playing time; correlation is not incremental information. The two findings that challenge practice ("Stuff+ cannot condemn bad stuff"; "sell-high beats buy-low") are confounded (M9). |
| Academic rigor / validity | **2** (as submitted; **4** is reachable) | Strong design elements are undercut by specific problems: a baseline weaker than a naive three-year projection, with "admitted metrics" counted as public-metric gains (M1); season effects (M2); a wrong mechanism in §5.4 (M3); undisclosed canonical flaws (M4); misreported ablations and an omitted pre-specified sensitivity (M6); a survivorship confound (M9); overclaims (M7, M8). |
| Reproducibility | **4** | Excellent: claims ledger, checksums, 71 tests, 55/55 checks, rebuild scripts, a protocol with amendments, and a lawful no-redistribution policy. Gaps: park factors come from external code that cannot be audited; result-guard assertions sit in the canonical code (M4); tuning grids, bootstrap details and family definitions are not in the paper (m3, M3); the protocol commit hash is not printed (M5). |
| Application (fantasy and public analysts) | **3** | Explicitly fantasy-facing and well researched (§3), with declared formats and usable rules. However, effects are about 1% of RMSE. The draft backtest finds no detectable improvement in picks. z-units are never scaled. Two headline recommendations (spend effort on playing time; pay a premium for FIP skill) are untested (M7, M10). |

### 1.1 Forbidden-claims check

| Forbidden claim | Present? | Where | Required action |
|---|---|---|---|
| "the six targets are fantasy scoring categories" | No. Explicitly negated (§2 p3: "None of the six is a standard fantasy scoring category"; §8.1 p15) | — | None |
| "fantasy players will win more" | Not stated. Negated in the abstract, §8.5 and §10.1 | But §10.1 p20 "worth a modest premium" and "Spend the most effort on playing time" imply decision gains that were not shown | Reword (M7a, M7c) |
| "MLB organizations can deploy this as-is" | Not in the new text (§10.4 disclaims) | The verbatim accepted abstract (App. A p23) says "For baseball operations, this framework provides a reproducible way to decide…", and Table 7 does not mark it withdrawn | Add a Table 7 row: "withdrawn" (M12) |
| "the 2026 holdout was truly prospective" | Not stated. §5.5 and §11 say retrospective | Abstract p1 and the §1 bullet p2 say only "frozen before outcomes were downloaded", with no "retrospective" | Add "retrospective" (M11) |
| "the framework handles any metric and any target" | **Quoted in order to reject it**: §9 p19, "…more honest portability claim than 'the framework handles any target'" | §9 | Remove the phrase entirely (m14) |

### 1.2 Required items: status

| Requirement | Status | Issue |
|---|---|---|
| Mandatory "Why These Six Prediction Targets?" (construct, why chosen, fantasy relevance, limits, for each target) | Present (Table 1 covers all six), but thin and partly post hoc; construct details missing | M14 |
| "Unstable" defined operationally | Met (Table 4); a fifth, undefined use of "stable" remains | m6 |
| No business-style jargon | Mostly met; some residue | m17 |
| Graphics carry the argument | Partly; concrete defects in Figs 1, 3, 4, 6, 7 | M15 |
| Precise statements about what the model does | Partly | M7f, M7g, M7n |
| Real fantasy practice, with sources | Largely met in §3; Table 2 rows have no in-table citations and some tests do not match their beliefs | M8 |
| Front-office limits | Met (§10.4); Table 7 does not withdraw the operations claim | M12 |
| Public-data compression | Met (§10.5) | — |
| Real Discussion, not a recap | Met structurally; content errors; no fantasy-terms translation | M7, m18 |
| Baseball units instead of RMSE decimals | Partly: six-target results are % only, and Table 5 still prints raw decimals | M13 |
| Named players in both directions, including failures | Partly: two pitchers, one metric | M13 |
| K% vs K-BB% explained | Present, but the mechanism is wrong and a number is inconsistent | M3 |

---

## 2. Major issues

### M1. "Admitted metrics" partly means a longer history of the target itself; the baseline is weaker than claimed; the Projection count includes the baseline's own inputs

**Location.**
- Abstract p1 (sentence beginning "Re-running the whole selection…").
- §1 p1 framing ("once a sensible model already knows his recent record").
- §5.1 p7 ("the target's own two-year history").
- §6.2 heading p10 ("Admitted metrics improve strong baselines").
- §8.4 p18 ("The public metrics admitted for FIP and wOBA therefore carry some fantasy information beyond history").
- §10.6 p21: "Weak baselines. The history baselines are strong (two- and three-year weighted rates, age, playing time, park)".
- Table 3 p8 ("Projection … 27") and Figure 2 ("Projection (statistical pass)").

**Problem.**
- **The baseline holds only two-year history.** The nested baselines (`PSL/sloan2027/results/nested/admission/*_T20xx_default_meta.json`, key `baseline`) contain only two-year history (`woba_w2`, `fip_w2`, `br_rv_rate_w2`, `def_rv_rate_w2`, `war_rate_w2`) plus age, playing time and park, role or position.
- **Three-year history is a candidate, and it gets admitted:**
  - `woba_w3` for wOBA, in all six windows;
  - `br_rv_rate_w3` for baserunning, in all six;
  - `def_rv_rate_w3` for fielding: the only admitted input in 2022–2026, with nothing admitted in 2021.
- **The fielding gain is history alone.** The fielding gain in the abstract (−1.0% [−1.6, −0.3]) comes entirely from using three seasons of fielding history instead of two. Part of the wOBA and baserunning gains is the same thing.
- **Pitcher WAR uses standard stats.** Its admitted inputs are `fip_w2` (2021) and then `k_bb_pct_w2`: standard statistics, not "public metrics" in the Statcast sense the introduction sells.
- **§10.6 is factually wrong.** §6.2 does disclose the three-year selections, but §10.6 then states that the baseline itself contains three-year rates.
- **The baseline is shorter than Marcel's.** Marcel, which §3.2 calls "the deliberately naive benchmark", already uses three seasons (5/4/3). The practice-audit plan (`fantasy/hypotheses.md` §0.2: "At minimum, include a Marcel replica") is not reported.
- **Six of the 27 canonical Projection rows are baseline inputs** (`PSL/sloan2027/tables/table7_reason_codes_208.csv`): `woba_w2`, `fip_w2`, `br_rv_rate_w2`, `def_rv_rate_w2`, and `war_rate_w2` for both hitters and pitchers.
  - Their rationale reads "…or a declared baseline input…".
  - They were scored against a different, weaker baseline: in `/Users/Shirin/Future_Predictor/artifacts/admission_table.csv`, `baseline_rmse` is 0.0398 for `woba_w2` against 0.0354 for every other wOBA candidate, and 7.85 against 7.29 for fielding.
  - Eq. (2), "B ∪ {j}", cannot apply to a feature already in B.
- **Four more are other forms of the target's own record:** `woba_w3`, `br_rv_rate_w3`, `def_rv_rate_w3` and `br_rv`.
- **Only 17 of the 27 go beyond the target's own record:** wOBA 2, FIP 10, baserunning 3, fielding 0, hitter WAR 1, pitcher WAR 1.

**Why it matters.** The thesis, the novelty claim and the fantasy advice all rest on "which public metrics deserve to change a forecast once the model knows his recent record". As written, readers will credit Statcast-type metrics with gains that partly come from more seasons of the same statistic. The fielding result says nothing about any metric.

**Fix.**
- (a) Put three-year history (or a Marcel-style 5/4/3 history) in B and rerun the nested selection. At minimum, report the decomposition B0 → B0 + three-year history → ADM for each target.
- (b) Split "Projection" in Table 3 and Figure 2 into three groups:
  - baseline input, checked against the current-season baseline (6);
  - another window of the target's own history (4);
  - new metric (17).
- (c) Correct §10.6, §5.1 and the §6.2 heading.
- (d) Rewrite the abstract sentence. For example: "admitted inputs (including three-year target history) lowered RMSE…; for fielding the only admitted input was three-year fielding history."
- (e) In §8.4, change "beyond history" to "beyond two-year history".

### M2. Season effects: inference is conditional on five fixed seasons, season-level evidence is weak and flips verdicts, and part of the six-target gain is season-level calibration

**Location.** §5.5 p9 (player-cluster bootstrap); §6.2 p10–11; Table 6 and its caption p16 ("coarse with five seasons"); §8.3 p16–17; §10.6 p21 ("Era effects"); abstract.

**Problem.**
- **Per-season results.** Per-season ΔRMSE% for the primary family, 2021–2025, from `fantasy/by_year.csv`:

  | Linkage | Per-season ΔRMSE% | Season-level t(4) 95% CI | Table 6 verdict |
  |---|---|---|---|
  | FIP → ERA | −2.68, −0.35, **+0.58**, −1.59, −1.60 | [−2.69, +0.44] | "adds information" |
  | FIP → WHIP | −2.99, −1.44, **+1.58**, −1.72, −1.64 | [−3.34, +0.86] | "adds information" |
  | wOBA → HR | −2.02, −0.09, −1.26, −0.86, −0.99 | **[−1.91, −0.18]** | "no detectable gain" |

  - At the season level, the only primary linkage whose interval excludes zero is the one called "no detectable gain".
  - Both "adds information" linkages reversed in 2023, the pitch-clock and shift-ban season.
  - With five seasons, an exact sign-flip test cannot go below p = 0.0625 two-sided: no season-level test can reach 0.05.
- **The season-block bootstrap is not "coarse"; it is too narrow.** With five clusters there are only 126 distinct resamples, and percentile intervals under-cover. The wOBA→HR season-block interval (−1.54 to −0.52) is narrower than its player-cluster interval [−2.16, +0.03].
- **Table 6 contradicts itself silently.** It prints a season-block interval for FIP→WHIP that crosses zero (−2.48 to +0.35) next to "adds information"; §8.3 never mentions it.
- **Season-level calibration inside the six-target gains.** In `PSL/sloan2027/results/nested/predictions_default.parquet`, the history baseline's IP-weighted mean FIP residual was −0.43 in 2021 and −0.59 in 2022 (actual minus forecast).
  - Removing each model's season-mean residual leaves a within-season comparison, which is all that matters for ranking players in a draft.
  - On that comparison, the selected-vs-baseline gains change as follows:

    | Target | Raw | Within-season |
    |---|---|---|
    | FIP | −7.5% | **−4.4%** |
    | wOBA | −2.6% | −5.0% |
    | Baserunning | −5.8% | −6.2% |
    | Fielding | −1.0% | −1.0% |
    | Hitter WAR | −0.3% | −0.4% |
    | Pitcher WAR | −1.7% | −1.7% |

  - So about 40% of the top of the abstract's "1.0–7.5%" range is a level shift with no draft value. For K% alone (unweighted, `forecast_changes.parquet`), the gain goes from −4.5% to −2.3%.
  - The fantasy FIP→ERA and FIP→WHIP gains survive this check (−1.25% and −1.63%).
- **The era bullet is incomplete.** §10.6 omits the 2023 shift ban, which bears directly on AVG, wOBA and BABIP, and the 2021–22 run-environment swings.
- **Mismatched citation.** [70] (Cameron, Gelbach & Miller), cited for the player bootstrap, is the standard reference for the few-cluster problem the paper does not address.

**Why it matters.** "Adds information" generalizes to other players within 2021–2025, not to 2027, which is the season a fantasy reader cares about. The FIP headline overstates the player-level signal.

**Fix.**
- State the inferential target in §5.5 ("conditional on these seasons").
- For each headline contrast, report per-season deltas plus a t(4) or wild-cluster (season) interval.
- Report within-season (de-meaned or rank-based) skill next to raw RMSE for the six targets.
- In §8.3, write "4 of 5 seasons; 2023 reversed; season-level interval includes zero."
- Replace "coarse" with "few-cluster; likely too narrow".
- Expand the era bullet.

### M3. §5.4 (K% versus K-BB%) explains the result with the wrong mechanism and prints a number inconsistent with Table 5

**Location.** §5.4 p9; §5.1 p8 ("only the best-performing member is kept"); Table 2 K-BB% row p6; Table 5 H6 p12.

**Problem.**
- **The families are not what §5.4 implies.** In `/Users/Shirin/Future_Predictor/src/psl/catalog.py` (`PITCHER_FAMILIES`):
  - K% sits in `k_bb_skill`, with the K% windows and BB%;
  - every K-BB% variant (current, w2, w3, z, ×age, ×role) sits in `outcome`, alongside the FIP and ERA history.
- **How the family step works.** It is greedy (`src/psl/admission/run.py::_greedy_family_representatives`): keep the best member, then add other members of the same family only if they still cut RMSE by at least 0.5% given the baseline plus the kept members.
- **Consequences:**
  - Current K-BB% (−3.16%) was demoted by three-year K-BB% (−3.61%, same family), not by K%.
  - Three-year K-BB% was its family's first representative, not "a separate representative".
  - K-BB%×role was also kept from the same family, which contradicts §5.1's "only the best-performing member is kept".
  - Redundancy is never checked across families: K%, three-year K-BB%, CSW% and zone-contact rate all enter the FIP set together.
  - Family membership is a human choice that decides 32 Diagnostic labels, but §5.2 and Figure 1 list only the role and process flags as human choices.
- **The K% number is inconsistent.** The −3.24% printed for K% is a mean-of-folds estimate, and its own interval is [−3.20, −0.85] (`app/public/data/evaluations.json`): the point lies outside its interval. The project's leakage audit (`PSL/sloan2027/audits/leakage_audit.md`, item 5) says this "must be disclosed". Table 5 prints the same contrast as −1.89% [−3.13, −0.71].
- **The decisive baseball fact is missing.** K-BB% ≡ K% − BB%, and BB% added nothing beyond two-year FIP (canonical ΔRMSE +0.0002; improved in 4/7 folds). So the predictive content of K-BB% is its strikeout part.

**Why it matters.** This explanation was explicitly requested, and as written it is wrong. Readers also see two different numbers, −3.24% and −1.89%, for "strikeout rate → FIP".

**Fix.**
- Rewrite §5.4: correct families, the greedy step, the BB% null, and pooled values with CIs for K%, current K-BB% and three-year K-BB%.
- Correct §5.1.
- Add family membership to the human choices in §5.2 and Figure 1.
- List the families in an appendix.

### M4. The "exact reproduction" inherits undisclosed weaknesses of the canonical pipeline

**Location.** Abstract ("The original 208 metric–target evaluations reproduce exactly"); §6.1 p10 ("matched all 55 of 55 reproduction checks… every published selective and kitchen-sink RMSE"); Table 7; Appendix C.

**Problem.** The project's own register (`PSL/sloan2027/00_validation_risks.md`, items R2, R4, R6, R7) and `PSL/sloan2027/FINAL_REPORT.md` §3 list five problems. None appears in the manuscript:
- (a) **Result-guard assertions.** `assert_audited_admission_table` (`src/psl/admission/run.py`, around lines 894–939 in the working tree) refuses to write the canonical table unless hard-coded results hold:
  - two-year xwOBA ΔRMSE = −0.000931 ± 2×10⁻⁵ with 7/7 folds;
  - exit velocity labelled Projection;
  - Barrel%, HardHit% and Chase labelled Diagnostic;
  - sprint speed labelled Diagnostic for wOBA;
  - current wOBA labelled Exclude.

  R6 also says the hitting table was "preserved from an earlier code revision".
- (b) **Post hoc hitting list.** The hitting "selective" model in the published selective-vs-kitchen comparison is a hard-coded seven-feature list (`KITCHEN_ADMITTED_HITTER`) "chosen after results were known" (R2).
- (c) **Mismatched rows.** The published FIP selective and kitchen-sink RMSEs were computed on 1,699 and 1,866 rows (8.9% dropped) (`audits/phase1_reverification_2026-11-13.log`, "kitchen population").
- (d) **The gate's interval ignores repeated players.** The admission gate's interval (u_j in Eq. 3) is an i.i.d. row bootstrap with 400 draws (`src/psl/config.py`: `N_BOOTSTRAP = 400`; `src/psl/models/baselines.py::bootstrap_delta`). The same players recur across folds.
- (e) **Two estimands are mixed.** Δ_j (the mean of fold deltas) and u_j (pooled) estimate different quantities; 7 of the 208 canonical points lie outside their own interval.

**Why it matters.** "Reproduces exactly" reads as validation. It is in fact consistency with a pipeline whose headline values are partly asserted in code and whose original comparison used mismatched rows. A reviewer who opens the repository will find all of this; disclosing it first is far better.

**Fix.**
- Add a short paragraph to §6.1, "What the reproduction does and does not show", covering (a)–(e).
- Add (b) and (c) to Table 7.
- Describe the gate bootstrap in §5.1 and Appendix B.
- State that the nested pipeline uses rules only, with no assertions and with player-cluster intervals.

### M5. Fantasy bridge: no leakage of test-season outcomes, but training rows do not carry "genuinely out-of-sample" forecasts, and pre-specification is asserted rather than evidenced

**Location.** §8.1 p15 ("refit chronologically so that every training row also carries a genuinely out-of-sample forecast"); §1 p2 ("publicly time-stamped"); §8.1 ("committed publicly"); Appendix C.

**Problem.**
- **Training rows use the window-T feature set.** `experiments/fb03_bridge.py::window_frame` attaches the window-T upstream forecasts to every training row (feature seasons 2017…T−2). `experiments/fb02_upstream.py` fits each forecast's coefficients on seasons ≤ f−1, but always with the window-T feature set S_T.
- **S_T saw those rows' outcomes.** S_T was selected using outcomes through T−1, which includes the training rows' own outcome seasons.
- **The protocol discloses this; the paper does not.** Protocol §5 says so ("the training rows see a feature set chosen with in-window information").
- **No test-season leakage found.** I traced every input to the season-T test predictions and found no path for season-T outcomes:
  - upstream fit ≤ T−2;
  - downstream fit ≤ T−2;
  - z-score references ≤ T−1;
  - tuning on inner folds.

  `audits/fb_upstream_consistency.csv` reproduces the E1 and frozen predictions to 1.8×10⁻¹⁵.
- **The protocol commit is not printed.** The manuscript prints commit hashes for the 2026 predictions but none for protocol v1.0; the issue tracker cites `b482448` only for Amendment 1. The protocol, the practice audit, all fantasy results and the proof are dated the same day.

**Why it matters.** Training-row forecasts benefited from selection look-ahead (worth up to 0.53% of RMSE per §6.2), so the downstream weight on the forecast is fitted on slightly flattered inputs. This is probably conservative but unquantified. Pre-specification is a central selling point and must be checkable.

**Fix.**
- Replace "genuinely out-of-sample" with an accurate description.
- Optionally rerun with S_{f+1} for training rows whose window exists, and B0 elsewhere, and report the difference.
- Print the v1.0 and Amendment 1 commit hashes with UTC times.
- State that the six-target results and the 2026 season had already been seen when the protocol was written.

### M6. §6.5 misreports the ablation table, and a pre-specified sensitivity is not reported

**Location.** §6.5 p12–13 ("Only two kinds of change altered out-of-time error with an interval excluding zero"); §6.3 and §10.3 ("a tuned elastic net matched selection").

**Problem.** `PSL/sloan2027/tables/table5_gate_ablation_threshold_sensitivity.csv` shows more changes than §6.5 admits:
- **Min folds = 4** changed error for baserunning (+0.0071), wOBA (+0.0002) and FIP (+0.0149).
- **Consistency share 0.75** changed FIP (+0.0059).
- **Materiality 0.25%** *improved* hitter WAR (−0.0056), the one target where "selection failed", and worsened FIP (+0.0102).
- **Materiality 0** moved fielding and FIP in opposite directions (−0.0100 and +0.0125). The text says only "changed".
- The difference between "threshold 0" (error changes) and "materiality gate removed" (no change) is not explained.
- Units (raw target units) are never stated.

Separately, the E1 protocol (`PSL/sloan2027/protocol.md`, line 19) pre-specifies "Sensitivity: inner start 2017 (outer 2020–2025)". In `PSL/sloan2027/results/nested/comparisons_inner2017.csv`:
- the tuned elastic net **beats** the selected FIP model (−0.88%; the interval excludes 0);
- FIP selected vs baseline is −2.6% rather than −7.5%;
- 2020 went the wrong way for FIP and pitcher WAR.

None of this is reported.

**Why it matters.** The paper's conclusions that only two gates matter and that selection "ties" a tuned elastic net are not robust to analyses the author ran or pre-specified.

**Fix.**
- Put the full ablation table, with units, signs and CIs, in an appendix.
- Rewrite §6.5 to list every change that moved error, with its direction.
- Note in §6.2 that the hitter-WAR null depends on the threshold.
- Report the inner-2017 sensitivity and qualify "tied".

### M7. Claims stronger than the analyses support

Each item gives the location and problem, followed by the fix.

- **(a) "Playing time dominates" is untested.** §3.2 p5: "consistent with the finding in Section 8.5 that playing time dominates draft value". Also Table 2 p6 (playing-time row, "Consistent") and §10.1 p20: "Spend the most effort on playing time. It, not marginal skill metrics, dominated the illustrative draft decisions."
  - Nothing isolates playing time: there is no comparison of playing-time forecasts against skill forecasts and no oracle-playing-time draft.
  - *Fix:* run that experiment, or delete these sentences.
- **(b) "The forecasts mostly reorder the middle of the pool. At the top of a draft, playing time and category history dominate."** §8.5 p18 and Table 2. Nothing is shown.
  - My check of `local/fantasy/decision_rankings.parquet` supports the first half. Per season, the baseline and augmented top-156 hitters overlap 93–96% and the top-108 pitchers 88–95%. The median rank change is about 1–3 places in the top 12, against roughly 7–27 for ranks 51–156.
  - *Fix:* add those numbers and drop the "playing time dominates" clause unless (a) is done.
- **(c) "Fielding-independent skill is worth a modest premium"** (§10.1). "Premium" implies draft price, and §8.5 found no detectable improvement in picks.
  - *Fix:* "deserves modest extra weight in ERA/WHIP forecasts".
- **(d) Defense.** §10.2 p20 lists "ignore defense except as a playing-time clue" among beliefs that hold up. Table 2 says "no playing-time signal detected either" (fielding → AB −0.3% [−0.8, +0.3]). This is a direct contradiction.
- **(e) "Trust sprint speed for steals and nothing else"** (§10.2) contradicts the paper's headline that sprint speed is admitted for baserunning.
- **(f) Rogers generalized to all pitch models.** §7 p14: "It has no term for what an extreme release does to a hitter's view, and Rogers' results show that this matters". §10.2: "The model can fail badly for pitchers whose deliveries fall outside its training distribution". Table 2: "fails for unusual deliveries".
  - This rests on n = 1.
  - "A pitch-quality model scores velocity, movement and spin against how pitches from typical release points perform" generalizes to all pitch models; FanGraphs' Stuff+ uses release point.
  - *Fix:* "this study's Stuff+ (no arm-angle or release-height term) mis-graded one extreme submariner in all five seasons; whether this generalizes was not tested."
- **(g) In-house Stuff+ presented as public Stuff+.** §10.2 ("Pitch-quality scores such as Stuff+ added little") and Table 2's Stuff+ row generalize from the in-house expected-whiff model. That model is also fitted on seasons ≤ t, so it is in-sample for season t (`leakage_audit.md`, R10).
  - *Fix:* say so in the row and in the sentence, and consider renaming it (e.g., "xWhiff+").
- **(h) Format dependence not tested.** Table 2: "Points and category formats value players differently → Supported: which forecast helps depends on the format".
  - This compares significance across outcomes without testing the difference.
  - The FIP → points result it cites is "not robust to multiplicity" (BH-adjusted p = 0.069, `results_by_target_category.csv`).
- **(i) "Raw metrics beat the intermediate target"** (§8.4 p17). There is no paired test of BF + raw metric against BF + target forecast. For HR, xwOBA (−1.18%) and the wOBA forecast (−1.02%) are almost the same.
  - *Fix:* test the difference directly, or say "were detectable where the target forecast was not".
- **(j) Verdict words that contradict intervals.** §6.4 p12: "xwOBA (two-year) improved next-season wOBA in every evidence source" and "Sprint speed improved baserunning in every source, the 2026 interval again touching zero".
  - The 2026 intervals *include* zero (upper bounds +0.19 and +0.09).
  - *Fix:* "point estimates favored the metric in every source."
- **(k) False description of Figure 4.** §6.3 p12: "The ridge kitchen-sink model's disadvantage for wOBA and FIP was largest in 2021".
  - This is false for FIP: +2.3% in 2021, peaking at +12.8% in 2022 (`figures/data/fig4_year_by_year.csv`).
  - The "scarce data" story therefore fits wOBA only.
- **(l) "Tied a tuned elastic net"** (abstract, §6.3). No equivalence margin was set.
  - *Fix:* "no detectable difference".
- **(m) Secondary results in the abstract.** The abstract presents the raw sprint-speed and Barrel% results next to the primary result. They are secondary and exploratory, BH-adjusted within a 12-test family.
  - *Fix:* label them as such.
- **(n) Imprecise statements about what the model does.** §7 says "Stuff+ is good at confirming that elite stuff will keep missing bats", but the target is FIP, not whiffs. It also says "That is why the average gain is small": an untested causal account.
- **(o) "The same metric often had different jobs"** (abstract) rests on one example.
  - *Fix:* quantify how many metrics evaluated for two or more targets changed label.

### M8. Several Table 2 tests do not test the belief as stated

**Location.** Table 2 p6; §3.3 p5.

**Problem.**
- **"FIP-type estimators project ERA better than ERA itself" → "Supported".**
  - The test adds a FIP *forecast* (built from K%, three-year K-BB%, CSW%, velocity, Stuff+ and others) to a model with ERA and WHIP history. That is an incremental test of a skill composite, not FIP against ERA.
  - In the direct ERA admission (`fantasy/generalization_era/admission_by_window.csv`), two- and three-year FIP were *never* admitted beyond ERA history in any window, while K% always was.
- **"Barrel% and exit velocity flag power breakouts".** Exit velocity is not tested for HR. Breakouts (large positive changes) are not tested either; average RMSE is.
- **"Stuff+ predicts future results, especially strikeouts".** The test uses season K *totals* over the full pool, which are dominated by innings and role, while the belief is about strikeout rate.
  - *Fix:* test K/9 or K% for pitchers with at least 20 IP.
- **"xwOBA above wOBA marks an unlucky hitter".** The decile shares (70% against 54%) are never compared statistically, and they are exposed to the selection problem in M9.
- **No in-table sources.** Rows carry no citations; sources live only in a repository file. The reviewer asked for researched practice with sources, and they already exist in `fantasy/research_sources.md`.
- **Wrong period.** The caption says "outcome seasons 2021–2025 unless noted", but the Stuff+ → FIP entry (−0.48% [−0.92, −0.03]) is the 2019–25 pooled value. The 2021–25 value is −0.76% [−1.46, −0.02].
- **Rounding hides interval signs:**
  - "[−0.3, 0.0]" (true upper bound +0.046);
  - "[−1.1, 0.0]" (+0.014);
  - "[−0.9, 0.0]" (−0.006: this interval actually excludes zero).

**Why it matters.** Table 2 is the centerpiece of the "real fantasy practice" requirement. A "Supported" verdict based on a mismatched test misleads exactly the audience the paper targets.

**Fix.**
- Rerun or reword the four mismatched rows.
- Add citations to each row.
- Correct the period of the Stuff+ entry.
- Use two decimals whenever an interval bound is within ±0.05 of zero.

### M9. The player-level asymmetries in §7 are confounded by who stays in the outcome-observed sample

**Location.** §7 p14–15 (Stuff+ deciles, K% deciles, xwOBA buy-low/sell-high, Tyler Rogers); Figure 5C–D; Table 2 (xwOBA row).

**Problem.**
- **Retention differs sharply by Stuff+ decile.** Among year-t-eligible pitchers in feature seasons 2020–2024 (the forecast-date pool), the share retained in the FIP study's outcome-observed sample is:
  - 54% in the bottom Stuff+ decile (116/214) and 52% in decile 2;
  - 64–74% in deciles 8–10.

  Source: `data/processed/pitcher_labeled.parquet` joined to `pitcher_sample_role_ip.parquet` in the PSL worktree.
- **Why that biases the result.** Low-Stuff+ pitchers who keep their jobs are selected for good next-season results. That mechanically makes an upward FIP adjustment look wrong.
- **The same logic applies elsewhere:** to the xwOBA deciles and to Rogers, a durable survivor.
- **No intervals on the decile shares.** With n ≈ 130–135 per decile, the standard error is about 4.3 points, and decile 3 (36%) sits below decile 1 (38.5%).

**Why it matters.** "Stuff+ is good at confirming… poor at condemning" and "sell high beats buy low" are offered as practical advice. They may be artifacts of conditioning on next-season playing time, the very issue §4.2 raises.

**Fix.**
- Report retention by decile.
- Repeat the analysis with inverse-probability-of-retention weights (retention modeled on season-t information), or bound the effect.
- Add binomial CIs.
- Soften the conclusions.

### M10. The fantasy value score and the draft backtest are under-specified and never translated into fantasy terms

**Location.** §3.1 p4; §8.1 Eq. (5) p15; Table 6; §8.5 p18; Figure 7.

**Problem.**
- **Eq. (5) is incomplete.** It omits the WHIP term (in code: IP·WHIP_ref − (BB+H)), and AVG_ref, ERA_ref and the set C are not defined in the text.
- **The reference pool is non-standard.**
  - μ_c and σ_c come from the entire forecast-date pool: about 400 players per group, including zero-production non-returners.
  - Standard z-score practice, and the project's own plan (`fantasy/hypotheses.md` §0.9, "within a 10- or 12-team Yahoo-default rostered pool"), use the rostered pool instead.
  - §3.1 describes value "against replacement level", but V has no replacement level and no positional adjustment.
  - This choice changes the effective category weights, especially for SB and SV.
- **z-units are never scaled.** The SD of realized V in 2021–2025 is 3.8 for hitters and 3.2 for pitchers (`decision_rankings.parquet`).
  - So "+0.03 z per pick" is about 0.007 SD.
  - Value RMSEs of about 2.8 mean little without this context.
- **The roster assumption is unjustified.** k = 156/108 implies 13 hitters and 9 pitchers per team. That matches neither the declared Yahoo default (10 active hitters and 8 active pitchers; `fantasy/scoring_weights.json`) nor the NFBC (14 and 9, so 210 hitters for 15 teams, not 195).
- **What the backtest measures.** It ranks the whole pool for the whole league. It does not measure one manager's edge over consensus ADP. Say so in §8.5, not only in the limitations.
- **Pre-specified decision metrics are not reported** (protocol §6; `fantasy/ranking_value_sensitivity.csv`):
  - top-k overlap with the realized top-k (12-team: hitters 0.726 → 0.731; pitchers 0.572 → 0.583);
  - the points-format backtest (no detectable gain).
- **The most decision-relevant unconditional result is buried.** FIP forecast → pitcher 5×5 value on the full pool is −1.77% [−2.58, −0.93], 5/5 seasons, "adds information". It appears only as a cell in Figure 6. It corroborates the conditional ERA and WHIP findings and belongs in §8.3.

**Fix.**
- Complete Eq. (5).
- Justify the pool and roster sizes, and add a rostered-pool (or SGP) sensitivity.
- Scale z-units (SD and approximate standings points).
- Report the pre-specified metrics.
- Promote the full-pool pitcher-value result to the text.

### M11. The 2026 check is reported selectively, and the abstract and introduction omit "retrospective"

**Location.** §6.2 p10–11; abstract; §1 bullet p2; §5.5 p9–10.

**Problem.**
- **The 2026 selected-vs-baseline results are left out of §6.2.** In 2026 (`PSL/sloan2027/tables/table2_nested_and_2026_model_comparison.csv`), the selected model's advantage over B0 was undetectable for five of six targets:

  | Target | 2026, selected vs B0 |
  |---|---|
  | wOBA | −2.14 [−5.34, +1.02] |
  | FIP | −2.14 [−5.64, +1.69] |
  | Baserunning | −2.89 [−7.43, +1.80] |
  | Fielding | +0.17 [−1.05, +1.46] |
  | Hitter WAR | +0.72 [−0.49, +1.82] |
  | Pitcher WAR (only detectable gain) | −1.71 [−3.14, −0.26] |

  Yet 2026 is cited where it hurts broad models (§6.3) or supports flagship contrasts (§6.4).
- **A second 2026 result is omitted:** for pitcher WAR, the all-feature ridge beat selection (−0.59 [−1.12, −0.06]).
- **"Retrospective" is missing up front.** The abstract and the §1 bullet say only "frozen before outcomes were downloaded".
- **The ancillary files are not named.** "Earlier ancillary files contained some 2026 rows" (p10) is vague. Per register R11 and tracker item M1, these are the park-factor and Stuff+ files containing partial-2026 rows, which were not used by the 2025-feature forecasts. Say so.

**Fix.** Add one sentence to §6.2 and to the abstract, name the files, and insert "retrospective" in the abstract and §1.

### M12. Departures from the accepted abstract are incompletely disclosed

**Location.** Appendix A and Table 7, p23; §1; Table 5 caption p12.

**Problem.** Table 7 omits five departures:
- (i) **The operations claim.** "For baseball operations, this framework provides a reproducible way…" and "important for baseball decision systems" are now withdrawn: §10.4 calls the evidence "insufficient by design". This is the largest departure and the closest thing to the forbidden deployment claim.
- (ii) **"Temporal stability" as a criterion.** Reliability never gates (Table 4).
- (iii) **Selection on the evaluation seasons** (look-ahead of at most 0.53%).
- (iv) **The original selective-vs-kitchen comparison** used mismatched rows and a post hoc hitting list (M4).
- (v) **"Strong history-aware baseline".** Three-year history was later admitted (M1).

Appendix A is never cited from the main text. Table 5's caption calls H6 (K%) an accepted-abstract contrast, which it is not.

**Fix.** Add these rows with a status of "withdrawn" or "qualified". Cite Appendix A in §1 and §6.4. Correct the Table 5 caption.

### M13. Two requested items are only partly met: baseball units and named players

**Location.** Abstract, §6.2, Figures 3–4, Table 5 p12, §7, Table 6.

**Problem.**
- **Units.**
  - The six-target results are reported only as % RMSE.
  - Table 5's "Original ΔRMSE" column prints raw decimals (−0.00093, −0.00730): exactly the format the reviewer asked to replace.
  - Unit RMSEs already exist in `table2_nested_and_2026_model_comparison.csv`:

    | Target | RMSE, baseline → selected |
    |---|---|
    | wOBA | 0.0339 → 0.0330 (33.9 → 33.0 wOBA points) |
    | FIP | 0.862 → 0.798 |
    | Baserunning | 1.385 → 1.305 runs per 100 times on base |
    | Fielding | 6.83 → 6.76 runs per 1,000 innings |
    | Hitter WAR | 1.987 → 1.981 WAR per 600 PA |
    | Pitcher WAR | 4.70 → 4.62 WAR per 200 IP |

  - "Points" of wOBA are never defined as thousandths.
  - The Table 6 HR improvement (7.98 → 7.89) and SB improvement (6.38 → 6.36) are never put in words: under 0.1 HR and 0.02 SB per player-season.
- **Named players.** There are two, both pitchers, both for one metric (Stuff+) and one target. The paper has:
  - no hitter;
  - no sprint-speed or xwOBA case;
  - no fantasy-bridge case (for example, a pitcher whose FIP forecast moved his ERA forecast the wrong way);
  - no failure of any headline metric other than Stuff+.

**Fix.**
- Add a units table and plain-language translations.
- Add three or four named cases chosen by a stated rule (largest improvement and largest harm for each headline contrast), for example:
  - an xwOBA buy-low failure;
  - a sprint-speed stolen-base case;
  - a FIP → ERA fantasy case.

### M14. The mandatory section "Why These Six Prediction Targets?" is present and per-target but thin, partly post hoc, and missing construct details

**Location.** §2 p3–4, Table 1, Box 1.

**Problem.**
- (i) **"Why it was used" entries are one-liners**, for example "Aggregate pitching value; a noisy stress test".
- (ii) **The fantasy rationale is retrospective.** §2 says the targets predate the fantasy framing, yet fielding is called "a deliberate boundary case". Say that the fantasy roles were assigned afterwards.
- (iii) **Construct gaps:**
  - the FIP label mixes Savant FIP with computed FIP plus a same-season constant built from unweighted pitcher means (register R9);
  - the fielding target is Baseball-Reference fielding runs (DRS-based), while the candidates include Statcast OAA: a cross-provider construct;
  - the baserunning denominator switches to "per 600 PA below 20 times on base" without explanation or a row count;
  - pitcher WAR uses a looser population (2,917 outer rows against 1,328 for FIP; no workload floor; weights clipped at 1 IP), so the FIP and pitcher-WAR findings describe different pitchers.
- (iv) **The fantasy-link column overreaches.** It lists R and RBI for wOBA, but only AVG and HR were pre-specified.
- (v) **No per-target outcome.** The section never says what the paper ultimately found for each target.
- (vi) **Table 1 is hard to read:** five dense columns at about 7 pt.

**Fix.** Write one short paragraph per target covering:
- construct;
- why it was chosen;
- its fantasy role and how that role was tested;
- what it does not establish;
- what was found.

Alternatively, add "Result in this paper" and "Population (n)" columns to Table 1. Either way, disclose the construct gaps in (iii).

### M15. Figure defects that undercut "graphics that carry the argument"

Print sizes below combine the font sizes in `figures/make_figures.py` with the placement scale from `pdfimages -list` (Figures 1, 3, 6 and 7 are placed at 0.94–0.99× and embedded as JPEG).

| Fig | Legible in print | Direction of "better" clear | Units and sample | Colour (CVD) | Supports the caption? | Defects and fixes |
|---|---|---|---|---|---|---|
| 1 | Marginal: box text ≈ 6.0 pt; the "History baseline" title overflows its box | n/a | Worked example in % of baseline RMSE; "7 folds" stated | OK (blue/orange plus solid/dashed lines) | Partly. The family step depends on human-defined families but is drawn as purely statistical. The human-rule boxes are unconnected, so the order (role label before testing; process flag after failure) is not shown. The worked example's −4.3% differs from Table 5 (−3.99) and the abstract (−4.8). | Add connectors; mark families as human-specified; reconcile the estimand. |
| 2 | OK (≈6.6–7 pt) | n/a | Counts. "Candidate metrics" includes baseline inputs and context variables | 5 hues; orange vs gold and aqua vs gold are close for deuteranopes; printed counts help | Partly. "Projection (statistical pass)" includes 6 baseline inputs (M1); the 1-count redundant segment for pitcher bWAR is unlabelled | Split the Projection bar; label every segment. |
| 3 | Marginal (≈6.3–7.4 pt) | Stated per panel, but "first-named model" is the selected model in panel A and the broad model in B–C | % of the second-named model's RMSE; **n not stated** (1,328–2,917; 2026: 268–586) | OK (colour plus filled/open markers) | Yes, but the 2026 nulls in panel A go unmentioned (M11) | Use one convention (negative = selected better); share x-axes (currently ±10, ±8, ±6); add n. |
| 4 | OK | The y-label rule ("below 0: first-named better") gives the orange series the opposite meaning from the blue | No per-season intervals for 2021–25 | OK | **No.** The caption says no metric was selected for hitter WAR in 2021–2023, but EV was selected in 2022. The text claims the FIP disadvantage peaked in 2021; it peaks in 2022. | Fix the caption and text; add per-season intervals. |
| 5 | OK (scaled up 1.11×) | Not stated. For FIP lower is better, so a positive change means a worse projection | FIP units ✓; n = 1,328 in caption ✓ | Orange means "observed FIP" in A–B and "forecast raised" in C | Partly: no CIs on decile shares; survivorship (M9) | Add CIs; state the direction; use colours consistently. |
| 6 | Marginal (≈6.0–6.3 pt; colourbar ≈5.95 pt) | ✓ ("blue = more accurate") | %, pooled 2021–25 ✓; n not stated (fielding subset is 1,666) | OK (diverging blue–red) | **Defect.** In the dark FIP → 5×5-value cell, the "adds information" marker is white (the code switches marker colour when \|Δ\| > 1.3%), so it reads as the legend's open circle, "no detectable gain". Also prints "−0.0%". | Keep marker semantics fixed (e.g., black disk with white outline); fix "−0.0". |
| 7 | Marginal (≈5.8–6.6 pt) | C: "augmented minus baseline", but "positive = better" is not stated | z-units unscaled (SD 3.8 hitters, 3.2 pitchers) | Blue/orange mean the model in A–B and the player group in C | Partly. The panel A legend covers the 2021 points and the y-axis label. The 2021 hitter dip (ρ 0.41, a 203-player pool; m8) is unexplained. | Move the legend; use colours consistently; give the SD. |

Global fixes:
- raise every figure font to at least 7 pt at print size;
- embed the existing vector PDF/SVG (or PNG) instead of JPEG;
- use one name for the broad model ("all-feature ridge" in figures; "all-metric ridge", "kitchen-sink" and "KS" in the text).

### M16. The blind copy has no names, affiliations or links, but several identifiers make de-anonymization trivial

**Location.**
- Figure 1 caption p2 and Appendix C: "commit 17da742".
- §5.5 p9: "f8023bf, SHA-256 af61b2b8…".
- Appendix C p24: "An earlier version of the study is available as a preprint [74]".
- §1 and Appendix D: the "open web application… Fantasy Linkage Explorer".

**Problem.**
- Commit hashes can be searched with GitHub's commit search.
- The preprint carries the same title and is public.
- The app name is searchable.

The rest checks out:
- PDF and DOCX metadata are clean: empty creator and lastModifiedBy, and no URI annotations in the PDF.
- The blind/named diff is limited to the author line, Appendix C and references [73]–[74].

**Fix.**
- In the blind copy, replace the hashes with "[withheld for review]" and move them to the submission form.
- Remove the preprint sentence, or confirm with the organizers that preprints are allowed (the project's register R19 already flags this question).
- Describe the app generically.

---

## 3. Minor issues

- **m1. Figure 4 caption error.** "For hitter WAR in 2021–2023 no metric was selected" should be "in 2021 and 2023". EV was selected in 2022 (`overall_war_T2022_default_meta.json`), which is consistent with §6.2's "4 of 6".
- **m2. §5.1 and Appendix B disagree on gate details.**
  - "Majority of large subgroups" (§5.1) vs "at least half" (Appendix B).
  - §5.1 omits the 90% coverage rule for systematic missingness.
  - "RMSE(B)" in Eq. (3) is ambiguous (mean of fold RMSEs?).
  - The gate bootstrap is unspecified (i.i.d. rows, 400 draws).
  - Weights are season-t opportunities (register R8): say so, and report unweighted errors.
- **m3. Nested validation (§5.5) is described incompletely.**
  - The training rows of the final outer model are not stated.
  - T = 2021 has only three inner folds: K ≥ 3 is barely met, and consistency then requires 2 of 3.
  - Gate statistics are computed on training rows only. The leakage audit confirms this; say it in the paper.
  - The tuning grids for the elastic net, LightGBM and random forest are not given (only the ridge grid appears, and only in the protocol).
  - The KS eligibility rule (≥5% coverage) and the imputation are not described.
  - Bootstrap B and seed (2,000 and 42) are missing.
- **m4. Notation is inconsistent.**
  - The baseline is B (Eqs 2–3), B0 (§5.5, §8), and "category-history baseline" or BF (protocol).
  - The broad model is KS, kitchen-sink, all-metric ridge, all-feature ridge, or "broad models".
  - 𝒜 and 𝒟 in Eq. (4) are undefined.
  - Eqs (1)–(5) are never cross-referenced, although the template requires cross-references.
  - Table 5's H1–H7 are undefined.
- **m5. Terms not defined at first use.**
  - wOBA and FIP (used in the abstract and §1; defined only in Table 1 and Box 1).
  - RMSE (abstract), PA, IP, CI, SP/RP.
  - 5×5, roto, NFBC, ATC, OOPSY.
  - SIERA, xFIP, BABIP, K-BB%, Barrel%, CSW.
  - BH (never introduced as an abbreviation), q-value, and Holm (uncited).
  - "Points" of wOBA, "z-score value" and "z-units" (used in §3.1 and §8.5 without or before definition), and WHIP.
- **m6. A fifth meaning of "stable".** §6.2 says "the selections were stable across windows" (selection stability), and Figure 1 calls the coefficient-sign gate "stable". Add this to Table 4 or use another word. Table 4's coefficient-drift example is "—".
- **m7. The placebos are misdescribed.** §6.5 calls them "metrics of pure noise"; they are permuted copies of real metrics (`placebo_verdicts.csv`: `placebo_perm0_woba`, …; 25 per target-window).
  - 896 of the 900 were labelled Diagnostic, which shows that the Diagnostic label carries no information beyond the human flag. That is worth saying.
  - 13 placebos improved in every fold and failed only the materiality gate.
- **m8. 2020 is handled asymmetrically.** Pitcher thresholds were scaled for 2020 (25/10 IP); the hitter 150-PA rule was not.
  - As a result, the 2021 hitter pool has 203 players (about 410 in other seasons; `cohort_by_year.csv`), and only 46% of 2020 pool hitters met the canonical rule.
  - This explains the 2021 dip in Figure 7A and should be disclosed in §4.2 and §10.6.
  - Prorating 2020 counting stats by 162/60 inflates their variance inside the z-score references; say how this was handled.
- **m9. The "park factor" is not a park factor.** It is a same-season team run-environment index that includes the player's own team's runs, generated by external code not in the repository (`leakage_audit.md` item 3; R11). Rename and disclose. This also contradicts §4.3's "code that rebuilds every dataset from the original sources".
- **m10. Two panel details from the leakage audit are not disclosed.**
  - "lag1" means the previous *observed* season; 6.1% of lagged hitter rows skip a season.
  - Stuff+ for season t is in-sample for t.
- **m11. A count without a denominator.** §8.4 says "9 favored the forecasts" (2026). The denominator is 132 secondary comparisons. At 95% one would expect about 3 favorable exclusions by chance (ignoring correlation).
- **m12. Table 6 needs three small additions.**
  - Add n per row: the fielding linkage uses 1,666 hitters with a fielding forecast, not 1,845.
  - Note that Holm p = 0.008 sits at the bootstrap floor (raw p = 2/2,001 × 8).
  - Mention that the season-block interval for FIP → WHIP crosses zero.
- **m13. §9 has three small problems.**
  - The ERA selection list omits exit velocity against (selected in 2021).
  - Its four bullets switch sign conventions: negative = better, then positive = worse, then positive = better.
  - "More honest" is self-congratulatory.
- **m14. Forbidden phrase in §9.** It quotes "the framework handles any target". Rephrase: "The procedure selected sensible metrics for a closely related new target, but re-selection did not beat reusing the FIP selections."
- **m15. The abstract is overloaded.**
  - About 270 words, dense with numbers, including a five-clause sentence ("Admitted models beat… lost for FIP in a 2026 check…").
  - It says 2015–2025 although 2026 data are used.
  - The §1 bullet "an open web application in which every result can be queried": "every" is unverifiable; say "the main results".
- **m16. Two sentences in §3 need rewording.**
  - §3.3: "could not be read by the automated retrieval used for this review" reads as a tooling note; replace it with a scope statement.
  - §3.4: "No peer-reviewed treatment of rotisserie valuation methods was found" should become "we did not find…", with a citation of the practitioner valuation literature (SGP, z-score and auction calculators).
- **m17. Business-style residue:** "auditable"/"audit" (six uses), "materiality", "admission", "gates", "jobs", "channel", "discipline". Each is defined, but the reviewer flagged business framing specifically; prefer plain words ("checkable", "minimum improvement").
- **m18. The Discussion needs a fantasy translation and an ending.**
  - §10.1–10.2 carry the overclaims in M7, and §10.6 has the baseline error in M1.
  - Nothing translates the ~1% ERA/WHIP gain into fantasy terms (expected standings points) or compares it with typical accuracy gaps between public projection systems.
  - There is no short conclusion; the closing paragraph is buried at the end of §10.6.
  - Page 22 holds a single orphaned bullet.
- **m19. Appendix C contains a production note.** "Proofs were rendered with LibreOffice… Microsoft Word was not available" does not belong in a paper. The proof uses Caladea rather than the template's Cambria (`pdffonts`); check the final layout in Word.
- **m20. Uncited elements.** Tables 3, 4 and 5 and Box 1 are never cited in the text. Appendices A, B and D are never referenced from the body.
- **m21. Reference list problems.**
  - **Conflated entries:** several sources under one date in [2]; [14], dated 2018 for "Rules: Main Event (2027)" and bundled with a 2018 FanGraphs FAAB article; [15]; [18]; [20]; [21], which bundles four articles; [23]; [26].
  - **Unverified titles:** "(title per URL)" in [39] and "URL slug" in [13].
  - **Non-canonical URLs:** regional ESPN pages ([13] africa.espn.com, [30] global.espn.com, [39]) and `?p=` short links ([32], [38]).
  - **Inconsistent author forms:** "Slowinski, P." vs "Piper Slowinski (SIERA entry) / FanGraphs"; "Derek Carty / FanGraphs; RotoGrinders".
  - **Missing references:** Holm (1979); Breiman (2001) for random forest; a source for the *realized* post-2023 rise in steals ([30] is a preseason article; `research_sources.md` S26 has the Baseball-Reference league averages).
  - **Citations that do not support their sentence:**
    - [1] (Savant) and [3] (Marcel, which uses no Statcast inputs) for "projection systems that blend several of these";
    - [39]–[40] are thin support for "widely described as the dominant… driver";
    - [70] fits the season-level problem better than the player bootstrap it is attached to.
- **m22. Claims-ledger problems.**
  - Rows 207–208 of `paper/claims_to_evidence.csv` record "+0.03% [−0.05, +0.09]" with a % sign; the paper (correctly) prints z-units.
  - Many ledger paths start with `sloan2027/...`, which does not exist in this repository (it is in the PSL worktree). Say so in the ledger header.
- **m23. Multiplicity families need one explanatory sentence in §8.1.**
  - BH is applied within four secondary families of different sizes (12, 40, 32, 48), so the q-values depend on how families were drawn.
  - The six-target flagship Holm p-values are computed (H1–H6) but not reported.
  - The 2026 rows are unadjusted.
- **m24. Stale DOCX metadata.** `docProps/app.xml` still reports the template's 4 pages / 346 words. Harmless, but sloppy.
- **m25. The study's own data collection is not described.** §4.3 advises readers on data rights, but the repository's data-rights note flags that scripted collection may fall under MLB's Terms §1(xi) and Sports Reference's automated-access and AI clauses. State briefly how the study's data were obtained and whether permission was sought.
- **m26. Table 1 caption.** It gives "feature seasons 2015–2024; outcomes 2016–2025", but the evaluation seasons are 2019–2025 (canonical) and 2021–2025 (nested). Give both.
- **m27. WAR "straw man" tension.** §3.3 calls "WAR is a fantasy shortcut" a straw man, while §2 says "Many fans treat WAR as a shortcut for player quality". Reconcile.
- **m28. Next to Eq. (5), say what is conditioned on playing time.** §8.1's "Future playing time is never an input" holds for features, but:
  - ratio outcomes are *filtered* on future playing time;
  - the AVG, ERA and WHIP models are trained only on players who cleared the floor.

---

## 4. Number spot-checks

46 printed values were checked; 40 match their source exactly. Rows marked "No" or "Partial" are discussed in the issues above.

| # | Printed value | Location | Source file | Value found | Match |
|---|---|---|---|---|---|
| 1 | "1.0–7.5% lower RMSE" | Abstract | `PSL/sloan2027/tables/table2_nested_and_2026_model_comparison.csv` | −0.99 (fielding) to −7.50 (FIP) | Yes |
| 2 | "−4.8% [−6.2, −3.3]" (sprint → baserunning) | Abstract | `PSL/sloan2027/tables/table3_flagship_contrasts.csv` (H5, nested) | −4.75 [−6.16, −3.30] | Yes |
| 3 | "−1.2% [−1.8, −0.6]" (FIP → ERA) | Abstract, §8.3 | `fantasy/results_by_target_category.csv` | −1.168 [−1.767, −0.594] | Yes |
| 4 | "−1.3% [−2.0, −0.6]" (FIP → WHIP) | Abstract, §8.3 | same | −1.298 [−2.022, −0.573] | Yes |
| 5 | "r = 0.92" (sprint speed) | §1, Table 4 | `figures/data/fig1_sprint_speed_examples.csv` | 0.9159 | Yes |
| 6 | "1,845 hitter-seasons and 2,115 pitcher-seasons" | §4.2 | `fantasy/cohort_by_year.csv` | 203+411+417+404+410; 457+421+413+417+407 | Yes |
| 7 | "74–93% … 60–64%" | §4.2 | same | 74.1–93.1%; 59.7–64.1% | Yes |
| 8 | "24% of hitters and 34% of pitchers" | §4.2 | `PSL/sloan2027/tables/table4_2026_cohort_attrition.csv` | 24.2; 33.8 | Yes |
| 9 | "between 2% and 9% … 9%–14%" | §8.1 | `fantasy/cohort_by_year.csv` | 1.5–8.9%; 9.0–14.0% | Yes |
| 10 | "K% … −3.24%; K-BB% −3.16%; 3-yr K-BB% −3.61%" | §5.4 | `app/public/data/evaluations.json` | −3.235 (own CI [−3.203, −0.846]); −3.160; −3.607 | Matches its source, **but** conflicts with Table 5 H6 pooled (−1.89), and the point lies outside its CI (M3) |
| 11 | "2,081 of 2,081 labels" | §5.5 | `PSL/sloan2027/audits/e2_label_validation_2025.csv` | 305+243+305+335+305+588 = 2,081, all exact | Yes |
| 12 | "78 … 32" | §6.1, App. B | `PSL/sloan2027/tables/table7b_reason_code_counts.csv` | 78; 32 | Yes |
| 13 | "23 of 27 Projection rows have BH q < 0.05" | §6.1 | `PSL/sloan2027/results/multiplicity/summary.json` | 23 | Yes |
| 14 | "wOBA −2.6% [−4.4, −0.9]; FIP −7.5% [−9.4, −5.5]" | §6.2 | table2 (row 1) | −2.60 [−4.39, −0.88]; −7.50 [−9.38, −5.48] | Yes |
| 15 | "hitter WAR −0.3% [−0.9, +0.2]" | §6.2 | same | −0.29 [−0.86, +0.25] | Yes (upper bound 0.25 printed as +0.2) |
| 16 | "exit velocity chosen in only 4 of 6 windows" | §6.2 | `PSL/sloan2027/results/nested/admission/overall_war_T20xx_default_meta.json` | EV in 2022, 2024, 2025, 2026 | Yes. **The Fig 4 caption ("none 2021–2023") does not match** |
| 17 | "8–12 metrics; Stuff+ from the 2022 window" | §6.2 | `pitching_fip_T20xx_default_meta.json` | 8, 12, 11, 11, 11, 11; stuff_plus from T2022 | Yes |
| 18 | "flattered accuracy by at most 0.53%" | §6.2 | `PSL/sloan2027/results/nested/comparisons_default.csv` | FIX vs ADM, FIP: −0.527% | Yes |
| 19 | "+2.6% [+1.0, +4.1]; +5.2% [+2.9, +7.6]" | §6.3 | table2 | +2.61 [+1.04, +4.07]; +5.19 [+2.91, +7.57] | Yes |
| 20 | "disadvantage for wOBA and FIP was largest in 2021" | §6.3 | `figures/data/fig4_year_by_year.csv` | wOBA: 2021 max (+10.55) ✓; **FIP: 2021 +2.28, 2022 +12.77** | **No** (FIP) |
| 21 | "2026: −3.8% [−7.3, −0.1]; −2.4% [−4.4, −0.2]; −3.7% [−5.9, −1.3]" | §6.3 | table2 | −3.78 [−7.26, −0.10]; −2.36 [−4.39, −0.22]; −3.67 [−5.92, −1.34] | Yes |
| 22 | "never admitted (0 of 900)" | §6.5 | `PSL/sloan2027/results/placebo/placebo_verdicts.csv` | 0 Projection (896 Diagnostic, 4 Insufficient Evidence) | Count: yes. Description ("pure noise"): **no**, they are permutations |
| 23 | "Only two kinds of change altered out-of-time error" | §6.5 | `PSL/sloan2027/tables/table5_gate_ablation_threshold_sensitivity.csv` | min-folds 4, share 0.75 and materiality 0.25% also moved error | **No** |
| 24 | "0.05 FIP units (90th pct 0.14), 53%" (Stuff+) | §7 | `PSL/sloan2027/results/players/forecast_changes.parquet` | median 0.055; p90 0.144; 53.4% | Yes |
| 25 | "top decile −0.14, 69%; bottom +0.16, 39%" | §7 | `figures/data/fig5_stuff_deciles.csv` | −0.144, 68.9%; +0.160, 38.5% | Yes |
| 26 | Rogers: "−61°, Stuff+ 85–88, +0.37–0.54, FIP 3.21–3.99" | §7, Fig 5 | `figures/data/fig5_cases.csv` | arm angle −58.8 to −64.1 (mean −61.2); 85.0–88.1; 0.369–0.538; 3.21–3.99 | Yes |
| 27 | "4 of the 6 largest … 5 of those 6 worsened" | §7 | `forecast_changes.parquet` | top 6 \|Δ\|: Rogers ×4, Alvarado (improved), Abreu (worsened) | Yes |
| 28 | Wheeler: "104–107; 0.16–0.24; every one improved" | §7 | `fig5_cases.csv` | 104.5–106.7; −0.157 to −0.238; 5/5 | Yes |
| 29 | K%: "median 0.13, 90th pct 0.36; −0.36, 70% vs 39%" | §7 | `unit_translation.csv`, `cohort_effects.csv` | 0.133; 0.361; −0.358, 69.6% vs 39.3% | Yes |
| 30 | xwOBA: "5.3 points (13.4); −11, 70%; +15, 54%" | §7, Table 2 | same | 5.31 (13.37); −10.6, 69.7%; +15.5, 53.8% | Yes |
| 31 | "to within 2 × 10⁻¹⁵" | §8.1 | `audits/fb_upstream_consistency.csv` | max 1.78×10⁻¹⁵; all 72 references matched | Yes |
| 32 | "HR 0.64 [0.60, 0.67] … fielding 0.23 [0.17, 0.28]" | §8.2 | `fantasy/level1_correlations.csv` | 0.635 [0.596, 0.672] … 0.225 [0.165, 0.284] | Yes |
| 33 | Table 6 wOBA → HR: "7.98 → 7.89; −1.02 [−2.16, +0.03]; −1.54 to −0.52; 5/5; 0.310" | Table 6 | `results_by_target_category.csv` | 7.976 → 7.894; −1.021 [−2.157, +0.032]; −1.544 to −0.523; 5/5; 0.3098 | Yes |
| 34 | Table 6 FIP → ERA/WHIP: "Holm p 0.008" | Table 6 | same | raw p 0.0009995 (= 2/2001, bootstrap floor) × 8 = 0.007996 | Yes (at floor) |
| 35 | Table 6 hitter bWAR → value: "[−0.91, −0.01]; 0.270" | Table 6 | same | [−0.911, −0.006]; 0.2699 | Yes |
| 36 | "Raw K-BB% → ERA −0.1% [−0.3, 0.0]" | Table 2 | same | −0.132 [−0.304, **+0.046**] | Partial (upper bound misrounded) |
| 37 | "Stuff+ → FIP −0.48% [−0.92, −0.03]" (caption: 2021–25 unless noted) | Table 2 | `table3_flagship_contrasts.csv` | that is the 2019–25 value; 2021–25 is −0.76 [−1.46, −0.02] | **No** (period) |
| 38 | "9 favored the forecasts" (2026, secondary) | §8.4 | `results_by_target_category.csv` | 9 of 132 "directional gain"; 1 harmful | Yes (denominator missing) |
| 39 | "0.631 → 0.651; 0.484 → 0.503; +0.03 [−0.05, +0.09]; +0.05 [−0.06, +0.17]" | §8.5 | `fantasy/ranking_value_sensitivity.csv` | 0.6305 → 0.6515; 0.4844 → 0.5034; +0.025 [−0.055, +0.089]; +0.051 [−0.056, +0.170] | Yes |
| 40 | ERA: "−5.1 [−6.7, −3.7]; −5.6 [−7.3, −3.9]; +0.5 [−0.2, +1.1]; +2.4 [+0.2, +4.6]; +0.8 [−0.2, +1.9]" | §9 | `fantasy/generalization_era/comparisons.csv` | −5.15 [−6.66, −3.73]; −5.61 [−7.27, −3.95]; +0.49 [−0.17, +1.14]; +2.44 [+0.20, +4.65]; +0.85 [−0.22, +1.90] | Yes |
| 41 | "6–9 metrics per window" | §9 | `generalization_era/selected_sets.csv` | 6, 8, 8, 9, 9 | Yes (the listed names omit ev_against) |
| 42 | "71 automated tests … 55 of 55 … 873 files" | App. C | `audits/phase1_reverification_2026-11-13.log`; `PSL/sloan2027/00_immutable_baseline_manifest.json` | 71 passed; 55 rows "match"; 873 | Yes |
| 43 | "Of the 140 … 46 … 1 harmful" | App. D | `results_by_target_category.csv` | 140 pooled rows; 46 "adds information"; 1 harmful (2021–25) | Yes |
| 44 | "all 1,328 outcome-observed pitcher-seasons" | Fig 5 caption | `fig5_stuff_deciles.csv` | Σn = 1,328 | Yes |
| 45 | Yahoo points weights (§3.1 bullet) | §3.1 | `fantasy/scoring_weights.json` | identical | Yes |
| 46 | "+0.03 [−0.05, +0.09] z-units" | Ledger rows 207–208 | `paper/claims_to_evidence.csv` | the ledger writes "%" | Ledger error (m22) |

---

## 5. Overall recommendation

**Major revision. Do not submit in the current form.** The core work is sound and unusually transparent, and the narrowed claims are mostly honest. But a skeptical Sloan reviewer who opens the repository would find factual errors in the text (M3, M6, M7d/e/j/k, m1, §10.6) and undisclosed weaknesses the project's own audits say must be disclosed (M4, m9, m10). These would cost far more credibility than the fixes cost time.

Suggested order before 2026-12-01:

1. **Text corrections with no new analysis.** M3, M6 (rewrite §6.5), M7, M8 (wording, period, rounding, citations), M11, M12, M16, m1, m14, and §10.6 (M1c).
2. **Disclosures.** M4 (§6.1 paragraph and Table 7 rows), M5 (§8.1 wording plus protocol hashes), m8, m9, m10, m23.
3. **Targeted reruns, all feasible with the existing pipeline:**
   - M1: put three-year history or a Marcel replica in the baseline, or at least show the decomposition;
   - M2: within-season skill and season-level intervals;
   - M9: retention by decile and IPW;
   - M10: rostered-pool z-scores and SD scaling;
   - M7a: a playing-time decomposition, or delete the claim.
4. **Presentation.** M13 (units table and named cases), M14 (per-target paragraphs), M15 (figure fixes), m18 (short conclusion; translate 1% into standings terms).

If items 1–3 are done, I would expect rigor to move to 4/5 and application to 3–4/5. The paper's central message — a metric's value depends on the forecast it feeds, and correlation is not added information — would then be stated at the strength the evidence supports.

---

## 6. Referee re-analysis notes (so the author can verify)

All inputs are the project's own files; no project file was modified.

1. **Season-level intervals (M2).**
   - Input: `fantasy/by_year.csv`, rows with `family == "primary"` and sample 2021–2025.
   - For each linkage: mean of the five per-season `delta_pct`; t(4) 95% CI; exact two-sided sign-flip p over all 32 sign patterns.
2. **Within-season comparison of six-target forecasts (M2).**
   - Input: `PSL/sloan2027/results/nested/predictions_default.parquet`, `outer_year ≤ 2025`, models `B0|ridge` and `ADM|ridge` on identical (player, season) rows.
   - Residual = y − pred. Subtract each model's weighted (`w`) mean residual within each outer year, then recompute weighted RMSE and ΔRMSE%.
   - The raw values reproduce the paper exactly: −2.60, −7.50, −5.79, −0.99, −0.29, −1.70.
   - Within-season values: wOBA −4.97, FIP −4.40, baserunning −6.24, fielding −0.99, hitter WAR −0.41, pitcher WAR −1.69.
   - Same procedure on `local/fantasy/downstream_predictions.parquet` (window ≤ 2025; ratio rows with w > 0):

     | Linkage | Raw | Within-season |
     |---|---|---|
     | FIP → ERA | −1.17 | −1.25 |
     | FIP → WHIP | −1.30 | −1.63 |
     | wOBA → HR | −1.02 | −1.60 |
     | sprint speed → SB | −0.71 | −0.64 |
     | Barrel% → HR | −1.62 | −1.68 |
     | FIP → pitcher value | −1.77 | −2.30 |
     | hitter WAR → value | −0.46 | −0.43 |
3. **Retention by Stuff+ decile (M9).**
   - Input: `PSL/data/processed/pitcher_labeled.parquet`, seasons 2020–2024.
   - Year-t eligible via `psl.data.assemble._ip_threshold` (80/30 IP; 25/10 in 2020); deciles of `stuff_plus` within season.
   - Retained = (mlbam_id, season) present in `pitcher_sample_role_ip.parquet`.
   - Retention by decile (1→10): 0.54, 0.52, 0.59, 0.62, 0.63, 0.68, 0.63, 0.74, 0.69, 0.64.
4. **Pick overlap and rank changes (M7b, M10).**
   - Input: `local/fantasy/decision_rankings.parquet`.
   - Per window and group: top-k by `pv_base` vs `pv_aug`; overlap share; median \|rank change\| by baseline-rank bucket.
   - SD of `realized_value` over 2021–2025: hitters 3.81, pitchers 3.24.
5. **Code paths read for leakage and method checks (M3–M5).**
   - Fantasy bridge: `experiments/fb02_upstream.py`, `experiments/fb03_bridge.py`, `experiments/fb_lib.py`.
   - Canonical engine: `/Users/Shirin/Future_Predictor/src/psl/admission/run.py` (`_greedy_family_representatives`, `assert_audited_admission_table`), `src/psl/admission/engine.py` (`incremental_oos`), `src/psl/models/baselines.py` (`bootstrap_delta`), `src/psl/config.py`, `src/psl/catalog.py`.
   - Note: `src/psl/catalog.py` and `components.py` carry uncommitted edits in the Future_Predictor working tree. Line numbers refer to the working tree; confirm against commit 17da742 before quoting them.
