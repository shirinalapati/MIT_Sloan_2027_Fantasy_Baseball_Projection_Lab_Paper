/**
 * Target-forecast × fantasy-category matrix. Each cell shows ΔRMSE%, a verdict icon, and a mini
 * interval glyph on a scale shared by the whole matrix. Nulls and harms are drawn exactly like gains.
 */
import type { FantasyResult } from '../../data/schemas';
import { fmtCI, fmtP, fmtPct } from '../../lib/format';
import { FANTASY_VERDICT_INFO } from '../../lib/labels';
import { FantasyIcon } from '../Icons';
import { ChartFigure, DataTable, PolarityLegend, type TableColumn } from './ChartFigure';
import { niceDomain, polarity } from './scale';

export interface MatrixAxis {
  key: string;
  label: string;
}

const GW = 64;
const GH = 12;

function Glyph({ r, domain }: { r: FantasyResult; domain: [number, number] }) {
  const x = (v: number) => 3 + ((Math.min(Math.max(v, domain[0]), domain[1]) - domain[0]) / (domain[1] - domain[0])) * (GW - 6);
  const cls = `mark-${polarity(r.ci_low_pct, r.ci_high_pct)}`;
  const clippedLo = r.ci_low_pct < domain[0];
  const clippedHi = r.ci_high_pct > domain[1];
  return (
    <svg className="glyph" viewBox={`0 0 ${GW} ${GH}`} aria-hidden="true" focusable="false">
      <line x1={x(0)} x2={x(0)} y1={0} y2={GH} className="zero-line" style={{ stroke: 'var(--zero)' }} />
      <line x1={x(r.ci_low_pct)} x2={x(r.ci_high_pct)} y1={GH / 2} y2={GH / 2} className={`ci-line ${cls}`} />
      {clippedLo ? <path d={`M1,${GH / 2} l4,-3 v6 z`} className={cls} /> : null}
      {clippedHi ? <path d={`M${GW - 1},${GH / 2} l-4,-3 v6 z`} className={cls} /> : null}
      <circle cx={x(r.delta_pct)} cy={GH / 2} r={3.2} className={`pt ${cls}`} style={{ strokeWidth: 1.5 }} />
    </svg>
  );
}

export function FantasyMatrix({
  title,
  subtitle,
  rows,
  cols,
  results,
  selected,
  onSelect,
  rowHeader,
}: {
  title: string;
  subtitle?: string;
  rows: MatrixAxis[];
  cols: MatrixAxis[];
  results: FantasyResult[];
  selected?: { target: string; outcome: string };
  onSelect: (target: string, outcome: string) => void;
  rowHeader: string;
}) {
  const find = (t: string, o: string) => results.find((r) => r.target === t && r.outcome === o);
  const all = rows.flatMap((r) => cols.map((c) => find(r.key, c.key))).filter((x): x is FantasyResult => !!x);
  const raw = niceDomain(all.flatMap((r) => [r.ci_low_pct, r.ci_high_pct]), { includeZero: true, pad: 0.02, count: 4 });
  const domain: [number, number] = [Math.max(raw[0], -6), Math.min(raw[1], 6)];

  const tableRows = all;
  const columns: TableColumn<FantasyResult>[] = [
    { key: 'pair', label: 'Forecast → outcome', render: (r) => `${rows.find((x) => x.key === r.target)?.label ?? r.target} → ${cols.find((x) => x.key === r.outcome)?.label ?? r.outcome}` },
    { key: 'd', label: 'ΔRMSE %', num: true, render: (r) => fmtPct(r.delta_pct) },
    { key: 'ci', label: '95% CI', num: true, render: (r) => fmtCI(r.ci_low_pct, r.ci_high_pct) },
    { key: 'p', label: 'Adjusted p', num: true, render: (r) => fmtP(r.p_adjusted) },
    { key: 'v', label: 'Verdict', render: (r) => FANTASY_VERDICT_INFO[r.verdict].label },
  ];

  return (
    <ChartFigure
      title={title}
      subtitle={subtitle}
      legend={
        <>
          <PolarityLegend betterText="Interval below 0: augmented more accurate" worseText="Interval above 0: augmented less accurate" />
          <ul className="legend" aria-label="Verdict icons">
            {(['gain', 'partial', 'null', 'harm', 'directional'] as const).map((tone) => {
              const label = Object.values(FANTASY_VERDICT_INFO).find((v) => v.tone === tone)?.label ?? tone;
              return (
                <li key={tone}>
                  <FantasyIcon tone={tone} size={13} />
                  {label}
                </li>
              );
            })}
            <li>
              <span style={{ display: 'inline-block', width: 16, height: 12, border: '2px solid var(--border-strong)', borderRadius: 3 }} aria-hidden="true" />
              Thick border: pre-specified primary linkage
            </li>
          </ul>
        </>
      }
      table={<DataTable caption={`${title}: all cells`} columns={columns} rows={tableRows} rowKey={(r) => `${r.target}|${r.outcome}`} />}
    >
      <div className="matrix-wrap" role="region" aria-label={`${title} (scrolls horizontally on small screens)`} tabIndex={0}>
        <table className="matrix">
          <caption className="sr-only">{title}</caption>
          <thead>
            <tr>
              <th scope="col">{rowHeader}</th>
              {cols.map((c) => (
                <th key={c.key} scope="col" style={{ textAlign: 'center' }}>
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.key}>
                <th scope="row">{row.label}</th>
                {cols.map((c) => {
                  const r = find(row.key, c.key);
                  if (!r) {
                    return (
                      <td key={c.key} className="matrix-empty">
                        <span aria-hidden="true">—</span>
                        <span className="sr-only">not tested</span>
                      </td>
                    );
                  }
                  const info = FANTASY_VERDICT_INFO[r.verdict];
                  const isSel = selected?.target === r.target && selected?.outcome === r.outcome;
                  return (
                    <td key={c.key}>
                      <button
                        type="button"
                        className={`matrix-cell${r.family === 'primary' ? ' primary' : ''}`}
                        aria-pressed={isSel}
                        aria-label={`${row.label} → ${c.label}: ΔRMSE ${fmtPct(r.delta_pct)}, 95% CI ${fmtCI(r.ci_low_pct, r.ci_high_pct)}, ${info.label}${r.family === 'primary' ? ', primary linkage' : ''}`}
                        title={`${info.label} · 95% CI ${fmtCI(r.ci_low_pct, r.ci_high_pct)}`}
                        onClick={() => onSelect(r.target, r.outcome)}
                      >
                        <span className="mv">
                          <FantasyIcon tone={info.tone} size={12} />
                          {fmtPct(r.delta_pct, 1)}
                        </span>
                        <Glyph r={r} domain={domain} />
                      </button>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted small" style={{ marginTop: 6 }}>
        Glyph scale: {fmtPct(domain[0], 0)} to {fmtPct(domain[1], 0)} ΔRMSE; the vertical tick is zero; ← left of zero = augmented model more accurate.
        {raw[0] < domain[0] || raw[1] > domain[1] ? ' Arrowheads mark intervals that run past the scale.' : ''}
      </p>
    </ChartFigure>
  );
}
