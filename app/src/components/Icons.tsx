/** Inline SVG icons. Always decorative (aria-hidden): every icon sits next to a text label. */
import type { VerdictKey } from '../lib/labels';

interface IconProps {
  size?: number;
}

const base = (size: number) => ({
  width: size,
  height: size,
  viewBox: '0 0 16 16',
  'aria-hidden': true as const,
  focusable: false as const,
});

export function VerdictIcon({ verdict, size = 14 }: IconProps & { verdict: VerdictKey }) {
  switch (verdict) {
    case 'Projection':
      return (
        <svg {...base(size)}>
          <circle cx="8" cy="8" r="7" fill="var(--better)" />
          <path d="M4.6 8.3l2.2 2.2 4.6-4.8" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'Augmented Projection':
      return (
        <svg {...base(size)}>
          <circle cx="8" cy="8" r="6.3" fill="none" stroke="var(--better)" strokeWidth="1.6" />
          <path d="M8 4.8v6.4M4.8 8h6.4" stroke="var(--better)" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      );
    case 'Diagnostic':
      return (
        <svg {...base(size)}>
          <circle cx="7" cy="7" r="4.4" fill="none" stroke="currentColor" strokeWidth="1.6" />
          <path d="M10.2 10.2l3.6 3.6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
      );
    case 'Exclude':
      return (
        <svg {...base(size)}>
          <circle cx="8" cy="8" r="6.3" fill="none" stroke="currentColor" strokeWidth="1.6" />
          <path d="M4.9 8h6.2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
      );
    case 'Context':
      return (
        <svg {...base(size)}>
          <path d="M8 1.8l6.2 6.2L8 14.2 1.8 8z" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
          <circle cx="8" cy="8" r="1.6" fill="currentColor" />
        </svg>
      );
    case 'Insufficient Evidence':
      return (
        <svg {...base(size)}>
          <circle cx="8" cy="8" r="6.3" fill="none" stroke="currentColor" strokeWidth="1.6" />
          <path d="M6.2 6.3a1.9 1.9 0 113 1.5c-.8.5-1.2.9-1.2 1.7" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <circle cx="8" cy="11.6" r="0.9" fill="currentColor" />
        </svg>
      );
    default:
      return (
        <svg {...base(size)}>
          <circle cx="8" cy="8" r="6.3" fill="none" stroke="currentColor" strokeWidth="1.4" strokeDasharray="2.2 2" />
        </svg>
      );
  }
}

export type FantasyTone = 'gain' | 'partial' | 'null' | 'harm' | 'directional';

export function FantasyIcon({ tone, size = 14 }: IconProps & { tone: FantasyTone }) {
  switch (tone) {
    case 'gain':
      return (
        <svg {...base(size)}>
          <circle cx="8" cy="8" r="7" fill="var(--better)" />
          <path d="M8 4.2v7M5 8.4L8 11.4l3-3" fill="none" stroke="#fff" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'partial':
      return (
        <svg {...base(size)}>
          <circle cx="8" cy="8" r="6.3" fill="none" stroke="var(--better)" strokeWidth="1.6" />
          <path d="M8 4.6v6.4M5.3 8.4L8 11.1l2.7-2.7" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'directional':
      return (
        <svg {...base(size)}>
          <circle cx="8" cy="8" r="6.3" fill="none" stroke="currentColor" strokeWidth="1.4" strokeDasharray="2.2 1.8" />
          <path d="M8 4.6v6.4M5.3 8.4L8 11.1l2.7-2.7" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case 'harm':
      return (
        <svg {...base(size)}>
          <circle cx="8" cy="8" r="7" fill="var(--worse)" />
          <path d="M8 11.8v-7M5 7.6L8 4.6l3 3" fill="none" stroke="#fff" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    default:
      return (
        <svg {...base(size)}>
          <circle cx="8" cy="8" r="6.3" fill="none" stroke="currentColor" strokeWidth="1.6" />
          <path d="M5 6.7h6M5 9.3h6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      );
  }
}

export function ResultIcon({ improved, size = 14 }: IconProps & { improved: boolean }) {
  return improved ? (
    <svg {...base(size)}>
      <circle cx="8" cy="8" r="7" fill="var(--better)" />
      <path d="M4.6 8.3l2.2 2.2 4.6-4.8" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ) : (
    <svg {...base(size)}>
      <circle cx="8" cy="8" r="7" fill="var(--worse)" />
      <path d="M5.4 5.4l5.2 5.2M10.6 5.4l-5.2 5.2" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function InfoIcon({ size = 16 }: IconProps) {
  return (
    <svg {...base(size)}>
      <circle cx="8" cy="8" r="6.8" fill="none" stroke="currentColor" strokeWidth="1.4" />
      <path d="M8 7.2v4.2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="8" cy="4.9" r="0.95" fill="currentColor" />
    </svg>
  );
}

export function FlaskIcon({ size = 16 }: IconProps) {
  return (
    <svg {...base(size)}>
      <path d="M6 1.8h4M6.8 1.8v4.3L2.6 12.6a1.2 1.2 0 001 1.8h8.8a1.2 1.2 0 001-1.8L9.2 6.1V1.8" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M4.4 10h7.2" stroke="currentColor" strokeWidth="1.3" />
    </svg>
  );
}

export function MenuIcon({ size = 18 }: IconProps) {
  return (
    <svg {...base(size)}>
      <path d="M2.5 4.5h11M2.5 8h11M2.5 11.5h11" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

export function LogoMark() {
  return (
    <svg className="brand-mark" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <rect width="32" height="32" rx="7" fill="var(--link)" />
      <path d="M7 22h18M9 22V14M15 22V9M21 22v-6" stroke="var(--surface)" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}
