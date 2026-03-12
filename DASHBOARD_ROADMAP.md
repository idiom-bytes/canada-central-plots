# Canada Central Plots: Dashboard Roadmap

## Existing Dashboards (16 total)

### Fiscal (📊)
- **Deficit / Surplus Per Capita** — Annual budgetary balance, federal + 10 provinces (Finance Canada)
- **Net Debt Per Capita** — Accumulated government debt (Finance Canada)
- **Government Revenue Per Capita** — Total revenue by level of government (StatCan 36-10-0450)
- **Government Spending Per Capita** — Total expenditure by level of government (StatCan 36-10-0450)

### Economy (🏭)
- **GDP Per Capita** — Real GDP per person by province (StatCan 36-10-0222)
- **Median Weekly Wages** — Earnings by province (StatCan 14-10-0064)
- **Employment by Sector** — Public vs. private sector employment (StatCan 14-10-0288)

### Housing (🏠)
- **Housing Starts** — Annual housing starts by province (StatCan 34-10-0135)
- **New Housing Price Index** — NHPI indexed over time (StatCan 18-10-0205)
- **Rental Vacancy Rate** — CMA-level vacancy data (CMHC, manual)

### Crime (🔴)
- **Crime Severity Index** — Total, violent, non-violent CSI (StatCan 35-10-0026)
- **Crime Breakdown** — Detailed crime category analysis (StatCan 35-10-0026)
- **Homicide Rate** — Per 100K population (StatCan 35-10-0068)

### Demographics (👥)
- **Population** — Provincial population estimates (StatCan 17-10-0005)
- **Population Growth Rate** — Annual growth percentage (StatCan 17-10-0005)
- **International Immigration** — Immigration by province (StatCan 17-10-0014)
- **Interprovincial Migration** — Net migration flows (StatCan 17-10-0045)

### Cross-Cutting
- **Provincial Scorecard** — 15 metrics across 5 verticals, composite grades (scorecard.html)

---

## 10 Verticals for Federal/Provincial Analysis

### 1. Housing & Real Estate
The housing crisis is the defining economic issue for a generation of Canadians. Provincial policies (zoning, rent control, foreign buyer bans) vary wildly and outcomes diverge just as much.

**Data sources:**
- StatCan Table 18-10-0205: New Housing Price Index by province
- CMHC Housing Starts & Completions (monthly, by province)
- StatCan Table 46-10-0065: Average home prices by province
- CREA MLS Home Price Index

**Potential dashboards:**
- Housing starts vs. completions (supply pipeline gap)
- Average home price indexed over time (affordability trajectory)
- Price-to-income ratio by province
- Rental vacancy rates

---

### 2. Immigration & Population Growth
Immigration policy is federal but outcomes are felt provincially. Population growth rates, temporary vs. permanent residents, and interprovincial migration tell very different stories depending on where you look.

**Data sources:**
- StatCan Table 17-10-0009: Population estimates quarterly by province
- IRCC Open Data: Permanent residents, temporary residents, study permits, work permits by province
- StatCan Table 17-10-0045: Interprovincial migration

**Potential dashboards:**
- Population growth rate by province (total, natural, migratory)
- Temporary vs. permanent residents as % of population
- Interprovincial migration flows (who's leaving, who's arriving)
- International students and work permit holders by province

---

### 3. Healthcare Performance
Healthcare is provincially administered but federally funded through transfers. Wait times, spending per capita, and physician density vary enormously and are central to every provincial election.

**Data sources:**
- CIHI (Canadian Institute for Health Information): Wait times, spending, workforce
- StatCan Table 13-10-0451: Health expenditure by province
- Fraser Institute annual wait time surveys
- StatCan Table 13-10-0096: Health indicators by province

**Potential dashboards:**
- Health spending per capita by province (vs. outcomes)
- Median wait times for specialist referral to treatment
- Physicians and nurses per 100,000 population
- Federal health transfers as % of provincial health budgets

---

### 4. Crime & Public Safety
Crime rates have been rising nationally since 2015 after decades of decline. The Crime Severity Index captures both volume and severity, and provincial variation is significant.

**Data sources:**
- StatCan Table 35-10-0026: Crime Severity Index by province
- StatCan Table 35-10-0177: Incident-based crime statistics
- StatCan Table 35-10-0015: Homicide rates by province
- StatCan Table 35-10-0066: Police-reported hate crimes

**Potential dashboards:**
- Crime Severity Index over time (violent + non-violent)
- Homicide rate per 100,000 by province
- Property crime vs. violent crime trends
- Incarceration rates and correctional spending

---

### 5. Education & Workforce Development
Education is provincial jurisdiction. Post-secondary attainment, PISA scores, apprenticeship completions, and education spending per student reveal which provinces are investing in human capital.

**Data sources:**
- StatCan Table 37-10-0027: Education spending by province
- StatCan Table 37-10-0130: Post-secondary enrollment
- OECD PISA results (provincial breakdowns available for Canada)
- StatCan Table 37-10-0023: Apprenticeship registrations and completions

**Potential dashboards:**
- Education spending per student by province
- Post-secondary attainment rates (25-64 age group)
- Apprenticeship completions (trades pipeline)
- Student debt levels at graduation

---

### 6. GDP & Productivity
Canada's productivity crisis is well-documented. GDP per capita has been stagnant while the US pulls ahead. Provincial GDP composition (resource-dependent vs. diversified) tells a critical story.

**Data sources:**
- StatCan Table 36-10-0222: GDP by province (expenditure-based)
- StatCan Table 36-10-0402: GDP by industry by province
- StatCan Table 36-10-0480: Labour productivity by province
- StatCan Table 36-10-0303: GDP per capita

**Potential dashboards:**
- Real GDP per capita by province (indexed to a base year)
- GDP growth rate by province
- Labour productivity (GDP per hour worked)
- GDP composition by industry (resource vs. services vs. manufacturing)

---

### 7. Tax Revenue & Government Spending
How much does each government collect, and where does it spend? Comparing revenue mix (income tax, sales tax, resource royalties) and expenditure categories reveals structural differences between provinces.

**Data sources:**
- Finance Canada Fiscal Reference Tables (same source as deficit/net debt)
- StatCan Table 10-10-0024: Government revenue by source
- StatCan Table 10-10-0005: Government expenditure by function
- Provincial budget documents

**Potential dashboards:**
- Revenue per capita by source (income tax, sales tax, transfers, royalties)
- Spending per capita by function (health, education, social services, debt servicing)
- Debt servicing costs as % of revenue (fiscal room indicator)
- Federal transfers as % of provincial revenue (dependency ratio)

---

### 8. Cost of Living & Inflation
CPI tells you inflation, but provincial CPI diverges meaningfully. Food, shelter, and energy costs hit differently in Halifax vs. Calgary. This is what Canadians feel in their daily lives.

**Data sources:**
- StatCan Table 18-10-0004: CPI by province (monthly)
- StatCan Table 18-10-0005: CPI by product group by province
- StatCan Table 11-10-0190: Market Basket Measure (poverty thresholds)
- StatCan Table 11-10-0239: Median income by province

**Potential dashboards:**
- CPI inflation rate by province (headline + core)
- Food price index by province
- Shelter cost index by province
- Median household income vs. cost of living (purchasing power)

---

### 9. Energy & Environment
Canada's energy sector is both its economic engine and its political fault line. Provincial energy mix, emissions intensity, carbon pricing revenue, and renewable investment vary enormously.

**Data sources:**
- StatCan Table 25-10-0015: Electricity generation by province and fuel type
- Environment Canada: GHG emissions by province (National Inventory Report)
- Canada Energy Regulator: Provincial energy production and consumption
- NRCan Energy Fact Book

**Potential dashboards:**
- GHG emissions per capita by province
- Electricity generation mix (hydro, nuclear, gas, wind, solar)
- Oil and gas production by province
- Carbon pricing revenue and allocation

---

### 10. Labour Market & Income Inequality
Beyond headline employment, the quality of jobs matters. Wage growth, part-time vs. full-time, youth unemployment, and income inequality (Gini coefficient) paint a richer picture of economic well-being.

**Data sources:**
- StatCan Table 14-10-0064: Employee wages by province
- StatCan Table 14-10-0287: Labour force characteristics by province
- StatCan Table 11-10-0134: Gini coefficient by province
- StatCan Table 14-10-0036: Actual hours worked by province

**Potential dashboards:**
- Median wage growth (real, inflation-adjusted) by province
- Full-time vs. part-time employment share
- Youth unemployment rate (15-24) by province
- Income inequality (Gini coefficient) over time

---

## Next Wave: Trade & Structural Economy (4 dashboards)

These metrics go beyond snapshot comparisons to reveal **structural vulnerabilities** — trade dependencies, concentration risks, and economic fragility that make provinces susceptible to external shocks (tariffs, commodity busts, supply chain disruptions).

### 1. Trade Balance by Province (`economy-trade-balance`)
**Why:** Net exports reveal whether a province is earning or bleeding. Breaking this into international vs interprovincial shows whether domestic or foreign demand drives the economy.

**Data:** StatCan Table 36-10-0222 — already downloaded. Filter `Estimates` for export/import categories, `Prices="Current prices"`.

**Structural signal:** Alberta runs a massive international surplus (energy) but what happens when it shrinks? Ontario's trade balance reveals manufacturing competitiveness. Interprovincial trade shows internal dependency patterns.

**Scorecard metric:** Net trade balance per capita (higher = better).

---

### 2. Trade Openness (`economy-trade-openness`)
**Why:** (Exports + Imports) / GDP measures how exposed a province is to trade disruptions. High openness isn't inherently bad — but high openness + high concentration = high vulnerability.

**Data:** StatCan Table 36-10-0222 — total exports, total imports, and GDP are all in the same table.

**Structural signal:** A province with 80% trade openness and a single dominant sector is one tariff away from recession. Compare Alberta (energy-dependent openness) vs Ontario (manufacturing-dependent openness) vs Quebec (more balanced).

**Scorecard metric:** Trade openness ratio (informational, no grade — context for other metrics).

---

### 3. US Trade Dependency (`economy-us-trade-dependency`)
**Why:** THE tariff vulnerability metric. What % of each province's exports go to the US? This is the single most policy-relevant trade metric in the current political environment.

**Data:** StatCan Table 12-10-0119 — monthly provincial exports by trading partner. Aggregate to annual, compute US share = US exports / total exports.

**Structural signal:** Most provinces send 70-90% of exports to the US. Tracking this over 25 years reveals whether diversification rhetoric has produced actual results. Spoiler: mostly not.

**Scorecard metric:** US dependency % (lower = better, inverted — diversification is resilience).

---

### 4. Export Concentration Index (`economy-export-concentration`)
**Why:** The Herfindahl-Hirschman Index (HHI) across export sectors measures how fragile a province's export base is. HHI > 0.25 = dangerously concentrated.

**Data:** StatCan Table 12-10-0098 — provincial exports by NAICS sector (45 sectors, 2000–2024).

**Structural signal:** Alberta's HHI will be extremely high (oil+gas dominance). Ontario's will be moderate (auto + diversified manufacturing). Saskatchewan will be high (potash + agriculture). This quantifies the "Dutch disease" risk.

**Scorecard metric:** Export HHI (lower = better, inverted — diversification is resilience).

---

## Future Verticals (Not Yet Started)

### Healthcare Performance
- Health spending per capita vs outcomes
- Wait times, physician density
- **Data:** CIHI, StatCan 13-10-0451

### Education & Workforce
- Education spending per student, post-secondary attainment
- **Data:** StatCan 37-10-0027, 37-10-0130

### Cost of Living & Inflation
- Provincial CPI divergence, food/shelter indices
- **Data:** StatCan 18-10-0004, 18-10-0005

### Energy & Environment
- GHG per capita, electricity generation mix
- **Data:** StatCan 25-10-0015, Environment Canada NIR

### Labour Market & Income Inequality
- Real wage growth, Gini coefficient, youth unemployment
- **Data:** StatCan 14-10-0064, 11-10-0134

---

## Design Principles

All dashboards should follow the established pattern:
- **Entity chips** for Federal + 10 provinces
- **Bar charts** as default (consistent with deficit/net debt)
- **Smart unit scaling** (Billions vs. Millions based on data magnitude)
- **Data table below** with Copy + Download CSV
- **Inline data** (no fetch, works on file:// protocol)
- **Description paragraph** explaining what the metric measures and why it matters
- **Source attribution** with link to the official data source
- **Consistent color palette** matching canada-central.com design system

## Scorecard Evolution

The Provincial Scorecard (v1) is live with 15 metrics and A-D grades. Next evolution:

### Time-Series Scorecard (Issue #29)
- Compute grades for every year with sufficient data (2005–2024) → `scorecard_timeseries.json`
- Score components: **Level** (peer rank), **Trend** (EMA 3y vs 10y), **Momentum** (acceleration), **Stability** (volatility)
- Compare S(t) vs S(t-10y) to identify structural improvement or decline
- 3D Three.js visualizer: provinces × metrics × time, with timeline scrubber

### Methodology Improvements
- EMA (Exponential Moving Average) for smoothing noisy annual data
- Rolling windows for trend detection instead of simple 3yr vs 5yr comparison
- Historical baseline scoring: grade relative to "good periods" (10y, 20y ago), not just current peers
- Composite score weighting: allow user-adjustable importance sliders

## Long-Term Vision

| Layer | Status | Description |
|-------|--------|-------------|
| Data Pipeline | ✅ Done | StatCan CSV → JSON transform, 12 tables, 14 auto-generated files |
| Dashboards (v1) | ✅ Done | 16 dashboards across 5 verticals |
| Scorecard (v1) | ✅ Done | 15 metrics, A-D grades, composite scores |
| `/metric_architect` | ✅ Done | Claude Code skill for reproducible metric creation |
| Trade Dashboards | 🔜 Next | 4 structural economy dashboards (trade balance, openness, US dependency, concentration) |
| Scorecard (v2) | 🔜 Planned | Time-series grades, EMA, historical baselines (Issue #29) |
| 3D Visualizer | 🔜 Planned | Three.js matrix with timeline scrubber (Issue #29) |
| Healthcare | 📋 Backlog | CIHI data, wait times, spending vs outcomes |
| Education | 📋 Backlog | Post-secondary attainment, spending per student |
| Cost of Living | 📋 Backlog | Provincial CPI, food/shelter indices |
| Energy | 📋 Backlog | GHG per capita, electricity mix |
| Policy Cards | 📋 Backlog | Qualitative provincial policy comparison (see PROVINCIAL_POLICY_CARDS_ROADMAP.md) |

The mission: let Canadians objectively compare provincial governance outcomes, free of partisan framing. Every metric is sourced from official data, every dashboard follows the same pattern, and the scorecard evolves from snapshot to time-series to predictive.
