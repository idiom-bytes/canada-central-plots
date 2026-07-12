"""Fetch and compile data for the Heavy-Duty Truck Certification Gap investigation.

This topic has no live machine-readable API — the data is compiled from:
  - Canada Gazette SOR/2018-98 (regulatory language)
  - Environment and Climate Change Canada regulatory filings (2024 acknowledgement)
  - ECCC Forward Regulatory Plan 2024-2026 (gap acknowledgement)
  - FleetNerd Canada Trucking Statistics (unit volumes)
  - ACT Research North America Class 8 Forecast (market sizing)
  - Canadian Truck Dealers Association / BNN Bloomberg (May 2026 reporting)
  - EPA Federal Register (Phase 3 rule, GHG rescission)
  - UK SI 2019/648 — Road Vehicles (Type-Approval) (Amendment) (EU Exit) Regulations 2019
  - Transport Canada MVSA 2026 consultation (January-March 2026) — ambulatory references debate
  - SOR/2003-2 On-Road Vehicle and Engine Emission Regulations (parallel GHG gap)

Output: data/trucking.json
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    result = {
        "metadata": {
            "title": "Canada Heavy-Duty Truck Certification Gap",
            "slug": "trucking-certification",
            "updated": "2026-05-21",
            "sources": [
                "Canada Gazette SOR/2018-98",
                "ECCC HD GHG Emission Regulations (SOR-2013-24)",
                "SOR/2003-2 On-Road Vehicle and Engine Emission Regulations — Justice Canada",
                "ECCC Forward Regulatory Plan 2024-2026 — Canada.ca",
                "EPA Federal Register — GHG Phase 3 Final Rule (2024-04-22)",
                "EPA Federal Register — GHG Rescission Final Rule (2026-02-12)",
                "FleetNerd Canada Trucking Statistics",
                "ACT Research 2026 Class 8 Forecast",
                "Canadian Truck Dealers Association (May 2026)",
                "BNN Bloomberg / Globe and Mail (2026-05-21)",
                "UK SI 2019/648 — Road Vehicles (Type-Approval) (Amendment) (EU Exit) Regulations 2019 — legislation.gov.uk",
                "Transport Canada MVSA 2026 Consultation — Various changes to regulations under the MVSA (January-March 2026)",
            ],
        },

        # ── Regulatory timeline ──────────────────────────────────────────────
        "timeline": [
            {
                "date": "2013",
                "label": "Canada HD GHG Regulations published",
                "body": "SOR/2013-24 published. Canada adopts HD GHG emission standards aligned with U.S. EPA Phase 1. Language: engines certified by EPA may be sold in Canada.",
                "type": "milestone",
            },
            {
                "date": "2016-10",
                "label": "U.S. Phase 2 joint EPA/NHTSA rule finalized",
                "body": "EPA and NHTSA jointly finalize Phase 2 HD GHG standards for MY2021–2027. Both agencies co-certify.",
                "type": "milestone",
            },
            {
                "date": "2018-05",
                "label": "Canada harmonizes with EPA Phase 2",
                "body": "SOR/2018-98 published. Canada aligns with Phase 2. Key provision: any engine certified by EPA may be sold in Canada without separate Canadian compliance demonstration.",
                "type": "milestone",
            },
            {
                "date": "2024-04",
                "label": "Biden EPA finalizes Phase 3 (EPA-only)",
                "body": "Phase 3 GHG standards for MY2027+ finalized by EPA alone — NHTSA not a co-author, unlike Phase 1 and 2. Canada's own regulatory documents note amendments will be needed. No amendments published.",
                "type": "warning",
            },
            {
                "date": "2025-03",
                "label": "Trump EPA announces intent to rescind GHG Endangerment Finding",
                "body": "EPA announces reconsideration of the 2009 Endangerment Finding — the legal basis for all GHG vehicle certifications. U.S. manufacturers flag Transport Canada immediately. No action taken.",
                "type": "warning",
            },
            {
                "date": "2025-05",
                "label": "Canadian manufacturers formally flag Ottawa",
                "body": "Canadian Truck Dealers Association and U.S. manufacturers formally flag the certification gap to Transport Canada. Government acknowledges but takes no action.",
                "type": "warning",
            },
            {
                "date": "2026-02-12",
                "label": "Trump EPA rescinds all GHG vehicle standards",
                "body": "EPA finalizes repeal of 2009 Endangerment Finding and all federal GHG vehicle emission standards. EPA can no longer legally certify heavy-duty trucks. NHTSA becomes sole federal certifier. Gap is now a legal fact.",
                "type": "gap_created",
            },
            {
                "date": "2026-05-21",
                "label": "Canadian Truck Dealers Association goes public",
                "body": "CTDA publicly warns dealers cannot import 2027-model trucks. Government confirms it is working on a resolution.",
                "type": "current",
            },
            {
                "date": "2026-08",
                "label": "Fleet ordering window — key deadline",
                "body": "Canadian fleets make annual renewal decisions for the 2027 model year. Regulatory alignment must be in place before this window.",
                "type": "deadline",
            },
            {
                "date": "2027",
                "label": "2027 model year",
                "body": "Without orders placed in August 2026, new heavy-duty truck supply for 2027 would be significantly curtailed.",
                "type": "risk",
            },
        ],

        # ── Market sizing ────────────────────────────────────────────────────
        "market": {
            "annual_units_low": 17000,
            "annual_units_mid": 18500,
            "annual_units_high": 20000,
            "avg_price_usd": 195000,
            "avg_price_cad": 265000,
            "us_supply_share_pct": 95,
            "lead_time_months_min": 12,
            "lead_time_months_max": 18,
            "built_to_order_note": "Class 8 trucks are essentially 100% built-to-order. Missing the ordering window means missing supply for that model year entirely.",
            "north_america_combined_2025": 232741,
            "canada_pct_of_na": 8,
            "source": "FleetNerd; ACT Research 2026 Forecast; BNN Bloomberg",
        },

        # ── Historical unit volumes (Canada, Class 8) ─────────────────────
        "unit_history": [
            {"year": 2019, "units": 23310, "note": "pre-COVID peak"},
            {"year": 2020, "units": 14720, "note": "COVID disruption"},
            {"year": 2021, "units": 12500, "note": "chip shortage"},
            {"year": 2025, "units": 18500, "note": "down 11% from 2024; estimate based on NA share"},
        ],

        # ── Financial impact ─────────────────────────────────────────────────
        "financial_impact": {
            "direct_purchase_low_cad": 4505000000,
            "direct_purchase_mid_cad": 4902500000,
            "direct_purchase_high_cad": 5300000000,
            "industry_annual_revenue_cad": 65000000000,
            "aftermarket_2025_cad": 6340000000,
            "aftermarket_2026_forecast_cad": 7000000000,
            "incremental_maintenance_per_truck_cad": 20000,
            "incremental_fuel_cost_estimate_cad": 255000000,
            "incremental_maintenance_estimate_cad": 340000000,
            "fleet_operating_cost_total_estimate_cad": 595000000,
            "freight_rate_pressure_low_cad": 3250000000,
            "freight_rate_pressure_high_cad": 6500000000,
            "new_2027_spec_price_premium_usd_low": 20000,
            "new_2027_spec_price_premium_usd_high": 30000,
            "note": "Direct purchase figure well-grounded in unit volumes and pricing. Downstream freight rate pressure is order-of-magnitude estimate from 5-10% capacity squeeze on $65B industry.",
        },

        # ── Affected sectors ──────────────────────────────────────────────────
        "sectors": [
            {"name": "Shipping & Freight",   "icon": "truck",     "desc": "Primary logistics backbone. Fleet aging raises per-km costs and reduces capacity."},
            {"name": "Construction",          "icon": "building",  "desc": "Heavy equipment transport and materials delivery depend on Class 8 availability."},
            {"name": "Infrastructure",        "icon": "road",      "desc": "Road, utilities, and public works projects rely on continuous heavy hauling."},
            {"name": "Forestry",              "icon": "tree",      "desc": "Log and pulp transport with tight operational windows."},
            {"name": "Mining",                "icon": "mine",      "desc": "Ore and mineral haulage; fleet constraints compound in remote locations."},
            {"name": "Agriculture",           "icon": "grain",     "desc": "Grain, livestock, and supply transport compressed into short seasonal windows."},
        ],

        # ── Regulatory context ───────────────────────────────────────────────
        "regulatory": {
            "canada_statute": "Canadian Environmental Protection Act, 1999 (CEPA) — SOR/2013-24 as amended by SOR/2018-98",
            "canada_key_provision": "Section 13: any engine certified by EPA may be sold in Canada without demonstrating separate Canadian compliance.",
            "canada_gap_provision": "Section 59.1 addresses suspension or revocation of individual EPA certificates — it has no provision for EPA ceasing to issue certificates entirely.",
            "us_change": "EPA rescission of 2009 GHG Endangerment Finding (February 12, 2026) eliminated EPA's legal authority to certify GHG emissions for all vehicle classes.",
            "remaining_us_certifier": "NHTSA retains authority over fuel economy (CAFE) standards and safety — now the primary federal certifier for 2027+ heavy-duty trucks.",
            "canada_2018_commitment_type": "Unilateral domestic regulation under CEPA. Motivated by non-binding 2016 Obama-Trudeau Joint Statement. Not a treaty, not an MOU.",
            "trailer_precedent": "When U.S. trailer GHG standards were challenged in 2019, Canada did not amend its regulations — it issued the first of seven consecutive ministerial interim orders under CEPA section 163(3).",
            "eccc_2024_acknowledgement": "In mid-2024, ECCC's own regulatory documents stated 'amendments to the HD Vehicle and Engine GHG Emission Regulations will be needed in Canada to ensure continued alignment.' No proposed amendments were published in Canada Gazette Part I.",
            "parallel_ghg_gap": "Canada's SOR/2003-2 (On-Road Vehicle and Engine Emission Regulations) and SOR/2013-24 also cite EPA certificates as the recognized standard. Both are subject to the same gap created by the February 2026 EPA GHG rescission — the trucking certification issue is one instance of a broader regulatory reference failure.",
            "uk_precedent": "When the UK left the EU in 2021, vehicle type approval regulations (SI 2019/648) were updated via statutory instrument to replace EU certifying body references with domestic GB equivalents — the same mechanism available under Canada's Motor Vehicle Safety Act.",
            "ambulatory_reference_debate": "Transport Canada's January-March 2026 MVSA consultation explicitly raised whether references to foreign standards should be 'ambulatory' (automatically tracking changes when a cited standard or agency updates) rather than fixed to specific versions. CMVSS 1106 (noise standards) was used as a test case. Making MVSA references ambulatory would structurally prevent future certification gaps.",
            "months_warning_before_deadline": 14,
        },

        # ── Recommendations ──────────────────────────────────────────────────
        "recommendations": [
            {
                "num": 1,
                "title": "Amend the Motor Vehicle Safety Act regulations",
                "body": "Transport Canada should amend the regulations to recognize NHTSA certifications as equivalent to EPA certifications for heavy-duty truck imports. The technical standards are already aligned — this is an administrative citation update, not a policy debate.",
                "precedent": "UK SI 2019/648 (2019) — when the UK's departure from the EU left vehicle type approval regulations citing an authority that no longer had jurisdiction, targeted statutory instruments updated the certifying body references. Same mechanism available under Canada's MVSA.",
                "precedent_source": "https://www.legislation.gov.uk/uksi/2019/648/contents",
                "who_implements": "Transport Canada via amendment to Motor Vehicle Safety Regulations under the Motor Vehicle Safety Act",
                "measurable_target": "Amendment in force before August 2026 ordering window",
                "feasibility": "High",
                "impact": "Direct",
            },
            {
                "num": 2,
                "title": "Deliver a formal amendment before August 2026",
                "body": "Fleet renewal ordering decisions happen in August. A ministerial interim order may be the fastest first step, but it expires in 12 months and is not a durable fix. A full regulatory amendment with a public completion date is the correct outcome.",
                "precedent": "Canada's own trailer GHG precedent: seven consecutive ministerial interim orders (2019-present) instead of a formal amendment — the pattern to avoid repeating.",
                "who_implements": "Transport Canada (amendment) / Minister of Environment (interim order under CEPA s.163(3))",
                "measurable_target": "Formal amendment published in Canada Gazette Part I by June 2026; in force by August 2026",
                "feasibility": "Medium",
                "impact": "Critical",
            },
            {
                "num": 3,
                "title": "Adopt ambulatory references in MVSA regulations",
                "body": "Transport Canada's own January-March 2026 MVSA consultation explicitly debated making foreign standard references 'ambulatory' — automatically tracking changes when a cited agency updates — rather than fixed to specific versions. The current gap is a direct consequence of a fixed EPA citation. Ambulatory references would prevent the next one.",
                "precedent": "Transport Canada MVSA 2026 consultation (January-March 2026) — TC itself raised ambulatory vs. fixed reference design using CMVSS 1106 as a test case. Mexico's NOM-044 uses a dual-pathway design (EPA or Euro standards) that provides structural resilience when either certifying body changes.",
                "precedent_source": "https://tc.canada.ca/en/corporate-services/consultations/various-changes-regulations-under-motor-vehicle-safety-act-mvsa-2026",
                "who_implements": "Transport Canada via MVSA regulatory drafting process",
                "measurable_target": "All MVSA references to foreign certifying bodies converted to ambulatory form in next scheduled omnibus amendment",
                "feasibility": "Medium",
                "impact": "Preventive",
            },
        ],
    }

    out = os.path.join(DATA_DIR, "trucking.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {out}")

    # Verification
    print(f"\n  timeline entries:   {len(result['timeline'])}")
    print(f"  sectors:            {len(result['sectors'])}")
    print(f"  recommendations:    {len(result['recommendations'])}")
    print(f"  direct impact (mid): ${result['financial_impact']['direct_purchase_mid_cad']:,.0f} CAD")
    print(f"  industry exposure:   ${result['financial_impact']['industry_annual_revenue_cad']:,.0f} CAD")


if __name__ == "__main__":
    main()
