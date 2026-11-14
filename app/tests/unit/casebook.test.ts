import { describe, expect, it } from 'vitest';
import { DEFAULT_CASE_FILTER, displayName, filterCases, matchesPlayer, normalizeName, summarizeCases } from '../../src/lib/casebook';
import type { Case } from '../../src/data/schemas';
import { loadAll } from '../helpers/data';

const { casebook } = loadAll();
const cases = casebook.cases;

const mk = (over: Partial<Case>): Case => ({ ...cases[0], ...over });

describe('casebook filters', () => {
  it('no filter returns everything', () => {
    expect(filterCases(cases, DEFAULT_CASE_FILTER)).toHaveLength(cases.length);
  });

  it('filters by contrast, selection type, season and result together', () => {
    const f = { ...DEFAULT_CASE_FILTER, contrast: 'pitching_fip:stuff_plus', selection: 'largest decrease' as const };
    const rows = filterCases(cases, f);
    expect(rows).toHaveLength(20);
    expect(rows.every((c) => c.contrast === 'pitching_fip:stuff_plus' && c.selection === 'largest decrease')).toBe(true);
    const improved = filterCases(cases, { ...f, result: 'improved' });
    const worsened = filterCases(cases, { ...f, result: 'worsened' });
    expect(improved.length + worsened.length).toBe(20);
    expect(improved.every((c) => c.improved)).toBe(true);
    expect(worsened.every((c) => !c.improved)).toBe(true);
    const season = filterCases(cases, { ...DEFAULT_CASE_FILTER, season: 2023 });
    expect(season.length).toBeGreaterThan(0);
    expect(season.every((c) => c.outcome_season === 2023)).toBe(true);
  });

  it('keeps both successes and failures visible for every contrast', () => {
    for (const contrast of new Set(cases.map((c) => c.contrast))) {
      const s = summarizeCases(filterCases(cases, { ...DEFAULT_CASE_FILTER, contrast }));
      expect(s.improved).toBeGreaterThan(0);
      expect(s.worsened).toBeGreaterThan(0);
    }
  });

  it('player search ignores case, accents and name order', () => {
    const sample = [mk({ player: 'Acuña Jr., Ronald' }), mk({ player: 'Mateo, Jorge' })];
    expect(filterCases(sample, { ...DEFAULT_CASE_FILTER, query: 'acuna' })).toHaveLength(1);
    expect(filterCases(sample, { ...DEFAULT_CASE_FILTER, query: 'Jorge Mateo' })).toHaveLength(1);
    expect(filterCases(sample, { ...DEFAULT_CASE_FILTER, query: 'mateo, jorge' })).toHaveLength(1);
    expect(filterCases(sample, { ...DEFAULT_CASE_FILTER, query: 'zzz' })).toHaveLength(0);
    expect(matchesPlayer('Mateo, Jorge', '')).toBe(true);
    expect(normalizeName('  José  RAMÍREZ ')).toBe('jose ramirez');
    expect(displayName('Acuña Jr., Ronald')).toBe('Ronald Acuña Jr.');
  });

  it('summaries count improved and worsened', () => {
    const s = summarizeCases([mk({ improved: true }), mk({ improved: false }), mk({ improved: false })]);
    expect(s).toEqual({ n: 3, improved: 1, worsened: 2 });
  });
});
