"""Revised manuscript text (Paper ID 18). Numbers come from artifacts via content_data getters and are logged.

Run:  PSL_ROOT=... python sloan2027_fantasy/paper/build_content.py
Out:  paper/sloan_2027_fantasy_revised.docx (blind), paper/sloan_2027_fantasy_revised_named.docx (named; git-ignored),
      paper/claims_to_evidence.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_manuscript import CLAIMS, PAPER, Builder, ev, m, num, pct  # noqa: E402
import content_data as D  # noqa: E402
from bibliography import bibliography  # noqa: E402
from section3 import section3  # noqa: E402

TITLE = "One Metric, Different Jobs: Target-Specific Feature Admission for Major League Baseball Player Projection"
H, Pi = "hitter", "pitcher"
TF, AV, DM, JT = "target_forecast_added", "admitted_vs_history_target_forecast", "direct_metric_added", "joint_target_forecasts"
LIFT, KSR, KEN = "Selected vs baseline, % [95% CI]", "Kitchen-sink ridge vs selected, %", "Kitchen-sink elastic net vs selected, %"
L26, K26, E26 = "2026 selected vs baseline, %", "2026 kitchen-sink ridge vs selected, %", "2026 elastic net vs selected, %"


def build(blind: bool) -> Builder:
    CLAIMS.clear()
    b = Builder(blind)
    c = b.cite
    S = D.SRC
    lift = {s: D.T2v(s, LIFT) for s in D.STUDIES}
    five = [s for s in D.STUDIES if lift[s][2] < 0]
    lo5, hi5 = min(abs(lift[s][0]) for s in five), max(abs(lift[s][0]) for s in five)
    rog = D.cases[D.cases.case == "Rogers, Tyler"]
    whe = D.cases[D.cases.case == "Wheeler, Zack"]
    att_h = D.t4.loc["hitting_woba", "pct_failing_2026_playing_time_rule"]
    att_p = D.t4.loc["pitching_fip", "pct_failing_2026_playing_time_rule"]
    fip_sizes = [D.metas[("pitching_fip", T)]["n_selected"] for T in range(2021, 2027)]
    stuff_from = min(T for T in range(2021, 2027) if "stuff_plus" in D.metas[("pitching_fip", T)]["selected"])
    ev_war = sum("ev" in D.metas[("overall_war", T)]["selected"] for T in range(2021, 2027))
    sprint = D.fig1.loc["Baserunning rate"]
    sprint_w = D.fig1.loc["wOBA"]
    q05, nproj = D.mult["projection_rows_q_bh_all_lt_0.05"], D.mult["canonical_Projection_rows"]

    b.title_block(TITLE)
    # ================================================================== Abstract
    b.para(
        "**Abstract.** Fantasy baseball managers and public analysts can look up hundreds of statistics, from batting average to expected wOBA, sprint speed and "
        "pitch-quality scores. A statistic that *describes* a player well is not automatically one that *improves next season's forecast* once a sensible model already knows "
        "his recent record. This paper turns that distinction into a transparent, testable admission rule and applies it to MLB player-seasons from 2015–2025 for six "
        "next-season targets: wOBA, FIP, baserunning and fielding run-value rates, and Baseball-Reference WAR per 600 PA and per 200 IP. The original 208 metric–target "
        "evaluations reproduce exactly. Re-running the whole selection inside each training window, admitted metrics lowered forecast error against a history-only baseline "
        f"for five of six targets ({ev(m(f'{lo5:.1f}–{hi5:.1f}%'), S['t2'], 'abstract')} lower RMSE; not hitter WAR). The same metric often had different jobs: sprint speed "
        f"improved baserunning forecasts ({D.T3('H5', 'Nested 2021–25, %', 1, 'abstract')}) but added nothing to wOBA. Admitted models beat an all-metric ridge model for wOBA "
        "and FIP but tied a tuned elastic net, lost for both WAR targets, and lost for FIP in a 2026 check frozen before outcomes were downloaded. A new, pre-specified test "
        "then asked whether these forecasts carry information about real fantasy categories. Adding the FIP forecast to a fantasy-category history model improved next-season "
        f"ERA and WHIP forecasts ({D.Fp(Pi, 'ERA', TF, 'fip', sec='abstract')} and {D.Fp(Pi, 'WHIP', TF, 'fip', sec='abstract')}); wOBA, baserunning, fielding and WAR forecasts "
        "showed no multiplicity-robust gain for their pre-specified categories, although raw sprint speed and Barrel% did help stolen-base and home-run forecasts. The "
        "contribution is an auditable way to ask which public metrics deserve to change a forecast, with its failures shown, not a new projection system or a promise of "
        "fantasy wins.", size=21)

    # ================================================================== 1 Introduction
    b.h1("1. Introduction: a fantasy manager's question")
    b.para(
        "Before a draft, a fantasy manager can sort hitters by expected wOBA (xwOBA), Barrel%, exit velocity or sprint speed on Baseball Savant, compare pitchers by FIP, "
        f"K-BB% or a pitch-quality score, and read projection systems that blend several of these {c('savant', 'fa:S40', 'marcel')}. Each statistic is a reasonable "
        "*description* of what happened. The forecasting question is narrower: once a model already knows a player's last two seasons, his age and his playing time, does "
        "this statistic still change next season's estimate, and does the change make the estimate more accurate? Statisticians call this the difference between explaining "
        f"and predicting {c('shmueli')}. Fantasy discussions usually settle it one metric at a time, by correlation or anecdote.")
    b.para(
        "This paper treats the question as a decision rule that can be audited. A candidate metric is *admitted* to a target-specific projection only if adding it lowers "
        "out-of-time forecast error, in seasons the model has not seen, by a material and consistent amount, without being redundant with simpler information. Everything "
        "else keeps a descriptive role, and the reason is recorded. The rule is applied separately to six next-season targets, because a metric can earn a place in one "
        "forecast and add nothing to another. Sprint speed is the cleanest example. It is one of the most stable statistics in the data (year-to-year r = "
        f"{num(sprint_w.reliability_r, '.2f', S['fig1'], '1')}), it sharply improves next-season baserunning forecasts, and it adds nothing to next-season wOBA (Figure 1).")
    b.para("The intended reader is a public analyst or fantasy manager. The contributions are specific and falsifiable:")
    b.bullets([
        "**A reproducible admission rule with its human choices labelled.** The statistical test is separated from the human-specified labels: which inputs count as "
        "\"context\", and which failed metrics are kept as \"diagnostic\" (Section 5).",
        "**Stronger validation of the original six-target results.** The entire selection is repeated inside each training window (nested chronological validation), compared "
        "with broad regularized models on identical players, checked with placebo metrics, and examined season by season, including a 2026 check frozen before outcomes were "
        "downloaded (Section 6). Several original claims narrow or fail, and the paper says which.",
        "**Player-level evidence in baseball units**, for named players, including the largest adjustments that made forecasts worse (Section 7).",
        "**A pre-specified test of fantasy relevance.** Do forecasts of the six targets add information about real fantasy categories beyond a direct category-history model? "
        "The protocol was written and publicly time-stamped before any fantasy model was fit (Section 8).",
        "**A new-target generalization check** on next-season ERA (Section 9) and an open web application in which every result can be queried.",
    ])
    b.para(
        "The paper does not claim that its labels are universal baseball facts, that thinner models generally beat broad ones, or that it can replace the proprietary tracking "
        "and modeling of professional organizations. Public single-number metrics compress far richer data, and a team with pitch-level tracking, biomechanics and medical "
        "information faces a different problem (Section 10.4). Nor does it publish a 2027 leaderboard: the research question is which public metrics carry repeatable "
        "next-season information, not who will lead the league.")
    b.figure("fig1_decision_flow.png",
             "How a metric earns admission. Steps 1–4 and the gate box are statistical; the two dashed boxes are human-specified rules recorded in the metric catalog. "
             "The worked example uses the canonical seven-fold evaluation (outcome seasons 2019–2025): the same metric, sprint speed, is admitted for baserunning and labelled "
             "Diagnostic for wOBA. Source: canonical admission artifacts (commit 17da742).")

    # ================================================================== 2 Why these six targets
    b.h1("2. Why These Six Prediction Targets?")
    b.para(
        "The six targets were chosen for general MLB projection before the fantasy framing existed, and they are kept unchanged. They cover four *components* of a player's "
        "contribution (hitting, the pitcher's own run prevention, baserunning, fielding) and two *aggregate* value rates that combine components (hitter and pitcher WAR). "
        "The design question was whether a metric's usefulness depends on what is being forecast. Answering it needs targets that overlap, such as wOBA and hitter WAR, which "
        "both reward hitting, and targets that should not respond to the same inputs, such as baserunning versus wOBA, or fielding versus anything a hitter does at the plate. "
        "All six are *rates*: they measure performance per opportunity and deliberately leave out playing time, which Section 8 forecasts separately.")
    b.para(
        "None of the six is a standard fantasy scoring category. Default rotisserie formats score runs, home runs, RBI, stolen bases and batting average for hitters, and wins, "
        f"saves, strikeouts, ERA and WHIP for pitchers {c('fa:S01')}; points leagues score individual events. The six targets can matter to a fantasy manager only as "
        "*intermediate* indicators, and Section 8 tests whether they do. Table 1 states, for each target, what it measures in this study's code, why it was used, the "
        "hypothesized fantasy link, and what it does not establish.")
    t1 = pd.DataFrame([
        ["Next-season **wOBA**", "Weighted on-base average: each way of reaching base weighted by its average run value, on the OBP scale; per PA; ≥150 PA in t and t+1",
         "Tests whether hitting-process metrics (xwOBA, exit velocity, plate discipline) add to a hitter's own two-year wOBA",
         "Offensive rate skill → AVG, HR, R, RBI; points-league batting", "Not a category; ignores playing time, lineup slot and team context; silent on SB"],
        ["Next-season **FIP**", "Fielding Independent Pitching: (13·HR + 3·(BB+HBP) − 2·K)/IP plus a league constant; per IP; ≥80 IP (SP) or ≥30 IP (RP) in t and t+1",
         "The part of run prevention a pitcher controls most directly; tests pitch-quality and strikeout metrics", "K, BB and HR skill → ERA, WHIP, K",
         "Not ERA, WHIP, wins, saves or innings; ignores balls in play, sequencing and defense"],
        ["Next-season **baserunning rate**", "Baseball-Reference baserunning runs per 100 times on base (H+BB+HBP−HR); per 600 PA below 20 times on base; ≥150 PA",
         "A running-only component where speed metrics should matter most", "Running value → SB", "Not SB, attempts or success rate; no playing time or green light"],
        ["Next-season **fielding rate**", "Baseball-Reference fielding + catcher runs per 1,000 defensive innings; ≥200 innings in t and t+1",
         "A non-batting component and a deliberate boundary case", "None directly; at most through playing time", "Not scored in standard 5×5 or points formats"],
        ["Next-season **hitter bWAR/600 PA**", "Baseball-Reference position-player WAR scaled to 600 PA; ≥150 PA in t and t+1",
         "Batting, running, fielding and position combined: do component signals survive aggregation?", "Broad hitter quality; playing-time signal",
         "Not points or roto value; credits defense and position, which fantasy ignores; bWAR is not fWAR"],
        ["Next-season **pitcher bWAR/200 IP**", "Baseball-Reference pitcher WAR (runs-allowed based, adjusted for defense and park) scaled to 200 IP; no workload floor",
         "Aggregate pitching value; a noisy stress test", "Broad pitcher quality", "Not wins, saves or innings; differs from FanGraphs' FIP-based pitcher WAR"],
    ], columns=["Target", "What it measures here (verified in code)", "Why it was used", "Hypothesized fantasy link", "What it does not establish"])
    b.table(t1, "The six prediction targets (feature seasons 2015–2024; outcomes 2016–2025). Definitions verified against the study code and source documentation.",
            widths=[0.95, 1.75, 1.4, 1.1, 1.3], font=14)
    b.para(
        "**Components versus aggregates.** wOBA and FIP isolate skills that a player largely owns. The two run-value rates isolate skills that public metrics measure directly, "
        "such as sprint speed, but that fantasy formats ignore or count only indirectly. The WAR rates ask whether a metric that helps a component still helps once that "
        "component is diluted inside a broad value measure built on further modeling choices: positional adjustments, replacement level and, for pitchers, runs allowed with a "
        f"defense adjustment {c('bref_war')}. Baseball-Reference WAR is not FanGraphs WAR, whose pitcher version is built from FIP {c('fg_war')}; nothing here is a statement "
        "about fWAR.")
    b.para(
        "**Why keep defense and WAR in a fantasy-facing paper.** Defense is the boundary case: real player value that standard fantasy scoring never counts. A fantasy-relevant "
        "forecast should show little or no fielding signal, and a method that found one would deserve suspicion. The WAR targets are the opposite stress test. Many fans treat "
        "WAR as a shortcut for player quality, so the question is whether aggregate value is a useful intermediate for fantasy value or simply a different construct. Section 8 "
        "tests both roles instead of assuming them.")
    b.para(
        "**Box 1. Four summary statistics in plain terms.** *wOBA* weights singles, doubles, triples, home runs, walks and hit-by-pitches by their average run value and scales "
        f"the result like on-base percentage {c('fg_woba', 'tango_book')}. *xwOBA* credits each batted ball with the typical outcome of balls hit with similar exit velocity and "
        f"launch angle (adding sprint speed for some weakly hit balls) and keeps actual strikeouts and walks {c('mlb_xwoba')}: it describes quality of contact and cannot see "
        f"defense, park or what happens after contact. *FIP* rebuilds a pitcher's run prevention from strikeouts, walks, hit-by-pitches and home runs only {c('fg_fip')}, so it "
        "ignores balls in play. *Baseball-Reference WAR* adds batting, baserunning, fielding and positional runs relative to a replacement-level player and converts runs to "
        f"wins {c('bref_war')}. Each is a modelled summary, not a raw measurement.", size=20)

    # ================================================================== 3 Fantasy practice
    b.h1("3. What fantasy managers already use")
    section3(b, D)

    # ================================================================== 4 Data, populations and timing
    b.h1("4. Data, populations and timing")
    b.h2("4.1 Sources and seasons")
    b.para(
        f"Season-level hitting, pitching and fielding statistics come from the MLB Stats API {c('statsapi')} and Baseball Savant leaderboards {c('savant')}. Baserunning, fielding "
        f"and WAR come from Baseball-Reference's published WAR files {c('bref_data')}, downloaded on 2026-08-20 for 2015–2025 and on 2026-11-12 for 2026, and player "
        f"identifiers come from the Chadwick register {c('chadwick')}. Baseball-Reference revises historical WAR inputs from time to time {c('bref_update2025')}, so the "
        "download dates define the version used. Stuff+ here is the "
        "project's own expanding-window expected-whiff model of velocity, movement, spin, extension and location, scaled so that 100 is average and fitted only on seasons up to "
        f"t; it is not FanGraphs' Stuff+ {c('fg_stuff')}. A registry of {ev('402', S['repro'], '4.1')} fields yields {ev('208', S['repro'], '4.1')} eligible metric–target "
        f"evaluations across {ev('163', S['repro'], '4.1')} distinct metrics. Features come from season t and outcomes from season t+1, and every model is trained only on seasons "
        "before the one it forecasts.")
    b.h2("4.2 Two kinds of population")
    b.para(
        "The original evaluations, like most published projection tests, use **outcome-observed returners**: players who met the playing-time rule in both seasons. That is the "
        "right population for asking whether a metric predicts a *rate*, but it is not a draft-day population, because a manager does not know who will be injured or demoted. "
        f"In 2026, {ev(f'{att_h:.0f}%', S['t4'], '4.2')} of hitters and {ev(f'{att_p:.0f}%', S['t4'], '4.2')} of pitchers who were eligible in 2025 failed the 2026 playing-time "
        "rule and would drop out of an outcome-observed evaluation. The fantasy analysis in Section 8 therefore uses **forecast-date pools** defined only by the previous season "
        "(at least 150 PA, or the FIP study's innings floor), keeps players who never return, and scores them as producing zero counting statistics. That is what a drafted "
        f"player who misses the season contributes. In 2021–2025 the pools hold {ev(f'{D.POOL[H]:,}', S['cb'], '4.2')} hitter-seasons and "
        f"{ev(f'{D.POOL[Pi]:,}', S['cb'], '4.2')} pitcher-seasons. In a given season only {ev(m(f'{100 * D.CANON_T1[H]["min"]:.0f}–{100 * D.CANON_T1[H]["max"]:.0f}%'), S['cb'], '4.2')} "
        f"of pool hitters and {ev(m(f'{100 * D.CANON_T1[Pi]["min"]:.0f}–{100 * D.CANON_T1[Pi]["max"]:.0f}%'), S['cb'], '4.2')} of pool pitchers would have met the original "
        "study's next-season rule. Rookies and players below the thresholds are outside both populations, so every conclusion applies to established major leaguers.")
    b.h2("4.3 Data rights")
    b.para(
        f"MLB Advanced Media and Sports Reference restrict redistribution of their data, and Sports Reference's data-use policy also asks for written permission before "
        f"automated access {c('fa:S50')}, so rebuild scripts should be run only in line with those terms. The public repository therefore contains code that rebuilds every dataset from the "
        "original sources, SHA-256 checksums of each derived file, aggregate results, and a small curated set of player examples. It does not contain raw tables or "
        "player-season panels (Appendix C).")

    # ================================================================== 5 Method
    b.h1("5. How a metric earns admission")
    b.h2("5.1 Baseline, loss and the incremental test")
    b.para(
        "Each target has a **history baseline** B: a ridge regression on the target's own two-year history, age, playing time and park factor (starter role for pitchers; "
        f"position group for fielding) {c('hoerl')}. Errors are weighted by opportunities (PA, innings or defensive innings). For fold k and feature set F, accuracy is the "
        "weighted root-mean-squared error:")
    b.equation("rmse")
    b.para(
        f"The **incremental effect** of candidate metric j is the average change in RMSE when j is added to the baseline, across K expanding chronological folds {c('tashman', 'bergmeir')}. "
        "Each fold trains on all seasons before its test season. The canonical study uses seven folds with outcome seasons 2019–2025; negative values mean the metric helped:")
    b.equation("delta")
    b.para("A metric is a candidate for **Projection** only if the improvement is material (at least 0.5% of the baseline RMSE), measured over at least three folds, and "
           "either consistent (improving in at least 60% of folds, π) or clearly negative (upper 95% bootstrap bound u below zero):")
    b.equation("admit")
    b.para(
        "It must then also survive a feature-family redundancy step. Within a family (for example two-year, three-year and current-season versions of the same rate), only "
        "the best-performing member is kept. It also needs a coefficient that changes sign fewer than two times across folds, coverage of at least 70% of player-seasons, and "
        "no material harm in a majority of large subgroups (age, playing time, handedness, role).")
    b.h2("5.2 What the labels mean, and which ones are human choices")
    t3 = pd.DataFrame([
        ["Projection", "Passes the incremental test and every gate", "Statistical", f"{D.VERDICTS['Projection']}"],
        ["Diagnostic", "Fails the projection test (or is redundant with a kept family member) **and** the catalog flags it as an interpretable process measure", "Statistical test, then a human flag", f"{D.VERDICTS['Diagnostic']}"],
        ["Exclude", "Fails the projection test and carries no process flag; means \"no conditional value for this target given this baseline\", not \"useless\"", "Statistical test, then a human flag", f"{D.VERDICTS['Exclude']}"],
        ["Context", "Park, environment, age or playing-time inputs, whatever their lift", "Human-specified role", f"{D.VERDICTS['Context']}"],
        ["Augmented Projection / Insufficient Evidence", "Predictive only where observed / too few folds and too sparse coverage", "Statistical", "0 (every evaluation had 7 folds)"],
    ], columns=["Label", "Rule", "Basis", "Count (of 208)"])
    b.table(t3, "Admission labels, how each is decided, and whether a human choice is involved (decision rule `decide_verdict` in the study code; canonical counts).",
            widths=[1.2, 3.0, 1.35, 0.95], font=15)
    b.para(
        "Two points matter for reading the labels. First, the algorithm does not discover baseball semantics. \"Context\" comes from a role assigned in the metric catalog, and "
        "the difference between \"Diagnostic\" and \"Exclude\" is a human flag recording whether the metric is an interpretable process measure. Second, every label is "
        "conditional: on the target, on what the baseline already contains, on the population and on the seasons. An Exclude for wOBA says nothing about the same metric for "
        "baserunning.")
    b.h2("5.3 Four different things called \"unstable\"")
    t4 = pd.DataFrame([
        ["Feature reliability", "Year-to-year Pearson r of the metric itself (same player, t and t+1)", "Reported; listed in Diagnostic reasons; never gates", f"Sprint speed: r = {num(sprint_w.reliability_r, '.2f', S['fig1'], '5.3')}, yet no wOBA value"],
        ["Lift consistency", "Share of the 7 folds in which adding the metric lowered RMSE", "Gates: ≥60% (or CI below zero)", f"Sprint speed → baserunning: {int(sprint.folds_improved)} of {int(sprint.n_folds)} folds"],
        ["Coefficient drift", "Number of sign changes of the metric's coefficient across folds", "Gates: fewer than 2", "—"],
        ["Uncertainty", "Width of the 95% bootstrap interval of the RMSE change", "Gates only via \"CI below zero\" alternative", "Stuff+ → FIP pooled interval nearly touches zero"],
    ], columns=["Meaning", "How it is measured", "Role in the rule", "Example"])
    b.table(t4, "Operational definitions of \"unstable\". A metric can be stable in the first sense and useless for a target in the second.", widths=[1.1, 2.2, 1.6, 1.6], font=15)
    b.h2("5.4 Strikeout rate versus K-BB%")
    kpct, kbb = D.EV("k_pct", "pitching_fip"), D.EV("k_bb_pct", "pitching_fip")
    kbb3 = D.EV("k_bb_pct_w3", "pitching_fip")
    b.para(
        "FIP is built from strikeouts, walks and home runs, so its predictors deserve care. In the canonical FIP study, current-season strikeout rate (K%) is admitted as its "
        f"family's representative (Projection; ΔRMSE {pct(kpct['delta_pct'], nd=2, src=S['eval'], sec='5.4')} of baseline RMSE). Current-season K-BB% "
        f"({pct(kbb['delta_pct'], nd=2, src=S['eval'], sec='5.4')}) is labelled Diagnostic. That is not because it lacks information: a kept member of the same family already carries "
        f"it. The three-year K-BB% ({pct(kbb3['delta_pct'], nd=2, src=S['eval'], sec='5.4')}) was admitted as a separate representative. \"K-BB% is diagnostic\" therefore means "
        "\"redundant once K% and a longer K-BB% history are in the model\", not \"K-BB% does not predict FIP\".")
    b.h2("5.5 Nested validation, comparisons and the 2026 check")
    b.para(
        "The original evaluation chose metrics using the same seasons on which it reported accuracy. The reanalysis removes that look-ahead. For each outer season T from 2021 to "
        f"2025, the **entire** admission procedure is rerun on rows with feature season at most T−2, with inner test years 2018 to T−1 {c('varma', 'cawley', 'ambroise')}. The "
        "selected set S_T is then used to forecast season T:")
    b.equation("nested")
    b.para("All competing models are scored on the **same players and seasons**:", keep_next=True)
    b.bullets([
        "the history baseline (B0);",
        "the nested selection (ADM);",
        "the original look-ahead selection (FIX);",
        "a kitchen-sink model with every numeric skill candidate (KS), fitted as ridge with α = 1;",
        f"tuned versions of these: ridge, elastic net {c('zou')}, LightGBM {c('ke')} and random forest, with hyperparameters chosen on inner chronological folds.",
    ])
    b.para(
        f"Differences are reported as % of the reference model's RMSE, with 95% paired bootstrap intervals that resample players {c('cameron')}. A **2026 check** used the same "
        f"code: predictions for every 2025-eligible player were committed to version control before any 2026 outcome table was downloaded ({ev(fetch_time(), S['fetch'], '5.5')}). "
        f"The 2026 label pipeline was first validated on 2025, reproducing {ev(f'{D.LAB_OK:,} of {D.LAB_N:,}', S['lv'], '5.5')} labels exactly. This is a *frozen-in-workflow, "
        "retrospective* check. The 2026 season had already been played and earlier ancillary files contained some 2026 rows, so it is not a prospective trial, and any "
        "analysis added afterwards is exploratory.")

    # ================================================================== 6 Results I
    b.h1("6. Results I: what survives stronger validation")
    b.h2("6.1 The original computation reproduces exactly")
    b.para(
        f"Re-running the canonical code on 2026-11-13 matched all {ev(f'{D.N_REPRO_MATCH} of {D.N_REPRO}', S['repro'], '6.1')} reproduction checks. These include the "
        f"402/208/163 counts, every published selective and kitchen-sink RMSE, and the label counts ({D.VERDICTS['Projection']} Projection, {D.VERDICTS['Diagnostic']} "
        f"Diagnostic, {D.VERDICTS['Context']} Context, {D.VERDICTS['Exclude']} Exclude). Figure 2 shows how those labels divide by target. Of the Diagnostic labels, "
        f"{ev(str(int(D.reason['Diagnostic — no material incremental lift'])), S['reason'], '6.1')} showed no material lift, and "
        f"{ev(str(int(D.reason['Diagnostic — predictive alone, redundant with a kept family member'])), S['reason'], '6.1')} were predictive alone but redundant with a kept "
        f"family member. Across all 208 tests with cluster bootstrap p-values, {ev(f'{q05} of {nproj}', S['mult'], '6.1')} "
        f"Projection rows have Benjamini–Hochberg q < 0.05 {c('bh')}. Because those seasons had already been examined, these adjustments are exploratory.")
    # ---------------- precomputed values for sections 6-11
    stq = D.t3.loc["H4", "BH q (all 208)"]
    st = D.units.loc["pitching_fip:stuff_plus"]
    kp = D.units.loc["pitching_fip:k_pct"]
    xw = D.units.loc["hitting_woba:xwoba_w2"]
    brs = D.units.loc["baserunning_rv:sprint_speed"]
    wos = D.units.loc["hitting_woba:sprint_speed"]
    s_top_ch = D.CO("pitching_fip:stuff_plus", "top decile", "mean_forecast_change")
    s_top_im = D.CO("pitching_fip:stuff_plus", "top decile", "share_improved")
    s_bot_ch = D.CO("pitching_fip:stuff_plus", "bottom decile", "mean_forecast_change")
    s_bot_im = D.CO("pitching_fip:stuff_plus", "bottom decile", "share_improved")
    k_top_ch = D.CO("pitching_fip:k_pct", "top decile", "mean_forecast_change")
    k_top_im = D.CO("pitching_fip:k_pct", "top decile", "share_improved")
    k_bot_im = D.CO("pitching_fip:k_pct", "bottom decile", "share_improved")
    x_over_ch = D.CO("hitting_woba:xwoba_w2", "xwOBA-wOBA gap bottom decile (over-performers)", "mean_forecast_change")
    x_over_im = D.CO("hitting_woba:xwoba_w2", "xwOBA-wOBA gap bottom decile (over-performers)", "share_improved")
    x_under_ch = D.CO("hitting_woba:xwoba_w2", "xwOBA-wOBA gap top decile (under-performers)", "mean_forecast_change")
    x_under_im = D.CO("hitting_woba:xwoba_w2", "xwOBA-wOBA gap top decile (under-performers)", "share_improved")
    b_top_ch = D.CO("baserunning_rv:sprint_speed", "top decile", "mean_forecast_change")
    b_bot_ch = D.CO("baserunning_rv:sprint_speed", "bottom decile", "mean_forecast_change")
    b_top_im = D.CO("baserunning_rv:sprint_speed", "top decile", "share_improved")
    b_bot_im = D.CO("baserunning_rv:sprint_speed", "bottom decile", "share_improved")
    zh, zp = D.ZERO[H], D.ZERO[Pi]
    era_fip = D.F(Pi, "ERA", TF, "fip")
    whip_fip = D.F(Pi, "WHIP", TF, "fip")
    hr_woba = D.F(H, "HR", TF, "woba")
    sb_sp = D.F(H, "SB", DM, "sprint_speed")
    hr_bar = D.F(H, "HR", DM, "barrel_pct")
    ab_hwar = D.F(H, "AB", TF, "hwar")
    rho_h_b, rho_h_a = D.RV(H, 156, "spearman_base"), D.RV(H, 156, "spearman_aug")
    rho_p_b, rho_p_a = D.RV(Pi, 108, "spearman_base"), D.RV(Pi, 108, "spearman_aug")
    era_sel = D.erasets.era_selected.str.split(",").apply(len)
    e26 = D.fr[D.fr["sample"].str.startswith("2026")]
    n26_gain = int((e26.ci_high_pct < 0).sum())
    E = "sloan2027_fantasy/fantasy/results_by_target_category.csv"

    b.figure("fig2_classification_map.png",
             "What the 208 canonical evaluations concluded, by target. Blue is the only purely statistical admission. Orange and green are both Diagnostic: orange metrics "
             "were predictive alone but redundant with a kept family member; green ones showed no material lift. The green/yellow split (Diagnostic vs Exclude) is a human "
             "process flag, and pink (Context) is assigned from a human-specified role. Counts are target-specific verdicts, not 208 different statistics.")
    # ---------------- 6.2 nested selection
    b.h2("6.2 Admitted metrics improve strong baselines for five of six targets")
    b.para(
        "Re-running the selection inside each training window, the admitted set lowered out-of-time RMSE against the history baseline, pooled over 2021–2025, for:")
    b.bullets([
        f"wOBA: {D.T2('hitting_woba', LIFT, sec='6.2')};",
        f"FIP: {D.T2('pitching_fip', LIFT, sec='6.2')};",
        f"baserunning: {D.T2('baserunning_rv', LIFT, sec='6.2')};",
        f"fielding: {D.T2('defense_rv', LIFT, sec='6.2')};",
        f"pitcher WAR: {D.T2('pitcher_war', LIFT, sec='6.2')}.",
    ])
    b.para(f"For hitter WAR it did not ({D.T2('overall_war', LIFT, sec='6.2')}; Figure 3A). The selections were stable across windows:")
    b.bullets([
        "for wOBA, the three-year wOBA history, two-year xwOBA and exit velocity were chosen in all six windows (2021–2026);",
        "for baserunning, the three-year history, sprint speed, stolen-base attempt rate and second-to-home advancement rate were chosen in all six;",
        f"for FIP, the window sets held {ev(m(f'{min(fip_sizes)}–{max(fip_sizes)}'), S['meta'], '6.2')} metrics, with Stuff+ entering from the "
        f"{ev(str(stuff_from), S['meta'], '6.2')} window onward;",
        f"for hitter WAR, exit velocity was chosen in only {ev(f'{ev_war} of 6', S['meta'], '6.2')} windows.",
    ])
    b.para(
        f"Choosing metrics with knowledge of the evaluation seasons had flattered accuracy by at most {ev(f'{D.FIXADM_MAX:.2f}%', S['nest'], '6.2')} of RMSE, judged by the "
        "original look-ahead set against the nested set. The look-ahead problem was real but small.")
    b.figure("fig3_model_comparisons.png",
             "Six-target model comparisons on identical players. Filled markers: outer seasons 2021–2025 with nested selection. Open markers: the 2026 frozen-in-workflow check "
             "(retrospective cohort). Panel A compares the selected model with the history baseline; panels B and C compare broad all-metric models with the selected model, "
             "so negative values favor the broad model. Intervals are 95% paired player-cluster bootstrap intervals.")
    # ---------------- 6.3 broad models
    b.h2("6.3 Selective versus broad models depends on the comparison and the season")
    b.para(
        f"Against an all-metric ridge model with a fixed penalty, the selected models were more accurate for wOBA ({D.T2('hitting_woba', KSR, sec='6.3')}, kitchen-sink minus "
        f"selected) and FIP ({D.T2('pitching_fip', KSR, sec='6.3')}). The original claim survives only in that narrow form:")
    b.bullets([
        f"a tuned elastic net tied the selected model for wOBA ({D.T2('hitting_woba', KEN, sec='6.3')}) and FIP ({D.T2('pitching_fip', KEN, sec='6.3')});",
        f"broad models were better for hitter WAR ({D.T2('overall_war', KSR, sec='6.3')}) and pitcher WAR ({D.T2('pitcher_war', KSR, sec='6.3')});",
        f"in 2026 the all-metric ridge model beat the selected model for FIP ({D.T2('pitching_fip', K26, sec='6.3')});",
        f"in 2026 the elastic net beat it for wOBA ({D.T2('hitting_woba', E26, sec='6.3')}) and FIP ({D.T2('pitching_fip', E26, sec='6.3')}).",
    ])
    b.para(
        "Figure 4 suggests why. The ridge kitchen-sink model's disadvantage for wOBA and FIP was largest in 2021, when the training window was shortest. It shrank as seasons "
        "accumulated and had reversed by 2025. One reading is that selection mainly protects a lightly regularized broad model from estimation noise when data are scarce. That "
        "protection matters less as the training window grows, and a tuned elastic net already provides it. Five outer seasons cannot separate this explanation from a change in "
        "the game, so the paper reports the pattern without claiming a cause. The practical lesson is that \"thinner beats broader\" is not a law; it is a result specific to "
        "the comparison and the era.")
    # ---------------- 6.4 flagships
    b.h2("6.4 The headline metrics, one at a time")
    rows = []
    for h in D.t3.index:
        rows.append([h, D.t3.loc[h, "Contrast"], m(f"{D.t3.loc[h, 'Published ΔRMSE (mean of 7 folds)']:+.5f}"),
                     ev(m(D.t3.loc[h, "2019–25 pooled, % [cluster CI]"]), S["t3"], "Table 5"), ev(m(D.t3.loc[h, "Nested 2021–25, %"]), S["t3"], "Table 5"),
                     ev(m(D.t3.loc[h, "2026 holdout, %"]), S["t3"], "Table 5")])
    t5 = pd.DataFrame(rows, columns=["", "Contrast (baseline + one metric)", "Original ΔRMSE (7-fold mean)", "2019–25 pooled, %", "Outer 2021–25, %", "2026, %"])
    b.table(t5, "Headline contrasts from the accepted abstract under stronger tests: ΔRMSE as % of the baseline RMSE, with 95% player-cluster bootstrap intervals; negative favors "
            "adding the metric. \"Outer 2021–25\" adds the fixed metric to the history baseline in each outer season; the metric is not re-selected.",
            widths=[0.3, 1.85, 1.0, 1.15, 1.15, 1.1], font=15)
    b.bullets([
        f"**xwOBA (two-year)** improved next-season wOBA in every evidence source, although its 2026 interval included zero ({D.T3('H1', '2026 holdout, %', sec='6.4')}).",
        f"**Strikeout rate** improved FIP, including in 2026 ({D.T3('H6', '2026 holdout, %', sec='6.4')}).",
        f"**Sprint speed** improved baserunning in every source, the 2026 interval again touching zero ({D.T3('H5', '2026 holdout, %', sec='6.4')}). It was null for wOBA "
        f"throughout ({D.T3('H7', '2026 holdout, %', sec='6.4')}).",
        f"**Stuff+** helped FIP only slightly ({D.T3('H4', '2019–25 pooled, % [cluster CI]', sec='6.4')}; Benjamini–Hochberg q = {num(stq, '.3f', S['t3'], '6.4')} across "
        "the 208 tests).",
        f"**Exit velocity → hitter WAR** did not hold up: outer 2021–25 {D.T3('H3', 'Nested 2021–25, %', sec='6.4')}; 2026 {D.T3('H3', '2026 holdout, %', sec='6.4')}.",
    ])
    # ---------------- 6.5 gates, placebos
    b.h2("6.5 Which gates change the answer")
    b.para(
        "One-at-a-time ablations reran the nested selection with a single gate removed or a threshold changed. Only two kinds of change altered out-of-time error with an "
        "interval excluding zero:")
    b.bullets([
        "removing the family-redundancy step made FIP forecasts worse;",
        "moving the materiality threshold away from 0.5% changed error: 2% worsened baserunning, fielding, pitcher WAR and FIP, and zero changed fielding and FIP.",
    ])
    b.para("The other ablations did not change error:")
    b.bullets([
        "removing the coverage gate changed which metrics were selected for fielding, but not the error;",
        "removing the materiality gate entirely changed selections for five targets, also without a detectable change in error;",
        "the consistency, coefficient-sign and subgroup gates changed nothing in these data, and neither did the admission ridge penalty (α = 0.1 or 10).",
    ])
    b.para(
        "The defensible summary is narrower than \"only two gates work\". In these ablations only the materiality threshold and the family step materially changed forecast "
        "error, while other gates could still change labels and selections. Placebo metrics of pure noise, passed through the same gates, were never admitted "
        f"({ev(f'{D.N_PLAC_ADMIT} of {D.N_PLAC:,}', S['plac'], '6.5')}).")
    b.figure("fig4_year_by_year.png",
             "Season-by-season view of the two central comparisons for each target. Blue: selected minus history baseline (below zero means selection helped). Orange: "
             "all-metric ridge minus selected (above zero means the selected model was better). The 2026 points carry 95% intervals. For hitter WAR in 2021–2023 no metric was "
             "selected, so the selected and baseline models coincide. The orange series for wOBA and FIP falls toward and below zero as training seasons accumulate.")

    # ================================================================== 7 Player stories
    b.h1("7. Results II: player stories in baseball units")
    b.para(
        f"Average RMSE changes hide what happens to individual forecasts. Adding Stuff+ to the FIP baseline changed RMSE by {pct(st.pct, nd=2, src=S['units'], sec='7')} "
        f"in the outer seasons. Yet the typical forecast moved by only {num(st.median_abs_forecast_change, '.2f', S['units'], '7')} FIP units (90th percentile "
        f"{num(st.p90_abs_forecast_change, '.2f', S['units'], '7')}), and {ev(f'{100 * st.share_improved_abs_error:.0f}%', S['units'], '7')} of forecasts became more accurate. "
        "These are changes in FIP units: a projected FIP moving by 0.14, not 0.14 earned runs saved or 0.14 points of fantasy ERA.")
    b.para(
        "**Where Stuff+ helps and where it hurts (Figure 5).** For pitchers in the top Stuff+ decile, adding the metric lowered the FIP forecast by "
        f"{num(abs(s_top_ch), '.2f', S['coh'], '7')} on average, and {ev(f'{100 * s_top_im:.0f}%', S['coh'], '7')} of those forecasts improved. For the bottom decile it raised "
        f"the forecast by {num(s_bot_ch, '.2f', S['coh'], '7')}, and only {ev(f'{100 * s_bot_im:.0f}%', S['coh'], '7')} improved. Stuff+ is good at confirming that elite stuff "
        "will keep missing bats and poor at condemning pitchers whose stuff grades badly.")
    b.para(
        f"Tyler Rogers shows the failure in its purest form. A submarine reliever with an arm angle near {ev(m(f'{rog.arm_angle.mean():.0f}°'), S['cases'], '7')}, far outside the "
        f"range of conventional deliveries, he graded at Stuff+ {ev(m(f'{rog.feature_value.min():.0f}–{rog.feature_value.max():.0f}'), S['cases'], '7')}. In each of five "
        f"outer seasons, adding Stuff+ raised his FIP forecast by {ev(m(f'{rog.change.min():.2f}–{rog.change.max():.2f}'), S['cases'], '7')}. His observed FIPs were "
        f"{ev(m(f'{rog.y.min():.2f}–{rog.y.max():.2f}'), S['cases'], '7')}, below even the forecasts without Stuff+, so all five adjustments made the forecast worse. He accounts "
        f"for {ev(f'{D.LARGEST6_ROGERS} of the 6', S['fc'], '7')} largest Stuff+ adjustments in the whole sample, and {ev(f'{D.LARGEST6_WORSE} of those 6', S['fc'], '7')} worsened "
        "the forecast. A pitch-quality model scores velocity, movement and spin against how pitches from typical release points perform. It has no term for what an extreme "
        "release does to a hitter's view, and Rogers' results show that this matters.")
    b.para(
        f"Zack Wheeler is the success case. With Stuff+ {ev(m(f'{whe.feature_value.min():.0f}–{whe.feature_value.max():.0f}'), S['cases'], '7')}, the metric lowered his FIP "
        f"forecast by {ev(m(f'{abs(whe.change).min():.2f}–{abs(whe.change).max():.2f}'), S['cases'], '7')} in each of five seasons. Every one of those forecasts improved, "
        "because his results kept beating the history-only forecast. For most pitchers, though, two-year FIP already contains much of what Stuff+ knows. That is why the average gain is "
        "small even though the metric is genuinely informative at the extremes.")
    b.figure("fig5_player_stories_stuff.png",
             "Stuff+ and next-season FIP forecasts. A–B: forecasts without (open) and with (filled) Stuff+ against observed FIP for two named pitchers, outer seasons 2021–2025. "
             "These cases were chosen to illustrate extremes and are not typical. C–D: all 1,328 outcome-observed pitcher-seasons by Stuff+ decile within season, showing the mean "
             "change in the FIP forecast and the share of forecasts that became more accurate. FIP units, not runs.")
    b.para(
        "**Strikeout rate.** K% moves FIP forecasts more than Stuff+ does (median change "
        f"{num(kp.median_abs_forecast_change, '.2f', S['units'], '7')} FIP; 90th percentile {num(kp.p90_abs_forecast_change, '.2f', S['units'], '7')}). Its asymmetry runs "
        f"the same way: in the top decile the forecast fell by {num(abs(k_top_ch), '.2f', S['coh'], '7')} and {ev(f'{100 * k_top_im:.0f}%', S['coh'], '7')} of forecasts "
        f"improved, against {ev(f'{100 * k_bot_im:.0f}%', S['coh'], '7')} in the bottom decile.")
    b.para(
        f"**xwOBA.** Two-year xwOBA moved a typical wOBA forecast by {num(1000 * xw.median_abs_forecast_change, '.1f', S['units'], '7')} points (90th percentile "
        f"{num(1000 * xw.p90_abs_forecast_change, '.1f', S['units'], '7')}). Its value is concentrated among hitters whose results ran ahead of their contact quality. For "
        f"the decile with the largest wOBA-over-xwOBA gap, the forecast fell by {num(1000 * abs(x_over_ch), '.0f', S['coh'], '7')} points on average, and "
        f"{ev(f'{100 * x_over_im:.0f}%', S['coh'], '7')} of forecasts improved. For the opposite decile, apparent bad luck, it rose by "
        f"{num(1000 * x_under_ch, '.0f', S['coh'], '7')} points, and only {ev(f'{100 * x_under_im:.0f}%', S['coh'], '7')} improved. \"Buy low on xwOBA under-performers\" "
        "is weaker in these data than \"sell high on over-performers\".")
    b.para(
        f"**Sprint speed.** For baserunning, the fastest decile's forecasts rose by {num(b_top_ch, '.2f', S['coh'], '7')} runs per 100 times on base and the slowest decile's "
        f"fell by {num(abs(b_bot_ch), '.2f', S['coh'], '7')}; {ev(f'{100 * b_top_im:.0f}%', S['coh'], '7')} and {ev(f'{100 * b_bot_im:.0f}%', S['coh'], '7')} of those "
        f"forecasts improved. For wOBA, the median change was {num(1000 * wos.median_abs_forecast_change, '.1f', S['units'], '7')} wOBA points: in practice, nothing.")

    # ================================================================== 8 Fantasy bridge
    b.h1("8. Results III: from performance forecasts to fantasy categories")
    b.h2("8.1 Design")
    b.para(
        "The six targets are not fantasy categories, so their relevance to fantasy play has to be tested, not assumed. The test asks whether out-of-time forecasts of the "
        "targets add information about next-season fantasy outcomes beyond a **direct fantasy baseline**. The protocol was committed publicly before any fantasy-category "
        "model was fit; one dated amendment added the ERA check in Section 9 before it was run. The baseline is a tuned ridge model of each category on things a careful manager "
        "can compute from standard statistics:")
    b.bullets([
        "the previous season's and two-year per-PA rates of R, HR, RBI and SB, AVG, BB% and K%, plus prior PA and games, for hitters;",
        "prior innings, starts, wins, saves, holds, strikeouts per inning, ERA and WHIP, for pitchers;",
        "age and age squared, for both.",
    ])
    b.para(
        "Future playing time is never an input. The target forecasts are the nested ADM forecasts (and, for comparison, the history-only B0 forecasts), refit chronologically so "
        "that every training row also carries a genuinely out-of-sample forecast. For the test seasons they reproduce the Section 6 predictions, including the frozen 2026 file, "
        f"to within {ev('2 × 10⁻¹⁵', S['up'], '8.1')}.")
    b.para(
        "Outcomes are 5×5 categories: R, HR, RBI, SB and AVG for hitters; W, SV, K, ERA and WHIP for pitchers. Counting categories are evaluated on the full forecast-date pool, "
        f"where between {ev(f'{100 * zh['min']:.0f}%', S['cb'], '8.1')} and {ev(f'{100 * zh['max']:.0f}%', S['cb'], '8.1')} of pool hitters and "
        f"{ev(f'{100 * zp['min']:.0f}%', S['cb'], '8.1')}–{ev(f'{100 * zp['max']:.0f}%', S['cb'], '8.1')} of pool pitchers produced nothing the next season. Ratio categories "
        "are computed from components (AVG = H/AB; ERA = 9·ER/IP; WHIP = (BB+H)/IP, with innings from recorded outs), weighted by volume, and evaluated among players with at "
        "least 100 AB or 20 IP, so they are conditional on playing. A 5×5 **value** score sums category z-scores, treating AVG, ERA and WHIP as volume-weighted contributions, "
        "with means and SDs taken from earlier seasons only:")
    b.equation("value")
    b.para(
        "Eight linkages were pre-specified as primary and Holm-adjusted: wOBA → AVG, wOBA → HR, FIP → ERA, FIP → WHIP, baserunning → SB, and fielding, hitter WAR and pitcher "
        "WAR → value. The full target × category matrix, the admitted-versus-history comparisons and a small set of raw-metric tests are secondary, with Benjamini–Hochberg "
        "adjustment within each family. Outcome seasons 2021–2025 are primary; 2026 is exploratory.")
    b.h2("8.2 Association is not added information")
    b.para(
        f"The target forecasts correlate with fantasy outcomes as expected (Spearman ρ, 2021–2025): wOBA forecast with HR {D.L1('woba', 'HR', '8.2')}, baserunning forecast with "
        f"SB {D.L1('br', 'SB', '8.2')}, FIP forecast with ERA {D.L1('fip', 'ERA', '8.2')} and with WHIP {D.L1('fip', 'WHIP', '8.2')}, and fielding forecast with 5×5 value "
        f"{D.L1('fld', 'VAL_H', '8.2')}. These correlations are the kind of evidence fantasy discussions often rely on. They establish association only. A manager who "
        "already uses last season's statistics needs to know whether the forecast adds anything to them.")
    b.h2("8.3 Which target forecasts add fantasy information")
    pr = D.fr[D.fr["sample"].str.startswith("2021") & D.fr.family.eq("primary")]
    lab = {"woba": "wOBA", "fip": "FIP", "br": "Baserunning", "fld": "Fielding", "hwar": "Hitter bWAR", "pwar": "Pitcher bWAR"}
    olab = {"VAL_H": "5×5 value (hitters)", "VAL_P": "5×5 value (pitchers)"}
    unitfmt = {"HR": ".2f", "SB": ".2f", "AVG": ".4f", "ERA": ".3f", "WHIP": ".4f", "VAL_H": ".3f", "VAL_P": ".3f"}
    t6 = pd.DataFrame([[f"{lab[r.target]} forecast → {olab.get(r.outcome, r.outcome)}",
                        ev(m(f"{r.rmse_base:{unitfmt[r.outcome]}} → {r.rmse_aug:{unitfmt[r.outcome]}}"), E, "Table 6"),
                        pct(r.delta_pct, r.ci_low_pct, r.ci_high_pct, 2, E, "Table 6"), ev(m(f"{r.season_block_ci_low_pct:+.2f} to {r.season_block_ci_high_pct:+.2f}"), E, "Table 6"),
                        ev(f"{int(r.years_improved)}/5", E, "Table 6"), ev(f"{r.p_adjusted:.3f}", E, "Table 6"), r.verdict]
                       for _, r in pr.iterrows()],
                      columns=["Pre-specified linkage", "RMSE, baseline → with forecast (category units)", "ΔRMSE % [player-cluster 95% CI]", "Season-block 95% interval",
                               "Seasons improved", "Holm p", "Reading"])
    b.table(t6, "Primary fantasy linkages, outcome seasons 2021–2025 pooled, identical players. RMSE in the category's own units (home runs, stolen bases, batting average, "
            "ERA, WHIP, z-score value). The season-block interval resamples whole seasons and is coarse with five seasons.",
            widths=[1.55, 1.05, 1.05, 0.85, 0.6, 0.5, 0.9], font=14)
    b.para(
        f"Only the FIP forecast passed (Table 6; Figure 6). Adding it to the category-history model lowered ERA forecast error from {num(era_fip.rmse_base, '.3f', E, '8.3')} to "
        f"{num(era_fip.rmse_aug, '.3f', E, '8.3')} earned runs per nine innings ({D.Fp(Pi, 'ERA', TF, 'fip', sec='8.3')}), and WHIP error from "
        f"{num(whip_fip.rmse_base, '.4f', E, '8.3')} to {num(whip_fip.rmse_aug, '.4f', E, '8.3')} ({D.Fp(Pi, 'WHIP', TF, 'fip', sec='8.3')}). Four of five seasons improved "
        "in each case. The classic fantasy advice to judge pitchers by their fielding-independent skills therefore has measurable support beyond simply reading last season's "
        "ERA and WHIP. The gain is about 1% of forecast error, real but modest.")
    b.para("The other primary linkages showed no gain that survived adjustment:")
    b.bullets([
        f"the wOBA forecast improved HR forecasts in all five seasons, but the pooled interval included zero ({D.Fp(H, 'HR', TF, 'woba', nd=2, sec='8.3')});",
        f"wOBA → AVG: {D.Fp(H, 'AVG', TF, 'woba', sec='8.3')};",
        f"the baserunning forecast added nothing to stolen-base forecasts ({D.Fp(H, 'SB', TF, 'br', sec='8.3')});",
        f"the fielding forecast added nothing to hitter value ({D.Fp(H, 'VAL_H', TF, 'fld', sec='8.3')}), as a boundary case should;",
        f"hitter WAR → value: {D.Fp(H, 'VAL_H', TF, 'hwar', nd=2, sec='8.3')}, an interval that excludes zero but does not survive Holm adjustment;",
        f"pitcher WAR → value: {D.Fp(Pi, 'VAL_P', TF, 'pwar', sec='8.3')}.",
    ])
    b.figure("fig6_fantasy_linkage.png",
             "Which target forecasts add information about which fantasy categories. Each cell is the change in out-of-time forecast error for a fantasy category when one target "
             "forecast is added to the direct category-history baseline (outcome seasons 2021–2025 pooled; identical players). Marker: verdict after multiplicity adjustment. "
             "Bold outline: the eight pre-specified primary linkages.")
    b.h2("8.4 What does carry information, and through which channel")
    b.para(
        "Three secondary findings sharpen the picture. They are exploratory and BH-adjusted within their families.")
    b.bullets([
        f"**Raw metrics beat the intermediate target for some categories.** Sprint speed added directly to the category model improved stolen-base forecasts "
        f"({D.Fp(H, 'SB', DM, 'sprint_speed', sec='8.4')}, {int(sb_sp.years_improved)} of 5 seasons), even though the baserunning *forecast* did not. The baserunning target "
        "measures run value per time on base, including advancement and outs on the bases, which is a different quantity from stolen-base volume. Barrel% improved HR "
        f"forecasts ({D.Fp(H, 'HR', DM, 'barrel_pct', sec='8.4')}), and so did two-year xwOBA ({D.Fp(H, 'HR', DM, 'xwoba_w2', sec='8.4')}). Stuff+, K% and K-BB% added nothing "
        "to K, ERA or WHIP forecasts beyond the category history.",
        f"**The admitted metrics travel through the target forecast.** Replacing a history-only target forecast with the admitted one improved several category forecasts, "
        f"for example ERA ({D.Fp(Pi, 'ERA', AV, 'fip', sec='8.4')}), WHIP ({D.Fp(Pi, 'WHIP', AV, 'fip', sec='8.4')}) and runs ({D.Fp(H, 'R', AV, 'woba', sec='8.4')}). The public "
        f"metrics admitted for FIP and wOBA therefore carry some fantasy information beyond history. One comparison went the other way (hitter WAR, AVG: "
        f"{D.Fp(H, 'AVG', AV, 'hwar', sec='8.4')}).",
        f"**WAR forecasts mostly carry playing time.** The hitter WAR forecast improved at-bat forecasts ({D.Fp(H, 'AB', TF, 'hwar', sec='8.4')}) more than any rate category: "
        f"better players keep their jobs. All target forecasts together improved AVG ({D.Fp(H, 'AVG', JT, 'woba+br+hwar', sec='8.4')}) and pitcher 5×5 value "
        f"({D.Fp(Pi, 'VAL_P', JT, 'fip+pwar', sec='8.4')}).",
    ])
    b.para(
        f"In 2026 none of the eight primary linkages had an interval excluding zero (for example FIP → ERA {D.Fp(Pi, 'ERA', TF, 'fip', '2026', nd=2, sec='8.4')} "
        f"and wOBA → HR {D.Fp(H, 'HR', TF, 'woba', '2026', nd=2, sec='8.4')}). Among secondary comparisons, {ev(str(n26_gain), S['fr'], '8.4')} favored the forecasts with "
        f"intervals excluding zero, for example FIP → pitcher 5×5 value ({D.Fp(Pi, 'VAL_P', TF, 'fip', '2026', sec='8.4')}). The one harmful comparison from 2021–2025 "
        f"(hitter WAR, AVG) was harmful again ({D.Fp(H, 'AVG', AV, 'hwar', '2026', sec='8.4')}). One season of roughly 300–400 players has little power, and 2026 had "
        "already been inspected for the six targets, so these rows are exploratory.")
    b.h2("8.5 Does it change a draft? An illustrative backtest")
    b.para(
        "Better category forecasts do not automatically mean better picks. In each season the forecast-date pool was ranked by predicted 5×5 value and the top k players were "
        "taken (k = 156 hitters and 108 pitchers corresponds to a 12-team league). The realized value of the players chosen by the baseline models was then compared with that "
        "of the players chosen by models that also used the target forecasts. Adding the target forecasts improved rank agreement with realized value for hitters "
        f"(Spearman ρ {num(rho_h_b, '.3f', S['rv'], '8.5')} → {num(rho_h_a, '.3f', S['rv'], '8.5')}) and pitchers ({num(rho_p_b, '.3f', S['rv'], '8.5')} → "
        f"{num(rho_p_a, '.3f', S['rv'], '8.5')}), with intervals for the differences excluding zero. The players actually picked were not detectably better at any league size: "
        f"12-team hitters {pct(D.RV(H, 156, 'delta_mean_realized_value'), D.RV(H, 156, 'ci_low'), D.RV(H, 156, 'ci_high'), 2, S['rv'], '8.5').replace('%', '')} z-units per pick, "
        f"pitchers {pct(D.RV(Pi, 108, 'delta_mean_realized_value'), D.RV(Pi, 108, 'ci_low'), D.RV(Pi, 108, 'ci_high'), 2, S['rv'], '8.5').replace('%', '')} (Figure 7). The forecasts "
        "mostly reorder the middle of the pool. At the top of a draft, playing time and category history dominate. The backtest ignores average draft position, positions, snake "
        "order and in-season management, so it is a what-if illustration, not evidence about winning leagues.")
    b.figure("fig7_draft_backtest.png",
             "Illustrative draft backtest. A–B: rank agreement between predicted and realized 5×5 value for the category-history models and for models that also use the target "
             "forecasts, by season (2026 exploratory). C: difference in the mean realized value of the top-k players picked by each ranking, pooled 2021–2025, with 95% intervals "
             "from resampling players. No positions, average draft position or in-season moves.")

    # ================================================================== 9 ERA
    b.h1("9. A new target: does the procedure generalize to ERA?")
    b.para(
        "Earlier alternative-target analyses reused metric sets selected for the original targets. That is transfer, not a test of whether the procedure can choose metrics for "
        "a new target. As a direct test, specified in a dated protocol amendment before it was run, the full nested admission was applied to next-season **ERA**, a fantasy "
        "category, using the FIP study's pitchers, an ERA-history baseline and the unchanged candidate catalog. The procedure selected "
        f"{ev(m(f'{era_sel.min()}–{era_sel.max()}'), S['erasets'], '9')} metrics per window. These were strikeout rate, K-BB%, zone-contact rate, called-strike-plus-whiff or "
        "whiff rate, fastball velocity, spin, platoon K-BB% and, from 2022, Stuff+: a sensible skill set. Results on 2021–2025, on identical rows:")
    b.bullets([
        f"ERA-specific selection beat the ERA-history baseline ({D.ERA('ERA-ADM vs B0', sec='9')});",
        f"so did simply reusing the FIP study's selections ({D.ERA('TRANSFER vs B0', sec='9')});",
        f"the ERA-specific set was no better than the reused set ({D.ERA('ERA-ADM vs TRANSFER', sec='9')});",
        f"it beat an all-metric ridge model ({D.ERA('KS ridge vs ERA-ADM', sec='9')}) and tied a tuned elastic net ({D.ERA('KS elastic net vs ERA-ADM', sec='9')}).",
    ])
    b.para(
        "The procedure therefore produces useful, interpretable selections for a new target. For closely related targets such as ERA and FIP, however, target-specific "
        "re-selection added nothing beyond reusing a related target's choices. That is a narrower and more honest portability claim than \"the framework handles any target\".")

    # ================================================================== 10 Discussion
    b.h1("10. Discussion")
    b.h2("10.1 How a public reader should use these results")
    b.para(
        "A metric's job depends on the forecast. For a fantasy manager, that implies four working rules:")
    b.bullets([
        "**Prefer category-matched evidence.** Sprint speed for steals, and Barrel% or xwOBA for home runs, carried information beyond category history. The baserunning run-value forecast did not carry it for steals.",
        "**For pitchers, fielding-independent skill is worth a modest premium.** The FIP forecast improved ERA and WHIP forecasts by about 1%.",
        "**Treat WAR as a measure of value, not fantasy value.** Its forecast mostly signals playing time.",
        "**Spend the most effort on playing time.** It, not marginal skill metrics, dominated the illustrative draft decisions.",
    ])
    b.para("None of these results promise more wins in any particular league.")
    b.h2("10.2 Where fantasy conventional wisdom agrees and disagrees with the evidence")
    from section3 import discussion_audit  # noqa: E402
    discussion_audit(b, D)
    b.h2("10.3 Target, model and era conditionality")
    b.para(
        "Every result here is conditional on the target, the baseline, the population, the estimator and the seasons. The same metric changes role across targets: sprint "
        "speed is admitted for baserunning and labelled Diagnostic for wOBA. The advantage of selection over an all-metric ridge model faded as training seasons accumulated, "
        "a tuned elastic net matched selection, and broad models won for aggregate targets. A defensible reading is that selection helps most where signal is concentrated in "
        "a few metrics and data are scarce, and helps least for aggregate targets that draw on many weak signals. The paper did not re-run selection inside the non-linear "
        "models, so it makes no claim that the admitted sets are the right sets for LightGBM or random forests.")
    b.h2("10.4 What this is not: front-office decision support")
    b.para(
        "Single-number public metrics such as wOBA, Barrel% or WAR are summaries designed largely for fans and analysts. Professional organizations work with pitch-level "
        "tracking, biomechanics, medical and scouting information, and models built on far richer inputs. Nothing in this paper suggests that teams need these labels or that "
        "the admission rule, applied to public data, would change their decisions. The application is public analysis and fantasy play. For front-office use the evidence "
        "here is insufficient by design.")
    b.h2("10.5 Public data compress the game")
    b.para(
        "Many candidate metrics are compressions:"
        f" Barrel% reduces each batted ball's exit velocity and launch angle to a yes/no threshold {c('mlb_barrel')};"
        " xwOBA summarizes contact quality and ignores spray direction for most batted balls;"
        " WAR stacks positional, replacement-level and defensive models;"
        " and bWAR and fWAR differ by construction. Upstream cleaning and model updates by data providers are not fully visible to users. A metric that fails admission here may "
        "have failed because the public summary threw away the information, not because the underlying skill is unpredictable. The labels are about the public statistics as "
        "published.")
    b.h2("10.6 Alternative explanations")
    b.bullets([
        "**Weak baselines.** The history baselines are strong (two- and three-year weighted rates, age, playing time, park), and broad regularized models were scored on the same rows.",
        "**Selection on the evaluation years.** Nested selection removes it; its effect was at most about half a percent of RMSE.",
        "**Multiplicity.** Primary families are Holm-adjusted and secondary families BH-adjusted. All of it is exploratory relative to earlier looks at these seasons.",
        "**Era effects.** The 2020 season was 60 games; counts are prorated in the fantasy analysis. The 2023 rule changes (pitch timer, limits on pickoffs, larger bases) changed the stolen-base environment. With five outer seasons, the paper reports season-by-season results instead of modeling regimes.",
        "**Survivorship.** Outcome-observed populations exclude players who lost their jobs. The fantasy pools keep them, but rookies remain outside the study.",
    ])
    b.para(
        "One statistic can do different jobs. Asking what each job is, before letting a statistic change a forecast, is a discipline that public analysts can apply with public "
        "data. Its value lies as much in the metrics it declines to promote, and in the failures it shows openly, as in the ones it admits.")

    # ================================================================== 11 Limitations
    b.h1("11. Limitations and future work")
    b.bullets([
        "**No prospective test yet.** The 2026 check was frozen within the workflow but evaluated after the season. A genuinely prospective test would freeze 2027 forecasts and the protocol before Opening Day 2027.",
        "**Exploratory fantasy evidence.** The fantasy bridge was pre-specified, but the seasons were not new. Its decision backtest is illustrative: no average draft position, positions, roster rules or in-season moves.",
        "**Narrow populations.** Rookies and sub-threshold players are excluded. Ratio categories are conditional on playing.",
        "**Human-specified labels.** The role and process flags are human choices. Different, defensible choices would change some Diagnostic/Exclude/Context labels, though not the statistical admissions.",
        "**Particular metric versions.** Stuff+ is this study's own model, and WAR is Baseball-Reference's. Results may differ for FanGraphs' versions.",
        "**Untested model families.** Admission was not re-run inside non-linear models, and no archived third-party projections (Steamer, ZiPS, ATC, THE BAT X) served as baselines, because they are not lawfully available to the study.",
        "**Future work:**"
        " richer public inputs (pitch-level and bat-tracking data);"
        " playing-time and injury models;"
        " position- and average-draft-position-aware valuation;"
        " a frozen, prospective 2027 evaluation.",
    ])
    # ================================================================== Appendices
    b.unnumbered("Appendix A. The accepted abstract and what changed", page_break=True)
    b.para("The abstract accepted for the full-paper stage is preserved verbatim below as the historical record. Table 7 lists each of its claims next to the evidence in "
           "this paper.", size=20)
    abstract = (Path(__file__).resolve().parents[2] / "app/content/study_notes.md").read_text().split("## What changed")[0]
    paras = [p.strip() for p in abstract.split("\n\n") if p.strip() and not p.startswith("#") and not p.startswith("**Title")]
    for p in paras:
        if p.startswith("**") and p.endswith("**"):
            b.para(p, size=19, keep_next=True, space_after=2)
        else:
            b.para(p, size=19)
    ta = pd.DataFrame([
        ["402 fields; 208 evaluations; 163 metrics", "Reproduced exactly (55/55 checks)", "Unchanged"],
        ["Two-year xwOBA → wOBA (−0.00093; 7/7 folds)", f"Pooled {D.T3('H1', '2019–25 pooled, % [cluster CI]', sec='A')}; outer 2021–25 {D.T3('H1', 'Nested 2021–25, %', sec='A')}; 2026 {D.T3('H1', '2026 holdout, %', sec='A')}", "Supported; 2026 directional"],
        ["Exit velocity improved wOBA and hitter WAR", f"wOBA outer {D.T3('H2', 'Nested 2021–25, %', sec='A')}; hitter WAR outer {D.T3('H3', 'Nested 2021–25, %', sec='A')}, 2026 {D.T3('H3', '2026 holdout, %', sec='A')}", "wOBA supported; hitter WAR not supported"],
        ["Stuff+ → FIP (−0.00730; 5/7)", f"Pooled {D.T3('H4', '2019–25 pooled, % [cluster CI]', sec='A')}; outer {D.T3('H4', 'Nested 2021–25, %', sec='A')}; 2026 {D.T3('H4', '2026 holdout, %', sec='A')}", "Weakened: small, consistent direction"],
        ["Sprint speed: stable, no wOBA value, baserunning −0.0599 (7/7)", f"Baserunning outer {D.T3('H5', 'Nested 2021–25, %', sec='A')}; wOBA 2026 {D.T3('H7', '2026 holdout, %', sec='A')}", "Supported"],
        ["Selective beat kitchen-sink for wOBA and FIP", f"Versus all-metric ridge: wOBA {D.T2('hitting_woba', KSR, sec='A')}, FIP {D.T2('pitching_fip', KSR, sec='A')} (positive favors selective); versus tuned elastic net: ties; 2026 FIP reversed {D.T2('pitching_fip', K26, sec='A')}", "Holds only narrowly"],
        ["Broader model better for hitter WAR", f"Outer {D.T2('overall_war', KSR, sec='A')}; also pitcher WAR {D.T2('pitcher_war', KSR, sec='A')}", "Supported; extends to pitcher WAR"],
    ], columns=["Accepted-abstract claim", "Evidence in this paper (ΔRMSE %, 95% CI)", "Status"])
    b.table(ta, "Original versus revised claims.", widths=[1.9, 3.3, 1.3], font=14)
    b.unnumbered("Appendix B. Gate definitions and reason codes")
    b.para(
        "Projection requires all of the following: ΔRMSE ≤ −0.5% of the baseline RMSE; at least 3 folds; at least 60% of folds improved or the 95% bootstrap upper bound below zero; "
        "survival of the family-redundancy step; fewer than 2 coefficient sign changes; coverage of at least 70% (90% when missingness is systematic); and no material harm in "
        "at least half of the large subgroups (n ≥ 150). Reason-code counts across the 208 canonical evaluations are: "
        + "; ".join(f"{k}: {ev(str(int(v)), S['reason'], 'B')}" for k, v in D.reason.items()) + ".", size=20)
    b.unnumbered("Appendix C. Reproducibility and data rights")
    if blind:
        repo_sentence = "Code, aggregate results, figure data, checksums and the web application are in public repositories whose links are given in the submission form " \
                        f"{c('repo')}. An earlier version of the study is available as a preprint {c('preprint')}."
    else:
        repo_sentence = f"Code, aggregate results, figure data, checksums and the web application are public {c('repo')}. An earlier version is available as a preprint {c('preprint')}."
    b.para(
        repo_sentence + " The canonical study (commit 17da742) and the November 2026 reanalysis were re-run on 2026-11-13: 71 automated tests passed and 55 of 55 reproduction "
        "checks matched. All 873 files of the immutable baseline were byte-identical to their recorded SHA-256 values. The fantasy-bridge protocol, version 1.0, and its one "
        "amendment were committed and pushed before the corresponding models were fit. Raw MLB Advanced Media and Baseball-Reference tables and player-season panels are not "
        "redistributed, because their terms restrict redistribution. The repositories contain scripts that rebuild them from the original sources, with checksums that verify "
        "a rebuild. The Baseball-Reference WAR files reflect that site's methodology at download time; Sports Reference revises historical fielding inputs from time to time "
        f"{c('bref_update2025')}. Proofs were rendered with LibreOffice using a Cambria-metric font; Microsoft Word was not available for the final layout check.", size=20)
    b.unnumbered("Appendix D. Full fantasy-linkage results")
    b.para(
        "The complete target × category matrix, covering all comparison types, both samples, per-season values, season-block intervals and multiplicity adjustments, is in "
        "`fantasy/results_by_target_category.csv`, `fantasy/by_year.csv` and `fantasy/paired_uncertainty.csv`. The same results can be browsed in the web application's "
        f"Fantasy Linkage Explorer. Of the {ev(str(int((D.fr['sample'].str.startswith('2021')).sum())), S['fr'], 'D')} pooled 2021–2025 comparisons, "
        f"{ev(str(int(((D.fr['sample'].str.startswith('2021')) & (D.fr.verdict == 'adds information')).sum())), S['fr'], 'D')} met the adds-information criterion, "
        f"{ev(str(int(((D.fr['sample'].str.startswith('2021')) & (D.fr.verdict == 'harmful')).sum())), S['fr'], 'D')} was harmful (hitter WAR, AVG), and the rest showed no detectable or "
        "no multiplicity-robust gain.", size=20)
    b.references(bibliography(blind))
    return b



def fetch_time() -> str:
    t = D.fetch["started"].replace("T", " ").replace("+00:00", " UTC")
    return f"2026 tables fetched {t[:16]} UTC; predictions committed earlier as f8023bf, SHA-256 af61b2b8…"


def main():
    for blind in (True, False):
        b = build(blind)
        out = PAPER / ("sloan_2027_fantasy_revised.docx" if blind else "sloan_2027_fantasy_revised_named.docx")
        b.save(out)
        claims = pd.DataFrame(CLAIMS)
        claims.insert(0, "claim_id", range(1, len(claims) + 1))
        claims.to_csv(PAPER / ("claims_to_evidence.csv" if blind else "claims_to_evidence_named.csv"), index=False)
        print(out.name, "figures", b.fig_n, "tables", b.tab_n, "equations", b.eq_n, "references", len(b.ref_order), "claims", len(claims))


if __name__ == "__main__":
    main()
