# 00 — Inventory, source of truth, preservation, and top risks

**Date:** 2026-11-13 · **Paper:** MIT Sloan SSAC 2027, Baseball track, Paper ID 18 · **Deadline:** Tue 2026-12-01, 11:59 p.m. ET = **8:59 p.m. Pacific**

## 1. Repositories and what each one is for

| Location | Role | State on 2026-11-13 |
|---|---|---|
| `github.com/shirinalapati/MIT_Sloan_2027_Fantasy_Baseball_Projection_Lab_Paper` (this repo; local clone `~/MIT_Sloan_2027_Fantasy_Baseball_Projection_Lab_Paper`) | Fantasy extension, new experiments, revised manuscript, new fantasy web app | Public, created 2026-11-13 22:57 UTC, empty at start. The author instructed that it be used for this work. |
| `github.com/shirinalapati/Projection-Signal-Lab` (local `~/Future_Predictor`) | Original study, preprint, original companion site | `main` @ `1571d28` (pushed earlier with approval). **Not modified by this work.** |
| Local branch `research/sloan-2027` @ `04fddeb` (worktree `.worktrees/sloan-2027`) | Nov 11–12 Sloan reanalysis: nested admission, 2026 check, player analysis, prior draft manuscript | Private. Its history contains player-level data, so it must **never be pushed**. This repo reads from it but never writes to it. |
| Local branch `public/sloan-2027` @ `e82b4ac` | Publishable version of the reanalysis (no player-level files) | Not pushed. |
| `https://future-predictor-green.vercel.app/` (deployed from `research/` of the original repo) | Original research companion | **Untouched.** |

The author's main checkout also contains uncommitted edits (`src/psl/catalog.py`, `src/psl/components.py`) and untracked K%-target files from the Phillies trial branch. These were **not used and not touched**, per the author's earlier instruction to exclude Phillies trial material.

## 2. Source of truth

1. **Canonical study:**
   - commit `17da742`;
   - canonical artifacts in `artifacts/` (the 208 admission evaluations, kitchen-sink comparisons);
   - data panels in `data/` (from the research bundle; 632/632 files verified in Phase 0 on 2026-11-12).
2. **Reanalysis evidence:** `research/sloan-2027` @ `04fddeb`:
   - `sloan2027/results/` (nested admission, comparisons, frozen 2026 predictions, player files);
   - `sloan2027/tables/`, `sloan2027/FINAL_REPORT.md`.
3. **Prior manuscript:** `sloan2027/paper/sloan_2027_manuscript.docx` and its proof. These are a **previous Claude draft, not final and not approved.** They are used only as provenance and as a starting point for template mechanics.
4. **Official template:** `sloan2027/paper/SSAC_Paper_Template_official.docx` (downloaded 2026-11-12 from the organizers' Google Docs link) and `~/Downloads/Paper Template.pdf`.

SHA-256 of every reused artifact: [`provenance/reused_artifacts_sha256.csv`](provenance/reused_artifacts_sha256.csv), 41 files.

## 3. Feedback sources found and not found
- **Found:** `~/Downloads/Cluely_Meredith_Sloan_2027_Reference.docx` (Nov 11). It is the author's *pre-meeting* conversation brief, not a meeting record. It confirms that Phil Birnbaum said he was not qualified to judge technical specifics, and records the original example numbers.
- **Not found on disk:**
  - the Nov 12 meeting transcript;
  - Meredith's comment screenshots;
  - a separate Phil Birnbaum feedback file;
  - `Sloan_2027_Referee_Review_Paper18.md`.
  The master prompt's §C (Meredith, Phil) and §F2 (seven referee concerns) are therefore treated as the authoritative record of that feedback. Nothing beyond them is attributed to the reviewers.
- **Found:** `~/Downloads/Sloan2027_Paper18_for_review.zip` (12 MB). It intentionally omits player-level files. **It is not the full repository.** The full private worktree does contain:
  - `results/holdout2026/frozen_predictions_2026.parquet` (sha256 `af61b2b8…`, committed `f8023bf` before the 2026 download);
  - `results/players/illustrative_cases.csv` and `forecast_changes.parquet`;
  - all modeling panels.
  All are verified present and hashed.

## 4. Phase 1 re-verification (run 2026-11-13 23:06–23:09 UTC, commit `04fddeb`)
Log: [`audits/phase1_reverification_2026-11-13.log`](audits/phase1_reverification_2026-11-13.log)
- `pytest tests sloan2027/tests`: **71 passed** (67 original + 4 temporal-leakage tests).
- `p0_reproduce.py` (canonical engine re-run of all six studies, 161 s), then `p0_diff.py`: **55/55 checks match**. These include 402 registry fields, 208 evaluations, 163 unique features, and every selective and kitchen-sink RMSE.
- `p0_kitchen_population_check.py`: the published FIP selective-vs-kitchen RMSEs come from different rows (1,699 vs 1,866). This is a known issue (R2).
- `e3_audit.py`: all leakage and provenance checks pass.
- **Immutable baseline:** 873/873 files are byte-identical to the 2026-11-12 manifest (canonical artifacts, preprint, public site).
- The test run rewrote three timing-only files (`*_leaktest_*_meta.json` "seconds", `p0_repro/run_log.json`). They were restored with `git checkout`, and the research worktree is clean.

## 5. Code and data paths used by this repository
- `PSL_ROOT` (env var; default `~/Future_Predictor/.worktrees/sloan-2027`): read-only source of `src/psl`, `data/`, `artifacts/`, `sloan2027/results/`.
- Player-level outputs go to `local/` in this repo, which is git-ignored.
- Aggregate outputs go to `sloan2027_fantasy/fantasy/`, `sloan2027_fantasy/audits/`, and `app/public/data/`.
- **Python:** the research worktree's `.venv` (Python 3.13; pandas, scikit-learn, lightgbm, python-docx). Pins are in `requirements.txt`.
- **App:** Node 24 / npm 11, under `app/`.

## 6. App status at start
- The original companion is a static HTML site (`research/*.html`) deployed on Vercel. It stays as is.
- The new fantasy app is a **separate, independently deployable project** in `app/` of this repository, with a root `vercel.json`. Nothing is deployed without the author's go-ahead.

## 7. Top risks (and how they are handled)
1. **Blind review vs a public, author-named repository.** The repo URL names the author. The blind manuscript contains no names, and named copies stay local (git-ignored). This needs an organizer answer (draft email exists; not sent).
2. **Data rights.**
   - MLBAM (Savant, Stats API) and Baseball-Reference terms restrict redistribution.
   - No raw tables or player-season panels are committed.
   - The app ships aggregate results plus a *curated* casebook (420 player-seasons: the study's own forecasts and public season outcomes). That is an author decision, flagged here.
3. **2026 is not a prospective trial.** It is frozen-in-workflow and retrospective. Several 2026 intervals include zero. Any new 2026 analysis (the fantasy bridge) is exploratory.
4. **Conditional populations.**
   - Historical evaluations require next-season playing time.
   - The fantasy pools include non-returners (scored zero) to reduce this bias.
   - Rookies and sub-threshold players remain excluded.
5. **Taxonomy is partly human-specified.** "Context" comes from role labels. "Diagnostic" versus "Exclude" comes from a human `process` flag. This is stated in the paper and the app.
6. **Multiplicity and few seasons.** Five outer seasons; the bootstrap does not capture common season shocks. Season-block intervals are reported as a sensitivity.
7. **No Microsoft Word on this machine.** Proofs come from LibreOffice with a Cambria-metric font. The author must do a final check in Word.
8. **Scope creep.** The fantasy bridge is kept separate from the metric-to-target admission study and labeled exploratory.
9. **Deadline:** 8:59 p.m. Pacific on Dec 1. Submission requires the author's Google sign-in. Claude cannot and will not submit.
