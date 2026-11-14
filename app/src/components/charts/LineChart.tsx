/** Multi-series line chart over years with a snapping crosshair, one tooltip for every series, and a toggle legend. */
import { useState, type ReactNode } from 'react';
import { ChartFigure, DataTable, type TableColumn } from './ChartFigure';
import { linearScale, niceDomain, niceTicks, tickDigits } from './scale';
import { LineKey, TooltipView, useTooltip } from './Tooltip';
import { useMeasure } from './useMeasure';
import { fmt } from '../../lib/format';

export interface LineSeries {
  id: string;
  label: string;
  color: string;
  points: Array<{ x: number; y: number }>;
}

export function LineChart({
  title,
  subtitle,
  series,
  visible,
  onToggle,
  yLabel,
  xLabel,
  valueDigits = 3,
  ariaLabel,
  height = 260,
  note,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  series: LineSeries[];
  visible: string[];
  onToggle: (id: string) => void;
  yLabel: string;
  xLabel: string;
  valueDigits?: number;
  ariaLabel: string;
  height?: number;
  note?: ReactNode;
}) {
  const { ref, width } = useMeasure<HTMLDivElement>(640);
  const tt = useTooltip();
  const [focusIdx, setFocusIdx] = useState<number | null>(null);
  const shown = series.filter((s) => visible.includes(s.id));
  const xs = [...new Set(series.flatMap((s) => s.points.map((p) => p.x)))].sort((a, b) => a - b);
  const ys = shown.flatMap((s) => s.points.map((p) => p.y));
  const m = { l: 52, r: 16, t: 14, b: 30 };
  const innerW = Math.max(60, width - m.l - m.r);
  const innerH = height - m.t - m.b;
  const [y0, y1] = niceDomain(ys.length ? ys : [0, 1], { includeZero: false, pad: 0.08, count: 5 });
  const y = linearScale([y0, y1], [m.t + innerH, m.t]);
  const yTicks = niceTicks(y0, y1, 5).filter((t) => t >= y0 - 1e-9 && t <= y1 + 1e-9);
  const yDigits = tickDigits(yTicks);
  const x = (v: number) => (xs.length <= 1 ? m.l + innerW / 2 : m.l + ((v - xs[0]) / (xs[xs.length - 1] - xs[0])) * innerW);

  const tipFor = (i: number) => {
    const xv = xs[i];
    const rows = shown
      .map((s) => ({ s, p: s.points.find((p) => p.x === xv) }))
      .filter((r): r is { s: LineSeries; p: { x: number; y: number } } => !!r.p)
      .sort((a, b) => a.p.y - b.p.y)
      .map((r) => ({ key: r.s.label, value: fmt(r.p.y, valueDigits), swatch: <LineKey color={r.s.color} /> }));
    return { title: `${xLabel} ${xv} (lowest first)`, rows };
  };

  const showIdx = (i: number) => {
    setFocusIdx(i);
    const box = tt.ref.current?.getBoundingClientRect();
    if (!box) return;
    const svgBox = tt.ref.current?.querySelector('svg')?.getBoundingClientRect();
    const left = (svgBox?.left ?? box.left) + x(xs[i]);
    const top = (svgBox?.top ?? box.top) + m.t + 20;
    tt.showAtEvent({ clientX: left, clientY: top }, tipFor(i));
  };

  const onMove = (e: React.PointerEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const px = e.clientX - r.left;
    let best = 0;
    xs.forEach((v, i) => {
      if (Math.abs(x(v) - px) < Math.abs(x(xs[best]) - px)) best = i;
    });
    setFocusIdx(best);
    tt.showAtEvent(e, tipFor(best));
  };

  const onKey = (e: React.KeyboardEvent<SVGSVGElement>) => {
    if (!xs.length) return;
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      e.preventDefault();
      const cur = focusIdx ?? (e.key === 'ArrowRight' ? -1 : xs.length);
      const next = Math.min(xs.length - 1, Math.max(0, cur + (e.key === 'ArrowRight' ? 1 : -1)));
      showIdx(next);
    } else if (e.key === 'Escape') {
      setFocusIdx(null);
      tt.hide();
    }
  };

  const columns: TableColumn<number>[] = [
    { key: 'x', label: xLabel, render: (xv) => String(xv) },
    ...series.map((s) => ({
      key: s.id,
      label: s.label,
      num: true,
      render: (xv: number) => {
        const p = s.points.find((q) => q.x === xv);
        return p ? fmt(p.y, valueDigits) : '—';
      },
    })),
  ];

  const legend = (
    <ul className="legend" aria-label="Series (press to show or hide)">
      {series.map((s) => {
        const on = visible.includes(s.id);
        return (
          <li key={s.id}>
            <button type="button" aria-pressed={on} onClick={() => onToggle(s.id)}>
              <LineKey color={s.color} />
              {s.label}
            </button>
          </li>
        );
      })}
    </ul>
  );

  return (
    <ChartFigure title={title} subtitle={subtitle} legend={legend} table={<DataTable caption={typeof title === 'string' ? title : ariaLabel} columns={columns} rows={xs} rowKey={(xv) => String(xv)} />}>
      <div className="chart-wrap" ref={tt.ref}>
        <div className="muted small" style={{ marginBottom: 2 }}>
          {yLabel}
        </div>
        <div ref={ref} style={{ width: '100%' }}>
          <svg
            width={width}
            height={height}
            viewBox={`0 0 ${width} ${height}`}
            role="img"
            aria-label={ariaLabel}
            tabIndex={0}
            onPointerMove={onMove}
            onPointerLeave={() => {
              setFocusIdx(null);
              tt.hide();
            }}
            onKeyDown={onKey}
            onFocus={() => showIdx(focusIdx ?? xs.length - 1)}
            onBlur={() => {
              setFocusIdx(null);
              tt.hide();
            }}
            style={{ display: 'block', touchAction: 'pan-y' }}
          >
            {yTicks.map((t) => (
              <g key={t}>
                <line x1={m.l} x2={m.l + innerW} y1={y(t)} y2={y(t)} className="grid-line" />
                <text x={m.l - 8} y={y(t) + 4} textAnchor="end" style={{ fontVariantNumeric: 'tabular-nums' }}>
                  {fmt(t, yDigits)}
                </text>
              </g>
            ))}
            <line x1={m.l} x2={m.l + innerW} y1={m.t + innerH} y2={m.t + innerH} className="axis-line" />
            {xs.map((v) => (
              <text key={v} x={x(v)} y={height - 10} textAnchor="middle">
                {v}
              </text>
            ))}
            {focusIdx !== null && xs[focusIdx] !== undefined ? (
              <line x1={x(xs[focusIdx])} x2={x(xs[focusIdx])} y1={m.t} y2={m.t + innerH} style={{ stroke: 'var(--text-2)' }} strokeWidth={1} />
            ) : null}
            {shown.map((s) => {
              const pts = [...s.points].sort((a, b) => a.x - b.x);
              const d = pts.map((p, i) => `${i ? 'L' : 'M'}${x(p.x).toFixed(1)},${y(p.y).toFixed(1)}`).join(' ');
              return (
                <g key={s.id}>
                  <path d={d} fill="none" style={{ stroke: s.color }} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
                  {pts.map((p) => (
                    <circle key={p.x} cx={x(p.x)} cy={y(p.y)} r={4} style={{ fill: s.color, stroke: 'var(--surface)' }} strokeWidth={2} />
                  ))}
                </g>
              );
            })}
          </svg>
        </div>
        <TooltipView tip={tt.tip} containerWidth={width} />
        {note ? <div className="muted small">{note}</div> : null}
      </div>
    </ChartFigure>
  );
}
