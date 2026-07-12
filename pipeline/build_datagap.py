"""View 1 data — the country-of-origin / immigration-status DATA GAP.

Quantifies, from our own deduped case DB, how rarely Canadian news coverage
identifies an offender's immigration status or nationality. This evidences the
structural finding: Canada's police-reported crime statistics (UCR/CCJS) do not
record offender immigration status or country of origin at all, so news coverage
is effectively the ONLY public signal — and it almost never carries it either.

Reads:  data/immigration_incidents.json   (distinct cases)
Writes: data/datagap.js                    (window.DATAGAP_DB) for the dashboard
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# Nationality / origin adjectives that would signal country-of-origin reporting.
NATIONALITY = [
    "pakistani", "indian", "afghan", "syrian", "somali", "nigerian", "iranian",
    "iraqi", "eritrean", "sudanese", "ethiopian", "lebanese", "palestinian",
    "chinese", "vietnamese", "filipino", "mexican", "jamaican", "haitian",
    "romanian", "ukrainian", "russian", "bangladeshi", "sri lankan", "turkish",
    "egyptian", "moroccan", "algerian", "venezuelan", "colombian", "honduran",
    "guatemalan", "nepalese", "indonesian", "saudi", "yemeni", "libyan",
    "foreign national", "foreign-born", "born in",
]
STATUS = [
    "refugee", "asylum", "asylum seeker", "permanent resident", "deport",
    "deportation", "removal order", "temporary foreign worker", "migrant",
    "immigrant", "newcomer", "international student", "study permit",
    "work permit", "non-citizen", "undocumented", "visa",
]


def hits(text, terms):
    t = text.lower()
    return sorted({k for k in terms if k in t})


def main():
    db = json.load(open(os.path.join(DATA, "immigration_incidents.json")))
    cases = db["cases"]
    total = len(cases)

    nat_cases, status_cases = [], []
    nat_terms, status_terms = {}, {}
    for c in cases:
        title = c.get("title", "")
        nh = hits(title, NATIONALITY)
        sh = hits(title, STATUS)
        if nh:
            nat_cases.append({"year": c["year"], "title": title, "source": c["source"],
                              "url": c["url"], "terms": nh})
            for k in nh:
                nat_terms[k] = nat_terms.get(k, 0) + 1
        if sh:
            status_cases.append({"year": c["year"], "title": title, "source": c["source"],
                                 "url": c["url"], "terms": sh})
            for k in sh:
                status_terms[k] = status_terms.get(k, 0) + 1

    identified = {c["url"] for c in nat_cases} | {c["url"] for c in status_cases}
    exceptions = sorted(
        {c["url"]: c for c in (status_cases + nat_cases)}.values(),
        key=lambda c: (c["year"], c["title"]))

    out = {
        "meta": {
            "total_cases": total,
            "status_mentioned": len(status_cases),
            "status_rate_pct": round(100 * len(status_cases) / total, 1),
            "nationality_mentioned": len(nat_cases),
            "nationality_rate_pct": round(100 * len(nat_cases) / total, 1),
            "any_identified": len(identified),
            "any_identified_rate_pct": round(100 * len(identified) / total, 1),
            "silent_pct": round(100 * (total - len(identified)) / total, 1),
        },
        "status_terms": dict(sorted(status_terms.items(), key=lambda x: -x[1])),
        "nationality_terms": dict(sorted(nat_terms.items(), key=lambda x: -x[1])),
        "exceptions": exceptions,
        "pipeline": [
            {"stage": "Gather", "detail": "A decade of Canadian news coverage, 2016–2026",
             "n": 24514, "unit": "articles reviewed"},
            {"stage": "Filter", "detail": "Canadian exploitation & trafficking cases",
             "n": 18189, "unit": "Canadian articles"},
            {"stage": "Combine", "detail": "Merge multiple outlets' coverage of one case",
             "n": total, "unit": "distinct cases"},
            {"stage": "Origin check", "detail": "Cases naming any immigration status or nationality",
             "n": len(identified), "unit": "cases (the rest are silent)"},
        ],
    }
    with open(os.path.join(DATA, "datagap.js"), "w") as f:
        f.write("window.DATAGAP_DB = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    m = out["meta"]
    print(f"total cases            : {m['total_cases']}")
    print(f"status mentioned       : {m['status_mentioned']} ({m['status_rate_pct']}%)")
    print(f"nationality mentioned  : {m['nationality_mentioned']} ({m['nationality_rate_pct']}%)")
    print(f"any origin identified  : {m['any_identified']} ({m['any_identified_rate_pct']}%)")
    print(f"silent on origin       : {m['silent_pct']}%")
    print(f"status terms           : {out['status_terms']}")
    print(f"nationality terms      : {out['nationality_terms']}")


if __name__ == "__main__":
    main()
