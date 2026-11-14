import { describe, expect, it } from 'vitest';
import { fmt, fmtCI, fmtP, fmtPct, fmtRate3, fmtSigned, MINUS } from '../../src/lib/format';

describe('number formatting', () => {
  it('uses a true minus sign and an explicit plus sign', () => {
    expect(fmtPct(-4.284967)).toBe(`${MINUS}4.28%`);
    expect(fmtPct(0.077738)).toBe('+0.08%');
    expect(fmtSigned(-7.498349)).toBe(`${MINUS}7.50`);
  });
  it('never prints negative zero', () => {
    expect(fmt(-0)).toBe('0.00');
    expect(fmtSigned(-0.001)).toBe('0.00');
    expect(fmtPct(-0.004)).toBe('0.00%');
  });
  it('formats intervals, p-values and rates', () => {
    expect(fmtCI(-5.147414, -3.016109)).toBe(`[${MINUS}5.15, ${MINUS}3.02]`);
    expect(fmtCI(null, 1)).toBe('no interval');
    expect(fmtP(0.0004)).toBe('< 0.001');
    expect(fmtP(0.018)).toBe('0.018');
    expect(fmtP(null)).toBe('not adjusted');
    expect(fmtRate3(180 / 700)).toBe('.257');
  });
});
