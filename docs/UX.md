# Story / Chapter pattern

How multi-part investigative reports are structured on Canada Central. This
codifies a pattern that was already used once (the grooming-gangs
investigation, `report.html` on `feature/immigration-asylum-narrative`) and
is now the standard for any report big enough to outgrow a single page.

## Vocabulary

- **Story** — one landing page that tells the whole narrative arc in
  miniature. It never contains the full chart toggles or data table for any
  single topic; it summarizes and links out.
- **Chapter** — one standalone HTML dashboard, `reports/{slug}.html`, built
  per the `report_architect` skill (hero stats, accountability section,
  full chart views, complete downloadable data table). A Chapter is a
  first-class page — it can be read with zero Story context.
- A Story is a thin `chapters: []` array over full Chapter pages, not a
  container that owns their content. **All real data lives in the
  Chapters**; the Story only re-renders small preview slices of it.

```
Story (reports/{story-slug}.html)
├── chapters[0] → reports/{chapter-1-slug}.html
├── chapters[1] → reports/{chapter-2-slug}.html
└── chapters[N] → reports/{chapter-n-slug}.html
```

## When to use which

- **Single Chapter, no Story**: the topic is one investigation with one
  spine of evidence (e.g. `cancelled-projects.html`, `food-insecurity.html`).
  Most reports live here. Don't build a Story for a one-Chapter topic.
- **Story + multiple Chapters**: the topic naturally splits into 2+ major
  sub-investigations that each deserve their own hero stats, chart views,
  and data table, but which add up to one bigger argument (e.g. "is a UK-style
  grooming-gang pattern emerging in Canada?" splits into the blind spot, the
  official crime trend, the policy timeline, enforcement capacity, the UK
  comparison...). If you catch yourself appending a 4th unrelated chart
  block to an existing Chapter's HTML file just because the topic is
  related, that's usually the signal to split it into its own Chapter and
  wire it into (or create) a Story instead.

## Data flow — same pipeline-first rule, shared across pages

A Story and its Chapters typically read from the **same pipeline output**.
Two acceptable shapes:

1. One `pipeline/report_{topic}.py` → one `data/report-{topic}.json`,
   consumed by every Chapter page AND the Story's preview charts (each page
   reads only the JSON keys it needs). This is the default — simplest to
   keep in sync.
2. Several topic-specific `data/{name}.js` globals (e.g. `data/crime_rates.js`,
   `data/datagap.js`), each produced by its own pipeline script, loaded via
   `<script src="data/{name}.js">` on both the Story page and whichever
   Chapter page(s) need that slice. Use this only when the Chapters
   genuinely draw on different, independently-updated source pipelines.

Either way: **never hand-copy a number from a Chapter into the Story.** The
Story's summarized stats and preview chart must compute from the same JSON/JS
the Chapter reads, so the two can never drift out of sync.

## Story page structure (reference: `report.html`)

In source order:

1. **Topbar** — sticky, brand + mobile "jump to section" `<select>` + nav
   links. Desktop hides the jump-select in favor of the sidebar TOC.
2. **Sidebar TOC** (`.toc`, desktop only, `position: sticky`) — built from a
   single JS array of `[sectionId, label]` pairs (`const CH = [...]` in the
   reference implementation), with an `IntersectionObserver` scrollspy that
   highlights the active section as the reader scrolls. One array is the
   single source of truth for both the sidebar and the mobile dropdown.
3. **Hero** — kicker line (byline/date), `<h1>` narrative title, one lede
   paragraph stating the investigation's central question.
4. **"Before you read" section** — methodology/standards disclosure
   (sources used, what the report does and doesn't claim, how figures are
   normalized). Builds trust before the narrative starts.
5. **One `<section id="...">` per chapter**, each containing, in order:
   - `.ch-num` eyebrow: `"Chapter N"` or `"Chapter N · subtitle"`
   - `<h2>` — a narrative, provocative-but-accurate chapter title (not the
     Chapter page's own `<title>` necessarily — the Story can rephrase it
     for the arc)
   - *(optional)* `.finding` — a single, high-impact gradient callout block
     for the chapter's ONE most important number, when it's a strong lead
   - *(optional)* `.stats` — a small grid of 2-4 stat cards, a simplified
     subset of the Chapter's own hero stats (not all 5)
   - 1-2 body paragraphs of narrative prose, bolding key figures
   - *(optional, at most one)* `.chart-card` with a small canvas — a
     **summarized preview** of the Chapter's primary chart, built from the
     same shared data. Simpler styling than a Chapter's chart-card (no
     colored top border, no view toggles) — it's a teaser, not the full view.
   - *(optional)* `.callout` — one sentence of context, caveat, or
     comparison that doesn't fit the prose
   - one or more `.deep` pill-button links: `"Deep dive: {Chapter title} →"`,
     pointing at `reports/{chapter-slug}.html`. A chapter section may link
     to more than one Chapter page if closely related topics were split.
6. **Closing "Explore the evidence" section** — `.index-grid` linking every
   Chapter page (title + one-line description), even ones only briefly
   mentioned in the narrative above. This is the exhaustive index; the
   numbered chapters above are the curated narrative path.
7. **Footer** — one-line source list + "compiled by Canada Central."

## Chapter page structure

Unchanged from the existing `report_architect` skill: hero stats,
accountability/entity-tag section, 2-4 chart views, full downloadable data
table. A Chapter must stand alone — assume the reader arrived from a search
engine, not from the Story.

## `reports.html` integration

- The Story gets its own `.report-card`, tagged distinctly (reference
  implementation uses `● Start Here — The Full Investigation`) so it reads
  as the entry point, not just another report.
- Chapters that are strong enough to stand alone editorially (a flagship
  finding, not just supporting detail) **also** get their own `.report-card`
  below the Story's, tagged with their own angle (e.g.
  `● The Core Question — June 2026`). Not every Chapter needs a card —
  supporting/detail Chapters can be reached only via the Story's index-grid
  and cross-links from other Chapter pages.

## CSS class contract (Story-only additions)

These are new, on top of the existing Chapter/report CSS tokens
(`--color-cream`, `--accent`, `.hero-stat`, `.chart-card`, `.accountability`,
etc. — see the `report_architect` skill's CSS reference):

| Class | Purpose |
|---|---|
| `.topbar`, `.topbar-jump`, `.topbar-links` | sticky top nav + mobile section jump |
| `.toc`, `.toc-h`, `.toc a.active` | desktop sidebar TOC + scrollspy active state |
| `.hero .lede`, `.kicker` | Story hero (distinct from a Chapter's `.page-title`/`.page-desc`) |
| `.ch-num` | chapter eyebrow (equivalent to a Chapter's `.section-eyebrow`) |
| `.finding`, `.finding-tag`, `.finding-big`, `.finding-num`, `.finding-label` | single-stat gradient hero callout for a chapter's lead number |
| `.stats`, `.stat` (+ color variants) | small simplified stat grid, distinct from a Chapter's larger `.hero-stats`/`.hero-stat` |
| `.callout`, `.callout.teal` | one-line context/caveat box |
| `.deep` | pill-button deep-dive link |
| `.index-grid` | closing exhaustive chapter index |

## Worked example

- Story: `report.html` — "Could It Happen Here? Grooming Gangs, Britain &
  Canada's Data"
- Chapters: `origin-data-gap.html`, `ucr-record.html`,
  `exploitation-record.html`, `immigration-volumes.html`,
  `asylum-channel.html`, `policy-timeline.html`, `justice-backlog.html`,
  `enforcement.html`, `canada-vs-uk.html`, `lobbying-influence.html`,
  `policy-crime-impact.html`, and others — each a full standalone dashboard.
- Shared data: `data/asylum.js`, `data/crime_rates.js`, `data/datagap.js`,
  `data/justice.js`, `data/lobbying.js`, `data/policy_events.js`,
  `data/gazette_events.js` — loaded by the Story for its preview charts AND
  by whichever Chapter pages need that slice.
