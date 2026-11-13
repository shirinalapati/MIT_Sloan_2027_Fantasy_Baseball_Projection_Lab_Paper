"""FB Levels 1–2: do out-of-time forecasts of the six targets add information about fantasy outcomes? (protocol §4–§7)

Outputs (aggregate, committed)
  fantasy/level1_correlations.csv          descriptive association of ADM target forecasts with next-season categories
  fantasy/results_by_target_category.csv   every pre-specified comparison, pooled 2021-2025 (+2026 exploratory rows)
  fantasy/paired_uncertainty.csv           bootstrap details (player-cluster + season-block) for each comparison
  fantasy/by_year.csv                      per-outcome-season ΔRMSE for each comparison
Outputs (player-level, git-ignored)
  local/fantasy/downstream_predictions.parquet
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

import fb_lib as F

HIT_COUNTS = ["R", "HR", "RBI", "SB", "AB", "H"]
PIT_COUNTS = ["W", "SV", "K", "IP", "ER", "BBH"]
BF_H = ["PA_t", "PA_t1", "G_t", "age", "age2", "R_pa", "HR_pa", "RBI_pa", "SB_pa", "R_pa2", "HR_pa2", "RBI_pa2", "SB_pa2",
        "AVG_t", "AVG2", "BB_pct_t", "K_pct_t"]
BF_P = ["IP_t", "IP_t1", "G_t", "GS_t", "GS_share", "age", "age2", "W_t", "SV_t", "SVO_t", "HLD_t", "K_ip", "K_ip2",
        "ERA_t", "WHIP_t", "ERA2", "WHIP2"]
HIT_TARGETS, PIT_TARGETS = ["woba", "br", "fld", "hwar"], ["fip", "pwar"]
DIRECT = {"hitter": {"sprint_speed": ["SB"], "xwoba_w2": ["AVG", "HR", "R", "RBI"], "barrel_pct": ["HR"]},
          "pitcher": {"stuff_plus": ["K", "ERA", "WHIP"], "k_pct": ["K"], "k_bb_pct": ["ERA", "WHIP"]}}
PRIMARY = {("woba", "AVG"), ("woba", "HR"), ("fip", "ERA"), ("fip", "WHIP"), ("br", "SB"), ("fld", "VAL_H"), ("hwar", "VAL_H"), ("pwar", "VAL_P")}
UNITS = {"R": "runs", "HR": "home runs", "RBI": "RBI", "SB": "stolen bases", "AVG": "batting average", "AB": "at-bats",
         "W": "wins", "SV": "saves", "K": "strikeouts", "ERA": "ERA (earned runs per 9 IP)", "WHIP": "WHIP", "IP": "innings",
         "PTS_H": "fantasy points", "PTS_P": "fantasy points", "VAL_H": "roto z-score units", "VAL_P": "roto z-score units"}
RATE = {"AVG": ("H", "AB", 100.0, 1.0), "ERA": ("ER", "IP", 20.0, 9.0), "WHIP": ("BBH", "IP", 20.0, 1.0)}


def load_weights():
    p = F.FANTASY / "scoring_weights.json"
    return json.loads(p.read_text()) if p.exists() else None


# ----------------------------------------------------------------------------- frame construction
def season_tables():
    o = pd.read_parquet(F.LOCAL / "category_outcomes.parquet")
    H = o[o.group == "hitter"].copy()
    P = o[o.group == "pitcher"].copy()
    P["BBH"] = P["BB"] + P["H"]
    return H, P


def prorate(df: pd.DataFrame, cols, season_col="season"):
    df = df.copy()
    df[cols] = df[cols].astype(float)
    m = df[season_col].eq(F.COVID)
    df.loc[m, cols] = df.loc[m, cols] * F.COVID_SCALE
    return df


def hitter_features(H: pd.DataFrame, pool: pd.DataFrame) -> pd.DataFrame:
    cur = H.set_index(["mlbam_id", "season"])
    t = pool[["mlbam_id", "season", "age", "xwoba_w2", "sprint_speed", "barrel_pct"]].copy()
    a = cur.reindex(list(zip(t.mlbam_id, t.season))).reset_index(drop=True)
    b = cur.reindex(list(zip(t.mlbam_id, t.season - 1))).reset_index(drop=True).fillna(0.0)
    X = t.reset_index(drop=True)
    pa, pa1 = a["PA"].clip(lower=1), b["PA"]
    for c in ("R", "HR", "RBI", "SB"):
        X[f"{c}_pa"] = a[c] / pa
        X[f"{c}_pa2"] = (a[c] + b[c]) / (pa + pa1)
    X["AVG_t"] = a["H"] / a["AB"].clip(lower=1)
    X["AVG2"] = (a["H"] + b["H"]) / (a["AB"] + b["AB"]).clip(lower=1)
    X["BB_pct_t"], X["K_pct_t"] = a["BB"] / pa, a["SO"] / pa
    scale_t = np.where(X.season.eq(F.COVID), F.COVID_SCALE, 1.0)
    scale_t1 = np.where((X.season - 1).eq(F.COVID), F.COVID_SCALE, 1.0)
    X["PA_t"], X["G_t"], X["PA_t1"] = a["PA"] * scale_t, a["G"] * scale_t, b["PA"] * scale_t1
    X["age2"] = X["age"] ** 2
    return X


def pitcher_features(P: pd.DataFrame, pool: pd.DataFrame) -> pd.DataFrame:
    cur = P.set_index(["mlbam_id", "season"])
    t = pool[["mlbam_id", "season", "age", "stuff_plus", "k_pct", "k_bb_pct"]].copy()
    a = cur.reindex(list(zip(t.mlbam_id, t.season))).reset_index(drop=True)
    b = cur.reindex(list(zip(t.mlbam_id, t.season - 1))).reset_index(drop=True).fillna(0.0)
    X = t.reset_index(drop=True)
    ip, ip1 = a["IP"].clip(lower=1 / 3), b["IP"]
    X["K_ip"], X["K_ip2"] = a["K"] / ip, (a["K"] + b["K"]) / (ip + ip1)
    X["ERA_t"], X["WHIP_t"] = 9 * a["ER"] / ip, a["BBH"] / ip
    X["ERA2"], X["WHIP2"] = 9 * (a["ER"] + b["ER"]) / (ip + ip1), (a["BBH"] + b["BBH"]) / (ip + ip1)
    X["GS_share"] = a["GS"] / a["G"].clip(lower=1)
    s_t = np.where(X.season.eq(F.COVID), F.COVID_SCALE, 1.0)
    s_t1 = np.where((X.season - 1).eq(F.COVID), F.COVID_SCALE, 1.0)
    for c, src in (("IP_t", "IP"), ("G_t", "G"), ("GS_t", "GS"), ("W_t", "W"), ("SV_t", "SV"), ("SVO_t", "SVO"), ("HLD_t", "HLD")):
        X[c] = a[src] * s_t
    X["IP_t1"] = b["IP"] * s_t1
    X["age2"] = X["age"] ** 2
    return X


def attach_outcomes(X: pd.DataFrame, tab: pd.DataFrame, counts: list[str], weights_cfg, group: str) -> pd.DataFrame:
    nxt = tab[["mlbam_id", "season", *counts, *(["2B", "3B", "1B", "BB", "HBP", "CS", "SO"] if group == "hitter" else ["L", "HLD", "BB", "H", "HBP", "HR", "CG", "SHO", "GS", "BS", "RA", "OUTS"])]].copy()
    nxt = nxt.loc[:, ~nxt.columns.duplicated()]
    nxt = prorate(nxt, [c for c in nxt.columns if c not in ("mlbam_id", "season")])
    nxt = nxt.rename(columns={c: f"y_{c}" for c in nxt.columns if c not in ("mlbam_id", "season")})
    nxt["season"] -= 1  # align outcome season t+1 to feature season t
    out = X.merge(nxt, on=["mlbam_id", "season"], how="left")
    ycols = [c for c in out.columns if c.startswith("y_")]
    out[ycols] = out[ycols].fillna(0.0)          # non-returners score zero
    out["outcome_season"] = out["season"] + 1
    for r, (num, den, floor, k) in RATE.items():
        if f"y_{den}" in out:
            raw_den = out[f"y_{den}"] / np.where(out.outcome_season.eq(F.COVID), F.COVID_SCALE, 1.0)
            out[f"y_{r}"] = np.where(raw_den >= floor, k * out[f"y_{num}"] / out[f"y_{den}"].replace(0, np.nan), np.nan)
            out[f"w_{r}"] = raw_den
    if weights_cfg:
        wcfg = weights_cfg["batters" if group == "hitter" else "pitchers"]
        pts = np.zeros(len(out))
        for stat, wt in wcfg.items():
            col = {"IP": "y_IP"}.get(stat, f"y_{stat}")
            if col not in out:
                raise KeyError(f"points stat {stat} not available")
            pts = pts + wt * out[col]
        out["y_PTS_H" if group == "hitter" else "y_PTS_P"] = pts
    return out


def roto_value(df: pd.DataFrame, group: str, ref_mask: pd.Series, pred_prefix: str = "y_") -> tuple[pd.Series, dict]:
    """5x5 z-score value; reference mean/SD and pooled ratios come from realized training-season rows only."""
    R = df[ref_mask]
    if group == "hitter":
        avg_ref = R["y_H"].sum() / R["y_AB"].sum()
        comp = {c: df[f"{pred_prefix}{c}"] for c in ("R", "HR", "RBI", "SB")}
        comp["AVGc"] = df[f"{pred_prefix}H"] - df[f"{pred_prefix}AB"] * avg_ref
        ref = {c: R[f"y_{c}"] for c in ("R", "HR", "RBI", "SB")}
        ref["AVGc"] = R["y_H"] - R["y_AB"] * avg_ref
        consts = {"avg_ref": avg_ref}
    else:
        era_ref = 9 * R["y_ER"].sum() / R["y_IP"].sum()
        whip_ref = R["y_BBH"].sum() / R["y_IP"].sum()
        comp = {c: df[f"{pred_prefix}{c}"] for c in ("W", "SV", "K")}
        comp["ERAc"] = df[f"{pred_prefix}IP"] * era_ref / 9 - df[f"{pred_prefix}ER"]
        comp["WHIPc"] = df[f"{pred_prefix}IP"] * whip_ref - df[f"{pred_prefix}BBH"]
        ref = {c: R[f"y_{c}"] for c in ("W", "SV", "K")}
        ref["ERAc"] = R["y_IP"] * era_ref / 9 - R["y_ER"]
        ref["WHIPc"] = R["y_IP"] * whip_ref - R["y_BBH"]
        consts = {"era_ref": era_ref, "whip_ref": whip_ref}
    val = sum((comp[c] - ref[c].mean()) / ref[c].std(ddof=0) for c in comp)
    consts.update({f"mu_{c}": float(ref[c].mean()) for c in ref})
    consts.update({f"sd_{c}": float(ref[c].std(ddof=0)) for c in ref})
    return val, consts


def window_frame(T: int, group: str, base: pd.DataFrame, up: pd.DataFrame) -> pd.DataFrame:
    d = base[(base.season >= F.FIRST_FEATURE_SEASON) & (base.season <= T - 1)].copy()
    targets = HIT_TARGETS if group == "hitter" else PIT_TARGETS
    u = up[(up.window_T == T) & up.target.isin(targets)]
    for (tgt, model), g in u.groupby(["target", "model"]):
        col = f"F_{tgt}" if model == "ADM" else f"F_{tgt}_B0"
        d = d.merge(g[["mlbam_id", "feature_season", "forecast"]].rename(columns={"feature_season": "season", "forecast": col}),
                    on=["mlbam_id", "season"], how="left")
    ref = d.season <= T - 2
    d["y_VAL_H" if group == "hitter" else "y_VAL_P"], _ = roto_value(d, group, ref)
    d["window_T"] = T
    return d


# ----------------------------------------------------------------------------- model specifications
def specs(group: str, outcomes: list[str]):
    bf = BF_H if group == "hitter" else BF_P
    targets = HIT_TARGETS if group == "hitter" else PIT_TARGETS
    joint = [f"F_{t}" for t in targets if t != "fld"]
    S = {"BF": (bf, None), "BF@fld": (bf, "F_fld") if group == "hitter" else None,
         "BF+joint": (bf + joint, None), "BF+joint_B0": (bf + [f"{c}_B0" for c in joint], None)}
    for t in targets:
        sub = "F_fld" if t == "fld" else None
        S[f"BF+{t}"] = (bf + [f"F_{t}"], sub)
        S[f"BF+{t}_B0"] = (bf + [f"F_{t}_B0"], sub)
    for m in DIRECT[group]:
        S[f"BF+{m}"] = (bf + [m], None)
    return {k: v for k, v in S.items() if v is not None}


def comparisons(group: str, outcomes: list[str]):
    targets = HIT_TARGETS if group == "hitter" else PIT_TARGETS
    rows = []
    for o in outcomes:
        for t in targets:
            base = "BF@fld" if t == "fld" else "BF"
            rows.append({"outcome": o, "kind": "target_forecast_added", "target": t, "base": base, "aug": f"BF+{t}",
                         "family": "primary" if (t, o) in PRIMARY else "secondary_single"})
            rows.append({"outcome": o, "kind": "admitted_vs_history_target_forecast", "target": t, "base": f"BF+{t}_B0", "aug": f"BF+{t}", "family": "secondary_b0_vs_adm"})
        rows.append({"outcome": o, "kind": "joint_target_forecasts", "target": "+".join(t for t in targets if t != "fld"), "base": "BF", "aug": "BF+joint", "family": "secondary_joint"})
        rows.append({"outcome": o, "kind": "joint_admitted_vs_history", "target": "+".join(t for t in targets if t != "fld"), "base": "BF+joint_B0", "aug": "BF+joint", "family": "secondary_joint"})
        for m, outs in DIRECT[group].items():
            if o in outs:
                rows.append({"outcome": o, "kind": "direct_metric_added", "target": m, "base": "BF", "aug": f"BF+{m}", "family": "secondary_direct"})
    return rows


def fit_task(T: int, group: str, outcome: str, d: pd.DataFrame, S: dict) -> pd.DataFrame:
    y = f"y_{outcome}"
    frames = []
    for name, (feats, subset) in S.items():
        dd = d if subset is None else d[d[subset].notna()]
        dd = dd[dd[y].notna()] if outcome not in RATE else dd
        train = dd[(dd.season <= T - 2) & dd[y].notna()].copy()
        test = dd[dd.season == T - 1].copy()
        if outcome in RATE:
            train["model_weight"] = train[f"w_{outcome}"]
        else:
            train["model_weight"] = 1.0
        pred, alpha, use = F.fit_ridge(train, test, feats, y, T, tuned=True)
        frames.append(pd.DataFrame({"window_T": T, "group": group, "outcome": outcome, "model": name, "mlbam_id": test.mlbam_id.to_numpy(),
                                    "season": test.season.to_numpy(), "outcome_season": T, "y": test[y].to_numpy(float),
                                    "w": test[f"w_{outcome}"].to_numpy(float) if outcome in RATE else 1.0, "pred": pred,
                                    "alpha": alpha, "n_features": len(use), "n_train": len(train)}))
    return pd.concat(frames, ignore_index=True)


def evaluate(pred: pd.DataFrame, comps: list[dict], years: list[int], label: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    res, by_year = [], []
    P = pred[pred.outcome_season.isin(years)]
    for c in comps:
        o = c["outcome"]
        a = P[(P.outcome == o) & (P.model == c["aug"])][["mlbam_id", "season", "outcome_season", "y", "w", "pred"]]
        b = P[(P.outcome == o) & (P.model == c["base"])][["mlbam_id", "season", "pred"]]
        m = a.merge(b, on=["mlbam_id", "season"], suffixes=("_aug", "_base")).dropna(subset=["y"])
        if m.empty:
            continue
        r = F.paired_bootstrap(m, "pred_aug", "pred_base")
        r.update(F.season_block_bootstrap(m, "pred_aug", "pred_base") if len(years) > 1 else {})
        yrs = []
        for T, g in m.groupby("outcome_season"):
            ra, rb = F.wrmse(g.y, g.pred_aug, g.w), F.wrmse(g.y, g.pred_base, g.w)
            yrs.append(ra < rb)
            by_year.append({**c, "sample": label, "outcome_season": int(T), "n": len(g), "rmse_base": rb, "rmse_aug": ra,
                            "delta_rmse": ra - rb, "delta_pct": 100 * (ra - rb) / rb})
        res.append({**c, "sample": label, "units": UNITS[o], **r, "years_improved": int(np.sum(yrs)), "n_years": len(yrs)})
    return pd.DataFrame(res), pd.DataFrame(by_year)


def level1(up: pd.DataFrame, frames: dict) -> pd.DataFrame:
    rows = []
    for group, d in frames.items():
        targets = HIT_TARGETS if group == "hitter" else PIT_TARGETS
        outs = ["R", "HR", "RBI", "SB", "AVG", "AB", "VAL_H"] if group == "hitter" else ["W", "SV", "K", "ERA", "WHIP", "IP", "VAL_P"]
        for t in targets:
            for o in outs:
                ss = []
                for T in F.WINDOWS:
                    g = d[T][(d[T].season == T - 1)][[f"F_{t}", f"y_{o}", "mlbam_id"]].dropna()
                    if len(g) > 10:
                        ss.append((T, g))
                prim = pd.concat([g.assign(T=T) for T, g in ss if T <= 2025])
                rho = prim[[f"F_{t}", f"y_{o}"]].corr(method="spearman").iloc[0, 1]
                rng = np.random.default_rng(F.SEED)
                ids = prim.mlbam_id.unique()
                boots = []
                grp = {k: v for k, v in prim.groupby("mlbam_id")}
                for _ in range(500):
                    pick = rng.choice(ids, len(ids))
                    bb = pd.concat([grp[i] for i in pick])
                    boots.append(bb[[f"F_{t}", f"y_{o}"]].corr(method="spearman").iloc[0, 1])
                per = {f"rho_{T}": round(float(g[[f"F_{t}", f"y_{o}"]].corr(method="spearman").iloc[0, 1]), 3) for T, g in ss}
                rows.append({"group": group, "target_forecast": t, "fantasy_outcome": o, "n_2021_2025": len(prim), "spearman_2021_2025": round(float(rho), 3),
                             "ci_low": round(float(np.quantile(boots, 0.025)), 3), "ci_high": round(float(np.quantile(boots, 0.975)), 3), **per,
                             "note": "association only (Level 1); not incremental value"})
    return pd.DataFrame(rows)


def main():
    wcfg = load_weights()
    H, P = season_tables()
    pool = pd.read_parquet(F.LOCAL / "pools.parquet")
    up = pd.read_parquet(F.LOCAL / "out_of_time_upstream_forecasts.parquet")
    base = {"hitter": attach_outcomes(hitter_features(H, pool[pool.group == "hitter"]), H, HIT_COUNTS, wcfg, "hitter"),
            "pitcher": attach_outcomes(pitcher_features(P, pool[pool.group == "pitcher"]), P, PIT_COUNTS, wcfg, "pitcher")}
    frames = {g: {T: window_frame(T, g, base[g], up) for T in F.WINDOWS} for g in base}
    outs = {"hitter": ["R", "HR", "RBI", "SB", "AVG", "AB", "VAL_H"] + (["PTS_H"] if wcfg else []),
            "pitcher": ["W", "SV", "K", "ERA", "WHIP", "IP", "VAL_P"] + (["PTS_P"] if wcfg else [])}
    # Level 3 also needs predictions of the ratio components' ingredients
    level3_extra = {"hitter": ["H"], "pitcher": ["ER", "BBH"]}
    tasks = [(T, g, o) for g in base for T in F.WINDOWS for o in outs[g] + level3_extra[g]]
    res = Parallel(n_jobs=10, backend="loky")(delayed(fit_task)(T, g, o, frames[g][T], specs(g, outs[g])) for T, g, o in tasks)
    pred = pd.concat(res, ignore_index=True)
    pred.to_parquet(F.LOCAL / "downstream_predictions.parquet", index=False)
    for g in base:
        pd.concat(frames[g].values()).to_parquet(F.LOCAL / f"downstream_frames_{g}.parquet", index=False)

    comps = [c | {"group": g} for g in base for c in comparisons(g, outs[g])]
    prim, by_p = evaluate(pred, comps, F.PRIMARY_YEARS, "2021-2025 pooled (primary)")
    expl, by_e = evaluate(pred, comps, F.EXPLORATORY_YEARS, "2026 (exploratory)")
    allr = pd.concat([prim, expl], ignore_index=True)
    # multiplicity: Holm across the 8 primary rows; BH within each secondary family (2021-2025 sample only)
    allr["p_adjusted"] = np.nan
    allr["adjustment"] = ""
    pm = (allr["sample"].str.startswith("2021")) & allr.family.eq("primary")
    allr.loc[pm, "p_adjusted"] = F.holm(allr.loc[pm, "p_two_sided"]).to_numpy()
    allr.loc[pm, "adjustment"] = "Holm (8 primary)"
    for fam in allr.family.unique():
        if fam == "primary":
            continue
        mm = allr["sample"].str.startswith("2021") & allr.family.eq(fam)
        allr.loc[mm, "p_adjusted"] = F.bh(allr.loc[mm, "p_two_sided"]).to_numpy()
        allr.loc[mm, "adjustment"] = f"BH within {fam}"

    def verdict(r):
        if r["ci_high_pct"] < 0 and (pd.isna(r["p_adjusted"]) or r["p_adjusted"] < 0.05):
            return "adds information" if r["sample"].startswith("2021") else "directional gain (exploratory; CI excludes 0)"
        if r["ci_low_pct"] > 0:
            return "harmful"
        if r["ci_high_pct"] < 0:
            return "gain not robust to multiplicity"
        return "no detectable gain"
    allr["verdict"] = allr.apply(verdict, axis=1)
    cols = ["group", "outcome", "units", "kind", "target", "base", "aug", "family", "sample", "n_rows", "n_players", "rmse_b", "rmse_a",
            "delta_rmse", "delta_pct", "ci_low_pct", "ci_high_pct", "season_block_ci_low_pct", "season_block_ci_high_pct", "mae_b", "mae_a",
            "p_two_sided", "p_adjusted", "adjustment", "years_improved", "n_years", "verdict"]
    out = allr.rename(columns={"rmse_b": "rmse_b", "rmse_a": "rmse_a"})[cols].rename(columns={"rmse_b": "rmse_base", "rmse_a": "rmse_aug", "mae_b": "mae_base", "mae_a": "mae_aug"})
    out.to_csv(F.FANTASY / "results_by_target_category.csv", index=False)
    allr.to_csv(F.FANTASY / "paired_uncertainty.csv", index=False)
    pd.concat([by_p, by_e]).to_csv(F.FANTASY / "by_year.csv", index=False)
    level1(up, frames).to_csv(F.FANTASY / "level1_correlations.csv", index=False)
    show = out[out["sample"].str.startswith("2021") & out.family.isin(["primary", "secondary_joint"])]
    print(show[["group", "outcome", "target", "aug", "base", "delta_pct", "ci_low_pct", "ci_high_pct", "p_adjusted", "years_improved", "verdict"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
