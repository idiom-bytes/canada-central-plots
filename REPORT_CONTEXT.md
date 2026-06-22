# REPORT_CONTEXT.md — Infographic brief for an image-generation LLM

**Purpose:** generate a **cover/masthead + 5 sequenced infographics (6 images total)** that lead a
viewer through one data investigation (Canada Central). The five story panels form an arc:
**the conditions → the problem at home → the blind spot → can we respond? → Britain's precedent** —
opened by a title card. This file is self-contained: everything the image model needs is below.

## The investigation's name

> # COULD IT HAPPEN HERE?
> ### Grooming gangs in Britain — and what Canada's data on exploitation, policy and enforcement reveal about the same risk at home.

Use this as the title throughout. It is an open, investigative question — not an accusation — which
keeps the door open to readers across the spectrum.
*(Acceptable alternates if a variant is needed: "The Warning from Britain" · "On the Same Path?" · "Reading the Signals.")*

> **READ THIS FIRST — the lens, and the lines we don't cross.**
> The United Kingdom spent two decades uncovering **organized, group-based child sexual exploitation**
> — the "grooming gang" scandals of Rotherham, Telford and elsewhere — while institutions looked away
> and failed even to record who was responsible. This investigation asks a careful question: **is a
> similar pattern emerging in Canada, and would we even know?** It is a broad, holistic review across
> several areas — the crime trends, how the problem manifests here, the policies that reshaped
> screening/asylum/enforcement, the courts and removal system, and the data Canada keeps — measured
> against the UK's experience.
> - It **blames no community, faith, or ethnicity.** The subject is *institutions, decisions, and evidence.*
> - It does **NOT claim immigration causes crime.** Canada does not record offender origin, so any link
>   is *unmeasurable* — and that gap is itself a finding. **Correlation is not causation.**
> - Use precise, neutral terms: **"organized / group-based child sexual exploitation."** "Grooming
>   gangs" is the recognizable UK label, used descriptively — never as a slur or a claim about a group.
> Every image must hold this calm, factual, data-journalism tone. The data carries the weight.

---

## 1. The master narrative (context for the model)

In Britain, organized groups sexually exploited thousands of children over decades while authorities
hesitated — partly over how the perpetrators' background would look — and often did not even record
the basic facts. The 2025 Casey audit found offender ethnicity unrecorded in two-thirds of cases.

This investigation asks whether Canada could be on a similar path, and builds a holistic picture to
find out. Canada's police-reported rates for child sexual exploitation, human trafficking, kidnapping
and sexual assault have all **risen sharply over the past decade**. Over the same period the
immigration system was reshaped — rapid growth in temporary residents and a still-climbing asylum
stream, changed largely by **executive decisions rather than parliamentary votes** — while the courts
and removal system fell behind. And crucially, **Canada records no offender immigration status or
origin**, so the question that consumed Britain cannot even be measured here — even as Canada
publishes the origins of asylum claimants in detail. The conditions, the rising harm, the recording
gap, and the strained response together form the picture this report lays out — against the UK as a
cautionary precedent, and without blaming anyone.

---

## 2. Global style guide (applies to ALL 6 images)

**Aesthetic:** clean editorial **data-journalism** / infographic style — a serious national
newspaper's graphics desk or an Economist/Reuters explainer. Flat vector, generous whitespace, crisp
charts, restrained iconography. NOT dramatic, NOT photographic, NOT a poster, NOT propaganda.

**Color palette (use these exact tones):**
- Background / cream: `#F0ECE3`
- Card / white: `#FEFEFE`
- Primary text / near-black: `#2D2D2D`
- Alarm red (rising/negative series): `#B83232` (dark `#8B2020`)
- Teal (neutral/structural): `#3A5F6F`
- Amber (secondary): `#C47A3F`
- Green (corrective/positive): `#3A7A4A`
- UK accent: `#1D3A6B`

**Typography vibe:** clean humanist sans-serif (Inter / Helvetica / system-ui); bold for big hero
numbers, regular for labels. Clear hierarchy: hero number → label → supporting.

**Format:** design for **1200×1500 px portrait** unless noted. Footer strip for a source line + the
"Canada Central" wordmark.

**TEXT-RENDERING CAVEAT:** image models render long text poorly. Each image should carry **at most
1–3 large hero numbers + a few short labels**; exact strings are given per image so they can be
corrected/typeset in post. Prefer rendering the **chart shape + big number** visually and adding
fine-print numbers afterward. Keep on-image words minimal and spelled exactly as given.

**HARD CONTENT GUARDRAILS (non-negotiable — sensitive topic):**
- **No depictions of people by race, ethnicity, religion, or as offenders/victims.** No children, no
  crowds, no figures in cultural/religious dress, no "criminal" or abuse imagery, no borders. Use
  abstract data-viz, charts, maps, documents, neutral icons (scales, files, locks, a maple leaf, a
  magnifying glass, a redaction bar).
- **Non-partisan.** No party logos, no politicians, no flags used as weapons, no slogans.
- **No fear-mongering, no gore, nothing exploitative of the subject matter.** Calm and factual.
- Where an image touches crime or origin, include a short footer note:
  **"Canada does not record offender origin · correlation ≠ causation · no community is blamed."**
- Numbers must match this document exactly. Do not invent figures.

**Footer line (a version on every image):**
`Source: Statistics Canada, IRCC, Canada Gazette, PBO, UK Jay/Casey reviews · Canada Central · plots.canada-central.com/report.html`

---

## 3. The images

### № 0 — "COULD IT HAPPEN HERE?" (COVER · masthead / title card)
- **Role:** the splash that names the investigation, sets the calm/objective tone, invites the reader. Lead image / carousel slide 1 / share thumbnail.
- **One-line message:** A serious, source-based investigation — is the UK's grooming-gang pattern emerging in Canada, and would we know?
- **Title (exact, large):** `COULD IT HAPPEN HERE?`
- **Subtitle (exact, smaller):** `Grooming gangs in Britain — and what Canada's data on exploitation, policy & enforcement reveal about the risk at home`
- **Eyebrow (small, top):** `A CANADA CENTRAL DATA INVESTIGATION · 2026`
- **Optional bottom stat-ticker (small):** `Child sexual exploitation +148% in a decade` · `3,342 catalogued cases` · `99.4% of cases: offender origin unrecorded` · `UK: ~1,400 children in Rotherham alone`
- **Visual concept:** a calm broadsheet special-report cover. Cream `#F0ECE3` background, large
  near-black title. One quiet motif: a **magnifying glass over a faint data field / blank form**
  (we're investigating, and much is unrecorded), OR a subtle **two-territory split** (a faint UK
  outline and a faint Canada/maple-leaf motif on a shared timeline), OR a single thin rising red line.
  Heavy whitespace, a thin rule above the stat-ticker, understated wordmark.
- **Mood:** investigative but trustworthy — restrained, credible, not alarmist.
- **Avoid:** people, children, abuse cues, flags-as-symbols, drama, clip-art.
- **Footer adds:** `plots.canada-central.com/report.html` + standard source line.

### № 1 — "The conditions" (PANEL 1 · context)
- **Role:** establish the backdrop — rapid, fast-changing migration with a stream that keeps growing even as headline intake falls. (The UK's crisis grew amid rapid migration + weak institutional attention; this panel sets Canada's comparable conditions, neutrally.)
- **One-line message:** Headline immigration is down, but the least-controlled stream — asylum — keeps rising.
- **Hero numbers (exact):** `2.56M` temporary residents (2026) · `+608%` new asylum claims since 2015 · `525,000` asylum claimants now present.
- **Supporting:** work permits 1.30M and study permits 394k are *down* from 2024–25 peaks; net non-permanent residents peaked at **+781,000** in 2023/24.
- **Visual:** four trend lines — three (work, study, total) curving **down** from a peak, one
  (**asylum, alarm red**) continuing **up**. Big `+608%` callout. Title: "Coming down?"
- **Avoid:** people, borders. Pure chart + numbers.
- **Footer adds:** "Source: StatCan 17-10-0121; IRCC. Context, not blame."

### № 2 — "The problem at home" (PANEL 2 · the core question)
- **Role:** the heart of the investigation — are these crimes growing in Canada?
- **One-line message:** Police-reported child exploitation, trafficking and related crimes have all climbed.
- **Hero numbers (exact) — police-reported rate change, 2014→2024:**
  - Child sexual exploitation `+148%`  *(lead with this — it is the grooming-gang-adjacent category)*
  - Human trafficking `+205%`
  - Kidnapping `+63%`
  - Sexual assault `+53%`
  - Anchor: `3,342` distinct Canadian exploitation & trafficking cases catalogued (2016–2026)
- **Visual:** four upward arrows / small-multiples bars, child sexual exploitation as the focal one;
  alarm red/amber; clean dashboard look.
- **Avoid:** victims, perpetrators, any abuse imagery. Charts/icons only.
- **Footer adds:** "Police-reported rate per 100k (StatCan UCR 35-10-0177); undercounts true
  prevalence; indexed to 2014. Correlation ≠ causation; no community is blamed."

### № 3 — "We can't see who" (PANEL 3 · the blind spot, the UK parallel)
- **Role:** the pivot — Canada makes the central question unanswerable, the same recording failure that delayed Britain.
- **One-line message:** 99.4% of catalogued cases record no offender origin — the exact gap Britain's Casey audit condemned.
- **Hero numbers (exact):** `99.4%` of 3,342 cases name **no** offender origin/status · only `19` do ·
  UK parallel: Casey 2025 found ethnicity **unrecorded in 2/3** of grooming-gang cases.
- **Supporting contrast:** Canada *does* publish asylum claimants' countries of citizenship monthly —
  so origin is tracked when the state chooses to.
- **Visual:** split panel. Left: a nearly-all-grey donut with a tiny red 0.6% sliver + a **redaction-
  bar over a blank form** ("offender origin: not recorded"). Right: a small note that asylum origin
  *is* published (a neutral admin statistic, clearly labelled, NOT linked to the crimes).
- **Avoid:** depicting any nationality as criminal; do not connect the two panels causally.
- **Footer adds:** "Offender origin: not a field in StatCan's crime survey. Shown to illustrate a
  recording gap, not a link. No community is blamed."

### № 4 — "If we found it, could we act?" (PANEL 4 · enforcement & courts)
- **Role:** the response capacity — Britain's failure was also institutional follow-through.
- **One-line message:** Most people in provincial jail aren't convicted, removals are outpaced, and the rules changed largely without a vote.
- **Hero numbers (exact):** `76.6%` of provincial-jail population is **un-convicted** (remand; was
  22.5% in 1978) · `~300,000` asylum-claim IRB backlog · `8 of 11` landmark policy decisions made
  with **no parliamentary vote** · removals hit a record ~23,000 in 2025 but were **still outpaced**.
- **Visual:** a gauge/bar at 76.6% "held without conviction"; below it a mini-timeline 2012→2026 with
  a red cluster of system-weakening decisions in **2016–2022** and a few green "brakes" only in
  **2023–2026**. Motifs: scales of justice, a funnel/pipe, a stamped document.
- **Avoid:** prisoners, jail drama. Schematic only.
- **Footer adds:** "StatCan 35-10-0154; IRB; CBSA; Canada Gazette. Timing is correlation, not cause."

### № 5 — "Britain already lived this" (PANEL 5 · the precedent + CTA)
- **Role:** close the loop — the cautionary template and the call to read.
- **One-line message:** Britain only grasped the scale after a national reckoning; Canada sits a decade behind and can't yet measure it.
- **Hero numbers (exact):** UK `~1,400` children in **Rotherham alone** (1997–2013, Jay) · UK `19,125`
  modern-slavery referrals in 2024 (record) · Casey 2025: ethnicity **unrecorded in 2/3** of cases ·
  Canada: **same crimes rising, no offender-origin data to compare.**
- **Visual:** a two-country split (UK accent `#1D3A6B` left, Canada cream/red right) with a horizontal
  timeline showing Canada positioned ~10 years "behind" the UK's reckoning; a magnifying glass over a
  blank file ("can't see it yet"). CTA strip: "Read the full investigation → plots.canada-central.com/report.html".
- **Avoid:** grooming/abuse imagery of any kind; no people. Maps, timeline, documents only.
- **Footer adds:** "UK: Jay 2014; Casey 2025; Home Office NRM 2024. Canada is NOT claimed to mirror
  the UK's offender profile — that data isn't collected here."

---

## 4. Suggested sequence (carousel / article)

1. **COULD IT HAPPEN HERE?** — cover / title card (№ 0)
2. *The conditions* — rapid intake, the rising asylum stream (№ 1)
3. *The problem at home* — child exploitation & related crimes rising (№ 2)
4. *We can't see who* — the recording blind spot, the UK parallel (№ 3)
5. *If we found it, could we act?* — courts & enforcement (№ 4)
6. *Britain already lived this* — the precedent + read the investigation (№ 5)

---

## 5. Master source list (for fine print / credibility)

- Statistics Canada — Uniform Crime Reporting Survey, Table **35-10-0177-01** (police-reported crime, rate/100k)
- Statistics Canada — Table **17-10-0121-01** (non-permanent residents by type); **35-10-0154-01** (adults in custody / remand)
- IRCC Open Data — asylum claimants by office type and by top-25 country of citizenship
- Canada Gazette Part II / Justice Laws — IRPR amending regulations (SOR), ministerial instructions
- Parliamentary Budget Officer — asylum/IFHP cost figures
- Office of the Commissioner of Lobbying — Monthly Communication Reports
- United Kingdom — Independent Inquiry into CSE in Rotherham (Jay, 2014); Baroness Casey National Audit on Group-based CSE (2025); Home Office Modern Slavery NRM statistics (2024)

**Full investigation & all interactive dashboards:** https://plots.canada-central.com/report.html
