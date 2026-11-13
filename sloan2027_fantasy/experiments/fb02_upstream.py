"""FB step 2: out-of-time upstream forecasts of the six targets for every forecast-date pool row (protocol §5).

For window T (outcome season of the downstream test rows) and every feature season f in 2017..T-1:
  train = canonical study sample rows with feature season <= f-1   (outcomes <= f)
  test  = labeled-panel rows of season f meeting the study's year-t eligibility (no t+1 filter)
  ADM   = window-T baseline + nested-admission selected set S_T   (ridge alpha=1, canonical weights)
  B0    = window-T history baseline only
For f = T-1 this is exactly the E1 outer-year model (T<=2025) or the frozen 2026 model (T=2026); fb02 checks both.

Outputs
  local/fantasy/out_of_time_upstream_forecasts.parquet      (player-level; git-ignored)
  fantasy/upstream_feature_sets.csv                           (window-specific feature sets; aggregate)
  audits/fb_upstream_consistency.csv                          (max |diff| against E1 predictions / frozen 2026 file)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

import fb_lib as F

STUDIES = F.HITTER_STUDIES + F.PITCHER_STUDIES


def run_study(sid: str) -> tuple[pd.DataFrame, list[dict]]:
    spec, sample = F.load_study(sid)
    lab = F.load_labeled(sid)
    lab = lab[F.year_t_eligible(sid, lab)]
    canon_keys = set(zip(sample.mlbam_id.astype(int), sample.season.astype(int)))
    frames, sets = [], []
    for T in F.WINDOWS:
        meta = F.window_meta(sid, T)
        fs = {"ADM": [*meta["baseline"], *meta["selected"]], "B0": list(meta["baseline"])}
        sets.append({"study_id": sid, "target": F.SHORT[sid], "window_T": T, "baseline": ",".join(meta["baseline"]),
                     "selected": ",".join(meta["selected"]), "n_selected": len(meta["selected"]),
                     "admission_train_seasons": f"{meta['train_seasons'][0]}-{meta['train_seasons'][1]}"})
        for f in range(F.FIRST_FEATURE_SEASON, T):
            train = sample[sample.season <= f - 1].reset_index(drop=True)
            test = lab[lab.season == f].reset_index(drop=True)
            if test.empty:
                continue
            for model, feats in fs.items():
                pred, alpha, use = F.fit_ridge(train, test, feats, spec.target, T, tuned=False)
                frames.append(pd.DataFrame({
                    "study_id": sid, "target": F.SHORT[sid], "window_T": T, "feature_season": f, "outcome_season": f + 1,
                    "mlbam_id": test.mlbam_id.astype(int).to_numpy(), "model": model, "forecast": pred,
                    "y_target": pd.to_numeric(test[spec.target], errors="coerce").to_numpy() if spec.target in test else np.nan,
                    "n_train": len(train), "n_features": len(use),
                    "in_canonical_sample": [(int(a), f) in canon_keys for a in test.mlbam_id]}))
    return pd.concat(frames, ignore_index=True), sets


def consistency(up: pd.DataFrame) -> pd.DataFrame:
    e1 = pd.read_parquet(F.RESULTS / "nested/predictions_default.parquet")
    fr = pd.read_parquet(F.RESULTS / "holdout2026/frozen_predictions_2026.parquet")
    rows = []
    for (sid, T, model), g in up[up.feature_season == up.window_T - 1].groupby(["study_id", "window_T", "model"]):
        if T <= 2025:
            ref = e1[(e1.study_id == sid) & (e1.outer_year == T) & (e1.model_id == f"{model}|ridge")][["mlbam_id", "season", "pred"]]
            m = g.merge(ref, left_on=["mlbam_id", "feature_season"], right_on=["mlbam_id", "season"], how="inner")
            src = "E1 predictions_default.parquet (outcome-observed canonical rows)"
        else:
            ref = fr[(fr.study_id == sid) & (fr.model_id == f"{model}|ridge")][["mlbam_id", "season", "pred"]]
            m = g.merge(ref, left_on=["mlbam_id", "feature_season"], right_on=["mlbam_id", "season"], how="inner")
            src = "frozen_predictions_2026.parquet (all year-t eligible rows)"
        rows.append({"study_id": sid, "window_T": T, "model": model, "reference": src, "n_reference": len(ref),
                     "n_matched": len(m), "n_pool_rows": len(g), "max_abs_diff": float((m.forecast - m.pred).abs().max()) if len(m) else np.nan})
    return pd.DataFrame(rows)


def main():
    res = Parallel(n_jobs=6, backend="loky")(delayed(run_study)(s) for s in STUDIES)
    up = pd.concat([r[0] for r in res], ignore_index=True)
    up.to_parquet(F.LOCAL / "out_of_time_upstream_forecasts.parquet", index=False)
    pd.DataFrame([s for r in res for s in r[1]]).to_csv(F.FANTASY / "upstream_feature_sets.csv", index=False)
    c = consistency(up)
    c.to_csv(F.AUDITS / "fb_upstream_consistency.csv", index=False)
    print(c.to_string(index=False))
    print("rows", len(up), up.groupby(["study_id", "model"]).size().unstack().to_dict())
    assert (c.n_matched == c.n_reference).all(), "every reference row must be matched"
    assert (c.max_abs_diff < 1e-9).all(), "upstream test-row forecasts must reproduce E1 / frozen predictions"


if __name__ == "__main__":
    main()
