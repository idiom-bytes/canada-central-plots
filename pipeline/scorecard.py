"""
Compute scorecard_data.json from the transformed data files.

15 metrics across 5 verticals (3 per vertical):
  Fiscal:       Deficit/Capita, Net Debt/Capita, Revenue/Capita
  Economy:      GDP/Capita, Median Wages, Employment Rate
  Housing:      Starts/10K, Price Index, Vacancy Rate
  Crime:        CSI, Violent CSI, Homicide Rate
  Demographics: Pop Growth, Immigration/1K, Interprovincial Migration/1K

Grading: A (rank 1-2), B (rank 3-5), C (rank 6-8), D (rank 9-10)
Trend:   3yr avg vs prior 2yr avg, >5% change threshold

Usage: python pipeline/scorecard.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_DIR, PROVINCES_ORDERED

PROVINCES = [p for p in PROVINCES_ORDERED if p != "Canada"]


def load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    with open(path) as f:
        return json.load(f)


def get_latest_value_nested(data: dict, entity: str, n_years: int = 1) -> list[float]:
    """Get latest n values from {entity: [{year, value}, ...]} format."""
    if entity not in data:
        return []
    entries = sorted(data[entity], key=lambda x: x["year"], reverse=True)
    return [e["value"] for e in entries[:n_years] if e["value"] is not None]


def get_latest_value_yearlist(data: dict, entity: str, n_years: int = 1) -> list[float]:
    """Get latest n values from {years: [...], entities: {name: [values]}} format."""
    if entity not in data.get("entities", {}):
        return []
    values = data["entities"][entity]
    # Get last n non-None values
    result = []
    for v in reversed(values):
        if v is not None and len(result) < n_years:
            result.append(v)
    return result


def compute_trend(values_recent: list[float], values_prior: list[float]) -> str:
    """Compute trend: up/down/stable based on 5% threshold."""
    if not values_recent or not values_prior:
        return "stable"
    avg_recent = sum(values_recent) / len(values_recent)
    avg_prior = sum(values_prior) / len(values_prior)
    if avg_prior == 0:
        return "stable"
    pct_change = (avg_recent - avg_prior) / abs(avg_prior) * 100
    if pct_change > 5:
        return "up"
    elif pct_change < -5:
        return "down"
    return "stable"


def assign_grades(province_values: dict[str, float], invert: bool = False) -> dict[str, str]:
    """Assign grades based on ranking. invert=True means lower is better."""
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


def compute_per_capita(value: float, population: float) -> float:
    """Compute per-capita value."""
    if population and population > 0:
        return round(value / population, 2)
    return 0


def build_metric(
    name: str,
    vertical: str,
    province_values: dict[str, float],
    canada_value: float | None,
    invert: bool = False,
    unit: str = "",
    trends: dict[str, str] | None = None,
) -> dict:
    """Build a single metric entry for the scorecard."""
    grades = assign_grades(province_values, invert=invert)

    provinces_data = {}
    for p in PROVINCES:
        val = province_values.get(p)
        provinces_data[p] = {
            "value": val,
            "grade": grades.get(p, "C"),
            "trend": (trends or {}).get(p, "stable"),
        }

    return {
        "name": name,
        "vertical": vertical,
        "unit": unit,
        "invert": invert,
        "canada": canada_value,
        "provinces": provinces_data,
    }


def main():
    print("=== Computing scorecard ===\n")

    # Load all data files
    population = load_json("demographics-population.json")
    gdp = load_json("economy-gdp-per-capita.json")
    wages = load_json("economy-median-weekly-wages.json")
    employment = load_json("economy-employment.json")
    csi = load_json("crime-severity-index.json")
    crime_bd = load_json("crime-breakdown.json")
    homicide = load_json("crime-homicide-rate.json")
    pop_growth = load_json("demographics-population-growth.json")
    immigration = load_json("demographics-international-immigration.json")
    interp_mig = load_json("demographics-interprovincial-migration.json")
    deficit = load_json("fiscal-deficit.json")
    net_debt = load_json("fiscal-net-debt.json")
    gov_revenue = load_json("fiscal-government-revenue.json")
    housing_starts = load_json("housing-starts.json")
    nhpi = load_json("housing-new-price-index.json")
    vacancy = load_json("housing-rental-vacancy-rate.json")

    # Get latest population for per-capita calcs
    pop_latest = {}
    for entity in PROVINCES_ORDERED:
        vals = get_latest_value_nested(population, entity, 1)
        if vals:
            pop_latest[entity] = vals[0]

    metrics = []

    # --- FISCAL ---
    # 1. Deficit per capita (invert: lower deficit = better)
    def fiscal_entity(name):
        return "Federal" if name == "Canada" else name

    deficit_pc = {}
    deficit_trends = {}
    BILLION = 1_000_000_000
    for p in PROVINCES:
        fe = fiscal_entity(p)
        recent = get_latest_value_yearlist(deficit, fe, 3)
        prior = get_latest_value_yearlist(deficit, fe, 5)
        if recent and p in pop_latest:
            deficit_pc[p] = round(recent[0] * BILLION / pop_latest[p], 2)
            deficit_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_def_recent = get_latest_value_yearlist(deficit, "Federal", 1)
    canada_deficit = round(canada_def_recent[0] * BILLION / pop_latest.get("Canada", 1), 2) if canada_def_recent else None

    metrics.append(build_metric("Deficit per Capita", "fiscal", deficit_pc, canada_deficit, invert=True, unit="$", trends=deficit_trends))

    # 2. Net Debt per capita (invert: lower = better)
    debt_pc = {}
    debt_trends = {}
    for p in PROVINCES:
        fe = fiscal_entity(p)
        recent = get_latest_value_yearlist(net_debt, fe, 3)
        prior = get_latest_value_yearlist(net_debt, fe, 5)
        if recent and p in pop_latest:
            debt_pc[p] = round(recent[0] * BILLION / pop_latest[p], 2)
            debt_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_debt_recent = get_latest_value_yearlist(net_debt, "Federal", 1)
    canada_debt = round(canada_debt_recent[0] * BILLION / pop_latest.get("Canada", 1), 2) if canada_debt_recent else None

    metrics.append(build_metric("Net Debt per Capita", "fiscal", debt_pc, canada_debt, invert=True, unit="$", trends=debt_trends))

    # 3. Revenue per capita (revenue is in millions)
    MILLION = 1_000_000
    rev_pc = {}
    rev_trends = {}
    for p in PROVINCES:
        fe = fiscal_entity(p)
        recent = get_latest_value_nested(gov_revenue, fe, 3)
        prior = get_latest_value_nested(gov_revenue, fe, 5)
        if recent and p in pop_latest:
            rev_pc[p] = round(recent[0] * MILLION / pop_latest[p], 2)
            rev_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_rev = get_latest_value_nested(gov_revenue, "Federal", 1)
    canada_rev_pc = round(canada_rev[0] * MILLION / pop_latest.get("Canada", 1), 2) if canada_rev else None

    metrics.append(build_metric("Revenue per Capita", "fiscal", rev_pc, canada_rev_pc, invert=False, unit="$", trends=rev_trends))

    # --- ECONOMY ---
    # 4. GDP per capita (years/entities format)
    gdp_vals = {}
    gdp_trends = {}
    for p in PROVINCES:
        recent = get_latest_value_yearlist(gdp, p, 3)
        prior = get_latest_value_yearlist(gdp, p, 5)
        if recent:
            gdp_vals[p] = recent[0]
            gdp_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_gdp = get_latest_value_yearlist(gdp, "Canada", 1)

    metrics.append(build_metric("GDP per Capita", "economy", gdp_vals, canada_gdp[0] if canada_gdp else None, unit="$", trends=gdp_trends))

    # 5. Median Weekly Wages
    wage_vals = {}
    wage_trends = {}
    for p in PROVINCES:
        recent = get_latest_value_nested(wages, p, 3)
        prior = get_latest_value_nested(wages, p, 5)
        if recent:
            wage_vals[p] = recent[0]
            wage_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_wages = get_latest_value_nested(wages, "Canada", 1)

    metrics.append(build_metric("Median Weekly Wages", "economy", wage_vals, canada_wages[0] if canada_wages else None, unit="$", trends=wage_trends))

    # 6. Employment Rate (private + public total, per capita)
    emp_vals = {}
    emp_trends = {}
    dates = employment.get("dates", [])
    for p in PROVINCES:
        pdata = employment.get("provinces", {}).get(p, {})
        priv = pdata.get("private", [])
        pub = pdata.get("public", [])
        if priv and pub:
            # Get last 12 months average
            recent_total = []
            for i in range(max(0, len(priv) - 12), len(priv)):
                pv = priv[i] if i < len(priv) and priv[i] is not None else 0
                pu = pub[i] if i < len(pub) and pub[i] is not None else 0
                recent_total.append(pv + pu)
            if recent_total and p in pop_latest:
                avg = sum(recent_total) / len(recent_total)
                # Employment rate per 1000 people (avg is in thousands, pop is persons)
                emp_vals[p] = round(avg * 1000 / pop_latest[p] * 1000, 1)

                # Trend: compare last 12mo avg to prior 12mo avg
                prior_total = []
                start = max(0, len(priv) - 24)
                end = max(0, len(priv) - 12)
                for i in range(start, end):
                    pv = priv[i] if i < len(priv) and priv[i] is not None else 0
                    pu = pub[i] if i < len(pub) and pub[i] is not None else 0
                    prior_total.append(pv + pu)
                if prior_total:
                    emp_trends[p] = compute_trend(recent_total[-3:], prior_total[-3:])

    canada_emp = employment.get("provinces", {}).get("Canada", {})
    canada_emp_val = None
    if canada_emp and pop_latest.get("Canada"):
        priv = canada_emp.get("private", [])
        pub = canada_emp.get("public", [])
        if priv and pub:
            recent = [
                (priv[i] or 0) + (pub[i] or 0)
                for i in range(max(0, len(priv) - 12), len(priv))
            ]
            if recent:
                canada_emp_val = round(sum(recent) / len(recent) * 1000 / pop_latest["Canada"] * 1000, 1)

    metrics.append(build_metric("Employment Rate", "economy", emp_vals, canada_emp_val, unit="per 1K", trends=emp_trends))

    # --- HOUSING ---
    # 7. Housing Starts per 10K
    starts_vals = {}
    starts_trends = {}
    for p in PROVINCES:
        recent = get_latest_value_nested(housing_starts, p, 3)
        prior = get_latest_value_nested(housing_starts, p, 5)
        if recent and p in pop_latest:
            starts_vals[p] = round(recent[0] / pop_latest[p] * 10000, 1)
            starts_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_starts = get_latest_value_nested(housing_starts, "Canada", 1)
    canada_starts_pc = round(canada_starts[0] / pop_latest["Canada"] * 10000, 1) if canada_starts and pop_latest.get("Canada") else None

    metrics.append(build_metric("Housing Starts per 10K", "housing", starts_vals, canada_starts_pc, unit="starts", trends=starts_trends))

    # 8. New Housing Price Index (invert: lower = more affordable = better)
    nhpi_vals = {}
    nhpi_trends = {}
    for p in PROVINCES:
        # NHPI may use "Newfoundland and Labrador" not "&"
        key = p
        if p not in nhpi:
            alt = p.replace("&", "and")
            if alt in nhpi:
                key = alt
        recent = get_latest_value_nested(nhpi, key, 3)
        prior = get_latest_value_nested(nhpi, key, 5)
        if recent:
            nhpi_vals[p] = recent[0]
            nhpi_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_nhpi = get_latest_value_nested(nhpi, "Canada", 1)

    metrics.append(build_metric("Housing Price Index", "housing", nhpi_vals, canada_nhpi[0] if canada_nhpi else None, invert=True, unit="index", trends=nhpi_trends))

    # 9. Rental Vacancy Rate (higher = better for renters)
    vac_vals = {}
    vac_trends = {}
    for p in PROVINCES:
        recent = get_latest_value_nested(vacancy, p, 3)
        prior = get_latest_value_nested(vacancy, p, 5)
        if recent:
            vac_vals[p] = recent[0]
            vac_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_vac = get_latest_value_nested(vacancy, "Canada", 1)

    metrics.append(build_metric("Rental Vacancy Rate", "housing", vac_vals, canada_vac[0] if canada_vac else None, invert=False, unit="%", trends=vac_trends))

    # --- CRIME ---
    # 10. Crime Severity Index (invert: lower = better)
    csi_vals = {}
    csi_trends = {}
    for p in PROVINCES:
        recent = get_latest_value_yearlist(csi, p, 3)
        prior = get_latest_value_yearlist(csi, p, 5)
        if recent:
            csi_vals[p] = recent[0]
            csi_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_csi = get_latest_value_yearlist(csi, "Canada", 1)

    metrics.append(build_metric("Crime Severity Index", "crime", csi_vals, canada_csi[0] if canada_csi else None, invert=True, unit="index", trends=csi_trends))

    # 11. Violent CSI (invert: lower = better)
    vcsi_vals = {}
    vcsi_trends = {}
    violent = crime_bd.get("violent", {})
    for p in PROVINCES:
        recent = get_latest_value_nested(violent, p, 3)
        prior = get_latest_value_nested(violent, p, 5)
        if recent:
            vcsi_vals[p] = recent[0]
            vcsi_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_vcsi = get_latest_value_nested(violent, "Canada", 1)

    metrics.append(build_metric("Violent CSI", "crime", vcsi_vals, canada_vcsi[0] if canada_vcsi else None, invert=True, unit="index", trends=vcsi_trends))

    # 12. Homicide Rate (invert: lower = better)
    hom_vals = {}
    hom_trends = {}
    for p in PROVINCES:
        recent = get_latest_value_nested(homicide, p, 3)
        prior = get_latest_value_nested(homicide, p, 5)
        if recent:
            hom_vals[p] = recent[0]
            hom_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_hom = get_latest_value_nested(homicide, "Canada", 1)

    metrics.append(build_metric("Homicide Rate", "crime", hom_vals, canada_hom[0] if canada_hom else None, invert=True, unit="per 100K", trends=hom_trends))

    # --- DEMOGRAPHICS ---
    # 13. Population Growth (higher = better)
    pg_vals = {}
    pg_trends = {}
    for p in PROVINCES:
        recent = get_latest_value_nested(pop_growth, p, 3)
        prior = get_latest_value_nested(pop_growth, p, 5)
        if recent:
            pg_vals[p] = recent[0]
            pg_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_pg = get_latest_value_nested(pop_growth, "Canada", 1)

    metrics.append(build_metric("Population Growth", "demographics", pg_vals, canada_pg[0] if canada_pg else None, unit="%", trends=pg_trends))

    # 14. International Immigration per 1K pop
    imm_vals = {}
    imm_trends = {}
    for p in PROVINCES:
        recent = get_latest_value_nested(immigration, p, 3)
        prior = get_latest_value_nested(immigration, p, 5)
        if recent and p in pop_latest:
            imm_vals[p] = round(recent[0] / pop_latest[p] * 1000, 2)
            imm_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    canada_imm = get_latest_value_nested(immigration, "Canada", 1)
    canada_imm_pc = round(canada_imm[0] / pop_latest["Canada"] * 1000, 2) if canada_imm and pop_latest.get("Canada") else None

    metrics.append(build_metric("Immigration per 1K", "demographics", imm_vals, canada_imm_pc, unit="per 1K", trends=imm_trends))

    # 15. Interprovincial Migration per 1K (positive = gaining people = better)
    mig_vals = {}
    mig_trends = {}
    for p in PROVINCES:
        recent = get_latest_value_nested(interp_mig, p, 3)
        prior = get_latest_value_nested(interp_mig, p, 5)
        if recent and p in pop_latest:
            mig_vals[p] = round(recent[0] / pop_latest[p] * 1000, 2)
            mig_trends[p] = compute_trend(recent, prior[3:] if len(prior) >= 5 else prior[len(recent):])

    metrics.append(build_metric("Interprovincial Migration per 1K", "demographics", mig_vals, None, unit="per 1K", trends=mig_trends))

    # --- COMPOSITE SCORES ---
    # Average grade score per province (A=4, B=3, C=2, D=1)
    grade_scores = {"A": 4, "B": 3, "C": 2, "D": 1}
    composites = {}
    for p in PROVINCES:
        scores = []
        for m in metrics:
            g = m["provinces"].get(p, {}).get("grade")
            if g:
                scores.append(grade_scores[g])
        if scores:
            composites[p] = round(sum(scores) / len(scores), 2)

    # Build output
    scorecard = {
        "metrics": metrics,
        "composites": composites,
        "provinces": PROVINCES,
    }

    path = os.path.join(DATA_DIR, "scorecard_data.json")
    with open(path, "w") as f:
        json.dump(scorecard, f, indent=2)
    print(f"  -> scorecard_data.json ({len(metrics)} metrics, {len(PROVINCES)} provinces)")
    print("Done.")


if __name__ == "__main__":
    main()
