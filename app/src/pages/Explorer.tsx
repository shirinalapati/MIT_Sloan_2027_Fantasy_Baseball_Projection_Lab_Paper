import { useMemo } from 'react';
import { useData } from '../data/load';
import type { Evaluation, Meta, Metric, Target } from '../data/schemas';
import { NESTED_YEARS, SOURCE_FILES, nestedSourceFile } from '../data/constants';
import { setParams, useRoute } from '../router';
import { Callout, Gate, PageHead, Tile } from '../components/Page';
import { Combobox, type ComboOption } from '../components/Combobox';
import { Segmented } from '../components/Segmented';
import { VerdictBadge } from '../components/Badges';
import { VerdictIcon } from '../components/Icons';
import { ResultMeta } from '../components/ResultMeta';
import { ForestPlot, type ForestRow } from '../components/charts/ForestPlot';
import {
  buildEvaluationIndex,
  estimateOutsideCi,
  evaluationsForMetric,
  lookupEvaluation,
  metricIndex,
} from '../lib/lookup';
import { BASIS_LABELS, VERDICT_DESCRIPTIONS, metricLabel, subgroupLabel, verdictBasisKind, type VerdictKey } from '../lib/labels';
import { evaluationSummary, targetPhrase } from '../lib/wording';
import { digitsFor, fmt, fmtCI, fmtInt, fmtPct, fmtShare, fmtUnits } from '../lib/format';

const DEFAULT_METRIC = 'sprint_speed';
const DEFAULT_TARGET = 'baserunning_rv';

const QUICK_PICKS: Array<{ metric: string; target: string; label: string }> = [
  { metric: 'sprint_speed', target: 'baserunning_rv', label: 'Sprint speed → baserunning' },
  { metric: 'sprint_speed', target: 'hitting_woba', label: 'Sprint speed → wOBA' },
  { metric: 'xwoba_w2', target: 'hitting_woba', label: 'xwOBA (2-yr) → wOBA' },
  { metric: 'ev', target: 'overall_war', label: 'Exit velocity → hitter bWAR' },
  { metric: 'stuff_plus', target: 'pitching_fip', label: 'Stuff+ → FIP' },
  { metric: 'k_pct', target: 'pitching_fip', label: 'Strikeout rate → FIP' },
];

const VERDICT_FILTERS = ['all', 'Projection', 'Diagnostic', 'Exclude', 'Context'] as const;
type VerdictFilter = (typeof VERDICT_FILTERS)[number];

export default function Explorer() {
  const state = useData('meta', 'targets', 'metrics', 'evaluations');
  return (
    <>
      <PageHead eyebrow="Primary tool" title="Metric → Target Explorer">
        <p className="lede">
          Pick a metric and one of the six targets. You will see whether adding that metric to the target&apos;s history baseline made
          out-of-time forecasts more accurate, which role the study assigned, and on what basis.
        </p>
      </PageHead>
      <Gate state={state} what="metric evaluations">
        {(d) => <ExplorerBody {...d} />}
      </Gate>
    </>
  );
}

function ExplorerBody({ meta, targets, metrics, evaluations }: { meta: Meta; targets: Target[]; metrics: Metric[]; evaluations: Evaluation[] }) {
  const route = useRoute();
  const mIdx = useMemo(() => metricIndex(metrics), [metrics]);
  const eIdx = useMemo(() => buildEvaluationIndex(evaluations), [evaluations]);
  const metricParam = route.params.get('metric');
  const targetParam = route.params.get('target');
  const metricId = metricParam && mIdx.has(metricParam) ? metricParam : DEFAULT_METRIC;
  const target = targets.find((t) => t.id === targetParam) ?? targets.find((t) => t.id === DEFAULT_TARGET) ?? targets[0];
  const verdictFilter = (VERDICT_FILTERS as readonly string[]).includes(route.params.get('verdict') ?? '')
    ? (route.params.get('verdict') as VerdictFilter)
    : 'all';
  const metric = mIdx.get(metricId);
  const lookup = lookupEvaluation(eIdx, metricId, target.id);
  const targetOrder = targets.map((t) => t.id);
  const evaluatedFor = evaluationsForMetric(evaluations, metricId, targetOrder);

  const options: ComboOption[] = useMemo(() => {
    const byMetric = new Map<string, string[]>();
    for (const e of evaluations) byMetric.set(e.metric, [...(byMetric.get(e.metric) ?? []), e.target]);
    return [...metrics]
      .sort((a, b) => a.description.localeCompare(b.description))
      .map((m) => {
        const ts = (byMetric.get(m.id) ?? []).map((t) => targets.find((x) => x.id === t)?.short ?? t);
        return {
          value: m.id,
          label: m.description,
          sub: `${m.id} · ${m.family.replace(/_/g, ' ')} · evaluated for ${ts.join(', ') || 'no target'}`,
          keywords: `${m.family} ${m.player_types.join(' ')}`,
        };
      });
  }, [metrics, evaluations, targets]);

  const pick = (metric: string, target: string) => setParams({ metric, target });

  return (
    <>
      <div className="card" role="search" aria-label="Choose a metric and a target">
        <div className="controls" style={{ marginBottom: 12 }}>
          <Combobox
            label={`Metric (${metrics.length} in the catalog)`}
            options={options}
            value={metricId}
            onChange={(v) => setParams({ metric: v })}
            placeholder="Search, e.g. sprint, xwOBA, Stuff+"
            hint="Type to filter; use ↑ ↓ and Enter."
          />
          <Segmented
            legend="Target (next season)"
            value={target.id}
            onChange={(v) => setParams({ target: v })}
            options={targets.map((t) => ({ value: t.id, label: t.short, title: t.label }))}
          />
        </div>
        <div className="chip-row" aria-label="Headline examples">
          <span className="muted small">Headline examples:</span>
          {QUICK_PICKS.map((q) => (
            <button
              key={q.label}
              type="button"
              className="btn small"
              aria-pressed={q.metric === metricId && q.target === target.id}
              onClick={() => pick(q.metric, q.target)}
            >
              {q.label}
            </button>
          ))}
        </div>
      </div>

      <section className="section" aria-labelledby="result-title" style={{ marginTop: 20 }}>
        {lookup.status === 'evaluated' ? (
          <EvaluatedCard row={lookup.row} metric={metric} target={target} meta={meta} metricsIdx={mIdx} />
        ) : (
          <NotEvaluatedCard metric={metric} metricId={metricId} target={target} evaluatedFor={evaluatedFor} targets={targets} onPick={pick} meta={meta} />
        )}
      </section>

      <section className="section" aria-labelledby="across-title">
        <h2 id="across-title">Same metric, different targets</h2>
        <p className="section-intro">
          The study&apos;s central point: a metric&apos;s value depends on the job. Every target is listed; pairs that were never evaluated say so.
          Select a row to open it above.
        </p>
        <div className="card">
          <AcrossTargets metricId={metricId} metric={metric} targets={targets} eIdx={eIdx} selected={target.id} />
        </div>
      </section>

      <section className="section" aria-labelledby="all-title">
        <h2 id="all-title">All candidates evaluated for {targetPhrase(target)}</h2>
        <p className="section-intro">
          {target.n_candidates} candidate metrics, sorted from the largest average improvement to the largest average worsening.
        </p>
        <CandidateTable
          target={target}
          evaluations={evaluations}
          metricsIdx={mIdx}
          selectedMetric={metricId}
          verdictFilter={verdictFilter}
          onFilter={(v) => setParams({ verdict: v === 'all' ? null : v })}
          onPick={(m) => {
            setParams({ metric: m });
            document.getElementById('result-title')?.scrollIntoView?.({ block: 'start' });
          }}
        />
      </section>
    </>
  );
}

// ------------------------------------------------------------------------- evaluated pair
function EvaluatedCard({
  row,
  metric,
  target,
  meta,
  metricsIdx,
}: {
  row: Evaluation;
  metric: Metric | undefined;
  target: Target;
  meta: Meta;
  metricsIdx: Map<string, Metric>;
}) {
  const name = metric?.description ?? row.metric;
  const basis = verdictBasisKind(row);
  const nImproved = Math.round(row.folds_improved_share * row.n_folds);
  const outside = estimateOutsideCi(row);
  const allZero = row.fold_deltas_pct.every((f) => f.delta_pct === 0);
  const unitDigits = digitsFor([row.delta_rmse, row.baseline_rmse]);
  const nestedProjection = row.nested_projection_count_2021_2025;

  const foldRows: ForestRow[] = [
    ...row.fold_deltas_pct.map((f) => ({
      key: String(f.year),
      label: String(f.year),
      labelText: `Fold with outcome season ${f.year}`,
      est: f.delta_pct,
      lo: null,
      hi: null,
      tone: 'ink' as const,
      valueText: fmtPct(f.delta_pct),
      group: 'Per fold, by outcome season (point estimates)',
    })),
    {
      key: 'mean',
      label: `Mean of ${row.n_folds} folds`,
      labelText: `Mean of ${row.n_folds} folds with 95% bootstrap CI`,
      sub: '95% player-cluster bootstrap CI',
      est: row.delta_pct,
      lo: row.ci_low_pct,
      hi: row.ci_high_pct,
      valueText: fmtPct(row.delta_pct),
      valueSub: fmtCI(row.ci_low_pct, row.ci_high_pct),
      group: 'Summary',
    },
  ];

  const subgroupRows: ForestRow[] = row.subgroups.map((s) => ({
    key: s.name,
    label: subgroupLabel(s.name),
    labelText: `${subgroupLabel(s.name)} (n = ${s.n})`,
    sub: `n = ${fmtInt(s.n)} player-seasons`,
    est: s.delta_pct,
    lo: null,
    hi: null,
    tone: 'ink' as const,
    valueText: fmtPct(s.delta_pct),
    tableExtra: { n: fmtInt(s.n) },
  }));

  return (
    <article className="card" aria-labelledby="result-title">
      <div className="card-head">
        <h2 id="result-title" className="card-title">
          {name} <span className="muted">→</span> {target.label}
        </h2>
        <VerdictBadge verdict={row.verdict} />
      </div>
      <p style={{ maxWidth: '85ch' }}>{evaluationSummary(row, name, target)}</p>

      {outside ? (
        <Callout kind="note" title="Why the estimate sits outside its interval">
          <p>
            The point estimate here is the mean of the {row.n_folds} fold deltas ({fmtPct(row.delta_pct)}), while the 95% interval{' '}
            {fmtCI(row.ci_low_pct, row.ci_high_pct)} comes from the player-cluster bootstrap. They are different summaries, and for this pair the
            fold mean falls outside the bootstrap interval. Both values are shown exactly as published in the research table.
          </p>
        </Callout>
      ) : null}
      {allZero ? (
        <Callout kind="note" title="All fold deltas are zero at reported precision">
          <p>
            Every fold delta rounds to 0.000%, so the share of folds counted as improved ({fmtShare(row.folds_improved_share)}) reflects
            differences below display precision. The verdict for this pair is a human-specified role, not a statistical finding.
          </p>
        </Callout>
      ) : null}

      <div className="tile-row">
        <Tile label={`ΔRMSE, mean of ${row.n_folds} folds`} value={fmtPct(row.delta_pct)} sub={`95% CI ${fmtCI(row.ci_low_pct, row.ci_high_pct)}`} />
        <Tile
          label="ΔRMSE in target units"
          value={fmtUnits(row.delta_rmse, unitDigits)}
          sub={`baseline RMSE ${fmtUnits(row.baseline_rmse, unitDigits)}`}
        />
        <Tile label="Folds improved (lift consistency)" value={`${nImproved} of ${row.n_folds}`} sub="needs ≥ 60% or a CI below 0" />
        <Tile
          label="Reliability (year-to-year r)"
          value={row.reliability_r === null ? 'not available' : fmt(row.reliability_r, 2)}
          sub="reported; never blocks admission"
        />
        <Tile label="Coverage" value={fmtShare(row.coverage)} sub="share of modelling sample with the metric" />
        <Tile label="Coefficient sign changes" value={String(row.coef_sign_changes)} sub="2 or more blocks Projection" />
      </div>

      <div className="grid-2" style={{ alignItems: 'start' }}>
        <ForestPlot
          headingLevel="h3"
          title="Fold-by-year ΔRMSE %"
          subtitle="Each fold trains on earlier seasons and forecasts the next one."
          rows={foldRows}
          axisLabel="ΔRMSE, % of baseline RMSE"
          betterLabel="more accurate with the metric"
          worseLabel="less accurate"
          unit="%"
          tableCaption={`Fold-by-year ΔRMSE for ${name} → ${target.short}`}
        />
        <div>
          <h3 style={{ fontSize: '0.98rem' }}>Why this verdict</h3>
          <dl className="meta">
            <dt>Verdict</dt>
            <dd>
              <VerdictBadge verdict={row.verdict} size="sm" /> {VERDICT_DESCRIPTIONS[row.verdict]}
            </dd>
            <dt>Reason code</dt>
            <dd>{row.reason_code}</dd>
            <dt>Verdict basis</dt>
            <dd>
              <strong>{BASIS_LABELS[basis]}.</strong> <span className="muted">({row.verdict_basis})</span>
            </dd>
            <dt>Rationale</dt>
            <dd>{row.rationale}</dd>
            <dt>Redundancy</dt>
            <dd>
              {row.max_corr_partner ? (
                <>
                  Most correlated baseline input: {metricLabel(row.max_corr_partner, metricsIdx)} (<code>{row.max_corr_partner}</code>), r ={' '}
                  {fmt(row.max_corr_with_baseline, 2)}.
                </>
              ) : (
                'No baseline correlation reported.'
              )}{' '}
              Redundancy family: <code>{row.family}</code>
              {row.family_representative ? ' (family representative)' : ''}
              {row.family_redundant ? '; redundant with a kept family member' : ''}.
            </dd>
            <dt>Nested windows</dt>
            <dd>
              Projection in {nestedProjection} of 5 nested windows (2021–2025); 2026 window:{' '}
              {row.nested_projection_2026_window ? 'Projection' : row.nested_verdicts['2026']}.
            </dd>
          </dl>
        </div>
      </div>

      <div className="section" style={{ marginTop: 24 }}>
        <h3 style={{ fontSize: '0.98rem' }}>Nested window verdicts, 2021–2026</h3>
        <p className="muted small" style={{ marginBottom: 4 }}>
          For each outer year the admission rules were re-run using only earlier seasons. 2026 is the frozen-in-workflow check (exploratory).
        </p>
        <div className="nested-strip" role="list" aria-label="Nested window verdicts">
          {NESTED_YEARS.map((y) => {
            const v = row.nested_verdicts[y];
            return (
              <div
                key={y}
                role="listitem"
                className={`nested-cell${v === 'Projection' ? ' v-projection' : ''}${y === '2026' ? ' y2026' : ''}`}
                aria-label={`${y}${y === '2026' ? ' (exploratory)' : ''}: ${v}`}
              >
                <span className="yr">
                  {y}
                  {y === '2026' ? ' · exploratory' : ''}
                </span>
                <span className="vd">
                  <VerdictIcon verdict={v} size={12} />
                  {v}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="section" style={{ marginTop: 24 }}>
        <ForestPlot
          headingLevel="h3"
          title="ΔRMSE % by subgroup"
          subtitle="Point estimates only (no subgroup intervals were published). The Projection test requires no harm in most large subgroups."
          rows={subgroupRows}
          axisLabel="ΔRMSE, % of baseline RMSE"
          betterLabel="more accurate with the metric"
          worseLabel="less accurate"
          unit="%"
          extraColumns={[{ key: 'n', label: 'Player-seasons', num: true }]}
          tableCaption={`Subgroup ΔRMSE for ${name} → ${target.short}`}
        />
      </div>

      <ResultMeta
        targetDefinition={
          <>
            {target.definition} <span className="muted">Unit: {target.unit}.</span>
          </>
        }
        population={`${target.eligibility}; ${fmtInt(row.n_player_seasons)} player-seasons, weighted by ${target.weight}.`}
        seasons={`${row.seasons}; nested windows 2021–2025 and a 2026 window.`}
        method={`Ridge regression. History baseline (${target.baseline}) versus baseline + ${name}; out-of-time RMSE, training seasons always precede the forecast season.`}
        ciType={`${meta.ci_definition} Point estimate: mean of the fold deltas.`}
        tier={{ key: 'historical', label: meta.evidence_tiers[row.evidence_tier] }}
        sources={[SOURCE_FILES.evaluations, ...NESTED_YEARS.map((y) => nestedSourceFile(target.id, y))]}
        sha256={meta.sources_sha256}
      />
    </article>
  );
}

// ------------------------------------------------------------------------- never-evaluated pair
function NotEvaluatedCard({
  metric,
  metricId,
  target,
  evaluatedFor,
  targets,
  onPick,
  meta,
}: {
  metric: Metric | undefined;
  metricId: string;
  target: Target;
  evaluatedFor: Evaluation[];
  targets: Target[];
  onPick: (metric: string, target: string) => void;
  meta: Meta;
}) {
  const name = metric?.description ?? metricId;
  return (
    <article className="card" aria-labelledby="result-title">
      <div className="card-head">
        <h2 id="result-title" className="card-title">
          {name} <span className="muted">→</span> {target.label}
        </h2>
        <VerdictBadge verdict="Not evaluated" />
      </div>
      <p>
        This metric was not among the {target.n_candidates} candidates evaluated for {targetPhrase(target)}. No verdict exists for this
        pair, and the lab does not infer one.
      </p>
      <dl className="meta">
        <dt>Metric catalog</dt>
        <dd>
          <code>{metricId}</code> · player types: {metric?.player_types.join(', ') ?? 'unknown'} · family: {metric?.family ?? 'unknown'}
        </dd>
        <dt>Target population</dt>
        <dd>
          {target.group === 'hitter' ? 'Hitters' : 'Pitchers'}: {target.eligibility}
        </dd>
      </dl>
      {evaluatedFor.length ? (
        <>
          <h3 style={{ fontSize: '0.98rem', marginTop: 16 }}>Evaluated for</h3>
          <div className="chip-row">
            {evaluatedFor.map((e) => (
              <button key={e.target} type="button" className="btn small" onClick={() => onPick(metricId, e.target)}>
                <VerdictIcon verdict={e.verdict} size={12} />
                {targets.find((t) => t.id === e.target)?.short ?? e.target}: {e.verdict}
              </button>
            ))}
          </div>
        </>
      ) : (
        <p className="muted">This metric has no evaluations in the canonical set.</p>
      )}
      <ResultMeta
        targetDefinition={
          <>
            {target.definition} <span className="muted">Unit: {target.unit}.</span>
          </>
        }
        population={`${target.eligibility}; ${fmtInt(target.n_player_seasons)} player-seasons.`}
        seasons="Not applicable: this pair has no evaluation."
        method={`Candidate metrics for this target were tested against its history baseline (${target.baseline}); this metric was not one of them.`}
        ciType="None: no estimate exists for this pair."
        tier={{ key: 'historical', label: meta.evidence_tiers.historical }}
        sources={[SOURCE_FILES.evaluations]}
        sha256={meta.sources_sha256}
        extra={[['Lookup result', 'Pair absent from the 208 canonical evaluations']]}
      />
    </article>
  );
}

// ------------------------------------------------------------------------- across targets
function AcrossTargets({
  metricId,
  metric,
  targets,
  eIdx,
  selected,
}: {
  metricId: string;
  metric: Metric | undefined;
  targets: Target[];
  eIdx: ReturnType<typeof buildEvaluationIndex>;
  selected: string;
}) {
  const name = metric?.description ?? metricId;
  const rows: ForestRow[] = targets.map((t) => {
    const l = lookupEvaluation(eIdx, metricId, t.id);
    const verdict: VerdictKey = l.status === 'evaluated' ? l.row.verdict : 'Not evaluated';
    const common = {
      key: t.id,
      label: (
        <>
          {t.label} <VerdictBadge verdict={verdict} size="sm" />
        </>
      ),
      labelText: `${t.label}: ${verdict}`,
      selected: t.id === selected,
      onSelect: () => setParams({ target: t.id }),
    };
    if (l.status !== 'evaluated') {
      return { ...common, est: null, lo: null, hi: null, valueText: 'Not evaluated', missingText: 'Not evaluated' };
    }
    return {
      ...common,
      est: l.row.delta_pct,
      lo: l.row.ci_low_pct,
      hi: l.row.ci_high_pct,
      valueText: fmtPct(l.row.delta_pct),
      valueSub: fmtCI(l.row.ci_low_pct, l.row.ci_high_pct),
      tableExtra: { verdict, folds: `${Math.round(l.row.folds_improved_share * l.row.n_folds)}/${l.row.n_folds}` },
    };
  });
  return (
    <ForestPlot
      headingLevel="h3"
      title={`${name}: ΔRMSE % for each target`}
      subtitle="Mean of fold deltas with the 95% player-cluster bootstrap interval."
      rows={rows}
      axisLabel="ΔRMSE, % of baseline RMSE"
      betterLabel="more accurate with the metric"
      worseLabel="less accurate"
      unit="%"
      selectLabel="Open target"
      extraColumns={[
        { key: 'verdict', label: 'Verdict' },
        { key: 'folds', label: 'Folds improved', num: true },
      ]}
      tableCaption={`${name} across targets`}
    />
  );
}

// ------------------------------------------------------------------------- candidate table
function CandidateTable({
  target,
  evaluations,
  metricsIdx,
  selectedMetric,
  verdictFilter,
  onFilter,
  onPick,
}: {
  target: Target;
  evaluations: Evaluation[];
  metricsIdx: Map<string, Metric>;
  selectedMetric: string;
  verdictFilter: VerdictFilter;
  onFilter: (v: VerdictFilter) => void;
  onPick: (metric: string) => void;
}) {
  const all = evaluations.filter((e) => e.target === target.id).sort((a, b) => a.delta_pct - b.delta_pct);
  const counts = new Map<string, number>();
  for (const e of all) counts.set(e.verdict, (counts.get(e.verdict) ?? 0) + 1);
  const rows = verdictFilter === 'all' ? all : all.filter((e) => e.verdict === verdictFilter);
  return (
    <div className="card">
      <Segmented<VerdictFilter>
        legend="Show verdicts"
        value={verdictFilter}
        onChange={onFilter}
        options={VERDICT_FILTERS.map((v) => ({
          value: v,
          label: v === 'all' ? `All (${all.length})` : `${v} (${counts.get(v) ?? 0})`,
        }))}
      />
      <p className="muted small" role="status" style={{ margin: '10px 0' }}>
        Showing {rows.length} of {all.length} candidates for {target.short}.
      </p>
      <div className="table-scroll" role="region" aria-label={`Candidates for ${target.label}`} tabIndex={0}>
        <table>
          <caption className="sr-only">
            Candidate metrics for {target.label}: verdict and change in forecast error
          </caption>
          <thead>
            <tr>
              <th scope="col">Metric</th>
              <th scope="col">Verdict</th>
              <th scope="col" className="num">
                ΔRMSE % (mean of folds)
              </th>
              <th scope="col" className="num">
                95% CI
              </th>
              <th scope="col" className="num">
                Folds improved
              </th>
              <th scope="col" className="num">
                Reliability r
              </th>
              <th scope="col" className="num">
                Nested Projection (of 5)
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((e) => (
              <tr key={e.metric} className={e.metric === selectedMetric ? 'selected' : undefined}>
                <th scope="row" style={{ fontWeight: 500 }}>
                  <button type="button" className="link-button" onClick={() => onPick(e.metric)} aria-current={e.metric === selectedMetric ? 'true' : undefined}>
                    {metricLabel(e.metric, metricsIdx)}
                  </button>
                  <div className="muted small">
                    <code>{e.metric}</code>
                  </div>
                </th>
                <td>
                  <VerdictBadge verdict={e.verdict} size="sm" />
                </td>
                <td className="num">{fmtPct(e.delta_pct)}</td>
                <td className="num">{fmtCI(e.ci_low_pct, e.ci_high_pct)}</td>
                <td className="num">
                  {Math.round(e.folds_improved_share * e.n_folds)}/{e.n_folds}
                </td>
                <td className="num">{e.reliability_r === null ? '—' : fmt(e.reliability_r, 2)}</td>
                <td className="num">{e.nested_projection_count_2021_2025}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
