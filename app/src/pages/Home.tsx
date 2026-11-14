import { useData } from '../data/load';
import type { Flagship } from '../data/schemas';
import { hrefFor } from '../router';
import { Callout, Gate, PageHead } from '../components/Page';
import { ForestPlot, type ForestRow } from '../components/charts/ForestPlot';
import { parseCiString } from '../data/validate';
import { fmtCI, fmtP, fmtPct } from '../lib/format';
import { FlaskIcon, InfoIcon } from '../components/Icons';
import { ResultMeta } from '../components/ResultMeta';
import { SOURCE_FILES } from '../data/constants';

const TOOLS = [
  {
    path: '/explorer',
    title: 'Metric → Target Explorer',
    text: 'Pick a metric and a target. See the verdict, why it was assigned, the fold-by-fold evidence, and how the same metric fared for other targets.',
  },
  {
    path: '/fantasy',
    title: 'Fantasy Linkage Explorer',
    text: 'Do better forecasts of wOBA, FIP, baserunning, fielding or WAR carry information about R, HR, SB, ERA, WHIP and the rest? Gains, nulls and harms side by side.',
  },
  {
    path: '/casebook',
    title: 'Player Casebook',
    text: 'Curated player-seasons where adding one metric moved a forecast, including the cases where it made the forecast worse.',
  },
  {
    path: '/models',
    title: 'Model Comparison',
    text: 'Selected features vs history baseline, kitchen-sink ridge, elastic net, LightGBM and random forest on identical rows.',
  },
  {
    path: '/value-lab',
    title: 'Fantasy Value Lab (illustrative)',
    text: 'A calculator for 5×5 and points arithmetic with ratio categories built from components. Not a research finding.',
  },
  {
    path: '/methods',
    title: 'Methods, Limits & Sources',
    text: 'The original abstract and what changed, target definitions, verdict rules, caveats, data rights and file checksums.',
  },
];

const DESIGNS: Array<{ col: keyof Flagship; label: string; hollow?: boolean }> = [
  { col: '2019–25 pooled, % [cluster CI]', label: 'Pooled 2019–25 (7 folds)' },
  { col: 'Nested 2021–25, %', label: 'Nested 2021–25' },
  { col: '2026 holdout, %', label: '2026 check', hollow: true },
];

function flagshipRows(flagships: Flagship[]): ForestRow[] {
  const rows: ForestRow[] = [];
  for (const f of flagships) {
    for (const d of DESIGNS) {
      const ci = parseCiString(String(f[d.col]));
      if (!ci) continue;
      const label = d.col === '2026 holdout, %' ? `${d.label} (n = ${f['2026 n']})` : d.label;
      rows.push({
        key: `${f.Hypothesis}-${d.col}`,
        group: `${f.Hypothesis} · ${f.Contrast}`,
        label,
        labelText: `${f.Hypothesis} ${f.Contrast}, ${label}`,
        est: ci.est,
        lo: ci.lo,
        hi: ci.hi,
        hollow: d.hollow,
        valueText: fmtPct(ci.est),
        valueSub: fmtCI(ci.lo, ci.hi),
        tableExtra: {
          holm: fmtP(f['Holm-adjusted p (H1–H6)']),
          bh: fmtP(f['BH q (all 208)']),
        },
      });
    }
  }
  return rows;
}

export default function Home() {
  const state = useData('meta', 'targets', 'metrics', 'flagships');
  return (
    <>
      <PageHead eyebrow="Paper ID 18 · MIT Sloan Sports Analytics Conference 2027 · Baseball track" title="Fantasy Projection Lab">
        <p className="lede">Which public baseball metrics improve next-season forecasts, and does that reach your fantasy categories?</p>
      </PageHead>
      <Gate state={state} what="study overview">
        {({ meta, targets, metrics, flagships }) => {
          const nEval = targets.reduce((s, t) => s + t.n_candidates, 0);
          const sprintBr = flagships.find((f) => f.Hypothesis === 'H5');
          const sprintWoba = flagships.find((f) => f.Hypothesis === 'H7');
          const br = sprintBr ? parseCiString(sprintBr['2019–25 pooled, % [cluster CI]']) : null;
          const wo = sprintWoba ? parseCiString(sprintWoba['2019–25 pooled, % [cluster CI]']) : null;
          return (
            <>
              <section className="section" style={{ marginTop: 8 }} aria-labelledby="asks">
                <h2 id="asks">What the study asks</h2>
                <div className="prose">
                  <p style={{ fontSize: '1.12rem', fontWeight: 600 }}>
                    A metric that describes a player is not automatically one that improves next year&apos;s forecast.
                  </p>
                  <p>
                    The paper, <em>{meta.paper.title}</em>, tested {metrics.length} public metrics one target at a time: does adding the metric
                    to a strong, history-aware baseline make next-season forecasts more accurate on seasons the model has not seen? That is{' '}
                    {nEval} metric × target evaluations across {targets.length} targets ({targets.map((t) => t.short).join(', ')}).
                  </p>
                  {br && wo ? (
                    <p>
                      The answer depends on the job. Historically, adding Statcast sprint speed improved next-season baserunning forecasts beyond a
                      history baseline (pooled 2019–25 ΔRMSE {fmtPct(br.est)}, 95% CI {fmtCI(br.lo, br.hi)}). It was not useful for wOBA (
                      {fmtPct(wo.est)}, {fmtCI(wo.lo, wo.hi)}).
                    </p>
                  ) : null}
                  <p>
                    None of the six targets is a fantasy category, so a separate, exploratory bridge asks whether those forecasts carry information
                    about R, HR, SB, ERA, WHIP and the other categories you actually score.
                  </p>
                </div>
              </section>

              <section className="section" aria-labelledby="tiers">
                <h2 id="tiers">Three kinds of evidence, labelled everywhere</h2>
                <p className="section-intro">Every result card in the lab carries one of these labels.</p>
                <div className="grid-3">
                  <div className="card tier-card">
                    <h3>
                      <InfoIcon /> {meta.evidence_tiers.historical}
                    </h3>
                    <p className="muted small">
                      Out-of-time results from 2015–2025 data: expanding-window folds with outcomes 2019–2025, and nested windows 2021–2025 where
                      feature selection used only earlier seasons. The separate 2026 check is labelled “{meta.evidence_tiers['historical-2026']}”.
                    </p>
                  </div>
                  <div className="card tier-card">
                    <h3>
                      <InfoIcon /> {meta.evidence_tiers.exploratory_fantasy}
                    </h3>
                    <p className="muted small">
                      Whether forecasts of the six targets add information about next-season fantasy outcomes beyond a fantasy-history baseline. The
                      protocol was written before any fantasy model was fit, but the seasons are not new.
                    </p>
                  </div>
                  <div className="card tier-card">
                    <h3>
                      <FlaskIcon /> {meta.evidence_tiers.illustrative}
                    </h3>
                    <p className="muted small">
                      Calculators and what-if backtests that show arithmetic or a hypothetical policy. They are not research findings.
                    </p>
                  </div>
                </div>
              </section>

              <section className="section" aria-labelledby="tools">
                <h2 id="tools">Tools</h2>
                <div className="tool-grid">
                  {TOOLS.map((t) => (
                    <a key={t.path} className="tool-card" href={hrefFor(t.path)}>
                      <h3>{t.title}</h3>
                      <p>{t.text}</p>
                    </a>
                  ))}
                </div>
              </section>

              <section className="section" aria-labelledby="headline">
                <h2 id="headline">Headline contrasts across three evaluation designs</h2>
                <p className="section-intro">
                  Seven pre-specified single-metric contrasts. Each row is the change in next-season forecast error (RMSE, %) from adding the
                  metric to the history baseline, with its 95% player-cluster bootstrap interval. The 2026 check is one season that had already
                  been played when forecasts were frozen.
                </p>
                <div className="card">
                  <ForestPlot
                    title="ΔRMSE % from adding one metric, by design"
                    subtitle={`Source: ${SOURCE_FILES.flagships} · ${meta.evidence_tiers.historical}`}
                    rows={flagshipRows(flagships)}
                    axisLabel="ΔRMSE, % of baseline RMSE"
                    betterLabel="forecast more accurate"
                    worseLabel="less accurate"
                    unit="%"
                    extraColumns={[
                      { key: 'holm', label: 'Holm-adjusted p (H1–H6)', num: true },
                      { key: 'bh', label: 'BH q (all 208)', num: true },
                    ]}
                    tableCaption="Headline contrasts: estimate and 95% CI by design"
                  />
                  <ResultMeta
                    targetDefinition={`Each contrast uses its own target: ${targets.map((t) => t.label).join('; ')}. Definitions are on the Methods page.`}
                    population="Each target's own eligibility rule in both seasons (see Methods); 2026 n is shown per row."
                    seasons="Pooled 2019–25 (7 expanding folds, outcomes 2019–2025); nested outer years 2021–25; 2026 frozen-in-workflow check."
                    method="Ridge regression: history baseline versus baseline + one metric, scored out of time on identical rows."
                    ciType={meta.ci_definition}
                    tier={{ key: 'historical', label: `${meta.evidence_tiers.historical} (2026 rows: ${meta.evidence_tiers['historical-2026']})` }}
                    sources={[SOURCE_FILES.flagships]}
                    sha256={meta.sources_sha256}
                    extra={[['Multiplicity', 'Holm-adjusted p within H1–H6 and BH q across all 208 evaluations are in the data table.']]}
                  />
                </div>
                <Callout kind="note" title="Read this first">
                  <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>
                    <li>No 2027 player forecasts are published here: 2026 feature panels were not built.</li>
                    <li>wOBA, FIP and WAR are not scored in standard 5×5 or points leagues.</li>
                    <li>
                      The 2026 check is retrospective (the season had been played); several 2026 intervals include zero, so those results are
                      directional.
                    </li>
                  </ul>
                  <p style={{ marginTop: 8 }}>
                    <a href={hrefFor('/methods')}>All caveats, verdict rules and sources</a>
                  </p>
                </Callout>
              </section>
            </>
          );
        }}
      </Gate>
    </>
  );
}
