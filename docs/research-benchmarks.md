# Research memo — verifying the two "scale" comparisons

Independent verification of the two benchmark claims made in the source
social media thread (see `docs/kb-bc-treaty-land.md`, section 1a) about
135,425 ha (1,354.25 km², ~334,642 acres) of BC provincial Crown land
committed under current Final and Incremental Treaty Agreement tables.
This is a research memo, not report copy — numbers below still need to be
transplanted into the pipeline/report with proper citation formatting.

Base figure used throughout: **135,425 ha = 1,354.25 km²** (exact unit
conversion, ha ÷ 100) **≈ 334,642 acres** (135,425 × 2.4710538 acres/ha,
the precise ha→acre conversion factor). The tweet's "334,000 acres" is a
reasonable rounding (−0.2%, immaterial).

---

## 1. "Roughly 47% of the entire land area of Metro Vancouver"

**Verdict: Confirmed. The 47% figure is accurate.**

### Metro Vancouver's official land area

- **2,878.93 km²** — Statistics Canada, 2021 Census of Population, Census
  Profile for Metro Vancouver Regional District (census division
  DGUID 2021A00055915020).
  https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm
  (StatCan's direct census-profile page for this DGUID 404'd on fetch in
  this session — the figure was corroborated via Wikipedia's cited
  infobox, which sources the same 2021 Census table; re-pull the live
  StatCan profile page before publication to get a first-party
  screenshot/citation rather than relying on the Wikipedia mirror.)
- **≈2,870 km²** — Metro Vancouver Regional District's own regional
  planning figure ("the region has a land base of 2,870 square
  kilometres"), reported by Daily Hive citing Metro Vancouver directly:
  https://dailyhive.com/vancouver/metro-vancouver-land-size-affordability-issue

The two independent figures (StatCan census boundary vs. Metro Vancouver's
own regional-planning land base) agree to within 0.3%, so the region's
land area is solidly in the **2,870–2,879 km²** range.

### Recomputed percentage

- 1,354.25 km² ÷ 2,878.93 km² (StatCan) = **47.0%**
- 1,354.25 km² ÷ 2,870 km² (Metro Vancouver's own figure) = **47.2%**

Both independent recomputations land on **~47%** — the tweet's claim
checks out almost exactly. No correction needed on this one.

### Alternative benchmarks (clearer for a general reader than a regional
district's technical land area)

Metro Vancouver's ~2,879 km² isn't an intuitive quantity for most readers
(a "regional district" boundary is a planning abstraction, not a place
people picture). These are more concrete, all independently sourced:

| Benchmark | Official size | 135,425 ha (1,354.25 km²) as a multiple |
|---|---|---|
| **City of Vancouver** (the city proper, not the region) | 115.18 km² — StatCan 2021 Census, Census Profile, Vancouver CSD (DGUID 2021A00055915022) | **≈11.8×** the land area of the City of Vancouver |
| **Stanley Park** | 404.9 ha — Wikipedia, sourced to City of Vancouver/Vancouver Park Board data (a 2025 Park Board report cites 418 ha as a more recent internal figure) | **≈332–335×** the size of Stanley Park |
| **E.C. Manning Provincial Park** | 70,844 ha as of the park's last BC Parks boundary revision (Oct. 1999); some sources report ~83,671 ha after a 2012 amalgamation with the former Cascade Recreation Area — see https://en.wikipedia.org/wiki/E._C._Manning_Provincial_Park | **≈1.6–1.9×** the size of Manning Park |
| **Golden Ears Provincial Park** | ~55,590 ha per Wikipedia (555.9 km²); other sources cite "over 62,000 ha" — BC Parks' own page (https://bcparks.ca/golden-ears-park/) does not state an area figure, so this needs a firmer primary-source pull before publication | **≈2.2–2.4×** the size of Golden Ears Park (range reflects the source discrepancy) |
| **Capital Regional District** (Greater Victoria, all 13 municipalities + electoral areas) | 2,341.11 km² — per Wikipedia's CRD infobox | **≈58%** of the CRD's land area |

**Recommendation:** Lead with "**~11.8 times the land area of the City of
Vancouver**" or "**about 335 Stanley Parks**" — both are concrete, visual,
and independently verifiable to a precise primary/secondary source, more
so than "47% of Metro Vancouver" (which is correct but requires the reader
to already know Metro Vancouver's size, which most don't). Keep the Metro
Vancouver comparison too since it's confirmed accurate and was the
original claim — just don't rely on it as the *only* scale anchor.
Before publication, get a first-party BC Parks or Wikipedia-cited
BC Parks area figure for whichever provincial park comparison is used, to
resolve the Golden Ears / Manning Park source discrepancies noted above.

---

## 2. "At B.C.'s 2025 average agricultural land value of about
$10,477/acre, that much land would represent roughly $3.5 BILLION"

**Verdict: Directionally confirmed, with a correction to the per-acre
figure.** The headline "~$3.5 billion" conclusion holds up under
independent recomputation from an official source — but the precise
$10,477/acre figure is not what the primary government data series says
for 2025. It should be corrected to **$10,577/acre**, and the underlying
benchmark should be flagged more strongly than the tweet already flags it
(see caveat discussion below).

### Where the actual official 2025 BC figure comes from

Two candidate sources were checked; only one publishes a single
blended provincial average per acre — the other doesn't, which itself is
an important finding:

1. **Statistics Canada, Table 32-10-0047-01, "Value per acre of farm land
   and buildings at July 1"** (formerly CANSIM 002-0003). This is the
   correct source for a single BC-wide average $/acre figure. Pulled the
   full table directly (CSV bulk download,
   https://www150.statcan.gc.ca/n1/tbl/csv/32100047-eng.zip) and read the
   raw values:
   - **British Columbia, 2025: $10,577/acre** (no preliminary/revision
     flag on this record — it's StatCan's current published figure as of
     this research, Aug 2026)
   - British Columbia, 2024: $10,181/acre
   - British Columbia, 2023: $10,069/acre
   - Canada national average, 2025: $5,643/acre (BC is roughly double the
     national average, consistent with BC having Canada's highest
     farmland values per the FCC report below)
   - Table URL: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210004701

2. **Farm Credit Canada, 2025 FCC Farmland Values Report**
   (https://www.fcc-fac.ca/en/reports/2025-farmland-values-report;
   PDF text extracted directly from a mirrored copy). This report is
   almost certainly what the "2025 average agricultural land value"
   framing is gesturing at, but **it does not publish a single
   province-wide blended $/acre average for BC at all** — only
   region-by-region "reference values," which vary enormously:

   | BC region (cultivated land) | 2025 value $/acre | 2025 % change |
   |---|---|---|
   | Peace-Northern | $2,400 | 0.0% |
   | Cariboo-Chilcotin | $4,400 | 0.0% |
   | Kootenay | $17,000 | −21.1% |
   | Okanagan | $40,500 | 0.0% |
   | Vancouver Island | $65,600 | +5.3% |
   | South Coast | $104,600 | −7.4% |

   FCC's report headline is that BC's *average cultivated farmland value*
   "edged down 1.7%" province-wide in 2025 (a rate of change, not a
   dollar figure) — following an 11.3% increase in 2024. BC has the
   highest farmland values of any province, but a single "average $/acre"
   number for the whole province is not something FCC actually publishes,
   because the regional range ($2,400 to $104,600/acre — a 43x spread) is
   too wide for a single average to mean much.

**Conclusion on the source of $10,477/acre:** it's in the right
neighbourhood but doesn't match either primary source exactly. It's
closest to the StatCan series — $10,477 sits between the StatCan 2024
figure ($10,181) and 2025 figure ($10,577), about 1% below the current
2025 published value. The most likely explanation is the tweet used a
slightly earlier data pull or a preliminary StatCan release that was
subsequently revised upward to $10,577 (StatCan revises this annual
series after initial publication). **Recommendation: correct the report's
figure to $10,577/acre, sourced to StatCan Table 32-10-0047-01**, since
that is the only official series that actually publishes a single BC-wide
average and it's directly traceable/reproducible.

Note also that the StatCan series measures "value of farm land **and
buildings**," not land alone — so it modestly overstates pure land value
by folding in barns, houses, and other farm structures. This is a second,
independent reason (beyond the land being mostly non-agricultural — see
below) to caveat this benchmark as approximate.

### Recomputed total value

Using the corrected, sourced StatCan figure and the precise acreage:

- 334,642 acres × $10,577/acre = **$3,540 million (≈$3.54 billion)**
- Using the tweet's rounder "334,000 acres" × $10,577 = **$3,533 million
  (≈$3.53 billion)**
- Using the tweet's original $10,477/acre × 334,000 acres = **$3,499
  million (≈$3.50 billion)** — this is the tweet's own math, and it
  checks out arithmetically (334,000 × 10,477 = 3,499,318,000).

**All three variants round to "roughly $3.5 billion."** So while the
per-acre figure needs a small correction (see above), the tweet's
bottom-line dollar conclusion is not materially wrong — it would still
round to $3.5B using the corrected, properly-sourced $10,577/acre figure.
This can be reported as: *"~$3.5 billion, using BC's official 2025 average
farmland value of $10,577/acre (Statistics Canada)."*

### Is agricultural land value the right benchmark at all? (the more
important finding)

The tweet itself flags this ("that is NOT an appraisal, the land varies
enormously by location and use... simply a benchmark to understand the
scale") — and that caveat is well-founded and should be kept, or
strengthened, in the report. Two structural problems with the
farmland-value benchmark specifically:

1. **The 135,425 ha of treaty-committed land is not farmland.** Per the
   Public Accounts table (kb doc, section 1c), this is a province-wide
   mix of forested Crown land, rural/remote parcels (Kaska Dena, Wuikinuxv,
   Lax Kw'alaams, etc.), and some higher-value coastal/urban-adjacent
   parcels (Te'mexw/Victoria area). Farmland value — which the FCC data
   above shows ranges 43x across BC's own agricultural regions — is a
   weak proxy for land that's mostly *not* agricultural.
2. **A single average conceals a huge range even within farmland**, so
   applying one BC-wide number to 335,000 acres of ecologically and
   geographically diverse Crown land compounds the imprecision.

**A more defensible alternative benchmark was investigated but could not
be fully sourced in this session:**

- **BC Assessment's Managed Forest Land valuation schedule** (under the
  *Managed Forest Land and Cut Timber Values Regulation*, BC Reg. 90/2000,
  Schedule B, most recently amended by BC Reg. 284/2024) sets official
  per-hectare bare-land values by valuation zone specifically for forest
  land — which is a much closer match to the actual land types in Note 28
  than farmland is. However, the actual Schedule B dollar table did not
  render in the web-fetch tools available this session (it appears to be
  a graphical/tabular schedule not captured by the text extraction used
  here). **This is flagged as unverified and needs a follow-up pull**
  — either the BC Laws PDF directly, or BC Assessment's managed-forest-land
  product pages — before it can be used as a published figure.
- **BC's own Crown land pricing policy** (Land Policy: Pricing,
  https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/natural-resource-use/land-water-use/crown-land/pricing.pdf)
  confirms fee-simple Crown land dispositions are priced at "market value,"
  and licences of occupation are typically rented at 4.5% of BC
  Assessment's actual/appraised land value — but the document is a policy
  statement, not a published price schedule, so it doesn't yield a
  reusable $/hectare figure either.
- **A real precedent exists but is not a clean per-hectare price:** in
  2023, five Treaty 8 First Nations settled Treaty Land Entitlement claims
  for **$800 million in cash plus 44,266 hectares of Crown land**
  (BC government news release,
  https://news.gov.bc.ca/releases/2023IRR0019-000539; CBC,
  https://www.cbc.ca/news/canada/british-columbia/treaty-land-entitlement-claims-bc-canada-treaty-8-nations-april-2023-1.6812180).
  Dividing naively gives ~$18,070/ha (~$7,300/acre), but **this should not
  be published as a land-value benchmark** — the $800M compensates for
  decades of treaty-entitlement shortfall generally, not purely for the
  land's market value, so the ratio conflates two different things. It's
  useful only as directional context that a real BC treaty settlement
  land-plus-cash package, at this scale, lands in the same order of
  magnitude ($10–20K/ha-equivalent) as the farmland-value estimate — which
  is a mild, indirect corroboration that $3.5B is not an absurd
  order-of-magnitude for land+compensation at this scale, without
  standing in as its own precise benchmark.

**Recommendation for the report:**
1. Use the corrected **$10,577/acre (StatCan, 2025)** → **~$3.5 billion**
   framing, explicitly cited to StatCan Table 32-10-0047-01, not FCC (FCc
   doesn't publish this number).
2. Keep — and arguably strengthen — the original poster's own caveat that
   this is illustrative scale, not an appraisal. Add the specific reason
   why: farmland value is a poor proxy because the committed land is
   mostly non-agricultural (forested/rural Crown land) and farmland
   values themselves vary >40x by BC region.
3. If time allows before publication, chase the BC Assessment Managed
   Forest Land Schedule B rates (flagged above as unverified) as a
   second, more defensible per-hectare figure for forested Crown land
   specifically, and present both figures side by side rather than
   leaning on the farmland number alone.
4. Do not use the Treaty 8 $800M/44,266ha ratio as a stated benchmark —
   it's structurally a compensation package, not a land price, and
   presenting it as $/hectare would be more misleading than the
   farmland-value comparison it would be trying to improve on.

---

## Items flagged as unverified / needing follow-up before publication

- Golden Ears Provincial Park's official area (BC Parks' own page states
  no figure; secondary sources disagree, 55,590 ha vs. ~62,000+ ha).
- Manning Park's current official area depends on reference date (70,844
  ha in 1999 vs. ~83,671 ha post-2012 amalgamation) — confirm which
  boundary BC Parks currently uses for its public-facing figure.
- BC Assessment's Managed Forest Land Schedule B per-hectare bare-land
  values (BC Reg. 90/2000, Sched. B) — table did not extract from the
  BC Laws page in this session; needs a direct PDF/primary-source pull.
- Metro Vancouver's StatCan 2021 Census Profile page 404'd directly in
  this session; the 2,878.93 km² and 115.18 km² (City of Vancouver)
  figures were corroborated via Wikipedia's citation of the same StatCan
  table rather than a first-party StatCan page render — re-pull the live
  StatCan Census Profile URL before publication for a first-party
  citation/screenshot.
