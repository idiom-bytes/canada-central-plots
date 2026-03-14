"""Transform data for the Food Insecurity report.

Sources:
  - StatCan 13-10-0835: Food insecurity by demographics (CCHS), 2018-2023, provinces
  - StatCan 13-10-0385: Household food security by living arrangement, 2015-2018, incl. territories
  - PROOF (U of T): National trend data 2011-2024, territory rates, CIS-based
  - Food Banks Canada HungerCount: Monthly food bank visits 2016-2025

Output: data/report-food-insecurity.json
"""
import csv
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transform import normalize_geo, find_csv, read_csv_iter
from config import DATA_DIR

def parse_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def main():
    result = {}

    # =========================================================================
    # 1. NATIONAL TREND — Food insecurity rate (% of persons), 2011-2024
    #    Source: PROOF / Canadian Income Survey + CCHS
    #    2011-2017 from CIS, 2018+ from CCHS (13-10-0835)
    # =========================================================================
    # Hardcoded from PROOF research — CIS-based estimates (persons in 10 provinces)
    # Note: CCHS and CIS use slightly different methodologies; we use CCHS from 2018+
    # where available since it's the StatCan official table.
    national_trend_hardcoded = {
        2011: 12.3,
        2012: 12.6,
        2013: 12.5,
        2014: 12.0,
        2015: 12.4,
        2016: 12.2,
        2017: 12.5,
        # 2018+ pulled from StatCan 13-10-0835 below
    }

    # Pull 2018-2023 from StatCan 13-10-0835
    national_trend_statcan = {}
    for row in read_csv_iter(find_csv("13-10-0835")):
        if (row["GEO"] == "Canada" and
            row["Demographic characteristics"] == "All persons" and
            row["Household food security status"] == "Food insecure" and
            row["Statistics"] == "Percentage of persons"):
            val = parse_float(row.get("VALUE"))
            if val is not None:
                year = int(row["REF_DATE"])
                national_trend_statcan[year] = val

    # Merge: use StatCan where available, PROOF for earlier years
    national_trend = []
    for year in sorted(set(list(national_trend_hardcoded.keys()) + list(national_trend_statcan.keys()))):
        val = national_trend_statcan.get(year, national_trend_hardcoded.get(year))
        if val is not None:
            national_trend.append({"year": year, "value": val})

    # Note: CCHS and CIS report slightly different rates for the same year
    # due to methodology. We use CCHS (13-10-0835) as primary from 2018+.
    # 2024 CCHS data not yet released; omitting to avoid mixing survey sources.

    result["national_trend"] = national_trend

    # =========================================================================
    # 2. PROVINCIAL RATES — by year, from StatCan 13-10-0835
    # =========================================================================
    provincial = defaultdict(list)
    for row in read_csv_iter(find_csv("13-10-0835")):
        if (row["Demographic characteristics"] == "All persons" and
            row["Household food security status"] == "Food insecure" and
            row["Statistics"] == "Percentage of persons"):
            geo = normalize_geo(row["GEO"])
            if not geo:
                continue
            val = parse_float(row.get("VALUE"))
            if val is not None:
                provincial[geo].append({"year": int(row["REF_DATE"]), "value": val})

    # Add territory data from PROOF/CIS (not in 13-10-0835)
    # 2023 CIS data from PROOF
    provincial["Nunavut"] = [
        {"year": 2017, "value": 57.0},
        {"year": 2018, "value": 57.0},  # interpolated
        {"year": 2021, "value": 46.1},
        {"year": 2022, "value": 46.1},
        {"year": 2023, "value": 58.1},
    ]
    provincial["Northwest Territories"] = [
        {"year": 2017, "value": 21.8},
        {"year": 2021, "value": 22.2},
        {"year": 2022, "value": 22.2},
        {"year": 2023, "value": 34.2},
    ]
    provincial["Yukon"] = [
        {"year": 2017, "value": 15.2},
        {"year": 2021, "value": 12.8},
        {"year": 2022, "value": 12.8},
        {"year": 2023, "value": 21.8},
    ]

    result["provincial"] = dict(provincial)

    # =========================================================================
    # 3. SEVERITY BREAKDOWN — Canada by year, from StatCan 13-10-0835
    # =========================================================================
    severity = defaultdict(dict)
    severity_map = {
        "Food insecure, marginal": "marginal",
        "Food insecure, moderate": "moderate",
        "Food insecure, severe": "severe",
    }
    for row in read_csv_iter(find_csv("13-10-0835")):
        if (row["GEO"] == "Canada" and
            row["Demographic characteristics"] == "All persons" and
            row["Statistics"] == "Percentage of persons" and
            row["Household food security status"] in severity_map):
            val = parse_float(row.get("VALUE"))
            if val is not None:
                year = int(row["REF_DATE"])
                key = severity_map[row["Household food security status"]]
                severity[year][key] = val

    result["severity"] = [
        {"year": y, **severity[y]} for y in sorted(severity)
    ]

    # =========================================================================
    # 4. DEMOGRAPHIC BREAKDOWN — Canada 2023 (latest), from StatCan 13-10-0835
    # =========================================================================
    demographics = {}
    target_demos = [
        "All persons",
        "Persons under 18 years",
        "Persons 18 to 64 years",
        "Persons 65 years and over",
        "Black",
        "Indigenous population",
        "South Asian",
        "Filipino",
        "Latin American",
        "Arab",
        "Chinese",
        "Not a visible minority nor Indigenous",
        "Visible minority population",
        "Recent immigrants (10 years or less) aged 15 years and over",
        "Persons aged 15 years and over born in Canada",
    ]
    # Friendly labels for display
    demo_labels = {
        "All persons": "All Canadians",
        "Persons under 18 years": "Children (under 18)",
        "Persons 18 to 64 years": "Working age (18-64)",
        "Persons 65 years and over": "Seniors (65+)",
        "Black": "Black Canadians",
        "Indigenous population": "Indigenous peoples",
        "South Asian": "South Asian",
        "Filipino": "Filipino",
        "Latin American": "Latin American",
        "Arab": "Arab",
        "Chinese": "Chinese",
        "Not a visible minority nor Indigenous": "White / non-minority",
        "Visible minority population": "All visible minorities",
        "Recent immigrants (10 years or less) aged 15 years and over": "Recent immigrants (<10 yrs)",
        "Persons aged 15 years and over born in Canada": "Canadian-born",
    }

    for row in read_csv_iter(find_csv("13-10-0835")):
        if (row["REF_DATE"] == "2023" and
            row["GEO"] == "Canada" and
            row["Household food security status"] == "Food insecure" and
            row["Statistics"] == "Percentage of persons" and
            row["Demographic characteristics"] in target_demos):
            val = parse_float(row.get("VALUE"))
            if val is not None:
                key = row["Demographic characteristics"]
                demographics[key] = {
                    "label": demo_labels.get(key, key),
                    "value": val,
                }

    result["demographics"] = demographics

    # =========================================================================
    # 5. FOOD BANK VISITS — from Food Banks Canada HungerCount (hardcoded)
    #    Monthly visits in March of each year
    # =========================================================================
    result["food_bank_visits"] = {
        "national_trend": [
            {"year": 2016, "value": 863000},
            {"year": 2017, "value": 890000},
            {"year": 2018, "value": 950000},
            {"year": 2019, "value": 1086280},
            # 2020: no HungerCount (COVID)
            {"year": 2021, "value": 1272580},
            {"year": 2022, "value": 1465721},
            {"year": 2023, "value": 1935911},
            {"year": 2024, "value": 2059636},
            {"year": 2025, "value": 2166000},
        ],
        "provincial_2025": [
            {"province": "Ontario", "visits": 763756, "children": 228689, "change_since_2019": 124.9},
            {"province": "Quebec", "visits": 746411, "children": 260419, "change_since_2019": 116.2},
            {"province": "British Columbia", "visits": 223340, "children": 68053, "change_since_2019": 79.1},
            {"province": "Alberta", "visits": 210541, "children": 75968, "change_since_2019": 134.4},
            {"province": "Manitoba", "visits": 64975, "children": 25047, "change_since_2019": 97.0},
            {"province": "Saskatchewan", "visits": 55310, "children": 20906, "change_since_2019": 48.6},
            {"province": "Nova Scotia", "visits": 43421, "children": 14023, "change_since_2019": 69.4},
            {"province": "New Brunswick", "visits": 32343, "children": 10781, "change_since_2019": 45.3},
            {"province": "Newfoundland & Labrador", "visits": 15422, "children": 4700, "change_since_2019": 44.1},
            {"province": "Prince Edward Island", "visits": 5350, "children": 1757, "change_since_2019": 80.8},
            {"province": "Territories", "visits": 4897, "children": 1428, "change_since_2019": None},
        ],
        "demographics_2025": {
            "children_pct": 33,
            "employed_pct": 19.4,
            "newcomers_pct": 34,
            "social_assistance_pct": 40,
            "seniors_pct": 8.3,
            "market_rent_pct": 70.4,
        },
    }

    # =========================================================================
    # 6. CHILDREN — food insecurity rate for children by province, 2023
    # =========================================================================
    children_provincial = {}
    for row in read_csv_iter(find_csv("13-10-0835")):
        if (row["REF_DATE"] == "2023" and
            row["Demographic characteristics"] == "Persons under 18 years" and
            row["Household food security status"] == "Food insecure" and
            row["Statistics"] == "Percentage of persons"):
            geo = normalize_geo(row["GEO"])
            if geo:
                val = parse_float(row.get("VALUE"))
                if val is not None:
                    children_provincial[geo] = val

    result["children_provincial_2023"] = children_provincial

    # =========================================================================
    # 7. BENCHMARKS & CONTEXT
    # =========================================================================
    result["benchmarks"] = {
        "healthcare_cost_per_person": {
            "food_secure": 1605,
            "marginal": 2161,
            "moderate": 2806,
            "severe": 3930,
            "source": "PROOF / ICES",
        },
        "housing_burden": {
            "lowest_income_pct_on_housing_2025": 66,
            "lowest_income_pct_on_housing_2021": 49,
            "source": "Statistics Canada / PROOF",
        },
        "food_bank_coverage": {
            "food_insecure_total": 10000000,
            "food_bank_users": 1200000,
            "coverage_pct": 12,
            "note": "Only 12% of food-insecure Canadians actually use food banks",
        },
        "lone_parent_2024": {
            "female_lone_parent_pct": 52.1,
            "source": "PROOF 2024",
        },
    }

    # =========================================================================
    # 8. METADATA
    # =========================================================================
    result["metadata"] = {
        "title": "A Nation That Can't Feed Its Children",
        "last_updated": "2025",
        "sources": [
            "Statistics Canada, Table 13-10-0835-01 (CCHS)",
            "Statistics Canada, Table 13-10-0385-01 (CCHS)",
            "PROOF - Food Insecurity Policy Research, University of Toronto",
            "Food Banks Canada, HungerCount 2025",
        ],
    }

    # Write output
    out_path = os.path.join(DATA_DIR, "report-food-insecurity.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Wrote {out_path}")


if __name__ == "__main__":
    main()
