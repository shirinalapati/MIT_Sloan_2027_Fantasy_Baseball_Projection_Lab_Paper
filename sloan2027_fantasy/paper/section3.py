"""Section 3 (fantasy practice and prior work) and the Section 10.2 audit discussion.

Every fantasy-practice statement is taken from the verified research files (fantasy/scoring_conventions.md,
fantasy/projection_systems.md, fantasy/research_sources.md, fantasy/practice_audit.csv); citation keys "fa:Sxx" resolve to
the source table in fantasy/research_sources.md via fantasy_refs.py. Empirical results come from content_data getters.
"""
from __future__ import annotations

import pandas as pd

from build_manuscript import ev, m, pct

H, Pi = "hitter", "pitcher"
TF, AV, DM, JT = "target_forecast_added", "admitted_vs_history_target_forecast", "direct_metric_added", "joint_target_forecasts"


def section3(b, D):
    c = b.cite
    b.h2("3.1 Formats decide what a forecast is for")
    b.para(
        "Fantasy formats differ in what they reward. Yahoo made head-to-head points the default for newly created leagues in 2026. Its "
        f"rotisserie and category formats score runs, home runs, RBI, stolen bases and batting average for hitters, and wins, saves, strikeouts, ERA and WHIP for pitchers "
        f"{c('fa:S01', 'fa:S02')}. ESPN's standard rotisserie adds holds (\"5×6\") {c('fa:S04')}. The high-stakes NFBC Main Event uses 15-team 5×5 rotisserie leagues with 23 "
        f"active players {c('fa:S06')}. Points systems weight events very differently. Measured against an inning pitched, which earns 3 points on all three "
        f"platforms, a strikeout is worth 3 points on Yahoo, 1 on ESPN and half a point on CBS {c('fa:S01', 'fa:S03', 'fa:S07')}. The same strikeout skill therefore "
        "matters several times more in one league than in another. None of the six study targets appears in any of these scoring systems.")
    b.para(
        "This paper therefore declares its formats instead of assuming one:")
    b.bullets([
        "**Primary:** a 12-team 5×5 rotisserie league with Yahoo's default categories.",
        "**Sensitivity:** Yahoo's default points scoring, with weights transcribed from Yahoo's help page before any fantasy model was fit: singles 2.6, doubles 5.2, "
        "triples 7.8, home runs 10.4, runs and RBI 1.9, walks and hit-by-pitches 2.6, steals 4.2; for pitchers, wins and saves 8, strikeouts 3, outs 1, earned runs −3, and "
        "walks, hits and hit batters −1.3.",
    ])
    b.para(
        "Ratio categories (AVG, ERA, WHIP) are aggregated from their components. Fantasy value means different things in different contexts: a raw category total, a z-score or "
        f"standings-gain value against replacement level, or an auction price {c('fa:S09')}. Section 8 uses category totals and a transparent z-score value. It does not claim "
        "to estimate auction prices or league outcomes.")
    b.h2("3.2 What public projection systems already do")
    b.para(
        "Managers rarely build forecasts from scratch. Public systems on FanGraphs disclose varying amounts of method, and their approaches differ:")
    b.bullets([
        f"**Marcel**, the deliberately naive benchmark, weights three seasons 5/4/3, regresses toward the league average and applies a simple age adjustment {c('marcel')}.",
        f"**Steamer** regresses each statistic in proportion to its unreliability but does not publish its full formula {c('fa:S51')}.",
        f"**ZiPS** builds baselines from several seasons and projects from a cohort of comparable players, adding Statcast inputs only after validating them; its basic version "
        f"assumes a full-time role {c('fa:S41')}.",
        f"**ATC** averages other systems with statistic-specific weights {c('fa:S42')}.",
        f"**THE BAT X** blends a results-based model with a Statcast-based one that uses maximum exit velocity, barrels and sprint speed {c('fa:S43')}.",
        f"**OOPSY** starts from Marcel and adds Stuff+, barrel rate and swing speed {c('fa:S44')}.",
        f"**FanGraphs Depth Charts** averages Steamer and ZiPS and assigns playing time by hand {c('fa:S39')}.",
    ])
    b.para(
        "Two lessons follow. First, mainstream projections already admit some Statcast information, mostly after their authors checked it, so the question this paper "
        "formalizes is one projection builders face informally. Second, playing time is treated as a separate and largely judgmental forecast, which is consistent with the "
        "separate role playing time plays in fantasy value (Section 8.5 shows that adding skill forecasts barely changes the top of a ranking). Archived preseason projections from these systems are members-only or subject to terms that restrict "
        f"redistribution {c('fa:S40')}, so the study's fantasy baseline is its own transparent model rather than an external system. That limitation is stated in Section 11.")
    b.h2("3.3 Popular metrics, popular beliefs, and what this paper tests")
    b.para(
        "Fantasy analysis leans on a recognizable toolkit:"
        f" expected statistics and Barrel% to find hitters due for breakouts or regression {c('mlb_xwoba', 'fa:S17')};"
        f" FIP, xFIP and SIERA instead of ERA, following the evidence that pitchers have limited control over balls in play {c('mccracken', 'fa:S19')};"
        f" K-BB% as a quick summary of pitching skill {c('fa:S21')};"
        f" Stuff+ and related pitch models {c('fg_stuff', 'driveline')};"
        f" and sprint speed as a steals indicator, especially after the 2023 rule changes {c('fa:S25')}, which were followed by higher league stolen-base totals {c('fa:S26')}."
        " Analysts who tested these ideas disagree about their size:")
    b.bullets([
        f"Baseball Prospectus warned that expected metrics can mislead for pitchers {c('judge_siren', 'fa:S24')};",
        f"FanGraphs analyses found hitter expected statistics useful, although less so in season {c('szym_xstats', 'fa:S14', 'fa:S15')};",
        f"steals analyses stress attempt rate and opportunity more than raw speed {c('fa:S27', 'fa:S28')};",
        f"fantasy writers say WAR is *not* fantasy value, because defense, position and replacement level do not score {c('fa:S30')};",
        f"playing time is widely described as the dominant, underrated driver of value {c('fa:S32', 'fa:S33')}.",
    ])
    b.para(
        f"Reliability (\"stabilization\") studies are often cited as evidence of which numbers to trust, but stable is not the same as predictive of a different target {c('carleton')}. "
        "Table 2 turns the most common beliefs into falsifiable statements and records what this paper's tests found. The beliefs, sources and counter-views are documented in "
        "the repository's practice audit. The review covers published articles, provider documentation and platform help pages; discussion forums were outside its scope, "
        "so no forum consensus is claimed. Where the audit found that a strong version of a belief is a straw man (for example, \"speed alone predicts steals\" or "
        "\"WAR is a fantasy shortcut\"), Table 2 tests the version people actually publish.")
    audit = audit_table(D, c)
    b.table(audit, "Conventional-wisdom audit. Each belief is stated as it appears in public fantasy analysis (counter-views in the repository's practice audit) and "
            "matched to the closest test in this paper. Effects are ΔRMSE % with 95% player-cluster intervals, outcome seasons 2021–2025; negative favors adding the metric "
            "or forecast. Rows marked post hoc were added after an internal review. Not tested here: BABIP regression, projection averaging, and points-versus-categories "
            "differences (which need a test of the difference, not of each format separately).",
            widths=[1.75, 2.75, 2.0], font=14)
    b.h2("3.4 Prior research and what is new here")
    b.para(
        "The statistical ingredients are not new, and the paper claims no firstness for them:"
        f" shrinkage toward the mean has a long history in baseball forecasting {c('efron_morris', 'brown', 'jensen')};"
        f" Bayesian variable selection and metric reliability have been studied for hitting and pitching statistics {c('piette', 'mcshane', 'franks')};"
        f" the predictive value of Statcast-era expected statistics has been tested directly {c('judge_expected', 'szym_xstats', 'bailey')};"
        f" measuring the *incremental* value of a new predictor beyond an existing model is standard in psychology and medicine {c('hunsley', 'pencina')};"
        f" and selecting variables on the data used to evaluate them is a known source of optimism, which nested validation removes {c('ambroise', 'varma', 'cawley')}."
        f" Time-ordered evaluation is the norm in forecasting {c('tashman', 'bergmeir')}, and the stability of feature selection has its own literature {c('meinshausen', 'nogueira')}."
        f" Fantasy sports have been studied mostly as optimization problems: lineup construction, drafts and contest strategy {c('haugh', 'hunter', 'fry')}."
        f" We did not find a peer-reviewed treatment of rotisserie valuation; practitioner methods (category z-scores, standings-gain points and auction calculators) are "
        f"documented by their providers {c('fa:S09', 'fa:S36')}.")
    b.para(
        "The contribution is a combination applied end to end:"
        " a single, auditable admission rule;"
        " applied across six targets that were chosen to differ;"
        " with nested chronological validation;"
        " with its human choices labelled;"
        " with its failures and harms reported at the player level in baseball units;"
        " followed by a pre-specified test of whether the resulting forecasts carry information about the categories fantasy players actually score.")


def audit_table(D, c):
    """Table 2 rows: belief as published (fantasy/practice_audit.csv, with sources) -> closest test -> finding (numbers from artifacts)."""
    S = D.SRC

    def r(*a, **k):
        return D.Fp(*a, sec="Table 2", nd=2, **k)
    rr = D.ret
    rows = [
        [f"xwOBA above wOBA marks an unlucky hitter (buy low); below marks regression (sell high) {c('mlb_xwoba', 'szym_xstats')}",
         f"xwOBA (two-year) → next wOBA, outer 2021–25: {D.T3('H1', 'Nested 2021–25, %', sec='Table 2')}. Largest wOBA-over-xwOBA decile: forecast lowered, 70% of "
         "forecasts more accurate; opposite decile: 54% (95% intervals about ±7–8 points; Section 7)",
         "Supported for forecasting wOBA; \"sell high\" holds up better than \"buy low\" (conditional on players who returned)"],
        [f"Barrel% and exit velocity flag power {c('fa:S17')}",
         f"Barrel% → HR {r(H, 'HR', DM, 'barrel_pct')}; exit velocity → HR {D.DIRECT('ev -> HR', sec='Table 2')} (post hoc); beyond HR history and playing time",
         "Supported for average HR forecasts; breakouts (large changes) were not tested"],
        [f"FIP-type skill measures project ERA better than ERA itself {c('fa:S19', 'fa:S21')}",
         f"FIP forecast (a skill composite) → next ERA {r(Pi, 'ERA', TF, 'fip')}; in the ERA admission (Section 9), two- and three-year FIP were never admitted beyond ERA history, while K% always was",
         "Supported for skill composites, not for FIP itself"],
        [f"The estimator signal carries over to WHIP and ratio value {c('fa:S22')}",
         f"FIP forecast → WHIP {r(Pi, 'WHIP', TF, 'fip')}; → pitcher 5×5 value {r(Pi, 'VAL_P', TF, 'fip')} (full pool, including non-returners)",
         "Supported, modestly (about 1–2% of forecast error)"],
        [f"K-BB% is the best quick indicator of pitching skill {c('fa:S21', 'fa:S16')}",
         f"FIP study: K% admitted; current K-BB% set aside in favor of three-year K-BB% (same family); BB% alone added nothing. Raw K-BB% → ERA {r(Pi, 'ERA', DM, 'k_bb_pct')}; → WHIP {r(Pi, 'WHIP', DM, 'k_bb_pct')}",
         "Qualified: its strikeout component carries the signal; adds nothing to a model with category history"],
        [f"Stuff+ predicts future results, especially strikeouts {c('fg_stuff', 'fa:S24')}",
         f"In-house Stuff+ → FIP, outer 2021–25: {D.T3('H4', 'Nested 2021–25, %', sec='Table 2')}; → strikeout rate per 9 IP {D.DIRECT('stuff_plus -> K9', sec='Table 2')} (post hoc); → ERA {r(Pi, 'ERA', DM, 'stuff_plus')}",
         "Small for FIP; no detectable gain for strikeout rate or ERA beyond category history"],
        [f"Fast runners are steals targets; attempts and opportunity matter most {c('fa:S27', 'fa:S28')}",
         f"Sprint speed → SB {r(H, 'SB', DM, 'sprint_speed')}, beyond SB-rate history and playing time; sprint speed vs baserunning forecast, paired: {D.DIRECT('BF+sprint_speed vs BF+br (SB)', sec='Table 2')} (post hoc)",
         "Supported: speed adds to attempt history, and the run-value target is the weaker intermediate"],
        [f"WAR is not fantasy value {c('fa:S30')}", f"Hitter WAR forecast → 5×5 value {r(H, 'VAL_H', TF, 'hwar')}; → at-bats {r(H, 'AB', TF, 'hwar')}; pitcher WAR → value {r(Pi, 'VAL_P', TF, 'pwar')}",
         "Agrees: WAR forecasts mainly carry playing time"],
        [f"Defense matters only through playing time {c('fa:S31')}", f"Fielding forecast → 5×5 value {r(H, 'VAL_H', TF, 'fld')}; → at-bats {r(H, 'AB', TF, 'fld')}",
         "No direct signal and no playing-time signal detected"],
        [f"Playing time is the dominant driver of fantasy value {c('fa:S32', 'fa:S33')}", "Not tested directly. In the draft backtest (Section 8.5), skill forecasts left 91–96% of the top-k unchanged",
         "Not tested"],
    ]
    return pd.DataFrame(rows, columns=["Belief as published (sources)", "Closest test in this paper", "Reading"])


def discussion_audit(b, D):
    b.para(
        "Table 2 shows several beliefs that hold up:"
        " weight pitchers' strikeout and run-prevention skill when forecasting ERA and WHIP;"
        " use expected statistics, Barrel% and exit velocity when forecasting home runs;"
        " use sprint speed for steals (and, through baserunning, for running value) but not for batting;"
        " do not treat WAR as fantasy value;"
        " and expect no fantasy signal from defensive metrics.")
    b.para(
        "It also shows where popular practice outruns the evidence. More Statcast inputs do not reliably help. This study's in-house pitch-quality score added little "
        "beyond a pitcher's recent strikeout and run-prevention record, and it mis-graded one extreme submariner in every season; whether that generalizes to other "
        "pitch models was not tested. WAR is a poor intermediate for rotisserie value, and its forecast mostly signals who will play.")
    b.para(
        "The most common reasoning step, correlation, is the one this paper most often contradicts. Forecasts of wOBA and baserunning correlate strongly with home runs and "
        "steals (Section 8.2), yet add little once the category history is already known.")
