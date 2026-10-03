"""Screenshot + PDF the print validation packet at 2x."""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKET = os.path.join(ROOT, "docs/previews/print-validation/all_10_types.html")

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 850, "height": 1100}, device_scale_factor=2)
    page.goto(f"file://{PACKET}")
    page.wait_for_load_state("networkidle")

    # Screenshot each page div
    page_divs = page.query_selector_all(".page")
    out_dir = os.path.join(ROOT, "docs/previews/print-validation")
    os.makedirs(out_dir, exist_ok=True)

    names = [
        "venn_diagram", "handwriting", "pixel_copy", "alphabet", "sequencing",
        "fill_in_blank", "story_map", "number_line", "labeled_diagram", "two_operand",
    ]

    for i, div in enumerate(page_divs):
        name = names[i] if i < len(names) else f"page_{i}"
        path = os.path.join(out_dir, f"html_{name}.png")
        div.screenshot(path=path)
        print(f"  ✓ {name}")

    # Generate PDF
    pdf_path = os.path.join(out_dir, "all_10_types.pdf")
    page.pdf(path=pdf_path, print_background=True)
    print(f"\nPDF: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")

    browser.close()