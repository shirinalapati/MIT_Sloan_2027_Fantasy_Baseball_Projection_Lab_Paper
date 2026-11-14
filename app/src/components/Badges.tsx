/** Verdict badges: text + icon, never color alone. */
import type { FantasyVerdict } from '../data/schemas';
import { FANTASY_VERDICT_INFO, type VerdictKey } from '../lib/labels';
import { FantasyIcon, FlaskIcon, VerdictIcon } from './Icons';

function verdictClass(v: VerdictKey): string {
  switch (v) {
    case 'Projection':
      return 'v-projection';
    case 'Diagnostic':
      return 'v-diagnostic';
    case 'Exclude':
      return 'v-exclude';
    case 'Context':
      return 'v-context';
    case 'Not evaluated':
      return 'v-not-evaluated';
    default:
      return 'v-other';
  }
}

export function VerdictBadge({ verdict, size }: { verdict: VerdictKey; size?: 'sm' }) {
  return (
    <span className={`badge ${verdictClass(verdict)}${size === 'sm' ? ' sm' : ''}`} data-verdict={verdict}>
      <VerdictIcon verdict={verdict} size={size === 'sm' ? 12 : 14} />
      <span>{verdict}</span>
    </span>
  );
}

export function FantasyVerdictBadge({ verdict, size }: { verdict: FantasyVerdict; size?: 'sm' }) {
  const info = FANTASY_VERDICT_INFO[verdict];
  return (
    <span className={`badge f-${info.tone}${size === 'sm' ? ' sm' : ''} badge-wrap`} data-verdict={verdict}>
      <FantasyIcon tone={info.tone} size={size === 'sm' ? 12 : 14} />
      <span>{info.label}</span>
    </span>
  );
}

export type TierKey = 'historical' | 'historical-2026' | 'exploratory_fantasy' | 'illustrative';

/** Evidence-tier tag. Labels come from meta.json evidence_tiers. */
export function TierTag({ tier, label }: { tier: TierKey; label: string }) {
  return (
    <span className={`tier-tag${tier === 'illustrative' ? ' illustrative' : ''}`}>
      {tier === 'illustrative' ? <FlaskIcon size={13} /> : null}
      <span>Evidence tier: {label}</span>
    </span>
  );
}
