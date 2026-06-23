"""Canada-vs-UK view data — Canadian police-reported rates for the crime types
at issue, direct from Statistics Canada UCR. No model, no search.

Source: StatCan Table 35-10-0177-01 (Incident-based crime statistics, by
detailed violations), national (GEO = Canada). We pull, per year:
  - Trafficking in persons [1525]            -> compares to UK NRM referrals
  - Total sexual violations against children [130] -> compares to UK group CSE
  - Sexual assault, level 1 [1330]           -> general sexual-assault context
both as actual incidents and rate per 100,000 population.

Output: data/crime_rates.json, data/crime_rates.js (window.CRIME_RATES)
"""

import csv
import io
import json
import os
import urllib.request
import zipfile
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
UA = "Mozilla/5.0 (X11; Linux x86_64) research-bot"

TARGETS = {
    "Trafficking in persons [1525]": "trafficking",
    "Kidnapping [1515]": "kidnapping",
    "Total sexual violations against children [130]": "child_sexual",
    "Sexual assault, level 1 [1330]": "sexual_assault",
}
RATE = "Rate per 100,000 population"
COUNT = "Actual incidents"


def main():
    url = "https://www150.statcan.gc.ca/n1/tbl/csv/35100177-eng.zip"
    raw = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA}), timeout=180).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    fn = [n for n in z.namelist() if n.endswith(".csv") and "MetaData" not in n][0]

    rate = defaultdict(dict)   # key -> {year: rate}
    count = defaultdict(dict)  # key -> {year: count}
    stats_seen = set()
    with z.open(fn) as f:
        rd = csv.reader(io.TextIOWrapper(f, "utf-8-sig"))
        next(rd)
        for r in rd:
            if r[1] != "Canada":
                continue
            v = r[3]
            if v not in TARGETS:
                continue
            key = TARGETS[v]
            stat = r[4]
            stats_seen.add(stat)
            try:
                year = int(r[0][:4])
                val = float(r[11]) if r[11] not in ("", "..") else None
            except (ValueError, IndexError):
                continue
            if val is None:
                continue
            if stat == RATE:
                rate[key][year] = val
            elif stat == COUNT:
                count[key][year] = int(val)

    all_years = sorted({y for k in rate for y in rate[k]})
    # per series, start at the first year the offence has a non-zero rate
    # (e.g. "trafficking in persons" only entered the Criminal Code in 2005)
    series = {}
    series_years = {}
    for key in TARGETS.values():
        ys = [y for y in all_years if (rate[key].get(y) or 0) > 0]
        yrs = [y for y in all_years if ys and y >= ys[0]]
        series_years[key] = yrs
        series[key] = {
            "years": yrs,
            "rate": [rate[key].get(y) for y in yrs],
            "count": [count[key].get(y) for y in yrs],
        }

    def latest(key):
        ys = [y for y in series_years[key] if rate[key].get(y) is not None]
        return ys[-1] if ys else None

    out = {"meta": {}, "series": series, "labels": {
        "trafficking": "Human trafficking",
        "child_sexual": "Child exploitation",
        "sexual_assault": "Sexual assault (level 1)",
        "kidnapping": "Kidnapping",
    }, "source": "Statistics Canada Table 35-10-0177-01 (incident-based crime, police-reported)"}

    for key in TARGETS.values():
        ly = latest(key)
        fy = next((y for y in series_years[key] if rate[key].get(y) is not None), None)
        y10 = ly - 10 if ly else None
        r10 = rate[key].get(y10)
        out["meta"][key] = {
            "latest_year": ly, "latest_rate": rate[key].get(ly), "latest_count": count[key].get(ly),
            "first_year": fy, "first_rate": rate[key].get(fy),
            # since-inception change is a base-effect artifact for new offences; prefer 10yr.
            "change_10yr_pct": (round(100 * (rate[key][ly] / r10 - 1)) if (ly and r10) else None),
            "ten_year_from": y10 if r10 else None,
        }

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "crime_rates.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "crime_rates.js"), "w") as f:
        f.write("window.CRIME_RATES = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    print("Statistics labels seen:", sorted(stats_seen))
    print("years span:", all_years[0], "->", all_years[-1])
    for key in TARGETS.values():
        m = out["meta"][key]
        print(f"{key:16s} {m['latest_year']}: {m['latest_rate']}/100k ({m['latest_count']:,} incidents)  10yr change {m['change_10yr_pct']}%")


if __name__ == "__main__":
    main()
