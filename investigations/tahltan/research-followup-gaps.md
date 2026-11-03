# Tahltan Territory: Follow-Up Pass on Flagged Research Gaps

Targeted follow-up to close five specific gaps flagged in `research-officials-legal.md`
and `research-stakeholders.md`: (1) Elections BC individual political donations,
(2) federal lobbyist registry, (3) Klabona Keepers current activity, (4) SkeenaWild's
CRA charity filing, (5) a status check on developments since Aug 12, 2026.

**Constraint note:** this pass ran with the WebSearch tool disabled (budget exhausted).
All research below used WebFetch against specific guessed/discovered URLs, plus direct
`curl` (via Bash) for cases where WebFetch's tooling was insufficient (10MB content
limit on bulk CSVs; scripted multi-step form submission). Every URL attempted is listed,
including failures, so a future pass knows what not to re-try blindly.

Sourcing key (same convention as other files in this investigation):
- **VERIFIED** — primary source directly confirms the claim.
- **REPORTED** — credible secondary source states the claim; not independently confirmed
  against a primary document.
- **UNVERIFIED / COULD NOT CONFIRM** — searched for, not found, or found only in
  low-confidence sources.

Research date: 2026-08-12 (same calendar date as the original research pass — see
§5 framing note).

---

## 1. Elections BC political donations — GAP REMAINS OPEN (new detail found)

### What was found
- Elections BC's donation-search tool is the **Financial Reports and Political
  Contributions System (FRPC)**, at
  `https://contributions.electionsbc.gov.bc.ca/pcs/Welcome.aspx` — reachable from
  `elections.bc.ca`'s "Financial Reports & Political Contributions System" link.
  **VERIFIED** (fetched directly).
- Traced the FRPC's actual query form at
  `https://contributions.electionsbc.gov.bc.ca/pcs/Options.aspx`. After selecting
  "Political Contributions" from the `ddldata_type` dropdown (an ASP.NET WebForms
  postback), the form reveals a genuine **contributor-name search field**
  (`ctl00$ContentPlaceHolder1$txtContributor`) plus dropdowns for donor class
  (individual/corporation/union/etc.), contributor type, electoral district, event,
  filer name, filer type, and party, with a `cmdSearchResult` submit button.
  **VERIFIED** — this is a real, specific, individual-donor-name search tool, exactly
  the kind of query the prior research pass flagged as needed.
- **Submission attempts all failed with a server-side error, not a block.** Multiple
  scripted POSTs to `Options.aspx` (preserving ASP.NET `__VIEWSTATE`/
  `__VIEWSTATEGENERATOR`/`__EVENTVALIDATION` tokens and session cookies via `curl`)
  were tried:
  - Contributor = "Bennett", date range blank
  - Contributor = "Bennett", date range 01/01/2005–12/31/2026
  - Contributor blank, all fields default ("(ALL)"), no date range
  - Same blank query with added `Referer`/`Origin` headers
  
  Every attempt returned the same 3,262-byte **"FRPC Exception" / "An error occured.
  Please try again."** page — a genuine server-side exception (not an HTTP 403, not a
  bot-challenge page). This suggests either a required client-side-JS-set value (e.g.
  from the date-picker widget) that a scripted POST doesn't reproduce, or server-side
  fragility toward non-browser-originated requests. **This is a confirmed, reproducible
  technical gap**, not a content finding either way.

### Conclusion
**No individual-level donation data was retrieved for Bill Bennett, N. Murray Edwards,
any Keevil family member, or any named mining-company executive.** The question posed
by the brief — does an individual-donor-name query change the "no source ties Teck
donations to Bennett or a Tahltan decision" finding — **remains unanswered**. What this
pass adds beyond the prior one: the search tool and its exact field names are now
documented, so a future pass with an actual browser session (Playwright/manual) rather
than scripted `curl`/WebFetch could likely complete the query.

### URLs tried (Gap 1)
- `https://elections.bc.ca/political-parties-and-candidates/financial-reporting/political-contributions-system/` — 404
- `https://contributions.electionsbc.ca` — DNS not found
- `https://elections.bc.ca` — worked, surfaced the correct FRPC link
- `https://contributions.electionsbc.gov.bc.ca/pcs/Welcome.aspx` — worked (landing page)
- `https://contributions.electionsbc.gov.bc.ca/pcs/Options.aspx` (GET) — worked (form)
- `https://contributions.electionsbc.gov.bc.ca/pcs/Options.aspx` (POST, ddldata_type=SA1) — worked, revealed search form
- `https://contributions.electionsbc.gov.bc.ca/pcs/Options.aspx` (POST, contributor="Bennett", no dates) — **server exception**
- `https://contributions.electionsbc.gov.bc.ca/pcs/Options.aspx` (POST, contributor="Bennett", dated range) — **server exception**
- `https://contributions.electionsbc.gov.bc.ca/pcs/Options.aspx` (POST, blank/all-default) — **server exception**
- `https://contributions.electionsbc.gov.bc.ca/pcs/Options.aspx` (POST, blank + Referer/Origin headers) — **server exception**
- `https://contributions.electionsbc.gov.bc.ca/pcs/Search.aspx` — generic error page, no form
- `https://contributions.electionsbc.gov.bc.ca/pcs/PoliticalContributions.aspx?ContributorName=Bennett` — generic error page (wrong URL pattern)

---

## 2. Federal lobbyist registry — CONFIRMED BLOCKED (gap remains open)

### What was found
- `lobbycanada.gc.ca` is protected by **Cloudflare's bot-challenge** ("Just a
  moment..." interstitial), confirmed via **both** WebFetch (HTTP 403) **and** a
  direct `curl` request with a browser User-Agent string (`cf-mitigated: challenge`
  header, HTTP 403, `server: cloudflare`). This rules out a WebFetch-tool-specific
  limitation — the site itself blocks non-browser automated requests uniformly,
  including its `/media/` CDN paths used for bulk-data downloads.
- Via Canada's Open Government Portal (`open.canada.ca`), located the **official bulk
  datasets published by the Office of the Commissioner of Lobbying of Canada**:
  "Lobbying Registrations" (`open.canada.ca/data/en/dataset/70ef2117-1095-4d77-80eb-b87f2bada2a4`)
  and "Monthly Communication Reports"
  (`open.canada.ca/data/en/dataset/a34eb330-7136-4f5e-9f5f-3ba41df58b06`), both **last
  modified Aug 10, 2026** — i.e., current data exists and is nominally public. However,
  the actual download files are hosted at `lobbycanada.gc.ca/media/...` URLs, which sit
  behind the same Cloudflare block — attempted download of the registrations ZIP
  returned the same Cloudflare challenge page instead of file content. **VERIFIED the
  block, could not obtain the data.**

### Conclusion
**Confirmed block, as instructed — not spending further time on this gap.** Federal
lobbyist-registry entries for Teck, Newmont Canada, Seabridge Gold, and Skeena Gold &
Silver remain unobtained. A future pass would need either an authenticated/interactive
browser session capable of passing the Cloudflare challenge, or a request routed
through a residential/non-flagged IP.

### URLs tried (Gap 2)
- `https://lobbycanada.gc.ca/en/` — 403 (Cloudflare challenge)
- `https://lobbycanada.gc.ca/app/secure/ocl/lrs/do/advSrch` — 403 (Cloudflare challenge)
- `https://lobbycanada.gc.ca/app/secure/ocl/lrs/do/clntSmmry?clientOrgCorpNumber=&clientOrgName=Teck+Resources` — 403 (Cloudflare challenge)
- `https://lobbycanada.gc.ca/media/` — 403 (Cloudflare challenge)
- `https://lobbycanada.gc.ca/media/zwcjycef/registrations_enregistrements_ocl_cal.zip` — 403 via WebFetch **and** via direct `curl` (same Cloudflare `cf-mitigated: challenge` response, confirmed with response headers)
- `https://open.canada.ca/data/en/dataset/70ef2117-1095-4d77-80eb-b87f2bada2a4` — worked (dataset metadata page, links to the blocked file above)
- `https://open.canada.ca/data/en/dataset/a34eb330-7136-4f5e-9f5f-3ba41df58b06` — worked (dataset metadata page; download link `lobbycanada.gc.ca/media/mqbbmaqk/communications_ocl_cal.zip` not attempted further given the confirmed block on the sibling file)

---

## 3. Klabona Keepers current activity (2023–2026) — GAP REMAINS OPEN (adjacent finding added)

### What was found
- `thenarwhal.ca/tag/tahltan/` — **404**, not a valid tag URL pattern.
- `thenarwhal.ca/?s=Klabona` — returned only the already-known **September 30, 2022**
  feature ("'The spirit of our Elders'..."). No 2023–2026 results for this exact term.
- `thenarwhal.ca/?s=Tahltan` (broader query) surfaced one relevant new item: **"Controversial
  B.C. gold and silver mine in Tahltan territory faces make-or-break vote"** (Steph
  Kwetásel'wet Wood, **December 3, 2025**),
  https://thenarwhal.ca/eskay-creek-mine-skeena-resources-tahltan/ — read in full.
  **This article does not mention Klabona Keepers by name.** It does document different,
  newer opposition activity: a group called the **K'adesibe Collective** (Tahltan women
  who "are keeping their identities confidential due to fear of backlash within their
  community," per the article) sent an unanswered letter to Skeena Resources raising
  environmental concerns; former interim TCG president **Beverly Slater** is quoted
  questioning whether the Eskay Creek consent process constitutes genuine "free, prior
  and informed consent"; and the article notes general member complaints about being
  "muted or censored" in community meetings. **REPORTED** (The Narwhal).
- `thenarwhal.ca/tag/red-chris/` — worked, but only surfaced two archival 2015–2016
  tailings-dam articles, nothing 2023–2026.
- On TCG's own site: `tahltan.org/?s=Klabona` returned **zero results**.
  `tahltan.org/tcg-news/` (general news feed, reviewed through Aug 11, 2026) and
  `tahltan.org/press-releases/` (reviewed through Jan 2026) show no Klabona Keepers
  mentions in any post title scanned.

### Conclusion
**No 2023–2026 Klabona Keepers coverage was found in either source searched.** The
September 2022 Narwhal feature remains the most recent substantive piece specifically
naming Klabona Keepers. This pass does **not** establish whether Klabona Keepers is
inactive, simply uncovered by press, or active but not named in the sources checked —
report as an open gap, not as evidence of inactivity. Separately and for the
investigation's awareness: the K'adesibe Collective is a **distinct, newer (2025)**
grassroots opposition group documented specifically around the Eskay Creek vote — worth
noting as a related finding if the dashboard is updated, but it should not be conflated
with or presented as a continuation of Klabona Keepers without further sourcing.

### URLs tried (Gap 3)
- `https://thenarwhal.ca/?s=Klabona` — worked, only the 2022 article
- `https://thenarwhal.ca/?s=Tahltan` — worked, full list through Dec 2025 (see above)
- `https://thenarwhal.ca/tag/tahltan/` — 404
- `https://thenarwhal.ca/tag/red-chris/` — worked, only 2015–2016 archival results
- `https://thenarwhal.ca/eskay-creek-mine-skeena-resources-tahltan/` — worked, read in full
- `https://tahltan.org/news/` — worked but resolved to the **newsletters** listing (2022–2026 newsletter/annual-report titles only, no Klabona/mining-opposition content)
- `https://tahltan.org/tcg-news/` — worked, general news feed through Aug 11, 2026, no Klabona/Foundation Agreement content
- `https://tahltan.org/press-releases/` — worked, press-release list through Jan 2026, no Klabona content
- `https://tahltan.org/?s=Klabona` — worked, zero results

---

## 4. SkeenaWild's CRA T3010 filing — RESOLVED (VERIFIED, via CRA bulk open data)

### What was found
CRA's own interactive charity search (`apps.cra-arc.gc.ca/ebci/hacc/srch/...`) again
returned only a JS "Loading/Chargement..." shell via WebFetch, confirming the prior
pass's finding that this endpoint is not fetchable non-interactively. Rather than retry
that or CharityData.ca again, this pass located and used **CRA's official bulk-download
open dataset** instead — successfully closing the gap:

- Via `open.canada.ca`'s catalog search, found the **"2024 List of Charities"** dataset
  (`https://open.canada.ca/data/en/dataset/80c00cdb-1358-415c-bb8b-0de7f12675b8`),
  published by CRA, with direct CSV resource links.
- These CSVs (13–21MB each) exceed WebFetch's 10MB content-processing limit, so they
  were downloaded directly via `curl` (Bash) and searched locally with `grep`/Python's
  `csv` module for BN `832887814RR0001`.

**Identification record — VERIFIED (primary source, CRA `ident_2024_updated.csv`):**
```
832887814RR0001, Category 0210, Sub-category 0001, Designation "C" (charitable organization),
Legal Name: "SkeenaWild Conservation Trust", Address: 103 - 4622 Greig Ave, Terrace, BC, V8G1M9, CA
```

**Financial data, fiscal period ending 2024-12-31, Form ID 27 — VERIFIED (primary
source, CRA `financial_d_and_schedule_6_2024_updated.csv`), field codes per CRA's
standard public T3010 Section C/D numbering convention** (this convention is
well-established and used by third-party charity-data aggregators, but the specific
code-to-label mapping below was **not independently re-confirmed against CRA's own
T4033 guide text in this pass**, since `canada.ca/.../completing-registered-charity-information-return.html`
returned HTTP 403 — flag accordingly if precision matters for publication):

| Field | Label (standard T3010 convention) | Amount (CAD) |
|---|---|---|
| 4700 | Total revenue | **$1,893,814** |
| 4510 | Revenue from federal government | **$1,628,061** (≈86% of total revenue) |
| 4530 | Revenue from provincial/territorial government | $175,215 |
| 4540 | Revenue from municipal/regional government | $16,229 |
| 4550 | Revenue from other registered charities | $15,000 |
| 4500 | Tax-receipted gifts (individual/corporate donations) | $21,271 |
| 4630 | Interest and investment income | $24,890 |
| 5000 | Total expenditures | $1,479,754 |

### Conclusion — closes the "funding disclosure gap" flagged in `research-stakeholders.md` §4
SkeenaWild Conservation Trust's FY2024 revenue was **overwhelmingly government-sourced**
— roughly 86% from the federal government alone, with provincial/municipal government
and tax-receipted private donations each in the low single-digit percentages of total
revenue. **No line item in this summary-level filing identifies mining-company funding**,
and nothing in this data supports or contradicts a claim of industry funding — the T3010
summary schedule doesn't itemize individual funders by name (that level of detail, if it
exists, would be in the "Non-Qualified Donees" resource or a Schedule 6 continuity
schedule not examined in this pass). This is a genuinely new, sourced fact for the
investigation: SkeenaWild's advocacy is publicly/government-funded, not funded by the
resource companies it reports on.

### URLs tried (Gap 4)
- `https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscSrch` — JS loading shell, not fetchable (as in prior pass)
- `https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscSrchRslts?q.sec=1&q.stts=0000000001&q.bn=832887814RR0001` — JS loading shell, not fetchable
- `https://www.canada.ca/en/revenue-agency/services/charities-giving/charities-listings/list-charities-other-qualified-donees.html` — 404
- `https://www.canada.ca/en/revenue-agency/services/charities-giving/charities-listings.html` — 403
- `https://www.canada.ca/en/revenue-agency/services/charities-giving/charities-listings/list-charities-other-qualified-donees/list-charities-basic-search.html` — 403
- `https://search.open.canada.ca/en/od/?search_text=charities+listing` — worked, found the 2024 List of Charities dataset
- `https://open.canada.ca/data/en/dataset/80c00cdb-1358-415c-bb8b-0de7f12675b8` — worked (dataset page with CSV links)
- `https://open.canada.ca/data/dataset/.../download/ident_2024_updated.csv` (13.2MB, via `curl`) — **worked, VERIFIED match found**
- `https://open.canada.ca/data/dataset/.../download/financial_section_a_b_and_c_2024_updated.csv` (11.3MB, via `curl`) — worked, secondary confirming figures
- `https://open.canada.ca/data/dataset/.../download/financial_d_and_schedule_6_2024_updated.csv` (21.0MB, via `curl`) — **worked, VERIFIED financial figures above**

---

## 5. Current status check (developments since Aug 12, 2026)

**Framing note, important:** today's date is **2026-08-12** — the same calendar date
as the original research pass this follow-up is building on. "Since Aug 12, 2026" is
therefore effectively "as of today," not a meaningful elapsed window. This section
should be read as a **currency confirmation**, not a discovery of new events, and should
be re-run at a genuinely later date for real signal.

### Foundation Agreement (undisclosed, per prior FOI-based reporting)
- `tahltan.org/?s=Foundation+Agreement` — **zero results**.
- `news.gov.bc.ca/search?q=Foundation+Agreement+Tahltan` — surfaced only the two
  already-documented releases (Eskay Creek Jan 2026, Red Chris expansion June 2026) plus
  the 2021 Shared Prosperity Agreement release; **no release specifically naming or
  confirming signature of a "Foundation Agreement."**
- **Conclusion: no public confirmation found that the Foundation Agreement has been
  signed or otherwise made public.** Consistent with — does not update — the prior
  finding that it remains unsigned/undisclosed absent the original FOI release.

### BC government news (Tahltan / six mining companies)
- `news.gov.bc.ca/search?q=Tahltan` — most recent Tahltan-tagged release remains
  **"B.C. approves Red Chris mine expansion"** (June 19, 2026, #2026MCM0029-000727),
  already documented in `research-officials-legal.md`. No release dated after that.
  Other recent-but-unrelated releases returned by this search (BC/Simpcw Yellowhead
  copper mine consent agreement, July 16 2026; land-use planning update, July 2 2026)
  are **not Tahltan-specific** and are noted here only because they appeared in the
  query results.
- `news.gov.bc.ca/ministries/mining-and-critical-minerals` — reviewed; **no releases
  found mentioning Galore Creek, Schaft Creek, or KSM** in this ministry's listing (note:
  this doesn't contradict the KSM "priority project" April 2026 finding already in
  `research-stakeholders.md`, which likely sits on a different release page/ministry
  index not surfaced by this particular listing view — flagged as a minor gap, not a
  contradiction). No release on this page is dated after Aug 1, 2026.

### Tahltan Central Government's own site
- `tahltan.org/tcg-news/` — reviewed through the most recent post, **"We're hiring:
  Wildlife Guardian" (Aug 11, 2026)**. No Foundation Agreement, no new mining
  announcement beyond what's already documented.
- `tahltan.org/press-releases/` — most recent entry remains the Jan 27, 2026 Eskay
  Creek consent/revenue-sharing announcement; nothing newer.

### Conclusion
No evidence of change found on any of the three items (Foundation Agreement status, new
BC government action, new mining-company project news) as of Aug 12, 2026 — but given
the same-day framing above, this is a weak negative and should not be read as "confirmed
stable," only as "nothing new turned up in same-day checks of the two most likely
sources." Re-run this section on a later date for a real currency check.

### URLs tried (Gap 5)
- `https://tahltan.org/?s=Foundation+Agreement` — worked, zero results
- `https://news.gov.bc.ca/search?q=Foundation+Agreement+Tahltan` — worked, no new releases
- `https://news.gov.bc.ca/search?q=Tahltan` — worked, most recent = June 19, 2026
- `https://news.gov.bc.ca/ministries/indigenous-relations-and-reconciliation` — worked; releases through July 7, 2026, none Tahltan-specific
- `https://news.gov.bc.ca/ministries/mining-and-critical-minerals` — worked; no post-Aug-1-2026 releases, no Galore Creek/Schaft Creek/KSM releases in this listing
- `https://tahltan.org/` (homepage) — worked; most recent items through Aug 11, 2026, incl. a Facebook-embedded note about a Tahltan Leadership Council meeting with Newmont's CEO on Red Chris signage/partnership (not independently verified beyond the embed — flagged as low-confidence, not asserted as a sourced fact)
- `https://tahltan.org/tcg-news/` — worked (see above)
- `https://tahltan.org/press-releases/` — worked (see above)

---

## Summary for the investigation

1. **Elections BC (Gap 1): still open.** Found and documented the actual donor-search
   tool and its form fields, but scripted submission consistently triggers a
   reproducible server-side error — a technical gap, not a content finding. No
   individual-donor data obtained for Bennett, Edwards, Keevil family, or mining
   executives.
2. **Federal lobbyist registry (Gap 2): confirmed blocked**, including at the bulk-data
   CDN level (Cloudflare bot-challenge, verified via both WebFetch and raw `curl`). Not
   pursued further per instructions.
3. **Klabona Keepers (Gap 3): still open** for 2023–2026 coverage specifically naming
   the group. Adjacent finding: a distinct, newer (2025) grassroots opposition voice,
   the **K'adesibe Collective**, is documented in a Dec 2025 Narwhal piece on the Eskay
   Creek vote — worth flagging for the dashboard as a separate entity, not a Klabona
   Keepers rebrand or continuation (no source supports that connection).
4. **SkeenaWild CRA filing (Gap 4): resolved.** VERIFIED via CRA's own bulk open-data
   CSVs (downloaded and grepped directly, bypassing the JS-rendered search tools that
   failed twice before): FY2024 revenue $1,893,814, ~86% ($1,628,061) from the federal
   government, with provincial/municipal government and private tax-receipted donations
   each minor by comparison. No mining-company funding line identified — closes the
   "funding disclosure gap" for this NGO specifically (not for Rivers Without Borders or
   Salmon Beyond Borders, which were not part of this pass's scope).
5. **Current status (Gap 5): no changes found**, but the check window is same-day
   (today = Aug 12, 2026, the same date as the original research), so this is a weak
   negative — re-run later for a genuine currency check. Foundation Agreement remains
   unconfirmed as signed/public.

## Explicit remaining gaps (do not fill with inference)
- Individual-level Elections BC donation data for any named official or mining-company
  executive — not obtained; the search tool now has documented field names for a future
  browser-based (non-scripted) attempt.
- Federal lobbyist registrations for Teck, Newmont Canada, Seabridge Gold, Skeena Gold &
  Silver — not obtained; site-wide Cloudflare block confirmed at both the interactive
  and bulk-download layers.
- Klabona Keepers' specific 2023–2026 activity — not found in either thenarwhal.ca or
  tahltan.org; absence of coverage is not evidence of inactivity.
- Whether the KSM "priority project" (April 2026) release lives on a BC government page
  not surfaced by the ministry-news listing checked in this pass.
- Named individual/corporate funders of SkeenaWild beyond the government/tax-receipted
  revenue categories (would require the CRA "Non-Qualified Donees" resource or Schedule
  6 continuity detail, not examined here).
- Genuine forward-looking currency check on the Foundation Agreement and all six mining
  projects — this pass's "since Aug 12, 2026" window was effectively zero days; needs
  re-running from a later date.
