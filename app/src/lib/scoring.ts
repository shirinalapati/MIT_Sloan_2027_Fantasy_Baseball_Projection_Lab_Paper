/**
 * Points-scoring configuration for the illustrative Value Lab.
 *
 * scoring.json (optional) is the research repo's verified default scoring, read by the research
 * pipeline as `batters` / `pitchers` maps of {stat: weight}. Any other top-level fields are treated
 * as provenance (source, date, ...) and displayed verbatim. If the file is absent or unreadable the
 * lab falls back to clearly labelled example weights.
 */
import type { Weights } from './fantasyMath';

export interface ScoringConfig {
  origin: 'scoring.json' | 'example';
  batters: Weights;
  pitchers: Weights;
  provenance: Array<{ key: string; value: string }>;
}

/** Example weights for illustration only. They are not any platform's default. */
export const EXAMPLE_SCORING: ScoringConfig = {
  origin: 'example',
  batters: { R: 1, HR: 4, RBI: 1, SB: 2, H: 1 },
  pitchers: { W: 5, SV: 5, K: 1, IP: 3, ER: -2, BBH: -1 },
  provenance: [],
};

function isWeights(v: unknown): v is Weights {
  if (!v || typeof v !== 'object' || Array.isArray(v)) return false;
  const entries = Object.entries(v as Record<string, unknown>);
  return entries.length > 0 && entries.every(([, w]) => typeof w === 'number' && Number.isFinite(w));
}

function flatten(prefix: string, v: unknown, out: Array<{ key: string; value: string }>, depth = 0): void {
  if (v === null || v === undefined) return;
  if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') {
    out.push({ key: prefix, value: String(v) });
  } else if (Array.isArray(v)) {
    if (v.every((x) => typeof x === 'string' || typeof x === 'number')) out.push({ key: prefix, value: v.join(', ') });
  } else if (typeof v === 'object' && depth < 2) {
    for (const [k, x] of Object.entries(v as Record<string, unknown>)) flatten(`${prefix}.${k}`, x, out, depth + 1);
  }
}

/** Parse scoring.json leniently. Returns null when the shape is unusable. */
export function parseScoring(raw: unknown): ScoringConfig | null {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  const obj = raw as Record<string, unknown>;
  if (!isWeights(obj.batters) || !isWeights(obj.pitchers)) return null;
  const provenance: Array<{ key: string; value: string }> = [];
  for (const [k, v] of Object.entries(obj)) {
    if (k === 'batters' || k === 'pitchers') continue;
    flatten(k, v, provenance);
  }
  return { origin: 'scoring.json', batters: { ...obj.batters }, pitchers: { ...obj.pitchers }, provenance };
}

/** ISO dates (YYYY-MM-DD) mentioned anywhere in the provenance fields, in order of appearance. */
export function provenanceDates(cfg: ScoringConfig): string[] {
  const out: string[] = [];
  for (const p of cfg.provenance) for (const m of p.value.matchAll(/\b\d{4}-\d{2}-\d{2}\b/g)) if (!out.includes(m[0])) out.push(m[0]);
  return out;
}

/** Find a provenance value whose key mentions one of the given words (e.g. "source", "date"). */
export function provenanceValue(cfg: ScoringConfig, words: string[]): string | undefined {
  const hit = cfg.provenance.find((p) => words.some((w) => p.key.toLowerCase().includes(w)));
  return hit?.value;
}

export const STAT_LABELS: Record<string, string> = {
  R: 'Runs',
  HR: 'Home runs',
  RBI: 'RBI',
  SB: 'Stolen bases',
  AB: 'At-bats',
  H: 'Hits',
  '1B': 'Singles',
  '2B': 'Doubles',
  '3B': 'Triples',
  BB: 'Walks',
  HBP: 'Hit by pitch',
  CS: 'Caught stealing',
  SO: 'Strikeouts (batter)',
  W: 'Wins',
  L: 'Losses',
  SV: 'Saves',
  HLD: 'Holds',
  BS: 'Blown saves',
  K: 'Strikeouts',
  IP: 'Innings pitched',
  OUTS: 'Outs recorded',
  ER: 'Earned runs',
  BBH: 'Walks + hits allowed',
  CG: 'Complete games',
  SHO: 'Shutouts',
  GS: 'Games started',
  RA: 'Runs allowed',
};

export function statLabel(stat: string, group: 'hitter' | 'pitcher'): string {
  if (group === 'pitcher' && stat === 'H') return 'Hits allowed';
  if (group === 'pitcher' && stat === 'BB') return 'Walks allowed';
  if (group === 'pitcher' && stat === 'HR') return 'Home runs allowed';
  if (group === 'pitcher' && stat === 'HBP') return 'Hit batters';
  return STAT_LABELS[stat] ?? stat;
}
