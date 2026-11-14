# Reviewer packet: Paper 18, revised full paper (for Meredith Wills and Billy)

**What to read:** `paper/sloan_2027_fantasy_revised_proof.pdf`, 28 pages including references and appendices. The core argument is pages 1–22. Nothing has been sent to anyone yet; the author will share this packet herself.

## The paper in plain language
1. **The question.** A baseball statistic can describe a player well and still add nothing to next season's forecast once the model already knows his recent record.
2. **The method.** The paper turns that into a simple, auditable rule. A metric earns a place in a forecast only if adding it makes forecasts of seasons the model hasn't seen more accurate, by a meaningful and consistent amount.
3. **The six targets.** The rule is applied separately to wOBA, FIP, baserunning, fielding, hitter WAR and pitcher WAR. The same metric can have different jobs: sprint speed helps baserunning forecasts and is useless for wOBA.
4. **The fantasy test.** The new part asks whether these forecasts help with categories fantasy players actually score: HR, SB, AVG, ERA, WHIP and so on. The test was written down and time-stamped before it was run.
5. **What it found.**
   - The FIP forecast improves ERA and WHIP forecasts a little, about 1%.
   - Most other links do not survive a fair test.
   - Raw sprint speed helps stolen-base forecasts, and Barrel% helps home-run forecasts.
   - Better forecasts did not pick detectably better players in a simple draft simulation.

## What changed after your feedback
- **Fantasy is the application context, not a new study.** The six targets and 2015–2025 data are unchanged (Section 2 explains each target, including why defense and WAR stay).
- **"Unstable" is defined four separate ways** (Table 4).
- **Business-style terms are defined with baseball examples.** The paper also says which labels are human choices (Table 3).
- **Seven figures carry the argument:** a decision-flow diagram, the classification map, model comparisons, season-by-season results, named player stories, a fantasy linkage map and a draft backtest.
- **Phil Birnbaum's requests:**
  - results in FIP and wOBA units;
  - named players in both directions, e.g., Tyler Rogers (a submariner) whose low Stuff+ made every forecast worse, and Zack Wheeler, where it helped every time;
  - K% versus K-BB% explained.
- **A real Discussion section**, with a front-office limitation and public-data compression stated plainly.

## Where your judgment would help most
1. **Is the fantasy framing convincing?** Is "which public metrics deserve to change a forecast" the right pitch for fantasy readers?
2. **Is Section 2 (why these six targets) persuasive**, especially keeping defense as a boundary case?
3. **Are the player stories (Section 7, Figure 5) the right examples?** Would different players make the point better?
4. **Is the paper too long?** 22 pages of argument. What would you cut first?
5. **Do the honest negative results help or hurt the paper's impact?** These include the FIP reversal in 2026, the WAR results, and most fantasy links being null.

## Open questions for the author (not decided by Claude)
- **Anonymity.** The repository link names the author. The blind manuscript omits names and links.
- **Data rights.** No raw MLB or Baseball-Reference data are shared. Sports Reference asks for permission before automated access.
- **Subtitle.** A fantasy-facing subtitle is optional.
- **Deployment.** Whether to deploy the companion web app publicly.
