/** Chart container: titled <figure>, optional legend, and the data-table twin every chart carries. */
import { useId, type ReactNode } from 'react';

export interface TableColumn<R> {
  key: string;
  label: string;
  num?: boolean;
  render: (row: R) => ReactNode;
}

export function DataTable<R>({
  caption,
  columns,
  rows,
  rowKey,
}: {
  caption: string;
  columns: TableColumn<R>[];
  rows: R[];
  rowKey: (row: R, i: number) => string;
}) {
  return (
    <div className="table-scroll" role="region" aria-label={caption} tabIndex={0}>
      <table>
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key} scope="col" className={c.num ? 'num' : undefined}>
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={rowKey(r, i)}>
              {columns.map((c, j) =>
                j === 0 ? (
                  <th key={c.key} scope="row" className={c.num ? 'num' : undefined} style={{ fontWeight: 500 }}>
                    {c.render(r)}
                  </th>
                ) : (
                  <td key={c.key} className={c.num ? 'num' : undefined}>
                    {c.render(r)}
                  </td>
                ),
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ChartFigure({
  title,
  subtitle,
  legend,
  table,
  tableLabel = 'Show data table',
  children,
  headingLevel,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  legend?: ReactNode;
  table?: ReactNode;
  tableLabel?: string;
  children: ReactNode;
  headingLevel?: 'h3' | 'h4';
}) {
  const id = useId();
  const titleId = `fig-title-${id}`;
  const Title = headingLevel ?? 'span';
  return (
    <figure className="chart" aria-labelledby={titleId}>
      <figcaption>
        <Title id={titleId} className="chart-title" style={headingLevel ? { margin: 0 } : undefined}>
          {title}
        </Title>
        {subtitle ? <span className="chart-sub">{subtitle}</span> : null}
      </figcaption>
      {legend}
      {children}
      {table ? (
        <details className="data-table">
          <summary>{tableLabel}</summary>
          {table}
        </details>
      ) : null}
    </figure>
  );
}

/** Legend for interval color = where the 95% interval sits relative to zero. */
export function PolarityLegend({
  betterText = 'Interval entirely below 0: more accurate',
  worseText = 'Interval entirely above 0: less accurate',
  neutralText = 'Interval includes 0',
  inkText,
  hollowText,
}: {
  betterText?: string;
  worseText?: string;
  neutralText?: string;
  inkText?: string;
  hollowText?: string;
}) {
  const key = (cls: string) => (
    <svg width="26" height="12" aria-hidden="true" focusable="false">
      <line x1="2" y1="6" x2="24" y2="6" className={`ci-line ${cls}`} />
      <circle cx="13" cy="6" r="4" className={`pt ${cls}`} />
    </svg>
  );
  return (
    <ul className="legend" aria-label="Legend">
      <li>
        {key('mark-better')}
        {betterText}
      </li>
      <li>
        {key('mark-worse')}
        {worseText}
      </li>
      <li>
        {key('mark-neutral')}
        {neutralText}
      </li>
      {inkText ? (
        <li>
          <svg width="14" height="12" aria-hidden="true" focusable="false">
            <circle cx="7" cy="6" r="4" className="pt mark-ink" />
          </svg>
          {inkText}
        </li>
      ) : null}
      {hollowText ? (
        <li>
          <svg width="14" height="12" aria-hidden="true" focusable="false">
            <circle cx="7" cy="6" r="4" className="pt-hollow mark-ink" />
          </svg>
          {hollowText}
        </li>
      ) : null}
    </ul>
  );
}
