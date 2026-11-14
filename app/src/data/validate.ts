/**
 * Cross-file data validation. Pure TypeScript (no DOM, no Node APIs) so it runs in the
 * build-time script, in Vitest, and anywhere else.
 */
import type { ZodError, ZodTypeAny } from 'zod';
import {
  CI_STRING_RE,
  casebookSchema,
  evaluationsSchema,
  fantasySchema,
  flagshipsSchema,
  metaSchema,
  metricsSchema,
  modelComparisonsSchema,
  scoringSchema,
  targetsSchema,
  type Casebook,
  type Evaluation,
  type Fantasy,
  type FantasyResult,
  type Flagship,
  type Meta,
  type Metric,
  type ModelComparisons,
  type Target,
} from './schemas';
import { FANTASY_TARGET_ALIASES, TARGET_IDS } from './constants';
import { isPinnedCiException } from './knownExceptions';

export const REQUIRED_FILES = [
  'meta',
  'targets',
  'metrics',
  'evaluations',
  'model_comparisons',
  'flagships',
  'casebook',
  'fantasy',
] as const;
export const OPTIONAL_FILES = ['scoring'] as const;
export type DataFileName = (typeof REQUIRED_FILES)[number] | (typeof OPTIONAL_FILES)[number];

export interface ValidationReport {
  errors: string[];
  warnings: string[];
  notes: string[];
}

const SCHEMAS: Record<DataFileName, ZodTypeAny> = {
  meta: metaSchema,
  targets: targetsSchema,
  metrics: metricsSchema,
  evaluations: evaluationsSchema,
  model_comparisons: modelComparisonsSchema,
  flagships: flagshipsSchema,
  casebook: casebookSchema,
  fantasy: fantasySchema,
  scoring: scoringSchema,
};

const MAX_ISSUES_PER_FILE = 25;

function zodIssues(file: string, err: ZodError): string[] {
  const out = err.issues.slice(0, MAX_ISSUES_PER_FILE).map((i) => {
    const where = i.path.length ? i.path.join('.') : '(root)';
    const extra =
      i.code === 'unrecognized_keys' ? ` (${(i as { keys?: string[] }).keys?.join(', ')})` : '';
    return `${file}.json: ${where}: ${i.message}${extra}`;
  });
  if (err.issues.length > MAX_ISSUES_PER_FILE) {
    out.push(`${file}.json: ... ${err.issues.length - MAX_ISSUES_PER_FILE} more schema issues`);
  }
  return out;
}

/** True when lo <= est <= hi (with a tiny tolerance for float rounding in the source files). */
export function brackets(lo: number, est: number, hi: number, tol = 1e-9): boolean {
  return lo - tol <= est && est <= hi + tol;
}

/** Parse "est [lo, hi]" strings used in flagships.json. */
export function parseCiString(s: string): { est: number; lo: number; hi: number } | null {
  const m = CI_STRING_RE.exec(s);
  if (!m) return null;
  return { est: Number(m[1]), lo: Number(m[2]), hi: Number(m[3]) };
}

/** Expected fantasy verdict under the pre-registered protocol rule (experiment_protocol.md §7). */
export function expectedFantasyVerdict(r: Pick<FantasyResult, 'ci_low_pct' | 'ci_high_pct' | 'p_adjusted' | 'sample'>): string {
  if (r.ci_low_pct > 0) return 'harmful';
  if (r.ci_high_pct < 0) {
    if (r.sample === '2026 (exploratory)') return 'directional gain (exploratory; CI excludes 0)';
    return r.p_adjusted !== null && r.p_adjusted < 0.05 ? 'adds information' : 'gain not robust to multiplicity';
  }
  return 'no detectable gain';
}

/**
 * Validate a full dataset. `files` maps a file name (without .json) to its parsed JSON value.
 * A key that is absent means the file is missing. `parseErrors` carries JSON syntax errors
 * (for example NaN or Infinity tokens, which are not valid JSON).
 */
export function validateDataset(
  files: Partial<Record<DataFileName, unknown>>,
  parseErrors: Partial<Record<DataFileName, string>> = {},
): ValidationReport {
  const errors: string[] = [];
  const warnings: string[] = [];
  const notes: string[] = [];
  const parsed: Partial<Record<DataFileName, unknown>> = {};

  for (const name of REQUIRED_FILES) {
    if (parseErrors[name]) {
      errors.push(`${name}.json: invalid JSON (${parseErrors[name]})`);
      continue;
    }
    if (!(name in files) || files[name] === undefined) {
      errors.push(`${name}.json: missing required file`);
      continue;
    }
    const res = SCHEMAS[name].safeParse(files[name]);
    if (res.success) parsed[name] = res.data;
    else errors.push(...zodIssues(name, res.error));
  }

  for (const name of OPTIONAL_FILES) {
    if (parseErrors[name]) {
      errors.push(`${name}.json: invalid JSON (${parseErrors[name]})`);
      continue;
    }
    if (!(name in files) || files[name] === undefined) {
      notes.push(`${name}.json: not present (optional; the Value Lab falls back to example weights)`);
      continue;
    }
    const res = SCHEMAS[name].safeParse(files[name]);
    if (res.success) {
      parsed[name] = res.data;
      const meta = Object.keys(res.data as object).filter((k) => k !== 'batters' && k !== 'pitchers');
      if (meta.length === 0) warnings.push('scoring.json: no provenance fields (source/date) besides the weights');
    } else errors.push(...zodIssues(name, res.error));
  }

  const meta = parsed.meta as Meta | undefined;
  const targets = parsed.targets as Target[] | undefined;
  const metrics = parsed.metrics as Metric[] | undefined;
  const evaluations = parsed.evaluations as Evaluation[] | undefined;
  const comparisons = parsed.model_comparisons as ModelComparisons | undefined;
  const flagships = parsed.flagships as Flagship[] | undefined;
  const casebook = parsed.casebook as Casebook | undefined;
  const fantasy = parsed.fantasy as Fantasy | undefined;

  const targetIds = new Set<string>();
  const targetGroup = new Map<string, string>();
  if (targets) {
    for (const t of targets) {
      if (targetIds.has(t.id)) errors.push(`targets.json: duplicate target id "${t.id}"`);
      targetIds.add(t.id);
      targetGroup.set(t.id, t.group);
    }
    for (const id of TARGET_IDS) {
      if (!targetIds.has(id)) errors.push(`targets.json: required study target "${id}" is missing`);
    }
  }
  const metricIds = new Map<string, Metric>();
  if (metrics) {
    for (const m of metrics) {
      if (metricIds.has(m.id)) errors.push(`metrics.json: duplicate metric id "${m.id}"`);
      metricIds.set(m.id, m);
    }
  }
  const knownTarget = (id: string) => !targets || targetIds.has(id);
  const knownMetric = (id: string) => !metrics || metricIds.has(id);

  // ------------------------------------------------------------ evaluations
  if (evaluations) {
    const seen = new Set<string>();
    let pinned = 0;
    evaluations.forEach((r, i) => {
      const at = `evaluations.json[${i}] (${r.metric} × ${r.target})`;
      if (!knownTarget(r.target)) errors.push(`${at}: target "${r.target}" is not in targets.json`);
      if (!knownMetric(r.metric)) errors.push(`${at}: metric "${r.metric}" is not in metrics.json`);
      const key = `${r.target}|${r.metric}`;
      if (seen.has(key)) errors.push(`${at}: duplicate metric × target pair`);
      seen.add(key);
      if (r.fold_deltas_pct.length !== r.n_folds) {
        errors.push(`${at}: n_folds=${r.n_folds} but ${r.fold_deltas_pct.length} fold deltas`);
      }
      const years = r.fold_deltas_pct.map((f) => f.year);
      if (new Set(years).size !== years.length) errors.push(`${at}: duplicate fold years`);
      const mean = r.fold_deltas_pct.reduce((s, f) => s + f.delta_pct, 0) / r.fold_deltas_pct.length;
      if (Math.abs(mean - r.delta_pct) > 1e-3) {
        errors.push(`${at}: delta_pct ${r.delta_pct} is not the mean of its fold deltas (${mean.toFixed(6)})`);
      }
      if (r.ci_low_pct > r.ci_high_pct) errors.push(`${at}: CI low ${r.ci_low_pct} > CI high ${r.ci_high_pct}`);
      else if (!brackets(r.ci_low_pct, r.delta_pct, r.ci_high_pct)) {
        if (isPinnedCiException(r)) pinned += 1;
        else {
          errors.push(
            `${at}: CI [${r.ci_low_pct}, ${r.ci_high_pct}] does not bracket the point estimate ${r.delta_pct}`,
          );
        }
      }
      const projCount = (['2021', '2022', '2023', '2024', '2025'] as const).filter(
        (y) => r.nested_verdicts[y] === 'Projection',
      ).length;
      if (projCount !== r.nested_projection_count_2021_2025) {
        errors.push(`${at}: nested_projection_count_2021_2025 does not match nested_verdicts`);
      }
      if ((r.nested_verdicts['2026'] === 'Projection') !== r.nested_projection_2026_window) {
        errors.push(`${at}: nested_projection_2026_window does not match nested_verdicts.2026`);
      }
      if (!r.reason_code.startsWith(r.verdict)) {
        errors.push(`${at}: reason_code "${r.reason_code}" does not match verdict "${r.verdict}"`);
      }
      if (meta && !(r.evidence_tier in meta.evidence_tiers)) {
        errors.push(`${at}: evidence_tier "${r.evidence_tier}" is not defined in meta.json`);
      }
      if (r.max_corr_partner !== null && !knownMetric(r.max_corr_partner)) {
        errors.push(`${at}: max_corr_partner "${r.max_corr_partner}" is not in metrics.json`);
      }
    });
    if (pinned > 0) {
      notes.push(
        `evaluations.json: ${pinned} audited row(s) where the fold-mean ΔRMSE% lies outside its bootstrap CI (pinned in src/data/knownExceptions.ts; shown with a note in the app)`,
      );
    }
  }

  // ------------------------------------------------------------ model comparisons
  if (comparisons) {
    const checkModel = (at: string, id: string) => {
      const set = id.split('|')[0];
      if (set.startsWith('B0+')) {
        const m = set.slice(3);
        if (!knownMetric(m)) errors.push(`${at}: model "${id}" references unknown metric "${m}"`);
      }
    };
    comparisons.comparisons.forEach((c, i) => {
      const at = `model_comparisons.json comparisons[${i}] (${c.target}: ${c.comparison})`;
      if (!knownTarget(c.target)) errors.push(`${at}: target "${c.target}" is not in targets.json`);
      checkModel(at, c.model_a);
      checkModel(at, c.model_b);
      if ((c.ci_low_pct === null) !== (c.ci_high_pct === null)) errors.push(`${at}: only one CI bound is null`);
      if (c.ci_low_pct === null || c.ci_high_pct === null) {
        if (c.delta_pct !== 0 || c.delta_rmse !== 0) {
          errors.push(`${at}: CI is missing although the models differ (delta_pct=${c.delta_pct})`);
        }
      } else if (c.ci_low_pct > c.ci_high_pct) {
        errors.push(`${at}: CI low > CI high`);
      } else if (!brackets(c.ci_low_pct, c.delta_pct, c.ci_high_pct)) {
        errors.push(`${at}: CI [${c.ci_low_pct}, ${c.ci_high_pct}] does not bracket ${c.delta_pct}`);
      }
      const nested = c.sample === 'outer years 2021-2025 (nested)';
      if (nested && (c.years_a_better === undefined || c.n_years === undefined || c.cohort !== undefined)) {
        errors.push(`${at}: nested rows need years_a_better and n_years and no cohort`);
      }
      if (!nested && (c.cohort === undefined || c.years_a_better !== undefined || c.n_years !== undefined)) {
        errors.push(`${at}: 2026 rows need a cohort and no per-year counts`);
      }
      if (c.years_a_better !== undefined && c.n_years !== undefined && c.years_a_better > c.n_years) {
        errors.push(`${at}: years_a_better > n_years`);
      }
    });
    const seen = new Set<string>();
    comparisons.per_year.forEach((p, i) => {
      const at = `model_comparisons.json per_year[${i}]`;
      if (!knownTarget(p.study_id)) errors.push(`${at}: study_id "${p.study_id}" is not in targets.json`);
      checkModel(at, p.model_id);
      const key = `${p.study_id}|${p.model_id}|${p.outer_year}`;
      if (seen.has(key)) errors.push(`${at}: duplicate study/model/year`);
      seen.add(key);
    });
  }

  // ------------------------------------------------------------ flagships
  if (flagships) {
    flagships.forEach((f, i) => {
      for (const col of ['2019–25 pooled, % [cluster CI]', 'Nested 2021–25, %', '2026 holdout, %'] as const) {
        const ci = parseCiString(f[col]);
        if (!ci) errors.push(`flagships.json[${i}] ${col}: unparseable "${f[col]}"`);
        else if (!brackets(ci.lo, ci.est, ci.hi)) {
          errors.push(`flagships.json[${i}] ${col}: CI does not bracket its estimate ("${f[col]}")`);
        }
      }
    });
  }

  // ------------------------------------------------------------ casebook
  if (casebook) {
    const contrasts = new Set<string>();
    const checkContrast = (at: string, contrast: string) => {
      const [t, m, ...rest] = contrast.split(':');
      if (!t || !m || rest.length) {
        errors.push(`${at}: contrast "${contrast}" must be "target:metric"`);
        return;
      }
      if (!knownTarget(t)) errors.push(`${at}: contrast "${contrast}" references unknown target "${t}"`);
      if (!knownMetric(m)) errors.push(`${at}: contrast "${contrast}" references unknown metric "${m}"`);
    };
    casebook.cases.forEach((c, i) => {
      const at = `casebook.json cases[${i}] (${c.player})`;
      checkContrast(at, c.contrast);
      if (c.contrast !== `${c.target}:${c.metric}`) errors.push(`${at}: contrast does not match target/metric`);
      if (!knownTarget(c.target)) errors.push(`${at}: unknown target "${c.target}"`);
      if (!knownMetric(c.metric)) errors.push(`${at}: unknown metric "${c.metric}"`);
      contrasts.add(c.contrast);
      if (c.outcome_season !== c.feature_season + 1) errors.push(`${at}: outcome_season must be feature_season + 1`);
      if (Math.abs(c.forecast_with - c.forecast_without - c.forecast_change) > 1e-4) {
        errors.push(`${at}: forecast_change does not equal forecast_with − forecast_without`);
      }
      const aec = Math.abs(c.forecast_with - c.observed) - Math.abs(c.forecast_without - c.observed);
      if (Math.abs(aec - c.abs_error_change) > 1e-4) errors.push(`${at}: abs_error_change is inconsistent`);
      if (c.improved !== c.abs_error_change < 0) errors.push(`${at}: improved flag disagrees with abs_error_change`);
    });
    casebook.cohorts.forEach((c, i) => {
      const at = `casebook.json cohorts[${i}] (${c.contrast} / ${c.cohort})`;
      checkContrast(at, c.contrast);
      if (!contrasts.has(c.contrast)) errors.push(`${at}: contrast has no curated cases`);
      if (c.ci_low > c.ci_high || !brackets(c.ci_low, c.delta_rmse, c.ci_high)) {
        errors.push(`${at}: CI [${c.ci_low}, ${c.ci_high}] does not bracket ${c.delta_rmse}`);
      }
    });
    casebook.unit_translation.forEach((u, i) => {
      const at = `casebook.json unit_translation[${i}] (${u.contrast})`;
      checkContrast(at, u.contrast);
      if (!contrasts.has(u.contrast)) errors.push(`${at}: contrast has no curated cases`);
      if (u.ci_low > u.ci_high || !brackets(u.ci_low, u.delta_rmse, u.ci_high)) {
        errors.push(`${at}: CI [${u.ci_low}, ${u.ci_high}] does not bracket ${u.delta_rmse}`);
      }
    });
  }

  // ------------------------------------------------------------ fantasy
  if (fantasy) {
    const keyOf = (r: { group: string; outcome: string; kind: string; target: string; base: string; aug: string; sample: string }) =>
      [r.group, r.outcome, r.kind, r.target, r.base, r.aug, r.sample].join('|');
    const resultKeys = new Set<string>();
    fantasy.results.forEach((r, i) => {
      const at = `fantasy.json results[${i}] (${r.target} → ${r.outcome}, ${r.kind}, ${r.sample})`;
      const key = keyOf(r);
      if (resultKeys.has(key)) errors.push(`${at}: duplicate result`);
      resultKeys.add(key);
      if (r.kind === 'direct_metric_added') {
        const m = metricIds.get(r.target);
        if (metrics && !m) errors.push(`${at}: direct metric "${r.target}" is not in metrics.json`);
        else if (m && !m.player_types.includes(r.group)) {
          errors.push(`${at}: metric "${r.target}" is not a ${r.group} metric`);
        }
      } else {
        for (const part of r.target.split('+')) {
          const tid = FANTASY_TARGET_ALIASES[part];
          if (!tid) errors.push(`${at}: unknown target forecast "${part}"`);
          else if (!knownTarget(tid)) errors.push(`${at}: target forecast "${part}" maps to unknown target "${tid}"`);
          else if (targets && targetGroup.get(tid) !== r.group) {
            errors.push(`${at}: target forecast "${part}" is not a ${r.group} target`);
          }
        }
      }
      if (!r.base.startsWith('BF') || !r.aug.startsWith('BF')) errors.push(`${at}: base/aug must be built on BF`);
      if (r.ci_low_pct > r.ci_high_pct || !brackets(r.ci_low_pct, r.delta_pct, r.ci_high_pct)) {
        errors.push(`${at}: CI [${r.ci_low_pct}, ${r.ci_high_pct}] does not bracket ${r.delta_pct}`);
      }
      const sbLo = r.season_block_ci_low_pct;
      const sbHi = r.season_block_ci_high_pct;
      if ((sbLo === null) !== (sbHi === null)) errors.push(`${at}: only one season-block CI bound is null`);
      if (sbLo !== null && sbHi !== null && (sbLo > sbHi || !brackets(sbLo, r.delta_pct, sbHi))) {
        errors.push(`${at}: season-block CI [${sbLo}, ${sbHi}] does not bracket ${r.delta_pct}`);
      }
      if ((r.p_adjusted === null) !== (r.adjustment === null)) {
        errors.push(`${at}: p_adjusted and adjustment must both be present or both be null`);
      }
      if (r.years_improved > r.n_years) errors.push(`${at}: years_improved > n_years`);
      const expected = expectedFantasyVerdict(r);
      if (expected !== r.verdict) {
        errors.push(`${at}: verdict "${r.verdict}" contradicts the protocol rule (expected "${expected}")`);
      }
    });
    fantasy.by_year.forEach((b, i) => {
      if (!resultKeys.has(keyOf(b))) {
        errors.push(`fantasy.json by_year[${i}] (${b.target} → ${b.outcome}, ${b.outcome_season}): no matching result row`);
      }
    });
    fantasy.level1.forEach((l, i) => {
      const at = `fantasy.json level1[${i}] (${l.target_forecast} → ${l.fantasy_outcome})`;
      if (!FANTASY_TARGET_ALIASES[l.target_forecast]) errors.push(`${at}: unknown target forecast`);
      if (l.ci_low > l.ci_high || !brackets(l.ci_low, l.spearman_2021_2025, l.ci_high)) {
        errors.push(`${at}: CI does not bracket the Spearman estimate`);
      }
    });
    fantasy.decision.forEach((d, i) => {
      const at = `fantasy.json decision[${i}] (${d.group}, k=${d.k}, ${d.sample})`;
      if (d.ci_low > d.ci_high || !brackets(d.ci_low, d.delta_mean_realized_value, d.ci_high)) {
        errors.push(`${at}: value CI does not bracket its estimate`);
      }
      if (d.spearman_ci_low > d.spearman_ci_high || !brackets(d.spearman_ci_low, d.delta_spearman, d.spearman_ci_high)) {
        errors.push(`${at}: Spearman CI does not bracket its estimate`);
      }
    });
  }

  return { errors, warnings, notes };
}
