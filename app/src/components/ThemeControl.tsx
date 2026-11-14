/** Light / dark / system theme. System follows prefers-color-scheme; a manual choice is remembered when storage allows. */
import { useEffect, useState } from 'react';
import { Segmented } from './Segmented';

export type ThemeChoice = 'system' | 'light' | 'dark';
const KEY = 'fpl-theme';

function readStored(): ThemeChoice {
  try {
    const v = window.localStorage.getItem(KEY);
    return v === 'light' || v === 'dark' ? v : 'system';
  } catch {
    return 'system';
  }
}

export function useTheme(): [ThemeChoice, (t: ThemeChoice) => void] {
  const [theme, setTheme] = useState<ThemeChoice>(() => (typeof window === 'undefined' ? 'system' : readStored()));
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'system') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', theme);
    try {
      if (theme === 'system') window.localStorage.removeItem(KEY);
      else window.localStorage.setItem(KEY, theme);
    } catch {
      /* storage unavailable: the choice lasts for this page view */
    }
  }, [theme]);
  return [theme, setTheme];
}

export function ThemeControl({ theme, onChange, className }: { theme: ThemeChoice; onChange: (t: ThemeChoice) => void; className?: string }) {
  return (
    <div className={className}>
      <Segmented<ThemeChoice>
        legend="Color theme"
        hideLegend
        value={theme}
        onChange={onChange}
        options={[
          { value: 'system', label: 'System' },
          { value: 'light', label: 'Light' },
          { value: 'dark', label: 'Dark' },
        ]}
      />
    </div>
  );
}
