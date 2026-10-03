"""Programmatic vision-QA fallback for the fraction repair packet.

Checks per .page: (a) DOM geometry — nothing overflows the page box or is
clipped; (b) pixel analysis of the 2x screenshot — the three partition
circles and gray starter scaffolds are actually drawn, and no ink touches
the page edges (clipping signal).
"""
import os

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKET = os.path.join(ROOT, "docs", "previews", "fraction_repair", "fraction_repair_packet.html")
OUTDIR = os.path.join(ROOT, "docs", "previews", "fraction_repair")
from PIL import Image  # noqa: E402


def pixel_report(path):
    img = Image.open(path).convert("L")
    w, h = img.size
    px = img.load()
    dark = gray = 0
    edge_ink = 0
    for y in range(h):
        for x in range(w):
            v = px[x, y]
            if v < 100:
                dark += 1
                if x < 4 or y < 4 or x >= w - 4 or y >= h - 4:
                    edge_ink += 1
            elif 120 <= v <= 210:
                gray += 1
    return {
        "size": (w, h), "dark_px": dark, "gray_px": gray,
        "edge_ink_px": edge_ink,
        "dark_ratio": dark / (w * h),
    }


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 850, "height": 1100}, device_scale_factor=2)
    page.goto("file://" + PACKET)
    page.wait_for_load_state("networkidle")
    n = page.locator(".page").count()
    for i in range(n):
        shot = os.path.join(OUTDIR, f"html_page_{i + 1}.png")
        page.locator(".page").nth(i).screenshot(path=shot)
        # DOM geometry: overflow / clipped cards inside this page div.
        geo = page.evaluate(
            """(i) => {
                const pg = document.querySelectorAll('.page')[i];
                const pr = pg.getBoundingClientRect();
                const issues = [];
                pg.querySelectorAll('.ea-card').forEach((card, k) => {
                    const r = card.getBoundingClientRect();
                    if (r.bottom > pr.bottom + 1) issues.push(`card ${k+1} overflows page bottom`);
                    if (r.right > pr.right + 1) issues.push(`card ${k+1} overflows right`);
                    if (r.left < pr.left - 1) issues.push(`card ${k+1} overflows left`);
                    card.querySelectorAll('svg').forEach((svg, s) => {
                        const sr = svg.getBoundingClientRect();
                        const cr = card.getBoundingClientRect();
                        if (sr.bottom > cr.bottom + 1) issues.push(`card ${k+1} svg ${s+1} clipped by card`);
                    });
                });
                return {
                    page_h: pr.height,
                    svg_count: pg.querySelectorAll('svg').length,
                    path_count: pg.querySelectorAll('svg path').length,
                    issues,
                };
            }""",
            i,
        )
        rep = pixel_report(shot)
        print(f"page {i+1}: {geo['svg_count']} svgs, {geo['path_count']} wedge paths, "
              f"h={geo['page_h']:.0f}")
        print("  pixels:", rep)
        print("  issues:", geo["issues"] or "none")
    browser.close()
