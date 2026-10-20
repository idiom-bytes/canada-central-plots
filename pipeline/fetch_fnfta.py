"""Acquire First Nations Financial Transparency Act (FNFTA) filing records.
Source: ISC/CIRNAC First Nation Profiles portal (public, per-band 'Date Received' by fiscal year).
Output: lake/bc_fn_accountability/fnfta/fnfta_{province}.json  (raw per-band rows, no interpretation)
Usage: python3 pipeline/fetch_fnfta.py [PROV ...]   (default: all provinces)
"""
import json, os, re, sys, time
import requests
from bs4 import BeautifulSoup

BASE = "https://fnp-ppn.aadnc-aandc.gc.ca/FNP/Main/Search/"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lake", "bc_fn_accountability", "fnfta")
PROVS = ["BC", "AB", "MB", "NB", "NL", "NS", "NT", "ON", "PE", "QC", "SK", "YT"]

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) Chrome/120"


def hidden(html):
    b = BeautifulSoup(html, "html.parser")
    return {i["name"]: i.get("value", "") for i in b.find_all("input", type="hidden") if i.get("name", "").startswith("__")}


def band_list(prov):
    url = BASE + "SearchFF.aspx?lang=eng"
    d = hidden(s.get(url, timeout=60).text); d["ctl00$plcMain$btnFNFTA"] = "FNFTA"
    d = hidden(s.post(url, data=d, timeout=60).text) | {"ctl00$plcMain$ddlProvince": prov, "ctl00$plcMain$btnSearch": "Search"}
    t = BeautifulSoup(s.post(url, data=d, timeout=60).text, "html.parser").find("table", id="tblFNlist")
    rows = []
    for tr in (t.find_all("tr")[1:] if t else []):
        c = [x.get_text(" ", strip=True) for x in tr.find_all("td")]
        if len(c) >= 3:
            rows.append({"band": c[0], "name": c[1], "address": c[2]})
    return rows


def band_filings(band):
    u = BASE + f"FederalFundingNote.aspx?BAND_NUMBER={band}&lang=eng"
    d = hidden(s.get(u, timeout=60).text); d["ctl00$plcMain$btnOK"] = "OK"
    b = BeautifulSoup(s.post(u, data=d, timeout=60).text, "html.parser")
    t = b.find("table", id="plcMain_dgFundslist")
    out = []
    for tr in (t.find_all("tr")[1:] if t else []):
        c = [x.get_text(" ", strip=True) for x in tr.find_all("td")]
        if len(c) == 3:
            out.append({"fy": c[0], "doc": c[1], "received": c[2]})
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    for prov in (sys.argv[1:] or PROVS):
        path = os.path.join(OUT, f"fnfta_{prov}.json")
        if os.path.exists(path):
            continue
        bands = band_list(prov)
        for i, b in enumerate(bands):
            for attempt in range(3):
                try:
                    b["filings"] = band_filings(b["band"]); break
                except Exception as e:
                    time.sleep(2 * (attempt + 1)); b["filings"] = None
            time.sleep(0.25)
        json.dump({"province": prov, "fetched": time.strftime("%Y-%m-%d"), "bands": bands}, open(path, "w"), indent=1)
        print(prov, len(bands), "bands", sum(1 for b in bands if b["filings"] is None), "failed", flush=True)


if __name__ == "__main__":
    main()
