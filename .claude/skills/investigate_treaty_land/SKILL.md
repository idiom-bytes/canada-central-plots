---
name: investigate_treaty_land
description: Build a per-Nation/per-agreement relationship-graph investigation (dashboard + CONTEXT.md) mapping financial stakeholders, officials, and advocacy/NGO networks around a First Nations treaty or resource-land agreement. Adapted from the generic lobbying/procurement `investigate` skill for this specific subject matter, hardened by two full passes on the Tahltan investigation.
argument-hint: <Nation/agreement name> [source material: tweets, images, documents, URLs]
user-invocable: true
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Agent, WebSearch, WebFetch
---

# Treaty & Resource-Land Investigation

You are building a standalone investigative dossier — a relationship graph plus a fully
sourced research document — for a specific First Nations treaty or resource-land
agreement. This is **not** the same deliverable as a `report_architect` Story/Chapter
(a polished public accountability page); it's the underlying network-mapping dossier:
who's involved, who has money at stake, who facilitated it, who's advocating on which
side, and how those people/organizations connect to each other. The two are
complementary — a `report_architect` report can link out to one of these dossiers, or
vice versa.

One investigation per Nation/agreement, in its own directory:

```
investigations/{slug}/{slug}-dashboard.html   — interactive relationship graph
investigations/{slug}/{slug}-CONTEXT.md       — full sourced research document
investigations/{slug}/research-*.md           — working research files (keep — audit trail)
investigations/{slug}/MANUAL-STEPS.md         — required, see Phase 6
```

`investigations/README.md` is the index of completed investigations in this repo —
update it when you finish one, but this skill file is the canonical process reference,
not that file.

---

## Phase 0: Is this the right skill?

- Use this skill when the ask is about **who's involved, who benefits, who has a stake,
  who lobbied, or what the network looks like** around a treaty, land transfer, consent
  agreement, or resource-revenue deal involving a First Nation.
- Use the generic `investigate` skill instead for an ordinary government contract or
  lobbying relationship with no treaty/land dimension.
- Use `report_architect` instead (or in addition) when the deliverable is a polished,
  public-facing accountability page for the site rather than an internal/investigative
  relationship-mapping dossier.

## Phase 1: Anchor research — verify the claim before mapping anything

**Do this before any stakeholder research.** In the Tahltan investigation, the user's
starting claim ("$1.28T in minerals... the Tahltan land transfer") turned out to
conflate two entirely unrelated documents — a regional mineral-endowment estimate that
never mentioned the Nation, and a separate, unsigned, undisclosed agreement. If Phase 2
had started from the unexamined claim, the whole investigation would have been built on
a false premise.

Run one dedicated research pass whose only job is: **what specific document, agreement,
or number is actually being referenced, verified directly against a primary source** —
not a screenshot, not a news summary, not the user's framing of it. Identify the legal
mechanism precisely (is this a completed treaty, an unsigned framework, a project-level
consent agreement, a revenue-sharing deal?), the actual parties (get exact legal-entity
names — a Nation's elected government, its band councils, and any grassroots/community
groups are usually distinct entities, not interchangeable), and whether the Nation is
even part of the formal treaty-commission process at all (many are not, and pursue
negotiated agreements or litigation instead — check this explicitly, don't assume).

If the user's source material references an image/document you don't have, say so
plainly and proceed with what can be independently verified rather than blocking.

## Phase 2: Parallel stakeholder research — 3 thematic clusters

Split into three parallel agents, matching the node categories below:

- **Financial stakeholders**: who holds tenure/ownership/equity in the resources at
  stake — get exact ownership percentages and the ownership chain (acquisitions,
  joint ventures). Report foreign ownership as ordinary FDI, not "interference," unless
  a specific source uses that framing. Name individual investors at billionaire/
  controlling-family scale where documented.
- **Government officials**: who facilitated the agreement in an official capacity —
  ministers, MLAs/MPs, negotiators. Run an explicit **revolving-door / prior-employment
  check on every single named official**, in both directions (government → company,
  company → government). Report "none found" as a real, valid, reportable finding — do
  not treat a clean record as not worth stating. Only escalate to "documented conflict"
  with a specific basis: a financial stake, a prior employer/client relationship, a
  donation, a family connection. **Normal exercise of a government role — a minister
  signing an agreement, an MLA representing the riding — is not itself a finding.**
- **NGO / advocacy landscape**: map both industry associations and environmental/
  Indigenous-rights groups with equal rigor — this is not a one-sided check. Industry
  association boards being staffed by the mapped companies' own executives is *normal
  trade-association structure*, not a conflict — say so explicitly to avoid implying
  otherwise.

Each cluster researcher writes its own `research-*.md` file, labeling every claim
**VERIFIED** (primary source), **REPORTED** (credible secondary source), or
**UNVERIFIED / COULD NOT CONFIRM** (searched, not found). Never let a later phase
upgrade a REPORTED or UNVERIFIED claim to a stated fact.

## Phase 3: Build the dashboard + CONTEXT.md

**Design** (self-contained, no CDN/external JS — hand-roll the force-directed graph in
vanilla JS, since D3 or similar would violate "no external dependencies"):

- Dark theme: `#0d1117` background, `#161b22` surfaces, `#30363d` borders.
- Node categories: Government/Crown (orange), First Nation entity (teal), Resource
  company (blue), NGO/advocacy (purple), Individual (green). Add a Foreign entity
  (pink) category only if a specific, sourced foreign-government-interference finding
  exists — otherwise fold foreign ownership facts into Resource company node detail
  text instead of inventing a category with nothing verified to put in it.
- Edge types: Agreement/consent (orange dashed), Ownership/tenure (blue solid),
  Funding/donation (red solid), Advisory/legal (gray dotted — also use this for
  fiscal-sponsorship/administrative relationships, e.g. a campaign hosted by a larger
  foundation), Revolving door (red solid + warning icon), Litigation/opposition (purple
  dashed — reuse this style for direct-action/protest events too, but state clearly in
  the tooltip when something is a blockade or letter, not a court case), Lobbying
  contact (cyan dashed).
- Risk categories: (1) Documented conflicts of interest — specific basis required;
  (2) Financial interest concentration — who actually holds the value at stake;
  (3) Advocacy influence — sourced to registry filings, statements, or reporting, not
  assumed from an org's existence; (4) Foreign involvement — FDI vs. interference,
  explicitly distinguished; (5) Process/oversight — litigation, audits, disclosure gaps.
- Interactions: hover tooltips, click-for-detail panel, drag-to-reposition, edge-type
  filter toggles. Nodes with a documented conflict get a red-dashed border + warning icon.

**Validate independently after every build or update pass — do not trust an agent's
self-reported validation.** Re-run these yourself:
1. Extract the inline `<script>` block, run `node --check` on it.
2. Run a Python `html.parser`-based tag-balance check on the full HTML file.
3. Regex-extract every edge's `s`/`t` node-ID references and confirm each resolves to
   an actual node ID in the NODES array — no dangling references, no duplicate IDs.

This caught a real bug once already in this repo's treaty-land work (an inconsistent
"effective treaty" count propagated from one research file to downstream pages) — don't
skip cross-checking research files against each other, either.

## Phase 4 (when asked to go deeper): NGO/network cross-connection pass

When asked specifically to dig into the advocacy/NGO side — founding, funding, boards,
overlaps — split research by natural clusters (e.g. a conservation/watershed cluster, an
Indigenous-led-plus-national cluster, an industry/transparency cluster), not by
individual org, so cross-cluster overlaps get checked rather than each org researched
in isolation. Task each cluster explicitly with:

- Founding history and legal/fiscal structure. Many small advocacy campaigns are **not
  independently incorporated** — they're fiscally sponsored projects of a larger
  umbrella (Tides, MakeWay, New Venture Fund and similar). This matters: it means there
  is no standalone tax filing to look up, so don't waste time hunting for one.
- Funding sources. For Canadian registered charities, **do not rely on the CRA's
  interactive charity search or third-party summary sites — they are JavaScript-
  rendered and will not return real content to a non-browser fetch.** Instead, go
  straight to CRA's bulk **"List of Charities" open-data CSVs** on open.canada.ca and
  grep by Business Number. This is slower to set up but far more reliable, and gives
  primary-source, itemized T3010 figures rather than a scraped summary.
- Board of directors / leadership, cross-checked by name against every company,
  individual, and official already mapped in Phase 2's research files.
- The overlap check is the actual point of this phase — spend real effort on it. Report
  genuine negative findings ("no overlap found between X and Y") as plainly and fully as
  positive ones; a clean network is a real, useful finding.
- Handle any vulnerable or anonymous sources (e.g. community members withholding their
  identities out of stated fear of backlash) with explicit care: report factually, cite
  precisely, never speculate about who they are, and never let their concerns read as
  this investigation's own allegation. Two things can be true at once — an agreement
  passed through its official process, and people affected by it raised concerns about
  that process — present both, adjudicate neither.

## Phase 5 (when asked to close remaining gaps): follow-up pass

By this point in a session the shared WebSearch budget is often exhausted (it's a
session-wide cap, not per-agent). Default to **WebFetch against specific, predictable
government-database URLs** instead of blind search:

- Federal/provincial "completed FOI/ATI request" logs exist and are real — federal
  (`open.canada.ca`'s ATI Summaries) has a working bulk-downloadable dataset; BC's
  provincial equivalent (Open Information portal) exists but its search results are
  JavaScript-rendered and won't return to a non-browser fetch — flag that as a real
  limitation for a human to close, in the Phase 6 handoff, not something to fake around.
- Campaign-finance databases (e.g. Elections BC's FRPC) and national lobbyist registries
  (e.g. `lobbycanada.gc.ca`) are usually real, correctly-targeted tools that are simply
  unreachable by non-browser automation — one may reject scripted form submissions with
  a server error even when the field names are right, the other may sit behind a bot
  challenge. Confirm the block genuinely exists (don't give up after one try, but also
  don't burn excessive time on a single gap) and document the exact tool URL and field
  names precisely enough that a human with a browser can finish the query in minutes.
- There is no MuckRock-equivalent aggregator for Canada — don't suggest filing through
  or browsing one; it doesn't cover this jurisdiction.
- Write findings to a new `research-followup-gaps.md`, using the same confidence
  labeling as every other file, and list every URL attempted (successes and failures)
  so a future pass doesn't repeat blocked paths blindly.

## Phase 6 (required, every investigation): manual-steps handoff

End every investigation — and every deepening/follow-up pass that leaves gaps behind —
with an `investigations/{slug}/MANUAL-STEPS.md`. This is not the same as a "Research
Gaps" list buried in the CONTEXT.md; it's a short, standalone, actionable checklist for
a human with a browser: what to open, what to search, how long it takes, and exactly
what finding it would resolve. Don't include filing a *new* formal FOI/FOIPPA/ATIA
request on this list unless the user has explicitly said they're ready to do that —
default to read-only lookups against tools that already exist.

## Quality bar (unchanged from the base `investigate` skill, restated for this subject)

- Cite everything with a direct URL; confidence-label everything.
- Normal exercise of an official's role is not a conflict of interest. A trade
  association's board being staffed by its member companies' executives is not a
  conflict. Only report a conflict with a specific documented basis.
- Foreign ownership is reported as ordinary FDI, never as "interference," unless a
  specific source makes that claim explicitly — and even then, attribute it as a claim,
  not adopt it as this investigation's own conclusion.
- Keep similarly-named entities straight (a company and an NGO can share a near-identical
  name; a grassroots group and its parallel/successor movements can be entirely
  unconnected despite covering the same territory) — verify before conflating.
- Do not characterize a Nation's internal politics (elected government vs. grassroots
  movements, competing community voices) in terms of legitimacy — report what each
  actually did and said, sourced, and leave it there.
