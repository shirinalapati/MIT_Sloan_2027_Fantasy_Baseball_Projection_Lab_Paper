import { describe, expect, it } from 'vitest';
import {
  buildEvaluationIndex,
  displayVerdict,
  estimateOutsideCi,
  evaluationsForMetric,
  fantasyOutcomesFor,
  findComparison,
  findFantasyResult,
  level1For,
  lookupEvaluation,
  NESTED_SAMPLE,
} from '../../src/lib/lookup';
import { NOT_EVALUATED } from '../../src/lib/labels';
import { loadAll } from '../helpers/data';

const data = loadAll();

describe('metric × target lookup', () => {
  it('finds sprint speed × baserunning as Projection with the published numbers', () => {
    const l = lookupEvaluation(data.evaluations, 'sprint_speed', 'baserunning_rv');
    expect(l.status).toBe('evaluated');
    expect(displayVerdict(l)).toBe('Projection');
    if (l.status === 'evaluated') {
      expect(l.row.delta_pct).toBeCloseTo(-4.284967, 6);
      expect(l.row.ci_low_pct).toBeCloseTo(-5.147414, 6);
      expect(l.row.ci_high_pct).toBeCloseTo(-3.016109, 6);
      expect(l.row.n_folds).toBe(7);
    }
  });

  it('finds sprint speed × wOBA as Diagnostic (same metric, different job)', () => {
    const idx = buildEvaluationIndex(data.evaluations);
    expect(displayVerdict(lookupEvaluation(idx, 'sprint_speed', 'hitting_woba'))).toBe('Diagnostic');
  });

  it('returns "Not evaluated" — never a verdict — for pairs absent from the data', () => {
    const idx = buildEvaluationIndex(data.evaluations);
    const pitcherMetricOnHitterTarget = lookupEvaluation(idx, 'stuff_plus', 'hitting_woba');
    expect(pitcherMetricOnHitterTarget.status).toBe('not-evaluated');
    expect(displayVerdict(pitcherMetricOnHitterTarget)).toBe(NOT_EVALUATED);
    expect(displayVerdict(lookupEvaluation(idx, 'sprint_speed', 'pitching_fip'))).toBe('Not evaluated');
    expect(displayVerdict(lookupEvaluation(idx, 'no_such_metric', 'hitting_woba'))).toBe('Not evaluated');
    expect(displayVerdict(lookupEvaluation(data.evaluations, 'sprint_speed', 'no_such_target'))).toBe('Not evaluated');
  });

  it('every one of the 6 × 163 cells is either a data row or "Not evaluated"', () => {
    const idx = buildEvaluationIndex(data.evaluations);
    let evaluated = 0;
    let notEvaluated = 0;
    for (const m of data.metrics) {
      for (const t of data.targets) {
        const v = displayVerdict(lookupEvaluation(idx, m.id, t.id));
        if (v === 'Not evaluated') notEvaluated += 1;
        else evaluated += 1;
      }
    }
    expect(evaluated).toBe(data.evaluations.length);
    expect(evaluated + notEvaluated).toBe(data.metrics.length * data.targets.length);
  });

  it('lists a metric across targets in target order', () => {
    const rows = evaluationsForMetric(data.evaluations, 'sprint_speed', data.targets.map((t) => t.id));
    expect(rows.map((r) => r.target)).toEqual(['hitting_woba', 'baserunning_rv', 'defense_rv', 'overall_war']);
  });

  it('flags published estimates that sit outside their published interval', () => {
    const kpct = lookupEvaluation(data.evaluations, 'k_pct', 'pitching_fip');
    const sprint = lookupEvaluation(data.evaluations, 'sprint_speed', 'baserunning_rv');
    expect(kpct.status === 'evaluated' && estimateOutsideCi(kpct.row)).toBe(true);
    expect(sprint.status === 'evaluated' && estimateOutsideCi(sprint.row)).toBe(false);
  });
});

describe('model comparison lookup', () => {
  it('FIP: ADM vs B0 (selection policy lift) is about −7.498%', () => {
    const c = findComparison(data.model_comparisons.comparisons, 'pitching_fip', 'ADM vs B0 (selection policy lift)', NESTED_SAMPLE);
    expect(c).toBeDefined();
    expect(c!.delta_pct).toBeCloseTo(-7.498, 3);
    expect(c!.years_a_better).toBe(5);
  });
});

describe('fantasy result lookup', () => {
  it('finds the pre-specified FIP → ERA linkage and its verdict', () => {
    const r = findFantasyResult(data.fantasy.results, {
      kind: 'target_forecast_added',
      target: 'fip',
      outcome: 'ERA',
      sample: '2021-2025 pooled (primary)',
    });
    expect(r).toBeDefined();
    expect(r!.family).toBe('primary');
    expect(r!.verdict).toBe('adds information');
    expect(r!.delta_pct).toBeCloseTo(-1.168, 3);
  });

  it('returns undefined for untested combinations', () => {
    expect(
      findFantasyResult(data.fantasy.results, { kind: 'target_forecast_added', target: 'fip', outcome: 'HR', sample: '2021-2025 pooled (primary)' }),
    ).toBeUndefined();
  });

  it('lists outcomes for a forecast and finds Level 1 correlations', () => {
    const outs = fantasyOutcomesFor(data.fantasy.results, 'target_forecast_added', 'woba');
    expect(outs).toEqual(expect.arrayContaining(['R', 'HR', 'RBI', 'SB', 'AVG']));
    expect(level1For(data.fantasy.level1, 'woba', 'HR')?.note).toMatch(/association only/);
  });
});
