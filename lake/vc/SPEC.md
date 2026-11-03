# VC Report — Build Specification

Status: DECISIONS LOCKED — ready to build
Last updated: 2026-05-20

---

## Purpose

Build a single-page HTML report (`vc-comparison-q1-2026.html`) comparing Canadian and US venture capital in Q1 2026. The report must be accurate, internally consistent, and use data sourced exclusively from `lake/vc/clean/` JSON files. No numbers may be hard-coded in the HTML without a traceable entry in those files.

---

## Locked Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Canada quarterly series = **KPMG/PitchBook throughout** | Same methodology, same source, 25 unbroken quarters. See Methodology section for why. |
| D2 | Annual and quarterly normalized charts **share the same base year (2019=100)**. When one series has more data, both are plotted on the same chart. Triangle (▲) marks the first quarterly data point; square (■) marks the last. | Avoids two near-identical charts. Reader sees where the quarterly series starts and ends relative to the annual backbone. |
| D3 | Canada 2019 base = **$6.55B CAD** (average of CVCA $6.5B and BDC $6.6B — values are essentially identical) | Locked. US base = $156.5B USD (NVCA, unchanged). |
| D4 | Growth stage collapse is shown **in context of the full annual stage chart**, not in a standalone bar. No separate "collapse vs 5-yr avg" chart. **DRY** — if the broader chart tells the story, a duplicate chart is noise. |

---

## Data Rules

1. **Every chart data array must reference a clean JSON file + field path.**
2. **No mixing series within a single chart.** CVCA and KPMG cannot share an axis. NVCA and KPMG cannot share an axis. One methodology per chart.
3. **Confidence floors:**
   - Stat chips: `high` only
   - Trend/line charts: `high` or `medium`; medium points shown with hollow or lighter marker
   - Stage charts: `high` for dollar values; `medium` accepted for deal counts
4. **Currency labelled on every axis and chart title.**
5. **Derived/estimated values footnoted.**

---

## Methodology: Why KPMG for Quarterly + Why Two Series Exist

This section must appear verbatim (or condensed version) in the report's Methodology section.

### The two Canada data series

**CVCA (Canadian Venture Capital & Private Equity Association):** Member-reported data. The authoritative source for Canadian VC. Published quarterly in CAD. Captures a broader set of deals because it draws directly from fund managers operating in Canada. However, quarterly reports are only publicly available for select periods; Q2–Q4 2025 were not accessible at time of writing.

**KPMG/PitchBook:** PitchBook's global deal database, used by KPMG in their Venture Pulse report. Published quarterly for 25+ countries using consistent methodology. For Canada, this series runs Q1-2020 through Q1-2026 without gaps. However, it systematically underestimates Canadian VC by 10–30% relative to CVCA because PitchBook does not capture all Canadian fund-manager-reported activity, particularly smaller seed and angel deals that CVCA members disclose directly.

**Why we use KPMG for trend charts:** The quarterly trend and normalized index charts require a continuous, gap-free series covering both countries simultaneously with identical methodology. Mixing CVCA and KPMG within one Canada series would introduce a ~15% step-change at the seam. The KPMG series provides 25 unbroken quarters for both US and Canada from the same data provider, making it the only internally consistent option for trend comparison. All absolute dollar figures in narrative text use CVCA where available.

### The two US data series

**NVCA/PitchBook Venture Monitor:** Published quarterly by the National Venture Capital Association using PitchBook data. The standard benchmark for US VC. Used for all US headline figures in this report (Q1-2025 onward confirmed directly; Q1-2020–Q4-2024 from KPMG chart extraction).

**KPMG Venture Pulse US series:** Also PitchBook-sourced but with different deal-inclusion filters at the global aggregation level. Diverges materially from NVCA for some quarters (example: NVCA Q1-2025 = $91.5B vs KPMG Q1-2025 = $56.0B — a 39% gap). The KPMG US series is used **only** in the quarterly normalized index chart (Chart 4b) to maintain methodological parity with the KPMG Canada series. It is not used for any standalone US headline figures.

### Exchange rate

CAD/USD conversion at **0.72** (approximate Q1 2026 market rate). Used only where explicit USD comparisons are made (stage ratio table, stat chips). All Canada trend charts are in CAD to avoid compounding currency uncertainty with data uncertainty.

---

## Data Coverage Summary

| Series | Quarters / Years | Confidence | Used in |
|---|---|---|---|
| US quarterly (NVCA direct) | Q1-2025 – Q1-2026 (5 qtrs) | High | Chart 2 |
| US quarterly (KPMG chart) | Q1-2020 – Q4-2024 (20 qtrs) | Medium | Chart 4b overlay |
| Canada quarterly (KPMG) | Q1-2020 – Q1-2026 (25 qtrs) | Medium | Charts 3, 4b |
| Canada quarterly (CVCA) | Q1-2019 – Q1-2025 (spot-checks) | High | Narrative text, stat chips |
| US annual (NVCA) | 2016–2025 (10 yrs) | High | Chart 4a |
| Canada annual (BDC/CVCA) | 2015–2025 (11 yrs) | High (medium for 2015–2018) | Chart 4a |
| Canada stage annual | 2020–2024 | High (2023 seed/early medium) | Chart 5 |
| Canada stage Q1 snapshots | Q1-2024, Q1-2025, Q1-2026 | Medium | Chart 6 |

---

## Charts — Acceptance Criteria

### Chart 1 · US Q1 2026 Composition

**Type:** Horizontal stacked bar (1 bar)
**Source:** `top_deals.json` → `us_q1_2026_decomposition`
**Unit:** USD billions

| Segment | Value | Derivation |
|---|---|---|
| OpenAI | $122.0B | direct — `openai.amount_usd_b` |
| Anthropic + xAI + Waymo | $66.6B | $30.6 + $20.0 + $16.0 |
| Other | $78.6B | $267.2B − $122.0B − $66.6B (includes Databricks $7B + all remaining deals) |
| **Total** | **$267.2B** | ✓ exact |

**Done when:** Bar sums to exactly $267.2B. Three segments, colour-coded. Tooltip shows USD amount. Chart note: "Top 5 deals (OpenAI, Anthropic, xAI, Waymo, Databricks) account for $195.6B (73%). Remaining $71.6B is everything else."

---

### Chart 2 · US Quarterly Trend (KPMG, 25 quarters)

**Type:** Bar chart
**Source:** `us_quarterly.json` → `data`, Q1-2020 through Q1-2026 (all 25 quarters)
**Unit:** USD billions
**Series:** KPMG values throughout for methodological consistency with Chart 3

| Quarters | Source | Confidence | Visual treatment |
|---|---|---|---|
| Q1-2020 – Q4-2024 | KPMG chart | Medium | Standard opacity |
| Q1-2025 – Q1-2026 | NVCA direct | High | Full opacity |

Note: NVCA and KPMG diverge for some quarters (e.g. Q1-2025: NVCA=$91.5B vs KPMG=$56.0B). Chart 2 uses KPMG throughout to match Chart 3's methodology. NVCA values are used for all narrative text and stat chips.

**Done when:** 25 bars, no gaps, Q1-2026 in burgundy, Y-axis "USD Billions". Chart note: "Source: KPMG/PitchBook. NVCA Venture Monitor figures differ for Q1-2025 onward (see Methodology); NVCA values cited in narrative text."

---

### Chart 3 · Canada Quarterly Trend (KPMG, 25 quarters)

**Type:** Bar chart
**Source:** `canada_quarterly.json` → `series_kpmg_pitchbook`
**Unit:** CAD millions
**Quarters:** Q1-2020 through Q1-2026 (25 bars)
**Confidence:** Medium throughout

Key values to verify in rendering:
- Q4-2021 (peak): $3,560.7M
- Q4-2025 (near-peak): $3,923.5M  
- Q1-2026 (current): $1,017.2M

**Done when:** 25 bars, no gaps, Q1-2026 in burgundy, Q4-2025 annotated (unusually high — investigate/note), Y-axis "CAD Millions", chart note: "Source: KPMG Venture Pulse / PitchBook. Values are ~10–15% lower than CVCA member-reported data for the same periods (see Methodology)."

---

### Chart 4 · Normalized Index — Annual + Quarterly Overlay (combined)

**Decision D2 implemented here.** Annual and quarterly share the same 2019=100 base. Both are plotted on the same chart.

**Type:** Multi-series line chart
**Unit:** Index (2019 = 100)

#### 4a — Annual backbone (2016–2025)

**Source:** `us_annual.json` + `canada_annual.json`
**Base:** US = $156.5B USD (2019); Canada = $6.55B CAD (2019, D3)
**Point style:** Filled circles

| Year | US raw | US idx | CA raw | CA idx |
|---|---|---|---|---|
| 2016 | 83.7 | 53.5 | 3.0 | 45.8 |
| 2017 | 93.6 | 59.8 | 3.8 | 58.0 |
| 2018 | 149.7 | 95.7 | 3.8 | 58.0 |
| 2019 | 156.5 | 100.0 | 6.55 | 100.0 |
| 2020 | 175.5 | 112.1 | 4.6 | 70.2 |
| 2021 | 358.1 | 228.8 | 15.4 | 235.1 |
| 2022 | 236.2 | 150.9 | 10.4 | 158.8 |
| 2023 | 167.3 | 106.9 | 7.1 | 108.4 |
| 2024 | 212.6 | 135.8 | 8.5 | 129.8 |
| 2025 | 339.4 | 216.9 | 8.0 | 122.1 |

Estimated points (hollow marker): Canada 2016–2018 (BDC/PitchBook, not CVCA)

#### 4b — Quarterly overlay (Q1-2020 through Q4-2025, excluding Q1-2026)

**Source:** `us_quarterly.json` (KPMG values) + `canada_quarterly.json` → `series_kpmg_pitchbook`
**Base:** US quarterly base = $156.5B / 4 = $39.125B; Canada quarterly base = $6,550M / 4 = $1,637.5M
**Index calc:** `quarterly_value / base * 100`
**Point style:** ▲ triangle on first point (Q1-2020), ■ square on last point (Q4-2025), small dots in between
**Line style:** Dashed (to distinguish from annual solid lines)
**Note:** Q1-2026 excluded from overlay — US value ($267.2B → idx 682) is so far above scale it would crush the rest of the chart. Show Q1-2026 as an annotated off-chart callout instead.

Key quarterly index values (spot checks):
- US Q1-2020: $39.5B / $39.125B × 100 = **101.0** (starts near 100 — good anchor)
- CA Q1-2020: $1,017.2M / $1,637.5M × 100 = **62.1**
- US Q4-2021 (peak): $100.6B / $39.125B × 100 = **257.1**
- CA Q4-2025 (high): $3,923.5M / $1,637.5M × 100 = **239.6**
- US Q4-2025: $91.6B / $39.125B × 100 = **234.1**

**Done when:**
- Annual lines (solid, circles) cover 2016–2025 for both countries
- Quarterly overlay lines (dashed, small dots) cover Q1-2020–Q4-2025
- ▲ on Q1-2020 quarterly point, ■ on Q4-2025 quarterly point, for each country
- Q1-2026 shown as annotated callout: US idx ≈ 682, Canada idx ≈ 62
- Estimated annual points (Canada 2016–2018) in hollow/lighter style
- Y-axis: "Index (2019 = 100)", reference line at 100
- Legend: 4 entries — "US Annual (NVCA)", "Canada Annual (CVCA/BDC)", "US Quarterly (KPMG)", "Canada Quarterly (KPMG)"
- Chart note: "Annual and quarterly series share a common 2019=100 base (quarterly scaled to annual by dividing by 4). Quarterly uses KPMG/PitchBook data for both countries for methodological consistency. US Q1-2026 index (~682) is off-scale due to OpenAI mega-round; shown as callout."

---

### Chart 5 · Canada Annual Stage Breakdown (2020–2024)

**Type:** Stacked bar (years on x-axis, stages stacked) OR grouped bar
**Preferred:** Stacked — shows total and composition simultaneously; reader sees growth-stage collapse in context of the full stack without a dedicated chart (D4)
**Source:** `canada_stage_annual.json` → `data`, years 2020–2024
**Unit:** CAD millions

| Year | Pre-seed | Seed | Early | Later | Growth | Total | Confidence |
|---|---|---|---|---|---|---|---|
| 2020 | — | 603 | 1480 | 787 | 220 | 4600 | Medium — approximate chart reads; Pre-seed not available |
| 2021 | 161 | 958 | 4310 | 3050 | 1809 | ~15400 |
| 2022 | 241 | 851 | 4030 | 2394 | 328 | ~10400 |
| 2023 | 163 | 927* | 3155* | 2184 | 91 | ~7100 |
| 2024 | 99 | 510 | 2930 | 2129 | 1487† | ~8500 |

*Derived (medium confidence) — lighter fill or hatching
†2024 Growth inflated by Clio $1.24B; annotate bar

**Done when:**
- 5 stacked bars (2020–2024), each stage a distinct colour
- Derived values (2023 Seed, 2023 Early) visually marked
- 2020 included with visual caveats: all 2020 bars lighter/hatched; Pre-seed bar absent; chart note flags 2020 as approximate
- 2021–2024 shown at full opacity
- Clio annotation on 2024 Growth bar
- Note: "2024 Growth Equity includes Clio's $1.24B Series F (84% of stage total); ex-Clio = $247M"
- Y-axis: "CAD Millions (annual)"

---

### Chart 6 · Canada Q1 Stage Snapshots (Q1-2024, Q1-2025, Q1-2026)

**Why this is not redundant with Chart 5 (DRY check):** Chart 5 shows annual totals across years. This shows Q1-to-Q1 comparison — same seasonal unit, 3 consecutive years. It answers "is Q1-2026 actually a departure from the Q1 trend, or is Q1 always weak?" That is a different question from the annual view.

**Type:** Grouped bar (stages on x-axis, years as bar groups)
**Source:** `canada_stage_annual.json` → `quarterly_snapshots`
**Unit:** CAD millions
**Scale:** Log scale (D4 — show all data including near-zero Growth; linear scale collapses $1M into invisibility)

| Stage | Q1-2024 | Q1-2025 | Q1-2026 |
|---|---|---|---|
| Seed/Pre-seed | 119 | 101 | 185 |
| Early (A–B) | 576 | 376 | 651 |
| Later (C–D) | 278 | 349 | 248 |
| Growth (E+) | 26 | 17 | 1 |

**Done when:**
- Log Y-axis, label "CAD Millions (log scale)"
- All 4 stage groups rendered with 3 bars each
- Growth stage bars visible at log scale (no stage suppressed)
- Chart note: "Log scale used so all stages are visible. Q1-2026 Growth Equity = $1M (1 undisclosed deal) vs $140M five-year Q1 average (CVCA via Globe and Mail)."
- Source: CVCA Q1-2024, Q1-2025, Q1-2026 (Q1-2026 from press materials — medium confidence)

---

### Chart 7 · US vs Canada Stage Comparison (Q1-2026, Log Scale)

**Type:** Grouped bar, log Y-axis
**Source:** `canada_stage_annual.json` → `quarterly_snapshots[Q1-2026]` + `top_deals.json` → `us_q1_2026_decomposition`
**Unit:** USD billions (Canada converted at 0.72)

| Stage | US Headline | US ex-Top-5 | Canada (USD) |
|---|---|---|---|
| Seed/PS | ~10.0B* | ~10.0B | 0.133B |
| Early (A–B) | 25.1B | 25.1B | 0.469B |
| Later+Growth (C+) | 222.4B* | ~33.8B* | 0.179B |

*Estimated — badge or lighter colour

**Done when:**
- Log scale, 3 grouped bars per stage
- Estimated values labelled
- Note: "US Later+Growth distorted by OpenAI, Anthropic, xAI, Waymo mega-rounds ($188.6B). Ex-Top-5 = ~$33.8B. Log scale — each gridline = 10×."

---

## Stat Chips — Acceptance Criteria

| Label | Value | Source | Confidence |
|---|---|---|---|
| US Q1 2026 · All Stages | $267B USD | `us_quarterly.json` NVCA Q1-2026 | High |
| Canada Q1 2026 · All Stages | $936M CAD | `canada_quarterly.json` CVCA spot-check | Medium |
| All-Stage Ratio (headline) | 396× | $267.2B / ($936M × 0.72 / 1000) = 396× | Medium |
| All-Stage Ratio (ex top-5) | 107× | $71.6B / ($936M × 0.72 / 1000) = 107× | Medium |

---

## Section Structure

| # | Title | Charts | Key claim |
|---|---|---|---|
| 1 | What's Inside the $267B | Chart 1 | Top-5 = $195.6B (73%); ex-top-5 = $71.6B |
| 2 | 25-Quarter Trend | Charts 2 + 3 | US record high; Canada at 25-quarter low |
| 3 | A Decade in Context | Chart 4 (combined annual+quarterly) | Both markets moved in lockstep 2019–2022; diverged after |
| 4 | VC Stage-wise Comparison | Charts 5 + 6 + 7 | Annual stage trend; Q1 seasonal comparison; US vs CA cross-section |
| 5 | Key Findings | Text cards | Derived from charts — no new data introduced |
| 6 | Methodology & Sources | Text | Full methodology section from this spec |

Total charts: **7** (down from 8 in previous draft; "growth vs 5-yr avg" bar removed per D4)

---

## Done Definition (overall)

The report is complete when:
- [ ] All chart data traces to a `lake/vc/clean/*.json` field
- [ ] No chart mixes CVCA and KPMG on the same series
- [ ] No chart mixes USD and CAD on the same axis without explicit labelling
- [ ] Chart 4 renders with both annual (solid) and quarterly (dashed) overlays, correct ▲/■ markers
- [ ] Chart 4 Q1-2026 US callout shown off-scale
- [ ] Chart 5 stacked bar shows growth-stage collapse in annual context (no separate collapse chart)
- [ ] Chart 6 uses log scale — all 4 stages visible including $1M Growth
- [ ] All 7 charts render without console errors
- [ ] Every chart has a `chart-note` with source citation
- [ ] Methodology section explains CVCA vs KPMG, NVCA vs KPMG, exchange rate, and index calculation
- [ ] 4 stat chips correct within stated confidence level
