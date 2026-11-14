/** Number formatting. Negative numbers use the true minus sign (U+2212). */
export const MINUS = '−';

function core(x: number, digits: number): string {
  if (!Number.isFinite(x)) return '—';
  const s = Math.abs(x).toFixed(digits);
  if (Number(s) === 0) return s; // never print "−0.00"
  return (x < 0 ? MINUS : '') + s;
}

/** 1234.5 -> "1234.50"; −0.004 -> "0.00". */
export function fmt(x: number | null | undefined, digits = 2): string {
  if (x === null || x === undefined) return '—';
  return core(x, digits);
}

/** Explicit sign: +0.08, −4.28, 0.00. */
export function fmtSigned(x: number | null | undefined, digits = 2): string {
  if (x === null || x === undefined) return '—';
  const s = core(x, digits);
  if (s === '—' || s.startsWith(MINUS) || Number(s) === 0) return s;
  return `+${s}`;
}

/** Signed percentage: "−4.28%". */
export function fmtPct(x: number | null | undefined, digits = 2): string {
  const s = fmtSigned(x, digits);
  return s === '—' ? s : `${s}%`;
}

/** "[−5.15, −3.02]" (signed). */
export function fmtCI(lo: number | null | undefined, hi: number | null | undefined, digits = 2): string {
  if (lo === null || lo === undefined || hi === null || hi === undefined) return 'no interval';
  return `[${fmtSigned(lo, digits)}, ${fmtSigned(hi, digits)}]`;
}

/** Thousands separators for counts. */
export function fmtInt(n: number | null | undefined): string {
  if (n === null || n === undefined || !Number.isFinite(n)) return '—';
  return Math.round(n).toLocaleString('en-US');
}

/** Share in 0..1 as a percentage: 0.714 -> "71%". */
export function fmtShare(x: number | null | undefined, digits = 0): string {
  if (x === null || x === undefined || !Number.isFinite(x)) return '—';
  return `${(x * 100).toFixed(digits)}%`;
}

/** p-values: "0.018", "< 0.001". */
export function fmtP(p: number | null | undefined): string {
  if (p === null || p === undefined) return 'not adjusted';
  if (p < 0.001) return '< 0.001';
  return p.toFixed(3);
}

/** Baseball rate style without the leading zero: 0.2571 -> ".257"; 1.25 -> "1.250". */
export function fmtRate3(x: number | null | undefined): string {
  if (x === null || x === undefined || !Number.isFinite(x)) return '—';
  const s = core(x, 3);
  return s.replace(/^(−?)0\./, '$1.');
}

/** Significant-digit formatting for values in target units (RMSE, forecasts). */
export function fmtUnits(x: number | null | undefined, digits = 3): string {
  if (x === null || x === undefined) return '—';
  return core(x, digits);
}

/** Choose decimals so that small target-unit values (e.g. wOBA 0.0009) stay readable. */
export function digitsFor(values: number[]): number {
  const m = Math.max(...values.map((v) => Math.abs(v)).filter((v) => Number.isFinite(v)), 0);
  if (m === 0) return 3;
  if (m < 0.01) return 5;
  if (m < 0.1) return 4;
  if (m < 10) return 3;
  return 2;
}
