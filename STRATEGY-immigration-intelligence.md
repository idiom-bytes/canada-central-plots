# Strategy & Intelligence Charter — Canada's Immigration Reality

**Created:** 2026-06-21 · **Status:** living strategy doc (re-think of the whole problem)
**Detailed work log:** see [[CHECKPOINT-asylum-policy-chain.md]] for the granular per-view state.

---

## 1. The mission, in one line

> Use Canada's own official data to test the claims being made about immigration —
> and to produce an objective, sourced account of the system that legislative, policy,
> and ministerial decisions have actually built, and the risks now emerging from it.

We are not making an argument from sentiment. We are auditing **stated narrative vs.
measured reality**, decision by decision, with primary sources, and flagging honestly
where the data is strong, weak, contested, or deliberately absent.

## 2. The three claims we are testing

1. **"Immigration is coming down."** — True only for the levers the government controls
   directly (PR targets, study/work permits, all now falling from 2024-25 peaks). The
   **asylum stream is the exception and is exploding**, and the temporary-resident pool
   already inside the country (2.56M) cannot be un-admitted. *The headline is technically
   true and substantively misleading.* (Covered: Immigration Volumes, Asylum Channel.)

2. **"This happened to us / it's a border crisis."** — No. It was **built by policy**, as a
   chain of mostly executive decisions (8 of 11 by regulation / ministerial instruction /
   treaty, no parliamentary vote), over a decade, with named ministers. (Covered: Policy Timeline.)

3. **The narrative gap is systemic.** — Official and media attention repeatedly diverges from
   what the data measures. Examples: origin tracked for asylum claimants but blank for those
   charged with exploitation; heavy institutional focus on Islamophobia while **antisemitic
   incidents are far higher by both count and rate** (see §5). *This meta-pattern — narrative
   vs. data — is itself a finding.*

## 3. Analytical pillars (the architecture)

| Pillar | Question | Existing views | Status |
|---|---|---|---|
| **A. The Volume Reality** | Is immigration actually down? What's the real composition? | immigration-volumes, asylum-channel | ✅ strong |
| **B. The Policy Design** | How was this built, by whom, with what instrument? | policy-timeline | ✅ strong; deepen w/ Gazette (#146) + Senate (#147) |
| **C. The Consequences & Risks** | What problems result (UK-style)? | exploitation-record, origin-data-gap, justice-backlog | 🟡 partial — needs cohesion + fiscal + housing |
| **D. The Influence/Demand side** | Who benefits and lobbies for volume? | lobbying-influence | 🟡 partial |
| **E. The Narrative Gap** | Where does framing diverge from data? | (implicit; needs a home) | 🔴 not yet a view |
| **F. The Synthesis** | How does it all connect? Risks still in place? | policy-timeline "what's still broken" | 🟡 started; wants a landing/story page |

## 4. The risk taxonomy — "UK-style unchecked immigration," mapped to Canada

The UK is the cautionary template: rapid intake + weak integration + slow enforcement →
social-cohesion breakdown, grooming-gang scandals, two-tier-justice perceptions, surging
antisemitism, fiscal strain. Canada is running the same experiment. The risks to track:

- **A. Social cohesion** — religious/ethnic hate crime (esp. the antisemitism surge),
  imported foreign conflicts, segregation. *(new view needed — see §5)*
- **B. Public safety** — sexual exploitation & trafficking (the UK grooming-gang parallel;
  note `lake/working/The Rape Gang Inquiry Report.pdf`), organized crime. *(exploitation-record)*
- **C. Justice-system capacity** — court/remand backlog, catch-and-release, **enforcement
  collapse** (CBSA: 34,700 lost; removals rare). *(justice-backlog; deepen removals)*
- **D. Fiscal** — asylum processing/IFHP health/housing costs, federal→provincial downloading,
  PBO figures. *(new view: the real cost — uses verified PBO/IRB numbers, corrects the "$5B" myth)*
- **E. Institutional integrity** — IRB backlog (~300k), selective data tracking (origin gap),
  policy-by-regulation evading parliamentary scrutiny. *(origin-data-gap; policy-timeline)*
- **F. Housing & services** — affordability/capacity strain vs. intake. *(tie to economic-distress)*

## 5. New analysis to add — Narrative vs. Reality: antisemitism (from user example)

**Claim in the data (StatCan UCR 2024, to verify):** Jewish Canadians face the highest
police-reported hate-crime burden by a wide margin — ~920 incidents (2024) vs ~229 for Muslims;
**by rate, ~25× higher** (Jewish ~275/100k vs Muslim ~11/100k), despite Jews being <1% of the
population. This is consistent with the multi-year StatCan pattern and the post-Oct-2023 surge.

**Why this belongs:** it is the clearest "narrative vs. data" case — institutional and media
attention to Islamophobia is large, yet the measured incident burden falls overwhelmingly on
Jewish Canadians. That gap is the story.

**OBJECTIVITY CAVEAT (must carry into any view):** the example chart inflates the Muslim
denominator to ~2.10M ("adjusted for 2022-24 immigration surge"), which *lowers* the Muslim rate
and *widens* the gap. Using the 2021 Census (~1.78M Muslim) the Muslim rate is ~13/100k and the
gap ~21×. **Either way the gap is large and real**, but we will (a) show both denominators,
(b) cite StatCan UCR directly, (c) note police-reported ≠ total (underreporting varies), and
(d) lead with rate AND show counts. Rate-normalization is correct; denominator transparency is
mandatory. Counts alone, or a hidden denominator choice, would make us as unreliable as what we critique.

## 6. Objectivity standards (non-negotiable — this is what makes it "a review," not a polemic)

1. **Primary/official sources only** for headline claims (StatCan, PBO, IRB, OAG, IRCC, ESDC,
   CBSA, Canada Gazette, Parliament).
2. **Normalize by population (per-100k rates), and disclose the denominator.** Counts mislead.
3. **Correct exaggerations even when they favor the thesis** (we already corrected the viral
   "$5B" to itemized PBO figures).
4. **Flag contested attributions** (e.g. Century Initiative / McKinsey influence — asserted, denied).
5. **State what the data cannot establish** (inland claimants' prior status; offender origin;
   causation vs. correlation).
6. **Separate the people from the policy.** The accountability subject is *decisions and
   decision-makers*, not migrants as individuals. Keep risk framing about systems and outcomes.
7. **Show counter-evidence / steelman** where it exists.

## 7. Data acquisition roadmap (what to scrape next)

- **#146 Canada Gazette** — OICs, SORs, ministerial instructions, RIAS. The regulatory layer
  where most policy actually happens. *(issue open)*
- **#147 Senate** — current + historical, mirror HoC model. *(issue open)*
- **StatCan UCR hate-crime tables** (Table 35-10-0191 et al.) — for §5, multi-year, by religion/rate.
- **IRB statistics** (claims, backlog, finalization times, by country) — Pillar C/E.
- **PBO reports** (asylum cost, levels-plan demographics) — Pillar D.
- **IRCC asylum open data** (claims by year/office/country) — already partly in `data/asylum.js`.
- **CIMM committee binders** (canada.ca transparency) — ministerial Q&A, internal framing.

## 8. Build roadmap (proposed priority)

1. **Capstone overview / story page** — ties all pillars into one navigable narrative
   (extends the "what's still broken" nav). The connective tissue the project lacks.
2. **Narrative vs. Reality: antisemitism** view (§5) — high-impact, clean data, verify first.
3. **The real cost** view (Pillar D) — PBO/IRB fiscal, corrects "$5B."
4. **Deepen enforcement/removals** (Pillar C) — CBSA collapse as its own surface.
5. Then data depth: Gazette (#146) → richer policy-timeline; Senate (#147) → full Parliament.

## 9. House rules / process (learned)
- Token-aware: prefer **lean inline WebSearch** (5-8 queries) over the deep-research Workflow
  (50+ agents). Checkpoint findings as you go so nothing is lost at a limit.
- All plot work lives on branch `feature/immigration-asylum-narrative` in `canada-central-plots`
  (separate repo from `house_of_commons`). Commit per increment.
- Pages are static HTML + house design tokens; data-driven arrays where possible; verify
  `node --check` on script blocks and div balance before commit.
