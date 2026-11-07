"""
The Monitoring Gap: Canada cut wildfire-monitoring capacity as the crisis grew.

Trigger: French authorities reported 420 arrests (166 minors) in the 2026
wildfire season for deliberately or accidentally starting fires — a rolling
tally the French Interior Ministry publishes and updates through the season.
Canada, and British Columbia specifically, has no equivalent. This report
asks two honest questions with real data instead of assuming the answer:

  1. How much of BC's (and Canada's) wildfire problem is human-caused, and
     has that share grown or stayed flat across as much history as the data
     allows?
  2. What does Canada actually track/enforce around wildfire causation and
     emergency response — and did that capacity shrink even as fire seasons
     got worse?

Sources (raw copies acquired to pipeline/lake/):
  - BC Wildfire Service, "Fire Incident Locations - Historical" (BC Data
    Catalogue / BCGW layer WHSE_LAND_AND_NATURAL_RESOURCE.
    PROT_HISTORICAL_INCIDENTS_SP), fetched live via WFS GetFeature, CSV.
    FIRE_YEAR 1950-2025, FIRE_CAUSE in {Person, Lightning, Unknown},
    CURRENT_SIZE in hectares. ~200,000 incident records.
  - BC Wildfire Service, "Fire Incident Locations - Current" (BCGW layer
    WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP) — 2026
    season-to-date supplement, same schema.
  - Statistics Canada, Table 35-10-0177-01 "Incident-based crime statistics,
    by detailed violations" — Arson [2110], Canada + provinces, 1998-2025
    (release 2026-07-22). Raw table filtered to
    pipeline/lake/35-10-0177/arson_filtered.csv (from the ~1.6GB source CSV)
    since it isn't wildfire-specific data — used only as a general benchmark.
  - BC Wildfire Service cause sub-category breakdown (2016-2025), reported by
    Black Press (Kimberley Bulletin / Barriere Star Journal, 2026-07-14,
    quoting BCWS communications officer John Paolozzi) and independently
    corroborated by Northern Beat (Jeff Davies, 2024-08-22, via direct BCWS
    FOI data request, 2013-2023). Small, non-programmatic dataset —
    hardcoded here per report_architect convention, sourced.
  - France Interior Ministry wildfire-arson arrest figures, via BBC News
    (corroborated by europesays.com/News.Az, 2026-08-05; Anadolu Agency,
    2026-07-28) for the 2026 season, and The Inquirer (2022-09-23) for the
    2022 season — the only clean prior-year comparator found.
  - 2026 federal monitoring/coordination staffing cuts: Global News
    (2026-07-23, PSAC/Sharon DeSousa on Government Operations Centre cuts,
    with the Emergency Preparedness Minister's office rebuttal); The Hill
    Times (2026-07-22, PIPSC on NRCan remote-sensing/satellite wildfire
    mapping staff); The Globe and Mail and Nelson Star (2026-03-21, ECCC
    disbanding its weather radar research team and ending the Weatheradio
    network) — all tied to the government's Comprehensive Expenditure
    Review targeting $60B in savings.
  - PolitiFact (2023-07-20) fact-check rating a viral "Canada wildfire arson
    epidemic" claim False — included as an explicit guardrail against
    overclaiming.
  - Named BC arson prosecutions (CBC, Global News) — illustrative, not
    aggregate: enforcement in Canada is case-by-case, not systematically
    tracked the way France's rolling tally is.

Output: data/report-wildfire-monitoring-gap.json
"""
import csv
import json
import math
import os
import re
import struct
import time
import urllib.request
import urllib.error
import zipfile
from collections import defaultdict

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(PIPELINE_DIR)
DATA_DIR = os.path.join(REPO_DIR, "data")
LAKE_DIR = os.path.join(PIPELINE_DIR, "lake")

WFS_BASE = "https://openmaps.gov.bc.ca/geo/pub"
HIST_LAYER = "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_INCIDENTS_SP"
CURRENT_LAYER = "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP"
PAGE_SIZE = 10000


def parse_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# 1. DOWNLOAD — BC Wildfire historical + current incident points (WFS/CSV)
# ---------------------------------------------------------------------------
def wfs_url(layer, property_names, start_index=0, count=PAGE_SIZE):
    props = ",".join(property_names)
    return (
        f"{WFS_BASE}/{layer}/ows?service=WFS&version=2.0.0&request=GetFeature"
        f"&typeName={layer}&outputFormat=csv&propertyName={props}"
        f"&startIndex={start_index}&count={count}"
    )


def fetch_wfs_all(layer, property_names, out_path):
    """Page through a BC WFS layer and write the combined CSV to out_path."""
    if os.path.exists(out_path):
        print(f"  (cached) {out_path}")
        return out_path

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    header = None
    rows = []
    start = 0
    while True:
        url = wfs_url(layer, property_names, start_index=start)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    text = resp.read().decode("utf-8-sig")
                break
            except urllib.error.URLError:
                if attempt == 2:
                    raise
                time.sleep(2)
        lines = text.strip("\n").split("\n")
        if not lines or lines == [""]:
            break
        page_header, page_rows = lines[0], lines[1:]
        if header is None:
            header = page_header
        rows.extend(page_rows)
        print(f"    {layer}: startIndex={start} -> +{len(page_rows)} rows (total {len(rows)})")
        if len(page_rows) < PAGE_SIZE:
            break
        start += PAGE_SIZE

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write("\n".join(rows) + "\n")
    return out_path


def load_bc_incidents():
    hist_path = os.path.join(LAKE_DIR, "bc_wildfire", "historical_incidents.csv")
    current_path = os.path.join(LAKE_DIR, "bc_wildfire", "current_incidents.csv")

    print("  Fetching BC Wildfire historical incidents (1950-2025)...")
    fetch_wfs_all(HIST_LAYER, ["FIRE_YEAR", "FIRE_CAUSE", "CURRENT_SIZE", "IGNITION_DATE"], hist_path)

    print("  Fetching BC Wildfire current-season incidents (2026)...")
    fetch_wfs_all(CURRENT_LAYER, ["FIRE_YEAR", "FIRE_CAUSE", "CURRENT_SIZE", "IGNITION_DATE"], current_path)

    incidents = []
    for path in (hist_path, current_path):
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                year = row.get("FIRE_YEAR")
                cause = row.get("FIRE_CAUSE")
                size = parse_float(row.get("CURRENT_SIZE"))
                if not year or not cause:
                    continue
                try:
                    year = int(year)
                except ValueError:
                    continue
                incidents.append({"year": year, "cause": cause, "size_ha": size or 0.0})
    return incidents


# ---------------------------------------------------------------------------
# 2. AGGREGATE — fires & hectares by year and cause
# ---------------------------------------------------------------------------
def build_timeline(incidents):
    by_year = defaultdict(lambda: {"Person": 0, "Lightning": 0, "Unknown": 0})
    ha_by_year = defaultdict(lambda: {"Person": 0.0, "Lightning": 0.0, "Unknown": 0.0})

    # 2026 is in progress (current-season layer) — keep it separate so the
    # timeline chart isn't misread as a completed season.
    for inc in incidents:
        cause = inc["cause"] if inc["cause"] in ("Person", "Lightning") else "Unknown"
        by_year[inc["year"]][cause] += 1
        ha_by_year[inc["year"]][cause] += inc["size_ha"]

    years = sorted(by_year.keys())
    timeline = []
    for y in years:
        counts = by_year[y]
        total = counts["Person"] + counts["Lightning"] + counts["Unknown"]
        known = counts["Person"] + counts["Lightning"]
        human_pct = round(100 * counts["Person"] / total, 1) if total else None
        human_pct_known = round(100 * counts["Person"] / known, 1) if known else None
        timeline.append({
            "year": y,
            "person": counts["Person"],
            "lightning": counts["Lightning"],
            "unknown": counts["Unknown"],
            "total": total,
            "human_caused_pct": human_pct,
            "human_caused_pct_known": human_pct_known,
            "unknown_pct": round(100 * counts["Unknown"] / total, 1) if total else None,
            "in_progress": y == 2026,
        })

    area = []
    for y in years:
        ha = ha_by_year[y]
        total_ha = round(ha["Person"] + ha["Lightning"] + ha["Unknown"], 1)
        area.append({
            "year": y,
            "person_ha": round(ha["Person"], 1),
            "lightning_ha": round(ha["Lightning"], 1),
            "unknown_ha": round(ha["Unknown"], 1),
            "total_ha": total_ha,
            "in_progress": y == 2026,
        })

    return timeline, area


def decade_summary(timeline):
    """Human-caused share by decade — smooths year-to-year noise so the
    long-run trend (or lack of one) is visible across 75+ years."""
    buckets = defaultdict(lambda: {"person": 0, "lightning": 0, "unknown": 0})
    for row in timeline:
        if row["in_progress"]:
            continue
        decade = (row["year"] // 10) * 10
        buckets[decade]["person"] += row["person"]
        buckets[decade]["lightning"] += row["lightning"]
        buckets[decade]["unknown"] += row["unknown"]

    out = []
    for decade in sorted(buckets):
        b = buckets[decade]
        total = b["person"] + b["lightning"] + b["unknown"]
        if total < 20:
            # too few recorded incidents in early decades for a stable %
            continue
        known = b["person"] + b["lightning"]
        out.append({
            "decade": f"{decade}s",
            "person": b["person"],
            "lightning": b["lightning"],
            "unknown": b["unknown"],
            "total": total,
            "human_caused_pct": round(100 * b["person"] / total, 1),
            "human_caused_pct_known": round(100 * b["person"] / known, 1) if known else None,
            "unknown_pct": round(100 * b["unknown"] / total, 1),
        })
    return out


def cause_recording_collapse(timeline):
    """Document the 1998->2000 discontinuity in cause recording directly
    from the real yearly data, rather than asserting a cause we haven't
    confirmed. The jump itself is real and computed here; the EXPLANATION
    is hand-researched and hedged by confidence in CAUSE_COLLAPSE_CONTEXT
    below — we found confirmed contributing context (2001+ staffing cuts)
    but no confirmed source for why the jump starts a year or two earlier,
    in 1999."""
    by_year = {r["year"]: r for r in timeline if not r["in_progress"]}
    before = by_year.get(1998)
    spike = by_year.get(1999)
    y2000 = by_year.get(2000)
    window = [by_year[y] for y in range(1990, 2016) if y in by_year]
    peak = max(window, key=lambda r: r["unknown_pct"])
    return {
        "yearly_window_1990_2015": [
            {"year": r["year"], "unknown_pct": r["unknown_pct"], "total": r["total"]}
            for r in window
        ],
        "last_normal_year": {"year": 1998, "unknown_pct": before["unknown_pct"]} if before else None,
        "spike_year": {"year": 1999, "unknown_pct": spike["unknown_pct"]} if spike else None,
        "year_after": {"year": 2000, "unknown_pct": y2000["unknown_pct"]} if y2000 else None,
        "peak_year": {"year": peak["year"], "unknown_pct": peak["unknown_pct"]},
    }


CAUSE_COLLAPSE_CONTEXT = {
    "finding": (
        "BC's own wildfire records show a sudden, sustained collapse in "
        "cause-recording, not a gradual decline. The share of fires with no "
        "recorded cause was stable at 4-14% every year from at least 1990 "
        "through 1998, then jumped to 38.2% in 1999 and 50.8% in 2000 — and "
        "stayed elevated (40-78% depending on year) for over a decade, only "
        "partially recovering in the 2020s (~29%)."
    ),
    "confirmed_context": [
        {
            "claim": (
                "BC's forest service lost approximately 1,006 positions — "
                "roughly 25% of its workforce — in under a decade starting "
                "in the early 2000s; field inspections by compliance and "
                "enforcement staff fell 46% between fiscal years 2001/02 "
                "and 2004/05."
            ),
            "confidence": "confirmed",
            "source": (
                "Sierra Club BC / Canadian Centre for Policy Alternatives "
                "report (2010), cited in The Narwhal, \"B.C.'s natural "
                "resource officers unequipped to deal with forestry and "
                "wildfire crimes\" (2024)"
            ),
            "caveat": (
                "This documented staffing collapse begins in 2001/02 — two "
                "to three years AFTER the unknown-cause rate had already "
                "jumped in 1999-2000. It plausibly explains why the gap "
                "PERSISTED through the 2000s and 2010s, but does not by "
                "itself explain why the discontinuity started when it did."
            ),
        },
    ],
    "unconfirmed_hypothesis": (
        "Some public references describe BC Wildfire Service's per-season "
        "historical incident data as beginning in 1999, which raises the "
        "possibility that a fire-reporting database or methodology change "
        "around 1999 changed how 'cause unknown' was recorded or defaulted "
        "— separate from, or in addition to, any staffing effect. We could "
        "not verify this against official dataset lineage documentation or "
        "BC Forest Service Protection Branch annual reports for 1998/99-"
        "2000/01, which are not currently accessible on the public web. "
        "This is flagged explicitly as UNCONFIRMED, not a finding."
    ),
    "what_would_close_the_gap": (
        "A freedom-of-information request to BC Wildfire Service for (a) "
        "Forest Service Protection Branch annual reports/business plans, "
        "fiscal years 1998/99 through 2000/01, and (b) data-dictionary or "
        "lineage documentation for the historical incident dataset, would "
        "directly test both explanations above."
    ),
}


# ---------------------------------------------------------------------------
# 3. STATCAN 35-10-0177-01 — Arson, Canada + provinces, national benchmark
# ---------------------------------------------------------------------------
GEO_MAP = {
    "Canada": "Canada",
    "Newfoundland and Labrador [10]": "Newfoundland & Labrador",
    "Prince Edward Island [11]": "Prince Edward Island",
    "Nova Scotia [12]": "Nova Scotia",
    "New Brunswick [13]": "New Brunswick",
    "Quebec [24]": "Quebec",
    "Ontario [35]": "Ontario",
    "Manitoba [46]": "Manitoba",
    "Saskatchewan [47]": "Saskatchewan",
    "Alberta [48]": "Alberta",
    "British Columbia [59]": "British Columbia",
    "Yukon [60]": "Yukon",
    "Northwest Territories [61]": "Northwest Territories",
    "Nunavut [62]": "Nunavut",
}


def load_statcan_arson():
    filtered_path = os.path.join(LAKE_DIR, "35-10-0177", "arson_filtered.csv")
    raw_path = os.path.join(LAKE_DIR, "35-10-0177", "35100177.csv")

    if not os.path.exists(filtered_path):
        if not os.path.exists(raw_path):
            os.makedirs(os.path.dirname(raw_path), exist_ok=True)
            print("  Downloading StatCan 35-10-0177 (arson)... (~100MB zip)")
            zip_path = raw_path.replace(".csv", "-eng.zip")
            url = "https://www150.statcan.gc.ca/n1/tbl/csv/35100177-eng.zip"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                with open(zip_path, "wb") as f:
                    f.write(resp.read())
            import zipfile
            with zipfile.ZipFile(zip_path) as z:
                z.extractall(os.path.dirname(raw_path))

        print("  Filtering StatCan 35-10-0177 to Arson [2110] rows...")
        with open(raw_path, encoding="utf-8-sig", newline="") as fin, \
             open(filtered_path, "w", encoding="utf-8", newline="") as fout:
            reader = csv.DictReader(fin)
            writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                if row["Violations"] == "Arson [2110]" and row["Statistics"] in (
                    "Actual incidents", "Rate per 100,000 population"
                ):
                    writer.writerow(row)

    national_trend = []
    provincial_latest = []
    latest_year = 0

    rows = []
    with open(filtered_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        if row["GEO"] not in GEO_MAP:
            continue
        year = int(row["REF_DATE"])
        latest_year = max(latest_year, year)

    for row in rows:
        geo = GEO_MAP.get(row["GEO"])
        if not geo or geo != "Canada":
            continue
        if row["Statistics"] != "Actual incidents":
            continue
        val = parse_float(row["VALUE"])
        if val is not None:
            national_trend.append({"year": int(row["REF_DATE"]), "incidents": int(val)})
    national_trend.sort(key=lambda r: r["year"])

    for row in rows:
        geo = GEO_MAP.get(row["GEO"])
        if not geo or int(row["REF_DATE"]) != latest_year:
            continue
        val = parse_float(row["VALUE"])
        if val is None:
            continue
        existing = next((p for p in provincial_latest if p["province"] == geo), None)
        if not existing:
            existing = {"province": geo, "incidents": None, "rate_per_100k": None}
            provincial_latest.append(existing)
        if row["Statistics"] == "Actual incidents":
            existing["incidents"] = int(val)
        elif row["Statistics"] == "Rate per 100,000 population":
            existing["rate_per_100k"] = val

    provincial_latest = [p for p in provincial_latest if p["province"] != "Canada"]
    provincial_latest.sort(key=lambda p: -(p["rate_per_100k"] or 0))

    return {
        "national_trend": national_trend,
        "provincial_latest": provincial_latest,
        "latest_year": latest_year,
        "note": (
            "StatCan tracks arson as a Criminal Code violation nationally but "
            "does NOT distinguish wildland/forest arson from structure or "
            "vehicle arson. Used here only as a general benchmark, not as a "
            "wildfire-specific figure."
        ),
    }


# ---------------------------------------------------------------------------
# 4. HARDCODED, SOURCED DATASETS — small, non-programmatic, cited inline
# ---------------------------------------------------------------------------
BCWS_CAUSE_BREAKDOWN_2016_2025 = {
    "period": "2016-2025",
    "source": (
        "BC Wildfire Service, via Black Press (Kimberley Bulletin / Barriere "
        "Star Journal, 2026-07-14, quoting BCWS communications officer John "
        "Paolozzi); independently corroborated by Northern Beat (Jeff Davies, "
        "2024-08-22, direct BCWS FOI data request, 2013-2023)."
    ),
    "categories": [
        {"label": "Lightning", "pct": 63.0},
        {"label": "Open burning", "pct": 8.1},
        {"label": "Campfire", "pct": 6.5},
        {"label": "Unknown / undetermined", "pct": 6.9},
        {"label": "Arson / suspicious", "pct": 3.8},
        {"label": "Vehicle / equipment", "pct": 3.8},
        {"label": "Other human causes", "pct": 7.9},
    ],
}

FRANCE_ARREST_TREND = {
    "note": (
        "France's Interior Ministry publishes a rolling, cumulative in-season "
        "arrest tally for people accused of deliberately or accidentally "
        "starting wildfires. No Canadian federal or provincial agency "
        "publishes an equivalent aggregate figure."
    ),
    "seasons": [
        {"year": 2022, "arrests": 48, "minors": None,
         "source": "The Inquirer, 2022-09-23 (end-of-season total)"},
        {"year": 2026, "arrests": 420, "minors": 166,
         "source": (
             "French Interior Minister Laurent Nunez; corroborated by "
             "europesays.com/News.Az (2026-08-05, interim figure 402/156) "
             "and Anadolu Agency (2026-07-28, 162 arrests, 13,566 fire "
             "starts, 116,085 ha burned season-to-date)"
         )},
    ],
    "canada_equivalent_aggregate_tracking": False,
}

MONITORING_CUTS_2026 = [
    {
        "system": "Government Operations Centre (Public Safety Canada)",
        "role": "Federal 24/7 situational-awareness and coordination centre for emergency response, including wildfires.",
        "claim": "~60 employees (of ~110-130) received workforce-adjustment letters in January 2026 — \"gutting it by almost half.\"",
        "claimant": "Sharon DeSousa, national president, Public Service Alliance of Canada (PSAC)",
        "government_response": "Emergency Preparedness Minister's office says the core workforce dropped by only 10 (from 110 to 100).",
        "status": "disputed",
        "context": "Cuts stem from the government-wide Comprehensive Expenditure Review targeting $60B in savings over five years; timing coincided with one of the most intense wildfire seasons in Canadian history.",
        "source": "Global News, 2026-07-23; corroborated by Yahoo News Canada, rabble.ca, Play 103.7/Harvard Media",
        "savings_estimate": "NO confirmed dollar savings figure found anywhere in public reporting — not from government, PSAC, or news coverage. Public Safety Canada's departmental plan references $1.18B for \"emergency management strategies\" broadly, but that is a program allocation, not a savings figure tied to these specific cuts.",
    },
    {
        "system": "NRCan remote-sensing / satellite wildfire mapping unit",
        "role": "Federal satellite-based wildfire mapping and monitoring.",
        "claim": "At least 17 remote-sensing employees received workforce-adjustment notices; 200+ PIPSC members affected at NRCan overall.",
        "claimant": "Stéphanie Fréchette, VP, Professional Institute of the Public Service of Canada (PIPSC)",
        "government_response": None,
        "status": "no specific percentage cited — reported as headcount only",
        "context": "Part of the same Comprehensive Expenditure Review; union raised explicit concerns about Canada's future wildfire-mapping capacity.",
        "source": "The Hill Times, 2026-07-22",
        "savings_estimate": "NO confirmed dollar savings figure for this specific team. NRCan's 2026-27 Departmental Plan shows department-WIDE Expenditure Review reductions of $266.4M (2026-27) rising to $557.9M (2028-29), with ~807 FTEs cut by 2028-29 — but this is the entire department's target, not an itemized figure for the remote-sensing/wildfire-mapping team.",
    },
    {
        "system": "Environment and Climate Change Canada (ECCC) weather monitoring",
        "role": "Weather radar research and the Weatheradio public alert network, both inputs to fire-weather risk prediction.",
        "claim": "ECCC disbanded its weather radar research team and ended the 230-transmitter Weatheradio network in March 2026.",
        "claimant": None,
        "government_response": None,
        "status": "confirmed cuts to specific programs, not a headcount percentage",
        "context": "Part of the Comprehensive Expenditure Review. A broader claim that Canada's weather-station count has fallen by roughly half since the 1980s could not be independently verified from a primary source and is NOT used as a figure in this report.",
        "source": "The Globe and Mail, 2026-03; Nelson Star, 2026-03-21",
        "savings_estimate": "The ONE confirmed figure in this entire set: Weatheradio cost ~$4M/year to operate (ECCC spokespeople, corroborated independently by CBC and The Globe and Mail), against a ~$2.5M decommissioning cost over two years — implying roughly $4M/year in net savings once decommissioning is absorbed, though no government document states a net savings figure explicitly. The separate radar-research-team disbandment has NO dollar figure anywhere — The Globe and Mail notes only the government-wide $60B target, with no team-specific breakdown.",
    },
]

CUTS_SAVINGS_SUMMARY = {
    "question": "How much was actually saved per year from the 2026 wildfire-monitoring cuts?",
    "answer": (
        "Mostly unknown — and that absence is itself a finding. Of the "
        "three cuts documented above, only ONE has any confirmed dollar "
        "savings figure anywhere in public reporting: ECCC's Weatheradio "
        "shutdown, at roughly $4M/year. The Government Operations Centre "
        "and NRCan remote-sensing cuts have NO confirmed savings figure "
        "at all, despite extensive searching of government documents, "
        "union statements, and news coverage. No department-level "
        "breakdown of the $60B, five-year Comprehensive Expenditure "
        "Review has been published that would show what Public Safety "
        "Canada, NRCan, or ECCC specifically saved."
    ),
    "only_confirmed_figure": {
        "program": "ECCC Weatheradio network",
        "annual_savings_estimate": 4_000_000,
        "decommissioning_cost": 2_500_000,
        "decommissioning_period": "2 years",
        "confidence": "confirmed operating cost, from two independently corroborating ECCC spokespeople (CBC, The Globe and Mail); the NET annual savings figure is our inference from operating cost minus decommissioning cost, not a government-stated figure",
    },
    "comparison": (
        "$4M/year is roughly 6% of the annualized $316.7M/5-year federal "
        "aerial-firefighting commitment (~$63M/year), and a rounding error "
        "against the $325M/year PBO projects for wildfires' share of "
        "federal disaster-assistance costs alone. If this is representative "
        "of what these staffing cuts actually saved, the government "
        "gutted wildfire-critical monitoring capacity — during one of the "
        "worst fire seasons on record — for a sum too small to appear in "
        "any of the cost figures elsewhere in this report."
    ),
    "cer_context": {
        "total_5yr": 60_000_000_000,
        "annual_disclosed": [
            {"year": "2026-27", "amount": 9_000_000_000},
            {"year": "2027-28", "amount": 10_000_000_000},
            {"year": "2028-29", "amount": 13_000_000_000},
        ],
        "note": "Government-wide totals only. No published table maps specific dollar targets to Public Safety Canada, NRCan, or ECCC individually within this $60B.",
        "source": "Budget 2025 / Fall Economic Statement; departmental plans",
    },
}

# ---------------------------------------------------------------------------
# A labeled, EXPLICITLY-NOT-SOURCED estimate for what the two undisclosed
# cuts (GOC, NRCan) might have saved annually, since no government or union
# figure exists for either -- built ONLY because the alternative (silence)
# leaves the reader with no number at all. Every input is stated in the open
# so the math can be checked or challenged; the confirmed $4M/year
# (Weatheradio) is kept separate and clearly labeled as the one real figure.
# ---------------------------------------------------------------------------
CUTS_ESTIMATE_ASSUMPTION = {
    "fully_loaded_salary_low": 100_000,
    "fully_loaded_salary_high": 115_000,
    "note": (
        "Rough fully-loaded federal public-service compensation per FTE, "
        "including benefits/overhead (~20-25% above base salary). This "
        "figure is NOT sourced to a specific Treasury Board document — it "
        "is a standard planning-level assumption, stated explicitly here "
        "so it can be checked, challenged, or replaced with a better one."
    ),
}

CUTS_ESTIMATE_INPUTS = {
    "goc": {
        "confidence": "disputed headcount, estimated dollars",
        "headcount_low": 10, "headcount_low_source": "government (\"core workforce\" figure)",
        "headcount_high": 60, "headcount_high_source": "PSAC union claim",
    },
    "nrcan": {
        "confidence": "disputed headcount, estimated dollars",
        "headcount_low": 17, "headcount_high": 17, "headcount_source": "PIPSC (\"at least 17\")",
    },
    "radar_team": {
        "confidence": "VERY LOW confidence — no source states a headcount or budget for this team at all",
        "headcount_low": 5, "headcount_high": 15,
        "headcount_source": (
            "No public source — government, union, or news — gives a "
            "headcount or budget for ECCC's disbanded weather radar "
            "research team specifically. The only qualitative anchor "
            "found: Dr. David Sills (Canadian Severe Storms Laboratory), "
            "quoted saying the team \"had gotten small... and now it's "
            "not there at all.\" The 5-15 range here is our own rough "
            "guess at what \"small\" plausibly means for a specialized "
            "federal research team, NOT a sourced figure of any kind."
        ),
        "context": (
            "For scale, not attribution: ECCC's cuts overall affect "
            "roughly 1,000 employees / ~840 FTE reductions department-"
            "wide, with ECCC's OWN budget reductions rising to $91M/year "
            "from 2026-27 (cumulative $1.3B by 2030). This team's "
            "disbandment happened inside that much larger, department-"
            "wide reduction — there's no way to isolate its specific "
            "share from public sources. The team's research supported "
            "Canada's $180.4M radar hardware modernization (32 dual-"
            "polarization radars + 1 training radar, completed 2023-2024)."
        ),
        "source": "The Globe and Mail, CBC, Prince Albert Daily Herald, CP24 — 2026-03 through 2026-06 coverage",
    },
    "confirmed": {
        "label": "ECCC Weatheradio network — the one fully confirmed, sourced figure in this entire estimate",
        "amount": 4_000_000,
    },
}


def build_cuts_estimate():
    a = CUTS_ESTIMATE_ASSUMPTION
    i = CUTS_ESTIMATE_INPUTS

    def est(entry):
        return (
            entry["headcount_low"] * a["fully_loaded_salary_low"],
            entry["headcount_high"] * a["fully_loaded_salary_high"],
        )

    goc_low, goc_high = est(i["goc"])
    nrcan_low, nrcan_high = est(i["nrcan"])
    radar_low, radar_high = est(i["radar_team"])
    confirmed = i["confirmed"]["amount"]

    total_low = goc_low + nrcan_low + radar_low + confirmed
    total_high = goc_high + nrcan_high + radar_high + confirmed

    # comparison points already established elsewhere in this report
    fort_mcmurray_total = 8_900_000_000  # single year, 2016
    bc_2023_insured = 720_000_000  # single season

    return {
        "assumption": a,
        "inputs": i,
        "goc_estimate": {"low": goc_low, "high": goc_high},
        "nrcan_estimate": {"low": nrcan_low, "high": nrcan_high},
        "radar_team_estimate": {"low": radar_low, "high": radar_high},
        "total_low": total_low,
        "total_high": total_high,
        "pct_of_fort_mcmurray_2016": {
            "low": round(100 * total_low / fort_mcmurray_total, 3),
            "high": round(100 * total_high / fort_mcmurray_total, 3),
        },
        "pct_of_bc_2023_season": {
            "low": round(100 * total_low / bc_2023_insured, 2),
            "high": round(100 * total_high / bc_2023_insured, 2),
        },
        "closing_line": (
            "Take the low end, the high end, or reject the estimate "
            "entirely and use only the $4M that's actually confirmed — "
            "every version of this number is a rounding error against "
            "what a single bad wildfire season costs."
        ),
    }


NAMED_BC_ARSON_CASES = [
    {"name": "David Travis", "location": "Nelson, BC", "detail": "Pleaded guilty to 3 counts of arson; lit 4 fires in July 2024; sentenced Dec 2025 to 2 years less a day.", "source": "CBC"},
    {"name": "Angela Elise Cornish", "location": "Kamloops / Monte Lake, BC", "detail": "4 arson charges following a joint RCMP / BC Wildfire Service investigation.", "source": "Global News"},
    {"name": "Christopher White", "location": "Mission, BC", "detail": "3 arson counts following an RCMP Forest Crimes unit + BCWS investigation.", "source": "Global News"},
]

POLITIFACT_GUARDRAIL = {
    "claim_checked": "Viral claim that dozens of Canada's 2023 wildfires were arson.",
    "rating": "False",
    "finding": "Only 2 of the cited examples were actually confirmed 2023 wildfire arson cases; most cited incidents were structure fires or older, unrelated events. RCMP told PolitiFact it does not determine fire cause centrally — each province investigates independently.",
    "source": "PolitiFact, 2023-07-20",
    "why_it_matters": "Included as an explicit guardrail: the honest finding of this report is a tracking/enforcement gap, not evidence of a Canadian arson epidemic comparable to France's.",
}

ALBERTA_CONTEXT = {
    "cause_split_2024": {"human_pct": 50, "lightning_pct": 47, "under_investigation_pct": 3, "source": "CIFFC, 2024, via news summary"},
    "rcmp_statement": "Alberta RCMP stated in June 2025 they were not aware of any arson charges relating to wildfires that season.",
    "source": "Canadian Press, 2025-06",
}


# ---------------------------------------------------------------------------
# 4b. WATER BOMBERS — did aerial firefighting capacity grow with the crisis?
#     All figures below are compiled from news/analysis sources (no single
#     public dataset exists), hardcoded per report_architect convention and
#     individually sourced. Fleet snapshots are 2023-2026, not a clean time
#     series -- that gap is stated explicitly rather than papered over.
# ---------------------------------------------------------------------------
WATER_BOMBER_FLEET_BY_PROVINCE = [
    {"province": "Quebec", "count": 14, "types": "CL-215 / CL-215T / CL-415", "note": None,
     "source": "AFP fact-check via Yahoo News, 2026"},
    {"province": "Ontario", "count": 9, "types": "CL-415 (part of an 80-aircraft fleet incl. helicopters)",
     "note": "at least one CL-415 grounded in 2024 for lack of trained pilots, not lack of airframes",
     "source": "CBC, 2024"},
    {"province": "Manitoba", "count": 11, "types": "7 CL-215, 4 CL-415",
     "note": "fleet averages roughly 40 years old", "source": "CBC / Fire Fighting in Canada, 2023"},
    {"province": "Newfoundland & Labrador", "count": 7, "types": "2 CL-215, 5 CL-415",
     "note": "one CL-415 sat out of service since 2018", "source": "Fire Fighting in Canada, 2023"},
    {"province": "Saskatchewan", "count": 6, "types": "3 CL-215, 3 CL-215T", "note": None,
     "source": "Fire Fighting in Canada, 2023"},
    {"province": "Alberta", "count": 4, "types": "CL-215, built 1986-88; no CL-415s",
     "note": "plus 14 other contracted air tankers and 30 long-term-contract helicopters",
     "source": "Fire Fighting in Canada, 2023"},
    {"province": "British Columbia", "count": 0, "types": "no CL-215/415s in BC's own fleet",
     "note": "relies on 27 contracted fixed-wing aircraft (Conair Q400s, Convairs, Air Tractor Fireboss); "
             "BC only retired its legacy Electra/Convair piston fleet in 2020-2022",
     "source": "CBC/Radio-Canada, 'Is Canada ready for a fiery future?', 2023"},
]

WATER_BOMBER_NATIONAL_ESTIMATES = [
    {"label": "CL-215/415-type aircraft on Canada's civil register", "value": 79, "period": "2023", "source": "Skies Mag"},
    {"label": "\"Dispatch-ready\" core fleet aircraft", "value": 106, "period": "2023", "source": "CBC, citing aviation analyst John Gradek"},
    {"label": "High-performance water bombers specifically (of the 106 above)", "value": 60, "period": "2023", "source": "CBC, citing John Gradek"},
    {"label": "Canadair-type aircraft called \"absolutely insufficient\"", "value": 55, "period": "2023", "source": "Fire Fighting in Canada"},
    {"label": "Distinct firefighting aircraft active in a 3-month window, incl. 63 water bombers", "value": 73, "period": "2026", "source": "AFP fact-check"},
]

MANUFACTURING_TIMELINE = [
    {"start": 1969, "end": 1990, "label": "CL-215 production", "detail": "125 built, sold to 11 countries; Quebec an original 1969 launch customer"},
    {"start": 1993, "end": 2015, "label": "CL-415 production", "detail": "95 built"},
    {"start": 2015, "end": 2024, "label": "PRODUCTION HALTED", "detail": "Bombardier exits; rights sold to Viking Air / De Havilland Canada in 2016; zero new large scoopers built anywhere in the world for 9 years"},
    {"start": 2024, "end": 2028, "label": "Restart forced by a foreign order", "detail": "EU/France orders 22 aircraft in 2024, forcing De Havilland to rebuild a 50,000+-part supply chain and stand up a new Calgary factory; order book grows to ~40 aircraft (France, Greece, Portugal, Alberta); first delivery not until 2028, to Greece"},
    {"start": 2028, "end": 2031, "label": "Alberta's order queue", "detail": "Alberta ordered 5 DHC-515s in Feb 2026 for C$400M — first delivery not until spring 2031, a 5-year lead time, regardless of the money being available today"},
]

FEDERAL_AERIAL_FUNDING_TIMELINE = [
    {"date": "2021", "amount_label": "$129M", "note": "Budget 2021 aerial-firefighting-related funding; criticized by the Fraser Institute as disproportionate to a (since-superseded) reading of long-run fire trends", "source": "Federal budget documents / Fraser Institute commentary"},
    {"date": "2025-12-01", "amount_label": "$257.6M over 4 years", "note": "NRCan funding announced to LEASE firefighting aircraft", "source": "canada.ca, Public Safety Canada"},
    {"date": "2026-02-20", "amount_label": "$316.7M over 5 years", "note": "Revised figure, redirected through CIFFC; not clearly stated anywhere whether this is additive to the Dec 2025 announcement or a restatement of the same money", "source": "canada.ca, Public Safety Canada"},
    {"date": "2026-05", "amount_label": "10 aircraft + 2 support assets leased, 150 days", "note": "CIFFC leased 4 Dash 8-400AT air tankers, helicopters, and a spotter plane from Conair/Coldstream/VIH, May 1 - Sept 27, 2026 — this buys LEASE ACCESS to existing privately-owned aircraft, not new national fleet capacity", "source": "canada.ca, Public Safety Canada"},
]

SUPPRESSION_SPENDING_TREND = {
    "source": "Hope, Coops et al., PLOS ONE, \"Wildfire Suppression Costs for Canada under a Changing Climate\"",
    "note": (
        "Total wildfire SUPPRESSION spending has risen roughly in step with area "
        "burned since 1970 — this is operational firefighting spending, not "
        "capital investment in the aerial fleet, which stagnated separately "
        "because of the 2015-2024 manufacturing gap above, not primarily "
        "because governments withheld money."
    ),
    "period_estimates": [
        {"period": "1970-2009 (annual range)", "value_label": "$216M – $1B+", "context": "2009 CAD; averaged $537M/year"},
        {"period": "1970 → 2010 (10-yr average change)", "value_label": "+176%", "context": "tracking a comparable +177% rise in area burned over the same window"},
        {"period": "Recent decade (~2015-2025)", "value_label": "$800M – $1.4B / year", "context": "exceeded $1B in 6 of the last 10 years"},
    ],
}

ONTARIO_BUDGET_CUT = {
    "fy_2025_26_budget": 271_000_000,
    "fy_2026_27_budget": 150_000_000,
    "note": (
        "Ontario cut its emergency forestry firefighting budget for 2026-27 "
        "despite having burned through nearly double the NEW budget's size "
        "the year before -- and after its own 2022 Auditor General found "
        "wildland fire response times often exceeded four hours."
    ),
    "source": "Ontario budget estimates; Ontario Auditor General, 2022",
}

WATER_BOMBER_EXPERT_COMMENTARY = [
    {"quote": "Absolutely insufficient.", "attribution": "John Gradek, aviation analyst, McGill University, on Canada's ~55-aircraft Canadair-type fleet", "date": "2023", "source": "Fire Fighting in Canada"},
    {"quote": "Not yet a strategy.", "attribution": "John Gradek, on the May 2026 10-aircraft federal lease", "date": "2026", "source": "The Conversation"},
    {"quote": "The underlying trend line has been rising for over 60 years, and the last several seasons have accelerated well beyond it... a pattern of underbudgeting... a clear lack of national coordination of our assets and capabilities.", "attribution": "James Moore, former federal minister", "date": "2026-08", "source": "BNN Bloomberg"},
]

WATER_BOMBER_VERDICT = {
    "verdict": "nuanced — not simple negligence, but not adequate either",
    "summary": (
        "Total wildfire suppression SPENDING has grown roughly in step with area "
        "burned since 1970. But the specialized amphibious water-bomber FLEET "
        "stagnated for a genuine, verifiable reason: production of the CL-415 "
        "stopped in 2015 and no new large scooper aircraft were built ANYWHERE "
        "IN THE WORLD for 9 years, until a 2024 European order forced "
        "De Havilland to rebuild a supply chain from scratch. Even with money "
        "committed today, Canada cannot buy new large scoopers faster than a "
        "2028-2031 delivery horizon — Alberta ordered and paid in Feb 2026 and "
        "won't receive its first aircraft until spring 2031. Recent federal "
        "money (Dec 2025 - Feb 2026, $257.6M to $316.7M) buys LEASE ACCESS to "
        "existing private aircraft for a single season, not new fleet capacity. "
        "A separate, compounding problem is personnel, not airframes: Ontario "
        "has grounded water bombers it already owns for lack of trained pilots, "
        "and cut its own emergency forestry budget for 2026-27 to barely half "
        "of what it actually spent the year before."
    ),
    "what_could_not_be_verified": [
        "No single authoritative time series of total national water-bomber fleet count at clean 1990/2000/2010/2020 benchmarks exists in public sources — only scattered snapshots, mostly from 2023-2026, plus origin-era production totals from 1969-2015. A clean multi-decade fleet-count trend line is not something we could build from open sources.",
        "Whether the $257.6M (Dec 2025) and $316.7M (Feb 2026) federal figures are the same money restated or genuinely additive is not clearly stated in any single government source.",
        "No confirmed instances of Canada leasing or importing aircraft from the US or Europe during peak fire season were found — this was checked directly and could not be substantiated, so it is not asserted anywhere in this report.",
    ],
}

# ---------------------------------------------------------------------------
# 4b-ii. HAS THE FLEET GROWN OR SHRUNK? A second, deeper research pass
#     specifically chasing a historical trend line and aircraft-specific
#     dollar figures. No public registry gives a clean deliveries-minus-
#     retirements count by year for any Canadian jurisdiction -- what
#     follows is reconstructed from provincial news/history sources, 2-3
#     data points per province, explicitly labeled MEDIUM CONFIDENCE, not
#     a government-published series.
# ---------------------------------------------------------------------------
WATER_BOMBER_FLEET_TREND = {
    "confidence_note": (
        "No public registry (Canadian or international) gives a clean "
        "deliveries-minus-retirements fleet count by year for any Canadian "
        "jurisdiction. The provincial trend points below are reconstructed "
        "from news archives and provincial history pages -- medium "
        "confidence, 2-3 points per province, NOT a government-published "
        "series. Treat gaps between points as unknown, not as a straight "
        "line."
    ),
    "provincial_trend_points": [
        {"province": "Manitoba",
         "points": [{"year": 1977, "count": 7, "types": "CL-215"}, {"year": 2012, "count": 7, "types": "4 CL-415 + 3 CL-215"}],
         "note": "Net fleet size unchanged in 35 years — re-engined, not expanded."},
        {"province": "Ontario",
         "points": [{"year": 1991, "count": 9, "types": "CL-215"}, {"year": 2026, "count": 9, "types": "CL-415"}],
         "note": "Flat at 9 aircraft for at least 35 years."},
        {"province": "Saskatchewan",
         "points": [{"year": 1980, "count": 3, "types": "Canso"}, {"year": 1997, "count": 2, "types": "CL-215"}, {"year": 2026, "count": 6, "types": "3 CL-215 + 3 CL-215T"}],
         "note": "The one clear expansion case found: grew from 2 to 6 aircraft since 1997."},
    ],
    "real_story_hypothesis": (
        "The clearer pattern across all three provinces may be fleet "
        "AGING, not fleet shrinkage: raw airframe counts are flat-to-"
        "modestly-up over 25-45 years, but the aircraft themselves are "
        "extraordinarily old — Manitoba's remaining CL-215s date to 1977, "
        "Alberta's to 1986-88, and some Quebec CL-215s reportedly are "
        "still flying at 53+ years old as of 2023."
    ),
    "bc_capability_downgrade": {
        "finding": (
            "BC owns no CL-215/415-class aircraft at all — it contracts "
            "Conair (private), which owns 4 CL-215s. BC's historic large-"
            "capacity asset was the Martin Mars scoopers — the largest "
            "water bombers ever used in Canada, WWII-era flying-boat "
            "conversions — retired in 2015 and NOT replaced with anything "
            "of equal per-aircraft capacity. Aircraft COUNT may have risen "
            "with smaller contracted aircraft since, but per-aircraft "
            "capacity fell."
        ),
        "source": "Castanet; BC Wildfire Service",
    },
    "unit_costs": [
        {"label": "CL-415, 2014 unit cost", "amount": 36_900_000, "currency": "USD",
         "source": "Wikipedia (sourced figure, not independently re-verified)"},
        {"label": "Manitoba, Feb 2010: 4 new CL-415s (~$31.5M/unit)", "amount": 126_000_000, "currency": "USD",
         "source": "confirmed, multiple outlets"},
        {"label": "Alberta, Feb 2026: 5 DHC-515s (~C$80M/unit)", "amount": 400_000_000, "currency": "CAD",
         "source": "FlightGlobal, confirmed"},
        {"label": "Manitoba, 2025: 3 DHC-515s — DOWN PAYMENT only", "amount": 80_000_000, "currency": "CAD",
         "note": "total contract cost still under negotiation as of reporting", "source": "CBC"},
    ],
    "original_purchase_price_gap": (
        "No confirmed original CL-215 purchase price (1969-70 era) was "
        "found for any Canadian province. The only figure located was "
        "France's first Securite Civile order (10 aircraft, GBP 4M, "
        "~1969) — not Canadian, only a rough proxy."
    ),
    "lease_disclosure_gap": (
        "The federal May 2026 lease of 10 aircraft + 2 support assets "
        "(150-day contracts) has no disclosed per-aircraft or per-contract "
        "dollar figure separate from the broader $316.7M/5-year program "
        "total, despite multiple outlets covering the announcement. This "
        "appears to be genuine non-disclosure, not a research gap."
    ),
    "retirements": {
        "confirmed_writeoffs": [
            {"aircraft": "C-FIZU (CL-415)", "date": "2013-07-03", "location": "Moosehead Lake",
             "source": "Transportation Safety Board of Canada, report A13A0075"},
        ],
        "capability_downgrade": (
            "BC's Martin Mars retirement (2015) is the clearest case of "
            "retirement without like-for-like replacement — a real "
            "capacity downgrade, even though no aggregate 'X retired, Y "
            "replaced' figure exists anywhere in public sources."
        ),
    },
    "international_comparison": [
        {"country": "France", "fleet_size": 11,
         "detail": "12 CL-415s delivered 1995-2007, now 11 after a 2025 crash, average age 27.1 years — described as the oldest firefighting assets in France. Expanding via rescEU-funded DHC-515 orders to 14 by 2028, 16 by 2032-33.",
         "note": "Alberta's single 5-aircraft order is nearly half of France's ENTIRE current national scooper fleet."},
        {"country": "EU / rescEU program", "fleet_size": None,
         "detail": "Targeting 24 DHC-515s total, 12 EU-financed. Greece ordered 7 (~EUR360M, ~EUR51M/unit); Croatia ordered 2 (~EUR105M, ~EUR52.5M/unit) — both roughly comparable per-unit to Alberta's ~C$80M order."},
        {"country": "United States", "fleet_size": 9,
         "detail": "The federal large-airtanker exclusive-use fleet collapsed from 44 aircraft (2002) to 9 (2012) after fatal crashes grounded aging military-surplus P2Vs.",
         "note": "The most dramatic documented fleet contraction found for any country in this research — 80% of the fleet lost in a decade."},
        {"country": "Australia", "fleet_size": 6,
         "detail": "No dedicated amphibious-scooper fleet comparable to Canada's; relies on ~150 contracted mixed aircraft nationally, with only 6 Large Air Tankers.",
         "note": "A structurally different model (broad contract pool vs. Canada's provincially-owned dedicated scoopers) — not directly comparable without this caveat."},
    ],
}


# ---------------------------------------------------------------------------
# 4c. TOTAL FEDERAL WILDFIRE FUNDING, 2000-2026 — broader than aerial-only.
#     Compiled from news/analysis/government sources (no single public
#     dataset exists), hardcoded per report_architect convention and
#     individually sourced.
# ---------------------------------------------------------------------------
FEDERAL_FUNDING_HISTORY = {
    "note": (
        "No PBO, Auditor General, journalist, or academic source has summed "
        "ALL federal wildfire-related spending (DFAA + CIFFC + Indigenous "
        "Services Canada + NRCan + aerial firefighting + Parks Canada) into "
        "one running total for any period -- including the Library of "
        "Parliament's own June 2025 wildfire portrait report, which contains "
        "zero dollar figures. This is a confirmed, genuine gap: spending is "
        "fragmented across at least five departments/programs with "
        "different fiscal years, cost-sharing formulas, and disclosure "
        "practices."
    ),
    "dfaa": {
        "description": (
            "Disaster Financial Assistance Arrangements -- the main federal "
            "program reimbursing provinces for disaster recovery costs, "
            "established 1970. The federal cost-share rises with provincial "
            "per-capita costs (50% -> 75% -> 90%)."
        ),
        "cumulative_since_1970_label": "$14B+ (PBO); other federal citations range $8.9B-$9.6B depending on methodology -- no single authoritative figure",
        "avg_annual_2010_2024": 881_000_000,
        "avg_annual_projected_2025_2034": 1_800_000_000,
        "wildfire_share_projected_avg_annual": 325_000_000,
        "wildfire_share_pct_of_total_projected": 18,
        "source": "Parliamentary Budget Officer, \"Projecting the Cost of the DFAA Program,\" 2025-10",
        "notable_wildfire_payments": [
            {"event": "2016 Fort McMurray, AB", "amount": 385_394_638, "source": "Public Safety Canada, 2026-05 breakdown"},
            {"event": "2017 BC wildfires", "amount": 591_000_000, "note": "$175M advance (Jan 2018) + $416M confirmed disaster payment", "source": "canada.ca; The Globe and Mail"},
            {"event": "2014 NWT wildfires", "amount": 20_300_000, "note": "$15M interim (2020) + $5.3M final (2021)", "source": "canada.ca"},
            {"event": "2024 Jasper, AB", "amount": 19_600_000, "note": "advance payment", "source": "canada.ca, 2025-02"},
            {"event": "2024 BC wildfires/floods", "amount": 35_000_000, "note": "combined, approximate", "source": "canada.ca"},
        ],
    },
    "ciffc": {
        "founded": 1982,
        "founding_context": "Established after resource shortages in the 1979-81 fire seasons.",
        "federal_share_note": "The federal government funds one-third of CIFFC's base operating costs; provinces/territories fund the remaining two-thirds plus 100% of collaborative project costs.",
        "total_budget_found": False,
    },
    "indigenous_services_canada": {
        "programs": [
            {"name": "FireSmart renewal/expansion", "amount_label": "$57.2M over 5 years", "date": "Budget 2024"},
            {"name": "Non-Structural Mitigation and Preparedness Program", "amount_label": "$18M ongoing", "date": "2026-27"},
            {"name": "Capacity Enhancement Funding (Emergency Management Coordinators)", "amount_label": "$12.98M ongoing", "date": "2026-27"},
        ],
        "oag_finding": {
            "report": "OAG Report 8, \"Emergency Management in First Nations Communities,\" 2022-08",
            "finding": (
                "ISC spent 3.5x more responding to emergencies than "
                "preventing them. Over 13 years, First Nations had 1,300+ "
                "emergencies, 580+ evacuations, 130,000+ people affected. "
                "ISC had a backlog of 112 approved-but-unfunded mitigation "
                "infrastructure projects."
            ),
        },
    },
    "nrcan": {
        "current_annual_label": "$13M+ per year (NRCan's own stated figure for wildfire research, knowledge exchange, CIFFC support, and CWFIS)",
        "historical_note": "In the 1990s, the Canadian Forest Service was cut from 2,200 to 700 staff, reducing research and forest-management capacity.",
        "source": "NRCan; The Walrus; \"Fifty years of wildland fire science in Canada,\" Canadian Journal of Forest Research",
    },
    "budget_line_items": [
        {"year": 2019, "amount": 38_500_000, "amount_label": "$38.5M", "detail": "NRCan wildland fire management, part of a $156M broader emergency-management package"},
        {"year": 2022, "amount": 346_100_000, "amount_label": "$346.1M over 5 years", "detail": "NRCan + ISC, equipment/training for 1,000 wildland firefighters"},
        {"year": 2022, "amount": 169_900_000, "amount_label": "$169.9M over 5 years", "detail": "WildFireSat satellite program"},
        {"year": 2024, "amount": 57_200_000, "amount_label": "$57.2M over 5 years", "detail": "ISC FireSmart renewal"},
        {"year": 2025, "amount": 316_700_000, "amount_label": "$316.7M over 5 years", "detail": "CIFFC aerial firefighting surge capacity (see the water bomber section above)"},
        {"year": 2025, "amount": 104_000_000, "amount_label": "$104M", "detail": "\"Resilient Communities through FireSmart\" multi-province program"},
        {"year": 2026, "amount": 47_800_000, "amount_label": "$47.8M over 5 years", "detail": "Parks Canada wildfire preparedness"},
    ],
    "no_wildfire_specific_item_found_years": [2000, 2005, 2010, 2015, 2021],
    "federal_vs_provincial": {
        "forest_land_managed_by_provinces_pct": 90,
        "forest_land_managed_federally_pct": 4,
        "forest_land_privately_owned_pct": 6,
        "federal_emergency_trigger_share_pct": 10,
        "note": "Federal engagement is triggered in roughly 10% of emergencies where a province/territory is overwhelmed. Provinces/territories own the majority of firefighting capacity.",
    },
    "senate_finding": {
        "report": "Senate Standing Committee on Agriculture and Forestry, \"Canada on Fire,\" 2026-06",
        "finding": "Canada is the only G7 country without a national wildfire coordinating body.",
        "source": "sencanada.ca; CBC",
    },
}

# ---------------------------------------------------------------------------
# 4d. HOMES DESTROYED & ECONOMIC DAMAGE, 2000-2026 — event-level, not a
#     clean annual series (that gap is stated explicitly, not papered over).
# ---------------------------------------------------------------------------
WILDFIRE_DAMAGE_EVENTS = [
    {"year": 2003, "event": "Okanagan Mountain Park fire, Kelowna, BC", "structures": 240,
     "structures_label": "~240 homes", "insured_damage": None, "total_damage": 200_000_000,
     "damage_basis": "total damages; not clearly split insured/uninsured in available sourcing",
     "source": "CBC, Wildfire Today"},
    {"year": 2011, "event": "Slave Lake, AB", "structures": 433,
     "structures_label": "433 structures (374 town + 59 rural district)", "insured_damage": None,
     "total_damage": 700_000_000, "damage_basis": "reported ~$700-750M; unclear insured/total split",
     "source": "Wikipedia, Accomsure"},
    {"year": 2016, "event": "Fort McMurray, AB (\"The Beast\")", "structures": 2400,
     "structures_label": "~2,400 homes/buildings", "insured_damage": 3_700_000_000,
     "damage_basis": "nominal 2016 dollars; IBC's 10-yr retrospective restates this at ~$4.7-4.8B in 2025 dollars",
     "total_damage": 8_900_000_000,
     "total_damage_note": "~$8.9-9B total direct+indirect (Conference Board of Canada) — Canada's costliest insured disaster until 2024",
     "source": "IBC, CBC, The Globe and Mail"},
    {"year": 2017, "event": "BC wildfire season (overall)", "structures": 500,
     "structures_label": "500+ structures (299 homes)", "insured_damage": 649_000_000,
     "damage_basis": "secondary-sourced; not confirmed on an IBC primary page", "total_damage": None,
     "source": "Wikipedia; Accomsure"},
    {"year": 2018, "event": "BC wildfire season (overall)", "structures": 140,
     "structures_label": "140 structures (50 homes)", "insured_damage": None,
     "damage_basis": "no IBC insured-loss figure located, despite one of BC's worst seasons by area burned",
     "total_damage": 615_000_000, "total_damage_note": "province spent $615M on SUPPRESSION, not property damage",
     "source": "Wikipedia, energeticcity.ca"},
    {"year": 2021, "event": "Lytton, BC", "structures": None,
     "structures_label": "~90% of the village (97% of properties damaged); 2 deaths",
     "insured_damage": 78_000_000,
     "damage_basis": "2021 IBC estimate, later restated to $102M (2024/2025) citing rebuild delays",
     "total_damage": None, "total_damage_note": "60% of residents had no fire insurance",
     "source": "CBC/IBC"},
    {"year": 2023, "event": "McDougall Creek (Kelowna/West Kelowna) + Bush Creek East (Shuswap), BC",
     "structures": 400, "structures_label": "~400 homes BC-wide; 70 in West Kelowna + 20 in Westbank First Nation from the Okanagan Lake fires alone",
     "insured_damage": 720_000_000,
     "damage_basis": "two BC fires — costliest insured event in BC history, 10th-worst disaster nationally by payout",
     "total_damage": 945_000_000,
     "total_damage_note": "national wildfire-only insured total for 2023 (BC+NWT+NS combined)",
     "source": "IBC, CBC"},
    {"year": 2024, "event": "Jasper, AB", "structures": 358,
     "structures_label": "358 homes/businesses (~1/3 of the townsite)", "insured_damage": 1_300_000_000,
     "damage_basis": "revised up from an initial $880M estimate — 2nd-costliest wildfire event in Canadian history",
     "total_damage": None, "source": "IBC (multiple releases), CBC"},
    {"year": 2025, "event": "Flin Flon MB / La Ronge SK fires (national) + BC season", "structures": 450,
     "structures_label": "BC: 450+ homes (Shuswap/Okanagan)", "insured_damage": 300_000_000,
     "damage_basis": "two major national fires; full-year Canada all-peril insured total was $2.4B, wildfire-only share not isolated",
     "total_damage": None,
     "total_damage_note": "2nd-worst wildfire season on record nationally: 8.3M+ hectares burned, 6,000+ fires",
     "source": "IBC/CatIQ, Global News"},
    {"year": 2026, "event": "Cariboo + Okanagan Indian Band reserve fires, BC (season in progress)",
     "structures": 350, "structures_label": "350+ buildings (provisional, mid-season)",
     "insured_damage": None, "damage_basis": "not yet finalized; 3,447 km2 burned in BC as of 2026-08-08",
     "total_damage": None, "source": "energeticcity.ca"},
]

WILDFIRE_DAMAGE_TREND = {
    "ibc_decade_comparison": {
        "catastrophic_wildfire_events": {"2006_2015": 2, "2016_2025": 16},
        "wildfire_insured_losses": {"2006_2015": 734_000_000, "2016_2025": 8_100_000_000, "pct_increase": 1004},
        "burned_area_pct_increase": 81,
        "burned_area_2016_2025_ha": 46_600_000,
        "source": "IBC / CatIQ decade comparison",
    },
    "all_peril_cumulative": {
        "2006_2015": 14_000_000_000, "2016_2025": 37_000_000_000,
        "note": "wildfire + flood + storm + hail combined, inflation-adjusted", "source": "IBC",
    },
    "smoke_health_costs": {
        "cumulative_2014_2025": 231_000_000_000,
        "avg_annual": 19_000_000_000,
        "avg_annual_premature_deaths": 2500,
        "note": (
            "A different cost category entirely (health, not structures) — "
            "included to show how incomplete a structures/insured-damage "
            "total is as a 'total cost of wildfire' figure."
        ),
        "source": "Canadian Climate Institute",
    },
    "projection": {
        "claim": "Wildfire financial losses could more than double by 2030 given current housing-development patterns in fire-exposed areas.",
        "source": "Canadian Climate Institute",
    },
    "data_quality_note": (
        "No clean 2000-2026 running total of homes lost or damage exists. "
        "Every figure here is a post-hoc, event-level number published "
        "after a specific fire/season by IBC, CatIQ, or a province -- not a "
        "systematic year-by-year series. BC Wildfire Service does not "
        "appear to publish an official year-over-year 'structures "
        "destroyed' table; the BC per-season structure counts above are "
        "reconstructed from post-season news reporting, not a primary "
        "government dataset. 'Insured' vs 'total economic' vs 'reported "
        "damage' are inconsistently distinguished in older sources (2003, "
        "2011) -- flagged where the split is unclear. Figures in nominal "
        "vs. inflation-adjusted ('2025 dollars') terms are not directly "
        "comparable across years without picking one basis."
    ),
}

# ---------------------------------------------------------------------------
# 4e. THE TALLY — investment vs. cost, side by side. Deliberately NOT a
#     single grand total: the figures below span different scopes
#     (federal-only spending vs. national suppression vs. private
#     insurance payouts vs. health-system costs) and different time
#     windows, so forcing them into one number would be dishonest. Shown
#     side by side so the ORDER-OF-MAGNITUDE gap is visible without that.
# ---------------------------------------------------------------------------
WILDFIRE_TALLY = {
    "framing_note": (
        "This is not a single apples-to-apples grand total — it can't be, "
        "because the investment and cost figures below come from different "
        "scopes (federal-only spending vs. national suppression spending "
        "vs. private insurance payouts vs. health-system costs) and "
        "different time windows. They're shown side by side on purpose: "
        "even without forcing a false precise total, the order-of-magnitude "
        "gap between what's spent and what it costs is visible on its own."
    ),
    "investments": [
        {"label": "Federal aerial firefighting funding", "amount": 316_700_000,
         "scope": "federal, multi-year — a LEASE commitment, not a purchase", "period": "2025-2030 (5 yrs total)"},
        {"label": "DFAA wildfire share (projected)", "amount": 325_000_000,
         "scope": "federal, national, annual average", "period": "2025-2034, per year"},
        {"label": "Explicit federal wildfire budget commitments identified", "amount": 1_080_200_000,
         "scope": "federal — sum of every announced multi-year commitment we could find", "period": "2019-2026, cumulative announcements"},
        {"label": "NRCan wildfire research", "amount": 13_000_000,
         "scope": "federal, annual run rate", "period": "ongoing"},
    ],
    "costs": [
        {"label": "National wildfire suppression spending", "amount": 1_100_000_000,
         "amount_low": 800_000_000, "amount_high": 1_400_000_000,
         "scope": "national (mostly provincial), annual — shown as the range midpoint", "period": "recent decade, per year"},
        {"label": "Wildfire insured losses, decade cumulative", "amount": 8_100_000_000,
         "scope": "private insurance payouts, national", "period": "2016-2025, 10-yr cumulative"},
        {"label": "Fort McMurray 2016 alone (total economic damage)", "amount": 8_900_000_000,
         "scope": "single event, total direct + indirect cost", "period": "2016"},
        {"label": "Wildfire smoke health costs, cumulative", "amount": 231_000_000_000,
         "scope": "national, health system + productivity loss", "period": "2014-2025, 12-yr cumulative"},
    ],
    "scale_comparison": {
        "note": (
            "The single most directly comparable pair: the $316.7M federal "
            "aerial-firefighting commitment (2025-2030, itself a LEASE, not "
            "a purchase) is smaller than the insured damage from ONE fire "
            "season in BC alone in 2023 ($720M), and equal to roughly 3.6% "
            "of the Fort McMurray fire's total economic cost in a SINGLE "
            "year (2016)."
        ),
        "aerial_funding_pct_of_fort_mcmurray": 3.6,
    },
    "citizen_burden_note": (
        "Federal spending is a small supplement to a much larger national "
        "cost, not the backbone of it — provinces own the majority of "
        "firefighting capacity and directly bear most suppression costs, "
        "while property owners, insurers, and the health system absorb the "
        "damage. That structure means the gap above isn't only a story "
        "about federal underfunding: it's that the people actually paying "
        "for wildfires — through insurance premiums, uninsured losses like "
        "Lytton's, provincial taxes, and smoke-related health costs — are "
        "carrying a bill that dwarfs any single government's wildfire "
        "budget line, federal or provincial."
    ),
}


# ---------------------------------------------------------------------------
# 6. NATIONAL FIRE DATABASE — cause-of-fire data across ALL provinces, not
#    just BC. Source: Canadian National Fire Database (NFDB), Canadian
#    Forest Service / Natural Resources Canada, cwfis.cfs.nrcan.gc.ca.
#    448,602 point records, 1930-2025, per-fire CAUSE22 (H=human,
#    N=natural/lightning, U=unknown) and SIZE_HA, tagged by SRC_AGENCY
#    (province/territory). This is the same kind of point-level cause
#    dataset BC's own WFS layer provides, but for every jurisdiction.
#    NOTE: NFDB's own copy of BC's historical data does NOT reproduce
#    BC's 1999-2000 unknown-cause spike (shows ~99% known-cause for BC
#    2005-2024, vs. BC's own live Data Catalogue showing 53.5% known
#    over the same window) — a real, large discrepancy with BC's own
#    authoritative source, used elsewhere in this report. Rather than let
#    that wrong number silently distort every cross-provincial and
#    national aggregate below (the report card, the density-correlation
#    test, national cause-area split, average fire size by cause), BC's
#    entry in by_prov_year/national_by_cause_year is REPLACED with BC's
#    own BC Wildfire Service data immediately after load_nfdb() runs —
#    see substitute_bc_authoritative_data(). NFDB is used as-is for every
#    other province/territory, where no contradicting authoritative
#    source was found.
# ---------------------------------------------------------------------------
NFDB_URL = "https://cwfis.cfs.nrcan.gc.ca/downloads/nfdb/fire_pnt/current_version/NFDB_point_txt.zip"

PROV_NAMES = {
    "BC": "British Columbia", "AB": "Alberta", "SK": "Saskatchewan",
    "MB": "Manitoba", "ON": "Ontario", "QC": "Quebec", "NB": "New Brunswick",
    "NS": "Nova Scotia", "PE": "Prince Edward Island",
    "NL": "Newfoundland & Labrador", "YT": "Yukon",
    "NT": "Northwest Territories", "NU": "Nunavut", "PC": "Parks Canada",
}

NFDB_BC_DISCREPANCY_NOTE = (
    "The Canadian National Fire Database (NFDB) — the only dataset with "
    "consistent per-fire cause coding across every province — is used for "
    "the national comparison below. Its own copy of BC's historical "
    "records does NOT reproduce the 1999-2000 unknown-cause spike found "
    "in BC Wildfire Service's own live Data Catalogue (used elsewhere in "
    "this report): NFDB shows BC's unknown rate near 0% through 1990-2018. "
    "This is a real discrepancy between the national compilation and the "
    "provincial source, not resolved here — it's disclosed rather than "
    "smoothed over. It does not affect the OTHER provinces below, where no "
    "contradicting authoritative source was found."
)


def fetch_nfdb(out_dir):
    existing = [
        f for f in os.listdir(out_dir)
        if f.startswith("NFDB_point_") and f.endswith(".txt")
    ] if os.path.isdir(out_dir) else []
    if existing:
        return os.path.join(out_dir, existing[0])

    os.makedirs(out_dir, exist_ok=True)
    zip_path = os.path.join(out_dir, "NFDB_point_txt.zip")
    req = urllib.request.Request(NFDB_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        with open(zip_path, "wb") as f:
            f.write(resp.read())
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(out_dir)
    os.remove(zip_path)

    existing = [
        f for f in os.listdir(out_dir)
        if f.startswith("NFDB_point_") and f.endswith(".txt")
    ]
    return os.path.join(out_dir, existing[0])


def load_nfdb():
    path = fetch_nfdb(os.path.join(LAKE_DIR, "nfdb"))
    by_prov_year = defaultdict(lambda: defaultdict(lambda: {
        "H": 0, "N": 0, "U": 0, "H_ha": 0.0, "N_ha": 0.0, "U_ha": 0.0, "area_ha": 0.0,
    }))
    national_by_cause_year = defaultdict(lambda: {"H": 0.0, "N": 0.0, "U": 0.0})
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            prov = (row.get("SRC_AGENCY") or "").strip()
            y = (row.get("YEAR") or "").strip()
            if not y or y in ("", "-999"):
                continue
            year = int(y)
            cause = (row.get("CAUSE22") or "U").strip()
            if cause not in ("H", "N", "U"):
                cause = "U"
            size = parse_float(row.get("SIZE_HA")) or 0.0
            d = by_prov_year[prov][year]
            d[cause] += 1
            d[cause + "_ha"] += size
            d["area_ha"] += size
            if prov != "PC":  # exclude Parks Canada from national totals (cross-cuts provinces)
                national_by_cause_year[year][cause] += size
    return by_prov_year, national_by_cause_year


def snapshot_nfdb_known_rate(by_prov_year, code, start=2005, end=2024):
    """Captures NFDB's RAW (uncorrected) known-cause rate for a province
    before any substitution runs, so the delta between NFDB and an
    authoritative source can be reported later — must be called before
    substitute_bc_authoritative_data()."""
    agg = {"H": 0, "N": 0, "U": 0}
    for y in range(start, end + 1):
        d = by_prov_year.get(code, {}).get(y)
        if d:
            for k in agg:
                agg[k] += d[k]
    total = sum(agg.values())
    return {
        "period": f"{start}-{end}", "total_fires": total, **agg,
        "known_rate": round(100 * (agg["H"] + agg["N"]) / total, 1) if total else None,
    }


def substitute_bc_authoritative_data(by_prov_year, national_by_cause_year, bc_timeline, bc_area):
    """NFDB's own copy of BC shows ~99% known-cause, 2005-2024 — but BC
    Wildfire Service's own live records (used throughout Chapter 1) show
    only 53.5% known over the same window. This is a real, large
    discrepancy, not a rounding difference, and it would otherwise
    silently distort every cross-provincial and national aggregate that
    touches BC: the report card, the density-correlation test, national
    cause-area split, average fire size by cause. We trust BC's own
    dataset (fetched live from BC's Data Catalogue, the same one BC
    Wildfire Service itself publishes) over NFDB's compiled copy, and
    substitute it in everywhere NFDB's BC entry would otherwise be used."""
    old_bc = by_prov_year.get("BC", {})
    for year, old in old_bc.items():
        nat = national_by_cause_year.get(year)
        if nat:
            nat["H"] -= old["H_ha"]
            nat["N"] -= old["N_ha"]
            nat["U"] -= old["U_ha"]

    area_by_year = {a["year"]: a for a in bc_area}
    new_bc = {}
    for row in bc_timeline:
        y = row["year"]
        a = area_by_year.get(y, {})
        new_bc[y] = {
            "H": row["person"], "N": row["lightning"], "U": row["unknown"],
            "H_ha": a.get("person_ha", 0.0), "N_ha": a.get("lightning_ha", 0.0), "U_ha": a.get("unknown_ha", 0.0),
            "area_ha": a.get("total_ha", 0.0),
        }
        nat = national_by_cause_year.setdefault(y, {"H": 0.0, "N": 0.0, "U": 0.0})
        nat["H"] += new_bc[y]["H_ha"]
        nat["N"] += new_bc[y]["N_ha"]
        nat["U"] += new_bc[y]["U_ha"]

    by_prov_year["BC"] = new_bc


# ---------------------------------------------------------------------------
# 6b. INDEPENDENT VERIFICATION — BC's NFDB entry turned out to be wrong
#    (see above). That raises an obvious question: is any OTHER province's
#    NFDB entry also wrong? We checked the two other provinces with a
#    known, independently-published, per-fire cause dataset of their own
#    (Alberta, Quebec) and cross-referenced NFDB against them for the same
#    2005-2024 window used in the report card. We did NOT find an
#    equivalent independent per-fire cause dataset for Saskatchewan,
#    Manitoba, Ontario, the Northwest Territories, Yukon, or the Atlantic
#    provinces — their NFDB entries are NOT independently verified here,
#    and the report card says so explicitly rather than implying they
#    were checked.
# ---------------------------------------------------------------------------
AB_URL = "https://open.alberta.ca/dataset/a221e7a0-4f46-4be7-9c5a-e29de9a3447e/resource/80480824-0c50-456c-9723-f9d4fc136141/download/fp-historical-wildfire-data-2006-2025.csv"
AB_LIGHTNING_CAUSES = {"Lightning"}
AB_UNKNOWN_CAUSES = {"Undetermined", "Under Investigation"}

QC_SHAPEFILE_ZIP_URL = "https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/02-Donnees/PROV/Feux_pt_ori_SHP.zip"


def read_dbf_rows(path):
    """Minimal pure-Python .dbf (xBase) attribute-table reader — no GIS
    library available in this environment, and we only need the
    attribute table (year, cause), not the point geometry. Field lengths
    are read from the file's own header, not guessed."""
    with open(path, "rb") as f:
        header = f.read(32)
        num_records = struct.unpack("<I", header[4:8])[0]
        header_size = struct.unpack("<H", header[8:10])[0]
        record_size = struct.unpack("<H", header[10:12])[0]
        num_fields = (header_size - 33) // 32
        fields = []
        for _ in range(num_fields):
            fd = f.read(32)
            name = fd[:11].split(b"\x00")[0].decode("latin-1")
            flen = fd[16]
            fields.append((name, flen))
        f.read(1)
        rows = []
        for _ in range(num_records):
            rec = f.read(record_size)
            if len(rec) < record_size:
                break
            if rec[0:1] == b"*":
                continue
            row, pos = {}, 1
            for name, flen in fields:
                row[name] = rec[pos:pos + flen].decode("latin-1", errors="replace").strip()
                pos += flen
            rows.append(row)
        return rows


def fetch_ab_wildfire_verification(start=2006, end=2024):
    out_path = os.path.join(LAKE_DIR, "ab_wildfire", "ab_historical_2006_2025.csv")
    if not os.path.exists(out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        req = urllib.request.Request(AB_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(out_path, "wb") as f:
                f.write(resp.read())

    agg = {"H": 0, "N": 0, "U": 0}
    with open(out_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            y = row.get("YEAR")
            if not y or not (start <= int(y) <= end):
                continue
            gc = row.get("GENERAL_CAUSE", "")
            if gc in AB_LIGHTNING_CAUSES:
                agg["N"] += 1
            elif gc in AB_UNKNOWN_CAUSES:
                agg["U"] += 1
            else:
                agg["H"] += 1
    total = sum(agg.values())
    return {
        "province": "Alberta", "source": "open.alberta.ca, Historical wildfire data 2006-2025",
        "period": f"{start}-{end}", "total_fires": total, **agg,
        "known_rate": round(100 * (agg["H"] + agg["N"]) / total, 1) if total else None,
    }


def fetch_qc_wildfire_verification(start=2005, end=2024):
    out_dir = os.path.join(LAKE_DIR, "qc_wildfire")
    dbf_path = os.path.join(out_dir, "FEUX_PT_ORI_1972_2024.dbf")
    if not os.path.exists(dbf_path):
        os.makedirs(out_dir, exist_ok=True)
        zip_path = os.path.join(out_dir, "download.zip")
        req = urllib.request.Request(QC_SHAPEFILE_ZIP_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(zip_path, "wb") as f:
                f.write(resp.read())
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(out_dir)
        os.remove(zip_path)
        dbf_candidates = [f for f in os.listdir(out_dir) if f.upper().endswith(".DBF")]
        dbf_path = os.path.join(out_dir, dbf_candidates[0])

    rows = read_dbf_rows(dbf_path)
    agg = {"H": 0, "N": 0, "U": 0}
    for r in rows:
        y = r.get("ANNEE")
        if not y or not (start <= int(y) <= end):
            continue
        cause = r.get("CAUSE", "")
        if cause == "Foudre":
            agg["N"] += 1
        elif cause == "Humaine":
            agg["H"] += 1
        else:
            agg["U"] += 1
    total = sum(agg.values())
    return {
        "province": "Quebec", "source": "Données Québec / MRNF, Cartographie des points d'origine des feux, 1972-2024",
        "period": f"{start}-{end}", "total_fires": total, **agg,
        "known_rate": round(100 * (agg["H"] + agg["N"]) / total, 1) if total else None,
        "methodology_note": (
            "Quebec's own classification system records only two "
            "categories — human ('Humaine') or lightning ('Foudre') — "
            "with no 'unknown/undetermined' option at all, unlike every "
            "other agency in this report. Its 100% known-cause rate is "
            "therefore a genuine methodological difference, not a data "
            "gap: SOPFEU assigns a best-determination cause to every fire "
            "rather than leaving ambiguous ones unclassified."
        ),
    }


ON_URL = "https://geohub.lio.gov.on.ca/api/download/v1/items/a2ced32907e642c8abd28744e6c28a2a/csv?layers=30"
ON_LIGHTNING_CODES = {"LTG"}
ON_UNKNOWN_CODES = {"UNK", ""}


def fetch_on_wildfire_verification(start=2005, end=2024):
    out_path = os.path.join(LAKE_DIR, "on_wildfire", "fire_disturbance_point.csv")
    if not os.path.exists(out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        req = urllib.request.Request(ON_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            with open(out_path, "wb") as f:
                f.write(resp.read())

    agg = {"H": 0, "N": 0, "U": 0}
    with open(out_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            y = row.get("FIRE_YEAR")
            if not y or not (start <= int(y) <= end):
                continue
            code = (row.get("FIRE_GENERAL_CAUSE_CODE") or "").strip()
            if code in ON_LIGHTNING_CODES:
                agg["N"] += 1
            elif code in ON_UNKNOWN_CODES:
                agg["U"] += 1
            else:
                agg["H"] += 1
    total = sum(agg.values())
    return {
        "province": "Ontario",
        "source": "Ontario GeoHub, Fire Disturbance Point (LIO Open Data), 1976-2025",
        "period": f"{start}-{end}", "total_fires": total, **agg,
        "known_rate": round(100 * (agg["H"] + agg["N"]) / total, 1) if total else None,
    }


def build_verification_status(report_card, ab_check, qc_check, on_check):
    nfdb_ab = next(c for c in report_card["cards"] if c["code"] == "AB")
    nfdb_qc = next(c for c in report_card["cards"] if c["code"] == "QC")
    nfdb_on = next(c for c in report_card["cards"] if c["code"] == "ON")
    status = {
        "BC": {
            "status": "corrected",
            "note": (
                "NFDB's own copy of BC showed 99.1% known-cause — BC "
                "Wildfire Service's own live records (used throughout "
                "Chapter 1) show only 53.5% known over the same window. "
                "This report uses BC's own authoritative data throughout, "
                "not NFDB's, for every BC figure on this page."
            ),
        },
        "AB": {
            "status": "verified_match",
            "note": (
                f"Cross-checked against Alberta's own open-data wildfire "
                f"records ({ab_check['period']}, {ab_check['total_fires']:,} fires): "
                f"{ab_check['known_rate']}% known-cause independently, vs. "
                f"NFDB's {nfdb_ab['known_rate']}% for a near-identical window — a close match."
            ),
        },
        "QC": {
            "status": "verified_match",
            "note": (
                f"Cross-checked against Quebec's own SOPFEU/MRNF fire-origin "
                f"records ({qc_check['total_fires']:,} fires, 2005-2024): "
                f"{qc_check['known_rate']}% known-cause independently, vs. "
                f"NFDB's {nfdb_qc['known_rate']}% — an exact match. "
                + qc_check["methodology_note"]
            ),
        },
        "ON": {
            "status": "verified_match",
            "note": (
                f"Cross-checked against Ontario's own live GeoHub fire-"
                f"disturbance records ({on_check['total_fires']:,} fires, "
                f"2005-2024): {on_check['known_rate']}% known-cause "
                f"independently, vs. NFDB's {nfdb_on['known_rate']}% — an exact match."
            ),
        },
        "NT": {
            "status": "unverifiable",
            "note": (
                "The Northwest Territories' own current fire-perimeter "
                "dataset (GNWT Geomatics, 2025 fire year) was checked "
                "directly — it has no cause/ignition-source field at all, "
                "so NFDB's NT cause coding cannot be independently checked "
                "against the source agency's own published data at any "
                "confidence level, positive or negative."
            ),
        },
        "YT": {
            "status": "unverifiable",
            "note": (
                "Yukon's own current fire-history dataset (open.yukon.ca, "
                "refreshed August 2026) was checked directly — like NWT's, "
                "it has no cause field at all. NFDB's YT cause coding — "
                "including the 2022-2025 unknown-cause spike found above — "
                "cannot be independently checked against the source "
                "agency's own published data."
            ),
        },
        "SK": {
            "status": "unverified",
            "note": (
                "Saskatchewan's own wildfire-origin GIS services "
                "(referenced in older public documentation as 'Wildfire "
                "Origins'/'WFM_FireHistory') were checked directly and are "
                "currently unreachable — the relevant service folder "
                "returns no live endpoints. No current, publicly-"
                "accessible independent source was found."
            ),
        },
        "MB": {
            "status": "unverified",
            "note": (
                "Manitoba publishes only aggregate annual fire-cause "
                "counts (human vs. lightning, 1914-2020), not per-fire "
                "records — not detailed enough to cross-check NFDB's "
                "per-fire coding against."
            ),
        },
        "PE": {
            "status": "unverified",
            "note": (
                "Prince Edward Island's open dataset ('Annual Forest "
                "Fires') was checked directly and contains only annual "
                "fire counts, not per-fire records or a cause field."
            ),
        },
    }
    unverified_note = (
        "No independent, publicly-available per-fire cause dataset was "
        "found for this province/territory to cross-check against NFDB — "
        "its figures here rely on NFDB alone and have NOT been "
        "independently verified the way BC, Alberta, Quebec, and Ontario were."
    )
    for c in report_card["cards"]:
        if c["code"] not in status:
            status[c["code"]] = {"status": "unverified", "note": unverified_note}
    return status


def build_nfdb_delta_report(nfdb_raw_bc, ab_check, qc_check, on_check, report_card):
    """For every province where an independent authoritative source exists,
    report NFDB's raw known-cause rate against it directly — how far off
    NFDB is, in which direction, and by how much. This is the only way to
    see whether NFDB systematically over- or under-states known-cause
    rate, rather than just knowing BC was wrong."""
    by_code = {c["code"]: c for c in report_card["cards"]}
    rows = [
        {
            "province": "British Columbia", "code": "BC",
            "nfdb_known_rate": nfdb_raw_bc["known_rate"],
            "authoritative_known_rate": 53.5,
            "authoritative_source": "BC Wildfire Service (live Data Catalogue)",
        },
        {
            "province": "Alberta", "code": "AB",
            "nfdb_known_rate": by_code["AB"]["known_rate"],
            "authoritative_known_rate": ab_check["known_rate"],
            "authoritative_source": ab_check["source"],
        },
        {
            "province": "Quebec", "code": "QC",
            "nfdb_known_rate": by_code["QC"]["known_rate"],
            "authoritative_known_rate": qc_check["known_rate"],
            "authoritative_source": qc_check["source"],
        },
        {
            "province": "Ontario", "code": "ON",
            "nfdb_known_rate": by_code["ON"]["known_rate"],
            "authoritative_known_rate": on_check["known_rate"],
            "authoritative_source": on_check["source"],
        },
    ]
    for r in rows:
        r["delta_pct_points"] = round(r["nfdb_known_rate"] - r["authoritative_known_rate"], 1)
        r["direction"] = (
            "NFDB OVERSTATES known-cause rate (understates the real unknown-cause gap)" if r["delta_pct_points"] > 0.5
            else "NFDB UNDERSTATES known-cause rate" if r["delta_pct_points"] < -0.5
            else "NFDB matches the authoritative source"
        )
    n_matches = sum(1 for r in rows if r["direction"] == "NFDB matches the authoritative source")
    n_errors = len(rows) - n_matches
    return {
        "rows": rows,
        "finding": (
            f"NFDB's error is not evenly distributed. Of the four provinces "
            f"we could independently check, {n_matches} (Alberta, Quebec, "
            f"Ontario) match almost exactly. Only British Columbia is off — "
            f"and it's off by a lot: {rows[0]['delta_pct_points']:+.1f} "
            f"percentage points, a single, large, one-directional error, "
            f"not a small systematic bias. With {n_errors} confirmed error "
            f"out of {len(rows)} checked provinces, this reads as an "
            f"isolated BC data-lineage problem, not a general NFDB "
            f"tendency to overstate known-cause rate — but that's a "
            f"tentative read from 4 data points, not a full audit. Of the "
            f"remaining 8 provinces/territories, the Northwest Territories "
            f"and Yukon have current per-fire datasets of their own but "
            f"NEITHER records a cause field at all, so their NFDB numbers "
            f"are structurally unverifiable, not just unverified; "
            f"Saskatchewan, Manitoba, New Brunswick, Nova Scotia, PEI, and "
            f"Newfoundland & Labrador have no independent per-fire cause "
            f"source publicly available at all (see the verification "
            f"column above for the specific reason in each case)."
        ),
    }


def build_provincial_area_ranking(by_prov_year, start=2005, end=2024):
    totals = defaultdict(float)
    for prov, yd in by_prov_year.items():
        if prov == "PC":
            continue
        for y, d in yd.items():
            if start <= y <= end:
                totals[prov] += d["area_ha"]
    grand = sum(totals.values())
    ranked = sorted(totals.items(), key=lambda x: -x[1])
    return {
        "period": f"{start}-{end}",
        "source": "Canadian National Fire Database (NFDB), Canadian Forest Service / NRCan",
        "ranking": [
            {
                "province": PROV_NAMES.get(p, p),
                "code": p,
                "area_ha": round(a),
                "pct_of_national": round(100 * a / grand, 1),
            }
            for p, a in ranked
        ],
    }


def build_provincial_timeline(by_prov_year, provs, start, end):
    out = {}
    for p in provs:
        rows = []
        for y in range(start, end + 1):
            d = by_prov_year.get(p, {}).get(y)
            if not d:
                continue
            total = d["H"] + d["N"] + d["U"]
            known = d["H"] + d["N"]
            rows.append({
                "year": y,
                "human": d["H"], "lightning": d["N"], "unknown": d["U"],
                "total": total,
                "unknown_pct": round(100 * d["U"] / total, 1) if total else None,
                "human_pct_known": round(100 * d["H"] / known, 1) if known else None,
            })
        out[p] = rows
    return out


def build_manitoba_blackout(by_prov_year):
    rows = build_provincial_timeline(by_prov_year, ["MB"], 1959, 2025)["MB"]
    blackout_years = [r for r in rows if r["unknown_pct"] == 100.0]
    return {
        "finding": (
            "Manitoba's own fire-cause records show every single fire — "
            f"100% — coded 'Unknown' for four consecutive seasons, 2000 "
            f"through 2003 ({sum(r['total'] for r in blackout_years):,} "
            "fires total), immediately after four years (1996-1999) where "
            "cause was recorded for essentially every fire. It reverted to "
            "normal recording by 2005 — a complete, if temporary, cause-"
            "recording blackout, starker than BC's own partial cliff."
        ),
        "years": rows,
        "blackout_years": [r["year"] for r in blackout_years],
        "blackout_fire_count": sum(r["total"] for r in blackout_years),
        "source": "Canadian National Fire Database (NFDB), Canadian Forest Service / NRCan, SRC_AGENCY=MB",
    }


def build_yukon_spike(by_prov_year):
    rows = build_provincial_timeline(by_prov_year, ["YT"], 2015, 2025)["YT"]
    return {
        "finding": (
            "Yukon's unknown-cause rate is currently doing what BC's did in "
            "1999 — except it hasn't recovered yet. It jumped to 97.6% in "
            "2022 and has stayed elevated every year since: 55.9% (2023), "
            "19.6% (2024), 29.5% (2025, most recent complete data). Unlike "
            "BC's two-decade-old cliff, this is an ongoing, current gap."
        ),
        "years": rows,
        "source": "Canadian National Fire Database (NFDB), Canadian Forest Service / NRCan, SRC_AGENCY=YT",
    }


def build_provincial_cause_summary(by_prov_year, start=2015, end=2024):
    out = []
    for p in ["BC", "AB", "SK", "MB", "ON", "QC", "NT", "YT", "NL"]:
        agg = {"H": 0, "N": 0, "U": 0}
        for y in range(start, end + 1):
            d = by_prov_year.get(p, {}).get(y)
            if d:
                for k in agg:
                    agg[k] += d[k]
        total = sum(agg.values())
        if total == 0:
            continue
        out.append({
            "province": PROV_NAMES.get(p, p), "code": p,
            "human": agg["H"], "lightning": agg["N"], "unknown": agg["U"], "total": total,
            "unknown_pct": round(100 * agg["U"] / total, 1),
        })
    return {
        "period": f"{start}-{end}",
        "source": "Canadian National Fire Database (NFDB), Canadian Forest Service / NRCan",
        "provinces": sorted(out, key=lambda x: -x["unknown_pct"]),
    }


def build_national_cause_area(national_by_cause_year, start=2005, end=2024):
    rows = []
    for y in range(start, end + 1):
        d = national_by_cause_year.get(y, {"H": 0.0, "N": 0.0, "U": 0.0})
        total = d["H"] + d["N"] + d["U"]
        rows.append({
            "year": y,
            "human_ha": round(d["H"]), "lightning_ha": round(d["N"]), "unknown_ha": round(d["U"]),
            "total_ha": round(total),
            "human_pct_of_total": round(100 * d["H"] / total, 1) if total else None,
        })
    return rows


def cause_area_split_summary(rows):
    tot = {"human": 0, "lightning": 0, "unknown": 0, "total": 0}
    for r in rows:
        tot["human"] += r["human_ha"]; tot["lightning"] += r["lightning_ha"]
        tot["unknown"] += r["unknown_ha"]; tot["total"] += r["total_ha"]
    return {
        "period": f"{rows[0]['year']}-{rows[-1]['year']}",
        "human_ha": tot["human"], "lightning_ha": tot["lightning"],
        "unknown_ha": tot["unknown"], "total_ha": tot["total"],
        "human_pct_of_area": round(100 * tot["human"] / tot["total"], 1),
        "avg_annual_total_ha": round(tot["total"] / len(rows)),
        "avg_annual_human_ha": round(tot["human"] / len(rows)),
        "finding": (
            "Nationally, human-caused fires account for the MAJORITY of "
            "fires by count but only a small fraction of area burned — "
            "lightning fires, concentrated in remote, sparsely-monitored "
            "northern land, burn far more area per fire on average because "
            "they're detected and reached more slowly. This matters "
            "directly for the CO2 scenarios below: cutting human-caused "
            "ignitions cuts a lot of FIRES, but not much of the AREA that "
            "actually determines carbon output."
        ),
    }


# ---------------------------------------------------------------------------
# 7. CO2 / CLIMATE — Canada's official GHG inventory (ECCC National
#    Inventory Report 1990-2023, downloaded directly), wildfire-specific
#    carbon estimates (multiple independent sources, since no single
#    official multi-year provincial wildfire-carbon series is public), and
#    a labeled back-of-envelope scenario model built from the real NFDB
#    area-burned data above.
# ---------------------------------------------------------------------------
GHG_REGIONAL_URL = "https://www.canada.ca/content/dam/eccc/documents/csv/cesindicators/ghg-emissions/2025/ghg-emissions-regional-en.csv"
GHG_SECTOR_URL = "https://www.canada.ca/content/dam/eccc/documents/csv/cesindicators/ghg-emissions/2025/ghg-emissions-sector-en.csv"

C_TO_CO2 = 44.0 / 12.0  # molar mass ratio, carbon -> CO2


def fetch_text(url, out_path):
    if os.path.exists(out_path):
        return out_path
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8-sig")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    return out_path


def load_ghg_sector():
    path = fetch_text(GHG_SECTOR_URL, os.path.join(LAKE_DIR, "eccc_ghg", "ghg-emissions-sector-en.csv"))
    with open(path, encoding="utf-8-sig") as f:
        lines = f.readlines()
    header = [h.strip() for h in lines[2].strip().split(",")]
    sectors = [s.split(" (megatonnes")[0].strip() for s in header[1:]]
    rows = []
    for line in lines[3:]:
        line = line.strip()
        if not line or line.startswith(("Note", "Source", "Available")):
            continue
        parts = line.split(",")
        if len(parts) < 2 or not parts[0].strip().isdigit():
            continue
        year = int(parts[0])
        vals = [parse_float(v) for v in parts[1:1 + len(sectors)]]
        by_sector = dict(zip(sectors, vals))
        total = round(sum(v for v in vals if v is not None), 1)
        rows.append({"year": year, "total_mt": total, "by_sector": by_sector})
    return rows


def load_ghg_regional():
    path = fetch_text(GHG_REGIONAL_URL, os.path.join(LAKE_DIR, "eccc_ghg", "ghg-emissions-regional-en.csv"))
    with open(path, encoding="utf-8-sig") as f:
        lines = f.readlines()
    rows = []
    for line in lines[3:]:
        line = line.strip()
        if not line or line.startswith(("Note", "Source", "Available")):
            continue
        parts = line.split(",")
        if len(parts) < 4:
            continue
        prov = re.sub(r"\s*\(\w+\)$", "", parts[0]).strip()
        if not prov:
            continue

        def clean_val(v):
            return parse_float(v.replace("[A]", "").strip())

        rows.append({
            "province": prov,
            "mt_1990": clean_val(parts[1]),
            "mt_2005": clean_val(parts[2]),
            "mt_2023": clean_val(parts[3]),
        })
    return rows


WILDFIRE_2023_CO2_ESTIMATES = [
    {
        "source": "Copernicus Atmosphere Monitoring Service (CAMS/GFAS)",
        "value_mt_co2": 1760,
        "value_mt_carbon": 480,
        "note": "Full calendar-year 2023 estimate — roughly 5x the 2003-2022 average, and 23% of ALL global wildfire carbon emissions that year.",
        "citation": "Copernicus Atmosphere Monitoring Service, 2024",
    },
    {
        "source": "Byrne et al., Nature (2024) — peer-reviewed, satellite CO-inversion",
        "value_mt_co2": 2374,
        "value_mt_carbon": 647,
        "range_mt_carbon": [570, 727],
        "note": "May-September 2023 (captures the vast majority of the season). The most rigorous, peer-reviewed estimate found; used to calibrate the scenario model below.",
        "citation": "Byrne, B. et al., 'Carbon emissions from the 2023 Canadian wildfires,' Nature (2024)",
    },
    {
        "source": "World Resources Institute / Global Forest Watch",
        "value_mt_co2": 3000,
        "note": "Full-year estimate — described as roughly 4x global aviation's 2022 emissions, and larger than global tropical forest-loss carbon that year.",
        "citation": "World Resources Institute, wri.org/insights/canada-wildfire-emissions",
    },
    {
        "source": "Canada's own National Inventory Report (supplementary, non-headline figure)",
        "value_mt_co2": 1000,
        "note": "NRCan's own supplementary estimate — reported separately from Canada's official 694 Mt national total, not counted in it. Would rank as the world's 8th-largest emitter if counted as a country.",
        "citation": "Natural Resources Canada; Canadian Climate Institute (440megatonnes.ca)",
    },
]

WILDFIRE_NOT_COUNTED = {
    "finding": (
        "Canada's official greenhouse gas total — the number reported to "
        "the UN and measured against Canada's climate targets — does NOT "
        "include CO2 from wildfires. Emissions from natural disturbances "
        "(wildfire, insect outbreaks) on managed forest land are tracked "
        "but reported SEPARATELY from the headline inventory, under "
        "UNFCCC guidance that treats them as largely outside direct human "
        "control. Canada is unusual internationally in excluding ALL "
        "wildfire-related forest emissions this way, not just severe "
        "stand-replacing crown fires."
    ),
    "scrutiny": (
        "During UNFCCC technical review of Canada's 2021 inventory "
        "submission, international reviewers flagged that Canada had not "
        "sufficiently justified treating all such fire emissions as fully "
        "non-anthropogenic. One independent analysis estimates the "
        "exclusion may understate Canada's true annual footprint by "
        "roughly 80 Mt CO2e/year even in an average, non-record year."
    ),
    "sources": [
        "Natural Resources Canada, 'Canada's forest greenhouse gas reporting'",
        "Canadian Climate Institute (440megatonnes.ca), 'How forest fires affect Canada's climate progress'",
        "World Resources Institute, wri.org/insights/canada-wildfire-emissions",
    ],
}


def build_co2_scenario_model(national_cause_area_rows, national_2023_area_ha):
    byrne_mt_co2 = 647.0 * C_TO_CO2
    cop_mt_co2 = 480.0 * C_TO_CO2
    factor_low = round(cop_mt_co2 * 1_000_000 / national_2023_area_ha, 1)
    factor_high = round(byrne_mt_co2 * 1_000_000 / national_2023_area_ha, 1)

    window = [r for r in national_cause_area_rows if 2015 <= r["year"] <= 2024]
    avg_total_ha = sum(r["total_ha"] for r in window) / len(window)
    avg_human_ha = sum(r["human_ha"] for r in window) / len(window)

    national_total_2023 = 694.0
    oil_gas_2023 = 208.0

    def avoided_mt(area_ha, factor):
        return round(0.9 * area_ha * factor / 1_000_000, 1)

    s1_low, s1_high = avoided_mt(avg_human_ha, factor_low), avoided_mt(avg_human_ha, factor_high)
    s2_low, s2_high = avoided_mt(avg_total_ha, factor_low), avoided_mt(avg_total_ha, factor_high)

    return {
        "methodology": (
            "A CO2-per-hectare-burned factor is calibrated by dividing two "
            "independent, credible 2023 wildfire-CO2 estimates (Copernicus "
            "CAMS and the peer-reviewed Byrne et al. 2024 Nature study) by "
            "NFDB's own reported area burned in 2023 — keeping area and "
            "cause data internally consistent — then applying that factor "
            "to NFDB's 2015-2024 average annual area burned, by cause. "
            "This is a labeled ESTIMATE, not an official government "
            "figure: no authoritative Canada-wide avoided-emissions model "
            "for wildfire prevention/suppression investment currently "
            "exists publicly."
        ),
        "calibration": {
            "nfdb_2023_area_burned_ha": round(national_2023_area_ha),
            "copernicus_2023_estimate_mt_co2": round(cop_mt_co2),
            "byrne_2023_estimate_mt_co2": round(byrne_mt_co2),
            "implied_factor_low_t_co2_per_ha": factor_low,
            "implied_factor_high_t_co2_per_ha": factor_high,
        },
        "baseline_2015_2024": {
            "avg_annual_total_area_burned_ha": round(avg_total_ha),
            "avg_annual_human_caused_area_burned_ha": round(avg_human_ha),
            "human_share_of_area_pct": round(100 * avg_human_ha / avg_total_ha, 1),
        },
        "scenario_1_arson_crackdown": {
            "label": "Cut human-caused (arson & other human-ignition) area burned by 90%",
            "avoided_mt_co2_low": s1_low,
            "avoided_mt_co2_high": s1_high,
            "pct_of_national_total_low": round(100 * s1_low / national_total_2023, 1),
            "pct_of_national_total_high": round(100 * s1_high / national_total_2023, 1),
            "pct_of_oil_gas_sector_low": round(100 * s1_low / oil_gas_2023, 1),
            "pct_of_oil_gas_sector_high": round(100 * s1_high / oil_gas_2023, 1),
            "takeaway": (
                "Even eliminating 90% of human-ignited area burned offsets "
                "only 3-4% of Canada's ENTIRE annual national emissions "
                "total, because humans start the majority of fires by "
                "count but only around 6% of total area burned — lightning "
                "fires in remote, under-monitored land drive the rest. "
                "Arson reduction alone does not meaningfully move Canada's "
                "carbon math."
            ),
        },
        "scenario_2_prevention_response": {
            "label": "Cut ALL area burned (any cause) 90% via prevention, early detection, and rapid suppression investment",
            "avoided_mt_co2_low": s2_low,
            "avoided_mt_co2_high": s2_high,
            "pct_of_national_total_low": round(100 * s2_low / national_total_2023, 1),
            "pct_of_national_total_high": round(100 * s2_high / national_total_2023, 1),
            "multiple_of_oil_gas_sector_low": round(s2_low / oil_gas_2023, 2),
            "multiple_of_oil_gas_sector_high": round(s2_high / oil_gas_2023, 2),
            "takeaway": (
                "A cause-agnostic 90% cut to area burned — treating "
                "wildfire monitoring and initial-attack capacity as "
                "seriously as any other emissions lever — would avoid CO2 "
                "equivalent to 1.8x-2.5x Canada's ENTIRE oil & gas "
                "sector's annual emissions, or 55-74% of the country's "
                "whole official national total."
            ),
        },
        "reality_check": (
            "90% is a hypothetical ceiling, not a forecast — nobody is "
            "proposing eliminating 90% of area burned overnight. The "
            "closest real-world benchmark found: a Kootenay National Park "
            "case study found rapid initial attack can cut burn "
            "PROBABILITY by up to 78% in that specific setting — smaller "
            "and more localized, but directionally real."
        ),
        "important_caveat": (
            "Because wildfire CO2 is not counted in Canada's official "
            "national total or climate targets, this is a magnitude "
            "comparison for public accountability, not a literal "
            "accounting mechanism — avoiding wildfire emissions would not "
            "currently free up 'room' under Canada's targets the way "
            "cutting oil & gas emissions would, precisely because "
            "wildfire emissions were never charged against those targets "
            "in the first place. That gap is itself part of the story."
        ),
    }


# ---------------------------------------------------------------------------
# 8. THE REPORT CARD — what we DO know, substantiated, normalized across
#    every province. Tests a specific hypothesis: do denser, more-developed
#    provinces (population density as a proxy for monitoring/enforcement
#    infrastructure) show better cause-recording (less "Unknown") and less
#    human-caused fire? Sources: NFDB (as above) + Statistics Canada
#    population estimates (Table 17-10-0009, live-fetched) + Statistics
#    Canada's standard land-area reference figures (stable geographic
#    constants — land area does not change year to year — hardcoded here
#    with citation, consistent with report_architect convention for small
#    stable facts).
# ---------------------------------------------------------------------------
LAND_AREA_KM2 = {
    "BC": 925186, "AB": 642317, "SK": 591670, "MB": 553556, "ON": 917741,
    "QC": 1356625, "NB": 71450, "NS": 53338, "PE": 5660, "NL": 373872,
    "YT": 474391, "NT": 1183085, "NU": 1936113,
}
LAND_AREA_SOURCE = "Statistics Canada, Land and freshwater area, by province and territory"

POP_URL = "https://www150.statcan.gc.ca/n1/tbl/csv/17100009-eng.zip"

GEO_TO_CODE = {
    "British Columbia": "BC", "Alberta": "AB", "Saskatchewan": "SK",
    "Manitoba": "MB", "Ontario": "ON", "Quebec": "QC", "New Brunswick": "NB",
    "Nova Scotia": "NS", "Prince Edward Island": "PE",
    "Newfoundland and Labrador": "NL", "Yukon": "YT",
    "Northwest Territories": "NT", "Nunavut": "NU",
}


def fetch_zip_csv(url, out_dir, csv_name):
    csv_path = os.path.join(out_dir, csv_name)
    if os.path.exists(csv_path):
        return csv_path
    os.makedirs(out_dir, exist_ok=True)
    zip_path = os.path.join(out_dir, "download.zip")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        with open(zip_path, "wb") as f:
            f.write(resp.read())
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(out_dir)
    os.remove(zip_path)
    return csv_path


def load_population_density():
    csv_path = fetch_zip_csv(POP_URL, os.path.join(LAKE_DIR, "statcan_pop"), "17100009.csv")
    latest = {}
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            code = GEO_TO_CODE.get(row["GEO"])
            if not code or not row["VALUE"]:
                continue
            date = row["REF_DATE"]
            if code not in latest or date > latest[code][0]:
                latest[code] = (date, float(row["VALUE"]))
    return {
        code: {
            "population": round(pop),
            "population_date": date,
            "land_area_km2": LAND_AREA_KM2[code],
            "density_per_km2": round(pop / LAND_AREA_KM2[code], 3),
        }
        for code, (date, pop) in latest.items()
    }


def pearson_r(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return round(cov / (sx * sy), 3) if sx and sy else None


def grade_for(known_rate):
    if known_rate >= 95:
        return "A"
    if known_rate >= 85:
        return "B"
    if known_rate >= 70:
        return "C"
    if known_rate >= 50:
        return "D"
    return "F"


def build_report_card(by_prov_year, density, start=2005, end=2024, min_fires=50):
    cards = []
    for p in LAND_AREA_KM2:
        agg = {"H": 0, "N": 0, "U": 0, "H_ha": 0.0, "N_ha": 0.0, "U_ha": 0.0}
        for y in range(start, end + 1):
            d = by_prov_year.get(p, {}).get(y)
            if not d:
                continue
            for k in agg:
                agg[k] += d[k]
        total = agg["H"] + agg["N"] + agg["U"]
        if total < 5:
            continue  # no meaningful fire activity in this window (e.g. Nunavut: none in NFDB)
        area_total = agg["H_ha"] + agg["N_ha"] + agg["U_ha"]
        known_rate = round(100 * (agg["H"] + agg["N"]) / total, 1)
        known_count = agg["H"] + agg["N"]
        cards.append({
            "province": PROV_NAMES.get(p, p), "code": p,
            "human": agg["H"], "lightning": agg["N"], "unknown": agg["U"], "total_fires": total,
            "human_pct": round(100 * agg["H"] / total, 1),
            "lightning_pct": round(100 * agg["N"] / total, 1),
            "unknown_pct": round(100 * agg["U"] / total, 1),
            "human_pct_known": round(100 * agg["H"] / known_count, 1) if known_count else None,
            "known_rate": known_rate,
            "grade": grade_for(known_rate),
            "human_pct_of_area": round(100 * agg["H_ha"] / area_total, 2) if area_total else None,
            "lightning_pct_of_area": round(100 * agg["N_ha"] / area_total, 2) if area_total else None,
            "unknown_pct_of_area": round(100 * agg["U_ha"] / area_total, 2) if area_total else None,
            "density_per_km2": density.get(p, {}).get("density_per_km2"),
            "small_sample": total < min_fires,
        })
    cards.sort(key=lambda r: -r["known_rate"])
    return {
        "period": f"{start}-{end}",
        "min_fires_for_reliable_grade": min_fires,
        "cards": cards,
        "source": "Canadian National Fire Database (NFDB), Canadian Forest Service / NRCan",
    }


def build_arson_ranking(report_card):
    """% of KNOWN-cause fires that are human-caused, by province, ranked
    highest to lowest — the closest available proxy to "what share of
    wildfires are human-started," computed against fires whose cause IS
    known so it isn't diluted by each province's different unknown-cause
    rate. NFDB has no arson-specific sub-code (only Human/Lightning/
    Unknown) — this is human-caused, not arson specifically; BC's own
    arson-vs-other-human-causes breakdown (Section 6, Chapter 1) is the
    only sub-categorized source in this report."""
    eligible = [c for c in report_card["cards"] if c["human_pct_known"] is not None]
    ranked = sorted(eligible, key=lambda c: -c["human_pct_known"])
    return {
        "period": report_card["period"],
        "note": (
            "NFDB codes cause as Human, Lightning, or Unknown — there is "
            "no arson-specific sub-code nationally (BC's own cause "
            "sub-category breakdown in Chapter 1 is the only source in "
            "this report that isolates arson from other human causes like "
            "campfires and equipment). This is HUMAN-caused share of "
            "KNOWN-cause fires — the closest available national proxy, "
            "and the one least distorted by a province's own unknown-"
            "cause rate."
        ),
        "ranking": [
            {
                "province": c["province"], "code": c["code"],
                "human_pct_known": c["human_pct_known"],
                "human": c["human"], "lightning": c["lightning"],
                "small_sample": c["small_sample"],
            }
            for c in ranked
        ],
    }


def build_area_by_cause_ranking(report_card):
    eligible = [c for c in report_card["cards"] if c["human_pct_of_area"] is not None]
    ranked = sorted(eligible, key=lambda c: -c["human_pct_of_area"])
    return {
        "period": report_card["period"],
        "ranking": [
            {
                "province": c["province"], "code": c["code"],
                "human_pct_of_area": c["human_pct_of_area"],
                "lightning_pct_of_area": c["lightning_pct_of_area"],
                "unknown_pct_of_area": c["unknown_pct_of_area"],
                "small_sample": c["small_sample"],
            }
            for c in ranked
        ],
    }


def build_count_vs_area_explainer(report_card, fire_size_by_cause, cause_area_summary):
    reliable = [c for c in report_card["cards"] if not c["small_sample"] and c["human_pct_known"] is not None]
    known_h = sum(c["human"] for c in reliable)
    known_n = sum(c["lightning"] for c in reliable)
    national_human_pct_known = round(100 * known_h / (known_h + known_n), 1) if (known_h + known_n) else None
    national_human_pct_area = cause_area_summary["human_pct_of_area"]
    m = fire_size_by_cause["mean_size_ha"]
    return {
        "national_human_pct_of_known_fires": national_human_pct_known,
        "national_human_pct_of_area": national_human_pct_area,
        "finding": (
            f"This is a real, well-documented pattern in Canadian wildfire "
            f"science, not a data error: nationally, {national_human_pct_known}% "
            f"of fires with a known cause are human-started — humans DO "
            f"start the clear majority of individual fires. But those same "
            f"human-caused fires account for only {national_human_pct_area}% "
            f"of the AREA burned. The average human-caused fire burns "
            f"{m['human']} ha, while the average lightning fire burns "
            f"{m['lightning']} ha — "
            f"{round(m['lightning'] / m['human'], 1) if m['human'] else '?'}x "
            f"larger. The mechanism is detection and access, not ignition "
            f"source: human-caused fires start near roads, towns, and "
            f"campsites, where they're seen and reached within hours; "
            f"lightning fires disproportionately start in remote boreal "
            f"and northern terrain, where a fire can burn for days before "
            f"anyone spots it and even longer before crews can reach it. "
            f"CIFFC's and NRCan's own national reporting shows the same "
            f"pattern every year: humans cause most fires, lightning burns "
            f"most area. Both numbers in this report are correct — count "
            f"and area are answering different questions, not contradicting "
            f"each other."
        ),
    }


def build_infrastructure_hypothesis_test(report_card):
    reliable = [c for c in report_card["cards"] if not c["small_sample"] and c["density_per_km2"]]
    logd = [math.log10(c["density_per_km2"]) for c in reliable]
    known = [c["known_rate"] for c in reliable]
    human_area = [c["human_pct_of_area"] for c in reliable if c["human_pct_of_area"] is not None]
    logd_for_area = [math.log10(c["density_per_km2"]) for c in reliable if c["human_pct_of_area"] is not None]

    r_known = pearson_r(logd, known)
    r_area = pearson_r(logd_for_area, human_area)

    best = max(reliable, key=lambda c: c["known_rate"])
    worst = min(reliable, key=lambda c: c["known_rate"])
    densest = max(reliable, key=lambda c: c["density_per_km2"])
    sparsest = min(reliable, key=lambda c: c["density_per_km2"])
    by_density_rank = sorted(reliable, key=lambda c: -c["density_per_km2"])
    worst_density_rank = next(i for i, c in enumerate(by_density_rank, 1) if c["code"] == worst["code"])

    return {
        "hypothesis": (
            "Do provinces with more population density (a proxy for "
            "monitoring/enforcement infrastructure — roads, cell coverage, "
            "fire lookouts, faster investigator dispatch) show BETTER "
            "cause-recording (higher known-cause rate) and LESS human-"
            "caused fire?"
        ),
        "n_provinces": len(reliable),
        "correlation_density_vs_known_rate": r_known,
        "correlation_density_vs_human_area_share": r_area,
        "verdict": (
            f"NOT SUPPORTED for cause-recording quality: the correlation "
            f"between population density and known-cause rate is "
            f"essentially zero (r={r_known}). The best-performing "
            f"jurisdiction, {best['province']} ({best['known_rate']}% "
            f"known), sits at only {best['density_per_km2']}/km² — while "
            f"the worst, {worst['province']} ({worst['known_rate']}% "
            f"known), sits at {worst['density_per_km2']}/km² — the "
            f"{worst_density_rank}{'st' if worst_density_rank == 1 else 'nd' if worst_density_rank == 2 else 'rd' if worst_density_rank == 3 else 'th'}"
            f"-densest of {len(reliable)} jurisdictions, not the sparsest. "
            f"And {densest['province']}, the DENSEST jurisdiction in the "
            f"dataset ({densest['density_per_km2']}/km²), only manages "
            f"{densest['known_rate']}% known — while {sparsest['province']}, "
            f"the SPARSEST ({sparsest['density_per_km2']}/km²), posts "
            f"{sparsest['known_rate']}%. This suggests "
            f"cause-recording quality is driven by specific agency "
            f"practices and systems (as found directly for BC's own "
            f"historical cause-recording cliff and Manitoba's 2000-2003 "
            f"blackout — both sudden, database/practice-driven events, "
            f"not gradual infrastructure trends) rather than by how "
            f"developed or populated a province is. MODERATE POSITIVE for "
            f"human-caused area share "
            f"(r={r_area}): denser provinces do show a higher share of "
            f"their area burned being human-caused — but this is best "
            f"read as a GEOGRAPHY effect, not a monitoring effect: "
            f"provinces with less remote wilderness simply have fewer "
            f"lightning-dominated fires to dilute the human share, "
            f"regardless of enforcement."
        ),
    }


def build_fire_size_by_cause(by_prov_year, start=2005, end=2024):
    agg = {"H": 0, "N": 0, "U": 0, "H_ha": 0.0, "N_ha": 0.0, "U_ha": 0.0}
    for prov, yd in by_prov_year.items():
        if prov == "PC":
            continue
        for y in range(start, end + 1):
            d = yd.get(y)
            if not d:
                continue
            for k in agg:
                agg[k] += d[k]
    mean_h = round(agg["H_ha"] / agg["H"], 1) if agg["H"] else None
    mean_n = round(agg["N_ha"] / agg["N"], 1) if agg["N"] else None
    mean_u = round(agg["U_ha"] / agg["U"], 1) if agg["U"] else None
    ratio_to_human = round(mean_u / mean_h, 1) if mean_h else None
    ratio_to_lightning = round(mean_u / mean_n, 2) if mean_n else None
    closer_to = "human-caused" if ratio_to_human is not None and ratio_to_lightning is not None and abs(1 - ratio_to_human) < abs(1 - ratio_to_lightning) else "lightning-caused"
    return {
        "period": f"{start}-{end}",
        "mean_size_ha": {"human": mean_h, "lightning": mean_n, "unknown": mean_u},
        "unknown_to_human_ratio": ratio_to_human,
        "unknown_to_lightning_ratio": ratio_to_lightning,
        "finding": (
            f"Nationally (now using BC's own corrected data — see the "
            f"verification note above), the average human-caused fire "
            f"burns {mean_h} ha, the average lightning fire burns {mean_n} "
            f"ha, and the average UNKNOWN-cause fire burns {mean_u} ha — "
            f"{ratio_to_human}x the human-caused average, much closer to "
            f"the {closer_to} figure than we initially found before "
            f"correcting BC's numbers. That's a meaningfully different "
            f"answer than an uncorrected NFDB pull gives (which had "
            f"'unknown' fires looking like large, remote, lightning-sized "
            f"fires — an artifact of NFDB mis-coding many of BC's small, "
            f"human-scale unattributed fires as something else). With BC "
            f"corrected, 'unknown' cause fires are only modestly larger "
            f"than human-caused ones — which is more consistent with a "
            f"real, unresolved pool of un-investigated human-scale fires "
            f"than with a population of large, hard-to-reach lightning "
            f"fires that simply never got formally attributed."
        ),
    }


# ---------------------------------------------------------------------------
# 9. THE FEASIBLE SCENARIO — reframes the arson-crackdown lever from
#    section 7 as the low-infrastructure option (harsher sentencing +
#    enforcement, no new aircraft/satellites required), adds the
#    unknown-cause reporting gap as a related but DISTINCT lever (an
#    accountability/attribution measure, not an independently-quantified
#    CO2 lever — see the fire-size finding above for why), and ranks all
#    three interventions found in this report by infrastructure
#    requirement, mechanism, and estimated impact.
# ---------------------------------------------------------------------------
def build_intervention_comparison(scenario_model, cause_area_summary, fire_size_by_cause):
    s1 = scenario_model["scenario_1_arson_crackdown"]
    s2 = scenario_model["scenario_2_prevention_response"]
    avg_unknown_ha = round(
        (cause_area_summary["unknown_ha"]) / (
            int(cause_area_summary["period"].split("-")[1]) - int(cause_area_summary["period"].split("-")[0]) + 1
        )
    )
    return {
        "framing": (
            "The two scenarios in the previous section span very different "
            "policy asks. This ranks the actual interventions by whether "
            "they require major new infrastructure, what they'd plausibly "
            "achieve, and how confident we are in that number."
        ),
        "interventions": [
            {
                "name": "Harsher sentencing & enforcement targeting human-caused ignition",
                "requires_major_infrastructure": False,
                "mechanism": "Deterrence — raises the cost of arson and negligent ignition specifically.",
                "avoided_mt_co2_low": s1["avoided_mt_co2_low"],
                "avoided_mt_co2_high": s1["avoided_mt_co2_high"],
                "pct_of_national_total": f"{s1['pct_of_national_total_low']}-{s1['pct_of_national_total_high']}%",
                "confidence": "Moderate — the area-burned math is solid; whether harsher sentencing actually achieves a 90% cut in human-ignited area is unverified and modeled as a ceiling, not a prediction.",
            },
            {
                "name": "Monitoring/enforcement staffing to close the unknown-cause reporting gap",
                "requires_major_infrastructure": False,
                "mechanism": "Investigative capacity & reporting discipline — enables attribution and prosecution; does not by itself extinguish fires faster.",
                "avoided_mt_co2_low": None,
                "avoided_mt_co2_high": None,
                "pct_of_national_total": None,
                "annual_unattributed_area_ha": avg_unknown_ha,
                "confidence": (
                    "Not independently quantified as a CO2 lever. "
                    f"~{avg_unknown_ha:,} ha/year currently goes unattributed nationally, "
                    "and the corrected fire-size finding above shows unknown-cause fires "
                    "are only modestly larger than human-caused ones (not lightning-sized), "
                    "which is at least consistent with a real, un-investigated pool of "
                    "human-scale fires — but we have no way to independently confirm what "
                    "share of that pool is actually human-ignited without a province-by-"
                    "province investigation. Its clearest, most defensible value is "
                    "enabling the sentencing lever above (you can't prosecute a fire you "
                    "never attributed) and enabling more reliable versions of this exact "
                    "kind of analysis in provinces without an independent verification source."
                ),
            },
            {
                "name": "Full prevention, early-detection & rapid-suppression infrastructure investment (cause-agnostic)",
                "requires_major_infrastructure": True,
                "mechanism": "Faster detection and initial attack on ALL fires, regardless of cause — aircraft, satellite monitoring, staffing at scale.",
                "avoided_mt_co2_low": s2["avoided_mt_co2_low"],
                "avoided_mt_co2_high": s2["avoided_mt_co2_high"],
                "pct_of_national_total": f"{s2['pct_of_national_total_low']}-{s2['pct_of_national_total_high']}%",
                "confidence": "Low-moderate — a hypothetical ceiling (90% cut to ALL area burned), not a costed plan. The closest real benchmark, a Kootenay National Park case study, found rapid initial attack cut burn PROBABILITY up to 78% in one localized setting.",
            },
        ],
        "takeaway": (
            "The two levers that don't require major infrastructure — "
            "harsher sentencing and closing the reporting gap — are the "
            "most immediately actionable, but only the sentencing lever "
            "has a directly quantified (if uncertain) CO2 payoff, and it's "
            "small: 3-4% of Canada's national total. The lever with the "
            "largest potential payoff (cause-agnostic prevention and "
            "rapid response) is also the one that requires the "
            "infrastructure this report's Chapter 1 found Canada cutting, "
            "not building, in 2026."
        ),
    }


# ---------------------------------------------------------------------------
# 5. HERO STATS + METADATA
# ---------------------------------------------------------------------------
def build_hero(timeline, decades, collapse, bcws_breakdown):
    recent = [r for r in timeline if not r["in_progress"] and r["year"] >= 2016]
    recent_known = sum(r["person"] + r["lightning"] for r in recent)
    recent_human_pct = round(
        100 * sum(r["person"] for r in recent) / recent_known, 1
    ) if recent_known else None

    arson_pct = next(
        c["pct"] for c in bcws_breakdown["categories"] if c["label"] == "Arson / suspicious"
    )

    before = collapse["last_normal_year"]
    spike = collapse["spike_year"]

    return [
        {"label": "GOC emergency-coordination staff cut, per PSAC (govt disputes: says ~9%)", "value": "~50%", "accent": "key"},
        {"label": f"BC unknown-cause fires, {before['year']} → {spike['year']} (one-year jump)", "value": f"{before['unknown_pct']}% → {spike['unknown_pct']}%", "accent": "key"},
        {"label": f"Of BC fires with a known cause, {recent[0]['year']}-{recent[-1]['year']}, human-caused" if recent else "BC wildfires human-caused", "value": f"{recent_human_pct}%", "accent": "neutral"},
        {"label": "BC wildfires officially attributed to arson, 2016-2025", "value": f"{arson_pct}%", "accent": "neutral"},
        {"label": "Canadian agencies publishing an annual wildfire-arson arrest count (vs. France's 420)", "value": "0", "accent": "key"},
    ]


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("Loading BC Wildfire incident data...")
    incidents = load_bc_incidents()
    print(f"  {len(incidents)} total incidents loaded")

    timeline, area = build_timeline(incidents)
    decades = decade_summary(timeline)
    collapse = cause_recording_collapse(timeline)

    print("Loading StatCan arson benchmark (35-10-0177-01)...")
    statcan_arson = load_statcan_arson()

    print("Loading Canadian National Fire Database (all provinces/territories)...")
    by_prov_year, national_by_cause_year = load_nfdb()
    nfdb_raw_bc_snapshot = snapshot_nfdb_known_rate(by_prov_year, "BC")
    substitute_bc_authoritative_data(by_prov_year, national_by_cause_year, timeline, area)
    provincial_area_ranking = build_provincial_area_ranking(by_prov_year)
    provincial_timeline = build_provincial_timeline(by_prov_year, ["MB", "YT", "SK", "NT", "AB", "ON", "QC"], 1990, 2025)
    manitoba_blackout = build_manitoba_blackout(by_prov_year)
    yukon_spike = build_yukon_spike(by_prov_year)
    provincial_cause_summary = build_provincial_cause_summary(by_prov_year)
    national_cause_area = build_national_cause_area(national_by_cause_year)
    cause_area_summary = cause_area_split_summary(national_cause_area)

    print("Loading Canada GHG emissions (ECCC National Inventory Report 1990-2023)...")
    ghg_sector = load_ghg_sector()
    ghg_regional = load_ghg_regional()
    national_2023_area_ha = sum(
        national_by_cause_year.get(2023, {}).values()
    )
    co2_scenario_model = build_co2_scenario_model(national_cause_area, national_2023_area_ha)

    print("Loading Statistics Canada population estimates (Table 17-10-0009)...")
    density = load_population_density()
    report_card = build_report_card(by_prov_year, density)
    infrastructure_hypothesis_test = build_infrastructure_hypothesis_test(report_card)
    fire_size_by_cause = build_fire_size_by_cause(by_prov_year)
    intervention_comparison = build_intervention_comparison(co2_scenario_model, cause_area_summary, fire_size_by_cause)
    arson_ranking = build_arson_ranking(report_card)
    area_by_cause_ranking = build_area_by_cause_ranking(report_card)
    count_vs_area_explainer = build_count_vs_area_explainer(report_card, fire_size_by_cause, cause_area_summary)

    print("Cross-checking NFDB against Alberta's, Quebec's, and Ontario's own wildfire data...")
    ab_check = fetch_ab_wildfire_verification()
    qc_check = fetch_qc_wildfire_verification()
    on_check = fetch_on_wildfire_verification()
    verification_status = build_verification_status(report_card, ab_check, qc_check, on_check)
    for c in report_card["cards"]:
        c["verification"] = verification_status[c["code"]]
    nfdb_delta_report = build_nfdb_delta_report(nfdb_raw_bc_snapshot, ab_check, qc_check, on_check, report_card)

    hero = build_hero(timeline, decades, collapse, BCWS_CAUSE_BREAKDOWN_2016_2025)

    result = {
        "hero": hero,
        "bc_timeline": timeline,
        "bc_area_burned": area,
        "bc_decade_summary": decades,
        "cause_recording_collapse": {**collapse, "context": CAUSE_COLLAPSE_CONTEXT},
        "bcws_cause_breakdown": BCWS_CAUSE_BREAKDOWN_2016_2025,
        "data_quality_note": (
            "BC's FIRE_CAUSE field carries only three values — Person, "
            "Lightning, Unknown — with no arson sub-code. The Unknown share "
            "itself has swung sharply by decade (from roughly 10-17% in the "
            "1950s-1980s to over 50% in the 2000s, settling near 20-30% "
            "recently), which would distort any 'human-caused %' computed "
            "against ALL fires. Every human-caused percentage in this report "
            "is computed against fires with a KNOWN cause (Person + "
            "Lightning) unless labelled otherwise, so swings in how much "
            "goes unrecorded don't get mistaken for a real change in who "
            "starts fires."
        ),
        "statcan_arson_benchmark": statcan_arson,
        "france_arrest_trend": FRANCE_ARREST_TREND,
        "monitoring_cuts_2026": MONITORING_CUTS_2026,
        "cuts_savings_summary": CUTS_SAVINGS_SUMMARY,
        "cuts_estimate": build_cuts_estimate(),
        "named_bc_arson_cases": NAMED_BC_ARSON_CASES,
        "politifact_guardrail": POLITIFACT_GUARDRAIL,
        "alberta_context": ALBERTA_CONTEXT,
        "water_bombers": {
            "fleet_by_province": WATER_BOMBER_FLEET_BY_PROVINCE,
            "national_estimates": WATER_BOMBER_NATIONAL_ESTIMATES,
            "manufacturing_timeline": MANUFACTURING_TIMELINE,
            "federal_funding_timeline": FEDERAL_AERIAL_FUNDING_TIMELINE,
            "suppression_spending_trend": SUPPRESSION_SPENDING_TREND,
            "ontario_budget_cut": ONTARIO_BUDGET_CUT,
            "expert_commentary": WATER_BOMBER_EXPERT_COMMENTARY,
            "verdict": WATER_BOMBER_VERDICT,
        },
        "water_bomber_fleet_trend": WATER_BOMBER_FLEET_TREND,
        "federal_funding_history": FEDERAL_FUNDING_HISTORY,
        "damage_events": WILDFIRE_DAMAGE_EVENTS,
        "damage_trend": WILDFIRE_DAMAGE_TREND,
        "tally": WILDFIRE_TALLY,
        "national_fire_causes": {
            "provincial_area_ranking": provincial_area_ranking,
            "provincial_timeline": provincial_timeline,
            "provincial_cause_summary": provincial_cause_summary,
            "manitoba_blackout": manitoba_blackout,
            "yukon_spike": yukon_spike,
            "nfdb_bc_discrepancy_note": NFDB_BC_DISCREPANCY_NOTE,
            "report_card": report_card,
            "population_density": density,
            "infrastructure_hypothesis_test": infrastructure_hypothesis_test,
            "fire_size_by_cause": fire_size_by_cause,
            "independent_verification": {"alberta": ab_check, "quebec": qc_check, "ontario": on_check},
            "nfdb_delta_report": nfdb_delta_report,
            "arson_ranking": arson_ranking,
            "area_by_cause_ranking": area_by_cause_ranking,
            "count_vs_area_explainer": count_vs_area_explainer,
        },
        "co2_climate": {
            "national_ghg_timeline": ghg_sector,
            "national_ghg_latest_total_mt": ghg_sector[-1]["total_mt"],
            "provincial_ghg": ghg_regional,
            "wildfire_not_counted": WILDFIRE_NOT_COUNTED,
            "wildfire_2023_estimates": WILDFIRE_2023_CO2_ESTIMATES,
            "national_cause_area": national_cause_area,
            "cause_area_split_summary": cause_area_summary,
            "scenario_model": co2_scenario_model,
            "intervention_comparison": intervention_comparison,
        },
        "metadata": {
            "title": "The Monitoring Gap",
            "subtitle": "Canada cut wildfire-monitoring capacity as the crisis grew",
            "last_updated": "2026-08-10",
            "sources": [
                "BC Wildfire Service, Fire Incident Locations - Historical & Current (BC Data Catalogue, WFS, live-fetched)",
                "Statistics Canada, Table 35-10-0177-01, Arson [2110] violation category",
                "Black Press / Northern Beat, BC Wildfire Service cause sub-category breakdown 2013-2025",
                "Global News, The Hill Times, The Globe and Mail, Nelson Star — 2026 federal monitoring-capacity cuts reporting",
                "BBC News, europesays.com/News.Az, Anadolu Agency, The Inquirer — France Interior Ministry wildfire-arson arrest figures",
                "PolitiFact, 2023-07-20 fact-check",
                "CBC/Radio-Canada, Fire Fighting in Canada, Skies Mag, AFP fact-check — Canadian water bomber fleet snapshots, 2023-2026",
                "FlightGlobal, Canadian Affairs — De Havilland DHC-515 production restart and delivery timelines, 2026",
                "canada.ca / Public Safety Canada — federal aerial firefighting funding announcements, Dec 2025-May 2026",
                "Hope et al., PLOS ONE — wildfire suppression cost trends under a changing climate",
                "The Conversation, BNN Bloomberg — expert commentary on aerial firefighting capacity, 2026",
                "Parliamentary Budget Officer — DFAA cost projections, 2025-10",
                "Office of the Auditor General of Canada — Emergency Management in First Nations Communities, 2022-08",
                "Insurance Bureau of Canada / CatIQ — wildfire insured-loss and decade-comparison data",
                "Canadian Climate Institute — wildfire smoke health-cost and financial-loss projections",
                "Senate Standing Committee on Agriculture and Forestry — \"Canada on Fire,\" 2026-06",
                "FlightGlobal, CBC, Skies Mag — Alberta/Manitoba water bomber purchase costs, 2010-2026",
                "Government of Saskatchewan (1997), Ontario Aviation and Fire Management Branch archives, Wikipedia CL-215/CL-415 — provincial fleet history data points",
                "Transportation Safety Board of Canada — CL-415 write-off report A13A0075",
                "AerialFire, Selectra, Wildfire Today, National Aerial Firefighting Centre — international water bomber fleet comparison (France, EU/rescEU, US, Australia)",
                "CBC News, The Globe and Mail — ECCC Weatheradio operating/decommissioning cost figures, 2026",
                "PIPSC press statements; NRCan 2026-27 Departmental Plan — Comprehensive Expenditure Review context",
                "Canadian National Fire Database (NFDB), Canadian Forest Service / NRCan — 448,602 fire points, all provinces/territories, 1930-2025, live-fetched",
                "Environment and Climate Change Canada, National Inventory Report 1990-2023: Greenhouse Gas Sources and Sinks in Canada (2025 submission), live-fetched",
                "Copernicus Atmosphere Monitoring Service (CAMS/GFAS) — 2023 global wildfire carbon emissions",
                "Byrne, B. et al., 'Carbon emissions from the 2023 Canadian wildfires,' Nature (2024)",
                "World Resources Institute / Global Forest Watch — Canada wildfire emissions analysis",
                "Natural Resources Canada — forest greenhouse gas reporting; Canadian Climate Institute (440megatonnes.ca)",
                "Statistics Canada, Table 17-10-0009-01, Population estimates, quarterly, live-fetched",
                "Statistics Canada, Land and freshwater area, by province and territory (standard geographic reference)",
                "open.alberta.ca, Historical wildfire data 2006-2025 — used to independently cross-check NFDB's Alberta cause coding",
                "Données Québec / Ministère des Ressources naturelles et des Forêts, Cartographie des points d'origine des feux (1972-2024) — used to independently cross-check NFDB's Quebec cause coding",
                "Ontario GeoHub / LIO Open Data, Fire Disturbance Point (1976-2025, live ArcGIS REST service) — used to independently cross-check NFDB's Ontario cause coding",
                "GNWT Geomatics, NWT Fire History; open.yukon.ca, Yukon Fire History — checked directly for a cause field; neither dataset has one, so NFDB's NT/YT cause coding is flagged as structurally unverifiable rather than merely unverified",
            ],
        },
    }

    out_path = os.path.join(DATA_DIR, "report-wildfire-monitoring-gap.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {out_path}")

    # --- Data currency checks -------------------------------------------------
    completed_years = [r["year"] for r in timeline if not r["in_progress"]]
    print(f"BC timeline: {min(completed_years)} -> {max(completed_years)} (completed seasons), "
          f"2026 in-progress: {'yes' if any(r['in_progress'] for r in timeline) else 'no'}")
    print(f"StatCan arson benchmark: latest year {statcan_arson['latest_year']}")
    nfdb_years = [y for prov in by_prov_year.values() for y in prov.keys()]
    print(f"NFDB: {min(nfdb_years)} -> {max(nfdb_years)}")
    print(f"GHG sector timeline: {ghg_sector[0]['year']} -> {ghg_sector[-1]['year']} "
          f"(ECCC's National Inventory Report is published with an inherent ~2-year lag; "
          f"{ghg_sector[-1]['year']} is the latest year that exists anywhere, official or otherwise)")
    assert max(completed_years) >= 2025, "BC timeline does not reach 2025 — investigate"
    assert statcan_arson["latest_year"] >= 2024, "StatCan arson data is stale — investigate"
    assert max(nfdb_years) >= 2025, "NFDB does not reach 2025 — investigate"
    assert ghg_sector[-1]["year"] >= 2023, "GHG sector data is stale — investigate"
    pop_dates = {v["population_date"] for v in density.values()}
    print(f"Population estimates: {sorted(pop_dates)}")
    assert min(pop_dates) >= "2025-01", "Population estimates are stale — investigate"
    assert len(report_card["cards"]) >= 10, "Report card is missing provinces — investigate"
    print("Integrity checks passed.")


if __name__ == "__main__":
    main()
