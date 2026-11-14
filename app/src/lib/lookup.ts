/** Result lookups. A pair that is absent from the data is "Not evaluated" — never a verdict. */
import type {
  Comparison,
  Evaluation,
  FantasyByYear,
  FantasyKind,
  FantasyResult,
  FantasySample,
  Level1,
  Metric,
  PerYear,
} from '../data/schemas';
import { NOT_EVALUATED, type VerdictKey } from './labels';

export type EvaluationLookup =
  | { status: 'evaluated'; row: Evaluation }
  | { status: 'not-evaluated'; metric: string; target: string };

export type EvaluationIndex = Map<string, Evaluation>;

const pairKey = (metric: string, target: string) => `${metric}\u0000${target}`;

export function buildEvaluationIndex(rows: Evaluation[]): EvaluationIndex {
  const idx: EvaluationIndex = new Map();
  for (const r of rows) idx.set(pairKey(r.metric, r.target), r);
  return idx;
}

export function lookupEvaluation(
  source: Evaluation[] | EvaluationIndex,
  metric: string,
  target: string,
): EvaluationLookup {
  const row = Array.isArray(source)
    ? source.find((r) => r.metric === metric && r.target === target)
    : source.get(pairKey(metric, target));
  return row ? { status: 'evaluated', row } : { status: 'not-evaluated', metric, target };
}

/** The verdict to display for a lookup: the data's verdict, or "Not evaluated". */
export function displayVerdict(l: EvaluationLookup): VerdictKey {
  return l.status === 'evaluated' ? l.row.verdict : NOT_EVALUATED;
}

/** Every evaluation of one metric, in target order. */
export function evaluationsForMetric(rows: Evaluation[], metric: string, targetOrder?: string[]): Evaluation[] {
  const out = rows.filter((r) => r.metric === metric);
  if (targetOrder) out.sort((a, b) => targetOrder.indexOf(a.target) - targetOrder.indexOf(b.target));
  return out;
}

export function evaluationsForTarget(rows: Evaluation[], target: string): Evaluation[] {
  return rows.filter((r) => r.target === target);
}

/** True when the published point estimate lies outside its published interval (see knownExceptions.ts). */
export function estimateOutsideCi(r: Pick<Evaluation, 'delta_pct' | 'ci_low_pct' | 'ci_high_pct'>): boolean {
  return r.delta_pct < r.ci_low_pct - 1e-9 || r.delta_pct > r.ci_high_pct + 1e-9;
}

export function metricIndex(metrics: Metric[]): Map<string, Metric> {
  return new Map(metrics.map((m) => [m.id, m]));
}

// ---------------------------------------------------------------- model comparisons
export const NESTED_SAMPLE = 'outer years 2021-2025 (nested)';
export const SAMPLE_2026 = '2026 (frozen-in-workflow, exploratory)';

export function findComparison(
  rows: Comparison[],
  target: string,
  comparison: string,
  sample: string = NESTED_SAMPLE,
  cohort?: string,
): Comparison | undefined {
  return rows.find(
    (c) =>
      c.target === target &&
      c.comparison === comparison &&
      c.sample === sample &&
      (cohort === undefined || c.cohort === cohort),
  );
}

export function comparisonsFor(rows: Comparison[], target: string, sample: string, cohort?: string): Comparison[] {
  return rows.filter((c) => c.target === target && c.sample === sample && (cohort === undefined || c.cohort === cohort));
}

export function perYearFor(rows: PerYear[], target: string): PerYear[] {
  return rows.filter((p) => p.study_id === target);
}

// ---------------------------------------------------------------- fantasy
export interface FantasyQuery {
  kind: FantasyKind;
  target: string;
  outcome: string;
  sample: FantasySample;
}

export function findFantasyResult(rows: FantasyResult[], q: FantasyQuery): FantasyResult | undefined {
  return rows.find((r) => r.kind === q.kind && r.target === q.target && r.outcome === q.outcome && r.sample === q.sample);
}

export function fantasyByYearFor(rows: FantasyByYear[], r: FantasyResult): FantasyByYear[] {
  return rows
    .filter(
      (b) =>
        b.kind === r.kind &&
        b.target === r.target &&
        b.outcome === r.outcome &&
        b.base === r.base &&
        b.aug === r.aug,
    )
    .sort((a, b) => a.outcome_season - b.outcome_season);
}

export function level1For(rows: Level1[], target: string, outcome: string): Level1 | undefined {
  return rows.find((l) => l.target_forecast === target && l.fantasy_outcome === outcome);
}

/** Targets (forecast aliases, joint sets or metric ids) that have results for a kind. */
export function fantasyTargetsForKind(rows: FantasyResult[], kind: FantasyKind): string[] {
  const seen: string[] = [];
  for (const r of rows) if (r.kind === kind && !seen.includes(r.target)) seen.push(r.target);
  return seen;
}

/** Outcomes with a result for a kind + target, in data order. */
export function fantasyOutcomesFor(rows: FantasyResult[], kind: FantasyKind, target: string): string[] {
  const seen: string[] = [];
  for (const r of rows) if (r.kind === kind && r.target === target && !seen.includes(r.outcome)) seen.push(r.outcome);
  return seen;
}
