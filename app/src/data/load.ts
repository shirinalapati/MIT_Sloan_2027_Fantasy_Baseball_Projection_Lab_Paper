/**
 * Runtime data access: each JSON file is fetched once from /data/*.json and cached.
 * Pages request only the files they need, so heavy files (evaluations, fantasy, casebook,
 * model comparisons) load lazily. Data were validated at build time (scripts/validate-data.ts).
 */
import { useEffect, useState } from 'react';
import type {
  Casebook,
  Evaluation,
  Fantasy,
  Flagship,
  Meta,
  Metric,
  ModelComparisons,
  Target,
} from './schemas';
import { parseScoring, type ScoringConfig } from '../lib/scoring';

export interface DataFiles {
  meta: Meta;
  targets: Target[];
  metrics: Metric[];
  evaluations: Evaluation[];
  model_comparisons: ModelComparisons;
  flagships: Flagship[];
  casebook: Casebook;
  fantasy: Fantasy;
}
export type DataName = keyof DataFiles;

const cache = new Map<string, Promise<unknown>>();

export function dataUrl(name: string): string {
  const base = import.meta.env.BASE_URL || '/';
  return `${base.endsWith('/') ? base : `${base}/`}data/${name}.json`;
}

async function fetchJson(name: string): Promise<unknown> {
  const res = await fetch(dataUrl(name));
  if (!res.ok) throw new Error(`Could not load ${name}.json (HTTP ${res.status})`);
  return res.json();
}

export function loadData<K extends DataName>(name: K): Promise<DataFiles[K]> {
  let p = cache.get(name);
  if (!p) {
    p = fetchJson(name);
    p.catch(() => cache.delete(name)); // allow a retry after a failure
    cache.set(name, p);
  }
  return p as Promise<DataFiles[K]>;
}

/** Optional scoring.json. Resolves to null when it was absent at build time or is unusable. */
export function loadScoring(): Promise<ScoringConfig | null> {
  if (!__HAS_SCORING_JSON__) return Promise.resolve(null);
  let p = cache.get('scoring');
  if (!p) {
    p = fetch(dataUrl('scoring'))
      .then(async (res) => {
        if (!res.ok) return null;
        const type = res.headers.get('content-type') ?? '';
        if (type && !type.includes('json')) return null;
        try {
          return parseScoring(await res.json());
        } catch {
          return null;
        }
      })
      .catch(() => null);
    cache.set('scoring', p);
  }
  return p as Promise<ScoringConfig | null>;
}

/** Test helper: forget cached responses. */
export function clearDataCache(): void {
  cache.clear();
}

export type DataState<K extends DataName> =
  | { status: 'loading' }
  | { status: 'error'; error: string }
  | { status: 'ready'; data: Pick<DataFiles, K> };

/** Load several files; re-renders when all are ready. */
export function useData<K extends DataName>(...names: K[]): DataState<K> {
  const key = names.join(',');
  const [state, setState] = useState<DataState<K>>({ status: 'loading' });
  useEffect(() => {
    let alive = true;
    setState((s) => (s.status === 'ready' ? s : { status: 'loading' }));
    Promise.all(names.map((n) => loadData(n)))
      .then((values) => {
        if (!alive) return;
        const data = {} as Pick<DataFiles, K>;
        names.forEach((n, i) => {
          (data as Record<string, unknown>)[n] = values[i];
        });
        setState({ status: 'ready', data });
      })
      .catch((e: unknown) => {
        if (alive) setState({ status: 'error', error: e instanceof Error ? e.message : String(e) });
      });
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  return state;
}

export function useScoring(): { status: 'loading' | 'ready'; scoring: ScoringConfig | null } {
  const [state, setState] = useState<{ status: 'loading' | 'ready'; scoring: ScoringConfig | null }>({
    status: 'loading',
    scoring: null,
  });
  useEffect(() => {
    let alive = true;
    loadScoring().then((s) => alive && setState({ status: 'ready', scoring: s }));
    return () => {
      alive = false;
    };
  }, []);
  return state;
}
