/**
 * Result sentences. Copy rule: describe what happened historically, never what a player "will" do,
 * and say "adds information" only when the verdict in the data says so.
 */
import type { Evaluation, FantasyResult, Target } from '../data/schemas';
import { fmtCI, fmtP, fmtPct } from './format';

/** Lower-case the first letter unless the first word is an acronym ("FIP forecast" stays as is). */
export function lowerFirst(s: string): string {
  const first = s.split(/[\s(]/)[0] ?? '';
  if (first.length > 1 && first === first.toUpperCase() && /[A-Z]/.test(first)) return s;
  return s.charAt(0).toLowerCase() + s.slice(1);
}

function upperFirst(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** "next-season baserunning run-value rate" from targets.json label "Next-season baserunning run-value rate". */
export function targetPhrase(t: Pick<Target, 'label'>): string {
  // Keep acronyms (wOBA, FIP, bWAR) intact; only lower-case the leading word.
  return lowerFirst(t.label);
}

export function evaluationSummary(row: Evaluation, metricName: string, target: Pick<Target, 'label'>): string {
  const tp = targetPhrase(target);
  const nImproved = Math.round(row.folds_improved_share * row.n_folds);
  const change = `RMSE changed by ${fmtPct(row.delta_pct)} on average across ${row.n_folds} out-of-time folds (95% CI ${fmtCI(row.ci_low_pct, row.ci_high_pct)})`;
  const folds = `${nImproved} of ${row.n_folds} folds improved`;
  switch (row.verdict) {
    case 'Projection':
      return `Historically, adding ${metricName} improved ${tp} forecasts beyond the history baseline: ${change}, and ${folds}.`;
    case 'Diagnostic': {
      const redundant = row.reason_code.includes('redundant')
        ? ' On its own it carried predictive signal, but another member of its metric family already captured that information.'
        : '';
      return `Adding ${metricName} did not pass the projection test for ${tp}: ${change}; ${folds}.${redundant} It is labelled Diagnostic because the metric catalog marks it as an interpretable process metric, a human-specified label rather than a statistical finding.`;
    }
    case 'Exclude':
      return `Adding ${metricName} did not pass the projection test for ${tp}: ${change}; ${folds}. "Exclude" means no conditional value for this target given this baseline, not that the metric is useless.`;
    case 'Context':
      return `${metricName} has the Context role for ${tp}, assigned by a human-specified rule (environment, demographic or playing-time variable) whatever its predictive value. For reference, ${change}.`;
    default:
      return `${metricName} for ${tp}: ${row.verdict}. ${change}; ${folds}.`;
  }
}

// ---------------------------------------------------------------- fantasy
export interface FantasyWordingContext {
  forecast: string; // e.g. "wOBA forecast", "PA-weighted 2-year xwOBA (raw metric)"
  outcome: string; // e.g. "home runs (HR)"
}

function samplePhrase(r: Pick<FantasyResult, 'sample'>): string {
  return r.sample.startsWith('2026') ? 'In 2026 (one exploratory season)' : 'Across 2021–2025 (pooled)';
}

function actionPhrase(r: Pick<FantasyResult, 'kind'>, ctx: FantasyWordingContext): string {
  const f = lowerFirst(ctx.forecast);
  switch (r.kind) {
    case 'target_forecast_added':
      return `adding the ${f} to the fantasy baseline`;
    case 'admitted_vs_history_target_forecast':
      return `using the admitted-metric ${f} instead of the history-only one`;
    case 'joint_target_forecasts':
      return `adding all admitted target forecasts together to the fantasy baseline`;
    case 'joint_admitted_vs_history':
      return `using all admitted-metric target forecasts instead of the history-only ones`;
    case 'direct_metric_added':
      return `adding ${f.replace(/ \(raw metric\)$/, '')} directly to the fantasy baseline`;
    default:
      return `the augmented model`;
  }
}

/** One-sentence account of a fantasy-bridge result that obeys the wording rule. */
export function fantasyResultSentence(r: FantasyResult, ctx: FantasyWordingContext): string {
  const head = `${samplePhrase(r)}, ${actionPhrase(r, ctx)} changed ${ctx.outcome} forecast error (RMSE) by ${fmtPct(r.delta_pct)} (95% CI ${fmtCI(r.ci_low_pct, r.ci_high_pct)}).`;
  const adj = r.adjustment ? `${r.adjustment}, adjusted p = ${fmtP(r.p_adjusted)}` : 'no multiplicity adjustment';
  switch (r.verdict) {
    case 'adds information':
      return `${head} The interval lies below zero and the gain survives the multiplicity adjustment (${adj}), so under the protocol's rule it adds information about ${ctx.outcome}.`;
    case 'gain not robust to multiplicity':
      return `${head} The interval lies below zero, but the gain does not survive the multiplicity adjustment (${adj}), so it is not counted as adding information.`;
    case 'no detectable gain':
      return `${head} The interval includes zero: no detectable gain.`;
    case 'harmful':
      return `${head} The interval lies entirely above zero: forecasts of ${ctx.outcome} became less accurate (harmful).`;
    case 'directional gain (exploratory; CI excludes 0)':
      return `${head} The interval excludes zero, but this is a single, already-inspected season with no multiplicity adjustment, so read it as directional only.`;
    default:
      return head;
  }
}

/** How the 2026 row relates to the pooled 2021–2025 row. */
export function compare2026(pooled: FantasyResult | undefined, r2026: FantasyResult | undefined): string | null {
  if (!r2026) return null;
  const includesZero = r2026.ci_low_pct <= 0 && r2026.ci_high_pct >= 0;
  if (!pooled) {
    return includesZero
      ? 'This 2026 interval included zero.'
      : 'This 2026 interval excluded zero; with one season and no adjustment it is directional only.';
  }
  const sameSign = Math.sign(pooled.delta_pct) === Math.sign(r2026.delta_pct) && r2026.delta_pct !== 0;
  if (includesZero) {
    return sameSign
      ? 'This 2026 effect was directionally consistent with 2021–2025, but its interval included zero.'
      : 'This 2026 estimate went the other way from 2021–2025, and its interval included zero.';
  }
  return sameSign
    ? 'This 2026 effect was directionally consistent with 2021–2025 and its interval excluded zero; one exploratory season, so directional only.'
    : 'This 2026 estimate went the other way from 2021–2025 and its interval excluded zero; one exploratory season, so directional only.';
}

/** Model-comparison sentence for a row "A vs B". */
export function comparisonSentence(
  deltaPct: number,
  lo: number | null,
  hi: number | null,
  aName: string,
  bName: string,
): string {
  if (lo === null || hi === null) {
    return upperFirst(`${aName} and ${bName} produced identical forecasts here (same feature set), so the difference is exactly zero.`);
  }
  if (hi < 0) return upperFirst(`${aName} was more accurate than ${bName} (${fmtPct(deltaPct)}, 95% CI ${fmtCI(lo, hi)}).`);
  if (lo > 0) return upperFirst(`${aName} was less accurate than ${bName} (${fmtPct(deltaPct)}, 95% CI ${fmtCI(lo, hi)}).`);
  return `No clear difference between ${aName} and ${bName}: ${fmtPct(deltaPct)}, and the 95% CI ${fmtCI(lo, hi)} includes zero.`;
}
