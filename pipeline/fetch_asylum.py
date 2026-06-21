"""View 5 data — THE ASYLUM CHANNEL. Ties together the user's points 2/3/4:
  (3) asylum claimants seen in isolation (not buried in "non-permanent residents")
  (4) the divergence — work/study permits cut from their 2025 peak while asylum
      keeps rising (the "population shrinking, but immigration at generational
      highs" story)
  (2) origin — for asylum claimants, country of citizenship IS published (unlike
      for crime offenders, see the Origin Data Gap view). The accumulation of
      claimants present is the measurable face of an enforcement system that
      cannot resolve or remove fast enough.

Sources:
  - IRCC Open Data: Asylum Claimants by Province/Office Type (monthly inflow).
  - IRCC Open Data: Asylum Claimants by Top-25 Country of Citizenship.
  - StatCan 17-10-0121-01 stock series (reused from data/immigration_volumes.json).

Output: data/asylum.json, data/asylum.js (window.ASYLUM_DB)
"""

import csv
import io
import json
import os
import ssl
import urllib.request
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
UA = "Mozilla/5.0 (X11; Linux x86_64) research-bot"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

OFFICE = "https://www.ircc.canada.ca/opendata-donneesouvertes/data/ODP-Asylum-PT_OfficeType.csv"
TOP25 = "https://www.ircc.canada.ca/opendata-donneesouvertes/data/ODP-Asylum-Top25CitzProv-LastYear.csv"


def tsv(url):
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90, context=CTX).read()
    return list(csv.reader(io.StringIO(raw.decode("utf-8-sig", "ignore")), delimiter="\t"))


def val(s):
    s = (s or "").strip().replace(",", "")
    if s in ("", "--", "..", "n/a"):
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def main():
    # ---- inflow by year + by office type ----
    rows = tsv(OFFICE)
    by_year = defaultdict(int)
    by_office = defaultdict(lambda: defaultdict(int))   # year -> office -> n
    months_per_year = defaultdict(set)
    for r in rows[1:]:
        if len(r) < 9 or not r[0].isdigit():
            continue
        yr = int(r[0]); office = r[6]; n = val(r[8])
        by_year[yr] += n
        by_office[yr][office] += n
        months_per_year[yr].add(r[1])
    years = sorted(by_year)
    inflow_year = [{"year": y, "n": by_year[y], "months": len(months_per_year[y])} for y in years]
    offices = ["Inland", "Border", "Airport", "Other Offices"]
    inflow_office = {"years": years,
                     "series": {o: [by_office[y].get(o, 0) for y in years] for o in offices}}

    # ---- top source countries (latest full year) ----
    trows = tsv(TOP25)
    # columns: yr,quarter,month,fr...,rank_en,rank_fr,country_en,country_fr,office_en,office_fr,VALUE
    cty_year = defaultdict(lambda: defaultdict(int))
    yr_months = defaultdict(set)
    for r in trows[1:]:
        if len(r) < 13 or not r[0].isdigit():
            continue
        yr = int(r[0]); country = r[10].split(",")[0].strip(); n = val(r[12])
        if not country:
            continue
        cty_year[yr][country] += n
        yr_months[yr].add(r[2])
    full_years = [y for y in sorted(cty_year) if len(yr_months[y]) >= 12]
    ref_year = full_years[-1] if full_years else sorted(cty_year)[-1]

    def is_country(c):
        return c.lower() not in ("other countries", "other")

    ranked = [(c, n) for c, n in sorted(cty_year[ref_year].items(), key=lambda x: -x[1])
              if is_country(c)][:15]
    top_countries = [{"country": c, "n": n} for c, n in ranked]

    # historical by-country series (full years only) for the leading source countries
    totals = defaultdict(int)
    for y in full_years:
        for c, n in cty_year[y].items():
            if is_country(c):
                totals[c] += n
    hist_top = [c for c, _ in sorted(totals.items(), key=lambda x: -x[1])[:8]]
    countries_by_year = {
        "years": full_years,
        "countries": hist_top,
        "series": {c: [cty_year[y].get(c, 0) for y in full_years] for c in hist_top},
    }

    # ---- stock series (reuse volumes.json) ----
    stock = None
    vp = os.path.join(DATA, "immigration_volumes.json")
    if os.path.exists(vp):
        v = json.load(open(vp))
        s = v["npr"]["series"]
        stock = {"periods": v["npr"]["periods"],
                 "asylum": s["asylum"], "work": s["work"], "study": s["study"], "total": s["total"]}

    # divergence: peak vs latest for each stock component
    diverge = None
    if stock:
        def peak_latest(arr):
            pk = max(range(len(arr)), key=lambda i: arr[i] or 0)
            return {"peak": arr[pk], "peak_period": stock["periods"][pk],
                    "latest": arr[-1], "latest_period": stock["periods"][-1]}
        diverge = {k: peak_latest(stock[k]) for k in ("asylum", "work", "study", "total")}

    latest_full = next((d for d in reversed(inflow_year) if d["months"] >= 12), inflow_year[-1])
    first = inflow_year[0]
    out = {
        "meta": {
            "inflow_first_year": first["year"], "inflow_first_n": first["n"],
            "inflow_latest_full_year": latest_full["year"], "inflow_latest_full_n": latest_full["n"],
            "inflow_growth_pct": round(100 * (latest_full["n"] / first["n"] - 1)) if first["n"] else None,
            "stock_asylum_latest": stock["asylum"][-1] if stock else None,
            "stock_latest_period": stock["periods"][-1] if stock else None,
            "ref_year_countries": ref_year,
            "top_country": top_countries[0]["country"] if top_countries else None,
            "top_country_n": top_countries[0]["n"] if top_countries else None,
            "sources": [
                "IRCC Open Data — Asylum Claimants by Province/Territory and Office Type (monthly)",
                "IRCC Open Data — Asylum Claimants by Top-25 Country of Citizenship",
                "Statistics Canada Table 17-10-0121-01 (non-permanent residents by type)",
            ],
        },
        "inflow_year": inflow_year,
        "inflow_office": inflow_office,
        "top_countries": top_countries,
        "countries_by_year": countries_by_year,
        "stock": stock,
        "diverge": diverge,
    }
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "asylum.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "asylum.js"), "w") as f:
        f.write("window.ASYLUM_DB = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    m = out["meta"]
    print(f"inflow years    : {first['year']} -> {inflow_year[-1]['year']} ({inflow_year[-1]['months']}mo in last)")
    print(f"new claims      : {m['inflow_first_n']:,} ({m['inflow_first_year']}) -> {m['inflow_latest_full_n']:,} ({m['inflow_latest_full_year']})  +{m['inflow_growth_pct']}%")
    print(f"stock asylum    : {m['stock_asylum_latest']:,} present ({m['stock_latest_period']})")
    print(f"top countries {ref_year}:")
    for c in top_countries[:10]:
        print(f"   {c['n']:>7,}  {c['country']}")
    if diverge:
        print("divergence (peak -> latest):")
        for k, d in diverge.items():
            print(f"   {k:6s}: {d['peak']:>9,} ({d['peak_period']}) -> {d['latest']:>9,} ({d['latest_period']})")


if __name__ == "__main__":
    main()
