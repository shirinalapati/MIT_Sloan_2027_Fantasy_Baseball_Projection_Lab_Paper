/**
 * Zod schemas for every JSON file in public/data.
 *
 * Objects are `.strict()`: an unknown key or a missing required key is a validation error.
 * `z.number()` rejects NaN; `.finite()` also rejects ±Infinity.
 *
 * These schemas run at build time (scripts/validate-data.ts, wired to `prebuild`) and in the
 * unit tests. The browser bundle imports only the inferred *types*, so zod is not shipped.
 */
import { z } from 'zod';

const num = z.number().finite();
const int = z.number().int();
const nonNegInt = int.nonnegative();
const posInt = int.positive();
const share = num.min(0).max(1);
const corr = num.min(-1).max(1);
const text = z.string().min(1);

// ---------------------------------------------------------------- enumerations
export const EVALUATION_VERDICTS = [
  'Projection',
  'Diagnostic',
  'Exclude',
  'Context',
  'Augmented Projection',
  'Insufficient Evidence',
] as const;
export const evaluationVerdict = z.enum(EVALUATION_VERDICTS);

export const FANTASY_VERDICTS = [
  'adds information',
  'gain not robust to multiplicity',
  'no detectable gain',
  'harmful',
  'directional gain (exploratory; CI excludes 0)',
] as const;
export const fantasyVerdict = z.enum(FANTASY_VERDICTS);

export const FANTASY_KINDS = [
  'target_forecast_added',
  'admitted_vs_history_target_forecast',
  'joint_target_forecasts',
  'joint_admitted_vs_history',
  'direct_metric_added',
] as const;

export const FANTASY_SAMPLES = ['2021-2025 pooled (primary)', '2026 (exploratory)'] as const;

/** Outcome ids the fantasy pipeline can emit (fb03_bridge.py UNITS map, plus the 2026-capable points outcomes). */
export const KNOWN_FANTASY_OUTCOMES = [
  'R', 'HR', 'RBI', 'SB', 'AVG', 'AB', 'H', 'VAL_H', 'PTS_H',
  'W', 'SV', 'K', 'ERA', 'WHIP', 'IP', 'VAL_P', 'PTS_P',
] as const;

export const COMPARISON_SAMPLES = ['outer years 2021-2025 (nested)', '2026 (frozen-in-workflow, exploratory)'] as const;
export const COMPARISON_COHORTS = [
  'retrospective (canonical rule)',
  'prospective (2025 eligibility, any 2026 label)',
] as const;

export const CASE_SELECTIONS = ['largest increase', 'largest decrease', 'random sample (seed 42)'] as const;

/** `SET|estimator`, where SET is a named feature set or the history baseline plus one metric. */
export const MODEL_ID_RE = /^(B0|ADM|KS|FIX|UNI|FAM|CORR|B0\+[a-z0-9_]+)\|(ridge|ridge_tuned|enet|lgbm|rf)$/;
const modelId = z.string().regex(MODEL_ID_RE, 'model id must look like SET|estimator');

// ---------------------------------------------------------------- meta.json
export const metaSchema = z
  .object({
    schema_version: text,
    generated_at: text,
    paper: z.object({ title: text, venue: text }).strict(),
    provenance: z.object({ psl_research_root: text, fantasy_protocol_commit: text }).strict(),
    evidence_tiers: z
      .object({
        historical: text,
        'historical-2026': text,
        exploratory_fantasy: text,
        illustrative: text,
      })
      .strict(),
    ci_definition: text,
    sources_sha256: z.record(z.string().regex(/^[0-9a-f]{64}$/, 'sha256 must be 64 lowercase hex characters')),
  })
  .strict();

// ---------------------------------------------------------------- targets.json
export const targetSchema = z
  .object({
    id: text,
    short: text,
    label: text,
    group: z.enum(['hitter', 'pitcher']),
    unit: text,
    definition: text,
    denominator: text,
    eligibility: text,
    weight: text,
    baseline: text,
    why: text,
    fantasy_link: text,
    not_established: text,
    n_candidates: nonNegInt,
    n_player_seasons: posInt,
  })
  .strict();
export const targetsSchema = z.array(targetSchema).min(1);

// ---------------------------------------------------------------- metrics.json
export const metricSchema = z
  .object({
    id: text,
    description: text,
    family: text,
    role: z.enum(['skill', 'demographic', 'environment']),
    process_flag: z.boolean(),
    player_types: z.array(z.enum(['hitter', 'pitcher'])).min(1),
  })
  .strict();
export const metricsSchema = z.array(metricSchema).min(1);

// ---------------------------------------------------------------- evaluations.json
export const evaluationSchema = z
  .object({
    target: text,
    metric: text,
    family: text,
    verdict: evaluationVerdict,
    reason_code: text,
    rationale: text,
    verdict_basis: text,
    delta_rmse: num,
    delta_pct: num,
    ci_low_pct: num,
    ci_high_pct: num,
    baseline_rmse: num.positive(),
    folds_improved_share: share,
    n_folds: posInt,
    fold_deltas_pct: z.array(z.object({ year: int, delta_pct: num }).strict()).min(1),
    reliability_r: corr.nullable(),
    coverage: share,
    coef_sign_changes: nonNegInt,
    max_corr_with_baseline: corr.nullable(),
    max_corr_partner: text.nullable(),
    family_redundant: z.boolean(),
    family_representative: z.boolean(),
    n_player_seasons: posInt,
    subgroups: z.array(z.object({ name: text, n: nonNegInt, delta_pct: num }).strict()),
    nested_verdicts: z
      .object({
        '2021': evaluationVerdict,
        '2022': evaluationVerdict,
        '2023': evaluationVerdict,
        '2024': evaluationVerdict,
        '2025': evaluationVerdict,
        '2026': evaluationVerdict,
      })
      .strict(),
    nested_projection_count_2021_2025: int.min(0).max(5),
    nested_projection_2026_window: z.boolean(),
    evidence_tier: z.enum(['historical', 'historical-2026']),
    seasons: text,
  })
  .strict();
export const evaluationsSchema = z.array(evaluationSchema).min(1);

// ---------------------------------------------------------------- model_comparisons.json
export const comparisonSchema = z
  .object({
    target: text,
    comparison: text,
    cohort: z.enum(COMPARISON_COHORTS).optional(),
    model_a: modelId,
    model_b: modelId,
    delta_rmse: num,
    delta_pct: num,
    ci_low_pct: num.nullable(),
    ci_high_pct: num.nullable(),
    years_a_better: nonNegInt.optional(),
    n_years: posInt.optional(),
    n_rows: posInt,
    n_players: posInt,
    sample: z.enum(COMPARISON_SAMPLES),
    evidence_tier: z.enum(['historical', 'historical-2026']),
  })
  .strict();
export const perYearSchema = z
  .object({
    study_id: text,
    model_id: modelId,
    outer_year: int,
    n: posInt,
    wrmse: num.positive(),
    rmse_unweighted: num.positive(),
    mae_unweighted: num.positive(),
  })
  .strict();
export const modelComparisonsSchema = z
  .object({
    comparisons: z.array(comparisonSchema).min(1),
    per_year: z.array(perYearSchema).min(1),
  })
  .strict();

// ---------------------------------------------------------------- flagships.json
/** "−2.44 [−3.60, −1.35]" written with ASCII signs, e.g. "-2.44 [-3.60, -1.35]" or "+0.72 [-0.49, +1.82]". */
export const CI_STRING_RE = /^([+-]?\d+(?:\.\d+)?) \[([+-]?\d+(?:\.\d+)?), ([+-]?\d+(?:\.\d+)?)\]$/;
const ciString = z.string().regex(CI_STRING_RE, 'expected "estimate [low, high]"');
export const flagshipSchema = z
  .object({
    Hypothesis: text,
    Contrast: text,
    'Published ΔRMSE (mean of 7 folds)': num,
    '2019–25 pooled, % [cluster CI]': ciString,
    'Holm-adjusted p (H1–H6)': share.nullable(),
    'BH q (all 208)': share,
    'Nested 2021–25, %': ciString,
    '2026 holdout, %': ciString,
    '2026 n': posInt,
  })
  .strict();
export const flagshipsSchema = z.array(flagshipSchema).min(1);

// ---------------------------------------------------------------- casebook.json
export const caseSchema = z
  .object({
    contrast: text,
    target: text,
    metric: text,
    selection: z.enum(CASE_SELECTIONS),
    player: text,
    feature_season: int,
    outcome_season: int,
    metric_value: num,
    forecast_without: num,
    forecast_with: num,
    observed: num,
    forecast_change: num,
    abs_error_change: num,
    improved: z.boolean(),
  })
  .strict();
export const cohortEffectSchema = z
  .object({
    contrast: text,
    cohort: text,
    n: posInt,
    mean_feature: num,
    mean_forecast_change: num,
    mean_actual_minus_base: num,
    delta_rmse: num,
    ci_low: num,
    ci_high: num,
    share_improved: share,
  })
  .strict();
export const unitTranslationSchema = z
  .object({
    contrast: text,
    target_unit: text,
    n: posInt,
    rmse_base: num.positive(),
    rmse_aug: num.positive(),
    delta_rmse: num,
    ci_low: num,
    ci_high: num,
    pct: num,
    translated_delta: num,
    translation: text,
    median_abs_forecast_change: num.nonnegative(),
    p90_abs_forecast_change: num.nonnegative(),
    share_improved_abs_error: share,
  })
  .strict();
export const casebookSchema = z
  .object({
    cases: z.array(caseSchema).min(1),
    cohorts: z.array(cohortEffectSchema),
    unit_translation: z.array(unitTranslationSchema),
    selection_note: text,
  })
  .strict();

// ---------------------------------------------------------------- fantasy.json
export const fantasyResultSchema = z
  .object({
    group: z.enum(['hitter', 'pitcher']),
    outcome: z.enum(KNOWN_FANTASY_OUTCOMES),
    units: text,
    kind: z.enum(FANTASY_KINDS),
    target: text,
    base: text,
    aug: text,
    family: z.string().regex(/^(primary|secondary(_[a-z0-9_]+)?)$/, 'family must be primary or secondary_*'),
    sample: z.enum(FANTASY_SAMPLES),
    n_rows: posInt,
    n_players: posInt,
    rmse_base: num.nonnegative(),
    rmse_aug: num.nonnegative(),
    delta_rmse: num,
    delta_pct: num,
    ci_low_pct: num,
    ci_high_pct: num,
    season_block_ci_low_pct: num.nullable(),
    season_block_ci_high_pct: num.nullable(),
    mae_base: num.nonnegative(),
    mae_aug: num.nonnegative(),
    p_two_sided: share,
    p_adjusted: share.nullable(),
    adjustment: text.nullable(),
    years_improved: nonNegInt,
    n_years: posInt,
    verdict: fantasyVerdict,
  })
  .strict();
export const fantasyByYearSchema = z
  .object({
    group: z.enum(['hitter', 'pitcher']),
    outcome: z.enum(KNOWN_FANTASY_OUTCOMES),
    kind: z.enum(FANTASY_KINDS),
    target: text,
    base: text,
    aug: text,
    sample: z.enum(FANTASY_SAMPLES),
    outcome_season: int,
    n: posInt,
    delta_pct: num,
  })
  .strict();
export const level1Schema = z
  .object({
    group: z.enum(['hitter', 'pitcher']),
    target_forecast: text,
    fantasy_outcome: z.enum(KNOWN_FANTASY_OUTCOMES),
    n_2021_2025: posInt,
    spearman_2021_2025: corr,
    ci_low: corr,
    ci_high: corr,
    rho_2021: corr.nullable(),
    rho_2022: corr.nullable(),
    rho_2023: corr.nullable(),
    rho_2024: corr.nullable(),
    rho_2025: corr.nullable(),
    rho_2026: corr.nullable(),
    note: text,
  })
  .strict();
export const fantasyCohortSchema = z
  .object({
    player_group: z.enum(['hitter', 'pitcher']),
    outcome_season: int,
    pool_size: posInt,
    share_any_T_appearance: share,
    share_zero_counting_outcome: share,
    'share_meeting_canonical_t+1_rule': share.nullable(),
    share_meeting_rate_floor: share,
    status: z.enum(['training only', 'primary', 'exploratory']),
  })
  .strict();
export const decisionSchema = z
  .object({
    group: z.enum(['hitter', 'pitcher']),
    format: text,
    k: posInt,
    league_size_equivalent: text.nullable(),
    mean_realized_value_of_picks_base: num,
    mean_realized_value_of_picks_aug: num,
    delta_mean_realized_value: num,
    ci_low: num,
    ci_high: num,
    seasons_aug_better: nonNegInt.nullable(),
    spearman_base: corr,
    spearman_aug: corr,
    delta_spearman: num,
    spearman_ci_low: num,
    spearman_ci_high: num,
    topk_overlap_base: share,
    topk_overlap_aug: share,
    sample: text,
  })
  .strict();
export const fantasySchema = z
  .object({
    results: z.array(fantasyResultSchema).min(1),
    by_year: z.array(fantasyByYearSchema),
    level1: z.array(level1Schema),
    cohorts: z.array(fantasyCohortSchema),
    decision: z.array(decisionSchema),
    protocol: text,
  })
  .strict();

// ---------------------------------------------------------------- scoring.json (optional)
/**
 * scoring.json is a direct dump of the research repo's scoring_weights.json. The research
 * pipeline (fb03_bridge.py) reads `batters` and `pitchers` as {stat: weight}; everything else is
 * provenance metadata (source, date, ...), which is allowed but not interpreted.
 */
export const scoringSchema = z
  .object({
    batters: z.record(num),
    pitchers: z.record(num),
  })
  .passthrough();

export type Meta = z.infer<typeof metaSchema>;
export type Target = z.infer<typeof targetSchema>;
export type Metric = z.infer<typeof metricSchema>;
export type Evaluation = z.infer<typeof evaluationSchema>;
export type EvaluationVerdict = z.infer<typeof evaluationVerdict>;
export type Comparison = z.infer<typeof comparisonSchema>;
export type PerYear = z.infer<typeof perYearSchema>;
export type ModelComparisons = z.infer<typeof modelComparisonsSchema>;
export type Flagship = z.infer<typeof flagshipSchema>;
export type Case = z.infer<typeof caseSchema>;
export type CohortEffect = z.infer<typeof cohortEffectSchema>;
export type UnitTranslation = z.infer<typeof unitTranslationSchema>;
export type Casebook = z.infer<typeof casebookSchema>;
export type FantasyResult = z.infer<typeof fantasyResultSchema>;
export type FantasyByYear = z.infer<typeof fantasyByYearSchema>;
export type Level1 = z.infer<typeof level1Schema>;
export type FantasyCohort = z.infer<typeof fantasyCohortSchema>;
export type Decision = z.infer<typeof decisionSchema>;
export type Fantasy = z.infer<typeof fantasySchema>;
export type FantasyVerdict = z.infer<typeof fantasyVerdict>;
export type FantasyKind = (typeof FANTASY_KINDS)[number];
export type FantasySample = (typeof FANTASY_SAMPLES)[number];
export type FantasyOutcome = (typeof KNOWN_FANTASY_OUTCOMES)[number];
export type CaseSelection = (typeof CASE_SELECTIONS)[number];
export type Scoring = z.infer<typeof scoringSchema>;
