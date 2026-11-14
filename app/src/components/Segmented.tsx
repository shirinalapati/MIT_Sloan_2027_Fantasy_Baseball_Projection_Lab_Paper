/** A radio group styled as segmented pills. Native radios give arrow-key navigation for free. */
import { useId, type ReactNode } from 'react';

export interface SegmentedOption<V extends string> {
  value: V;
  label: ReactNode;
  disabled?: boolean;
  title?: string;
}

export function Segmented<V extends string>({
  legend,
  options,
  value,
  onChange,
  name,
  hideLegend,
}: {
  legend: string;
  options: SegmentedOption<V>[];
  value: V;
  onChange: (v: V) => void;
  name?: string;
  hideLegend?: boolean;
}) {
  const auto = useId();
  const groupName = name ?? `seg-${auto}`;
  return (
    <fieldset className="control">
      <legend className={hideLegend ? 'sr-only' : undefined}>{legend}</legend>
      <div className="segmented">
        {options.map((o) => (
          <label key={o.value} title={o.title}>
            <input
              type="radio"
              name={groupName}
              value={o.value}
              checked={o.value === value}
              disabled={o.disabled}
              onChange={() => onChange(o.value)}
            />
            <span>{o.label}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}

/** Labelled native select. */
export function SelectControl<V extends string>({
  label,
  value,
  options,
  onChange,
  id,
}: {
  label: string;
  value: V;
  options: Array<{ value: V; label: string; disabled?: boolean }>;
  onChange: (v: V) => void;
  id?: string;
}) {
  const auto = useId();
  const sid = id ?? `sel-${auto}`;
  return (
    <div className="control">
      <label className="control-label" htmlFor={sid}>
        {label}
      </label>
      <select id={sid} value={value} onChange={(e) => onChange(e.target.value as V)}>
        {options.map((o) => (
          <option key={o.value} value={o.value} disabled={o.disabled}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}
