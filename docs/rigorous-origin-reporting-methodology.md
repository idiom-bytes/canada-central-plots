# How to report offender-origin data rigorously (and non-inflammatorily)

A working standard for the report. The point is *not* to avoid the question — peer
democracies show it can be asked responsibly (see
[international-crime-origin-sources.md](international-crime-origin-sources.md)). The
point is to ask it the way a national statistics agency would, so the numbers inform
rather than inflame, and so no individual or group is impugned.

> **North star:** measure institutions and systems, not peoples. Every figure gets a
> denominator, a caveat, and a comparator. If a number can be misread as "group X is
> criminal," it is not yet finished — decompose it until it describes a *measurable gap*
> with stated causes, not a verdict on a population.

---

## 1. Rates, never raw counts
A count ("N offenders were foreign-born") is meaningless without the population it came
from. A large group produces large counts simply by being large.
- **Always** divide by the relevant population: per 100,000 of *that* origin group.
- State the denominator explicitly and its source/year.
- Prefer an **index to a common baseline** (the all-population average = 100), as
  Denmark's *Kriminalitet og herkomst* does — it reads honestly and resists cherry-picking.

## 2. Standardise for structure (age and sex first)
Crime is overwhelmingly committed by **young men**. A group that skews young and male
will show a higher crude rate for that reason alone.
- Report **age- and sex-standardised** rates (direct standardisation to the national
  age/sex profile). This is the single most important adjustment; Germany's TVBZ,
  Denmark's age-standardised index, and SSB's adjustments all do it.
- Show crude *and* standardised side by side so readers see how much structure explains.

## 3. Decompose the gap — report what's left after controls
Origin frequently **proxies** for things that actually drive offending: age/sex,
income/poverty, education, neighbourhood, unemployment, time-since-arrival.
- Control for the obvious confounders and report the **residual** gap (Sweden's Brå and
  the Netherlands' CBS both do exactly this — the gap shrinks markedly, sometimes most
  of the way, after controls).
- Frame the result as "X of the difference is explained by composition; Y remains
  unexplained," never as an intrinsic property of the group.

## 4. Aggregate only — protect individuals
- Publish group-level aggregates; **never** identify individuals.
- **Suppress small cells** (a common rule: counts < 5 are not released, or are rounded /
  combined) to prevent re-identification and unstable rates.
- Avoid intersections so fine they single people out (e.g., one nationality × one small
  town × one offence-year).

## 5. Show heterogeneity — and under-representation
Lumping all immigrants / all "non-Western" people together hides huge variation and
reads as a smear.
- Break out by country/region group; **report the groups that are *under*-represented**
  too (Norway: India, China, the Philippines, Western countries). Reporting only the
  high end is advocacy, not statistics.

## 6. Name the data's limits out loud
- **Reporting/recording bias:** police-recorded crime reflects *what is reported and
  detected*, not all crime; victim surveys (e.g. GSS) catch what police data misses.
- **Enforcement bias:** differential policing/stop rates can inflate a group's recorded
  contact with the system independent of underlying behaviour.
- **Suspect ≠ convicted:** "suspects/charged" and "convicted" are different universes;
  say which you're using. (Germany's PKS is *suspects*; Denmark's is *convictions*.)
- **Status vs. origin:** "foreign national," "foreign-born," "immigrant background,"
  "asylum claimant," and "non-citizen" are **different categories** — never conflate them.

## 7. Correlation ≠ causation (state it, mean it)
- A higher rate associated with an origin group does **not** establish that origin
  *causes* offending. Composition and context usually carry the association.
- Avoid causal verbs ("immigration drove crime") unless you have a design that supports
  causation. Prefer "is associated with," "co-occurs with," "remains after adjusting for."

## 8. Comparators and trend, not snapshots
- Give a **time series** (is the gap widening or narrowing?). Norway's headline is that
  over-representation *fell* over 10–15 years — a snapshot would have hidden that.
- Compare like with like (same offence definitions, same years, same denominators).

## 9. Provenance and reproducibility
- Cite the **primary source** (agency, table ID, year) for every figure; link it.
- Keep the acquisition reproducible (script → data lake → published number), so any
  reader can re-derive it.

## 10. Language discipline
- Subject of every sentence = a **system, policy, or measured rate**, not a people.
- No collective blame, no ethnic descriptors as explanations, no loaded nouns.
- When a number is uncertain or contested, say so in the same breath.

---

### Checklist (paste at the top of any origin-related analysis)
- [ ] Rate with an explicit denominator (not a raw count)
- [ ] Age/sex standardised (crude shown alongside)
- [ ] Confounders controlled; residual gap reported as residual
- [ ] Aggregate only; small cells suppressed
- [ ] Heterogeneity shown, including under-represented groups
- [ ] Data limits stated (reporting bias, suspect≠convicted, status≠origin)
- [ ] Causal language avoided unless design supports it
- [ ] Trend + like-for-like comparator included
- [ ] Primary source cited and reproducible
- [ ] Subject = system/rate, never a people

### Precedent that this can be done well
Germany (BKA/PKS), Denmark (Justitsministeriet/DST), Norway (SSB), Netherlands (CBS),
Sweden (Brå) — each applies most of the above and publishes anyway. The methodology
here is reverse-engineered from what those agencies already do.
