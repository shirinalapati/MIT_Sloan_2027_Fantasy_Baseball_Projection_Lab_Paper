# Reference verification: complete list

**Paper:** "One Metric, Different Jobs: Target-Specific Feature Admission for Major League Baseball Player Projection" (MIT Sloan Sports Analytics Conference 2027, Baseball track)

**Checked:** 2026-11-13 (new entries). Entries A1–A17 come from the 2026-11-11/12 pass and were copied without re-checking, as instructed.

**Method.** No bibliographic field comes from memory. Every field was read from one of these sources:
- **Crossref:** the REST API record `https://api.crossref.org/works/{DOI}` for every DOI. DOIs were first located with Crossref bibliographic search.
- **OpenAlex:** `https://api.openalex.org/works/doi:{DOI}`, used only to read abstracts and issue numbers where Crossref had none. The publisher (De Gruyter) returned a bot challenge.
- **Publisher and official pages:** fetched directly and converted to text. Bylines and dates come from the page text or its `article:published_time` metadata.
- **Open Library catalog records:** for book ISBNs, publishers, and dates.

The DOI or stable URL is the last element of each citation.

**Type codes:** PR = peer-reviewed journal article · BK = book · PP = preprint (not peer-reviewed) · GL = official glossary, help, or methodology page · AA = analytics article (practitioner, not peer-reviewed) · DS = data, software, or news source.

## Summary

| Group | Count | Result |
|---|---|---|
| A. Previously verified (copied) | 17 | 17 VERIFIED (16 via Crossref or publisher, plus Holm verified manually) |
| B. Items already in `references.md` but not among the 17, re-checked now | 16 | 15 VERIFIED (5 corrected or completed: B5, B6, B7, B9, B11), 1 PARTLY VERIFIED (B8, PECOTA book chapter) |
| C–G. New scholarly and analytic references | 36 (D2 repeats B7 and is not counted) | 36 VERIFIED: 21 peer-reviewed, 3 books, 10 analytics articles, 1 glossary page, 1 preprint |
| H–I. New official definition and methodology pages | 40 | 40 VERIFIED (page read 2026-11-13) |
| J. Not verified, not found, or rejected | 7 | See Part J |

---

## A. Previously verified (copied; not re-checked)

| ID | Status | APA-style citation | Verified via | Type |
|---|---|---|---|---|
| A1 | VERIFIED (2026-11-11) | Ambroise, C., & McLachlan, G. J. (2002). Selection bias in gene extraction on the basis of microarray gene-expression data. *Proceedings of the National Academy of Sciences, 99*(10), 6562–6566. https://doi.org/10.1073/pnas.102102699 | Crossref | PR |
| A2 | VERIFIED (2026-11-11) | Varma, S., & Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics, 7*, 91. https://doi.org/10.1186/1471-2105-7-91 | Crossref | PR |
| A3 | VERIFIED (2026-11-11) | Cawley, G. C., & Talbot, N. L. C. (2010). On over-fitting in model selection and subsequent selection bias in performance evaluation. *Journal of Machine Learning Research, 11*(70), 2079–2107. https://www.jmlr.org/papers/v11/cawley10a.html | jmlr.org page and BibTeX (no DOI) | PR |
| A4 | VERIFIED (2026-11-11) | Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B, 57*(1), 289–300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x | Crossref | PR |
| A5 | VERIFIED (2026-11-11) | Bergmeir, C., & Benítez, J. M. (2012). On the use of cross-validation for time series predictor evaluation. *Information Sciences, 191*, 192–213. https://doi.org/10.1016/j.ins.2011.12.028 | Crossref | PR |
| A6 | VERIFIED (2026-11-11) | Tashman, L. J. (2000). Out-of-sample tests of forecasting accuracy: An analysis and review. *International Journal of Forecasting, 16*(4), 437–450. https://doi.org/10.1016/S0169-2070(00)00065-0 | Crossref | PR |
| A7 | VERIFIED (2026-11-11) | Meinshausen, N., & Bühlmann, P. (2010). Stability selection. *Journal of the Royal Statistical Society: Series B, 72*(4), 417–473. https://doi.org/10.1111/j.1467-9868.2010.00740.x | Crossref | PR |
| A8 | VERIFIED (2026-11-11) | Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. In I. Guyon et al. (Eds.), *Advances in Neural Information Processing Systems 30* (NIPS 2017). Curran Associates. https://proceedings.neurips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html | proceedings.neurips.cc page and BibTeX (no DOI, no pages) | PR (conference) |
| A9 | VERIFIED (2026-11-11) | Hoerl, A. E., & Kennard, R. W. (1970). Ridge regression: Biased estimation for nonorthogonal problems. *Technometrics, 12*(1), 55–67. https://doi.org/10.1080/00401706.1970.10488634 | Crossref | PR |
| A10 | VERIFIED (2026-11-11) | Zou, H., & Hastie, T. (2005). Regularization and variable selection via the elastic net. *Journal of the Royal Statistical Society: Series B, 67*(2), 301–320. https://doi.org/10.1111/j.1467-9868.2005.00503.x | Crossref | PR |
| A11 | VERIFIED (2026-11-11) | Guyon, I., & Elisseeff, A. (2003). An introduction to variable and feature selection. *Journal of Machine Learning Research, 3*, 1157–1182. https://www.jmlr.org/papers/v3/guyon03a.html | jmlr.org page (no DOI) | PR |
| A12 | VERIFIED (2026-11-11) | Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599 | Crossref | PR |
| A13 | VERIFIED (2026-11-11) | Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008). Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics, 90*(3), 414–427. https://doi.org/10.1162/rest.90.3.414 | Crossref | PR |
| A14 | VERIFIED (2026-11-11) | Nogueira, S., Sechidis, K., & Brown, G. (2018). On the stability of feature selection algorithms. *Journal of Machine Learning Research, 18*(174), 1–54. https://www.jmlr.org/papers/v18/17-514.html | jmlr.org page and BibTeX (no DOI) | PR |
| A15 | VERIFIED (2026-11-11) | Kalousis, A., Prados, J., & Hilario, M. (2007). Stability of feature selection algorithms: A study on high-dimensional spaces. *Knowledge and Information Systems, 12*(1), 95–116. https://doi.org/10.1007/s10115-006-0040-8 | Crossref | PR |
| A16 | VERIFIED (2026-11-11) | Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881 | Crossref | PR |
| A17 | VERIFIED, manual (2026-11-12) | Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics, 6*(2), 65–70. https://www.jstor.org/stable/4615733 | Volume, pages, and JSTOR 4615733 confirmed by two independent sources. The DOI 10.2307/4615733 listed by one aggregator did not resolve, so no DOI is given. | PR |

The full editor list for A8 and other field-level details are in the 2026-11-11 file (`sloan2027/paper/references_verified.md`).

---

## B. Items already in `references.md` (status P or S), re-checked 2026-11-13

| ID | Status | APA-style citation | Verified via | Type |
|---|---|---|---|---|
| B1 | VERIFIED | Shmueli, G. (2010). To explain or to predict? *Statistical Science, 25*(3), 289–310. https://doi.org/10.1214/10-STS330 | Crossref | PR |
| B2 | VERIFIED | MLB.com. (n.d.). *Statcast*. MLB Glossary. Retrieved November 13, 2026, from https://www.mlb.com/glossary/statcast | Page read | GL |
| B3 | VERIFIED | MLB.com. (n.d.). *Expected weighted on-base average (xwOBA)*. MLB Glossary. Retrieved November 13, 2026, from https://www.mlb.com/glossary/statcast/expected-woba | Page read | GL |
| B4 | VERIFIED | MLB.com. (n.d.). *Sprint speed (SS)*. MLB Glossary. Retrieved November 13, 2026, from https://www.mlb.com/glossary/statcast/sprint-speed | Page read | GL |
| B5 | VERIFIED, **corrected** | Langin, C. (2021, December 13). *Pitch design: What is Stuff+? Quantifying pitches with pitch models*. Driveline Baseball. https://www.drivelinebaseball.com/blogs/blog/what-is-stuff-quantifying-pitches-with-pitch-models | Page text: byline "By Chris Langin, Pitching Trainer"; `datePublished` 2021-12-13 | AA |
| B6 | VERIFIED, **corrected** | McGrattan, O. (2023, March 10). *Stuff+, Location+, and Pitching+ primer*. FanGraphs Library. https://library.fangraphs.com/pitching/stuff-location-and-pitching-primer/ | Page text: byline and date | GL |
| B7 | VERIFIED, **corrected** | Tango, T. [Tangotiger]. (2004, March 10). *The 2004 Marcels*. Tango on Baseball Archives. http://www.tangotiger.net/archives/stud0346.shtml. Hub page: Tango, T. [Tangotiger]. (n.d.). *Marcel 2012*. https://tangotiger.net/marcel/ | Both pages read. The method steps (5/4/3 weights, 1,200 PA of league average, age factor) appear in the 2004 page. | AA (primary description) |
| B8 | **PARTLY VERIFIED** | Silver, N. (2003). Introducing PECOTA. In G. Huckabay et al., *Baseball Prospectus 2003*. Brassey's. | The book was verified in the Open Library catalog: Brassey's, Inc., Dulles, VA, 2003; ISBN 1-57488-561-8 (978-1-57488-561-3); OCLC 52447792; by-statement "[by Gary Huckabay ... [et al.]]". The chapter title and page range were **not** verified. See Part J and the verified alternatives D3–D6. | BK chapter |
| B9 | VERIFIED, **corrected** | Szymborski, D. (2020, November 10). *The 2021 ZiPS projections: An introduction*. FanGraphs. https://blogs.fangraphs.com/the-2021-zips-projections-an-introduction/ | Page text and metadata: 2020-11-10, so **2020**, not 2021 | AA |
| B10 | VERIFIED | MLB.com. (n.d.). *Steamer*. MLB Glossary. Retrieved November 13, 2026, from https://www.mlb.com/glossary/projection-systems/steamer | Page read | GL |
| B11 | VERIFIED, **byline added** | Kadlick, M. (2025, September 23). *MLB to implement challenge system for balls and strikes ahead of 2026 season*. Sports Illustrated. https://www.si.com/mlb/mlb-abs-challenge-system-rule-2026 | Page metadata: headline, author, `datePublished` | DS (news) |
| B12 | VERIFIED (resolves) | Baseball Savant (MLB Advanced Media). (n.d.). *Custom leaderboards and Statcast search*. https://baseballsavant.mlb.com/ | HTTP 200 | DS |
| B13 | VERIFIED (resolves) | MLB Advanced Media. (n.d.). *MLB Stats API*. https://statsapi.mlb.com/ | HTTP 200/206 on /api/v1/sports | DS |
| B14 | VERIFIED (resolves) | Sports Reference LLC. (n.d.). *Baseball-Reference.com WAR data files* (war_daily_bat, war_daily_pitch). https://www.baseball-reference.com/data/ | war_daily_bat.txt returned HTTP 200. Header includes `runs_bat, runs_br, runs_dp, runs_field`. | DS |
| B15 | VERIFIED (resolves) | Chadwick Bureau. (n.d.). *Chadwick persons register* [Data set]. GitHub. https://github.com/chadwickbureau/register | Repository page title | DS |
| B16 | VERIFIED (resolves) | LeDoux, J., et al. (n.d.). *pybaseball* [Computer software]. GitHub. https://github.com/jldbc/pybaseball | Repository page title. Contributor list not checked. | DS |

The author's own items (preprint, software) were not checked.

---

## C. New: baseball projection, shrinkage, and metric signal (peer-reviewed)

| ID | Status | APA-style citation | Verified via | Type |
|---|---|---|---|---|
| C1 | VERIFIED | Efron, B., & Morris, C. (1975). Data analysis using Stein's estimator and its generalizations. *Journal of the American Statistical Association, 70*(350), 311–319. https://doi.org/10.1080/01621459.1975.10479864 | Crossref (print June 1975) | PR |
| C2 | VERIFIED | Brown, L. D. (2008). In-season prediction of batting averages: A field test of empirical Bayes and Bayes methodologies. *The Annals of Applied Statistics, 2*(1), 113–152. https://doi.org/10.1214/07-AOAS138 | Crossref | PR |
| C3 | VERIFIED | Jensen, S. T., McShane, B. B., & Wyner, A. J. (2009). Hierarchical Bayesian modeling of hitting performance in baseball. *Bayesian Analysis, 4*(4), 631–652. https://doi.org/10.1214/09-BA424 | Crossref. A rejoinder exists (pp. 669–674, 10.1214/09-BA424REJ). | PR |
| C4 | VERIFIED | Albert, J. (2006). Pitching statistics, talent and luck, and the best strikeout seasons of all-time. *Journal of Quantitative Analysis in Sports, 2*(1). https://doi.org/10.2202/1559-0410.1014 | Crossref; abstract via OpenAlex. No pages or article number registered. | PR |
| C5 | VERIFIED | Piette, J., Braunstein, A., McShane, B. B., & Jensen, S. T. (2010). A point-mass mixture random effects model for pitching metrics. *Journal of Quantitative Analysis in Sports, 6*(3). https://doi.org/10.2202/1559-0410.1237 | Crossref; abstract via OpenAlex. No pages registered. | PR |
| C6 | VERIFIED | McShane, B. B., Braunstein, A., Piette, J., & Jensen, S. T. (2011). A hierarchical Bayesian variable selection approach to Major League Baseball hitting metrics. *Journal of Quantitative Analysis in Sports, 7*(4). https://doi.org/10.2202/1559-0410.1323 | Crossref; abstract via OpenAlex. No pages registered. | PR |
| C7 | VERIFIED | Franks, A. M., D'Amour, A., Cervone, D., & Bornn, L. (2016). Meta-analytics: Tools for understanding the statistical properties of sports metrics. *Journal of Quantitative Analysis in Sports, 12*(4). https://doi.org/10.1515/jqas-2016-0098 | Crossref, including abstract. No pages registered. | PR |
| C8 | VERIFIED | Baumer, B. S., Jensen, S. T., & Matthews, G. J. (2015). openWAR: An open source system for evaluating overall player performance in Major League Baseball. *Journal of Quantitative Analysis in Sports, 11*(2). https://doi.org/10.1515/jqas-2014-0098 | Crossref. No pages registered. | PR |
| C9 | VERIFIED | Bailey, S. R., Loeppky, J., & Swartz, T. B. (2020). The prediction of batting averages in Major League Baseball. *Stats, 3*(2), 84–93. https://doi.org/10.3390/stats3020008 | Crossref, including abstract | PR |
| C10 | VERIFIED | Koseler, K., & Stephan, M. (2017). Machine learning applications in baseball: A systematic literature review. *Applied Artificial Intelligence, 31*(9–10), 745–763. https://doi.org/10.1080/08839514.2018.1442991 | Crossref (issue dated 2017-11-26; online 2018-02-26) | PR |
| C11 | VERIFIED | Healey, G. (2017). Learning, visualizing, and assessing a model for the intrinsic value of a batted ball. *IEEE Access, 5*, 13811–13822. https://doi.org/10.1109/ACCESS.2017.2728663 | Crossref | PR |
| C12 | VERIFIED | Healey, G. (2019). A Bayesian method for computing intrinsic pitch values using kernel density and nonparametric regression estimates. *Journal of Quantitative Analysis in Sports, 15*(1), 59–74. https://doi.org/10.1515/jqas-2017-0058 | Crossref (online 2018-12-20; issue 2019-02-25) | PR |

**Relevance notes (from the abstracts read):**
- **C5:** Ranks 20 pitching metrics by signal. Rankings "differ quite substantially" between starters and relievers.
- **C6:** Asks "which offensive metrics are most predictive within players across time" over 50 metrics, with automatic multiple-testing adjustment.
- **C7:** Proposes stability, discrimination, and **independence** ("does the metric provide new information?") meta-metrics.
- **C9:** Uses Statcast data to predict batting average and combines it with PECOTA by regression.
- **C11/C12:** Peer-reviewed models with physical inputs, analogous to xwOBA and Stuff-type models. They are not MLB's or FanGraphs' own models.

---

## D. New: sabermetric constructs and projection systems (books, analytics articles, glossary)

| ID | Status | APA-style citation | Verified via | Type |
|---|---|---|---|---|
| D1 | VERIFIED | Tango, T. M., Lichtman, M., & Dolphin, A. (2007). *The book: Playing the percentages in baseball*. Potomac Books. ISBN 978-1-59797-129-4 | Open Library edition record: Potomac Books Inc., March 10, 2007, 384 pp., LCCN 2007012634, OCLC 122337992. Author names from the linked Open Library author records. | BK |
| D2 | VERIFIED | (= B7) Tango (2004), *The 2004 Marcels*: the primary description of Marcel | Page read | AA |
| D3 | VERIFIED | Silver, N. (2003, March 19). *PECOTA preview: The American League*. Baseball Prospectus. https://www.baseballprospectus.com/news/article/1724/ | Page title, byline, `article:published_time` | AA |
| D4 | VERIFIED | Silver, N. (2004, January 16). *PECOTA takes on the field: How'd it fare against six other projections systems?* Baseball Prospectus. https://www.baseballprospectus.com/news/article/2515/ | Page title, byline, date | AA |
| D5 | VERIFIED | Pease, D. (2010, September 27). *Reintroducing PECOTA: What a long, strange trip it has been*. Baseball Prospectus. https://www.baseballprospectus.com/news/article/12082/ | Page title, byline, date. Text says PECOTA "was designed by Nate Silver and first offered" at BP in 2003. | AA |
| D6 | VERIFIED | MLB.com. (n.d.). *Player Empirical Comparison and Optimization Test Algorithm (PECOTA)*. MLB Glossary. Retrieved November 13, 2026, from https://www.mlb.com/glossary/projection-systems/player-empirical-comparison-and-optimization-test-algorithm | Page read ("developed by Nate Silver in 2003") | GL |
| D7 | VERIFIED | McCracken, V. (2001, January 23). *Pitching and defense: How much control do hurlers have?* Baseball Prospectus. https://www.baseballprospectus.com/news/article/878/ | Page title, byline, date | AA |
| D8 | VERIFIED | Carleton, R. A. (2012, July 16). *Baseball therapy: It's a small sample size after all*. Baseball Prospectus. https://www.baseballprospectus.com/news/article/17659/ | Page title, byline, date | AA |
| D9 | VERIFIED | Carleton, R. A. (2013, May 9). *Baseball therapy: Should I worry about my favorite pitcher?* Baseball Prospectus. https://www.baseballprospectus.com/news/article/20516/ | Page title, byline, date | AA |
| D10 | VERIFIED | Carleton, R. A. (2017, April 18). *Baseball therapy: Reliably stable (you keep using that word)*. Baseball Prospectus. https://www.baseballprospectus.com/news/article/31626/ | Page title, byline, date | AA |
| D11 | VERIFIED | Judge, J. (2018a, May 18). *Prospectus feature: The siren song of Statcast's "expected" metrics (for pitchers)*. Baseball Prospectus. https://www.baseballprospectus.com/news/article/40026/prospectus-feature-siren-song-statcasts-expected-metrics/ | Page title, byline, date; methods and tables read | AA |
| D12 | VERIFIED | Judge, J. (2018b, August 2). *Prospectus feature: The expected contribution*. Baseball Prospectus. https://www.baseballprospectus.com/news/article/41748/ | Page title, byline, date. SABR's repost calls it "The most likely contribution"; BP's current title is used here. | AA |
| D13 | VERIFIED | Szymborski, D. (2023, August 29). *Yes, hitter xStats are useful*. FanGraphs. https://blogs.fangraphs.com/yes-hitter-xstats-are-useful/ | Page title, byline, date; RMSE tables read | AA |

**Relevance notes:**
- **D8–D10:** Carleton's reliability ("stabilization") work. The original 2007 MVN article could not be fetched (see J3).
- **D11:** Compares xBA and xwOBA with FIP and DRA on descriptive, reliability, and predictive correlations, 2015–2017, for pitchers.
- **D12:** BP's framework for judging metrics by "descriptive," "reliability," and "predictive" properties.
- **D13:** Tests whether xStats improve next-year prediction **in conjunction with** actual stats, separately for BA, OBP, SLG, and wOBA.

---

## E. New: forecast evaluation, combination, and resampling

| ID | Status | APA-style citation | Verified via | Type |
|---|---|---|---|---|
| E1 | VERIFIED | Bates, J. M., & Granger, C. W. J. (1969). The combination of forecasts. *Journal of the Operational Research Society, 20*(4), 451–468. https://doi.org/10.1057/jors.1969.103 | Crossref (publisher DOI; issue December 1969). See the journal-title note below. | PR |
| E2 | VERIFIED | Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association, 102*(477), 359–378. https://doi.org/10.1198/016214506000001437 | Crossref | PR |
| E3 | VERIFIED | Bergmeir, C., Hyndman, R. J., & Koo, B. (2018). A note on the validity of cross-validation for evaluating autoregressive time series prediction. *Computational Statistics & Data Analysis, 120*, 70–83. https://doi.org/10.1016/j.csda.2017.11.003 | Crossref | PR |
| E4 | VERIFIED | Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts. https://otexts.com/fpp3/ | Book site: title, "3rd ed", both authors; "Modified 04 November 2026". Open Library: OTexts, Melbourne, Australia, 2021, ISBN 978-0-9875071-3-6. | BK (online) |
| E5 | VERIFIED | Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall. https://doi.org/10.1007/978-1-4899-4541-9 | Crossref book record (Springer US; ISBNs 9780412042317 and 9781489945419). Open Library: Chapman & Hall, New York, 1993, 436 pp., *Monographs on Statistics and Applied Probability* 57. | BK |

**Notes:**
- **E1 journal title:** Crossref also has a JSTOR DOI, 10.2307/3008764, whose journal is titled *OR* (ISSN 1473-2858). Crossref's journal records show the title *Operational Research Quarterly* only for 1970–1977. Citing the 1969 article as "*Operational Research Quarterly*" is common but does not match these records. Use the publisher DOI above, or "*OR*, 20(4), 451–468" with the JSTOR DOI.
- **E5:** A CRC Press DOI, 10.1201/9780429246593 (Crossref date 1994-05-15), also exists. Cite one record, not both.
- **E4:** The online text is continuously revised. Cite the URL with an access date.

---

## F. New: incremental validity and added predictive value

| ID | Status | APA-style citation | Verified via | Type |
|---|---|---|---|---|
| F1 | VERIFIED | Hunsley, J., & Meyer, G. J. (2003). The incremental validity of psychological testing and assessment: Conceptual, methodological, and statistical issues. *Psychological Assessment, 15*(4), 446–455. https://doi.org/10.1037/1040-3590.15.4.446 | Crossref | PR |
| F2 | VERIFIED | Pencina, M. J., D'Agostino, R. B., Sr., D'Agostino, R. B., Jr., & Vasan, R. S. (2008). Evaluating the added predictive ability of a new marker: From area under the ROC curve to reclassification and beyond. *Statistics in Medicine, 27*(2), 157–172. https://doi.org/10.1002/sim.2929 | Crossref, including the Sr. and Jr. suffix fields (online 2007-06-13; issue 2008-01-30) | PR |

The sports-specific works on added predictive value are C5, C6, C7, C9, D11, and D13.

---

## G. New: fantasy sports (academic)

| ID | Status | APA-style citation | Verified via | Type |
|---|---|---|---|---|
| G1 | VERIFIED as preprint | Hunter, D. S., Vielma, J. P., & Zaman, T. (2019). *Picking winners in daily fantasy sports using integer programming* (arXiv:1604.01455v3) [Preprint]. arXiv. https://doi.org/10.48550/arXiv.1604.01455 | arXiv abstract pages for v1 and v3. v1 (2016-04-06) was titled "Winning Daily Fantasy Sports Hockey Contests Using Integer Programming"; v3 is dated 2019-01-23. No journal reference is listed. | PP |
| G2 | VERIFIED | Haugh, M. B., & Singal, R. (2021). How to play fantasy sports strategically (and win). *Management Science, 67*(1), 72–92. https://doi.org/10.1287/mnsc.2019.3528 | Crossref, including abstract | PR |
| G3 | VERIFIED | Fry, M. J., Lundberg, A. W., & Ohlmann, J. W. (2007). A player selection heuristic for a sports league draft. *Journal of Quantitative Analysis in Sports, 3*(2). https://doi.org/10.2202/1559-0410.1050 | Crossref; abstract via OpenAlex (benchmarked on simulated **fantasy football** drafts, 2005) | PR |
| G4 | VERIFIED | Losak, J. M., Weinbach, A. P., & Paul, R. J. (2023). Behavioral biases in daily fantasy baseball: The case of the hot hand. *Journal of Sports Economics, 24*(3), 374–401. https://doi.org/10.1177/15270025221128955 | Crossref (online first 2022-09-21; issue April 2023) | PR |
| G5 | VERIFIED | Losak, J. M., Weinbach, A. P., & Paul, R. J. (2026). Does smart money believe in the hot hand? Evidence from daily fantasy baseball. *American Behavioral Scientist, 70*(1), 93–110. https://doi.org/10.1177/00027642241235828 | Crossref (online first 2024-03-12; issue January 2026) | PR |

**No peer-reviewed paper on season-long fantasy-baseball valuation (SGP, z-scores, auction values) was found.** See J2.

---

## H. New: Statcast and pitch-quality primary sources (official pages)

| ID | Status | APA-style citation | Verified via | Type |
|---|---|---|---|---|
| H1 | VERIFIED | MLB.com. (n.d.). *Barrel*. MLB Glossary. Retrieved November 13, 2026, from https://www.mlb.com/glossary/statcast/barrel | Page read | GL |
| H2 | VERIFIED | MLB.com. (n.d.). *Hard-hit rate*. MLB Glossary. Retrieved November 13, 2026, from https://www.mlb.com/glossary/statcast/hard-hit-rate | Page read | GL |
| H3 | VERIFIED | MLB.com. (n.d.). *Outs Above Average (OAA)*. MLB Glossary. Retrieved November 13, 2026, from https://www.mlb.com/glossary/statcast/outs-above-average | Page read | GL |
| H4 | VERIFIED | Baseball Savant. (n.d.). *Statcast expected wOBA, xBA, xSLG* [Leaderboard and definitions]. MLB Advanced Media. Retrieved November 13, 2026, from https://baseballsavant.mlb.com/leaderboard/expected_statistics | Page read | GL |
| H5 | VERIFIED | Baseball Savant. (n.d.). *Statcast sprint speed leaderboard*. Retrieved November 13, 2026, from https://baseballsavant.mlb.com/leaderboard/sprint_speed | Page read | GL |
| H6 | VERIFIED | Baseball Savant. (n.d.). *Statcast Outs Above Average leaderboard*. Retrieved November 13, 2026, from https://baseballsavant.mlb.com/leaderboard/outs_above_average | Page read | GL |
| H7 | VERIFIED | Baseball Savant. (n.d.). *Statcast search CSV documentation*. Retrieved November 13, 2026, from https://baseballsavant.mlb.com/csv-docs | Page read (`estimated_woba_using_speedangle`, `woba_value`, `woba_denom`) | GL |
| H8 | VERIFIED | Appelman, D. (2023, March 10). *PitchingBot and Stuff+ pitch modeling is now on FanGraphs!* FanGraphs. https://blogs.fangraphs.com/pitchingbot-and-stuff-pitch-modeling-are-now-on-fangraphs/ | Page title, byline, date | GL (announcement) |

Also in this group: B3 (xwOBA), B4 (sprint speed), B5 (Driveline Stuff+), B6 (FanGraphs Stuff+ primer), C11, and C12.

---

## I. New: metric-definition and WAR-methodology pages (all read 2026-11-13)

FanGraphs Library pages carry the byline of the Library's keeper, Piper Slowinski. Some pages were later revised; for example, *Sample Size* is signed "Neil Weinberg, Updated August 2017."

| ID | Status | APA-style citation | Type |
|---|---|---|---|
| I1 | VERIFIED | Slowinski, P. (2010, February 15). *wOBA*. FanGraphs Library. https://library.fangraphs.com/offense/woba/ | GL |
| I2 | VERIFIED | Slowinski, P. (2010, February 15). *FIP*. FanGraphs Library. https://library.fangraphs.com/pitching/fip/ | GL |
| I3 | VERIFIED | Slowinski, P. (2010, February 15). *xFIP*. FanGraphs Library. https://library.fangraphs.com/pitching/xfip/ | GL |
| I4 | VERIFIED | Slowinski, P. (2011, July 27). *SIERA*. FanGraphs Library. https://library.fangraphs.com/pitching/siera/ | GL |
| I5 | VERIFIED | Slowinski, P. (2010, February 19). *K% and BB%*. FanGraphs Library. https://library.fangraphs.com/offense/rate-stats/ | GL |
| I6 | VERIFIED | Slowinski, P. (2010, February 19). *Strikeout and walk rates*. FanGraphs Library. https://library.fangraphs.com/pitching/rate-stats/ | GL |
| I7 | VERIFIED | Slowinski, P. (2010, February 16). *wRC and wRC+*. FanGraphs Library. https://library.fangraphs.com/offense/wrc/ | GL |
| I8 | VERIFIED | Slowinski, P. (2012, March 28). *WAR for pitchers*. FanGraphs Library. https://library.fangraphs.com/war/calculating-war-pitchers/ | GL |
| I9 | VERIFIED | Slowinski, P. (2012, April 2). *WAR for position players*. FanGraphs Library. https://library.fangraphs.com/war/war-position-players/ | GL |
| I10 | VERIFIED | Slowinski, P. (2012, March 22). *fWAR, rWAR, and WARP*. FanGraphs Library. https://library.fangraphs.com/war/differences-fwar-rwar/ | GL |
| I11 | VERIFIED | Slowinski, P. (2010, February 18). *Sample size*. FanGraphs Library. https://library.fangraphs.com/principles/sample-size/ | GL |
| I12 | VERIFIED | Appelman, D. (2022, April 21). *A FanGraphs WAR fielding update*. FanGraphs. https://blogs.fangraphs.com/a-fangraphs-war-fielding-update/ | GL (methodology post) |
| I13 | VERIFIED | Appelman, D. (2024, April 5). *2024 FanGraphs WAR update*. FanGraphs. https://blogs.fangraphs.com/2024-fangraphs-war-update/ | GL (methodology post) |
| I14 | VERIFIED | MLB.com. (n.d.). *Weighted on-base average (wOBA)*. MLB Glossary. https://www.mlb.com/glossary/advanced-stats/weighted-on-base-average | GL |
| I15 | VERIFIED | MLB.com. (n.d.). *Fielding independent pitching (FIP)*. MLB Glossary. https://www.mlb.com/glossary/advanced-stats/fielding-independent-pitching | GL |
| I16 | VERIFIED | MLB.com. (n.d.). *Expected fielding independent pitching (xFIP)*. MLB Glossary. https://www.mlb.com/glossary/advanced-stats/expected-fielding-independent-pitching | GL |
| I17 | VERIFIED | MLB.com. (n.d.). *Skill-interactive earned run average (SIERA)*. MLB Glossary. https://www.mlb.com/glossary/advanced-stats/skill-interactive-earned-run-average | GL |
| I18 | VERIFIED | MLB.com. (n.d.). *Strikeout rate (K%)*. MLB Glossary. https://www.mlb.com/glossary/advanced-stats/strikeout-rate | GL |
| I19 | VERIFIED | MLB.com. (n.d.). *Walk rate (BB%)*. MLB Glossary. https://www.mlb.com/glossary/advanced-stats/walk-rate | GL |
| I20 | VERIFIED | MLB.com. (n.d.). *Weighted runs created plus (wRC+)*. MLB Glossary. https://www.mlb.com/glossary/advanced-stats/weighted-runs-created-plus | GL |
| I21 | VERIFIED | MLB.com. (n.d.). *Wins above replacement (WAR)*. MLB Glossary. https://www.mlb.com/glossary/advanced-stats/wins-above-replacement | GL |
| I22 | VERIFIED | Sports Reference LLC. (n.d.). *Baseball-Reference.com WAR explained*. Baseball-Reference.com. https://www.baseball-reference.com/about/war_explained.shtml | GL |
| I23 | VERIFIED | Sports Reference LLC. (n.d.). *Position player WAR calculations and details*. Baseball-Reference.com. https://www.baseball-reference.com/about/war_explained_position.shtml | GL |
| I24 | VERIFIED | Sports Reference LLC. (n.d.). *Pitcher WAR calculations and details*. Baseball-Reference.com. https://www.baseball-reference.com/about/war_explained_pitch.shtml | GL |
| I25 | VERIFIED | Sports Reference LLC. (n.d.). *WAR download glossary and column headings*. Baseball-Reference.com. https://www.baseball-reference.com/about/war_explained_glossary.shtml | GL |
| I26 | VERIFIED | Sports Reference LLC. (n.d.). *WAR comparison chart*. Baseball-Reference.com. https://www.baseball-reference.com/about/war_explained_comparison.shtml | GL |
| I27 | VERIFIED | Sports Reference LLC. (n.d.). *Player value—batting* [Column definitions, e.g., Rbaser, Rdp, Rfield]. Baseball-Reference.com. Example page: https://www.baseball-reference.com/players/t/troutmi01.shtml | GL (table header tooltips) |
| I28 | VERIFIED | Bonilla, A. (2019, March 21). *2019 WAR update*. Sports Reference Blog. https://www.sports-reference.com/blog/2019/03/2019-war-update/ | GL (methodology post) |
| I29 | VERIFIED | Gardner, J. (2022, April 11). *2022 WAR update and new Retrosheet data*. Sports Reference Blog. https://www.sports-reference.com/blog/2022/04/2022-war-update-and-new-retrosheet-data/ | GL (methodology post) |
| I30 | VERIFIED | Lynch, M. (2024, March 19). *2024 preseason WAR update is live*. Sports Reference Blog. https://www.sports-reference.com/blog/2024/03/2024-preseason-war-update-is-live/ | GL (methodology post) |
| I31 | VERIFIED | Lynch, M. (2025, March 17). *2025 preseason WAR update is live*. Sports Reference Blog. https://www.sports-reference.com/blog/2025/03/2025-preseason-war-update-is-live/ | GL (methodology post) |
| I32 | VERIFIED | Lynch, M. (2026, March 26). *Updates to historical WAR figures*. Sports Reference Blog. https://www.sports-reference.com/blog/2026/03/updates-to-historical-war-figures/ | GL (methodology post) |

The Sports Reference blog's WAR category also lists posts that were not read: "2020 WAR Update" (March 2020), "December 2020 WAR Update", "2021 WAR Update", and "August 2021 Park Factor Update".

---

## J. Not verified, not found, or rejected

| ID | Item | Status | Why |
|---|---|---|---|
| J1 | Silver (2003), "Introducing PECOTA," chapter in *Baseball Prospectus 2003* (= B8) | **NOT VERIFIED (chapter)** | The book exists (Brassey's, 2003; ISBN 1-57488-561-8). No table of contents or page range could be found online; the "Introducing PECOTA" title appears only in secondary sources. **Fix:** cite D3, D4, D5, or D6, or check a library copy for pages. |
| J2 | Peer-reviewed work on fantasy-baseball valuation (SGP, z-scores, auction values) | **NOT FOUND** | Searched Crossref (title queries "fantasy baseball" and "fantasy sports player valuation draft", journal articles only) and the web. Found only practitioner material, such as FanGraphs community posts, BaseballHQ, and Masters Ball. Peer-reviewed fantasy work that does exist is G2–G5 (daily fantasy and draft heuristics), not valuation. Do not cite a peer-reviewed SGP or z-score source. |
| J3 | Carleton ("Pizza Cutter") (2007), "525,600 Minutes: How Do You Measure a Player in a Year?" (MVN/StatSpeak) | **NOT VERIFIED** | It survives only as a web.archive.org copy, and that domain could not be fetched. Cite D8–D10 (Carleton's own BP updates) and I11. |
| J4 | Peer-reviewed primary description of MLB's xwOBA model or FanGraphs' Stuff+ | **NOT FOUND** | The primary sources are official pages (B3, H4, H7, B6, H8). C11 and C12 are peer-reviewed models of the same kind but are not MLB's or FanGraphs' implementations. |
| J5 | Hunter, Vielma & Zaman as a peer-reviewed article | **NOT FOUND** | arXiv lists no journal reference, and Crossref search found no journal version. Cite as a preprint (G1). The title in the request ("Winning daily fantasy hockey contests…") is close to, but not the same as, v1's "Winning Daily Fantasy Sports Hockey Contests Using Integer Programming." |
| J6 | *Introducing Deserved Runs Created Plus (DRC+)*, Baseball Prospectus, 2018-12-03 (article 45338) | **REJECTED (byline unclear)** | The page metadata gives conflicting authors: the visible author block says Bryan Grosnick and the JSON-LD says Aaron Gleeman. Not needed; D12 covers BP's framework. |
| J7 | DOI 10.2307/4615733 for Holm (1979) | **NOT VERIFIED (DOI)** | Carried from the prior pass: the DOI did not resolve. Use the JSTOR stable URL (A17). |

---

## K. Corrections needed in `references.md`

1. **#4 Driveline:** replace with B5: author Chris Langin, dated 2021-12-13, title "Pitch design: What is Stuff+? Quantifying pitches with pitch models." The current entry reads "Driveline Baseball (n.d.). What is Stuff?…".
2. **#5 FanGraphs primer:** author Owen McGrattan, dated 2023-03-10 (B6). The current entry reads "FanGraphs (n.d.)".
3. **#6 Marcel:** the page at tangotiger.net/marcel is titled "Marcel 2012" and shows no publication date. The method is specified in "The 2004 Marcels" (2004-03-10). Cite B7.
4. **#7 PECOTA:** the chapter is not verified (J1). Brassey's as publisher is correct (Open Library). Add ISBN 1-57488-561-8, or substitute D3, D4, D5, or D6.
5. **#8 ZiPS:** the year is **2020** (published 2020-11-10), not 2021.
6. **#25 Sports Illustrated:** add the author and date: Kadlick, M. (2025, September 23).
7. **Optional:** if E1 is cited, use the journal name given in Part E. For G4 and G5, decide whether to cite the online-first year or the issue year, and apply that choice consistently with A15.
