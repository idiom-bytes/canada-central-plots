"""Take screenshots of trucking-certification.html sections for the Twitter thread.

Usage:
    python3 lake/trucking/take_screenshots.py

Output: lake/trucking/screenshots/{nn}-{label}.png

Thread map (nn = tweet number):
    01-gap.png             → tweet 1/   (Part 1: The Gap — NHTSA ≠ EPA diagram)
    02-dependency.png      → tweet 2/   (Part 2: The Dependency — stat row)
    03-timeline.png        → tweet 3/   (Part 3: Timeline — tweets 4 and 5 are text-only)
    06-financial.png       → tweet 6/   (Part 4: Financial scale — impact table; tweet 7 is text-only)
    08-findings.png        → tweet 8/   (Part 5: Findings — tweets 9 and 10 are text-only)
    11-recommendations.png → tweet 11/  (Part 6: Recommendations — card grid; tweet 12 is text-only)
"""

import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HTML_PATH = f"file://{os.path.join(BASE, 'trucking-certification.html')}"
OUT_DIR = os.path.join(BASE, "lake", "trucking", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

SHOTS = [
    ("01-gap",             "#section-gap"),
    ("02-dependency",      "#section-dependency"),
    ("03-timeline",        "#section-timeline"),
    ("06-financial",       "#section-financial"),
    ("08-findings",        "#section-findings"),
    ("11-recommendations", "#section-recommendations"),
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
        page.wait_for_timeout(1000)

        print(f"Screenshotting: {HTML_PATH}")
        print(f"Output dir:     {OUT_DIR}\n")

        for label, selector in SHOTS:
            take(page, label, selector)

        browser.close()

    print(f"\nDone. {len(SHOTS)} screenshots in lake/trucking/screenshots/")


if __name__ == "__main__":
    main()
