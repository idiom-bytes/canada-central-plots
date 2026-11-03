"""Transform data for "The Land Ledger" (BC treaty land commitments) report.

All figures below are manually compiled and cross-checked against primary
sources (BC Public Accounts PDFs 2021/22-2025/26, BC Treaty Commission
Final Agreement fact sheets, StatCan Table 32-10-0047-01, official treaty
text) rather than pulled from an automated bulk download -- see
docs/kb-bc-treaty-land.md and docs/research-*.md for the full research
trail and every source URL.

Sources:
- BC Public Accounts 2021/22-2025/26, Note 28 "Contingent Liabilities and
  Contractual Obligations" (gov.bc.ca)
- BC Treaty Commission Final Agreement fact sheets (Nisga'a, Tsawwassen,
  Maa-nulth, Tla'amin, Yale) (gov.bc.ca)
- Ministry of Indigenous Relations and Reconciliation, "TTA Treaty Area
  and Treaty Lands" map package (June 2026)
- StatCan Table 32-10-0047-01, "Value per acre of farm land and buildings"
- Encyclopedia of British Columbia (KnowBC) - BC reserve land aggregate
- News coverage: CHEK News, Times Colonist, Daily Hive, The Epoch Times
  (Aug 9-12, 2026 news cycle)
Output: data/report-bc-treaty-land.json
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# ---------------------------------------------------------------------------
# Chapter 1 data: the Note 28 commitment itself
# ---------------------------------------------------------------------------

TREND = [
    {"fiscal_year": "2021/22", "hectares": 129397.0, "nations_count": 18},
    {"fiscal_year": "2022/23", "hectares": 132980.0, "nations_count": 19},
    {"fiscal_year": "2023/24", "hectares": 138590.6, "nations_count": 20},
    {"fiscal_year": "2024/25", "hectares": 137591.3, "nations_count": 20},
    {"fiscal_year": "2025/26", "hectares": 135425.3, "nations_count": 20},
]

# 20 nations/tables listed in the 2025/26 Public Accounts, Note 28.
NATIONS_2025_26 = [
    {"name": "Ditidaht", "hectares": 3567.0, "status": "Negotiating"},
    {"name": "Homalco", "hectares": 707.0, "status": "Negotiating"},
    {"name": "In-SHUCK-ch (Skatin and Samahquam)", "hectares": 9474.0, "status": "Negotiating"},
    {"name": "Kaska Dena Council", "hectares": 677.0, "status": "Negotiating"},
    {"name": "Kitselas", "hectares": 35290.0, "status": "Final Agreement ratified Apr 10, 2025 -- awaiting effective date"},
    {"name": "Kitsumkalum", "hectares": 45789.0, "status": "Final Agreement ratified Nov 1, 2025 -- awaiting effective date"},
    {"name": "K'omoks", "hectares": 3040.0, "status": "Final Agreement ratified Mar 8, 2025 -- awaiting effective date"},
    {"name": "Ktunaxa Nation Council", "hectares": 418.0, "status": "Negotiating"},
    {"name": "Lake Babine Nation (BC only)", "hectares": 497.6, "status": "Incremental Treaty Agreement (+ one-time payment of $0.02M)"},
    {"name": "Lax Kw'alaams First Nation", "hectares": 4309.0, "status": "Negotiating"},
    {"name": "Lheidli T'enneh", "hectares": 3416.0, "status": "Negotiating"},
    {"name": "Nazko", "hectares": 172.0, "status": "Negotiating"},
    {"name": "NStQ (Canoe Creek, Sugar Cane, Canim Lake, Soda Creek)", "hectares": 3095.0, "status": "Negotiating"},
    {"name": "Pacheedaht", "hectares": 1216.0, "status": "Negotiating"},
    {"name": "Te'mexw (Malahat, Scia'new, Snaw-naw-as, Songhees, T'Sou-ke)", "hectares": 1916.7, "status": "Stage 5 negotiation -- Victoria/South Island (see Chapter 2)"},
    {"name": "Tla-o-qui-aht", "hectares": 47.0, "status": "Negotiating"},
    {"name": "Wei Wai Kai (Cape Mudge First Nation)", "hectares": 612.0, "status": "Negotiating"},
    {"name": "Wei Wai Kum (Campbell River First Nation)", "hectares": 1276.0, "status": "Negotiating"},
    {"name": "Wuikinuxv", "hectares": 13946.0, "status": "Negotiating"},
    {"name": "Yekooche", "hectares": 5960.0, "status": "Negotiating"},
]

# Disclosed in the same Note 28 but NOT included in the 20-nation table sum.
YALE = {
    "name": "Yale First Nation",
    "note28_hectares": 1179.0,
    "fact_sheet_hectares": 1966.0,
    "status": "Final Agreement ratified 2011/2013 -- effective date not yet agreed, 13+ years on",
    "discrepancy_note": (
        "BC Public Accounts Note 28 has listed Yale's commitment as 1,179 ha, "
        "unchanged, in every fiscal year from 2021/22 through 2025/26. BC's own "
        "2010 Yale Lands fact sheet states 1,966 ha (217 ha former reserve + "
        "1,749 ha additional Crown land). The discrepancy is unresolved in "
        "public documents -- reported here as an open question, not settled."
    ),
}

NOTE28_TOTAL_2025_26 = 135425.3
NOTE28_TOTAL_INCL_YALE = 136604.3

# Land already transferred under BC's completed, in-effect modern treaties --
# contrast figure for the pending Note 28 commitment.
COMPLETED_TREATIES = [
    {"name": "Nisga'a", "effective_date": "2000-05-11", "hectares": 199200.0},
    {"name": "Tsawwassen", "effective_date": "2009-04-03", "hectares": 724.0},
    {"name": "Maa-nulth (5 Nations)", "effective_date": "2011-04-01", "hectares": 24500.0},
    {"name": "Tla'amin", "effective_date": "2016-04-05", "hectares": 8322.0},
]
COMPLETED_TREATIES_TOTAL_HA = sum(t["hectares"] for t in COMPLETED_TREATIES)  # ~232,746 ha

BENCHMARKS = {
    "acres_total": 334642,
    "km2_total": 1354.25,
    "metro_vancouver_km2": 2878.93,
    "metro_vancouver_pct": 47.0,
    "vancouver_city_km2": 115.18,
    "vancouver_city_multiple": 11.8,
    "stanley_park_ha": 404.9,
    "stanley_park_multiple": 334.5,
    "farmland_value_per_acre_2025": 10577,
    "farmland_value_source": "Statistics Canada, Table 32-10-0047-01 (2025)",
    "farmland_total_value_estimate": 3540000000,
    "farmland_caveat": (
        "Farmland value is a weak proxy for this land -- the Note 28 total is "
        "mostly forested/rural Crown land, not agricultural land, and BC "
        "farmland values themselves range more than 40x by region ($2,400 to "
        "$104,600/acre per Farm Credit Canada's 2025 report). This is an "
        "illustrative scale benchmark, not an appraisal."
    ),
}

RESERVE_LAND = {
    "bc_reserve_hectares": 473485.0,
    "bc_reserve_source": "Encyclopedia of British Columbia (KnowBC) -- secondary reference figure, no single ISC/StatCan provincial rollup located",
    "pending_commitment_hectares": NOTE28_TOTAL_2025_26,
    "ratio_reserve_to_pending": round(473485.0 / NOTE28_TOTAL_2025_26, 2),
}

# ---------------------------------------------------------------------------
# Chapter 2 data: Victoria / Te'mexw / Songhees case study
# ---------------------------------------------------------------------------

VICTORIA_PARCELS = [
    {
        "parcel": "Hatley Park / Hatley Castle",
        "map_category": "Federal Crown Land",
        "approx_hectares": 229.0,
        "status": "Existing federal Crown land (Dept. of National Defence); proposed transfer to Songhees as treaty settlement land; contested by a separate Esquimalt Nation civil claim filed Mar 27, 2026",
        "in_note28": False,
        "reason": "Federal land -- outside Note 28's provincial-Crown-land scope entirely",
    },
    {
        "parcel": "New Songhees 1A",
        "map_category": "Songhees Nation Reserve",
        "approx_hectares": None,
        "status": "Existing Indian Reserve since 1911 (Songhees relocated from Inner Harbour)",
        "in_note28": False,
        "reason": "Already-held reserve land, not a new commitment",
    },
    {
        "parcel": "Esquimalt 113",
        "map_category": "Provincial Crown Land",
        "approx_hectares": None,
        "status": "New provincial Crown land parcel near Lampson St.",
        "in_note28": True,
        "reason": "Genuine new provincial commitment, part of the Te'mexw 1,916.7 ha figure",
    },
    {
        "parcel": "Enterprise Wharf",
        "map_category": "Provincial Crown Land",
        "approx_hectares": None,
        "status": "Waterfront parking/dock parcel, 1112 Wharf St.",
        "in_note28": True,
        "reason": "Genuine new provincial commitment",
    },
    {
        "parcel": "Q Lot",
        "map_category": "Provincial Crown Land",
        "approx_hectares": None,
        "status": "Parking lot, 430 Menzies St. beside the Legislature; assessed at $24.8M (Times Colonist)",
        "in_note28": True,
        "reason": "Genuine new provincial commitment",
    },
    {
        "parcel": "PCC Pandora",
        "map_category": "Songhees Nation Private Land",
        "approx_hectares": None,
        "status": "Already privately owned by Songhees Nation (fee simple)",
        "in_note28": False,
        "reason": "Not Crown land at all",
    },
    {
        "parcel": "Tl'ches -- Chatham Islands 4",
        "map_category": "Songhees Nation Reserve",
        "approx_hectares": None,
        "status": "Existing Chatham Islands Indian Reserve No. 4",
        "in_note28": False,
        "reason": "Already-held reserve land",
    },
    {
        "parcel": "Tl'ches -- Discovery Island 3",
        "map_category": "Songhees Nation Reserve",
        "approx_hectares": None,
        "status": "Likely existing Indian Reserve No. 3 (not independently confirmed against a federal reserve registry)",
        "in_note28": False,
        "reason": "Already-held reserve land (pending final confirmation)",
    },
    {
        "parcel": "Tl'ches -- Discovery Island Park",
        "map_category": "Provincial Park Land",
        "approx_hectares": None,
        "status": "Strip of Discovery Island Marine Provincial Park",
        "in_note28": True,
        "reason": "New commitment, park sub-category",
    },
]

TEMEXW_STATUS = {
    "member_nations": ["Malahat", "Scia'new (Beecher Bay)", "Snaw-naw-as", "Songhees", "T'Sou-ke"],
    "statement_of_intent": "1994-07-15",
    "agreement_in_principle": "2015-04-10",
    "agreement_in_principle_hectares": 1565.0,
    "current_stage": "Stage 5 of 6 (Negotiation to Finalize a Treaty)",
    "map_source": "Ministry of Indigenous Relations and Reconciliation, \"TTA Treaty Area and Treaty Lands\" map package, June 2026 (govTogetherBC engagement site)",
    "esquimalt_claim_filed": "2026-03-27",
    "esquimalt_claim_status": "Ongoing / unresolved as of Aug 12, 2026",
}

# ---------------------------------------------------------------------------
# Chapter 3 data: public access precedent on already-effective treaties
# ---------------------------------------------------------------------------

# NOTE: Yale First Nation is intentionally excluded here. Its Final Agreement
# was ratified by all parties (2011/2013) but BC Public Accounts Note 28
# states verbatim, across all 5 fiscal years checked: "A treaty effective
# date has not yet been agreed to by the parties." Yale is therefore NOT
# one of BC's effective/in-force modern treaties -- see YALE above, which
# already treats it as a separate, not-yet-effective disclosure. Including
# it here as "effective" would contradict that and Chapter 1's treatment.
ACCESS_PRECEDENT = [
    {
        "treaty": "Nisga'a",
        "effective_date": "2000-05-11",
        "default_land_status": "Fee simple",
        "access_summary": "Public access guaranteed on Nisga'a Public Lands for temporary recreational use (Ch. 6). But Nisga'a Nation may close to the public any non-village Nisga'a road (Ch. 7, para 60(1)) -- the clearest documented precedent for restricted access.",
        "restriction_example": True,
    },
    {
        "treaty": "Tsawwassen",
        "effective_date": "2009-04-03",
        "default_land_status": "Fee simple",
        "access_summary": "Public rights-of-way written into standard interest documents. Tsawwassen Mills (1.2M sq ft mall) was later built on treaty settlement land removed from the Agricultural Land Reserve -- a real, documented land-use change, though the mall itself remains open to the public.",
        "restriction_example": False,
    },
    {
        "treaty": "Maa-nulth (5 Nations)",
        "effective_date": "2011-04-01",
        "default_land_status": "Fee simple, explicit private-land parity",
        "access_summary": "Official text: each Maa-nulth Nation has \"the same rights and obligations in respect of public access... as other owners of estates in fee simple.\" Thunderbird's Nest (2,185 ha) was added to protected status under the treaty -- an access/conservation gain.",
        "restriction_example": False,
    },
    {
        "treaty": "Tla'amin",
        "effective_date": "2016-04-05",
        "default_land_status": "Fee simple",
        "access_summary": "Public recreational access guaranteed on Tla'amin Public Lands and the Sunshine Coast Trail. But Ahgykson (Harwood Island) was designated Tla'amin Private Land with restricted public access on the treaty's own effective date -- the clearest named example of access being narrowed.",
        "restriction_example": True,
    },
]

TREATY_PROCESS_STAGES = [
    "1. Statement of Intent",
    "2. Readiness to Negotiate",
    "3. Framework Agreement",
    "4. Agreement in Principle",
    "5. Finalization -> Final Agreement",
    "6. Implementation",
]


def main():
    result = {
        "metadata": {
            "title": "The Land Ledger",
            "last_updated": "2026-08-12",
            "sources": [
                "BC Public Accounts 2021/22-2025/26, Note 28 (gov.bc.ca)",
                "BC Treaty Commission Final Agreement fact sheets (gov.bc.ca)",
                "Ministry of Indigenous Relations and Reconciliation, TTA Treaty Area and Treaty Lands map (June 2026)",
                "Statistics Canada Table 32-10-0047-01",
                "Encyclopedia of British Columbia (KnowBC)",
                "CHEK News, Times Colonist, Daily Hive, The Epoch Times (Aug 9-12 2026)",
            ],
        },
        "trend": TREND,
        "nations_2025_26": NATIONS_2025_26,
        "yale": YALE,
        "note28_total_2025_26": NOTE28_TOTAL_2025_26,
        "note28_total_incl_yale": NOTE28_TOTAL_INCL_YALE,
        "completed_treaties": COMPLETED_TREATIES,
        "completed_treaties_total_ha": COMPLETED_TREATIES_TOTAL_HA,
        "benchmarks": BENCHMARKS,
        "reserve_land": RESERVE_LAND,
        "victoria_parcels": VICTORIA_PARCELS,
        "temexw_status": TEMEXW_STATUS,
        "access_precedent": ACCESS_PRECEDENT,
        "treaty_process_stages": TREATY_PROCESS_STAGES,
    }

    out_path = os.path.join(DATA_DIR, "report-bc-treaty-land.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Wrote {out_path}")
    print(f"  Trend: {TREND[0]['fiscal_year']} ({TREND[0]['hectares']} ha) -> {TREND[-1]['fiscal_year']} ({TREND[-1]['hectares']} ha)")
    print(f"  Nations in 2025/26 table: {len(NATIONS_2025_26)}, sum = {sum(n['hectares'] for n in NATIONS_2025_26):.1f} ha")


if __name__ == "__main__":
    main()
