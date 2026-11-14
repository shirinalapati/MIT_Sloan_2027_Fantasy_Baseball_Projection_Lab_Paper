import { describe, expect, it } from 'vitest';
import type { FantasyResult } from '../../src/data/schemas';
import { compare2026, comparisonSentence, evaluationSummary, fantasyResultSentence } from '../../src/lib/wording';
import { lookupEvaluation } from '../../src/lib/lookup';
import { loadAll } from '../helpers/data';

const data = loadAll();
const ctx = { forecast: 'wOBA forecast', outcome: 'home runs (HR)' };

function variant(over: Partial<FantasyResult>): FantasyResult {
  const base = data.fantasy.results[0];
  return { ...base, ...over };
}

describe('fantasy verdict wording', () => {
  it('says "adds information" only when the verdict says so', () => {
    for (const r of data.fantasy.results) {
      const s = fantasyResultSentence(r, ctx);
      if (r.verdict === 'adds information') expect(s).toMatch(/adds information/);
      else expect(s).not.toMatch(/adds information/);
    }
  });

  it('describes a multiplicity-fragile gain without claiming information', () => {
    const s = fantasyResultSentence(variant({ verdict: 'gain not robust to multiplicity', ci_low_pct: -1, ci_high_pct: -0.1, delta_pct: -0.5, p_adjusted: 0.2, adjustment: 'Holm (8 primary)' }), ctx);
    expect(s).toMatch(/does not survive the multiplicity adjustment/);
    expect(s).toMatch(/not counted as adding information/);
  });

  it('makes nulls and harms explicit', () => {
    expect(fantasyResultSentence(variant({ verdict: 'no detectable gain' }), ctx)).toMatch(/includes zero: no detectable gain/);
    expect(fantasyResultSentence(variant({ verdict: 'harmful', ci_low_pct: 0.1, ci_high_pct: 0.3, delta_pct: 0.2 }), ctx)).toMatch(/less accurate \(harmful\)/);
  });

  it('labels 2026 directional results as directional only', () => {
    const s = fantasyResultSentence(variant({ verdict: 'directional gain (exploratory; CI excludes 0)', sample: '2026 (exploratory)', p_adjusted: null, adjustment: null }), ctx);
    expect(s).toMatch(/^In 2026/);
    expect(s).toMatch(/directional only/);
  });

  it('compares 2026 with 2021–2025 in plain language', () => {
    const pooled = variant({ delta_pct: -1.0 });
    expect(compare2026(pooled, variant({ delta_pct: -1.5, ci_low_pct: -3, ci_high_pct: 0.2 }))).toBe(
      'This 2026 effect was directionally consistent with 2021–2025, but its interval included zero.',
    );
    expect(compare2026(pooled, variant({ delta_pct: 0.4, ci_low_pct: -0.5, ci_high_pct: 1 }))).toMatch(/went the other way/);
  });

  it('never phrases a fantasy result as a player forecast', () => {
    for (const r of data.fantasy.results.slice(0, 60)) {
      expect(fantasyResultSentence(r, ctx)).not.toMatch(/\bwill\b/);
    }
  });
});

describe('evaluation and comparison wording', () => {
  it('describes Projection as historical improvement and Diagnostic as a human-specified label', () => {
    const t = data.targets.find((x) => x.id === 'baserunning_rv')!;
    const proj = lookupEvaluation(data.evaluations, 'sprint_speed', 'baserunning_rv');
    if (proj.status !== 'evaluated') throw new Error('missing row');
    expect(evaluationSummary(proj.row, 'Statcast sprint speed', t)).toMatch(/^Historically, adding Statcast sprint speed improved next-season baserunning/);
    const w = data.targets.find((x) => x.id === 'hitting_woba')!;
    const diag = lookupEvaluation(data.evaluations, 'sprint_speed', 'hitting_woba');
    if (diag.status !== 'evaluated') throw new Error('missing row');
    const s = evaluationSummary(diag.row, 'Statcast sprint speed', w);
    expect(s).toMatch(/did not pass the projection test for next-season wOBA/);
    expect(s).toMatch(/human-specified/);
  });

  it('comparison sentences follow the interval', () => {
    expect(comparisonSentence(-7.5, -9.4, -5.5, 'ADM', 'B0')).toMatch(/ADM was more accurate than B0/);
    expect(comparisonSentence(5.2, 2.9, 7.6, 'KS', 'ADM')).toMatch(/KS was less accurate than ADM/);
    expect(comparisonSentence(0.2, -1, 1.4, 'EN', 'ADM')).toMatch(/No clear difference/);
    expect(comparisonSentence(0, null, null, 'FAM', 'ADM')).toMatch(/identical forecasts/);
  });
});
