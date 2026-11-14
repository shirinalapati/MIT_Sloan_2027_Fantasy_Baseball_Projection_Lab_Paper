import { useEffect, type ReactNode } from 'react';
import type { DataName, DataState, DataFiles } from '../data/load';

export function PageHead({ eyebrow, title, children }: { eyebrow?: string; title: string; children?: ReactNode }) {
  useEffect(() => {
    document.title = `${title} · Fantasy Projection Lab`;
  }, [title]);
  return (
    <header className="page-head">
      {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
      <h1 id="page-title" tabIndex={-1}>
        {title}
      </h1>
      {children}
    </header>
  );
}

export function Gate<K extends DataName>({
  state,
  what,
  children,
}: {
  state: DataState<K>;
  what: string;
  children: (data: Pick<DataFiles, K>) => ReactNode;
}) {
  if (state.status === 'loading') {
    return (
      <p className="loading" role="status">
        Loading {what}…
      </p>
    );
  }
  if (state.status === 'error') {
    return (
      <div className="error-box" role="alert">
        <strong>Could not load the research data.</strong> {state.error}. Try reloading the page.
      </div>
    );
  }
  return <>{children(state.data)}</>;
}

export function Callout({
  kind = 'note',
  title,
  icon,
  children,
  id,
}: {
  kind?: 'note' | 'info' | 'caution' | 'illustrative';
  title?: ReactNode;
  icon?: ReactNode;
  children: ReactNode;
  id?: string;
}) {
  return (
    <div className={`callout ${kind}`} id={id}>
      {title ? (
        <p className="callout-title">
          {icon}
          {title}
        </p>
      ) : null}
      {children}
    </div>
  );
}

export function Tile({ label, value, sub }: { label: string; value: ReactNode; sub?: ReactNode }) {
  return (
    <div className="tile">
      <p className="tile-label">{label}</p>
      <div className="tile-value">{value}</div>
      {sub ? <div className="tile-sub">{sub}</div> : null}
    </div>
  );
}
