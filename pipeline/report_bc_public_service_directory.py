"""
The Last Census: mapping who worked inside B.C.'s government right before the
public directory that listed them was taken down.

B.C.'s official employee directory (dir.gov.bc.ca) let anyone search every
public-service position by name, title, ministry, and office. On 2026-08-20
the province restricted public access, citing "cybersecurity and employee
privacy." No aggregate replacement (a public headcount-by-ministry table, for
example) was published alongside the takedown — so a preserved snapshot of
the directory is now the only public record of how B.C.'s ~22,000-position
public service is organized by ministry and function.

Source (raw copy acquired to pipeline/lake/bc_government_directory/):
  - BC Government Directory bulk export, recovered via the Wayback Machine's
    only capture of https://dir.gov.bc.ca/downloads/BCGOV_directory_people.csv
    (2026-04-09), patched with 1,147 individually-archived directory pages
    captured 2026-01 through 2026-08 where available (up to 2026-07-14).
    22,441 records. Full provenance, patch-acceptance methodology, and
    departure-detection analysis: see the companion
    bc_government_directory archive's README.md (a separate local project,
    not part of this repo).
  - The employee-level data that fed this report has already been stripped
    of every individually-identifying field (name, direct phone/fax, email,
    street address, postal code) by that archive's
    scripts/deidentify.py — employees_deidentified.csv here contains only
    job title, ministry, branch, office city/province, and record
    provenance. See DROPPED_COLUMNS in that script for the full list of
    what was removed and why.

This is a single snapshot, not a time series — there is no earlier public
export to compare it against, and the live source is now gone, so year-over-
year change cannot be shown. What this report can show: the composition of
one government at one moment, which is itself no longer publicly
reconstructable now that dir.gov.bc.ca is down.

Output: data/report-bc-public-service-directory.json
"""
import csv
import json
import os
import re
from collections import Counter, defaultdict

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(PIPELINE_DIR)
DATA_DIR = os.path.join(REPO_DIR, "data")
LAKE_DIR = os.path.join(PIPELINE_DIR, "lake", "bc_government_directory")
IN_CSV = os.path.join(LAKE_DIR, "employees_deidentified.csv")
FRESHNESS_JSON = os.path.join(LAKE_DIR, "freshness_report.json")

# ---------------------------------------------------------------------------
# Job-function classification — keyword match against job title, first hit
# wins (ordered by specificity, most senior/specific categories first). This
# is a heuristic over free-text government job titles, not an official
# occupational taxonomy: ~30% of titles don't match any category and land in
# "Management & Generalist" or "Other / Unclassified" — both are reported
# honestly rather than forced into a specific bucket. See the report's
# methodology note.
# ---------------------------------------------------------------------------
CATEGORIES = [
    ("Executive & Senior Management", re.compile(
        r"\b(Assistant Deputy Minister|Deputy Minister|Executive Director|ADM|"
        r"Associate Deputy|Chief Executive|CEO|President|Vice President|VP|"
        r"Director General)\b", re.I)),
    ("Communications & Public Affairs", re.compile(
        r"\b(Communications?|Public Affairs|Media Relations|Public Information)\b", re.I)),
    ("Information Technology & Data", re.compile(
        r"\b(IT|Information Technology|Systems Analyst|Software|Network Analyst|"
        r"Database|Application Developer|Full Stack Developer|Developer|Cyber|"
        r"Technology Officer|Web Developer|Geospatial|Data (Analyst|Scientist)|"
        r"GIS|Service Desk)\b", re.I)),
    ("Finance & Accounting", re.compile(
        r"\b(Finance|Financial|Accounting|Accountant|Payroll|Auditor|Budget|"
        r"Revenue (&|and)? ?Collection|Audit Analyst|Collection (Officer|Analyst))\b", re.I)),
    ("Human Resources", re.compile(
        r"\b(Human Resources|HR|Recruit(ment|er)|Labour Relations|People (and|&) Culture)\b", re.I)),
    ("Legal & Compliance", re.compile(
        r"\b(Legal|Counsel|Solicitor|Compliance|Crown Counsel|Ombudsperson|Judge|"
        r"Justice|FOI (Analyst|Specialist)|Authorizations Specialist)\b", re.I)),
    ("Policy & Economic Analysis", re.compile(
        r"\b(Policy|Corporate Planning|Strategic Planning|Planning Analyst|"
        r"Economist|Research (Officer|Analyst))\b", re.I)),
    ("Land, Environment & Natural Resources", re.compile(
        r"\b(Biologist|Ecosystem|Forester|Forestry|Wildfire|Environmental|Geologist|"
        r"Hydrologist|Wildlife|Fisheries|Range|Silviculture|Conservation|Climate|"
        r"Land and Resource|Natural Resource|Resource Manager|Resource Officer)\b", re.I)),
    ("Engineering & Infrastructure", re.compile(
        r"\b(Engineer|Engineering|Surveyor|Transportation Technician|Highways?|"
        r"Operations Technologist)\b", re.I)),
    ("Health & Social Services", re.compile(
        r"\b(Nurse|Social Worker|Psychiatric|Health Officer|Public Health|"
        r"Child Protection|Youth Worker|Clinician|Pharmacist)\b", re.I)),
    ("Enforcement, Inspection & Public Safety", re.compile(
        r"\b(Conservation Officer|Enforcement|Peace Officer|Fire (Officer|Investigator)|"
        r"Emergency (Management|Program)|Sheriff|Correctional|Inspector|Investigator|"
        r"Coroner|Workers'? Adviser|Industrial Relations Officer)\b", re.I)),
    ("Administrative & Program Support", re.compile(
        r"\b(Clerk|Administrative Assistant|Program Assistant|Office Manager|"
        r"Receptionist|Data Entry|Records Management|Field Services Assistant)\b", re.I)),
    ("Retail & Frontline Operations", re.compile(
        r"\b(Liquor Store|Stockworker|Cashier|Warehouse)\b", re.I)),
    ("Management & Project/Business Generalist", re.compile(
        r"\b(Director|Manager|Team Lead(er)?|Supervisor|Coordinator|Business Analyst|"
        r"Project (Manager|Coordinator|Administrator|Director|Assessment|Management)|"
        r"Business Administrator|Executive Assistant|Executive Coordinator)\b", re.I)),
]

ROLE_PLACEHOLDER_LABEL = "Fax / vacant / generic mailbox lines (not individuals)"


def classify_title(title):
    for label, rx in CATEGORIES:
        if rx.search(title):
            return label
    return "Other / Unclassified"


def main():
    with open(IN_CSV, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    result = {}

    total_records = len(rows)
    individuals = [r for r in rows if r["record_type"] == "individual"]
    placeholders = [r for r in rows if r["record_type"] != "individual"]

    # =========================================================================
    # 1. BY MINISTRY — every organizationName, ranked
    # =========================================================================
    org_counts = Counter(r["organizationName"].strip() or "(Unspecified)" for r in individuals)
    by_ministry = [
        {"organization": org, "count": count}
        for org, count in org_counts.most_common()
    ]
    result["by_ministry"] = by_ministry

    # =========================================================================
    # 2. BY JOB FUNCTION — title-keyword classification
    # =========================================================================
    func_counts = Counter(classify_title(r["title"].strip()) for r in individuals)
    by_job_function = [
        {"category": cat, "count": count}
        for cat, count in func_counts.most_common()
    ]
    result["by_job_function"] = by_job_function

    # =========================================================================
    # 3. BY LOCATION — office city (individuals only; many records have no
    #    city on file, reported explicitly rather than silently dropped)
    # =========================================================================
    city_counts = Counter()
    no_city = 0
    for r in individuals:
        city = r["mailCity"].strip()
        if not city:
            no_city += 1
            continue
        # normalize casing variants seen in the source (e.g. "VICTORIA" vs "Victoria")
        city = city.title() if city.isupper() else city
        city_counts[city] += 1
    by_location = [
        {"city": city, "count": count}
        for city, count in city_counts.most_common(25)
    ]
    result["by_location"] = by_location
    result["location_unspecified_count"] = no_city

    # =========================================================================
    # 4. DATA PROVENANCE — how fresh each record is (as_of date histogram)
    # =========================================================================
    as_of_counts = Counter(r["as_of"].strip() for r in rows if r["as_of"].strip())
    by_as_of_date = [
        {"date": d, "count": c} for d, c in sorted(as_of_counts.items())
    ]
    result["by_as_of_date"] = by_as_of_date

    source_counts = Counter(r["source"].strip() for r in rows if r["source"].strip())
    result["by_source"] = [
        {"source": s, "count": c} for s, c in source_counts.most_common()
    ]

    # =========================================================================
    # 5. MINISTRY x JOB FUNCTION — full cross-tab for the data table
    # =========================================================================
    cross = defaultdict(Counter)
    for r in individuals:
        org = r["organizationName"].strip() or "(Unspecified)"
        cross[org][classify_title(r["title"].strip())] += 1

    table_rows = []
    for org in org_counts:
        row_total = org_counts[org]
        top_function, top_function_count = cross[org].most_common(1)[0]
        table_rows.append({
            "organization": org,
            "total": row_total,
            "top_function": top_function,
            "top_function_count": top_function_count,
        })
    table_rows.sort(key=lambda r: -r["total"])
    result["ministry_table"] = table_rows

    # =========================================================================
    # 6. PROVINCIAL/TERRITORIAL/FEDERAL COMPARISON — is BC actually alone?
    #    Hardcoded per report_architect convention: this is a small, manually-
    #    researched comparison table, not a bulk/API dataset. Each row checked
    #    live 2026-08-20 (see 'checked' field); tier assignments and status
    #    text reflect what was directly observed or, where automated access
    #    was blocked by bot-protection (Saskatchewan, PEI), what the
    #    jurisdiction's own site describes plus independent news corroboration
    #    (see sources below).
    # =========================================================================
    result["provincial_comparison"] = [
        {"jurisdiction": "Ontario", "tier": "Full public directory", "status": "INFO-GO (infogo.gov.on.ca) — name, position, email, phone, address; updated daily", "checked": "2026-08-20"},
        {"jurisdiction": "New Brunswick", "tier": "Full public directory", "status": "gnb.ca contacts directory — searchable by name, department, keyword, no login", "checked": "2026-08-20"},
        {"jurisdiction": "Newfoundland & Labrador", "tier": "Full public directory", "status": "telephonedirectory.gov.nl.ca — searchable by name, title, phone, department", "checked": "2026-08-20"},
        {"jurisdiction": "Prince Edward Island", "tier": "Full public directory", "status": "princeedwardisland.ca employee directory — searchable by name, phone, email, title", "checked": "2026-08-20"},
        {"jurisdiction": "Saskatchewan", "tier": "Full public directory", "status": "saskatchewan.ca/government/directory — official public directory; automated verification blocked by bot-protection, confirmed via provincial media comparison", "checked": "2026-08-20"},
        {"jurisdiction": "Yukon", "tier": "Full public directory", "status": "find-employee.service.yukon.ca — searchable by name, title, email, phone", "checked": "2026-08-20"},
        {"jurisdiction": "Federal (Canada)", "tier": "Full public directory", "status": "GEDS (geds-sage.gc.ca) — searchable by name, phone, title; some departments incomplete", "checked": "2026-08-20"},
        {"jurisdiction": "Alberta", "tier": "Public, limited fields", "status": "alberta.ca/staff-directory.cfm — name and phone only, no email/address, cited cyberattack protection", "checked": "2026-08-20"},
        {"jurisdiction": "Nova Scotia", "tier": "Public, limited fields", "status": "novascotia.ca employee directory — phone number only, no email or address", "checked": "2026-08-20"},
        {"jurisdiction": "Quebec", "tier": "Public, partial coverage", "status": "REPTEL (reptel.gouv.qc.ca) — some departments/agencies and some employees excluded by policy", "checked": "2026-08-20"},
        {"jurisdiction": "Manitoba", "tier": "No public directory found", "status": "No province-wide public employee directory found on manitoba.ca; only scattered per-branch listings", "checked": "2026-08-20"},
        {"jurisdiction": "Northwest Territories", "tier": "No public directory found", "status": "No public employee directory found on gov.nt.ca", "checked": "2026-08-20"},
        {"jurisdiction": "Nunavut", "tier": "Internal use only", "status": "gov.nu.ca/en/staff-directory requires sign-in; public must email communications@gov.nu.ca", "checked": "2026-08-20"},
        {"jurisdiction": "British Columbia", "tier": "Restricted August 2026", "status": "Public since at least 1930, online since 2007 — access restricted 2026-08-18, two days ahead of the announced Aug. 20 cutoff", "checked": "2026-08-20"},
    ]
    result["provincial_comparison_summary"] = {
        "full_public": 7,
        "public_limited_fields": 2,
        "public_partial_coverage": 1,
        "no_directory_found": 2,
        "internal_only": 1,
        "restricted_2026": 1,
        "note": (
            "B.C. is not literally the only jurisdiction without a fully public directory — "
            "Manitoba and the Northwest Territories appear never to have built one, and Nunavut "
            "restricts its directory to signed-in staff. But B.C. is the only jurisdiction found "
            "where an existing, decades-old public directory was deliberately taken down in 2026, "
            "with provincial media directly naming Ontario, Saskatchewan, and New Brunswick as far "
            "more open by comparison, and Alberta as the next-most restrictive."
        ),
    }

    # =========================================================================
    # 7. HERO STATS
    # =========================================================================
    largest_ministry = by_ministry[0]
    comms_count = func_counts.get("Communications & Public Affairs", 0)
    result["hero_stats"] = {
        "total_records": total_records,
        "individual_count": len(individuals),
        "placeholder_count": len(placeholders),
        "ministry_count": len(org_counts),
        "largest_ministry_name": largest_ministry["organization"],
        "largest_ministry_count": largest_ministry["count"],
        "largest_ministry_pct": round(largest_ministry["count"] / len(individuals) * 100, 1),
        "communications_count": comms_count,
        "communications_pct": round(comms_count / len(individuals) * 100, 2),
    }

    # =========================================================================
    # 8. METADATA
    # =========================================================================
    freshness = {}
    if os.path.exists(FRESHNESS_JSON):
        with open(FRESHNESS_JSON, encoding="utf-8") as f:
            freshness = json.load(f)

    result["metadata"] = {
        "title": "The Last Census",
        "snapshot_captured": freshness.get("baseline_date", "2026-04-09"),
        "as_of_date_range": freshness.get("as_of_date_range", ["2026-04-09", "2026-07-14"]),
        "public_access_restricted": "2026-08-18",
        "public_access_cutoff_announced": "2026-08-20",
        "sources": [
            "BC Government Directory bulk export (Wayback Machine capture, 2026-04-09), "
            "patched with individually-archived pages through 2026-07-14",
            "Rob Shaw, \"B.C. cutting public access to decades-old government directory,\" "
            "Business in Vancouver, 2026-08-18",
            "\"B.C. disables employee directory, leaving public in the dark about who works "
            "for gov't,\" Black Press Media (Vancouver Island Free Daily and syndicated "
            "outlets), 2026-08-18",
            "\"Transparency issues raised over B.C. gov't decision to remove public employee "
            "directory,\" CBC News, 2026-08",
            "Direct verification of provincial/territorial/federal directory status, 2026-08-20 "
            "(see provincial_comparison)",
        ],
    }

    # Write output
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "report-bc-public-service-directory.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Wrote {out_path}")
    print(f"  {total_records} total records: {len(individuals)} individuals, {len(placeholders)} placeholders")
    print(f"  {len(org_counts)} ministries/orgs")
    print(f"  Unclassified job function: {func_counts.get('Other / Unclassified', 0)} "
          f"({func_counts.get('Other / Unclassified', 0) / len(individuals) * 100:.1f}%)")


if __name__ == "__main__":
    main()
