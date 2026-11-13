"""FB Level 0: fantasy-category outcomes, forecast-date pools, mapping and coverage (protocol §2–§4, §9).

Outputs
  local/fantasy/category_outcomes.parquet   player-season totals 2015-2026 (rights-restricted; git-ignored)
  local/fantasy/pools.parquet               forecast-date pools (feature season t, outcome season t+1)
  fantasy/mapping_and_coverage.csv          category definitions, sources, availability, pool coverage
  fantasy/cohort_by_year.csv                pool size, returners, floors, canonical t+1 eligibility, zero shares
  fantasy/target_category_map.csv           pre-specified target -> category linkages (primary flags from protocol §7)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import fb_lib as F

HIT_MAP = {"gamesPlayed": "G", "plateAppearances": "PA", "atBats": "AB", "hits": "H", "doubles": "2B", "triples": "3B",
           "homeRuns": "HR", "runs": "R", "rbi": "RBI", "stolenBases": "SB", "caughtStealing": "CS", "baseOnBalls": "BB",
           "intentionalWalks": "IBB", "hitByPitch": "HBP", "strikeOuts": "SO", "groundIntoDoublePlay": "GIDP", "sacFlies": "SF",
           "totalBases": "TB"}
PIT_MAP = {"gamesPitched": "G", "gamesStarted": "GS", "outs": "OUTS", "wins": "W", "losses": "L", "saves": "SV",
           "saveOpportunities": "SVO", "holds": "HLD", "blownSaves": "BS", "strikeOuts": "K", "baseOnBalls": "BB",
           "intentionalWalks": "IBB", "hits": "H", "earnedRuns": "ER", "runs": "RA", "homeRuns": "HR", "hitBatsmen": "HBP",
           "completeGames": "CG", "shutouts": "SHO", "wildPitches": "WP", "battersFaced": "BF", "gamesFinished": "GF"}


def raw_tables():
    h = pd.concat([pd.read_parquet(F.DATA / "raw/mlb_hitting_2015_2025.parquet"), pd.read_parquet(F.RAW_2026 / "mlb_hitting_2026.parquet")])
    p = pd.concat([pd.read_parquet(F.DATA / "raw/mlb_pitching_2015_2025.parquet"), pd.read_parquet(F.RAW_2026 / "mlb_pitching_2026.parquet")])
    assert not h.duplicated(["mlbam_id", "season"]).any() and not p.duplicated(["mlbam_id", "season"]).any()
    H = h[["mlbam_id", "season", "full_name", *HIT_MAP]].rename(columns=HIT_MAP)
    P = p[["mlbam_id", "season", "full_name", *PIT_MAP]].rename(columns=PIT_MAP)
    for d, cols in ((H, HIT_MAP.values()), (P, PIT_MAP.values())):
        for c in cols:
            d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)
    P["IP"] = P["OUTS"] / 3.0  # never parse the ".1/.2" inningsPitched text
    H["1B"] = H["H"] - H["2B"] - H["3B"] - H["HR"]
    H["group"], P["group"] = "hitter", "pitcher"
    return H, P


def pools() -> pd.DataFrame:
    hl = F.load_labeled("hitting_woba")
    pl = F.load_labeled("pitching_fip")
    hp = hl[F.year_t_eligible("hitting_woba", hl) & hl.season.between(2015, 2025)]
    pp = pl[F.year_t_eligible("pitching_fip", pl) & pl.season.between(2015, 2025)]
    keep_h = ["mlbam_id", "season", "name", "age", "pa", "primary_position", "position_group", "xwoba_w2", "sprint_speed", "barrel_pct", "k_pct", "bb_pct"]
    keep_p = ["mlbam_id", "season", "name", "age", "ip", "starter_role", "gs_share", "stuff_plus", "k_pct", "k_bb_pct", "bb_pct"]
    a = hp[[c for c in keep_h if c in hp.columns]].assign(group="hitter")
    b = pp[[c for c in keep_p if c in pp.columns]].assign(group="pitcher")
    out = pd.concat([a, b], ignore_index=True)
    out["outcome_season"] = out["season"] + 1
    return out


def main():
    H, P = raw_tables()
    outcomes = pd.concat([H, P], ignore_index=True)
    outcomes.to_parquet(F.LOCAL / "category_outcomes.parquet", index=False)
    pool = pools()
    pool.to_parquet(F.LOCAL / "pools.parquet", index=False)

    # ---- mapping and coverage
    avail = {g: d.groupby("season").size().to_dict() for g, d in (("hitter", H), ("pitcher", P))}
    rows = []
    spec = [("R", "hitter", "runs", "production", "count"), ("HR", "hitter", "homeRuns", "production", "count"),
            ("RBI", "hitter", "rbi", "production", "count"), ("SB", "hitter", "stolenBases", "production", "count"),
            ("AVG", "hitter", "hits / atBats (aggregated from components)", "rate", "AB>=100 in T; weight AB"),
            ("AB", "hitter", "atBats", "production (playing time; Level 3 input)", "count"),
            ("W", "pitcher", "wins", "production", "count"), ("SV", "pitcher", "saves", "production", "count"),
            ("K", "pitcher", "strikeOuts", "production", "count"),
            ("ERA", "pitcher", "9*earnedRuns / (outs/3)", "rate", "IP>=20 in T; weight IP"),
            ("WHIP", "pitcher", "(baseOnBalls+hits) / (outs/3)", "rate", "IP>=20 in T; weight IP"),
            ("IP", "pitcher", "outs/3", "production (playing time; Level 3 input)", "count")]
    for cat, grp, src, form, evalpop in spec:
        pg = pool[pool.group == grp]
        tab = H if grp == "hitter" else P
        nxt = tab[["mlbam_id", "season", "AB" if grp == "hitter" else "IP"]].copy()
        nxt["season"] -= 1
        j = pg.merge(nxt, on=["mlbam_id", "season"], how="left")
        vol = j.iloc[:, -1]
        floor = 100 if grp == "hitter" else 20
        rows.append({"category": cat, "player_group": grp, "source": "MLB Stats API season totals (data/raw/mlb_*; 2026 from holdout2026/raw_2026)",
                     "construction": src, "form": form, "evaluation_population": evalpop,
                     "seasons_available": f"{min(avail[grp])}-{max(avail[grp])}",
                     "pool_rows_2021_2026": int(pg.outcome_season.between(2021, 2026).sum()),
                     "share_with_any_T_record": round(float(vol.notna().mean()), 3),
                     "share_meeting_rate_floor": round(float((vol.fillna(0) >= floor).mean()), 3) if form == "rate" else None,
                     "derived_by_formula_from_other_metrics": "no"})
    pd.DataFrame(rows).to_csv(F.FANTASY / "mapping_and_coverage.csv", index=False)

    # ---- cohort attrition per outcome season
    canon = {}
    for sid in ("hitting_woba", "pitching_fip"):
        _, sample = F.load_study(sid)
        canon[sid] = set(zip(sample.mlbam_id.astype(int), sample.season.astype(int)))
    frozen = pd.read_parquet(F.RESULTS / "holdout2026/frozen_predictions_2026.parquet")
    coh = []
    for grp, sid, tab, vol, floor in (("hitter", "hitting_woba", H, "PA", 100), ("pitcher", "pitching_fip", P, "IP", 20)):
        pg = pool[pool.group == grp]
        nxt = pd.DataFrame({"mlbam_id": tab["mlbam_id"], "season": tab["season"] - 1, "VOL_T": tab[vol],
                            "FLOOR_T": tab["AB" if grp == "hitter" else "IP"]})
        j = pg.merge(nxt, on=["mlbam_id", "season"], how="left")
        for T, g in j.groupby("outcome_season"):
            if T < 2018:
                continue
            in_canon = np.mean([(int(a), int(b)) in canon[sid] for a, b in zip(g.mlbam_id, g.season)]) if T <= 2025 else np.nan
            coh.append({"player_group": grp, "outcome_season": int(T), "pool_size": len(g),
                        "share_any_T_appearance": round(float((g["VOL_T"].fillna(0) > 0).mean()), 3),
                        "share_zero_counting_outcome": round(float((g["VOL_T"].fillna(0) == 0).mean()), 3),
                        "share_meeting_canonical_t+1_rule": round(float(in_canon), 3) if T <= 2025 else None,
                        "share_meeting_rate_floor": round(float((g["FLOOR_T"].fillna(0) >= floor).mean()), 3),
                        "status": "primary" if 2021 <= T <= 2025 else ("exploratory" if T == 2026 else "training only")})
    pd.DataFrame(coh).to_csv(F.FANTASY / "cohort_by_year.csv", index=False)
    assert frozen.season.eq(2025).all()

    # ---- pre-specified linkage map (protocol §5, §7)
    links = []
    hit_out = ["R", "HR", "RBI", "SB", "AVG", "PTS_H", "VAL_H"]
    pit_out = ["W", "SV", "K", "ERA", "WHIP", "PTS_P", "VAL_P"]
    primary = {("woba", "AVG"), ("woba", "HR"), ("fip", "ERA"), ("fip", "WHIP"), ("br", "SB"), ("fld", "VAL_H"), ("hwar", "VAL_H"), ("pwar", "VAL_P")}
    hyp = {"woba": "offensive rate skill -> AVG, HR, R, RBI, points", "br": "running value -> SB (not identical: SB volume depends on attempts/opportunity)",
           "fld": "boundary case: defense is not scored; any link would run through playing time", "hwar": "broad hitter value -> roto/points value (WAR includes defense, position, replacement level)",
           "fip": "K/BB/HR skill -> ERA, WHIP, K (FIP excludes balls in play and sequencing)", "pwar": "broad pitcher value -> roto/points value (bWAR is runs-allowed based)"}
    for t in ["woba", "br", "fld", "hwar"]:
        for o in hit_out:
            links.append({"target": t, "target_label": F.TARGET_LABEL[t], "fantasy_outcome": o, "family": "primary" if (t, o) in primary else "secondary", "hypothesized_link": hyp[t]})
    for t in ["fip", "pwar"]:
        for o in pit_out:
            links.append({"target": t, "target_label": F.TARGET_LABEL[t], "fantasy_outcome": o, "family": "primary" if (t, o) in primary else "secondary", "hypothesized_link": hyp[t]})
    pd.DataFrame(links).to_csv(F.FANTASY / "target_category_map.csv", index=False)
    print("outcomes", outcomes.shape, "pool", pool.groupby(["group", "outcome_season"]).size().unstack(0).tail(8).to_dict())


if __name__ == "__main__":
    main()
