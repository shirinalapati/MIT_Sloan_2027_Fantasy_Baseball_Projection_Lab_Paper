"""Artifact loading and value getters for the manuscript text. Each getter logs the printed value and its source."""
from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from build_manuscript import PSL_ROOT, REPO, ev, m, num, pct

S27 = PSL_ROOT / "sloan2027"
FAN = REPO / "sloan2027_fantasy" / "fantasy"
FIGD = REPO / "sloan2027_fantasy" / "figures" / "data"

SRC = {"t2": "sloan2027/tables/table2_nested_and_2026_model_comparison.csv", "t3": "sloan2027/tables/table3_flagship_contrasts.csv",
       "t4": "sloan2027/tables/table4_2026_cohort_attrition.csv", "gate": "sloan2027/results/gates/gate_variant_summary.csv",
       "mult": "sloan2027/results/multiplicity/summary.json", "units": "sloan2027/results/players/unit_translation.csv",
       "coh": "sloan2027/results/players/cohort_effects.csv", "nest": "sloan2027/results/nested/comparisons_default.csv",
       "c26": "sloan2027/results/holdout2026/comparisons_2026.csv", "plac": "sloan2027/results/placebo/placebo_verdicts.csv",
       "repro": "sloan2027/00_reproduction_diff.csv", "lv": "sloan2027/audits/e2_label_validation_2025.csv",
       "fetch": "sloan2027/results/holdout2026/fetch_log_2026.json", "meta": "sloan2027/results/nested/admission/*_default_meta.json",
       "canon": "artifacts/admission_*.parquet (canonical commit 17da742)", "reason": "sloan2027/tables/table7b_reason_code_counts.csv",
       "fr": "sloan2027_fantasy/fantasy/results_by_target_category.csv", "l1": "sloan2027_fantasy/fantasy/level1_correlations.csv",
       "cb": "sloan2027_fantasy/fantasy/cohort_by_year.csv", "rv": "sloan2027_fantasy/fantasy/ranking_value_sensitivity.csv",
       "bt": "sloan2027_fantasy/fantasy/decision_backtest.csv", "era": "sloan2027_fantasy/fantasy/generalization_era/comparisons.csv",
       "erasets": "sloan2027_fantasy/fantasy/generalization_era/selected_sets.csv", "cases": "sloan2027_fantasy/figures/data/fig5_cases.csv",
       "fig1": "sloan2027_fantasy/figures/data/fig1_sprint_speed_examples.csv", "up": "sloan2027_fantasy/audits/fb_upstream_consistency.csv",
       "dec": "sloan2027_fantasy/figures/data/fig5_stuff_deciles.csv", "pop": "sloan2027/audits/kitchen_sink_population_check.csv",
       "eval": "app/public/data/evaluations.json (exported from canonical artifacts)"}

t2 = pd.read_csv(S27 / "tables/table2_nested_and_2026_model_comparison.csv").set_index("Target")
t3 = pd.read_csv(S27 / "tables/table3_flagship_contrasts.csv").set_index("Hypothesis")
t4 = pd.read_csv(S27 / "tables/table4_2026_cohort_attrition.csv").set_index("study_id")
gate = pd.read_csv(S27 / "tables/table5_gate_ablation_threshold_sensitivity.csv").set_index("Variant")
mult = json.loads((S27 / "results/multiplicity/summary.json").read_text())
units = pd.read_csv(S27 / "results/players/unit_translation.csv").set_index("contrast")
coh = pd.read_csv(S27 / "results/players/cohort_effects.csv")
nest = pd.read_csv(S27 / "results/nested/comparisons_default.csv")
c26 = pd.read_csv(S27 / "results/holdout2026/comparisons_2026.csv")
plac = pd.read_csv(S27 / "results/placebo/placebo_verdicts.csv")
repro = pd.read_csv(S27 / "00_reproduction_diff.csv")
lv = pd.read_csv(S27 / "audits/e2_label_validation_2025.csv")
fetch = json.loads((S27 / "results/holdout2026/fetch_log_2026.json").read_text())
reason = pd.read_csv(S27 / "tables/table7b_reason_code_counts.csv").set_index("reason_code")["rows"]
popchk = pd.read_csv(S27 / "audits/kitchen_sink_population_check.csv").set_index("study")
STUDIES = ["hitting_woba", "pitching_fip", "baserunning_rv", "defense_rv", "overall_war", "pitcher_war"]
metas = {(s, T): json.loads((S27 / f"results/nested/admission/{s}_T{T}_default_meta.json").read_text()) for s in STUDIES for T in range(2021, 2027)}
evals = json.loads((REPO / "app/public/data/evaluations.json").read_text())
fr = pd.read_csv(FAN / "results_by_target_category.csv")
l1 = pd.read_csv(FAN / "level1_correlations.csv")
cb = pd.read_csv(FAN / "cohort_by_year.csv")
rv = pd.read_csv(FAN / "ranking_value_sensitivity.csv")
bt = pd.read_csv(FAN / "decision_backtest.csv")
era = pd.read_csv(FAN / "generalization_era/comparisons.csv").set_index("comparison")
erasets = pd.read_csv(FAN / "generalization_era/selected_sets.csv")
cases = pd.read_csv(FIGD / "fig5_cases.csv")
fig1 = pd.read_csv(FIGD / "fig1_sprint_speed_examples.csv").set_index("target")
dec = pd.read_csv(FIGD / "fig5_stuff_deciles.csv")
upc = pd.read_csv(REPO / "sloan2027_fantasy/audits/fb_upstream_consistency.csv")

TL = {"hitting_woba": "wOBA", "pitching_fip": "FIP", "baserunning_rv": "Baserunning rate", "defense_rv": "Fielding rate",
      "overall_war": "Hitter bWAR/600 PA", "pitcher_war": "Pitcher bWAR/200 IP"}


def tri(s: str):
    v = [float(x) for x in re.findall(r"[-+]?\d+\.\d+", str(s))]
    return v[0], v[1], v[2]


def T2(sid: str, col: str, nd: int = 1, sec: str = "") -> str:
    p, lo, hi = tri(t2.loc[TL[sid], col])
    return pct(p, lo, hi, nd, SRC["t2"], sec)


def T2v(sid: str, col: str):
    return tri(t2.loc[TL[sid], col])


def T3(h: str, col: str, nd: int = 2, sec: str = "") -> str:
    p, lo, hi = tri(t3.loc[h, col])
    return pct(p, lo, hi, nd, SRC["t3"], sec)


def F(group, outcome, kind, target, sample="2021"):
    r = fr[(fr.group == group) & (fr.outcome == outcome) & (fr.kind == kind) & (fr.target == target) & fr["sample"].str.startswith(sample)]
    if len(r) != 1:
        raise KeyError((group, outcome, kind, target, sample, len(r)))
    return r.iloc[0]


def Fp(group, outcome, kind, target, sample="2021", nd=1, sec="") -> str:
    r = F(group, outcome, kind, target, sample)
    return pct(r.delta_pct, r.ci_low_pct, r.ci_high_pct, nd, SRC["fr"], sec)


def L1(target, outcome, sec="") -> str:
    r = l1[(l1.target_forecast == target) & (l1.fantasy_outcome == outcome)].iloc[0]
    return ev(m(f"{r.spearman_2021_2025:.2f} [{r.ci_low:.2f}, {r.ci_high:.2f}]"), SRC["l1"], sec)


def C26(sid: str, comp: str, cohort="retrospective"):
    r = c26[(c26.study_id == sid) & (c26.comparison == comp) & c26.cohort.str.startswith(cohort)].iloc[0]
    rb = r.delta_rmse / (r.pct_of_b / 100)
    return r.pct_of_b, 100 * r.ci_low / rb, 100 * r.ci_high / rb


def C26p(sid, comp, nd=1, sec="", cohort="retrospective") -> str:
    p, lo, hi = C26(sid, comp, cohort)
    return pct(p, lo, hi, nd, SRC["c26"], sec)


def CO(contrast, cohort, col):
    return coh[(coh.contrast == contrast) & (coh.cohort == cohort)].iloc[0][col]


def EV(metric, target):
    for e in evals:
        if e["metric"] == metric and e["target"] == target:
            return e
    raise KeyError((metric, target))


def ERA(comp, nd=1, sec="") -> str:
    r = era.loc[comp]
    return pct(r.delta_pct, r.ci_low_pct, r.ci_high_pct, nd, SRC["era"], sec)


def RV(group, k, col, sample="2021"):
    r = rv[(rv.group == group) & (rv.format == "roto_5x5") & (rv.k == k) & rv["sample"].str.startswith(sample)]
    return r.iloc[0][col]


# derived facts used in several places
FIXADM_MAX = float(nest[nest.comparison.str.startswith("FIX vs ADM")].pct_of_b.abs().max())
N_PLAC = len(plac)
N_PLAC_ADMIT = int(plac.verdict.isin(["Projection", "Augmented Projection"]).sum())
N_REPRO = len(repro)
N_REPRO_MATCH = int((repro.status == "match").sum())
LAB_N = int(lv["sample_rows_Y-1"].sum())
LAB_OK = int(lv["exact_match(|d|<1e-9)"].sum())
VERDICTS = pd.Series([e["verdict"] for e in evals]).value_counts().to_dict()
UP_MAXDIFF = float(upc.max_abs_diff.max())
POOL = cb[cb.outcome_season.between(2021, 2025)].groupby("player_group").pool_size.sum().to_dict()
ZERO = cb[cb.outcome_season.between(2021, 2025)].groupby("player_group").share_zero_counting_outcome.agg(["min", "max"]).to_dict("index")
CANON_T1 = cb[cb.outcome_season.between(2021, 2025)].groupby("player_group")["share_meeting_canonical_t+1_rule"].agg(["min", "max"]).to_dict("index")

# largest Stuff+ adjustments (player-level file read locally; only aggregate statements are printed)
_fc = pd.read_parquet(S27 / "results/players/forecast_changes.parquet")
_st = _fc[_fc.contrast == "pitching_fip:stuff_plus"].assign(absch=lambda x: x.change.abs())
_top6 = _st.nlargest(6, "absch")
LARGEST6_WORSE = int((_top6.abs_err_change > 0).sum())
LARGEST6_ROGERS = int((_top6.player == "Rogers, Tyler").sum())
SRC["fc"] = "sloan2027/results/players/forecast_changes.parquet (aggregate statement only)"
