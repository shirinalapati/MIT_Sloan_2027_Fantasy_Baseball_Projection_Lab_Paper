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
    _ev = pd.DataFrame(D.evals)
    _g = _ev.groupby("metric").verdict.agg(["nunique", "size"])
    n_multi, n_change = int((_g["size"] > 1).sum()), int(((_g["size"] > 1) & (_g["nunique"] > 1)).sum())
    q05, nproj = D.mult["projection_rows_q_bh_all_lt_0.05"], D.mult["canonical_Projection_rows"]

    b.title_block(TITLE)
    # ================================================================== Abstract
    b.para(
        "**Abstract.** Fantasy baseball managers and public analysts can look up hundreds of statistics. A statistic that *describes* a player well is not automatically "
        "one that *improves next season's forecast* once a model already knows his recent record. This paper turns that distinction into a transparent admission rule and "
        "tests it on MLB player-seasons from 2015–2025, plus a 2026 check, for six next-season targets: wOBA, FIP, baserunning and fielding run-value rates, and "
        "Baseball-Reference WAR per 600 PA and per 200 IP. The original 208 metric–target evaluations reproduce. With the selection re-run inside each training window, "
        f"admitted inputs lowered out-of-time error against a two-year history baseline for five targets ({ev(m(f'{lo5:.1f}–{hi5:.1f}%'), S['t2'], 'abstract')} lower RMSE), "
        "but not for hitter WAR; for fielding the whole gain came from a third season of fielding history. The same metric can do different jobs: sprint speed improved "
        f"baserunning forecasts ({D.T3('H5', 'Nested 2021–25, %', 1, 'abstract')}) and added nothing to wOBA. Selected models beat an all-metric ridge model for wOBA and FIP, "
        "showed no detectable difference from a tuned elastic net, lost for both WAR targets, and lost for FIP in a retrospective 2026 check frozen before outcomes were "
        "downloaded. A pre-specified fantasy test found that adding the FIP forecast to a category-history model improved ERA and WHIP forecasts by about 1% "
        f"({D.Fp(Pi, 'ERA', TF, 'fip', sec='abstract')} and {D.Fp(Pi, 'WHIP', TF, 'fip', sec='abstract')}), although both reversed in 2023 and are not clear of zero at "
        "the season level; the other primary links showed no multiplicity-robust gain. Exploratory tests suggest raw sprint speed helps stolen-base forecasts and Barrel% "
        "helps home-run forecasts. The contribution is a checkable way to ask which public metrics deserve to change a forecast, failures included.", size=21)

    # ================================================================== 1 Introduction
    b.h1("1. Introduction: a fantasy manager's question")
    b.para(
        "Before a draft, a fantasy manager can sort hitters by expected wOBA (xwOBA), Barrel%, exit velocity or sprint speed on Baseball Savant, compare pitchers by FIP, "
        f"K-BB% or a pitch-quality score, and read projection systems that blend several of these {c('savant', 'fa:S39', 'fa:S40')}. Each statistic is a reasonable "
        "*description* of what happened. The forecasting question is narrower: once a model already knows a player's last two seasons, his age and his playing time, does "
        "this statistic still change next season's estimate, and does the change make the estimate more accurate? Statisticians call this the difference between explaining "
        f"and predicting {c('shmueli')}. Fantasy discussions usually settle it one metric at a time, by correlation or anecdote.")
    b.para(
        "This paper treats the question as a decision rule that can be audited. A candidate metric is *admitted* to a target-specific projection only if adding it lowers "
        "out-of-time forecast error, in seasons the model has not seen, by a material and consistent amount, without being redundant with simpler information. Everything "
        "else keeps a descriptive role, and the reason is recorded. The rule is applied separately to six next-season targets, because a metric can earn a place in one "
        "forecast and add nothing to another. Sprint speed is the cleanest example. It is one of the most stable statistics in the data (year-to-year r = "
        f"{num(sprint_w.reliability_r, '.2f', S['fig1'], '1')}), it sharply improves next-season baserunning forecasts, and it adds nothing to next-season wOBA. Of the "
        f"{ev(str(n_multi), S['eval'], '1')} metrics evaluated for more than one target, {ev(str(n_change), S['eval'], '1')} received different labels for different targets.")
    b.para("The intended reader is a public analyst or fantasy manager. The contributions are specific and falsifiable:")
    b.bullets([
        "**A reproducible admission rule with its human choices labelled.** The statistical test is separated from the human-specified labels: which inputs count as "
        "\"context\", and which failed metrics are kept as \"diagnostic\" (Section 5).",
        "**Stronger validation of the original six-target results.** The entire selection is repeated inside each training window (nested chronological validation), compared "
        "with broad regularized models on identical players, checked with placebo metrics, and examined season by season, including a retrospective 2026 check frozen "
        "before outcomes were downloaded (Section 6). Several original claims narrow or fail; Appendix A lists each claim of the accepted abstract and its status.",
        "**Player-level evidence in baseball units**, for named players, including the largest adjustments that made forecasts worse (Section 7).",
        "**A pre-specified test of fantasy relevance.** Do forecasts of the six targets add information about real fantasy categories beyond a direct category-history model? "
        "The protocol was written and publicly time-stamped before any fantasy model was fit (Section 8).",
        "**A new-target generalization check** on next-season ERA (Section 9), and a companion web application in which the main results can be queried.",
    ])
    b.para(
        "The paper does not claim that its labels are universal baseball facts, that thinner models generally beat broad ones, or that it can replace the proprietary tracking "
        "and modeling of professional organizations. Public single-number metrics compress far richer data, and a team with pitch-level tracking, biomechanics and medical "
        "information faces a different problem (Section 10.4). Nor does it publish a 2027 leaderboard: the research question is which public metrics carry repeatable "
        "next-season information, not who will lead the league.")
    b.figure("fig1_decision_flow.png",
             "How a metric earns admission. Steps 1–4 and the gate box are statistical; the two dashed boxes are human-specified rules recorded in the metric catalog. "
             "The worked example uses the canonical seven-fold evaluation (outcome seasons 2019–2025): the same metric, sprint speed, is admitted for baserunning and labelled "
             "Diagnostic for wOBA; the worked-example values are canonical fold averages. Feature-family definitions are also human-specified (Section 5.4). "
             f"Source: canonical admission artifacts ({'commit withheld for review' if blind else 'commit 17da742'}).")

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
        "hypothesized fantasy link, and what it does not establish; Box 1 defines the summary statistics involved.")
    t1 = pd.DataFrame([
        ["Next-season **wOBA**", "Weighted on-base average: each way of reaching base weighted by its average run value, on the OBP scale; per PA; ≥150 PA in t and t+1",
         "Tests whether hitting-process metrics (xwOBA, exit velocity, plate discipline) add to a hitter's own two-year wOBA",
         "AVG, HR (pre-specified); R, RBI, points (secondary)", "Not a category; ignores playing time, lineup slot and team context; silent on SB"],
        ["Next-season **FIP**", "Fielding Independent Pitching: (13·HR + 3·(BB+HBP) − 2·K)/IP plus a league constant; per IP; ≥80 IP (SP) or ≥30 IP (RP) in t and t+1",
         "The part of run prevention a pitcher controls most directly; tests pitch-quality and strikeout metrics", "ERA, WHIP (pre-specified); K, W, points (secondary)",
         "Not ERA, WHIP, wins, saves or innings; ignores balls in play, sequencing and defense"],
        ["Next-season **baserunning rate**", "Baseball-Reference baserunning runs per 100 times on base (H+BB+HBP−HR); per 600 PA below 20 times on base; ≥150 PA",
         "A running-only component where speed metrics should matter most", "SB (pre-specified)", "Not SB, attempts or success rate; no playing time or green light"],
        ["Next-season **fielding rate**", "Baseball-Reference fielding + catcher runs per 1,000 defensive innings; ≥200 innings in t and t+1",
         "A non-batting component and a deliberate boundary case", "5×5 value (pre-specified boundary case)", "Not scored in standard 5×5 or points formats"],
        ["Next-season **hitter bWAR/600 PA**", "Baseball-Reference position-player WAR scaled to 600 PA; ≥150 PA in t and t+1",
         "Batting, running, fielding and position combined: do component signals survive aggregation?", "5×5 value (pre-specified)",
         "Not points or roto value; credits defense and position, which fantasy ignores; bWAR is not fWAR"],
        ["Next-season **pitcher bWAR/200 IP**", "Baseball-Reference pitcher WAR (runs-allowed based, adjusted for defense and park) scaled to 200 IP; no workload floor",
         "Aggregate pitching value; a noisy stress test", "5×5 value (pre-specified)", "Not wins, saves or innings; differs from FanGraphs' FIP-based pitcher WAR"],
    ], columns=["Target", "What it measures here (verified in code)", "Why it was used", "Hypothesized fantasy link", "What it does not establish"])
    b.table(t1, "The six prediction targets. Panels use feature seasons 2015–2024 and outcomes 2016–2025; evaluation seasons are 2019–2025 (canonical seven folds) and "
            "2021–2025 (nested outer seasons). Definitions verified against the study code and source documentation. The fantasy roles in the fourth column were assigned "
            "after the targets were chosen and were tested in Section 8.",
            widths=[0.95, 1.75, 1.4, 1.1, 1.3], font=14)
    b.para("**Each target in brief: construct, role, and what the paper found.**", keep_next=True, space_after=4)
    b.bullets([
        f"**wOBA.** Weights each way of reaching base by its run value. It tests whether contact-quality metrics add to a hitter's own record. Two-year xwOBA and exit "
        f"velocity were admitted in every window, and the admitted set beat the two-year baseline ({D.T2('hitting_woba', LIFT, sec='2')}), mostly beyond what a third season "
        f"of wOBA adds ({D.HIST('hitting_woba', 'ADM vs B0+3yr', sec='2')}). For fantasy, the wOBA forecast did not clear the bar for HR or AVG (Section 8.3).",
        f"**FIP.** The label uses Baseball Savant's FIP where available and otherwise FIP computed from MLB Stats API counts, with a same-season constant estimated "
        f"from unweighted pitcher means (noisier than the published constant). It is "
        f"the pitching component a pitcher controls most directly, and the admitted strikeout and pitch-quality metrics gave the largest lift "
        f"({D.T2('pitching_fip', LIFT, sec='2')}). It is the only target whose forecast added fantasy information (ERA and WHIP).",
        "**Baserunning rate.** Baseball-Reference baserunning runs: stolen-base and caught-stealing runs plus advancement, outs on the bases and pickoffs, but not "
        f"double plays {c('bref_war_pos')}, per 100 times on base. The per-600-PA fallback never applied in the study sample. Sprint speed and attempt rate were admitted "
        f"({D.T2('baserunning_rv', LIFT, sec='2')}), but the forecast added nothing to stolen-base forecasts; raw sprint speed did (Section 8.4).",
        f"**Fielding rate.** Baseball-Reference fielding and catcher runs, which rest on Defensive Runs Saved {c('bref_war_pos')}. Some candidates (Statcast Outs Above "
        f"Average) come from a different provider, so this is a cross-provider test. The only admitted input was a third season of fielding history "
        f"({D.HIST('defense_rv', 'B0+3yr vs B0', sec='2')} for that history alone), and the fielding forecast added nothing to fantasy value, as a boundary case should.",
        f"**Hitter bWAR/600 PA.** Combines batting, running, fielding, position and replacement level. Selection did not beat the baseline "
        f"({D.T2('overall_war', LIFT, sec='2')}); a third season of WAR history alone helped more ({D.HIST('overall_war', 'B0+3yr vs B0', sec='2')}). Its forecast mainly "
        "carries playing-time information for fantasy.",
        f"**Pitcher bWAR/200 IP.** Runs-allowed based, with defense and park adjustments {c('bref_war_pitch')}. Its population is looser than FIP's (no workload floor; "
        f"2,917 outer rows against 1,328), so the two pitching targets describe overlapping but different pitchers. Selection helped ({D.T2('pitcher_war', LIFT, sec='2')}) "
        "through two-year K-BB%, and the forecast added little to fantasy value.",
    ])
    b.para(
        "**Components versus aggregates.** wOBA and FIP isolate skills that a player largely owns. The two run-value rates isolate skills that public metrics measure directly, "
        "such as sprint speed, but that fantasy formats ignore or count only indirectly. The WAR rates ask whether a metric that helps a component still helps once that "
        "component is diluted inside a broad value measure built on further modeling choices: positional adjustments, replacement level and, for pitchers, runs allowed with a "
        f"defense adjustment {c('bref_war')}. Baseball-Reference WAR is not FanGraphs WAR, whose pitcher version is built from FIP {c('fg_war')}; nothing here is a statement "
        "about fWAR.")
    b.para(
        "**Why keep defense and WAR in a fantasy-facing paper.** Defense is the boundary case: real player value that standard fantasy scoring never counts. A fantasy-relevant "
        "forecast should show little or no fielding signal, and a method that found one would deserve suspicion. The WAR targets are the opposite stress test. WAR is widely "
        "used as a summary of player *quality*; fantasy writers explicitly say it is not fantasy *value* (Section 3.3). The question is whether an aggregate-value forecast is "
        "a useful intermediate for fantasy value or simply a different construct. These roles were assigned after the targets were chosen, and Section 8 tests them instead of "
        "assuming them.")
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
        "before the one it forecasts. The data were collected programmatically, with the open-source pybaseball library and the MLB Stats API, without special permission "
        "from the providers. Three panel details matter for interpretation:")
    b.bullets([
        "the \"park factor\" is a same-season team run-environment index that includes the player's own team, generated by external code outside the repository;",
        "\"previous season\" features use the previous *observed* season (6% of lagged hitter rows skip a year), and Stuff+ for season t is scored by a model fitted on seasons up to and including t;",
        "eligibility uses 150 PA for hitters in every season, including the 60-game 2020 season, while the pitcher floors were scaled down for 2020; the 2021 hitter populations are therefore about half their usual size.",
    ])
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
        f"automated access {c('fa:S50')}, so rebuild scripts should be run only in line with those terms. The public repository therefore contains code that rebuilds every dataset (except the externally generated run-environment index) from the "
        "original sources, SHA-256 checksums of each derived file, aggregate results, and a small curated set of player examples. It does not contain raw tables or "
        "player-season panels (Appendix C).")

    # ================================================================== 5 Method
    b.h1("5. How a metric earns admission")
    b.h2("5.1 Baseline, loss and the incremental test")
    b.para(
        "Each target has a **history baseline** B (written B0 in the comparisons): a ridge regression on the target's own *two-year* history, age, playing time and the "
        f"run-environment index (starter role for pitchers; position group for fielding) {c('hoerl')}. A third season of history is not in B; it is a candidate like any "
        "other metric, which matters for interpreting Section 6.2. Errors are weighted by season-t opportunities (PA, innings or defensive innings). For fold k and feature "
        "set F, accuracy is the weighted root-mean-squared error in Equation 1:")
    b.equation("rmse")
    b.para(
        f"The **incremental effect** of candidate metric j is the average change in RMSE when j is added to the baseline, across K expanding chronological folds {c('tashman', 'bergmeir')}. "
        "Each fold trains on all seasons before its test season. The canonical study uses seven folds with outcome seasons 2019–2025 (four for arm angle, which begins in 2020); negative values mean the metric helped. "
        "The canonical point estimate averages the fold-level changes, while its interval is a pooled bootstrap of paired errors; the two estimate slightly different quantities, "
        "and for 7 of the 208 evaluations the fold average falls just outside its interval. The nested, 2026 and fantasy analyses compute the point estimate and interval from the same pooled statistic:")
    b.equation("delta")
    b.para("A metric is a candidate for **Projection** (Equation 3) only if the improvement Δ is material (at least 0.5% of the baseline's mean fold RMSE), measured over at "
           "least three folds, and either consistent (improving in at least 60% of folds, π) or clearly negative (upper 95% bootstrap bound u below zero). The bootstrap "
           "behind u resamples rows independently (400 draws) and so ignores that the same players recur across folds; the nested and fantasy analyses use player-cluster "
           "intervals instead.")
    b.equation("admit")
    b.para(
        "It must then also survive a greedy feature-family step. Metrics are grouped into human-defined families (Appendix E). The best metric in each family is kept, and "
        "another member of the same family is added only if it still lowers RMSE by at least 0.5% given the baseline and the members already kept; redundancy across "
        "families is not checked. A Projection metric also needs a coefficient that changes sign fewer than two times across folds, coverage of at least 70% of "
        "player-seasons (90% when missingness is systematic), and no material harm in at least half of the large subgroups (n ≥ 150; age, playing time, handedness, role).")
    b.h2("5.2 What the labels mean, and which ones are human choices")
    t3 = pd.DataFrame([
        ["Projection", "Passes the incremental test and every gate", "Statistical", f"{D.VERDICTS['Projection']}"],
        ["Diagnostic", "Fails the projection test (or is redundant with a kept family member) **and** the catalog flags it as an interpretable process measure", "Statistical test, then a human flag", f"{D.VERDICTS['Diagnostic']}"],
        ["Exclude", "Fails the projection test and carries no process flag; means \"no conditional value for this target given this baseline\", not \"useless\"", "Statistical test, then a human flag", f"{D.VERDICTS['Exclude']}"],
        ["Context", "Park, environment, age or playing-time inputs, whatever their lift", "Human-specified role", f"{D.VERDICTS['Context']}"],
        ["Augmented Projection / Insufficient Evidence", "Predictive only where observed / too few folds and too sparse coverage", "Statistical", "0 (207 of 208 evaluations had 7 folds; arm angle, available from 2020, had 4)"],
    ], columns=["Label", "Rule", "Basis", "Count (of 208)"])
    b.table(t3, "Admission labels, how each is decided, and whether a human choice is involved (decision rule `decide_verdict` in the study code; canonical counts).",
            widths=[1.2, 3.0, 1.35, 0.95], font=15)
    b.para(
        "Two points matter for reading the labels (Table 3). First, the algorithm does not discover baseball semantics. Three inputs are human choices: the role that makes "
        "a metric \"Context\", the process flag that separates \"Diagnostic\" from \"Exclude\", and the family definitions that decide which metrics compete in the "
        "redundancy step (and so 32 of the Diagnostic labels). Second, every label is "
        "conditional: on the target, on what the baseline already contains, on the population and on the seasons. An Exclude for wOBA says nothing about the same metric for "
        "baserunning.")
    b.h2("5.3 Four different things called \"unstable\"")
    t4 = pd.DataFrame([
        ["Feature reliability", "Year-to-year Pearson r of the metric itself (same player, t and t+1)", "Reported; listed in Diagnostic reasons; never gates", f"Sprint speed: r = {num(sprint_w.reliability_r, '.2f', S['fig1'], '5.3')}, yet no wOBA value"],
        ["Lift consistency", "Share of the out-of-time folds (7 for 207 of 208 evaluations) in which adding the metric lowered RMSE", "Gates: ≥60% (or CI below zero)", f"Sprint speed → baserunning: {int(sprint.folds_improved)} of {int(sprint.n_folds)} folds"],
        ["Coefficient drift", "Number of sign changes of the metric's coefficient across folds", "Gates: fewer than 2", "—"],
        ["Uncertainty", "Width of the 95% bootstrap interval of the RMSE change", "Gates only via the \"CI below zero\" alternative", "Stuff+ → FIP pooled interval nearly touches zero"],
        ["Selection stability", "Whether the same metrics are chosen in every nested window", "Descriptive only; never gates", "wOBA: the same three inputs in all six windows"],
    ], columns=["Meaning", "How it is measured", "Role in the rule", "Example"])
    b.table(t4, "Operational definitions of \"unstable\" and \"stable\" (Section 5.3). A metric can be stable in the first sense and useless for a target in the second.", widths=[1.1, 2.2, 1.6, 1.6], font=15)
    b.h2("5.4 Strikeout rate versus K-BB%")
    b.para(
        "FIP is built from strikeouts, walks, hit-by-pitches and home runs, so its predictors deserve care. K-BB% is simply K% minus BB%. In the canonical FIP study the "
        "families are defined as follows: K% and BB% form a \"strikeout and walk skill\" family, while every K-BB% variant sits in the \"outcome\" family with the FIP and ERA "
        "histories (Appendix E). Pooled over 2019–2025 with player-cluster intervals:")
    b.bullets([
        f"current-season K% improved FIP forecasts ({D.POOLED('k_pct', sec='5.4')}) and was admitted as its family's representative;",
        f"BB% added nothing ({D.POOLED('bb_pct', sec='5.4')}), so the predictive content of K-BB% is its strikeout part;",
        f"three-year K-BB% ({D.POOLED('k_bb_pct_w3', sec='5.4')}) was the outcome family's first representative, and current-season K-BB% "
        f"({D.POOLED('k_bb_pct', sec='5.4')}) was then set aside because, given three-year K-BB%, it no longer cleared the 0.5% bar;",
        "because redundancy is checked only within families, K%, three-year K-BB% and other strikeout metrics can all enter the FIP model together.",
    ])
    b.para(
        "\"Current K-BB% is Diagnostic\" therefore means \"redundant once a longer K-BB% history is in the model\", not \"K-BB% does not predict FIP\". (The canonical fold "
        "averages for these metrics are larger, about −3%, because they average fold-level changes; Section 5.1 explains why the two estimates differ.)")
    b.h2("5.5 Nested validation, comparisons and the 2026 check")
    b.para(
        "The original evaluation chose metrics using the same seasons on which it reported accuracy. The reanalysis removes that look-ahead. For each outer season T from 2021 to "
        f"2025, the entire admission procedure 𝒜 is rerun on the data 𝒟 with feature season at most T−2, using inner test years 2018 to T−1 {c('varma', 'cawley', 'ambroise')}. "
        "All gate statistics are computed on those training rows only; for T = 2021 there are just three inner folds, so the consistency rule then requires two of three. "
        "The selected set S_T is used to fit the final model on all rows with feature season at most T−2 and to forecast season T (Equation 4):")
    b.equation("nested")
    b.para("All competing models are scored on the same players and seasons:", keep_next=True)
    b.bullets([
        "the history baseline (B0);",
        "the nested selection (ADM);",
        "the original look-ahead selection (FIX);",
        "a kitchen-sink model (KS) with every numeric skill candidate that covers at least 5% of training rows, fitted as ridge with α = 1 after training-median imputation;",
        f"tuned versions of these: ridge (α from 0.01 to 1,000), elastic net {c('zou')}, LightGBM {c('ke')} and random forest {c('breiman')}, with hyperparameters chosen on "
        "inner chronological folds (grids in the repository).",
    ])
    hashes = "commit and checksum withheld for review" if blind else "committed as f8023bf, SHA-256 af61b2b8…"
    b.para(
        f"Differences are reported as % of the reference model's RMSE, with 95% paired bootstrap intervals that resample players (2,000 draws, seed 42). These intervals "
        "describe uncertainty about players *within* the 2021–2025 seasons. With five seasons, season-to-season variation is reported separately and is much coarser. A "
        f"**2026 check** used the same code: predictions for every 2025-eligible player were frozen before any 2026 outcome table was downloaded ({hashes}; tables fetched "
        f"{ev('2026-11-12 06:49 UTC', S['fetch'], '5.5')}). The 2026 label pipeline was first validated on 2025, reproducing {ev(f'{D.LAB_OK:,} of {D.LAB_N:,}', S['lv'], '5.5')} "
        "labels exactly. This is a *frozen-in-workflow, retrospective* check. The 2026 season had already been played, and two ancillary input files (the run-environment index "
        "and the Stuff+ scores) contained partial 2026 rows that the 2025-feature forecasts did not use. It is not a prospective trial, and any analysis added afterwards is "
        "exploratory.")

    # ================================================================== 6 Results I
    b.h1("6. Results I: what survives stronger validation")
    b.h2("6.1 The original computation reproduces; what that does and does not show")
    b.para(
        f"Re-running the canonical code on 2026-11-13 matched all {ev(f'{D.N_REPRO_MATCH} of {D.N_REPRO}', S['repro'], '6.1')} reproduction checks. These include the "
        f"402/208/163 counts, every published selective and kitchen-sink RMSE, and the label counts ({D.VERDICTS['Projection']} Projection, {D.VERDICTS['Diagnostic']} "
        f"Diagnostic, {D.VERDICTS['Context']} Context, {D.VERDICTS['Exclude']} Exclude). Figure 2 shows how those labels divide by target. Of the Diagnostic labels, "
        f"{ev(str(int(D.reason['Diagnostic — no material incremental lift'])), S['reason'], '6.1')} showed no material lift, and "
        f"{ev(str(int(D.reason['Diagnostic — predictive alone, redundant with a kept family member'])), S['reason'], '6.1')} were predictive alone but redundant with a kept "
        f"family member. Of the 27 Projection labels, 6 are the baselines' own two-year inputs (scored against a weaker current-season baseline), 4 are other windows of the "
        f"target's own record, and 17 are other metrics. Across all 208 tests with cluster bootstrap p-values, {ev(f'{q05} of {nproj}', S['mult'], '6.1')} Projection rows have "
        f"Benjamini–Hochberg {c('bh')} q < 0.05; because those seasons had already been examined, these adjustments are exploratory.")
    b.para("Exact reproduction shows consistency with the original pipeline, not that the pipeline was flawless. Five weaknesses are disclosed:", keep_next=True)
    b.bullets([
        "the canonical code refuses to write its table unless certain headline values hold (for example the two-year xwOBA effect and several labels): a guard that locks results;",
        "the hitting \"selective\" model in the original selective-versus-kitchen-sink comparison was a hard-coded list chosen after results were known;",
        "the original FIP selective and kitchen-sink errors were computed on different rows (1,699 and 1,866);",
        "the admission gate's interval resamples rows independently and ignores repeated players;",
        "the canonical point estimate (a fold average) and its interval (a pooled bootstrap) estimate slightly different quantities.",
    ])
    b.para("The nested reanalysis below uses rules only, with no guards, identical rows and player-cluster intervals.")
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
             "What the 208 canonical evaluations concluded, by target. The Projection labels are split into the baselines' own two-year inputs, other windows of the target's "
             "own record, and other metrics. Diagnostic labels are split into metrics that were predictive alone but redundant with a kept family member, and metrics with no "
             "material lift. The Diagnostic/Exclude split is a human process flag, and Context is assigned from a human-specified role. Counts are target-specific verdicts.")

    # ---------------- 6.2 nested selection
    b.h2("6.2 Admitted inputs improve two-year-history baselines for five of six targets")
    b.para(
        "Re-running the selection inside each training window, the admitted set lowered out-of-time RMSE against the two-year history baseline, pooled over 2021–2025, for:")
    b.bullets([
        f"wOBA: {D.T2('hitting_woba', LIFT, sec='6.2')};",
        f"FIP: {D.T2('pitching_fip', LIFT, sec='6.2')};",
        f"baserunning: {D.T2('baserunning_rv', LIFT, sec='6.2')};",
        f"fielding: {D.T2('defense_rv', LIFT, sec='6.2')};",
        f"pitcher WAR: {D.T2('pitcher_war', LIFT, sec='6.2')}.",
    ])
    b.para(f"For hitter WAR it did not ({D.T2('overall_war', LIFT, sec='6.2')}; Figure 3A). In baseball units (Table 5), the RMSEs moved as follows:")
    u6 = []
    for sid, unit, scale, fmt in (("hitting_woba", "wOBA points (thousandths)", 1000, ".1f"), ("pitching_fip", "FIP (runs per 9 IP)", 1, ".3f"),
                                  ("baserunning_rv", "baserunning runs per 100 times on base", 1, ".3f"), ("defense_rv", "fielding runs per 1,000 innings", 1, ".2f"),
                                  ("overall_war", "WAR per 600 PA", 1, ".3f"), ("pitcher_war", "WAR per 200 IP", 1, ".2f")):
        rb_, ra_ = D.t2.loc[D.TL[sid], "Baseline RMSE"] * scale, D.t2.loc[D.TL[sid], "Selected RMSE"] * scale
        u6.append([D.TL[sid], unit, ev(m(f"{rb_:{fmt}} → {ra_:{fmt}}"), S["t2"], "Table 5"), D.T2(sid, LIFT, sec="Table 5"), D.HIST(sid, "B0+3yr vs B0", sec="Table 5"),
                   D.HIST(sid, "ADM vs B0+3yr", sec="Table 5")])
    b.table(pd.DataFrame(u6, columns=["Target", "Unit", "RMSE: baseline → selected", "Selected vs baseline", "Third season of history vs baseline (post hoc)",
                                      "Selected vs baseline + third season (post hoc)"]),
            "Nested results in baseball units (outer seasons 2021–2025, identical rows; ΔRMSE % with 95% player-cluster intervals). The last two columns separate the gain from "
            "a third season of the target's own history from the gain due to other admitted metrics.", widths=[0.95, 1.35, 1.0, 1.05, 1.1, 1.1], font=14)
    b.para(
        "The decomposition matters for the paper's thesis. For FIP, baserunning, wOBA and pitcher WAR, most of the gain comes from metrics other than a longer history of the "
        "target. For fielding, the whole gain is a third season of fielding history: no public metric earned a place. For hitter WAR, a third season of history alone helped "
        "more than the selection did. The selections were stable across windows:")
    b.bullets([
        "for wOBA, the three-year wOBA history, two-year xwOBA and exit velocity were chosen in all six windows (2021–2026);",
        "for baserunning, the three-year history, sprint speed, stolen-base attempt rate and second-to-home advancement rate were chosen in all six;",
        f"for FIP, the window sets held {ev(m(f'{min(fip_sizes)}–{max(fip_sizes)}'), S['meta'], '6.2')} metrics, with Stuff+ entering from the "
        f"{ev(str(stuff_from), S['meta'], '6.2')} window onward;",
        f"for hitter WAR, exit velocity was chosen in only {ev(f'{ev_war} of 6', S['meta'], '6.2')} windows.",
    ])
    b.para(
        f"Choosing metrics with knowledge of the evaluation seasons had flattered accuracy by at most {ev(f'{D.FIXADM_MAX:.2f}%', S['nest'], '6.2')} of RMSE, judged by the "
        "original look-ahead set against the nested set. Two further checks (post hoc) qualify the headline numbers:")
    b.bullets([
        f"**Season level.** Across the five outer seasons, selection beat the baseline in every season for wOBA, FIP, baserunning and pitcher WAR. For FIP, though, the "
        f"per-season gains ranged from −14.0% to −0.9% ({D.SEAS('pitching_fip: selected vs history baseline', '6.2')}). With five seasons no season-level test can reach "
        "p < 0.05 by sign-flipping.",
        f"**Level versus ranking.** Part of the FIP gain is a season-wide level correction that does not help rank players: after removing each model's season-mean error, "
        f"the FIP gain falls from {num(D.within.loc['pitching_fip: selected vs history baseline', 'raw_pct'], '+.1f', S['within'], '6.2')}% to "
        f"{num(D.within.loc['pitching_fip: selected vs history baseline', 'within_season_pct'], '+.1f', S['within'], '6.2')}%, while the wOBA gain grows "
        f"({num(D.within.loc['hitting_woba: selected vs history baseline', 'within_season_pct'], '+.1f', S['within'], '6.2')}%).",
    ])
    b.para(
        f"In the retrospective 2026 check, the selected model's advantage over the baseline had an interval excluding zero only for pitcher WAR "
        f"({D.T2('pitcher_war', L26, sec='6.2')}); for wOBA ({D.T2('hitting_woba', L26, sec='6.2')}), FIP ({D.T2('pitching_fip', L26, sec='6.2')}) and baserunning "
        f"({D.T2('baserunning_rv', L26, sec='6.2')}) the point estimates favored selection, and for fielding and hitter WAR they did not.")
    b.figure("fig3_model_comparisons.png",
             "Six-target model comparisons on identical players. Filled markers: outer seasons 2021–2025 with nested selection (n = 1,328–2,917 player-seasons per target). "
             "Open markers: the 2026 frozen-in-workflow check (retrospective cohort; n = 268–586). Panel A: selected minus history baseline. Panels B and C: broad all-metric "
             "model minus selected, so values left of zero favor the broad model. Intervals are 95% paired player-cluster bootstrap intervals.")
    # ---------------- 6.3 broad models
    b.h2("6.3 Selective versus broad models depends on the comparison and the season")
    b.para(
        f"Against an all-metric ridge model (KS) with a fixed penalty, the selected models were more accurate for wOBA ({D.T2('hitting_woba', KSR, sec='6.3')}, KS minus "
        f"selected) and FIP ({D.T2('pitching_fip', KSR, sec='6.3')}). The original claim survives only in that narrow form:")
    b.bullets([
        f"a tuned elastic net showed no detectable difference from the selected model for wOBA ({D.T2('hitting_woba', KEN, sec='6.3')}) and FIP ({D.T2('pitching_fip', KEN, sec='6.3')}); "
        f"in the pre-specified sensitivity with inner folds starting in 2017, the elastic net was better for FIP ({D.INNER('pitching_fip', 'EN-KS vs ADM (tuned elastic net on kitchen)', sec='6.3')});",
        f"broad models were better for hitter WAR ({D.T2('overall_war', KSR, sec='6.3')}) and pitcher WAR ({D.T2('pitcher_war', KSR, sec='6.3')});",
        f"in 2026 the all-metric ridge model beat the selected model for FIP ({D.T2('pitching_fip', K26, sec='6.3')}) and pitcher WAR ({D.T2('pitcher_war', K26, sec='6.3')});",
        f"in 2026 the elastic net beat it for wOBA ({D.T2('hitting_woba', E26, sec='6.3')}) and FIP ({D.T2('pitching_fip', E26, sec='6.3')}).",
    ])
    b.para(
        "Figure 4 shows the pattern over time. For wOBA, the all-metric ridge model's disadvantage was largest in 2021, when the training window was shortest, and shrank "
        "until it reversed in 2025. For FIP it peaked in 2022 and had also reversed by 2025. One reading is that selection mainly protects a lightly regularized broad model "
        "from estimation noise when data are scarce, a protection a tuned elastic net already provides. Five outer seasons cannot separate this from a change in the game, so "
        "the paper reports the pattern without claiming a cause. \"Thinner beats broader\" is not a law; it is a result specific to the comparison and the era.")
    # ---------------- 6.4 flagships
    b.h2("6.4 The headline metrics, one at a time")
    b.para("Table 6 follows the accepted abstract's headline examples through every stronger test.", keep_next=True)
    rows = []
    for h in D.t3.index:
        rows.append([h, D.t3.loc[h, "Contrast"], m(f"{D.t3.loc[h, 'Published ΔRMSE (mean of 7 folds)']:+.5f}"),
                     ev(m(D.t3.loc[h, "2019–25 pooled, % [cluster CI]"]), S["t3"], "Table 6"), ev(m(D.t3.loc[h, "Nested 2021–25, %"]), S["t3"], "Table 6"),
                     ev(m(D.t3.loc[h, "2026 holdout, %"]), S["t3"], "Table 6")])
    t5 = pd.DataFrame(rows, columns=["", "Contrast (baseline + one metric)", "As published (target units, 7-fold mean)", "2019–25 pooled, %", "Outer 2021–25, %", "2026, %"])
    b.table(t5, "Headline contrasts under stronger tests (H1–H7). H1–H5 and H7 are the accepted abstract's examples (Appendix A); H6 (strikeout rate) was added in the "
            "reanalysis. ΔRMSE as % of the baseline RMSE with 95% player-cluster intervals; negative favors adding the metric. \"Outer 2021–25\" adds the fixed metric to the "
            "history baseline in each outer season; the metric is not re-selected.", widths=[0.3, 1.85, 1.0, 1.15, 1.15, 1.1], font=15)
    b.bullets([
        f"**xwOBA (two-year)**: the point estimate favored the metric in every evidence source; the 2026 interval included zero ({D.T3('H1', '2026 holdout, %', sec='6.4')}).",
        f"**Strikeout rate** improved FIP, including in 2026 ({D.T3('H6', '2026 holdout, %', sec='6.4')}).",
        f"**Sprint speed**: point estimates favored it for baserunning in every source, and the 2026 interval included zero ({D.T3('H5', '2026 holdout, %', sec='6.4')}). It "
        f"was null for wOBA throughout ({D.T3('H7', '2026 holdout, %', sec='6.4')}).",
        f"**Stuff+** helped FIP only slightly ({D.T3('H4', '2019–25 pooled, % [cluster CI]', sec='6.4')}; Benjamini–Hochberg q = {num(stq, '.3f', S['t3'], '6.4')} across "
        "the 208 tests).",
        f"**Exit velocity → hitter WAR** did not hold up: outer 2021–25 {D.T3('H3', 'Nested 2021–25, %', sec='6.4')}; 2026 {D.T3('H3', '2026 holdout, %', sec='6.4')}.",
    ])
    # ---------------- 6.5 gates, placebos
    b.h2("6.5 Which gates change the answer")
    b.para(
        "One-at-a-time ablations reran the nested selection with a single gate removed or a threshold changed (Appendix E lists every variant). Changes that moved "
        "out-of-time error with an interval excluding zero, in each target's own units:")
    b.bullets([
        "removing the family-redundancy step worsened FIP (+0.019);",
        "materiality threshold 0 improved fielding (−0.010) but worsened FIP (+0.013); 0.25% improved hitter WAR (−0.006) but worsened FIP (+0.010); 1% worsened fielding "
        "(+0.068) and FIP (+0.010); 2% worsened baserunning, fielding, pitcher WAR and FIP;",
        "requiring at least 4 folds worsened baserunning, wOBA and FIP; requiring 75% of folds to improve worsened FIP (+0.006).",
    ])
    b.para(
        "Removing the materiality gate entirely, the coverage gate, the coefficient-sign or subgroup gates, or changing the admission ridge penalty (α = 0.1 or 10) changed no "
        "target's error, although removing the coverage or materiality gate changed which metrics were selected. The hitter-WAR null in Section 6.2 therefore depends on the "
        "threshold. In short, the threshold settings and the family step move forecast error; several other gates change only labels and selections.")
    b.para(
        f"Placebo metrics, built by permuting real metrics across player-seasons, were never admitted ({ev(f'{D.N_PLAC_ADMIT} of {D.N_PLAC:,}', S['plac'], '6.5')}). "
        f"{ev(str(int(D.plac2.diagnostic)), S['plac2'], '6.5')} of them were labelled Diagnostic, which shows that the Diagnostic label carries no information beyond the "
        f"human process flag. {ev(str(int(D.plac2.improved_every_fold_but_not_admitted)), S['plac2'], '6.5')} placebos improved in every fold and were stopped only by the "
        "materiality threshold.")
    b.figure("fig4_year_by_year.png",
             "Season-by-season view of the two central comparisons for each target. Blue: selected minus history baseline (below zero means selection helped). Orange: "
             "all-metric ridge minus selected (above zero means the selected model was better). The 2026 points carry 95% intervals; 2021–2025 points are point estimates. "
             "For hitter WAR in 2021 and 2023 no metric was selected, so the selected and baseline models coincide in those seasons.")

    # ================================================================== 7 Player stories
    b.h1("7. Results II: player stories in baseball units")
    r1, r10 = D.ret.loc[1], D.ret.loc[10]
    b.para(
        f"Average RMSE changes hide what happens to individual forecasts. Adding the study's in-house Stuff+ (an expected-whiff score with no arm-angle term) to the FIP "
        f"baseline changed RMSE by {pct(st.pct, nd=2, src=S['units'], sec='7')} in the outer seasons. The typical forecast moved by only "
        f"{num(st.median_abs_forecast_change, '.2f', S['units'], '7')} FIP units (90th percentile {num(st.p90_abs_forecast_change, '.2f', S['units'], '7')}), and "
        f"{ev(f'{100 * st.share_improved_abs_error:.0f}%', S['units'], '7')} of forecasts became more accurate. These are changes in FIP units: a projected FIP moving by "
        "0.14, not 0.14 earned runs saved or 0.14 points of fantasy ERA. A positive change means a higher, that is worse, FIP forecast.")
    b.para(
        "**Where Stuff+ helps and where it hurts (Figure 5).** For pitchers in the top Stuff+ decile, adding the metric lowered the FIP forecast by "
        f"{num(abs(s_top_ch), '.2f', S['coh'], '7')} on average, and {ev(f'{100 * r10.share_improved:.0f}%', S['ret'], '7')} of those forecasts became more accurate "
        f"(95% interval {ev(m(f'{100 * r10.wilson_low:.0f}–{100 * r10.wilson_high:.0f}%'), S['ret'], '7')}). For the bottom decile it raised the forecast by "
        f"{num(s_bot_ch, '.2f', S['coh'], '7')}, and only {ev(f'{100 * r1.share_improved:.0f}%', S['ret'], '7')} became more accurate "
        f"({ev(m(f'{100 * r1.wilson_low:.0f}–{100 * r1.wilson_high:.0f}%'), S['ret'], '7')}). These shares are conditional on pitchers who stayed in the evaluated sample, "
        f"and retention differed by decile: {ev(f'{100 * r1.retained_share:.0f}%', S['ret'], '7')} of bottom-decile pitchers against "
        f"{ev(m(f'{100 * D.ret.loc[8:10].retained_share.min():.0f}–{100 * D.ret.loc[8:10].retained_share.max():.0f}%'), S['ret'], '7')} in the top three deciles. Low-Stuff+ "
        "pitchers who keep their jobs are partly selected for good results, which would make an upward adjustment look wrong. Reweighting by the inverse of a retention model "
        "built from season-t information (post hoc) left the pattern essentially unchanged "
        f"({ev(m(f'{100 * r1.ipw_share_improved:.0f}%'), S['ret'], '7')} against {ev(m(f'{100 * r10.ipw_share_improved:.0f}%'), S['ret'], '7')}), although unobserved "
        "reasons for retention cannot be ruled out. For high-grade pitchers the adjustment usually helped; for low-grade pitchers it usually did not.")
    b.para(
        f"Tyler Rogers is the extreme case. A submarine reliever with an arm angle near {ev(m(f'{rog.arm_angle.mean():.0f}°'), S['cases'], '7')}, far outside the range of "
        f"conventional deliveries, he graded at Stuff+ {ev(m(f'{rog.feature_value.min():.0f}–{rog.feature_value.max():.0f}'), S['cases'], '7')}. In each of five outer "
        f"seasons, adding Stuff+ raised his FIP forecast by {ev(m(f'{rog.change.min():.2f}–{rog.change.max():.2f}'), S['cases'], '7')}. His observed FIPs were "
        f"{ev(m(f'{rog.y.min():.2f}–{rog.y.max():.2f}'), S['cases'], '7')}, below even the forecasts without Stuff+, so all five adjustments made the forecast worse. He accounts "
        f"for {ev(f'{D.LARGEST6_ROGERS} of the 6', S['fc'], '7')} largest Stuff+ adjustments in the whole sample, and {ev(f'{D.LARGEST6_WORSE} of those 6', S['fc'], '7')} worsened "
        "the forecast. This study's Stuff+ has no arm-angle or release-height term, and it mis-graded this one pitcher in every season; whether other pitch models share the "
        "problem was not tested.")
    b.para(
        f"Zack Wheeler is a success case. With Stuff+ {ev(m(f'{whe.feature_value.min():.0f}–{whe.feature_value.max():.0f}'), S['cases'], '7')}, the metric lowered his FIP "
        f"forecast by {ev(m(f'{abs(whe.change).min():.2f}–{abs(whe.change).max():.2f}'), S['cases'], '7')} in each of five seasons, and every one of those forecasts improved, "
        "because his results kept beating the history-only forecast.")
    b.figure("fig5_player_stories_stuff.png",
             "Stuff+ and next-season FIP forecasts. A–B: forecasts without (open) and with (filled) Stuff+ against observed FIP for two named pitchers, outer seasons 2021–2025; "
             "these cases illustrate extremes and are not typical. C–D: all 1,328 outcome-observed pitcher-seasons by Stuff+ decile within season, showing the mean change in the "
             "FIP forecast (positive = higher, worse forecast) and the share of forecasts that became more accurate, with 95% intervals. FIP units, not runs.")
    b.para("Table 7 adds named cases chosen by a fixed rule, one improvement and one harm per contrast, so that the examples are not hand-picked.")
    b.para(
        "**Strikeout rate.** K% moves FIP forecasts more than Stuff+ does (median change "
        f"{num(kp.median_abs_forecast_change, '.2f', S['units'], '7')} FIP; 90th percentile {num(kp.p90_abs_forecast_change, '.2f', S['units'], '7')}). Its asymmetry runs "
        f"the same way: in the top decile the forecast fell by {num(abs(k_top_ch), '.2f', S['coh'], '7')} and {ev(f'{100 * k_top_im:.0f}%', S['coh'], '7')} of forecasts "
        f"improved, against {ev(f'{100 * k_bot_im:.0f}%', S['coh'], '7')} in the bottom decile (the same retention caveat applies).")
    b.para(
        f"**xwOBA.** Two-year xwOBA moved a typical wOBA forecast by {num(1000 * xw.median_abs_forecast_change, '.1f', S['units'], '7')} wOBA points (thousandths of wOBA; "
        f"90th percentile {num(1000 * xw.p90_abs_forecast_change, '.1f', S['units'], '7')}). For the decile with the largest wOBA-over-xwOBA gap, the forecast fell by "
        f"{num(1000 * abs(x_over_ch), '.0f', S['coh'], '7')} points on average and {ev(f'{100 * x_over_im:.0f}%', S['coh'], '7')} of forecasts improved. For the opposite decile, "
        f"apparent bad luck, it rose by {num(1000 * x_under_ch, '.0f', S['coh'], '7')} points and {ev(f'{100 * x_under_im:.0f}%', S['coh'], '7')} improved (each share "
        "±7–8 points). Among hitters who returned, \"sell high on over-performers\" held up better than \"buy low on under-performers\".")
    b.para(
        f"**Sprint speed.** For baserunning, the fastest decile's forecasts rose by {num(b_top_ch, '.2f', S['coh'], '7')} runs per 100 times on base and the slowest decile's "
        f"fell by {num(abs(b_bot_ch), '.2f', S['coh'], '7')}; {ev(f'{100 * b_top_im:.0f}%', S['coh'], '7')} and {ev(f'{100 * b_bot_im:.0f}%', S['coh'], '7')} of those "
        f"forecasts improved. For wOBA, the median change was {num(1000 * wos.median_abs_forecast_change, '.1f', S['units'], '7')} wOBA points: in practice, nothing.")
    cr = []
    for _, r in D.cases2.iterrows():
        unit = {"wOBA": ".3f", "BR runs per 100 times on base": ".2f", "ERA": ".2f"}[r.unit]
        name = r.player if "," not in str(r.player) else " ".join(reversed([s.strip() for s in r.player.split(",", 1)]))
        lab = {"hitting_woba:xwoba_w2": "xwOBA → wOBA", "baserunning_rv:sprint_speed": "Sprint speed → baserunning", "fantasy: FIP forecast -> ERA": "FIP forecast → ERA (fantasy)"}[r.contrast]
        cr.append([lab, r.rule.replace(" (≥60 IP)", ""), name, f"{int(r.feature_season)}→{int(r.outcome_season)}",
                   ev(m(f"{r.forecast_without:{unit}} → {r.forecast_with:{unit}}"), S["cases2"], "Table 7"), ev(m(f"{r.observed:{unit}}"), S["cases2"], "Table 7"),
                   ev(m(f"{r.abs_error_change:+{unit}}"), S["cases2"], "Table 7")])
    b.table(pd.DataFrame(cr, columns=["Contrast", "Rule", "Player", "Seasons", "Forecast without → with", "Observed", "Error change"]),
            "Named cases chosen by a fixed rule (post hoc): for each contrast, the player-season whose forecast error improved most and the one whose error grew most when the "
            "metric (or, for ERA, the FIP forecast) was added. Units: wOBA; baserunning runs per 100 times on base; ERA (pitchers with at least 60 IP). The ERA cases come from "
            "the 2020-to-2021 window, when the 60-game season made forecasts noisy.", widths=[1.25, 0.95, 1.15, 0.65, 1.05, 0.65, 0.8], font=14)

    # ================================================================== 8 Fantasy bridge
    b.h1("8. Results III: from performance forecasts to fantasy categories")
    b.h2("8.1 Design")
    proto = ("protocol commits and their times are withheld for review and given in the repository" if blind else
             "protocol version 1.0 was pushed as commit 8819791 and Amendment 1 as b482448, both on 2026-11-13 before the corresponding models were fit; "
             "Amendment 2 (5f6d854) records post hoc analyses")
    b.para(
        "The six targets are not fantasy categories, so their relevance to fantasy play has to be tested, not assumed. The test asks whether out-of-time forecasts of the "
        "targets add information about next-season fantasy outcomes beyond a **direct fantasy baseline**. The protocol was written and pushed to a public repository before any "
        f"fantasy-category model was fit ({proto}). By then the six-target results and the 2026 season had already been seen, so the fantasy results are exploratory. The "
        "baseline is a tuned ridge model of each category on things a careful manager can compute from standard statistics:")
    b.bullets([
        "the previous season's and two-year per-PA rates of R, HR, RBI and SB, AVG, BB% and K%, plus prior PA and games, for hitters;",
        "prior innings, starts, wins, saves, holds, strikeouts per inning, ERA and WHIP, for pitchers;",
        "age and age squared, for both.",
    ])
    b.para(
        "Future playing time is never an input. The target forecasts are the nested ADM forecasts (and, for comparison, the history-only B0 forecasts). For every training row "
        "the forecast's coefficients are fitted only on earlier seasons, but its metric set is the window's set S_T, which was chosen using outcomes that include those "
        "training rows' seasons; test-season outcomes never enter. For the test seasons the forecasts reproduce the Section 6 predictions, including the frozen 2026 file, "
        f"to within {ev('2 × 10⁻¹⁵', S['up'], '8.1')}.")
    b.para(
        "Outcomes are 5×5 categories: R, HR, RBI, SB and AVG for hitters; W, SV, K, ERA and WHIP for pitchers. Counting categories are evaluated on the full forecast-date pool, "
        f"where between {ev(f'{100 * zh['min']:.0f}%', S['cb'], '8.1')} and {ev(f'{100 * zh['max']:.0f}%', S['cb'], '8.1')} of pool hitters and "
        f"{ev(f'{100 * zp['min']:.0f}%', S['cb'], '8.1')}–{ev(f'{100 * zp['max']:.0f}%', S['cb'], '8.1')} of pool pitchers produced nothing the next season. Ratio categories "
        "are computed from components (AVG = H/AB; ERA = 9·ER/IP; WHIP = (BB+H)/IP, with innings from recorded outs) and weighted by volume. They are evaluated, and their "
        "models trained, only among players with at least 100 AB or 20 IP the next season, so they are conditional on playing. A 5×5 **value** score V (Equation 5) sums "
        "the z-scores of R, HR, RBI and SB, or W, SV and K, plus volume-weighted contributions for AVG, ERA and WHIP measured against reference ratios. Means, SDs and "
        "reference ratios come from earlier seasons' full forecast-date pools, not from rostered players, and V has no replacement-level or positional adjustment:")
    b.equation("value")
    b.para(
        f"Eight linkages were pre-specified as primary and Holm-adjusted {c('holm')}: wOBA → AVG, wOBA → HR, FIP → ERA, FIP → WHIP, baserunning → SB, and fielding, hitter WAR "
        "and pitcher WAR → value. Secondary comparisons are Benjamini–Hochberg-adjusted within four families: single target forecasts (40), admitted versus history-only "
        "forecasts (48), joint forecasts (32) and raw metrics (12). Because q-values depend on these family definitions, secondary results are labelled exploratory. Outcome "
        "seasons 2021–2025 are primary; the 2026 rows are unadjusted and exploratory.")
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
    seas_key = {("fip", "ERA"): "fantasy primary: fip -> ERA", ("fip", "WHIP"): "fantasy primary: fip -> WHIP", ("woba", "HR"): "fantasy primary: woba -> HR",
                ("woba", "AVG"): "fantasy primary: woba -> AVG", ("br", "SB"): "fantasy primary: br -> SB", ("fld", "VAL_H"): "fantasy primary: fld -> VAL_H",
                ("hwar", "VAL_H"): "fantasy primary: hwar -> VAL_H", ("pwar", "VAL_P"): "fantasy primary: pwar -> VAL_P"}
    t6 = pd.DataFrame([[f"{lab[r.target]} forecast → {olab.get(r.outcome, r.outcome)}", ev(f"{int(r.n_rows):,}", E, "Table 8"),
                        ev(m(f"{r.rmse_base:{unitfmt[r.outcome]}} → {r.rmse_aug:{unitfmt[r.outcome]}}"), E, "Table 8"),
                        pct(r.delta_pct, r.ci_low_pct, r.ci_high_pct, 2, E, "Table 8"),
                        ev(m(f"{D.seas.loc[seas_key[(r.target, r.outcome)], 't4_low']:+.2f} to {D.seas.loc[seas_key[(r.target, r.outcome)], 't4_high']:+.2f}"), S["seas"], "Table 8"),
                        ev(f"{int(r.years_improved)}/5", E, "Table 8"), ev(f"{r.p_adjusted:.3f}", E, "Table 8"), r.verdict]
                       for _, r in pr.iterrows()],
                      columns=["Pre-specified linkage", "n", "RMSE, baseline → with forecast (category units)", "ΔRMSE % [player-cluster 95% CI]",
                               "Season-level t(4) interval (post hoc)", "Seasons improved", "Holm p", "Verdict (player-level)"])
    b.table(t6, "Primary fantasy linkages, outcome seasons 2021–2025 pooled, identical players. RMSE is in each category's own units (home runs, stolen bases, batting "
            "average, ERA, WHIP, z-score value). Holm p = 0.008 is the smallest value the 2,000-draw bootstrap can produce. The season-level interval treats the five season "
            "estimates as the units, so it shows how far the result generalizes beyond these seasons.", widths=[1.35, 0.45, 0.95, 1.0, 0.8, 0.55, 0.45, 0.85], font=13)
    b.para(
        f"Only the FIP forecast passed at the player level (Table 8; Figure 6). Adding it to the category-history model lowered ERA forecast error from "
        f"{num(era_fip.rmse_base, '.3f', E, '8.3')} to {num(era_fip.rmse_aug, '.3f', E, '8.3')} earned runs per nine innings ({D.Fp(Pi, 'ERA', TF, 'fip', sec='8.3')}), and "
        f"WHIP error from {num(whip_fip.rmse_base, '.4f', E, '8.3')} to {num(whip_fip.rmse_aug, '.4f', E, '8.3')} ({D.Fp(Pi, 'WHIP', TF, 'fip', sec='8.3')}). On the full "
        f"pool, including pitchers who did not return, it also improved pitcher 5×5 value ({D.Fp(Pi, 'VAL_P', TF, 'fip', sec='8.3')}; secondary). Two cautions follow from "
        "the season-by-season view:")
    b.bullets([
        "both ERA and WHIP improved in four of five seasons and reversed in 2023, the season of the pitch timer and the shift ban;",
        f"treating the five seasons as the units, the intervals include zero (ERA {D.SEAS('fantasy primary: fip -> ERA', '8.3')}; WHIP "
        f"{D.SEAS('fantasy primary: fip -> WHIP', '8.3')}).",
    ])
    b.para(
        "The evidence therefore says that fielding-independent skill improved ERA and WHIP forecasts for players within 2021–2025, by about 1% of forecast error. Whether that "
        "carries into a new season is less certain. Removing each season's average error does not erase the gain (post hoc: "
        f"{num(D.within.loc['fantasy: fip -> ERA', 'within_season_pct'], '+.2f', S['within'], '8.3')}% for ERA).")
    b.para("The other primary linkages showed no gain that survived adjustment at the player level:")
    b.bullets([
        f"the wOBA forecast improved HR forecasts in all five seasons, but the pooled player-level interval included zero ({D.Fp(H, 'HR', TF, 'woba', nd=2, sec='8.3')}); "
        f"at the season level it is the only primary linkage whose interval excludes zero ({D.SEAS('fantasy primary: woba -> HR', '8.3')}), so the two views disagree;",
        f"wOBA → AVG: {D.Fp(H, 'AVG', TF, 'woba', nd=2, sec='8.3')};",
        f"the baserunning forecast added nothing to stolen-base forecasts ({D.Fp(H, 'SB', TF, 'br', nd=2, sec='8.3')});",
        f"the fielding forecast added nothing to hitter value ({D.Fp(H, 'VAL_H', TF, 'fld', nd=2, sec='8.3')}), as a boundary case should;",
        f"hitter WAR → value: {D.Fp(H, 'VAL_H', TF, 'hwar', nd=2, sec='8.3')}, an interval that excludes zero but does not survive Holm adjustment;",
        f"pitcher WAR → value: {D.Fp(Pi, 'VAL_P', TF, 'pwar', nd=2, sec='8.3')}.",
    ])
    b.para(
        f"In baseball terms these are small changes: the HR forecast error moved from {num(hr_woba.rmse_base, '.2f', E, '8.3')} to {num(hr_woba.rmse_aug, '.2f', E, '8.3')} home runs "
        "per player-season, less than a tenth of a home run.")
    b.figure("fig6_fantasy_linkage.png",
             "Which target forecasts add information about which fantasy categories. Each cell is the change in out-of-time forecast error for a fantasy category when one target "
             "forecast is added to the direct category-history baseline (outcome seasons 2021–2025 pooled; identical players; n = 1,506–2,115 per cell, 1,666 for fielding). "
             "Marker: verdict after multiplicity adjustment. Bold outline: the eight pre-specified primary linkages.")
    b.h2("8.4 What does carry information, and through which channel")
    b.para("Four secondary findings sharpen the picture. They are exploratory; the paired comparisons marked post hoc were added after the internal review.")
    b.bullets([
        f"**Raw sprint speed carried stolen-base information that the baserunning forecast did not.** Added directly to the category model, sprint speed improved stolen-base "
        f"forecasts ({D.Fp(H, 'SB', DM, 'sprint_speed', nd=2, sec='8.4')}, {int(sb_sp.years_improved)} of 5 seasons), and in a direct paired comparison it beat the "
        f"baserunning forecast ({D.DIRECT('BF+sprint_speed vs BF+br (SB)', sec='8.4')}, post hoc). The baserunning target measures run value per time on base, including "
        "advancement and outs on the bases, which is a different quantity from stolen-base volume.",
        f"**Power metrics helped HR forecasts.** Barrel% ({D.Fp(H, 'HR', DM, 'barrel_pct', nd=2, sec='8.4')}), exit velocity ({D.DIRECT('ev -> HR', sec='8.4')}, post hoc) "
        f"and two-year xwOBA ({D.Fp(H, 'HR', DM, 'xwoba_w2', nd=2, sec='8.4')}) each improved HR forecasts. Two-year xwOBA and the wOBA forecast did no better than each "
        f"other ({D.DIRECT('BF+xwoba_w2 vs BF+woba (HR)', sec='8.4')}, post hoc). The in-house Stuff+, K% and K-BB% added nothing to strikeout totals, strikeout rate per "
        f"nine innings ({D.DIRECT('stuff_plus -> K9', sec='8.4')} for Stuff+, post hoc), ERA or WHIP beyond the category history.",
        f"**The admitted metrics travel through the target forecast.** Replacing a history-only target forecast with the admitted one improved several category forecasts, "
        f"for example ERA ({D.Fp(Pi, 'ERA', AV, 'fip', sec='8.4')}), WHIP ({D.Fp(Pi, 'WHIP', AV, 'fip', sec='8.4')}) and runs ({D.Fp(H, 'R', AV, 'woba', sec='8.4')}): "
        "the admitted metrics carry some fantasy information beyond two-year history. One comparison went the other way (hitter WAR, AVG: "
        f"{D.Fp(H, 'AVG', AV, 'hwar', nd=2, sec='8.4')}).",
        f"**WAR forecasts mostly carry playing time.** The hitter WAR forecast improved at-bat forecasts ({D.Fp(H, 'AB', TF, 'hwar', sec='8.4')}) more than any rate "
        f"category. All target forecasts together improved AVG ({D.Fp(H, 'AVG', JT, 'woba+br+hwar', sec='8.4')}) and pitcher 5×5 value "
        f"({D.Fp(Pi, 'VAL_P', JT, 'fip+pwar', sec='8.4')}).",
    ])
    b.para(
        f"In 2026 none of the eight primary linkages had an interval excluding zero (for example FIP → ERA {D.Fp(Pi, 'ERA', TF, 'fip', '2026', nd=2, sec='8.4')} and "
        f"wOBA → HR {D.Fp(H, 'HR', TF, 'woba', '2026', nd=2, sec='8.4')}). Among the 132 secondary comparisons, {ev(str(n26_gain), S['fr'], '8.4')} favored the forecasts "
        "with intervals excluding zero. About 3 would be expected by chance if no forecast helped, but the comparisons share players and inputs, so they are "
        "not independent and the excess is weak evidence. The one harmful comparison from 2021–2025 (hitter WAR, AVG) was harmful again "
        f"({D.Fp(H, 'AVG', AV, 'hwar', '2026', nd=2, sec='8.4')}). One season of roughly 300–400 players has little power, and 2026 had already been inspected, so these rows "
        "are exploratory.")
    b.h2("8.5 Does it change a draft? An illustrative backtest")
    dsd = D.draft.dropna(subset=["k"])
    sd_h, sd_p = dsd[dsd.group == "hitter"].realized_value_sd.iloc[0], dsd[dsd.group == "pitcher"].realized_value_sd.iloc[0]
    yh = dsd[(dsd.group == "hitter") & (dsd.k == 120)].iloc[0]
    yp = dsd[(dsd.group == "pitcher") & (dsd.k == 96)].iloc[0]
    ovh = dsd[dsd.group == "hitter"].mean_overlap_base_vs_aug
    ov_txt = f"{100 * ovh.min():.0f}–{100 * ovh.max():.0f}%"
    b.para(
        "Better category forecasts do not automatically mean better picks. In each season the forecast-date pool was ranked by predicted 5×5 value and the top k players were "
        "taken. The realized value of the players chosen by the baseline models was compared with that of the players chosen by models that also used the target forecasts. "
        "This measures the ranking of the whole pool, not one manager's edge over a consensus draft. The protocol fixed k = 156 hitters and 108 pitchers; the post hoc "
        "analysis adds Yahoo's default active roster (12 teams × 10 hitters and 8 pitchers) and the NFBC Main Event (15 teams × 14 and 9). Findings:")
    b.bullets([
        f"rank agreement with realized value improved for hitters (Spearman ρ {num(rho_h_b, '.3f', S['rv'], '8.5')} → {num(rho_h_a, '.3f', S['rv'], '8.5')}) and pitchers "
        f"({num(rho_p_b, '.3f', S['rv'], '8.5')} → {num(rho_p_a, '.3f', S['rv'], '8.5')}), with intervals for the differences excluding zero;",
        f"the players actually picked were not detectably better at any roster size. For a 12-team Yahoo roster, the difference was "
        f"{ev(m(f'{yh.delta_mean_value_per_pick:+.2f} [{yh.ci_low:+.2f}, {yh.ci_high:+.2f}]'), S['draft'], '8.5')} z-units per hitter and "
        f"{ev(m(f'{yp.delta_mean_value_per_pick:+.2f} [{yp.ci_low:+.2f}, {yp.ci_high:+.2f}]'), S['draft'], '8.5')} per pitcher. The realized value has an SD of "
        f"{num(sd_h, '.1f', S['draft'], '8.5')} (hitters) and {num(sd_p, '.1f', S['draft'], '8.5')} (pitchers), so these are under 0.02 SD per pick;",
        f"the two rankings shared {ev(m(ov_txt), S['draft'], '8.5')} "
        "of their top-k hitters. The median rank change was about one place in the top 12 and grew to roughly 10–16 places beyond the top 50: the target forecasts mostly "
        "reorder the middle and bottom of the pool;",
        "the pre-specified top-k overlap with the realized top-k changed by about one point, and the points-league version showed no detectable gain either.",
    ])
    b.para(
        "The backtest ignores average draft position, positions, snake order and in-season management, so it is a what-if illustration, not evidence about winning leagues.")
    b.figure("fig7_draft_backtest.png",
             "Illustrative draft backtest. A–B: rank agreement between predicted and realized 5×5 value for the category-history models (dashed) and for models that also use the "
             "target forecasts (solid), by season (2026 exploratory). C: difference in the mean realized value of the top-k players picked by each ranking, pooled 2021–2025, "
             "with 95% intervals from resampling players; positive favors the augmented ranking; z-units (realized-value SD ≈ 3.8 hitters, 3.2 pitchers).")

    # ================================================================== 9 ERA
    b.h1("9. A new target: does the procedure generalize to ERA?")
    b.para(
        "Earlier alternative-target analyses reused metric sets selected for the original targets. That is transfer, not a test of whether the procedure can choose metrics for "
        "a new target. As a direct test, specified in a dated protocol amendment before it was run, the full nested admission was applied to next-season **ERA**, a fantasy "
        "category, using the FIP study's pitchers, an ERA-history baseline and the unchanged candidate catalog. The procedure selected "
        f"{ev(m(f'{era_sel.min()}–{era_sel.max()}'), S['erasets'], '9')} metrics per window: strikeout rate, K-BB%, zone-contact rate, called-strike-plus-whiff or whiff rate, "
        "fastball velocity, spin, platoon K-BB%, exit velocity allowed (2021 only) and, from 2022, Stuff+. Two- and three-year FIP were never admitted beyond ERA history. "
        "Results on 2021–2025, on identical rows (each comparison is the first-named model minus the second; negative favors the first):")
    b.bullets([
        f"ERA-specific selection beat the ERA-history baseline ({D.ERA('ERA-ADM vs B0', sec='9')});",
        f"so did simply reusing the FIP study's selections ({D.ERA('TRANSFER vs B0', sec='9')});",
        f"the ERA-specific set was no better than the reused set ({D.ERA('ERA-ADM vs TRANSFER', sec='9')});",
        f"an all-metric ridge model was worse than the ERA-specific set ({D.ERA('KS ridge vs ERA-ADM', sec='9')}), and a tuned elastic net showed no detectable difference ({D.ERA('KS elastic net vs ERA-ADM', sec='9')}).",
    ])
    b.para(
        "The procedure selected sensible metrics for a closely related new target, but re-selection did not beat reusing the FIP selections. The supported portability claim "
        "is therefore narrow: between closely related targets, selections transfer.")

    # ================================================================== 10 Discussion
    b.h1("10. Discussion")
    b.h2("10.1 How a public reader should use these results")
    b.para(
        "A metric's job depends on the forecast. For a fantasy manager, that implies four working rules:")
    b.bullets([
        "**Prefer category-matched evidence.** Sprint speed for steals, and Barrel%, exit velocity or xwOBA for home runs, carried information beyond category history; the baserunning run-value forecast did not carry it for steals.",
        "**For pitchers, give strikeout and run-prevention skill modest extra weight in ERA and WHIP forecasts.** The FIP forecast improved them by about 1% within 2021–2025, though not in every season.",
        "**Treat WAR as a measure of value, not fantasy value.** Its forecast mostly signals playing time.",
        "**Do not expect skill metrics to reshape the top of a draft.** In the backtest, adding the target forecasts left 91–96% of the top picks unchanged; playing time itself was not modeled separately.",
    ])
    b.para("None of these results promise more wins in any particular league.")
    b.h2("10.2 Where fantasy conventional wisdom agrees and disagrees with the evidence")
    from section3 import discussion_audit  # noqa: E402
    discussion_audit(b, D)
    b.h2("10.3 Target, model and era conditionality")
    b.para(
        "Every result here is conditional on the target, the baseline, the population, the estimator and the seasons. The same metric changes role across targets: sprint "
        "speed is admitted for baserunning and labelled Diagnostic for wOBA. The advantage of selection over an all-metric ridge model faded as training seasons accumulated, "
        "a tuned elastic net showed no detectable difference from selection (and beat it for FIP in one sensitivity analysis), and broad models won for aggregate targets. A defensible reading is that selection helps most where signal is concentrated in "
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
        "**A weak baseline.** The baseline holds two seasons of history, age, playing time and run environment. A third season of the target's own history, which a naive Marcel-style projection would include, was a candidate rather than part of the baseline; Table 5 separates its contribution. For fielding it accounts for the whole gain. A full Marcel-style baseline was not run.",
        "**Selection on the evaluation years.** Nested selection removes it; its effect was at most about half a percent of RMSE.",
        "**Multiplicity.** Primary families are Holm-adjusted and secondary families BH-adjusted. All of it is exploratory relative to earlier looks at these seasons.",
        f"**Season effects and era changes.** Player-cluster intervals describe players within 2021–2025. Season-level variation is larger, and some verdicts weaken at that level (Section 8.3) {c('cameron')}. The 2020 season was 60 games; counts are prorated in the fantasy analysis. The 2023 changes (pitch timer, pickoff limits, larger bases, the end of the infield shift) changed the stolen-base and batting-average environment, and 2021–2022 saw large swings in league run scoring.",
        "**Survivorship.** Outcome-observed populations exclude players who lost their jobs, which can bias player-level comparisons (Section 7). The fantasy pools keep them, but rookies remain outside the study.",
    ])

    # ================================================================== 11 Limitations
    b.h1("11. Limitations and future work")
    b.bullets([
        "**No prospective test yet.** The 2026 check was frozen within the workflow but evaluated after the season. A genuinely prospective test would freeze 2027 forecasts and the protocol before Opening Day 2027.",
        "**Exploratory fantasy evidence.** The fantasy bridge was pre-specified, but the seasons were not new. Its decision backtest is illustrative: no average draft position, positions, roster rules or in-season moves.",
        "**Narrow populations.** Rookies and sub-threshold players are excluded. Ratio categories are conditional on playing.",
        "**Human-specified labels.** The role flags, process flags and family definitions are human choices. Different, defensible choices would change some Diagnostic/Exclude/Context labels and, through the family step, some admissions.",
        "**Particular metric versions.** Stuff+ is this study's own model (fitted on seasons up to and including t), and WAR is Baseball-Reference's. Results may differ for FanGraphs' versions.",
        "**Untested model families.** Admission was not re-run inside non-linear models, and no archived third-party projections (Steamer, ZiPS, ATC, THE BAT X) served as baselines, because they are not lawfully available to the study.",
        "**Future work:**"
        " richer public inputs (pitch-level and bat-tracking data);"
        " playing-time and injury models;"
        " position- and average-draft-position-aware valuation;"
        " a frozen, prospective 2027 evaluation.",
    ])
    b.h1("12. Conclusion")
    b.para(
        "One statistic can do different jobs, and asking which job it does before letting it change a forecast is a check that public analysts can run with public data. In "
        "this study the check admitted sprint speed for baserunning but not for batting, and strikeout and pitch-quality metrics for FIP. It credited fielding's gain to "
        "nothing more than a third season of history. For fantasy play, only the FIP forecast carried detectable extra information about the categories managers score, and "
        "even that was modest and uneven across seasons. The value of the procedure lies as much in what it declines to promote, and in the failures it shows, as in what it admits.")
    # ================================================================== Appendices
    b.unnumbered("Appendix A. The accepted abstract and what changed", page_break=True)
    b.para("The abstract accepted for the full-paper stage is preserved verbatim below as the historical record. Table 9 lists each of its claims next to the evidence in "
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
        ["\"For baseball operations, this framework provides a reproducible way to decide…\"; \"important for baseball decision systems\"", "Public single-number metrics are insufficient for front-office decisions (Section 10.4)", "Withdrawn; application reframed to public analysts and fantasy"],
        ["Temporal stability as an evaluation criterion", "Feature reliability is reported but never gates (Table 4)", "Qualified"],
        ["Headline results from seven expanding folds", "Metrics were chosen on the same seasons used to report accuracy; nested selection removes this (≤0.53% of RMSE)", "Qualified"],
        ["Selective vs kitchen-sink comparison", "Original FIP errors used different rows (1,699 vs 1,866); the hitting selective list was chosen after results were known (Section 6.1)", "Qualified; replaced by identical-row comparisons"],
        ["\"Strong history-aware ridge-regression baseline\"", "The baseline holds two seasons; a third season of history was later admitted for wOBA, baserunning and fielding (Table 5)", "Qualified"],
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
        repo_sentence = ("Code, aggregate results, figure data, checksums and the web application are in public repositories whose links are given in the submission form "
                         f"{c('repo')}. Commit identifiers are withheld here for review.")
    else:
        repo_sentence = (f"Code, aggregate results, figure data, checksums and the web application are public {c('repo')}; the canonical study is commit 17da742. An earlier "
                         f"version is available as a preprint {c('preprint')}.")
    b.para(
        repo_sentence + " The canonical study and the November 2026 reanalysis were re-run on 2026-11-13: 71 automated tests passed and 55 of 55 reproduction checks matched. "
        "All 873 files of the immutable baseline were byte-identical to their recorded SHA-256 values. The fantasy-bridge protocol and its first amendment were pushed before "
        "the corresponding models were fit; a second amendment records the post hoc analyses. Raw MLB Advanced Media and Baseball-Reference tables and player-season panels "
        "are not redistributed because their terms restrict redistribution; the repositories contain scripts that rebuild them, with checksums that verify a rebuild. The "
        "Baseball-Reference WAR files reflect that site's methodology at download time; Sports Reference revises historical fielding inputs from time to time "
        f"{c('bref_update2025')}.", size=20)
    b.unnumbered("Appendix D. Full fantasy-linkage results")
    b.para(
        "The complete target × category matrix, covering all comparison types, both samples, per-season values, season-block intervals and multiplicity adjustments, is in "
        "`fantasy/results_by_target_category.csv`, `fantasy/by_year.csv` and `fantasy/paired_uncertainty.csv`. The same results can be browsed in the web application's "
        f"Fantasy Linkage Explorer. Of the {ev(str(int((D.fr['sample'].str.startswith('2021')).sum())), S['fr'], 'D')} pooled 2021–2025 comparisons, "
        f"{ev(str(int(((D.fr['sample'].str.startswith('2021')) & (D.fr.verdict == 'adds information')).sum())), S['fr'], 'D')} met the adds-information criterion, "
        f"{ev(str(int(((D.fr['sample'].str.startswith('2021')) & (D.fr.verdict == 'harmful')).sum())), S['fr'], 'D')} was harmful (hitter WAR, AVG), and the rest showed no detectable or "
        "no multiplicity-robust gain.", size=20)
    b.unnumbered("Appendix E. Gate ablations and feature families")
    ab = D.abl.copy()
    ab.columns = ["Variant", "Targets whose selection changed", "Targets whose error changed (CI excludes 0; target units)", "Mean Jaccard similarity to default"]
    ab["Variant"] = ab["Variant"].str.replace("abl_no_", "remove ", regex=False).str.replace("thr_", "threshold ", regex=False).str.replace("default|", "admission ridge ", regex=False)
    b.table(ab, "Every one-at-a-time ablation of the nested selection (outer seasons 2021–2025). Error changes are in each target's own units; positive = worse than the default.",
            widths=[1.2, 2.2, 2.3, 0.8], font=12, keep_together=False)
    fams = families()
    b.table(pd.DataFrame(fams, columns=["Player type", "Family", "Members"]), "Human-defined feature families used by the redundancy step.", widths=[0.8, 1.2, 4.5], font=12, keep_together=False)
    b.references(bibliography(blind))
    return b



def families():
    import sys as _s
    _s.path.insert(0, str(D.PSL_ROOT / "src"))
    from psl.catalog import HITTER_FAMILIES, PITCHER_FAMILIES
    out = []
    for ptype, fam in (("Hitter", HITTER_FAMILIES), ("Pitcher", PITCHER_FAMILIES)):
        for k, v in fam.items():
            out.append([ptype, k.replace("_", " "), ", ".join(v)])
    return out


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
