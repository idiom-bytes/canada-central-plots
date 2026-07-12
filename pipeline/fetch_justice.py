"""View 3 data — the backed-up justice system: remand (held without conviction)
vs. sentenced custody, direct from Statistics Canada. No search, no model.

The remand population — people held in jail awaiting trial, NOT convicted of
anything — is the measurable symptom of a court system that cannot process cases
fast enough. When remand outgrows the sentenced population, the system is jailing
more un-convicted people than convicted ones, while the R v. Jordan time ceilings
force serious charges to be stayed for delay (the "release" side of the problem).

Source:
  - StatCan 35-10-0154-01: Average counts of adults in provincial/territorial
    correctional programs. National total is GEO = "Provinces and Territories".

Output:
  data/justice.json
  data/justice.js   (window.JUSTICE_DB)
"""

import csv
import io
import json
import os
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
UA = "Mozilla/5.0 (X11; Linux x86_64) research-bot"
NAT = "Provinces and Territories"


def load(tid):
    url = f"https://www150.statcan.gc.ca/n1/tbl/csv/{tid}-eng.zip"
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    fn = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n][0]
    return csv.DictReader(io.TextIOWrapper(z.open(fn), "utf-8-sig"))


def num(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def main():
    r = load("35100154")
    ck = None
    by_year = {}
    for row in r:
        if ck is None:
            ck = next(c for c in row if "Custodial" in c)
        if row["GEO"] != NAT or row["UOM"] != "Persons":
            continue
        comp = row[ck]
        slot = {
            "Remand, actual-in count": "remand",
            "Sentenced, actual-in count": "sentenced",
            "Total actual-in count": "total_custody",
        }.get(comp)
        if slot:
            by_year.setdefault(row["REF_DATE"], {})[slot] = num(row["VALUE"])

    series = []
    for yr in sorted(by_year):
        d = by_year[yr]
        rem, sent = d.get("remand"), d.get("sentenced")
        share = round(100 * rem / (rem + sent), 1) if (rem and sent) else None
        series.append({"year": yr, "remand": rem, "sentenced": sent,
                       "total_custody": d.get("total_custody"), "remand_share": share})

    # restrict to years with both remand & sentenced for clean charting
    series = [s for s in series if s["remand"] is not None and s["sentenced"] is not None]
    latest = series[-1]
    # first year remand share crossed 50%
    crossover = next((s["year"] for s in series if s["remand_share"] and s["remand_share"] >= 50), None)
    earliest = series[0]

    out = {
        "meta": {
            "latest_year": latest["year"],
            "remand_latest": round(latest["remand"]),
            "sentenced_latest": round(latest["sentenced"]),
            "remand_share_latest": latest["remand_share"],
            "remand_share_earliest": earliest["remand_share"],
            "earliest_year": earliest["year"],
            "crossover_year": crossover,
            "remand_growth_pct": round(100 * (latest["remand"] / earliest["remand"] - 1))
            if earliest["remand"] else None,
            "source": "Statistics Canada Table 35-10-0154-01 (average counts of adults in provincial/territorial correctional programs)",
        },
        "series": series,
    }
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "justice.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "justice.js"), "w") as f:
        f.write("window.JUSTICE_DB = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    m = out["meta"]
    print(f"years           : {earliest['year']} -> {latest['year']} ({len(series)})")
    print(f"remand latest   : {m['remand_latest']:,} ({m['latest_year']})")
    print(f"sentenced latest: {m['sentenced_latest']:,}")
    print(f"remand share    : {m['remand_share_earliest']}% ({m['earliest_year']}) -> {m['remand_share_latest']}% ({m['latest_year']})")
    print(f"crossed 50% in  : {m['crossover_year']}")
    print(f"remand growth   : +{m['remand_growth_pct']}% since {m['earliest_year']}")


if __name__ == "__main__":
    main()
