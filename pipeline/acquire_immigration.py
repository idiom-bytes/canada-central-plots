"""Stage A (acquire) for the immigration / exploitation research.

Token-efficient research pipeline — see memory feedback_low_token_research.
This script does ALL the searching+downloading with ZERO model involvement.
It harvests Google News RSS (keyless) for a set of incident queries, saves the
raw XML to the lake, and writes a consolidated manifest of article metadata
(title, source, date, url, query, sub-topic). It prints ONLY counts.

Stage B (extract_immigration.py) turns raw HTML into clean text / JSON later.

Output:
  lake/immigration/raw/rss/<slug>.xml      raw RSS responses
  lake/immigration/raw/articles.jsonl      one row per article (deduped by url)
  lake/immigration/raw/manifest.json       per-query counts summary
"""

import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "lake", "immigration", "raw")
RSS_DIR = os.path.join(RAW, "rss")

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 research-bot"

# Canadian trafficking/exploitation hubs + provinces for geographic fan-out.
CA_PLACES = [
    "Toronto", "Peel Region", "York Region", "Ottawa", "Hamilton Ontario",
    "Windsor Ontario", "London Ontario", "Niagara", "Durham Region",
    "Montreal", "Quebec", "Vancouver", "Surrey BC", "Calgary", "Edmonton",
    "Winnipeg", "Halifax", "Saskatoon", "Ontario", "British Columbia",
    "Alberta", "Manitoba", "Nova Scotia",
]
# Incident phrasings to combine with each place.
CA_INCIDENT_TERMS = [
    "human trafficking charged",
    "sex trafficking arrest",
    "child exploitation charges",
    "sexual assault luring charged",
]


def _geo_queries():
    out = []
    for p in CA_PLACES:
        for t in CA_INCIDENT_TERMS:
            out.append(f"{p} {t}")
    return out


# 4 sub-topics from the original research brief, each with targeted queries.
QUERIES = {
    "1_immigration_categories": [
        "Canada temporary foreign workers numbers surge",
        "Canada asylum claims backlog",
        "Canada immigration levels permanent residents record",
    ],
    "2_crime_perpetrator_origin": [
        "Canada human trafficking arrest immigration status",
        "Canada sexual assault gang charges newcomer",
        "Canada child exploitation ring arrests nationality",
        "Canada grooming gang investigation",
        "RCMP human trafficking charges",
        "OPP human trafficking arrest",
        "CBSA foreign national sexual offence deport",
        "Canada refugee sexual assault charged",
        "Canada foreign worker sexual assault charged",
    ],
    "3_catch_and_release_backlog": [
        "Canada bail catch and release violent offender",
        "Canada deportation order ignored removal backlog",
        "Canada immigration detention release criminal",
        "Canada failed deportation reoffend",
    ],
    "4_political_institutional": [
        "Lena Diab immigration minister policy",
        "Canada CSIS RCMP failure deport criminal",
        "Canada immigration lobby influence policy",
    ],
    # geographic fan-out of Canadian incidents to maximise corpus size
    "2_crime_geo": _geo_queries(),
}

RSS = "https://news.google.com/rss/search?q={q}&hl=en-CA&gl=CA&ceid=CA:en"

# Walk each query across yearly windows so older coverage isn't crowded out by
# recent results. ~10-year lookback. Google News RSS honors after:/before:.
YEARS = list(range(2016, 2027))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def parse_rss(xml_bytes, topic, query):
    rows = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return rows
    for item in root.iter("item"):
        def g(tag):
            el = item.find(tag)
            return el.text if el is not None and el.text else ""
        src_el = item.find("source")
        rows.append({
            "topic": topic,
            "query": query,
            "title": g("title"),
            "url": g("link"),
            "date": g("pubDate"),
            "source": src_el.text if src_el is not None else "",
        })
    return rows


def main():
    os.makedirs(RSS_DIR, exist_ok=True)
    seen = OrderedDict()  # url -> row (dedupe)
    manifest = []
    for topic, queries in QUERIES.items():
        for q in queries:
            for yr in YEARS:
                windowed = f"{q} after:{yr}-01-01 before:{yr+1}-01-01"
                url = RSS.format(q=urllib.parse.quote(windowed))
                try:
                    xml = fetch(url)
                except Exception as e:
                    manifest.append({"topic": topic, "query": q, "year": yr,
                                     "items": 0, "error": str(e)})
                    continue
                fn = os.path.join(RSS_DIR, f"{topic}__{slug(q)}__{yr}.xml")
                with open(fn, "wb") as f:
                    f.write(xml)
                rows = parse_rss(xml, topic, q)
                new = 0
                for r in rows:
                    if r["url"] and r["url"] not in seen:
                        seen[r["url"]] = r
                        new += 1
                manifest.append({"topic": topic, "query": q, "year": yr,
                                 "items": len(rows), "new": new})
                time.sleep(0.4)  # be polite

    with open(os.path.join(RAW, "articles.jsonl"), "w") as f:
        for r in seen.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(RAW, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    # terminal output: counts only, no article content
    total = sum(m.get("items", 0) for m in manifest)
    print(f"queries run : {len(manifest)}")
    print(f"items seen  : {total}")
    print(f"unique urls : {len(seen)}")
    by_topic = {}
    for r in seen.values():
        by_topic[r["topic"]] = by_topic.get(r["topic"], 0) + 1
    for t in sorted(by_topic):
        print(f"  {t}: {by_topic[t]} unique articles")
    errs = [m for m in manifest if m.get("error")]
    if errs:
        print(f"errors      : {len(errs)} (see manifest.json)")


if __name__ == "__main__":
    main()
