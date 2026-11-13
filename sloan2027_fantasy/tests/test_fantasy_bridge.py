"""Tests for the fantasy-bridge pipeline (protocol §8). Data-dependent tests skip when the local, rights-restricted
panels (PSL_ROOT) or the git-ignored local outputs are absent, e.g. on a fresh public clone."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
EXP = HERE.parent / "experiments"
sys.path.insert(0, str(EXP))
PSL_ROOT = Path(os.environ.get("PSL_ROOT", "/Users/Shirin/Future_Predictor/.worktrees/sloan-2027"))
HAS_DATA = (PSL_ROOT / "src" / "psl").exists() and (PSL_ROOT / "data" / "raw").exists()
LOCAL = HERE.parents[1] / "local" / "fantasy"
HAS_LOCAL = (LOCAL / "downstream_frames_hitter.parquet").exists()
FANTASY = HERE.parent / "fantasy"
needs_data = pytest.mark.skipif(not HAS_DATA, reason="requires local Projection-Signal-Lab data panels (PSL_ROOT)")
needs_local = pytest.mark.skipif(not (HAS_DATA and HAS_LOCAL), reason="requires local fantasy-bridge outputs (run fb01-fb03)")


def test_ratio_categories_aggregate_components_not_rates():
    """A team's AVG is total H / total AB, never the mean of player AVGs."""
    pytest.importorskip("sklearn")
    if not HAS_DATA:
        pytest.skip("fb03 imports fb_lib, which needs PSL_ROOT")
    import fb03_bridge as B
    df = pd.DataFrame({"y_R": [0, 0], "y_HR": [0, 0], "y_RBI": [0, 0], "y_SB": [0, 0], "y_H": [1.0, 0.0], "y_AB": [1.0, 100.0]})
    _, consts = B.roto_value(df, "hitter", pd.Series([True, True]))
    assert consts["avg_ref"] == pytest.approx(1 / 101)
    assert consts["avg_ref"] != pytest.approx(0.5)


@needs_data
def test_innings_come_from_outs_not_text():
    import fb01_outcomes as O
    _, P = O.raw_tables()
    assert np.allclose(P["IP"], P["OUTS"] / 3.0)
    sample = P[P["OUTS"] % 3 == 2].iloc[0]
    assert sample["IP"] == pytest.approx(int(sample["OUTS"]) / 3.0)  # e.g. "6.2" innings = 20 outs = 6.667 IP


@needs_data
def test_future_target_labels_cannot_change_upstream_forecasts():
    """Perturbing season-T outcomes (feature-season T-1 labels) leaves the forecast for T unchanged."""
    import fb_lib as F
    spec, sample = F.load_study("hitting_woba")
    lab = F.load_labeled("hitting_woba")
    T = 2024
    meta = F.window_meta("hitting_woba", T)
    feats = [*meta["baseline"], *meta["selected"]]
    test = lab[(lab.season == T - 1) & F.year_t_eligible("hitting_woba", lab)].reset_index(drop=True)
    train = sample[sample.season <= T - 2].reset_index(drop=True)
    p1, _, _ = F.fit_ridge(train, test, feats, spec.target, T, tuned=False)
    test2 = test.copy()
    test2[spec.target] = 9.99  # future outcome perturbed
    sample2 = sample.copy()
    sample2.loc[sample2.season == T - 1, spec.target] = -5.0  # season-T labels in the canonical sample perturbed
    train2 = sample2[sample2.season <= T - 2].reset_index(drop=True)
    p2, _, _ = F.fit_ridge(train2, test2, feats, spec.target, T, tuned=False)
    assert np.array_equal(p1, p2)


@needs_local
def test_future_fantasy_outcomes_cannot_change_downstream_forecasts():
    import fb03_bridge as B
    d = pd.read_parquet(LOCAL / "downstream_frames_hitter.parquet")
    T = 2023
    fw = d[d.window_T == T].copy()
    S = {k: v for k, v in B.specs("hitter", ["HR"]).items() if k in ("BF", "BF+woba")}
    a = B.fit_task(T, "hitter", "HR", fw, S)
    fw2 = fw.copy()
    fw2.loc[fw2.season == T - 1, "y_HR"] = 999.0
    b = B.fit_task(T, "hitter", "HR", fw2, S)
    assert np.allclose(a.pred.to_numpy(), b.pred.to_numpy())


@needs_local
def test_nonreturners_score_zero_and_drop_from_ratio_categories():
    d = pd.read_parquet(LOCAL / "downstream_frames_hitter.parquet")
    gone = d[d.y_AB == 0]
    assert len(gone) > 0
    assert (gone[["y_R", "y_HR", "y_RBI", "y_SB"]] == 0).all().all()
    assert gone["y_AVG"].isna().all()


@needs_local
def test_covid_season_counting_outcomes_are_prorated():
    import fb03_bridge as B
    H, _ = B.season_tables()
    d = pd.read_parquet(LOCAL / "downstream_frames_hitter.parquet")
    row = d[(d.season == 2019) & (d.window_T == 2022)].iloc[0]
    raw = H[(H.mlbam_id == row.mlbam_id) & (H.season == 2020)]
    if len(raw):
        assert row["y_HR"] == pytest.approx(raw["HR"].iloc[0] * 162 / 60)


def test_upstream_forecasts_reproduce_e1_and_frozen_predictions():
    c = pd.read_csv(HERE.parent / "audits" / "fb_upstream_consistency.csv")
    assert (c.n_matched == c.n_reference).all()
    assert (c.max_abs_diff < 1e-9).all()
    assert set(c.window_T) == {2021, 2022, 2023, 2024, 2025, 2026}


def test_results_are_real_and_verdicts_match_intervals():
    r = pd.read_csv(FANTASY / "results_by_target_category.csv")
    assert len(r) > 0 and (r.n_rows > 0).all()
    assert np.isfinite(r[["rmse_base", "rmse_aug", "delta_pct", "ci_low_pct", "ci_high_pct"]]).all().all()
    adds = r[r.verdict == "adds information"]
    assert (adds.ci_high_pct < 0).all() and (adds.p_adjusted < 0.05).all()
    harm = r[r.verdict == "harmful"]
    assert (harm.ci_low_pct > 0).all()
    prim = r[r.family.eq("primary") & r["sample"].str.startswith("2021")]
    assert len(prim) == 8 and prim.adjustment.eq("Holm (8 primary)").all()
