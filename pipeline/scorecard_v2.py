"""
Scorecard v2: Three-layer grading with historical benchmarking, computed for every year.

For each year t in the available range:
  Layer 1 — Peer Rank:   Province rank among 10 provinces at year t
  Layer 2 — Trajectory:  EMA(3y) vs EMA(10y) + percentile in 20y range ending at t
  Layer 3 — Natl Health: Canada's 10y growth rate ending at t caps provincial grades

Output: data/scorecard_v2.json
  {years: [2007, ...], snapshots: {2007: {metrics, composites}, ...}, latest_year, ...}

Usage: python pipeline/scorecard_v2.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_DIR, PROVINCES_ORDERED

PROVINCES = [p for p in PROVINCES_ORDERED if p != "Canada"]

# Minimum provinces/territories with data to include a metric in a year's snapshot
MIN_PROVINCES = 7
# Minimum years of history before we start scoring
MIN_HISTORY = 5


def load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Time-series extraction
# ---------------------------------------------------------------------------

def get_timeseries_nested(data: dict, entity: str) -> list[tuple[int, float]]:
    if entity not in data:
        return []
    return sorted(
        [(e["year"], e["value"]) for e in data[entity] if e.get("value") is not None],
        key=lambda x: x[0],
    )


def get_timeseries_yearlist(data: dict, entity: str) -> list[tuple[int, float]]:
    if entity not in data.get("entities", {}):
        return []
    years = data.get("years", [])
    values = data["entities"][entity]
    result = []
    for i, y in enumerate(years):
        if i < len(values) and values[i] is not None:
            yr = int(str(y)[:4]) if isinstance(y, str) else int(y)
            result.append((yr, values[i]))
    return sorted(result, key=lambda x: x[0])


def get_timeseries_employment(data: dict, entity: str, pop_data: dict,
                              mode: str = "total") -> list[tuple[int, float]]:
    """mode: 'private' = private sector per 1K, 'public_share' = public % of total, 'total' = all."""
    pdata = data.get("provinces", {}).get(entity, {})
    dates = data.get("dates", [])
    priv = pdata.get("private", [])
    pub = pdata.get("public", [])
    if not priv or not pub or not dates:
        return []

    pop_ts = get_timeseries_nested(pop_data, entity)
    pop_by_year = {y: v for y, v in pop_ts}

    yearly_priv = {}
    yearly_pub = {}
    for i, d in enumerate(dates):
        yr = int(d[:4])
        pv = priv[i] if i < len(priv) and priv[i] is not None else 0
        pu = pub[i] if i < len(pub) and pub[i] is not None else 0
        if pv + pu > 0:
            yearly_priv.setdefault(yr, []).append(pv)
            yearly_pub.setdefault(yr, []).append(pu)

    result = []
    for yr in sorted(yearly_priv):
        pv_vals = yearly_priv.get(yr, [])
        pu_vals = yearly_pub.get(yr, [])
        if len(pv_vals) >= 6:
            avg_priv = sum(pv_vals) / len(pv_vals)
            avg_pub = sum(pu_vals) / len(pu_vals)
            pop = pop_by_year.get(yr)
            if mode == "private" and pop and pop > 0:
                rate = round(avg_priv * 1000 / pop * 1000, 1)
                result.append((yr, rate))
            elif mode == "public_share" and (avg_priv + avg_pub) > 0:
                share = round(avg_pub / (avg_priv + avg_pub) * 100, 1)
                result.append((yr, share))
            elif mode == "total" and pop and pop > 0:
                rate = round((avg_priv + avg_pub) * 1000 / pop * 1000, 1)
                result.append((yr, rate))
    return result


BILLION = 1_000_000_000
MILLION = 1_000_000


def extract_timeseries(mdef: dict, raw: dict, entity: str,
                       pop_data: dict, employment_data: dict) -> list[tuple[int, float]]:
    fmt = mdef["format"]
    per_cap = mdef.get("per_capita")

    lookup = entity

    if fmt == "employment":
        return get_timeseries_employment(employment_data, entity, pop_data, mode="total")
    elif fmt == "employment_private":
        return get_timeseries_employment(employment_data, entity, pop_data, mode="private")
    elif fmt == "employment_public_share":
        return get_timeseries_employment(employment_data, entity, pop_data, mode="public_share")
    elif fmt == "nested":
        ts = get_timeseries_nested(raw, lookup)
    elif fmt == "yearlist":
        ts = get_timeseries_yearlist(raw, lookup)
    elif fmt == "nested_sub":
        sub = raw.get(mdef.get("sub_key", ""), {})
        ts = get_timeseries_nested(sub, lookup)
    else:
        return []

    if per_cap and pop_data:
        pop_by_year = {y: v for y, v in get_timeseries_nested(pop_data, entity)}
        scaled = []
        for yr, val in ts:
            pop = pop_by_year.get(yr)
            if pop and pop > 0:
                if per_cap == "billion":
                    scaled.append((yr, round(val * BILLION / pop, 2)))
                elif per_cap == "million":
                    scaled.append((yr, round(val * MILLION / pop, 2)))
                elif per_cap == "per_10k":
                    scaled.append((yr, round(val / pop * 10000, 1)))
                elif per_cap == "per_1k":
                    scaled.append((yr, round(val / pop * 1000, 2)))
        return scaled
    return ts


# ---------------------------------------------------------------------------
# Scoring functions — all operate on truncated timeseries (up to year t)
# ---------------------------------------------------------------------------

def truncate_ts(ts: list[tuple[int, float]], up_to_year: int) -> list[tuple[int, float]]:
    """Return only entries with year <= up_to_year."""
    return [(y, v) for y, v in ts if y <= up_to_year]


def ema(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (span + 1)
    result = [values[0]]
    for v in values[1:]:
        result.append(alpha * v + (1 - alpha) * result[-1])
    return result


def compute_peer_grade(province_values: dict[str, float], invert: bool) -> dict[str, str]:
    ranked = sorted(
        [(p, v) for p, v in province_values.items() if v is not None],
        key=lambda x: x[1],
        reverse=not invert,
    )
    n = len(ranked)
    grades = {}
    for rank, (province, _) in enumerate(ranked, 1):
        pct = rank / n if n > 0 else 1
        if pct <= 0.2:
            grades[province] = "A"
        elif pct <= 0.5:
            grades[province] = "B"
        elif pct <= 0.8:
            grades[province] = "C"
        else:
            grades[province] = "D"
    return grades


def compute_trend(ts: list[tuple[int, float]], invert: bool) -> dict:
    values = [v for _, v in ts]
    if len(values) < MIN_HISTORY:
        return {"grade": "C", "direction": "stable", "pct_change": 0}

    ema_3 = ema(values, 3)
    ema_10 = ema(values, min(10, len(values)))
    e3, e10 = ema_3[-1], ema_10[-1]

    pct = ((e3 - e10) / abs(e10) * 100) if e10 != 0 else 0

    if invert:
        # Lower values are better, so negative change = good
        if pct < -10:
            grade, direction = "A", "strong_improving"
        elif pct < -3:
            grade, direction = "B", "improving"
        elif pct < 3:
            grade, direction = "C", "stable"
        elif pct < 10:
            grade, direction = "C", "worsening"
        else:
            grade, direction = "D", "strong_worsening"
    else:
        if pct > 10:
            grade, direction = "A", "strong_improving"
        elif pct > 3:
            grade, direction = "B", "improving"
        elif pct > -3:
            grade, direction = "C", "stable"
        elif pct > -10:
            grade, direction = "C", "worsening"
        else:
            grade, direction = "D", "strong_worsening"

    return {"grade": grade, "direction": direction, "pct_change": round(pct, 1)}


def compute_percentile(ts: list[tuple[int, float]], invert: bool, window: int = 20) -> dict:
    values = [v for _, v in ts]
    if len(values) < MIN_HISTORY:
        return {"grade": "C", "percentile": 50}

    window_vals = values[-window:] if len(values) >= window else values
    current = values[-1]
    lo, hi = min(window_vals), max(window_vals)

    if hi == lo:
        pct = 50
    else:
        pct = (current - lo) / (hi - lo) * 100

    # Invert: being at the LOW end is good
    if invert:
        pct = 100 - pct

    if pct >= 75:
        grade = "A"
    elif pct >= 50:
        grade = "B"
    elif pct >= 25:
        grade = "C"
    else:
        grade = "D"

    return {"grade": grade, "percentile": round(pct, 1)}


def compute_national_health(canada_ts: list[tuple[int, float]], invert: bool) -> dict:
    values = [v for _, v in canada_ts]
    if len(values) < MIN_HISTORY:
        return {"grade": "B", "ceiling": "A", "growth_10y": None, "status": "insufficient_data"}

    current = values[-1]
    idx_10 = max(0, len(values) - 11)
    val_10y = values[idx_10]
    growth = ((current - val_10y) / abs(val_10y) * 100) if val_10y != 0 else 0
    effective = -growth if invert else growth

    if effective > 15:
        status, grade, ceiling = "strong", "A", "A"
    elif effective > 5:
        status, grade, ceiling = "moderate", "B", "A"
    elif effective > -5:
        status, grade, ceiling = "stagnant", "C", "B"
    else:
        status, grade, ceiling = "declining", "D", "C"

    return {"grade": grade, "ceiling": ceiling, "growth_10y": round(growth, 1), "status": status}


GRADE_VALUES = {"A": 4, "B": 3, "C": 2, "D": 1}
VALUE_GRADES = {4: "A", 3: "B", 2: "C", 1: "D"}


def adjusted_grade(peer: str, trend: str, percentile: str, ceiling: str) -> str:
    raw = (GRADE_VALUES.get(peer, 2) * 0.4
           + GRADE_VALUES.get(trend, 2) * 0.3
           + GRADE_VALUES.get(percentile, 2) * 0.3)
    rounded = max(1, min(4, round(raw)))
    raw_g = VALUE_GRADES[rounded]
    ceiling_v = GRADE_VALUES.get(ceiling, 4)
    return VALUE_GRADES[ceiling_v] if GRADE_VALUES[raw_g] > ceiling_v else raw_g


# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------

METRIC_DEFS = [
    {"id": "deficit_pc", "name": "Deficit per Capita", "vertical": "fiscal",
     "file": "fiscal-deficit.json", "unit": "$", "invert": True,
     "format": "yearlist", "canada_key": "Canada", "per_capita": "billion",
     "dashboard": "dashboards/fiscal-deficit-per-capita.html"},
    {"id": "net_debt_pc", "name": "Net Debt per Capita", "vertical": "fiscal",
     "file": "fiscal-net-debt.json", "unit": "$", "invert": True,
     "format": "yearlist", "canada_key": "Canada", "per_capita": "billion",
     "dashboard": "dashboards/fiscal-net-debt-per-capita.html"},
    {"id": "revenue_pc", "name": "Revenue per Capita", "vertical": "fiscal",
     "file": "fiscal-government-revenue.json", "unit": "$", "invert": False,
     "format": "nested", "canada_key": "Canada", "per_capita": "million",
     "dashboard": "dashboards/fiscal-revenue-and-spending.html"},
    {"id": "gdp_pc", "name": "GDP per Capita", "vertical": "economy",
     "file": "economy-gdp-per-capita.json", "unit": "$", "invert": False,
     "format": "yearlist", "canada_key": "Canada", "per_capita": None,
     "dashboard": "dashboards/economy-gdp-per-capita.html"},
    {"id": "wages", "name": "Median Weekly Wages", "vertical": "economy",
     "file": "economy-median-weekly-wages.json", "unit": "$", "invert": False,
     "format": "nested", "canada_key": "Canada", "per_capita": None,
     "dashboard": "dashboards/economy-median-weekly-wages.html"},
    {"id": "priv_employment", "name": "Private Employment Rate", "vertical": "economy",
     "file": "economy-employment.json", "unit": "per 1K", "invert": False,
     "format": "employment_private", "canada_key": "Canada", "per_capita": None,
     "dashboard": "dashboards/economy-employment-by-sector.html"},
    {"id": "pub_share", "name": "Public Sector Share", "vertical": "economy",
     "file": "economy-employment.json", "unit": "%", "invert": True,
     "format": "employment_public_share", "canada_key": "Canada", "per_capita": None,
     "dashboard": "dashboards/economy-employment-by-sector.html"},
    {"id": "starts", "name": "Housing Starts per 10K", "vertical": "housing",
     "file": "housing-starts.json", "unit": "starts", "invert": False,
     "format": "nested", "canada_key": "Canada", "per_capita": "per_10k",
     "dashboard": "dashboards/housing-starts-by-province.html"},
    {"id": "nhpi", "name": "Housing Price Index", "vertical": "housing",
     "file": "housing-new-price-index.json", "unit": "index", "invert": True,
     "format": "nested", "canada_key": "Canada", "per_capita": None,
     "dashboard": "dashboards/housing-new-price-index.html"},
    {"id": "vacancy", "name": "Rental Vacancy Rate", "vertical": "housing",
     "file": "housing-rental-vacancy-rate.json", "unit": "%", "invert": False,
     "format": "nested", "canada_key": "Canada", "per_capita": None,
     "dashboard": "dashboards/housing-rental-vacancy-rate.html"},
    {"id": "csi", "name": "Crime Severity Index", "vertical": "crime",
     "file": "crime-severity-index.json", "unit": "index", "invert": True,
     "format": "yearlist", "canada_key": "Canada", "per_capita": None,
     "dashboard": "dashboards/crime-severity-index.html"},
    {"id": "vcsi", "name": "Violent CSI", "vertical": "crime",
     "file": "crime-breakdown.json", "unit": "index", "invert": True,
     "format": "nested_sub", "sub_key": "violent", "canada_key": "Canada",
     "per_capita": None, "dashboard": "dashboards/crime-violent-vs-nonviolent.html"},
    {"id": "homicide", "name": "Homicide Rate", "vertical": "crime",
     "file": "crime-homicide-rate.json", "unit": "per 100K", "invert": True,
     "format": "nested", "canada_key": "Canada", "per_capita": None,
     "dashboard": "dashboards/crime-homicide-rate.html"},
    {"id": "pop_growth", "name": "Population Growth", "vertical": "demographics",
     "file": "demographics-population-growth.json", "unit": "%", "invert": False,
     "format": "nested", "canada_key": "Canada", "per_capita": None,
     "dashboard": "dashboards/demographics-population-growth.html"},
    {"id": "immigration", "name": "Immigration per 1K", "vertical": "demographics",
     "file": "demographics-international-immigration.json", "unit": "per 1K",
     "invert": False, "format": "nested", "canada_key": "Canada",
     "per_capita": "per_1k", "dashboard": "dashboards/demographics-international-immigration.html"},
    {"id": "migration", "name": "Interp. Migration per 1K", "vertical": "demographics",
     "file": "demographics-interprovincial-migration.json", "unit": "per 1K",
     "invert": False, "format": "nested", "canada_key": None,
     "per_capita": "per_1k", "dashboard": "dashboards/demographics-interprovincial-migration.html"},
]


def score_metric_at_year(mdef: dict, all_ts: dict, canada_ts: list, t: int) -> dict | None:
    """Compute all three layers for one metric at year t."""
    invert = mdef["invert"]

    # Truncate all timeseries to year t
    prov_ts = {}
    prov_vals = {}
    for p in PROVINCES:
        tr = truncate_ts(all_ts.get(p, []), t)
        if tr and tr[-1][0] == t:  # must have data at exactly year t
            prov_ts[p] = tr
            prov_vals[p] = tr[-1][1]

    if len(prov_vals) < MIN_PROVINCES:
        return None

    can_tr = truncate_ts(canada_ts, t) if canada_ts else []

    # Layer 1: Peer rank
    peer_grades = compute_peer_grade(prov_vals, invert)

    # Layer 2: Trend + percentile
    trends = {}
    percentiles = {}
    for p, ts in prov_ts.items():
        trends[p] = compute_trend(ts, invert)
        percentiles[p] = compute_percentile(ts, invert)

    # Layer 3: National health
    if can_tr and len(can_tr) >= MIN_HISTORY:
        health = compute_national_health(can_tr, invert)
    else:
        health = {"grade": "B", "ceiling": "A", "growth_10y": None, "status": "no_data"}

    # Build province data
    provinces = {}
    for p in PROVINCES:
        if p not in prov_vals:
            continue
        pg = peer_grades.get(p, "C")
        tg = trends.get(p, {}).get("grade", "C")
        hg = percentiles.get(p, {}).get("grade", "C")
        adj = adjusted_grade(pg, tg, hg, health.get("ceiling", "A"))

        provinces[p] = {
            "value": prov_vals[p],
            "peer_grade": pg,
            "trend": trends.get(p, {}),
            "historical": percentiles.get(p, {}),
            "adjusted_grade": adj,
        }

    canada_val = can_tr[-1][1] if can_tr and can_tr[-1][0] == t else None

    return {
        "id": mdef["id"],
        "name": mdef["name"],
        "vertical": mdef["vertical"],
        "unit": mdef["unit"],
        "invert": invert,
        "dashboard": mdef["dashboard"],
        "canada_value": canada_val,
        "national_health": health,
        "provinces": provinces,
    }


def compute_composites(metrics: list[dict]) -> dict:
    composites = {}
    for p in PROVINCES:
        adj_scores, peer_scores = [], []
        for m in metrics:
            pd = m["provinces"].get(p, {})
            if pd.get("adjusted_grade"):
                adj_scores.append(GRADE_VALUES[pd["adjusted_grade"]])
            if pd.get("peer_grade"):
                peer_scores.append(GRADE_VALUES[pd["peer_grade"]])
        if adj_scores:
            avg_a = sum(adj_scores) / len(adj_scores)
            avg_p = sum(peer_scores) / len(peer_scores) if peer_scores else avg_a
            composites[p] = {
                "adjusted_score": round(avg_a, 2),
                "adjusted_grade": VALUE_GRADES[max(1, min(4, round(avg_a)))],
                "peer_score": round(avg_p, 2),
                "peer_grade": VALUE_GRADES[max(1, min(4, round(avg_p)))],
            }
    return composites


def main():
    print("=== Computing Scorecard v2 (Time-Series) ===\n")

    pop_data = load_json("demographics-population.json")
    employment_data = load_json("economy-employment.json")

    # Load raw data and extract full timeseries per metric per entity
    raw_cache = {}
    metric_ts = {}  # metric_id -> {entity: [(year, val), ...]}
    metric_canada_ts = {}

    for mdef in METRIC_DEFS:
        fname = mdef["file"]
        if fname not in raw_cache:
            raw_cache[fname] = load_json(fname)
        raw = raw_cache[fname]

        all_ts = {}
        for p in PROVINCES:
            ts = extract_timeseries(mdef, raw, p, pop_data, employment_data)
            if ts:
                all_ts[p] = ts
        metric_ts[mdef["id"]] = all_ts

        canada_ts = []
        if mdef["canada_key"]:
            canada_ts = extract_timeseries(mdef, raw, "Canada", pop_data, employment_data)
        metric_canada_ts[mdef["id"]] = canada_ts

    # Determine year range: find the range where most metrics have data
    all_years = set()
    for mid, ts_dict in metric_ts.items():
        for p, ts in ts_dict.items():
            for yr, _ in ts:
                all_years.add(yr)

    year_range = sorted(all_years)
    # Start from the year where we have enough history for scoring
    # Need MIN_HISTORY years of prior data, so start at earliest_data + MIN_HISTORY
    earliest_starts = []
    for mdef in METRIC_DEFS:
        ts_dict = metric_ts[mdef["id"]]
        if ts_dict:
            first_years = [ts[0][0] for ts in ts_dict.values() if ts]
            if first_years:
                earliest_starts.append(min(first_years))
    if not earliest_starts:
        print("No data found!")
        return

    # Start scoring from the year where at least half the metrics have MIN_HISTORY years
    start_year = max(min(earliest_starts) + MIN_HISTORY, 2000)
    end_year = max(year_range)

    print(f"  Computing scores for years {start_year}–{end_year}\n")

    snapshots = {}
    valid_years = []

    for t in range(start_year, end_year + 1):
        metrics_for_year = []
        for mdef in METRIC_DEFS:
            result = score_metric_at_year(
                mdef,
                metric_ts[mdef["id"]],
                metric_canada_ts[mdef["id"]],
                t,
            )
            if result:
                metrics_for_year.append(result)

        # Need at least 8 metrics for a meaningful scorecard
        if len(metrics_for_year) < 8:
            continue

        composites = compute_composites(metrics_for_year)
        snapshots[t] = {
            "metrics": metrics_for_year,
            "composites": composites,
            "metric_count": len(metrics_for_year),
        }
        valid_years.append(t)

    latest = max(valid_years) if valid_years else end_year

    # Build output
    scorecard = {
        "version": 2,
        "years": valid_years,
        "latest_year": latest,
        "provinces": PROVINCES,
        "metric_defs": [
            {"id": m["id"], "name": m["name"], "vertical": m["vertical"],
             "unit": m["unit"], "invert": m["invert"], "dashboard": m["dashboard"]}
            for m in METRIC_DEFS
        ],
        "methodology": {
            "layer_1": "Peer rank among provinces/territories at year t (top 20%=A, 20-50%=B, 50-80%=C, bottom 20%=D)",
            "layer_2": "Historical trajectory: EMA(3y) vs EMA(10y) trend + 20y percentile, all ending at year t",
            "layer_3": "National health: Canada's 10y growth rate ending at year t sets grade ceiling",
            "weights": {"peer_rank": 0.4, "trend": 0.3, "historical_percentile": 0.3},
        },
        "snapshots": snapshots,
    }

    path = os.path.join(DATA_DIR, "scorecard_v2.json")
    with open(path, "w") as f:
        json.dump(scorecard, f, separators=(",", ":"))

    print(f"  -> scorecard_v2.json ({len(valid_years)} years, {len(METRIC_DEFS)} metrics)")

    # Print latest year summary
    if latest in snapshots:
        snap = snapshots[latest]
        print(f"\n=== Year {latest} ({snap['metric_count']} metrics) ===\n")
        for m in snap["metrics"]:
            h = m["national_health"]
            print(f"  {m['name']:30s}  health: {h['status']:12s}  ceiling: {h['ceiling']}")

        print(f"\n=== Composites (year {latest}) ===\n")
        for p in sorted(snap["composites"], key=lambda x: snap["composites"][x]["adjusted_score"], reverse=True):
            c = snap["composites"][p]
            print(f"  {p:30s}  Peer: {c['peer_grade']} ({c['peer_score']})  →  Adjusted: {c['adjusted_grade']} ({c['adjusted_score']})")

    print("\nDone.")


if __name__ == "__main__":
    main()
