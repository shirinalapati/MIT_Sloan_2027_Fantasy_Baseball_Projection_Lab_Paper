import notesSource from '../../content/study_notes.md?raw';
import { useData } from '../data/load';
import type { Meta, Target } from '../data/schemas';
import { Gate, PageHead } from '../components/Page';
import { MarkdownBlocks } from '../components/Markdown';
import { DataTable } from '../components/charts/ChartFigure';
import { parseMarkdown, type Section } from '../lib/markdown';
import { ISSUES_URL, PSL_URL, REPO_URL } from '../lib/links';
import { fmtInt } from '../lib/format';

const doc = parseMarkdown(notesSource);

/** Section headings in the notes include instructions to the app; show readers a clean title, keep the body verbatim. */
export function displayHeading(h: string): string {
  if (h.startsWith('Caveats the app must keep visible')) return 'Caveats';
  return h.replace(/\s*\(show next to the abstract\)\s*$/, '').trim();
}

const KNOWN = ['Original accepted abstract', 'What changed', 'Verdict roles', 'Four different things', 'Caveats', 'Data rights'];
const find = (prefix: string): Section | undefined => doc.sections.find((s) => s.heading.startsWith(prefix));

function NotesSection({ prefix, id }: { prefix: string; id: string }) {
  const s = find(prefix);
  if (!s) return null;
  return (
    <section className="section" aria-labelledby={id}>
      <h2 id={id}>{displayHeading(s.heading)}</h2>
      <div className="card prose">
        <MarkdownBlocks blocks={s.blocks} />
      </div>
    </section>
  );
}

export default function Methods() {
  const state = useData('meta', 'targets');
  return (
    <>
      <PageHead eyebrow="Read before you rely on anything here" title="Methods, Limits & Sources">
        <p className="lede">
          The study&apos;s original abstract and what changed under stronger validation, how verdicts are assigned, the caveats that apply
          everywhere in this lab, data rights, and checksums for every source file.
        </p>
      </PageHead>
      <Gate state={state} what="study metadata">
        {({ meta, targets }) => <MethodsBody meta={meta} targets={targets} />}
      </Gate>
    </>
  );
}

function MethodsBody({ meta, targets }: { meta: Meta; targets: Target[] }) {
  const abstract = find('Original accepted abstract');
  const changed = find('What changed');
  const others = doc.sections.filter((s) => !KNOWN.some((k) => s.heading.startsWith(k)));
  const shaRows = Object.entries(meta.sources_sha256).map(([file, hash]) => ({ file, hash }));
  return (
    <>
      <section className="section" aria-labelledby="about" style={{ marginTop: 8 }}>
        <h2 id="about">About this study</h2>
        <div className="card">
          <dl className="meta">
            <dt>Paper</dt>
            <dd>
              <em>{meta.paper.title}</em>
            </dd>
            <dt>Venue</dt>
            <dd>{meta.paper.venue}</dd>
            <dt>Code and data builders</dt>
            <dd>
              <a href={REPO_URL} target="_blank" rel="noopener noreferrer">
                MIT_Sloan_2027_Fantasy_Baseball_Projection_Lab_Paper
              </a>{' '}
              (this paper, the fantasy bridge and this app) ·{' '}
              <a href={PSL_URL} target="_blank" rel="noopener noreferrer">
                Projection-Signal-Lab
              </a>{' '}
              (the original study, left unchanged)
            </dd>
            <dt>Feedback</dt>
            <dd>
              Please open an issue on{' '}
              <a href={ISSUES_URL} target="_blank" rel="noopener noreferrer">
                GitHub Issues
              </a>
              .
            </dd>
            <dt>Identification</dt>
            <dd>Referred to as Paper ID 18; author names are omitted for blind review.</dd>
          </dl>
        </div>
      </section>

      {abstract || changed ? (
        <section className="section" aria-labelledby="abstract">
          <h2 id="abstract" className="sr-only">
            Original abstract and what changed
          </h2>
          <div className="abstract-grid">
            {abstract ? (
              <div className="card prose">
                <h3>{displayHeading(abstract.heading)}</h3>
                <MarkdownBlocks blocks={abstract.blocks} />
              </div>
            ) : null}
            {changed ? (
              <div className="card prose" style={{ borderLeft: '4px solid var(--text-2)' }}>
                <h3>{displayHeading(changed.heading)}</h3>
                <MarkdownBlocks blocks={changed.blocks} />
              </div>
            ) : null}
          </div>
        </section>
      ) : null}

      <section className="section" aria-labelledby="targets">
        <h2 id="targets">The six targets</h2>
        <p className="section-intro">Every target is a next-season rate. Definitions come from the study&apos;s target registry.</p>
        <div className="grid-2">
          {targets.map((t) => (
            <article key={t.id} className="card" aria-labelledby={`t-${t.id}`}>
              <h3 id={`t-${t.id}`}>{t.label}</h3>
              <p>{t.definition}</p>
              <dl className="meta">
                <dt>Unit</dt>
                <dd>{t.unit}</dd>
                <dt>Denominator</dt>
                <dd>{t.denominator}</dd>
                <dt>Eligibility</dt>
                <dd>{t.eligibility}</dd>
                <dt>Weight</dt>
                <dd>{t.weight}</dd>
                <dt>History baseline</dt>
                <dd>{t.baseline}</dd>
                <dt>Why chosen</dt>
                <dd>{t.why}</dd>
                <dt>Fantasy link</dt>
                <dd>{t.fantasy_link}</dd>
                <dt>Not established</dt>
                <dd>{t.not_established}</dd>
                <dt>Evaluations</dt>
                <dd>
                  {t.n_candidates} candidate metrics; {fmtInt(t.n_player_seasons)} player-seasons
                </dd>
              </dl>
            </article>
          ))}
        </div>
      </section>

      <NotesSection prefix="Verdict roles" id="verdicts" />
      <NotesSection prefix="Four different things" id="unstable" />
      <NotesSection prefix="Caveats" id="caveats" />
      <NotesSection prefix="Data rights" id="rights" />
      {others.map((s, i) => (
        <section className="section" key={s.heading} aria-labelledby={`extra-${i}`}>
          <h2 id={`extra-${i}`}>{displayHeading(s.heading)}</h2>
          <div className="card prose">
            <MarkdownBlocks blocks={s.blocks} />
          </div>
        </section>
      ))}

      <section className="section" aria-labelledby="tiers">
        <h2 id="tiers">Evidence tiers and intervals</h2>
        <div className="card">
          <dl className="meta">
            {Object.entries(meta.evidence_tiers).map(([k, v]) => (
              <Def key={k} k={k} v={v} />
            ))}
            <dt>Interval definition</dt>
            <dd>{meta.ci_definition}</dd>
          </dl>
        </div>
      </section>

      <section className="section" aria-labelledby="provenance">
        <h2 id="provenance">Provenance</h2>
        <div className="card">
          <dl className="meta" style={{ marginBottom: 14 }}>
            <dt>Research root</dt>
            <dd>{meta.provenance.psl_research_root}</dd>
            <dt>Fantasy protocol commit</dt>
            <dd>
              <code>{meta.provenance.fantasy_protocol_commit}</code>
            </dd>
            <dt>App data generated</dt>
            <dd>
              {meta.generated_at} (schema {meta.schema_version})
            </dd>
          </dl>
          <DataTable
            caption="SHA-256 of every source artifact behind the app data"
            rows={shaRows}
            rowKey={(r) => r.file}
            columns={[
              { key: 'file', label: 'Source file', render: (r) => <code style={{ overflowWrap: 'anywhere' }}>{r.file}</code> },
              { key: 'hash', label: 'SHA-256', render: (r) => <span className="hash">{r.hash}</span> },
            ]}
          />
        </div>
      </section>
    </>
  );
}

function Def({ k, v }: { k: string; v: string }) {
  return (
    <>
      <dt>
        <code>{k}</code>
      </dt>
      <dd>{v}</dd>
    </>
  );
}
