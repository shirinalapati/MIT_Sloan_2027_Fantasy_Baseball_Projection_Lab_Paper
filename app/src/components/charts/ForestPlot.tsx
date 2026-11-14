/**
 * Forest / interval plot. Rows are HTML (readable, wrapping labels); each interval is an SVG mark
 * on a shared horizontal scale. Left of zero is always "more accurate".
 * Color encodes where the 95% interval sits relative to zero (diverging blue / gray / red).
 */
import { Fragment, type ReactNode } from 'react';
import { fmt } from '../../lib/format';
import { ChartFigure, DataTable, PolarityLegend, type TableColumn } from './ChartFigure';
import { niceDomain, niceTicks, polarity, tickDigits, type Polarity } from './scale';
import { TooltipView, useTooltip, type TooltipContent } from './Tooltip';
import { useMeasure } from './useMeasure';

export interface ForestRow {
  key: string;
  label: ReactNode;
  labelText: string;
  sub?: ReactNode;
  est: number | null;
  lo: number | null;
  hi: number | null;
  valueText: string;
  valueSub?: string;
  group?: string;
  hollow?: boolean;
  tone?: Polarity | 'ink';
  tooltip?: TooltipContent;
  onSelect?: () => void;
  selected?: boolean;
  missingText?: string;
  tableExtra?: Record<string, string>;
}

export interface ForestPlotProps {
  title: ReactNode;
  subtitle?: ReactNode;
  rows: ForestRow[];
  axisLabel: string;
  betterLabel: string;
  worseLabel: string;
  unit?: string;
  domain?: [number, number];
  legend?: 'polarity' | 'none' | ReactNode;
  extraColumns?: Array<{ key: string; label: string; num?: boolean }>;
  tableCaption?: string;
  headingLevel?: 'h3' | 'h4';
  digits?: number;
  selectLabel?: string;
}

const PAD = 10;
const MARK_H = 26;

export function ForestPlot(p: ForestPlotProps) {
  const { ref: axisRef, width } = useMeasure<HTMLDivElement>(320);
  const tt = useTooltip();
  const values: number[] = [];
  for (const r of p.rows) {
    for (const v of [r.est, r.lo, r.hi]) if (v !== null && Number.isFinite(v)) values.push(v);
  }
  const domain = p.domain ?? niceDomain(values, { includeZero: true, pad: 0.04, count: width < 360 ? 3 : 5 });
  const ticks = niceTicks(domain[0], domain[1], width < 360 ? 3 : 5).filter((t) => t >= domain[0] - 1e-9 && t <= domain[1] + 1e-9);
  const dg = tickDigits(ticks);
  const inner = Math.max(40, width - PAD * 2);
  const x = (v: number) => PAD + ((Math.min(Math.max(v, domain[0]), domain[1]) - domain[0]) / (domain[1] - domain[0] || 1)) * inner;
  const pct = (v: number) => `${(x(v) / width) * 100}%`;
  const unit = p.unit ?? '';

  const hasInk = p.rows.some((r) => r.tone === 'ink');
  const hasHollow = p.rows.some((r) => r.hollow);
  const legend =
    p.legend === 'none' ? null : p.legend === undefined || p.legend === 'polarity' ? (
      <PolarityLegend
        inkText={hasInk ? 'Point estimate (no interval available)' : undefined}
        hollowText={hasHollow ? 'Exploratory 2026 value' : undefined}
      />
    ) : (
      p.legend
    );

  const columns: TableColumn<ForestRow>[] = [
    { key: 'label', label: 'Row', render: (r) => r.labelText },
    { key: 'est', label: `Estimate${unit ? ` (${unit})` : ''}`, num: true, render: (r) => (r.est === null ? r.missingText ?? '—' : fmt(r.est, p.digits ?? 2)) },
    { key: 'lo', label: '95% CI low', num: true, render: (r) => (r.lo === null ? '—' : fmt(r.lo, p.digits ?? 2)) },
    { key: 'hi', label: '95% CI high', num: true, render: (r) => (r.hi === null ? '—' : fmt(r.hi, p.digits ?? 2)) },
    ...(p.extraColumns ?? []).map((c) => ({
      key: c.key,
      label: c.label,
      num: c.num,
      render: (r: ForestRow) => r.tableExtra?.[c.key] ?? '—',
    })),
  ];

  let lastGroup: string | undefined;

  return (
    <ChartFigure
      title={p.title}
      subtitle={p.subtitle}
      legend={legend}
      headingLevel={p.headingLevel}
      table={<DataTable caption={p.tableCaption ?? (typeof p.title === 'string' ? p.title : 'Chart data')} columns={columns} rows={p.rows} rowKey={(r) => r.key} />}
    >
      <div className="chart-wrap" ref={tt.ref} onPointerLeave={tt.hide}>
        <div className="forest">
          {p.rows.map((r) => {
            const showGroup = r.group !== undefined && r.group !== lastGroup;
            lastGroup = r.group;
            const pol: Polarity | 'ink' = r.tone ?? polarity(r.lo, r.hi);
            const cls = pol === 'ink' ? 'mark-ink' : `mark-${pol}`;
            const tip: TooltipContent = r.tooltip ?? {
              title: r.labelText,
              rows: [
                { key: 'Estimate', value: r.est === null ? r.missingText ?? '—' : `${fmt(r.est, p.digits ?? 2)}${unit}` },
                ...(r.lo !== null && r.hi !== null ? [{ key: '95% CI', value: `${fmt(r.lo, p.digits ?? 2)} to ${fmt(r.hi, p.digits ?? 2)}${unit}` }] : []),
              ],
            };
            const outOfRange =
              r.est !== null && (r.est < domain[0] || r.est > domain[1] || (r.lo ?? r.est) < domain[0] || (r.hi ?? r.est) > domain[1]);
            return (
              <Fragment key={r.key}>
                {showGroup ? <div className="forest-group">{r.group}</div> : null}
                <div className={`forest-row${r.selected ? ' forest-row-selected' : ''}`}>
                  <div className="forest-label">
                    {r.onSelect ? (
                      <button
                        type="button"
                        className="forest-rowbtn"
                        aria-pressed={!!r.selected}
                        aria-label={p.selectLabel ? `${p.selectLabel}: ${r.labelText}` : undefined}
                        onClick={r.onSelect}
                        onFocus={(e) => tt.showAtElement(e.currentTarget, tip)}
                        onBlur={tt.hide}
                      >
                        <span className="lbl">{r.label}</span>
                        {r.sub ? <span className="sub">{r.sub}</span> : null}
                      </button>
                    ) : (
                      <>
                        {r.label}
                        {r.sub ? <span className="sub">{r.sub}</span> : null}
                      </>
                    )}
                  </div>
                  <div
                    className={`forest-plot forest-hit${r.onSelect ? ' selectable' : ''}`}
                    style={{ position: 'relative' }}
                    onPointerMove={(e) => tt.showAtEvent(e, tip)}
                    onClick={r.onSelect}
                    tabIndex={r.onSelect ? -1 : 0}
                    role="img"
                    aria-label={`${r.labelText}: ${r.valueText}${r.valueSub ? ` ${r.valueSub}` : ''}`}
                    onFocus={(e) => tt.showAtElement(e.currentTarget, tip)}
                    onBlur={tt.hide}
                  >
                    {ticks.map((t) => (
                      <span
                        key={t}
                        aria-hidden="true"
                        style={{
                          position: 'absolute',
                          top: 0,
                          bottom: 0,
                          left: pct(t),
                          width: 1,
                          background: t === 0 ? 'var(--zero)' : 'var(--grid)',
                        }}
                      />
                    ))}
                    {ticks.includes(0) ? null : (
                      <span aria-hidden="true" style={{ position: 'absolute', top: 0, bottom: 0, left: pct(0), width: 1, background: 'var(--zero)' }} />
                    )}
                    <svg
                      viewBox={`0 0 ${width} ${MARK_H}`}
                      width="100%"
                      height={MARK_H}
                      preserveAspectRatio="none"
                      aria-hidden="true"
                      focusable="false"
                      style={{ position: 'relative', alignSelf: 'center', overflow: 'visible' }}
                    >
                      {r.est === null ? (
                        <text x={x(0) + 6} y={MARK_H / 2 + 4} style={{ fontSize: 11 }}>
                          {r.missingText ?? 'no estimate'}
                        </text>
                      ) : (
                        <>
                          {r.lo !== null && r.hi !== null ? (
                            <line x1={x(r.lo)} x2={x(r.hi)} y1={MARK_H / 2} y2={MARK_H / 2} className={`ci-line ${cls}`} />
                          ) : null}
                          <circle cx={x(r.est)} cy={MARK_H / 2} r={4.5} className={`${r.hollow ? 'pt-hollow' : 'pt'} ${cls}`} />
                          {outOfRange ? (
                            <text x={r.est > domain[1] ? width - PAD : PAD} y={MARK_H / 2 - 7} textAnchor={r.est > domain[1] ? 'end' : 'start'} style={{ fontSize: 10 }}>
                              off scale
                            </text>
                          ) : null}
                        </>
                      )}
                    </svg>
                  </div>
                  <div className="forest-value">
                    <strong>{r.valueText}</strong>
                    {r.valueSub ? <span className="sub">{r.valueSub}</span> : null}
                  </div>
                </div>
              </Fragment>
            );
          })}
          <div ref={axisRef} className="forest-axis" aria-hidden="true">
            {ticks.map((t) => (
              <span
                key={t}
                className="forest-axis-label"
                style={{
                  position: 'absolute',
                  top: 3,
                  left: pct(t),
                  transform: 'translateX(-50%)',
                  fontVariantNumeric: 'tabular-nums',
                  whiteSpace: 'nowrap',
                }}
              >
                {fmt(t, dg)}
                {unit}
              </span>
            ))}
          </div>
          <div className="forest-dir">
            <div className="direction-labels">
              <span>← {p.betterLabel}</span>
              <span>{p.worseLabel} →</span>
            </div>
            <div className="forest-axis-label" style={{ textAlign: 'center' }}>
              {p.axisLabel}
            </div>
          </div>
        </div>
        <TooltipView tip={tt.tip} containerWidth={tt.ref.current?.getBoundingClientRect().width ?? width} />
      </div>
    </ChartFigure>
  );
}
