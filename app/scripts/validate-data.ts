/**
 * Build gate: validates every JSON file in public/data (or --dir <path>) and exits non-zero on
 * any error. Wired to `prebuild`, so `npm run build` cannot produce a site from bad data.
 *
 *   npm run validate-data
 *   npx tsx scripts/validate-data.ts --dir path/to/data
 */
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  OPTIONAL_FILES,
  REQUIRED_FILES,
  validateDataset,
  type DataFileName,
} from '../src/data/validate';

function resolveDir(): string {
  const i = process.argv.indexOf('--dir');
  if (i >= 0 && process.argv[i + 1]) return path.resolve(process.argv[i + 1]);
  return fileURLToPath(new URL('../public/data', import.meta.url));
}

const dir = resolveDir();
const files: Partial<Record<DataFileName, unknown>> = {};
const parseErrors: Partial<Record<DataFileName, string>> = {};

if (!existsSync(dir)) {
  console.error(`validate-data: data directory not found: ${dir}`);
  process.exit(1);
}

for (const name of [...REQUIRED_FILES, ...OPTIONAL_FILES]) {
  const p = path.join(dir, `${name}.json`);
  if (!existsSync(p)) continue;
  const raw = readFileSync(p, 'utf8');
  try {
    files[name] = JSON.parse(raw);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    const hint = /\bNaN\b|Infinity/.test(raw) ? '; NaN/Infinity tokens are not valid JSON' : '';
    parseErrors[name] = `${msg}${hint}`;
  }
}

const known = new Set<string>([...REQUIRED_FILES, ...OPTIONAL_FILES].map((n) => `${n}.json`));
const extras = readdirSync(dir).filter((f) => f.endsWith('.json') && !known.has(f));

const report = validateDataset(files, parseErrors);
for (const f of extras) report.warnings.push(`${f}: unexpected file (not read by the app)`);

console.log(`validate-data: ${dir}`);
for (const n of report.notes) console.log(`  note: ${n}`);
for (const w of report.warnings) console.warn(`  warning: ${w}`);
if (report.errors.length) {
  for (const e of report.errors) console.error(`  error: ${e}`);
  console.error(`validate-data: FAILED with ${report.errors.length} error(s)`);
  process.exit(1);
}
const present = [...REQUIRED_FILES, ...OPTIONAL_FILES].filter((n) => n in files);
console.log(`validate-data: OK (${present.length} files: ${present.map((n) => `${n}.json`).join(', ')})`);
