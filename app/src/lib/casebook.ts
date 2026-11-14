/** Casebook filtering and summaries. */
import type { Case, CaseSelection } from '../data/schemas';

export interface CaseFilter {
  contrast: string; // "target:metric" or "all"
  selection: CaseSelection | 'all';
  season: number | 'all'; // outcome season
  query: string;
  result: 'all' | 'improved' | 'worsened';
}

export const DEFAULT_CASE_FILTER: CaseFilter = {
  contrast: 'all',
  selection: 'all',
  season: 'all',
  query: '',
  result: 'all',
};

/** Lower-case and strip accents: "Acuña" -> "acuna". */
export function normalizeName(s: string): string {
  return s
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim();
}

/** "Schneemann, Daniel" -> "Daniel Schneemann"; "Acuña Jr., Ronald" -> "Ronald Acuña Jr.". */
export function displayName(player: string): string {
  const i = player.indexOf(',');
  if (i < 0) return player.trim();
  const last = player.slice(0, i).trim();
  const first = player.slice(i + 1).trim();
  return first ? `${first} ${last}` : last;
}

export function matchesPlayer(player: string, query: string): boolean {
  const q = normalizeName(query);
  if (!q) return true;
  const a = normalizeName(player);
  const b = normalizeName(displayName(player));
  return a.includes(q) || b.includes(q);
}

export function filterCases(cases: Case[], f: CaseFilter): Case[] {
  return cases.filter(
    (c) =>
      (f.contrast === 'all' || c.contrast === f.contrast) &&
      (f.selection === 'all' || c.selection === f.selection) &&
      (f.season === 'all' || c.outcome_season === f.season) &&
      (f.result === 'all' || (f.result === 'improved' ? c.improved : !c.improved)) &&
      matchesPlayer(c.player, f.query),
  );
}

export function summarizeCases(cases: Case[]): { n: number; improved: number; worsened: number } {
  const improved = cases.filter((c) => c.improved).length;
  return { n: cases.length, improved, worsened: cases.length - improved };
}

export function contrastsOf(cases: Case[]): string[] {
  const out: string[] = [];
  for (const c of cases) if (!out.includes(c.contrast)) out.push(c.contrast);
  return out;
}

export function seasonsOf(cases: Case[]): number[] {
  return [...new Set(cases.map((c) => c.outcome_season))].sort((a, b) => a - b);
}

export const SELECTION_SHORT: Record<CaseSelection, string> = {
  'largest increase': 'Largest increase',
  'largest decrease': 'Largest decrease',
  'random sample (seed 42)': 'Random (seed 42)',
};

export const SELECTION_LABELS: Record<CaseSelection, string> = {
  'largest increase': 'Largest forecast increases',
  'largest decrease': 'Largest forecast decreases',
  'random sample (seed 42)': 'Random sample (seed 42)',
};
