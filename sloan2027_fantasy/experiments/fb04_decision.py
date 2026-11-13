"""FB Level 3 (illustrative): does adding the target forecasts change draft-style decisions for the better? (protocol §6)

Policy: in each outcome season, rank the forecast-date pool by predicted 5x5 roto value (or predicted points) and take the
top k. Compare the realized value of the players chosen by the baseline-category models (BF) with those chosen by the
augmented models (BF + all ADM target forecasts). No ADP, positions, snake order or in-season moves: a what-if backtest.

Outputs
  fantasy/decision_backtest.csv            per season x group x format x k: mean realized value of picks, Spearman, overlap
  fantasy/ranking_value_sensitivity.csv    pooled 2021-2025 differences with player-resampling bootstrap CIs
  local/fantasy/decision_rankings.parquet  player-level predicted/realized values (git-ignored)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import fb_lib as F
import fb03_bridge as B

K = {"hitter": [50, 100, 156, 195], "pitcher": [50, 100, 108, 135]}
LEAGUE_K = {"hitter": 156, "pitcher": 108}


def predicted_totals(pred: pd.DataFrame, T: int, group: str, model: str) -> pd.DataFrame:
    p = pred[(pred.window_T == T) & (pred.group == group) & (pred.model == model)]
    w = p.pivot_table(index=["mlbam_id", "season"], columns="outcome", values="pred").reset_index()
    if group == "hitter":
        w["H_from_avg"] = w["AVG"] * w["AB"].clip(lower=0)
        out = w.rename(columns={c: f"p_{c}" for c in ("R", "HR", "RBI", "SB", "AB")})
        out["p_H"] = w["H_from_avg"]
    else:
        ip = w["IP"].clip(lower=0)
        out = w.rename(columns={c: f"p_{c}" for c in ("W", "SV", "K", "IP")})
        out["p_ER"], out["p_BBH"] = w["ERA"] * ip / 9, w["WHIP"] * ip
    for c in ("R", "HR", "RBI", "SB", "W", "SV", "K"):  # counts cannot be negative
        if f"p_{c}" in out:
            out[f"p_{c}"] = out[f"p_{c}"].clip(lower=0)
    pts = "PTS_H" if group == "hitter" else "PTS_P"
    if pts in w:
        out["p_PTS"] = w[pts]
    return out


def season_metrics(df: pd.DataFrame, pcol: str, ycol: str, k: int) -> dict:
    top_pred = df.nlargest(k, pcol)
    top_real = set(df.nlargest(k, ycol).index)
    return {"mean_realized_of_picks": float(top_pred[ycol].mean()), "spearman": float(spearmanr(df[pcol], df[ycol]).statistic),
            "topk_overlap": len(top_real & set(top_pred.index)) / k}


def main():
    pred = pd.read_parquet(F.LOCAL / "downstream_predictions.parquet")
    frames = {g: pd.read_parquet(F.LOCAL / f"downstream_frames_{g}.parquet") for g in ("hitter", "pitcher")}
    rng = np.random.default_rng(F.SEED)
    rows, rank_rows, boot_store = [], [], {}
    for g, d in frames.items():
        vcol = "y_VAL_H" if g == "hitter" else "y_VAL_P"
        ptscol = "y_PTS_H" if g == "hitter" else "y_PTS_P"
        for T in F.WINDOWS:
            fw = d[d.window_T == T].copy()
            test = fw[fw.season == T - 1].copy()
            ref_mask = fw.season <= T - 2
            per_model = {}
            for model in ("BF", "BF+joint"):
                pt = predicted_totals(pred, T, g, model)
                m = fw.merge(pt, on=["mlbam_id", "season"], how="left")
                val, _ = B.roto_value(m, g, ref_mask.to_numpy(), pred_prefix="p_")
                m["pred_value"] = val
                tm = m[m.season == T - 1].set_index("mlbam_id")
                per_model[model] = tm
            joined = per_model["BF"][["pred_value"]].rename(columns={"pred_value": "pv_base"}).join(
                per_model["BF+joint"][["pred_value"]].rename(columns={"pred_value": "pv_aug"}))
            joined["realized_value"] = test.set_index("mlbam_id")[vcol]
            fmts = [("roto_5x5", "pv_base", "pv_aug", "realized_value")]
            if "p_PTS" in per_model["BF"]:
                joined["pp_base"], joined["pp_aug"] = per_model["BF"]["p_PTS"], per_model["BF+joint"]["p_PTS"]
                joined["realized_points"] = test.set_index("mlbam_id")[ptscol]
                fmts.append(("points", "pp_base", "pp_aug", "realized_points"))
            joined = joined.dropna(subset=["pv_base", "pv_aug", "realized_value"])
            joined["window_T"], joined["group"] = T, g
            rank_rows.append(joined.reset_index())
            for fmt, cb, ca, cy in fmts:
                for k in K[g]:
                    mb, ma = season_metrics(joined, cb, cy, k), season_metrics(joined, ca, cy, k)
                    rows.append({"group": g, "format": fmt, "outcome_season": T, "k": k, "n_pool": len(joined),
                                 **{f"{kk}_base": v for kk, v in mb.items()}, **{f"{kk}_aug": v for kk, v in ma.items()}})
                    # player-resampling bootstrap within season (paired: same resample for both models)
                    diffs = np.empty(1000)
                    sdiff = np.empty(1000)
                    arr_b, arr_a, arr_y = joined[cb].to_numpy(), joined[ca].to_numpy(), joined[cy].to_numpy()
                    n = len(joined)
                    for b in range(1000):
                        ix = rng.integers(0, n, n)
                        yb, pb, pa = arr_y[ix], arr_b[ix], arr_a[ix]
                        kk = min(k, n)
                        diffs[b] = yb[np.argsort(-pa)[:kk]].mean() - yb[np.argsort(-pb)[:kk]].mean()
                        sdiff[b] = spearmanr(pa, yb).statistic - spearmanr(pb, yb).statistic
                    boot_store[(g, fmt, T, k)] = (diffs, sdiff)
    bt = pd.DataFrame(rows)
    bt.to_csv(F.FANTASY / "decision_backtest.csv", index=False)
    pd.concat(rank_rows).to_parquet(F.LOCAL / "decision_rankings.parquet", index=False)

    sens = []
    for (g, fmt, k), grp in bt[bt.outcome_season.isin(F.PRIMARY_YEARS)].groupby(["group", "format", "k"]):
        diffs = np.mean([boot_store[(g, fmt, T, k)][0] for T in F.PRIMARY_YEARS], axis=0)
        sdiffs = np.mean([boot_store[(g, fmt, T, k)][1] for T in F.PRIMARY_YEARS], axis=0)
        d_val = (grp.mean_realized_of_picks_aug - grp.mean_realized_of_picks_base).mean()
        d_rho = (grp.spearman_aug - grp.spearman_base).mean()
        sens.append({"group": g, "format": fmt, "k": k, "league_size_equivalent": {50: "small", 100: "~8-team", 156: "12-team", 195: "15-team", 108: "12-team", 135: "15-team"}.get(k, ""),
                     "mean_realized_value_of_picks_base": grp.mean_realized_of_picks_base.mean(), "mean_realized_value_of_picks_aug": grp.mean_realized_of_picks_aug.mean(),
                     "delta_mean_realized_value": d_val, "ci_low": float(np.quantile(diffs, 0.025)), "ci_high": float(np.quantile(diffs, 0.975)),
                     "seasons_aug_better": int((grp.mean_realized_of_picks_aug > grp.mean_realized_of_picks_base).sum()),
                     "spearman_base": grp.spearman_base.mean(), "spearman_aug": grp.spearman_aug.mean(), "delta_spearman": d_rho,
                     "spearman_ci_low": float(np.quantile(sdiffs, 0.025)), "spearman_ci_high": float(np.quantile(sdiffs, 0.975)),
                     "topk_overlap_base": grp.topk_overlap_base.mean(), "topk_overlap_aug": grp.topk_overlap_aug.mean(),
                     "sample": "2021-2025 pooled (illustrative what-if backtest)"})
    for (g, fmt, k), grp in bt[bt.outcome_season.eq(2026)].groupby(["group", "format", "k"]):
        diffs, sdiffs = boot_store[(g, fmt, 2026, k)]
        sens.append({"group": g, "format": fmt, "k": k, "mean_realized_value_of_picks_base": grp.mean_realized_of_picks_base.iloc[0],
                     "mean_realized_value_of_picks_aug": grp.mean_realized_of_picks_aug.iloc[0],
                     "delta_mean_realized_value": float(grp.mean_realized_of_picks_aug.iloc[0] - grp.mean_realized_of_picks_base.iloc[0]),
                     "ci_low": float(np.quantile(diffs, 0.025)), "ci_high": float(np.quantile(diffs, 0.975)),
                     "spearman_base": grp.spearman_base.iloc[0], "spearman_aug": grp.spearman_aug.iloc[0],
                     "delta_spearman": float(grp.spearman_aug.iloc[0] - grp.spearman_base.iloc[0]),
                     "spearman_ci_low": float(np.quantile(sdiffs, 0.025)), "spearman_ci_high": float(np.quantile(sdiffs, 0.975)),
                     "topk_overlap_base": grp.topk_overlap_base.iloc[0], "topk_overlap_aug": grp.topk_overlap_aug.iloc[0],
                     "sample": "2026 (exploratory)"})
    s = pd.DataFrame(sens)
    s.to_csv(F.FANTASY / "ranking_value_sensitivity.csv", index=False)
    print(s.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
