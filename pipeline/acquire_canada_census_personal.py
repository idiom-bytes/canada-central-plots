#!/usr/bin/env python3
"""
Acquire official Statistics Canada census products that show how granular and
"personal" the data the government already collects AND publishes is — religion,
ethnic/cultural origin, visible-minority group, place of birth, Indigenous
identity, generation status — in aggregate, down to small geographies.

This is the *contrast* set for the offender-origin "data gap": Canada will publish
your religion by neighbourhood, but records nothing about an offender's origin.

Token-lean: downloads to the data lake; nothing is read into a model.

Run:  python3 pipeline/acquire_canada_census_personal.py
Out:  lake/canada_census/<files>  +  manifest.json
"""
import http.client, json, ssl, time, urllib.request, urllib.error
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "lake" / "canada_census"
OUT.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

SOURCES = [
  # ---- The questionnaire itself: the actual questions asked ----
  dict(kind="questionnaire", title="2021 Census long-form questionnaire (Form 2A-L) — full instrument incl. religion (Q30), ethnic/cultural origin, Indigenous identity, place of birth",
       fname="census2021_2AL_questionnaire.html",
       url="https://www.statcan.gc.ca/en/statistical-programs/instrument/3901_Q2_V6",
       page="https://www12.statcan.gc.ca/census-recensement/2021/ref/questionnaire/index-eng.cfm",
       shows="Every question put to a 25% sample of households, including religion, ethnic/cultural origins, Indigenous identity, and place of birth."),

  # ---- Reference guides: how each personal variable is defined & released ----
  dict(kind="guide", title="Religion Reference Guide, 2021 Census",
       fname="census2021_religion_reference_guide.pdf",
       url="https://www12.statcan.gc.ca/census-recensement/2021/ref/98-500/016/98-500-x2021016-eng.pdf",
       page="https://www12.statcan.gc.ca/census-recensement/2021/ref/98-500/016/98-500-x2021016-eng.cfm",
       shows="Religion is collected and disseminated; 200+ denominations classifiable."),
  dict(kind="guide", title="Ethnic or Cultural Origin Reference Guide, 2021 Census",
       fname="census2021_ethnic_origin_reference_guide.pdf",
       url="https://www12.statcan.gc.ca/census-recensement/2021/ref/98-500/008/98-500-x2021008-eng.pdf",
       page="https://www12.statcan.gc.ca/census-recensement/2021/ref/98-500/008/98-500-x2021008-eng.cfm",
       shows="Hundreds of ethnic/cultural origins coded and published."),
  dict(kind="guide", title="Visible Minority and Population Group Reference Guide, 2021 Census",
       fname="census2021_visible_minority_reference_guide.pdf",
       url="https://www12.statcan.gc.ca/census-recensement/2021/ref/98-500/006/98-500-x2021006-eng.pdf",
       page="https://www12.statcan.gc.ca/census-recensement/2021/ref/98-500/006/98-500-x2021006-eng.cfm",
       shows="A derived 'population group' / visible-minority classification, published by geography."),

  # ---- The Daily: official release announcing the personal-diversity data ----
  dict(kind="release", title="The Daily — A rich portrait of the country's religious and ethnocultural diversity (2022-10-26)",
       fname="census2021_thedaily_diversity.html",
       url="https://www150.statcan.gc.ca/n1/daily-quotidien/221026/dq221026b-eng.htm",
       page="https://www150.statcan.gc.ca/n1/daily-quotidien/221026/dq221026b-eng.htm",
       shows="Official release of religion + ethnocultural data, with geographic breakdowns."),

  # ---- Published data tables (CSV zip) — proof of granular dissemination ----
  dict(kind="table", title="Religion by visible minority and generation status (98-10-0342-01)",
       fname="census2021_religion_by_vismin_generation_98100342.zip",
       url="https://www150.statcan.gc.ca/n1/tbl/csv/98100342-eng.zip",
       page="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810034201",
       shows="Religion crossed with visible minority and generation status, by geography."),
  dict(kind="table", title="Visible minority by place of birth and generation status (98-10-0326-01)",
       fname="census2021_vismin_by_birthplace_generation_98100326.zip",
       url="https://www150.statcan.gc.ca/n1/tbl/csv/98100326-eng.zip",
       page="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810032601",
       shows="Visible minority crossed with place of birth and generation status, by geography."),
  dict(kind="table", title="Visible minority by ethnic or cultural origin (98-10-0337-01)",
       fname="census2021_vismin_by_ethnicorigin_98100337.zip",
       url="https://www150.statcan.gc.ca/n1/tbl/csv/98100337-eng.zip",
       page="https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810033701",
       shows="Visible minority crossed with ethnic/cultural origin, by geography."),
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(url, dest, retries=3):
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
                ct = r.headers.get("Content-Type", "")
                code = r.getcode()
                buf = bytearray()
                while True:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    buf.extend(chunk)
            dest.write_bytes(buf)
            return code, ct, len(buf)
        except http.client.IncompleteRead as e:
            last = e
            if e.partial and len(e.partial) > 1024:
                dest.write_bytes(e.partial)
                return 200, "incomplete", len(e.partial)
            time.sleep(1.5 * (attempt + 1))
    raise last if last else RuntimeError("fetch failed")


def main():
    manifest = []
    for s in SOURCES:
        dest = OUT / s["fname"]
        rec = {k: s[k] for k in ("kind", "title", "fname", "url", "page", "shows")}
        try:
            code, ct, n = fetch(s["url"], dest)
            rec.update(status=code, content_type=ct, bytes=n, ok=(code == 200 and n > 1024))
            print(f"[{'OK ' if rec['ok'] else 'WARN'}] {s['kind']:<13} {n:>10,}B  {ct:<26} {s['fname']}")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            rec.update(status=None, content_type=None, bytes=0, ok=False, error=str(e))
            print(f"[FAIL] {s['kind']:<13} {s['fname']}  -> {e}")
        manifest.append(rec)

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    ok = sum(1 for m in manifest if m["ok"])
    print(f"\n{ok}/{len(manifest)} downloaded to {OUT}")


if __name__ == "__main__":
    main()
