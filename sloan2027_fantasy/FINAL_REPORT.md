# FINAL REPORT: Sloan 2027 Paper 18, fantasy revision (2026-11-13)

Every number below comes from a committed artifact. Intervals are 95% paired player-cluster bootstrap intervals; ΔRMSE is given as a percentage of the reference model's RMSE, and negative favors the first-named model.

**Status:**
- not submitted, not emailed, and the app is not deployed;
- pushed only to the new repository `MIT_Sloan_2027_Fantasy_Baseball_Projection_Lab_Paper`, which the author designated for this work;
- the original Projection-Signal-Lab repository and its site are untouched: all 873 baseline files are byte-identical.

## 1. Answers to the five required questions

**(a) Why these six outcomes?**
- They cover four components: hitting (wOBA), the pitcher's own run prevention (FIP), baserunning, and fielding. Two aggregates, hitter and pitcher bWAR rates, test whether a metric's usefulness depends on the job.
- Defense is the deliberate boundary case: real value that fantasy scoring ignores. WAR is the aggregate stress test.
- The targets were chosen before the fantasy framing and are unchanged. None of them is a fantasy category, and their fantasy roles were assigned afterward and then tested.
- Manuscript Section 2 has Table 1 plus a paragraph per target covering construct, role, construct caveats, and what was found.

**(b) Which target forecasts add out-of-time information for fantasy scoring beyond reasonable baselines?**
- **FIP is the only one at the player level.**
  - It improves ERA (−1.17% [−1.77, −0.59], Holm p = 0.008) and WHIP (−1.30% [−2.02, −0.57]) beyond a category-history model. On the full pool it also improves pitcher 5×5 value (−1.77%).
  - **Season-level caveat:** both ERA and WHIP reversed in 2023. Treating the five seasons as units, the intervals include zero: ERA −1.13% (t(4) interval −2.69 to +0.44); WHIP −1.24% (−3.34 to +0.86).
- **No multiplicity-robust gain:**
  - wOBA → HR: −1.02% [−2.16, +0.03], improved in 5 of 5 seasons. Its season-level interval excludes zero, so the player-level and season-level views disagree.
  - wOBA → AVG, baserunning → SB, fielding → value, and pitcher WAR → value: no detectable gain.
  - Hitter WAR → value: −0.46%, not robust to multiplicity.
- **Exploratory findings:**
  - raw sprint speed improves SB forecasts (−0.71%) and beats the baserunning forecast in a paired test (−0.41% [−0.75, −0.06], post hoc);
  - Barrel% (−1.62%), exit velocity (−1.44%, post hoc) and xwOBA (−1.18%) improve HR forecasts;
  - WAR forecasts mostly carry playing time.
- **2026:** no primary linkage has an interval excluding zero. 9 of 132 secondary comparisons favor the forecasts with intervals excluding zero, against about 3 expected by chance; the comparisons are correlated, so this is weak evidence.
- **Draft decisions:** rank agreement improves by about 0.02 Spearman. Picks are not detectably better at the protocol, Yahoo, or NFBC roster sizes; the gain is under 0.02 SD per pick.

**(c) Where do popular fantasy beliefs agree or disagree with the evidence?** This is the manuscript's Table 2, with sources.
- **Agree:**
  - FIP-type skill composites (not FIP history itself) for ERA and WHIP;
  - power metrics for HR;
  - sprint speed for SB;
  - WAR is not fantasy value.
- **Qualify:**
  - "sell high" on xwOBA over-performers holds up better than "buy low", conditional on returners;
  - K-BB%'s signal is its strikeout part, and it adds nothing beyond the category history;
  - the in-house Stuff+ adds nothing to strikeout rate or ERA beyond the history.
- **Not supported:** "more Statcast always helps".
- **Not tested:** "playing time dominates" and points-versus-categories differences.

**(d) What can the app actually do today?** See Section 6.

**(e) What remains unvalidated, and why?**
- No prospective test.
- The fantasy evidence is exploratory.
- Season-level evidence covers only five seasons.
- No ADP-aware or position-aware draft evaluation.
- No 2027 forecasts.
- No re-selection inside non-linear models.
- Rookies are excluded.
- Role, process and family labels are human choices.
- No Marcel-style baseline was run.

## 2. Experiments
| ID | What | Result |
|---|---|---|
| Phase 1 | 71 tests; 55/55 reproduction checks; 873/873 hashes; leakage audit | All pass |
| FB L0–L3 | Fantasy bridge (protocol v1.0, pushed before fitting) | See (b); 140 pooled comparisons: 46 add information, 1 harmful |
| FB-G | ERA nested admission (Amendment 1, pushed before running) | ERA-specific −5.1%; reusing FIP's selection −5.6%; no difference between them |
| FB-PH | Post hoc referee checks (Amendment 2) | History decomposition, season-level and within-season checks, retention/IPW, direct tests, roster-size draft checks, named cases |

### History decomposition (post hoc)
For each target, the gain over the two-year baseline from adding only a third season of history, and the further gain from the other admitted metrics:

| Target | Third season of history alone | Other admitted metrics beyond it |
|---|---|---|
| FIP | none (+0.8%) | −8.2% |
| Baserunning | −0.8% | −5.0% |
| wOBA | −0.6% | −2.0% |
| Pitcher WAR | 0.0% | −1.7% |
| Fielding | −1.2% | **+0.2% (worse)**: the whole gain is history |
| Hitter WAR | −0.75% | +0.5% (none): history alone beats selection |

## 3. Internal referee review and resolutions (`audits/referee_self_review.md`, "major revision")
| Issue | Resolution |
|---|---|
| M1: baseline/history | §5.1 states the baseline is two-year. Table 5 decomposes the gain into third-season history versus other metrics. Figure 2 splits the 27 Projection labels into 6 baseline inputs, 4 own-history windows and 17 other metrics. Abstract, §6.2 heading and §10.6 corrected. App flags the baseline-input labels. A full Marcel baseline was not run; this is stated. |
| M2: season effects | §5.5 states the inferential target. Season-level t(4) intervals appear in Table 8 and §8.3, including the 2023 reversal. Within-season ΔRMSE is in §6.2 and §8.3. The abstract carries the caveat. The era bullet is expanded. |
| M3: K% vs K-BB% | §5.4 rewritten: correct families, the greedy step, the BB% null, and pooled values. §5.1 describes the greedy step. Families are listed as a human choice (§5.2, Fig. 1, Appendix E). |
| M4: reproduction caveats | New §6.1 paragraph listing five weaknesses. Table 9 gains rows. The gate bootstrap is described in §5.1. |
| M5: fantasy look-ahead / timestamps | §8.1 gives an accurate description of the training-row forecasts. Protocol commits are printed in the named copy and withheld in the blind copy. The text states the six-target results and 2026 had already been seen. |
| M6: ablations, inner-2017 | §6.5 lists every change that moved error, with direction and units. Appendix E has the full table. The inner-2017 sensitivity is reported: the elastic net beats selection for FIP. "Tied" replaced by "no detectable difference". |
| M7: overclaims | "Playing time dominates" removed; overlap and rank-change numbers reported instead. "Premium" changed to "modest extra weight". Defense and sprint-speed statements corrected. Rogers no longer generalized; the Stuff+ model's limits stated. "Every source" changed to "point estimates favored". Figure 4 statement corrected. The "raw beats target" claim now rests on a paired test. Secondary results labelled exploratory. |
| M8: Table 2 | Rows re-matched (FIP-type composites; EV→HR, post hoc; Stuff+→K/9, post hoc), with citations in rows, the period corrected, and two decimals near zero. |
| M9: survivorship | Retention by decile reported (54% bottom vs 64–74% top). Wilson intervals added. IPW leaves the pattern essentially unchanged (36% vs 69%). Conclusions softened. |
| M10: value score / draft | Eq. 5 completed with the WHIP term; the pool definition stated; z-units scaled to SDs; Yahoo/NFBC roster sizes added (post hoc); pre-specified overlap metric and points backtest reported; the FIP → pitcher value result promoted. |
| M11: 2026 | 2026 selected-vs-baseline results reported (only pitcher WAR detectable) plus the 2026 pitcher-WAR kitchen-sink result. "Retrospective" added to the abstract and §1. The ancillary files are named. |
| M12: departures | Table 9 adds the withdrawn operations claim, temporal stability, look-ahead, the original comparison's flaws, and the baseline. Appendix A is cited from §1. |
| M13: units / names | Table 5 gives units. A rule-based named-case table (Table 7) covers Ben Rice, Alex Kirilloff, Daniel Schneemann, Andrew McCutchen, Jose Quintana and Miguel Castro. HR and SB changes are put in words. |
| M14: six-target section | A paragraph per target covers construct caveats (FIP label sources, cross-provider fielding, the baserunning fallback never used, the different pitcher-WAR population), roles assigned afterward, and per-target findings. |
| M15: figures | Fonts ≥ 7 pt. Figure 6 markers have fixed meanings and "−0.0" is fixed. Figure 7 legend moved and encodings separated. Direction labels on Figures 3 and 4. Figure 4 caption fixed. Wilson intervals on Figure 5D. Figure 2 split. Lossless images in the proof. |
| M16: anonymity | The blind copy withholds commit hashes and the preprint sentence and describes the app generically. The repository link remains only in the submission form. |
| Minor (m1–m28) | All addressed in text or tables, with two exceptions: the DOCX app.xml counts are scrubbed, and the regional ESPN URLs are kept as fetched. |

## 4. Data rights and provenance (author decisions flagged)
- **Raw data not redistributed.** Raw MLBAM and Sports Reference tables and player-season panels are not committed. Rebuild scripts and SHA-256 manifests are provided instead.
- **Curated player examples.** The app ships 420 player-seasons. **Author decision:** keep, shrink or remove them before any public deployment.
- **Sports Reference automated access.** Sports Reference asks for written permission for automated access, and the data were collected programmatically (via pybaseball). **Author decision:** seek permission, or describe the rebuild as a manual download.
- **Anonymity.** The repository URL names the author, and a preprint is public. The blind DOCX has no names, links or commit hashes. Named copies and the organizer email draft stay local (unsent).

## 5. Paper
- **Blind manuscript:** `paper/sloan_2027_fantasy_revised.docx`. Official template, 5 numbered equations, 7 figures, 11 tables, 82 references, 328 logged values in `claims_to_evidence.csv`. Schema-valid.
- **Proof:** `paper/sloan_2027_fantasy_revised_proof.pdf`, 38 pages, rendered with LibreOffice 26.8.2 and Caladea with lossless images. **Microsoft Word was not available; the author must check the file in Word.**
- **Supporting files:** `figure_map.md`, `original_vs_revised_claims.md`, `references_verified.md`, `metric_definitions_sources.md`, `SUBMISSION_PACKET.md`.

## 6. App (`app/`)
**Screens:**
- Metric→Target Explorer: all 208 evaluations; "Not evaluated" for absent pairs; verdict basis shown, including the flagged baseline inputs;
- Fantasy Linkage Explorer;
- Player Casebook;
- Model Comparison;
- Value Lab (illustrative);
- Methods & Sources.

**Tests:** 68 unit and integration tests and 13 Playwright e2e tests pass, covering no console errors, all tabs, filters, 360 px width, axe accessibility checks, and keyboard navigation. The build is 1.5 MB.

**Deployment:** root `vercel.json` (`npm ci --prefix app` → `app/dist`). Not deployed. To deploy, connect the repository in Vercel, or run `vercel --prod` from the repo root after authenticating.

## 7. Remaining author decisions before December 1
1. Check the DOCX in Microsoft Word, then read the whole paper.
2. Settle anonymity, open data, and the subtitle, optionally by sending the local email draft.
3. Settle data rights: Sports Reference permission and the curated casebook.
4. Optionally approve a Vercel deployment.
5. Submit via the form (Paper ID 18) by **December 1, 8:59 p.m. Pacific**.
