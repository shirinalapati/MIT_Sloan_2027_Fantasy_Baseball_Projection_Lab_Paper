/** Constants shared by the build-time validator, the tests, and the UI. No DOM or React imports. */

/** The six study targets (ids in targets.json). */
export const TARGET_IDS = [
  'hitting_woba',
  'pitching_fip',
  'baserunning_rv',
  'defense_rv',
  'overall_war',
  'pitcher_war',
] as const;
export type TargetId = (typeof TARGET_IDS)[number];

/** Short target-forecast ids used in fantasy.json, mapped to targets.json ids. */
export const FANTASY_TARGET_ALIASES: Record<string, TargetId> = {
  woba: 'hitting_woba',
  br: 'baserunning_rv',
  fld: 'defense_rv',
  hwar: 'overall_war',
  fip: 'pitching_fip',
  pwar: 'pitcher_war',
};

export const HITTER_FORECASTS = ['woba', 'br', 'fld', 'hwar'] as const;
export const PITCHER_FORECASTS = ['fip', 'pwar'] as const;

/** Evaluation files are cited by these source artifacts (keys of meta.sources_sha256). */
export const SOURCE_FILES = {
  evaluations: 'sloan2027/tables/table7_reason_codes_208.csv',
  comparisonsNested: 'sloan2027/results/nested/comparisons_default.csv',
  perYearNested: 'sloan2027/results/nested/per_year_default.csv',
  comparisons2026: 'sloan2027/results/holdout2026/comparisons_2026.csv',
  flagships: 'sloan2027/tables/table3_flagship_contrasts.csv',
  forecastChanges: 'sloan2027/results/players/forecast_changes.parquet',
  cohortEffects: 'sloan2027/results/players/cohort_effects.csv',
  unitTranslation: 'sloan2027/results/players/unit_translation.csv',
  fantasyResults: 'sloan2027_fantasy/fantasy/results_by_target_category.csv',
  fantasyByYear: 'sloan2027_fantasy/fantasy/by_year.csv',
  fantasyLevel1: 'sloan2027_fantasy/fantasy/level1_correlations.csv',
  fantasyCohorts: 'sloan2027_fantasy/fantasy/cohort_by_year.csv',
  fantasyDecision: 'sloan2027_fantasy/fantasy/ranking_value_sensitivity.csv',
} as const;

/** Source artifact for the nested admission window of a target study and outer year. */
export function nestedSourceFile(targetId: string, year: number | string): string {
  return `sloan2027/results/nested/admission/${targetId}_T${year}_default_final.parquet`;
}

export const NESTED_YEARS = ['2021', '2022', '2023', '2024', '2025', '2026'] as const;
