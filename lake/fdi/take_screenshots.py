"""Take screenshots of fdi.html sections for the Twitter thread.

Usage:
    python3 lake/fdi/take_screenshots.py

Output: lake/fdi/screenshots/{nn}-{label}.png

Thread map (nn = tweet number):
    01-sectors.png         → tweet 1/   (Part 1: sector chart — 6-bucket breakdown)
    05-kiss-explainer.png  → tweet 5/   (Part 2: KISS green/red framework; tweets 2-4 are text-only)
    07-history.png         → tweet 7/   (Part 2: 19-year KISS history table; tweet 6 is text-only)
    08-findings.png        → tweet 8/   (Part 3: findings card grid; tweets 9-11 are text-only)
    12-recommendations.png → tweet 12/  (Part 4: recommendations grid; tweets 13-17 are text-only)
"""

import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HTML_PATH = f"file://{os.path.join(BASE, 'fdi.html')}"
OUT_DIR = os.path.join(BASE, "lake", "fdi", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

SHOTS = [
    ("01-sectors",          "#charts"),
    ("05-kiss-explainer",   ".kiss-explainer"),
    ("07-history",          "#data-table"),
    ("08-findings",         "#findings"),
    ("12-recommendations",  "#recommendations"),
]


def take(page, label, selector):
    out = os.path.join(OUT_DIR, f"{label}.png")
    el = page.locator(selector)
    el.screenshot(path=out)
    size = os.path.getsize(out)
    print(f"  {label}.png  ({size // 1024}KB)")


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Installing playwright...")
        os.system(f"{sys.executable} -m pip install playwright -q")
        os.system(f"{sys.executable} -m playwright install chromium --quiet")
        from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        page.goto(HTML_PATH)
        page.wait_for_timeout(2000)  # charts need time to render

        print(f"Screenshotting: {HTML_PATH}")
        print(f"Output dir:     {OUT_DIR}\n")

        for label, selector in SHOTS:
            take(page, label, selector)

        browser.close()

    print(f"\nDone. {len(SHOTS)} screenshots in lake/fdi/screenshots/")


if __name__ == "__main__":
    main()
