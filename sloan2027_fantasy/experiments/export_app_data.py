"""Export audited research artifacts to the fantasy web app's static data (app/public/data/*.json).

Every number in the app comes from a file listed in data/manifest.json (path + sha256 of the source artifact).
No values are computed for display that are not in an audited artifact, except unit conversions recorded here
(ΔRMSE as % of the reference model's RMSE, which the source files also report).

Player-level content is a CURATED casebook (largest increases, largest decreases, and a seeded random sample per
contrast) rather than the full prediction file, to limit redistribution of MLBAM-derived player data.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import fb_lib as F

APP = F.REPO / "app" / "public" / "data"
APP.mkdir(parents=True, exist_ok=True)
CANON = F.PSL_ROOT / "artifacts"
S27 = F.PSL_ROOT / "sloan2027"
SOURCES: dict[str, str] = {}

STUDY_FILE = {"hitting_woba": "admission_hitting_y_woba", "pitching_fip": "admission_pitching_y_fip", "baserunning_rv": "admission_baserunning_y_br_rv_rate",
              "defense_rv": "admission_defense_y_def_rv_rate", "overall_war": "admission_overall_y_war_rate", "pitcher_war": "admission_pitcher_overall_y_war_rate"}
TARGETS = [
    {"id": "hitting_woba", "short": "wOBA", "label": "Next-season wOBA", "group": "hitter", "unit": "wOBA points (0.001 = 1 point)",
     "definition": "Weighted on-base average in season t+1: each way of reaching base is weighted by its average run value, scaled like on-base percentage.",
     "denominator": "per plate appearance", "eligibility": "≥150 PA in season t and in season t+1", "weight": "PA",
     "baseline": "age, PA, two-year PA-weighted wOBA, park factor",
     "why": "Tests whether hitting-process metrics (expected stats, exit velocity, plate discipline) add to a hitter's own two-year wOBA.",
     "fantasy_link": "Offensive rate skill that plausibly relates to AVG, HR, R and RBI and to points-league batting scores.",
     "not_established": "Not a fantasy category; ignores playing time, lineup slot, team context and stolen bases; no AVG/HR/R/RBI projection by itself."},
    {"id": "pitching_fip", "short": "FIP", "label": "Next-season FIP", "group": "pitcher", "unit": "runs per 9 innings (FIP scale)",
     "definition": "Fielding Independent Pitching in season t+1: (13·HR + 3·(BB+HBP) − 2·K)/IP plus a league constant; it ignores balls in play.",
     "denominator": "per inning pitched", "eligibility": "≥80 IP (starters) or ≥30 IP (relievers) in t and t+1 (25/10 in 2020)", "weight": "IP",
     "baseline": "age, IP, starter role, two-year FIP, park factor",
     "why": "Tests pitch-quality and plate-discipline metrics against the part of run prevention a pitcher controls most directly.",
     "fantasy_link": "Strikeout, walk and home-run skill that plausibly relates to ERA, WHIP and K.",
     "not_established": "Not ERA, WHIP, wins, saves or innings; excludes balls in play, sequencing and defense."},
    {"id": "baserunning_rv", "short": "Baserunning", "label": "Next-season baserunning run-value rate", "group": "hitter", "unit": "Baseball-Reference baserunning runs per 100 times on base",
     "definition": "Baseball-Reference baserunning runs (runs_br) in t+1 per 100 times on base (H + BB + HBP − HR); per 600 PA if fewer than 20 times on base.",
     "denominator": "per 100 times on base", "eligibility": "≥150 PA in t and t+1", "weight": "PA",
     "baseline": "age, PA, two-year baserunning rate, park factor",
     "why": "A running-only component target: tests speed and running metrics where they should matter most.",
     "fantasy_link": "Running value is related to, but not the same as, stolen bases.",
     "not_established": "Not SB, SB attempts or success; a rate, so it ignores playing time and team green-light decisions."},
    {"id": "defense_rv", "short": "Fielding", "label": "Next-season fielding run-value rate", "group": "hitter", "unit": "Baseball-Reference fielding + catcher runs per 1,000 defensive innings",
     "definition": "Baseball-Reference runs_field + runs_catcher in t+1 per 1,000 defensive innings.",
     "denominator": "per 1,000 defensive innings", "eligibility": "≥200 defensive innings in t and t+1", "weight": "defensive innings",
     "baseline": "age, defensive innings, position group, two-year fielding rate",
     "why": "A non-batting component and deliberate boundary case: defense is part of player value but not of standard fantasy scoring.",
     "fantasy_link": "None directly; any link would run through playing time (good fielders may keep their jobs).",
     "not_established": "Not a fantasy category in standard 5×5 or points formats; no evidence it improves fantasy returns."},
    {"id": "overall_war", "short": "Hitter bWAR", "label": "Next-season hitter bWAR per 600 PA", "group": "hitter", "unit": "Baseball-Reference wins above replacement per 600 PA",
     "definition": "Baseball-Reference position-player WAR in t+1 scaled to 600 plate appearances.",
     "denominator": "per 600 PA", "eligibility": "≥150 PA in t and t+1", "weight": "PA",
     "baseline": "age, PA, two-year WAR rate, park factor",
     "why": "An aggregate target combining batting, running, fielding and positional value: tests whether component signals survive aggregation.",
     "fantasy_link": "Broad skill proxy; fantasy formats do not score defense, position or replacement level the way WAR does.",
     "not_established": "Not fantasy points or roto value; bWAR differs from FanGraphs fWAR."},
    {"id": "pitcher_war", "short": "Pitcher bWAR", "label": "Next-season pitcher bWAR per 200 IP", "group": "pitcher", "unit": "Baseball-Reference wins above replacement per 200 IP",
     "definition": "Baseball-Reference pitcher WAR in t+1 scaled to 200 innings (runs-allowed based, adjusted for defense and park).",
     "denominator": "per 200 IP", "eligibility": "pitchers with a season-t and season-t+1 record (no workload floor)", "weight": "IP",
     "baseline": "age, IP, starter role, two-year WAR rate, park factor",
     "why": "An aggregate pitching-value stress test with a noisy, runs-allowed-based outcome.",
     "fantasy_link": "Broad pitching quality; not wins, saves or innings.",
     "not_established": "Not fantasy points or roto value; bWAR's runs-allowed basis differs from FanGraphs' FIP-based pitcher WAR."},
]


def src(path: Path) -> str:
    key = str(path.relative_to(F.PSL_ROOT)) if str(path).startswith(str(F.PSL_ROOT)) else str(path.relative_to(F.REPO))
    SOURCES[key] = F.sha256(path)
    return key


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if (o is None or math.isnan(o) or math.isinf(o)) else round(float(o), 6)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def dump(name: str, obj) -> None:
    (APP / name).write_text(json.dumps(clean(obj), ensure_ascii=False, separators=(",", ":")))


def basis(verdict: str) -> str:
    return {"Context": "human-specified role (environment / demographic / playing time); not a statistical finding",
            "Diagnostic": "failed the projection test; labelled Diagnostic (not Exclude) because the catalog marks it as an interpretable process metric (human-specified)",
            "Exclude": "failed the projection test and is not marked as an interpretable process metric",
            "Projection": "passed the statistical projection test (material, consistent out-of-time lift; not redundant; stable sign; acceptable coverage)",
            "Augmented Projection": "predictive where observed but coverage too incomplete",
            "Insufficient Evidence": "too few out-of-time windows and too sparse coverage"}.get(verdict, "")


def main():
    from psl.components import studies
    st = studies()
    reason = pd.read_csv(S27 / "tables/table7_reason_codes_208.csv")
    src(S27 / "tables/table7_reason_codes_208.csv")
    metrics, evals = {}, []
    for t in TARGETS:
        sid = t["id"]
        spec = st[sid]
        p = CANON / f"{STUDY_FILE[sid]}.parquet"
        d = pd.read_parquet(p)
        src(p)
        t["n_candidates"] = int(len(d))
        t["n_player_seasons"] = int(pd.to_numeric(d["same_pop_n"], errors="coerce").max())
        nested = {}
        for T in (2021, 2022, 2023, 2024, 2025, 2026):
            fp = S27 / f"results/nested/admission/{sid}_T{T}_default_final.parquet"
            fin = pd.read_parquet(fp)
            src(fp)
            for _, r in fin.iterrows():
                nested.setdefault(r["feature"], {})[str(T)] = r["verdict"]
        for fs in spec.features:
            metrics.setdefault(fs.name, {"id": fs.name, "description": fs.description, "family": fs.family, "role": fs.role,
                                         "process_flag": bool(fs.process), "player_types": set()})["player_types"].add(spec.player_type)
        rc = reason[reason.study_id == sid].set_index("feature")
        for _, r in d.iterrows():
            br = float(r["baseline_rmse"]) if pd.notna(r["baseline_rmse"]) else None
            folds = json.loads(r["fold_rmse_deltas"]) if isinstance(r["fold_rmse_deltas"], str) else []
            sub = json.loads(r["subgroup"]) if isinstance(r["subgroup"], str) else {}
            nw = nested.get(r["feature"], {})
            pct = (lambda v: None if (v is None or pd.isna(v) or not br) else 100 * float(v) / br)
            evals.append({
                "target": sid, "metric": r["feature"], "family": r["family"], "verdict": r["verdict"],
                "reason_code": rc.loc[r["feature"], "reason_code"] if r["feature"] in rc.index else None,
                "rationale": r["rationale"],
                "verdict_basis": ("the target's own two-year history, a declared input of the history baseline; it was scored against a weaker current-season baseline, "
                                  "so this Projection label is not evidence that a new metric adds information") if (r["verdict"] == "Projection" and r["feature"] in set(spec.baseline))
                                 else basis(r["verdict"]),
                "delta_rmse": r["oos_rmse_delta"], "delta_pct": pct(r["oos_rmse_delta"]),
                "ci_low_pct": pct(r["oos_rmse_ci_low"]), "ci_high_pct": pct(r["oos_rmse_ci_high"]),
                "baseline_rmse": br, "folds_improved_share": r["folds_improved"], "n_folds": r["n_folds"],
                "fold_deltas_pct": [{"year": f["test_year"], "delta_pct": pct(f["rmse_delta"])} for f in folds],
                "reliability_r": r["reliability_pearson"], "coverage": r["coverage"], "coef_sign_changes": r["coef_sign_changes"],
                "max_corr_with_baseline": r["max_corr_with_baseline"], "max_corr_partner": r["max_corr_partner"],
                "family_redundant": bool(r["family_redundant"]) if pd.notna(r["family_redundant"]) else None,
                "family_representative": bool(r["family_representative"]) if pd.notna(r["family_representative"]) else None,
                "n_player_seasons": r["same_pop_n"],
                "subgroups": [{"name": k, "n": v.get("n"), "delta_pct": pct(v.get("rmse_delta"))} for k, v in sub.items() if isinstance(v, dict) and v.get("ok")],
                "nested_verdicts": nw, "nested_projection_count_2021_2025": sum(nw.get(str(T)) == "Projection" for T in (2021, 2022, 2023, 2024, 2025)),
                "nested_projection_2026_window": nw.get("2026") == "Projection",
                "evidence_tier": "historical", "seasons": "feature seasons 2015-2024; outcomes 2019-2025 (7 expanding folds)"})
    for m in metrics.values():
        m["player_types"] = sorted(m["player_types"])
    dump("targets.json", TARGETS)
    dump("metrics.json", sorted(metrics.values(), key=lambda m: m["id"]))
    dump("evaluations.json", evals)

    # ---- model comparisons (nested 2021-2025 + 2026)
    comp = pd.read_csv(S27 / "results/nested/comparisons_default.csv"); src(S27 / "results/nested/comparisons_default.csv")
    per = pd.read_csv(S27 / "results/nested/per_year_default.csv"); src(S27 / "results/nested/per_year_default.csv")
    c26 = pd.read_csv(S27 / "results/holdout2026/comparisons_2026.csv"); src(S27 / "results/holdout2026/comparisons_2026.csv")
    rows = []
    for _, r in comp.iterrows():
        rb = r["delta_rmse"] / (r["pct_of_b"] / 100) if r["pct_of_b"] else np.nan  # RMSE of model_b
        rows.append({"target": r["study_id"], "comparison": r["comparison"], "model_a": r["model_a"], "model_b": r["model_b"],
                     "delta_rmse": r["delta_rmse"], "delta_pct": r["pct_of_b"], "ci_low_pct": 100 * r["ci_low"] / rb, "ci_high_pct": 100 * r["ci_high"] / rb,
                     "years_a_better": r["years_a_better"], "n_years": r["n_years"], "n_rows": r["n_rows"], "n_players": r["n_players"],
                     "sample": "outer years 2021-2025 (nested)", "evidence_tier": "historical"})
    for _, r in c26.iterrows():
        rb = r["delta_rmse"] / (r["pct_of_b"] / 100) if r["pct_of_b"] else np.nan
        rows.append({"target": r["study_id"], "comparison": r["comparison"], "cohort": r["cohort"], "model_a": r["model_a"], "model_b": r["model_b"],
                     "delta_rmse": r["delta_rmse"], "delta_pct": r["pct_of_b"], "ci_low_pct": 100 * r["ci_low"] / rb, "ci_high_pct": 100 * r["ci_high"] / rb,
                     "n_rows": r["n_rows"], "n_players": r["n_players"], "sample": "2026 (frozen-in-workflow, exploratory)", "evidence_tier": "historical-2026"})
    dump("model_comparisons.json", {"comparisons": rows, "per_year": per.to_dict("records")})

    flag = pd.read_csv(S27 / "tables/table3_flagship_contrasts.csv"); src(S27 / "tables/table3_flagship_contrasts.csv")
    dump("flagships.json", flag.to_dict("records"))

    # ---- curated casebook
    fc = pd.read_parquet(S27 / "results/players/forecast_changes.parquet"); src(S27 / "results/players/forecast_changes.parquet")
    coh = pd.read_csv(S27 / "results/players/cohort_effects.csv"); src(S27 / "results/players/cohort_effects.csv")
    ut = pd.read_csv(S27 / "results/players/unit_translation.csv"); src(S27 / "results/players/unit_translation.csv")
    rng = np.random.default_rng(F.SEED)
    cases = []
    for con, g in fc.groupby("contrast"):
        g = g.assign(abs_change=g.change.abs())
        pick = pd.concat([g.nlargest(20, "change").assign(selection="largest increase"), g.nsmallest(20, "change").assign(selection="largest decrease")])
        rest = g.drop(pick.index)
        pick = pd.concat([pick, rest.iloc[rng.choice(len(rest), 20, replace=False)].assign(selection="random sample (seed 42)")])
        for _, r in pick.iterrows():
            cases.append({"contrast": con, "target": con.split(":")[0], "metric": con.split(":")[1], "selection": r["selection"],
                          "player": r["player"], "feature_season": int(r["season"]), "outcome_season": int(r["outer_year"]),
                          "metric_value": r["feature_value"], "forecast_without": r["pred_base"], "forecast_with": r["pred_aug"],
                          "observed": r["y"], "forecast_change": r["change"], "abs_error_change": r["abs_err_change"],
                          "improved": bool(r["abs_err_change"] < 0)})
    dump("casebook.json", {"cases": cases, "cohorts": coh.to_dict("records"), "unit_translation": ut.to_dict("records"),
                           "selection_note": "Per contrast: the 20 largest forecast increases, the 20 largest decreases, and 20 randomly drawn player-seasons (seed 42) "
                                             "from the outer years 2021-2025. Single-feature contrasts: history baseline vs baseline + the metric (ridge). "
                                             "Population: players meeting the study's eligibility in both seasons (outcome observed). Extreme cases are not typical."})

    # ---- fantasy bridge
    fr = pd.read_csv(F.FANTASY / "results_by_target_category.csv"); src(F.FANTASY / "results_by_target_category.csv")
    fy = pd.read_csv(F.FANTASY / "by_year.csv"); src(F.FANTASY / "by_year.csv")
    l1 = pd.read_csv(F.FANTASY / "level1_correlations.csv"); src(F.FANTASY / "level1_correlations.csv")
    cb = pd.read_csv(F.FANTASY / "cohort_by_year.csv"); src(F.FANTASY / "cohort_by_year.csv")
    rv = pd.read_csv(F.FANTASY / "ranking_value_sensitivity.csv"); src(F.FANTASY / "ranking_value_sensitivity.csv")
    dump("fantasy.json", {"results": fr.to_dict("records"), "by_year": fy[["group", "outcome", "kind", "target", "base", "aug", "sample", "outcome_season", "n", "delta_pct"]].to_dict("records"),
                          "level1": l1.to_dict("records"), "cohorts": cb.to_dict("records"), "decision": rv.to_dict("records"),
                          "protocol": "sloan2027_fantasy/fantasy/experiment_protocol.md (v1.0, committed before any fantasy model was fit)"})
    sw = F.FANTASY / "scoring_weights.json"
    if sw.exists():
        src(sw)
        dump("scoring.json", json.loads(sw.read_text()))
    meta = {"schema_version": "1.0", "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "paper": {"title": "One Metric, Different Jobs: Target-Specific Feature Admission for Major League Baseball Player Projection",
                      "venue": "MIT Sloan Sports Analytics Conference 2027, Research Papers (Baseball track), Paper ID 18 — full-paper stage"},
            "provenance": {"psl_research_root": "Projection-Signal-Lab research branch (research/sloan-2027 @ 04fddeb); canonical study commit 17da742",
                           "fantasy_protocol_commit": "8819791"},
            "evidence_tiers": {"historical": "Historical research evidence", "historical-2026": "2026 frozen-in-workflow check (exploratory; 2026 was already inspected)",
                               "exploratory_fantasy": "Exploratory fantasy linkage", "illustrative": "Illustrative / unvalidated scenario"},
            "ci_definition": "95% paired player-cluster bootstrap interval (2,000 resamples; players resampled across seasons). Negative ΔRMSE means the first-named model is more accurate.",
            "sources_sha256": SOURCES}
    dump("meta.json", meta)
    print({p.name: p.stat().st_size for p in APP.glob("*.json")})


if __name__ == "__main__":
    main()
