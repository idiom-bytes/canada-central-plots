"""
Transform StatCan CSVs from pipeline/lake/ into JSON data files in data/.

Each transform function reads the relevant CSV and outputs the JSON format
expected by the dashboard HTML files.

Usage: python pipeline/transform.py
"""
import csv
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import LAKE_DIR, DATA_DIR, PROVINCE_CANONICAL, PROVINCES_ORDERED


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_csv(table_id: str) -> str:
    """Find the main CSV file for a StatCan table in the lake."""
    table_clean = table_id.replace("-", "")
    path = os.path.join(LAKE_DIR, table_id, f"{table_clean}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}. Run download.py first.")
    return path


def read_csv_iter(path: str):
    """Iterate over a StatCan CSV, handling BOM and encoding. Memory efficient."""
    with open(path, "r", encoding="utf-8-sig") as f:
        yield from csv.DictReader(f)


def normalize_geo(geo: str) -> str | None:
    """Normalize a StatCan GEO string to our canonical province name.
    Handles GEO values like 'Ontario [35]' by stripping bracket suffixes."""
    geo = geo.strip()
    # Strip DGUID bracket suffix: "Ontario [35]" -> "Ontario"
    if "[" in geo:
        geo = geo[:geo.index("[")].strip()
    if geo == "Canada":
        return "Canada"
    return PROVINCE_CANONICAL.get(geo)


def save_json(filename: str, data: dict | list):
    """Save data as formatted JSON to data/ directory."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"    -> {filename}")


def parse_year(ref_date: str) -> int | None:
    """Parse REF_DATE to year. Handles '2020', '2020-01', '2020-Q3', etc."""
    try:
        return int(ref_date[:4])
    except (ValueError, IndexError):
        return None


def parse_float(val: str) -> float | None:
    """Parse VALUE field, returning None for empty/missing."""
    if not val or val.strip() == "":
        return None
    try:
        return float(val)
    except ValueError:
        return None


def dedup_by_year(items: list[dict]) -> list[dict]:
    """Deduplicate [{year, value}] entries, keeping last per year, sorted."""
    seen = {}
    for item in items:
        seen[item["year"]] = item
    return sorted(seen.values(), key=lambda x: x["year"])


def build_result(data: dict, include_canada: bool = True) -> dict:
    """Build ordered result dict from province data."""
    result = {}
    for geo in PROVINCES_ORDERED:
        if not include_canada and geo == "Canada":
            continue
        if geo in data and data[geo]:
            result[geo] = dedup_by_year(data[geo])
    return result


# ---------------------------------------------------------------------------
# Transform functions
# ---------------------------------------------------------------------------

def transform_gdp_per_capita():
    """36-10-0222 + 17-10-0005 -> economy-gdp-per-capita.json
    GDP is in millions (chained 2017 dollars); divide by population for per-capita.
    Output format: {years: [...], entities: {name: [values]}}
    """
    print("  [transform] 36-10-0222: GDP per capita")

    # Load population for per-capita calculation
    pop_path = os.path.join(DATA_DIR, "demographics-population.json")
    if os.path.exists(pop_path):
        with open(pop_path) as f:
            pop_json = json.load(f)
        pop_lookup = {}
        for entity, entries in pop_json.items():
            for e in entries:
                pop_lookup[(entity, e["year"])] = e["value"]
    else:
        raise FileNotFoundError("demographics-population.json must be generated first (run population transform)")

    gdp_raw = defaultdict(dict)  # {geo: {year: gdp_millions}}

    for row in read_csv_iter(find_csv("36-10-0222")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue
        if row.get("Estimates", "") != "Gross domestic product at market prices":
            continue
        if row.get("Prices", "") != "Chained (2017) dollars":
            continue
        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue
        gdp_raw[geo][year] = val  # in millions

    # Compute per-capita and build years/entities format
    all_years = set()
    for geo in gdp_raw:
        all_years.update(gdp_raw[geo].keys())
    years_sorted = sorted(all_years)

    entities = {}
    for geo in PROVINCES_ORDERED:
        if geo not in gdp_raw:
            continue
        values = []
        for y in years_sorted:
            gdp_m = gdp_raw[geo].get(y)
            pop = pop_lookup.get((geo, y))
            if gdp_m is not None and pop and pop > 0:
                # GDP in millions * 1,000,000 / population
                values.append(round(gdp_m * 1_000_000 / pop))
            else:
                values.append(None)
        entities[geo] = values

    save_json("economy-gdp-per-capita.json", {"years": [str(y) for y in years_sorted], "entities": entities})


def transform_median_wages():
    """14-10-0064 -> economy-median-weekly-wages.json
    Filter: Wages="Median weekly wage rate", Gender="Total - Gender",
            Type of work="Both full- and part-time employees"
    """
    print("  [transform] 14-10-0064: Median weekly wages")
    data = defaultdict(list)

    for row in read_csv_iter(find_csv("14-10-0064")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue
        if row.get("Wages", "") != "Median weekly wage rate":
            continue
        if row.get("Gender", "") != "Total - Gender":
            continue
        if row.get("Type of work", "") != "Both full- and part-time employees":
            continue
        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue
        naics = row.get("North American Industry Classification System (NAICS)", "")
        if naics and naics != "Total employees, all industries":
            continue
        data[geo].append({"year": year, "value": round(val, 2)})

    save_json("economy-median-weekly-wages.json", build_result(data))


def transform_employment():
    """14-10-0288 -> economy-employment.json
    Filter: Gender="Total - Gender", Statistics="Estimate",
            Class of worker in {Private sector employees, Public sector employees}
    Format: {dates: [...], provinces: {name: {private: [...], public: [...]}}}
    """
    print("  [transform] 14-10-0288: Employment by sector")

    province_data = defaultdict(lambda: {"private": {}, "public": {}})
    all_dates = set()

    for row in read_csv_iter(find_csv("14-10-0288")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue
        if row.get("Gender", "") != "Total - Gender":
            continue
        if row.get("Statistics", "") != "Estimate":
            continue
        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        ref_date = row["REF_DATE"]
        cow = row.get("Class of worker", "")

        if cow == "Private sector employees":
            province_data[geo]["private"][ref_date] = round(val, 1)
            all_dates.add(ref_date)
        elif cow == "Public sector employees":
            province_data[geo]["public"][ref_date] = round(val, 1)
            all_dates.add(ref_date)

    dates_sorted = sorted(all_dates)
    provinces = {}
    for geo in PROVINCES_ORDERED:
        if geo in province_data:
            pd = province_data[geo]
            provinces[geo] = {
                "private": [pd["private"].get(d) for d in dates_sorted],
                "public": [pd["public"].get(d) for d in dates_sorted],
            }

    save_json("economy-employment.json", {"dates": dates_sorted, "provinces": provinces})


def transform_crime_severity():
    """35-10-0026 -> crime-severity-index.json + crime-breakdown.json
    Filter: Statistics column for exact CSI type names
    """
    print("  [transform] 35-10-0026: Crime Severity Index")

    csi_total = defaultdict(dict)
    csi_violent = defaultdict(list)
    csi_nonviolent = defaultdict(list)
    all_years = set()

    for row in read_csv_iter(find_csv("35-10-0026")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue
        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue
        stat = row.get("Statistics", "")

        if stat == "Crime severity index":
            csi_total[geo][year] = round(val, 2)
            all_years.add(year)
        elif stat == "Violent crime severity index":
            csi_violent[geo].append({"year": year, "value": round(val, 2)})
        elif stat == "Non-violent crime severity index":
            csi_nonviolent[geo].append({"year": year, "value": round(val, 2)})

    years_sorted = sorted(all_years)
    entities = {}
    for geo in PROVINCES_ORDERED:
        if geo in csi_total:
            entities[geo] = [csi_total[geo].get(y) for y in years_sorted]

    save_json("crime-severity-index.json", {"years": years_sorted, "entities": entities})

    breakdown = {"violent": {}, "nonviolent": {}}
    for geo in PROVINCES_ORDERED:
        if geo in csi_violent:
            breakdown["violent"][geo] = sorted(csi_violent[geo], key=lambda x: x["year"])
        if geo in csi_nonviolent:
            breakdown["nonviolent"][geo] = sorted(csi_nonviolent[geo], key=lambda x: x["year"])

    save_json("crime-breakdown.json", breakdown)


def transform_homicide():
    """35-10-0068 -> crime-homicide-rate.json
    Filter: Homicides="Homicide rates per 100,000 population"
    """
    print("  [transform] 35-10-0068: Homicide rate")
    data = defaultdict(list)

    for row in read_csv_iter(find_csv("35-10-0068")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue
        if row.get("Homicides", "") != "Homicide rates per 100,000 population":
            continue
        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue
        data[geo].append({"year": year, "value": round(val, 2)})

    save_json("crime-homicide-rate.json", build_result(data))


def transform_population():
    """17-10-0005 -> demographics-population.json + demographics-population-growth.json
    Filter: Gender="Total - gender", Age group="All ages"
    Annual data (REF_DATE is just year)
    """
    print("  [transform] 17-10-0005: Population")

    pop_data = defaultdict(dict)

    for row in read_csv_iter(find_csv("17-10-0005")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue
        if row.get("Gender", "") != "Total - gender":
            continue
        age = row.get("Age group", "")
        if age != "All ages":
            continue
        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue
        pop_data[geo][year] = round(val)

    # Population JSON
    population = {}
    for geo in PROVINCES_ORDERED:
        if geo in pop_data:
            years = sorted(pop_data[geo].keys())
            population[geo] = [{"year": y, "value": pop_data[geo][y]} for y in years]

    save_json("demographics-population.json", population)

    # Growth JSON (year-over-year % change)
    growth = {}
    for geo in PROVINCES_ORDERED:
        if geo in pop_data:
            years = sorted(pop_data[geo].keys())
            growth_points = []
            for i in range(1, len(years)):
                prev = pop_data[geo][years[i - 1]]
                curr = pop_data[geo][years[i]]
                if prev and prev > 0:
                    pct = round((curr - prev) / prev * 100, 2)
                    growth_points.append({"year": years[i], "value": pct})
            growth[geo] = growth_points

    save_json("demographics-population-growth.json", growth)


def transform_immigration():
    """17-10-0014 -> demographics-international-immigration.json
    Filter: Type of migrant="Immigrants", Gender="Total - gender", Age group="All ages"
    """
    print("  [transform] 17-10-0014: International immigration")
    data = defaultdict(list)

    for row in read_csv_iter(find_csv("17-10-0014")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue
        if row.get("Type of migrant", "") != "Immigrants":
            continue
        if row.get("Gender", "") != "Total - gender":
            continue
        if row.get("Age group", "") != "All ages":
            continue
        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue
        data[geo].append({"year": year, "value": round(val)})

    save_json("demographics-international-immigration.json", build_result(data))


def transform_interprovincial_migration():
    """17-10-0045 -> demographics-interprovincial-migration.json
    This table has origin-destination pairs. Net migration = (in to province) - (out from province).
    Format: {entity: [{year, value}, ...]} (no Canada entry)
    """
    print("  [transform] 17-10-0045: Interprovincial migration")

    # Collect: for each province, sum inflows (as destination) minus outflows (as origin)
    # GEO = "Province, province of origin", destination col = "Province, province of destination"
    inflows = defaultdict(lambda: defaultdict(float))   # {province: {year: total_in}}
    outflows = defaultdict(lambda: defaultdict(float))  # {province: {year: total_out}}

    dest_col = None
    for row in read_csv_iter(find_csv("17-10-0045")):
        # Find the destination column name (has newline in it)
        if dest_col is None:
            for k in row.keys():
                if "destination" in k.lower():
                    dest_col = k
                    break

        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue

        ref_date = row["REF_DATE"]
        year = parse_year(ref_date)
        if year is None:
            continue

        # Parse origin province from GEO
        origin_raw = row["GEO"].replace(", province of origin", "").strip()
        origin = normalize_geo(origin_raw)

        # Parse destination province
        dest_raw = row.get(dest_col, "").replace(", province of destination", "").strip()
        dest = normalize_geo(dest_raw)

        # For quarterly data, use fiscal year (sum quarters)
        if origin and origin != "Canada":
            outflows[origin][year] += val
        if dest and dest != "Canada":
            inflows[dest][year] += val

    # Compute net migration
    all_provinces = set(list(inflows.keys()) + list(outflows.keys()))
    result = {}
    for geo in PROVINCES_ORDERED:
        if geo == "Canada":
            continue
        if geo in all_provinces:
            all_years = sorted(set(list(inflows[geo].keys()) + list(outflows[geo].keys())))
            entries = []
            for y in all_years:
                net = round(inflows[geo].get(y, 0) - outflows[geo].get(y, 0))
                entries.append({"year": y, "value": net})
            result[geo] = entries

    save_json("demographics-interprovincial-migration.json", result)


def transform_nhpi():
    """18-10-0205 -> housing-new-price-index.json
    Filter: New housing price indexes="Total (house and land)"
    Monthly data averaged to annual.
    """
    print("  [transform] 18-10-0205: New Housing Price Index")
    monthly_data = defaultdict(lambda: defaultdict(list))

    for row in read_csv_iter(find_csv("18-10-0205")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue
        if row.get("New housing price indexes", "") != "Total (house and land)":
            continue
        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue
        monthly_data[geo][year].append(val)

    result = {}
    for geo in PROVINCES_ORDERED:
        if geo in monthly_data:
            years = sorted(monthly_data[geo].keys())
            result[geo] = [
                {"year": y, "value": round(sum(monthly_data[geo][y]) / len(monthly_data[geo][y]), 1)}
                for y in years
            ]

    save_json("housing-new-price-index.json", result)


def transform_housing_starts():
    """34-10-0135 -> housing-starts.json
    Filter: Housing estimates="Housing starts", Type of unit="Total units",
            Seasonal adjustment="Unadjusted"
    Monthly data summed to annual.
    """
    print("  [transform] 34-10-0135: Housing starts")
    monthly_data = defaultdict(lambda: defaultdict(float))

    for row in read_csv_iter(find_csv("34-10-0135")):
        geo = normalize_geo(row["GEO"])
        if not geo:
            continue
        if row.get("Housing estimates", "") != "Housing starts":
            continue
        if row.get("Type of unit", "") != "Total units":
            continue
        if row.get("Seasonal adjustment", "") != "Unadjusted":
            continue
        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue
        monthly_data[geo][year] += val

    result = {}
    for geo in PROVINCES_ORDERED:
        if geo in monthly_data:
            years = sorted(monthly_data[geo].keys())
            result[geo] = [{"year": y, "value": round(monthly_data[geo][y])} for y in years]

    save_json("housing-starts.json", result)


def transform_government_revenue_spending():
    """36-10-0450 -> fiscal-government-revenue.json + fiscal-government-spending.json
    Columns: Levels of government, Estimates
    Filter: Provincial data by "Provincial and territorial general governments" level,
            Federal by "Federal general government"
    """
    print("  [transform] 36-10-0450: Government revenue & spending")

    revenue = defaultdict(dict)
    spending = defaultdict(dict)

    for row in read_csv_iter(find_csv("36-10-0450")):
        level = row.get("Levels of government", "")
        estimates = row.get("Estimates", "").lower()
        geo_raw = row["GEO"]

        # For federal: GEO="Canada", Level="Federal general government"
        # For provinces: GEO=province, Level="Provincial and territorial general governments"
        if level == "Federal general government" and geo_raw.strip() == "Canada":
            geo = "Federal"
        elif level == "Provincial and territorial general governments":
            geo = normalize_geo(geo_raw)
            if not geo or geo == "Canada":
                continue
        else:
            continue

        val = parse_float(row.get("VALUE", ""))
        if val is None:
            continue
        year = parse_year(row["REF_DATE"])
        if year is None:
            continue

        if "revenue" in estimates:
            revenue[geo][year] = round(val)
        elif "expenditure" in estimates and "final" not in estimates:
            spending[geo][year] = round(val)

    for geo_set, filename in [(revenue, "fiscal-government-revenue.json"),
                               (spending, "fiscal-government-spending.json")]:
        result = {}
        all_geos = ["Federal"] + [g for g in PROVINCES_ORDERED if g != "Canada"]
        for geo in all_geos:
            if geo in geo_set:
                years = sorted(geo_set[geo].keys())
                result[geo] = [{"year": y, "value": geo_set[geo][y]} for y in years]
        save_json(filename, result)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TRANSFORMS = [
    # Population must run first (GDP per-capita depends on it)
    transform_population,
    transform_gdp_per_capita,
    transform_median_wages,
    transform_employment,
    transform_crime_severity,
    transform_homicide,
    transform_immigration,
    transform_interprovincial_migration,
    transform_nhpi,
    transform_housing_starts,
    transform_government_revenue_spending,
    # NOTE: rental vacancy (34-10-0127) is CMA-level only, not provincial.
    # housing-rental-vacancy-rate.json is maintained manually.
    # NOTE: fiscal-deficit.json and fiscal-net-debt.json are from Dept of Finance
    # Fiscal Reference Tables, maintained manually.
]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print("=== Transforming data ===\n")

    success = 0
    failed = 0

    for fn in TRANSFORMS:
        try:
            fn()
            success += 1
        except Exception as e:
            print(f"    [ERROR] {fn.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\nDone: {success} transforms succeeded, {failed} failed")

    # Note manual data files
    print("\nManual data files (not auto-generated):")
    print("  - housing-rental-vacancy-rate.json (CMHC, CMA-level aggregated)")
    print("  - fiscal-deficit.json (Dept of Finance FRT)")
    print("  - fiscal-net-debt.json (Dept of Finance FRT)")

    if failed:
        print("\nWARNING: Some transforms failed. Check errors above.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
