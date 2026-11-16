"""Vision-QA: screenshot each .page of the fraction repair HTML packet at 2x."""
import os

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKET = os.path.join(ROOT, "docs", "previews", "fraction_repair", "fraction_repair_packet.html")
OUTDIR = os.path.join(ROOT, "docs", "previews", "fraction_repair")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 850, "height": 1100}, device_scale_factor=2)
    page.goto("file://" + PACKET)
    page.wait_for_load_state("networkidle")
    pages = page.locator(".page")
    n = pages.count()
    for i in range(n):
        path = os.path.join(OUTDIR, f"html_page_{i + 1}.png")
        pages.nth(i).screenshot(path=path)
        print("OK", path)
    browser.close()
print("DONE", n, "pages")
