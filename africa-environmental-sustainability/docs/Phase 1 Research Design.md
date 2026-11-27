# Environmental Sustainability in Africa
## Research Design and Data Discovery

Martin B. Mwaala | 26 November 2026

---

## 1. Summary

The project is feasible, but the six dimensions sit on data of very uneven quality. Carbon, energy access, GDP and governance data support a 54-country annual panel. Water and biodiversity data do not: they are sparse, modelled or a single snapshot. Several of the questions I started with would produce misleading answers if run on the obvious World Bank indicators, so I revised them before building anything (Section 5).

The project runs as ten Jupyter notebooks, CSV files in `data/` and a Python (Plotly Dash) dashboard. The indicator catalogue (88 indicators) is in `config/indicator-catalogue.csv` and the country list (54 African countries, 9 comparator aggregates and 7 comparator countries) is in `config/countries.csv`.

Data coverage is measured, not estimated. `01 Data.ipynb` pulls every World Bank code, saves the raw responses and calculates coverage for each country and indicator (Section 6). Of the 79 indicators pulled, 68 are complete enough for panel work.

### Eight findings that shaped the design
1. **"Renewable energy share" is mostly poverty in Africa.** `EG.FEC.RNEW.ZS` counts traditional biomass (firewood, charcoal) as renewable. DRC, Ethiopia and Uganda score near the top of the world, and the share falls as countries get richer and switch to LPG and grid power. A naive regression would "find" that development reduces renewable adoption. Fix: measure the transition with renewable electricity generation (Ember, IRENA) and clean cooking access (`EG.CFT.ACCS.ZS`). Keep `EG.FEC.RNEW.ZS` only as context.
2. **Energy CO2 understates emissions in Africa's forest economies.** The World Bank's EDGAR series exclude land use change (LULUCF). For DRC, Zambia, Tanzania and Mozambique, land use change emissions are likely the larger part of the total. Fix: report energy CO2 and LULUCF separately, and never add them without a flag. Use Global Carbon Budget data through OWID as a cross-check.
3. **FAO forest area series are often straight lines.** For many African countries the annual values are interpolated between assessment years. Year-on-year changes are artefacts. Fix: use forest area for levels and 5-year changes only. Use satellite tree cover loss for annual dynamics.
4. **Tree cover loss is not deforestation, and the series has breaks.** It includes plantation harvest, shifting cultivation and fire. Global Forest Watch warns that the model changed around 2011 and 2015. Fix: use 3-year moving averages and the dominant-driver data, which separates permanent agriculture from shifting cultivation. Test for breaks around 2011 and 2015.
5. **Water data cannot support a panel.** AQUASTAT withdrawals have few measured years per country. Many values are repeated or modelled. Fix: treat water stress as a cross-section with a measured-or-modelled flag. Drop the question "are water risks increasing over time" unless the measured observations support it.
6. **Threatened species counts are a single snapshot and scale with species richness.** They cannot test whether "deforestation increases biodiversity threat" over time. Fix: use the Red List Index (SDG 15.5.1) as the time series. Use counts only as normalised cross-section context.
7. **ND-GAIN versus GDP is partly circular.** Readiness includes economic components, and vulnerability includes adaptive capacity, both of which move with income. Regressing ND-GAIN on GDP partly regresses GDP on itself. Fix: use the components, the GDP-adjusted score that ND-GAIN publishes, and an explicit test of the overlap.
8. **2000 to 2024 is the search window, not the analytical window.** Most series end between 2021 and 2023. The realistic common panel is about 2000 to 2021 or 2022. That gives T of about 22 and N of 54: enough for fixed effects with robust errors, but too short for credible ARIMA on most country series.

### Design choices

| Area | Choice |
|---|---|
| Country scope | All 54 AU member states (North Africa included), with Sub-Saharan subsets for robustness. Western Sahara excluded (no World Bank coverage) |
| Comparators | World, WB aggregates (SSF, AFE, AFW), the four income groups, OECD, plus China, India, Brazil, Indonesia, USA, Germany, UK |
| Analytical window | 2000 to the latest common year per model; descriptive charts to the latest available year |
| Added sources | Ember (electricity mix), UN SDG database (Red List Index) and FAO FRA 2025, alongside the World Bank, FAOSTAT, ND-GAIN, Global Forest Watch, IRENA, IUCN and OWID |
| Composite index | No composite ranking. Clusters and dimension-level rankings only |
| Storage | CSV files in `data/`: long observation table, country-year panel, indicator dictionary and quality flags |
| Dashboard | Python dashboard built with Plotly Dash (pages, filters, cross-filtering) |
| Public repo | Fine for World Bank, FAO, GFW, Ember, ND-GAIN and OWID outputs, with attribution. IUCN raw data stays out of the public repo |

---

---

## 2. Scope

**Countries.** All 54 African Union member states, grouped into the AU's five regions (North 6, West 15, Central 9, East 14, Southern 10). The World Bank region and income group are pulled from the API, not hardcoded, because income groups change over time. Known breaks:

- **Sudan and South Sudan:** South Sudan exists from 2011. Before then its values sit inside Sudan's. Sudan series break in 2011. Panel models need a dummy for the break, or Sudan excluded.
- **Libya, South Sudan, Somalia, Eritrea:** conflict years leave large gaps and extreme growth rates. Run robustness checks without them.
- **Small island states** (Cabo Verde, Comoros, Mauritius, Sao Tome and Principe, Seychelles): very low absolute emissions and forest area. Per-capita and share measures behave erratically. Flag them in clustering.
- **16 landlocked countries:** marine protected area is *not applicable*, which must not be stored as zero.

**Comparators.** World, World Bank aggregates (Sub-Saharan Africa, Africa Eastern and Southern, Africa Western and Central), the four income groups, OECD, and seven reference countries. The "developed versus developing" contrast uses income groups, not a binary label.

**Period.** Pull 2000 to 2024. Analyse on the longest common window each model supports. Report the window with every result.

---

## 3. Source assessment

| Source | Access method (verified) | Authentication | Licence | Historical coverage | Update | Verdict |
|---|---|---|---|---|---|---|
| World Bank WDI | REST API v2 `api.worldbank.org/v2` | None | CC BY 4.0 for most series. Some IEA-based energy series carry IEA terms | 1960 onward; emissions series (EDGAR) 1970 to 2024 | Several releases a year | Backbone of the panel |
| World Bank Sovereign ESG portal | Same API, `source=75` | None | CC BY 4.0 | Varies by indicator; portal data runs to 2024 | Periodic (latest January 2026 refresh) | Use for tree cover loss and primary forest loss via the API |
| World Bank CCKP | REST API `cckpapi.worldbank.org/cckp/v1/`; gridded NetCDF on AWS open data | None | World Bank open data; ODbL on the AWS registry | CRU TS 4.08 from 1901; ERA5 1950 to 2022; CMIP6 projections | Irregular | Use for observed temperature, rainfall and extremes |
| Global Forest Watch | Data API `data-api.globalforestwatch.org`; country statistics downloads | Free API key | CC BY 4.0 | Tree cover loss 2001 onward; primary forest 2002 onward | Annual (around April) | Core for annual forest dynamics |
| FAOSTAT | Bulk zip downloads (no key); new API developer portal (April 2026) | None for bulk; API needs login or token | CC BY 4.0 for FAO statistical databases since 1 July 2024 | Land use 1961 onward | Annual | Use bulk downloads; keep the FAO flag column |
| FAO FRA 2025 | FRA platform, including an API | None (confirm) | CC BY 4.0 (confirm on platform) | 1990 to 2025 at 5-year points | Every 5 years | Authoritative forest area and deforestation, as period averages |
| ND-GAIN | Zip bulk download only. **No API** | None | Free and open with citation (confirm exact licence text) | 1995 onward; latest release runs to 2023 | Annual | Core for Dimension F; automate with a scripted zip download |
| Our World in Data | Grapher CSV and metadata JSON per chart | None | CC BY 4.0 for OWID work; underlying source terms still apply | Varies | Varies | Cross-check and convenience source; always cite the original producer |
| IRENA (IRENASTAT) | PxWeb API `pxweb.irena.org/api/v1/en/` | None | IRENA terms, attribution (confirm) | Capacity and generation from 2000 | Capacity in March, generation in July | Core for solar, wind and hydro capacity |
| IUCN Red List | API v4 `api.iucnredlist.org/api/v4/` | Free token | Non-commercial only; no redistribution of raw data | Current Red List version | 1 to 2 versions a year | Use for derived counts only. Not suitable for a public raw-data repo |
| **Added: Ember** | Yearly electricity data CSV; API | Key for API | CC BY 4.0 (confirm on download page) | 2000 onward, 200+ geographies | Monthly | Best open source for electricity mix in Africa |
| **Added: UN SDG Global Database** | SDG API v5 | None | Open with attribution | Red List Index 1993 onward | Annual | Time-series fix for the biodiversity dimension |

"Confirm" items are checked against the licence text on each download page, and the wording is recorded in the indicator dictionary.

---

## 4. Indicator catalogue

The full catalogue is `config/indicator-catalogue.csv`: 88 indicators with code, source, unit, frequency, expected coverage, endpoint, licence, role and known limitations. Each indicator is tagged with a **role**:

- **Core:** used in the main models and dashboard.
- **Supporting:** decomposition or robustness.
- **Control:** an explanatory variable in the econometrics.
- **Validation:** an alternative source used to cross-check a core series.
- **Cross-section only:** a single snapshot or period average, never used in a panel.
- **Legacy:** probably discontinued around 2015. Kept so the audit can confirm the end year and the series can be retired.

**Verification status.** Every World Bank code is checked when `01 Data.ipynb` pulls it. A code that returns nothing is reported and left out of the analysis.

### Group summary

| Group | Count | Core series | Main source |
|---|---|---|---|
| A Carbon emissions | 9 | CO2 per capita and total, CH4, N2O, total GHG, carbon intensity of GDP (all AR5 GWP100, EDGAR) | WB WDI |
| B Renewable energy | 11 | Electricity mix by source, renewable capacity, electricity access, clean cooking | Ember, IRENA, WB |
| C Forests and land | 11 | Tree cover loss, primary forest loss, FRA forest area and deforestation, agricultural and cropland share | WB ESG, GFW, FAO |
| D Water | 12 | Water stress (SDG 6.4.2), withdrawals by sector, basic and safely managed drinking water | WB (AQUASTAT, JMP) |
| E Biodiversity | 9 | Red List Index, protected area coverage | UN SDG, WB, IUCN |
| F Climate vulnerability | 9 | ND-GAIN score, vulnerability, readiness and components; observed climate | ND-GAIN, CCKP |
| G Controls | 15 | GDP per capita (PPP), urbanisation, population, agricultural share, resource rents, WGI governance | WB WDI, WGI |

**Important code change.** The World Bank has replaced the old Climate Watch emissions series (`EN.ATM.CO2E.PC`, `EN.ATM.METH.KT.CE` and related codes, 1990 to 2020, AR2 GWPs) with EDGAR-based series (`EN.GHG.*.AR5`, 1970 to 2024, AR5 GWPs). The two families use different methods and warming potentials. Do not mix them in one series. The project uses only the EDGAR family.

---

## 5. Research questions: revised wording

| Dimension | Question as first framed | Problem | Question as tested |
|---|---|---|---|
| A | Fastest growth in emissions | Growth from tiny bases (e.g. 0.05 t per capita) produces meaningless percentages | Largest absolute and per-capita increases, 2000 to latest; growth rates reported only above a materiality floor |
| A | Is economic growth associated with emissions? | Fine as an association; the EKC form needs care at Africa's income range | Association between GDP per capita (PPP) and CO2 per capita, within-country, with income-squared tested and not assumed |
| B | Which countries are transitioning? | Final-energy renewable share rewards biomass dependence | Change in the non-hydro renewable share of electricity generation and in clean cooking access, 2000 to latest |
| B | Renewables and declining carbon intensity | Hydro-dominated grids (Zambia, Ethiopia, DRC) were already low-carbon; drought years cause swings | Within-country association between the change in renewable electricity share and the change in CO2 intensity, with a hydro-dependence interaction |
| C | Highest forest loss | Absolute loss favours large countries; tree cover loss includes plantation rotation | Rank on loss as % of 2000 tree cover and on permanent-agriculture-driven loss, 3-year averages |
| C | Agricultural expansion and deforestation | Annual FAO land series are interpolated | Period-level (5-year) association between cropland expansion and FRA deforestation, cross-checked with GFW driver data |
| D | Greatest water stress | Valid as a cross-section | Unchanged, with measured-or-modelled flags shown |
| D | Are water risks increasing? | Too few measured observations for most countries | Answer only for countries with at least 3 measured AQUASTAT points; otherwise report "insufficient data" |
| E | Greatest biodiversity pressure | Raw threatened counts track species richness | Red List Index level and trend; threatened counts normalised by assessed species |
| E | Deforestation and biodiversity threat | Snapshot counts cannot test change | Cross-country association between primary forest loss and Red List Index change, stated as exploratory |
| E | Protected areas and outcomes | Protected area is designation, not effectiveness; reverse causality likely | Descriptive comparison only, with the limitation stated |
| F | Does development improve resilience? | ND-GAIN readiness embeds economic variables | Association between GDP per capita and the vulnerability components that exclude economic inputs, plus the ND-GAIN GDP-adjusted score |

---

---

## 6. Data availability

### 6.1 How coverage is measured

Section 7 of `01 Data.ipynb` measures, for every indicator and every African country, the share of the 25 years from 2000 to 2024 with an observed value. It also records the first and last year, the longest run of missing years and the count of zero values, so true zeros can be reviewed separately from missing values. Each indicator is then classified on Africa-wide coverage:

- **Panel ready:** 80% or more of country-years observed.
- **Limited panel:** 50% to 80%.
- **Descriptive or cross-section only:** under 50%.

### 6.2 What the measured coverage shows

- 68 of the 79 indicators pulled are complete enough for panel work.
- Below 50% coverage: threatened species counts (a single snapshot year), disaster exposure (one 1990 to 2009 average), marine protected areas and terrestrial protected areas. These are used for cross-section comparisons only.
- The quality checks in Section 8 of `01 Data.ipynb` confirm that FAO forest area and AQUASTAT water series are largely drawn in straight lines between survey years.
- Indicators that need an API key or a manual file (Global Forest Watch, IRENA, CCKP, IUCN, FRA 2025) are listed in the catalogue but not pulled.

### 6.3 What coverage decides

- Which indicators enter the panel models (coverage rule plus quality flags).
- Which countries drop out of each model, and whether drop-outs are systematic (e.g. conflict states), which would bias results.
- The common analytical window per model.
- Where "missing" is genuinely missing and where it is "not applicable".

---

## 7. Methodological limitations by dimension

**A Carbon.** EDGAR values for African countries are modelled from activity data and default emission factors, not measured inventories. Methane and nitrous oxide from agriculture use Tier 1 defaults with wide uncertainty. Excluding LULUCF removes the largest emissions source for forest economies. Consumption-based emissions (adjusted for trade) are not available for most African countries. Small bases make percentage growth unstable.

**B Energy.** Final-energy renewable share is biomass-dominated (finding 1). Hydro output swings with rainfall (Zambia and Zimbabwe during the 2015 to 2016 and 2024 droughts), so year-on-year renewable shares partly measure weather. Off-grid solar is under-recorded in national statistics. Ember shares are of generation, not consumption, and exclude imports, which matters for importers such as Namibia and Botswana. The IEA-based WDI series carry IEA terms, so check before publishing raw values.

**C Forests.** FAO annual series are interpolated (finding 3). FRA data for data-poor countries are often desk estimates. GFW tree cover loss depends on the canopy threshold (default 30%), includes non-deforestation loss, and changed methodology around 2011 and 2015 (finding 4). Tree cover gain cannot be netted against loss. Satellite and national figures will disagree, and the reasons should be documented, not reconciled by force.

**D Water.** AQUASTAT is sparse and partly modelled (finding 5). Internal renewable resources exclude transboundary inflows, so Egypt and Botswana look worse than their actual supply. Withdrawal shares can exceed 100% of internal resources. Safely managed water is missing for many countries because quality testing data is not collected.

**E Biodiversity.** Threatened counts are a snapshot driven by species richness and assessment effort (finding 6). Protected area is a legal designation, not evidence of effective management. IUCN terms restrict redistribution. The Red List Index is a better time series but is driven by a limited set of comprehensively assessed groups (birds, mammals, amphibians, corals, cycads).

**F Vulnerability.** ND-GAIN fills missing inputs internally and includes projected climate exposure that barely changes over time. Its overlap with GDP and governance makes regressions on those variables partly mechanical (finding 7). Disaster exposure in WDI is a single 1990 to 2009 average. EM-DAT is the better disaster source but has registration, non-commercial terms and known under-reporting for Africa before about 2000.

**G Controls.** WGI estimates have standard errors, and many year-to-year moves are within the margin of error. They were also biennial before 2002. GDP series are rebased periodically, so the vintage is recorded in every load. Income-group classifications change, so the history is kept, not just today's label.

**Cross-cutting.**
- Mixed observed, modelled and composite data must stay labelled through to the dashboard.
- Source vintages change values retrospectively. Every load records its vintage and a file hash, so results can be reproduced.
- Correlation results across 54 countries are dominated by a few large emitters (South Africa, Egypt, Algeria, Nigeria). Report results with and without them.

---

## 8. Analytical methods

**Panel econometrics.** `statsmodels` does not include panel fixed or random effects estimators, so add `linearmodels` (`PanelOLS`, `RandomEffects`). The specification plan:

- Dependent variables in logs per capita. Regressors: log GDP per capita (PPP) and its square (EKC test), renewable electricity share, urbanisation, population growth, agricultural value added share, natural resource rents, and governance (the first principal component of WGI, to avoid four collinear regressors).
- Country and year fixed effects as the baseline. Hausman test for random effects.
- **Driscoll-Kraay standard errors** as the default, because African economies share commodity cycles and droughts. Run the Pesaran CD test for cross-sectional dependence.
- Second-generation unit root tests (CIPS) before any cointegration claim. Python lacks a maintained Westerlund test. If cointegration becomes central, either implement it or run that single step in R or Stata, and document the step.
- Lag governance and income by one year to reduce simultaneity, and state that this does not establish causality.

**Clustering.** Cluster on standardised multi-year averages (e.g. 2015 to 2021), not single years, to dampen noise. Use PCA first to remove redundant indicators. Compare k-means with Ward hierarchical clustering. Validate with silhouette scores, bootstrap stability (Jaccard) and a sense-check of membership. Small island states may need separate treatment or robust scaling.

**Forecasting.** Forecast only series with at least 15 observed (not interpolated) annual points and no unresolved break. Use ETS and ARIMA with rolling-origin backtests against a naive benchmark. Publish 80% and 95% intervals. Keep forecasts in `data/forecasts.csv`, separate from observed data, with a distinct style in the dashboard. Do not forecast FAO forest area, AQUASTAT water or threatened species counts.

---

## 9. Data rules

- A value is left blank when it is not observed. Missing values stay missing: nothing is interpolated and nothing is filled with zero.
- "Not applicable" (for example, marine protected area for the 16 landlocked countries) is kept separate from "missing".
- Publisher flags (FAOSTAT E, I and X; World Bank observation status) are kept as published.
- Quality checks flag duplicates, outliers, year-on-year jumps, series breaks and suspected interpolation. They never change the data.
- Raw downloads in `data/raw/` are kept unchanged, so results can be reproduced and later runs work offline.
- Original units are kept, and any conversion or derived formula is recorded in the indicator dictionary.
- Forecasts are kept separate from observed data.
- IUCN raw data is not published in the repo.

## 10. Dashboard

**Plotly Dash with Dash Bootstrap Components.** It gives a multi-page layout, filters that apply to every visual, click-to-cross-filter between charts, KPI cards and choropleth maps. It runs locally with `python dashboard/app.py` and opens in the browser. Streamlit is quicker to build but reruns the whole page on every filter change and handles cross-filtering poorly, so it suits prototypes better than an executive dashboard.

**Pages:** 1 Overview, 2 Carbon emissions, 3 Renewable energy transition, 4 Forests, 5 Water stress, 6 Biodiversity, 7 Climate vulnerability, 8 African country comparisons.

**Standard visuals:** KPI cards (latest value, change since 2000, rank among 54), trend lines against comparators, ranked bar charts, an Africa choropleth, scatter plots for the relationships tested in the panel models, and coverage notes so gaps are visible instead of hidden.

**Integrity rules:**
- Every chart carries the indicator's definition, unit and source from the indicator dictionary.
- Missing values show as gaps, never as zero.
- Forecasts use dashed lines and shaded intervals with a "Forecast" label.
- No composite overall ranking. Rankings are per indicator, with the indicator's polarity stated.

---

## Sources consulted

- World Bank Data, EN.GHG.CO2.PC.CE.AR5 (EDGAR-based CO2 per capita): https://data.worldbank.org/indicator/EN.GHG.CO2.PC.CE.AR5
- World Bank Metadata Glossary, EN.ATM.CO2E.PC (legacy Climate Watch series): https://databank.worldbank.org/metadataglossary/world-development-indicators/series/EN.ATM.CO2E.PC
- World Bank API, ESG source 75 indicator list: https://api.worldbank.org/v2/source/75/indicators
- Sovereign ESG Data Portal updates: https://esgdata.worldbank.org/explore/stories
- World Bank Data, EG.ELC.RNEW.ZS (IEA terms): https://data.worldbank.org/indicator/EG.ELC.RNEW.ZS
- CCKP download and API documentation: https://climateknowledgeportal.worldbank.org/download-data
- CCKP on AWS open data: https://registry.opendata.aws/wbg-cckp/
- GFW Data API, umd_tree_cover_loss: https://data-api.globalforestwatch.org/dataset/umd_tree_cover_loss
- GFW, assessing trends in tree cover loss: https://www.globalforestwatch.org/blog/data/tree-cover-loss-satellite-data-trend-analysis
- FAO Statistical Database Terms of Use: https://www.fao.org/contact-us/terms/db-terms-of-use
- FAOSTAT API developer portal launch (April 2026): https://www.fao.org/statistics/highlights-archive/highlights-detail/faostat-launches-a-new-api-developer-portal-to-make-data-access-easier/en
- FAO FRA 2025 release: https://www.fao.org/newsroom/detail/global-deforestation-slows--but-forests-remain-under-pressure--fao-report-shows/en
- ND-GAIN download page: https://gain.nd.edu/our-work/country-index/download-data/
- ND-GAIN coverage (QoG Data Finder): https://datafinder.qog.gu.se/variable/gain_gaingdp
- ND-GAIN Technical Report 2024: https://gain.nd.edu/assets/581554/nd_gain_countryindex_technicalreport_2024.pdf
- IRENASTAT PxWeb: https://pxweb.irena.org/pxweb/en/IRENASTAT/
- IRENA Data overview: https://www.irena.org/Data
- IUCN Red List API usage terms: https://iucn-uk.github.io/iucnredlist
- Ember Yearly Electricity Data: https://ember-energy.org/data/yearly-electricity-data/
- OWID solar and wind share (download and API pattern): https://ourworldindata.org/grapher/share-of-electricity-production-from-solar-and-wind

