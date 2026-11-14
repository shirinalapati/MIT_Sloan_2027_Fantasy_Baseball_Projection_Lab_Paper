/** One tooltip per chart: shown on pointer hover and on keyboard focus. Text only (no innerHTML). */
import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';

export interface TooltipRow {
  key: ReactNode;
  value: ReactNode;
  swatch?: ReactNode;
}
export interface TooltipContent {
  title?: ReactNode;
  rows: TooltipRow[];
}
interface TipState {
  x: number;
  y: number;
  content: TooltipContent;
}

const TIP_WIDTH = 260;

export function useTooltip() {
  const ref = useRef<HTMLDivElement>(null);
  const [tip, setTip] = useState<TipState | null>(null);

  const showAt = useCallback((clientX: number, clientY: number, content: TooltipContent) => {
    const box = ref.current?.getBoundingClientRect();
    if (!box) return;
    setTip({ x: clientX - box.left, y: clientY - box.top, content });
  }, []);

  const showAtEvent = useCallback(
    (e: { clientX: number; clientY: number }, content: TooltipContent) => showAt(e.clientX, e.clientY, content),
    [showAt],
  );

  const showAtElement = useCallback(
    (el: Element, content: TooltipContent) => {
      const r = el.getBoundingClientRect();
      showAt(r.left + r.width / 2, r.top + r.height / 2, content);
    },
    [showAt],
  );

  const hide = useCallback(() => setTip(null), []);

  useEffect(() => {
    if (!tip) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setTip(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [tip]);

  return { ref, tip, showAtEvent, showAtElement, hide };
}

export function TooltipView({ tip, containerWidth }: { tip: TipState | null; containerWidth: number }) {
  if (!tip) return null;
  const width = Math.min(TIP_WIDTH, Math.max(160, containerWidth - 8));
  let left = tip.x + 14;
  if (left + width > containerWidth) left = Math.max(0, tip.x - 14 - width);
  const style = { left, top: tip.y + 14, width };
  return (
    <div className="tooltip" role="tooltip" style={style}>
      {tip.content.title ? <div className="tt-title">{tip.content.title}</div> : null}
      {tip.content.rows.map((r, i) => (
        <div className="tt-row" key={i}>
          <span className="k">
            {r.swatch}
            {r.key}
          </span>
          <span className="v">{r.value}</span>
        </div>
      ))}
    </div>
  );
}

/** Short stroke used to key a series inside tooltips (line keys, not boxes). */
export function LineKey({ color }: { color: string }) {
  return (
    <svg width="14" height="8" aria-hidden="true" focusable="false">
      <line x1="1" y1="4" x2="13" y2="4" style={{ stroke: color }} strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}
