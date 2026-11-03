# Primary Source Research — BC Crown Land Treaty Commitments (Note 28)

Research pass against the claims in `docs/kb-bc-treaty-land.md`, section 1c/1a.
All primary-source PDFs were downloaded directly and parsed with `pdftotext`
(not just AI-summarized) so the figures below are verified against actual
document text, not screenshots or search-engine summaries. Access date for
all sources: **2026-08-12**.

**Important methodology note:** two BC-government PDFs in this note were
served encrypted (owner-password-protected against copying) but `pdftotext`
extracted full readable text regardless — the permission flag does not block
extraction. Where WebFetch's built-in summarizer choked on a binary/encrypted
PDF and returned nothing or (in one case, Nisga'a) an apparently
**hallucinated figure**, I re-fetched the raw PDF and ran `pdftotext -layout`
on it myself and quote only that ground-truth text below. This is flagged
explicitly at the one point it mattered (Nisga'a land area).

---

## (a) Verified / corrected transcription — 2025/26 Note 28

**Source:** *Public Accounts 2025/26* (Province of British Columbia, Ministry
of Finance — Office of the Comptroller General), page 82, Note 28
"Contingent Liabilities and Contractual Obligations — Continued."

- Direct PDF: https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/public-accounts-2025-26.pdf
- Document metadata: Title "Public Accounts 2025/26", Author "Ministry of
  Finance - Office of the Comptroller General", CreationDate 2026-07-14,
  ModDate 2026-08-05.
- **Official release date: August 10, 2026**, per BC government news release
  2026FIN0029-000934 ("Year-end results show commitment to reducing costs" —
  Minister of Finance Brenda Bailey): https://news.gov.bc.ca/releases/2026FIN0029-000934
- Public Accounts index page (all component documents):
  https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts

**Verbatim text, page 82, Note 28** (extracted directly from the PDF, footer
page numbers confirmed at "82 … PUBLIC ACCOUNTS 2025/26" immediately above
this passage):

> It is expected the capital transfer components for all treaty agreements
> will be, in most cases, entirely provided by Canada. The current
> commitments of provincial Crown land for all Final Agreement and
> Incremental Treaty Agreement tables are as follows:

| First Nation / Table | Hectares (verified) | Screenshot (KB 1c) | Match? |
|---|---|---|---|
| Ditidaht | 3,567 | 3,567 | ✅ |
| Homalco | 707 | 707 | ✅ |
| In-SHUCK-ch (Skatin and Samahquam) | 9,474 | 9,474 | ✅ |
| Kaska Dena Council | 677 | 677 | ✅ |
| Kitselas | 35,290 | 35,290 | ✅ |
| Kitsumkalum | 45,789 | 45,789 | ✅ |
| K'omoks | 3,040 | 3,040 | ✅ |
| Ktunaxa Nation Council | 418 | 418 | ✅ |
| Lake Babine Nation (BC only) | 497.6 (+ one-time $0.02M) | 497.6 | ✅ |
| Lax Kw'alaams First Nation | 4,309 | 4,309 | ✅ |
| Lheidli T'enneh | 3,416 | 3,416 | ✅ |
| Nazko | 172 | 172 | ✅ |
| NStQ (Canoe Creek, Sugar Cane, Canim Lake, Soda Creek) | 3,095 | 3,095 | ✅ |
| Pacheedaht | 1,216 | 1,216 | ✅ |
| Te'mexw (Malahat, Scia'new, Snaw-naw-as, Songhees, T'Sou-ke) | 1,916.7 | 1,916.7 | ✅ |
| Tla-o-qui-aht | 47 | 47 | ✅ |
| Wei Wai Kai (Cape Mudge First Nation) | 612 | 612 | ✅ |
| Wei Wai Kum (Campbell River First Nation) | 1,276 | 1,276 | ✅ |
| Wuikinuxv | 13,946 | 13,946 | ✅ |
| Yekooche | 5,960 | 5,960 | ✅ |
| **Sum** | **135,425.3 ha** | 135,425 ha (tweet) | ✅ (matches to rounding) |

**Verdict: the screenshot's transcription is accurate, word for word,
against the official PDF.** No fabrication or misquotation found.

**However — one material omission the tweet does NOT correct for:** in the
same Note 28, immediately before this table, the note separately discloses:

> A Final Agreement with Yale First Nation was ratified by Yale First Nation
> in March 2011, by the provincial government on June 2, 2011, and by the
> Parliament of Canada on June 19, 2013. A treaty effective date has not yet
> been agreed to by the parties. Through the treaty, the Province will
> provide Yale with a capital transfer of $2.5 million, economic development
> funding of $1.1 million and **1,179 hectares of provincial Crown lands**.

Yale is **not** one of the 20 nations in the table and its 1,179 ha is not
included in the 135,425 ha sum — but it is unambiguously also a "current",
not-yet-transferred provincial Crown land commitment disclosed in the same
note. Fully inclusive of Yale, the Note 28 total is **~136,604.3 ha
(~337,564 acres)**, about 0.9% higher than the headline 135,425 ha figure.
This is a modest understatement in the tweet, not an overstatement — worth
noting in the report as "the number most commonly cited is actually a
slight undercount of the note's full disclosure."

**Unresolved discrepancy (flagged, not resolved):** the official 2010
gov.bc.ca Yale Lands fact sheet (see section (c) below) states Yale First
Nation Land totals **1,966 ha** (217 ha former reserve + 1,749 ha additional
Crown land in fee simple) — not 1,179 ha. This exact "1,179 hectares of
provincial Crown lands" wording is *unchanged, word-for-word, in every
Public Accounts year from 2021/22 through 2025/26* (see trend table below),
so it isn't a typo introduced this year — it appears to be a figure BC
Finance has carried for years that does not match BC's own treaty-office
land fact sheet. I could not reconcile this within scope (possible
explanations: the 1,179 ha may reflect only the Crown-land portion net of
some already-transferred or ALR-excluded parcel, or the fact sheet may
itself be stale from 2010 negotiations later revised — but this is
speculation). **Recommend the report either use Note 28's own figure with a
footnote, or flag this as an open question rather than assert either number
as definitive.**

---

## (b) Year-over-year trend, FY2021/22 – FY2025/26

All five fiscal years' Public Accounts were downloaded and parsed directly
(same Note 28 location, "28. Contingent Liabilities and Contractual
Obligations" in each). Note number is **consistently Note 28** across all
five years checked.

| Fiscal Year | Note 28 table total (ha) | # Nations/tables listed | Yale (separate, ha) | First Nations in active/completed negotiations (as of Mar 31) | Source PDF |
|---|---|---|---|---|---|
| 2021/22 | 129,397 | 18 | 1,179 | not stated in this note's text | [PDF](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2021-22/public-accounts-2021-22.pdf) |
| 2022/23 | 132,980 | 19 (+Wei Wai Kum) | 1,179 | 73 in various stages / 39 active | [PDF](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2022-23/public-accounts-2022-23.pdf) |
| 2023/24 | 138,590.6 | 20 (+Lax Kw'alaams) | 1,179 | 38, representing 69 bands | [PDF](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2023-24/public-accounts-2023-24.pdf) |
| 2024/25 | 137,591.3 | 20 | 1,179 | 37, representing 61 bands | [PDF](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/public-accounts-2024-25.pdf) |
| 2025/26 | 135,425.3 | 20 | 1,179 | 37, representing 61 bands | [PDF](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/public-accounts-2025-26.pdf) |

**Key finding — this is NOT a monotonically growing number.** It rose from
FY2021/22 to a peak in FY2023/24 (138,591 ha), then **declined for two
consecutive years** to 135,425 ha in FY2025/26 — a ~2.3% drop from peak.
This materially changes the "committed and growing" framing a reader might
assume from the tweet in isolation; the report should show the full trend
line, not just the latest snapshot.

**What's driving the shape of the curve** (documented from the raw diffs,
not the underlying transactions — flagged as observed correlation, not a
verified causal explanation, since I did not access individual Incremental
Treaty Agreement instruments):

- The table itself grew from **18 nations/tables (2021/22) to 20
  (2023/24 onward)** — Wei Wai Kum was added ~FY2022/23 (2,276 ha) and Lax
  Kw'alaams ~FY2023/24 (4,309 ha), which mechanically inflated the total
  independent of any single Nation's allotment changing.
- Several individual figures moved down between FY2023/24 and FY2025/26:
  Wei Wai Kai fell from 2,217 ha (2023/24) → 612 ha (2024/25–2025/26); NStQ
  fell from 3,656 ha → 3,095 ha (2025/26 only); Homalco fell from 822 ha
  (2021/22–2022/23) → 707 ha (2023/24 onward).
- Per the BC Treaty Commission's own "Modern Treaties" listing (see (c)
  below), **K'ómoks (ratified Mar 8, 2025), Kitselas (ratified Apr 10,
  2025) and Kitsumkalum (ratified Nov 1, 2025)** all had Final Agreements
  ratified during the FY2024/25–2025/26 window — yet they *remain* in the
  Note 28 table at essentially unchanged hectare figures (Kitselas actually
  rose slightly, from 34,839 ha in 2022/23 to 35,290 ha from 2023/24 on;
  Kitsumkalum similarly 44,661 ha → 45,789 ha). This confirms "ratified" ≠
  "in effect" in this note's accounting: land only drops off the Note 28
  table once a treaty's **effective date** is reached (as with Tsawwassen,
  Maa-nulth, Tla'amin below), not at ratification. Yale is the clearest
  illustration of this: ratified in 2011/2013, still listed as an
  uneffective commitment in 2025/26, 15 years on.
- I could **not** verify a specific causal transaction for the Wei Wai Kai
  or NStQ decreases (e.g., a partial early transfer under their Incremental
  Treaty Agreement) — flagging as something the report should not assert
  without going to those Nations' individual ITA documents.

---

## (c) BC Treaty Commission / completed-treaty cumulative totals

**Caveat up front:** bctreaty.ca itself does not appear to publish a single
consolidated "total hectares transferred to date" figure in an
easily-citable page (I checked its Modern Treaties page directly). The
figures below are compiled by me from the **individual, primary
gov.bc.ca/Canada.ca Final Agreement fact sheets and treaty-chapter text**
for each *completed and in-effect* treaty — verified by direct `pdftotext`
extraction of each PDF, not AI summarization of search snippets. This
compiled total should be understood as independently assembled, not quoted
from a single BCTC publication — flag this framing explicitly if citing "BC
Treaty Commission" as the source in the report; better to cite it as
"compiled from official Final Agreement land fact sheets."

| Treaty (First Nation) | Effective date | Settlement land area | Process | Source |
|---|---|---|---|---|
| Nisga'a Final Agreement | May 11, 2000 | **199,200 ha** (1,992 km²: 1,930 km² Crown + 62 km² former Nisga'a Indian reserves) | Negotiated directly (pre-dates the BC Treaty Commission's 6-stage process; BCTC was created in 1993, Nisga'a talks began 1976) | [Nisga'a Final Agreement, Ch. 3 "Lands," ¶2](https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/consulting-with-first-nations/agreements/chapter_03-lands.pdf) — verified via direct PDF text extraction |
| Tsawwassen First Nation | Apr 3, 2009 | **724 ha total** (662 ha "Tsawwassen Lands" with full FN law-making authority [290 ha former reserve + 372 ha former Crown] + 62 ha "Other Lands" fee-simple, remaining under Delta jurisdiction) | BCTC process (2nd Final Agreement reached) | [Tsawwassen Lands fact sheet](https://www2.gov.bc.ca/assets/gov/zzzz-to-be-moved/9efbd86da302a0712e6559bdb2c7f9dd/9efbd86da302a0712e6559bdb2c7f9dd/agreements/factsheet_final_tsawwassen_lands.pdf) |
| Maa-nulth First Nations (5 nations: Huu-ay-aht, Ka:'yu:'k't'h'/Che:k'tles7et'h', Toquaht, Uchucklesaht, Ucluelet) | Apr 1, 2011 | **~24,500 ha** (Huu-ay-aht 8,258 / Ka:'yu:'k't'h' 6,299 / Toquaht 1,489 / Uchucklesaht 3,067 / Ucluelet 5,346, + a separate 92 ha of non-treaty fee-simple federal lots for Ucluelet) | BCTC process | [Maa-nulth First Nation Lands fact sheet](https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/consulting-with-first-nations/agreements/fact_sheet_final_maanulth_lands.pdf) |
| Tla'amin Nation | Apr 5, 2016 | **8,322 ha** (1,917 ha former reserve + 6,405 ha former Crown land; ≈2.6% of Tla'amin's traditional territory per the fact sheet's own framing) | BCTC process | [Tla'amin (Sliammon) Lands fact sheet](https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/consulting-with-first-nations/agreements/fact_sheet_tlaamin_lands.pdf) |
| Yale First Nation | **Not yet effective** (ratified 2011/2013, no effective date agreed as of Aug 2026) | 1,966 ha per fact sheet / 1,179 ha per Note 28 (unresolved, see (a)) | BCTC process | [Yale Lands fact sheet](https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/consulting-with-first-nations/agreements/fact_sheet_yale_lands.pdf) |

**Cumulative land ALREADY transferred under completed, in-effect modern BC
treaties: Nisga'a + Tsawwassen + Maa-nulth + Tla'amin = 199,200 + 724 +
24,500 + 8,322 = 232,746 ha (~575,000 acres, ~2,327 km²).** (Using the
narrower "Tsawwassen Lands" 662 ha figure instead of the full 724 ha total
gives 232,684 ha — the difference is immaterial at this scale.)

**This is the crucial contrast for the report:** the 135,425 ha (or ~136,604
ha inclusive of Yale) in Note 28 is *pending, not-yet-transferred*
commitments. Land **already actually transferred and in First Nations'
hands** under completed treaties is roughly **1.7× larger** than the
pending Note 28 figure — about 232,746 ha versus 135,425 ha. A report that
presents only the Note 28 number without this comparison understates the
total scale of land that has moved (and overstates how novel/unprecedented
the pending figure is, since a larger transfer has already happened without
the controversy the tweet implies is new).

**A further, separate category not to conflate with either number above:**
in 2023, five Treaty 8 First Nations in Northeast BC reached a **Treaty
Land Entitlement (TLE)** settlement for **44,266 hectares** of Crown land —
this fulfills outstanding entitlements under the **historic 1899/1900
Treaty 8**, a completely different legal mechanism from the *modern*
BC Treaty Commission "Final Agreement / Incremental Treaty Agreement"
process that Note 28 and this whole report are about. It should not be
added into either total above, but is worth one sentence of context so a
reader doesn't later find it and think it was omitted from "the real
number." Source: [BC Gov News release 2023IRR0019-000539](https://news.gov.bc.ca/releases/2023IRR0019-000539); [Global News coverage](https://globalnews.ca/news/9627420/five-first-nations-reach-historic-800-million-44266-hectares-settlement-with-b-c-federal-government).

---

## (d) Discrepancies / corrections versus the KB's screenshot claims

1. **Transcription accuracy: CONFIRMED, no corrections needed.** All 20
   line items and the note's surrounding text match the official PDF
   word-for-word, independently re-extracted from the source document (not
   just re-reading the screenshot).
2. **Slight undercount, not overcount:** the commonly-cited 135,425 ha
   excludes Yale's separately-disclosed 1,179 ha (same note), making the
   note's full "current commitments" figure ~136,604 ha. The public
   narrative (including the Daily Hive piece covering the same document,
   published Aug 11, 2026) also uses the 20-nation total only, so this
   omission isn't unique to the tweet.
3. **Unresolved internal inconsistency:** Note 28's Yale figure (1,179 ha,
   unchanged since at least 2021/22) does not match BC's own 2010 Yale
   Lands fact sheet (1,966 ha). Flagged, not resolved — do not present
   either number in the report as settled without a caveat, or omit Yale
   detail entirely and stick to the 20-nation table if precision matters
   more than completeness.
4. **The trend is not monotonic growth.** It peaked in FY2023/24 at
   138,591 ha and has fallen ~2.3% over the two most recent fiscal years.
   Any report framing that implies ever-increasing commitments needs the
   full five-year table, not just the latest year, to be accurate.
5. **"Ratified" ≠ "land no longer committed."** K'ómoks, Kitselas and
   Kitsumkalum all had Final Agreements ratified in 2025 (per bctreaty.ca)
   but remain fully in the Note 28 table — their land doesn't leave the
   "committed" column until an effective date is reached, which can take
   years after ratification (Yale: 13+ years and counting).
6. **Note 28's own text (verbatim, unchanged across all 5 years checked)
   directly confirms the legal-distinction point in task 4**: "It is
   expected the capital transfer components for all treaty agreements will
   be, in most cases, entirely provided by Canada." The **land** is
   provincial Crown land (province's to commit); the **capital transfer
   money** is disclosed as mostly a federal (Canada) obligation. The report
   must keep these separate and not describe the $ side as a provincial
   cost.
7. **Metro Vancouver comparison — checks out.** Metro Vancouver Regional
   District land area = 2,878.93 km² (StatCan 2021 Census, cross-confirmed
   via Wikipedia's citation of the same census table). 135,425 ha =
   1,354.25 km². 1,354.25 / 2,878.93 = **47.03%** — the tweet's "~47% of
   Metro Vancouver" figure is arithmetically correct against a verifiable
   area figure.
8. **Farmland value ($10,477/acre, ~$3.5B) — NOT independently verified in
   this pass.** I located what is almost certainly the source document —
   Farm Credit Canada's *2025 Farmland Values Report* (covers Jan–Dec 2025,
   created March 2026) — and confirmed it reports BC cultivated farmland
   values **fell 1.7% in 2025** (a reversal from +11.3% in 2024), so
   directionally the report is discussing the right document. I did not
   locate the specific $10,477/acre BC average figure within the sections I
   pulled. This was not one of the four assigned research tasks and I
   flag it as **open** rather than spend further budget confirming it — the
   FCC report PDF is saved locally if a follow-up pass wants to dig further
   (Farm Credit Canada, farmcreditcanada.com / fcc-fac.ca).
9. **Hatley Castle / Songhees map (KB section 1b) — out of scope of this
   pass, still open.** Not researched here; the KB's existing open item
   about tracing that map's provenance and reconciling it against the
   1,916.7 ha Te'mexw table figure still needs to be done separately. Note
   only that Note 28 explicitly covers *provincial* Crown land — Hatley
   Castle/Royal Roads is federal land per the map's own legend, so even if
   verified, it would not appear as a line item in Note 28 regardless of
   Songhees' status as one of the five Te'mexw member nations.

---

## (e) Full source list

**Primary — BC Public Accounts (all fetched and parsed directly, 2026-08-12):**
- 2025/26: https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/public-accounts-2025-26.pdf (Note 28, p. 82)
- 2024/25: https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2024-25/public-accounts-2024-25.pdf
- 2023/24: https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2023-24/public-accounts-2023-24.pdf
- 2022/23: https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2022-23/public-accounts-2022-23.pdf
- 2021/22: https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2021-22/public-accounts-2021-22.pdf
- Public Accounts index/archive: https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts and https://www2.gov.bc.ca/gov/content/governments/finances/public-accounts/archive
- BC Gov News release announcing 2025/26 results (Aug 10, 2026): https://news.gov.bc.ca/releases/2026FIN0029-000934

**Primary — completed-treaty land fact sheets (gov.bc.ca / Final Agreement text, fetched and parsed directly):**
- Nisga'a Final Agreement, Chapter 3 "Lands": https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/consulting-with-first-nations/agreements/chapter_03-lands.pdf
- Tsawwassen Lands fact sheet: https://www2.gov.bc.ca/assets/gov/zzzz-to-be-moved/9efbd86da302a0712e6559bdb2c7f9dd/9efbd86da302a0712e6559bdb2c7f9dd/agreements/factsheet_final_tsawwassen_lands.pdf
- Maa-nulth First Nation Lands fact sheet: https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/consulting-with-first-nations/agreements/fact_sheet_final_maanulth_lands.pdf
- Tla'amin (Sliammon) Lands fact sheet: https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/consulting-with-first-nations/agreements/fact_sheet_tlaamin_lands.pdf
- Yale First Nation Lands fact sheet: https://www2.gov.bc.ca/assets/gov/environment/natural-resource-stewardship/consulting-with-first-nations/agreements/fact_sheet_yale_lands.pdf

**BC Treaty Commission:**
- Modern Treaties listing (ratification/effective dates for K'ómoks, Kitselas, Kitsumkalum, Tsawwassen, Maa-nulth, Yale, Tla'amin): https://bctreaty.ca/treaties-and-agreements/modern-treaties/
- Note: bctreaty.ca did not yield a single consolidated cumulative-hectares figure in the pages checked; the "Financial and Economic Impacts of Treaty Settlements" PwC report on bctreaty.ca (https://bctreaty.ca/wp-content/uploads/2016/09/BC-Treaty-Commission-PricewaterhouseCoopers-Report.pdf, 2016) was located but not deeply parsed in this pass — flagged as a possible further source if a BCTC-branded consolidated figure is specifically needed.

**Separate historic-treaty context (not part of Note 28 / BCTC modern-treaty totals):**
- Treaty 8 Treaty Land Entitlement, Northeast BC, 44,266 ha (2023): https://news.gov.bc.ca/releases/2023IRR0019-000539 ; https://globalnews.ca/news/9627420/five-first-nations-reach-historic-800-million-44266-hectares-settlement-with-b-c-federal-government

**Corroborating secondary coverage (same underlying document, useful for context/attribution, not used as a factual source in place of the PDF itself):**
- Daily Hive / Urbanized, Kenneth Chan, Aug 11 2026, "BC NDP government's First Nations land transfer commitments span 12 Vancouvers": https://dailyhive.com/vancouver/bc-ndp-government-first-nations-land-transfer-commitments-public-accounts
- The Epoch Times, "Newly Revealed BC First Nations Land Transfers Amount to More Than 135,000 Hectares": https://www.theepochtimes.com/world/newly-revealed-bc-ndp-first-nations-land-transfers-amount-to-nearly-135000-hectares-6073480 (found via search; not independently parsed/fetched in this pass — treat as unverified until read directly)

**Metro Vancouver comparison:**
- StatCan 2021 Census, Greater Vancouver (Census division) land area 2,878.93 km²: https://www12.statcan.gc.ca/census-recensement/2021/as-sa/fogs-spg/Page.cfm?lang=E&topic=1&dguid=2021A00035915

**Farmland value (open item, not fully verified — see (d)8):**
- Farm Credit Canada, *2025 Farmland Values Report* (covers Jan 1 – Dec 31, 2025; PDF saved locally during this research pass) — publisher site: farmcreditcanada.com / fcc-fac.ca. Exact report URL not captured; located via search result title "2025 FCC Farmland Values Report" — **re-locate and cite the canonical FCC URL before publishing the $/acre figure.**

---

## Flags for the report team, summarized

- ✅ Screenshot transcription verified accurate against the primary PDF.
- ✅ Trend data obtained for 5 fiscal years (2021/22–2025/26); non-monotonic, peaked FY2023/24.
- ✅ Cumulative "already transferred" total compiled (~232,746 ha) — larger than the pending Note 28 figure; use for contrast.
- ✅ Federal-money / provincial-land distinction confirmed verbatim, unchanged across all 5 years.
- ✅ Metro Vancouver 47% comparison verified.
- ⚠️ Yale figure (1,179 ha vs. 1,966 ha) — internal inconsistency, unresolved, needs a decision on how to present.
- ⚠️ BC Treaty Commission itself doesn't publish one clean cumulative number — the "completed treaties" total here is independently compiled from several fact sheets, cite accordingly.
- ⚠️ Farmland $/acre figure — not verified this pass, likely FCC 2025 report, needs a follow-up fetch.
- ❌ Not researched this pass (still open from the KB): Songhees/Hatley Castle map provenance; public-access-restriction precedent on existing treaty lands; First Nations/BCTC perspective context; current BC reserve-land totals.
