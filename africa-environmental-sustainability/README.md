# Environmental Sustainability in Africa: Emissions, Energy, Forests, Water, Biodiversity and Climate Risk

A data analysis of environmental sustainability across 54 African countries, with global comparisons, 2000 to 2024. It uses real data pulled from the World Bank, Our World in Data (Global Carbon Budget, Ember), ND-GAIN, the UN SDG database and FAOSTAT.

**Author:** Martin B. Mwaala, Qualified Accountant (ZICA) | MSc Financial Engineering | MBA Finance

![CO2 per capita, Africa against the world](outputs/02%20carbon/co2%20per%20capita%20trend.png)

## Key findings

| Hypothesis (within countries, fixed effects, Driscoll-Kraay SE) | Result | Verdict |
|---|---|---|
| H1 Income goes with higher CO2 per capita | 0.627, p < 0.001 | Supported |
| H1 Inverted U (environmental Kuznets curve) | turning point about 64,000 PPP $ per person | Outside Africa's income range |
| H2 Higher renewable electricity share goes with lower CO2 intensity | -0.001, p = 0.26 | Not significant |
| H3 Development goes with more renewable electricity | -10.45, p < 0.001 | Rejected: significant but opposite sign |
| H4 More agricultural land goes with more tree cover loss | 0.056, p < 0.001 | Supported |
| H5 Richer countries face less climate exposure (across countries) | 0.002, p = 0.79 | Not significant |

- **Low per person, concentrated in total:** the median African country emits 0.49 t CO2e per person against a world average of 4.7 t. Five countries (South Africa, Egypt, Algeria, Nigeria and Morocco) produce 72.7% of Africa's fossil CO2.
- **Methane is the main greenhouse gas** for the median African country (56% of the total, against 18% worldwide).
- **Land use is the bigger CO2 source in 25 of 53 countries.** In DR Congo it is 513 Mt against 6 Mt fossil, and in Zambia 50 Mt against 12 Mt.
- **Grids are still mostly fossil:**
  - The average country's grid is 58% fossil, almost unchanged since 2000.
  - Solar and wind grew from near zero to about 7%.
  - 18 countries get half or more of their power from hydro, including Zambia (86%).
- **Tree cover loss roughly tripled**, from about 1.3 million ha a year (2001 to 2003) to about 4 million ha (2022 to 2024). DR Congo accounts for a third of it.
- **Water stress is a North African problem:** Libya, Algeria, Egypt and Sudan withdraw more than their renewable supply.
- **Biodiversity is declining almost everywhere:** the Red List Index fell in 98% of countries.
- **Climate vulnerability eased in 89% of countries, but readiness rose in only 40%.** 17 countries are both highly vulnerable and poorly prepared.
- **On current trends**, the median country reaches about 67% electricity access by 2030, short of universal access (SDG 7).

## Why it matters for finance

- Climate risk in Africa sits in different places in different countries:
  - In North and South Africa it is fossil CO2, exposed to carbon pricing and the EU's carbon border adjustment (CBAM).
  - In Central and Southern Africa it is land use, methane, drought and hydro dependence.
- For lenders, investors and treasury teams, a single per-capita CO2 metric misses most of that.
- The panel results show that African growth still raises emissions and lowers the renewable share of electricity. Power-sector financing decisions are therefore effectively choosing the continent's emissions path.

## Notebooks

| Notebook | What it does |
|---|---|
| `01 Data.ipynb` | Pulls every source, checks coverage and quality, builds the country-year panel and data dictionary |
| `02 Carbon Emissions.ipynb` | Emissions levels, growth, gas mix, carbon intensity, land-use CO2 |
| `03 Renewable Energy.ipynb` | Electricity mix, solar and wind growth, hydro dependence, access |
| `04 Forests and Land.ipynb` | Forest cover, tree cover loss, primary forest, agricultural expansion |
| `05 Water.ipynb` | Water stress, irrigation pressure, trends, drinking water |
| `06 Biodiversity.ipynb` | Red List Index, threatened species, protected areas |
| `07 Climate Vulnerability.ipynb` | ND-GAIN vulnerability, readiness, components, income links |
| `08 Panel Models.ipynb` | Fixed and random effects, Driscoll-Kraay errors, Pesaran CD, CIPS, robustness |
| `09 Country Clustering.ipynb` | PCA, k-means and Ward clustering, bootstrap stability |
| `10 Forecasting.ipynb` | Drift, ETS and ARIMA forecasts to 2030 with backtests and intervals |

Each notebook opens with its questions and hypotheses and writes its charts and Excel tables to `outputs/`.

## Dashboard

A Python dashboard (Plotly Dash), styled like Power BI, with 8 pages: overview, the six dimensions, and country comparisons. It has filters, cross-filtering from the map, KPI cards, rankings and forecast overlays.

```
python dashboard/app.py      # then open http://127.0.0.1:8050
```

## Run it

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Then run the notebooks in order (01 first). Raw downloads are kept in `data/raw/`, so later runs work offline. To pull fresh data, set `REFRESH = True` in `01 Data.ipynb`.

## Data rules

- Missing values stay missing. Nothing is interpolated and nothing is filled with zero.
- Publisher flags are kept. Suspected interpolation, jumps and breaks are flagged, never overwritten.
- Forecasts are kept separate from observed data.
- Results are associations, not causal effects.

## Sources

World Bank World Development Indicators, Sovereign ESG data and Worldwide Governance Indicators (CC BY 4.0); Our World in Data CO2 and energy datasets (Global Carbon Budget, Ember, Energy Institute; CC BY 4.0); ND-GAIN Country Index 2026, University of Notre Dame; UN SDG Global Database, Red List Index (IUCN, BirdLife); FAOSTAT Land Use (CC BY 4.0).
