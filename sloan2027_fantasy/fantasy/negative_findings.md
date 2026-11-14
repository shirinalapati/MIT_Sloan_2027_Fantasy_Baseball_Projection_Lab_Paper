# Negative and null findings (fantasy bridge)

Reported with the same prominence as the gains. Generated from `results_by_target_category.csv`.

- Pooled 2021–2025 comparisons: 140; adds information: 46; not robust to multiplicity: 21; no detectable gain: 72; harmful: 1.
- Primary family: 2 of 8 linkages add information (FIP → ERA, FIP → WHIP). The other six do not survive Holm adjustment.
- Harmful: the admitted hitter-WAR forecast was worse than the history-only hitter-WAR forecast for AVG, in 2021–2025 and again in 2026.
- Boundary case: the fielding forecast added nothing to hitter 5×5 value, at-bats or any category.
- The baserunning run-value forecast added nothing to stolen-base forecasts. Raw sprint speed did.
- Stuff+, K% and K-BB% added nothing to K, ERA or WHIP beyond the category history.
- Illustrative draft: no league size at which the augmented ranking picked detectably better players.

| Group | Outcome | Comparison | Added | ΔRMSE % [95% CI] | Adjusted p | Verdict |
|---|---|---|---|---|---|---|
| hitter | AB | admitted vs history-only target forecast | baserunning run-value rate | −0.01% [−0.10, +0.08] | 0.900 | no detectable gain |
| hitter | AB | admitted vs history-only target forecast | fielding run-value rate | +0.04% [−0.09, +0.17] | 0.658 | no detectable gain |
| hitter | AVG | admitted vs history-only target forecast | wOBA | −0.77% [−2.05, +0.47] | 0.393 | no detectable gain |
| hitter | AVG | admitted vs history-only target forecast | baserunning run-value rate | −0.22% [−0.65, +0.19] | 0.413 | no detectable gain |
| hitter | AVG | admitted vs history-only target forecast | fielding run-value rate | +0.00% [−0.03, +0.03] | 0.877 | no detectable gain |
| hitter | AVG | admitted vs history-only target forecast | hitter bWAR/600 PA | +0.19% [+0.09, +0.29] | 0.004 | harmful |
| hitter | HR | admitted vs history-only target forecast | wOBA | −0.98% [−1.93, −0.10] | 0.058 | gain not robust to multiplicity |
| hitter | HR | admitted vs history-only target forecast | baserunning run-value rate | +0.07% [−0.07, +0.20] | 0.506 | no detectable gain |
| hitter | HR | admitted vs history-only target forecast | fielding run-value rate | −0.02% [−0.11, +0.06] | 0.777 | no detectable gain |
| hitter | HR | admitted vs history-only target forecast | hitter bWAR/600 PA | −0.10% [−0.25, +0.03] | 0.232 | no detectable gain |
| hitter | Yahoo hitter points | admitted vs history-only target forecast | baserunning run-value rate | −0.07% [−0.19, +0.05] | 0.333 | no detectable gain |
| hitter | Yahoo hitter points | admitted vs history-only target forecast | fielding run-value rate | −0.00% [−0.14, +0.13] | 0.969 | no detectable gain |
| hitter | R | admitted vs history-only target forecast | fielding run-value rate | −0.02% [−0.18, +0.14] | 0.877 | no detectable gain |
| hitter | RBI | admitted vs history-only target forecast | baserunning run-value rate | +0.04% [−0.08, +0.15] | 0.652 | no detectable gain |
| hitter | RBI | admitted vs history-only target forecast | fielding run-value rate | +0.04% [−0.06, +0.13] | 0.537 | no detectable gain |
| hitter | SB | admitted vs history-only target forecast | wOBA | −0.05% [−0.18, +0.09] | 0.652 | no detectable gain |
| hitter | SB | admitted vs history-only target forecast | fielding run-value rate | −0.04% [−0.13, +0.06] | 0.554 | no detectable gain |
| hitter | hitter 5×5 value | admitted vs history-only target forecast | fielding run-value rate | −0.02% [−0.13, +0.09] | 0.790 | no detectable gain |
| hitter | hitter 5×5 value | admitted vs history-only target forecast | hitter bWAR/600 PA | −0.19% [−0.38, −0.01] | 0.066 | gain not robust to multiplicity |
| pitcher | IP | admitted vs history-only target forecast | FIP | −0.06% [−0.42, +0.29] | 0.817 | no detectable gain |
| pitcher | IP | admitted vs history-only target forecast | pitcher bWAR/200 IP | −0.15% [−0.33, +0.04] | 0.178 | no detectable gain |
| pitcher | K | admitted vs history-only target forecast | FIP | +0.05% [−0.84, +0.90] | 0.928 | no detectable gain |
| pitcher | SV | admitted vs history-only target forecast | FIP | +0.10% [−0.06, +0.28] | 0.297 | no detectable gain |
| pitcher | SV | admitted vs history-only target forecast | pitcher bWAR/200 IP | −0.06% [−0.17, +0.03] | 0.333 | no detectable gain |
| pitcher | W | admitted vs history-only target forecast | pitcher bWAR/200 IP | −0.19% [−0.40, −0.00] | 0.087 | gain not robust to multiplicity |
| hitter | AVG | raw metric added | two-year xwOBA (raw) | −1.09% [−2.00, −0.17] | 0.060 | gain not robust to multiplicity |
| hitter | R | raw metric added | two-year xwOBA (raw) | −0.34% [−0.96, +0.26] | 0.379 | no detectable gain |
| hitter | RBI | raw metric added | two-year xwOBA (raw) | −0.62% [−1.23, −0.03] | 0.106 | gain not robust to multiplicity |
| pitcher | ERA | raw metric added | Stuff+ (raw) | +0.10% [−0.44, +0.68] | 0.810 | no detectable gain |
| pitcher | ERA | raw metric added | K-BB% (raw) | −0.13% [−0.30, +0.05] | 0.264 | no detectable gain |
| pitcher | K | raw metric added | Stuff+ (raw) | −0.05% [−0.30, +0.20] | 0.810 | no detectable gain |
| pitcher | K | raw metric added | K% (raw) | +0.05% [−0.16, +0.28] | 0.810 | no detectable gain |
| pitcher | WHIP | raw metric added | Stuff+ (raw) | −0.01% [−0.46, +0.49] | 0.953 | no detectable gain |
| pitcher | WHIP | raw metric added | K-BB% (raw) | −0.53% [−1.09, +0.01] | 0.124 | no detectable gain |
| hitter | AVG | joint admitted vs joint history-only | all hitter target forecasts | −1.26% [−2.51, −0.02] | 0.076 | gain not robust to multiplicity |
| hitter | HR | joint admitted vs joint history-only | all hitter target forecasts | −0.91% [−1.81, −0.06] | 0.070 | gain not robust to multiplicity |
| hitter | RBI | joint admitted vs joint history-only | all hitter target forecasts | −0.73% [−1.39, −0.07] | 0.070 | gain not robust to multiplicity |
| hitter | SB | joint admitted vs joint history-only | all hitter target forecasts | −0.22% [−0.58, +0.21] | 0.325 | no detectable gain |
| hitter | hitter 5×5 value | joint admitted vs joint history-only | all hitter target forecasts | −0.50% [−1.31, +0.27] | 0.258 | no detectable gain |
| pitcher | IP | joint admitted vs joint history-only | both pitcher target forecasts | −0.22% [−0.65, +0.20] | 0.336 | no detectable gain |
| pitcher | K | joint admitted vs joint history-only | both pitcher target forecasts | −0.40% [−1.39, +0.57] | 0.477 | no detectable gain |
| pitcher | SV | joint admitted vs joint history-only | both pitcher target forecasts | +0.05% [−0.16, +0.26] | 0.684 | no detectable gain |
| pitcher | W | joint admitted vs joint history-only | both pitcher target forecasts | −0.42% [−0.80, −0.05] | 0.053 | gain not robust to multiplicity |
| hitter | HR | all target forecasts jointly | all hitter target forecasts | −0.91% [−2.14, +0.18] | 0.155 | no detectable gain |
| hitter | RBI | all target forecasts jointly | all hitter target forecasts | −0.82% [−1.71, +0.07] | 0.102 | no detectable gain |
| hitter | SB | all target forecasts jointly | all hitter target forecasts | −0.65% [−1.24, −0.01] | 0.076 | gain not robust to multiplicity |
| hitter | hitter 5×5 value | all target forecasts jointly | all hitter target forecasts | −0.80% [−1.81, +0.18] | 0.147 | no detectable gain |
| pitcher | IP | all target forecasts jointly | both pitcher target forecasts | +0.03% [−0.50, +0.55] | 0.933 | no detectable gain |
| pitcher | K | all target forecasts jointly | both pitcher target forecasts | −0.30% [−1.26, +0.66] | 0.581 | no detectable gain |
| pitcher | Yahoo pitcher points | all target forecasts jointly | both pitcher target forecasts | −0.91% [−1.84, +0.06] | 0.099 | no detectable gain |
| pitcher | SV | all target forecasts jointly | both pitcher target forecasts | +0.01% [−0.18, +0.20] | 0.933 | no detectable gain |
| pitcher | W | all target forecasts jointly | both pitcher target forecasts | −0.59% [−1.25, +0.03] | 0.094 | no detectable gain |
| hitter | AB | target forecast added to the category baseline | wOBA | −0.42% [−0.92, +0.07] | 0.204 | no detectable gain |
| hitter | AB | target forecast added to the category baseline | baserunning run-value rate | −0.03% [−0.10, +0.03] | 0.400 | no detectable gain |
| hitter | AB | target forecast added to the category baseline | fielding run-value rate | −0.26% [−0.78, +0.30] | 0.481 | no detectable gain |
| hitter | AVG | target forecast added to the category baseline | wOBA | −0.73% [−1.89, +0.39] | 0.700 | no detectable gain |
| hitter | AVG | target forecast added to the category baseline | baserunning run-value rate | −0.31% [−0.83, +0.20] | 0.392 | no detectable gain |
| hitter | AVG | target forecast added to the category baseline | fielding run-value rate | +0.04% [−0.07, +0.15] | 0.540 | no detectable gain |
| hitter | AVG | target forecast added to the category baseline | hitter bWAR/600 PA | −0.22% [−0.49, +0.06] | 0.240 | no detectable gain |
| hitter | HR | target forecast added to the category baseline | wOBA | −1.02% [−2.16, +0.03] | 0.310 | no detectable gain |
| hitter | HR | target forecast added to the category baseline | baserunning run-value rate | +0.02% [−0.06, +0.09] | 0.687 | no detectable gain |
| hitter | HR | target forecast added to the category baseline | fielding run-value rate | −0.20% [−0.47, +0.07] | 0.268 | no detectable gain |
| hitter | HR | target forecast added to the category baseline | hitter bWAR/600 PA | −0.15% [−0.54, +0.28] | 0.540 | no detectable gain |
| hitter | Yahoo hitter points | target forecast added to the category baseline | wOBA | −1.01% [−1.86, −0.20] | 0.069 | gain not robust to multiplicity |
| hitter | Yahoo hitter points | target forecast added to the category baseline | baserunning run-value rate | −0.12% [−0.25, +0.02] | 0.196 | no detectable gain |
| hitter | Yahoo hitter points | target forecast added to the category baseline | fielding run-value rate | −0.46% [−0.91, +0.02] | 0.167 | no detectable gain |
| hitter | R | target forecast added to the category baseline | wOBA | −0.43% [−1.25, +0.35] | 0.408 | no detectable gain |
| hitter | R | target forecast added to the category baseline | baserunning run-value rate | −0.43% [−0.79, −0.07] | 0.080 | gain not robust to multiplicity |
| hitter | R | target forecast added to the category baseline | fielding run-value rate | −0.70% [−1.23, −0.15] | 0.080 | gain not robust to multiplicity |
| hitter | R | target forecast added to the category baseline | hitter bWAR/600 PA | −0.71% [−1.35, −0.04] | 0.111 | gain not robust to multiplicity |
| hitter | RBI | target forecast added to the category baseline | wOBA | −0.71% [−1.54, +0.07] | 0.172 | no detectable gain |
| hitter | RBI | target forecast added to the category baseline | baserunning run-value rate | +0.00% [−0.07, +0.07] | 0.969 | no detectable gain |
| hitter | RBI | target forecast added to the category baseline | fielding run-value rate | −0.26% [−0.60, +0.09] | 0.268 | no detectable gain |
| hitter | RBI | target forecast added to the category baseline | hitter bWAR/600 PA | −0.57% [−1.02, −0.10] | 0.080 | gain not robust to multiplicity |
| hitter | SB | target forecast added to the category baseline | wOBA | +0.08% [−0.13, +0.31] | 0.540 | no detectable gain |
| hitter | SB | target forecast added to the category baseline | baserunning run-value rate | −0.30% [−0.75, +0.19] | 0.700 | no detectable gain |
| hitter | SB | target forecast added to the category baseline | fielding run-value rate | −0.01% [−0.35, +0.32] | 0.956 | no detectable gain |
| hitter | SB | target forecast added to the category baseline | hitter bWAR/600 PA | −0.62% [−1.08, −0.15] | 0.069 | gain not robust to multiplicity |
| hitter | hitter 5×5 value | target forecast added to the category baseline | wOBA | −0.72% [−1.58, +0.08] | 0.187 | no detectable gain |
| hitter | hitter 5×5 value | target forecast added to the category baseline | baserunning run-value rate | −0.31% [−0.58, −0.03] | 0.111 | gain not robust to multiplicity |
| hitter | hitter 5×5 value | target forecast added to the category baseline | fielding run-value rate | −0.26% [−0.66, +0.15] | 0.700 | no detectable gain |
| hitter | hitter 5×5 value | target forecast added to the category baseline | hitter bWAR/600 PA | −0.46% [−0.91, −0.01] | 0.270 | gain not robust to multiplicity |
| pitcher | ERA | target forecast added to the category baseline | pitcher bWAR/200 IP | −0.18% [−0.36, +0.00] | 0.157 | no detectable gain |
| pitcher | IP | target forecast added to the category baseline | FIP | −0.12% [−0.67, +0.40] | 0.687 | no detectable gain |
| pitcher | IP | target forecast added to the category baseline | pitcher bWAR/200 IP | +0.22% [−0.24, +0.69] | 0.481 | no detectable gain |
| pitcher | K | target forecast added to the category baseline | FIP | −0.19% [−1.11, +0.72] | 0.719 | no detectable gain |
| pitcher | K | target forecast added to the category baseline | pitcher bWAR/200 IP | −0.17% [−0.59, +0.22] | 0.521 | no detectable gain |
| pitcher | Yahoo pitcher points | target forecast added to the category baseline | FIP | −1.12% [−1.93, −0.34] | 0.069 | gain not robust to multiplicity |
| pitcher | Yahoo pitcher points | target forecast added to the category baseline | pitcher bWAR/200 IP | −0.20% [−0.58, +0.15] | 0.404 | no detectable gain |
| pitcher | SV | target forecast added to the category baseline | FIP | +0.09% [−0.04, +0.23] | 0.268 | no detectable gain |
| pitcher | SV | target forecast added to the category baseline | pitcher bWAR/200 IP | −0.11% [−0.22, −0.01] | 0.080 | gain not robust to multiplicity |
| pitcher | pitcher 5×5 value | target forecast added to the category baseline | pitcher bWAR/200 IP | −0.27% [−0.69, +0.12] | 0.700 | no detectable gain |
| pitcher | W | target forecast added to the category baseline | FIP | −0.74% [−1.39, −0.11] | 0.080 | gain not robust to multiplicity |
| pitcher | W | target forecast added to the category baseline | pitcher bWAR/200 IP | −0.21% [−0.67, +0.23] | 0.481 | no detectable gain |
