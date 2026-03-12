"""
Scorecard v2: Three-layer grading with historical benchmarking.

Layer 1 — Peer Rank: Province rank among 10 provinces (same as v1)
Layer 2 — Historical Trajectory: EMA(3y) vs EMA(10y) + percentile in own 20y range
Layer 3 — National Health: Canada's 10y growth rate caps provincial grades

Output: data/scorecard_v2.json

Usage: python pipeline/scorecard_v2.py
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_DIR, PROVINCES_ORDERED

PROVINCES = [p for p in PROVINCES_ORDERED if p != "Canada"]


def load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Time-series extraction helpers
# ---------------------------------------------------------------------------

def get_timeseries_nested(data: dict, entity: str) -> list[tuple[int, float]]:
    """Extract sorted (year, value) pairs from {entity: [{year, value}]} format."""
    if entity not in data:
        return []
    entries = data[entity]
    return sorted(
        [(e["year"], e["value"]) for e in entries if e.get("value") is not None],
        key=lambda x: x[0],
    )


def get_timeseries_yearlist(data: dict, entity: str) -> list[tuple[int, float]]:
    """Extract sorted (year, value) pairs from {years: [], entities: {name: []}} format."""
    if entity not in data.get("entities", {}):
        return []
    years = data.get("years", [])
    values = data["entities"][entity]
    result = []
    for i, y in enumerate(years):
        if i < len(values) and values[i] is not None:
            # Handle fiscal years like "2024-25" -> 2024
            yr = int(str(y)[:4]) if isinstance(y, str) else int(y)
            result.append((yr, values[i]))
    return sorted(result, key=lambda x: x[0])


def get_timeseries_employment(data: dict, entity: str, pop_data: dict) -> list[tuple[int, float]]:
    """Extract annual employment rate from monthly employment data."""
    pdata = data.get("provinces", {}).get(entity, {})
    dates = data.get("dates", [])
    priv = pdata.get("private", [])
    pub = pdata.get("public", [])
    if not priv or not pub or not dates:
        return []

    # Get population timeseries for per-capita calc
    pop_ts = get_timeseries_nested(pop_data, entity)
    pop_by_year = {y: v for y, v in pop_ts}

    # Aggregate monthly to annual
    yearly = {}
    for i, d in enumerate(dates):
        yr = int(d[:4])
        pv = priv[i] if i < len(priv) and priv[i] is not None else 0
        pu = pub[i] if i < len(pub) and pub[i] is not None else 0
        if pv + pu > 0:
            yearly.setdefault(yr, []).append(pv + pu)

    result = []
    for yr in sorted(yearly):
        vals = yearly[yr]
        if len(vals) >= 6:  # need at least 6 months
            avg = sum(vals) / len(vals)
            pop = pop_by_year.get(yr)
            if pop and pop > 0:
                rate = round(avg * 1000 / pop * 1000, 1)
                result.append((yr, rate))
    return result


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def ema(values: list[float], span: int) -> list[float]:
    """Compute exponential moving average."""
    if not values:
        return []
    alpha = 2 / (span + 1)
    result = [values[0]]
    for v in values[1:]:
        result.append(alpha * v + (1 - alpha) * result[-1])
    return result


def compute_peer_grade(province_values: dict[str, float], invert: bool = False) -> dict[str, str]:
    """Assign A-D grades based on rank among provinces."""
    ranked = sorted(
        [(p, v) for p, v in province_values.items() if v is not None],
        key=lambda x: x[1],
        reverse=not invert,
    )
    grades = {}
    for rank, (province, _) in enumerate(ranked, 1):
        if rank <= 2:
            grades[province] = "A"
        elif rank <= 5:
            grades[province] = "B"
        elif rank <= 8:
            grades[province] = "C"
        else:
            grades[province] = "D"
    return grades


def compute_trend_score(timeseries: list[tuple[int, float]]) -> dict:
    """Compute trend score from EMA(3y) vs EMA(10y).

    Returns: {grade, ema_3, ema_10, direction, pct_change}
    """
    values = [v for _, v in timeseries]
    if len(values) < 5:
        return {"grade": "C", "ema_3": None, "ema_10": None, "direction": "stable", "pct_change": 0}

    ema_3 = ema(values, 3)
    ema_10 = ema(values, min(10, len(values)))

    latest_ema3 = ema_3[-1]
    latest_ema10 = ema_10[-1]

    if latest_ema10 == 0:
        pct = 0
    else:
        pct = (latest_ema3 - latest_ema10) / abs(latest_ema10) * 100

    # Grade the trend strength
    if pct > 10:
        grade, direction = "A", "strong_up"
    elif pct > 3:
        grade, direction = "B", "up"
    elif pct > -3:
        grade, direction = "C", "stable"
    elif pct > -10:
        grade, direction = "C", "down"
    else:
        grade, direction = "D", "strong_down"

    return {
        "grade": grade,
        "ema_3": round(latest_ema3, 2),
        "ema_10": round(latest_ema10, 2),
        "direction": direction,
        "pct_change": round(pct, 1),
    }


def compute_historical_percentile(timeseries: list[tuple[int, float]], window: int = 20) -> dict:
    """Where does current value sit in its own N-year historical range?

    Returns: {grade, percentile, min, max, current}
    """
    values = [v for _, v in timeseries]
    if len(values) < 5:
        return {"grade": "C", "percentile": 50, "min": None, "max": None, "current": None}

    # Use last `window` years
    window_vals = values[-window:] if len(values) >= window else values
    current = values[-1]
    lo, hi = min(window_vals), max(window_vals)

    if hi == lo:
        pct = 50
    else:
        pct = (current - lo) / (hi - lo) * 100

    # Grade based on percentile
    if pct >= 75:
        grade = "A"
    elif pct >= 50:
        grade = "B"
    elif pct >= 25:
        grade = "C"
    else:
        grade = "D"

    return {
        "grade": grade,
        "percentile": round(pct, 1),
        "min": round(lo, 2),
        "max": round(hi, 2),
        "current": round(current, 2),
    }


def compute_national_health(canada_ts: list[tuple[int, float]], invert: bool = False) -> dict:
    """Score Canada's own 10y trajectory.

    Returns: {grade, ceiling, growth_10y, growth_20y, status}
    """
    if len(canada_ts) < 5:
        return {"grade": "B", "ceiling": "A", "growth_10y": None, "growth_20y": None, "status": "insufficient_data"}

    values = [v for _, v in canada_ts]
    current = values[-1]

    # 10-year growth
    idx_10 = max(0, len(values) - 11)
    val_10y_ago = values[idx_10]
    if val_10y_ago != 0:
        growth_10y = (current - val_10y_ago) / abs(val_10y_ago) * 100
    else:
        growth_10y = 0

    # 20-year growth
    idx_20 = max(0, len(values) - 21)
    val_20y_ago = values[idx_20]
    if val_20y_ago != 0:
        growth_20y = (current - val_20y_ago) / abs(val_20y_ago) * 100
    else:
        growth_20y = 0

    # For inverted metrics (lower = better), flip the growth interpretation
    effective_growth = -growth_10y if invert else growth_10y

    # Determine health status and grade ceiling
    if effective_growth > 15:
        status, grade, ceiling = "strong", "A", "A"
    elif effective_growth > 5:
        status, grade, ceiling = "moderate", "B", "A"
    elif effective_growth > -5:
        status, grade, ceiling = "stagnant", "C", "B"
    else:
        status, grade, ceiling = "declining", "D", "C"

    return {
        "grade": grade,
        "ceiling": ceiling,
        "growth_10y": round(growth_10y, 1),
        "growth_20y": round(growth_20y, 1),
        "status": status,
    }


GRADE_VALUES = {"A": 4, "B": 3, "C": 2, "D": 1}
VALUE_GRADES = {4: "A", 3: "B", 2: "C", 1: "D"}


def compute_adjusted_grade(peer: str, trend: str, percentile: str, ceiling: str) -> str:
    """Combine layers into a single adjusted grade.

    Weights: peer_rank=40%, trend=30%, historical_percentile=30%
    Then cap at national health ceiling.
    """
    raw_score = (
        GRADE_VALUES.get(peer, 2) * 0.4
        + GRADE_VALUES.get(trend, 2) * 0.3
        + GRADE_VALUES.get(percentile, 2) * 0.3
    )
    # Round to nearest grade
    rounded = max(1, min(4, round(raw_score)))
    raw_grade = VALUE_GRADES[rounded]

    # Apply ceiling
    ceiling_val = GRADE_VALUES.get(ceiling, 4)
    if GRADE_VALUES[raw_grade] > ceiling_val:
        return VALUE_GRADES[ceiling_val]
    return raw_grade


# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------

METRIC_DEFS = [
    # (id, name, vertical, data_file, entity_key_for_canada, format, unit, invert, extractor, per_capita_scale)
    # Fiscal
    {
        "id": "deficit_per_capita",
        "name": "Deficit per Capita",
        "vertical": "fiscal",
        "file": "fiscal-deficit.json",
        "unit": "$",
        "invert": True,
        "format": "yearlist",
        "canada_key": "Federal",
        "per_capita": "billion",
        "dashboard": "dashboards/fiscal-deficit-per-capita.html",
    },
    {
        "id": "net_debt_per_capita",
        "name": "Net Debt per Capita",
        "vertical": "fiscal",
        "file": "fiscal-net-debt.json",
        "unit": "$",
        "invert": True,
        "format": "yearlist",
        "canada_key": "Federal",
        "per_capita": "billion",
        "dashboard": "dashboards/fiscal-net-debt-per-capita.html",
    },
    {
        "id": "revenue_per_capita",
        "name": "Revenue per Capita",
        "vertical": "fiscal",
        "file": "fiscal-government-revenue.json",
        "unit": "$",
        "invert": False,
        "format": "nested",
        "canada_key": "Federal",
        "per_capita": "million",
        "dashboard": "dashboards/fiscal-revenue-and-spending.html",
    },
    # Economy
    {
        "id": "gdp_per_capita",
        "name": "GDP per Capita",
        "vertical": "economy",
        "file": "economy-gdp-per-capita.json",
        "unit": "$",
        "invert": False,
        "format": "yearlist",
        "canada_key": "Canada",
        "per_capita": None,  # already per-capita
        "dashboard": "dashboards/economy-gdp-per-capita.html",
    },
    {
        "id": "median_wages",
        "name": "Median Weekly Wages",
        "vertical": "economy",
        "file": "economy-median-weekly-wages.json",
        "unit": "$",
        "invert": False,
        "format": "nested",
        "canada_key": "Canada",
        "per_capita": None,
        "dashboard": "dashboards/economy-median-weekly-wages.html",
    },
    {
        "id": "employment_rate",
        "name": "Employment Rate",
        "vertical": "economy",
        "file": "economy-employment.json",
        "unit": "per 1K",
        "invert": False,
        "format": "employment",
        "canada_key": "Canada",
        "per_capita": None,
        "dashboard": "dashboards/economy-employment-by-sector.html",
    },
    # Housing
    {
        "id": "housing_starts",
        "name": "Housing Starts per 10K",
        "vertical": "housing",
        "file": "housing-starts.json",
        "unit": "starts",
        "invert": False,
        "format": "nested",
        "canada_key": "Canada",
        "per_capita": "per_10k",
        "dashboard": "dashboards/housing-starts-by-province.html",
    },
    {
        "id": "housing_price_index",
        "name": "Housing Price Index",
        "vertical": "housing",
        "file": "housing-new-price-index.json",
        "unit": "index",
        "invert": True,
        "format": "nested",
        "canada_key": "Canada",
        "per_capita": None,
        "dashboard": "dashboards/housing-new-price-index.html",
    },
    {
        "id": "rental_vacancy",
        "name": "Rental Vacancy Rate",
        "vertical": "housing",
        "file": "housing-rental-vacancy-rate.json",
        "unit": "%",
        "invert": False,
        "format": "nested",
        "canada_key": "Canada",
        "per_capita": None,
        "dashboard": "dashboards/housing-rental-vacancy-rate.html",
    },
    # Crime
    {
        "id": "crime_severity",
        "name": "Crime Severity Index",
        "vertical": "crime",
        "file": "crime-severity-index.json",
        "unit": "index",
        "invert": True,
        "format": "yearlist",
        "canada_key": "Canada",
        "per_capita": None,
        "dashboard": "dashboards/crime-severity-index.html",
    },
    {
        "id": "violent_csi",
        "name": "Violent CSI",
        "vertical": "crime",
        "file": "crime-breakdown.json",
        "unit": "index",
        "invert": True,
        "format": "nested_sub",  # special: data["violent"][entity]
        "sub_key": "violent",
        "canada_key": "Canada",
        "per_capita": None,
        "dashboard": "dashboards/crime-violent-vs-nonviolent.html",
    },
    {
        "id": "homicide_rate",
        "name": "Homicide Rate",
        "vertical": "crime",
        "file": "crime-homicide-rate.json",
        "unit": "per 100K",
        "invert": True,
        "format": "nested",
        "canada_key": "Canada",
        "per_capita": None,
        "dashboard": "dashboards/crime-homicide-rate.html",
    },
    # Demographics
    {
        "id": "pop_growth",
        "name": "Population Growth",
        "vertical": "demographics",
        "file": "demographics-population-growth.json",
        "unit": "%",
        "invert": False,
        "format": "nested",
        "canada_key": "Canada",
        "per_capita": None,
        "dashboard": "dashboards/demographics-population-growth.html",
    },
    {
        "id": "immigration",
        "name": "Immigration per 1K",
        "vertical": "demographics",
        "file": "demographics-international-immigration.json",
        "unit": "per 1K",
        "invert": False,
        "format": "nested",
        "canada_key": "Canada",
        "per_capita": "per_1k",
        "dashboard": "dashboards/demographics-international-immigration.html",
    },
    {
        "id": "interp_migration",
        "name": "Interprovincial Migration per 1K",
        "vertical": "demographics",
        "file": "demographics-interprovincial-migration.json",
        "unit": "per 1K",
        "invert": False,
        "format": "nested",
        "canada_key": None,  # no Canada aggregate for this one
        "per_capita": "per_1k",
        "dashboard": "dashboards/demographics-interprovincial-migration.html",
    },
]

BILLION = 1_000_000_000
MILLION = 1_000_000


def extract_timeseries(metric_def: dict, raw_data: dict, entity: str,
                       pop_data: dict = None, employment_data: dict = None) -> list[tuple[int, float]]:
    """Extract (year, value) timeseries for an entity from raw data."""
    fmt = metric_def["format"]
    per_cap = metric_def.get("per_capita")

    # Handle fiscal entity naming
    if entity == "Canada" and metric_def.get("canada_key") == "Federal":
        lookup_entity = "Federal"
    elif metric_def.get("canada_key") == "Federal" and entity != "Canada":
        lookup_entity = entity
    else:
        lookup_entity = entity

    if fmt == "employment":
        return get_timeseries_employment(employment_data or raw_data, entity, pop_data)
    elif fmt == "nested":
        ts = get_timeseries_nested(raw_data, lookup_entity)
    elif fmt == "yearlist":
        ts = get_timeseries_yearlist(raw_data, lookup_entity)
    elif fmt == "nested_sub":
        sub = raw_data.get(metric_def.get("sub_key", ""), {})
        ts = get_timeseries_nested(sub, lookup_entity)
    else:
        return []

    # Apply per-capita scaling if needed
    if per_cap and pop_data:
        pop_ts = get_timeseries_nested(pop_data, entity)
        pop_by_year = {y: v for y, v in pop_ts}

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
            # skip years without population data
        return scaled

    return ts


def main():
    print("=== Computing Scorecard v2 (Historical Benchmarking) ===\n")

    # Load population for per-capita calcs
    pop_data = load_json("demographics-population.json")
    employment_data = load_json("economy-employment.json")

    # Load all raw data files
    raw_data_cache = {}
    for mdef in METRIC_DEFS:
        fname = mdef["file"]
        if fname not in raw_data_cache:
            raw_data_cache[fname] = load_json(fname)

    metrics = []

    for mdef in METRIC_DEFS:
        print(f"  [{mdef['vertical']}] {mdef['name']}")
        raw = raw_data_cache[mdef["file"]]
        invert = mdef["invert"]

        # --- Extract timeseries for all entities ---
        all_ts = {}
        for entity in PROVINCES:
            ts = extract_timeseries(mdef, raw, entity, pop_data, employment_data)
            if ts:
                all_ts[entity] = ts

        # Canada timeseries
        canada_ts = []
        if mdef["canada_key"]:
            canada_ts = extract_timeseries(mdef, raw, "Canada", pop_data, employment_data)

        # --- Layer 1: Peer Rank ---
        latest_values = {}
        for p, ts in all_ts.items():
            if ts:
                latest_values[p] = ts[-1][1]

        peer_grades = compute_peer_grade(latest_values, invert=invert)

        # --- Layer 2: Historical Trajectory ---
        trend_scores = {}
        hist_percentiles = {}
        for p, ts in all_ts.items():
            trend_result = compute_trend_score(ts)
            # For inverted metrics, flip the trend interpretation
            if invert:
                # For inverted metrics, negative change (values going down) is GOOD
                trend_result = compute_trend_score_inverted(ts)
            trend_scores[p] = trend_result

            hist_result = compute_historical_percentile(ts)
            # For inverted metrics, flip percentile (being at the LOW end is good)
            if invert:
                hist_result["percentile"] = 100 - hist_result["percentile"]
                pct = hist_result["percentile"]
                if pct >= 75:
                    hist_result["grade"] = "A"
                elif pct >= 50:
                    hist_result["grade"] = "B"
                elif pct >= 25:
                    hist_result["grade"] = "C"
                else:
                    hist_result["grade"] = "D"
            hist_percentiles[p] = hist_result

        # --- Layer 3: National Health ---
        if canada_ts:
            national_health = compute_national_health(canada_ts, invert=invert)
        else:
            national_health = {"grade": "B", "ceiling": "A", "growth_10y": None, "growth_20y": None, "status": "no_national_data"}

        # --- Compute adjusted grades ---
        provinces_data = {}
        for p in PROVINCES:
            peer = peer_grades.get(p, "C")
            trend = trend_scores.get(p, {}).get("grade", "C")
            hist_pct = hist_percentiles.get(p, {}).get("grade", "C")
            ceiling = national_health.get("ceiling", "A")

            adjusted = compute_adjusted_grade(peer, trend, hist_pct, ceiling)

            provinces_data[p] = {
                "value": latest_values.get(p),
                "peer_grade": peer,
                "trend": trend_scores.get(p, {}),
                "historical": hist_percentiles.get(p, {}),
                "adjusted_grade": adjusted,
            }

        # Canada data
        canada_value = canada_ts[-1][1] if canada_ts else None
        canada_trend = compute_trend_score(canada_ts) if canada_ts else {}

        metric_entry = {
            "id": mdef["id"],
            "name": mdef["name"],
            "vertical": mdef["vertical"],
            "unit": mdef["unit"],
            "invert": invert,
            "dashboard": mdef["dashboard"],
            "canada": {
                "value": canada_value,
                "trend": canada_trend,
            },
            "national_health": national_health,
            "provinces": provinces_data,
        }

        metrics.append(metric_entry)
        print(f"    National health: {national_health['status']} (10y: {national_health.get('growth_10y')}%, ceiling: {national_health['ceiling']})")

    # --- Composite scores ---
    composites = {}
    for p in PROVINCES:
        adjusted_scores = []
        peer_scores = []
        for m in metrics:
            pdata = m["provinces"].get(p, {})
            adj = pdata.get("adjusted_grade")
            peer = pdata.get("peer_grade")
            if adj:
                adjusted_scores.append(GRADE_VALUES[adj])
            if peer:
                peer_scores.append(GRADE_VALUES[peer])

        if adjusted_scores:
            avg_adj = sum(adjusted_scores) / len(adjusted_scores)
            avg_peer = sum(peer_scores) / len(peer_scores) if peer_scores else avg_adj
            composites[p] = {
                "adjusted_score": round(avg_adj, 2),
                "adjusted_grade": VALUE_GRADES[max(1, min(4, round(avg_adj)))],
                "peer_score": round(avg_peer, 2),
                "peer_grade": VALUE_GRADES[max(1, min(4, round(avg_peer)))],
            }

    scorecard = {
        "version": 2,
        "methodology": {
            "layer_1": "Peer rank among 10 provinces (A=rank 1-2, B=3-5, C=6-8, D=9-10)",
            "layer_2": "Historical trajectory — EMA(3y) vs EMA(10y) trend + 20y percentile",
            "layer_3": "National health — Canada 10y growth rate sets grade ceiling",
            "weights": {"peer_rank": 0.4, "trend": 0.3, "historical_percentile": 0.3},
            "ceiling_rules": {
                "strong (>15%)": "A",
                "moderate (5-15%)": "A",
                "stagnant (-5% to 5%)": "B",
                "declining (<-5%)": "C",
            },
        },
        "metrics": metrics,
        "composites": composites,
        "provinces": PROVINCES,
    }

    path = os.path.join(DATA_DIR, "scorecard_v2.json")
    with open(path, "w") as f:
        json.dump(scorecard, f, indent=2)

    print(f"\n  -> scorecard_v2.json ({len(metrics)} metrics, {len(PROVINCES)} provinces)")

    # Print summary
    print("\n=== Grade Changes (Peer → Adjusted) ===\n")
    for m in metrics:
        changes = []
        for p in PROVINCES:
            pd = m["provinces"].get(p, {})
            peer = pd.get("peer_grade", "?")
            adj = pd.get("adjusted_grade", "?")
            if peer != adj:
                changes.append(f"{p}: {peer}→{adj}")
        if changes:
            health = m["national_health"]["status"]
            ceiling = m["national_health"]["ceiling"]
            print(f"  {m['name']} (health: {health}, ceiling: {ceiling})")
            for c in changes:
                print(f"    {c}")

    print("\n=== Composite Comparison ===\n")
    for p in sorted(composites, key=lambda x: composites[x]["adjusted_score"], reverse=True):
        c = composites[p]
        print(f"  {p:30s}  Peer: {c['peer_grade']} ({c['peer_score']})  →  Adjusted: {c['adjusted_grade']} ({c['adjusted_score']})")

    print("\nDone.")


def compute_trend_score_inverted(timeseries: list[tuple[int, float]]) -> dict:
    """Compute trend score for inverted metrics (lower = better).
    A declining value is GOOD for inverted metrics.
    """
    values = [v for _, v in timeseries]
    if len(values) < 5:
        return {"grade": "C", "ema_3": None, "ema_10": None, "direction": "stable", "pct_change": 0}

    ema_3 = ema(values, 3)
    ema_10 = ema(values, min(10, len(values)))

    latest_ema3 = ema_3[-1]
    latest_ema10 = ema_10[-1]

    if latest_ema10 == 0:
        pct = 0
    else:
        pct = (latest_ema3 - latest_ema10) / abs(latest_ema10) * 100

    # For inverted metrics: negative change = improving
    if pct < -10:
        grade, direction = "A", "strong_down"  # values dropping fast = great
    elif pct < -3:
        grade, direction = "B", "down"
    elif pct < 3:
        grade, direction = "C", "stable"
    elif pct < 10:
        grade, direction = "C", "up"  # values rising = bad for inverted
    else:
        grade, direction = "D", "strong_up"

    return {
        "grade": grade,
        "ema_3": round(latest_ema3, 2),
        "ema_10": round(latest_ema10, 2),
        "direction": direction,
        "pct_change": round(pct, 1),
    }


if __name__ == "__main__":
    main()
