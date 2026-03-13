"""
Inject fresh data from data/*.json into dashboard HTML files.

Each dashboard embeds its data as `const ALL_DATA = {...};` inline.
This script reads the pipeline-generated JSON files, transforms them
into the format each dashboard expects, and replaces the inline data.

Usage: python pipeline/build_dashboards.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_DIR, PROVINCES_ORDERED

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH_DIR = os.path.join(BASE_DIR, "dashboards")


def load_json(filename: str) -> dict:
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


def nested_to_yearlist(data: dict, year_as_str: bool = True) -> dict:
    """Convert {entity: [{year, value}]} -> {years: [...], entities: {entity: [values]}}"""
    all_years = set()
    for entity, entries in data.items():
        for e in entries:
            all_years.add(e["year"])
    years_sorted = sorted(all_years)

    entities = {}
    for geo in PROVINCES_ORDERED:
        if geo not in data:
            continue
        by_year = {e["year"]: e["value"] for e in data[geo]}
        entities[geo] = [by_year.get(y) for y in years_sorted]

    years_out = [str(y) for y in years_sorted] if year_as_str else years_sorted
    return {"years": years_out, "entities": entities}


def inject_all_data(html: str, data: dict) -> str:
    """Replace const ALL_DATA = {...}; in HTML with new data."""
    data_json = json.dumps(data, separators=(",", ":"))
    pattern = r"const ALL_DATA\s*=\s*\{.*?\};\s*\n"
    replacement = f"const ALL_DATA = {data_json};\n"
    result, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)
    if count == 0:
        raise ValueError("Could not find 'const ALL_DATA = {...};' in HTML")
    return result


# ---------------------------------------------------------------------------
# Dashboard-specific builders
# ---------------------------------------------------------------------------

def build_simple_yearlist(filename: str) -> dict:
    """For dashboards whose JSON is already {years, entities} format."""
    return load_json(filename)


def build_nested_as_yearlist(filename: str, year_as_str: bool = True) -> dict:
    """For dashboards whose JSON is {entity: [{year, value}]} format."""
    return nested_to_yearlist(load_json(filename), year_as_str)


def build_crime_breakdown_sub(sub_key: str) -> dict:
    """For crime-violent-csi / crime-nonviolent-csi — one sub-key from breakdown."""
    raw = load_json("crime-breakdown.json")
    sub = raw.get(sub_key, {})
    return nested_to_yearlist(sub, year_as_str=False)


def build_crime_violent_vs_nonviolent() -> dict:
    """Combined violent + nonviolent CSI."""
    raw = load_json("crime-breakdown.json")
    v = nested_to_yearlist(raw.get("violent", {}), year_as_str=False)
    nv = nested_to_yearlist(raw.get("nonviolent", {}), year_as_str=False)
    # Merge years (should be identical)
    years = sorted(set(v["years"]) | set(nv["years"]))
    # Reindex both to merged years
    def reindex(yl, merged_years):
        yr_idx = {y: i for i, y in enumerate(yl["years"])}
        result = {}
        for entity, vals in yl["entities"].items():
            result[entity] = [vals[yr_idx[y]] if y in yr_idx and yr_idx[y] < len(vals) else None for y in merged_years]
        return result
    return {
        "years": years,
        "violent": reindex(v, years),
        "nonviolent": reindex(nv, years),
    }


def build_immigration() -> dict:
    """Immigration with raw counts + per-1K rates."""
    raw = load_json("demographics-international-immigration.json")
    pop = load_json("demographics-population.json")
    pop_lookup = {}
    for entity, entries in pop.items():
        for e in entries:
            pop_lookup[(entity, e["year"])] = e["value"]

    yl = nested_to_yearlist(raw)
    years_int = [int(y) for y in yl["years"]]

    per1k = {}
    for entity, vals in yl["entities"].items():
        per1k_vals = []
        for i, y in enumerate(years_int):
            v = vals[i]
            p = pop_lookup.get((entity, y))
            if v is not None and p and p > 0:
                per1k_vals.append(round(v / p * 1000, 2))
            else:
                per1k_vals.append(None)
        per1k[entity] = per1k_vals

    return {"years": yl["years"], "raw": yl["entities"], "per1K": per1k}


def build_fiscal_per_capita(fiscal_file: str) -> dict:
    """Deficit or net-debt per capita."""
    fiscal = load_json(fiscal_file)
    pop = load_json("demographics-population.json")
    pop_lookup = {}
    for entity, entries in pop.items():
        for e in entries:
            pop_lookup[(entity, e["year"])] = e["value"]

    # fiscal is yearlist: {years: [...], entities: {entity: [values in billions]}}
    years = fiscal["years"]
    entities = {}
    for entity, vals in fiscal["entities"].items():
        pc_vals = []
        for i, y in enumerate(years):
            v = vals[i] if i < len(vals) else None
            # Parse year: fiscal years like "2020-21" -> use first year
            try:
                yr_int = int(str(y)[:4])
            except (ValueError, IndexError):
                pc_vals.append(None)
                continue
            p = pop_lookup.get((entity, yr_int)) or pop_lookup.get((entity, yr_int + 1))
            if v is not None and p and p > 0:
                # Values are in billions
                pc_vals.append(round(v * 1_000_000_000 / p, 2))
            else:
                pc_vals.append(None)
        entities[entity] = pc_vals

    return {"years": years, "entities": entities}


def build_revenue_and_spending() -> dict:
    """Combined revenue + spending + balance."""
    rev_raw = load_json("fiscal-government-revenue.json")
    spend_raw = load_json("fiscal-government-spending.json")

    rev_yl = nested_to_yearlist(rev_raw)
    spend_yl = nested_to_yearlist(spend_raw)

    # Merge years
    years = sorted(set(rev_yl["years"]) | set(spend_yl["years"]))

    def reindex(yl, merged_years):
        yr_idx = {y: i for i, y in enumerate(yl["years"])}
        result = {}
        for entity, vals in yl["entities"].items():
            result[entity] = [vals[yr_idx[y]] if y in yr_idx and yr_idx[y] < len(vals) else None for y in merged_years]
        return result

    revenue = reindex(rev_yl, years)
    spending = reindex(spend_yl, years)

    # Balance = revenue - spending (in millions)
    balance = {}
    all_entities = set(list(revenue.keys()) + list(spending.keys()))
    for entity in all_entities:
        rv = revenue.get(entity, [None] * len(years))
        sv = spending.get(entity, [None] * len(years))
        bv = []
        for r, s in zip(rv, sv):
            if r is not None and s is not None:
                bv.append(round(r - s, 1))
            else:
                bv.append(None)
        balance[entity] = bv

    return {"years": years, "revenue": revenue, "spending": spending, "balance": balance}


def build_housing_starts() -> dict:
    """Housing starts per 10K + raw + price index."""
    starts_raw = load_json("housing-starts.json")
    nhpi_raw = load_json("housing-new-price-index.json")
    pop = load_json("demographics-population.json")
    pop_lookup = {}
    for entity, entries in pop.items():
        for e in entries:
            pop_lookup[(entity, e["year"])] = e["value"]

    starts_yl = nested_to_yearlist(starts_raw)
    nhpi_yl = nested_to_yearlist(nhpi_raw)
    years = starts_yl["years"]
    years_int = [int(y) for y in years]

    starts_per_10k = {}
    for entity, vals in starts_yl["entities"].items():
        pc = []
        for i, y in enumerate(years_int):
            v = vals[i]
            p = pop_lookup.get((entity, y))
            if v is not None and p and p > 0:
                pc.append(round(v / p * 10000, 2))
            else:
                pc.append(None)
        starts_per_10k[entity] = pc

    # Reindex NHPI to same years
    nhpi_idx = {y: i for i, y in enumerate(nhpi_yl["years"])}
    price_index = {}
    for entity, vals in nhpi_yl["entities"].items():
        price_index[entity] = [vals[nhpi_idx[y]] if y in nhpi_idx and nhpi_idx[y] < len(vals) else None for y in years]

    return {
        "years": years,
        "startsPer10K": starts_per_10k,
        "startsRaw": starts_yl["entities"],
        "priceIndex": price_index,
    }


def build_housing_affordability() -> dict:
    """Housing affordability (NHPI) as yearlist."""
    return build_nested_as_yearlist("housing-new-price-index.json")


def build_interprovincial_migration() -> dict:
    """Interprovincial migration (no Canada entity)."""
    raw = load_json("demographics-interprovincial-migration.json")
    all_years = set()
    for entity, entries in raw.items():
        for e in entries:
            all_years.add(e["year"])
    years_sorted = sorted(all_years)

    entities = {}
    for geo in PROVINCES_ORDERED:
        if geo == "Canada":
            continue
        if geo not in raw:
            continue
        by_year = {e["year"]: e["value"] for e in raw[geo]}
        entities[geo] = [by_year.get(y) for y in years_sorted]

    return {"years": [str(y) for y in years_sorted], "entities": entities}


# ---------------------------------------------------------------------------
# Dashboard registry: filename -> builder function
# ---------------------------------------------------------------------------

DASHBOARD_BUILDERS = {
    # Crime
    "crime-severity-index.html": lambda: build_simple_yearlist("crime-severity-index.json"),
    "crime-homicide-rate.html": lambda: build_nested_as_yearlist("crime-homicide-rate.json"),
    "crime-violent-csi.html": lambda: build_crime_breakdown_sub("violent"),
    "crime-nonviolent-csi.html": lambda: build_crime_breakdown_sub("nonviolent"),
    "crime-violent-vs-nonviolent.html": build_crime_violent_vs_nonviolent,
    # Demographics
    "demographics-population-growth.html": lambda: build_nested_as_yearlist("demographics-population-growth.json"),
    "demographics-international-immigration.html": build_immigration,
    "demographics-interprovincial-migration.html": build_interprovincial_migration,
    # Economy
    "economy-gdp-per-capita.html": lambda: build_simple_yearlist("economy-gdp-per-capita.json"),
    "economy-median-weekly-wages.html": lambda: build_nested_as_yearlist("economy-median-weekly-wages.json"),
    # Fiscal
    "fiscal-deficit-per-capita.html": lambda: build_fiscal_per_capita("fiscal-deficit.json"),
    "fiscal-net-debt-per-capita.html": lambda: build_fiscal_per_capita("fiscal-net-debt.json"),
    "fiscal-government-revenue.html": lambda: build_nested_as_yearlist("fiscal-government-revenue.json"),
    "fiscal-government-spending.html": lambda: build_nested_as_yearlist("fiscal-government-spending.json"),
    "fiscal-revenue-and-spending.html": build_revenue_and_spending,
    # Housing
    "housing-new-price-index.html": lambda: build_nested_as_yearlist("housing-new-price-index.json"),
    "housing-rental-vacancy-rate.html": lambda: build_nested_as_yearlist("housing-rental-vacancy-rate.json"),
    "housing-starts-by-province.html": build_housing_starts,
    "housing-affordability-index.html": build_housing_affordability,
}


def main():
    print("=== Injecting data into dashboards ===\n")

    success = 0
    failed = 0

    for dash_file, builder in sorted(DASHBOARD_BUILDERS.items()):
        dash_path = os.path.join(DASH_DIR, dash_file)
        if not os.path.exists(dash_path):
            print(f"  [SKIP] {dash_file} — file not found")
            continue

        try:
            data = builder()
            with open(dash_path, "r") as f:
                html = f.read()
            html = inject_all_data(html, data)
            with open(dash_path, "w") as f:
                f.write(html)

            # Count entities
            ent_keys = set()
            for key in data:
                if key == "years":
                    continue
                val = data[key]
                if isinstance(val, dict):
                    ent_keys.update(val.keys())
            print(f"  [OK] {dash_file} ({len(ent_keys)} entities)")
            success += 1
        except Exception as e:
            print(f"  [ERROR] {dash_file}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\nDone: {success} dashboards updated, {failed} failed")

    # Note: economy-employment-by-sector.html fetches from JSON at runtime
    print("\nNote: economy-employment-by-sector.html fetches data at runtime (no injection needed)")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
