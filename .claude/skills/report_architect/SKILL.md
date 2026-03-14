---
name: report_architect
description: End-to-end workflow for creating an accountability report — from multi-source data research to data pipeline to multi-view investigative dashboard to reports page integration.
argument-hint: <report-topic-description> [optional data sources or URLs]
user-invocable: true
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Agent, WebSearch, WebFetch
---

# Report Architect

You are building an **accountability report** for **Canada Central** — a static site at `plots.canada-central.com`. Reports are investigative deep dives into specific problems, distinct from the metric dashboards used for provincial comparisons. Each report follows this pipeline:

```
Research → Data Collection → Transform → data/report-*.json → reports/*.html → reports.html → navbar
```

**Reports are NOT metrics.** They do not integrate into the scorecard. They live in `reports/`, link from `reports.html`, and tell a story with multiple chart views, contextual benchmarks, and a full data table.

**The user will give you a report topic and optionally data sources.** Follow every phase below in order. Do not skip steps. Ask the user to confirm at the end of Phase 1 before proceeding.

---

## Phase 1: Research & Planning

### 1a. Deep research the topic

Reports require thorough research before any code is written. Use WebSearch and WebFetch to find:

1. **Primary data sources** — StatCan tables, government reports, NGO publications, academic research
2. **Historical trend data** — go as far back as possible; long timescales make trends undeniable
3. **Provincial/territorial breakdowns** — every report should show geographic variation
4. **Demographic breakdowns** — who is affected? Age, gender, income, race, household type
5. **Benchmark/comparison data** — what makes this bad? Compare against:
   - Historical baseline ("X has doubled/tripled since YEAR")
   - International peers (G7, OECD averages)
   - Government targets or thresholds (poverty line, recommended intake, etc.)
   - Cost equivalents ("this costs taxpayers $X per year" or "equivalent to Y% of GDP")
6. **Accountability targets** — who is responsible? Which government body, policy, or decision?
7. **Key quotes** — officials, experts, affected people — that crystallize the failure

**Research checklist:**
- [ ] At least 2 independent data sources identified
- [ ] 10+ years of trend data found (or as much as exists)
- [ ] Provincial breakdown available
- [ ] At least 1 benchmark/comparison identified
- [ ] Cost or economic impact quantified
- [ ] Responsible institutions/actors identified

### 1b. Identify data sources for the pipeline

For each data source, determine:

| Source | Type | URL/Table | Format | Provincial? | Years | Notes |
|--------|------|-----------|--------|-------------|-------|-------|
| ... | StatCan / NGO / Gov | ... | CSV/JSON/scrape | Yes/No | YYYY-YYYY | ... |

**StatCan tables** (preferred for structured data):
- Pattern: `XX-XX-XXXX` (e.g. `13-10-0835`)
- Bulk CSV: `https://www150.statcan.gc.ca/n1/tbl/csv/{ID_NO_DASHES}-eng.zip`

**Non-StatCan sources** (NGO reports, government publications):
- Determine if data can be extracted programmatically or must be hardcoded
- For small datasets (< 100 rows), hardcoding inline in the HTML is acceptable
- For larger datasets, create a transform script

### 1c. Design the report structure

Every report needs these components:

1. **Headline statistics** (3-5 hero stat cards) — the numbers that shock
2. **Accountability narrative** — who is responsible and why
3. **Multiple chart views** (2-4 toggle-able views) — different angles on the same problem
4. **Benchmark visualization** — at least one chart/stat that contextualizes how bad it is
5. **Full data table** — every data point, with Copy and Download CSV

**Chart view ideas** (pick the most relevant):
- **Timeline** — trend over years (bar or line)
- **Provincial comparison** — horizontal bars or grouped bars
- **Demographic breakdown** — who's affected most
- **Composition** — stacked bars showing sub-categories
- **Rate of change** — year-over-year acceleration
- **Benchmark overlay** — Canada vs G7, vs targets, vs historical norm
- **Per-capita / normalized** — remove population bias
- **Cost/impact** — translate the problem into dollars

### 1d. Choose the report accent color

Reports use `--accent` for their theme. Pick based on the topic:

| Topic area | Accent | Rationale |
|-----------|--------|-----------|
| Economic destruction | `#8B2E2E` (deep red) | Loss, damage |
| Social welfare / poverty | `#6B4E2E` (dark brown) | Earthiness, gravity |
| Healthcare | `#2E5E6B` (dark teal) | Clinical, institutional |
| Education | `#4A3D6B` (deep purple) | Academic |
| Environment | `#2E4B3E` (dark green) | Nature, ecosystems |
| Infrastructure | `#5A4A3A` (dark taupe) | Built environment |
| Government spending | `#4A6FA5` (steel blue) | Institutional, fiscal |

### 1e. Define the report naming

Files follow the pattern:
- Data: `data/report-{slug}.json`
- Report HTML: `reports/{slug}.html`
- Transform (if needed): `pipeline/report_{slug}.py` or inline in HTML

### 1f. Confirm with user

Present:
- Report title and subtitle
- 3-5 headline statistics
- Data sources identified
- Chart views planned
- Accent color
- Benchmarks/comparisons that will be used
- Key accountability targets

Get confirmation before proceeding.

---

## Phase 2: Data Pipeline

### 2a. Download and inspect data

**For StatCan sources**, use the standard download pattern:

```bash
python3 -c "
import urllib.request, zipfile, os, shutil, csv
table_id = 'TABLE_ID'
table_clean = table_id.replace('-','')
url = f'https://www150.statcan.gc.ca/n1/tbl/csv/{table_clean}-eng.zip'
os.makedirs(f'pipeline/lake/{table_id}', exist_ok=True)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=120) as resp:
    with open(f'/tmp/{table_id}.zip', 'wb') as f:
        shutil.copyfileobj(resp, f)
with zipfile.ZipFile(f'/tmp/{table_id}.zip') as z:
    z.extractall(f'pipeline/lake/{table_id}')
os.remove(f'/tmp/{table_id}.zip')
with open(f'pipeline/lake/{table_id}/{table_clean}.csv', encoding='utf-8-sig') as f:
    r = csv.DictReader(f)
    rows = [next(r) for _ in range(5)]
    print('COLUMNS:', list(rows[0].keys()))
    for k in rows[0]:
        if k not in ('REF_DATE','GEO','DGUID','UOM','UOM_ID','SCALAR_FACTOR','SCALAR_ID','VECTOR','COORDINATE','VALUE','STATUS','SYMBOL','TERMINATED','DECIMALS'):
            vals = set()
            f.seek(0); next(f)
            for row2 in csv.DictReader(f):
                vals.add(row2.get(k,''))
                if len(vals) > 30: break
            print(f'{k}: {sorted(vals)[:15]}')
"
```

**For non-StatCan sources**, fetch and parse:
- Web scrape if structured HTML tables exist
- Download PDFs and extract data manually
- If data is small/irregular, hardcode it directly in the report HTML

### 2b. Build the transform

**If the data comes from StatCan or a large CSV**, create a standalone transform script:

```python
# pipeline/report_{slug}.py
"""Transform data for the {title} report.
Sources: {list sources}
Output: data/report-{slug}.json
"""
import csv, json, os
from collections import defaultdict

# Reuse pipeline utilities if available
import sys; sys.path.insert(0, os.path.dirname(__file__))
from transform import normalize_geo, parse_float, parse_year, find_csv, read_csv_iter

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def main():
    result = {}

    # Transform logic here — structure depends on what the report needs
    # Reports often need MULTIPLE data series in one JSON file:
    # {
    #   "trend": {"Canada": [{"year": 2011, "value": 12.3}], ...},
    #   "provincial": {"Ontario": [{"year": 2022, "value": 18.4}], ...},
    #   "demographics": {"children": {...}, "seniors": {...}},
    #   "benchmarks": {"G7_average": 8.2, "OECD_average": 10.1},
    #   "metadata": {"last_updated": "2024", "source": "..."}
    # }

    out_path = os.path.join(DATA_DIR, "report-{slug}.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Wrote {out_path}")

if __name__ == "__main__":
    main()
```

**If the data is small or manually compiled** (e.g. from multiple NGO reports), embed it directly as `const DATA = {...}` in the HTML. This is common for reports — unlike metric dashboards, report data often comes from heterogeneous sources that can't be automated.

### 2c. Register in config (optional)

If using a StatCan source that should be re-downloaded on pipeline runs, add to `pipeline/config.py`:

```python
"TABLE-ID": {
    "description": "Description",
    "outputs": ["report-slug.json"],
},
```

If the data is hardcoded or from non-StatCan sources, skip this step.

### 2d. Test the transform

```bash
python3 pipeline/report_{slug}.py
python3 -c "
import json
d = json.load(open('data/report-{slug}.json'))
print(json.dumps(d, indent=2)[:2000])
"
```

---

## Phase 3: Report Dashboard

### 3a. Report HTML structure

Read `reports/cancelled-projects.html` as the canonical template. Every report follows this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>REPORT TITLE | Canada Central</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
  <style>
    /* Full CSS block — see Reference: Report CSS below */
  </style>
</head>
<body>
  <nav class="navbar">
    <a class="navbar-brand" href="https://canada-central.com">Canada Central</a>
    <div class="navbar-links">
      <a href="https://canada-central.com">Home</a>
      <a href="../index.html">Statistics</a>
      <a href="../scorecard-v2.html">Scorecard</a>
      <a class="active" href="../reports.html">Reports</a>
    </div>
  </nav>

  <div class="page">
    <div class="content">

      <!-- 1. Title & Context -->
      <h1 class="page-title">PUNCHY REPORT TITLE</h1>
      <p class="page-subtitle">Source: SOURCE &middot; TIMEFRAME</p>
      <p class="page-desc">NARRATIVE PARAGRAPH — what happened, how bad it is,
        and why it matters. Use <strong>bold</strong> for key numbers.
        Write for someone who knows nothing about this topic.</p>

      <!-- 2. Hero Statistics (3-5 cards) -->
      <div class="hero-stats">
        <div class="hero-stat">
          <div class="big">HEADLINE NUMBER</div>
          <div class="label">CONTEXT LABEL</div>
        </div>
        <!-- ... more stat cards ... -->
      </div>

      <!-- 3. Accountability Section -->
      <div class="accountability">
        <h3>Who is responsible?</h3>
        <p><strong>INSTITUTION</strong>
          <span class="entity-tag govt">TAG</span><br>
          EXPLANATION OF RESPONSIBILITY</p>
        <!-- Quotes where relevant -->
        <div class="quote-block">
          "QUOTE TEXT"
          <span class="attr">&mdash; ATTRIBUTION</span>
        </div>
      </div>

      <!-- 4. Chart View Toggles -->
      <div class="view-toggle">
        <button class="view-btn on" onclick="setView('VIEW1')">View 1</button>
        <button class="view-btn" onclick="setView('VIEW2')">View 2</button>
        <!-- ... more views ... -->
      </div>

      <!-- 5. Chart -->
      <div class="chart-card full">
        <h3 id="chartTitle">CHART TITLE</h3>
        <div class="chart-wrap"><canvas id="chart"></canvas></div>
      </div>

      <!-- 6. Data Table -->
      <div class="table-section">
        <div class="table-header">
          <h2 class="table-title">TABLE TITLE</h2>
          <div class="table-actions">
            <button class="btn-sm" onclick="copyTable()">Copy</button>
            <button class="btn-sm" onclick="downloadCSV()">Download CSV</button>
          </div>
        </div>
        <div class="data-table-wrap">
          <table class="data-table" id="dataTable"></table>
        </div>
      </div>

    </div>
  </div>

<script>
  // DATA — either loaded from JSON or embedded inline
  const DATA = { ... };

  // CHART LOGIC — Chart.js 4.4.0
  let chart;
  let currentView = 'VIEW1';

  function setView(view) { ... }
  function updateChart() { ... }
  function buildTable() { ... }
  function copyTable() { ... }
  function downloadCSV() { ... }

  // Initialize
  updateChart();
  buildTable();
</script>
</body>
</html>
```

### 3b. Headline statistics — make them hit hard

Hero stats should be chosen for maximum impact. Use these patterns:

| Pattern | Example | When to use |
|---------|---------|-------------|
| **Raw scale** | "10M Canadians" | When the absolute number is shocking |
| **Fraction** | "1 in 3 children" | More intuitive than percentages for general audience |
| **Rate of change** | "2x since 2019" | When acceleration is the story |
| **Money** | "$670B" | Economic impact |
| **Duration** | "17 years" | Institutional failure over time |
| **Comparison** | "3x the G7 average" | International embarrassment |
| **Count** | "31 projects" | Cumulative institutional failure |

**Rules:**
- Maximum 5 hero stat cards
- At least 1 must be a benchmark/comparison (not just raw data)
- Use the `big` class for the number — make it large and colored with `--accent`
- Labels should be short (max 5 words), lowercase except proper nouns

### 3c. Accountability narrative — name names

Every report must have an accountability section answering:
1. **Who** — specific institutions, departments, politicians, policies
2. **What** — what they did or failed to do
3. **When** — timeline of decisions
4. **Consequence** — quantified impact of their action/inaction

Use entity tags to call out responsible parties:
```html
<span class="entity-tag govt">Government body</span>
<span class="entity-tag person">Named individual</span>
```

Include direct quotes where available — they're more powerful than summaries.

### 3d. Chart views — multiple angles on the problem

Every report needs 2-4 chart views toggled by buttons. Design chart views to answer different questions:

| View | Question it answers | Chart type |
|------|-------------------|------------|
| Timeline | "Is it getting worse?" | Bar or line chart, years on X axis |
| Provincial | "Where is it worst?" | Horizontal bar, provinces ranked |
| Demographic | "Who suffers most?" | Grouped bars or stacked |
| Composition | "What's driving it?" | Stacked bar breakdown |
| Benchmark | "How bad vs peers?" | Bar with reference lines |
| Per-capita | "Adjusting for population?" | Same data, normalized |
| Cost | "What does it cost us?" | Dollar values, bar or area |

**Chart.js patterns:**
- Use Chart.js 4.4.0 CDN (already loaded)
- Destroy and recreate chart on view toggle: `if (chart) chart.destroy();`
- Use `type: 'bar'` for most views, `type: 'line'` for trends
- Add dashed reference lines for benchmarks using annotation or a second dataset
- Color-code bars: use `--accent` for primary, `#8A8A8A` for comparison/benchmark

### 3e. Benchmark visualization — contextualize how bad it is

At least one chart view or hero stat MUST benchmark the problem against something external:

| Benchmark type | Example |
|---------------|---------|
| **Historical baseline** | "Food bank visits have doubled since 2019" |
| **International comparison** | "Canada's rate is 3x the OECD average" |
| **Government target** | "Below the official poverty line" |
| **Cost equivalent** | "$X billion — more than the annual defense budget" |
| **Per-capita normalization** | "Adjusting for population, Saskatchewan is 4x Ontario" |
| **Demographic contrast** | "Indigenous children: 40% vs national 25%" |

### 3f. Data table — full transparency

The table should include ALL data points with:
- All columns needed to understand each row
- A `<tfoot>` with totals/summaries
- Copy button (copies tab-separated to clipboard)
- Download CSV button

### 3g. Writing tone

**Target audience: Canadians who don't follow policy closely.** Write like you're explaining to a smart friend who doesn't know the jargon:
- No acronyms without explanation on first use
- Fractions ("1 in 3") over percentages where possible
- Dollar amounts always with context ("$X — enough to build Y")
- Short sentences. Punchy. Direct.
- Bold the most important numbers
- The title should be provocative but accurate — not clickbait, but not bureaucratic either

---

## Phase 4: Reports Page Integration

### 4a. Add report card to `reports.html`

Read `reports.html`. Add a new report card following the existing pattern:

```html
<a class="report-card" href="reports/{slug}.html">
  <div class="report-card-content">
    <span class="report-card-tag">TAG (e.g. Accountability, Social Policy, Infrastructure)</span>
    <h2 class="report-card-title">REPORT TITLE</h2>
    <p class="report-card-desc">2-3 sentence summary with key numbers.
      Use &mdash; for em dashes. Mention the most shocking statistic.</p>
    <div class="report-card-meta">
      <span class="meta-item">KEY: <span class="meta-value">VALUE</span></span>
      <!-- 2-4 meta items -->
    </div>
  </div>
  <div class="report-card-visual">
    <div class="visual-stat">
      <div class="big">HEADLINE</div>
      <div class="label">context</div>
      <!-- Optional second stat -->
      <div style="margin-top:8px;font-size:1.25rem;font-weight:700;color:#5A5A5A">SECONDARY</div>
      <div class="label">secondary context</div>
    </div>
  </div>
</a>
```

**Report card accent:** The `.report-card` has `border-left: 4px solid var(--accent)` where `--accent: #8B2E2E`. If the report has a different accent color, override inline:
```html
<a class="report-card" href="..." style="border-left-color: #6B4E2E">
```

### 4b. Update coming-soon section

If the report was listed in the "coming soon" topic pills, remove it from there.

### 4c. Reorder report cards

Place the newest/most impactful reports first. Reports should be ordered by impact, not chronologically.

---

## Phase 5: Navbar & Site Integration

### 5a. Verify navbar consistency

Every page on the site must have the same navbar links. Check that all pages include the Reports link:

**Top-level pages** (`index.html`, `scorecard-v2.html`, `reports.html`):
```html
<nav class="navbar">
  <a class="navbar-brand" href="https://canada-central.com">Canada Central</a>
  <div class="navbar-links">
    <a href="https://canada-central.com">Home</a>
    <a href="index.html">Statistics</a>
    <a href="scorecard-v2.html">Scorecard</a>
    <a href="reports.html">Reports</a>
  </div>
</nav>
```

**Nested pages** (`dashboards/*.html`, `reports/*.html`):
```html
<nav class="navbar">
  <a class="navbar-brand" href="https://canada-central.com">Canada Central</a>
  <div class="navbar-links">
    <a href="https://canada-central.com">Home</a>
    <a href="../index.html">Statistics</a>
    <a href="../scorecard-v2.html">Scorecard</a>
    <a href="../reports.html">Reports</a>
  </div>
</nav>
```

Set `class="active"` on the appropriate link for each page.

### 5b. Cross-link from relevant dashboards (optional)

If the report topic overlaps with existing metric dashboards, consider adding a subtle link from the dashboard page description. For example, a food insecurity report could be cross-linked from demographics dashboards:

```html
<p class="page-desc">... See also: <a href="../reports/food-insecurity.html">Food Insecurity Report</a></p>
```

Only do this if it genuinely helps the user find related content.

---

## Phase 6: Validate

### 6a. Check the report renders

Open `reports/{slug}.html` and verify:
- [ ] All hero stats display correctly
- [ ] Accountability section renders with entity tags
- [ ] All chart views work and toggle correctly
- [ ] Chart data matches source data
- [ ] Table renders with all columns
- [ ] Table footer shows correct totals
- [ ] Copy button works
- [ ] Download CSV button works
- [ ] Navbar links work (Reports is active)

### 6b. Check the reports page

Open `reports.html` and verify:
- [ ] New report card appears
- [ ] Card links to correct URL
- [ ] Visual stat shows correct headline number
- [ ] Meta items display correctly

### 6c. Spot-check data accuracy

Manually verify at least 3 data points against the original source. Reports are public-facing accountability documents — accuracy is non-negotiable.

---

## Reference: Report CSS

Copy the full CSS from `reports/cancelled-projects.html` as your starting template. Key classes:

```css
/* Report accent — change per report */
:root { --accent: #8B2E2E; }

/* Layout */
.page { flex:1; display:flex; flex-direction:column; padding:1rem; box-sizing:border-box }
.content { max-width:1400px; margin:0 auto; width:100% }

/* Hero stats */
.hero-stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:1rem; margin-bottom:1.5rem }
.hero-stat { background:var(--color-white); border-radius:var(--radius-lg); box-shadow:var(--shadow-card); padding:1.25rem; text-align:center; border-top:4px solid var(--accent) }
.hero-stat .big { font-size:2rem; font-weight:800; color:var(--accent); line-height:1.2 }
.hero-stat .label { font-size:0.75rem; color:var(--color-text-tertiary); text-transform:uppercase; letter-spacing:0.05em; font-weight:600; margin-top:4px }

/* Accountability */
.accountability { background:var(--color-white); border-radius:var(--radius-lg); box-shadow:var(--shadow-card); border-left:4px solid var(--accent); padding:1.25rem 1.5rem; margin-bottom:1.5rem }
.entity-tag.govt { background:#fde8e8; border-color:#f5c6c6; color:#8B2E2E }
.entity-tag.person { background:#fef3cd; border-color:#fde68a; color:#92400e }

/* Quote blocks */
.quote-block { background:var(--color-cream-dark); border-left:3px solid var(--accent); padding:0.75rem 1rem; margin:0.75rem 0; border-radius:0 var(--radius-md) var(--radius-md) 0; font-style:italic; font-size:0.8125rem }

/* View toggle */
.view-toggle { display:flex; gap:6px; margin-bottom:1rem; flex-wrap:wrap }
.view-btn { padding:5px 14px; border-radius:9999px; font-size:0.6875rem; font-weight:600; cursor:pointer; border:2px solid var(--color-beige-dark); background:var(--color-cream); color:var(--color-text-secondary) }
.view-btn.on { background:var(--accent); color:#fff; border-color:var(--accent) }

/* Charts */
.chart-card { background:var(--color-white); border-radius:var(--radius-lg); box-shadow:var(--shadow-card); border-top:4px solid var(--accent); padding:20px }
.chart-card.full { grid-column:1/-1 }
.chart-wrap { position:relative; height:300px }
.chart-wrap canvas { position:absolute; top:0; left:0; right:0; bottom:0 }

/* Data table */
.data-table-wrap { background:var(--color-white); border-radius:var(--radius-lg); box-shadow:var(--shadow-card); overflow-x:auto; border:1px solid var(--color-beige) }
.data-table { width:100%; border-collapse:collapse; font-size:0.8125rem }
.data-table th { text-align:left; padding:0.75rem 1rem; font-weight:600; font-size:0.6875rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--color-text-tertiary); border-bottom:2px solid var(--color-beige); background:var(--color-cream); white-space:nowrap }
.data-table td { padding:0.625rem 1rem; border-bottom:1px solid var(--color-cream-dark); vertical-align:top }
.data-table td.num { text-align:right; font-weight:600; font-variant-numeric:tabular-nums; white-space:nowrap }
```

## Reference: Design Tokens

```
Background:      #F0ECE3 (cream)
Card bg:         #FEFEFE (white)
Borders:         #D8D1C2 (beige)
Text primary:    #2D2D2D
Text secondary:  #5A5A5A
Text tertiary:   #8A8A8A
Good color:      #4A7A4A (green)
Bad color:       #A13F3F (red)
Chart.js:        4.4.0 CDN
Font:            system-ui stack
```

## Reference: Province Entity Colors

```javascript
const entityColors = {
  'Canada':                  '#2D2D2D',
  'Ontario':                 '#6B3838',
  'Quebec':                  '#3A5F6F',
  'British Columbia':        '#7C5A9D',
  'Alberta':                 '#C49A6C',
  'Manitoba':                '#4A7C59',
  'Saskatchewan':            '#8B6914',
  'Nova Scotia':             '#5B7FA5',
  'New Brunswick':           '#A05A5A',
  'Newfoundland & Labrador': '#6A8A6A',
  'Prince Edward Island':    '#9A7B5A',
  'Yukon':                   '#7A6B5A',
  'Northwest Territories':   '#5A6B7A',
  'Nunavut':                 '#6B5A7A'
};
```

## Reference: StatCan CSV Quirks

| Quirk | Solution |
|-------|----------|
| BOM encoding | `encoding='utf-8-sig'` |
| `"Ontario [35]"` in GEO | `normalize_geo()` strips brackets |
| `"Newfoundland and Labrador"` | Mapped to `"Newfoundland & Labrador"` |
| Monthly REF_DATE `"2020-01"` | `parse_year()` handles it |
| VALUE in thousands/millions | Check SCALAR_FACTOR, scale accordingly |
| Empty VALUE | `parse_float()` returns None |

## Reference: Existing Reports

| Report | Slug | Accent | File |
|--------|------|--------|------|
| Systematic Economic Dereliction | cancelled-projects | `#8B2E2E` | `reports/cancelled-projects.html` |

When creating a new report, read `reports/cancelled-projects.html` as the canonical example of tone, structure, and CSS.
