"""Stage B-1 (triage) — deterministic keyword scoring, no model, no key.

Ranks the harvested articles (lake/immigration/raw/articles.jsonl) so we only
download full HTML for the most relevant ones. Scores each title on three axes:
  - incident : signals an actual case (charged/convicted/arrested/sentenced...)
  - topic    : on-subject (trafficking/sexual exploitation/grooming/child...)
  - status   : mentions immigration status/origin (refugee/asylum/migrant/deport)
Tags a coarse kind (incident vs policy/other) and parses the year.

Output:
  lake/immigration/clean/triage.jsonl    all articles + scores/tags/year
  lake/immigration/clean/shortlist.jsonl top-ranked subset for HTML download
Prints counts only.
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "lake", "immigration", "raw")
CLEAN = os.path.join(ROOT, "lake", "immigration", "clean")

PER_TOPIC = 50  # top N per sub-topic into the shortlist

INCIDENT = {
    "charged": 3, "convicted": 4, "guilty": 4, "sentenced": 4, "pleaded": 3,
    "arrested": 3, "jailed": 4, "prison": 2, "accused": 2, "trial": 2,
    "charges": 2, "sentencing": 3, "found guilty": 4, "facing charges": 3,
    "police": 1, "court": 1, "suspect": 2, "victim": 1,
}
TOPIC = {
    "trafficking": 4, "human trafficking": 5, "sex trafficking": 5,
    "sexual assault": 4, "sexual exploitation": 5, "rape": 4, "raped": 4,
    "grooming": 5, "luring": 4, "child": 2, "minor": 2, "underage": 3,
    "prostitution": 3, "kidnap": 4, "abduction": 4, "exploitation": 2,
    "gang": 2, "sexual offence": 4, "sex offender": 3, "pimping": 3,
}
STATUS = {
    "refugee": 3, "asylum": 3, "foreign national": 4, "permanent resident": 3,
    "temporary foreign worker": 4, "migrant": 2, "immigrant": 2, "deport": 4,
    "deportation": 4, "removal order": 4, "newcomer": 3, "international student": 3,
    "study permit": 3, "work permit": 3, "visa": 2, "citizenship": 1,
    "non-citizen": 4, "illegal": 2, "border": 1,
}


# --- Canada classification -------------------------------------------------
# Canadian news outlets (substring match on the RSS <source>).
CA_SOURCES = [
    "cbc", "ctv", "global news", "globalnews", "toronto star", "thestar",
    "national post", "globe and mail", "theglobeandmail", "citynews",
    "toronto.com", "montreal gazette", "vancouver sun", "calgary herald",
    "edmonton journal", "ottawa citizen", "winnipeg free press", "the province",
    "cp24", "narcity", "blogto", "rcinet", "radio-canada", "canadian",
    "hamilton spectator", "the record", "windsor star", "saltwire",
    "regina leader", "saskatoon", "north bay", "sudbury", "iheartradio",
    "660 news", "ckpg", "kelowna", "nanaimo", "victoria news", "now toronto",
]
# Canadian places / institutions.
CA_GEO = [
    "canada", "canadian", "toronto", "ontario", "ottawa", "quebec", "montreal",
    "vancouver", "british columbia", " b.c.", " bc ", "alberta", "calgary",
    "edmonton", "manitoba", "winnipeg", "saskatchewan", "saskatoon", "regina",
    "nova scotia", "halifax", "new brunswick", "newfoundland", "peel",
    "york region", "durham", "hamilton", "mississauga", "brampton", "surrey",
    "niagara", "windsor", "kitchener", "waterloo", "barrie", "sudbury",
    "thunder bay", "north bay", "rcmp", "opp", "cbsa", "csis", "ircc",
    "sûreté", "surete du quebec", "provincial police", "regional police",
]
# Strong foreign markers (case is clearly NOT Canadian when these dominate).
FOREIGN = [
    "india", "indian", "delhi", "mumbai", "punjab", "pakistan", "uk ",
    "u.k.", "britain", "british", "england", "telford", "rochdale",
    "rotherham", "norfolk", "manchester", "yorkshire", "australia",
    "australian", "u.s.", "united states", "florida", "california", "texas",
    "new york", "ireland", "scotland", "nigeria", "kenya", "philippines",
    "bangladesh", "smallville", "nxivm",
]
# Foreign markers we still WANT to keep, as the UK comparison baseline.
UK_BASELINE = ["telford", "rochdale", "rotherham", "grooming gang", "norfolk"]


def classify_geo(text, source):
    t = text.lower()
    s = (source or "").lower()
    ca = sum(1 for k in CA_SOURCES if k in s) * 3
    ca += sum(1 for k in CA_GEO if k in t)
    fo = sum(1 for k in FOREIGN if k in t)
    is_uk_baseline = any(k in t for k in UK_BASELINE)
    if ca > 0 and ca >= fo:
        return "canada", ca, fo
    if is_uk_baseline:
        return "uk_baseline", ca, fo
    if fo > 0:
        return "foreign", ca, fo
    return "unknown", ca, fo


def score(text, table):
    t = text.lower()
    s = 0
    hits = []
    for kw, w in table.items():
        if kw in t:
            s += w
            hits.append(kw)
    return s, hits


def year_of(date):
    m = re.search(r"\b(20[12][0-9])\b", date or "")
    return int(m.group(1)) if m else None


def main():
    os.makedirs(CLEAN, exist_ok=True)
    rows = []
    with open(os.path.join(RAW, "articles.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            title = r.get("title", "")
            si, hi = score(title, INCIDENT)
            st, ht = score(title, TOPIC)
            ss, hs = score(title, STATUS)
            r["s_incident"] = si
            r["s_topic"] = st
            r["s_status"] = ss
            r["score"] = si + st * 2 + ss  # topic weighted highest
            r["hits"] = hi + ht + hs
            r["kind"] = "incident" if (si >= 3 and st >= 2) else "context"
            r["year"] = year_of(r.get("date", ""))
            geo, ca, fo = classify_geo(title, r.get("source", ""))
            r["geo"] = geo
            r["ca_score"] = ca
            r["foreign_score"] = fo
            rows.append(r)

    rows.sort(key=lambda r: r["score"], reverse=True)
    with open(os.path.join(CLEAN, "triage.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Canadian shortlist: keep ALL Canadian incident-type articles (maximise
    # the DB), plus top context articles per topic. Drop foreign noise.
    ca = [r for r in rows if r["geo"] == "canada" and r["score"] > 0]
    ca_incidents = [r for r in ca if r["kind"] == "incident"]
    ca_context = [r for r in ca if r["kind"] != "incident"]
    # all incidents + top context per topic
    by_topic = {}
    for r in ca_context:
        by_topic.setdefault(r["topic"], []).append(r)
    final = list(ca_incidents)
    for t, lst in by_topic.items():
        final.extend(lst[:PER_TOPIC])
    seen = set()
    deduped = []
    for r in final:
        if r["url"] not in seen:
            seen.add(r["url"])
            deduped.append(r)
    final = deduped
    with open(os.path.join(CLEAN, "shortlist.jsonl"), "w") as f:
        for r in final:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # UK comparison baseline, kept separate
    uk = [r for r in rows if r["geo"] == "uk_baseline" and r["score"] > 0]
    with open(os.path.join(CLEAN, "uk_baseline.jsonl"), "w") as f:
        for r in uk:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # summary
    geos = {}
    for r in rows:
        geos[r["geo"]] = geos.get(r["geo"], 0) + 1
    print(f"total articles   : {len(rows)}")
    print(f"geo breakdown    : {geos}")
    print(f"canada (score>0) : {len(ca)}  | incidents: {len(ca_incidents)}")
    print(f"canada shortlist : {len(final)}")
    print(f"uk baseline      : {len(uk)}")
    print("canada incidents by year:")
    by = {}
    for r in ca_incidents:
        if r["year"]:
            by[r["year"]] = by.get(r["year"], 0) + 1
    for y in sorted(by):
        print(f"  {y}: {by[y]}")


if __name__ == "__main__":
    main()
