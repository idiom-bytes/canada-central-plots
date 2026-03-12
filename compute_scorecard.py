#!/usr/bin/env python3
"""Compute scorecard data from individual dashboard JSON files."""
import json
import os

DATA_DIR = "data"

PROVINCES = [
    "Ontario", "Quebec", "British Columbia", "Alberta",
    "Manitoba", "Saskatchewan", "Nova Scotia", "New Brunswick",
    "Newfoundland & Labrador", "Prince Edward Island"
]

PROVINCE_ABBREV = {
    "Canada": "CAN", "Ontario": "ON", "Quebec": "QC",
    "British Columbia": "BC", "Alberta": "AB", "Manitoba": "MB",
    "Saskatchewan": "SK", "Nova Scotia": "NS", "New Brunswick": "NB",
    "Newfoundland & Labrador": "NL", "Prince Edward Island": "PE"
}

# Name mapping for files that use "Newfoundland and Labrador"
NL_ALT = "Newfoundland and Labrador"


def load_json(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)


def get_latest_values_yearlist(data, n_years=5):
    """For {years: [...], entities: {name: [values]}} format."""
    years = data["years"]
    result = {}
    for name, values in data["entities"].items():
        # Get last n_years non-null values
        pairs = [(y, v) for y, v in zip(years, values) if v is not None]
        result[name] = pairs[-n_years:] if len(pairs) >= n_years else pairs
    return result


def get_latest_values_nested(data, n_years=5):
    """For {name: [{year, value}, ...]} format."""
    result = {}
    for name, entries in data.items():
        pairs = [(e["year"], e["value"]) for e in entries if e["value"] is not None]
        mapped_name = "Newfoundland & Labrador" if name == NL_ALT else name
        result[mapped_name] = pairs[-n_years:] if len(pairs) >= n_years else pairs
    return result


def compute_trend(values, polarity):
    """Compare 3yr avg to prior 2yr avg. Returns 'improving', 'stable', 'declining'."""
    if len(values) < 5:
        return "stable"
    recent_3 = [v for _, v in values[-3:]]
    prior_2 = [v for _, v in values[-5:-3]]
    avg_recent = sum(recent_3) / len(recent_3)
    avg_prior = sum(prior_2) / len(prior_2)
    if avg_prior == 0:
        return "stable"
    pct_change = (avg_recent - avg_prior) / abs(avg_prior) * 100
    threshold = 5
    if polarity == "higher_better":
        if pct_change > threshold:
            return "improving"
        elif pct_change < -threshold:
            return "declining"
    else:  # lower_better
        if pct_change < -threshold:
            return "improving"
        elif pct_change > threshold:
            return "declining"
    return "stable"


def assign_grades(province_values, polarity):
    """Rank provinces and assign A/B/C/D grades."""
    # Sort by value
    items = [(name, val) for name, val in province_values.items()]
    reverse = (polarity == "higher_better")
    items.sort(key=lambda x: x[1], reverse=reverse)
    grades = {}
    for rank, (name, val) in enumerate(items, 1):
        if rank <= 2:
            grade = "A"
        elif rank <= 5:
            grade = "B"
        elif rank <= 8:
            grade = "C"
        else:
            grade = "D"
        grades[name] = {"grade": grade, "rank": rank}
    return grades


def compute_per_capita(raw_data, pop_data, multiplier=1, fiscal_year=False):
    """Compute per-capita values. Returns {name: [(year, per_capita_value), ...]}."""
    result = {}
    for name in list(raw_data.keys()):
        pop_name = name
        if name == "Federal":
            pop_name = "Canada"
        if name == NL_ALT:
            pop_name = "Newfoundland & Labrador"
        if pop_name not in pop_data:
            continue

        pop_lookup = {e["year"]: e["value"] for e in pop_data[pop_name]}
        pairs = []
        for year, value in raw_data[name]:
            cal_year = year
            if fiscal_year and isinstance(year, str) and "-" in year:
                cal_year = int(year.split("-")[0])
            if cal_year in pop_lookup and pop_lookup[cal_year] > 0:
                pc = (value * multiplier) / pop_lookup[cal_year]
                pairs.append((year, round(pc, 2)))
        display_name = "Canada" if name == "Federal" else name
        if name == NL_ALT:
            display_name = "Newfoundland & Labrador"
        result[display_name] = pairs
    return result


def build_metric(name, vertical, unit, fmt, polarity, dashboard, values_dict, n_recent=5):
    """Build a single metric entry for the scorecard."""
    metric = {
        "id": dashboard.replace(".html", ""),
        "name": name,
        "vertical": vertical,
        "unit": unit,
        "format": fmt,
        "polarity": polarity,
        "dashboard": dashboard,
        "values": {}
    }

    # Get latest value and trend for each entity
    province_latest = {}
    for entity_name, pairs in values_dict.items():
        if not pairs:
            continue
        latest_year, latest_val = pairs[-1]
        trend = compute_trend(pairs[-n_recent:], polarity)
        entry = {"value": latest_val, "year": str(latest_year), "trend": trend}
        metric["values"][entity_name] = entry
        if entity_name in PROVINCES:
            province_latest[entity_name] = latest_val

    # Assign grades to provinces only
    if province_latest:
        grades = assign_grades(province_latest, polarity)
        for prov, grade_info in grades.items():
            if prov in metric["values"]:
                metric["values"][prov].update(grade_info)

    # Set latest_year from Canada/Federal
    if "Canada" in metric["values"]:
        metric["latest_year"] = metric["values"]["Canada"]["year"]
    elif province_latest:
        first_prov = list(province_latest.keys())[0]
        metric["latest_year"] = metric["values"][first_prov]["year"]

    return metric


def main():
    pop_data = load_json("population.json")

    metrics = []

    # 1. GDP per Capita
    gdp = load_json("gdp_per_capita.json")
    gdp_vals = get_latest_values_yearlist(gdp, 7)
    metrics.append(build_metric(
        "GDP per Capita", "Economy", "$", "currency",
        "higher_better", "gdp_per_capita.html", gdp_vals
    ))

    # 2. Median Weekly Wages
    wages = load_json("median_wages.json")
    wage_vals = get_latest_values_nested(wages, 7)
    metrics.append(build_metric(
        "Median Weekly Wages", "Economy", "$", "currency",
        "higher_better", "median_wages.html", wage_vals
    ))

    # 3. Crime Severity Index
    csi = load_json("crime_severity.json")
    csi_vals = get_latest_values_yearlist(csi, 7)
    metrics.append(build_metric(
        "Crime Severity Index", "Crime", "", "number",
        "lower_better", "crime_severity.html", csi_vals
    ))

    # 4. Homicide Rate
    hom = load_json("homicide_rate.json")
    hom_vals = get_latest_values_nested(hom, 7)
    metrics.append(build_metric(
        "Homicide Rate", "Crime", "per 100K", "decimal",
        "lower_better", "homicide_rate.html", hom_vals
    ))

    # 5. Population Growth
    popg = load_json("population_growth.json")
    popg_vals = get_latest_values_yearlist(popg, 7)
    metrics.append(build_metric(
        "Population Growth", "Demographics", "%", "percent",
        "higher_better", "population_growth.html", popg_vals
    ))

    # 6. Housing Starts per 10K Pop
    hs = load_json("housing_starts.json")
    hs_nested = get_latest_values_nested(hs, 7)
    hs_pc = compute_per_capita(
        {name: pairs for name, pairs in hs_nested.items()},
        pop_data, multiplier=10000
    )
    metrics.append(build_metric(
        "Housing Starts per 10K", "Housing", "units", "decimal",
        "higher_better", "housing.html", hs_pc
    ))

    # 7. Rental Vacancy Rate
    rv = load_json("rental_vacancy.json")
    rv_vals = get_latest_values_nested(rv, 7)
    metrics.append(build_metric(
        "Rental Vacancy Rate", "Housing", "%", "percent",
        "higher_better", "rental_vacancy.html", rv_vals
    ))

    # 8. International Migration per 1K Pop
    imm = load_json("international_migration.json")
    imm_nested = get_latest_values_nested(imm, 7)
    imm_pc = compute_per_capita(
        {name: pairs for name, pairs in imm_nested.items()},
        pop_data, multiplier=1000
    )
    metrics.append(build_metric(
        "Immigration per 1K Pop", "Demographics", "", "decimal",
        "higher_better", "international_migration.html", imm_pc
    ))

    # 9. Deficit/Surplus per Capita ($ billions -> $ per capita)
    deficit = load_json("deficit.json")
    deficit_vals = {}
    years = deficit["years"]
    for name, values in deficit["entities"].items():
        pairs = [(y, v) for y, v in zip(years, values) if v is not None]
        deficit_vals[name] = pairs[-7:]
    deficit_pc = compute_per_capita(deficit_vals, pop_data,
                                     multiplier=1_000_000_000, fiscal_year=True)
    metrics.append(build_metric(
        "Deficit per Capita", "Fiscal", "$", "currency_signed",
        "higher_better", "deficit.html", deficit_pc
    ))

    # 10. Net Debt per Capita ($ billions -> $ per capita)
    ndebt = load_json("net_debt.json")
    ndebt_vals = {}
    years = ndebt["years"]
    for name, values in ndebt["entities"].items():
        pairs = [(y, v) for y, v in zip(years, values) if v is not None]
        ndebt_vals[name] = pairs[-7:]
    ndebt_pc = compute_per_capita(ndebt_vals, pop_data,
                                   multiplier=1_000_000_000, fiscal_year=True)
    metrics.append(build_metric(
        "Net Debt per Capita", "Fiscal", "$", "currency",
        "lower_better", "net_debt.html", ndebt_pc
    ))

    # Compute composite scores
    composites = {}
    grade_to_num = {"A": 4, "B": 3, "C": 2, "D": 1}
    for prov in PROVINCES:
        grades = []
        for m in metrics:
            if prov in m["values"] and "grade" in m["values"][prov]:
                grades.append(grade_to_num[m["values"][prov]["grade"]])
        if grades:
            avg = sum(grades) / len(grades)
            if avg >= 3.5:
                comp_grade = "A"
            elif avg >= 2.5:
                comp_grade = "B"
            elif avg >= 1.5:
                comp_grade = "C"
            else:
                comp_grade = "D"
            composites[prov] = {"score": round(avg, 1), "grade": comp_grade}

    scorecard = {
        "metrics": metrics,
        "provinces": PROVINCES,
        "province_abbrev": PROVINCE_ABBREV,
        "composites": composites
    }

    with open(os.path.join(DATA_DIR, "scorecard_data.json"), "w") as f:
        json.dump(scorecard, f, indent=2)

    print("Scorecard data written to data/scorecard_data.json")
    print(f"\nComposite scores:")
    ranked = sorted(composites.items(), key=lambda x: x[1]["score"], reverse=True)
    for prov, comp in ranked:
        print(f"  {PROVINCE_ABBREV[prov]:>3} {prov:<28} {comp['grade']} ({comp['score']})")


if __name__ == "__main__":
    main()
