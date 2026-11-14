/** Tiny scale helpers for hand-written SVG charts. */

export interface LinearScale {
  (v: number): number;
  domain: [number, number];
  range: [number, number];
  invert: (px: number) => number;
}

export function linearScale(domain: [number, number], range: [number, number]): LinearScale {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const span = d1 - d0 || 1;
  const f = ((v: number) => r0 + ((v - d0) / span) * (r1 - r0)) as LinearScale;
  f.domain = domain;
  f.range = range;
  f.invert = (px: number) => d0 + ((px - r0) / (r1 - r0 || 1)) * span;
  return f;
}

function niceStep(rough: number): number {
  const exp = Math.floor(Math.log10(rough));
  const base = 10 ** exp;
  const f = rough / base;
  const nice = f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10;
  return nice * base;
}

/** "Nice" tick values covering [min, max]. */
export function niceTicks(min: number, max: number, count = 5): number[] {
  if (!Number.isFinite(min) || !Number.isFinite(max)) return [];
  if (min === max) {
    const d = Math.abs(min) || 1;
    min -= d * 0.5;
    max += d * 0.5;
  }
  const step = niceStep((max - min) / Math.max(1, count));
  const start = Math.ceil(min / step - 1e-9) * step;
  const out: number[] = [];
  for (let v = start; v <= max + step * 1e-9; v += step) out.push(Math.abs(v) < step * 1e-9 ? 0 : Number(v.toFixed(10)));
  return out;
}

/** Extend a domain to nice bounds and (optionally) include zero. */
export function niceDomain(values: number[], opts: { includeZero?: boolean; pad?: number; count?: number } = {}): [number, number] {
  const { includeZero = true, pad = 0.06, count = 5 } = opts;
  const finite = values.filter((v) => Number.isFinite(v));
  let lo = finite.length ? Math.min(...finite) : -1;
  let hi = finite.length ? Math.max(...finite) : 1;
  if (includeZero) {
    lo = Math.min(lo, 0);
    hi = Math.max(hi, 0);
  }
  if (lo === hi) {
    lo -= 1;
    hi += 1;
  }
  const span = hi - lo;
  lo -= span * pad;
  hi += span * pad;
  const ticks = niceTicks(lo, hi, count);
  const step = ticks.length > 1 ? ticks[1] - ticks[0] : span;
  const nlo = Math.floor(lo / step + 1e-9) * step;
  const nhi = Math.ceil(hi / step - 1e-9) * step;
  return [Number(nlo.toFixed(10)), Number(nhi.toFixed(10))];
}

/** Decimal places needed to print tick values without noise. */
export function tickDigits(ticks: number[]): number {
  for (let d = 0; d <= 6; d++) {
    const k = 10 ** d;
    if (ticks.every((t) => Math.abs(t * k - Math.round(t * k)) < 1e-6)) return d;
  }
  return 6;
}

/** Interval polarity: entirely below zero, entirely above zero, or touching/including zero. */
export type Polarity = 'better' | 'worse' | 'neutral';
export function polarity(lo: number | null | undefined, hi: number | null | undefined): Polarity {
  if (lo === null || lo === undefined || hi === null || hi === undefined) return 'neutral';
  if (hi < 0) return 'better';
  if (lo > 0) return 'worse';
  return 'neutral';
}
