import { useMemo, useState } from 'react';
import { useData } from '../data/load';
import type { Comparison, Meta, Metric, ModelComparisons, Target } from '../data/schemas';
import { SOURCE_FILES } from '../data/constants';
import { setParams, useRoute } from '../router';
import { Callout, Gate, PageHead } from '../components/Page';
import { Segmented } from '../components/Segmented';
import { ResultMeta } from '../components/ResultMeta';
import { ForestPlot, type ForestRow } from '../components/charts/ForestPlot';
import { LineChart, type LineSeries } from '../components/charts/LineChart';
import { NESTED_SAMPLE, SAMPLE_2026, comparisonsFor, findComparison, metricIndex, perYearFor } from '../lib/lookup';
import { COMPARISON_GROUP_INFO, ESTIMATOR_INFO, MODEL_SET_INFO, comparisonGroup, modelLabel, type ComparisonGroup } from '../lib/labels';
import { comparisonSentence } from '../lib/wording';
import { digitsFor, fmtCI, fmtInt, fmtPct } from '../lib/format';

const DEFAULT_TARGET = 'pitching_fip';
const GROUP_ORDER: ComparisonGroup[] = ['admission', 'kitchen', 'lookahead', 'screens', 'estimators', 'single'];
const ESTIMATORS = ['ridge', 'ridge_tuned', 'enet', 'lgbm', 'rf'] as const;
type Estimator = (typeof ESTIMATORS)[number];

/** Fixed color per feature set (color follows the entity, never its rank). B0 is the neutral reference. */
const SET_COLORS: Record<string, string> = {
  B0: 'var(--mark-ink)',
  ADM: 'var(--s1)',
  KS: 'var(--s2)',
  FIX: 'var(--s3)',
  UNI: 'var(--s4)',
  FAM: 'var(--s5)',
  CORR: 'var(--s6)',
};
const SET_ORDER = ['B0', 'ADM', 'KS', 'FIX', 'UNI', 'FAM', 'CORR'];

export default function Models() {
  const state = useData('meta', 'targets', 'metrics', 'model_comparisons');
  return (
    <>
      <PageHead eyebrow="Historical research evidence" title="Model Comparison">
        <p className="lede">
          Does choosing features target by target beat simply using all of them? Within each target, every model below is scored on the same
          player-season rows across nested outer years 2021–2025, where feature selection used only earlier seasons. A separate 2026 check follows.
        </p>
      </PageHead>
      <Gate state={state} what="model comparisons">
        {(d) => <ModelsBody {...d} />}
      </Gate>
    </>
  );
}

function rowFor(c: Comparison, mIdx: Map<string, Metric>, opts: { group?: string; hollow?: boolean } = {}): ForestRow {
  const years = c.years_a_better !== undefined && c.n_years !== undefined ? `${c.years_a_better}/${c.n_years} years first model better` : undefined;
  const identical = c.ci_low_pct === null || c.ci_high_pct === null;
  return {
    key: `${c.comparison}|${c.cohort ?? ''}|${c.model_a}|${c.model_b}`,
    group: opts.group,
    label: c.comparison,
    labelText: `${c.comparison}${c.cohort ? `, ${c.cohort}` : ''}`,
    sub: `${modelLabel(c.model_a, mIdx)} vs ${modelLabel(c.model_b, mIdx)}`,
    est: c.delta_pct,
    lo: c.ci_low_pct,
    hi: c.ci_high_pct,
    hollow: opts.hollow,
    valueText: fmtPct(c.delta_pct),
    valueSub: identical ? 'identical feature sets' : `${fmtCI(c.ci_low_pct, c.ci_high_pct)}${years ? ` · ${years.split(' ')[0]} yrs` : ''}`,
    tooltip: {
      title: c.comparison,
      rows: [
        { key: 'ΔRMSE (first − second)', value: fmtPct(c.delta_pct) },
        { key: '95% CI', value: identical ? 'none (identical forecasts)' : fmtCI(c.ci_low_pct, c.ci_high_pct) },
        ...(years ? [{ key: 'Years', value: years }] : []),
        { key: 'Rows / players', value: `${fmtInt(c.n_rows)} / ${fmtInt(c.n_players)}` },
      ],
    },
    tableExtra: {
      a: modelLabel(c.model_a, mIdx),
      b: modelLabel(c.model_b, mIdx),
      years: years ?? '—',
      n: fmtInt(c.n_rows),
    },
  };
}

function ModelsBody({ meta, targets, metrics, model_comparisons }: { meta: Meta; targets: Target[]; metrics: Metric[]; model_comparisons: ModelComparisons }) {
  const route = useRoute();
  const mIdx = useMemo(() => metricIndex(metrics), [metrics]);
  const tParam = route.params.get('target');
  const target = targets.find((t) => t.id === tParam) ?? targets.find((t) => t.id === DEFAULT_TARGET) ?? targets[0];
  const eParam = route.params.get('est') as Estimator | null;
  const estimator: Estimator = eParam && (ESTIMATORS as readonly string[]).includes(eParam) ? eParam : 'ridge';
  const [hidden, setHidden] = useState<string[]>(['UNI', 'FAM', 'CORR']);

  const nested = comparisonsFor(model_comparisons.comparisons, target.id, NESTED_SAMPLE);
  const rows2026 = comparisonsFor(model_comparisons.comparisons, target.id, SAMPLE_2026);
  const nestedRows: ForestRow[] = GROUP_ORDER.flatMap((g) =>
    nested.filter((c) => comparisonGroup(c) === g).map((c) => rowFor(c, mIdx, { group: COMPARISON_GROUP_INFO[g].title })),
  );
  const cohorts = [...new Set(rows2026.map((c) => c.cohort ?? ''))];
  const rows26: ForestRow[] = cohorts.flatMap((co) =>
    rows2026.filter((c) => (c.cohort ?? '') === co).map((c) => rowFor(c, mIdx, { group: `2026 · ${co}`, hollow: true })),
  );

  const adm = findComparison(model_comparisons.comparisons, target.id, 'ADM vs B0 (selection policy lift)');
  const ks = findComparison(model_comparisons.comparisons, target.id, 'KS vs ADM (kitchen minus selective)');
  const en = findComparison(model_comparisons.comparisons, target.id, 'EN-KS vs ADM (tuned elastic net on kitchen)');
  const nRows = nested[0]?.n_rows;

  const perYear = perYearFor(model_comparisons.per_year, target.id);
  const series: LineSeries[] = SET_ORDER.map((set) => {
    const id = `${set}|${estimator}`;
    const pts = perYear.filter((p) => p.model_id === id).map((p) => ({ x: p.outer_year, y: p.wrmse }));
    return { id, label: MODEL_SET_INFO[set]?.name ?? set, color: SET_COLORS[set], points: pts };
  }).filter((s) => s.points.length > 0);
  const visible = series.map((s) => s.id).filter((id) => !hidden.includes(id.split('|')[0]));
  const yDigits = digitsFor(perYear.map((p) => p.wrmse)) + 1;

  return (
    <>
      <div className="card" role="search" aria-label="Choose a target">
        <Segmented
          legend="Target (next season)"
          value={target.id}
          onChange={(v) => setParams({ target: v })}
          options={targets.map((t) => ({ value: t.id, label: t.short, title: t.label }))}
        />
      </div>

      <section className="section" aria-labelledby="models-nested" style={{ marginTop: 20 }}>
        <h2 id="models-nested">{target.label}: nested outer years 2021–2025</h2>
        <div className="prose">
          {adm ? <p>{comparisonSentence(adm.delta_pct, adm.ci_low_pct, adm.ci_high_pct, 'the nested-admitted set (ADM)', 'the history baseline (B0)')}</p> : null}
          {ks ? <p>{comparisonSentence(ks.delta_pct, ks.ci_low_pct, ks.ci_high_pct, 'the all-feature ridge (KS)', 'the admitted set (ADM)')}</p> : null}
          {en ? <p>{comparisonSentence(en.delta_pct, en.ci_low_pct, en.ci_high_pct, 'a tuned elastic net on all features', 'the admitted set (ADM)')}</p> : null}
        </div>
        <div className="card">
          <ForestPlot
            title="ΔRMSE %, first-named model minus second-named model"
            subtitle={`Identical rows within the target (n = ${nRows ? fmtInt(nRows) : '—'} player-seasons). Negative = the first-named model was more accurate.`}
            rows={nestedRows}
            axisLabel="ΔRMSE, % of the second model's RMSE"
            betterLabel="first-named model more accurate"
            worseLabel="second-named more accurate"
            unit="%"
            extraColumns={[
              { key: 'a', label: 'First model' },
              { key: 'b', label: 'Second model' },
              { key: 'years', label: 'Years first better' },
              { key: 'n', label: 'Rows', num: true },
            ]}
            tableCaption={`Nested comparisons for ${target.label}`}
          />
          <ul className="muted small" style={{ marginTop: 12, paddingLeft: '1.1rem' }}>
            {GROUP_ORDER.filter((g) => nested.some((c) => comparisonGroup(c) === g)).map((g) => (
              <li key={g}>
                <strong>{COMPARISON_GROUP_INFO[g].title}:</strong> {COMPARISON_GROUP_INFO[g].note}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="section" aria-labelledby="models-year">
        <h2 id="models-year">Accuracy by outer year</h2>
        <p className="section-intro">Weighted RMSE of each feature set, per outer year, for one estimator at a time. Lower is more accurate.</p>
        <div className="card">
          <Segmented<Estimator>
            legend="Estimator"
            value={estimator}
            onChange={(v) => setParams({ est: v === 'ridge' ? null : v })}
            options={ESTIMATORS.map((e) => ({ value: e, label: ESTIMATOR_INFO[e].name }))}
          />
          <div style={{ marginTop: 12 }}>
            <LineChart
              title={`${target.short}: weighted RMSE by outer year (${ESTIMATOR_INFO[estimator].name})`}
              subtitle="Press a legend item to show or hide a feature set. Hover or focus the chart (←/→ keys) to read every series for one year."
              series={series}
              visible={visible}
              onToggle={(id) => {
                const set = id.split('|')[0];
                setHidden((h) => (h.includes(set) ? h.filter((x) => x !== set) : visible.length > 1 ? [...h, set] : h));
              }}
              yLabel={`Weighted RMSE (${target.unit}) · ↓ lower is more accurate`}
              xLabel="Outer year"
              valueDigits={yDigits}
              ariaLabel={`Line chart of weighted RMSE by outer year for ${target.label}, ${ESTIMATOR_INFO[estimator].name} estimator`}
              note={estimator !== 'ridge' ? 'Only B0, ADM and KS were refit with this estimator.' : undefined}
            />
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="models-2026">
        <h2 id="models-2026">2026 check</h2>
        <Callout kind="caution" title="Directional / exploratory">
          <p>
            {meta.evidence_tiers['historical-2026']}. Forecasts were frozen in the workflow before the 2026 tables were downloaded, but the season had
            already been played. Retrospective = the canonical eligibility rule; prospective = 2025 eligibility with any 2026 outcome. Treat intervals
            that include zero as directional only.
          </p>
        </Callout>
        <div className="card">
          <ForestPlot
            title="2026 ΔRMSE %, first-named model minus second-named model"
            subtitle="One season; hollow points mark exploratory values."
            rows={rows26}
            axisLabel="ΔRMSE, % of the second model's RMSE"
            betterLabel="first-named model more accurate"
            worseLabel="second-named more accurate"
            unit="%"
            extraColumns={[
              { key: 'a', label: 'First model' },
              { key: 'b', label: 'Second model' },
              { key: 'n', label: 'Rows', num: true },
            ]}
            tableCaption={`2026 comparisons for ${target.label}`}
          />
        </div>
      </section>

      <section className="section" aria-labelledby="models-defs">
        <h2 id="models-defs">What the models are</h2>
        <div className="grid-2">
          <div className="card">
            <h3>Feature sets</h3>
            <dl className="meta">
              {SET_ORDER.map((s) => (
                <Def key={s} term={MODEL_SET_INFO[s].name} text={MODEL_SET_INFO[s].definition} />
              ))}
            </dl>
            <p className="muted small" style={{ marginTop: 10 }}>
              History baseline for {target.short}: {target.baseline}.
            </p>
          </div>
          <div className="card">
            <h3>Estimators</h3>
            <dl className="meta">
              {ESTIMATORS.map((e) => (
                <Def key={e} term={ESTIMATOR_INFO[e].name} text={ESTIMATOR_INFO[e].definition} />
              ))}
            </dl>
            <p className="muted small" style={{ marginTop: 10 }}>
              Model ids in the data look like <code>KS|enet</code>: feature set, then estimator.
            </p>
          </div>
        </div>
        <div className="card" style={{ marginTop: 16 }}>
          <ResultMeta
            targetDefinition={`${target.label}: ${target.definition}`}
            population={`${target.eligibility}; rows identical across the models compared within a target.`}
            seasons="Nested outer years 2021–2025; 2026 frozen-in-workflow check shown separately."
            method="Each comparison fits both models on the same training seasons and scores them on the same outer-year rows (weighted RMSE)."
            ciType={meta.ci_definition}
            tier={{ key: 'historical', label: `${meta.evidence_tiers.historical} (2026 rows: ${meta.evidence_tiers['historical-2026']})` }}
            sources={[SOURCE_FILES.comparisonsNested, SOURCE_FILES.perYearNested, SOURCE_FILES.comparisons2026]}
            sha256={meta.sources_sha256}
          />
        </div>
      </section>
    </>
  );
}

function Def({ term, text }: { term: string; text: string }) {
  return (
    <>
      <dt>{term}</dt>
      <dd>{text}</dd>
    </>
  );
}
