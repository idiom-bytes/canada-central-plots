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
