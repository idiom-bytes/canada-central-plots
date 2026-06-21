# Session Summary — 2026-06-21

This window accidentally spanned **two unrelated workstreams**. This doc separates them so the
immigration work is recorded and the **hoc_db deployment work can be resumed cleanly**.

---

## ✅ Workstream 1 — Immigration Intelligence (canada-central-plots) — COMPLETE

**Repo:** `~/workspace/canada/canada-central-plots`
**Branch:** `feature/immigration-asylum-narrative` (working tree clean; **not pushed**)

### What it is
An objective, sourced intelligence suite auditing **Canada's stated immigration narrative vs.
measured reality** — and the system that legislative/policy/ministerial decisions built, plus the
emerging risks. Strategy lives in `STRATEGY-immigration-intelligence.md`; detailed work log in
`CHECKPOINT-asylum-policy-chain.md`.

### Pages built / changed
| Page | What it does |
|---|---|
| `overview.html` | **Capstone story spine** — 4 chapters (Volume → Policy → Consequences → What's Broken) + risk grid + objectivity standards. The connective navigation. |
| `immigration-volumes.html` | Added "Net change in temporary residents by type" flow chart (reconciles exactly to net_npr; 2023/24 = +781k). |
| `asylum-channel.html` | Added inland-shift docs (31%→71%→78%), "USA vs Canada enforcement" note; relocated the policy chain to its own view. |
| `policy-timeline.html` | "How the Channel Was Built" — 11 decisions, overview + detail, 8/11 executive (no vote); Bill C-12 verified; "what the brakes didn't fix" nav. |
| `hate-crime.html` | Narrative vs. reality: antisemitism. Jewish 70% of religious hate crime; 21–25× rate gap (both denominators shown). |
| `asylum-cost.html` | The real cost. IFHP $896M→>$1.5B; IHAP ~$1.1B; $16,500/claimant; "$5B" corrected; federal-only undercount flagged. |
| `enforcement.html` | "Running to stand still" — record removals (23,160 in 2025) still outpaced by intake; backlogs 23k→165k, 70k→270k. |
| `index.html` | "Start Here" banner card → overview. |

### Commit chain (newest first)
`c57a21f` enforcement view · `3dcf6ff` real-cost view · `0fd1253` hate-crime view ·
`8e095b5` capstone overview · `37a5dd2` strategy charter · `65aa0bc` policy-timeline C-12 + nav ·
`97bbaa9` policy-timeline view · `34385ee` asylum policy-chain section · `2d31f94` plots snapshot.

### Objectivity calls (how we stayed credible)
- Corrected the viral "$5B" cost myth with itemized PBO figures; flagged federal-only undercount.
- Hate-crime chart: confirmed counts, exposed the inflated Muslim denominator — showed both (21× vs 25×).
- Enforcement: corrected our own earlier "removal is rare" line — removals are at record highs but outpaced.
- Contested attributions (Century Initiative) flagged, not asserted.

### Related (separate repo — NOT done here)
GitHub issues opened on `idiom-bytes/house_of_commons`: **#146** (scrape Canada Gazette /
regulatory layer) and **#147** (scrape the Senate). These are backlog for that repo.

### Outstanding (optional)
- `git push -u origin feature/immigration-asylum-narrative`
- Propagate Overview/Hate Crime/Cost/Enforcement nav links to the remaining plot pages
  (exploitation, justice-backlog, origin-data-gap, lobbying, immigration-volumes).

---

## ⏸️ Workstream 2 — hoc_db deploy (hoc_db-main) — RESUME HERE

**Repo:** `~/workspace/canada/hoc_db-main` · **Branch:** `main` (25 ahead of origin/main)
**Goal:** deploy the **data-api** service to Railway + get **hoc_db main** deployed.

### State on disk (UNCOMMITTED — safe, but not yet committed)
Build fixes that make `pnpm build` pass (were failing on lint/types/prerender):
- `app-next/components/support/DonationConfirmation.tsx`, `.../civic-vote/VerifyCanadianModal.tsx` — escaped apostrophes
- `app-next/lib/support/stripe.ts`, `.../civic-vote/stripe.ts` — Stripe `apiVersion` → `2026-04-22.dahlia`
- `app-next/app/civic-vote/{queue,bundles/[slug],bills/[session]/[billId]}/page.tsx` — Suspense + `force-dynamic`
- `data-api/.dockerignore` (NEW) — stops the node_modules symlink clobbering the image
- (`data-api/node_modules` = dev symlink, `exports/` = artifacts — leave untracked)

### Verified earlier this session
- `pnpm build` **passes** (exit 0) with the fixes above.
- data-api deploy scaffolding already exists: `data-api/Dockerfile`, `railway-data-api.toml`,
  `yarn deploy:data-api`. Health `/health`, reads `PORT`, auth fails-closed in prod, `PARQUET_DIR` first.

### Resume checklist
1. Decide: commit the build fixes (branch off main first per repo rules) — then push.
2. `railway login` (CLI showed `invalid_grant` — must re-auth).
3. Create the data-api Railway service from `railway-data-api.toml`; attach the shared Volume at `/data`.
4. Set env: `PARQUET_DIR=/data/parquets`, `DATA_API_KEY`, `DATA_API_ADMIN_KEY`, `TURSO_*`, `NODE_ENV=production`.
5. Point web service at `DATA_API_URL=http://<data-api>.railway.internal:3001` (+ same `DATA_API_KEY`).
6. Seed parquets on the Volume (cron `export-to-app`) before data-api is useful.
7. `yarn deploy:data-api` then `yarn deploy:web` (each prompts; never `railway up` directly).

Full detail: `canada-central-plots/CHECKPOINT-asylum-policy-chain.md` → "Workstream A" section.
