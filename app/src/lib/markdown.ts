/**
 * A deliberately small Markdown parser for content/study_notes.md: headings, paragraphs,
 * nested bullet/numbered lists, **bold**, `code` and [links](url). It produces a plain
 * AST that React renders as elements (no innerHTML), so the source wording is reproduced exactly.
 */
export type Inline =
  | { t: 'text'; v: string }
  | { t: 'strong'; c: Inline[] }
  | { t: 'code'; v: string }
  | { t: 'link'; href: string; c: Inline[] };

export interface ListItem {
  c: Inline[];
  children: Block[];
}

export type Block =
  | { t: 'p'; c: Inline[] }
  | { t: 'h'; level: number; c: Inline[] }
  | { t: 'list'; ordered: boolean; items: ListItem[] };

export interface Section {
  heading: string;
  blocks: Block[];
}

export interface ParsedDoc {
  title: string | null;
  preamble: Block[];
  sections: Section[];
}

const INLINE_PATTERNS: Array<{ re: RegExp; make: (m: RegExpExecArray) => Inline }> = [
  { re: /`([^`]+)`/, make: (m) => ({ t: 'code', v: m[1] }) },
  { re: /\*\*(.+?)\*\*/, make: (m) => ({ t: 'strong', c: parseInline(m[1]) }) },
  { re: /\[([^\]]+)\]\(([^)\s]+)\)/, make: (m) => ({ t: 'link', href: m[2], c: parseInline(m[1]) }) },
];

export function parseInline(src: string): Inline[] {
  const out: Inline[] = [];
  let rest = src;
  while (rest.length) {
    let best: { idx: number; m: RegExpExecArray; make: (m: RegExpExecArray) => Inline } | null = null;
    for (const p of INLINE_PATTERNS) {
      const m = p.re.exec(rest);
      if (m && (best === null || m.index < best.idx)) best = { idx: m.index, m, make: p.make };
    }
    if (!best) {
      out.push({ t: 'text', v: rest });
      break;
    }
    if (best.idx > 0) out.push({ t: 'text', v: rest.slice(0, best.idx) });
    out.push(best.make(best.m));
    rest = rest.slice(best.idx + best.m[0].length);
  }
  return out;
}

const LIST_RE = /^(\s*)([-*]|\d+\.)\s+(.*)$/;

interface Frame {
  indent: number;
  list: { t: 'list'; ordered: boolean; items: ListItem[] };
}

function parseBlocks(lines: string[]): Block[] {
  const blocks: Block[] = [];
  let para: string[] = [];
  let stack: Frame[] = [];

  const flushPara = () => {
    if (para.length) blocks.push({ t: 'p', c: parseInline(para.join(' ')) });
    para = [];
  };
  const closeLists = () => {
    stack = [];
  };

  for (const line of lines) {
    if (!line.trim()) {
      flushPara();
      closeLists();
      continue;
    }
    const h = /^(#{1,6})\s+(.*)$/.exec(line);
    if (h) {
      flushPara();
      closeLists();
      blocks.push({ t: 'h', level: h[1].length, c: parseInline(h[2].trim()) });
      continue;
    }
    const li = LIST_RE.exec(line);
    if (li) {
      flushPara();
      const indent = li[1].replace(/\t/g, '  ').length;
      const ordered = /\d+\./.test(li[2]);
      const item: ListItem = { c: parseInline(li[3].trim()), children: [] };
      while (stack.length && stack[stack.length - 1].indent > indent) stack.pop();
      const top = stack[stack.length - 1];
      if (top && top.indent === indent) {
        top.list.items.push(item);
      } else if (top && indent > top.indent) {
        const parentItem = top.list.items[top.list.items.length - 1];
        const list = { t: 'list' as const, ordered, items: [item] };
        parentItem.children.push(list);
        stack.push({ indent, list });
      } else {
        const list = { t: 'list' as const, ordered, items: [item] };
        blocks.push(list);
        stack = [{ indent, list }];
      }
      continue;
    }
    if (stack.length && /^\s+\S/.test(line)) {
      // continuation of the last list item
      const top = stack[stack.length - 1];
      const last = top.list.items[top.list.items.length - 1];
      last.c.push({ t: 'text', v: ' ' }, ...parseInline(line.trim()));
      continue;
    }
    closeLists();
    para.push(line.trim());
  }
  flushPara();
  return blocks;
}

/** Split a document into an optional `# title`, a preamble and `## ` sections. */
export function parseMarkdown(src: string): ParsedDoc {
  const lines = src.replace(/\r\n?/g, '\n').split('\n');
  let title: string | null = null;
  const pre: string[] = [];
  const sections: Array<{ heading: string; lines: string[] }> = [];
  for (const line of lines) {
    const h1 = /^#\s+(.*)$/.exec(line);
    const h2 = /^##\s+(.*)$/.exec(line);
    if (h1 && title === null && sections.length === 0) {
      title = h1[1].trim();
      continue;
    }
    if (h2) {
      sections.push({ heading: h2[1].trim(), lines: [] });
      continue;
    }
    if (sections.length) sections[sections.length - 1].lines.push(line);
    else pre.push(line);
  }
  return {
    title,
    preamble: parseBlocks(pre),
    sections: sections.map((s) => ({ heading: s.heading, blocks: parseBlocks(s.lines) })),
  };
}

/** Plain text of inline content (for tests and accessible names). */
export function inlineText(c: Inline[]): string {
  return c
    .map((i) => (i.t === 'text' || i.t === 'code' ? i.v : inlineText(i.c)))
    .join('');
}
