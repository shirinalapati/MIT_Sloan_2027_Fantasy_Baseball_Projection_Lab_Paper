/**
 * Illustrative fantasy scoring arithmetic.
 *
 * Ratio categories are always aggregated from components:
 *   AVG  = total H / total AB
 *   ERA  = 9 × total ER / total IP
 *   WHIP = total (BB + H) / total IP
 * Player rates are never averaged (that would weight a 100-AB hitter like a 600-AB hitter).
 */

export type StatLine = Record<string, number>;

export interface PlayerLine {
  id: string;
  name: string;
  stats: StatLine;
}

function val(line: StatLine, key: string): number {
  const v = line[key];
  return typeof v === 'number' && Number.isFinite(v) ? v : 0;
}

export function sumStat(players: PlayerLine[], key: string): number {
  return players.reduce((s, p) => s + val(p.stats, key), 0);
}

/** Ratio from summed components; null when the denominator total is zero. */
export function ratioFromTotals(numerator: number, denominator: number, scale = 1): number | null {
  if (!(denominator > 0)) return null;
  return (scale * numerator) / denominator;
}

export function teamAvg(hitters: PlayerLine[]): number | null {
  return ratioFromTotals(sumStat(hitters, 'H'), sumStat(hitters, 'AB'));
}

export function teamEra(pitchers: PlayerLine[]): number | null {
  return ratioFromTotals(sumStat(pitchers, 'ER'), sumStat(pitchers, 'IP'), 9);
}

export function teamWhip(pitchers: PlayerLine[]): number | null {
  return ratioFromTotals(sumStat(pitchers, 'BBH'), sumStat(pitchers, 'IP'));
}

export interface HitterTotals {
  R: number;
  HR: number;
  RBI: number;
  SB: number;
  AB: number;
  H: number;
  AVG: number | null;
}
export interface PitcherTotals {
  W: number;
  SV: number;
  K: number;
  IP: number;
  ER: number;
  BBH: number;
  ERA: number | null;
  WHIP: number | null;
}

export function hitterTotals(hitters: PlayerLine[]): HitterTotals {
  return {
    R: sumStat(hitters, 'R'),
    HR: sumStat(hitters, 'HR'),
    RBI: sumStat(hitters, 'RBI'),
    SB: sumStat(hitters, 'SB'),
    AB: sumStat(hitters, 'AB'),
    H: sumStat(hitters, 'H'),
    AVG: teamAvg(hitters),
  };
}

export function pitcherTotals(pitchers: PlayerLine[]): PitcherTotals {
  return {
    W: sumStat(pitchers, 'W'),
    SV: sumStat(pitchers, 'SV'),
    K: sumStat(pitchers, 'K'),
    IP: sumStat(pitchers, 'IP'),
    ER: sumStat(pitchers, 'ER'),
    BBH: sumStat(pitchers, 'BBH'),
    ERA: teamEra(pitchers),
    WHIP: teamWhip(pitchers),
  };
}

/** A player's own rate (for display only; never averaged into team rates). */
export function playerRate(line: StatLine, num: string, den: string, scale = 1): number | null {
  return ratioFromTotals(val(line, num), val(line, den), scale);
}

/**
 * Change in a team ratio caused by including one player: ratio(all) − ratio(all except player).
 * For AVG a positive value raises team AVG; for ERA/WHIP a negative value lowers (improves) them.
 */
export function ratioImpact(
  players: PlayerLine[],
  playerId: string,
  ratio: (ps: PlayerLine[]) => number | null,
): number | null {
  const all = ratio(players);
  const without = ratio(players.filter((p) => p.id !== playerId));
  if (all === null || without === null) return null;
  return all - without;
}

/** The incorrect shortcut, used only to show readers why it is wrong. Ignores players with no denominator. */
export function naiveMeanOfRates(players: PlayerLine[], num: string, den: string, scale = 1): number | null {
  const rates = players
    .map((p) => playerRate(p.stats, num, den, scale))
    .filter((r): r is number => r !== null);
  if (!rates.length) return null;
  return rates.reduce((s, r) => s + r, 0) / rates.length;
}

// ---------------------------------------------------------------- points
export type Weights = Record<string, number>;

/** Points for one stat line: Σ weight × stat. Stats without a weight score nothing; missing stats count as 0. */
export function pointsFor(line: StatLine, weights: Weights): number {
  let total = 0;
  for (const [stat, w] of Object.entries(weights)) {
    if (!Number.isFinite(w)) continue;
    total += w * val(line, stat);
  }
  return total;
}

export function teamPoints(players: PlayerLine[], weights: Weights): number {
  return players.reduce((s, p) => s + pointsFor(p.stats, weights), 0);
}

/** Innings from outs (IP = outs / 3), the convention used in the study. */
export function inningsFromOuts(outs: number): number {
  return outs / 3;
}

/** Outs from decimal innings (180.33 IP -> 541 outs). */
export function outsFromInnings(ip: number): number {
  return Math.round(ip * 3);
}

/** Pitcher stat line with OUTS derived from IP (points systems often score outs rather than innings). */
export function withDerivedOuts(line: StatLine): StatLine {
  return { ...line, OUTS: outsFromInnings(val(line, 'IP')) };
}

/** Parse a user-entered number; blank or invalid input becomes 0 and negative input is clamped to 0. */
export function parseStatInput(raw: string): number {
  const t = raw.trim();
  if (t === '') return 0;
  const v = Number(t);
  if (!Number.isFinite(v) || v < 0) return 0;
  return v;
}
