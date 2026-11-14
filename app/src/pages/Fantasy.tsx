import { useMemo } from 'react';
import { useData } from '../data/load';
import {
  FANTASY_KINDS,
  type Fantasy,
  type FantasyKind,
  type FantasyResult,
  type Meta,
  type Metric,
  type Target,
} from '../data/schemas';
import { SOURCE_FILES } from '../data/constants';
import { setParams, useRoute } from '../router';
import { Callout, Gate, PageHead, Tile } from '../components/Page';
import { Segmented } from '../components/Segmented';
import { FantasyVerdictBadge } from '../components/Badges';
import { FlaskIcon } from '../components/Icons';
import { ResultMeta } from '../components/ResultMeta';
import { ForestPlot, type ForestRow } from '../components/charts/ForestPlot';
import { FantasyMatrix } from '../components/charts/FantasyMatrix';
import { DataTable } from '../components/charts/ChartFigure';
import {
  fantasyByYearFor,
  fantasyOutcomesFor,
  fantasyTargetsForKind,
  findFantasyResult,
  level1For,
  metricIndex,
} from '../lib/lookup';
import {
  FANTASY_KIND_INFO,
  FANTASY_VERDICT_INFO,
  fantasyModelLabel,
  fantasyTargetId,
  fantasyTargetLabel,
  fantasyTargetShort,
  familyLabel,
  outcomeDefinition,
  outcomeLabel,
} from '../lib/labels';
import { compare2026, fantasyResultSentence } from '../lib/wording';
import { digitsFor, fmt, fmtCI, fmtInt, fmtP, fmtPct, fmtShare, fmtSigned, fmtUnits } from '../lib/format';

const POOLED = '2021-2025 pooled (primary)' as const;
const L1_YEARS: Array<2021 | 2022 | 2023 | 2024 | 2025 | 2026> = [2021, 2022, 2023, 2024, 2025, 2026];
const S2026 = '2026 (exploratory)' as const;

export default function FantasyPage() {
  const state = useData('meta', 'targets', 'metrics', 'fantasy');
  return (
    <>
      <PageHead eyebrow="Exploratory fantasy linkage" title="Fantasy Linkage Explorer">
        <p className="lede">
          None of the six study targets is a fantasy category. This bridge asks whether out-of-time forecasts of those targets add information
          about next-season fantasy outcomes, beyond a direct fantasy-history baseline (BF) built from the same public data.
        </p>
      </PageHead>
      <Gate state={state} what="fantasy-bridge results">
        {(d) => <FantasyBody {...d} />}
      </Gate>
    </>
  );
}

function FantasyBody({ meta, targets, metrics, fantasy }: { meta: Meta; targets: Target[]; metrics: Metric[]; fantasy: Fantasy }) {
  const route = useRoute();
  const mIdx = useMemo(() => metricIndex(metrics), [metrics]);
  const results = fantasy.results;

  const kindParam = route.params.get('kind') as FantasyKind | null;
  const kind: FantasyKind = kindParam && (FANTASY_KINDS as readonly string[]).includes(kindParam) ? kindParam : 'target_forecast_added';
  const kindTargets = fantasyTargetsForKind(results, kind);
  const targetParam = route.params.get('target');
  const target = targetParam && kindTargets.includes(targetParam) ? targetParam : kindTargets.includes('woba') ? 'woba' : kindTargets[0];
  const outcomes = fantasyOutcomesFor(results, kind, target);
  const outcomeParam = route.params.get('outcome');
  const outcome = outcomeParam && outcomes.includes(outcomeParam) ? outcomeParam : outcomes.includes('HR') ? 'HR' : outcomes[0];
  const matrixSample = route.params.get('msample') === '2026' ? S2026 : POOLED;

  const pooled = findFantasyResult(results, { kind, target, outcome, sample: POOLED });
  const r2026 = findFantasyResult(results, { kind, target, outcome, sample: S2026 });

  const forecastLabel = fantasyTargetLabel(target, mIdx);
  const targetId = fantasyTargetId(target);
  const targetRow = targetId ? targets.find((t) => t.id === targetId) : undefined;

  return (
    <>
      <Callout kind="caution" title={`Evidence tier: ${meta.evidence_tiers.exploratory_fantasy}`}>
        <p>
          Protocol: {fantasy.protocol}. The 2021–2025 seasons were already analysed in the original study and 2026 had been inspected for the six
          targets, so these results are exploratory. Fantasy pools include players who did not return (scored as zero).
        </p>
      </Callout>

      <div className="card" role="search" aria-label="Choose a fantasy linkage">
        <div className="controls">
          <Segmented<FantasyKind>
            legend="Comparison"
            value={kind}
            onChange={(v) => setParams({ kind: v })}
            options={FANTASY_KINDS.map((k) => ({ value: k, label: FANTASY_KIND_INFO[k].label }))}
          />
        </div>
        <p className="muted small" style={{ marginTop: -6 }}>
          {FANTASY_KIND_INFO[kind].question} Baseline: {FANTASY_KIND_INFO[kind].base}; augmented: {FANTASY_KIND_INFO[kind].aug}.
        </p>
        <div className="controls" style={{ marginBottom: 0 }}>
          <Segmented
            legend={kind === 'direct_metric_added' ? 'Raw metric' : 'Target forecast'}
            value={target}
            onChange={(v) => setParams({ target: v })}
            options={kindTargets.map((t) => ({
              value: t,
              label: kind === 'direct_metric_added' ? mIdx.get(t)?.description ?? t : fantasyTargetShort(t),
            }))}
          />
          <Segmented
            legend="Fantasy outcome (next season)"
            value={outcome}
            onChange={(v) => setParams({ outcome: v })}
            options={outcomes.map((o) => ({ value: o, label: outcomeLabel(o, 'short'), title: outcomeLabel(o) }))}
          />
        </div>
      </div>

      <section className="section" aria-labelledby="fl-result" style={{ marginTop: 20 }}>
        {pooled ? (
          <PooledCard
            r={pooled}
            r2026={r2026}
            fantasy={fantasy}
            meta={meta}
            forecastLabel={forecastLabel}
            targetRow={targetRow}
            mIdx={mIdx}
          />
        ) : (
          <div className="card">
            <h2 id="fl-result" className="card-title">
              {forecastLabel} → {outcomeLabel(outcome)}
            </h2>
            <p>This combination was not tested in the fantasy bridge.</p>
          </div>
        )}
      </section>

      <section className="section" aria-labelledby="fl-matrix">
        <h2 id="fl-matrix">Overview: every forecast × category result for this comparison</h2>
        <p className="section-intro">
          {FANTASY_KIND_INFO[kind].label}. Select a cell to open it above. Gains, nulls and harms use the same cell size, text and glyph.
        </p>
        <Segmented
          legend="Sample"
          value={matrixSample === S2026 ? '2026' : 'pooled'}
          onChange={(v) => setParams({ msample: v === '2026' ? '2026' : null })}
          options={[
            { value: 'pooled', label: '2021–2025 pooled (primary)' },
            { value: '2026', label: '2026 (exploratory)' },
          ]}
        />
        <VerdictCounts results={results.filter((r) => r.kind === kind && r.sample === matrixSample)} />
        {(['hitter', 'pitcher'] as const).map((group) => {
          const rowsForGroup = results.filter((r) => r.kind === kind && r.sample === matrixSample && r.group === group);
          if (!rowsForGroup.length) return null;
          const rowKeys = [...new Set(rowsForGroup.map((r) => r.target))];
          const colKeys = [...new Set(rowsForGroup.map((r) => r.outcome))];
          return (
            <div className="card" key={group} style={{ marginTop: 14 }}>
              <FantasyMatrix
                title={`${group === 'hitter' ? 'Hitter' : 'Pitcher'} ${kind === 'direct_metric_added' ? 'raw metrics' : 'forecasts'} × ${group} categories (${matrixSample === POOLED ? '2021–2025 pooled' : '2026, exploratory'})`}
                subtitle={`ΔRMSE % of the augmented model vs the baseline, 95% player-cluster bootstrap interval. Source: ${SOURCE_FILES.fantasyResults}`}
                rowHeader={kind === 'direct_metric_added' ? 'Raw metric' : 'Forecast'}
                rows={rowKeys.map((k) => ({ key: k, label: kind === 'direct_metric_added' ? mIdx.get(k)?.description ?? k : fantasyTargetShort(k) }))}
                cols={colKeys.map((k) => ({ key: k, label: outcomeLabel(k, 'short') }))}
                results={rowsForGroup}
                selected={{ target, outcome }}
                onSelect={(t, o) => {
                  setParams({ target: t, outcome: o });
                  document.getElementById('fl-result')?.scrollIntoView?.({ block: 'start' });
                }}
              />
            </div>
          );
        })}
      </section>

      <section className="section" aria-labelledby="fl-pools">
        <h2 id="fl-pools">Who is in the fantasy pools</h2>
        <p className="section-intro">
          Pools are fixed at forecast time from the previous season, so they include players who later got hurt, were demoted or released. Those
          players count as zero in counting categories. Rookies and players below the thresholds are outside the pool.
        </p>
        <div className="card">
          <DataTable
            caption="Fantasy pool composition by outcome season"
            rows={fantasy.cohorts}
            rowKey={(c) => `${c.player_group}-${c.outcome_season}`}
            columns={[
              { key: 'g', label: 'Group', render: (c) => `${c.player_group === 'hitter' ? 'Hitters' : 'Pitchers'} ${c.outcome_season}` },
              { key: 's', label: 'Status', render: (c) => c.status },
              { key: 'n', label: 'Pool size', num: true, render: (c) => fmtInt(c.pool_size) },
              { key: 'a', label: 'Any season-T appearance', num: true, render: (c) => fmtShare(c.share_any_T_appearance, 1) },
              { key: 'z', label: 'Zero counting outcome', num: true, render: (c) => fmtShare(c.share_zero_counting_outcome, 1) },
              {
                key: 'c',
                label: "Meets original study's t+1 rule",
                num: true,
                render: (c) => (c['share_meeting_canonical_t+1_rule'] === null ? 'not computed' : fmtShare(c['share_meeting_canonical_t+1_rule'], 1)),
              },
              { key: 'f', label: 'Meets AB/IP floor for ratio categories', num: true, render: (c) => fmtShare(c.share_meeting_rate_floor, 1) },
            ]}
          />
          <p className="muted small" style={{ marginTop: 8 }}>
            Source: <code>{SOURCE_FILES.fantasyCohorts}</code>
          </p>
        </div>
      </section>

      <DecisionSection fantasy={fantasy} meta={meta} />
    </>
  );
}

function VerdictCounts({ results }: { results: FantasyResult[] }) {
  const counts = new Map<string, number>();
  for (const r of results) counts.set(r.verdict, (counts.get(r.verdict) ?? 0) + 1);
  const entries = Object.entries(FANTASY_VERDICT_INFO).filter(([v]) => counts.has(v));
  return (
    <p className="chip-row" style={{ margin: '12px 0 0' }} aria-label="Verdict counts">
      <span className="muted small">{results.length} results:</span>
      {entries.map(([v]) => (
        <span key={v} className="chip-row">
          <FantasyVerdictBadge verdict={v as FantasyResult['verdict']} size="sm" />
          <span className="small">× {counts.get(v)}</span>
        </span>
      ))}
    </p>
  );
}

function PooledCard({
  r,
  r2026,
  fantasy,
  meta,
  forecastLabel,
  targetRow,
  mIdx,
}: {
  r: FantasyResult;
  r2026: FantasyResult | undefined;
  fantasy: Fantasy;
  meta: Meta;
  forecastLabel: string;
  targetRow: Target | undefined;
  mIdx: Map<string, Metric>;
}) {
  const oLong = outcomeLabel(r.outcome);
  const ctx = { forecast: forecastLabel, outcome: oLong.charAt(0).toLowerCase() + oLong.slice(1) };
  const digits = digitsFor([r.rmse_base, r.rmse_aug, r.delta_rmse]);
  const byYear = fantasyByYearFor(fantasy.by_year, r);
  const l1 = level1For(fantasy.level1, r.target, r.outcome);
  const showL1 = (r.kind === 'target_forecast_added' || r.kind === 'admitted_vs_history_target_forecast') && !!l1;

  const yearRows: ForestRow[] = [
    ...byYear
      .filter((b) => b.sample === POOLED)
      .map((b) => ({
        key: `y${b.outcome_season}`,
        label: `${b.outcome_season}`,
        labelText: `Outcome season ${b.outcome_season} (n = ${b.n})`,
        sub: `n = ${fmtInt(b.n)}`,
        est: b.delta_pct,
        lo: null,
        hi: null,
        tone: 'ink' as const,
        valueText: fmtPct(b.delta_pct),
        group: '2021–2025, by season (point estimates)',
      })),
    {
      key: 'pooled',
      label: '2021–2025 pooled',
      labelText: '2021–2025 pooled with 95% CI',
      sub: `n = ${fmtInt(r.n_rows)} rows`,
      est: r.delta_pct,
      lo: r.ci_low_pct,
      hi: r.ci_high_pct,
      valueText: fmtPct(r.delta_pct),
      valueSub: fmtCI(r.ci_low_pct, r.ci_high_pct),
      group: 'Pooled',
    },
    ...(r2026
      ? [
          {
            key: 'y2026',
            label: '2026 (exploratory)',
            labelText: `2026 exploratory (n = ${r2026.n_rows})`,
            sub: `n = ${fmtInt(r2026.n_rows)}`,
            est: r2026.delta_pct,
            lo: r2026.ci_low_pct,
            hi: r2026.ci_high_pct,
            hollow: true,
            valueText: fmtPct(r2026.delta_pct),
            valueSub: fmtCI(r2026.ci_low_pct, r2026.ci_high_pct),
            group: '2026 (exploratory)',
          },
        ]
      : []),
  ];

  return (
    <article className="card" aria-labelledby="fl-result">
      <div className="card-head">
        <h2 id="fl-result" className="card-title">
          {forecastLabel} <span className="muted">→</span> {oLong}
        </h2>
        <FantasyVerdictBadge verdict={r.verdict} />
      </div>
      <p className="muted small" style={{ marginTop: -4 }}>
        {familyLabel(r.family)} · 2021–2025 pooled (primary sample)
      </p>
      <p style={{ maxWidth: '88ch' }}>{fantasyResultSentence(r, ctx)}</p>

      <div className="tile-row">
        <Tile label="ΔRMSE, augmented vs baseline" value={fmtPct(r.delta_pct)} sub={`95% CI ${fmtCI(r.ci_low_pct, r.ci_high_pct)}`} />
        <Tile
          label={`RMSE in ${r.units}`}
          value={`${fmtUnits(r.rmse_base, digits)} → ${fmtUnits(r.rmse_aug, digits)}`}
          sub={`change ${fmtSigned(r.delta_rmse, digits)}`}
        />
        <Tile
          label="Season-block 95% CI"
          value={r.season_block_ci_low_pct === null ? '—' : fmtCI(r.season_block_ci_low_pct, r.season_block_ci_high_pct)}
          sub="resamples the 5 seasons; coarse"
        />
        <Tile label="Adjusted p" value={fmtP(r.p_adjusted)} sub={r.adjustment ?? 'no adjustment'} />
        <Tile label="Seasons improved" value={`${r.years_improved} of ${r.n_years}`} sub="2021–2025" />
        <Tile label="Rows / players" value={fmtInt(r.n_rows)} sub={`${fmtInt(r.n_players)} players`} />
      </div>

      <ForestPlot
        headingLevel="h3"
        title="ΔRMSE % by season"
        subtitle="Per-season values are point estimates; the pooled and 2026 rows show 95% intervals."
        rows={yearRows}
        axisLabel="ΔRMSE, % of baseline RMSE"
        betterLabel="augmented model more accurate"
        worseLabel="less accurate"
        unit="%"
        tableCaption={`${forecastLabel} → ${oLong}: ΔRMSE by season`}
      />

      {r2026 ? (
        <div className="callout note" style={{ marginTop: 18 }}>
          <div className="card-head" style={{ marginBottom: 6 }}>
            <p className="callout-title" style={{ margin: 0 }}>
              2026 (exploratory): one season, already played when forecasts were frozen
            </p>
            <FantasyVerdictBadge verdict={r2026.verdict} size="sm" />
          </div>
          <p>{fantasyResultSentence(r2026, ctx)}</p>
          <p className="muted small">
            {compare2026(r, r2026)} n = {fmtInt(r2026.n_rows)} player-seasons; no multiplicity adjustment is applied to 2026 rows.
          </p>
        </div>
      ) : null}

      <div className="grid-2" style={{ alignItems: 'start', marginTop: 18 }}>
        <div>
          <h3 style={{ fontSize: '0.98rem' }}>Baseline vs augmented (identical rows)</h3>
          <DataTable
            caption="Baseline and augmented model error"
            rows={[
              { k: 'base', name: fantasyModelLabel(r.base, mIdx), rmse: r.rmse_base, mae: r.mae_base },
              { k: 'aug', name: fantasyModelLabel(r.aug, mIdx), rmse: r.rmse_aug, mae: r.mae_aug },
            ]}
            rowKey={(x) => x.k}
            columns={[
              { key: 'n', label: 'Model', render: (x) => x.name },
              { key: 'r', label: 'RMSE', num: true, render: (x) => fmtUnits(x.rmse, digits) },
              { key: 'm', label: 'MAE', num: true, render: (x) => fmtUnits(x.mae, digits) },
            ]}
          />
          <p className="muted small" style={{ marginTop: 8 }}>
            Errors in {r.units}. Two-sided bootstrap p = {fmtP(r.p_two_sided)} before adjustment. Negative ΔRMSE means the augmented model was
            more accurate.
          </p>
        </div>
        <div>
          <h3 style={{ fontSize: '0.98rem' }}>Level 1 correlation: association only</h3>
          {showL1 && l1 ? (
            <>
              <p>
                Across 2021–2025 (n = {fmtInt(l1.n_2021_2025)}), the admitted {fantasyTargetShort(r.target)} forecast and next-season{' '}
                {outcomeLabel(r.outcome, 'short')} had a Spearman rank correlation of {fmt(l1.spearman_2021_2025, 3)} (95% CI{' '}
                {fmtCI(l1.ci_low, l1.ci_high, 3)}). <strong>{l1.note.charAt(0).toUpperCase() + l1.note.slice(1)}.</strong> A forecast can correlate
                with a category and still add nothing beyond the fantasy baseline.
              </p>
              <DataTable
                caption="Spearman correlation by season (association only)"
                rows={L1_YEARS}
                rowKey={(y) => String(y)}
                columns={[
                  { key: 'y', label: 'Season', render: (y) => (y === 2026 ? '2026 (exploratory)' : String(y)) },
                  {
                    key: 'rho',
                    label: 'Spearman ρ',
                    num: true,
                    render: (y) => {
                      const v = l1[`rho_${y}` as const];
                      return v === null ? '—' : fmt(v, 3);
                    },
                  },
                ]}
              />
            </>
          ) : (
            <p className="muted">Level 1 correlations are reported only for single target forecasts (not for joint sets or raw metrics).</p>
          )}
        </div>
      </div>

      <ResultMeta
        targetDefinition={
          <>
            <strong>{oLong}:</strong> {outcomeDefinition(r.outcome)}{' '}
            {targetRow ? (
              <span className="muted">
                Forecast input: {targetRow.label} ({targetRow.definition}) Not established: {targetRow.not_established}
              </span>
            ) : null}
          </>
        }
        population={`Forecast-date pools: hitters with ≥ 150 PA, pitchers with ≥ 80 IP (starters) or ≥ 30 IP (relievers) in the season before; not filtered on next-season participation. ${fmtInt(r.n_rows)} rows from ${fmtInt(r.n_players)} players.`}
        seasons="Outcome seasons 2021–2025 pooled (primary); 2026 shown separately as exploratory. Training seasons always precede the outcome season."
        method={`Ridge regression on standardized features (penalty tuned on inner chronological folds). ${fantasyModelLabel(r.base, mIdx)} versus ${fantasyModelLabel(r.aug, mIdx)} on identical rows and training seasons.`}
        ciType={`95% paired player-cluster bootstrap (2,000 resamples, players resampled across outer years); season-block bootstrap over the five outer years as a coarse check. Multiplicity: ${r.adjustment ?? 'none'}.`}
        tier={{ key: 'exploratory_fantasy', label: meta.evidence_tiers.exploratory_fantasy }}
        sources={[SOURCE_FILES.fantasyResults, SOURCE_FILES.fantasyByYear, ...(showL1 ? [SOURCE_FILES.fantasyLevel1] : [])]}
        sha256={meta.sources_sha256}
      />
    </article>
  );
}

function DecisionSection({ fantasy, meta }: { fantasy: Fantasy; meta: Meta }) {
  const rows = fantasy.decision;
  if (!rows.length) return null;
  return (
    <section className="section" aria-labelledby="fl-decision">
      <h2 id="fl-decision">Illustrative draft backtest (what-if)</h2>
      <Callout kind="illustrative" icon={<FlaskIcon />} title={`Evidence tier: ${meta.evidence_tiers.illustrative}`}>
        <p>
          A hypothetical policy: rank players by predicted 5×5 value (or predicted points) and take the top k, with every category model using
          the fantasy baseline (“baseline”) or the baseline plus all admitted target forecasts (“augmented”). There is no average draft position, position
          eligibility, snake order, in-season management or league simulation, so this is not evidence that anyone wins leagues.
        </p>
      </Callout>
      <div className="card">
        <DataTable
          caption="Illustrative draft backtest: realized value of the top-k picks"
          rows={rows}
          rowKey={(d) => `${d.group}-${d.format}-${d.k}-${d.sample}`}
          columns={[
            {
              key: 'g',
              label: 'Group · sample',
              render: (d) => `${d.group === 'hitter' ? 'Hitters' : 'Pitchers'} · ${d.sample.startsWith('2021') ? '2021–25 pooled' : '2026 (exploratory)'}`,
            },
            { key: 'f', label: 'Format', render: (d) => (d.format === 'roto_5x5' ? '5×5 roto' : d.format === 'points' ? 'Points' : d.format) },
            { key: 'k', label: 'Top k (league size)', num: true, render: (d) => `${d.k}${d.league_size_equivalent ? ` (${d.league_size_equivalent})` : ''}` },
            { key: 'b', label: 'Mean realized value, baseline', num: true, render: (d) => fmt(d.mean_realized_value_of_picks_base, 3) },
            { key: 'a', label: 'Augmented', num: true, render: (d) => fmt(d.mean_realized_value_of_picks_aug, 3) },
            { key: 'd', label: 'Difference (95% CI)', num: true, render: (d) => `${fmtSigned(d.delta_mean_realized_value, 3)} ${fmtCI(d.ci_low, d.ci_high, 3)}` },
            { key: 's', label: 'Seasons augmented better', num: true, render: (d) => (d.seasons_aug_better === null ? '—' : `${d.seasons_aug_better} of 5`) },
            { key: 'rho', label: 'Spearman ρ, base → aug', num: true, render: (d) => `${fmt(d.spearman_base, 3)} → ${fmt(d.spearman_aug, 3)}` },
            { key: 'drho', label: 'Δρ (95% CI)', num: true, render: (d) => `${fmtSigned(d.delta_spearman, 3)} ${fmtCI(d.spearman_ci_low, d.spearman_ci_high, 3)}` },
            { key: 'o', label: 'Top-k overlap, base → aug', num: true, render: (d) => `${fmtShare(d.topk_overlap_base, 1)} → ${fmtShare(d.topk_overlap_aug, 1)}` },
          ]}
        />
        <p className="muted small" style={{ marginTop: 8 }}>
          Realized value is in roto z-score units for 5×5 rows and in fantasy points for points rows. Source:{' '}
          <code>{SOURCE_FILES.fantasyDecision}</code>
          {meta.sources_sha256[SOURCE_FILES.fantasyDecision] ? (
            <>
              {' '}
              · sha256 <span className="hash">{meta.sources_sha256[SOURCE_FILES.fantasyDecision].slice(0, 12)}…</span>
            </>
          ) : null}
        </p>
      </div>
    </section>
  );
}
