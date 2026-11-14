# Reproducing the fantasy extension, figures, manuscript and app data

This repository extends the study in [Projection-Signal-Lab](https://github.com/shirinalapati/Projection-Signal-Lab). That repository is left unchanged. The research code here reads its data panels and November 2026 reanalysis outputs from a local checkout. Nothing here writes to that checkout.

## 1. Prerequisites
1. **A Projection-Signal-Lab checkout** with:
   - `data/` and `artifacts/` rebuilt from the original sources. Follow that repository's `REPRODUCING.md`. MLB Advanced Media and Sports Reference terms restrict redistribution, so these files are not shipped. Sports Reference also asks for written permission before automated access.
   - The reanalysis outputs under `sloan2027/results/`. These are produced by `sloan2027/reproducibility/run_all.sh` on the reanalysis branch.
   Set `PSL_ROOT` to that checkout.
2. **Python 3.13** with `pip install -r requirements.txt`. The checkout's `src/` is added to `sys.path` automatically.
3. **For the manuscript:** the organizers' SSAC Word template. Set `SSAC_TEMPLATE=/path/to/template.docx`; the template is not redistributed here.
4. **For the app:** Node 24 and npm 11 (see `app/README.md`).

## 2. Run order (all scripts are deterministic; seed 42)
```bash
export PSL_ROOT=/path/to/Projection-Signal-Lab
cd sloan2027_fantasy/experiments
python fb01_outcomes.py        # pools, fantasy outcomes, coverage and cohort tables                 (~5 s)
python fb02_upstream.py        # out-of-time target forecasts; asserts equality with E1/frozen 2026  (~5 s)
python fb03_bridge.py          # fantasy-bridge models, bootstraps, multiplicity                    (~3 min)
python fb04_decision.py        # illustrative draft backtest                                         (~20 s)
python fbg_era_admission.py    # new-target (ERA) nested admission                                   (~3 min)
python fb05_summaries.py       # summary, negative findings, claims ledger, player-level manifest
python export_app_data.py      # app/public/data/*.json with SHA-256 of every source artifact
cd .. && python figures/make_figures.py          # Figures 1-7 (+ data CSVs)
cd paper && python make_fantasy_refs.py && python build_content.py   # DOCX (blind + named) + claims_to_evidence.csv
cd ../.. && python -m pytest sloan2027_fantasy/tests -q   # 8 tests; data-dependent tests skip without PSL_ROOT
```

## 3. Verifying a rebuild
- **Player-level outputs.** These stay in git-ignored `local/`. Their row counts and SHA-256 hashes are in `sloan2027_fantasy/fantasy/player_level_manifest.json`.
- **Reused reanalysis artifacts.** Hashes are in `sloan2027_fantasy/provenance/reused_artifacts_sha256.csv`.
- **Upstream forecasts.** `fb02_upstream.py` fails unless the upstream test-row forecasts reproduce the E1 and frozen-2026 predictions to 1e-9. The observed maximum difference is 1.8e-15.
- **Timing of the analysis plan.** The protocol (`fantasy/experiment_protocol.md`) and its amendment were pushed as commits `8819791` and `b482448`, before the corresponding models were fit.

## 4. Proof rendering
Microsoft Word was not available. Proofs were made with LibreOffice 26.8.2 using the Caladea font (metric-compatible with Cambria), loaded from a private profile:
`soffice -env:UserInstallation=file:///tmp/lo-profile --headless --convert-to pdf <docx>`, with the Caladea TTFs in `<profile>/user/fonts/`.
