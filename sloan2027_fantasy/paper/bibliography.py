"""Bibliography: every entry is copied from a verified record in references_verified.md (scholarly and official pages,
verified 2026-11-11/13) or fantasy/research_sources.md (fantasy practice sources, verified 2026-11-13). IDs in comments
point to those files. Nothing here comes from memory."""
from __future__ import annotations

ACC = "Retrieved November 13, 2026, from"


def bibliography(blind: bool) -> dict:
    B = {
        # --- statistics and forecasting (references_verified.md, Part A/B/E/F)
        "shmueli": "Shmueli, G. (2010). To explain or to predict? *Statistical Science, 25*(3), 289–310. https://doi.org/10.1214/10-STS330",  # B1
        "ambroise": "Ambroise, C., & McLachlan, G. J. (2002). Selection bias in gene extraction on the basis of microarray gene-expression data. *Proceedings of the National Academy of Sciences, 99*(10), 6562–6566. https://doi.org/10.1073/pnas.102102699",  # A1
        "varma": "Varma, S., & Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics, 7*, 91. https://doi.org/10.1186/1471-2105-7-91",  # A2
        "cawley": "Cawley, G. C., & Talbot, N. L. C. (2010). On over-fitting in model selection and subsequent selection bias in performance evaluation. *Journal of Machine Learning Research, 11*(70), 2079–2107. https://www.jmlr.org/papers/v11/cawley10a.html",  # A3
        "bh": "Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B, 57*(1), 289–300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x",  # A4
        "bergmeir": "Bergmeir, C., & Benítez, J. M. (2012). On the use of cross-validation for time series predictor evaluation. *Information Sciences, 191*, 192–213. https://doi.org/10.1016/j.ins.2011.12.028",  # A5
        "tashman": "Tashman, L. J. (2000). Out-of-sample tests of forecasting accuracy: An analysis and review. *International Journal of Forecasting, 16*(4), 437–450. https://doi.org/10.1016/S0169-2070(00)00065-0",  # A6
        "meinshausen": "Meinshausen, N., & Bühlmann, P. (2010). Stability selection. *Journal of the Royal Statistical Society: Series B, 72*(4), 417–473. https://doi.org/10.1111/j.1467-9868.2010.00740.x",  # A7
        "ke": "Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. In *Advances in Neural Information Processing Systems 30* (NIPS 2017). Curran Associates. https://proceedings.neurips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html",  # A8
        "hoerl": "Hoerl, A. E., & Kennard, R. W. (1970). Ridge regression: Biased estimation for nonorthogonal problems. *Technometrics, 12*(1), 55–67. https://doi.org/10.1080/00401706.1970.10488634",  # A9
        "breiman": "Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. https://doi.org/10.1023/A:1010933404324",  # verified via Crossref 2026-11-13
        "zou": "Zou, H., & Hastie, T. (2005). Regularization and variable selection via the elastic net. *Journal of the Royal Statistical Society: Series B, 67*(2), 301–320. https://doi.org/10.1111/j.1467-9868.2005.00503.x",  # A10
        "guyon": "Guyon, I., & Elisseeff, A. (2003). An introduction to variable and feature selection. *Journal of Machine Learning Research, 3*, 1157–1182. https://www.jmlr.org/papers/v3/guyon03a.html",  # A11
        "diebold": "Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599",  # A12
        "cameron": "Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008). Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics, 90*(3), 414–427. https://doi.org/10.1162/rest.90.3.414",  # A13
        "nogueira": "Nogueira, S., Sechidis, K., & Brown, G. (2018). On the stability of feature selection algorithms. *Journal of Machine Learning Research, 18*(174), 1–54. https://www.jmlr.org/papers/v18/17-514.html",  # A14
        "roberts": "Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881",  # A16
        "holm": "Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics, 6*(2), 65–70. https://www.jstor.org/stable/4615733",  # A17
        "bates": "Bates, J. M., & Granger, C. W. J. (1969). The combination of forecasts. *Journal of the Operational Research Society, 20*(4), 451–468. https://doi.org/10.1057/jors.1969.103",  # E1
        "gneiting": "Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association, 102*(477), 359–378. https://doi.org/10.1198/016214506000001437",  # E2
        "hunsley": "Hunsley, J., & Meyer, G. J. (2003). The incremental validity of psychological testing and assessment: Conceptual, methodological, and statistical issues. *Psychological Assessment, 15*(4), 446–455. https://doi.org/10.1037/1040-3590.15.4.446",  # F1
        "pencina": "Pencina, M. J., D'Agostino, R. B., Sr., D'Agostino, R. B., Jr., & Vasan, R. S. (2008). Evaluating the added predictive ability of a new marker: From area under the ROC curve to reclassification and beyond. *Statistics in Medicine, 27*(2), 157–172. https://doi.org/10.1002/sim.2929",  # F2
        # --- baseball statistics and projection (Part C/D)
        "efron_morris": "Efron, B., & Morris, C. (1975). Data analysis using Stein's estimator and its generalizations. *Journal of the American Statistical Association, 70*(350), 311–319. https://doi.org/10.1080/01621459.1975.10479864",  # C1
        "brown": "Brown, L. D. (2008). In-season prediction of batting averages: A field test of empirical Bayes and Bayes methodologies. *The Annals of Applied Statistics, 2*(1), 113–152. https://doi.org/10.1214/07-AOAS138",  # C2
        "jensen": "Jensen, S. T., McShane, B. B., & Wyner, A. J. (2009). Hierarchical Bayesian modeling of hitting performance in baseball. *Bayesian Analysis, 4*(4), 631–652. https://doi.org/10.1214/09-BA424",  # C3
        "piette": "Piette, J., Braunstein, A., McShane, B. B., & Jensen, S. T. (2010). A point-mass mixture random effects model for pitching metrics. *Journal of Quantitative Analysis in Sports, 6*(3). https://doi.org/10.2202/1559-0410.1237",  # C5
        "mcshane": "McShane, B. B., Braunstein, A., Piette, J., & Jensen, S. T. (2011). A hierarchical Bayesian variable selection approach to Major League Baseball hitting metrics. *Journal of Quantitative Analysis in Sports, 7*(4). https://doi.org/10.2202/1559-0410.1323",  # C6
        "franks": "Franks, A. M., D'Amour, A., Cervone, D., & Bornn, L. (2016). Meta-analytics: Tools for understanding the statistical properties of sports metrics. *Journal of Quantitative Analysis in Sports, 12*(4). https://doi.org/10.1515/jqas-2016-0098",  # C7
        "openwar": "Baumer, B. S., Jensen, S. T., & Matthews, G. J. (2015). openWAR: An open source system for evaluating overall player performance in Major League Baseball. *Journal of Quantitative Analysis in Sports, 11*(2). https://doi.org/10.1515/jqas-2014-0098",  # C8
        "bailey": "Bailey, S. R., Loeppky, J., & Swartz, T. B. (2020). The prediction of batting averages in Major League Baseball. *Stats, 3*(2), 84–93. https://doi.org/10.3390/stats3020008",  # C9
        "healey": "Healey, G. (2017). Learning, visualizing, and assessing a model for the intrinsic value of a batted ball. *IEEE Access, 5*, 13811–13822. https://doi.org/10.1109/ACCESS.2017.2728663",  # C11
        "tango_book": "Tango, T. M., Lichtman, M., & Dolphin, A. (2007). *The book: Playing the percentages in baseball*. Potomac Books. ISBN 978-1-59797-129-4",  # D1
        "marcel": "Tango, T. (2004, March 10). *The 2004 Marcels*. Tango on Baseball Archives. http://www.tangotiger.net/archives/stud0346.shtml",  # B7
        "pecota": "Silver, N. (2004, January 16). *PECOTA takes on the field: How'd it fare against six other projections systems?* Baseball Prospectus. https://www.baseballprospectus.com/news/article/2515/",  # D4
        "mccracken": "McCracken, V. (2001, January 23). *Pitching and defense: How much control do hurlers have?* Baseball Prospectus. https://www.baseballprospectus.com/news/article/878/",  # D7
        "carleton": "Carleton, R. A. (2017, April 18). *Baseball therapy: Reliably stable (you keep using that word)*. Baseball Prospectus. https://www.baseballprospectus.com/news/article/31626/",  # D10
        "judge_siren": "Judge, J. (2018, May 18). *Prospectus feature: The siren song of Statcast's \"expected\" metrics (for pitchers)*. Baseball Prospectus. https://www.baseballprospectus.com/news/article/40026/prospectus-feature-siren-song-statcasts-expected-metrics/",  # D11
        "judge_expected": "Judge, J. (2018, August 2). *Prospectus feature: The expected contribution*. Baseball Prospectus. https://www.baseballprospectus.com/news/article/41748/",  # D12
        "szym_xstats": "Szymborski, D. (2023, August 29). *Yes, hitter xStats are useful*. FanGraphs. https://blogs.fangraphs.com/yes-hitter-xstats-are-useful/",  # D13
        "zips": "Szymborski, D. (2020, November 10). *The 2021 ZiPS projections: An introduction*. FanGraphs. https://blogs.fangraphs.com/the-2021-zips-projections-an-introduction/",  # B9
        "steamer": f"MLB.com. (n.d.). *Steamer*. MLB Glossary. {ACC} https://www.mlb.com/glossary/projection-systems/steamer",  # B10
        "driveline": "Langin, C. (2021, December 13). *Pitch design: What is Stuff+? Quantifying pitches with pitch models*. Driveline Baseball. https://www.drivelinebaseball.com/blogs/blog/what-is-stuff-quantifying-pitches-with-pitch-models",  # B5
        "fg_stuff": "McGrattan, O. (2023, March 10). *Stuff+, Location+, and Pitching+ primer*. FanGraphs Library. https://library.fangraphs.com/pitching/stuff-location-and-pitching-primer/",  # B6
        # --- fantasy sports scholarship (Part G)
        "haugh": "Haugh, M. B., & Singal, R. (2021). How to play fantasy sports strategically (and win). *Management Science, 67*(1), 72–92. https://doi.org/10.1287/mnsc.2019.3528",  # G2
        "hunter": "Hunter, D. S., Vielma, J. P., & Zaman, T. (2019). *Picking winners in daily fantasy sports using integer programming* (arXiv:1604.01455v3) [Preprint]. arXiv. https://doi.org/10.48550/arXiv.1604.01455",  # G1
        "fry": "Fry, M. J., Lundberg, A. W., & Ohlmann, J. W. (2007). A player selection heuristic for a sports league draft. *Journal of Quantitative Analysis in Sports, 3*(2). https://doi.org/10.2202/1559-0410.1050",  # G3
        # --- definitions (Part B/H/I)
        "statcast": f"MLB.com. (n.d.). *Statcast*. MLB Glossary. {ACC} https://www.mlb.com/glossary/statcast",  # B2
        "mlb_xwoba": f"MLB.com. (n.d.). *Expected weighted on-base average (xwOBA)*. MLB Glossary. {ACC} https://www.mlb.com/glossary/statcast/expected-woba",  # B3
        "mlb_sprint": f"MLB.com. (n.d.). *Sprint speed (SS)*. MLB Glossary. {ACC} https://www.mlb.com/glossary/statcast/sprint-speed",  # B4
        "mlb_barrel": f"MLB.com. (n.d.). *Barrel*. MLB Glossary. {ACC} https://www.mlb.com/glossary/statcast/barrel",  # H1
        "fg_woba": "Slowinski, P. (2010, February 15). *wOBA*. FanGraphs Library. https://library.fangraphs.com/offense/woba/",  # I1
        "fg_fip": "Slowinski, P. (2010, February 15). *FIP*. FanGraphs Library. https://library.fangraphs.com/pitching/fip/",  # I2
        "fg_war": "Slowinski, P. (2012, March 22). *fWAR, rWAR, and WARP*. FanGraphs Library. https://library.fangraphs.com/war/differences-fwar-rwar/",  # I10
        "bref_war": "Sports Reference LLC. (n.d.). *Baseball-Reference.com WAR explained*. Baseball-Reference.com. https://www.baseball-reference.com/about/war_explained.shtml",  # I22
        "bref_war_pos": "Sports Reference LLC. (n.d.). *Position player WAR calculations and details*. Baseball-Reference.com. https://www.baseball-reference.com/about/war_explained_position.shtml",  # I23
        "bref_war_pitch": "Sports Reference LLC. (n.d.). *Pitcher WAR calculations and details*. Baseball-Reference.com. https://www.baseball-reference.com/about/war_explained_pitch.shtml",  # I24
        "bref_update2025": "Lynch, M. (2025, March 17). *2025 preseason WAR update is live*. Sports Reference Blog. https://www.sports-reference.com/blog/2025/03/2025-preseason-war-update-is-live/",  # I31
        # --- data sources (Part B)
        "savant": "Baseball Savant (MLB Advanced Media). (n.d.). *Custom leaderboards and Statcast search*. https://baseballsavant.mlb.com/",  # B12
        "statsapi": "MLB Advanced Media. (n.d.). *MLB Stats API*. https://statsapi.mlb.com/",  # B13
        "bref_data": "Sports Reference LLC. (n.d.). *Baseball-Reference.com WAR data files* (war_daily_bat, war_daily_pitch). https://www.baseball-reference.com/data/",  # B14
        "chadwick": "Chadwick Bureau. (n.d.). *Chadwick persons register* [Data set]. GitHub. https://github.com/chadwickbureau/register",  # B15
    }
    try:
        from fantasy_refs import FANTASY_REFS  # verified fantasy-practice sources (fantasy/research_sources.md)
        B.update(FANTASY_REFS)
    except ImportError:
        pass
    if blind:
        B["preprint"] = "[Author's earlier public preprint of this study (2026); citation withheld for blind review.]"
        B["repo"] = "[Author's public code and data-rebuild repositories; links provided in the submission form and withheld here for blind review.]"
    else:
        B["preprint"] = "Alapati, S. (2026). One metric, different jobs: Target-specific feature admission for Major League Baseball player projection [Preprint]. Zenodo. https://doi.org/10.5281/zenodo.22050908"
        B["repo"] = ("Alapati, S. (2026). MIT Sloan 2027 Fantasy Baseball Projection Lab [Code, results, and web application]. GitHub. "
                     "https://github.com/shirinalapati/MIT_Sloan_2027_Fantasy_Baseball_Projection_Lab_Paper")
    return B
