/** Horizontal bars (one series): thin bars, 4px rounded data end, square at the baseline, value at the tip. */
import type { ReactNode } from 'react';
import { ChartFigure, DataTable, type TableColumn } from './ChartFigure';
import { TooltipView, useTooltip, type TooltipContent } from './Tooltip';
import { useMeasure } from './useMeasure';

export interface BarRow {
  key: string;
  label: string;
  value: number; // 0..max
  valueText: string;
  tooltip: TooltipContent;
  tableExtra?: Record<string, string>;
}

function barPath(x0: number, y: number, w: number, h: number, r: number): string {
  const rr = Math.min(r, w, h / 2);
  if (w <= 0) return '';
  return `M${x0},${y} H${x0 + w - rr} Q${x0 + w},${y} ${x0 + w},${y + rr} V${y + h - rr} Q${x0 + w},${y + h} ${x0 + w - rr},${y + h} H${x0} Z`;
}

export function BarList({
  title,
  subtitle,
  rows,
  max = 1,
  reference,
  ariaLabel,
  valueLabel,
  extraColumns,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  rows: BarRow[];
  max?: number;
  reference?: { value: number; label: string };
  ariaLabel: string;
  valueLabel: string;
  extraColumns?: Array<{ key: string; label: string; num?: boolean }>;
}) {
  const { ref, width } = useMeasure<HTMLDivElement>(480);
  const tt = useTooltip();
  // Meter-list layout: the name sits on its own line above each bar, so labels never truncate.
  const valueW = 60;
  const barH = 16;
  const labelH = 18;
  const rowH = labelH + barH + 14;
  const top = reference ? 18 : 4;
  const plotW = Math.max(40, width - valueW);
  const height = top + rows.length * rowH;
  const x = (v: number) => (Math.max(0, Math.min(v, max)) / max) * plotW;

  const columns: TableColumn<BarRow>[] = [
    { key: 'label', label: 'Group', render: (r) => r.label },
    { key: 'value', label: valueLabel, num: true, render: (r) => r.valueText },
    ...(extraColumns ?? []).map((c) => ({ key: c.key, label: c.label, num: c.num, render: (r: BarRow) => r.tableExtra?.[c.key] ?? '—' })),
  ];

  return (
    <ChartFigure title={title} subtitle={subtitle} table={<DataTable caption={ariaLabel} columns={columns} rows={rows} rowKey={(r) => r.key} />}>
      <div className="chart-wrap" ref={tt.ref} onPointerLeave={tt.hide}>
        <div ref={ref} style={{ width: '100%' }}>
          <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel} style={{ display: 'block' }}>
            {reference ? (
              <g>
                <line x1={x(reference.value)} x2={x(reference.value)} y1={top - 4} y2={height} className="zero-line" />
                <text x={x(reference.value)} y={11} textAnchor="middle" style={{ fontSize: 11 }}>
                  {reference.label}
                </text>
              </g>
            ) : null}
            {rows.map((r, i) => {
              const y0 = top + i * rowH;
              const barY = y0 + labelH + 2;
              const w = x(r.value);
              return (
                <g
                  key={r.key}
                  tabIndex={0}
                  role="img"
                  aria-label={`${r.label}: ${r.valueText}`}
                  onPointerMove={(e) => tt.showAtEvent(e, r.tooltip)}
                  onFocus={(e) => tt.showAtElement(e.currentTarget, r.tooltip)}
                  onBlur={tt.hide}
                >
                  <rect x={0} y={y0} width={width} height={rowH} fill="transparent" />
                  <text x={0} y={y0 + 13} style={{ fill: 'var(--text-1)', fontSize: 12.5 }}>
                    {r.label}
                  </text>
                  <line x1={0} x2={plotW} y1={barY + barH / 2} y2={barY + barH / 2} className="grid-line" />
                  <path d={barPath(0, barY, w, barH, 4)} className="bar-fill" />
                  <text x={w + 6} y={barY + barH / 2 + 4} style={{ fill: 'var(--text-1)', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                    {r.valueText}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
        <TooltipView tip={tt.tip} containerWidth={width} />
      </div>
    </ChartFigure>
  );
}
