#!/usr/bin/env python3
"""
Acquire official, primary-source reports from peer democracies that publish
crime statistics broken down by national origin / immigrant background, in
aggregate. These establish that aggregate offender-origin reporting is a
normal product of national statistics agencies — not a taboo.

Token-lean: downloads files to the data lake; nothing is read into a model.
Verifies each URL (status, content-type, bytes) and writes a manifest.

Run:  python3 pipeline/acquire_intl_crime_origin.py
Out:  lake/intl_crime_origin/<files>  +  manifest.json
"""
import http.client, json, os, ssl, time, urllib.request, urllib.error
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "lake" / "intl_crime_origin"
OUT.mkdir(parents=True, exist_ok=True)

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Each entry is a primary source. `page` = the human-facing URL to screenshot;
# `url` = the direct artifact we download as a durable proof copy.
SOURCES = [
  # ---- GERMANY: Federal Criminal Police Office (BKA) ----
  dict(country="Germany", agency="Bundeskriminalamt (BKA) / BMI",
       title="Polizeiliche Kriminalstatistik 2024 — Tatverdächtige deutsch/nichtdeutsch nach Nationalitäten",
       year=2024, lang="de", fname="germany_pks2024_jahrbuch.pdf",
       url="https://www.polizei.hamburg/resource/blob/1053710/30efad000cc60586a22280031dad1ea0/pks-2024-jahrbuch-do-data.pdf",
       page="https://www.bka.de/DE/AktuelleInformationen/StatistikenLagebilder/PolizeilicheKriminalstatistik/PKS2024/PKSTabellen/BundTVNationalitaet/bundTVNationalitaet.html",
       shows="Annual federal police statistics tabulate suspects by nationality and by residence status."),
  dict(country="Germany", agency="Bundeskriminalamt (BKA)",
       title="PKS 2024 — Bund: Tatverdächtige nach Nationalitäten (official table page)",
       year=2024, lang="de", fname="germany_bka_tv_nationalitaet_2024.html",
       url="https://www.bka.de/DE/AktuelleInformationen/StatistikenLagebilder/PolizeilicheKriminalstatistik/PKS2024/PKSTabellen/BundTVNationalitaet/bundTVNationalitaet.html",
       page="https://www.bka.de/DE/AktuelleInformationen/StatistikenLagebilder/PolizeilicheKriminalstatistik/PKS2024/PKSTabellen/BundTVNationalitaet/bundTVNationalitaet.html",
       shows="Official BKA table set: suspects by German/non-German, by nationality, and by residence status — downloadable Excel/CSV linked here."),

  # ---- DENMARK: Ministry of Justice research unit + Statistics Denmark ----
  dict(country="Denmark", agency="Justitsministeriet (Ministry of Justice), Forskningsenheden",
       title="Kriminalitet og herkomst 2023 (Crime and Origin 2023)",
       year=2023, lang="da", fname="denmark_kriminalitet_og_herkomst_2023.pdf",
       url="https://www.justitsministeriet.dk/wp-content/uploads/2025/05/Kriminalitet-og-herkomst-2023-WT.pdf",
       page="https://www.justitsministeriet.dk/",
       shows="Recurring official report: convictions indexed by origin (immigrants/descendants/country groups), age-standardised."),
  dict(country="Denmark", agency="Danmarks Statistik (Statistics Denmark)",
       title="Indvandrere i Danmark 2023 — publication landing (crime chapter)",
       year=2023, lang="da", fname="denmark_dst_indvandrere_2023_landing.html",
       url="https://www.dst.dk/da/Statistik/nyheder-analyser-publ/Publikationer/VisPub?cid=47883",
       page="https://www.dst.dk/da/Statistik/nyheder-analyser-publ/Publikationer/VisPub?cid=47883",
       shows="National statistics office annual publication with a dedicated crime-by-origin chapter."),

  # ---- NORWAY: Statistics Norway (SSB) ----
  dict(country="Norway", agency="Statistisk sentralbyrå (Statistics Norway, SSB)",
       title="Crime and punishment among immigrants and the remaining Norwegian population (English discussion paper)",
       year=2012, lang="en", fname="norway_ssb_dp728_crime_immigrants.pdf",
       url="https://www.ssb.no/en/forskning/discussion-papers/_attachment/124152?_ts=13f5601b580",
       page="https://www.ssb.no/en/sosiale-forhold-og-kriminalitet/artikler-og-publikasjoner/crime-and-punishment-among-immigrants-and-the-remaining-norwegian-population--328011",
       shows="Statistics Norway analysis of charge/sanction rates by immigrant group vs the rest of the population."),

  # ---- NETHERLANDS: Statistics Netherlands (CBS) ----
  dict(country="Netherlands", agency="Centraal Bureau voor de Statistiek (CBS)",
       title="Criminaliteit onder personen met een niet-westerse migratieachtergrond",
       year=2021, lang="nl", fname="netherlands_cbs_criminaliteit_migratieachtergrond.pdf",
       url="https://open.overheid.nl/documenten/ronl-523f11e0-6364-4f20-ab95-ed083dd07532/pdf",
       page="https://longreads.cbs.nl/integratie-en-samenleven-2024/criminaliteit/",
       shows="National statistics office report on registered crime by migration background, with controls for background characteristics."),

  # ---- SWEDEN: Brå (National Council for Crime Prevention) ----
  dict(country="Sweden", agency="Brottsförebyggande rådet (Brå)",
       title="Registered offending among persons with domestic and foreign background (2021:9) — English summary",
       year=2021, lang="en", fname="sweden_bra_2021_summary_en.pdf",
       url="https://bra.se/download/18.45e4b8e192705389a34c2b/1729515966490/2021_9_Registered_offending_among_persons.pdf",
       page="https://bra.se/rapporter/arkiv/2021-08-25-misstankta-for-brott-bland-personer-med-inrikes-respektive-utrikes-bakgrund",
       shows="Brå study of suspects 2007–2018 by Swedish vs foreign background, with age/sex/income controls."),
  dict(country="Sweden", agency="Brottsförebyggande rådet (Brå)",
       title="Misstänkta för brott ... (2021:9) — main report (Swedish)",
       year=2021, lang="sv", fname="sweden_bra_2021_main_sv.pdf",
       url="https://bra.se/download/18.45e4b8e192705389a34b52/1729514247826/2021_9_Misstankta_for_brott_bland_personer_med_inrikes_respektive_utrikes_bakgrund.pdf",
       page="https://bra.se/rapporter/arkiv/2021-08-25-misstankta-for-brott-bland-personer-med-inrikes-respektive-utrikes-bakgrund",
       shows="Full Brå report with the methodology and breakdown tables."),
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
            # server closed early; if we got a usable payload, keep it
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
        rec = {k: s[k] for k in ("country", "agency", "title", "year", "lang",
                                 "fname", "url", "page", "shows")}
        try:
            code, ct, n = fetch(s["url"], dest)
            rec.update(status=code, content_type=ct, bytes=n, ok=(code == 200 and n > 1024))
            print(f"[{'OK ' if rec['ok'] else 'WARN'}] {s['country']:<12} {n:>9,}B  {ct:<28} {s['fname']}")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            rec.update(status=None, content_type=None, bytes=0, ok=False, error=str(e))
            print(f"[FAIL] {s['country']:<12} {s['fname']}  -> {e}")
        manifest.append(rec)

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    ok = sum(1 for m in manifest if m["ok"])
    print(f"\n{ok}/{len(manifest)} downloaded to {OUT}")
    print(f"manifest: {OUT/'manifest.json'}")


if __name__ == "__main__":
    main()
