"""Screenshot each .page of the HTML migration demo packet at 2x."""
import os

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKET = os.path.join(ROOT, "docs", "previews", "html-migration", "all_types_packet.html")
OUTDIR = os.path.join(ROOT, "docs", "previews", "html-migration")

# Page type labels in order
TYPE_LABELS = [
    "venn_diagram", "handwriting", "pixel_copy", "alphabet",
    "sequencing", "fill_in_the_blank", "story_map", "number_line",
    "labeled_diagram", "two_operand",
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 850, "height": 1100}, device_scale_factor=2)
    page.goto("file://" + PACKET)
    page.wait_for_load_state("networkidle")
    pages = page.locator(".page")
    n = pages.count()
    for i in range(n):
        label = TYPE_LABELS[i] if i < len(TYPE_LABELS) else f"page_{i+1}"
        path = os.path.join(OUTDIR, f"html_{label}.png")
        pages.nth(i).screenshot(path=path)
        print(f"OK {label}: {path}")
    browser.close()
print(f"DONE {n} pages")