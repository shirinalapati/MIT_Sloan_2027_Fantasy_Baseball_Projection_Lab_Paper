# Reviewer packet: Paper 18, revised full paper (for Meredith Wills and Billy)

**Status (2026-11-13):** this version was revised after an internal referee-style review (`audits/referee_self_review.md`). How each issue was handled is listed in `FINAL_REPORT.md`, Section 3. Nothing has been submitted or sent; the author will share this packet.

**What to read:** `paper/sloan_2027_fantasy_revised_proof.pdf`, 38 pages:
- main text: pages 1–29;
- appendices: pages 30–33;
- references: pages 34–38.

## The paper in plain language
1. **The question.** A baseball statistic can describe a player well and still add nothing to next season's forecast once the model already knows the player's recent record.
2. **The method.** The paper turns that into a simple, auditable rule. A metric earns a place in a forecast only if adding it makes forecasts of seasons the model hasn't seen more accurate, by a meaningful and consistent amount.
3. **The six targets.** The rule is applied separately to wOBA, FIP, baserunning, fielding, hitter WAR and pitcher WAR. The same metric can have different jobs: sprint speed helps baserunning forecasts and is useless for wOBA.
4. **The fantasy test.** The new part asks whether these forecasts help with categories fantasy players actually score: HR, SB, AVG, ERA, WHIP and so on. The test plan was written down and time-stamped before any fantasy model was fit.
5. **What it found.**
   - **FIP forecasts:** they improve ERA and WHIP forecasts a little, about 1%, beyond each pitcher's own ERA and WHIP history. The gain reversed in 2023, so with five seasons it is not yet clear that it holds season to season.
   - **Other links:** most do not survive a fair test.
   - **Exploratory checks:** raw sprint speed helps stolen-base forecasts, and Barrel% helps home-run forecasts.
   - **Fielding:** the fielding forecast's gain comes entirely from using a third season of history, not from any new metric.
   - **Draft simulation:** better forecasts did not pick detectably better players in a simple draft simulation.

## What changed after your feedback
- **Fantasy is the application context, not a new study.** The six targets and 2015–2025 data are unchanged. Section 2 explains each target, including why defense and WAR stay.
- **"Unstable" is defined four separate ways** (Table 4).
- **Business-style terms are defined with baseball examples.** The paper also says which labels are human choices (Table 3).
- **Seven figures carry the argument:**
  - a decision-flow diagram;
  - the classification map;
  - model comparisons;
  - season-by-season results;
  - named player stories;
  - a fantasy linkage map;
  - a draft backtest.
- **Phil Birnbaum's requests:**
  - results in FIP and wOBA units (Table 5);
  - named players in both directions:
    - Tyler Rogers, a submariner whose low Stuff+ made his FIP forecast worse in all five seasons;
    - Zack Wheeler, for whom Stuff+ helped in all five;
    - a table of cases picked by a fixed rule (Table 7), such as Ben Rice and Alex Kirilloff for xwOBA;
  - K% versus K-BB% explained (Section 5.4).
- **A real Discussion section** (Section 10), with a front-office limitation and public-data compression stated plainly.

## Where your judgment would help most
1. **Is the fantasy framing convincing?** Is "which public metrics deserve to change a forecast" the right pitch for fantasy readers?
2. **Is Section 2 (why these six targets) persuasive**, especially keeping defense as a boundary case?
3. **Are the player stories (Section 7, Figure 5, Table 7) the right examples?** Would different players make the point better?
4. **Is the paper too long?** It has 29 pages of main text. What would you cut first?
5. **Do the honest negative results help or hurt the paper's impact?** These include:
   - the all-metric model beating selection for FIP in 2026;
   - the WAR results;
   - most fantasy links being null.

## Open questions for the author (not decided by Claude)
- **Anonymity.** The repository link names the author. The blind manuscript omits names and links.
- **Data rights.** No raw MLB or Baseball-Reference data are shared. Sports Reference asks for permission before automated access.
- **Subtitle.** A fantasy-facing subtitle is optional.
- **Deployment.** Whether to deploy the companion web app publicly.
