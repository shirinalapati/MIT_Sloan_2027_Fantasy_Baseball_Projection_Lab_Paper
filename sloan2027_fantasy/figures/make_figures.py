"""Publication figures for the revised manuscript (Figs 1-7). Every plotted value is written to figures/data/*.csv.

Palette: dataviz reference categorical slots (validated: adjacent CVD ΔE ≥ 9.1, normal-vision ≥ 19.6 on #fcfcfb;
first three slots pass all-pairs). Contrast WARN for aqua/yellow/magenta is relieved with direct labels.
Run:  PSL_ROOT=... python sloan2027_fantasy/figures/make_figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import fb_lib as F  # noqa: E402

OUT = Path(__file__).resolve().parent
DATA = OUT / "data"
DATA.mkdir(exist_ok=True)
S27 = F.PSL_ROOT / "sloan2027"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"
INK, INK2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
mpl.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.titlesize": 8.5, "axes.titleweight": "bold", "axes.labelsize": 8,
                     "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": BASE, "axes.linewidth": 0.8, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.labelcolor": INK, "text.color": INK, "grid.color": GRID, "grid.linewidth": 0.6, "savefig.dpi": 300,
                     "pdf.fonttype": 42, "svg.fonttype": "none", "axes.titlelocation": "left", "legend.frameon": False})
TARGET_ORDER = ["hitting_woba", "pitching_fip", "baserunning_rv", "defense_rv", "overall_war", "pitcher_war"]
TLABEL = {"hitting_woba": "wOBA", "pitching_fip": "FIP", "baserunning_rv": "Baserunning rate", "defense_rv": "Fielding rate",
          "overall_war": "Hitter bWAR/600 PA", "pitcher_war": "Pitcher bWAR/200 IP"}
CANON = {"hitting_woba": "admission_hitting_y_woba", "pitching_fip": "admission_pitching_y_fip", "baserunning_rv": "admission_baserunning_y_br_rv_rate",
         "defense_rv": "admission_defense_y_def_rv_rate", "overall_war": "admission_overall_y_war_rate", "pitcher_war": "admission_pitcher_overall_y_war_rate"}


def m(txt: str) -> str:
    """Typographic minus for numbers in annotations."""
    return txt.replace("-", "\u2212")


def save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def canon(sid):
    return pd.read_parquet(F.PSL_ROOT / "artifacts" / f"{CANON[sid]}.parquet")


# ------------------------------------------------------------------ Figure 1: decision flow
def fig1():
    br = canon("baserunning_rv").set_index("feature").loc["sprint_speed"]
    wo = canon("hitting_woba").set_index("feature").loc["sprint_speed"]
    ex = []
    for lab, r in (("Baserunning rate", br), ("wOBA", wo)):
        ex.append({"target": lab, "delta_rmse": r.oos_rmse_delta, "delta_pct": 100 * r.oos_rmse_delta / r.baseline_rmse,
                   "folds_improved": int(round(r.folds_improved * r.n_folds)), "n_folds": int(r.n_folds), "verdict": r.verdict,
                   "reliability_r": r.reliability_pearson})
    pd.DataFrame(ex).to_csv(DATA / "fig1_sprint_speed_examples.csv", index=False)
    fig, ax = plt.subplots(figsize=(6.5, 3.9))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")

    def box(x, y, w, h, title, body, edge=BLUE, dashed=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=1.0", fc="white", ec=edge, lw=1.1,
                                    ls=(0, (3, 2)) if dashed else "solid"))
        ax.text(x + 1.0, y + h - 1.3, title, fontsize=7.2, fontweight="bold", va="top", color=INK)
        ax.text(x + 1.0, y + h - 4.6, body, fontsize=6.2, va="top", color=INK2, linespacing=1.3)

    def arrow(x0, y0, x1, y1):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=8, lw=0.9, color=INK2))

    y, h = 40, 18.5
    xs = [0.5, 20.6, 40.7, 60.8, 80.9]
    w = 18.2
    box(xs[0], y, w, h, "1  Metric", "season-t value of a\npublic metric (e.g.,\nsprint speed, ft/s)")
    box(xs[1], y, w, h, "2  History baseline", "ridge forecast from\nthe target's own two-\nyear history, age,\nplaying time, park")
    box(xs[2], y, w, h, "3  Add the metric", "the same model\nwith one added\ninput")
    box(xs[3], y, w, h, "4  Paired test", "train on earlier\nseasons only; score\nthe same players in\nt+1 (7 folds 2019–25;\nnested 2021–25)")
    box(xs[4], y, w, h, "5  Verdict", "Projection if every\ngate passes; else a\nlabel from the\ndashed rules")
    for i in range(4):
        arrow(xs[i] + w + 0.3, y + h / 2, xs[i + 1] - 0.4, y + h / 2)
    box(52.8, 16, 46.7, 19.5, "Statistical gates (all must pass for Projection)",
        "material: RMSE falls by ≥ 0.5% of the baseline RMSE\nconsistent: ≥ 60% of folds improve, or the 95% CI is below 0\n"
        "not redundant: survives the feature-family step\nstable: the coefficient changes sign fewer than 2 times\n"
        "coverage ≥ 70%; no harm in most large subgroups")
    arrow(xs[3] + w / 2, y - 0.4, xs[3] + w / 2, 35.9)
    box(0.5, 16, 24, 19.5, "Human rule: role label", "park, environment, age and\nplaying-time inputs are\nlabelled Context whatever\ntheir lift (set in the metric\ncatalog, not learned)", edge=ORANGE, dashed=True)
    box(25.8, 16, 25.5, 19.5, "Human rule: process flag", "after a failed test, metrics\nflagged as process measures\nbecome Diagnostic; the rest\nbecome Exclude (for this\ntarget only)", edge=ORANGE, dashed=True)
    b, wv = ex
    ax.text(0.5, 11.4, "Worked example: the same metric, two jobs (canonical 7-fold evaluation, outcomes 2019–2025)", fontsize=7.0, fontweight="bold")
    ax.text(0.5, 6.9, f"Sprint speed → next-season baserunning rate:  ΔRMSE {m(format(b['delta_pct'], '+.1f'))}% of baseline RMSE; {b['folds_improved']} of {b['n_folds']} folds improved  →  {b['verdict']}",
            fontsize=6.7, color=INK)
    ax.text(0.5, 2.6, f"Sprint speed → next-season wOBA:  ΔRMSE {m(format(wv['delta_pct'], '+.2f'))}%; {wv['folds_improved']} of {wv['n_folds']} folds improved  →  {wv['verdict']}"
            f"  (year-to-year r = {wv['reliability_r']:.2f}: stable, yet no added wOBA information)", fontsize=6.7, color=INK)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color=BLUE, lw=1.2, label="statistical step"), Line2D([], [], color=ORANGE, lw=1.2, ls=(0, (3, 2)), label="human-specified rule")],
              loc="upper right", bbox_to_anchor=(1.0, 1.06), ncol=2, fontsize=6.5)
    save(fig, "fig1_decision_flow")


# ------------------------------------------------------------------ Figure 2: player stories (Stuff+ -> FIP)
def fig2():
    fc = pd.read_parquet(S27 / "results/players/forecast_changes.parquet")
    s = fc[fc.contrast == "pitching_fip:stuff_plus"].copy()
    s["improved"] = s.abs_err_change < 0
    s["dec"] = s.groupby("outer_year").feature_value.transform(lambda x: pd.qcut(x.rank(method="first"), 10, labels=False)) + 1
    dec = s.groupby("dec").agg(n=("change", "size"), mean_stuff=("feature_value", "mean"), mean_forecast_change=("change", "mean"),
                               share_improved=("improved", "mean")).reset_index()
    dec.to_csv(DATA / "fig5_stuff_deciles.csv", index=False)
    pl = pd.read_parquet(F.DATA / "processed/pitcher_labeled.parquet")[["mlbam_id", "season", "arm_angle"]]
    cases = {}
    for name in ("Rogers, Tyler", "Wheeler, Zack"):
        g = s[s.player == name].sort_values("outer_year").merge(pl, on=["mlbam_id", "season"], how="left")
        cases[name] = g
    pd.concat([g.assign(case=n) for n, g in cases.items()])[["case", "season", "outer_year", "feature_value", "arm_angle", "pred_base", "pred_aug", "y", "change", "abs_err_change"]].to_csv(DATA / "fig5_cases.csv", index=False)

    fig = plt.figure(figsize=(6.5, 3.8))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1], hspace=0.66, wspace=0.42)
    titles = {"Rogers, Tyler": "A  Tyler Rogers: submarine (arm angle ≈ {a:.0f}°), Stuff+ {lo:.0f}–{hi:.0f}",
              "Wheeler, Zack": "B  Zack Wheeler: Stuff+ {lo:.0f}–{hi:.0f}"}
    for i, (name, g) in enumerate(cases.items()):
        ax = fig.add_subplot(gs[i, 0])
        x = g.outer_year.to_numpy()
        for xi, b, a, yv in zip(x, g.pred_base, g.pred_aug, g.y):
            ax.annotate("", xy=(xi, a), xytext=(xi, b), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.8, mutation_scale=7))
        ax.scatter(x, g.pred_base, s=26, facecolor="white", edgecolor=BLUE, lw=1.1, zorder=3, label="forecast without Stuff+")
        ax.scatter(x, g.pred_aug, s=26, color=BLUE, zorder=3, label="forecast with Stuff+")
        ax.scatter(x, g.y, s=30, marker="D", color=ORANGE, zorder=3, label="observed FIP")
        ax.set_xticks(x)
        ax.set_ylabel("Next-season FIP")
        ax.grid(axis="y")
        ax.set_axisbelow(True)
        worse = int((g.abs_err_change > 0).sum())
        t = m(titles[name].format(a=g.arm_angle.mean(), lo=g.feature_value.min(), hi=g.feature_value.max()))
        ax.set_title(t, fontsize=7.4)
        verdict = f"Stuff+ moved all {len(g)} forecasts {'up' if g.change.mean() > 0 else 'down'} (mean {g.change.mean():+.2f} FIP); " \
                  f"{worse} of {len(g)} became less accurate"
        ax.text(0.0, -0.36, verdict.replace("mean -", "mean \u2212"), transform=ax.transAxes, fontsize=6.6, color=INK2)
        if i == 0:
            handles, labels = ax.get_legend_handles_labels()
            ax.set_ylim(2.8, 5.2)
    ax1 = fig.add_subplot(gs[0, 1])
    ax1.bar(dec.dec, dec.mean_forecast_change, color=[ORANGE if v > 0 else BLUE for v in dec.mean_forecast_change], width=0.72)
    ax1.axhline(0, color=BASE, lw=0.8)
    ax1.set_xticks(range(1, 11))
    ax1.set_ylabel("Mean change in\nFIP forecast")
    ax1.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: m(f"{v:+.1f}") if v else "0"))
    ax1.set_title("C  Change by Stuff+ decile (1 = lowest)", fontsize=7.6)
    ax1.grid(axis="y")
    ax1.set_axisbelow(True)
    ax2 = fig.add_subplot(gs[1, 1])
    ax2.axhline(50, color=BASE, lw=0.8, ls=(0, (3, 2)))
    ax2.plot(dec.dec, 100 * dec.share_improved, color=INK2, lw=1.0)
    ax2.scatter(dec.dec, 100 * dec.share_improved, color=INK, s=14, zorder=3)
    ax2.set_xticks(range(1, 11))
    ax2.set_ylim(30, 75)
    ax2.set_ylabel("% of forecasts\nmore accurate")
    ax2.set_xlabel("Stuff+ decile within season")
    ax2.set_title("D  Share improved by decile", fontsize=7.6)
    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.03), fontsize=6.8)
    ax2.grid(axis="y")
    ax2.set_axisbelow(True)
    save(fig, "fig5_player_stories_stuff")


# ------------------------------------------------------------------ Figure 3: six-target model comparison
def comparison_rows():
    comp = pd.read_csv(S27 / "results/nested/comparisons_default.csv")
    c26 = pd.read_csv(S27 / "results/holdout2026/comparisons_2026.csv")
    c26 = c26[c26.cohort.str.startswith("retrospective")]
    want = {"ADM vs B0": ("ADM vs B0 (selection policy lift)", "ADM vs B0"), "KS vs ADM": ("KS vs ADM (kitchen minus selective)", "KS vs ADM (kitchen minus selective)"),
            "EN-KS vs ADM": ("EN-KS vs ADM (tuned elastic net on kitchen)", "EN-KS vs ADM"), "LGBM vs ridge (ADM set)": ("LGBM ADM vs ridge ADM", "LGBM ADM vs ridge ADM")}
    rows = []
    for key, (lab_hist, lab_26) in want.items():
        for sid in TARGET_ORDER:
            for sample, df, lab in (("2021–2025 (nested)", comp, lab_hist), ("2026 (exploratory)", c26, lab_26)):
                r = df[(df.study_id == sid) & (df.comparison == lab)]
                if r.empty:
                    continue
                r = r.iloc[0]
                rb = r.delta_rmse / (r.pct_of_b / 100)
                rows.append({"comparison": key, "target": sid, "sample": sample, "delta_pct": r.pct_of_b,
                             "ci_low_pct": 100 * r.ci_low / rb, "ci_high_pct": 100 * r.ci_high / rb, "n_rows": r.n_rows})
    return pd.DataFrame(rows)


def fig3():
    d = comparison_rows()
    d.to_csv(DATA / "fig3_model_comparisons.csv", index=False)
    panels = [("ADM vs B0", "A  Selected vs history baseline"), ("KS vs ADM", "B  All-feature ridge vs selected"),
              ("EN-KS vs ADM", "C  All-feature elastic net vs selected")]
    fig, axes = plt.subplots(1, 3, figsize=(6.5, 3.0), sharey=True)
    for ax, (key, title) in zip(axes, panels):
        g = d[d.comparison == key]
        for i, sid in enumerate(TARGET_ORDER):
            for j, (sample, col, face) in enumerate((("2021–2025 (nested)", BLUE, BLUE), ("2026 (exploratory)", ORANGE, "white"))):
                r = g[(g.target == sid) & (g["sample"] == sample)]
                if r.empty:
                    continue
                r = r.iloc[0]
                yy = i + (j * 0.32 - 0.16)
                ax.plot([r.ci_low_pct, r.ci_high_pct], [yy, yy], color=col, lw=1.4 if j == 0 else 1.0, solid_capstyle="round")
                ax.scatter([r.delta_pct], [yy], s=22, color=face, edgecolor=col, lw=1.1, zorder=3)
        ax.axvline(0, color=INK2, lw=0.8)
        ax.set_title(title, fontsize=7.6)
        ax.grid(axis="x")
        ax.set_axisbelow(True)
        xmin, xmax = ax.get_xlim()
        lim = max(abs(xmin), abs(xmax))
        ax.set_xlim(-lim, lim)
        ax.set_xlabel("← first-named model more accurate", fontsize=6.4, color=INK2, loc="left")
    axes[0].set_yticks(range(len(TARGET_ORDER)))
    axes[0].set_yticklabels([TLABEL[s] for s in TARGET_ORDER])
    axes[0].invert_yaxis()
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=BLUE, marker="o", lw=1.4, label="outer years 2021–2025 (nested selection)"),
         Line2D([], [], color=ORANGE, marker="o", markerfacecolor="white", lw=1.0, label="2026 frozen-in-workflow check (exploratory)")]
    fig.legend(handles=h, loc="upper center", ncol=2, bbox_to_anchor=(0.55, 1.04))
    fig.supxlabel("ΔRMSE as % of the second-named model's RMSE (95% player-cluster bootstrap interval)", fontsize=7.4, y=-0.06)
    fig.subplots_adjust(wspace=0.12)
    save(fig, "fig3_model_comparisons")


# ------------------------------------------------------------------ Figure 4: classification map
def fig4():
    rc = pd.read_csv(S27 / "tables/table7_reason_codes_208.csv")
    cats = [("Projection", "Projection (statistical pass)", BLUE),
            ("Diagnostic — predictive alone, redundant with a kept family member", "Diagnostic: predictive alone, redundant with a kept family member", ORANGE),
            ("Diagnostic — no material incremental lift", "Diagnostic: no material lift (human process flag)", AQUA),
            ("Exclude — no material incremental lift", "Exclude: no material lift, no process flag", YELLOW),
            ("Context (role/environment)", "Context: human-specified role (park, age, playing time)", MAGENTA)]
    tab = rc.groupby(["study_id", "reason_code"]).size().unstack(fill_value=0).reindex(TARGET_ORDER).fillna(0)
    tab = tab[[c for c, _, _ in cats if c in tab.columns]]
    tab.to_csv(DATA / "fig2_reason_codes_by_target.csv")
    fig, ax = plt.subplots(figsize=(6.5, 2.75))
    left = np.zeros(len(tab))
    for code, lab, col in cats:
        v = tab[code].to_numpy() if code in tab else np.zeros(len(tab))
        ax.barh(range(len(tab)), v, left=left, color=col, edgecolor="white", lw=1.0, height=0.66, label=lab)
        for i, (l, vv) in enumerate(zip(left, v)):
            if vv >= 2:
                ax.text(l + vv / 2, i, f"{int(vv)}", ha="center", va="center", fontsize=6.8, color="#0b0b0b" if col in (YELLOW, AQUA, MAGENTA) else "white", fontweight="bold")
        left += v
    for i, tot in enumerate(left):
        ax.text(tot + 0.8, i, f"{int(tot)}", va="center", fontsize=7, color=INK2)
    ax.set_yticks(range(len(tab)))
    ax.set_yticklabels([TLABEL[s] for s in tab.index])
    ax.invert_yaxis()
    ax.set_xlabel("Number of candidate metrics evaluated for the target (208 in total; canonical 7-fold evaluation)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.25), ncol=2, fontsize=6.6, handlelength=1.2, columnspacing=1.0)
    ax.grid(axis="x")
    ax.set_axisbelow(True)
    save(fig, "fig2_classification_map")


# ------------------------------------------------------------------ Figure 5: fantasy linkage matrix
MARK = {"adds information": dict(marker="o", fillstyle="full"), "gain not robust to multiplicity": dict(marker="o", fillstyle="left"),
        "no detectable gain": dict(marker="o", fillstyle="none"), "harmful": dict(marker="X", fillstyle="full")}
MLAB = {"adds information": "adds information (95% CI < 0, adjusted p < 0.05)", "gain not robust to multiplicity": "CI < 0, not robust to multiplicity",
        "no detectable gain": "no detectable gain", "harmful": "harmful (CI > 0)"}


def fig5():
    r = pd.read_csv(F.FANTASY / "results_by_target_category.csv")
    r = r[r["sample"].str.startswith("2021") & r.kind.eq("target_forecast_added")]
    has_pts = r.outcome.isin(["PTS_H", "PTS_P"]).any()
    hit_cols = ["R", "HR", "RBI", "SB", "AVG", "VAL_H"] + (["PTS_H"] if has_pts else [])
    pit_cols = ["W", "SV", "K", "ERA", "WHIP", "VAL_P"] + (["PTS_P"] if has_pts else [])
    colname = {"VAL_H": "5×5 value", "VAL_P": "5×5 value", "PTS_H": "Points", "PTS_P": "Points"}
    rows_h, rows_p = ["woba", "br", "fld", "hwar"], ["fip", "pwar"]
    rl = {"woba": "wOBA forecast", "br": "Baserunning forecast", "fld": "Fielding forecast", "hwar": "Hitter bWAR forecast",
          "fip": "FIP forecast", "pwar": "Pitcher bWAR forecast"}
    r[["group", "target", "outcome", "delta_pct", "ci_low_pct", "ci_high_pct", "p_adjusted", "adjustment", "family", "verdict", "n_rows"]].to_csv(DATA / "fig6_fantasy_linkage.csv", index=False)
    cmap = mpl.colors.LinearSegmentedColormap.from_list("div", ["#1c5cab", "#86b6ef", "#f0efec", "#f3a3a2", "#c23b3a"])
    norm = mpl.colors.TwoSlopeNorm(vmin=-2.0, vcenter=0.0, vmax=2.0)
    fig, axes = plt.subplots(2, 1, figsize=(6.5, 4.1), gridspec_kw={"height_ratios": [4, 2], "hspace": 0.5})
    for ax, rows, cols, title in ((axes[0], rows_h, hit_cols, "A  Hitters"), (axes[1], rows_p, pit_cols, "B  Pitchers")):
        for i, t in enumerate(rows):
            for j, o in enumerate(cols):
                c = r[(r.target == t) & (r.outcome == o)]
                if c.empty:
                    ax.add_patch(plt.Rectangle((j, i), 1, 1, fc="white", ec=GRID))
                    continue
                c = c.iloc[0]
                ax.add_patch(plt.Rectangle((j, i), 1, 1, fc=cmap(norm(np.clip(c.delta_pct, -2, 2))), ec="white", lw=1.5))
                if c.family == "primary":
                    ax.add_patch(plt.Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, fill=False, ec=INK, lw=1.3))
                txtcol = "white" if abs(c.delta_pct) > 1.3 else INK
                ax.plot([j + 0.5], [i + 0.36], ms=6.5, color=txtcol, markeredgecolor=txtcol, markeredgewidth=1.0, **MARK[c.verdict])
                ax.text(j + 0.5, i + 0.72, m(f"{c.delta_pct:+.1f}%"), ha="center", va="center", fontsize=6.6, color=txtcol)
        ax.set_xlim(0, len(cols))
        ax.set_ylim(len(rows), 0)
        ax.set_xticks(np.arange(len(cols)) + 0.5)
        ax.set_xticklabels([colname.get(c, c) for c in cols])
        ax.xaxis.tick_top()
        ax.set_yticks(np.arange(len(rows)) + 0.5)
        ax.set_yticklabels([rl[t] for t in rows])
        ax.tick_params(length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(title, fontsize=7.6, pad=16)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], ls="none", color=INK, ms=6, label=MLAB[k], **MARK[k]) for k in MARK]
    h.append(plt.Rectangle((0, 0), 1, 1, fill=False, ec=INK, lw=1.3, label="pre-specified primary linkage (Holm, 8 tests)"))
    fig.legend(handles=h, loc="lower left", ncol=2, bbox_to_anchor=(0.30, -0.10), fontsize=6.4, handlelength=1.2, columnspacing=1.2)
    cax = fig.add_axes([0.05, -0.035, 0.18, 0.016])
    cb = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm, orientation="horizontal", ticks=[-2, 0, 2])
    cb.ax.set_xticklabels([m("-2%"), "0", "+2%"], fontsize=6.2)
    cb.outline.set_visible(False)
    cax.set_title("ΔRMSE (blue = more accurate)", fontsize=6.2, pad=2)
    save(fig, "fig6_fantasy_linkage")


# ------------------------------------------------------------------ Figure 6: illustrative draft backtest
def fig6():
    bt = pd.read_csv(F.FANTASY / "decision_backtest.csv")
    sens = pd.read_csv(F.FANTASY / "ranking_value_sensitivity.csv")
    roto = bt[(bt.format == "roto_5x5")]
    rho = roto.drop_duplicates(["group", "outcome_season"])[["group", "outcome_season", "spearman_base", "spearman_aug"]]
    rho.to_csv(DATA / "fig7_rank_correlation.csv", index=False)
    s = sens[(sens.format == "roto_5x5") & sens["sample"].str.startswith("2021")]
    s.to_csv(DATA / "fig7_topk_value.csv", index=False)
    fig = plt.figure(figsize=(6.5, 4.3))
    gsp = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], hspace=0.62, wspace=0.28)
    axA, axB, axC = fig.add_subplot(gsp[0, 0]), fig.add_subplot(gsp[0, 1]), fig.add_subplot(gsp[1, :])
    for ax, grp, title in ((axA, "hitter", "A  Hitters: rank agreement, predicted vs realized value"), (axB, "pitcher", "B  Pitchers: same measure")):
        g = rho[rho.group == grp].sort_values("outcome_season")
        ax.axvspan(2025.5, 2026.5, color="#f0efec", zorder=0, lw=0)
        ax.plot(g.outcome_season, g.spearman_base, color=BLUE, lw=1.2, marker="o", ms=3.5, markerfacecolor="white", label="category-history baseline")
        ax.plot(g.outcome_season, g.spearman_aug, color=ORANGE, lw=1.2, marker="o", ms=3.5, label="+ target forecasts (hitters: wOBA, baserunning, bWAR; pitchers: FIP, bWAR)")
        ax.set_xticks(list(g.outcome_season))
        ax.set_xticklabels([str(v) if v != 2026 else "2026*" for v in g.outcome_season], fontsize=6.6)
        ax.set_title(title, fontsize=7.4)
        ax.grid(axis="y")
        ax.set_axisbelow(True)
    axA.set_ylabel("Spearman ρ")
    axA.legend(loc="lower right", fontsize=6.3)
    lab = []
    ss = s.sort_values(["group", "k"]).reset_index(drop=True)
    for i, r in ss.iterrows():
        col = BLUE if r.group == "hitter" else ORANGE
        axC.plot([r.ci_low, r.ci_high], [i, i], color=col, lw=1.3)
        axC.scatter([r.delta_mean_realized_value], [i], color=col, s=18, zorder=3)
        lab.append(f"{'Hitters' if r.group == 'hitter' else 'Pitchers'}: top {int(r.k)}" + (" (12-team)" if int(r.k) in (156, 108) else " (15-team)" if int(r.k) in (195, 135) else ""))
    axC.axvline(0, color=INK2, lw=0.8)
    axC.set_yticks(range(len(lab)))
    axC.set_yticklabels(lab, fontsize=6.6)
    axC.invert_yaxis()
    axC.set_xlabel("Difference in mean realized 5×5 value per drafted player, augmented minus baseline (z-score units; 2021–2025, 95% interval)")
    axC.set_title("C  Did the augmented ranking pick better players? Top-k picks by predicted value", fontsize=7.4)
    axC.grid(axis="x")
    axC.set_axisbelow(True)
    fig.text(0.01, -0.01, "* 2026 is exploratory (season already inspected for the six targets).", fontsize=6.2, color=INK2)
    save(fig, "fig7_draft_backtest")


# ------------------------------------------------------------------ Figure 7: year by year
def fig7():
    per = pd.read_csv(S27 / "results/nested/per_year_default.csv")
    c26 = pd.read_csv(S27 / "results/holdout2026/comparisons_2026.csv")
    c26 = c26[c26.cohort.str.startswith("retrospective")]
    rows = []
    for sid in TARGET_ORDER:
        p = per[per.study_id == sid].pivot(index="outer_year", columns="model_id", values="wrmse")
        for T, r in p.iterrows():
            rows.append({"target": sid, "season": int(T), "series": "selected vs baseline", "delta_pct": 100 * (r["ADM|ridge"] - r["B0|ridge"]) / r["B0|ridge"]})
            rows.append({"target": sid, "season": int(T), "series": "all-feature ridge vs selected", "delta_pct": 100 * (r["KS|ridge"] - r["ADM|ridge"]) / r["ADM|ridge"]})
        for lab, series in (("ADM vs B0", "selected vs baseline"), ("KS vs ADM (kitchen minus selective)", "all-feature ridge vs selected")):
            q = c26[(c26.study_id == sid) & (c26.comparison == lab)]
            if len(q):
                q = q.iloc[0]
                rb = q.delta_rmse / (q.pct_of_b / 100)
                rows.append({"target": sid, "season": 2026, "series": series, "delta_pct": q.pct_of_b, "ci_low_pct": 100 * q.ci_low / rb, "ci_high_pct": 100 * q.ci_high / rb})
    d = pd.DataFrame(rows)
    d.to_csv(DATA / "fig4_year_by_year.csv", index=False)
    fig, axes = plt.subplots(2, 3, figsize=(6.5, 3.7), sharex=True)
    for ax, sid in zip(axes.flat, TARGET_ORDER):
        g = d[d.target == sid]
        for series, col, face in (("selected vs baseline", BLUE, BLUE), ("all-feature ridge vs selected", ORANGE, "white")):
            h = g[(g.series == series) & (g.season <= 2025)].sort_values("season")
            ax.plot(h.season, h.delta_pct, color=col, lw=1.1, marker="o", ms=3.4, markerfacecolor=face, label=series)
            q = g[(g.series == series) & (g.season == 2026)]
            if len(q):
                q = q.iloc[0]
                xo = 2025.85 if series == "selected vs baseline" else 2026.15
                ax.plot([xo, xo], [q.ci_low_pct, q.ci_high_pct], color=col, lw=1.0)
                ax.scatter([xo], [q.delta_pct], s=18, color=face, edgecolor=col, lw=1.1, zorder=3)
        ax.axhline(0, color=INK2, lw=0.8)
        ax.axvline(2025.5, color=BASE, lw=0.8, ls=(0, (3, 2)))
        ax.set_title(TLABEL[sid], fontsize=7.6)
        ax.set_xticks([2021, 2022, 2023, 2024, 2025, 2026])
        ax.set_xticklabels(["21", "22", "23", "24", "25", "26"])
        ax.grid(axis="y")
        ax.set_axisbelow(True)
    fig.supylabel("ΔRMSE, % (below 0: first-named model more accurate)", fontsize=7.4, x=0.0)
    fig.supxlabel("Outcome season (2026 shown with its 95% interval; right of the dashed line = exploratory)", fontsize=7.4, y=0.0)
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.03))
    fig.subplots_adjust(hspace=0.45, wspace=0.35)
    save(fig, "fig4_year_by_year")


if __name__ == "__main__":
    which = sys.argv[1:] or ["1", "2", "3", "4", "5", "6", "7"]
    for w in which:
        {"1": fig1, "2": fig4, "3": fig3, "4": fig7, "5": fig2, "6": fig5, "7": fig6}[w]()  # keys = manuscript figure numbers
        print("figure", w, "done", flush=True)
