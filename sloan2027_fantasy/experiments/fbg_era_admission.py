"""FB-G (protocol Amendment 1): can the admission procedure select features for a NEW target (next-season ERA)?

Uses the canonical engine exactly as E1 does (nested windows T=2021..2025, inner years 2018..T-1, canonical gates,
ridge alpha=1) with a new StudySpec built from the FIP study (same pitcher sample, same candidate catalog) whose target is
y_era and whose history baseline uses two-year ERA. Compares ERA-specific selection with TRANSFER (re-using the FIP
study's window-T selections), the history baseline, and kitchen-sink models on identical outer rows.

Outputs: fantasy/generalization_era/{admission_by_window.csv, selected_sets.csv, comparisons.csv, per_year.csv}
         local/fantasy/era_predictions.parquet (player-level; git-ignored)
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace

import numpy as np
import pandas as pd

import fb_lib as F

sys.path.insert(0, str(F.PSL_ROOT / "sloan2027" / "experiments"))
import lib_nested as L  # noqa: E402  (redirects canonical side-files to a scratch folder; canonical artifacts untouched)

OUT = F.FANTASY / "generalization_era"
OUT.mkdir(parents=True, exist_ok=True)


def era_w2(sample: pd.DataFrame) -> pd.Series:
    raw = pd.read_parquet(F.DATA / "raw/mlb_pitching_2015_2025.parquet")[["mlbam_id", "season", "earnedRuns", "outs"]]
    raw = raw.rename(columns={"earnedRuns": "ER", "outs": "OUTS"})
    cur = sample[["mlbam_id", "season"]].merge(raw, on=["mlbam_id", "season"], how="left")
    prev = sample[["mlbam_id", "season"]].assign(season=sample.season - 1).merge(raw, on=["mlbam_id", "season"], how="left").fillna(0)
    ip = (cur.OUTS.fillna(0) + prev.OUTS) / 3
    w2 = 9 * (cur.ER.fillna(0) + prev.ER) / ip.replace(0, np.nan)
    return pd.Series(np.where(cur.OUTS.notna(), w2, sample["era"]), index=sample.index)


def build_spec():
    base = L.studies()["pitching_fip"]
    s = pd.read_parquet(base.sample_path).reset_index(drop=True)
    s["era_w2"] = era_w2(s).to_numpy()
    seasons = pd.read_parquet(base.seasons_path).reset_index(drop=True)
    seasons["era_w2"] = era_w2(seasons).to_numpy()
    sp, ssp = F.LOCAL / "pitcher_sample_era.parquet", F.LOCAL / "pitcher_seasons_era.parquet"
    s.to_parquet(sp, index=False)
    seasons.to_parquet(ssp, index=False)
    return replace(base, study_id="pitching_era", target="y_era", target_label="next-season ERA", sample_path=sp, seasons_path=ssp,
                   baseline=("age", "ip", "starter_role", "era_w2", "park_factor"), baseline_weak=("age", "ip", "era"),
                   persistence_col="era", secondary_targets=(), output_stem="admission_pitching_y_era", is_primary=False)


def admission(spec, sample, seasons, T):
    train = sample[sample.season <= T - 2].reset_index(drop=True)
    seasons_win = seasons[pd.to_numeric(seasons.season, errors="coerce") <= T - 1].copy()
    L.B.EXPANDING_TEST_YEARS = list(range(L.INNER_START, T))
    try:
        _, baseline = L.R._baselines_for_study(spec, train)
        rows = []
        for fs in spec.features:
            if fs.name not in train.columns:
                continue
            res = L.E.admit_feature(player_type=spec.player_type, spec=fs, sample=train, seasons=seasons_win, baseline=baseline,
                                    target=spec.target, family_cols=None, component=spec.component)
            rows.append(res.to_dict())
        raw = pd.DataFrame(rows)
        final = L.R.apply_post_admission_rules(raw.copy(), sample=train, seasons=seasons_win, baseline=baseline, target=spec.target,
                                               families=spec.families, player_type=spec.player_type, redecide=False,
                                               apply_kbb_demotion=spec.apply_kbb_demotion)
    finally:
        L.B.EXPANDING_TEST_YEARS = L.CANONICAL_TEST_YEARS
    selected = final.loc[final.verdict.eq("Projection") & ~final.feature.isin(baseline), "feature"].tolist()
    return baseline, selected, final


def main():
    spec = build_spec()
    sample = pd.read_parquet(spec.sample_path)
    sample["model_weight"] = pd.to_numeric(sample["ip"], errors="coerce")
    sample["season"] = sample.season.astype(int)
    seasons = pd.read_parquet(spec.seasons_path)
    preds, sets, verdicts = [], [], []
    for T in F.PRIMARY_YEARS:
        baseline, selected, final = admission(spec, sample, seasons, T)
        fip_sel = json.loads((F.ADMISSION / f"pitching_fip_T{T}_default_meta.json").read_text())["selected"]
        train = sample[sample.season <= T - 2].reset_index(drop=True)
        test = sample[sample.season == T - 1].reset_index(drop=True)
        skill = [f.name for f in spec.features if f.role == "skill"]
        ks = [c for c in dict.fromkeys([*baseline, *skill]) if c in train.columns and pd.api.types.is_numeric_dtype(train[c]) and train[c].notna().mean() >= 0.05]
        fsets = {"B0": list(baseline), "ADM": [*baseline, *selected], "TRANSFER": [*baseline, *[f for f in fip_sel if f not in baseline]], "KS": ks}
        sets.append({"outer_year": T, "baseline": ",".join(baseline), "era_selected": ",".join(selected), "n_era_selected": len(selected),
                     "fip_selected_transfer": ",".join(fip_sel), "n_transfer": len(fip_sel),
                     "overlap": ",".join(sorted(set(selected) & set(fip_sel)))})
        for _, r in final.iterrows():
            verdicts.append({"outer_year": T, "feature": r["feature"], "family": r["family"], "verdict": r["verdict"],
                             "oos_rmse_delta": r["oos_rmse_delta"], "folds_improved": r["folds_improved"]})
        for name, feats in fsets.items():
            for est in (("ridge", "enet") if name == "KS" else ("ridge",)):
                fit = L.fit_outer(est, train, test, feats, spec.target, T)
                preds.append(L.predictions_frame("pitching_era", T, f"{name}|{est}", test, spec.target, fit))
        print(T, "selected", selected, flush=True)
    P = pd.concat(preds, ignore_index=True)
    P.to_parquet(F.LOCAL / "era_predictions.parquet", index=False)
    pd.DataFrame(sets).to_csv(OUT / "selected_sets.csv", index=False)
    pd.DataFrame(verdicts).to_csv(OUT / "admission_by_window.csv", index=False)
    comps = [("ERA-ADM vs B0", "ADM|ridge", "B0|ridge"), ("TRANSFER vs B0", "TRANSFER|ridge", "B0|ridge"),
             ("ERA-ADM vs TRANSFER", "ADM|ridge", "TRANSFER|ridge"), ("KS ridge vs ERA-ADM", "KS|ridge", "ADM|ridge"),
             ("KS elastic net vs ERA-ADM", "KS|enet", "ADM|ridge")]
    rows = []
    for label, a, b in comps:
        r = L.paired_cluster_bootstrap(P[P.model_id == a], P[P.model_id == b])
        rb = L.wrmse(P[P.model_id == b].y, P[P.model_id == b].pred, P[P.model_id == b].w)
        rows.append({"comparison": label, "model_a": a, "model_b": b, **r, "rmse_b": rb, "delta_pct": 100 * r["delta_rmse"] / rb,
                     "ci_low_pct": 100 * r["ci_low"] / rb, "ci_high_pct": 100 * r["ci_high"] / rb})
    C = pd.DataFrame(rows)
    C.to_csv(OUT / "comparisons.csv", index=False)
    L.per_year_table(P).to_csv(OUT / "per_year.csv", index=False)
    print(C[["comparison", "delta_pct", "ci_low_pct", "ci_high_pct", "n_rows"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
