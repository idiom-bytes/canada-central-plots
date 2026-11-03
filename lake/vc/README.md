# VC Data Lake

Raw PDFs and extracted text in `raw/`. Clean structured data in `clean/`.

## Sources

| File | Source | Coverage | Confidence |
|---|---|---|---|
| `nvca-q1-2026.pdf` | PitchBook-NVCA Venture Monitor Q1 2026 | US Q1 2026 + annual 2016–2025 | High — primary US source |
| `nvca-q4-2025.pdf` | PitchBook-NVCA Venture Monitor Q4 2025 | US full-year 2025 + annual history | High |
| `nvca-q2-2025.pdf` | PitchBook-NVCA Venture Monitor Q2 2025 | US Q2 2025, H1 2025 | High |
| `nvca-q1-2025.pdf` | PitchBook-NVCA Venture Monitor Q1 2025 | US Q1 2025 | High |
| `nvca-q3-2025.pdf` | PitchBook-NVCA Venture Monitor Q3 2025 | US Q3 2025 | High |
| `cvca-yearend-2024.pdf` | CVCA Year-End 2024 | Canada full-year 2024 + quarterly 2020–2024 | High — primary Canada source |
| `cvca-q1-2025.pdf` | CVCA Q1 2025 Market Overview | Canada Q1 2025, revised 2024 annual | High |
| `cvca-q1-2024.pdf` | CVCA Q1 2024 Market Overview | Canada Q1 2024, annual 2019–2023 | High |
| `bdc-vc-landscape-2025.pdf` | BDC Canada VC Landscape 2025 | Canada annual 2015–2024, stage, sector | High — best historical Canada source |
| `kpmg-venture-pulse-q1-2026.pdf` | KPMG Venture Pulse Q1 2026 | Global + US + Canada quarterly Q1 2020–Q1 2026 | Medium — PitchBook data, methodology differs from CVCA |

## Methodology Warnings

**Two Canada data series exist — do not mix:**
- **CVCA series** (primary): CVCA member-reported data, higher deal capture for Canadian market. Published in CAD. ~10–15% higher than PitchBook for same periods.
- **KPMG/PitchBook series** (secondary): PitchBook-sourced, useful for quarterly completeness and directional trends where CVCA data has gaps. Published in CAD for Canada charts.

**Two US data series exist — do not mix:**
- **NVCA/PitchBook Venture Monitor** (primary): Standard US VC definition used throughout clean data files.
- **KPMG Venture Pulse US**: Also PitchBook data but with different deal inclusion filters. Q1 2025 example: NVCA = $91.5B vs KPMG = $56.0B for the same period. KPMG underweights large rounds differently.

**Canada 2024 revised:** CVCA originally reported $7.9B/592 deals (Year-End 2024 report). Revised upward to **$8.5B/619 deals** as of May 2025 (per BDC footnote and CVCA Q1 2025 report). Use $8.5B as the authoritative 2024 figure.

**CVCA Q1 2026:** Not publicly available as PDF at time of extraction (May 20, 2026). Q1 2026 Canada figures ($936M total, stage breakdown) sourced from prior session research: BetaKit, The Logic, CVCA press release. Confidence = Medium.

## Clean Data Files

| File | Contents |
|---|---|
| `us_quarterly.json` | US VC quarterly totals Q1 2020–Q1 2026 (NVCA, USD billions) |
| `us_annual.json` | US VC annual totals 2016–2025 (NVCA, USD billions) |
| `canada_quarterly.json` | Canada VC quarterly Q1 2019–Q1 2026 (CVCA spot-checks + KPMG series, CAD millions) |
| `canada_annual.json` | Canada VC annual totals 2015–2025 (BDC/CVCA, CAD billions) |
| `canada_stage_annual.json` | Canada VC by stage, annual 2020–2024 (CVCA, CAD millions) |
| `canada_stage_q.json` | Canada VC by stage, quarterly snapshots where available (CVCA, CAD millions) |
| `top_deals.json` | Large individual deals (US + Canada) with company, amount, date, stage |
