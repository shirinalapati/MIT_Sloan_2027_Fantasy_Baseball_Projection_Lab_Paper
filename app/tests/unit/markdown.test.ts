import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { inlineText, parseMarkdown, parseInline } from '../../src/lib/markdown';

const notes = readFileSync(path.resolve(process.cwd(), 'content/study_notes.md'), 'utf8');

describe('study notes parser', () => {
  const doc = parseMarkdown(notes);
  it('finds every section of the notes', () => {
    const heads = doc.sections.map((s) => s.heading);
    expect(heads[0]).toMatch(/^Original accepted abstract/);
    expect(heads).toEqual(
      expect.arrayContaining([
        expect.stringMatching(/^What changed after stronger validation/),
        expect.stringMatching(/^Verdict roles/),
        expect.stringMatching(/^Four different things called/),
        expect.stringMatching(/^Caveats/),
        expect.stringMatching(/^Data rights/),
      ]),
    );
  });

  it('keeps the abstract text verbatim', () => {
    const abs = doc.sections[0];
    const text = abs.blocks.map((b) => (b.t === 'list' ? '' : inlineText(b.c))).join('\n');
    expect(text).toContain('Two-year xwOBA improved next-season wOBA RMSE by 0.00093 beyond a baseline already containing two-year wOBA and improved all seven folds.');
    expect(text).toContain('Baseball metrics should not be classified as universally “predictive” or “non-predictive.”');
  });

  it('parses nested lists and bold text', () => {
    const changed = doc.sections.find((s) => s.heading.startsWith('What changed'))!;
    const list = changed.blocks.find((b) => b.t === 'list');
    expect(list && list.t === 'list' && list.items.length).toBe(4);
    if (list && list.t === 'list') expect(list.items[2].children.length).toBe(1);
    expect(parseInline('**Projection**: statistical')[0]).toEqual({ t: 'strong', c: [{ t: 'text', v: 'Projection' }] });
  });
});
