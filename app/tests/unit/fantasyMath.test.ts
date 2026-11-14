import { describe, expect, it } from 'vitest';
import {
  hitterTotals,
  inningsFromOuts,
  naiveMeanOfRates,
  outsFromInnings,
  parseStatInput,
  pitcherTotals,
  ratioFromTotals,
  ratioImpact,
  teamAvg,
  teamEra,
  teamWhip,
  type PlayerLine,
} from '../../src/lib/fantasyMath';

const hitters: PlayerLine[] = [
  { id: 'a', name: 'A', stats: { H: 30, AB: 100, R: 10, HR: 2, RBI: 9, SB: 1 } }, // .300 in 100 AB
  { id: 'b', name: 'B', stats: { H: 150, AB: 600, R: 80, HR: 25, RBI: 90, SB: 12 } }, // .250 in 600 AB
];
const pitchers: PlayerLine[] = [
  { id: 'r', name: 'Reliever', stats: { ER: 10, IP: 30, BBH: 30, W: 3, SV: 20, K: 40 } }, // ERA 3.00, WHIP 1.000
  { id: 's', name: 'Starter', stats: { ER: 70, IP: 180, BBH: 210, W: 12, SV: 0, K: 190 } }, // ERA 3.50, WHIP 1.167
];

describe('ratio categories are aggregated from components', () => {
  it('AVG = total H / total AB, not the mean of player AVGs', () => {
    expect(teamAvg(hitters)).toBeCloseTo(180 / 700, 10); // .2571
    const naive = naiveMeanOfRates(hitters, 'H', 'AB');
    expect(naive).toBeCloseTo(0.275, 10);
    expect(teamAvg(hitters)).not.toBeCloseTo(naive!, 3);
  });

  it('ERA = 9 × total ER / total IP, not the mean of player ERAs', () => {
    expect(teamEra(pitchers)).toBeCloseTo((9 * 80) / 210, 10); // 3.4286
    const naive = naiveMeanOfRates(pitchers, 'ER', 'IP', 9);
    expect(naive).toBeCloseTo(3.25, 10);
    expect(teamEra(pitchers)).not.toBeCloseTo(naive!, 2);
  });

  it('WHIP = total (BB + H) / total IP, not the mean of player WHIPs', () => {
    expect(teamWhip(pitchers)).toBeCloseTo(240 / 210, 10); // 1.1429
    const naive = naiveMeanOfRates(pitchers, 'BBH', 'IP');
    expect(naive).toBeCloseTo((1 + 210 / 180) / 2, 10);
    expect(teamWhip(pitchers)).not.toBeCloseTo(naive!, 3);
  });

  it('returns null (not NaN) when the denominator total is zero', () => {
    expect(teamAvg([{ id: 'x', name: 'x', stats: { H: 0, AB: 0 } }])).toBeNull();
    expect(teamEra([{ id: 'x', name: 'x', stats: { ER: 3, IP: 0 } }])).toBeNull();
    expect(teamWhip([])).toBeNull();
    expect(ratioFromTotals(1, 0)).toBeNull();
  });

  it('totals add counting stats and derive ratios from the summed components', () => {
    const h = hitterTotals(hitters);
    expect(h).toMatchObject({ R: 90, HR: 27, RBI: 99, SB: 13, AB: 700, H: 180 });
    expect(h.AVG).toBeCloseTo(180 / 700, 10);
    const p = pitcherTotals(pitchers);
    expect(p).toMatchObject({ W: 15, SV: 20, K: 230, IP: 210, ER: 80, BBH: 240 });
    expect(p.ERA).toBeCloseTo(720 / 210, 10);
    expect(p.WHIP).toBeCloseTo(240 / 210, 10);
  });

  it('a heavier-AB hitter moves team AVG more than a light-AB hitter with a higher AVG', () => {
    // leave-one-out impact computed from components
    const impA = ratioImpact(hitters, 'a', teamAvg)!;
    const impB = ratioImpact(hitters, 'b', teamAvg)!;
    expect(impA).toBeCloseTo(180 / 700 - 150 / 600, 10); // A (.300) raises team AVG
    expect(impB).toBeCloseTo(180 / 700 - 30 / 100, 10); // B (.250) lowers it
    expect(impA).toBeGreaterThan(0);
    expect(impB).toBeLessThan(0);
  });

  it('a low-ERA reliever lowers team ERA (negative impact)', () => {
    expect(ratioImpact(pitchers, 'r', teamEra)!).toBeCloseTo((9 * 80) / 210 - (9 * 70) / 180, 10);
    expect(ratioImpact(pitchers, 'r', teamEra)!).toBeLessThan(0);
  });

  it('innings and outs convert with IP = outs / 3', () => {
    expect(inningsFromOuts(541)).toBeCloseTo(180.3333, 4);
    expect(outsFromInnings(180.33)).toBe(541);
    expect(outsFromInnings(64)).toBe(192);
  });

  it('parses user input safely', () => {
    expect(parseStatInput('')).toBe(0);
    expect(parseStatInput('  12 ')).toBe(12);
    expect(parseStatInput('-4')).toBe(0);
    expect(parseStatInput('abc')).toBe(0);
    expect(parseStatInput('180.33')).toBeCloseTo(180.33, 10);
  });
});
