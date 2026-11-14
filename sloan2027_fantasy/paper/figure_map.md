# Figure and table map (revised manuscript)

**Figures.**
- All figures come from `sloan2027_fantasy/figures/make_figures.py`. Each is saved as PNG at 300 dpi, plus PDF and SVG.
- The plotted values are written to `figures/data/`.
- Text is at least 7 pt at print size.
- `build_manuscript.py` checks that each figure's position in the paper matches the `figN_` prefix of its file.

**Palette.** The colors are the reference categorical slots of the dataviz validator, checked on #fcfcfb:
- worst adjacent color-vision-deficiency ΔE: 9.1;
- worst normal-vision ΔE: 19.6;
- the first three slots pass the all-pairs check;
- the low-contrast slots also carry direct labels.

**Path roots.** `S27/` is `sloan2027/` in the Projection-Signal-Lab checkout (`PSL_ROOT`). `RC/` is `fantasy/referee_checks/`. Post hoc material comes from protocol Amendment 2.

| # | File | Claim it carries | Data |
|---|---|---|---|
| Fig 1 | `fig1_decision_flow` | How admission works. It separates statistical steps from human-specified rules (role, process flag, feature families). The example is sprint speed: admitted for baserunning, Diagnostic for wOBA. | `data/fig1_sprint_speed_examples.csv` (canonical artifacts, commit 17da742) |
| Fig 2 | `fig2_classification_map` | What the 208 canonical evaluations concluded, by target and reason code. The 27 Projection labels are split three ways: 6 are the baselines' own two-year inputs, 4 are other windows of the target's own history, and 17 are other metrics. Context labels and the Diagnostic/Exclude split are human labels. | `data/fig2_reason_codes_by_target.csv` |
| Fig 3 | `fig3_model_comparisons` | Selected model versus three references on identical players: the history baseline, an all-metric ridge, and a tuned elastic net. Covers nested 2021–2025 and the 2026 check. Direction labels are on each panel. | `data/fig3_model_comparisons.csv` |
| Fig 4 | `fig4_year_by_year` | Season-by-season view of the two central comparisons. The selective advantage over the all-metric ridge shrinks as training seasons accumulate, and in 2026 the all-metric ridge beats selection for FIP. Only the 2026 points carry intervals. | `data/fig4_year_by_year.csv` |
| Fig 5 | `fig5_player_stories_stuff` | Stuff+ in FIP units: Tyler Rogers (failure, submarine delivery), Zack Wheeler (success), and the asymmetry across Stuff+ deciles (Wilson intervals). Decile retention and the IPW check are in Section 7. | `data/fig5_cases.csv`, `data/fig5_stuff_deciles.csv`; `RC/retention_by_decile.csv` |
| Fig 6 | `fig6_fantasy_linkage` | Which target forecasts add information about which fantasy categories, after multiplicity adjustment. Each marker shape keeps one meaning throughout. | `data/fig6_fantasy_linkage.csv` |
| Fig 7 | `fig7_draft_backtest` | Illustrative draft. Rank agreement improves slightly, but the players picked are not detectably better at the protocol roster size or at Yahoo or NFBC roster sizes (post hoc). | `data/fig7_rank_correlation.csv`, `data/fig7_topk_value.csv`; `RC/draft_scaling.csv` |

| # | Table | Source |
|---|---|---|
| 1 | The six prediction targets (construct, why, fantasy link, limits) | study code (`psl/components.py`, `psl/data/assemble_components.py`) + `metric_definitions_sources.md` |
| 2 | Conventional-wisdom audit, with citations in each row | `fantasy/practice_audit.csv`; `fantasy/results_by_target_category.csv`; `RC/direct_tests_posthoc.csv` (exit velocity → HR, Stuff+ → K/9; post hoc) |
| 3 | Admission labels, how each is decided, and which involve a human choice | `engine.decide_verdict`; label counts from the 208 canonical evaluations (`app/public/data/evaluations.json`, exported from the canonical artifacts) |
| 4 | Four meanings of "unstable" | canonical artifact columns |
| 5 | Nested results in baseball units, split into third-season history versus other metrics (post hoc) | `S27/tables/table2_nested_and_2026_model_comparison.csv`; `RC/history_decomposition.csv` |
| 6 | Headline contrasts H1–H7 under stronger tests | `S27/tables/table3_flagship_contrasts.csv` |
| 7 | Named cases chosen by a fixed rule (post hoc) | `RC/named_cases.csv` |
| 8 | Primary fantasy linkages, with season-level t(4) intervals | `fantasy/results_by_target_category.csv`; `RC/season_level.csv` |
| 9 | Original versus revised claims (Appendix A) | `S27/tables/table2…`, `table3…`, plus this revision's departures |
| 10 | Every one-at-a-time gate ablation (Appendix E) | `S27/tables/table5_gate_ablation_threshold_sensitivity.csv` |
| 11 | Human-defined feature families (Appendix E) | `psl.catalog.HITTER_FAMILIES` and `PITCHER_FAMILIES`, imported from the frozen study code at `PSL_ROOT` |
