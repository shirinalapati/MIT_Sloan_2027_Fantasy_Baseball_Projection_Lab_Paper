"""POST HOC analyses requested by the internal referee review (protocol Amendment 2). Reported as post hoc; separate family.

Outputs: fantasy/referee_checks/{history_decomposition, season_level, within_season, retention_by_decile,
         direct_tests_posthoc, raw_vs_forecast, draft_scaling, named_cases, inner2017, placebo_summary}.csv
"""
from __future__ import annotations

import json
import math
from itertools import product

import numpy as np
import pandas as pd
from scipy import stats

import fb_lib as F
import fb03_bridge as B

OUT = F.FANTASY / "referee_checks"
OUT.mkdir(parents=True, exist_ok=True)
STUDIES = ["hitting_woba", "pitching_fip", "baserunning_rv", "defense_rv", "overall_war", "pitcher_war"]
W3 = {"hitting_woba": "woba_w3", "pitching_fip": "fip_w3", "baserunning_rv": "br_rv_rate_w3", "defense_rv": "def_rv_rate_w3",
      "overall_war": "war_rate_w3", "pitcher_war": "war_rate_w3"}


def season_stats(deltas):
    d = np.asarray(deltas, float)
    n = len(d)
    m, s = d.mean(), d.std(ddof=1)
    half = stats.t.ppf(0.975, n - 1) * s / math.sqrt(n)
    signs = np.array(list(product([-1, 1], repeat=n)))
    null = (signs * np.abs(d)).mean(axis=1)
    p = float((np.abs(null) >= abs(m) - 1e-12).mean())
    return m, m - half, m + half, p


def within_season(df, col_a, col_b, y="y", w="w", season="season"):
    out = {}
    for col in (col_a, col_b):
        r = df[y] - df[col]
        mu = (r * df[w]).groupby(df[season]).transform("sum") / df[w].groupby(df[season]).transform("sum")
        out[col] = np.sqrt(np.average((r - mu) ** 2, weights=df[w]))
    return 100 * (out[col_a] - out[col_b]) / out[col_b]


def history_decomposition():
    rows, preds = [], []
    for sid in STUDIES:
        spec, sample = F.load_study(sid)
        for T in F.PRIMARY_YEARS:
            meta = F.window_meta(sid, T)
            train = sample[sample.season <= T - 2].reset_index(drop=True)
            test = sample[sample.season == T - 1].reset_index(drop=True)
            sets = {"B0": list(meta["baseline"]), "B0+3yr": [*meta["baseline"], W3[sid]], "ADM": [*meta["baseline"], *meta["selected"]]}
            for name, feats in sets.items():
                p, _, use = F.fit_ridge(train, test, feats, spec.target, T, tuned=False)
                preds.append(pd.DataFrame({"study_id": sid, "mlbam_id": test.mlbam_id.to_numpy(), "season": T, "model": name,
                                           "y": test[spec.target].to_numpy(float), "w": F.weights(test), "pred": p}))
    P = pd.concat(preds, ignore_index=True)
    wide = P.pivot_table(index=["study_id", "mlbam_id", "season", "y", "w"], columns="model", values="pred").reset_index()
    for sid, g in wide.groupby("study_id"):
        for a, b in (("B0+3yr", "B0"), ("ADM", "B0+3yr"), ("ADM", "B0")):
            r = F.paired_bootstrap(g, a, b)
            rows.append({"study_id": sid, "comparison": f"{a} vs {b}", "delta_pct": r["delta_pct"], "ci_low_pct": r["ci_low_pct"], "ci_high_pct": r["ci_high_pct"],
                         "n_rows": r["n_rows"], "three_year_column": W3[sid]})
    pd.DataFrame(rows).to_csv(OUT / "history_decomposition.csv", index=False)
    return P


def season_level_and_within():
    e1 = pd.read_parquet(F.RESULTS / "nested/predictions_default.parquet")
    e1 = e1[e1.outer_year <= 2025]
    rows, wrows = [], []
    for sid, g in e1.groupby("study_id"):
        w = g.pivot_table(index=["mlbam_id", "season", "outer_year", "y", "w"], columns="model_id", values="pred").reset_index()
        deltas = []
        for T, h in w.groupby("outer_year"):
            ra, rb = F.wrmse(h.y, h["ADM|ridge"], h.w), F.wrmse(h.y, h["B0|ridge"], h.w)
            deltas.append(100 * (ra - rb) / rb)
        m, lo, hi, p = season_stats(deltas)
        rows.append({"contrast": f"{sid}: selected vs history baseline", "per_season": ";".join(f"{d:+.2f}" for d in deltas), "mean": m, "t4_low": lo, "t4_high": hi, "signflip_p": p})
        wrows.append({"contrast": f"{sid}: selected vs history baseline", "raw_pct": 100 * (F.wrmse(w.y, w["ADM|ridge"], w.w) - F.wrmse(w.y, w["B0|ridge"], w.w)) / F.wrmse(w.y, w["B0|ridge"], w.w),
                      "within_season_pct": within_season(w.rename(columns={"outer_year": "season_"}).assign(season=w.outer_year), "ADM|ridge", "B0|ridge")})
    by = pd.read_csv(F.FANTASY / "by_year.csv")
    prim = by[(by.family == "primary") & by["sample"].str.startswith("2021")]
    for (o, t), g in prim.groupby(["outcome", "target"]):
        g = g.sort_values("outcome_season")
        m, lo, hi, p = season_stats(g.delta_pct)
        rows.append({"contrast": f"fantasy primary: {t} -> {o}", "per_season": ";".join(f"{d:+.2f}" for d in g.delta_pct), "mean": m, "t4_low": lo, "t4_high": hi, "signflip_p": p})
    dp = pd.read_parquet(F.LOCAL / "downstream_predictions.parquet")
    dp = dp[dp.window_T <= 2025]
    for o, t, base, aug in (("ERA", "fip", "BF", "BF+fip"), ("WHIP", "fip", "BF", "BF+fip"), ("HR", "woba", "BF", "BF+woba"), ("SB", "br", "BF", "BF+br"),
                            ("SB", "sprint_speed", "BF", "BF+sprint_speed"), ("HR", "barrel_pct", "BF", "BF+barrel_pct"), ("VAL_P", "fip", "BF", "BF+fip"),
                            ("VAL_H", "hwar", "BF", "BF+hwar"), ("AVG", "woba", "BF", "BF+woba")):
        g = dp[dp.outcome == o]
        w = g[g.model.isin([base, aug])].pivot_table(index=["mlbam_id", "season", "outcome_season", "y", "w"], columns="model", values="pred").reset_index().dropna(subset=["y"])
        w = w[w.w > 0]
        raw = 100 * (F.wrmse(w.y, w[aug], w.w) - F.wrmse(w.y, w[base], w.w)) / F.wrmse(w.y, w[base], w.w)
        wrows.append({"contrast": f"fantasy: {t} -> {o}", "raw_pct": raw, "within_season_pct": within_season(w.assign(season=w.outcome_season), aug, base)})
    pd.DataFrame(rows).to_csv(OUT / "season_level.csv", index=False)
    pd.DataFrame(wrows).to_csv(OUT / "within_season.csv", index=False)


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def retention():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    pl = F.load_labeled("pitching_fip")
    pool = pl[F.year_t_eligible("pitching_fip", pl) & pl.season.between(2020, 2024)].copy()
    _, sample = F.load_study("pitching_fip")
    keys = set(zip(sample.mlbam_id, sample.season))
    pool["retained"] = [(a, b) in keys for a, b in zip(pool.mlbam_id, pool.season)]
    pool["dec"] = pool.groupby("season").stuff_plus.transform(lambda x: pd.qcut(x.rank(method="first"), 10, labels=False)) + 1
    X = pool[["age", "ip", "starter_role", "fip", "k_pct", "bb_pct", "stuff_plus"]].astype(float)
    X = X.fillna(X.median())
    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X, pool.retained)
    pool["p_ret"] = lr.predict_proba(X)[:, 1]
    fc = pd.read_parquet(F.RESULTS / "players/forecast_changes.parquet")
    s = fc[fc.contrast == "pitching_fip:stuff_plus"][["mlbam_id", "season", "abs_err_change"]]
    m = s.merge(pool[["mlbam_id", "season", "dec", "p_ret"]], on=["mlbam_id", "season"], how="left")
    m["improved"] = m.abs_err_change < 0
    rows = []
    for d in range(1, 11):
        pd_ = pool[pool.dec == d]
        md = m[m.dec == d]
        k, n = int(md.improved.sum()), len(md)
        lo, hi = wilson(k, n)
        wts = 1 / md.p_ret.clip(lower=0.05)
        rows.append({"stuff_decile": d, "pool_n": len(pd_), "retained_share": pd_.retained.mean(), "evaluated_n": n,
                     "share_improved": k / n if n else np.nan, "wilson_low": lo, "wilson_high": hi,
                     "ipw_share_improved": float(np.average(md.improved, weights=wts)) if n else np.nan})
    pd.DataFrame(rows).to_csv(OUT / "retention_by_decile.csv", index=False)


def direct_tests():
    """Stuff+ -> K per 9 (>=20 IP, weight IP); exit velocity -> HR. Same BF, tuned ridge, same windows."""
    Hh, Pp = B.season_tables()
    pool = pd.read_parquet(F.LOCAL / "pools.parquet")
    hl = F.load_labeled("hitting_woba")[["mlbam_id", "season", "ev"]]
    fh = pd.read_parquet(F.LOCAL / "downstream_frames_hitter.parquet").merge(hl, on=["mlbam_id", "season"], how="left")
    fp = pd.read_parquet(F.LOCAL / "downstream_frames_pitcher.parquet")
    fp["y_K9"] = np.where(fp.w_ERA >= 20, 9 * fp.y_K / fp.y_IP.replace(0, np.nan), np.nan)
    fp["w_K9"] = fp.w_ERA
    rows, preds = [], []
    for grp, frame, outcome, metric, rate in (("pitcher", fp, "K9", "stuff_plus", True), ("hitter", fh, "HR", "ev", False)):
        bf = B.BF_P if grp == "pitcher" else B.BF_H
        for T in F.PRIMARY_YEARS:
            d = frame[frame.window_T == T]
            y = f"y_{outcome}"
            train = d[(d.season <= T - 2) & d[y].notna()].copy()
            test = d[d.season == T - 1].copy()
            train["model_weight"] = train["w_K9"] if rate else 1.0
            for name, feats in (("BF", bf), (f"BF+{metric}", bf + [metric])):
                p, _, _ = F.fit_ridge(train, test, feats, y, T, tuned=True)
                preds.append(pd.DataFrame({"outcome": outcome, "model": name, "mlbam_id": test.mlbam_id.to_numpy(), "season": test.season.to_numpy(),
                                           "outcome_season": T, "y": test[y].to_numpy(float), "w": test["w_K9"].to_numpy(float) if rate else 1.0, "pred": p}))
    P = pd.concat(preds, ignore_index=True)
    for (o, metric) in (("K9", "stuff_plus"), ("HR", "ev")):
        g = P[P.outcome == o]
        w = g.pivot_table(index=["mlbam_id", "season", "outcome_season", "y", "w"], columns="model", values="pred").reset_index().dropna(subset=["y"])
        r = F.paired_bootstrap(w, f"BF+{metric}", "BF")
        rows.append({"test": f"{metric} -> {o}", "delta_pct": r["delta_pct"], "ci_low_pct": r["ci_low_pct"], "ci_high_pct": r["ci_high_pct"], "p_two_sided": r["p_two_sided"],
                     "n_rows": r["n_rows"], "rmse_base": r["rmse_b"], "rmse_aug": r["rmse_a"], "status": "post hoc (referee request)"})
    dp = pd.read_parquet(F.LOCAL / "downstream_predictions.parquet")
    dp = dp[dp.window_T <= 2025]
    for o, a, b in (("SB", "BF+sprint_speed", "BF+br"), ("HR", "BF+xwoba_w2", "BF+woba")):
        g = dp[(dp.outcome == o) & dp.model.isin([a, b])]
        w = g.pivot_table(index=["mlbam_id", "season", "outcome_season", "y", "w"], columns="model", values="pred").reset_index()
        r = F.paired_bootstrap(w, a, b)
        rows.append({"test": f"{a} vs {b} ({o})", "delta_pct": r["delta_pct"], "ci_low_pct": r["ci_low_pct"], "ci_high_pct": r["ci_high_pct"], "p_two_sided": r["p_two_sided"],
                     "n_rows": r["n_rows"], "rmse_base": r["rmse_b"], "rmse_aug": r["rmse_a"], "status": "post hoc (referee request)"})
    pd.DataFrame(rows).to_csv(OUT / "direct_tests_posthoc.csv", index=False)


def draft_scaling():
    R = pd.read_parquet(F.LOCAL / "decision_rankings.parquet")
    R = R[R.window_T <= 2025]
    rows = []
    rng = np.random.default_rng(F.SEED)
    for g, d in R.groupby("group"):
        sd = d.realized_value.std()
        for k in ([120, 156, 210] if g == "hitter" else [96, 108, 135]):
            ov, dv, boots = [], [], []
            for T, h in d.groupby("window_T"):
                tb, ta = set(h.nlargest(k, "pv_base").mlbam_id), set(h.nlargest(k, "pv_aug").mlbam_id)
                ov.append(len(tb & ta) / k)
                dv.append(h.nlargest(k, "pv_aug").realized_value.mean() - h.nlargest(k, "pv_base").realized_value.mean())
            for _ in range(1000):
                acc = []
                for T, h in d.groupby("window_T"):
                    ix = rng.integers(0, len(h), len(h))
                    hh = h.iloc[ix]
                    acc.append(hh.nlargest(k, "pv_aug").realized_value.mean() - hh.nlargest(k, "pv_base").realized_value.mean())
                boots.append(np.mean(acc))
            rows.append({"group": g, "k": k, "league": {120: "Yahoo 12-team active", 96: "Yahoo 12-team active", 210: "NFBC 15-team", 135: "NFBC 15-team"}.get(k, "protocol k"),
                         "realized_value_sd": sd, "mean_overlap_base_vs_aug": float(np.mean(ov)), "delta_mean_value_per_pick": float(np.mean(dv)),
                         "ci_low": float(np.quantile(boots, 0.025)), "ci_high": float(np.quantile(boots, 0.975)), "delta_in_sd_units": float(np.mean(dv) / sd)})
        d = d.copy()
        d["rank_base"] = d.groupby("window_T").pv_base.rank(ascending=False)
        d["rank_aug"] = d.groupby("window_T").pv_aug.rank(ascending=False)
        d["bucket"] = pd.cut(d.rank_base, [0, 12, 50, 156 if g == "hitter" else 108, 10_000], labels=["1-12", "13-50", "51-k", "beyond k"])
        for bkt, h in d.groupby("bucket", observed=True):
            rows.append({"group": g, "k": None, "league": f"median |rank change|, baseline ranks {bkt}", "median_abs_rank_change": float((h.rank_aug - h.rank_base).abs().median())})
    pd.DataFrame(rows).to_csv(OUT / "draft_scaling.csv", index=False)


def named_cases():
    fc = pd.read_parquet(F.RESULTS / "players/forecast_changes.parquet")
    rows = []
    for con, unit in (("hitting_woba:xwoba_w2", "wOBA"), ("baserunning_rv:sprint_speed", "BR runs per 100 times on base")):
        g = fc[fc.contrast == con]
        for lab, r in (("largest improvement", g.nsmallest(1, "abs_err_change").iloc[0]), ("largest harm", g.nlargest(1, "abs_err_change").iloc[0])):
            rows.append({"contrast": con, "rule": lab, "player": r.player, "feature_season": int(r.season), "outcome_season": int(r.outer_year), "metric_value": r.feature_value,
                         "forecast_without": r.pred_base, "forecast_with": r.pred_aug, "observed": r.y, "abs_error_change": r.abs_err_change, "unit": unit})
    dp = pd.read_parquet(F.LOCAL / "downstream_predictions.parquet")
    o = pd.read_parquet(F.LOCAL / "category_outcomes.parquet")
    names = o.drop_duplicates("mlbam_id").set_index("mlbam_id").full_name
    g = dp[(dp.outcome == "ERA") & dp.model.isin(["BF", "BF+fip"]) & (dp.window_T <= 2025)]
    w = g.pivot_table(index=["mlbam_id", "season", "outcome_season", "y", "w"], columns="model", values="pred").reset_index().dropna(subset=["y"])
    w = w[w.w >= 60]  # at least 60 IP so a single case is not a tiny-sample ERA
    w["abs_error_change"] = (w.y - w["BF+fip"]).abs() - (w.y - w["BF"]).abs()
    for lab, r in (("largest improvement (≥60 IP)", w.nsmallest(1, "abs_error_change").iloc[0]), ("largest harm (≥60 IP)", w.nlargest(1, "abs_error_change").iloc[0])):
        rows.append({"contrast": "fantasy: FIP forecast -> ERA", "rule": lab, "player": names.get(r.mlbam_id, str(r.mlbam_id)), "feature_season": int(r.season),
                     "outcome_season": int(r.outcome_season), "metric_value": None, "forecast_without": r["BF"], "forecast_with": r["BF+fip"], "observed": r.y,
                     "abs_error_change": r.abs_error_change, "unit": "ERA", "ip_next_season": r.w})
    pd.DataFrame(rows).to_csv(OUT / "named_cases.csv", index=False)


def inner2017_and_placebo():
    c = pd.read_csv(F.RESULTS / "nested/comparisons_inner2017.csv")
    keep = c[c.comparison.isin(["ADM vs B0 (selection policy lift)", "KS vs ADM (kitchen minus selective)", "EN-KS vs ADM (tuned elastic net on kitchen)"])].copy()
    keep["rb"] = keep.delta_rmse / (keep.pct_of_b / 100)
    keep["ci_low_pct"], keep["ci_high_pct"] = 100 * keep.ci_low / keep.rb, 100 * keep.ci_high / keep.rb
    keep[["study_id", "comparison", "pct_of_b", "ci_low_pct", "ci_high_pct", "years_a_better", "n_years", "per_year"]].to_csv(OUT / "inner2017.csv", index=False)
    p = pd.read_csv(F.RESULTS / "placebo/placebo_verdicts.csv")
    allfold = int(((p.folds_improved >= 0.999) & (p.verdict != "Projection")).sum())
    pd.DataFrame([{"n": len(p), "projection": int((p.verdict == "Projection").sum()), "diagnostic": int((p.verdict == "Diagnostic").sum()),
                   "insufficient_evidence": int((p.verdict == "Insufficient Evidence").sum()), "improved_every_fold_but_not_admitted": allfold,
                   "construction": "permuted copies of real metrics (shuffled across player-seasons), e.g. placebo_perm0_woba"}]).to_csv(OUT / "placebo_summary.csv", index=False)


def main():
    history_decomposition()
    season_level_and_within()
    retention()
    direct_tests()
    draft_scaling()
    named_cases()
    inner2017_and_placebo()
    for f in sorted(OUT.glob("*.csv")):
        print("==", f.name)
        print(pd.read_csv(f).round(3).to_string(index=False)[:2500])


if __name__ == "__main__":
    main()
