/** The metadata block every result card carries. */
import type { ReactNode } from 'react';
import { TierTag, type TierKey } from './Badges';

export interface ResultMetaProps {
  targetDefinition: ReactNode;
  population: ReactNode;
  seasons: ReactNode;
  method: ReactNode;
  ciType: ReactNode;
  tier: { key: TierKey; label: string };
  sources: string[];
  sha256?: Record<string, string>;
  extra?: Array<[string, ReactNode]>;
}

export function ResultMeta(p: ResultMetaProps) {
  return (
    <section className="result-meta" aria-label="About this result">
      <h4>About this result</h4>
      <dl className="meta">
        <dt>Target definition</dt>
        <dd>{p.targetDefinition}</dd>
        <dt>Population</dt>
        <dd>{p.population}</dd>
        <dt>Seasons</dt>
        <dd>{p.seasons}</dd>
        <dt>Method</dt>
        <dd>{p.method}</dd>
        <dt>Interval</dt>
        <dd>{p.ciType}</dd>
        {p.extra?.map(([k, v]) => (
          <FragmentRow key={k} k={k} v={v} />
        ))}
        <dt>Evidence tier</dt>
        <dd>
          <TierTag tier={p.tier.key} label={p.tier.label} />
        </dd>
        <dt>Source file{p.sources.length > 1 ? 's' : ''}</dt>
        <dd>
          <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
            {p.sources.map((s) => (
              <li key={s}>
                <code>{s}</code>
                {p.sha256?.[s] ? (
                  <span className="muted small">
                    {' '}
                    · sha256 <span className="hash">{p.sha256[s].slice(0, 12)}…</span>
                  </span>
                ) : null}
              </li>
            ))}
          </ul>
        </dd>
      </dl>
    </section>
  );
}

function FragmentRow({ k, v }: { k: string; v: ReactNode }) {
  return (
    <>
      <dt>{k}</dt>
      <dd>{v}</dd>
    </>
  );
}
