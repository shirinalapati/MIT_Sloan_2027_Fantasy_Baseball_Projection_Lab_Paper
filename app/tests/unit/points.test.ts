import { describe, expect, it } from 'vitest';
import { pointsFor, teamPoints, withDerivedOuts, type PlayerLine } from '../../src/lib/fantasyMath';
import { EXAMPLE_SCORING, parseScoring, provenanceDates, provenanceValue } from '../../src/lib/scoring';
import { readData } from '../helpers/data';

describe('points scoring', () => {
  it('sums weight × stat, ignores stats without a weight, and treats missing stats as zero', () => {
    const w = { R: 1, HR: 4, SB: 2, CS: -1 };
    expect(pointsFor({ R: 80, HR: 25, SB: 10, AB: 550 }, w)).toBe(80 + 100 + 20); // CS missing = 0, AB unweighted
  });

  it('applies negative weights', () => {
    expect(pointsFor({ W: 10, ER: 60, K: 150 }, { W: 5, ER: -2, K: 1 })).toBe(50 - 120 + 150);
  });

  it('team points are the sum of player points', () => {
    const players: PlayerLine[] = [
      { id: '1', name: 'A', stats: { R: 10, HR: 1 } },
      { id: '2', name: 'B', stats: { R: 5, HR: 3 } },
    ];
    expect(teamPoints(players, { R: 1, HR: 4 })).toBe(10 + 4 + 5 + 12);
  });

  it('derives outs from decimal innings for systems that score outs', () => {
    expect(pointsFor(withDerivedOuts({ IP: 180.33, K: 200 }), { OUTS: 1, K: 3 })).toBe(541 + 600);
  });

  it('parses the bundled scoring.json (batters/pitchers weights plus provenance) or falls back', () => {
    let raw: unknown = null;
    try {
      raw = readData('scoring');
    } catch {
      raw = null;
    }
    if (raw === null) {
      expect(parseScoring(raw)).toBeNull();
      return;
    }
    const cfg = parseScoring(raw)!;
    expect(cfg).not.toBeNull();
    expect(cfg.origin).toBe('scoring.json');
    expect(Object.keys(cfg.batters).length).toBeGreaterThan(0);
    expect(Object.keys(cfg.pitchers).length).toBeGreaterThan(0);
    expect(Object.values(cfg.batters).every((v) => Number.isFinite(v))).toBe(true);
    expect(provenanceValue(cfg, ['source'])).toBeTruthy();
    expect(provenanceDates(cfg).length).toBeGreaterThan(0);
  });

  it('rejects unusable scoring shapes so the lab can fall back to example weights', () => {
    expect(parseScoring(null)).toBeNull();
    expect(parseScoring({ batters: { R: 'one' }, pitchers: { W: 1 } })).toBeNull();
    expect(parseScoring({ batters: {}, pitchers: { W: 1 } })).toBeNull();
    expect(parseScoring([1, 2])).toBeNull();
    expect(EXAMPLE_SCORING.origin).toBe('example');
  });
});
