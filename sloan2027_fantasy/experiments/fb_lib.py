"""Shared library for the fantasy-bridge (FB) experiments.

Protocol: sloan2027_fantasy/fantasy/experiment_protocol.md (v1.0, committed before any fantasy model was fit).

The estimator, imputation, weighting and bootstrap code below is copied verbatim in behaviour from
Projection-Signal-Lab `sloan2027/experiments/lib_nested.py` (branch research/sloan-2027 @ 04fddeb), so the
upstream test-row forecasts reproduce the E1 `ADM|ridge` / `B0|ridge` predictions exactly (checked in fb02).
It is copied rather than imported because importing lib_nested redirects the canonical ARTIFACTS folder.

Inputs come from a local Projection-Signal-Lab checkout that holds the rights-restricted data panels:
  PSL_ROOT (env var; default: the author's research worktree). Nothing under PSL_ROOT is modified.
Player-level outputs go to <repo>/local/ (git-ignored). Aggregate outputs go to sloan2027_fantasy/fantasy/.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
FB = REPO / "sloan2027_fantasy"
FANTASY = FB / "fantasy"
AUDITS = FB / "audits"
LOCAL = REPO / "local" / "fantasy"
LOCAL.mkdir(parents=True, exist_ok=True)

PSL_ROOT = Path(os.environ.get("PSL_ROOT", "/Users/Shirin/Future_Predictor/.worktrees/sloan-2027")).resolve()
if not (PSL_ROOT / "src" / "psl").exists():
    raise SystemExit(f"PSL_ROOT={PSL_ROOT} does not contain src/psl — see REPRODUCING.md")
sys.path.insert(0, str(PSL_ROOT / "src"))

from psl.components import studies  # noqa: E402  (side-effect free)
from psl.data.assemble import _ip_threshold  # noqa: E402

DATA = PSL_ROOT / "data"
RESULTS = PSL_ROOT / "sloan2027" / "results"
ADMISSION = RESULTS / "nested" / "admission"
RAW_2026 = PSL_ROOT / "sloan2027" / "holdout2026" / "raw_2026"

PRIMARY_YEARS = [2021, 2022, 2023, 2024, 2025]
EXPLORATORY_YEARS = [2026]
WINDOWS = PRIMARY_YEARS + EXPLORATORY_YEARS
FIRST_FEATURE_SEASON = 2017          # downstream training rows: feature seasons 2017..T-2 (outcomes 2018..T-1)
COVID = 2020
COVID_SCALE = 162.0 / 60.0
SEED = 42
N_BOOT = 2000

HITTER_STUDIES = ["hitting_woba", "baserunning_rv", "defense_rv", "overall_war"]
PITCHER_STUDIES = ["pitching_fip", "pitcher_war"]
SHORT = {"hitting_woba": "woba", "baserunning_rv": "br", "defense_rv": "fld", "overall_war": "hwar",
         "pitching_fip": "fip", "pitcher_war": "pwar"}
TARGET_LABEL = {"woba": "wOBA", "br": "baserunning run-value rate", "fld": "fielding run-value rate",
                "hwar": "hitter bWAR/600 PA", "fip": "FIP", "pwar": "pitcher bWAR/200 IP"}
LABELED = {"hitting_woba": "hitter_labeled", "pitching_fip": "pitcher_labeled", "baserunning_rv": "baserunning_labeled",
           "defense_rv": "defense_labeled", "overall_war": "war_hitter_labeled", "pitcher_war": "war_pitcher_labeled"}


# ----------------------------------------------------------------------------- study data
def load_study(sid: str):
    """Identical to lib_nested.load."""
    spec = studies()[sid]
    sample = pd.read_parquet(spec.sample_path).reset_index(drop=True)
    if spec.weight_col and spec.weight_col in sample.columns:
        sample["model_weight"] = pd.to_numeric(sample[spec.weight_col], errors="coerce")
    sample["season"] = sample["season"].astype(int)
    return spec, sample


def load_labeled(sid: str) -> pd.DataFrame:
    spec = studies()[sid]
    lab = pd.read_parquet(DATA / "processed" / f"{LABELED[sid]}.parquet")
    if spec.weight_col:
        lab["model_weight"] = pd.to_numeric(lab[spec.weight_col], errors="coerce")
    lab = lab[pd.to_numeric(lab["season"], errors="coerce").notna()].copy()
    lab["season"] = lab["season"].astype(int)
    return lab


def year_t_eligible(sid: str, d: pd.DataFrame) -> pd.Series:
    """Year-t part of each canonical eligibility rule (identical to e2_frozen_predictions.year_t_eligible)."""
    if sid in ("hitting_woba", "baserunning_rv", "overall_war"):
        return pd.to_numeric(d["pa"], errors="coerce") >= 150
    if sid == "pitching_fip":
        thr = _ip_threshold(d["season"], d["starter_role"], 80.0, 30.0)
        return pd.to_numeric(d["ip"], errors="coerce") >= thr
    if sid == "defense_rv":
        return pd.to_numeric(d["def_inn"], errors="coerce").fillna(0) >= 200
    return pd.Series(True, index=d.index)  # pitcher_war: canonical sample has no workload floor


def window_meta(sid: str, T: int) -> dict:
    return json.loads((ADMISSION / f"{sid}_T{T}_default_meta.json").read_text())


# ----------------------------------------------------------------------------- estimators (from lib_nested)
def weights(df: pd.DataFrame) -> np.ndarray:
    for c in ("model_weight", "pa", "ip", "def_inn"):
        if c in df.columns:
            return np.clip(pd.to_numeric(df[c], errors="coerce").fillna(1.0).to_numpy(float), 1.0, None)
    return np.ones(len(df))


def _impute(train: pd.DataFrame, test: pd.DataFrame, feats: list[str], min_cov: float = 0.05):
    use = [f for f in dict.fromkeys(feats) if f in train.columns and pd.api.types.is_numeric_dtype(train[f])
           and train[f].notna().mean() >= min_cov]
    med = train[use].median()
    return train[use].fillna(med).to_numpy(float), test[use].fillna(med).to_numpy(float), use


def _ridge(alpha: float):
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    return Pipeline([("s", StandardScaler()), ("m", Ridge(alpha=alpha))])


def _fit_pred(alpha, xtr, ytr, wtr, xte):
    est = _ridge(alpha)
    est.fit(xtr, ytr, m__sample_weight=wtr)
    return est.predict(xte)


def wrmse(y, p, w) -> float:
    return float(np.sqrt(np.average((np.asarray(y) - np.asarray(p)) ** 2, weights=w)))


GRID_TUNED = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]


def inner_folds(train: pd.DataFrame, T: int, inner_start: int = 2018):
    for Y in range(inner_start, T):
        tr = train[train["season"] <= Y - 2]
        te = train[train["season"] == Y - 1]
        if len(tr) >= 40 and len(te) >= 15:
            yield Y, tr, te


def fit_ridge(train: pd.DataFrame, test: pd.DataFrame, feats: list[str], target: str, T: int, tuned: bool):
    """tuned=False: alpha=1 (canonical admission ridge). tuned=True: alpha chosen on inner chronological folds."""
    best = 1.0
    if tuned:
        scores = []
        for a in GRID_TUNED:
            errs = []
            for _, tr, te in inner_folds(train, T):
                xtr, xte, _ = _impute(tr, te, feats)
                errs.append(wrmse(te[target].to_numpy(float), _fit_pred(a, xtr, tr[target].to_numpy(float), weights(tr), xte), weights(te)))
            scores.append(np.mean(errs) if errs else np.inf)
        best = GRID_TUNED[int(np.argmin(scores))]
    xtr, xte, use = _impute(train, test, feats)
    pred = _fit_pred(best, xtr, train[target].to_numpy(float), weights(train), xte)
    return pred, best, use


# ----------------------------------------------------------------------------- uncertainty
def paired_bootstrap(df: pd.DataFrame, col_a: str, col_b: str, y: str = "y", w: str = "w",
                     cluster: str = "mlbam_id", n_boot: int = N_BOOT, seed: int = SEED) -> dict:
    """ΔRMSE = RMSE(a) − RMSE(b) on pooled weighted errors, resampling clusters (players). Same logic as
    lib_nested.paired_cluster_bootstrap, plus percentage scale and a two-sided p-value."""
    m = df[[cluster, y, w, col_a, col_b]].dropna()
    ea = m[w] * (m[y] - m[col_a]) ** 2
    eb = m[w] * (m[y] - m[col_b]) ** 2
    g = pd.DataFrame({"c": m[cluster].to_numpy(), "w": m[w].to_numpy(), "ea": ea.to_numpy(), "eb": eb.to_numpy()}).groupby("c").sum()
    sw, sa, sb = g["w"].to_numpy(), g["ea"].to_numpy(), g["eb"].to_numpy()
    ra, rb = np.sqrt(sa.sum() / sw.sum()), np.sqrt(sb.sum() / sw.sum())
    rng = np.random.default_rng(seed)
    P = len(g)
    counts = np.vstack([np.bincount(rng.integers(0, P, P), minlength=P) for _ in range(n_boot)]).astype(float)
    tw, ta, tb = counts @ sw, counts @ sa, counts @ sb
    d = np.sqrt(ta / tw) - np.sqrt(tb / tw)
    dpct = 100 * d / np.sqrt(tb / tw)
    p2 = min(1.0, 2 * min((1 + (d >= 0).sum()) / (n_boot + 1), (1 + (d <= 0).sum()) / (n_boot + 1)))
    mae_a = float(np.average((m[y] - m[col_a]).abs(), weights=m[w]))
    mae_b = float(np.average((m[y] - m[col_b]).abs(), weights=m[w]))
    return {"rmse_a": float(ra), "rmse_b": float(rb), "delta_rmse": float(ra - rb), "delta_pct": float(100 * (ra - rb) / rb),
            "ci_low": float(np.quantile(d, 0.025)), "ci_high": float(np.quantile(d, 0.975)),
            "ci_low_pct": float(np.quantile(dpct, 0.025)), "ci_high_pct": float(np.quantile(dpct, 0.975)),
            "p_two_sided": float(p2), "mae_a": mae_a, "mae_b": mae_b, "n_rows": int(len(m)), "n_players": int(P), "n_boot": n_boot}


def season_block_bootstrap(df: pd.DataFrame, col_a: str, col_b: str, y="y", w="w", season="outcome_season",
                           n_boot: int = N_BOOT, seed: int = SEED) -> dict:
    """Resample whole outcome seasons with replacement (few seasons -> coarse; reported as sensitivity)."""
    m = df[[season, y, w, col_a, col_b]].dropna()
    g = m.assign(ea=m[w] * (m[y] - m[col_a]) ** 2, eb=m[w] * (m[y] - m[col_b]) ** 2).groupby(season)[[w, "ea", "eb"]].sum()
    sw, sa, sb = g[w].to_numpy(), g["ea"].to_numpy(), g["eb"].to_numpy()
    rng = np.random.default_rng(seed)
    S = len(g)
    counts = np.vstack([np.bincount(rng.integers(0, S, S), minlength=S) for _ in range(n_boot)]).astype(float)
    tw, ta, tb = counts @ sw, counts @ sa, counts @ sb
    dpct = 100 * (np.sqrt(ta / tw) - np.sqrt(tb / tw)) / np.sqrt(tb / tw)
    return {"season_block_ci_low_pct": float(np.quantile(dpct, 0.025)), "season_block_ci_high_pct": float(np.quantile(dpct, 0.975)), "n_seasons": int(S)}


def holm(p: pd.Series) -> pd.Series:
    p = p.astype(float)
    order = p.sort_values().index
    m = len(p)
    adj, running = {}, 0.0
    for i, idx in enumerate(order):
        running = max(running, min(1.0, (m - i) * p[idx]))
        adj[idx] = running
    return pd.Series(adj).reindex(p.index)


def bh(p: pd.Series) -> pd.Series:
    p = p.astype(float)
    m = len(p)
    order = p.sort_values(ascending=False).index
    adj, running = {}, 1.0
    for rank_from_top, idx in enumerate(order):
        k = m - rank_from_top
        running = min(running, p[idx] * m / k)
        adj[idx] = min(1.0, running)
    return pd.Series(adj).reindex(p.index)


def sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
