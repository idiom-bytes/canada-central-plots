# Checkpoint — Immigration / Asylum Accountability Narrative

**Last updated:** 2026-06-21
**Purpose:** Resumable state for the immigration-volumes + asylum-channel plot work and the
"how the channel was built" policy-chain research. If a session hits a limit, start here.

---

## Workstream B — Immigration plots (canada-central-plots) — ACTIVE

### DONE (committed? NO — working tree only, not yet committed/pushed)

1. **`immigration-volumes.html`** — added a new full-width stacked-bar chart
   **"Net change in temporary residents, by type"** between the annual-flow chart and the
   stock chart.
   - Derived AT RUNTIME from `DB.npr.series` as fiscal-year (Jul→Jul) deltas. No data file change.
   - VERIFIED: per-type deltas sum EXACTLY to `annual[].net_npr` for every year:
     2021/22 +224,715 · 2022/23 +671,525 · **2023/24 +781,075** · 2024/25 −14,954.
   - The "missing 781k jump" = stock total rising 2.26M (Jul-23) → 3.04M (Jul-24).
   - Coverage starts 2021/22 (by-type stock series begins Jul 2021).
   - Updated "Reading the data" prose to explain flow → flow-breakdown → stock.

2. **`asylum-channel.html`** — added **"Who is claiming: the inland shift"** prose section
   (after "What the data shows", before the `.chain`). Populated by JS from `DB.inflow_office`.
   - Inland share computed at runtime: 2022 31% → 2024 66% → 2025 71% → 2026(partial) 78%.
   - Border collapse after STCA Additional Protocol (Mar 2023): 46,315 (2022) → 20,935 (2025).
   - Elements: `#inlandLede`, `#inlandCallout`, `#inlandCaveat`, `#enforceNote`.
   - `#enforceNote` now lead-labelled **"USA vs. Canada enforcement."** (normal prose color,
     was faint tertiary gray — user couldn't find it).
   - Honest caveat documented: IRCC office-type data records WHERE a claim is filed, not the
     claimant's PRIOR status — so we CANNOT measure whether inland surge = former TFW/students
     converting vs. policy/behavioural shift. Both consistent with data; neither proven.
   - Office chart subtitle (`#officeSub`) now shows live inland %.

### TODO — "How the channel was built" section (RESEARCH PENDING)

User wants the CAUSE + ACCOUNTABILITY, not just the symptom: "how the gun was designed and
who shot it." Deliverable = a sourced `.chain`-style timeline section on `asylum-channel.html`
(lever → date → minister/dept → effect), with documented-fact visually distinct from
contested interpretation. Only include US figures with hard citations.

**Deep-research workflow was STOPPED** (too many agents: 5 search + 15 fetch + 3 verifiers/claim).
Resume with LEAN inline research instead: ~5 targeted WebSearches by the main agent, fetch only
primary sources, no sub-agent fan-out. Agent count target: 0.

#### Skeleton policy chain (MY PRIOR KNOWLEDGE — every line marked [VERIFY] before publishing)

Levers (the "design"):
- **Study-permit explosion** — uncapped Designated Learning Institutions; intake exploded
  2021–2023. **Jan 2024 study-permit cap** imposed by Min. **Marc Miller** (IRCC). [VERIFY dates/numbers]
- **TFWP / IMP expansion** — 2022 "Workforce Solutions Road Map" loosened LMIA caps
  (ESDC, Min. **Carla Qualtrough**); IMP (LMIA-exempt) grew fastest. [VERIFY]
- **Safe Third Country Agreement — Additional Protocol, 25 Mar 2023** — extended STCA to the
  ENTIRE land border, closed the Roxham Road loophole → pushed claims from border to INLAND/airport.
  [VERIFY effective date + mechanism]
- **Mexico visitor-visa lift, Dec 2016** (Min. **John McCallum**) → surge in Mexican claims;
  **partial re-imposition Feb 2024** (Min. Marc Miller). [VERIFY]
- **Immigration Levels Plan, Nov 2022** — 500,000/yr by 2025 target (Min. **Sean Fraser**);
  alleged **Century Initiative** (100M-by-2100) influence. [VERIFY influence claim — likely CONTESTED]
- **CBSA removals decline / enforcement gap** — **2020 Auditor General report**: CBSA could not
  locate a large share of people ordered removed. [VERIFY + find later data]
- **Asylum-claimant work permits + IFHP healthcare** eligibility — incentive/ability to remain
  inland during multi-year processing. [VERIFY any policy change vs. longstanding]

Actors (the "shooters") — IRCC ministers in sequence:
McCallum (2015–17) → Hussen (2017–19) → Mendicino (2019–21) → Fraser (2021–23) → Miller (2023–).
ESDC (TFWP): Qualtrough et al. External: employer associations, universities/colleges (demand
side — see `lobbying-influence.html`), Century Initiative. [VERIFY each attribution]

Costs / burden (to source):
- **PBO ~$5B** asylum processing/support estimate. [VERIFY exact figure + report date]
- **IRB backlog ~300,000** pending claims. [VERIFY current number]
- Federal–provincial cost disputes (housing, healthcare, IFHP). [VERIFY]

US contrast (only if hard-sourced): acceptance/grant rates, removal rates, backlog. [VERIFY — do NOT invent]

Key honesty constraint: the border paradox — inflow is NOT people forcing the world's most-defended
land border; it's policy-enabled intake. "Border crisis" → "policy choice." This is the thesis.

### VERIFIED FINDINGS — lean inline research, round 1 (2026-06-21) [CONFIRMED w/ sources]

1. **Study-permit cap** — CONFIRMED. Min. **Marc Miller** (IRCC) announced a 2-year national cap
   on **22 Jan 2024**: ~360,000 approved study permits for 2024, a **35% cut from 2023**; new
   provincial/territorial **attestation letter** required per application from that date. Implies
   intake was effectively uncapped before. Grad students later folded into cap in 2025.
   Sources: canada.ca (IRCC news, 22 Jan 2024) · cbc.ca/news/politics/miller-cap-international-students-1.7090779

2. **STCA Additional Protocol** — CONFIRMED. Announced **24 Mar 2023**, in force **12:01 EDT 25 Mar
   2023**; extended STCA to the ENTIRE land border (incl. between ports of entry). Claimants who cross
   irregularly and claim within **14 days** can be returned to the US. Roxham Road shut **25 Mar 2023**
   (~100,000 had crossed; ~81,148 irregular claims Jan2017–Dec2022, top source Haiti). Effect: pushed
   claims away from the border → inland/airport.
   Sources: loc.gov global-legal-monitor 2023-04-05 · migrationpolicy.org us-canada-safe-third-country-agreement · canada.ca STCA page

3. **TFWP Workforce Solutions Road Map** — CONFIRMED. ESDC Min. **Carla Qualtrough**, **4 Apr 2022**.
   LMIA validity 9→**18 months**; High-Wage/Global Talent employment duration to **3 years**; low-wage
   cap raised from **10%→20%** of workforce (30% for 7 sectors incl. Accommodation & Food Services);
   ended the auto-refusal of LMIAs in regions with ≥6% unemployment. (IMP, LMIA-exempt, grew fastest —
   [VERIFY IMP-specific numbers].)
   Source: canada.ca/en/employment-social-development/news/2022/04/ (backgrounder + announcement)

4. **Mexico visa** — CONFIRMED. Visitor-visa requirement **lifted 1 Dec 2016** (eTA only);
   **reimposed 29 Feb 2024** by Min. Miller. Mexican asylum claims rose **260 (2016) → 23,995 (2023)**;
   Mexico = **17% of all claims**. [VERIFY: McCallum was IRCC min. in Dec 2016 — not explicitly in source.]
   Sources: cbc.ca mexico-canada-visas-asylum-1.7128408 · canada.ca CIMM Nov 25 2024 Mexico note

5. **Costs / backlog** — CONFIRMED (and CORRECTS the "$5B" figure). PBO/IRB:
   - IFHP (asylum healthcare) **$722M in 2024-25**, could approach **$1B/yr by end of decade**.
   - PBO "Costing Asylum Claims from Visa-Exempt Countries": eTA-arrival inventory **$455M over 5yr**;
     clearing the recent backlog ~**half a billion**.
   - IRB backlog **~300,000 pending**; avg time-in-system **19 months** (2025).
   - CBSA removals inventory: **~74,000 failed claimants** (Dec 2025).
   - ⚠️ The viral "$5B" number is NOT a single documented PBO figure — real figures are smaller and
     itemized ($0.5–1B ranges). Use the specific PBO numbers, flag $5B as unverified/aggregate.
   Sources: pbo-dpb.ca RP-2425-007-S · globalnews.ca 10536523 · irb-cisr.gc.ca departmental plan 24-25

### VERIFIED FINDINGS — round 2 (2026-06-21) [CONFIRMED w/ sources]

6. **CBSA removals / enforcement gap** — CONFIRMED. Auditor General, Spring 2020, tabled **8 Jul 2020**:
   CBSA did not know the whereabouts of **~34,700** people under removal orders (two-thirds of cases
   sampled); ~50,000 enforceable cases in inventory; **failed asylum claimants = largest share** ordered
   to leave, most NOT removed within the 1-year target. (Pairs with ~74,000 failed claimants in removals
   inventory Dec 2025 from round 1.) Sources: oag-bvg.gc.ca mr_20200708 · cbc.ca 1.5641643 · theglobeandmail.com

7. **Immigration Levels Plan** — CONFIRMED. **1 Nov 2022**, Min. **Sean Fraser**: 465k (2023), 485k (2024),
   **500k (2025)** PRs. Century Initiative publicly applauded it; cofounder **Dominic Barton** chaired the
   2016 Advisory Council on Economic Growth (recommended 450k), consistent w/ 100M-by-2100. McKinsey/Barton
   influence = **CONTESTED** (Radio-Canada raised it; Fraser denied). NOTE: this is a PERMANENT-resident
   plan — backdrop/posture, not a direct asylum lever. Sources: canada.ca news 2022/11 · cicnews 1131587 ·
   theglobeandmail.com (McKinsey denial) · en.wikipedia Sean_Fraser

8. **US contrast** — CONFIRMED (indicative, different systems). US asylum grant rate fell **51%→19%**
   (Feb 2024–Aug 2025) as it tightened; US filed **905,632** asylum applications FY2024. Canada IRB
   inventory **70,223 (end 2022) → 272,440 (end 2024)**, waits up to **3.7 yrs**; claims 92k(2022) →
   144k(2023) → 173k(2024), down ~36% early 2025. Sources: cis.org · tracreports.org/766 · justice.gov EOIR ·
   canada.ca asylum stats · irb-cisr.gc.ca

STATUS: "How the channel was built — and who built it" section BUILT into asylum-channel.html
(static HTML: intro prose + 7-step .chain timeline + enforcement callout + who-built-it + cost/US note
+ sources line). Remaining optional: IMP-specific growth numbers; confirm McCallum as Dec-2016 minister
(public record says yes, IRCC min. Nov 2015–Jan 2017).

---

## Workstream A — main branch build + data-api deploy (../hoc_db-main) — PAUSED

### Build: PASSES (`pnpm build` exit 0). Fixes applied (working tree, NOT committed):
- Escaped apostrophes: `DonationConfirmation.tsx`, `VerifyCanadianModal.tsx` (`&apos;`)
- Stripe `apiVersion` → `2026-04-22.dahlia`: `lib/support/stripe.ts`, `lib/civic-vote/stripe.ts`
- `useSearchParams` Suspense + `force-dynamic`: civic-vote `queue`, `bundles/[slug]`,
  `bills/[session]/[billId]` pages (civic-vote disabled at runtime by middleware but still
  prerendered at build).
- Added `data-api/.dockerignore` (node_modules symlink would clobber image deps).

### data-api deploy structure: scaffolding already exists in repo
- `data-api/Dockerfile`, `railway-data-api.toml`, `yarn deploy:data-api` / `scripts/deploy.sh data-api`.
- Health `/health`, reads `PORT`, auth fails-closed in prod.
- REMAINING (manual Railway dashboard): create service from `railway-data-api.toml`; attach shared
  Volume at `/data`; set env (`PARQUET_DIR=/data/parquets`, `DATA_API_KEY`, `DATA_API_ADMIN_KEY`,
  `TURSO_*`, `NODE_ENV=production`); point web service at `DATA_API_URL=...railway.internal:3001`;
  seed parquets on Volume (cron `export-to-app`) before it's useful.
- BLOCKER: `railway login` (CLI shows invalid_grant). User must auth.

### main is 25 commits ahead of origin/main. "Merge to main" = push local main + deploy.

---

## Immediate next actions (pick up here)
1. Get user's choice on research depth (lean inline / defer / skeleton-now).
2. If lean: run ~5 WebSearches, fetch primary sources, fill skeleton above, build `.chain` section.
3. Commit plot changes to canada-central-plots (NOT yet done).
4. Separately: commit + push the main build fixes; do Railway data-api deploy after `railway login`.
