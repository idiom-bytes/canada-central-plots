"""View 2 data — immigration VOLUMES: permanent immigrants vs. temporary
residents (TFW / students / asylum), direct from Statistics Canada.

No search, no model — same pattern as fetch_fdi.py.

Sources:
  - StatCan 17-10-0008-01: Components of demographic growth, annual.
      -> Immigrants (permanent) and Net non-permanent residents, by fiscal year.
  - StatCan 17-10-0121-01: Non-permanent residents by type, quarterly (2021-).
      -> Stock of NPR split into work-permit / study / work+study / asylum / other.
        The five components sum exactly to total NPR.

Output:
  data/immigration_volumes.json
  data/volumes.js   (window.VOLUMES_DB) for the dashboard
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


def load(tid):
    url = f"https://www150.statcan.gc.ca/n1/tbl/csv/{tid}-eng.zip"
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    fn = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n][0]
    return list(csv.DictReader(io.TextIOWrapper(z.open(fn), "utf-8-sig")))


def num(v):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def main():
    # ---- annual: permanent immigrants vs net NPR (17-10-0008) ----
    r8 = load("17100008")
    ck = next(k for k in r8[0] if "Components" in k)
    annual = {}
    for row in r8:
        if row["GEO"] != "Canada":
            continue
        rd = row["REF_DATE"]
        if rd < "2000/2001":
            continue
        comp = row[ck]
        if comp == "Immigrants":
            annual.setdefault(rd, {})["immigrants"] = num(row["VALUE"])
        elif comp == "Net non-permanent residents":
            annual.setdefault(rd, {})["net_npr"] = num(row["VALUE"])
    annual_series = [{"year": k, **v} for k, v in sorted(annual.items())]

    # ---- quarterly: NPR stock by type (17-10-0121) ----
    r12 = load("17100121")
    tk = next(k for k in r12[0] if "Non-permanent resident types" in k)
    COMPONENTS = {
        "Work permit holders only": "work",
        "Work and study permit holders": "work_study",
        "Study permit holders only": "study",
        "Total, asylum claimants, protected persons and related groups": "asylum",
        "Other": "other",
    }
    periods = sorted({row["REF_DATE"] for row in r12 if row["GEO"] == "Canada"})
    npr = {v: {p: None for p in periods} for v in COMPONENTS.values()}
    npr["total"] = {p: None for p in periods}
    for row in r12:
        if row["GEO"] != "Canada":
            continue
        t = row[tk]
        if t in COMPONENTS:
            npr[COMPONENTS[t]][row["REF_DATE"]] = num(row["VALUE"])
        elif t == "Total, non-permanent residents":
            npr["total"][row["REF_DATE"]] = num(row["VALUE"])
    npr_series = {
        "periods": periods,
        "series": {k: [npr[k][p] for p in periods] for k in npr},
    }

    latest = periods[-1]
    li = {k: npr[k][latest] for k in npr}
    first_npr = periods[0]
    fi = npr["total"][first_npr]

    # peak NPR-growth year and latest PR
    pr_latest = annual_series[-1]
    peak_npr = max(annual_series, key=lambda a: a.get("net_npr") or -1e9)

    out = {
        "meta": {
            "npr_total_latest": li["total"],
            "npr_latest_period": latest,
            "npr_work": li["work"],
            "npr_asylum": li["asylum"],
            "npr_study": li["study"],
            "npr_growth_since_first": (li["total"] - fi) if (li["total"] and fi) else None,
            "npr_first_period": first_npr,
            "immigrants_latest": pr_latest.get("immigrants"),
            "immigrants_latest_year": pr_latest["year"],
            "peak_net_npr": peak_npr.get("net_npr"),
            "peak_net_npr_year": peak_npr["year"],
            "sources": [
                "Statistics Canada Table 17-10-0008-01 (components of demographic growth, annual)",
                "Statistics Canada Table 17-10-0121-01 (non-permanent residents by type, quarterly)",
            ],
        },
        "annual": annual_series,
        "npr": npr_series,
    }
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "immigration_volumes.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "volumes.js"), "w") as f:
        f.write("window.VOLUMES_DB = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    m = out["meta"]
    print(f"annual years     : {annual_series[0]['year']} -> {annual_series[-1]['year']} ({len(annual_series)})")
    print(f"NPR periods      : {first_npr} -> {latest} ({len(periods)})")
    print(f"NPR total latest : {m['npr_total_latest']:,}  (work {m['npr_work']:,} / asylum {m['npr_asylum']:,} / study {m['npr_study']:,})")
    print(f"NPR growth       : +{m['npr_growth_since_first']:,} since {first_npr}")
    print(f"PR latest        : {m['immigrants_latest']:,} ({m['immigrants_latest_year']})")
    print(f"peak net NPR     : {m['peak_net_npr']:,} ({m['peak_net_npr_year']})")


if __name__ == "__main__":
    main()
