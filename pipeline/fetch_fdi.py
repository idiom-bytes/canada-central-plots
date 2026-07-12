"""Fetch and aggregate FDI flows into Canada by sector, from Statistics Canada.

Sources:
  - StatCan 36-10-0026-01: Balance of international payments, FDI flows by NAICS industry (quarterly)
    Covers 2007-present. Aggregated to annual totals.

Output: data/fdi.json
"""

import csv
import io
import json
import os
import sys
import urllib.request
import zipfile
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

TABLE_URL = "https://www150.statcan.gc.ca/n1/tbl/csv/36100026-eng.zip"
TABLE_FILE = "36100026.csv"

# KISS classification: which sectors represent productive investment vs. extraction/control risk
KISS_GREEN = {
    "Manufacturing [31-33]",
    "Trade and transportation",
}
KISS_RED = {
    "Energy and mining",
    "Finance and Insurance [52]",
    "Management of companies and enterprises [55]",
    "Other industries",
}

SECTOR_LABELS = {
    "Manufacturing [31-33]": "Manufacturing",
    "Trade and transportation": "Trade & Transportation",
    "Energy and mining": "Energy & Mining",
    "Finance and Insurance [52]": "Finance & Insurance",
    "Management of companies and enterprises [55]": "Management of Companies",
    "Other industries": "Other",
}


def download_table():
    req = urllib.request.Request(TABLE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    zf = zipfile.ZipFile(io.BytesIO(data))
    return zf.read(TABLE_FILE).decode("utf-8-sig")


def parse_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def main():
    print("  Downloading StatCan 36-10-0026-01 (FDI flows by industry)...")
    raw = download_table()
    reader = csv.DictReader(io.StringIO(raw))

    # annual[year][sector] = sum of quarterly flows in C$ millions
    annual = defaultdict(lambda: defaultdict(float))
    for row in reader:
        if row["Type of direct investment"] != "Foreign direct investment in Canada":
            continue
        sector = row["North American Industry Classification System"]
        if sector == "All industries":
            continue
        val = parse_float(row.get("VALUE"))
        if val is None:
            continue
        year = int(row["REF_DATE"][:4])
        annual[year][sector] += val

    sectors = list(SECTOR_LABELS.keys())
    years = sorted(annual.keys())

    # Build sector time series (C$ billions)
    sector_series = []
    for yr in years:
        entry = {"year": yr}
        total = 0.0
        for s in sectors:
            val = round(annual[yr].get(s, 0.0) / 1000, 2)
            entry[SECTOR_LABELS[s]] = val
            total += annual[yr].get(s, 0.0)
        entry["total"] = round(total / 1000, 2)
        sector_series.append(entry)

    # Build KISS series: green (productive) vs red (extraction/control)
    kiss_series = []
    for yr in years:
        green = sum(annual[yr].get(s, 0.0) for s in KISS_GREEN)
        red = sum(annual[yr].get(s, 0.0) for s in KISS_RED)
        kiss_series.append({
            "year": yr,
            "green": round(green / 1000, 2),
            "red": round(red / 1000, 2),
            "total": round((green + red) / 1000, 2),
        })

    result = {
        "metadata": {
            "title": "Foreign Direct Investment Inflows to Canada by Sector",
            "source": "Statistics Canada, Table 36-10-0026-01",
            "unit": "C$ billions",
            "frequency": "Annual (aggregated from quarterly flows)",
            "coverage": f"{years[0]}–{years[-1]}",
        },
        "sectors": [SECTOR_LABELS[s] for s in sectors],
        "kiss_green_sectors": [SECTOR_LABELS[s] for s in KISS_GREEN],
        "kiss_red_sectors": [SECTOR_LABELS[s] for s in KISS_RED],
        "sector_series": sector_series,
        "kiss_series": kiss_series,
    }

    out_path = os.path.join(DATA_DIR, "fdi.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Wrote {out_path} ({len(sector_series)} years, {len(sectors)} sectors)")


if __name__ == "__main__":
    main()
