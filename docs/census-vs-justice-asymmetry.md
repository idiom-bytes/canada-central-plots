# The asymmetry: what Canada publishes about *people* vs. what it records about *offenders*

The core comparison. Canada is one of the most granular collectors of personal,
sensitive characteristics in the democratic world — and it **publishes** them in
aggregate, down to neighbourhood-level geography. Yet on the justice side it records
**nothing** about an offender's national origin or immigration status. The contrast is
the argument: the silence on offenders is a *choice*, not a privacy limit.

Proof copies: census side → `lake/canada_census/`; international precedent →
`lake/intl_crime_origin/` (see [international-crime-origin-sources.md](international-crime-origin-sources.md)).

---

## Side A — what the Census collects AND publishes about ordinary residents

From the **2021 Census long-form (Form 2A-L)**, asked of a 25% sample of households,
and disseminated by Statistics Canada as aggregate tables:

| Personal characteristic | Collected? | Published in aggregate? | How fine-grained |
|---|---|---|---|
| **Religion** (Q30; 200+ denominations) | ✅ | ✅ | Down to census subdivisions; crossed with visible minority & generation |
| **Ethnic or cultural origin** (hundreds of origins) | ✅ | ✅ | By geography; crossed with visible minority |
| **Visible minority / "population group"** | ✅ (derived) | ✅ | By place of birth, generation, geography |
| **Place of birth / country of origin** | ✅ | ✅ | By geography and generation |
| **Immigrant status, year of immigration, citizenship** | ✅ | ✅ | By geography |
| **Generation status** (1st/2nd/3rd+) | ✅ | ✅ | Crossed with the above |
| **Indigenous identity** | ✅ | ✅ | By community |
| **Language(s), mother tongue** | ✅ | ✅ | Neighbourhood level |
| **Income** (via tax-record linkage), **education**, **occupation** | ✅ | ✅ | By geography |

Granularity goes down to **census subdivisions and dissemination areas** (effectively
neighbourhoods), with only **small-cell rounding** for privacy. Cross-tabs combine the
most sensitive variables — e.g. *religion × visible minority × generation status ×
geography* is a single published table.

> Plainly: the government will tell you the religious composition of your neighbourhood,
> and cross it with ethnic origin and generation. That is how "personal" the published
> data already gets — by design, and uncontroversially.

## Side B — what the Justice system records about offenders

| Offender characteristic | Recorded? | Published in aggregate? |
|---|---|---|
| Offence, date, location | ✅ (UCR) | ✅ |
| Accused **age** and **sex** | ✅ (UCR) | ✅ |
| **Nationality / citizenship** | ❌ | ❌ |
| **Country of birth / origin** | ❌ | ❌ |
| **Immigration status** (citizen / PR / TFW / student / asylum claimant) | ❌ | ❌ |
| **Religion** | ❌ | ❌ |
| **Ethnic / cultural origin** | ❌ | ❌ |
| **Indigenous identity** | ⚠️ partial (corrections records it; not joined to offence-type series for this purpose) | limited |

The police-reported (UCR), courts (ICCS) and corrections systems are **never routinely
joined** to the census or to immigration landing records to report offending by origin.
The variable simply isn't carried.

---

## The two things, side by side

| | **Census (people)** | **Justice (offenders)** |
|---|---|---|
| Religion | Published, neighbourhood level | Not recorded |
| Ethnic / cultural origin | Published, hundreds of categories | Not recorded |
| Country of birth / origin | Published, by geography | Not recorded |
| Immigration status | Published, by geography | Not recorded |
| Aggregate, anonymized? | Yes | N/A — nothing to aggregate |
| Privacy mechanism | Small-cell rounding | — |

**Same country. Same statistical agency capable of both. Opposite choices.**

## Why this matters for the report
1. **The privacy objection collapses.** If publishing religion-by-neighbourhood is
   acceptable, then publishing *national, age-standardised* offender-origin rates — far
   coarser — cannot be ruled out on privacy grounds. Canada already clears a much higher
   bar of sensitivity on the census side.
2. **It's not a capability gap.** StatCan already does record-linkage (e.g. the
   Longitudinal Immigration Database links landing records to tax data). A justice ×
   immigration linkage is technically routine; it just isn't built.
3. **Peer democracies do the harder thing.** Germany, Denmark, Norway, the Netherlands
   and Sweden publish offending by origin in aggregate, with denominators and caveats
   (see the sources doc). Canada publishes the *more* sensitive census data but refuses
   the offender side.
4. **So the gap is a recording/reporting choice** — the same failure the UK's Casey
   review condemned — and it can be closed responsibly using the standard in
   [rigorous-origin-reporting-methodology.md](rigorous-origin-reporting-methodology.md).

> One-line framing for the report: *Canada will publish the religion of the family next
> door, but not the immigration status of a convicted trafficker — even in aggregate,
> even nationally. The data isn't missing because it's too personal. It's missing because
> no one chose to count it.*
