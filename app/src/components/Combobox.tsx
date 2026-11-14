/** Accessible searchable picker (ARIA 1.2 combobox with a listbox popup). */
import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { normalizeName } from '../lib/casebook';

export interface ComboOption {
  value: string;
  label: string;
  sub?: string;
  keywords?: string;
}

const MAX_RESULTS = 80;

export function Combobox({
  label,
  options,
  value,
  onChange,
  placeholder,
  hint,
}: {
  label: string;
  options: ComboOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  hint?: string;
}) {
  const id = useId();
  const inputId = `cb-input-${id}`;
  const listId = `cb-list-${id}`;
  const hintId = `cb-hint-${id}`;
  const selected = options.find((o) => o.value === value);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [editing, setEditing] = useState(false);
  const [active, setActive] = useState(0);
  const listRef = useRef<HTMLUListElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const results = useMemo(() => {
    const q = normalizeName(query);
    const matched = q
      ? options.filter((o) => normalizeName(`${o.label} ${o.sub ?? ''} ${o.value} ${o.keywords ?? ''}`).includes(q))
      : options;
    return matched.slice(0, MAX_RESULTS);
  }, [options, query]);

  useEffect(() => {
    setActive(0);
  }, [query]);

  useEffect(() => {
    if (!open || !listRef.current) return;
    const el = listRef.current.querySelector<HTMLElement>(`[data-index="${active}"]`);
    if (el && typeof el.scrollIntoView === 'function') el.scrollIntoView({ block: 'nearest' });
  }, [active, open]);

  const choose = (o: ComboOption | undefined) => {
    if (!o) return;
    onChange(o.value);
    setOpen(false);
    setEditing(false);
    setQuery('');
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (!open) {
          setOpen(true);
          setEditing(true);
        } else setActive((a) => Math.min(results.length - 1, a + 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (open) setActive((a) => Math.max(0, a - 1));
        break;
      case 'Home':
        if (open) {
          e.preventDefault();
          setActive(0);
        }
        break;
      case 'End':
        if (open) {
          e.preventDefault();
          setActive(Math.max(0, results.length - 1));
        }
        break;
      case 'Enter':
        if (open) {
          e.preventDefault();
          choose(results[active]);
        }
        break;
      case 'Escape':
        if (open) {
          e.preventDefault();
          setOpen(false);
          setEditing(false);
          setQuery('');
        }
        break;
      case 'Tab':
        setOpen(false);
        setEditing(false);
        setQuery('');
        break;
      default:
        break;
    }
  };

  const shown = editing ? query : selected?.label ?? '';
  const activeId = open && results[active] ? `${listId}-opt-${active}` : undefined;

  return (
    <div className="control">
      <label className="control-label" htmlFor={inputId}>
        {label}
      </label>
      <div className="combobox">
        <input
          ref={inputRef}
          id={inputId}
          type="text"
          role="combobox"
          aria-autocomplete="list"
          aria-expanded={open}
          aria-controls={listId}
          aria-activedescendant={activeId}
          aria-describedby={hint ? hintId : undefined}
          autoComplete="off"
          spellCheck={false}
          placeholder={placeholder}
          value={shown}
          onFocus={(e) => {
            e.currentTarget.select();
          }}
          onClick={() => {
            if (!open) {
              setOpen(true);
              setEditing(true);
              setQuery('');
            }
          }}
          onChange={(e) => {
            setEditing(true);
            setQuery(e.target.value);
            setOpen(true);
          }}
          onBlur={() => {
            // Let option clicks (mousedown) land first.
            window.setTimeout(() => {
              setOpen(false);
              setEditing(false);
              setQuery('');
            }, 120);
          }}
          onKeyDown={onKeyDown}
        />
        {open ? (
          <ul className="combobox-list" id={listId} role="listbox" aria-label={label} ref={listRef}>
            {results.length === 0 ? (
              <li className="combobox-empty" role="option" aria-selected="false" aria-disabled="true">
                No metric matches “{query}”
              </li>
            ) : (
              results.map((o, i) => (
                <li
                  key={o.value}
                  id={`${listId}-opt-${i}`}
                  data-index={i}
                  role="option"
                  aria-selected={i === active}
                  className={`combobox-option${o.value === value ? ' current' : ''}`}
                  onMouseDown={(e) => e.preventDefault()}
                  onMouseEnter={() => setActive(i)}
                  onClick={() => choose(o)}
                >
                  <span className="opt-main">{o.label}</span>
                  {o.sub ? <span className="opt-sub">{o.sub}</span> : null}
                </li>
              ))
            )}
          </ul>
        ) : null}
        {/* aria-controls must reference an element even when the popup is closed */}
        {!open ? <ul id={listId} role="listbox" aria-label={label} hidden /> : null}
      </div>
      {hint ? (
        <span id={hintId} className="muted small">
          {hint}
        </span>
      ) : null}
      <span className="sr-only" aria-live="polite">
        {open ? `${results.length} result${results.length === 1 ? '' : 's'}` : ''}
      </span>
    </div>
  );
}
