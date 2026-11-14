/**
 * Audited, pinned exceptions to the "CI must bracket its point estimate" rule.
 *
 * In evaluations.json, `delta_pct` is the MEAN OF THE FOLD DELTAS (it equals the average of
 * `fold_deltas_pct` for all 208 rows), while `ci_low_pct`/`ci_high_pct` come from the 95% paired
 * player-cluster bootstrap. They are different summaries. For the 7 rows below the fold mean
 * falls outside the bootstrap interval in the published research table
 * (sloan2027/tables/table7_reason_codes_208.csv). The app shows them exactly as published,
 * with a visible note on the result card.
 *
 * Each exception is pinned to its exact published values: if any of these numbers changes, or
 * any other row fails to bracket, the validator fails the build.
 */
export interface PinnedCiException {
  target: string;
  metric: string;
  delta_pct: number;
  ci_low_pct: number;
  ci_high_pct: number;
}

export const EVALUATION_CI_EXCEPTIONS: readonly PinnedCiException[] = [
  { target: 'pitching_fip', metric: 'k_bb_pct', delta_pct: -3.159681, ci_low_pct: -3.156525, ci_high_pct: -0.617309 },
  { target: 'pitching_fip', metric: 'k_bb_pct_w2', delta_pct: -3.48725, ci_low_pct: -3.380693, ci_high_pct: -1.022564 },
  { target: 'pitching_fip', metric: 'k_pct', delta_pct: -3.235095, ci_low_pct: -3.202878, ci_high_pct: -0.846124 },
  { target: 'pitching_fip', metric: 'ip', delta_pct: 0.251484, ci_low_pct: -0.094577, ci_high_pct: 0.210202 },
  { target: 'pitching_fip', metric: 'gs_share', delta_pct: 0.558083, ci_low_pct: 0.017839, ci_high_pct: 0.468682 },
  { target: 'pitching_fip', metric: 'lg_fip', delta_pct: -0.369391, ci_low_pct: -0.124211, ci_high_pct: 0.542622 },
  { target: 'pitcher_war', metric: 'starter_role', delta_pct: 0.212231, ci_low_pct: -0.053415, ci_high_pct: 0.208528 },
];

const EPS = 1e-9;

export function isPinnedCiException(row: PinnedCiException): boolean {
  return EVALUATION_CI_EXCEPTIONS.some(
    (e) =>
      e.target === row.target &&
      e.metric === row.metric &&
      Math.abs(e.delta_pct - row.delta_pct) < EPS &&
      Math.abs(e.ci_low_pct - row.ci_low_pct) < EPS &&
      Math.abs(e.ci_high_pct - row.ci_high_pct) < EPS,
  );
}
