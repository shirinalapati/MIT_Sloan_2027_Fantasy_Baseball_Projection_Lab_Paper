# Original (accepted abstract) versus revised claims

The accepted abstract is preserved verbatim in Appendix A of the manuscript and in `app/content/study_notes.md`. Each claim below is listed with its status under the stronger tests. Numbers are ΔRMSE as a percentage of the reference model's RMSE, with 95% player-cluster bootstrap intervals.

| Accepted-abstract claim | Revised evidence | Status |
|---|---|---|
| 402 fields → 208 evaluations, 163 metrics | Reproduced exactly; 55/55 checks re-run 2026-11-13 | Unchanged |
| Two-year xwOBA improved next-season wOBA (−0.00093; 7/7 folds) | Pooled −2.44% [−3.60, −1.35]; outer 2021–25 −2.26% [−3.59, −0.85]; 2026 −2.59% [−5.43, +0.19] | Supported; 2026 directional |
| Exit velocity improved wOBA and hitter WAR | wOBA outer −1.28% [−2.51, −0.03]; hitter WAR outer −0.57% [−1.19, +0.05], 2026 +0.72% [−0.49, +1.82] | wOBA supported; **hitter WAR not supported** |
| Stuff+ improved FIP (−0.00730; 5/7 folds) | Pooled −0.48% [−0.92, −0.03] (BH q 0.062); outer −0.76%; 2026 −0.90% [−2.35, +0.54]; player-level harms for unusual deliveries | **Weakened**: small, consistent direction |
| Sprint speed stable (r ≈ 0.92), no wOBA value, baserunning −0.0599 in 7/7 folds | Baserunning outer −4.75% [−6.16, −3.30], 2026 −3.30% [−6.68, +0.09]; wOBA ≈ 0 everywhere | Supported |
| Selective models beat kitchen-sink for wOBA and FIP | Against all-metric ridge: +2.61% (wOBA), +5.19% (FIP), favoring selective. Against a tuned elastic net: ties. 2026 FIP reversed (−3.78% [−7.26, −0.10]). | **Holds only narrowly** |
| Broader model better for hitter WAR | Outer −2.04% [−3.30, −0.79]; also pitcher WAR −0.68% | Supported; extends to pitcher WAR |
| The framework tells "baseball operations" which metrics to use | Reframed. The application is public analysis and fantasy. Front-office use is explicitly out of scope (Section 10.4). | **Revised framing** |

## New claims in the revision (not in the abstract)
- **Nested selection lift.** Five of six targets show a lift; hitter WAR does not. Look-ahead optimism is at most 0.53% of RMSE.
- **Fantasy bridge** (exploratory; protocol pushed before fitting):
  - the FIP forecast adds information for ERA and WHIP, about 1%;
  - six of eight primary linkages are null or not robust;
  - raw sprint speed adds information for SB, and Barrel% and xwOBA for HR;
  - WAR forecasts mainly carry playing time;
  - in the illustrative draft, the players picked were not detectably better.
- **New-target check (ERA).** Selection works, but re-selecting for ERA adds nothing beyond reusing FIP's selections.
