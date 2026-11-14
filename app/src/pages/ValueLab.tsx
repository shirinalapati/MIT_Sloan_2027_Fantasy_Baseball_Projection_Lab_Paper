import { useEffect, useMemo, useRef, useState } from 'react';
import { useData, useScoring } from '../data/load';
import { Callout, Gate, PageHead } from '../components/Page';
import { Segmented } from '../components/Segmented';
import { FlaskIcon } from '../components/Icons';
import { ResultMeta } from '../components/ResultMeta';
import {
  hitterTotals,
  naiveMeanOfRates,
  parseStatInput,
  pitcherTotals,
  playerRate,
  pointsFor,
  ratioImpact,
  teamAvg,
  teamEra,
  teamWhip,
  outsFromInnings,
  withDerivedOuts,
  type PlayerLine,
  type Weights,
} from '../lib/fantasyMath';
import { EXAMPLE_SCORING, provenanceDates, provenanceValue, statLabel, type ScoringConfig } from '../lib/scoring';
import { fmt, fmtInt, fmtRate3, fmtSigned } from '../lib/format';

type Group = 'hitter' | 'pitcher';
interface Draft {
  id: string;
  name: string;
  raw: Record<string, string>;
}

const HITTER_BASE = ['R', 'HR', 'RBI', 'SB', 'AB', 'H'];
const PITCHER_BASE = ['W', 'SV', 'K', 'IP', 'ER', 'BBH'];

// Made-up example lines. Hit types sum to H; BB + H allowed sum to BBH, so roto and points views agree.
const EXAMPLE_HITTERS: Draft[] = [
  {
    id: 'h1',
    name: 'Hitter A',
    raw: { R: '85', HR: '28', RBI: '90', SB: '8', AB: '560', H: '151', '1B': '90', '2B': '30', '3B': '3', BB: '60', HBP: '5' },
  },
  {
    id: 'h2',
    name: 'Hitter B',
    raw: { R: '72', HR: '12', RBI: '55', SB: '30', AB: '520', H: '148', '1B': '105', '2B': '26', '3B': '5', BB: '45', HBP: '3' },
  },
  {
    id: 'h3',
    name: 'Hitter C',
    raw: { R: '40', HR: '15', RBI: '50', SB: '2', AB: '300', H: '69', '1B': '40', '2B': '13', '3B': '1', BB: '25', HBP: '2' },
  },
];
const EXAMPLE_PITCHERS: Draft[] = [
  { id: 'p1', name: 'Pitcher A', raw: { W: '13', SV: '0', K: '200', IP: '185', ER: '70', BBH: '215', BB: '50', H: '165', HBP: '6' } },
  { id: 'p2', name: 'Pitcher B', raw: { W: '4', SV: '32', K: '78', IP: '64', ER: '21', BBH: '70', BB: '20', H: '50', HBP: '2' } },
  { id: 'p3', name: 'Pitcher C', raw: { W: '9', SV: '0', K: '130', IP: '150', ER: '75', BBH: '190', BB: '55', H: '135', HBP: '5' } },
];

/** Inputs shown in points mode: the weighted stats, with OUTS entered as IP (outs are derived as IP × 3). */
function pointsInputs(weights: Record<string, string>, group: Group): string[] {
  const keys = Object.keys(weights);
  if (group === 'pitcher') return [...new Set(keys.map((k) => (k === 'OUTS' ? 'IP' : k)))];
  return keys;
}

let nextId = 100;
const toLine = (d: Draft): PlayerLine => ({
  id: d.id,
  name: d.name || 'Unnamed player',
  stats: Object.fromEntries(Object.entries(d.raw).map(([k, v]) => [k, parseStatInput(v)])),
});
const toRawWeights = (w: Weights): Record<string, string> => Object.fromEntries(Object.entries(w).map(([k, v]) => [k, String(v)]));
const fromRawWeights = (w: Record<string, string>): Weights =>
  Object.fromEntries(
    Object.entries(w)
      .map(([k, v]) => [k, Number(v)] as const)
      .filter(([, v]) => Number.isFinite(v)),
  );

/** " · check: 1B + 2B + 3B + HR = 120 but H = 151" when the parts are entered and disagree with the total. */
function consistencyHint(d: Draft, parts: string[], total: string, partsLabel: string, totalLabel: string): string {
  const entered = parts.filter((k) => (d.raw[k] ?? '').trim() !== '');
  if (entered.length < parts.length - 1 || (d.raw[total] ?? '').trim() === '') return '';
  const sum = parts.reduce((acc, k) => acc + parseStatInput(d.raw[k] ?? ''), 0);
  const tot = parseStatInput(d.raw[total] ?? '');
  return Math.abs(sum - tot) > 1e-9 ? ` · check: ${partsLabel} = ${fmtInt(sum)} but ${totalLabel} = ${fmtInt(tot)}` : '';
}

function statName(stat: string, group: Group): string {
  if (stat === 'BBH') return 'BB + H allowed';
  if (stat === 'IP') return 'IP (decimal)';
  return statLabel(stat, group);
}

export default function ValueLab() {
  const state = useData('meta');
  const scoring = useScoring();
  return (
    <>
      <PageHead eyebrow="Illustrative / unvalidated scenario" title="Fantasy Value Lab">
        <p className="lede">
          A calculator for the arithmetic of 5×5 rotisserie and points scoring. Enter or edit a few hypothetical players&apos; season totals and see
          the category line and points they add up to.
        </p>
      </PageHead>
      <Callout kind="illustrative" icon={<FlaskIcon />} title="Illustrative / unvalidated scenario: not a research finding">
        <p>
          Nothing on this page comes from the study&apos;s models. It contains no real player projections and no 2027 forecasts; the example lines
          are made up. Ratio categories are always computed from components (total H ÷ total AB; 9 × ER ÷ IP; (BB + H) ÷ IP), never by averaging
          player rates.
        </p>
      </Callout>
      <Gate state={state} what="the calculator">
        {({ meta }) =>
          scoring.status === 'loading' ? (
            <p className="loading" role="status">
              Loading scoring defaults…
            </p>
          ) : (
            <Calculator scoring={scoring.scoring} tierLabel={meta.evidence_tiers.illustrative} sha256={meta.sources_sha256} />
          )
        }
      </Gate>
    </>
  );
}

function Calculator({ scoring, tierLabel, sha256 }: { scoring: ScoringConfig | null; tierLabel: string; sha256: Record<string, string> }) {
  const defaults = scoring ?? EXAMPLE_SCORING;
  const [mode, setMode] = useState<'roto' | 'points'>('roto');
  const [hitters, setHitters] = useState<Draft[]>(EXAMPLE_HITTERS);
  const [pitchers, setPitchers] = useState<Draft[]>(EXAMPLE_PITCHERS);
  const [wB, setWB] = useState<Record<string, string>>(toRawWeights(defaults.batters));
  const [wP, setWP] = useState<Record<string, string>>(toRawWeights(defaults.pitchers));
  const edited = useRef(false);

  useEffect(() => {
    if (!edited.current) {
      setWB(toRawWeights(defaults.batters));
      setWP(toRawWeights(defaults.pitchers));
    }
  }, [defaults]);

  const hitterStats = useMemo(() => (mode === 'points' ? pointsInputs(wB, 'hitter') : HITTER_BASE), [mode, wB]);
  const pitcherStats = useMemo(() => (mode === 'points' ? pointsInputs(wP, 'pitcher') : PITCHER_BASE), [mode, wP]);
  const hLines = hitters.map(toLine);
  const pLines = pitchers.map(toLine);

  return (
    <>
      <div className="card" style={{ marginTop: 16 }}>
        <Segmented<'roto' | 'points'>
          legend="Scoring format"
          value={mode}
          onChange={setMode}
          options={[
            { value: 'roto', label: 'Rotisserie 5×5' },
            { value: 'points', label: 'Points' },
          ]}
        />
        <p className="muted small" style={{ marginTop: 8, marginBottom: 0 }}>
          IP is entered as decimal innings (180⅓ innings = 180.33). Box-score notation such as 180.1 is not converted.
        </p>
      </div>

      <div className="grid-2" style={{ marginTop: 16, alignItems: 'start' }}>
        <PlayerEditor
          group="hitter"
          title="Hitters"
          drafts={hitters}
          stats={hitterStats}
          onChange={setHitters}
          example={EXAMPLE_HITTERS}
          showOuts={false}
        />
        <PlayerEditor
          group="pitcher"
          title="Pitchers"
          drafts={pitchers}
          stats={pitcherStats}
          onChange={setPitchers}
          example={EXAMPLE_PITCHERS}
          showOuts={mode === 'points' && 'OUTS' in wP}
        />
      </div>

      {mode === 'roto' ? (
        <RotoResults hitters={hLines} pitchers={pLines} />
      ) : (
        <PointsResults
          hitters={hLines}
          pitchers={pLines}
          wB={wB}
          wP={wP}
          setWB={(w) => {
            edited.current = true;
            setWB(w);
          }}
          setWP={(w) => {
            edited.current = true;
            setWP(w);
          }}
          reset={() => {
            edited.current = false;
            setWB(toRawWeights(defaults.batters));
            setWP(toRawWeights(defaults.pitchers));
          }}
          scoring={scoring}
        />
      )}

      <div className="card" style={{ marginTop: 16 }}>
        <ResultMeta
          targetDefinition="Season totals that you type in for hypothetical players. No research target is involved."
          population="Only the players entered on this page."
          seasons="None: hypothetical inputs, no real season."
          method="AVG = ΣH ÷ ΣAB; ERA = 9 × ΣER ÷ ΣIP; WHIP = Σ(BB + H) ÷ ΣIP; counting categories are sums; points = Σ weight × stat."
          ciType="None: this is arithmetic on your inputs, with no uncertainty estimate."
          tier={{ key: 'illustrative', label: tierLabel }}
          sources={
            scoring
              ? ['sloan2027_fantasy/fantasy/scoring_weights.json', 'user input']
              : ['user input', 'example weights in src/lib/scoring.ts (not a platform default)']
          }
          sha256={sha256}
        />
      </div>
    </>
  );
}

function PlayerEditor({
  group,
  title,
  drafts,
  stats,
  onChange,
  example,
  showOuts,
}: {
  group: Group;
  title: string;
  drafts: Draft[];
  stats: string[];
  onChange: (d: Draft[]) => void;
  example: Draft[];
  showOuts: boolean;
}) {
  const update = (id: string, patch: Partial<Draft>) => onChange(drafts.map((d) => (d.id === id ? { ...d, ...patch } : d)));
  return (
    <section className="card" aria-labelledby={`${group}-editor`}>
      <div className="card-head">
        <h2 id={`${group}-editor`} className="card-title">
          {title}
        </h2>
        <div className="chip-row">
          <button
            type="button"
            className="btn small"
            onClick={() => onChange([...drafts, { id: `${group[0]}${nextId++}`, name: `${group === 'hitter' ? 'Hitter' : 'Pitcher'} ${drafts.length + 1}`, raw: {} }])}
            disabled={drafts.length >= 12}
          >
            Add {group}
          </button>
          <button type="button" className="btn small ghost" onClick={() => onChange(example)}>
            Reset examples
          </button>
        </div>
      </div>
      <p className="muted small">Hypothetical example lines; replace them with your own numbers.</p>
      {drafts.map((d) => {
        const line = toLine(d);
        return (
          <fieldset key={d.id} className="player-card">
            <legend className="sr-only">{d.name || 'Unnamed player'}</legend>
            <div className="player-head">
              <label className="control" style={{ gap: 3 }}>
                <span className="control-label">Name</span>
                <input className="name-input" type="text" value={d.name} onChange={(e) => update(d.id, { name: e.target.value })} />
              </label>
              <button type="button" className="btn small ghost" onClick={() => onChange(drafts.filter((x) => x.id !== d.id))} aria-label={`Remove ${d.name || 'player'}`}>
                Remove
              </button>
            </div>
            <div className="stat-grid">
              {stats.map((s) => (
                <label key={s}>
                  {statName(s, group)}
                  <input
                    type="number"
                    inputMode="decimal"
                    min={0}
                    step={s === 'IP' ? 0.01 : 1}
                    value={d.raw[s] ?? ''}
                    placeholder="0"
                    onChange={(e) => update(d.id, { raw: { ...d.raw, [s]: e.target.value } })}
                  />
                </label>
              ))}
            </div>
            <p className="derived">
              {group === 'hitter' ? (
                <>
                  Own AVG {fmtRate3(playerRate(line.stats, 'H', 'AB'))}
                  {(line.stats.H ?? 0) > (line.stats.AB ?? 0) ? ' · check: H exceeds AB' : ''}
                  {consistencyHint(d, ['1B', '2B', '3B', 'HR'], 'H', '1B + 2B + 3B + HR', 'H')}
                </>
              ) : (
                <>
                  Own ERA {fmt(playerRate(line.stats, 'ER', 'IP', 9), 2)} · own WHIP {fmt(playerRate(line.stats, 'BBH', 'IP'), 3)}
                  {showOuts ? ` · outs used for points: ${fmtInt(outsFromInnings(line.stats.IP ?? 0))} (IP × 3)` : ''}
                  {consistencyHint(d, ['BB', 'H'], 'BBH', 'BB + H', 'BB + H allowed')}
                </>
              )}
            </p>
          </fieldset>
        );
      })}
      {drafts.length === 0 ? <p className="muted">No players. Add one to start.</p> : null}
    </section>
  );
}

function RotoResults({ hitters, pitchers }: { hitters: PlayerLine[]; pitchers: PlayerLine[] }) {
  const h = hitterTotals(hitters);
  const p = pitcherTotals(pitchers);
  const naiveAvg = naiveMeanOfRates(hitters, 'H', 'AB');
  const naiveEra = naiveMeanOfRates(pitchers, 'ER', 'IP', 9);
  const showWhy =
    (naiveAvg !== null && h.AVG !== null && Math.abs(naiveAvg - h.AVG) >= 0.0005) ||
    (naiveEra !== null && p.ERA !== null && Math.abs(naiveEra - p.ERA) >= 0.005);
  return (
    <section className="section" aria-labelledby="roto-title">
      <h2 id="roto-title">Team 5×5 line</h2>
      <div className="grid-2" style={{ alignItems: 'start' }}>
        <div className="card">
          <h3>Hitting categories</h3>
          <table>
            <caption className="sr-only">Hitting category totals</caption>
            <tbody>
              <TotalRow k="Runs (R)" v={fmtInt(h.R)} />
              <TotalRow k="Home runs (HR)" v={fmtInt(h.HR)} />
              <TotalRow k="Runs batted in (RBI)" v={fmtInt(h.RBI)} />
              <TotalRow k="Stolen bases (SB)" v={fmtInt(h.SB)} />
              <TotalRow k="Batting average (AVG)" v={fmtRate3(h.AVG)} how={`${fmtInt(h.H)} H ÷ ${fmtInt(h.AB)} AB`} />
            </tbody>
          </table>
        </div>
        <div className="card">
          <h3>Pitching categories</h3>
          <table>
            <caption className="sr-only">Pitching category totals</caption>
            <tbody>
              <TotalRow k="Wins (W)" v={fmtInt(p.W)} />
              <TotalRow k="Saves (SV)" v={fmtInt(p.SV)} />
              <TotalRow k="Strikeouts (K)" v={fmtInt(p.K)} />
              <TotalRow k="ERA" v={fmt(p.ERA, 2)} how={`9 × ${fmt(p.ER, 0)} ER ÷ ${fmt(p.IP, 2)} IP`} />
              <TotalRow k="WHIP" v={fmt(p.WHIP, 3)} how={`${fmt(p.BBH, 0)} (BB + H) ÷ ${fmt(p.IP, 2)} IP`} />
            </tbody>
          </table>
        </div>
      </div>

      {showWhy ? (
        <Callout kind="note" title="Why ratios come from components">
          <p>
            {naiveAvg !== null && h.AVG !== null ? (
              <>
                Averaging the hitters&apos; own AVGs would give {fmtRate3(naiveAvg)}, but the team AVG is {fmtRate3(h.AVG)}: a hitter with few
                at-bats cannot count as much as one with many.{' '}
              </>
            ) : null}
            {naiveEra !== null && p.ERA !== null ? (
              <>
                Likewise, the mean of the pitchers&apos; ERAs is {fmt(naiveEra, 2)}, while the team ERA from total ER and IP is {fmt(p.ERA, 2)}.
              </>
            ) : null}{' '}
            The shortcut is shown only to explain the difference; it is never used in the totals.
          </p>
        </Callout>
      ) : null}

      <div className="card" style={{ marginTop: 16 }}>
        <h3>What each player contributes</h3>
        <p className="muted small">
          Counting categories add up directly. For ratio categories, impact = team ratio with the player minus team ratio without the player.
          For ERA and WHIP a negative impact lowers (improves) the team ratio.
        </p>
        <div className="table-scroll" role="region" aria-label="Hitter contributions" tabIndex={0}>
          <table>
            <caption className="sr-only">Hitter contributions</caption>
            <thead>
              <tr>
                <th scope="col">Hitter</th>
                {['R', 'HR', 'RBI', 'SB', 'AB', 'H'].map((s) => (
                  <th key={s} scope="col" className="num">
                    {s}
                  </th>
                ))}
                <th scope="col" className="num">
                  Own AVG
                </th>
                <th scope="col" className="num">
                  Team AVG impact
                </th>
              </tr>
            </thead>
            <tbody>
              {hitters.map((x) => {
                const imp = ratioImpact(hitters, x.id, teamAvg);
                return (
                  <tr key={x.id}>
                    <th scope="row">{x.name}</th>
                    {['R', 'HR', 'RBI', 'SB', 'AB', 'H'].map((s) => (
                      <td key={s} className="num">
                        {fmtInt(x.stats[s] ?? 0)}
                      </td>
                    ))}
                    <td className="num">{fmtRate3(playerRate(x.stats, 'H', 'AB'))}</td>
                    <td className="num">{imp === null ? '—' : fmtSigned(imp, 3).replace(/^([+−])0\./, '$1.')}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="table-scroll" role="region" aria-label="Pitcher contributions" tabIndex={0} style={{ marginTop: 12 }}>
          <table>
            <caption className="sr-only">Pitcher contributions</caption>
            <thead>
              <tr>
                <th scope="col">Pitcher</th>
                {['W', 'SV', 'K', 'IP', 'ER', 'BB + H'].map((s) => (
                  <th key={s} scope="col" className="num">
                    {s}
                  </th>
                ))}
                <th scope="col" className="num">
                  Own ERA
                </th>
                <th scope="col" className="num">
                  ERA impact
                </th>
                <th scope="col" className="num">
                  WHIP impact
                </th>
              </tr>
            </thead>
            <tbody>
              {pitchers.map((x) => {
                const e = ratioImpact(pitchers, x.id, teamEra);
                const w = ratioImpact(pitchers, x.id, teamWhip);
                return (
                  <tr key={x.id}>
                    <th scope="row">{x.name}</th>
                    {['W', 'SV', 'K', 'IP', 'ER', 'BBH'].map((s) => (
                      <td key={s} className="num">
                        {s === 'IP' ? fmt(x.stats[s] ?? 0, 2) : fmtInt(x.stats[s] ?? 0)}
                      </td>
                    ))}
                    <td className="num">{fmt(playerRate(x.stats, 'ER', 'IP', 9), 2)}</td>
                    <td className="num">{e === null ? '—' : fmtSigned(e, 2)}</td>
                    <td className="num">{w === null ? '—' : fmtSigned(w, 3)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function TotalRow({ k, v, how }: { k: string; v: string; how?: string }) {
  return (
    <tr>
      <th scope="row" style={{ fontWeight: 550 }}>
        {k}
        {how ? <div className="muted small">{how}</div> : null}
      </th>
      <td className="num" style={{ fontSize: '1.1rem', fontWeight: 650 }}>
        {v}
      </td>
    </tr>
  );
}

function PointsResults({
  hitters,
  pitchers,
  wB,
  wP,
  setWB,
  setWP,
  reset,
  scoring,
}: {
  hitters: PlayerLine[];
  pitchers: PlayerLine[];
  wB: Record<string, string>;
  wP: Record<string, string>;
  setWB: (w: Record<string, string>) => void;
  setWP: (w: Record<string, string>) => void;
  reset: () => void;
  scoring: ScoringConfig | null;
}) {
  const bw = fromRawWeights(wB);
  const pw = fromRawWeights(wP);
  const hPts = hitters.map((x) => ({ x, pts: pointsFor(x.stats, bw) }));
  const pPts = pitchers.map((x) => ({ x, pts: pointsFor(withDerivedOuts(x.stats), pw) }));
  const hTotal = hPts.reduce((s, r) => s + r.pts, 0);
  const pTotal = pPts.reduce((s, r) => s + r.pts, 0);
  const format = scoring ? provenanceValue(scoring, ['format']) : undefined;
  const source = scoring ? provenanceValue(scoring, ['source', 'platform', 'url']) : undefined;
  const dateField = scoring ? provenanceValue(scoring, ['date', 'retrieved', 'verified', 'as_of', 'accessed']) : undefined;
  const dates = scoring ? provenanceDates(scoring) : [];
  const date = dateField ?? (dates.length ? dates.join(', ') : undefined);

  return (
    <section className="section" aria-labelledby="points-title">
      <h2 id="points-title">Points</h2>
      <Callout kind={scoring ? 'info' : 'caution'} title={scoring ? 'Default weights from scoring.json' : 'Example weights (not any platform default)'}>
        {scoring ? (
          <>
            {format ? (
              <p>
                <strong>Format:</strong> {format}
              </p>
            ) : null}
            <p>
              <strong>Source:</strong> {source ?? 'not stated in scoring.json'}
            </p>
            <p>
              <strong>Date{dates.length > 1 && !dateField ? 's' : ''}:</strong> {date ?? 'not stated in scoring.json'}
            </p>
            <p className="muted small">
              Pitcher outs are derived from the IP you enter (outs = IP × 3). Hitting points use singles, doubles and triples, so enter hit types
              as well as H.
            </p>
            {scoring.provenance.length ? (
              <details className="data-table">
                <summary>All provenance fields</summary>
                <dl className="meta">
                  {scoring.provenance.map((p) => (
                    <PDef key={p.key} k={p.key} v={p.value} />
                  ))}
                </dl>
              </details>
            ) : null}
          </>
        ) : (
          <p>
            No verified scoring file (scoring.json) is bundled with this build, so these round example weights are used. Edit them to match your
            league.
          </p>
        )}
      </Callout>
      <div className="grid-2" style={{ alignItems: 'start' }}>
        <WeightEditor title="Hitter weights" group="hitter" weights={wB} onChange={setWB} />
        <WeightEditor title="Pitcher weights" group="pitcher" weights={wP} onChange={setWP} />
      </div>
      <p>
        <button type="button" className="btn small" onClick={reset}>
          Reset weights to defaults
        </button>
      </p>
      <div className="card">
        <h3>Points by player</h3>
        <div className="table-scroll" role="region" aria-label="Points by player" tabIndex={0}>
          <table>
            <caption className="sr-only">Points by player</caption>
            <thead>
              <tr>
                <th scope="col">Player</th>
                <th scope="col">Group</th>
                <th scope="col" className="num">
                  Points
                </th>
              </tr>
            </thead>
            <tbody>
              {hPts.map(({ x, pts }) => (
                <tr key={x.id}>
                  <th scope="row">{x.name}</th>
                  <td>Hitter</td>
                  <td className="num">{fmt(pts, 1)}</td>
                </tr>
              ))}
              {pPts.map(({ x, pts }) => (
                <tr key={x.id}>
                  <th scope="row">{x.name}</th>
                  <td>Pitcher</td>
                  <td className="num">{fmt(pts, 1)}</td>
                </tr>
              ))}
              <tr>
                <th scope="row">Hitters total</th>
                <td />
                <td className="num">
                  <strong>{fmt(hTotal, 1)}</strong>
                </td>
              </tr>
              <tr>
                <th scope="row">Pitchers total</th>
                <td />
                <td className="num">
                  <strong>{fmt(pTotal, 1)}</strong>
                </td>
              </tr>
              <tr>
                <th scope="row">Team total</th>
                <td />
                <td className="num" style={{ fontSize: '1.1rem' }}>
                  <strong>{fmt(hTotal + pTotal, 1)}</strong>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function PDef({ k, v }: { k: string; v: string }) {
  return (
    <>
      <dt>{k}</dt>
      <dd>{v}</dd>
    </>
  );
}

function WeightEditor({
  title,
  group,
  weights,
  onChange,
}: {
  title: string;
  group: Group;
  weights: Record<string, string>;
  onChange: (w: Record<string, string>) => void;
}) {
  return (
    <fieldset className="card">
      <legend className="card-title" style={{ float: 'left', width: '100%', marginBottom: 8, fontSize: '1rem', fontWeight: 650, color: 'var(--text-1)' }}>
        {title}
      </legend>
      <div className="stat-grid" style={{ clear: 'both' }}>
        {Object.keys(weights).map((s) => (
          <label key={s}>
            {statName(s, group)}
            <input
              type="number"
              inputMode="decimal"
              step={0.5}
              value={weights[s]}
              onChange={(e) => onChange({ ...weights, [s]: e.target.value })}
            />
          </label>
        ))}
      </div>
      <p className="muted small" style={{ marginTop: 8, marginBottom: 0 }}>
        Points per unit of each stat; negative values subtract.
      </p>
    </fieldset>
  );
}
