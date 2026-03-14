# Canada Central Plots — Build Skill

This document describes how to add a new metric end-to-end: from StatCan data source to dashboard to scorecard. Follow every section in order.

---

## 1. Architecture Overview

```
pipeline/
  config.py          # Source registry, province mappings
  download.py        # StatCan bulk CSV download → pipeline/lake/
  transform.py       # CSV → JSON in data/
  scorecard.py       # All data/*.json → data/scorecard_data.json
  run.sh             # Single entry point
  lake/              # Raw CSVs (gitignored)

data/
  [vertical]-[metric].json     # 17 data files (14 auto, 3 manual)
  scorecard_data.json          # Aggregated scorecard

dashboards/
  [vertical]-[metric].html     # 1 metric = 1 dashboard, 20 files

index.html                     # Landing page with all dashboard links
scorecard.html                 # Provincial scorecard heat map
```

**Run the full pipeline:**
```bash
bash pipeline/run.sh                # download + transform + scorecard
bash pipeline/run.sh --skip-download # reuse cached CSVs
```

---

## 2. Naming Conventions

Everything is prefixed by vertical, kebab-case, descriptive.

### Verticals

| Vertical | Prefix | Accent Color | Icon |
|----------|--------|-------------|------|
| Fiscal | `fiscal-` | `#4A6FA5` | `📊` |
| Economy | `economy-` | `#3D7A4A` | `🏭` |
| Housing | `housing-` | `#C4763C` | `🏠` |
| Crime | `crime-` | `#A63D40` | `🔴` |
| Demographics | `demographics-` | `#7C5A9D` | `👥` |

### File naming examples

```
data/economy-gdp-per-capita.json
dashboards/economy-gdp-per-capita.html

data/crime-homicide-rate.json
dashboards/crime-homicide-rate.html
```

### Province entity colors

```javascript
const entityColors = {
  'Canada':                  '#2D2D2D',
  'Federal':                 '#2D2D2D',   // fiscal only
  'Ontario':                 '#6B3838',
  'Quebec':                  '#3A5F6F',
  'British Columbia':        '#7C5A9D',
  'Alberta':                 '#C49A6C',
  'Manitoba':                '#4A7C59',
  'Saskatchewan':            '#8B6914',
  'Nova Scotia':             '#5B7FA5',
  'New Brunswick':           '#A05A5A',
  'Newfoundland & Labrador': '#6A8A6A',
  'Prince Edward Island':    '#9A7B5A'
};
```

### Province entity order

```javascript
const entityOrder = [
  'Canada',        // or 'Federal' for fiscal dashboards
  'Ontario', 'Quebec', 'British Columbia', 'Alberta',
  'Manitoba', 'Saskatchewan', 'Nova Scotia', 'New Brunswick',
  'Newfoundland & Labrador', 'Prince Edward Island'
];
```

---

## 3. Adding a New Data Source

### Step 1: Find the StatCan table

StatCan bulk CSV download URL pattern:
```
https://www150.statcan.gc.ca/n1/tbl/csv/{TABLE_ID_NO_DASHES}-eng.zip
```

Example: table `36-10-0222` → `https://www150.statcan.gc.ca/n1/tbl/csv/36100222-eng.zip`

### Step 2: Register in `pipeline/config.py`

Add to the `SOURCES` dictionary:

```python
SOURCES = {
    # ...existing sources...
    "NEW-TABLE-ID": {
        "description": "Human-readable description",
        "outputs": ["vertical-metric-name.json"],
    },
}
```

If the source is not auto-downloadable (e.g. Dept of Finance PDFs), add to `MANUAL_SOURCES` instead:

```python
MANUAL_SOURCES = {
    "source-name": {
        "description": "...",
        "outputs": ["vertical-metric.json"],
        "note": "How to obtain this data manually",
    },
}
```

### Step 3: Explore the CSV

After running `python pipeline/download.py`, inspect the CSV:

```python
import csv
with open('pipeline/lake/TABLE-ID/TABLEID.csv', encoding='utf-8-sig') as f:
    r = csv.DictReader(f)
    row = next(r)
    print('Columns:', list(row.keys()))
    # Check unique filter values for each column
```

**Key things to check:**
- Column names (every table is different)
- Filter column values (e.g. `Gender="Total - Gender"`)
- GEO format — some tables append DGUID: `"Ontario [35]"` (handled by `normalize_geo`)
- UOM and SCALAR_FACTOR (thousands? millions? rate?)
- REF_DATE format (annual `"2020"`, monthly `"2020-01"`, quarterly `"2020-Q3"`)

### Step 4: Write a transform function in `pipeline/transform.py`

Follow this pattern:

```python
def transform_new_metric():
    """TABLE-ID -> vertical-metric-name.json
    Filter: [list exact column=value filters]
    """
    print("  [transform] TABLE-ID: Description")
    data = defaultdict(list)

    for row in read_csv_iter(find_csv("TABLE-ID")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue

        # Apply exact column filters
        if row.get("ColumnName", "") != "Exact Value":
            continue

        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue

        data[geo].append({"year": year, "value": round(val, 2)})

    save_json("vertical-metric-name.json", build_result(data))
```

**Add to TRANSFORMS list** (order matters if one transform depends on another):

```python
TRANSFORMS = [
    transform_population,        # Must run first (others use pop for per-capita)
    transform_gdp_per_capita,    # Depends on population
    # ...
    transform_new_metric,        # Add here
]
```

### Common transform patterns

**Per-capita computation** (requires population data):
```python
pop_path = os.path.join(DATA_DIR, "demographics-population.json")
with open(pop_path) as f:
    pop_json = json.load(f)
pop_lookup = {}
for entity, entries in pop_json.items():
    for e in entries:
        pop_lookup[(entity, e["year"])] = e["value"]

# Then: per_capita = raw_value * SCALE / pop_lookup[(geo, year)]
```

**Monthly → annual aggregation** (sum or average):
```python
monthly_data = defaultdict(lambda: defaultdict(list))
# ... collect monthly values ...
# Average:
result[geo] = [{"year": y, "value": round(sum(vals)/len(vals), 1)} for y, vals in ...]
# Sum:
result[geo] = [{"year": y, "value": round(sum(vals))} for y, vals in ...]
```

**Origin-destination → net** (e.g. interprovincial migration):
```python
inflows = defaultdict(lambda: defaultdict(float))
outflows = defaultdict(lambda: defaultdict(float))
# ... accumulate ...
net = inflows[geo][year] - outflows[geo][year]
```

### JSON output formats

**Format A — Entity-keyed** (most common):
```json
{
  "Canada": [{"year": 2020, "value": 1234.5}, ...],
  "Ontario": [{"year": 2020, "value": 1100.0}, ...]
}
```
Use `build_result(data)` helper.

**Format B — Year-list** (used by GDP, CSI, deficit, net_debt):
```json
{
  "years": ["2020", "2021", "2022"],
  "entities": {
    "Canada": [59000, 60000, 61000],
    "Ontario": [55000, 56000, 57000]
  }
}
```

**Format C — Monthly employment** (unique):
```json
{
  "dates": ["2020-01", "2020-02", ...],
  "provinces": {
    "Canada": {"private": [...], "public": [...]}
  }
}
```

**Format D — Categorized** (crime breakdown):
```json
{
  "violent": {"Canada": [{"year": 2020, "value": 95.3}], ...},
  "nonviolent": {"Canada": [{"year": 2020, "value": 65.1}], ...}
}
```

---

## 4. Dashboard HTML Structure

**Rule: 1 metric = 1 dashboard.** Only exception: same stat with different normalization (e.g. housing starts raw + per 10K pop).

### Skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>METRIC_TITLE | Canada Central</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
  <style>
    /* ... full CSS below ... */
  </style>
</head>
<body>
  <nav class="navbar">
    <a class="navbar-brand" href="https://canada-central.com">Canada Central</a>
    <div class="navbar-links">
      <a href="https://canada-central.com">Home</a>
      <a class="active" href="../index.html">Statistics</a>
    </div>
  </nav>
  <div class="page">
    <div class="content">
      <h1 class="page-title">DASHBOARD TITLE</h1>
      <p class="page-subtitle">Source: <a href="URL" target="_blank" rel="noopener">SOURCE</a> &middot; Table TABLE-ID</p>
      <p class="page-desc">DESCRIPTION. Provide context, what the metric measures, why it matters, and how to interpret it.</p>
      <div class="entities" id="entities"></div>
      <div class="chart-card"><canvas id="chart"></canvas></div>
      <div class="table-section">
        <div class="table-header">
          <h2 class="table-title" id="tableTitle">Historical Data</h2>
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
    // Inline data + all JS here
  </script>
</body>
</html>
```

### Full CSS

Every dashboard includes this complete CSS block. The **only thing that changes** is the `border-top` color on `.chart-card` — set it to the vertical accent color.

```css
:root{--color-cream:#F0ECE3;--color-cream-dark:#E8E2D5;--color-beige:#D8D1C2;--color-beige-dark:#C8C0B0;--color-white:#FEFEFE;--color-text-primary:#2D2D2D;--color-text-secondary:#5A5A5A;--color-text-tertiary:#8A8A8A;--color-teal:#3A5F6F;--shadow-card:0 2px 8px 0 rgba(0,0,0,0.08);--radius-md:0.5rem;--radius-lg:0.75rem}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--color-cream);color:var(--color-text-primary);display:flex;flex-direction:column}

.navbar{padding:0.75rem 1rem;display:flex;justify-content:space-between;align-items:center;background:var(--color-cream);border-bottom:1px solid var(--color-beige)}
.navbar-brand{display:flex;align-items:center;gap:0.5rem;font-size:1rem;font-weight:700;color:var(--color-text-primary);text-decoration:none}
.navbar-brand:hover{color:var(--color-teal)}
.navbar-links{display:flex;gap:1.5rem;font-size:0.875rem;font-weight:600}
.navbar-links a{color:var(--color-text-secondary);text-decoration:none;transition:color 0.2s}
.navbar-links a:hover,.navbar-links a.active{color:var(--color-text-primary)}

.page{flex:1;display:flex;flex-direction:column;padding:1rem;box-sizing:border-box}
@media(min-width:640px){.page{padding:1.25rem 1.5rem}}
.content{max-width:1400px;margin:0 auto;width:100%}

.page-title{font-size:1.5rem;font-weight:700;color:var(--color-text-primary);line-height:1.3;margin:0 0 0.25rem}
@media(min-width:640px){.page-title{font-size:1.875rem}}
.page-subtitle{font-size:0.75rem;color:var(--color-text-tertiary);margin:0 0 0.5rem}
@media(min-width:640px){.page-subtitle{font-size:0.875rem}}
.page-subtitle a{color:inherit}
.page-desc{font-size:0.8125rem;color:var(--color-text-secondary);line-height:1.6;margin:0 0 1rem;max-width:900px}

.entities{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.chip{padding:4px 10px;border-radius:9999px;cursor:pointer;font-size:0.6875rem;font-weight:600;border:2px solid;opacity:0.35;transition:opacity 0.15s,background 0.15s}
@media(min-width:640px){.chip{padding:5px 12px;font-size:0.75rem}}
.chip.on{opacity:1}
.chip.chip-national{border-width:3px;font-weight:800;font-size:0.75rem;letter-spacing:0.02em}
@media(min-width:640px){.chip.chip-national{padding:5px 14px;font-size:0.8125rem}}

.chart-card{background:var(--color-white);border-radius:var(--radius-lg);box-shadow:var(--shadow-card);border-top:4px solid VERTICAL_ACCENT_COLOR;min-height:350px;position:relative;padding:20px}
canvas{position:absolute;top:20px;left:20px;right:20px;bottom:20px}

.table-section{margin-top:1.5rem}
.table-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;flex-wrap:wrap;gap:8px}
.table-title{font-size:1.125rem;font-weight:700;color:var(--color-text-primary);margin:0}
.table-actions{display:flex;gap:6px}
.btn-sm{padding:5px 12px;border-radius:var(--radius-md);font-size:0.6875rem;font-weight:600;cursor:pointer;border:1px solid var(--color-beige-dark);background:var(--color-beige);color:var(--color-text-primary);transition:all 0.15s}
.btn-sm:hover{background:var(--color-beige-dark)}
.btn-sm.copied{background:var(--color-teal);color:var(--color-white);border-color:var(--color-teal)}

.data-table-wrap{background:var(--color-white);border-radius:var(--radius-lg);box-shadow:var(--shadow-card);overflow:auto;border:1px solid var(--color-beige)}
.data-table{width:100%;border-collapse:collapse;font-size:0.8125rem}
.data-table th{text-align:left;padding:0.75rem 1rem;font-weight:600;font-size:0.6875rem;text-transform:uppercase;letter-spacing:0.05em;color:var(--color-text-tertiary);border-bottom:2px solid var(--color-beige);background:var(--color-cream);white-space:nowrap}
.data-table th.num{text-align:right}
.data-table td{padding:0.625rem 1rem;border-bottom:1px solid var(--color-cream-dark);color:var(--color-text-primary);white-space:nowrap}
.data-table td.num{text-align:right;font-weight:600;font-variant-numeric:tabular-nums}
.data-table tr:last-child td{border-bottom:none}
.data-table tr:hover td{background:var(--color-cream)}

/* vs National color classes — choose ONE pair per dashboard */
/* Standard (higher = better): */
.data-table .above{color:#4A7A4A}
.data-table .below{color:#A13F3F}
/* Inverted (higher = worse, e.g. crime, price index): */
.data-table .positive{color:#A13F3F}
.data-table .negative{color:#4A7A4A}
/* Deficit/surplus: */
.data-table .surplus{color:#4A7A4A}
.data-table .deficit{color:#A13F3F}
```

### Inline JavaScript pattern

```javascript
// 1. Embed data directly (no fetch — works with file:// protocol)
const ALL_DATA = /* PASTE JSON HERE */;

// 2. Entity colors and order (copy from section 2 above)
const entityColors = { /* ... */ };
const entityOrder = [ /* ... */ ];

// 3. State
let chart = null;
let selectedEntity = 'Canada'; // or 'Federal' for fiscal dashboards

// 4. Init
function init() { buildChips(); update(); }

// 5. Build entity selector chips
function buildChips() {
  const container = document.getElementById('entities');
  entityOrder.forEach(name => {
    if (!ALL_DATA.entities?.[name] && !ALL_DATA[name]) return;
    const chip = document.createElement('span');
    const color = entityColors[name] || '#666';
    const isPrimary = name === 'Canada' || name === 'Federal';
    chip.className = 'chip' + (isPrimary ? ' chip-national' : '') + (name === selectedEntity ? ' on' : '');
    chip.dataset.entity = name;
    chip.style.borderColor = color;
    chip.style.color = color;
    if (name === selectedEntity) { chip.style.background = color; chip.style.color = '#fff'; }
    chip.textContent = name;
    chip.onclick = () => selectEntity(name);
    container.appendChild(chip);
  });
}

// 6. Select entity
function selectEntity(name) {
  selectedEntity = name;
  document.querySelectorAll('#entities .chip').forEach(c => {
    const isSelected = c.dataset.entity === name;
    const color = entityColors[c.dataset.entity] || '#666';
    c.classList.toggle('on', isSelected);
    c.style.background = isSelected ? color : '';
    c.style.color = isSelected ? '#fff' : color;
  });
  update();
}

// 7. Update chart + table (dashboard-specific logic here)
function update() {
  // Get data for selectedEntity
  // Rebuild chart
  // Rebuild table
}

// 8. Copy/Download helpers
function copyTable() {
  const t = document.getElementById('dataTable');
  const rows = t.querySelectorAll('tr');
  const lines = [];
  rows.forEach(r => {
    const cells = r.querySelectorAll('th,td');
    lines.push(Array.from(cells).map(c => c.textContent.trim()).join('\t'));
  });
  navigator.clipboard.writeText(lines.join('\n')).then(() => {
    const b = event.target;
    b.textContent = 'Copied';
    b.classList.add('copied');
    setTimeout(() => { b.textContent = 'Copy'; b.classList.remove('copied'); }, 2000);
  });
}

function downloadCSV() {
  const t = document.getElementById('dataTable');
  const rows = t.querySelectorAll('tr');
  const lines = [];
  rows.forEach(r => {
    const cells = r.querySelectorAll('th,td');
    lines.push(Array.from(cells).map(c => '"' + c.textContent.trim() + '"').join(','));
  });
  const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = selectedEntity.toLowerCase().replace(/[^a-z0-9]+/g, '_') + '_METRIC_NAME.csv';
  a.click();
}

init();
```

### Chart.js configuration

```javascript
if (chart) chart.destroy();
const ctx = document.getElementById('chart').getContext('2d');
const color = entityColors[selectedEntity] || '#666';

const datasets = [{
  label: selectedEntity,
  data: values,
  backgroundColor: color + 'B3',    // 70% opacity
  borderColor: color,
  borderWidth: 1,
  borderRadius: 2
}];

// Add national average line when viewing a province
if (selectedEntity !== 'Canada' && selectedEntity !== 'Federal') {
  datasets.push({
    label: 'National Average',
    data: nationalValues,
    type: 'line',
    borderColor: '#2D2D2D',
    borderWidth: 2,
    borderDash: [5, 3],
    pointRadius: 0,
    fill: false,
    order: -1
  });
}

chart = new Chart(ctx, {
  type: 'bar',
  data: { labels: yearLabels, datasets: datasets },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        display: selectedEntity !== 'Canada',
        position: 'top',
        labels: { boxWidth: 15, font: { size: 10 }, color: '#5A5A5A' }
      },
      title: {
        display: true,
        text: selectedEntity + ' — METRIC NAME',
        color: '#2D2D2D',
        font: { size: 13, weight: 600 }
      },
      tooltip: {
        callbacks: {
          label: ctx => {
            const v = ctx.parsed.y;
            if (v == null) return null;
            return ' ' + ctx.dataset.label + ': ' + FORMAT(v);
          }
        }
      }
    },
    scales: {
      x: {
        ticks: { maxRotation: 45, font: { size: 10 }, color: '#8A8A8A' },
        grid: { display: false }
      },
      y: {
        ticks: {
          font: { size: 10 },
          color: '#8A8A8A',
          callback: v => FORMAT(v)
        },
        grid: { color: 'rgba(0,0,0,0.06)' },
        title: {
          display: true,
          text: 'Y-AXIS LABEL',
          font: { size: 11 },
          color: '#5A5A5A'
        }
      }
    }
  }
});
```

### Table with "vs National" column

```javascript
function buildTable(labels, vals, natVals) {
  document.getElementById('tableTitle').textContent = selectedEntity + ' — METRIC NAME';
  const t = document.getElementById('dataTable');
  const showDiff = selectedEntity !== 'Canada' && selectedEntity !== 'Federal';
  let h = '<thead><tr><th>Year</th><th class="num">VALUE LABEL</th>';
  if (showDiff) h += '<th class="num">vs National</th>';
  h += '</tr></thead><tbody>';
  for (let i = labels.length - 1; i >= 0; i--) {
    const v = vals[i];
    h += '<tr><td>' + labels[i] + '</td><td class="num">' + FORMAT(v) + '</td>';
    if (showDiff && v != null && natVals[i] != null) {
      const d = ((v / natVals[i] - 1) * 100).toFixed(1);
      // For standard metrics (higher = better):
      const cls = parseFloat(d) >= 0 ? 'above' : 'below';
      // For inverted metrics (higher = worse): swap above/below to positive/negative
      const sign = parseFloat(d) >= 0 ? '+' : '';
      h += '<td class="num ' + cls + '">' + sign + d + '%</td>';
    } else if (showDiff) {
      h += '<td class="num">-</td>';
    }
    h += '</tr>';
  }
  h += '</tbody>';
  t.innerHTML = h;
}
```

**"vs National" color logic:**
- **Standard** (GDP, wages, vacancy, housing starts, pop growth, immigration): higher = green (`above`), lower = red (`below`)
- **Inverted** (crime, homicide, price index, deficit, debt, spending): higher = red (`positive`), lower = green (`negative`)

---

## 5. Updating index.html

Each dashboard needs a card in the correct vertical section of `index.html`.

### Card HTML

```html
<a class="plot-card" href="dashboards/vertical-metric-name.html"
   style="border-left-color:var(--v-VERTICAL)">
  <div class="card-content">
    <span class="card-category" style="color:var(--v-VERTICAL)">ICON VERTICAL_NAME</span>
    <h2 class="card-title">Dashboard Title</h2>
    <p class="card-desc">One-sentence description of what this metric shows.</p>
  </div>
  <div class="card-visual">
    <div class="card-visual-stat">
      <span class="stat-value">HEADLINE_STAT</span>
      <span class="stat-label">stat context label</span>
    </div>
  </div>
</a>
```

**CSS variables for verticals** (defined in index.html):
```css
--v-fiscal: #4A6FA5;
--v-economy: #3D7A4A;
--v-housing: #C4763C;
--v-crime: #A63D40;
--v-demographics: #7C5A9D;
```

### Where to add

Cards are grouped inside `<section>` elements with anchor IDs:

```html
<section class="category" id="fiscal">
  <h2 class="cat-title"><span class="cat-icon">📊</span> Fiscal</h2>
  <!-- cards go here -->
</section>
```

Also update the hero dashboard count if adding a new dashboard.

---

## 6. Adding to the Scorecard

### Step 1: Add metric computation in `pipeline/scorecard.py`

```python
# Load the data file
new_data = load_json("vertical-metric-name.json")

# Extract latest values per province
new_vals = {}
new_trends = {}
for p in PROVINCES:
    recent = get_latest_value_nested(new_data, p, 3)   # or get_latest_value_yearlist
    prior = get_latest_value_nested(new_data, p, 5)
    if recent:
        new_vals[p] = recent[0]
        new_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

# Get Canada benchmark
canada_val = get_latest_value_nested(new_data, "Canada", 1)

# Build and append
metrics.append(build_metric(
    "Metric Display Name",
    "vertical",               # fiscal, economy, housing, crime, demographics
    new_vals,
    canada_val[0] if canada_val else None,
    invert=False,              # True if lower values = better
    unit="$",                  # $, %, index, per 1K, per 100K, etc.
    trends=new_trends,
))
```

### Per-capita scorecard metrics

For metrics that need per-capita normalization:

```python
BILLION = 1_000_000_000
MILLION = 1_000_000

for p in PROVINCES:
    recent = get_latest_value_nested(data, entity_name, 3)
    if recent and p in pop_latest:
        vals[p] = round(recent[0] * SCALE_FACTOR / pop_latest[p], 2)
```

### Grade assignment

Grades are auto-computed by `assign_grades()`:
- **A**: rank 1-2 (top performers)
- **B**: rank 3-5
- **C**: rank 6-8
- **D**: rank 9-10 (worst performers)

When `invert=True`, lower values rank higher (better). When `invert=False`, higher values rank higher.

### Trend calculation

`compute_trend()` compares the most recent 3 values against the prior 2:
- `> 5%` change → `"up"`
- `< -5%` change → `"down"`
- Otherwise → `"stable"`

### Composite score

Automatically computed from all metrics: `A=4, B=3, C=2, D=1`, averaged per province.

---

## 7. End-to-End Checklist for a New Metric

```
[ ] 1. Identify StatCan table ID and verify bulk CSV download works
[ ] 2. Register source in pipeline/config.py SOURCES dict
[ ] 3. Download CSV: python pipeline/download.py
[ ] 4. Inspect CSV columns and filter values
[ ] 5. Write transform function in pipeline/transform.py
[ ] 6. Add function to TRANSFORMS list (order matters for dependencies)
[ ] 7. Run transform: python pipeline/transform.py — verify JSON output
[ ] 8. Create dashboard HTML in dashboards/vertical-metric-name.html
       - Use vertical accent color for border-top
       - Embed JSON data inline
       - Include source citation with table ID
       - Set correct "vs National" color logic (standard vs inverted)
[ ] 9. Add card to index.html in the correct vertical section
[ ] 10. Add scorecard metric in pipeline/scorecard.py
        - Set invert flag correctly
        - Handle unit scaling (billions, millions, thousands)
[ ] 11. Run full pipeline: bash pipeline/run.sh --skip-download
[ ] 12. Verify dashboard renders correctly in browser
[ ] 13. Verify scorecard grades are reasonable
```

---

## 8. StatCan CSV Quirks Reference

| Quirk | Solution |
|-------|----------|
| BOM encoding (`\ufeff`) | Use `encoding='utf-8-sig'` |
| GEO with DGUID brackets: `"Ontario [35]"` | `normalize_geo()` strips `[...]` |
| Province name: `"Newfoundland and Labrador"` | Mapped to `"Newfoundland & Labrador"` |
| Fiscal data uses `"Federal"` not `"Canada"` | Check entity name in each data file |
| Monthly REF_DATE: `"2020-01"` | `parse_year()` extracts first 4 chars |
| Quarterly: `"2020-Q3"` | Same — extract year, aggregate |
| Fiscal year: `"2022-23"` | Handled by year-list format |
| VALUES in thousands/millions | Check `SCALAR_FACTOR` column, multiply accordingly |
| Empty VALUE field | `parse_float()` returns `None` |
| Multiple rows per geo+year | `dedup_by_year()` keeps last, or use dict overwrite |

---

## 9. Manual Data Sources

These 3 files are NOT auto-generated by the pipeline and must be maintained manually:

| File | Source | Why Manual |
|------|--------|-----------|
| `fiscal-deficit.json` | Dept of Finance Fiscal Reference Tables | PDF-only, no bulk CSV |
| `fiscal-net-debt.json` | Dept of Finance Fiscal Reference Tables | PDF-only, no bulk CSV |
| `housing-rental-vacancy-rate.json` | CMHC | StatCan table 34-10-0127 has CMA-level only, not provincial |

Format: year-list (`{years: [...], entities: {...}}`) for deficit/debt, entity-keyed for vacancy.
