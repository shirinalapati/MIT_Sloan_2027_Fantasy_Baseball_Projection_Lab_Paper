# Novelty guardrails

IDs: `references_verified.md`.

## Close prior work

- **Szymborski 2023 [D13]:** do Statcast xStats improve next-year prediction alongside actual stats? Tested separately for BA, OBP, SLG, wOBA.
- **Judge 2018a [D11]:** xBA/xwOBA versus FIP/DRA for pitchers (next-year prediction, reliability); small gains. **Judge 2018b [D12]:** descriptive/reliability/predictive framework.
- **Bailey et al. 2020 [C9]:** Statcast predictions combined with PECOTA improve batting-average forecasts.
- **Piette et al. 2010 [C5]; McShane et al. 2011 [C6]:** which metrics carry persistent signal, with multiplicity control. Rankings differ between starters and relievers.
- **Franks et al. 2016 [C7]:** "independence" meta-metric (does a metric add new information?).
- **Reliability:** Carleton [D8–D10]; Albert 2006 [C4].
- **Incremental validity:** Hunsley & Meyer 2003 [F1]; Pencina et al. 2008 [F2]. **Forecast comparison:** Diebold & Mariano 1995 [A12].
- **Selection bias and nested CV:** Ambroise & McLachlan 2002 [A1]; Varma & Simon 2006 [A2]; Cawley & Talbot 2010 [A3].
- **Out-of-time evaluation:** Tashman 2000 [A6]; Bergmeir & Benítez 2012 [A5].

## Do NOT claim to be first to

1. Test whether Statcast metrics add predictive value beyond traditional statistics or projections (D11, D13, C9).
2. Show that a metric's usefulness depends on the outcome or player role (C5, D13).
3. Evaluate sports metrics for incremental or independent information (C6, C7).
4. Identify feature-selection bias, or use nested or forward-in-time validation (A1–A3, A5, A6).
5. Test added predictive value or incremental validity (F1, F2).
6. Benchmark against a simple projection baseline (Marcel [B7]; PECOTA comparisons [D4]).

Cite no peer-reviewed fantasy-baseball valuation work; none was found (J2).

## Safer framing

Claim only the specific combination the paper implements. Example: a fixed admission rule applied per target against one baseline, under out-of-time validation with multiplicity control. Qualify it with "to our knowledge" and limit it to the seasons and data studied.
