"""Take screenshots of vc-comparison-q1-2026.html sections for the Twitter thread.

Usage:
    python3 lake/vc/take_screenshots.py

Output: lake/vc/screenshots/{nn}-{label}.png

Thread map (nn = tweet number):
    01-us-decomposition.png       → tweet 2/  (Section 1: decomp chart + scenario cards)
    02-canada-stage-snapshots.png → tweet 4/  (Chart 6: Q1 stage log-scale)
    03-normalized-index.png       → tweet 8/  (Section 3: decade-in-context)
    11-findings.png               → tweet 11/ (all 6 findings cards)
    17-recommendations.png        → tweet 17/ (all 4 recommendation cards)
"""

import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HTML_PATH = f"file://{os.path.join(BASE, 'vc-comparison-q1-2026.html')}"
OUT_DIR = os.path.join(BASE, "lake", "vc", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

SHOTS = [
    ("01-us-decomposition",       "#section-decomp"),
    ("02-canada-stage-snapshots", "#section-stage-snapshots"),
    ("03-normalized-index",       "#section-normalized"),
    ("11-findings",               "#findings"),
    ("17-recommendations",        "#recommendations"),
]

# CSS injected before screenshotting — hides verbose text that clutters the image.
# Does not affect the live page (injected in-browser session only).
SCREENSHOT_CSS = """
    /* remove footnote text below charts */
    .chart-note        { display: none !important; }
    /* remove long section-level description paragraphs */
    .section-desc      { display: none !important; }
    /* remove page source line */
    .page-source       { display: none !important; }
    /* in rec cards: keep only What + Measurable target; hide Precedent and Who implements */
    .rec-precedent { display: none !important; }
    .rec-who       { display: none !important; }
"""

PADDING = 24  # px added around each element in the screenshot crop


def take(page, label, selector):
    out = os.path.join(OUT_DIR, f"{label}.png")
    el = page.locator(selector)
    box = el.bounding_box()
    if box is None:
        print(f"  {label}.png  SKIP — selector not found: {selector}")
        return
    clip = {
        "x": max(0, box["x"] - PADDING),
        "y": max(0, box["y"] - PADDING),
        "width":  min(1200, box["width"]  + PADDING * 2),
        "height": box["height"] + PADDING * 2,
    }
    page.screenshot(path=out, clip=clip, full_page=True)
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
        page.wait_for_timeout(1500)  # let charts render

        # Inject screenshot-only CSS (hides verbose text, doesn't affect live page)
        page.add_style_tag(content=SCREENSHOT_CSS)
        page.wait_for_timeout(100)

        print(f"Screenshotting: {HTML_PATH}")
        print(f"Output dir:     {OUT_DIR}\n")

        for label, selector in SHOTS:
            take(page, label, selector)

        browser.close()

    print(f"\nDone. {len(SHOTS)} screenshots in lake/vc/screenshots/")


if __name__ == "__main__":
    main()
