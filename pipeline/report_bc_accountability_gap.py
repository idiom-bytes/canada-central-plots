"""Transform data for "The Provincial and Federal Wedge Dividing BC's Sovereignty" report (BC First Nations finances, federal spending, land agreements).

Sources
  Computed (automated):
    - ISC/CIRNAC First Nation Profiles portal, FNFTA filings (lake/bc_fn_accountability/fnfta/*.json,
      acquired by pipeline/fetch_fnfta.py). Compliance is RECOMPUTED here from per-band "Date Received".
  Hand-compiled (no API exists; every figure carries its source in the JSON):
    - Canada Spends (FNFTA compliance chart, Indigenous-priorities spending chart, per-person screenshot)
    - Fraser Institute 2026 (Flanagan & Li) federal Indigenous spending
    - FNHA / BC Provincial Health Officer, Population Health and Wellness Agenda First Interim Update (Aug 2024):
      annual series PARSED from the PDF figures 4.7-4.9; indicator scorecard compiled from its executive summary
    - BC Public Accounts Note 28 (via the Land Ledger research), Northern Beat / PLUS FOI reporting,
      Western Standard ATIP story, Cowichan Tribes v. Canada (2025 BCSC 1490)
Output: data/report-bc-accountability-gap.json
"""
import glob, json, os, re, subprocess
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FNFTA_DIR = os.path.join(ROOT, "lake", "bc_fn_accountability", "fnfta")
OUT = os.path.join(ROOT, "data", "report-bc-accountability-gap.json")
FNHA_PDF = os.path.join(ROOT, "lake", "bc_fn_accountability", "raw", "fnha_pha_2024.pdf")

AUDITED, SCHEDULE = "Audited consolidated financial statements", "Schedule of Remuneration and Expenses"
FIRST_FY, LAST_FY = 2013, 2025  # fiscal years starting Apr 1 of that year (FY2013-14 ... FY2025-26)


def deadline(fy_start):
    """FNFTA: publish within 120 days after fiscal year end (Mar 31)."""
    return date(fy_start + 1, 3, 31) + timedelta(days=120)


def parse_date(s):
    try:
        return date.fromisoformat(s)
    except (TypeError, ValueError):
        return None  # "Not yet posted" etc.


def classify(filings, fy_start):
    """-> compliant | late | partial | none, from the two documents the Act requires."""
    fy = f"{fy_start}-{fy_start + 1}"
    got = {AUDITED: None, SCHEDULE: None}
    for f in filings:
        if f["fy"] == fy and f["doc"] in got:
            got[f["doc"]] = parse_date(f["received"])
    d = deadline(fy_start)
    have = [v for v in got.values() if v]
    if not have:
        return "none", None
    last = max(have)
    if len(have) == 1:
        return "partial", (last - d).days
    return ("compliant" if last <= d else "late"), (last - d).days


def load_bands():
    rows = []
    for p in sorted(glob.glob(os.path.join(FNFTA_DIR, "fnfta_*.json"))):
        j = json.load(open(p))
        for b in j["bands"]:
            rows.append({"prov": j["province"], **b})
    return rows


def is_exempt(filings):
    """Likely outside the Act (treaty / self-governing): never posted, or absent in 12+ of the 13 fiscal years.
    The portal does not label exemptions; this is an inference, and the nations are listed in bc_nations."""
    if not filings:
        return True
    missing = sum(1 for fy in range(FIRST_FY, LAST_FY + 1) if classify(filings, fy)[0] == "none")
    return missing >= 12


def timeline(bands):
    out = []
    for fy in range(FIRST_FY, LAST_FY + 1):
        c = {"compliant": 0, "late": 0, "partial": 0, "none": 0}
        n = 0
        for b in bands:
            if is_exempt(b["filings"]):
                continue
            n += 1
            c[classify(b["filings"], fy)[0]] += 1
        out.append({"fy": f"{fy}-{str(fy + 1)[2:]}", "fy_end_year": fy + 1, "deadline": deadline(fy).isoformat(),
                    "bands": n, **c, "filed_any": c["compliant"] + c["late"] + c["partial"],
                    "filed_both_pct": round(100 * (c["compliant"] + c["late"]) / n, 1) if n else None,
                    "on_time_pct": round(100 * c["compliant"] / n, 1) if n else None})
    return out


def median_days_after_deadline(bands):
    """Median days past the FY2024-25 deadline among BC nations that filed both documents (negative = early)."""
    days = []
    for b in bands:
        if b["prov"] == "BC" and not is_exempt(b["filings"]):
            st, d = classify(b["filings"], 2024)
            if st in ("compliant", "late"):
                days.append(d)
    days.sort()
    return days[len(days) // 2] if len(days) % 2 else (days[len(days) // 2 - 1] + days[len(days) // 2]) / 2


def bc_nations(bands):
    rows = []
    for b in bands:
        if b["prov"] != "BC":
            continue
        f = b["filings"] or []
        r = {"band": b["band"], "name": b["name"].lstrip("?"), "address": b["address"], "never_filed": not f, "likely_exempt": is_exempt(f)}
        for fy in (2023, 2024, 2025):
            st, days = classify(f, fy) if f else ("none", None)
            r[f"fy{fy}"] = st
            r[f"fy{fy}_days_vs_deadline"] = days
        r["years_missing_since_2013"] = sum(1 for fy in range(FIRST_FY, LAST_FY + 1) if f and classify(f, fy)[0] == "none") if f else None
        r["latest_audited_fy"] = max((x["fy"] for x in f if x["doc"] == AUDITED and parse_date(x["received"])), default=None)
        rows.append(r)
    rows.sort(key=lambda r: r["name"].lower())
    return rows


# ---------------- hand-compiled sections ----------------

CANADA_SPENDS_FNFTA = {
    "source": "Canada Spends, 'First Nations Financial Transparency Act Compliance' chart (X post, Feb 2026); underlying data: FNFTA portal",
    "url": "https://x.com/canada_spends/status/2020918286465253887",
    "note": "Chart year label = fiscal year; categories include Exempt (self-governed / sub-band) which the portal does not label. Transcribed from the chart image.",
    "years": {
        2014: {"compliant": 64, "late": 511, "non_compliant": None, "exempt_self_governed": None},
        2015: {"compliant": 192, "late": 382, "non_compliant": None, "exempt_self_governed": 38},
        2016: {"compliant": 158, "late": 413, "non_compliant": None, "exempt_self_governed": 38},
        2017: {"compliant": 109, "late": 458, "non_compliant": None, "exempt_self_governed": 39},
        2018: {"compliant": 54, "late": 507, "non_compliant": None, "exempt_self_governed": 39},
        2019: {"compliant": 55, "late": 490, "non_compliant": None, "exempt_self_governed": 40},
        2020: {"compliant": None, "late": 495, "non_compliant": 43, "exempt_self_governed": 40},
        2021: {"compliant": None, "late": 469, "non_compliant": 56, "exempt_self_governed": 40},
        2022: {"compliant": None, "late": 445, "non_compliant": 89, "exempt_self_governed": 40},
        2023: {"compliant": 38, "late": 386, "non_compliant": 137, "exempt_self_governed": 40},
        2024: {"compliant": None, "late": 321, "non_compliant": 204, "exempt_self_governed": 40},
        2025: {"compliant": None, "late": 191, "non_compliant": 349, "exempt_self_governed": 40},
    },
}

# Federal "Indigenous priorities" spending. Endpoints are as stated by Canada Spends (X post Nov 2025);
# intermediate bars are READ FROM THE CHART IMAGE (+/- ~$1B) because the series is not published as a table.
SPENDING = {
    "canada_spends": {
        "source": "Canada Spends: Public Accounts of Canada, departmental totals for CIRNAC, ISC and INAC (excludes Indigenous-specific programs in other departments)",
        "url": "https://x.com/canada_spends/status/1984211297924428149",
        "basis": "inflation-adjusted, as labelled on chart; includes settlement/liability accounting booked through ISC/CIRNAC (inferred from the 2023-24 and 2024 jumps; see caveat)",
        "cumulative_2014_2024_billions": 243.8,
        "stated_endpoints_billions": {"2014": 10.3, "2024": 63.9},
        "chart_read_billions_approx": {"2014": 10, "2015": 9, "2016": 9, "2017": 11, "2018": 14, "2019": 19,
                                      "2020": 22, "2021": 24, "2022": 25, "2023": 32, "2024": 62},
        "chart_read_note": "Bars read from image, +/- ~$1B. The 2024 bar reads ~$62B vs the $63.9B stated in the post text.",
        "page_figure_2024": "ISC + CIRNAC = ~$63B, 12.3% of federal spending (canadaspends.com, updated 2025-03-21)",
    },
    "fraser": {
        "source": "Fraser Institute, Flanagan & Li, The Cost of Federal Spending for Indigenous Peoples in British Columbia (Sept 2026)",
        "url": "https://www.fraserinstitute.org/sites/default/files/2026-09/cost-of-indigenous-spending-on-indigenous-peoples-in-british-columbia.pdf",
        "basis": "inflation-adjusted; excludes lawsuit/settlement payouts from 2015/16 onward; includes Indigenous programs in all departments",
        "national_billions": {"2014-15": 10.3, "2024-25": 40.8},
        "growth_vs_total_federal_spending": "7x faster since 2014/15",
        "bc_federal_2024_25_billions": 6.3,
        "bc_per_indigenous_person_2024_25": 20306,
        "bc_method_note": "Provincial figure apportions federal spending by each province's share of the Indigenous population (an estimate, not a ledger of payments to BC).",
    },
    "settlement_context": {
        "child_welfare_settlement_billions": 23.3,
        "note": "A ~$23.3B First Nations child-welfare settlement is booked in the 2023-24 departmental totals (per secondary reporting; confirm in Public Accounts before citing as a line item). One-time liabilities explain much of the gap between the $63.9B and $40.8B series.",
    },
    "per_person_screenshot": {
        "source": "Screenshot shared by @AmazingZoltan (X, Nov 2025) of a Canada Spends per-person view; screenshot has no title, year or denominator",
        "url": "https://x.com/AmazingZoltan/status/1984051601057992834",
        "rows": [
            {"area": "Indigenous Priorities", "dollars": 1251, "pct": 5.8},
            {"area": "Defence", "dollars": 1010, "pct": 4.7},
            {"area": "Employment Insurance", "dollars": 678, "pct": 3.2},
            {"area": "Public Safety", "dollars": 663, "pct": 3.1},
            {"area": "International Affairs", "dollars": 558, "pct": 2.6},
            {"area": "Colleges and Universities", "dollars": 469, "pct": 2.2},
            {"area": "Transportation", "dollars": 414, "pct": 1.9},
            {"area": "Infrastructure", "dollars": 366, "pct": 1.7},
            {"area": "Fisheries and Agriculture", "dollars": 293, "pct": 1.4},
            {"area": "Innovation and Research", "dollars": 271, "pct": 1.3},
            {"area": "Energy", "dollars": 227, "pct": 1.1},
            {"area": "Attorney and Solicitor General", "dollars": 212, "pct": 1.0},
            {"area": "Natural Resources", "dollars": 187, "pct": 0.9},
        ],
        "caveat": "The share (5.8%) does not match Canada Spends' own 12.3% for ISC+CIRNAC, so this view uses a different measure/denominator. Treat the ranking as indicative only; the screenshot's basis could not be verified.",
    },
}

LAND = {
    "note28_trend": [  # BC Public Accounts Note 28, hectares committed under treaty (Land Ledger research, primary PDFs)
        {"fy": "2021/22", "hectares": 129397.0}, {"fy": "2022/23", "hectares": 132980.0},
        {"fy": "2023/24", "hectares": 138590.6}, {"fy": "2024/25", "hectares": 137591.3},
        {"fy": "2025/26", "hectares": 135425.3},
    ],
    "note28_source": "BC Public Accounts 2021/22-2025/26, Note 28 (gov.bc.ca), as verified in the Canada Central 'Land Ledger' research",
    "completed_treaties_total_ha": 232746.0,
    "completed_treaties": ["Nisga'a (2000)", "Tsawwassen (2009)", "Maa-nulth (2011)", "Tla'amin (2016)"],
    "metro_vancouver_pct": 47.0,
    "parcels_committed": 400,
    "parcels_source": "Confidential 'Forest Compensation Framework' briefing dated Sept 10 2026, obtained by Northern Beat (Rob Shaw). BC NDP: 'a set of draft ideas'; slide deck states cabinet approved a request for decision in July. Parcel locations and total area not disclosed.",
    "forest_act_proposal": "Amend Forest Act (spring 2027 session): remove compensation to tenure holders for 'First Nations purposes' land deletions below a 5% cumulative AAC threshold; remove 6-year cap on special-purpose designations.",
    "agreements": [
        {"name": "Tahltan Foundation Agreement", "status": "Unsigned; revealed by FOI (Public Land Use Society, May 2026)",
         "scope": "~96,000 km2 asserted territory (~11% of BC); not proven in court or settled by treaty",
         "money": "$20M province grant (2020) to start negotiations; Eskay Creek consent deal reported ~$2B over 13 yrs; 37.5% of a portion of mineral-tax revenue; $500M federal support for Red Chris (announced Jul 2 2026)",
         "membership": "636 on reserve + 2,444 registered members elsewhere",
         "source": "Northern Beat / Public Land Use Society FOI", "url": "https://northernbeat.ca/news/backed-by-ottawa-bc-negotiates-governance-negotiates-aboriginal-title-in-mineral-rich-northwest/"},
        {"name": "Haida 'Rising Tide' title agreement", "status": "Signed 2025; BC + Canada joined Haida in BC Supreme Court for a consent declaration",
         "scope": "Aboriginal title recognized over entire Haida Gwaii archipelago (~1M ha), including private property", "source": "Northern Beat"},
        {"name": "shishalh Nation land and compensation deal", "status": "Struck before the 2024 election; details released after",
         "scope": "~6 km2 public land, $104M compensation", "source": "Northern Beat (Rob Shaw)"},
    ],
    "overlap_note": "Tahltan's own president (July 2025) cites overlapping claims with Kaska Dena and Taku River Tlingit as a core obstacle.",
}

COWICHAN = {
    "case": "Cowichan Tribes v. Canada (Attorney General), 2025 BCSC 1490",
    "decided": "2025-08-07", "judge": "Justice Barbara M. Young",
    "claimed_acres": 1846, "title_found_acres": 732,
    "held": [
        "The court found Aboriginal title over a portion of the claim area, called the Cowichan Title Lands (judgment para. 3724). The claim area is about 1,846 acres in Richmond; the judgment shows the title boundary on a map (Schedule A) and does not state its size in the text. Secondary reports put it at about 732 acres.",
        "Crown grants of fee simple in the title lands 'unjustifiably infringe' Aboriginal title. Only specific Canada-owned and Richmond-owned lots (other than the YVR fuel project lands) were declared 'defective and invalid'; that declaration is suspended for 18 months (paras. 3638, 3724).",
        "Privately held titles were not declared invalid: the plaintiffs did not seek that relief against private landowners, who are not parties (paras. 44, 2208). BC and Canada instead owe a duty to negotiate in good faith to reconcile those interests.",
        "On coexistence the judge wrote that Aboriginal title and private fee simple titles 'will exist in the same land at the same time until future litigation or negotiation further modifies them and/or clarifies the practical aspect of the relationship' (para. 2208).",
    ],
    "appeal": "All parties said they would appeal; BC stated 'a private property right sits above' Aboriginal title. A landowner (Montrose) bid to reopen was dismissed Jun 29 2026 and is itself under appeal. Status of the BC Court of Appeal hearing not confirmed.",
    "source": "Judgment text, Cowichan Tribes v. Canada (Attorney General), 2025 BCSC 1490, read directly; appeal status and the ~732-acre figure come from secondary reports",
}

CLAIM_CHECK = [
    {"claim": "95% of BC land is under an Aboriginal title claim (Keith Wilson, Nov 2025)",
     "source": "https://x.com/ikwilson/status/1986298645353013593",
     "verdict": "Not verified",
     "record": "No BC government, BC Treaty Commission or court source located for the 95% figure. It appears to originate in this post. Asserted territories overlap heavily and many are untested, so a share of 'claimed' land depends on whose map is used; asserted is not proven."},
    {"claim": "Once Aboriginal title is established it trumps fee simple granted to landowners",
     "verdict": "Partly accurate",
     "record": "Cowichan (2025 BCSC 1490): Crown grants of fee simple in the title lands were found to unjustifiably infringe Aboriginal title, and only specific Canada- and Richmond-owned lots were declared invalid (suspended 18 months). No private title was voided: that relief was not sought, and the judge wrote that title and private fee simple 'will exist in the same land at the same time' until litigation or negotiation clarifies it (para. 2208). The parties announced appeals, and BC says private property sits above title."},
    {"claim": "BC residents may soon no longer own their homes and businesses",
     "verdict": "Not supported by the ruling",
     "record": "Title was found over a portion of a 1,846-acre claim area of riverfront in Richmond (about 732 acres per secondary reports; the judgment shows a map, not a total). Private owners were not parties and no private title was declared invalid. The documented position is uncertainty until the appeals are decided; outcomes are not yet known."},
    {"claim": "Some 'First Nations' are First Nations only by name",
     "verdict": "Needs a precise term",
     "record": "Documented: Coastal First Nations is an alliance of ~8-10 of ~70 coastal communities, set up in 2004 with US foundation money (Rockefeller Brothers Fund $1M + $100k start-up). It is an association, not an Indian Act band or treaty government. Band councils and treaty nations are separate legal entities. Evidence offered is from Vivian Krause's tax-document research as reported by Northern Beat."},
    {"claim": "George Soros funds the groups behind these agreements",
     "verdict": "Not supported",
     "record": "The cited Northern Beat article never mentions Soros. Documented funders there: Packard, Hewlett, Rockefeller Brothers, Moore, Tides Canada / MakeWay, Nature Conservancy, MacKenzie Scott. Open Society Foundations has given to the US Tides Foundation (amounts vary by source) but no OSF grant to a BC First Nation was found, and OSF denied funding Northern Gateway opposition in 2012."},
    {"claim": "CIRNAC has no record of contact with BC's First Nations",
     "verdict": "Narrower than the headline",
     "record": "Western Standard (Jun 8 2026): an ATIP request for a summary of the latest contact with each BC First Nation returned 'none responsive'. ATIP covers records that exist; a department need not create a spreadsheet. It shows no consolidated contact log, not that no contact occurred. Financial submissions via the portal are themselves a documented contact."},
    {"claim": "First Nations quality of life has been falling over the same decade that spending rose",
     "verdict": "Partly accurate",
     "record": "BC First Nations life expectancy peaked at 75.7 years (2011 and 2013), fell to 73.3 by 2019 (before the pandemic) and to 67.2 in 2021; mortality rose; diabetes rose. But the steep fall is 2020-21, which the health authorities attribute mainly to the toxic drug crisis and COVID-19 (other BC residents fell ~1 year over the same span). Several indicators improved (infant mortality, school completion, youth suicide). The data stops in 2021, and nothing here shows spending or reporting rules caused or failed to prevent the decline."},
    {"claim": "$243.8B has gone to First Nations groups",
     "verdict": "Misleading as worded",
     "record": "$243.8B is cumulative federal 'Indigenous priorities' departmental spending 2014-2024 (Canada Spends), which includes health, housing, water, education, child welfare, land claims and settlement liabilities delivered to or for Indigenous people, not only transfers to band councils. Fraser's narrower inflation-adjusted series, excluding settlements, is $10.3B to $40.8B."},
]

# ---- Part 2: the wider fallout. Hand-compiled from the sources named in each item (searched 2026-10-19). ----
FALLOUT = {
    "settlements": [
        {"name": "First Nations child welfare / Jordan's Principle", "billions": 23.4, "status": "Approved", "when": "Approved Oct 24 2023; payments began Aug 2025",
         "note": "Covers children removed from homes on reserve or in Yukon, Apr 1 1991 to Mar 31 2022. Reported as $23.3B to $23.4B.",
         "url": "https://www.cbc.ca/1.7608989"},
        {"name": "Robinson Huron treaty annuities", "billions": 10.0, "status": "Settled", "when": "Settled 2023-24 (Canada $5B + Ontario $5B)",
         "note": "Annuity frozen at $4 per person since 1875. The Supreme Court (Restoule, July 2024) confirmed the Crown breached the treaties.",
         "url": "https://search.open.canada.ca/qpnotes/record/aandc-aadnc%2CCIR-2024-QP-2854"},
        {"name": "Drinking-water class action", "billions": 8.0, "status": "Approved", "when": "Agreement July 2021",
         "note": "Reported as nearly $8B: $1.5B compensation, a $400M restoration fund and at least $6B for water systems.",
         "url": "https://www.cbc.ca/1.6297372"},
        {"name": "Gottfriedson (language and culture)", "billions": 2.8, "status": "Approved", "when": "Approved Mar 13 2023",
         "note": "Paid to a trust run by a nine-member Indigenous board for 20 years; 325 First Nations in the class.",
         "url": "https://www.canada.ca/en/crown-indigenous-relations-northern-affairs/news/2023/03/federal-court-approves-band-class-litigation-settlement-agreement0.html"},
        {"name": "Treaty 9 annuities (Missanabie Cree class action)", "billions": 10.0, "status": "Claimed", "when": "Filed; certification pending",
         "note": "Claim of at least $10B. Treaty 9 has no promise to raise annuities with resource wealth, so the argument differs from Robinson. Not a settlement.",
         "url": "https://www.cbc.ca/lite/story/1.7355315"},
    ],
    "public_money": {
        "pbo_supp_b_2023_24": "PBO: Supplementary Estimates (B) 2023-24 included $5.0B for the Restoule Settlement Agreement, $1.6B for land-related claims and litigation and $596M for the Specific Claims Settlement Fund.",
        "pbo_url": "https://www.pbo-dpb.ca/en/publications/RP-2324-021-S--supplementary-estimates-b-2023-24--budget-supplementaire-depenses-b-2023-2024",
        "afr": "Government of Canada Annual Financial Report 2023-24: over $60B provided since 2016 to resolve Indigenous claims; about $16.4B of 2023-24 expenses were Indigenous contingent liabilities.",
        "afr_url": "https://www.canada.ca/en/department-finance/services/publications/annual-financial-report/2024.html",
        "clpa_s30_url": "https://laws-lois.justice.gc.ca/eng/acts/c-50/section-30-20090801.html",
    },
    "audits": {
        "fsin": {"auditor": "KPMG, for Indigenous Services Canada", "questionable_5yr_millions": 34, "demand_millions": 28.7, "covid_millions": 23.2,
                 "demand_letter": "2026-03-12", "period": "Apr 2019 to Mar 2024", "dispute_deadline": "2026-04-02",
                 "fsin_position": "Chief Bobby Cameron: 'We fully believe that we don't have to repay a dime'; legal action once chiefs give a mandate.",
                 "court_filing_found": False,
                 "url": "https://www.aptnnews.ca/national-news/feds-order-fsin-to-pay-back-28-7m-after-audit-found-issues/",
                 "isc_note_url": "https://search.open.canada.ca/qpnotes/record/isc-sac%2CISC-2026-QP-00838"},
        "auditor_general_2026_05": {"grants_billions": 6.5, "files_with_all_monitoring_pct": 39, "unmet_commitments": 2,
                 "url": "https://www.canada.ca/en/auditor-general/our-work/audit-reports/auditor-general-202605-new-fiscal-initiatives-with-first-nations.html"},
    },
    "projects": [
        {"project": "Northern Gateway pipeline", "year": 2016, "outcome": "Approval quashed (Federal Court of Appeal)", "stated_reason": "Federal consultation with First Nations was inadequate. Neither the company nor Ottawa appealed.", "url": "https://infonews.ca/?p=1839491"},
        {"project": "Trans Mountain expansion", "year": 2018, "outcome": "Approval quashed, later re-approved and built", "stated_reason": "Inadequate consultation and exclusion of marine traffic from the regulator's review.", "url": "https://www.fraserinstitute.org/commentary/trans-mountain-and-problem-pipeline-consultation-canada"},
        {"project": "Energy East pipeline", "year": 2017, "outcome": "Cancelled by TransCanada", "stated_reason": "Company cited regulatory delay, cost and the scope of the review; the federal minister and some economists cited market conditions. No First Nations court ruling was involved.", "url": "https://amp.cbc.ca/lite/story/1.4342050"},
        {"project": "Teck Frontier oil sands mine", "year": 2020, "outcome": "Application withdrawn", "stated_reason": "Teck cited the absence of a framework reconciling resource development and climate policy. No First Nations court ruling was involved.", "url": "https://www.teck.com/news/news-releases/2020/teck-withdraws-regulatory-application-for-frontier-project"},
        {"project": "Cedar LNG (Kitimat)", "year": 2025, "outcome": "Haisla Nation holds 50.1% equity; start-up expected 2027-28", "stated_reason": "Counter-example: Indigenous equity ownership, financed in part by a $1.4B loan from the First Nations Finance Authority.", "url": "https://www.bnnbloomberg.ca/business/2025/09/19/how-canadas-haisla-became-the-worlds-first-indigenous-lng-owners/"},
    ],
    "courts": {
        "gitxaala_bcca": "Dec 5 2025 (2025 BCCA 430): the majority held DRIPA brings UNDRIP into BC law with immediate effect and found the online mineral-claim system inconsistent with it.",
        "gitxaala_url": "https://www.bdplaw.com/insights/bcca-on-gitxaala-what-does-undrip-mean-for-resource-development-in-british-columbia-and-canada",
        "scc_leave": "The Gitxaala campaign page says the Supreme Court granted BC leave to appeal on May 21 2026, with a hearing expected in 2027.",
        "scc_url": "https://raventrust.com/gitxaala/",
        "eby": "Premier Eby called changing DRIPA 'non-negotiable' in April 2026. Search results later suggested a pivot to suspending key parts for three years; passage was not confirmed.",
        "eby_url": "https://theturtleislandnews.com/index.php/2026/04/02/premier-eby-says-changing-dripa-is-non-negotiable-and-will-pass-this-session/",
        "mining_fraser": "Fraser Institute commentary: BC mineral claims fell 29% in 2025 and claimed area 61% versus the seven-year average.",
        "mining_fraser_url": "https://www.fraserinstitute.org/commentary/bc-government-should-repeal-dripa-help-spur-mining-investment",
        "mining_counter": "The 2024 industry exploration survey (EY/AME) attributed a 14% fall in exploration spending partly to financing constraints and maturing projects; it predates the Gitxaala ruling.",
        "mining_counter_url": "https://www.ey.com/en_ca/newsroom/2025/02/bc-exploration-spending-declines-as-flagship-projects-mature",
        "mpo_url": "https://www.cp24.com/news/canada/2026/10/14/major-projects-ceo-faces-bc-first-nations-frustrated-over-lack-of-consultation/",
        "cowichan_lender_url": "https://www.ctvnews.ca/vancouver/article/councillor-says-100m-project-denied-loan-over-cowichan-case-bank-says-not-a-factor/",
        "wolastoqey_url": "https://www.torys.com/our-latest-thinking/publications/2026/05/scc-declines-to-hear-wolastoqey-nation-appeal",
    },
}

CLAIM_CHECK_2 = [
    {"claim": "The federal fast-track law is Bill C-39, the Building Canada Act", "verdict": "Not supported as stated",
     "record": "The law that lets 'designated projects' bypass some federal laws is Bill C-5. Coverage of the Oct 2026 Major Projects Office story describes it as Bill C-5.", "source": "https://www.cp24.com/news/canada/2026/10/14/major-projects-ceo-faces-bc-first-nations-frustrated-over-lack-of-consultation/"},
    {"claim": "The drinking-water settlement is $6.9B ($1.5B compensation plus $5.4B infrastructure)", "verdict": "Not supported as stated",
     "record": "Reports put it at nearly $8B: $1.5B compensation, a $400M restoration fund and at least $6B for water systems.", "source": "https://www.cbc.ca/1.6297372"},
    {"claim": "The Supreme Court ruling resulted in the $10B Robinson Huron settlement", "verdict": "Partly accurate",
     "record": "The $10B ($5B each from Canada and Ontario) was settled before the July 2024 Restoule ruling. The ruling confirmed the Crown breached the treaties and left the Robinson Superior claim to be negotiated.", "source": "https://search.open.canada.ca/qpnotes/record/aandc-aadnc%2CCIR-2024-QP-2854"},
    {"claim": "ISC demanded $12.3M from the FSIN and the FSIN filed a Federal Court judicial review", "verdict": "Not verified",
     "record": "ISC's March 2026 letter sought $28.7M after an audit flagged about $34M as questionable, ineligible or unsupported. The FSIN disputes it and says it will take legal action once chiefs give a mandate. No court filing or $12.3M figure was found.", "source": "https://www.aptnnews.ca/national-news/feds-order-fsin-to-pay-back-28-7m-after-audit-found-issues/"},
    {"claim": "Multibillion-dollar settlements bypass Parliament", "verdict": "Partly accurate",
     "record": "Parliament does not vote on each settlement, and judgment payments can come from the Consolidated Revenue Fund without an appropriation. But settlement money still enters the Estimates (for example $5.0B for Restoule in Supplementary Estimates B 2023-24) and the liabilities are recorded in the Public Accounts.", "source": "https://www.pbo-dpb.ca/en/publications/RP-2324-021-S--supplementary-estimates-b-2023-24--budget-supplementaire-depenses-b-2023-2024"},
    {"claim": "Firms cancel major projects because of First Nations disputes and lawsuits", "verdict": "Partly accurate",
     "record": "Northern Gateway and Trans Mountain approvals were quashed over consultation. Energy East and Frontier were cancelled citing regulatory delay, markets and climate policy, not a First Nations ruling. Indigenous equity ownership has also enabled projects such as Cedar LNG.", "source": "https://pgjonline.com/news/2025/march/canada-s-canceled-oil-pipelines-the-projects-that-didn-t-make-it"},
    {"claim": "A court let a First Nation's title claim proceed over land under a multibillion-dollar export facility", "verdict": "Not verified",
     "record": "The project and case were not named, and no matching case was found in the sources reviewed. The nearest documented examples are the Cowichan ruling (Richmond, with airport fuel lands carved out) and the Gitxaala mineral-claims ruling."},
]

# ---- Part 3: overlapping claims, BC project outcomes, who speaks for whom. Sources named per item (searched 2026-10-19). ----
OVERLAPS = [
    {"dispute": "Kitselas and K'omoks treaties", "who": "Nine Allied Tribes, Lax Kw'alaams, Wei Wai Kum vs the treaty nations and BC",
     "what": "In April 2026 a coalition said it was ready to block major projects, including the corridors feeding the Port of Prince Rupert, and take legal action unless BC paused the treaties. They said the agreements reach into their territory and they were not consulted. Lax Kw'alaams said it does not oppose the treaty process itself.",
     "status": "K'omoks Treaty Act passed on a free vote (May 2026 report); Kitselas Treaty Act not expected back for a vote until fall. BC's minister said overlap is not new and urged more talks.",
     "url": "https://www.castanetkamloops.net/news/BC/610140/Overlapping-claims-are-behind-protests-from-First-Nations-against-two-treaties",
     "url2": "https://energeticcity.ca/2026/05/28/a-first-nation-treaty-decades-in-making-faces-further-delays-says-b-c-minister/"},
    {"dispute": "Cowichan vs Musqueam and Tsawwassen (Richmond)", "who": "Cowichan Tribes, Stz'uminus, Penelakut, Halalt vs Musqueam and Tsawwassen",
     "what": "Musqueam and Tsawwassen were two of six defendants opposing the claim. The court found the Cowichan's evidence of occupation more persuasive. Musqueam said it 'fundamentally disagrees' with the judgment. The judge wrote that all parties have continued interests around the south arm of the Fraser and that the findings will affect relationships among them (para. 3726).",
     "status": "All parties have appealed; BC and Cowichan have begun negotiations.",
     "url": "https://www.coastreporter.net/real-estate/tsawwassen-first-nation-reviews-ruling-on-cowichan-nation-claims-11107099",
     "url2": "https://www.canlii.org/en/bc/bcsc/doc/2025/2025bcsc1490/2025bcsc1490.html"},
    {"dispute": "Gitanyow vs Nisga'a", "who": "Gitanyow vs Nisga'a Lisims Government",
     "what": "Gitanyow filed a 2003 claim to about 6,200 km2 that overlaps Nisga'a treaty lands; the Nisga'a were added as a party. Gitanyow argues overlaps must be resolved before treaties are concluded.",
     "status": "Long-running; legal commentators count dozens of overlap cases tied to modern treaty negotiations.",
     "url": "https://ablawg.ca/2024/09/23/modern-treaties-shared-territories-and-party-status-in-aboriginal-title-litigation/", "url2": "https://gitanyowchiefs.com/?p=7697"},
    {"dispute": "Tahltan vs Taku River Tlingit (Shesley River area)", "who": "Tahltan Nation vs Taku River Tlingit First Nation",
     "what": "After Taku River Tlingit declared an Indigenous protected area, the Tahltan said part of it, the Shesley River area, is Tahltan territory and that they had not consented (2024 report). The Tahltan also fully support the Eskay Creek mine, which Alaska tribal nations downstream have opposed.",
     "status": "Tahltan said they would meet their neighbour. Eskay Creek has all permits and is targeting a 2027 restart.",
     "url": "https://canadianminingjournal.com/news/alaska-tribes-seek-rights-in-british-columbia-to-protect-unuk-river-watershed-from-gold-mining", "url2": "https://www.cbc.ca/1.7107190"},
    {"dispute": "Wet'suwet'en hereditary chiefs vs elected councils", "who": "Hereditary house chiefs vs elected band councils",
     "what": "Two governance systems claim to speak for the same people. Eight of nine hereditary house chiefs opposed Coastal GasLink; 20 elected councils along the route signed benefits agreements. The Union of BC Indian Chiefs sided with the hereditary chiefs.",
     "status": "Contested since 2019-20; elected chiefs also disputed the 2020 title memorandum between hereditary chiefs, Ottawa and BC.",
     "url": "https://www.pressreader.com/canada/the-province/20190121/281522227276290", "url2": "https://www.plant.ca/general/wetsuweten-pact-with-ottawa-and-bc-disputed-by-elected-chiefs-192614/"},
    {"dispute": "Okanagan Nation Alliance civil claim", "who": "Okanagan Nation Alliance vs BC and Canada",
     "what": "A civil claim challenging BC's treaty process over overlapping claims; the BC Treaty Commission's Chief Commissioner called for negotiation rather than litigation.",
     "status": "Reported in the 2020s; current status not checked.",
     "url": "https://amp.cbc.ca/news/indigenous/first-nations-alliance-launches-court-challenge-of-b-c-treaty-process-1.2734282", "url2": None},
    {"dispute": "Haida title (Haida Gwaii)", "who": "Council of the Haida Nation, BC, Canada",
     "what": "The 2024 Rising Tide agreement recognizes Haida title to Haida Gwaii. Its preamble states the Haida have no overlap with other Indigenous nations' interests on terrestrial Haida Gwaii; that is the Haida position written into the agreement, not a tribunal finding. No objection from other nations was found. Critics question how private land and parks fit.",
     "status": "Provincial Act in force; a federal counterpart agreement followed in Feb 2025; transition issues remain.",
     "url": "https://nationalmagazine.ca/en-ca/articles/hot-topics-in-law/2024/will-the-haida-s-rising-tide-agreement-raise-all-boats", "url2": "https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/consulting-with-first-nations/agreements/draft_haida_title_lands_agreement_27march2024_bilateral.pdf"},
]
OVERLAP_CONTEXT = {
    "scale": "A University of Victoria source says every BC First Nation has at least one overlap area with another, because most nations never signed treaties.",
    "scale_url": "https://dspace.library.uvic.ca/server/api/core/bitstreams/9d0735a8-8ad0-4775-82a0-d0ff42da197b/content",
    "ancillary": "Overlap matters for the consent question: if two nations assert title to the same land, a deal with one can be challenged by the other.",
}

BC_PROJECTS = [
    {"project": "Pacific NorthWest LNG (Lelu Island)", "year": 2017, "outcome": "Cancelled by Petronas and partners",
     "stated_reason": "The company cited changes in market conditions. Some Lax Kw'alaams members camped on the site for most of a year in protest, while leaders of other nearby nations supported the project. An industry CEO blamed delays by BC and Ottawa. BC's energy minister said it was global pricing.",
     "url": "https://www.cbc.ca/news/canada/british-columbia/pacific-northwest-lng-project-in-port-edward-b-c-no-longer-proceeding-1.4220936", "url2": "https://www.cbc.ca/lite/story/1.4224651"},
    {"project": "New Prosperity gold-copper mine (Fish Lake)", "year": 2014, "outcome": "Rejected twice by Ottawa (2010, 2014); courts upheld; final appeal refused 2020",
     "stated_reason": "A federal panel found significant, irreversible effects on water, fisheries and Tsilhqot'in cultural heritage. Taseko's court challenges failed; the Supreme Court refused leave in 2020.",
     "url": "https://biv.com/article/2020/05/new-prosperity-mine-dead-tsilhqotin", "url2": "https://www.mining.com/?p=773103"},
    {"project": "Site C dam", "year": 2018, "outcome": "Built; Treaty 8 challenges did not stop it",
     "stated_reason": "The Federal Court of Appeal and BC Court of Appeal dismissed challenges in early 2017. In 2018 the BC Supreme Court refused an injunction but ordered the Treaty 8 infringement claim to be tried. The final outcome of that trial was not confirmed.",
     "url": "https://amp.cbc.ca/news/canada/british-columbia/site-c-west-moberly-first-nation-injunction-1.4877673", "url2": "https://biv.com/article/2017/02/bc-court-appeal-dismisses-another-site-c-legal-cha"},
    {"project": "Coastal GasLink pipeline", "year": 2019, "outcome": "Built despite hereditary-chief opposition",
     "stated_reason": "Benefits agreements were signed with 20 elected band councils along the route; eight of nine Wet'suwet'en hereditary house chiefs opposed. The dispute is about who has authority, not only about the project.",
     "url": "https://www.pressreader.com/canada/the-province/20190121/281522227276290", "url2": None},
    {"project": "Eskay Creek mine", "year": 2026, "outcome": "Permitted in a first joint regulatory decision with the Tahltan Nation",
     "stated_reason": "Tahltan support the mine and co-decided on it. Alaska tribal nations downstream, who are not parties to the BC decision, have asked BC and Canada for recognition and a pause.",
     "url": "https://canadianminingjournal.com/news/alaska-tribes-seek-rights-in-british-columbia-to-protect-unuk-river-watershed-from-gold-mining", "url2": None},
]

ORGS = {
    "caveat": "This is a high-level map from public documents, not a ranking. Funding is shown only where a public document gave it; 'not found' means the sources reviewed did not break it down.",
    "groups": [
        {"group": "Elected band councils", "kind": "Government (Indian Act)", "speaks_for": "Their registered members on reserve and often off-reserve. The legal counterpart for most federal funding and programs.",
         "funding": "Mainly federal transfers plus own-source revenue; they file the financial statements this report examines in sections 1-2.", "notes": "In BC about 200 bands, many not covered by the transparency Act because of treaty or self-government.", "url": None},
        {"group": "Hereditary chiefs and houses", "kind": "Traditional governance", "speaks_for": "Their houses and clans, and in several cases the title-holding nation (for example the Wet'suwet'en).",
         "funding": "Not found for the groups reviewed; the Office of the Wet'suwet'en was set up to represent the nation in treaty talks.", "notes": "Contested alongside elected councils in the Wet'suwet'en case.", "url": "https://www.plant.ca/general/wetsuweten-pact-with-ottawa-and-bc-disputed-by-elected-chiefs-192614/"},
        {"group": "Assembly of First Nations (AFN) and BC Assembly of First Nations (BCAFN)", "kind": "Political body of chiefs", "speaks_for": "Chiefs of member First Nations (AFN: over 600 bands nationally; BCAFN is the BC regional body).",
         "funding": "Audited statements are adopted by the chiefs in assembly (BCAFN's 2024-25 statements by KPMG, Oct 2025). Revenue by source was not found in the documents reviewed.", "notes": "Speaks for governments, not individual members.", "url": "https://www.bcafn.ca/sites/default/files/uploads/resolutions/2025_22_AGM_Resolution_ADOPTION%20OF%20THE%202024-2025%20AUDITED%20FINANCIAL%20STATEMENTS.pdf"},
        {"group": "First Nations Summit and Union of BC Indian Chiefs (UBCIC)", "kind": "Political bodies of chiefs", "speaks_for": "The Summit: about 150 First Nations taking part, focused on the treaty process. UBCIC (founded 1969): nations that reject the current treaty process and defend title and rights.",
         "funding": "Not found.", "notes": "With the BCAFN they form the First Nations Leadership Council under a 2005 accord. Some bands belong to more than one.", "url": "https://en.wikipedia.org/wiki/First_Nations_Summit"},
        {"group": "First Nations Health Authority (FNHA)", "kind": "Service organization created by tripartite agreement (2011)", "speaks_for": "BC First Nations for health governance and delivery.",
         "funding": "Federal funding agreement of roughly $380 million a year for 2013-2023 (about $4.7 billion), plus BC support.", "notes": "A public service body, not an advocacy group.", "url": "https://sac-isc.gc.ca/eng/1584706392620/1584706415366"},
        {"group": "Coastal First Nations - Great Bear Initiative", "kind": "Alliance of nations (non-profit society)", "speaks_for": "Nine to ten member First Nations on the north and central coast and Haida Gwaii. Its board has one representative from each member.",
         "funding": "Grants and contributions of $16.9 million in the year to March 2022 (from $10.6 million in FY2020). Partners named: governments of Canada and BC, Coast Funds, BC Hydro, the Gordon and Betty Moore Foundation, MakeWay, the Wilburforce Foundation, Nature United, The Nature Conservancy, Rogers and others. The split by funder was not given.",
         "notes": "An alliance of First Nation governments, not a nation or band itself. It is not 'in name only', but it is a mixed public and private-philanthropy funded body.", "url": "https://coastalfirstnations.ca/wp-content/uploads/2024/12/CFN-Annual-Report-2021-22.pdf"},
        {"group": "First Nations Major Projects Coalition", "kind": "Alliance (industry-participation focus)", "speaks_for": "Nearly 85 member nations, mostly in BC, seeking equity in major projects.",
         "funding": "Federal: $2.6 million (2021) and $13.5 million (2022) from Natural Resources Canada. It backed the federal Indigenous loan guarantee program.", "notes": "Supports Indigenous ownership of resource projects.", "url": "https://www.canada.ca/en/natural-resources-canada/news/2022/07/canada-invests-in-the-first-nations-major-projects-coalition-to-advance-indigenous-participation-in-natural-resource-projects.html"},
        {"group": "Indian Resource Council and National Coalition of Chiefs", "kind": "Pro-development advocacy", "speaks_for": "The IRC advocates federal policy to expand First Nations economic development (led by Stephen Buffalo). The Coalition: 50-plus chiefs and Metis leaders who opposed Bill C-69 and Bill C-48.",
         "funding": "Not found. Much coverage comes from think-tank commentary, so treat framing as advocacy.", "notes": "Membership lists were not found.", "url": "https://www.fraserinstitute.org/commentary/trudeau-government-should-listen-chiefs-and-support-natural-resource-development"},
        {"group": "Indigenous-led environmental groups and funders (for example Raven Trust, Indigenous Climate Action, Tides Canada / MakeWay)", "kind": "NGOs and intermediary funders", "speaks_for": "Their own boards and supporters, often alongside affected nations.",
         "funding": "Foundations such as Rockefeller Brothers, Moore, Packard, Hewlett and the Nature Conservancy, per the Northern Beat reporting used in section 7. Grant-level records are in public tax filings but were not compiled here.", "notes": "Foreign philanthropy is lawful and reported; whether it should shape land-use talks is a political question.", "url": "https://northernbeat.ca/news/us-money-behind-anti-resource-activism-in-bc-as-american-oil-exports-grew/"},
    ],
}

# ---- Part 4: the "reconciliation industry" debate, living conditions, and what public filings show about the groups. ----
CS_FEES_B = 23.4  # child-welfare settlement, $ billions (see FALLOUT)
RECON = {
    "quote_source": {"speaker": "Aaron Pete, Chief of Chawathil First Nation (per The Hub's author page)", "medium": "Video interview posted on X by Sitka Media (link supplied by the report's author); transcript produced by automatic speech recognition, so names and some numbers are garbled.",
                     "x_url": "https://x.com/sitkamedia/status/2098475436833747038", "hub_url": "https://thehub.ca/author/aaronpete/"},
    "claims": [
        {"claim": "Communities lack staff and funds, so lawyers and consultants fill gaps a municipality would fill in-house.",
         "verdict": "Supported in principle", "record": "Governance guidance and case law treat consultation capacity funding as a recognised need. A Saugeen decision linked the duty to consult to capacity funding, and a University of Calgary study found insufficient capacity funding pushes costs onto project proponents. No public data shows how much each nation spends on outside professionals.",
         "url": "https://fngovernance.org/Consultation_Funding_FactSheet"},
        {"claim": "Federal and provincial processes require lawyers by design, such as specific-claims tribunals and treaty negotiation.",
         "verdict": "Supported", "record": "The Specific Claims Tribunal is a court-like body that can award up to $150 million, and treaty negotiation is a legal process. BC's treaty negotiations were funded for decades by negotiation support loans: about $707 million allocated since 1993 (about $551 million as loans), with the loans forgiven federally from 2019-20. How that money was split between lawyers, consultants and staff is not published in the sources found.",
         "url": "https://amp.cbc.ca/news/indigenous/budget-2019-treaty-loans-forgiven-1.5063128"},
        {"claim": "Advisers push a confrontational approach instead of a good deal for everyone.",
         "verdict": "Not verifiable", "record": "This is a claim about motives and cannot be tested from documents. What the record shows: the child-welfare tribunal case ran from at least 2007 through the 2016 ruling and beyond, and Ottawa also spent on the other side. The Justice Department reported $5.26 million on the tribunal case (2007 to Dec 2019) while documents obtained by the Caring Society showed more than $8 million, and Federal Court costs were withheld.",
         "url": "https://www.aptnnews.ca/national-news/federal-government-holding-back-true-cost-of-fighting-first-nations-children-at-tribunal/"},
        {"claim": "Most of the money that goes to lawyers for specific claims does not improve anyone's life.",
         "verdict": "Not verified", "record": "No public source breaks down specific-claims settlements by what was spent on legal fees versus community programs. For the one large class action where fees are public, the court cut counsel fees from a negotiated $55 million to $40 million (about 0.17% of the $23.4 billion settlement). That is small relative to the award, but it was paid from public funds and is separate from the nations' own legal costs.",
         "url": "https://amp.cbc.ca/news/politics/federal-court-approves-40-million-legal-fees-child-welfare-1.7068704"},
        {"claim": "BCAFN and UBCIC are a large bureaucracy for 204 First Nations who are about 4% of the population, and it is not improving members' living conditions.",
         "verdict": "Not verified", "record": "The figures are garbled in the transcript and were not confirmed. BC has about 200 First Nations (this report's data lists 199 bands). The organizations' own funding by source was not found, and neither is a registered charity (see below), so there is no standard public return to check.",
         "url": None},
    ],
    "fees": {"child_welfare_requested_m": 80, "child_welfare_deal_m": 55, "child_welfare_awarded_m": 40, "tribunal_official_m": 5.26, "tribunal_atip_min_m": 8.0,
             "bc_treaty_support_allocated_m": 707, "bc_treaty_support_loans_m": 551, "bc_treaty_support_grants_m": 156,
             "fees_pct_of_settlement": round(40 / (CS_FEES_B * 1000) * 100, 2),
             "requested_pct_of_settlement": round(80 / (CS_FEES_B * 1000) * 100, 2),
             "fees_url": "https://amp.cbc.ca/news/politics/federal-court-approves-40-million-legal-fees-child-welfare-1.7068704",
             "deal_url": "https://www.cbc.ca/lite/story/1.7025474",
             "tribunal_url": "https://www.aptnnews.ca/national-news/federal-government-holding-back-true-cost-of-fighting-first-nations-children-at-tribunal/",
             "treaty_url": "https://amp.cbc.ca/news/indigenous/budget-2019-treaty-loans-forgiven-1.5063128",
             "treaty_url2": "https://bctreaty.ca/?p=2254"},
    "conditions": {
        "ltdwa_count": 40, "ltdwa_communities": 37, "ltdwa_asof": "May 2026",
        "ltdwa_url": "https://waterportal.ca/water-news/first-nations-drinking-water-advisories-2026/", "ltdwa_isc_url": "https://www.sac-isc.gc.ca/eng/1614387410146",
        "foster_care_indigenous_pct": 53.8, "foster_care_child_pop_pct": 7.7, "foster_care_url": "https://globalnews.ca/news/9145379/indigenous-kids-overrepresented-foster-care",
        "per_capita_indigenous_pct_in_care": 3.2, "per_capita_non_indigenous_pct_in_care": 0.2,
        "ag_grants_outcomes": "The Auditor General found the department did not know whether 10-year grants were closing gaps with other Canadians (May 2026).",
    },
    "filings_check": {
        "method": "Name search of the CRA's list of charities (apps.cra-arc.gc.ca) on 2026-10-19. A group that is a not-for-profit society or corporation rather than a registered charity files no public T3010 return.",
        "not_found": ["Assembly of First Nations", "First Nations Summit", "Union of BC Indian Chiefs", "Coastal First Nations - Great Bear Initiative", "First Nations Major Projects Coalition", "Indian Resource Council", "Indigenous Climate Action"],
        "found": [{"name": "MakeWay Foundation and MakeWay Charitable Society (formerly Tides Canada)", "note": "Both registered in Vancouver. A third-party aggregator reports about $25.8M revenue for the year to March 2024, and MakeWay says it supported 70 Indigenous governments. The T3010 line items were not retrieved because the CRA site would not render in automated browsing.", "url": "https://makeway.org/2024annualreport/", "url2": "https://www.causeiq.com/organizations/makeway-foundation,980404212"}],
        "caveat": "A name search can miss organizations registered under a different legal name. The AFN's own audited statements were not located in this research.",
        "cra_url": "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscSrch?request_locale=en",
    },
}

FOREIGN_FUNDING = {
    "source": "Northern Beat (Rob Shaw/ staff), 'US money behind anti-resource activism in BC', citing Vivian Krause's US tax-filing research",
    "url": "https://northernbeat.ca/news/us-money-behind-anti-resource-activism-in-bc-as-american-oil-exports-grew/",
    "reliability_note": "Northern Beat is an advocacy-leaning outlet and Krause's work is contested. The underlying filings (US Form 990s, Canadian charity returns) are public and should be checked at source.",
    "documented": [
        {"item": "Rockefeller Brothers Fund: $1M capital + $100k start-up for Coastal First Nations (2004)", "per": "Krause, citing tax filings"},
        {"item": "Moore Foundation: ~$270M into Canadian activism since 2000s, ~$30M to Coastal First Nations, ~$85M via Tides Canada (incl. $10M grant, 2015)", "per": "Krause (reported)"},
        {"item": "Great Bear Rainforest fund (2007): $120M total, $30M federal share; US donors named: Packard, Wilberforce, Hewlett, Rockefeller Brothers, Moore", "per": "Tides Canada's then-CEO (2007 remarks)"},
        {"item": "MakeWay (formerly Tides Canada): $86M from MacKenzie Scott since 2022", "per": "Northern Beat"},
        {"item": "Coast Economic Development Society + related society: $120M annual revenue and endowment, private donors plus BC and federal subsidies", "per": "Krause (reported)"},
    ],
    "context": [
        "Funding to First Nation-led conservation is lawful and charitable-sector transparent; the question raised is who sets land-use agenda when external funds shape negotiation tables.",
    ],
}

TIMELINE_EVENTS = [
    {"date": "2013-03", "event": "First Nations Financial Transparency Act passes (S.C. 2013, c. 7): bands must publish audited statements and a remuneration schedule within 120 days of year-end"},
    {"date": "2015-12-18", "event": "Minister Bennett ends discretionary compliance measures; ~$12M withheld from ~43 bands is reinstated; court actions suspended"},
    {"date": "2016-04", "event": "BC Provincial Health Officer declares the toxic drug (overdose) public health emergency"},
    {"date": "2017-01", "event": "National Post: 85% of bands still compliant for the last year, versus 90%+ while funding was at stake"},
    {"date": "2020", "event": "BC-Tahltan 'shared prosperity' agreement: $20M province grant to begin Foundation Agreement talks"},
    {"date": "2024", "event": "shishalh deal ($104M, ~6 km2) struck before the BC election, details released after"},
    {"date": "2024-08-21", "event": "FNHA/PHO report: First Nations life expectancy fell from 73.3 (2017) to 67.2 (2021)"},
    {"date": "2025-08-07", "event": "Cowichan Tribes v. Canada decided (BCSC)"},
    {"date": "2026-06-08", "event": "Western Standard publishes CIRNAC ATIP response: 'none responsive'"},
    {"date": "2026-07-02", "event": "Canada-BC 'cooperative prosperity agreement'; $500M federal support for Red Chris; Ottawa to support Tahltan Foundation Agreement"},
    {"date": "2026-09-10", "event": "Confidential BC briefing: ~400 parcels committed; Forest Act compensation change; cabinet approval in July per slide deck"},
]


# ---------------- health outcomes (FNHA/PHO) ----------------

YEARS_HEALTH = list(range(2005, 2022))  # the report's figures run 2005-2021


def _numbers(line, n):
    """Last n numeric tokens on a layout-text line (handles thousands commas)."""
    toks = re.findall(r"\d[\d,]*\.?\d*", line)
    return [float(t.replace(",", "")) for t in toks][-n:] if len(toks) >= n else None


def _figure_rows(text, marker, n_rows):
    i = text.index(marker)
    rows = []
    for line in text[i:i + 6000].splitlines():
        nums = _numbers(line, len(YEARS_HEALTH))
        # skip the axis line (2005 2006 ...), keep data rows
        if nums and not (nums[0] == 2005 and nums[-1] == 2021):
            rows.append(nums)
        if len(rows) == n_rows:
            return rows
    raise ValueError(f"could not parse {marker}")


def parse_health():
    txt_path = os.path.join(os.path.dirname(FNHA_PDF), "..", "clean", "fnha.txt")
    if not os.path.exists(txt_path):
        subprocess.run(["pdftotext", "-layout", FNHA_PDF, txt_path], check=True)
    text = open(txt_path, encoding="utf-8", errors="ignore").read()
    le = _figure_rows(text, "FIGURE 4.7", 2)
    sex = _figure_rows(text, "FIGURE 4.8", 4)
    mort = _figure_rows(text, "FIGURE 4.9", 4)
    # sanity checks against values stated in the report's own prose
    assert le[0][YEARS_HEALTH.index(2017)] == 73.3 and le[0][-1] == 67.2, "life expectancy parse drifted"
    assert mort[0][YEARS_HEALTH.index(2017)] == 117.3 and mort[0][-1] == 156.0, "mortality parse drifted"
    series = {}
    for name, vals in [("le_first_nations", le[0]), ("le_other", le[1]), ("le_fn_female", sex[0]), ("le_fn_male", sex[1]),
                       ("le_other_female", sex[2]), ("le_other_male", sex[3]), ("mort_first_nations", mort[0]), ("mort_other", mort[1]),
                       ("deaths_first_nations", mort[2]), ("deaths_other", mort[3])]:
        series[name] = dict(zip(YEARS_HEALTH, vals))
    return series


HEALTH_SCORECARD = {
    "source": "FNHA & BC Office of the Provincial Health Officer, First Nations Population Health and Wellness Agenda: First Interim Update (Aug 2024), executive summary and chapters 3-4. Status First Nations in BC unless stated.",
    "url": "https://www.fnha.ca/wp-content/uploads/migrated/Documents/FNHA-PHO-First-Nations-Population-Health-and-Wellness-Agenda-First-Interim-Update-2024.pdf",
    "data_ends": 2021,
    "next_update": "Mid-term update projected for 2026/27 (per the report); not yet located as of this report.",
    "indicators": [
        {"indicator": "Life expectancy at birth", "baseline": "73.3 yrs (2017)", "latest": "67.2 yrs (2021)", "direction": "worse", "size": "substantial"},
        {"indicator": "All-cause mortality (per 10,000, age-standardized)", "baseline": "117.3 (2017)", "latest": "156.0 (2021)", "direction": "worse", "size": "substantial"},
        {"indicator": "Diabetes incidence (per 1,000)", "baseline": "8.0 (2017/18)", "latest": "8.5 (2020/21)", "direction": "worse", "size": "substantial"},
        {"indicator": "Healthy birth weight (singleton births)", "baseline": "73.8% (2017)", "latest": "72.1% (2019)", "direction": "worse", "size": "slight"},
        {"indicator": "Infant mortality (per 1,000 live births)", "baseline": "5.3 (2013-17)", "latest": "4.6 (2015-19)", "direction": "better", "size": "slight, not statistically significant"},
        {"indicator": "Youth/young adult suicide deaths (per 10,000, age 15-24)", "baseline": "3.1 (2013-17)", "latest": "2.8 (2017-21)", "direction": "better", "size": "slight"},
        {"indicator": "High school completion, Indigenous students (within 8 yrs)", "baseline": "69.9% (2016/17)", "latest": "74.2% (2019/20)", "direction": "better", "size": "significant"},
        {"indicator": "Avoidable hospitalizations (per 10,000)", "baseline": "73.3 (2017/18)", "latest": "72.6 (2021/22)", "direction": "same", "size": "no substantial change"},
        {"indicator": "Serious injuries requiring hospital (per 1,000)", "baseline": "31.4 (2017/18)", "latest": "31.1 (2021/22)", "direction": "same", "size": "virtually unchanged"},
        {"indicator": "Physicians who self-identify as First Nations", "baseline": "0.32% (2019)", "latest": "0.39% (2023)", "direction": "same", "size": "no meaningful change"},
    ],
    "not_updated": "8 of the 22 tracked indicators had no new data; children's oral health data was excluded for quality reasons.",
    "toxic_drug_2023": {
        "rate_vs_other_residents": "more than 6x", "female_rate_vs_other_females": "11.7x", "fn_deaths": 448, "bc_total_deaths_prelim": 2511,
        "fn_share_of_deaths_pct": 17.8, "fn_share_of_bc_population": "under 4%", "fn_poisoning_events_2023": 3446, "fn_poisoning_events_2022": 3068,
        "emergency_declared": "2016 (BC Provincial Health Officer)",
    },
    "stated_cause": "The report and FNHA's chief medical officer attribute the 2019-2021 fall mainly to the toxic drug crisis and COVID-19; the report also frames the underlying inequities as the legacy of colonial policy. Its own analysis names drug toxicity and COVID-19 as the two leading causes of reduced life expectancy for both First Nations and other residents.",
    "quotes": [
        {"who": "Dr. Daniele Behn Smith, deputy provincial health officer for Indigenous health", "text": "Clearly, this life expectancy data is gut wrenching.", "src": "CBC News, Aug 21 2024"},
        {"who": "Dr. Nel Wieman, FNHA chief medical health officer", "text": "[The decline was] largely due to the COVID-19 pandemic and the province's opioid overdose crisis.", "src": "CBC News (paraphrase of her remarks), Aug 21 2024", "paraphrase": True},
    ],
    "caveats": [
        "Life expectancy is a population measure; the report notes it does not indicate quality of life or years in good health.",
        "2020-2021 First Nations births had not yet been added to the registry; the analysis assumes 2019 infant mortality for those years.",
        "Figures describe Status First Nations people in BC. Spending figures in this report are national (Canada Spends) or an estimate (Fraser), so the two cannot be matched dollar for dollar.",
        "Feb 2024 FNHA slides gave a 5.8-year fall for 2019-2021 and 7.1 years for 2015-2021; the 2024 report gives 6.1 and (from peak) larger. Differences reflect data vintage and chosen baseline.",
    ],
}


def outcomes_vs_spending(health):
    """Join by YEAR KEY (never array position). Spending: Canada Spends chart reads, national, 2014-2024."""
    sp = {int(k): v for k, v in SPENDING["canada_spends"]["chart_read_billions_approx"].items()}
    sp[2014], sp[2024] = 10.3, 63.9  # stated endpoints
    rows = []
    for y in YEARS_HEALTH:
        rows.append({"year": y, "le_first_nations": health["le_first_nations"][y], "le_other": health["le_other"][y],
                     "gap_years": round(health["le_other"][y] - health["le_first_nations"][y], 1),
                     "mort_first_nations": health["mort_first_nations"][y], "mort_other": health["mort_other"][y],
                     "deaths_first_nations": int(health["deaths_first_nations"][y]),
                     "federal_spending_billions": sp.get(y)})
    return rows


def sync_html(result):
    """Reports embed their data (no runtime fetch): re-stitch DATA between the markers in the page."""
    page = os.path.join(ROOT, "reports", "bc-accountability-gap.html")
    if not os.path.exists(page):
        return
    html = open(page, encoding="utf-8").read()
    a, b = "/*DATA_START*/", "/*DATA_END*/"
    i, j = html.index(a) + len(a), html.index(b)
    blob = json.dumps(result, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    open(page, "w", encoding="utf-8").write(html[:i] + "const DATA = " + blob + ";" + html[j:])
    print(f"  Synced DATA into {page}")


def main():
    bands = load_bands()
    health = parse_health()
    nat = timeline(bands)
    bc = timeline([b for b in bands if b["prov"] == "BC"])
    by_prov = {}
    for p in sorted({b["prov"] for b in bands}):
        t = timeline([b for b in bands if b["prov"] == p])
        by_prov[p] = {"fy2024_25": next(x for x in t if x["fy"] == "2024-25"), "fy2023_24": next(x for x in t if x["fy"] == "2023-24")}

    result = {
        "metadata": {
            "title": "The Provincial and Federal Wedge Dividing BC's Sovereignty",
            "last_updated": date.today().isoformat(),
            "fnfta_fetched": max(json.load(open(p))["fetched"] for p in glob.glob(os.path.join(FNFTA_DIR, "fnfta_*.json"))),
            "fnfta_method": ("Compliance recomputed from the ISC/CIRNAC portal 'Date Received' for the audited statements and the Schedule of "
                             "Remuneration. Deadline = fiscal year-end (Mar 31) + 120 days. compliant = both received by the deadline; late = both "
                             "received after; partial = only one; none = neither. Portal shows the latest version received, so a re-filed document "
                             "can show a later date. Bands that never filed in 12+ of 13 years are treated as likely exempt (treaty / self-governing) and excluded from the denominator."),
            "sources": [
                "ISC/CIRNAC First Nation Profiles: FNFTA search (fnp-ppn.aadnc-aandc.gc.ca)",
                "Canada Spends (canadaspends.com; X posts Feb 2026, Nov 2025)",
                "Fraser Institute, Flanagan & Li (Sept 2026)",
                "Northern Beat (Rob Shaw; Public Land Use Society FOI; US-funding article)",
                "Western Standard, 'EXCLUSIVE: Federal indigenous department admits it has no record of contact with BC's First Nations' (2026-06-08)",
                "BC Public Accounts 2025/26 Note 28",
                "Cowichan Tribes v. Canada, 2025 BCSC 1490 (judgment text)",
                "FNHA & BC PHO, Population Health and Wellness Agenda: First Interim Update (Aug 2024)",
                "CBC News, 'First Nations life expectancy plunges by 6 years in B.C.: report' (Aug 21 2024)",
                "Keith Wilson, X post 2025-11-07 (claim checked, not relied on)",
                "Part 2 sources: CBC, Canada.ca (CIRNAC, Auditor General, Annual Financial Report), PBO, APTN, Teck, CP24, Fraser Institute, EY (see fallout in this file)",
            ],
        },
        "fnfta_national": nat,
        "fnfta_bc": bc,
        "fnfta_by_province": by_prov,
        "fnfta_canada_spends": CANADA_SPENDS_FNFTA,
        "bc_nations": bc_nations(bands),
        "bc_median_days_after_deadline_2024_25": median_days_after_deadline(bands),
        "western_standard_claim": {"bc_2025_submitted": 69, "bc_2024_submitted": 128, "bc_first_nations": "200-plus",
                                   "note": "Counts as of the June 2026 article; portal recomputation is in fnfta_bc."},
        "health": {"source": HEALTH_SCORECARD, "series": health, "years": YEARS_HEALTH, "joined": outcomes_vs_spending(health)},
        "spending": SPENDING,
        "land": LAND,
        "cowichan": COWICHAN,
        "claim_check": CLAIM_CHECK,
        "claim_check_2": CLAIM_CHECK_2,
        "fallout": FALLOUT,
        "recon": RECON,
        "overlaps": OVERLAPS, "overlap_context": OVERLAP_CONTEXT, "bc_projects": BC_PROJECTS, "orgs": ORGS,
        "foreign_funding": FOREIGN_FUNDING,
        "timeline_events": TIMELINE_EVENTS,
        "images": {
            "bc_peoples_map": {"file": "lake/bc_fn_accountability/images/bc-first-nations-peoples-map.jpeg",
                               "note": "Cultural/linguistic territories map adapted from Cheryl Coull, 'A Traveller's Guide to Aboriginal B.C.' (Whitecap Books). It is NOT a title-claim or treaty map and cannot be used to estimate % of BC claimed."},
        },
    }
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Wrote {OUT}")
    sync_html(result)
    print("National FNFTA:", nat[0]["fy"], "->", nat[-1]["fy"])
    for t in nat[-4:]:
        print(" ", t["fy"], {k: t[k] for k in ("bands", "compliant", "late", "partial", "none", "filed_both_pct")})
    print("BC:")
    for t in bc[-4:]:
        print(" ", t["fy"], {k: t[k] for k in ("bands", "compliant", "late", "partial", "none", "filed_both_pct")})


if __name__ == "__main__":
    main()
