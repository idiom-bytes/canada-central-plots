# REPORT_CONTEXT.md — Infographic brief for an image-generation LLM

**Purpose:** generate a **cover/masthead + 5 sequenced infographics (6 images total)** that lead a
viewer through one data report (Canada Central). The five story panels form an arc:
**intake → crime → the data blind spot → system failure → the UK warning** — opened by a title card.
This file is self-contained: everything the image model needs is below.

## The report's name

> # WHAT CANADA DOESN'T COUNT
> ### Immigration, policy, and the public-safety record — measured to the edge of the data.

Use this as the title throughout. The name carries the report's spine on several levels: Canada
doesn't count **offenders' origin**; doesn't count the **asylum growth** hidden behind "immigration
is coming down"; and reshaped the system through **executive orders that bypassed parliamentary
scrutiny**. It is neutral, factual, and memorable.
*(Acceptable alternates if a variant is needed: "The Unrecorded" · "Coming Down?" · "The Blind Spot.")*

> **Read this first — what this report IS and ISN'T.** It is an objective, source-based review.
> It reports two things side by side — immigration policy/intake, and public-safety crime trends —
> and is explicit that **it does NOT claim immigration causes crime. Correlation is not causation.**
> Canada does not record offenders' origin, so the link is *unmeasurable*, and that gap is itself a
> finding. Every infographic must keep this neutral, factual, data-journalism tone.

---

## 1. The master narrative (context for the model)

Ottawa says immigration is being reduced. By the data, that's true for the levers it controls
directly (permanent residents, study and work permits — all falling from 2024–25 peaks), but the
**asylum stream is the exception and is still climbing**. Over the same decade, Canada's
police-reported rates for human trafficking, kidnapping, sexual assault and child exploitation all
rose. Yet Canada records **no offender immigration status or origin**, so any link can't be
measured — even as it publishes the origin of *asylum claimants* in detail. The justice and
enforcement systems can't keep pace (most people in provincial jail are un-convicted; removals are
outpaced by intake). The system was reshaped mostly by **executive decisions, not parliamentary
votes**. The UK lived a version of this — Rotherham, the grooming-gang scandals — and only after a
national reckoning began recording who was responsible. Canada sits roughly where the UK was a
decade ago, but **cannot yet see the pattern, because it doesn't collect the data.**

---

## 2. Global style guide (applies to ALL 5 infographics)

**Aesthetic:** clean editorial **data-journalism** / infographic style — think a serious national
newspaper's graphics desk or an Economist/Reuters explainer. Flat vector, generous whitespace,
crisp charts, restrained iconography. NOT dramatic, NOT photographic, NOT propaganda.

**Color palette (use these exact tones):**
- Background / cream: `#F0ECE3`
- Card / white: `#FEFEFE`
- Primary text / near-black: `#2D2D2D`
- Alarm red (the rising/negative series): `#B83232` (dark `#8B2020`)
- Teal (neutral/structural): `#3A5F6F`
- Amber (secondary): `#C47A3F`
- Green (corrective/positive): `#3A7A4A`
- UK accent (Chapter 5 only): `#1D3A6B`

**Typography vibe:** clean humanist sans-serif (Inter / Helvetica / system-ui), bold condensed for
big hero numbers, regular for labels. One clear visual hierarchy: hero number → label → supporting.

**Format:** design for **1200×1500 px portrait** (social/article share) unless noted. Leave a footer
strip for a source line + the wordmark "Canada Central".

**TEXT-RENDERING CAVEAT (important):** image models render long text poorly. Each infographic
should carry **at most 1–3 large hero numbers + a few short labels** baked in; the exact strings are
given per graphic so they can be corrected/typeset in post. Prefer rendering the *chart shape and
big number* visually and adding fine-print numbers afterward. Keep on-image words minimal and spelled
exactly as given.

**HARD CONTENT GUARDRAILS (non-negotiable — sensitive topic):**
- **No depictions of people by race, ethnicity, religion, or as offenders/victims.** No crowds at
  borders, no figures in cultural/religious dress, no "criminal" imagery. Use abstract data-viz,
  charts, maps, documents, icons (scales, files, locks, a maple leaf, a redaction bar).
- **Non-partisan.** No party logos, no politicians' faces, no flags used as weapons, no slogans.
- **No fear-mongering or gore.** The data carries the weight; the visuals stay calm and factual.
- Always include the **source** and, where the graphic touches crime/origin, a short
  **"correlation ≠ causation / Canada does not record offender origin"** note in the footer.
- Numbers must match this document exactly. Do not invent figures.

**Footer line (put a version on every graphic):**
`Source: Statistics Canada, IRCC, Canada Gazette, PBO, UK Jay/Casey reviews · Canada Central · plots.canada-central.com/report.html`

---

## 3. The infographics

### № 0 — "WHAT CANADA DOESN'T COUNT" (COVER · masthead / title card)
- **Role in arc:** the splash/cover that names the study, sets the objective tone, and invites the viewer in. This is the lead image (article header / carousel slide 1 / share thumbnail).
- **One-line message:** A serious, source-based national data report — what the numbers show, and where Canada stops counting.
- **Title text (exact, baked in large):** `WHAT CANADA DOESN'T COUNT`
- **Subtitle (exact, smaller):** `Immigration, policy & the public-safety record — measured to the edge of the data`
- **Eyebrow / kicker (small, top):** `A CANADA CENTRAL DATA REPORT · 2026`
- **Optional "inside this report" stat ticker (small, along the bottom):** `2.56M temporary residents` · `+608% asylum claims` · `99.4% of cases: offender origin unrecorded` · `76.6% in jail un-convicted`
- **Visual concept:** a calm, authoritative editorial **cover**. Cream `#F0ECE3` background, large
  near-black `#2D2D2D` title set in a bold humanist sans. Behind/around the title, a **faint,
  elegant motif**: a subtle maple leaf composed of fine data points or thin chart lines, OR a single
  thin rising line (alarm red `#B83232`) crossing the page, OR a faint **redaction bar** partly
  obscuring a line of text (evokes "doesn't count / unrecorded"). Lots of whitespace. A thin rule
  separating title from the bottom stat-ticker strip. The "Canada Central" wordmark, understated.
- **Mood:** investigative but trustworthy — a national broadsheet's special-report cover, not a poster.
- **Avoid:** people, flags-as-symbols, drama, clip-art. No politicians, no borders, no crowds.
  Typography and one quiet motif do all the work.
- **Footer adds:** `plots.canada-central.com/report.html` + the standard source line.

### № 1 — "Coming down? Not the part that matters." (PANEL 1 · THE HOOK · divergence)
- **Role in arc:** open with the contradiction between the message and the data.
- **One-line message:** Permits are falling, but asylum — the stream Ottawa controls least — keeps rising.
- **Hero numbers (exact strings):**
  - `2.56M` temporary residents in Canada (2026) — *nearly doubled since 2021*
  - `+608%` growth in new asylum claims since 2015 (15,965 → 113,040)
  - `525,000` asylum claimants now in the country
- **Supporting data:** work permits 1.30M and study permits 394k are *down* from 2024–25 peaks; net
  non-permanent residents peaked at **+781,000 in a single year** (2023/24).
- **Visual concept:** a line chart with **four trend lines** — three (work, study, total) curving
  **down** from a peak, one (**asylum, in alarm red `#B83232`**) continuing **up and to the right**.
  Big `+608%` callout on the rising line. Title across top: "Coming down?"
- **Avoid:** people, borders. Pure chart + numbers.
- **Footer adds:** "Source: StatCan 17-10-0121; IRCC asylum open data."

### № 2 — "The crimes rising at home" (CONSEQUENCE)
- **Role in arc:** the public-safety trends, stated plainly and neutrally.
- **One-line message:** Police-reported rates for four serious crimes all rose over the decade.
- **Hero numbers (exact strings) — police-reported rate change, 2014→2024:**
  - Human trafficking `+205%`
  - Child sexual exploitation `+148%`
  - Kidnapping `+63%`
  - Sexual assault `+53%`
  - Anchor stat: `3,342` distinct Canadian exploitation & trafficking cases catalogued (2016–2026)
- **Visual concept:** four upward arrows or a small-multiples bar set, each labelled with the crime
  and its % rise, in alarm red/amber. Clean "dashboard" look. A single large `+205%` as the focal point.
- **Avoid:** victims, perpetrators, police imagery beyond a neutral icon. No violence.
- **Footer adds:** "Police-reported rate per 100k (StatCan UCR 35-10-0177). Undercounts true
  prevalence. Indexed to 2014. Correlation ≠ causation."

### № 3 — "Canada doesn't record WHO." (THE BLIND SPOT · the unique finding)
- **Role in arc:** the pivot — why the obvious question can't be answered here.
- **One-line message:** 99.4% of catalogued cases name no offender origin — yet Canada publishes asylum-seekers' origins in detail.
- **Hero numbers (exact strings):**
  - `99.4%` of 3,342 exploitation/trafficking cases give **no** offender immigration status or origin
  - `19` cases out of 3,342 name any origin at all
  - vs. asylum claimant origins **are** published monthly (top 2025: Haiti, India, Iran, Nigeria, Mexico)
- **Visual concept:** a **split panel**. Left: a nearly-all-grey donut/bar labelled "Offender origin
  recorded" with a tiny red sliver = 0.6%, plus a **redaction-bar motif** (black censor bars over a
  blank form). Right: a tidy ranked list/bars of asylum source countries (fully visible). The
  contrast — blank vs. detailed — is the whole point.
- **Avoid:** depicting any nationality as criminal. The right panel is *asylum claimants* (a neutral
  administrative statistic), clearly labelled as such, NOT linked to the left panel's crimes.
- **Footer adds:** "Offender origin: not a field in StatCan's crime survey. Asylum origin: IRCC open
  data. The two are shown to illustrate a data asymmetry, not a link."

### № 4 — "A system that can't keep up." (SYSTEM FAILURE)
- **Role in arc:** intake + crime meet an overwhelmed state, reshaped mostly without a vote.
- **One-line message:** Most people in provincial jail aren't convicted, removals are outpaced, and the rules changed largely by executive order.
- **Hero numbers (exact strings):**
  - `76.6%` of people in provincial jails are **un-convicted** (remand) — up from 22.5% in 1978
  - `~300,000` asylum claims stuck in the IRB backlog
  - `8 of 11` landmark policy decisions made with **no parliamentary vote**
  - context: removals hit a record ~23,000 in 2025 but were **still outpaced** by new arrivals
- **Visual concept:** two stacked ideas — (top) a **gauge or bar at 76.6%** "held without
  conviction"; (bottom) a **mini-timeline** 2012→2026 with dots: a red cluster of "system-weakening"
  decisions in **2016–2022** and a few green "brakes" only in **2023–2026**. Motifs: scales of
  justice, a clogged pipe/funnel, a stamped document.
- **Avoid:** prisoners, jail-cell drama. Keep it schematic.
- **Footer adds:** "StatCan 35-10-0154; IRB; CBSA; Canada Gazette. Timing is correlation, not proof of cause."

### № 5 — "The UK already lived this." (THE WARNING · close + CTA)
- **Role in arc:** the cautionary template and the call to read the report.
- **One-line message:** Britain only learned the scale after a national reckoning; Canada sits a decade behind and can't yet measure it.
- **Hero numbers (exact strings):**
  - UK: `~1,400` children exploited in **Rotherham alone** (1997–2013, Jay Report)
  - UK: `19,125` modern-slavery referrals in 2024 (record); the 2025 Casey audit found offender
    ethnicity **unrecorded in two-thirds** of cases
  - Canada: **same crimes rising — but no offender-origin data to compare**
- **Visual concept:** a **two-country split** (left UK accent `#1D3A6B`, right Canada red/cream) with
  a horizontal **timeline/clock** showing Canada positioned ~10 years "behind" the UK's reckoning.
  A maple leaf + a magnifying glass over a blank file ("can't see it yet"). Clear **CTA strip**:
  "Read the full report → plots.canada-central.com/report.html".
- **Avoid:** grooming/abuse imagery of any kind; no people. Maps, timeline, documents only.
- **Footer adds:** "UK: Jay Report 2014; Baroness Casey National Audit 2025; Home Office NRM 2024.
  Canada is not claimed to mirror the UK's offender profile — that data isn't collected here."

---

## 4. Suggested sequence (if posted as a carousel / used in the article)

1. **WHAT CANADA DOESN'T COUNT** — cover / title card (№ 0)
2. *Coming down? Not the part that matters.* — the intake divergence (№ 1)
3. *The crimes rising at home.* — the four trends (№ 2)
4. *Canada doesn't record who.* — the blind spot (№ 3)
5. *A system that can't keep up.* — backlog, removals, executive rule-making (№ 4)
6. *The UK already lived this.* — the warning + read the report (№ 5)

---

## 5. Master source list (for fine print / credibility)

- Statistics Canada — Uniform Crime Reporting Survey, Table **35-10-0177-01** (police-reported crime, rate/100k)
- Statistics Canada — Table **17-10-0121-01** (non-permanent residents by type); **17-10-0008-01** (components of growth); **35-10-0154-01** (adults in custody / remand)
- IRCC Open Data — asylum claimants by office type and by top-25 country of citizenship
- Canada Gazette Part II / Justice Laws — IRPR amending regulations (SOR), ministerial instructions
- Parliamentary Budget Officer — asylum/IFHP cost figures (IFHP $896M in 2024-25; projected >$1.5B/yr by 2029-30)
- Office of the Commissioner of Lobbying — Monthly Communication Reports (6,094 immigration lobbying contacts, 2008–2024)
- United Kingdom — Independent Inquiry into CSE in Rotherham (Jay, 2014); Baroness Casey National Audit on Group-based CSE (2025); Home Office Modern Slavery NRM statistics (2024)

**Full report & all interactive dashboards:** https://plots.canada-central.com/report.html
