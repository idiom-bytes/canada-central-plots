"""Fetch sector-specific data on doers vs. administrative overhead in Canadian public sector.

Three sectors, each analyzed using only its own data:
  1. Education  — StatCan 37-10-0065-01: K-12 school board expenditures (1973–2023)
                  Teacher salaries vs. administration vs. other operating costs
  2. Healthcare — CIHI NHEX open data (1975–2024):
                  Public health spending: clinical care vs. administration
                  SEPH 14-10-0220-01: employment in physician offices vs. hospitals vs. all health
  3. Public Admin — SEPH 14-10-0220-01: federal / provincial / local employment (2001–2025)
                    StatCan 17-10-0005-01: Canada population for per-capita normalization

Output: data/admin_bloat.json
"""

import csv
import io
import json
import os
import urllib.request
import zipfile
from collections import defaultdict

import openpyxl

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _request(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _get_zip_csv(table_id):
    url = f"https://www150.statcan.gc.ca/n1/tbl/csv/{table_id}-eng.zip"
    print(f"  Downloading {table_id} ...")
    data = _request(url)
    zf = zipfile.ZipFile(io.BytesIO(data))
    return zf.read(f"{table_id}.csv").decode("utf-8-sig")


def _float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


# ── SECTOR 1: Education ───────────────────────────────────────────────────────

def fetch_education():
    """K-12 school board expenditures: teacher salaries vs. admin vs. other (1973–2023)."""
    raw = _get_zip_csv("37100065")
    reader = csv.DictReader(io.StringIO(raw))

    CATS = {
        "Total expenditures":                                "total",
        "Operating expenditures":                            "operating",
        "Operating expenditures, teachers' salaries":        "teacher_salaries",
        "Operating expenditures, administration":            "administration",
        "Operating expenditures, school facilities services": "facilities",
        "Operating expenditures, transportation":            "transportation",
        "Capital expenditures":                              "capital",
        "Other operating expenditures":                      "other_operating",
    }

    annual = defaultdict(dict)
    for row in reader:
        if row.get("GEO") != "Canada":
            continue
        cat = row.get("School board expenditures", "")
        key = CATS.get(cat)
        if key is None:
            continue
        val = _float(row.get("VALUE"))
        if val is None:
            continue
        year = int(row["REF_DATE"].split("/")[0])
        annual[year][key] = val

    series = []
    for yr in sorted(annual):
        e = {"year": yr, **annual[yr]}
        op = e.get("operating", 0)
        if op:
            e["teacher_pct"] = round(e.get("teacher_salaries", 0) / op * 100, 2)
            e["admin_pct"] = round(e.get("administration", 0) / op * 100, 2)
            e["facilities_pct"] = round(e.get("facilities", 0) / op * 100, 2)
            e["transport_pct"] = round(e.get("transportation", 0) / op * 100, 2)
            other = op - e.get("teacher_salaries", 0) - e.get("administration", 0) \
                      - e.get("facilities", 0) - e.get("transportation", 0)
            e["other_pct"] = round(max(other, 0) / op * 100, 2)
            e["non_teacher_pct"] = round(100 - e["teacher_pct"], 2)
        series.append(e)
    return series


# ── SECTOR 2: Healthcare ──────────────────────────────────────────────────────

def fetch_healthcare_nhex():
    """CIHI NHEX: public health spending by use of funds (1975–2024)."""
    url = "https://www.cihi.ca/sites/default/files/document/nhex-open-data-2025-en.xlsx"
    print("  Downloading CIHI NHEX Excel ...")
    data = _request(url, timeout=90)
    wb = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)

    # Find the O.1 sheet
    target_sheet = None
    for sname in wb.sheetnames:
        if "O.1" in sname or "o.1" in sname.lower():
            target_sheet = sname
            break
    if target_sheet is None:
        target_sheet = wb.sheetnames[0]

    ws = wb[target_sheet]
    rows = list(ws.iter_rows(values_only=True))

    # Find header row
    header_row = None
    for i, r in enumerate(rows):
        vals = [str(v).lower() for v in r if v]
        if "year" in vals or "province" in vals:
            header_row = i
            break
    if header_row is None:
        header_row = 0

    headers = [str(v) if v is not None else f"col_{i}" for i, v in enumerate(rows[header_row])]

    def col(name):
        for i, h in enumerate(headers):
            if name.lower() in h.lower():
                return i
        return None

    year_col = col("year")
    prov_col = col("province")
    sector_col = col("sector")
    fund_col = col("use of funds")
    curr_col = col("current dollars")
    if curr_col is None:
        for i, h in enumerate(headers):
            if "current" in h.lower() and "per capita" not in h.lower():
                curr_col = i
                break

    CLINICAL = {"Hospitals", "Physicians", "Other Professionals"}
    CATEGORIES = {
        "Administration", "Hospitals", "Physicians", "Other Professionals",
        "Public Health", "Other Institutions", "Drugs", "Capital",
    }

    annual = defaultdict(dict)
    for row in rows[header_row + 1:]:
        try:
            prov = str(row[prov_col]) if prov_col is not None else ""
            sector = str(row[sector_col]) if sector_col is not None else ""
            fund = str(row[fund_col]) if fund_col is not None else ""
            yr = int(float(str(row[year_col])))
            val = _float(str(row[curr_col]) if curr_col is not None else None)
        except (TypeError, ValueError, IndexError):
            continue
        if "canada" not in prov.lower():
            continue
        if sector.lower() not in ("public", "provincial government"):
            continue
        if fund not in CATEGORIES:
            continue
        if val is None:
            continue
        annual[yr][fund] = annual[yr].get(fund, 0) + val

    series = []
    for yr in sorted(annual):
        d = annual[yr]
        known = sum(d.get(k, 0) for k in CATEGORIES)
        if known == 0:
            continue
        clinical = sum(d.get(k, 0) for k in CLINICAL)
        e = {
            "year": yr,
            "admin_bn": round(d.get("Administration", 0) / 1e9, 3),
            "hospitals_bn": round(d.get("Hospitals", 0) / 1e9, 3),
            "physicians_bn": round(d.get("Physicians", 0) / 1e9, 3),
            "other_prof_bn": round(d.get("Other Professionals", 0) / 1e9, 3),
            "public_health_bn": round(d.get("Public Health", 0) / 1e9, 3),
            "other_inst_bn": round(d.get("Other Institutions", 0) / 1e9, 3),
            "drugs_bn": round(d.get("Drugs", 0) / 1e9, 3),
            "capital_bn": round(d.get("Capital", 0) / 1e9, 3),
            "total_known_bn": round(known / 1e9, 3),
            "clinical_bn": round(clinical / 1e9, 3),
            "admin_pct": round(d.get("Administration", 0) / known * 100, 2) if known else None,
            "hospitals_pct": round(d.get("Hospitals", 0) / known * 100, 2) if known else None,
            "physicians_pct": round(d.get("Physicians", 0) / known * 100, 2) if known else None,
            "clinical_pct": round(clinical / known * 100, 2) if known else None,
        }
        series.append(e)
    return series


def fetch_healthcare_seph(annual_seph):
    """Pull healthcare NAICS sub-sector employment from the pre-fetched SEPH data."""
    HEALTH_NAICS = {
        "Health care and social assistance [62]": "health_total",
        "Ambulatory health care services [621]": "ambulatory",
        "Offices of physicians [6211]": "physician_offices",
        "Hospitals [622]": "hospitals",
        "Nursing and residential care facilities [623]": "nursing",
        "Social assistance [624]": "social_assistance",
    }
    return _extract_seph_series(annual_seph, HEALTH_NAICS)


def fetch_pubadmin_seph(annual_seph):
    """Pull public administration NAICS employment from the pre-fetched SEPH data."""
    PA_NAICS = {
        "Public administration [91]": "pa_total",
        "Federal government public administration [911]": "federal",
        "Provincial and territorial public administration [912]": "provincial",
        "Local, municipal and regional public administration [913]": "local",
        "Aboriginal public administration [914]": "aboriginal",
        "Total, all industries": "total_economy",
    }
    return _extract_seph_series(annual_seph, PA_NAICS)


def _extract_seph_series(annual_seph, mapping):
    series = []
    for yr in sorted(annual_seph):
        d = annual_seph[yr]
        entry = {"year": yr}
        for naics_label, key in mapping.items():
            entry[key] = d.get(naics_label)
        series.append(entry)
    return [e for e in series if any(v is not None for k, v in e.items() if k != "year")]


def fetch_seph_raw():
    """Download SEPH 14-10-0220-01 and return annual December employment by NAICS/Canada."""
    raw = _get_zip_csv("14100220")
    reader = csv.DictReader(io.StringIO(raw))

    TARGET = {
        "Health care and social assistance [62]",
        "Ambulatory health care services [621]",
        "Offices of physicians [6211]",
        "Hospitals [622]",
        "Nursing and residential care facilities [623]",
        "Social assistance [624]",
        "Public administration [91]",
        "Federal government public administration [911]",
        "Provincial and territorial public administration [912]",
        "Local, municipal and regional public administration [913]",
        "Aboriginal public administration [914]",
        "Total, all industries",
    }

    annual = defaultdict(dict)
    for row in reader:
        if row.get("Estimate") != "Employment for all employees":
            continue
        naics = row.get("North American Industry Classification System (NAICS)", "")
        if naics not in TARGET:
            continue
        if "Canada" not in row.get("GEO", ""):
            continue
        if not row["REF_DATE"].endswith("-12"):
            continue
        val = _float(row.get("VALUE"))
        if val is None:
            continue
        year = int(row["REF_DATE"][:4])
        annual[year][naics] = val

    return annual


def fetch_population():
    """Annual Canada total population (persons) from 17-10-0005-01."""
    raw = _get_zip_csv("17100005")
    reader = csv.DictReader(io.StringIO(raw))

    pop = {}
    for row in reader:
        if row.get("GEO") != "Canada":
            continue
        if row.get("Gender") != "Total - gender":
            continue
        if row.get("Age group") != "All ages":
            continue
        val = _float(row.get("VALUE"))
        if val is None:
            continue
        try:
            year = int(row["REF_DATE"])
        except ValueError:
            continue
        pop[year] = val

    return pop


# ── Helpers ───────────────────────────────────────────────────────────────────

def index_to(series, key, base_year):
    """Return list of {year, value} indexed so base_year = 100."""
    base = next((e[key] for e in series if e.get("year") == base_year and e.get(key) is not None), None)
    if base is None or base == 0:
        return []
    return [
        {"year": e["year"], "idx": round(e[key] / base * 100, 1)}
        for e in series if e.get(key) is not None
    ]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    edu_series = fetch_education()
    nhex_series = fetch_healthcare_nhex()
    seph_raw = fetch_seph_raw()
    health_seph = fetch_healthcare_seph(seph_raw)
    pa_seph = fetch_pubadmin_seph(seph_raw)
    pop = fetch_population()

    BASE_YEAR = 2001

    # Build healthcare SEPH indexed series
    health_idx = {}
    for key in ("health_total", "physician_offices", "hospitals", "nursing", "social_assistance", "ambulatory"):
        health_idx[key] = index_to(health_seph, key, BASE_YEAR)

    # Build per-capita public admin series
    pa_percapita = []
    for e in pa_seph:
        yr = e["year"]
        p = pop.get(yr)
        if p is None or p == 0:
            continue
        entry = {"year": yr}
        for k in ("pa_total", "federal", "provincial", "local"):
            v = e.get(k)
            if v is not None:
                entry[k] = round(v * 1000 / p, 2)  # employees per 1,000 Canadians
        pa_percapita.append(entry)

    # Quick summary stats
    latest_edu = next((e for e in reversed(edu_series) if e.get("teacher_pct")), {})
    earliest_edu = next((e for e in edu_series if e.get("teacher_pct")), {})
    latest_nhex = nhex_series[-1] if nhex_series else {}
    earliest_nhex = nhex_series[0] if nhex_series else {}
    latest_pa = pa_percapita[-1] if pa_percapita else {}
    earliest_pa = pa_percapita[0] if pa_percapita else {}

    result = {
        "metadata": {
            "title": "Doers vs. Administrative Overhead in Canada's Public Sector",
            "subtitle": "Sector-specific analysis: education, healthcare, and public administration",
            "sources": [
                "Statistics Canada, Table 37-10-0065-01: School board expenditures, 1973–2023",
                "CIHI, National Health Expenditure Trends (NHEX), open data 2025 edition, 1975–2024",
                "Statistics Canada, Table 14-10-0220-01: SEPH employment by NAICS, monthly, 2001–2026",
                "Statistics Canada, Table 17-10-0005-01: Canada population estimates, annual, 1971–2025",
            ],
            "base_year": BASE_YEAR,
            "generated": "2026-06-09",
        },

        # ── SECTOR 1: Education ──────────────────────────────────────────────
        "education": {
            "label": "Education (K-12)",
            "description": "K-12 public school board expenditures: teacher salaries vs. administration vs. other operating costs",
            "source": "StatCan 37-10-0065-01",
            "series": edu_series,
            "summary": {
                "earliest_year": earliest_edu.get("year"),
                "latest_year": latest_edu.get("year"),
                "teacher_pct_earliest": earliest_edu.get("teacher_pct"),
                "teacher_pct_latest": latest_edu.get("teacher_pct"),
                "admin_pct_earliest": earliest_edu.get("admin_pct"),
                "admin_pct_latest": latest_edu.get("admin_pct"),
            },
        },

        # ── SECTOR 2: Healthcare ─────────────────────────────────────────────
        "healthcare": {
            "label": "Healthcare",
            "description": "Public health system spending by category and employment by sub-sector",
            "sources": [
                "CIHI NHEX 2025 — spending breakdown by use of funds, 1975–2024",
                "StatCan SEPH 14-10-0220-01 — employment by healthcare NAICS, 2001–2025",
            ],
            "nhex_series": nhex_series,
            "seph_series": health_seph,
            "seph_indexed": health_idx,
            "summary": {
                "nhex_earliest_year": earliest_nhex.get("year"),
                "nhex_latest_year": latest_nhex.get("year"),
                "admin_pct_earliest": earliest_nhex.get("admin_pct"),
                "admin_pct_latest": latest_nhex.get("admin_pct"),
                "hospitals_pct_latest": latest_nhex.get("hospitals_pct"),
                "physicians_pct_latest": latest_nhex.get("physicians_pct"),
                "clinical_pct_latest": latest_nhex.get("clinical_pct"),
                "health_total_2001": next((e.get("health_total") for e in health_seph if e.get("year") == BASE_YEAR), None),
                "physician_offices_2001": next((e.get("physician_offices") for e in health_seph if e.get("year") == BASE_YEAR), None),
                "health_total_latest": next((e.get("health_total") for e in reversed(health_seph) if e.get("health_total")), None),
                "physician_offices_latest": next((e.get("physician_offices") for e in reversed(health_seph) if e.get("physician_offices")), None),
            },
        },

        # ── SECTOR 3: Public Administration ─────────────────────────────────
        "public_admin": {
            "label": "Public Administration",
            "description": "Government employment per 1,000 Canadians by level of government",
            "source": "StatCan SEPH 14-10-0220-01 + population 17-10-0005-01",
            "seph_series": pa_seph,
            "percapita_series": pa_percapita,
            "summary": {
                "earliest_year": earliest_pa.get("year"),
                "latest_year": latest_pa.get("year"),
                "pa_per1k_earliest": earliest_pa.get("pa_total"),
                "pa_per1k_latest": latest_pa.get("pa_total"),
                "federal_per1k_earliest": earliest_pa.get("federal"),
                "federal_per1k_latest": latest_pa.get("federal"),
                "provincial_per1k_earliest": earliest_pa.get("provincial"),
                "provincial_per1k_latest": latest_pa.get("provincial"),
                "local_per1k_earliest": earliest_pa.get("local"),
                "local_per1k_latest": latest_pa.get("local"),
            },
        },
    }

    out_path = os.path.join(DATA_DIR, "admin_bloat.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n  Wrote {out_path}")

    # Print summary
    s = result["education"]["summary"]
    print(f"\n  Education (K-12):")
    print(f"    Teacher salary %: {s['teacher_pct_earliest']}% ({s['earliest_year']}) → {s['teacher_pct_latest']}% ({s['latest_year']})")
    print(f"    Admin %:          {s['admin_pct_earliest']}% ({s['earliest_year']}) → {s['admin_pct_latest']}% ({s['latest_year']})")

    s = result["healthcare"]["summary"]
    print(f"\n  Healthcare (NHEX spending):")
    print(f"    Admin %: {s['admin_pct_earliest']}% ({s['nhex_earliest_year']}) → {s['admin_pct_latest']}% ({s['nhex_latest_year']})")
    print(f"    Clinical % latest: {s['clinical_pct_latest']}%")
    if s.get("health_total_2001") and s.get("health_total_latest"):
        pct_h = round((s["health_total_latest"] / s["health_total_2001"] - 1) * 100)
        pct_p = round((s["physician_offices_latest"] / s["physician_offices_2001"] - 1) * 100) if s.get("physician_offices_2001") else "?"
        print(f"    SEPH health employment growth 2001→latest: +{pct_h}%")
        print(f"    SEPH physician-office employment growth:    +{pct_p}%")

    s = result["public_admin"]["summary"]
    print(f"\n  Public Administration (per 1,000 Canadians):")
    print(f"    Total: {s['pa_per1k_earliest']} ({s['earliest_year']}) → {s['pa_per1k_latest']} ({s['latest_year']})")
    print(f"    Federal:    {s['federal_per1k_earliest']} → {s['federal_per1k_latest']}")
    print(f"    Provincial: {s['provincial_per1k_earliest']} → {s['provincial_per1k_latest']}")
    print(f"    Local:      {s['local_per1k_earliest']} → {s['local_per1k_latest']}")


if __name__ == "__main__":
    main()
