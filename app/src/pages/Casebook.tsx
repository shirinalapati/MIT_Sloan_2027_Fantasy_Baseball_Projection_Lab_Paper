import { useMemo } from 'react';
import { useData } from '../data/load';
import { CASE_SELECTIONS, type Case, type Casebook, type CaseSelection, type Meta, type Metric, type Target } from '../data/schemas';
import { SOURCE_FILES } from '../data/constants';
import { setParams, useRoute } from '../router';
import { Callout, Gate, PageHead, Tile } from '../components/Page';
import { Segmented, SelectControl } from '../components/Segmented';
import { InfoIcon, ResultIcon } from '../components/Icons';
import { ResultMeta } from '../components/ResultMeta';
import { BarList } from '../components/charts/BarList';
import { ForestPlot, type ForestRow } from '../components/charts/ForestPlot';
import { metricIndex } from '../lib/lookup';
import { metricShort } from '../lib/labels';
import {
  SELECTION_LABELS,
  SELECTION_SHORT,
  contrastsOf,
  displayName,
  filterCases,
  seasonsOf,
  summarizeCases,
  type CaseFilter,
} from '../lib/casebook';
import { fmt, fmtCI, fmtInt, fmtPct, fmtShare, fmtSigned } from '../lib/format';

const DEFAULT_CONTRAST = 'pitching_fip:stuff_plus';

function targetDigits(targetId: string): number {
  return targetId === 'hitting_woba' ? 3 : 2;
}

function metricDigits(values: number[]): number {
  const m = Math.max(...values.map((v) => Math.abs(v)));
  if (m >= 10) return 1;
  if (m >= 1) return 2;
  return 3;
}

export default function CasebookPage() {
  const state = useData('meta', 'targets', 'metrics', 'casebook');
  return (
    <>
      <PageHead eyebrow="Historical research evidence" title="Player Casebook">
        <p className="lede">
          Curated player-seasons showing what adding one metric did to individual forecasts, including the cases where it made them worse.
          Forecasts are the study&apos;s own out-of-time forecasts; observed values are public season statistics.
        </p>
      </PageHead>
      <Gate state={state} what="the casebook">
        {(d) => <CasebookBody {...d} />}
      </Gate>
    </>
  );
}

function CasebookBody({ meta, targets, metrics, casebook }: { meta: Meta; targets: Target[]; metrics: Metric[]; casebook: Casebook }) {
  const route = useRoute();
  const mIdx = useMemo(() => metricIndex(metrics), [metrics]);
  const contrasts = useMemo(() => contrastsOf(casebook.cases), [casebook]);
  const seasons = useMemo(() => seasonsOf(casebook.cases), [casebook]);

  const cParam = route.params.get('contrast');
  const contrast = cParam === 'all' || (cParam && contrasts.includes(cParam)) ? cParam : contrasts.includes(DEFAULT_CONTRAST) ? DEFAULT_CONTRAST : contrasts[0];
  const selParam = route.params.get('selection');
  const selection = (CASE_SELECTIONS as readonly string[]).includes(selParam ?? '') ? (selParam as CaseSelection) : 'all';
  const seasonParam = Number(route.params.get('season'));
  const season = seasons.includes(seasonParam) ? seasonParam : 'all';
  const resParam = route.params.get('result');
  const result = resParam === 'improved' || resParam === 'worsened' ? resParam : 'all';
  const query = route.params.get('q') ?? '';

  const filter: CaseFilter = { contrast, selection, season, query, result };
  const rows = filterCases(casebook.cases, filter);
  const summary = summarizeCases(rows);

  const contrastLabel = (c: string) => {
    const [t, m] = c.split(':');
    return `${metricShort(m, mIdx)} → ${targets.find((x) => x.id === t)?.short ?? t}`;
  };

  return (
    <>
      <Callout kind="info" icon={<InfoIcon />} title="How these cases were selected">
        <p style={{ fontSize: '1.02rem' }}>{casebook.selection_note}</p>
      </Callout>

      <div className="card" role="search" aria-label="Filter the casebook">
        <div className="controls" style={{ marginBottom: 12 }}>
          <SelectControl
            label="Contrast (metric → target)"
            value={contrast}
            onChange={(v) => setParams({ contrast: v })}
            options={[{ value: 'all', label: 'All contrasts' }, ...contrasts.map((c) => ({ value: c, label: contrastLabel(c) }))]}
          />
          <SelectControl
            label="Forecast season"
            value={season === 'all' ? 'all' : String(season)}
            onChange={(v) => setParams({ season: v === 'all' ? null : v })}
            options={[{ value: 'all', label: 'All seasons (2021–2025)' }, ...seasons.map((s) => ({ value: String(s), label: `${s} (features from ${s - 1})` }))]}
          />
          <div className="control">
            <label className="control-label" htmlFor="case-search">
              Search player
            </label>
            <input
              id="case-search"
              type="search"
              value={query}
              placeholder="e.g. Mateo"
              onChange={(e) => setParams({ q: e.target.value || null })}
            />
          </div>
        </div>
        <div className="controls" style={{ marginBottom: 0 }}>
          <Segmented<'all' | CaseSelection>
            legend="Selection type"
            value={selection}
            onChange={(v) => setParams({ selection: v === 'all' ? null : v })}
            options={[{ value: 'all', label: 'All' }, ...CASE_SELECTIONS.map((s) => ({ value: s, label: SELECTION_LABELS[s] }))]}
          />
          <Segmented<'all' | 'improved' | 'worsened'>
            legend="Forecast error"
            value={result}
            onChange={(v) => setParams({ result: v === 'all' ? null : v })}
            options={[
              { value: 'all', label: 'All' },
              { value: 'improved', label: 'Improved' },
              { value: 'worsened', label: 'Worsened' },
            ]}
          />
        </div>
      </div>

      <section className="section" aria-labelledby="cases-title" style={{ marginTop: 20 }}>
        <h2 id="cases-title">Cases</h2>
        <p className="chip-row" role="status" aria-live="polite" style={{ marginBottom: 10 }}>
          <span>
            Showing <strong>{summary.n}</strong> of {casebook.cases.length} cases:
          </span>
          <span className="badge sm f-gain">
            <ResultIcon improved size={12} /> {summary.improved} improved
          </span>
          <span className="badge sm f-harm">
            <ResultIcon improved={false} size={12} /> {summary.worsened} worsened
          </span>
        </p>
        <CaseTable rows={rows} targets={targets} mIdx={mIdx} contrastLabel={contrastLabel} />
      </section>

      {contrast !== 'all' ? (
        <CohortSection contrast={contrast} casebook={casebook} targets={targets} meta={meta} mIdx={mIdx} contrastLabel={contrastLabel(contrast)} />
      ) : (
        <section className="section">
          <h2>Decile effects</h2>
          <p className="muted">Choose a single contrast above to see its cohort (decile) effects and unit translation.</p>
          <div className="card">
            <ResultMeta
              targetDefinition="Varies by contrast: each case is a forecast of that contrast's target (see the contrast column and the Methods page)."
              population="Players meeting the study's eligibility in both seasons (outcome observed)."
              seasons="Nested outer years 2021–2025 (feature seasons 2020–2024)."
              method="Single-feature contrasts (ridge): history baseline versus baseline + the metric."
              ciType="None for individual cases; cohort intervals are shown when a single contrast is selected."
              tier={{ key: 'historical', label: meta.evidence_tiers.historical }}
              sources={[SOURCE_FILES.forecastChanges]}
              sha256={meta.sources_sha256}
            />
          </div>
        </section>
      )}
    </>
  );
}

function CaseTable({
  rows,
  targets,
  mIdx,
  contrastLabel,
}: {
  rows: Case[];
  targets: Target[];
  mIdx: Map<string, Metric>;
  contrastLabel: (c: string) => string;
}) {
  if (!rows.length) {
    return <p className="card">No cases match these filters.</p>;
  }
  const mixed = new Set(rows.map((r) => r.contrast)).size > 1;
  return (
    <div className="table-scroll" role="region" aria-label="Casebook cases (scrolls horizontally)" tabIndex={0}>
      <table>
        <caption className="sr-only">Forecast without and with the metric, observed value, and change in absolute error for each case</caption>
        <thead>
          <tr>
            <th scope="col">Player</th>
            {mixed ? <th scope="col">Contrast</th> : null}
            <th scope="col">Seasons</th>
            <th scope="col">Selection</th>
            <th scope="col" className="num">
              Metric value
            </th>
            <th scope="col" className="num">
              Forecast without
            </th>
            <th scope="col" className="num">
              Forecast with
            </th>
            <th scope="col" className="num">
              Change
            </th>
            <th scope="col" className="num">
              Observed
            </th>
            <th scope="col" className="num">
              Abs. error change
            </th>
            <th scope="col">Result</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c, i) => {
            const d = targetDigits(c.target);
            const md = metricDigits([c.metric_value]);
            const t = targets.find((x) => x.id === c.target);
            return (
              <tr key={`${c.contrast}-${c.player}-${c.feature_season}-${c.selection}-${i}`}>
                <th scope="row" style={{ fontWeight: 550, whiteSpace: 'nowrap' }}>
                  {displayName(c.player)}
                </th>
                {mixed ? <td>{contrastLabel(c.contrast)}</td> : null}
                <td style={{ whiteSpace: 'nowrap' }}>
                  {c.feature_season} → {c.outcome_season}
                </td>
                <td style={{ whiteSpace: 'nowrap' }}>{SELECTION_SHORT[c.selection]}</td>
                <td className="num" title={mIdx.get(c.metric)?.description}>
                  {fmt(c.metric_value, md)}
                </td>
                <td className="num">{fmt(c.forecast_without, d)}</td>
                <td className="num">{fmt(c.forecast_with, d)}</td>
                <td className="num">{fmtSigned(c.forecast_change, d)}</td>
                <td className="num">{fmt(c.observed, d)}</td>
                <td className="num">{fmtSigned(c.abs_error_change, d)}</td>
                <td>
                  <span className="chip-row" style={{ flexWrap: 'nowrap', whiteSpace: 'nowrap' }}>
                    <ResultIcon improved={c.improved} size={13} />
                    {c.improved ? 'Improved' : 'Worsened'}
                  </span>
                  <span className="sr-only"> ({t?.short} forecast)</span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function CohortSection({
  contrast,
  casebook,
  targets,
  meta,
  mIdx,
  contrastLabel,
}: {
  contrast: string;
  casebook: Casebook;
  targets: Target[];
  meta: Meta;
  mIdx: Map<string, Metric>;
  contrastLabel: string;
}) {
  const [targetId, metricId] = contrast.split(':');
  const target = targets.find((t) => t.id === targetId);
  const cohorts = casebook.cohorts.filter((c) => c.contrast === contrast);
  const unit = casebook.unit_translation.find((u) => u.contrast === contrast);
  const d = targetDigits(targetId) + 1;

  const cohortRows: ForestRow[] = cohorts.map((c) => ({
    key: c.cohort,
    label: c.cohort,
    labelText: `${c.cohort} (n = ${c.n})`,
    sub: `n = ${fmtInt(c.n)} · mean metric ${fmt(c.mean_feature, metricDigits([c.mean_feature]))}`,
    est: c.delta_rmse,
    lo: c.ci_low,
    hi: c.ci_high,
    valueText: fmtSigned(c.delta_rmse, d + 1),
    valueSub: fmtCI(c.ci_low, c.ci_high, d + 1),
    tableExtra: {
      n: fmtInt(c.n),
      share: fmtShare(c.share_improved, 1),
      change: fmtSigned(c.mean_forecast_change, d + 1),
      gap: fmtSigned(c.mean_actual_minus_base, d + 1),
    },
  }));

  return (
    <section className="section" aria-labelledby="cohort-title">
      <h2 id="cohort-title">Decile effects: {contrastLabel}</h2>
      <p className="section-intro">
        Player-seasons grouped by the metric&apos;s value. Look for cohorts where adding the metric helped and where it hurt: both happen.
      </p>
      <div className="grid-2" style={{ alignItems: 'start' }}>
        <div className="card">
          <BarList
            title="Share of player-seasons whose forecast error shrank"
            subtitle="Above 50% means the metric helped more player-seasons than it hurt in that cohort."
            rows={cohorts.map((c) => ({
              key: c.cohort,
              label: `${c.cohort} (n = ${fmtInt(c.n)})`,
              value: c.share_improved,
              valueText: fmtShare(c.share_improved, 1),
              tooltip: {
                title: c.cohort,
                rows: [
                  { key: 'Share improved', value: fmtShare(c.share_improved, 1) },
                  { key: 'Player-seasons', value: fmtInt(c.n) },
                  { key: 'Mean forecast change', value: fmtSigned(c.mean_forecast_change, d + 1) },
                ],
              },
              tableExtra: { n: fmtInt(c.n) },
            }))}
            reference={{ value: 0.5, label: '50%' }}
            ariaLabel={`Share improved by cohort for ${contrastLabel}`}
            valueLabel="Share improved"
            extraColumns={[{ key: 'n', label: 'Player-seasons', num: true }]}
          />
        </div>
        <div className="card">
          <ForestPlot
            title="ΔRMSE by cohort, in target units"
            subtitle={target ? `${target.unit}; 95% player-cluster bootstrap interval.` : undefined}
            rows={cohortRows}
            axisLabel={`ΔRMSE (${target?.short ?? targetId} units)`}
            betterLabel="more accurate with the metric"
            worseLabel="less accurate"
            digits={d + 1}
            extraColumns={[
              { key: 'n', label: 'n', num: true },
              { key: 'share', label: 'Share improved', num: true },
              { key: 'change', label: 'Mean forecast change', num: true },
              { key: 'gap', label: 'Mean actual − baseline', num: true },
            ]}
            tableCaption={`Cohort ΔRMSE for ${contrastLabel}`}
          />
        </div>
      </div>

      {unit ? (
        <div className="card" style={{ marginTop: 16 }}>
          <h3>What the change means in units</h3>
          <p className="muted small">
            Nested outer years 2021–2025, n = {fmtInt(unit.n)} player-seasons. Unit: {unit.target_unit}.
          </p>
          <div className="tile-row">
            <Tile label="RMSE, baseline → with metric" value={`${fmt(unit.rmse_base, d + 1)} → ${fmt(unit.rmse_aug, d + 1)}`} />
            <Tile label="ΔRMSE (95% CI)" value={fmtSigned(unit.delta_rmse, d + 2)} sub={fmtCI(unit.ci_low, unit.ci_high, d + 2)} />
            <Tile label="ΔRMSE, % of baseline" value={fmtPct(unit.pct)} />
            <Tile label="Translated" value={fmtSigned(unit.translated_delta, 3)} sub={unit.translation} />
            <Tile
              label="Typical forecast change"
              value={fmt(unit.median_abs_forecast_change, d + 1)}
              sub={`median absolute; 90th percentile ${fmt(unit.p90_abs_forecast_change, d + 1)}`}
            />
            <Tile label="Forecast error shrank" value={fmtShare(unit.share_improved_abs_error, 1)} sub="share of player-seasons" />
          </div>
        </div>
      ) : null}

      <div className="card" style={{ marginTop: 16 }}>
        <ResultMeta
          targetDefinition={target ? `${target.label}: ${target.definition}` : targetId}
          population={`Players meeting the study's eligibility in both seasons (outcome observed): ${target?.eligibility ?? ''}.`}
          seasons="Nested outer years 2021–2025 (feature seasons 2020–2024)."
          method={`Single-feature contrast (ridge): history baseline versus baseline + ${mIdx.get(metricId)?.description ?? metricId}.`}
          ciType={meta.ci_definition}
          tier={{ key: 'historical', label: meta.evidence_tiers.historical }}
          sources={[SOURCE_FILES.forecastChanges, SOURCE_FILES.cohortEffects, SOURCE_FILES.unitTranslation]}
          sha256={meta.sources_sha256}
        />
      </div>
    </section>
  );
}
