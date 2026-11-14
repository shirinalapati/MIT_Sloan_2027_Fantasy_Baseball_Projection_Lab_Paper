/** Human-readable labels and plain-language definitions. Text only; every number comes from the JSON files. */
import type { Comparison, Evaluation, EvaluationVerdict, FantasyKind, FantasyVerdict, Metric } from '../data/schemas';
import { FANTASY_TARGET_ALIASES } from '../data/constants';

// ---------------------------------------------------------------- evaluation verdicts
export type VerdictKey = EvaluationVerdict | 'Not evaluated';
export const NOT_EVALUATED = 'Not evaluated' as const;

export const VERDICT_DESCRIPTIONS: Record<VerdictKey, string> = {
  Projection:
    'Passed the statistical projection test: material, consistent out-of-time lift; not redundant; stable sign; acceptable coverage.',
  Diagnostic:
    'Failed the projection test. Labelled Diagnostic (not Exclude) because the metric catalog marks it as an interpretable process metric, a human-specified label.',
  Exclude:
    'Failed the projection test and is not flagged as a process metric. It means "no conditional value for this target given this baseline", not "useless".',
  Context:
    'Assigned from a human-specified role (park/environment, age, playing time), whatever its predictive value.',
  'Augmented Projection':
    'Defined in the rules; never assigned in the 208 canonical evaluations. It appears in a few nested windows.',
  'Insufficient Evidence':
    'Defined in the rules; never assigned in the 208 canonical evaluations. It appears in a few nested windows.',
  'Not evaluated': 'This metric–target pair was never evaluated, so no verdict exists.',
};

export type BasisKind = 'statistical' | 'statistical+human' | 'human';

/** Classify the `verdict_basis` text: is the verdict a statistical finding or a human-specified label? */
export function verdictBasisKind(row: Pick<Evaluation, 'verdict' | 'verdict_basis'>): BasisKind {
  const b = row.verdict_basis.toLowerCase();
  if (b.startsWith('human-specified role')) return 'human';
  if (b.includes('human-specified')) return 'statistical+human';
  if (b.includes('statistical') || b.includes('failed the projection test')) return 'statistical';
  if (row.verdict === 'Context') return 'human';
  if (row.verdict === 'Diagnostic') return 'statistical+human';
  return 'statistical';
}

export const BASIS_LABELS: Record<BasisKind, string> = {
  statistical: 'Statistical finding',
  'statistical+human': 'Statistical test failed; label is human-specified',
  human: 'Human-specified role, not a statistical finding',
};

// ---------------------------------------------------------------- subgroups
const SUBGROUP_LABELS: Record<string, string> = {
  age_young: 'Age group: young',
  age_prime: 'Age group: prime',
  age_old: 'Age group: older',
  lhb: 'Left-handed batters',
  rhb: 'Right-handed batters',
  pa_low: 'Lower plate appearances',
  pa_high: 'Higher plate appearances',
  pos_C: 'Catchers',
  pos_DH: 'Designated hitters',
  pos_IF: 'Infielders',
  pos_OF: 'Outfielders',
  starter: 'Starters',
  reliever: 'Relievers',
  lhp: 'Left-handed pitchers',
  rhp: 'Right-handed pitchers',
  ip_low: 'Lower innings pitched',
  ip_high: 'Higher innings pitched',
};
export function subgroupLabel(name: string): string {
  return SUBGROUP_LABELS[name] ?? name;
}

// ---------------------------------------------------------------- metrics
export function metricLabel(id: string, metrics?: Map<string, Metric> | null): string {
  return metrics?.get(id)?.description ?? id;
}

/** Short names for the metrics used in headline contrasts; everything else falls back to the catalog description. */
const METRIC_SHORT: Record<string, string> = {
  sprint_speed: 'Sprint speed',
  ev: 'Exit velocity',
  xwoba_w2: 'xwOBA (2-yr)',
  stuff_plus: 'Stuff+',
  k_pct: 'Strikeout rate',
  k_bb_pct: 'K-BB%',
  barrel_pct: 'Barrel rate',
};
export function metricShort(id: string, metrics?: Map<string, Metric> | null): string {
  return METRIC_SHORT[id] ?? metricLabel(id, metrics);
}

// ---------------------------------------------------------------- fantasy
export const FANTASY_OUTCOME_LABELS: Record<string, { long: string; short: string }> = {
  R: { long: 'Runs (R)', short: 'R' },
  HR: { long: 'Home runs (HR)', short: 'HR' },
  RBI: { long: 'Runs batted in (RBI)', short: 'RBI' },
  SB: { long: 'Stolen bases (SB)', short: 'SB' },
  AVG: { long: 'Batting average (AVG)', short: 'AVG' },
  AB: { long: 'At-bats (AB)', short: 'AB' },
  H: { long: 'Hits (H)', short: 'H' },
  VAL_H: { long: 'Hitter roto value (5×5 z-score)', short: 'Roto value' },
  PTS_H: { long: 'Hitter points', short: 'Points' },
  W: { long: 'Wins (W)', short: 'W' },
  SV: { long: 'Saves (SV)', short: 'SV' },
  K: { long: 'Strikeouts (K)', short: 'K' },
  ERA: { long: 'Earned run average (ERA)', short: 'ERA' },
  WHIP: { long: 'Walks + hits per inning (WHIP)', short: 'WHIP' },
  IP: { long: 'Innings pitched (IP)', short: 'IP' },
  VAL_P: { long: 'Pitcher roto value (5×5 z-score)', short: 'Roto value' },
  PTS_P: { long: 'Pitcher points', short: 'Points' },
};
export function outcomeLabel(id: string, form: 'long' | 'short' = 'long'): string {
  return FANTASY_OUTCOME_LABELS[id]?.[form] ?? id;
}

/** How each fantasy outcome is defined and who is evaluated (experiment protocol §4). */
export function outcomeDefinition(id: string): string {
  switch (id) {
    case 'R':
    case 'HR':
    case 'RBI':
    case 'SB':
    case 'H':
      return 'Season-T total. All pool hitters, equal weight; a pool player with no season-T record counts as 0.';
    case 'AB':
      return 'Season-T at-bats (a playing-time outcome). All pool hitters; non-returners count as 0.';
    case 'AVG':
      return 'H / AB in season T. Pool hitters with at least 100 AB in T, weighted by AB, so results are conditional on playing (floor from the experiment protocol, §4).';
    case 'W':
    case 'SV':
    case 'K':
      return 'Season-T total. All pool pitchers, equal weight; non-returners count as 0.';
    case 'IP':
      return 'Season-T innings (a playing-time outcome, computed from outs). All pool pitchers; non-returners count as 0.';
    case 'ERA':
      return '9·ER / IP in season T. Pool pitchers with at least 20 IP in T, weighted by IP, so results are conditional on playing (floor from the experiment protocol, §4).';
    case 'WHIP':
      return '(BB + H) / IP in season T. Pool pitchers with at least 20 IP in T, weighted by IP, so results are conditional on playing (floor from the experiment protocol, §4).';
    case 'VAL_H':
    case 'VAL_P':
      return 'Sum of the five 5×5 category z-scores from realized season-T totals; reference means and SDs come from earlier seasons only; no positional adjustment.';
    case 'PTS_H':
    case 'PTS_P':
      return 'Season-T fantasy points under the verified Yahoo default head-to-head points weights (shown in the Value Lab). All pool players; non-returners count as 0.';
    default:
      return 'Season-T fantasy outcome.';
  }
}

const FORECAST_LABELS: Record<string, string> = {
  woba: 'wOBA forecast',
  br: 'Baserunning forecast',
  fld: 'Fielding forecast',
  hwar: 'Hitter bWAR forecast',
  fip: 'FIP forecast',
  pwar: 'Pitcher bWAR forecast',
};

/** Label for the `target` field of a fantasy row: a forecast alias, a joint set, or a raw metric id. */
export function fantasyTargetLabel(target: string, metrics?: Map<string, Metric> | null): string {
  if (FORECAST_LABELS[target]) return FORECAST_LABELS[target];
  if (target.includes('+')) {
    const parts = target.split('+').map((p) => (FORECAST_LABELS[p] ?? p).replace(/ forecast$/, ''));
    return `${parts.join(' + ')} forecasts (joint)`;
  }
  const m = metrics?.get(target);
  return m ? `${m.description} (raw metric)` : `${target} (raw metric)`;
}

export function fantasyTargetShort(target: string): string {
  const short: Record<string, string> = {
    woba: 'wOBA',
    br: 'Baserunning',
    fld: 'Fielding',
    hwar: 'Hitter bWAR',
    fip: 'FIP',
    pwar: 'Pitcher bWAR',
    'woba+br+hwar': 'Joint (wOBA+BR+bWAR)',
    'fip+pwar': 'Joint (FIP+bWAR)',
  };
  return short[target] ?? target;
}

/** targets.json id behind a fantasy forecast alias (undefined for joint sets and raw metrics). */
export function fantasyTargetId(target: string): string | undefined {
  return FANTASY_TARGET_ALIASES[target];
}

/** Plain-language label for a fantasy model id such as "BF", "BF@fld", "BF+woba_B0", "BF+joint". */
export function fantasyModelLabel(id: string, metrics?: Map<string, Metric> | null): string {
  if (id === 'BF') return 'Fantasy baseline (BF)';
  if (id === 'BF@fld') return 'Fantasy baseline (BF), fielding-forecast subset';
  const m = /^BF\+(.+?)(_B0)?$/.exec(id);
  if (!m) return id;
  const [, what, b0] = m;
  if (what === 'joint') return b0 ? 'BF + all history-only target forecasts' : 'BF + all admitted target forecasts';
  if (FORECAST_LABELS[what]) {
    const f = FORECAST_LABELS[what];
    return b0 ? `BF + history-only ${f}` : `BF + admitted ${f}`;
  }
  const metric = metrics?.get(what);
  return `BF + raw ${metric ? metric.description : what}`;
}

export const FANTASY_KIND_INFO: Record<FantasyKind, { label: string; question: string; base: string; aug: string }> = {
  target_forecast_added: {
    label: 'Target forecast added',
    question: 'Does one target forecast add information beyond the fantasy baseline?',
    base: 'BF',
    aug: 'BF + admitted target forecast',
  },
  admitted_vs_history_target_forecast: {
    label: 'Admitted vs history-only forecast',
    question:
      "Does the forecast built with admitted metrics carry more fantasy information than the forecast built from the target's own history?",
    base: 'BF + history-only forecast',
    aug: 'BF + admitted forecast',
  },
  joint_target_forecasts: {
    label: 'All target forecasts jointly',
    question: 'Do all available target forecasts together add information beyond the fantasy baseline?',
    base: 'BF',
    aug: 'BF + all admitted forecasts',
  },
  joint_admitted_vs_history: {
    label: 'Joint: admitted vs history-only',
    question: 'Together, do admitted-metric forecasts beat history-only forecasts for fantasy outcomes?',
    base: 'BF + all history-only forecasts',
    aug: 'BF + all admitted forecasts',
  },
  direct_metric_added: {
    label: 'Raw metric added directly',
    question: 'Does the raw season-t metric add information beyond the fantasy baseline, with no target model in between?',
    base: 'BF',
    aug: 'BF + raw metric',
  },
};

export const FANTASY_VERDICT_INFO: Record<FantasyVerdict, { label: string; tone: 'gain' | 'partial' | 'null' | 'harm' | 'directional' }> = {
  'adds information': { label: 'Adds information', tone: 'gain' },
  'gain not robust to multiplicity': { label: 'Gain not robust to multiplicity', tone: 'partial' },
  'no detectable gain': { label: 'No detectable gain', tone: 'null' },
  harmful: { label: 'Harmful', tone: 'harm' },
  'directional gain (exploratory; CI excludes 0)': { label: 'Directional gain (exploratory)', tone: 'directional' },
};

export function familyLabel(family: string): string {
  if (family === 'primary') return 'Primary pre-specified linkage (Holm-adjusted family of 8)';
  const map: Record<string, string> = {
    secondary_single: 'Secondary: single-forecast matrix (BH within family)',
    secondary_b0_vs_adm: 'Secondary: admitted vs history-only (BH within family)',
    secondary_joint: 'Secondary: joint forecasts (BH within family)',
    secondary_direct: 'Secondary: raw-metric tests (BH within family)',
  };
  return map[family] ?? `Secondary (${family})`;
}

// ---------------------------------------------------------------- model comparison
export const MODEL_SET_INFO: Record<string, { name: string; definition: string }> = {
  B0: {
    name: 'History baseline (B0)',
    definition:
      "The target's history-aware ridge baseline: the target's own recent history plus age, playing time and park, as listed for each target.",
  },
  ADM: {
    name: 'Nested-admitted set (ADM)',
    definition:
      'The baseline plus the metrics admitted by the study rules, re-selected for each outer year using only earlier seasons (nested), so no future information chooses the features.',
  },
  KS: {
    name: 'Kitchen sink (KS)',
    definition: 'The baseline plus every candidate metric, with no admission step.',
  },
  FIX: {
    name: 'Original August set (FIX)',
    definition:
      'The feature set fixed in the original analysis. It was chosen with data that overlap the evaluation years (look-ahead), so its scores are optimistic. Shown as a reference only.',
  },
  UNI: {
    name: 'Lift-only screen (UNI)',
    definition: 'A simpler screen that keeps metrics on incremental out-of-time lift alone.',
  },
  FAM: {
    name: 'Best-per-family screen (FAM)',
    definition: 'A simpler screen that keeps the best metric from each metric family.',
  },
  CORR: {
    name: 'Correlation-filtered kitchen sink (CORR)',
    definition: 'The kitchen sink after a correlation filter removes near-duplicate metrics.',
  },
};

export const ESTIMATOR_INFO: Record<string, { name: string; definition: string }> = {
  ridge: { name: 'ridge', definition: "Ridge regression with the study's fixed penalty (α = 1, per the experiment protocol); the default estimator." },
  ridge_tuned: { name: 'tuned ridge', definition: 'Ridge regression with the penalty tuned on inner chronological folds.' },
  enet: { name: 'elastic net', definition: 'Tuned elastic net (combined L1 and L2 penalties), which can drop features itself.' },
  lgbm: { name: 'LightGBM', definition: 'Gradient-boosted decision trees (LightGBM).' },
  rf: { name: 'random forest', definition: 'A random forest of decision trees.' },
};

/** "KS|enet" -> "Kitchen sink · elastic net"; "B0+stuff_plus|ridge" -> "History baseline + stuff_plus · ridge". */
export function modelLabel(id: string, metrics?: Map<string, Metric> | null): string {
  const [set, est] = id.split('|');
  const estName = ESTIMATOR_INFO[est]?.name ?? est;
  if (set.startsWith('B0+')) {
    const m = set.slice(3);
    return `History baseline + ${metricLabel(m, metrics)} · ${estName}`;
  }
  const setName = MODEL_SET_INFO[set]?.name.replace(/ \([A-Z0-9]+\)$/, '') ?? set;
  return `${setName} · ${estName}`;
}

export type ComparisonGroup = 'admission' | 'kitchen' | 'lookahead' | 'screens' | 'estimators' | 'single';

export const COMPARISON_GROUP_INFO: Record<ComparisonGroup, { title: string; note: string }> = {
  admission: {
    title: 'Selected (ADM) vs history baseline (B0)',
    note: 'Does nested feature admission improve on the history baseline? Repeated with each estimator.',
  },
  kitchen: {
    title: 'Kitchen sink (KS) vs selected or baseline',
    note: 'Does using every candidate metric beat selecting them? Positive values favour the selected set.',
  },
  lookahead: {
    title: 'Look-ahead reference (FIX)',
    note: 'The original August set saw the evaluation years; read these as an optimistic reference, not a fair competitor.',
  },
  screens: {
    title: 'Simpler selection screens vs ADM',
    note: 'Lift-only, best-per-family and correlation-filtered alternatives to the admission rules.',
  },
  estimators: {
    title: 'Estimator checks on the admitted set',
    note: 'Same admitted features, different estimator, compared with ridge.',
  },
  single: {
    title: 'Single-metric flagship contrasts',
    note: 'History baseline plus one metric vs the history baseline.',
  },
};

export function comparisonGroup(c: Pick<Comparison, 'model_a' | 'model_b'>): ComparisonGroup {
  const [aSet, aEst] = c.model_a.split('|');
  const [bSet, bEst] = c.model_b.split('|');
  if (aSet.startsWith('B0+')) return 'single';
  if (aSet === 'FIX' || bSet === 'FIX') return aSet === 'KS' ? 'kitchen' : 'lookahead';
  if (aSet === 'KS') return 'kitchen';
  if (aSet === 'UNI' || aSet === 'FAM' || aSet === 'CORR') return 'screens';
  if (aSet === 'ADM' && bSet === 'ADM' && aEst !== bEst) return 'estimators';
  return 'admission';
}

/** Short tier label for a comparison sample. */
export function comparisonSampleLabel(sample: string): string {
  return sample.startsWith('2026') ? '2026 check (directional / exploratory)' : 'Nested outer years 2021–2025';
}
