#!/usr/bin/env python3
"""Batch-migrate generator scripts from PIL renderer to HTML renderer.

Replaces:
  from worksheet_renderer import render_X_to_image, render_X_to_pdf
  render_X_to_image(ws, png_path)
  render_X_to_pdf(ws, pdf_path)

With HTML equivalents using render_worksheet_html + build_print_packet_html.
Scripts that use PIL directly (Image.new, etc.) are tagged with TODO comments.

Usage: python3 scripts/_migrate_to_html.py [--dry-run]
"""

import ast
import os
import re
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

# Map PIL render function prefix → HTML kind string
RENDER_PREFIX_TO_KIND = {
    "render_reading_worksheet": "readingWorksheet",
    "render_feature_matrix": "featureMatrixWorksheet",
    "render_tree_map": "treeMapWorksheet",
    "render_odd_one_out": "oddOneOutWorksheet",
    "render_matching": "matchingWorksheet",
    "render_cause_effect": "causeEffectWorksheet",
    "render_frayer_model": "frayerModelWorksheet",
    "render_word_sort": "wordSortWorksheet",
    "render_writing_scaffold": "writingScaffoldWorksheet",
    "render_t_chart": "tChartWorksheet",
    "render_handwriting": "handwritingWorksheet",
    "render_pixel_copy": "pixelCopyWorksheet",
    "render_alphabet": "alphabetWorksheet",
    "render_fill_in_blank": "fillInBlankWorksheet",
    "render_sequencing": "sequencingWorksheet",
    "render_venn_diagram": "vennDiagramWorksheet",
    "render_story_map": "storyMapWorksheet",
    "render_number_line": "numberLineWorksheet",
    "render_labeled_diagram": "labeledDiagramWorksheet",
    "render_error_audit": "errorAuditWorksheet",
    "render_ten_frame": "tenFrameWorksheet",
    "render_bar_graph": "barGraphWorksheet",
    "render_pictograph": "pictographWorksheet",
    "render_worksheet": "twoOperandWorksheet",
}

HTML_IMPORT = """from worksheet_html_renderer import (
    render_worksheet_html,
    build_print_packet_html,
)
"""


def _detect_kinds(content: str) -> set[str]:
    """Find which HTML kinds are used in the script's PIL render calls."""
    kinds = set()
    for prefix, kind in RENDER_PREFIX_TO_KIND.items():
        if re.search(rf"\b{prefix}_to_(image|pdf)\b", content):
            kinds.add(kind)
    return kinds


def _has_direct_pil(content: str) -> bool:
    """True if the script uses PIL directly (not just via worksheet_renderer)."""
    return bool(re.search(r'\bfrom PIL\b|\bImage\.new\b|\bImageDraw\b|\bImageFont\b', content))


def migrate_script(filepath: str, dry_run: bool = False) -> bool:
    with open(filepath) as f:
        content = f.read()

    kinds = _detect_kinds(content)
    has_pil = _has_direct_pil(content)

    if not kinds and not has_pil and "from worksheet_renderer import" not in content:
        return False

    original = content

    # Replace import line
    content = re.sub(
        r'from worksheet_renderer import .*?\n',
        f'{HTML_IMPORT}# ⚠️ PIL import migrated — was: worksheet_renderer\n',
        content,
    )
    content = re.sub(
        r'from worksheet_renderer import .*?\n',
        f'{HTML_IMPORT}# ⚠️ PIL import migrated — was: worksheet_renderer\n',
        content,
    )

    # Replace render_X_to_image / _to_pdf pairs
    for prefix, kind in RENDER_PREFIX_TO_KIND.items():
        img_pattern = rf'{prefix}_to_image\((\w+),\s*(.+?)\)'
        pdf_pattern = rf'{prefix}_to_pdf\((\w+),\s*(.+?)\)'

        def replace_img(m):
            var = m.group(1)
            path = m.group(2).strip().strip('"\'')
            html_path = path.rsplit('.', 1)[0] + '.html'
            return (
                f'# Migrated from {prefix}_to_image\n'
                f'    _html_{kind} = render_worksheet_html("{kind}", {var}.model_dump() if hasattr({var}, "model_dump") else vars({var}), "")\n'
                f'    Path("{html_path}").write_text(_html_{kind}) if _html_{kind} else print("⚠️  {kind} render failed")'
            )

        def replace_pdf(m):
            path = m.group(2).strip().strip('"\'')
            html_path = path.rsplit('.', 1)[0] + '.html'
            return f'# PDF replaced by HTML — see {html_path.split("/")[-1]}'

        content = re.sub(img_pattern, replace_img, content)
        content = re.sub(pdf_pattern, replace_pdf, content)

    # For scripts with direct PIL usage, add a TODO
    if has_pil:
        content = (
            f'# TODO: This script uses PIL directly (Image/ImageDraw/ImageFont).\n'
            f'# Full migration to HTML renderer needed — PIL deprecated.\n'
            f'{content}'
        )

    if content != original:
        if not dry_run:
            with open(filepath, 'w') as f:
                f.write(content)
        return True
    return False


def main():
    dry_run = '--dry-run' in sys.argv
    migrated = 0
    skipped = 0

    for fname in sorted(os.listdir(SCRIPTS_DIR)):
        if not fname.endswith('.py') or fname.startswith('_') or fname.startswith('screenshot'):
            continue
        fpath = os.path.join(SCRIPTS_DIR, fname)

        with open(fpath) as f:
            content = f.read()

        kinds = _detect_kinds(content)
        has_import = 'from worksheet_renderer import' in content
        has_pil = _has_direct_pil(content)

        if has_import or kinds:
            if migrate_script(fpath, dry_run=dry_run):
                tag = " [DRY-RUN]" if dry_run else ""
                print(f"  ✓ {fname}{tag} -> HTML kinds: {sorted(kinds) if kinds else 'direct-PIL-only'}")
                migrated += 1
            else:
                print(f"  - {fname}: no changes needed")
                skipped += 1
        else:
            skipped += 1

    print(f"\nMigrated: {migrated}, Skipped: {skipped}")
    if dry_run:
        print("DRY RUN — no files modified. Remove --dry-run to apply.")


if __name__ == "__main__":
    main()