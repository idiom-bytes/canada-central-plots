#!/usr/bin/env python3
"""
Build a DEFENSIBLE international comparison of recorded sexual-violence trends.

Deliberately NOT the viral-meme method (raw counts, cross-country levels). Instead:
  - rate per 100,000 (Eurostat unit P_HTHAB), never raw counts
  - indexed to a base year so we compare TREND SHAPE, not levels
  - every known legal / recording change annotated, so artifacts are visible
  - Canada included with an explicit definition caveat (no "rape" category since 1983)

Token-lean: downloads Eurostat JSON to the lake; a script parses it; the model never
reads the raw payload.

Sources:
  - Eurostat crim_off_cat, ICCS03011 (rape), unit P_HTHAB  (per 100k inhabitants)
  - Statistics Canada UCR (reused from data/crime_rates.json: sexual assault level 1)

Run:  python3 pipeline/fetch_intl_sexual_crime.py
Out:  lake/intl_crime/*.json  +  data/intl_crime_compare.js
"""
import json, ssl, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAKE = ROOT / "lake" / "intl_crime"
RAW = LAKE / "raw"
RAW.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
BASE = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
        "crim_off_cat?format=JSON&lang=EN&unit=P_HTHAB&iccs=ICCS03011&geo=")

# Eurostat geo code -> display name
GEOS = {
    "DE": "Germany", "FR": "France", "PL": "Poland", "SE": "Sweden",
    "NL": "Netherlands", "ES": "Spain", "IT": "Italy", "UK": "United Kingdom",
    "EU27_2020": "EU average",
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch_json(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90, context=ctx) as r:
        data = r.read()
    dest.write_bytes(data)
    return json.loads(data)


def parse_eurostat(d):
    """Single-geo JSON-stat -> {year:int -> rate:float}. Only `time` varies."""
    idx = d["dimension"]["time"]["category"]["index"]   # {"2008":0, ...}
    pos2year = {v: int(k) for k, v in idx.items()}
    out = {}
    for pos_str, val in d.get("value", {}).items():
        y = pos2year.get(int(pos_str))
        if y is not None and val is not None:
            out[y] = round(float(val), 2)
    return dict(sorted(out.items()))


def main():
    countries = {}
    for code, name in GEOS.items():
        try:
            d = fetch_json(BASE + code, RAW / f"eurostat_rape_{code}.json")
            series = parse_eurostat(d)
            if series:
                countries[name] = {"code": code, "source": "Eurostat crim_off_cat (rape, per 100k)",
                                   "definition": "Rape (ICCS 03011), police-recorded",
                                   "years": list(series.keys()), "rate": list(series.values())}
                yr = list(series.keys())
                print(f"[OK ] {name:<16} {yr[0]}–{yr[-1]}  ({len(yr)} yrs)  latest={series[yr[-1]]}/100k")
            else:
                print(f"[EMPTY] {name}")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, KeyError, ValueError) as e:
            print(f"[FAIL] {name}: {e}")

    # ---- England & Wales (not in current Eurostat): ONS recorded rape ----
    # Transparently derived: ONS police-recorded rape offences (year ending March)
    # divided by ONS mid-year E&W population. Trend (indexed) is the point; small
    # population rounding is immaterial. Source: ONS Crime in England & Wales tables.
    EW_COUNTS = {2013:16038,2014:22116,2015:29234,2016:35798,2017:41150,2018:53977,
                 2019:58657,2020:58856,2021:56710,2022:67125,2023:68109,2024:71227}
    EW_POP = {2013:56.9e6,2014:57.4e6,2015:57.9e6,2016:58.4e6,2017:58.7e6,2018:59.1e6,
              2019:59.4e6,2020:59.7e6,2021:59.6e6,2022:60.0e6,2023:60.2e6,2024:60.5e6}
    ew_y = sorted(EW_COUNTS)
    countries["England & Wales"] = {
        "code": "EW", "source": "ONS police-recorded rape ÷ ONS mid-year population (derived)",
        "definition": "Rape, police-recorded (E&W); recording rules broadened 2003 & 2014",
        "years": ew_y, "rate": [round(EW_COUNTS[y] / EW_POP[y] * 1e5, 2) for y in ew_y]}
    print(f"[OK ] {'England & Wales':<16} {ew_y[0]}–{ew_y[-1]}  ({len(ew_y)} yrs)  "
          f"latest={round(EW_COUNTS[ew_y[-1]]/EW_POP[ew_y[-1]]*1e5,2)}/100k  [derived]")

    # ---- Canada from StatCan UCR (reuse existing pipeline output) ----
    try:
        cr = json.loads((ROOT / "data" / "crime_rates.json").read_text())
        sa = cr["series"]["sexual_assault"]
        # trim to >=2008 to line up with Eurostat window
        # keep Canada's full history (back to 1998) so the absolute long-run is visible
        ys, rs = [], []
        for y, r in zip(sa["years"], sa["rate"]):
            ys.append(y); rs.append(round(float(r), 2))
        countries["Canada"] = {"code": "CA", "source": "StatCan UCR 35-10-0177 (sexual assault, level 1)",
                               "definition": "Sexual assault, level 1 (Canada has no separate 'rape' offence since 1983)",
                               "years": ys, "rate": rs}
        print(f"[OK ] {'Canada':<16} {ys[0]}–{ys[-1]}  ({len(ys)} yrs)  latest={rs[-1]}/100k  [definition differs]")
    except (OSError, KeyError, ValueError) as e:
        print(f"[FAIL] Canada: {e}")

    # ---- indexed series (base = each country's earliest year >= base_year) ----
    BASE_YEAR = 2010
    for c in countries.values():
        yrs, rate = c["years"], c["rate"]
        base = None
        for y, r in zip(yrs, rate):
            if y >= BASE_YEAR and r:
                base = r; break
        c["indexed"] = [round(r / base * 100, 1) if (base and r is not None) else None for r in rate]
        c["base_year"] = next((y for y in yrs if y >= BASE_YEAR), yrs[0] if yrs else None)

    # ---- annotations: legal / recording changes that drive recorded counts ----
    annotations = [
        {"year": 2003, "country": "United Kingdom", "label": "E&W Sexual Offences Act 2003 (broadened definition)"},
        {"year": 2014, "country": "United Kingdom", "label": "E&W recording overhaul (HMIC) — all reports recorded"},
        {"year": 2016, "country": "Germany", "label": "‘Nein heißt Nein’ §177 reform (widened what counts)"},
        {"year": 2018, "country": "France", "label": "Schiappa law; post-#MeToo reporting rise"},
        {"year": 2018, "country": "Sweden", "label": "Consent-based rape law (broadened)"},
        {"year": 2017, "country": "Canada", "label": "#MeToo reporting surge; ‘unfounded’ review changed recording"},
        {"year": 2017, "country": "(all)", "label": "#MeToo — broad increase in willingness to report"},
    ]

    out = {
        "meta": {
            "title": "Recorded sexual-violence trends, indexed",
            "metric": "Police-recorded rate per 100,000, indexed to base year = 100",
            "base_year": BASE_YEAR,
            "caveats": [
                "Levels are NOT comparable across countries: definitions and recording rules differ enormously.",
                "Rising numbers are driven substantially by legal redefinition and greater willingness to report — not necessarily by rising incidence.",
                "Canada has no separate 'rape' offence (folded into sexual assault in 1983); its series uses sexual assault level 1.",
                "This measures RECORDED crime, not victimization, and says nothing about offender origin.",
            ],
        },
        "countries": countries,
        "annotations": annotations,
    }

    (LAKE / "intl_crime_compare.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    js = "window.INTL_CRIME=" + json.dumps(out, ensure_ascii=False) + ";"
    (ROOT / "data" / "intl_crime_compare.js").write_text(js)
    print(f"\nwrote data/intl_crime_compare.js  ({len(countries)} countries)")


if __name__ == "__main__":
    main()
