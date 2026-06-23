# Peer democracies that report crime by origin — in aggregate, as official statistics

**Purpose.** Evidence that aggregate, anonymized reporting of offenders' national
origin / immigrant background is a *normal product of national statistics agencies*
across Western democracies — not a fringe or improper practice. This is the
counterpoint to Canada's choice never to join its population-by-origin data to its
justice data (the "origin data gap").

**What to screenshot.** Open each `page` URL below and capture the table/figure that
breaks offending down by origin. A durable copy of each source is saved in
`lake/intl_crime_origin/` (see `manifest.json`), in case a page moves.

> Framing note for the report: every one of these agencies reports **rates with
> denominators** and pairs the numbers with **explicit cautions** (age/sex structure,
> socioeconomic composition, reporting effects). That is the model to emulate — see
> [rigorous-origin-reporting-methodology.md](rigorous-origin-reporting-methodology.md).
> Cite these as "this is normal and can be done responsibly," **not** as claims about
> any group.

---

## 🇩🇪 Germany — Federal Criminal Police Office (BKA)
- **Source:** *Polizeiliche Kriminalstatistik (PKS) 2024* — the annual federal police
  statistics. Suspects are tabulated by **German / non-German**, by **nationality**,
  and by **residence status**.
- **Why it's strong:** Recurring (annual since 1971), federal, official. The PKS
  introduced a population-adjusted **suspect burden rate (Tatverdächtigenbelastungszahl,
  TVBZ)** precisely so non-German suspect counts aren't read as raw counts.
- **Screenshot page (table set):**
  https://www.bka.de/DE/AktuelleInformationen/StatistikenLagebilder/PolizeilicheKriminalstatistik/PKS2024/PKSTabellen/BundTVNationalitaet/bundTVNationalitaet.html
- **Local proof copies:** `germany_pks2024_jahrbuch.pdf` (full yearbook with the
  nationality tables), `germany_bka_tv_nationalitaet_2024.html` (table page).

## 🇩🇰 Denmark — Ministry of Justice (research unit) + Statistics Denmark
- **Source:** *Kriminalitet og herkomst 2023* ("Crime and Origin 2023") — a recurring
  official report indexing convictions by **origin** (immigrants, descendants, country
  groups), **standardised for age** (the all-population average = index 100). Statistics
  Denmark's annual *Indvandrere i Danmark* carries a parallel crime chapter.
- **Why it's strong:** Government statistical product, published for years, explicitly
  age-standardised — a textbook denominator/standardisation approach.
- **Screenshot page:** open `denmark_kriminalitet_og_herkomst_2023.pdf` (the index
  tables/figures) and the DST landing: https://www.dst.dk/da/Statistik/nyheder-analyser-publ/Publikationer/VisPub?cid=47883
- **Local proof copies:** `denmark_kriminalitet_og_herkomst_2023.pdf`,
  `denmark_dst_indvandrere_2023_landing.html`.

## 🇳🇴 Norway — Statistics Norway (SSB)
- **Source:** *Crime and punishment among immigrants and the remaining Norwegian
  population* (SSB). Charge/sanction rates by **immigrant group**; varies sharply by
  origin and **attenuates after adjusting for age, sex, and residence** — some groups
  (e.g. India, China, the Philippines, Western countries) are *under*-represented.
- **Why it's strong:** National statistics office, peer-reviewed-grade methodology,
  English version available; shows both over- and under-representation, which is exactly
  what honest reporting looks like.
- **Screenshot page:** https://www.ssb.no/en/sosiale-forhold-og-kriminalitet/artikler-og-publikasjoner/crime-and-punishment-among-immigrants-and-the-remaining-norwegian-population--328011
- **Local proof copy:** `norway_ssb_dp728_crime_immigrants.pdf` (English).

## 🇳🇱 Netherlands — Statistics Netherlands (CBS)
- **Source:** CBS report on **registered crime by migration background** (and the
  recurring *Jaarrapport Integratie / Integratie en samenleven* crime chapter).
  Overrepresentation of people with a non-Western background is reported and then
  **largely explained by background characteristics** (age, socioeconomic position,
  neighbourhood).
- **Why it's strong:** National statistics office; models the "report the gap, then
  decompose it" approach — the responsible way to publish.
- **Screenshot page:** https://longreads.cbs.nl/integratie-en-samenleven-2024/criminaliteit/
- **Local proof copy:** `netherlands_cbs_criminaliteit_migratieachtergrond.pdf`.

## 🇸🇪 Sweden — Brå (National Council for Crime Prevention)
- **Source:** *Registered offending among persons with domestic and foreign background*
  (Brå **2021:9**), suspects 2007–2018 by **Swedish vs foreign background**. The gap
  **shrinks substantially but does not vanish after controlling for age, sex, education,
  and income** — the controls are reported alongside the raw figures.
- **Why it's strong:** Government agency; first such study in ~15 years; English summary;
  explicit confounder controls and table appendices.
- **Screenshot page:** https://bra.se/rapporter/arkiv/2021-08-25-misstankta-for-brott-bland-personer-med-inrikes-respektive-utrikes-bakgrund
- **Local proof copies:** `sweden_bra_2021_summary_en.pdf` (English),
  `sweden_bra_2021_main_sv.pdf` (full report, Swedish).

---

### The one-line takeaway for the report
> Germany, Denmark, Norway, the Netherlands and Sweden — all of them — publish crime
> broken down by national origin or immigrant background, in aggregate, as routine
> official statistics, each with proper denominators and stated caveats. Canada
> publishes its population by origin but never joins it to the justice side. The
> silence is a choice, not a privacy necessity.

*Acquired via `pipeline/acquire_intl_crime_origin.py`. Files: `lake/intl_crime_origin/`.*
