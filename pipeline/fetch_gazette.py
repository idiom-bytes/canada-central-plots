#!/usr/bin/env python3
"""
fetch_gazette.py — Canada GAZETTE regulatory-layer harvester (immigration/asylum).

Builds the "policy was changed by REGULATION, not by Parliament" evidence layer:
registered regulations (SOR), Statutory Instruments (SI), Orders in Council (OIC),
and Ministerial Instructions touching IMMIGRATION / ASYLUM / TEMPORARY-RESIDENTS /
ENFORCEMENT-REMOVAL — with dates and citations.

TOKEN-LEAN DESIGN
-----------------
This script NEVER dumps raw HTML/PDF into anyone's reasoning context. It downloads
source pages to lake/gazette/ and parses with regex, printing only small summaries.

DATA SOURCES
------------
1. STRUCTURED: Justice Laws (laws-lois.justice.gc.ca)
   - IRPR consolidated regulation index (SOR/2002-227): "Amendments" list, where each
     amending instrument is a registered SOR with a coming-into-force date. This is the
     compact structured index of "regulations changing immigration rules".
   - IRPA (i-2.5) "Regulations made under this Act": the set of SOR/SI made under the Act.
   These pages are HTML; we cache them to lake/ and regex out citations + dates ONLY.

2. CURATED SUPPLEMENT: a hand-verified set of the most consequential immigration
   regulatory events (STCA designation + 2023 land-border expansion, Express Entry MIs,
   eTA, TFWP/IMP employer-compliance, biometrics expansion, study-permit cap, recent
   inadmissibility/removal SORs). Citations + dates verified against the Canada Gazette
   Part II RIAS and Justice Laws. Used because the comprehensive Gazette feed on CKAN is
   per-issue HTML/PDF (not a machine-readable immigration index), so a structured-only
   pull would miss SI/OIC/MI items and the policy-direction framing.

Each event carries "_source": "structured" or "curated" so coverage is auditable.

OUTPUT (ADD-only)
-----------------
  data/gazette_events.json   — {meta, events:[...]}
  data/gazette_events.js     — window.GAZETTE_EVENTS = {meta, events:[...]}; (1 line)
"""

import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LAKE = os.path.join(ROOT, "lake", "gazette")
DATA = os.path.join(ROOT, "data")
os.makedirs(LAKE, exist_ok=True)
os.makedirs(DATA, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (canada-central-plots gazette pipeline)"}

# Justice Laws structured pages (consolidated regs index = amendment list)
SOURCES = {
    "irpr_index": "https://laws-lois.justice.gc.ca/eng/regulations/SOR-2002-227/index.html",
    "irpa_index": "https://laws-lois.justice.gc.ca/eng/acts/i-2.5/index.html",
}


# ---------------------------------------------------------------------------
# Networking — download to lake/, return cached path. Never returns page text
# to the caller's context; the caller parses the file with regex.
# ---------------------------------------------------------------------------
def fetch_to_lake(key, url):
    path = os.path.join(LAKE, key + ".html")
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=45) as r:
            body = r.read()
        if b"Request Rejected" in body or len(body) < 500:
            raise ValueError("blocked or empty response")
        with open(path, "wb") as fh:
            fh.write(body)
        return path, None
    except Exception as e:  # noqa: BLE001 — we want to fall back gracefully
        return (path if os.path.exists(path) else None), f"{type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return re.sub(r"-+", "-", s)[:60]


def classify_instrument(citation):
    c = citation.upper()
    if c.startswith("SOR"):
        return "Regulation (SOR)"
    if c.startswith("SI"):
        return "Statutory Instrument (SI)"
    if "P.C." in c or c.startswith("OIC"):
        return "Order in Council"
    return "Ministerial Instruction"


def year_of(d):
    try:
        return int(d[:4])
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# STRUCTURED parse: pull amending SOR citations + dates out of cached HTML.
# We only regex; we never echo page text.
# ---------------------------------------------------------------------------
CIT_DATE_RE = re.compile(
    r"(SOR|SI)\s*[/\-]\s*(\d{4})-(\d{1,3})"          # citation
    r"(?:[^0-9A-Za-z]{0,40}?(\d{4}-\d{2}-\d{2}))?",  # optional nearby ISO date
)


def parse_structured(path, default_domain="other-immigration", source_label=""):
    """Return list of partial event dicts parsed from a cached Justice Laws page."""
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        html = fh.read()
    # strip tags so dates near citations are reachable, keep it cheap
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)

    seen = {}
    for m in CIT_DATE_RE.finditer(text):
        kind, yr, num, iso = m.group(1), m.group(2), m.group(3), m.group(4)
        citation = f"{kind}/{yr}-{int(num)}"
        # Skip the base IRPR itself — it is the regulation being amended, not an
        # amending instrument; and only accept entries with a genuine ISO date so
        # we never invent a placeholder. Keep the entry with a date if duplicated.
        if citation == "SOR/2002-227":
            continue
        if not (iso and iso[:4] == yr):
            continue
        if citation in seen:
            continue
        d = iso
        seen[citation] = {
            "id": slugify(citation),
            "date": d,
            "year": int(yr),
            "title": f"{citation} — amendment to immigration regulations",
            "instrument": classify_instrument(citation),
            "parliamentary_vote": False,
            "direction": "unknown",
            "domain": default_domain,
            "summary": (
                f"{citation} is a registered instrument listed in the "
                f"{source_label} index of regulations affecting immigration; "
                "effect on screening/enforcement not assessable from the index alone."
            ),
            "citation": f"Canada Gazette Part II, {citation}"
            if kind == "SOR"
            else f"Canada Gazette Part II, {citation}",
            "source_url": SOURCES.get("irpr_index"),
            "_source": "structured",
        }
    return list(seen.values())


# ---------------------------------------------------------------------------
# CURATED supplement — verified citations + dates (see module docstring).
# ---------------------------------------------------------------------------
def curated_events():
    raw = [
        {
            "date": "2004-12-29",
            "title": "Safe Third Country Agreement — US designated safe third country",
            "instrument": "Regulation (SOR)",
            "direction": "strengthened",
            "domain": "STCA",
            "summary": "Added s.159.3 to the IRPR designating the United States as a safe "
                       "third country; refugee claimants arriving at a land port of entry "
                       "from the US are ineligible to have a claim referred.",
            "citation": "Canada Gazette Part II, SOR/2004-217",
            "source_url": "https://laws-lois.justice.gc.ca/eng/regulations/SOR-2002-227/section-159.3.html",
        },
        {
            "date": "2023-03-25",
            "title": "STCA Additional Protocol — extended to the entire land border",
            "instrument": "Regulation (SOR)",
            "direction": "strengthened",
            "domain": "STCA",
            "summary": "IRPR amendment implementing the 2022 Additional Protocol, extending "
                       "the Safe Third Country Agreement to the whole land border including "
                       "between ports of entry (claim within 14 days of crossing).",
            "citation": "Canada Gazette Part II, SOR/2023-58",
            "source_url": "https://gazette.gc.ca/rp-pr/p2/2023/2023-04-12/html/sor-dors58-eng.html",
        },
        {
            "date": "2012-12-15",
            "title": "Designated Countries of Origin (DCO) regime established",
            "instrument": "Ministerial Instruction",
            "direction": "strengthened",
            "domain": "asylum",
            "summary": "Ministerial designation of 'safe' countries of origin imposing "
                       "accelerated timelines and appeal/PRRA bars on claimants from those "
                       "countries; the practice was ended (all countries removed) on 2019-05-17.",
            "citation": "Ministerial designation under IRPA (DCO list)",
            "source_url": "https://www.canada.ca/en/immigration-refugees-citizenship/news/2019/05/canada-ends-the-designated-country-of-origin-practice.html",
        },
        {
            "date": "2015-01-01",
            "title": "Express Entry system established (Ministerial Instructions)",
            "instrument": "Ministerial Instruction",
            "direction": "strengthened",
            "domain": "screening",
            "summary": "Ministerial Instructions under IRPA s.10.3 establishing the Express "
                       "Entry pool and ranking system for economic immigration; published in "
                       "Canada Gazette Part I (Vol.148, Extra No.10) on 2014-12-01.",
            "citation": "Canada Gazette Part I, Vol.148, Extra No.10 (Express Entry MIs)",
            "source_url": "https://gazette.gc.ca/rp-pr/p1/2014/2014-12-01-x10/html/extra10-eng.html",
        },
        {
            "date": "2015-04-22",
            "title": "Electronic Travel Authorization (eTA) introduced",
            "instrument": "Regulation (SOR)",
            "direction": "strengthened",
            "domain": "screening",
            "summary": "IRPR amendment creating the eTA pre-screening requirement for "
                       "visa-exempt air travellers (US citizens excepted); registered 2015, "
                       "mandatory from 2016-03-15.",
            "citation": "Canada Gazette Part II, SOR/2015-77",
            "source_url": "https://laws-lois.justice.gc.ca/eng/regulations/SOR-2002-227/",
        },
        {
            "date": "2013-11-21",
            "title": "Employer compliance regime for foreign workers (IRPR)",
            "instrument": "Regulation (SOR)",
            "direction": "strengthened",
            "domain": "TFW",
            "summary": "IRPR amendment adding the employer-compliance framework "
                       "(ss.209.2-209.92): conditions, inspections and consequences for "
                       "employers of foreign workers.",
            "citation": "Canada Gazette Part II, SOR/2013-245",
            "source_url": "https://laws-lois.justice.gc.ca/eng/regulations/SOR-2002-227/",
        },
        {
            "date": "2015-02-11",
            "title": "International Mobility Program — compliance fee and inspections",
            "instrument": "Regulation (SOR)",
            "direction": "strengthened",
            "domain": "TFW",
            "summary": "IRPR amendment for the International Mobility Program adding the "
                       "$230 employer compliance fee, inspection powers and penalties for "
                       "LMIA-exempt employers; in force 2015-02-21.",
            "citation": "Canada Gazette Part II, SOR/2015-25",
            "source_url": "https://gazette.gc.ca/rp-pr/p2/2015/2015-02-11/html/sor-dors25-eng.html",
        },
        {
            "date": "2018-07-11",
            "title": "Biometrics expansion to nearly all applicants",
            "instrument": "Regulation (SOR)",
            "direction": "strengthened",
            "domain": "screening",
            "summary": "IRPR amendment expanding biometric collection to nearly all "
                       "temporary- and permanent-resident applicants (visas, work/study "
                       "permits, TRPs); phased in 2018-07-31 and 2018-12-31.",
            "citation": "Canada Gazette Part II, SOR/2018-128",
            "source_url": "https://gazette.gc.ca/rp-pr/p2/2018/2018-07-11/html/sor-dors128-eng.html",
        },
        {
            "date": "2024-01-22",
            "title": "International student intake cap + Provincial Attestation Letter",
            "instrument": "Ministerial Instruction",
            "direction": "strengthened",
            "domain": "students",
            "summary": "Ministerial Instructions under IRPA s.87.3 imposing a national cap "
                       "on study-permit applications and requiring a Provincial Attestation "
                       "Letter (PAL) for most applicants.",
            "citation": "Ministerial Instructions under IRPA s.87.3 (study-permit cap)",
            "source_url": "https://www.canada.ca/en/immigration-refugees-citizenship/news/2024/01/canada-to-stabilize-growth-and-decrease-number-of-new-international-student-permits-issued-to-approximately-360000-for-2024.html",
        },
        {
            "date": "2024-11-20",
            "title": "Study-permit rules tied to DLI compliance + work-hour limits",
            "instrument": "Regulation (SOR)",
            "direction": "strengthened",
            "domain": "students",
            "summary": "IRPR amendment tying study permits to a specific Designated Learning "
                       "Institution, adding DLI compliance/reporting and setting off-campus "
                       "work at 24 hours/week; phased coming into force into 2025.",
            "citation": "Canada Gazette Part II, SOR/2024-219",
            "source_url": "https://gazette.gc.ca/rp-pr/p2/2024/2024-11-20/html/sor-dors219-eng.html",
        },
        {
            "date": "2024-06-19",
            "title": "Inadmissibility / transborder criminality amendment",
            "instrument": "Regulation (SOR)",
            "direction": "strengthened",
            "domain": "removal/enforcement",
            "summary": "IRPR amendment addressing inadmissibility and transborder "
                       "criminality provisions affecting removal and enforcement.",
            "citation": "Canada Gazette Part II, SOR/2024-128",
            "source_url": "https://gazette.gc.ca/rp-pr/p2/2024/2024-06-19/html/sor-dors128-eng.html",
        },
        {
            "date": "2025-02-12",
            "title": "Cancellation of immigration documents",
            "instrument": "Regulation (SOR)",
            "direction": "strengthened",
            "domain": "removal/enforcement",
            "summary": "IRPR amendment giving authority to cancel immigration documents in "
                       "connection with inadmissibility and removal.",
            "citation": "Canada Gazette Part II, SOR/2025-11",
            "source_url": "https://gazette.gc.ca/rp-pr/p2/2025/2025-02-12/html/sor-dors11-eng.html",
        },
    ]
    out = []
    for e in raw:
        e = dict(e)
        e["id"] = slugify(e["title"])
        e["year"] = year_of(e["date"])
        e["parliamentary_vote"] = False
        e["_source"] = "curated"
        out.append(e)
    return out


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build():
    notes = []
    structured = []

    p1, err1 = fetch_to_lake("irpr_index", SOURCES["irpr_index"])
    if err1:
        notes.append(f"irpr_index fetch failed ({err1}); used cache if present")
    structured += parse_structured(p1, "other-immigration", "IRPR (SOR/2002-227)")

    p2, err2 = fetch_to_lake("irpa_index", SOURCES["irpa_index"])
    if err2:
        notes.append(f"irpa_index fetch failed ({err2}); used cache if present")
    structured += parse_structured(p2, "other-immigration", "IRPA regulations")

    curated = curated_events()

    # Curated citations win over the thin structured stubs of the same SOR.
    curated_cits = {
        re.search(r"(SOR|SI)/\d{4}-\d+", e["citation"]).group(0)
        for e in curated
        if re.search(r"(SOR|SI)/\d{4}-\d+", e["citation"])
    }

    def cit_key(e):
        m = re.search(r"(SOR|SI)/\d{4}-\d+", e.get("citation", ""))
        return m.group(0) if m else None

    # Dedup structured across both source pages + drop any that collide with curated.
    dedup = {}
    for e in structured:
        k = cit_key(e)
        if not k or k in curated_cits or k in dedup:
            continue
        dedup[k] = e
    structured = list(dedup.values())

    events = curated + structured
    events.sort(key=lambda e: (e["date"], e["id"]))

    n_struct = sum(1 for e in events if e["_source"] == "structured")
    n_cur = sum(1 for e in events if e["_source"] == "curated")
    dates = [e["date"] for e in events if e.get("date")]
    drange = [min(dates), max(dates)] if dates else [None, None]

    meta = {
        "title": "Canada Gazette regulatory layer — immigration / asylum / enforcement",
        "description": "Registered regulations (SOR), Statutory Instruments (SI), Orders "
                       "in Council and Ministerial Instructions that changed immigration, "
                       "asylum, temporary-resident and removal/enforcement policy by "
                       "regulation rather than by Act of Parliament.",
        "method": "Structured pull of the IRPR (SOR/2002-227) amendment index and the "
                  "IRPA regulations index from Justice Laws (downloaded to lake/, parsed "
                  "with regex — no HTML loaded into reasoning context), merged with a "
                  "hand-verified curated set of the most consequential items (citations "
                  "and dates checked against Canada Gazette Part II RIAS / Justice Laws).",
        "coverage": "Curated layer covers the landmark STCA/asylum/TFW/students/screening/"
                    "removal instruments 2004-2025. Structured layer adds additional IRPR "
                    "amending SORs found in the Justice Laws index (direction='unknown' "
                    "until individually assessed). NOT an exhaustive Gazette Part II census.",
        "source_note": "open.canada.ca CKAN exposes Canada Gazette only as per-issue "
                       "HTML/PDF (no machine-readable immigration index), so the structured "
                       "backbone is the Justice Laws consolidated-regulation amendment index "
                       f"({SOURCES['irpr_index']}).",
        "count": len(events),
        "structured_count": n_struct,
        "curated_count": n_cur,
        "date_range": drange,
        "updated": date.today().isoformat(),
    }
    if notes:
        meta["fetch_notes"] = notes

    payload = {"meta": meta, "events": events}

    with open(os.path.join(DATA, "gazette_events.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    compact = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(DATA, "gazette_events.js"), "w", encoding="utf-8") as fh:
        fh.write("window.GAZETTE_EVENTS = " + compact + ";\n")

    return payload, meta


def main():
    payload, meta = build()
    events = payload["events"]

    # parse-check the JSON we just wrote
    with open(os.path.join(DATA, "gazette_events.json"), encoding="utf-8") as fh:
        reparsed = json.load(fh)
    assert reparsed["meta"]["count"] == len(reparsed["events"])

    by_inst = {}
    for e in events:
        by_inst[e["instrument"]] = by_inst.get(e["instrument"], 0) + 1

    print("=== gazette_events build ===")
    print(f"total events     : {meta['count']}")
    print(f"  structured     : {meta['structured_count']}")
    print(f"  curated        : {meta['curated_count']}")
    print(f"date range       : {meta['date_range'][0]} -> {meta['date_range'][1]}")
    print("instrument breakdown:")
    for k in sorted(by_inst):
        print(f"  {k:28s}: {by_inst[k]}")
    if "fetch_notes" in meta:
        print("fetch notes:")
        for n in meta["fetch_notes"]:
            print("  -", n)
    print("JSON re-parsed OK:", reparsed["meta"]["count"], "events")
    print("sample events:")
    for e in events[:5]:
        print(f"  {e['date']} | {e['instrument']:18s} | {e['citation'][:42]:42s} | {e['_source']}")


if __name__ == "__main__":
    main()
