"""View 4 data — political/institutional influence, measured the only neutral,
factual way: the federal Registry of Lobbyists. Who lobbies the Government of
Canada on immigration, how often, and which institutions they target.

This deliberately avoids editorial claims about any ethnic or religious group.
It reports the public lobbying record as filed with the Commissioner of Lobbying.

Source:
  - Office of the Commissioner of Lobbying — Monthly Communication Reports
    (open.canada.ca "Monthly Communication Reports"). Subject "Immigration" = SMT-19.
  Note: the lobbycanada.gc.ca TLS cert is expired; we fetch with verification off
  (public open data, known government domain).

Output:
  data/lobbying.json
  data/lobbying.js   (window.LOBBY_DB)
"""

import csv
import io
import json
import os
import re
import ssl
import urllib.request
import zipfile
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
UA = "Mozilla/5.0 (X11; Linux x86_64) research-bot"
URL = "https://lobbycanada.gc.ca/media/mqbbmaqk/communications_ocl_cal.zip"
IMMIG = "SMT-19"


def main():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    raw = urllib.request.urlopen(
        urllib.request.Request(URL, headers={"User-Agent": UA}), timeout=180, context=ctx).read()
    z = zipfile.ZipFile(io.BytesIO(raw))

    def rows(n):
        return csv.DictReader(io.TextIOWrapper(z.open(n), "utf-8-sig", errors="ignore"))

    # communications tagged Immigration
    immig_ids = {r["COMLOG_ID"] for r in rows("Communication_SubjectMattersExport.csv")
                 if r["SUBJECT_CODE_OBJET"] == IMMIG}

    # primary record: org + date
    by_year = Counter()
    org_counter = Counter()
    id_year = {}
    for r in rows("Communication_PrimaryExport.csv"):
        cid = r["COMLOG_ID"]
        if cid not in immig_ids:
            continue
        org = (r.get("EN_CLIENT_ORG_CORP_NM_AN") or "").strip()
        d = r.get("COMM_DATE", "")
        m = re.search(r"(20[0-2][0-9])", d)
        yr = int(m.group(1)) if m else None
        if yr:
            by_year[yr] += 1
            id_year[cid] = yr
        if org:
            org_counter[org] += 1

    # institutions lobbied (DPOH export)
    inst_counter = Counter()
    for r in rows("Communication_DpohExport.csv"):
        if r["COMLOG_ID"] in immig_ids:
            inst = (r.get("INSTITUTION") or "").strip()
            if inst:
                inst_counter[inst] += 1

    years = sorted(y for y in by_year if 2008 <= y <= 2026)
    year_series = [{"year": y, "n": by_year[y]} for y in years]
    top_orgs = [{"org": o, "n": n} for o, n in org_counter.most_common(20)]
    top_inst = [{"institution": i, "n": n} for i, n in inst_counter.most_common(15)]

    total = len(immig_ids)
    recent = sum(by_year[y] for y in years if y >= years[-3]) if len(years) >= 3 else None
    peak = max(year_series, key=lambda x: x["n"]) if year_series else None

    out = {
        "meta": {
            "total_immig_comms": total,
            "distinct_orgs": len(org_counter),
            "first_year": years[0] if years else None,
            "last_year": years[-1] if years else None,
            "peak_year": peak["year"] if peak else None,
            "peak_n": peak["n"] if peak else None,
            "top_org": top_orgs[0]["org"] if top_orgs else None,
            "top_org_n": top_orgs[0]["n"] if top_orgs else None,
            "top_institution": top_inst[0]["institution"] if top_inst else None,
            "source": "Office of the Commissioner of Lobbying of Canada — Monthly Communication Reports (subject: Immigration, SMT-19)",
        },
        "by_year": year_series,
        "top_orgs": top_orgs,
        "top_institutions": top_inst,
    }
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "lobbying.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(DATA, "lobbying.js"), "w") as f:
        f.write("window.LOBBY_DB = ")
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    m = out["meta"]
    print(f"immigration communications : {m['total_immig_comms']:,}")
    print(f"distinct organizations     : {m['distinct_orgs']:,}")
    print(f"years                      : {m['first_year']} -> {m['last_year']} (peak {m['peak_year']}: {m['peak_n']:,})")
    print(f"top org                    : {m['top_org']} ({m['top_org_n']:,})")
    print(f"top institution            : {m['top_institution']}")
    print("top 8 orgs:")
    for o in top_orgs[:8]:
        print(f"  {o['n']:5d}  {o['org']}")
    print("top 6 institutions:")
    for i in top_inst[:6]:
        print(f"  {i['n']:5d}  {i['institution']}")


if __name__ == "__main__":
    main()
