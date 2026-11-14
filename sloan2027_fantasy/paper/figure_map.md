# Figure and table map (revised manuscript)

All figures come from `sloan2027_fantasy/figures/make_figures.py`, saved as PNG at 300 dpi plus PDF and SVG. The plotted values are written to `figures/data/`. The palette uses the reference categorical slots of the dataviz validator: on #fcfcfb the worst adjacent CVD ΔE is 9.1 and the worst normal-vision ΔE is 19.6, and the first three slots pass all-pairs. The low-contrast slots are relieved with direct labels.

| # | File | Claim it carries | Data |
|---|---|---|---|
| Fig 1 | `fig1_decision_flow` | How admission works. It separates statistical steps from human-specified rules, using sprint speed admitted for baserunning and Diagnostic for wOBA as the example. | `data/fig1_sprint_speed_examples.csv` (canonical artifacts, commit 17da742) |
| Fig 2 | `fig2_classification_map` | What the 208 canonical evaluations concluded, by target and reason code. Context labels and the Diagnostic/Exclude split are human labels. | `data/fig2_reason_codes_by_target.csv` |
| Fig 3 | `fig3_model_comparisons` | Selected versus history baseline, all-metric ridge and tuned elastic net, on identical players. Nested 2021–2025 and the 2026 check. | `data/fig3_model_comparisons.csv` |
| Fig 4 | `fig4_year_by_year` | Season-by-season effects. The selective advantage over all-metric ridge decays as training seasons accumulate, and the FIP result reverses in 2026. | `data/fig4_year_by_year.csv` |
| Fig 5 | `fig5_player_stories_stuff` | Stuff+ in FIP units: Tyler Rogers (failure, submarine delivery), Zack Wheeler (success), and decile asymmetry. | `data/fig5_cases.csv`, `data/fig5_stuff_deciles.csv` |
| Fig 6 | `fig6_fantasy_linkage` | Which target forecasts add information about which fantasy categories, after multiplicity adjustment. | `data/fig6_fantasy_linkage.csv` |
| Fig 7 | `fig7_draft_backtest` | Illustrative draft: rank agreement improves slightly, but the players picked are not detectably better. | `data/fig7_rank_correlation.csv`, `data/fig7_topk_value.csv` |

| # | Table | Source |
|---|---|---|
| 1 | The six targets (construct, why, fantasy link, limits) | study code (`psl/components.py`, `psl/data/assemble_components.py`) + `metric_definitions_sources.md` |
| 2 | Conventional-wisdom audit | `fantasy/practice_audit.csv` + `fantasy/results_by_target_category.csv` |
| 3 | Admission labels and their basis | `engine.decide_verdict`; canonical counts |
| 4 | Four meanings of "unstable" | canonical artifact columns |
| 5 | Headline contrasts under stronger tests | `sloan2027/tables/table3_flagship_contrasts.csv` |
| 6 | Primary fantasy linkages | `fantasy/results_by_target_category.csv` |
| 7 | Original versus revised claims (Appendix A) | `sloan2027/tables/table2…`, `table3…` |
