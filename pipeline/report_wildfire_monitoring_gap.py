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
import os
import time
import urllib.request
import urllib.error
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
    assert max(completed_years) >= 2025, "BC timeline does not reach 2025 — investigate"
    assert statcan_arson["latest_year"] >= 2024, "StatCan arson data is stale — investigate"
    print("Integrity checks passed.")


if __name__ == "__main__":
    main()
