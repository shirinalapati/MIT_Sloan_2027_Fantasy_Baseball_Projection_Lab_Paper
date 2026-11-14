/** Test helpers: read the real data files and serve them through a mocked fetch. */
import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { vi } from 'vitest';
import type {
  Casebook,
  Evaluation,
  Fantasy,
  Flagship,
  Meta,
  Metric,
  ModelComparisons,
  Target,
} from '../../src/data/schemas';

/** Vitest runs from the app directory (its config root). */
export const APP_DIR = process.cwd();
export const DATA_DIR = path.resolve(APP_DIR, 'public/data');

export function readData<T = unknown>(name: string): T {
  return JSON.parse(readFileSync(path.join(DATA_DIR, `${name}.json`), 'utf8')) as T;
}

export function loadAll() {
  return {
    meta: readData<Meta>('meta'),
    targets: readData<Target[]>('targets'),
    metrics: readData<Metric[]>('metrics'),
    evaluations: readData<Evaluation[]>('evaluations'),
    model_comparisons: readData<ModelComparisons>('model_comparisons'),
    flagships: readData<Flagship[]>('flagships'),
    casebook: readData<Casebook>('casebook'),
    fantasy: readData<Fantasy>('fantasy'),
    ...(existsSync(path.join(DATA_DIR, 'scoring.json')) ? { scoring: readData('scoring') } : {}),
  };
}

/** Replace global fetch with one that serves public/data/*.json from disk. */
export function installDataFetch() {
  const fn = vi.fn(async (input: RequestInfo | URL) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
    const name = url.split('/').pop() ?? '';
    const file = path.join(DATA_DIR, name);
    if (!existsSync(file)) {
      return { ok: false, status: 404, headers: { get: () => 'text/plain' }, json: async () => ({}) } as unknown as Response;
    }
    const body = readFileSync(file, 'utf8');
    return { ok: true, status: 200, headers: { get: () => 'application/json' }, json: async () => JSON.parse(body) } as unknown as Response;
  });
  globalThis.fetch = fn as unknown as typeof fetch;
  return fn;
}
