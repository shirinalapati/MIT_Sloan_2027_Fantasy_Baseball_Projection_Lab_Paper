import { describe, expect, it } from 'vitest';
import { spawnSync } from 'node:child_process';
import { copyFileSync, mkdtempSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { validateDataset, type DataFileName } from '../../src/data/validate';
import { APP_DIR, DATA_DIR, loadAll } from '../helpers/data';

const clean = loadAll() as Record<string, unknown>;

function corrupt(mutate: (d: Record<string, any>) => void) {
  const d = structuredClone(clean) as Record<string, any>;
  mutate(d);
  return validateDataset(d as Partial<Record<DataFileName, unknown>>);
}

const has = (errors: string[], re: RegExp) => errors.some((e) => re.test(e));

describe('data validator', () => {
  it('accepts the real dataset with zero errors', () => {
    const r = validateDataset(clean as Partial<Record<DataFileName, unknown>>);
    expect(r.errors).toEqual([]);
  });

  it('rejects NaN and non-finite numbers', () => {
    const r = corrupt((d) => {
      d.evaluations[0].delta_pct = Number.NaN;
      d.fantasy.results[0].rmse_base = Number.POSITIVE_INFINITY;
    });
    expect(has(r.errors, /evaluations\.json: 0\.delta_pct/)).toBe(true);
    expect(has(r.errors, /fantasy\.json: results\.0\.rmse_base/)).toBe(true);
  });

  it('rejects unknown and missing fields', () => {
    const r = corrupt((d) => {
      d.targets[0].surprise = 'x';
      delete d.evaluations[3].reason_code;
    });
    expect(has(r.errors, /targets\.json: 0: Unrecognized key/)).toBe(true);
    expect(has(r.errors, /evaluations\.json: 3\.reason_code: Required/)).toBe(true);
  });

  it('rejects evaluation rows whose metric or target is unknown', () => {
    const r = corrupt((d) => {
      d.evaluations[0].metric = 'made_up_metric';
      d.evaluations[1].target = 'made_up_target';
    });
    expect(has(r.errors, /metric "made_up_metric" is not in metrics\.json/)).toBe(true);
    expect(has(r.errors, /target "made_up_target" is not in targets\.json/)).toBe(true);
  });

  it('rejects casebook contrasts that reference unknown targets or metrics', () => {
    const r = corrupt((d) => {
      d.casebook.cases[0].contrast = 'hitting_woba:not_a_metric';
      d.casebook.cases[0].metric = 'not_a_metric';
      d.casebook.cohorts[0].contrast = 'not_a_target:ev';
    });
    expect(has(r.errors, /references unknown metric "not_a_metric"/)).toBe(true);
    expect(has(r.errors, /references unknown target "not_a_target"/)).toBe(true);
  });

  it('rejects fantasy verdict strings outside the known set', () => {
    const r = corrupt((d) => {
      d.fantasy.results[0].verdict = 'probably helps';
    });
    expect(has(r.errors, /fantasy\.json: results\.0\.verdict: Invalid enum value/)).toBe(true);
  });

  it('rejects a fantasy verdict that contradicts the protocol rule', () => {
    const r = corrupt((d) => {
      const row = d.fantasy.results.find((x: any) => x.verdict === 'no detectable gain');
      row.verdict = 'adds information';
    });
    expect(has(r.errors, /contradicts the protocol rule/)).toBe(true);
  });

  it('rejects a CI that does not bracket its point estimate', () => {
    const r = corrupt((d) => {
      const f = d.fantasy.results[0];
      f.ci_low_pct = f.delta_pct + 0.5;
      f.ci_high_pct = f.delta_pct + 1.0;
      const c = d.model_comparisons.comparisons.find((x: any) => x.ci_low_pct !== null);
      c.ci_high_pct = c.delta_pct - 0.01;
      c.ci_low_pct = c.delta_pct - 0.02;
      const e = d.evaluations.find((x: any) => x.metric === 'sprint_speed' && x.target === 'baserunning_rv');
      e.ci_high_pct = e.delta_pct - 0.1;
      e.ci_low_pct = e.delta_pct - 0.2;
      d.flagships[0]['2026 holdout, %'] = '-2.59 [-5.43, -3.00]';
    });
    expect(has(r.errors, /fantasy\.json results\[0\].*does not bracket/)).toBe(true);
    expect(has(r.errors, /model_comparisons\.json comparisons\[\d+\].*does not bracket/)).toBe(true);
    expect(has(r.errors, /sprint_speed × baserunning_rv.*does not bracket/)).toBe(true);
    expect(has(r.errors, /flagships\.json\[0\] 2026 holdout.*does not bracket/)).toBe(true);
  });

  it('accepts the 7 pinned evaluation exceptions only at their exact published values', () => {
    const r = corrupt((d) => {
      const e = d.evaluations.find((x: any) => x.metric === 'k_pct' && x.target === 'pitching_fip');
      e.ci_low_pct += 0.0001; // any change to a pinned row is an error again
    });
    expect(has(r.errors, /k_pct × pitching_fip.*does not bracket/)).toBe(true);
  });

  it('rejects a missing required file', () => {
    const d = structuredClone(clean) as Record<string, unknown>;
    delete d.casebook;
    const r = validateDataset(d as Partial<Record<DataFileName, unknown>>);
    expect(has(r.errors, /casebook\.json: missing required file/)).toBe(true);
  });

  it('the CLI exits non-zero on a corrupted fixture directory and zero on the real data', () => {
    const tsx = path.join(APP_DIR, 'node_modules', '.bin', process.platform === 'win32' ? 'tsx.cmd' : 'tsx');
    const script = path.join(APP_DIR, 'scripts', 'validate-data.ts');
    const ok = spawnSync(tsx, [script], { cwd: APP_DIR, encoding: 'utf8' });
    expect(ok.status).toBe(0);
    expect(ok.stdout).toMatch(/validate-data: OK/);

    const dir = mkdtempSync(path.join(os.tmpdir(), 'fpl-fixture-'));
    try {
      for (const f of readdirSync(DATA_DIR)) copyFileSync(path.join(DATA_DIR, f), path.join(dir, f));
      // Python's json.dump writes NaN tokens, which are not valid JSON.
      const metrics = JSON.stringify(clean.metrics).replace('"process_flag":true', '"process_flag":NaN');
      writeFileSync(path.join(dir, 'metrics.json'), metrics);
      const bad = spawnSync(tsx, [script, '--dir', dir], { cwd: APP_DIR, encoding: 'utf8' });
      expect(bad.status).toBe(1);
      expect(bad.stderr).toMatch(/metrics\.json: invalid JSON/);
      expect(bad.stderr).toMatch(/FAILED/);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
