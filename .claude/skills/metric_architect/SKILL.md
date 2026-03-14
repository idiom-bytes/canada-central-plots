---
name: metric_architect
description: End-to-end workflow for adding a new Canadian statistics metric — from StatCan data source to pipeline transform to dashboard HTML to scorecard integration to index page.
argument-hint: <metric-description> [statcan-table-id]
user-invocable: true
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Agent
---

# Metric Architect

You are building a new metric for **Canada Central Plots** — a static site of provincial comparison dashboards at `plots.canada-central.com`. Each metric follows a strict, reproducible pipeline:

```
StatCan CSV → pipeline/transform.py → data/*.json → dashboards/*.html → index.html → scorecard
```

**The user will give you a metric description and optionally a StatCan table ID.** Follow every phase below in order. Do not skip steps. Ask the user to confirm at the end of Phase 1 before proceeding.

---

## Phase 1: Discovery & Planning

### 1a. Identify the data source

If the user provided a StatCan table ID, use it. Otherwise, search for the right table:
- StatCan tables follow pattern `XX-XX-XXXX` (e.g. `35-10-0026`)
- Bulk CSV download: `https://www150.statcan.gc.ca/n1/tbl/csv/{ID_NO_DASHES}-eng.zip`

### 1b. Download and inspect the CSV

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
# Show columns and unique filter values
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

**Check:**
- Which filter column + value isolates the metric you need
- What GEO values look like (plain `"Ontario"` vs bracketed `"Ontario [35]"`)
- UOM and SCALAR_FACTOR (is VALUE in units, thousands, millions, rate?)
- REF_DATE format (annual, monthly, quarterly, fiscal year)

### 1c. Determine output format

Choose the JSON format based on what the dashboards expect:

| Format | When to use | Example |
|--------|------------|---------|
| **Entity-keyed** | Most metrics | `{"Ontario": [{"year": 2020, "value": 123}]}` |
| **Year-list** | Already per-capita, parallel arrays | `{"years": ["2020"], "entities": {"Ontario": [123]}}` |

### 1d. Determine naming

All names use the vertical prefix, kebab-case:

| Vertical | Prefix | Accent Color |
|----------|--------|-------------|
| Fiscal | `fiscal-` | `#4A6FA5` |
| Economy | `economy-` | `#3D7A4A` |
| Housing | `housing-` | `#C4763C` |
| Crime | `crime-` | `#A63D40` |
| Demographics | `demographics-` | `#7C5A9D` |

Files:
- Data: `data/{vertical}-{metric}.json`
- Dashboard: `dashboards/{vertical}-{metric}.html`

### 1e. Determine "vs National" direction

- **Standard** (higher = better): GDP, wages, vacancy rate, housing starts, pop growth, immigration → green `above` / red `below`
- **Inverted** (lower = better): crime, homicide, price index, deficit, debt, spending → red `positive` / green `negative`

### 1f. Confirm with user

Present: metric name, table ID, filter columns, output filename, vertical, accent color, invert flag. Get confirmation before proceeding.

---

## Phase 2: Pipeline Integration

### 2a. Register source in `pipeline/config.py`

Read `pipeline/config.py` and add to the `SOURCES` dict:

```python
"TABLE-ID": {
    "description": "Description of what this table contains",
    "outputs": ["vertical-metric.json"],
},
```

### 2b. Write transform function in `pipeline/transform.py`

Read `pipeline/transform.py` and add a new function following this exact pattern:

```python
def transform_METRIC_NAME():
    """TABLE-ID -> vertical-metric.json
    Filter: ColumnName="Exact Value", ...
    """
    print("  [transform] TABLE-ID: Description")
    data = defaultdict(list)

    for row in read_csv_iter(find_csv("TABLE-ID")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue
        # EXACT column filters — use the values discovered in Phase 1
        if row.get("ColumnName", "") != "Exact Value":
            continue
        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue
        data[geo].append({"year": year, "value": round(val, 2)})

    save_json("vertical-metric.json", build_result(data))
```

**If per-capita is needed**, load population first:
```python
pop_path = os.path.join(DATA_DIR, "demographics-population.json")
with open(pop_path) as f:
    pop_json = json.load(f)
pop_lookup = {(e, entry["year"]): entry["value"] for e, entries in pop_json.items() for entry in entries}
# Then: value * SCALE / pop_lookup[(geo, year)]
```

**If monthly data**, aggregate to annual (sum or average).

Add the function to the `TRANSFORMS` list. If it depends on population, place it AFTER `transform_population`.

### 2c. Test the transform

```bash
python3 pipeline/transform.py
```

Verify the output file exists and has correct structure:
```bash
python3 -c "
import json
d = json.load(open('data/vertical-metric.json'))
print('Keys:', list(d.keys())[:5])
for e in ['Canada', 'Ontario', 'Alberta']:
    if e in d:
        print(f'{e} latest:', d[e][-3:])
"
```

---

## Phase 3: Dashboard HTML

### Rule: 1 metric = 1 dashboard

Only exception: same stat with different normalization (e.g. raw starts + starts per 10K).

### 3a. Create the dashboard file

Read an existing dashboard in the same vertical as a template. For example, if adding a crime metric, read `dashboards/crime-violent-csi.html`.

Create `dashboards/{vertical}-{metric}.html` with this structure. Every dashboard MUST include:

**Head:**
- `<title>METRIC TITLE | Canada Central</title>`
- Chart.js 4.4.0 CDN: `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js`
- Full CSS block (copy from template — only change `border-top` color on `.chart-card`)

**Navbar:**
```html
<nav class="navbar">
  <a class="navbar-brand" href="https://canada-central.com">Canada Central</a>
  <div class="navbar-links">
    <a href="https://canada-central.com">Home</a>
    <a class="active" href="../index.html">Statistics</a>
  </div>
</nav>
```

**Page content:**
```html
<h1 class="page-title">DASHBOARD TITLE</h1>
<p class="page-subtitle">Source: <a href="URL" target="_blank" rel="noopener">SOURCE NAME</a> &middot; Table TABLE-ID</p>
<p class="page-desc">CONTEXTUAL DESCRIPTION — what the metric measures, why it matters, how to interpret values.</p>
<div class="entities" id="entities"></div>
<div class="chart-card"><canvas id="chart"></canvas></div>
```

**Table section** with Copy and Download CSV buttons.

**Script:**
- Embed the JSON data inline as `const ALL_DATA = ...;`
- Entity colors and order (see Phase 1d)
- `selectedEntity` defaults to `'Canada'` (or `'Federal'` for fiscal)
- Chart: bar chart with national average dashed line overlay when viewing a province
- Table: Year, Value, and "vs National %" column with correct color logic

### 3b. Chart card border-top color

Set to the vertical accent color:
```css
.chart-card { border-top: 4px solid ACCENT_COLOR; }
```

### 3c. "vs National" table colors

**Standard** (higher = better):
```css
.data-table .above { color: #4A7A4A; }
.data-table .below { color: #A13F3F; }
```

**Inverted** (lower = better):
```css
.data-table .positive { color: #A13F3F; }
.data-table .negative { color: #4A7A4A; }
```

---

## Phase 4: Index Page

### 4a. Add dashboard card to `index.html`

Read `index.html`. Find the correct vertical `<section>` and add a card:

```html
<a class="plot-card" href="dashboards/vertical-metric.html"
   style="border-left-color:var(--v-VERTICAL)">
  <div class="card-content">
    <span class="card-category" style="color:var(--v-VERTICAL)">ICON VERTICAL_NAME</span>
    <h2 class="card-title">Dashboard Title</h2>
    <p class="card-desc">One-sentence description.</p>
  </div>
  <div class="card-visual">
    <div class="card-visual-stat">
      <span class="stat-value">HEADLINE</span>
      <span class="stat-label">context</span>
    </div>
  </div>
</a>
```

**Vertical CSS variables** (already defined in index.html):
- `--v-fiscal: #4A6FA5`
- `--v-economy: #3D7A4A`
- `--v-housing: #C4763C`
- `--v-crime: #A63D40`
- `--v-demographics: #7C5A9D`

**Icons:** Fiscal 📊, Economy 🏭, Housing 🏠, Crime 🔴, Demographics 👥

### 4b. Update dashboard count

Update the hero section dashboard count if it's hardcoded.

---

## Phase 5: Scorecard Integration

### 5a. Add metric to `pipeline/scorecard.py`

Read `pipeline/scorecard.py`. Add a new metric block:

```python
# Load data
new_data = load_json("vertical-metric.json")

# Extract latest values
new_vals = {}
new_trends = {}
for p in PROVINCES:
    recent = get_latest_value_nested(new_data, p, 3)   # or get_latest_value_yearlist for year-list format
    prior = get_latest_value_nested(new_data, p, 5)
    if recent:
        new_vals[p] = recent[0]
        new_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

canada_val = get_latest_value_nested(new_data, "Canada", 1)

metrics.append(build_metric(
    "Display Name",
    "vertical",          # fiscal, economy, housing, crime, demographics
    new_vals,
    canada_val[0] if canada_val else None,
    invert=BOOL,         # True if lower = better
    unit="UNIT",         # $, %, index, per 1K, per 100K
    trends=new_trends,
))
```

**For per-capita metrics**, multiply raw values by scale factor before dividing by population:
- Billions: `× 1_000_000_000`
- Millions: `× 1_000_000`
- Thousands: `× 1_000`

**Grade system** (auto-computed):
- A: rank 1-2, B: rank 3-5, C: rank 6-8, D: rank 9-10

### 5b. Add data file load

Add the `load_json()` call at the top of `main()` alongside other data loads.

---

## Phase 6: Validate

### 6a. Run the full pipeline

```bash
bash pipeline/run.sh --skip-download
```

### 6b. Verify output

```bash
# Check data file
python3 -c "
import json
d = json.load(open('data/vertical-metric.json'))
for e in ['Canada', 'Ontario', 'Alberta']:
    if e in d: print(f'{e}:', d[e][-3:])
"

# Check scorecard
python3 -c "
import json
d = json.load(open('data/scorecard_data.json'))
for m in d['metrics']:
    if 'METRIC' in m['name']:
        print(m['name'], ':', {p: v['grade'] for p, v in m['provinces'].items()})
"
```

### 6c. Open dashboard in browser

Open `dashboards/vertical-metric.html` and verify:
- Chart renders with correct data
- Entity chips toggle correctly
- National average line appears when viewing a province
- Table shows correct "vs National" colors
- Copy and Download CSV work

---

## Reference: Province Entity Colors

```javascript
const entityColors = {
  'Canada':                  '#2D2D2D',
  'Federal':                 '#2D2D2D',
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

## Reference: StatCan CSV Quirks

| Quirk | Solution |
|-------|----------|
| BOM encoding | `encoding='utf-8-sig'` |
| `"Ontario [35]"` in GEO | `normalize_geo()` strips brackets |
| `"Newfoundland and Labrador"` | Mapped to `"Newfoundland & Labrador"` |
| Fiscal uses `"Federal"` | Not `"Canada"` — check each data file |
| Monthly REF_DATE `"2020-01"` | `parse_year()` handles it |
| VALUE in thousands/millions | Check SCALAR_FACTOR, scale accordingly |
| Empty VALUE | `parse_float()` returns None |

## Reference: CSS Design Tokens

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
