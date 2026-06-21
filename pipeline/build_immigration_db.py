"""Stage B-2 (build DB) — deterministic, no model, no key.

Turns the triaged Canadian articles into a distinct-case incident database.
Keeps ALL flagged Canadian incidents (per user choice) but:
  - tags each with a coarse category (so weapons/drug false-positives stay
    filterable rather than deleted),
  - clusters cross-outlet coverage of the same case into one record (dedup),
  - pre-flags an immigration-linked subset (title mentions status/origin) as
    candidates for full-text extraction.

Output:
  data/immigration_incidents.json   distinct cases (broad DB) + meta
  lake/immigration/clean/fulltext_candidates.jsonl  cases to download/enrich
Prints counts only.
"""

import json
import os
import re
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(ROOT, "lake", "immigration", "clean")
DATA = os.path.join(ROOT, "data")

STOP = set("the a an of in on at to for and or with by from as is are was were "
           "be been after over into out about man woman men women year old ont "
           "police say says said charged charge charges following alleged "
           "allegedly his her he she they court case investigation".split())

CATEGORIES = [
    ("human_trafficking", ["human trafficking", "sex trafficking", "sexual servitude",
                            "trafficking in persons", "trafficking woman", "trafficking women"]),
    ("child_exploitation", ["child porn", "child sexual", "child sex", "child abuse",
                            "luring", "child exploitation", "underage", "minor",
                            "sextortion", "csam"]),
    ("weapons_drug", ["weapons trafficking", "drug trafficking", "gun", "firearm",
                      "fentanyl", "cocaine", "narcotic", "guns"]),
    ("sexual_assault_other", ["sexual assault", "rape", "raped", "sexual offence",
                              "sexual offences", "sex offender", "indecent"]),
]


def categorize(title):
    t = title.lower()
    cats = [name for name, kws in CATEGORIES if any(k in t for k in kws)]
    return cats or ["other"]


def norm_title(title):
    t = title.lower()
    t = re.sub(r"\s+-\s+[^-]+$", "", t)          # drop " - Outlet" suffix
    t = re.sub(r"^[a-z]{3,9}\.?\s*\d{4}:\s*", "", t)  # drop "Apr 2024:" prefix
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return t


def sig_tokens(ntitle):
    return frozenset(w for w in ntitle.split() if w not in STOP and len(w) > 2)


def main():
    rows = []
    with open(os.path.join(CLEAN, "triage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r.get("geo") == "canada" and r.get("kind") == "incident":
                rows.append(r)
    for r in rows:
        r["_norm"] = norm_title(r["title"])
        r["_sig"] = sig_tokens(r["_norm"])
        r["categories"] = categorize(r["title"])

    # cluster within year by token-Jaccard / sequence similarity
    by_year = {}
    for r in rows:
        by_year.setdefault(r.get("year") or 0, []).append(r)

    cases = []
    for yr, items in by_year.items():
        used = [False] * len(items)
        for i in range(len(items)):
            if used[i]:
                continue
            cluster = [items[i]]
            used[i] = True
            si = items[i]["_sig"]
            for j in range(i + 1, len(items)):
                if used[j]:
                    continue
                sj = items[j]["_sig"]
                if not si or not sj:
                    continue
                jac = len(si & sj) / len(si | sj)
                if jac >= 0.5 or (jac >= 0.35 and SequenceMatcher(
                        None, items[i]["_norm"], items[j]["_norm"]).ratio() >= 0.7):
                    cluster.append(items[j])
                    used[j] = True
            rep = max(cluster, key=lambda r: r["score"])
            cats = sorted({c for r in cluster for c in r["categories"]})
            cases.append({
                "year": yr,
                "title": rep["title"],
                "source": rep["source"],
                "url": rep["url"],
                "date": rep["date"],
                "categories": cats,
                "n_mentions": len(cluster),
                "s_status": max(r["s_status"] for r in cluster),
                "status_hits": sorted({h for r in cluster for h in r["hits"]
                                       if h in {"refugee", "asylum", "foreign national",
                                                "permanent resident", "temporary foreign worker",
                                                "migrant", "immigrant", "deport", "deportation",
                                                "removal order", "newcomer", "international student",
                                                "non-citizen"}}),
                "all_urls": [r["url"] for r in cluster],
            })

    cases.sort(key=lambda c: (c["year"], -c["n_mentions"]))

    # immigration-linked candidates (title already hints at status/origin)
    candidates = [c for c in cases if c["s_status"] > 0]
    with open(os.path.join(CLEAN, "fulltext_candidates.jsonl"), "w") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # category + year aggregates for the dashboard
    by_year_count = {}
    by_cat = {}
    for c in cases:
        by_year_count[c["year"]] = by_year_count.get(c["year"], 0) + 1
        for cat in c["categories"]:
            by_cat[cat] = by_cat.get(cat, 0) + 1

    out = {
        "meta": {
            "description": "Distinct Canadian sexual-exploitation/trafficking incidents from news coverage, 2016-2026",
            "method": "Google News RSS harvest (keyless) -> keyword triage -> Canada filter -> cross-outlet dedup. Title-level; perpetrator immigration status requires full-text enrichment.",
            "article_mentions": len(rows),
            "distinct_cases": len(cases),
            "immigration_linked_candidates": len(candidates),
        },
        "by_year": dict(sorted(by_year_count.items())),
        "by_category": dict(sorted(by_cat.items(), key=lambda x: -x[1])),
        "cases": cases,
    }
    os.makedirs(DATA, exist_ok=True)
    for c in cases:
        c.pop("_norm", None); c.pop("_sig", None)
    with open(os.path.join(DATA, "immigration_incidents.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # Slim build for the dashboard, loaded via <script src> so it works over
    # file:// (double-click) as well as a local server — no fetch/CORS issues.
    slim_cases = [{
        "year": c["year"], "title": c["title"], "source": c["source"],
        "url": c["url"], "categories": c["categories"],
        "n_mentions": c["n_mentions"], "status_hits": c["status_hits"],
    } for c in cases]
    slim = {"meta": out["meta"], "by_year": out["by_year"],
            "by_category": out["by_category"], "cases": slim_cases}
    with open(os.path.join(DATA, "immigration_incidents.slim.js"), "w") as f:
        f.write("window.INCIDENT_DB = ")
        json.dump(slim, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    print(f"article-mentions : {len(rows)}")
    print(f"distinct cases   : {len(cases)}")
    print(f"immig candidates : {len(candidates)}")
    print("distinct cases by year:")
    for y, n in sorted(by_year_count.items()):
        print(f"  {y}: {n}")
    print("by category (cases can have >1):")
    for cat, n in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    main()
