# Research: Songhees Nation Victoria-area treaty land map

Research log supporting Chapter 2 ("Victoria/South Island case study") of the
treaty land report. Confidence-labeled: **CONFIRMED** (multiple independent
sources or primary document), **LIKELY** (strong circumstantial evidence,
not independently verified against the primary artifact), **UNKNOWN**
(could not establish).

## 1. Source of the map (`lake/bc_treaty_land/songhees-victoria-map.jpeg`)

**CONFIRMED** — visually verified, not just inferred. The map is page 6 of
the official **"TTA Treaty Area and Treaty Lands" map package**, published
by the BC Ministry of Indigenous Relations and Reconciliation via the
govTogetherBC engagement site for the Te'mexw Treaty Negotiations, dated
**June 2026**:

- Landing page: https://engage.gov.bc.ca/govtogetherbc/engagement/temexw-treaty-negotiations/
- Direct PDF: https://engage.gov.bc.ca/app/uploads/sites/121/2026/06/TTA-Treaty-Area-and-Treaty-Lands_June-2026.pdf
  (5.4MB, 7 pages, hosted on gov.bc.ca)
- **PDF metadata confirms the publisher**: `pdfinfo` on the downloaded file
  shows `Title: PRINT25May2026_Ministry of Indigenous Relations and
  Reconciliation_AboutTTA36x48`, `Creator: Adobe Illustrator 30.3
  (Macintosh)`, `CreationDate: Wed Jun 10 08:06:39 2026 PDT` — a
  print-production file for a 36x48" poster series, created by the
  Ministry of Indigenous Relations and Reconciliation on June 10, 2026.
- **Rendered and visually compared page-by-page** (`pdftoppm -png -r 100`
  against each of the 7 pages): the document is a 7-page set — page 1
  (TTA overview/territories), page 2 (T'Sou-ke Nation), page 3 (Malahat
  Nation), page 4 (Snaw-naw-as First Nation), page 5 (Beecher Bay/SC'IȺNEW̱
  First Nation), **page 6 (Songhees Nation)**, page 7 ("Pre-Approved
  Additions" — a separate category, see note below). **Page 6 is a
  pixel-for-pixel structural match to `songhees-victoria-map.jpeg`**: same
  title "Songhees Nation — Proposed Treaty Lands," same five-panel layout
  (Overview / Colwood inset / Esquimalt inset / Victoria inset / Tl'ches
  inset), same legend with the same five categories and colours
  (Provincial Crown Land = yellow, Provincial Park Land = yellow hatch,
  Federal Crown Land = red, Songhees Nation Private Land = blue, Songhees
  Nation Reserve = purple), and the same labelled parcels in the same
  positions: Hatley Park (red, Colwood inset), New Songhees 1A (purple,
  Esquimalt inset), Esquimalt 113 (yellow, Esquimalt inset), Enterprise
  Wharf and Q Lot (yellow, Victoria inset), PCC Pandora (blue, Victoria
  inset), Tl'ches – Chatham Islands 4 and Tl'ches – Discovery Island 3
  (purple, Tl'ches inset), Tl'ches – Discovery Island Park (yellow hatch,
  Tl'ches inset). This is the primary source document for the map image in
  this repo.
- **Important additional context found on page 7 of the same PDF**
  ("Pre-Approved Additions"): a separate category of parcels — including a
  Songhees-specific set (Colwood/Esquimalt inset) — that the document
  explicitly states are **not** part of the treaty. Page 7's own text:
  *"To be clear, these parcels do not become Treaty Lands when the
  Te'mexw Treaties come into effect... Pre-approved additions are parcels
  of land identified by the First Nation that the First Nation is
  interested in the possibility of purchasing on a willing-buyer,
  willing-seller basis in the future."* None of the parcels shown in
  `songhees-victoria-map.jpeg` (page 6) are pre-approved additions — all
  are on the "Proposed Treaty Lands" page — but this distinction is worth
  keeping in the report in case other social-media claims about this
  document conflate the two categories.

**CONFIRMED**: this map (or the underlying document set) is what triggered
a wave of news coverage on **August 9–12, 2026**, timed to the BC Public
Accounts 2025/26 release, including:

- Rob Shaw / CHEK News, "Hatley Castle, Victoria waterfront lands among
  properties proposed for First Nations treaty" (Aug 9, 2026):
  https://cheknews.ca/hatley-castle-victoria-waterfront-lands-among-properties-proposed-for-first-nations-treaty-1341048/
  — explicitly states the map source is the Ministry of Indigenous
  Relations and Reconciliation, and that it shows ~30 Crown land parcels
  proposed for transfer, including Hatley Castle/Royal Roads, the Q Lot
  parking lot at 430 Menzies St. beside the Legislature, the Enterprise
  Wharf parking lot at 1112 Wharf St., Discovery Island Marine Provincial
  Park, and Sooke Mountain Provincial Park (T'Sou-ke).
- Business Examiner, "Royal Roads, Victoria Waterfront Among Crown Lands
  Proposed for Transfer Under Te'mexw Treaty":
  https://businessexaminer.ca/vancouver-island-articles/item/royal-roads-victoria-waterfront-among-crown-lands-proposed/
  (fetch blocked by 403 during this research; title and search-snippet
  content corroborate the CHEK story — same ~30-parcel figure).
- The Epoch Times, "Newly Revealed BC First Nations Land Transfers Amount
  to More Than 135,000 Hectares" (Aug 11–12, 2026):
  https://www.theepochtimes.com/world/newly-revealed-bc-ndp-first-nations-land-transfers-amount-to-nearly-135000-hectares-6073480
  — **this is the closest match to the original tweet's framing**, and
  explicitly cites *two separate documents* as its sources: the **BC
  Public Accounts 2025-26** (the 135,000 ha aggregate) and the **TTA
  Treaty Area and Treaty Lands (June 2026)** map (the Hatley
  Castle/Victoria parcel detail). This is direct confirmation that the
  original social-media thread conflated two distinct documents with two
  different scopes — see §2 below.
- Times Colonist, "City backs Songhees in Victoria land claims; properties
  include two parking lots":
  https://www.timescolonist.com/local-news/city-backs-songhees-in-victoria-land-claims-properties-include-two-parking-lots-5153558
  — identifies the Q Lot (430 Menzies St., assessed value $24.8M) and
  Enterprise Wharf (1112 Wharf St., adjacent to Ship Point) by street
  address.

No evidence found that the map originated from Songhees Nation or Te'mexw
Treaty Association directly (i.e., it is not a Nation-produced consultation
document) — it is a **provincial government** treaty-negotiation map,
picked up and re-illustrated by news outlets.

## 2. Reconciling the map against the Note 28 hectare figure

This is the central accuracy question. Two different figures, two different
scopes, and they should NOT be treated as interchangeable:

| Figure | Value | Source | Scope |
|---|---|---|---|
| Public Accounts 2025/26, Note 28 | **1,916.7 ha** | BC Public Accounts, "current commitments of provincial Crown land" | **Provincial** Crown land only, ALL FIVE Te'mexw Nations combined (Malahat, Scia'new, Snaw-naw-as, Songhees, T'Sou-ke), across their entire settlement areas (South Island-wide, not just Victoria) |
| 2015 Agreement-in-Principle land package | **~1,565 ha** | Canada.ca / Newswire backgrounder on the April 2015 Te'mexw AIP: https://www.canada.ca/en/news/archive/2015/04/backgrounder-agreement-principle-between-te-mexw-treaty-association-canada-british-columbia.html and https://www.newswire.ca/news-releases/five-temexw-member-first-nations-canada-and-british-columbia-sign-an-agreement-in-principle-towards-final-treaties-on-vancouver-island-517432931.html | Stated as "approximately 1,565 hectares of Crown lands, **not including existing Indian Reserves**" — the AIP-stage estimate, ~10 years older than Note 28, and it is **not clearly specified in available sources whether it includes federal as well as provincial Crown land** |

**LIKELY**: the ~1,916.7 ha (2025/26) vs. ~1,565 ha (2015 AIP) gap reflects
growth/refinement of the settlement-land package between the 2015
Agreement-in-Principle and Stage 5 finalization, not two measures of the
same thing at the same time — but the exact reconciliation (what grew,
which parcels were added or resized) was **not found** in any public
document during this research and should be flagged as **UNKNOWN** rather
than asserted. Do not present 1,916.7 ha and 1,565 ha as confirming or
contradicting each other in the report — present them side by side with
their distinct sourcing and dates.

**CONFIRMED, the most important finding for accuracy**: neither the 1,565
ha nor the 1,916.7 ha provincial figures can be assumed to include Hatley
Park, because Hatley Park is **federal** land (Department of National
Defence), and Note 28 explicitly and only covers *provincial* Crown land
commitments. See §3.

### Parcel-by-parcel classification (from the map legend + corroborating sources)

| Parcel (map label) | Map legend colour | Status | Is it part of Note 28's 1,916.7 ha provincial figure? |
|---|---|---|---|
| Hatley Park / Hatley Castle (Colwood inset) | Red = Federal Crown Land | **Existing federal Crown land** (Department of National Defence), proposed for transfer to Songhees as treaty settlement land | **NO** — federal land is outside Note 28's scope entirely |
| New Songhees 1A (Esquimalt inset) | Purple = Songhees Nation Reserve | **Already** an existing federal Indian Reserve, established 1911 when Songhees relocated from the Inner Harbour (Songhees Point) reserve; not new land of any kind | **NO** — already-held reserve land, not a new commitment, and not provincial in origin (reserves are federal under the Indian Act) |
| Esquimalt 113 | Yellow = Provincial Crown Land | New provincial Crown land parcel, small, near Lampson St. | **YES** — this is the kind of parcel Note 28's provincial figure is counting |
| Enterprise Wharf (Victoria inset) | Yellow = Provincial Crown Land | New provincial Crown land parcel; waterfront parking/dock at 1112 Wharf St. | **YES** |
| Q Lot (Victoria inset) | Yellow = Provincial Crown Land | New provincial Crown land parcel; parking lot at 430 Menzies St. beside the Legislature, assessed at $24.8M (Times Colonist) | **YES** |
| PCC Pandora (Victoria inset) | Blue = Songhees Nation Private Land | Already privately owned by Songhees Nation (fee simple), not Crown land at all | **NO** — not Crown land, not a treaty commitment |
| Tl'ches — Chatham Islands 4 | Purple = Songhees Nation Reserve | **Already** Chatham Islands Indian Reserve No. 4, already under Songhees control | **NO** — already-held reserve |
| Tl'ches — Discovery Island 3 | Purple = Songhees Nation Reserve | **Likely already** an existing Indian Reserve (IR 3) — a Wikipedia source referencing Songhees rights over "IR 3 & IR 4 foreshore" is consistent with this but was not cross-checked against a federal reserve registry | **NO** (pending final confirmation of IR 3 status) |
| Tl'ches — Discovery Island Park (hatched) | Yellow hatch = Provincial Park Land | **New** — Discovery Island Marine Provincial Park is one of two actual provincial parks named across news coverage as proposed for transfer (the other being Sooke Mountain Provincial Park, for T'Sou-ke, not shown in this map) | **YES**, but as *park* land, a distinct sub-category from the plain "Provincial Crown Land" yellow parcels |

**Bottom line for the report**: of everything visually prominent in this
four-panel map, only a handful of small yellow parcels (Esquimalt 113,
Enterprise Wharf, Q Lot) plus a strip of Discovery Island Marine Provincial
Park are actual *new provincial Crown land* commitments of the kind Note 28
is counting. Hatley Park (the single largest, most visually dramatic
parcel in the map, roughly 229–260 ha on its own — see §3) is federal land
outside Note 28's scope. New Songhees 1A and the Chatham/Discovery Island
reserve lands are land the Songhees Nation **already holds** today, not
incremental transfers. The 1,916.7 ha Note 28 figure for the *whole
five-Nation Te'mexw table* is almost certainly driven mostly by Crown
parcels elsewhere in the settlement areas (Malahat, Scia'new/Beecher Bay,
Snaw-naw-as/Nanoose, T'Sou-ke lands, and Sooke Mountain Provincial Park),
not by the small, visually striking Victoria-downtown yellow parcels shown
in this specific map. This could not be fully quantified (no source gives a
per-Nation or per-parcel hectare breakdown within the Te'mexw table), so
the report should describe this directionally and cite the absence of a
public breakdown rather than assert an exact split.

**Corroborating this directional read**: having now viewed all five
per-Nation maps in the same government PDF (§1), the pattern holds across
the whole Te'mexw table, not just Songhees. Each of the other four Nations'
maps (T'Sou-ke, Malahat, Snaw-naw-as, Beecher Bay/Sc'ianew) shows the same
structure — a scatter of many small, mostly rural yellow "Provincial Crown
Land" polygons (roadside lots, forest parcels, small waterfront pieces
near Sooke, Shawnigan Lake, Mill Bay, Parksville/Errington, Nanoose, and
East Sooke/Metchosin) plus a few purple existing-reserve polygons and a
handful of red federal parcels (e.g., a federal transmitter site
label led as "Nanoose Transmitter Site" on the Snaw-naw-as map; "Mary Hill
1" and other DND-adjacent land on the Beecher Bay map). None of the other
four Nations' maps contains anything close to the size or visual prominence
of Hatley Park. This supports treating the Songhees map's Victoria-area
yellow parcels as a small slice of a territory-wide, mostly rural 1,916.7
ha total — the Victoria parcels are unusual mainly for their downtown
visibility and assessed dollar value (e.g., the Q Lot's $24.8M assessment),
not their acreage.

## 3. Hatley Castle / Royal Roads: ownership and treaty status

**CONFIRMED**: Hatley Park/Hatley Castle is federal land.
- Owned by the **Department of National Defence** (Government of Canada).
  Confirmed independently by:
  - CHEK News (Aug 9, 2026): "Hatley Castle grounds at Royal Roads are
    federally owned." https://cheknews.ca/hatley-castle-victoria-waterfront-lands-among-properties-proposed-for-first-nations-treaty-1341048/
  - Times Colonist, "Esquimalt Nation suit opposes transfer of Hatley Park
    to Songhees": "The Department of National Defence owns Hatley Park,
    which is home to Royal Roads University."
    https://www.timescolonist.com/local-news/esquimalt-nation-lawsuit-opposes-transfer-of-hatley-park-to-songhees-12114021
  - Victoria News, "Esquimalt Nation files claim to halt designation of
    Hatley Park as Songhees land" (Apr 8, 2026):
    https://vicnews.com/2026/04/08/esquimalt-nation-files-claim-to-halt-designation-of-hatley-park-as-songhees-land/
- Also designated **Hatley Park National Historic Site of Canada**, under
  Parks Canada heritage designation (a designation, not a change of legal
  owner): https://www.pc.gc.ca/apps/dfhd/page_nhs_eng.aspx?id=868
- The Royal Roads University campus that operates on the site is a
  separate institution (a public BC university) that occupies the land;
  university-owned buildings/operations are distinct from underlying land
  title, which remains with DND.
- Size: the National Historic Site is **228.84 ha** (Parks Canada); other
  sources describe the broader campus as up to ~260 ha (565 acres). Either
  figure makes it larger than the combined small yellow provincial parcels
  in the map.
- History: built early 1900s as the residence of former BC premier James
  Dunsmuir; purchased by the federal government in 1940; Royal Roads
  Military College 1942–1995; Royal Roads University since 1995 (Epoch
  Times article, citing public record).

**CONFIRMED**: Hatley Park is a live, named component of the actual Te'mexw
treaty negotiation (Songhees table specifically) — it is not merely shown
in the map "for geographic context." Multiple 2026 sources state it has
been proposed, as part of the ongoing Stage 5 negotiations, for transfer
from Canada to Songhees Nation as treaty settlement land:
- CHEK News (Apr 2026), "Songhees says Esquimalt Nation's civil claim for
  Hatley Park 'does not alter' long negotiated treaty":
  https://cheknews.ca/songhees-says-esquimalt-nations-civil-claim-for-hatley-park-does-not-alter-long-negotiated-treaty-1318024/
- Goldstream Gazette / Oak Bay News (Apr 10, 2026), "Songhees 'confident'
  in Colwood land transfer despite Nation's injunction":
  https://goldstreamgazette.com/2026/04/10/songhees-confident-in-colwood-land-transfer-despite-nations-injunction/
  — Songhees Chief Ron Sam and legal counsel Robert Janes are quoted
  expecting Canada to proceed with the Hatley Park transfer once Songhees
  members ratify the treaty; Songhees says it "is not a party to" the
  Esquimalt claim and does not expect it to delay the transfer.
- Royal Roads University itself has publicly stated (per the Epoch Times
  summary) that it "will continue to hold classes at Hatley Park, but the
  size and layout of the campus may change" — consistent with an active,
  not hypothetical, transfer proposal.

**However — an active legal dispute complicates the transfer, and this
should be reported as unresolved, not settled:**
- **Esquimalt Nation** (a distinct First Nation from Songhees — both are
  successor communities of the Lekwungen people, split into separate
  Indian Act bands in the late 1800s) filed a **civil claim on March 27,
  2026** seeking a permanent injunction against designating Hatley Park as
  Songhees treaty land, and asking the federal government to recognize
  Esquimalt's own Aboriginal title over all or part of Hatley Park.
  Esquimalt argues the transfer to Songhees would leave it "few to no
  opportunities to re-acquire land" in its own territory given the
  scarcity of available Crown land in the area.
  https://vicnews.com/2026/04/08/esquimalt-nation-files-claim-to-halt-designation-of-hatley-park-as-songhees-land/
  https://www.timescolonist.com/local-news/esquimalt-nation-lawsuit-opposes-transfer-of-hatley-park-to-songhees-12114021
- Canada had 21 days from the March 27, 2026 filing to respond to the
  civil claim (per Victoria News); the outcome of that response/litigation
  was not found in sources retrieved during this research and should be
  treated as **UNKNOWN / ongoing** as of this writing (Aug 12, 2026).

**Conclusion on Hatley Castle**: the map is not showing Hatley Park merely
as adjacent geographic context — it is depicted as, and independently
confirmed by multiple 2026 news sources to be, an actual proposed
treaty-settlement parcel for Songhees Nation. But because it is **federal**
land, it sits entirely outside the BC Public Accounts Note 28 "provincial
Crown land" figure. The original tweet's framing — citing Hatley Castle
under the umbrella of the provincial 135,425 ha Public Accounts commitment
— **conflates two different documents/scopes**: the provincial accounting
disclosure (Note 28) and the separate federal-plus-provincial TTA treaty
land map. The report should make this distinction explicit rather than
imply Hatley Castle is counted in the 135,425 ha or 1,916.7 ha totals.

## 4. Te'mexw Treaty Association negotiation status

**CONFIRMED**:
- Statement of Intent to negotiate filed: **July 15, 1994** (per BC Treaty
  Commission: https://bctreaty.ca/temexw-treaty-association/).
- Currently in **Stage 5 of the BC Treaty Commission's 6-stage process**
  ("Negotiation to Finalize a Treaty") — confirmed independently by
  bctreaty.ca, the govTogetherBC engagement page, and multiple 2026 news
  articles (Victoria News, Times Colonist, Goldstream Gazette).
- **Agreement-in-Principle (Stage 4)** initialled April 9, 2015, signed
  April 10, 2015 — a joint announcement by the five Te'mexw member Nations,
  Canada, and BC:
  https://www.newswire.ca/news-releases/five-temexw-member-first-nations-canada-and-british-columbia-sign-an-agreement-in-principle-towards-final-treaties-on-vancouver-island-517432931.html
  https://www.canada.ca/en/news/archive/2015/04/backgrounder-agreement-principle-between-te-mexw-treaty-association-canada-british-columbia.html
- The province is negotiating **five separate, Nation-specific treaties**
  under the TTA umbrella (not one combined treaty) — each of the five
  member Nations (Malahat, Scia'new/Beecher Bay, Snaw-naw-as, Songhees,
  T'Sou-ke) will have its own final treaty text and its own membership
  ratification vote.
- **Public engagement**: a "What We Heard" report was published following
  2023–2024 public engagement (news release May 9, 2024:
  https://news.gov.bc.ca/releases/2024IRR0023-000708); a further round of
  public open houses ran **June 2026** (the same month the TTA treaty land
  map PDF referenced above was dated/uploaded), described as intended "to
  share information on the work underway and support public awareness,
  understanding and constructive community dialogue" ahead of finalization.
  https://engage.gov.bc.ca/govtogetherbc/engagement/temexw-treaty-negotiations/
- **Next steps after Stage 5 negotiations conclude**: each Te'mexw member
  Nation's citizens vote to ratify their treaty; BC and Canada must also
  approve; only then does the treaty come into effect (Stage 6:
  Implementation).
- As of **April 2026**, Songhees Nation was still awaiting its own
  membership vote to formally approve the treaty, after which Canada is
  expected to proceed with the Hatley Park transfer specifically (per the
  Goldstream Gazette Apr 10, 2026 reporting).

**Timeline summary**: 1994 (SOI filed) → 2015 (AIP, Stage 4) → 2023–2024
(public engagement, "What We Heard" report) → 2026 (further public
engagement in June; Esquimalt Nation legal challenge filed March 27, 2026;
Public Accounts 2025/26 disclosure and news coverage in August 2026) →
Stage 5 negotiations ongoing, not yet finalized as of this writing.

## 5. Open items / recommended before publication

1. Business Examiner's article returned HTTP 403 on fetch; if it's wanted
   as a citation, access it another way (cache, alternate reader) to quote
   it directly rather than relying on search snippets.
2. No source found that gives a per-Nation hectare breakdown *within* the
   1,916.7 ha Te'mexw Note 28 total — if this is needed for the chapter,
   it may require a direct records request or a closer read of the AIP/
   Final Agreement schedules (not located in this research pass). The
   qualitative cross-check in §2 (all five per-Nation maps show the same
   many-small-rural-parcels pattern) supports the directional claim without
   supplying an exact number.
3. Confirm Discovery Island IR 3 status against a federal reserve registry
   (e.g., ISC / CIRNAC reserve lookup) rather than the single Wikipedia
   inference used here.
4. Track the outcome of the Esquimalt Nation civil claim (filed Mar 27,
   2026) before Chapter 2 is finalized — if it changes Hatley Park's status
   before publication, that must be reflected.
5. If the report wants to reproduce or crop the map image, prefer
   re-rendering page 6 of the official PDF at higher resolution over the
   `lake/bc_treaty_land/songhees-victoria-map.jpeg` copy, since the
   original source (with full metadata/provenance) is now in hand — a
   local render is saved at
   `/tmp/claude-1000/-home-idiom-workspace-canada-canada-central-plots/64ce8464-8010-47d4-b05f-d98cb110258f/scratchpad/tta_page-6.png`
   (session scratchpad — regenerate from the source PDF for the final
   pipeline rather than depending on this ephemeral path).

## Full source list

- https://cheknews.ca/hatley-castle-victoria-waterfront-lands-among-properties-proposed-for-first-nations-treaty-1341048/
- https://businessexaminer.ca/vancouver-island-articles/item/royal-roads-victoria-waterfront-among-crown-lands-proposed/ (403 on fetch; snippet-only)
- https://www.theepochtimes.com/world/newly-revealed-bc-ndp-first-nations-land-transfers-amount-to-nearly-135000-hectares-6073480
- https://www.timescolonist.com/local-news/city-backs-songhees-in-victoria-land-claims-properties-include-two-parking-lots-5153558
- https://www.timescolonist.com/local-news/esquimalt-nation-lawsuit-opposes-transfer-of-hatley-park-to-songhees-12114021
- https://vicnews.com/2026/04/08/esquimalt-nation-files-claim-to-halt-designation-of-hatley-park-as-songhees-land/
- https://cheknews.ca/songhees-says-esquimalt-nations-civil-claim-for-hatley-park-does-not-alter-long-negotiated-treaty-1318024/
- https://goldstreamgazette.com/2026/04/10/songhees-confident-in-colwood-land-transfer-despite-nations-injunction/
- https://engage.gov.bc.ca/govtogetherbc/engagement/temexw-treaty-negotiations/
- https://engage.gov.bc.ca/app/uploads/sites/121/2026/06/TTA-Treaty-Area-and-Treaty-Lands_June-2026.pdf
- https://bctreaty.ca/temexw-treaty-association/
- https://bctreaty.ca/wp-content/uploads/2016/09/Temexw_AIP.pdf
- https://news.gov.bc.ca/releases/2024IRR0023-000708
- https://www.canada.ca/en/news/archive/2015/04/backgrounder-agreement-principle-between-te-mexw-treaty-association-canada-british-columbia.html
- https://www.newswire.ca/news-releases/five-temexw-member-first-nations-canada-and-british-columbia-sign-an-agreement-in-principle-towards-final-treaties-on-vancouver-island-517432931.html
- https://www.pc.gc.ca/apps/dfhd/page_nhs_eng.aspx?id=868 (Hatley Park National Historic Site, Parks Canada)
- https://en.wikipedia.org/wiki/Chatham_Islands_(British_Columbia)
- https://en.wikipedia.org/wiki/Te%27mexw_Treaty_Association
- https://en.wikipedia.org/wiki/Songhees_First_Nation
- https://hallmarkheritagesociety.ca/archives/history-articles/the-negotiations-to-relocate-the-songhees-1843-1911/
- https://www.esquimalt.ca/sites/default/files/docs/municipal-hall/temexw_treaty_tac_fact_sheet.pdf (fetch failed — binary/unreadable; re-attempt with a PDF text tool if needed)
