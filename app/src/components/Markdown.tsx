/** Renders the parsed study notes as React elements (no innerHTML). */
import type { Block, Inline } from '../lib/markdown';

function InlineView({ c }: { c: Inline[] }) {
  return (
    <>
      {c.map((i, k) => {
        switch (i.t) {
          case 'text':
            return <span key={k}>{i.v}</span>;
          case 'strong':
            return (
              <strong key={k}>
                <InlineView c={i.c} />
              </strong>
            );
          case 'code':
            return <code key={k}>{i.v}</code>;
          case 'link': {
            const external = /^https?:/.test(i.href);
            return (
              <a key={k} href={i.href} {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}>
                <InlineView c={i.c} />
              </a>
            );
          }
          default:
            return null;
        }
      })}
    </>
  );
}

export function MarkdownBlocks({ blocks, headingOffset = 2 }: { blocks: Block[]; headingOffset?: number }) {
  return (
    <>
      {blocks.map((b, k) => {
        if (b.t === 'p') {
          return (
            <p key={k}>
              <InlineView c={b.c} />
            </p>
          );
        }
        if (b.t === 'h') {
          const level = Math.min(6, b.level + headingOffset);
          const H = `h${level}` as 'h3';
          return (
            <H key={k}>
              <InlineView c={b.c} />
            </H>
          );
        }
        const L = b.ordered ? 'ol' : 'ul';
        return (
          <L key={k}>
            {b.items.map((it, j) => (
              <li key={j}>
                <InlineView c={it.c} />
                {it.children.length ? <MarkdownBlocks blocks={it.children} headingOffset={headingOffset} /> : null}
              </li>
            ))}
          </L>
        );
      })}
    </>
  );
}
