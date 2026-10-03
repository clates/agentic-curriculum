"""Migrate generator scripts from PIL renderer calls to HTML renderer.

Replaces:
  from worksheet_renderer import render_X_to_image, render_X_to_pdf
  render_X_to_image(ws, png_path)
  render_X_to_pdf(ws, pdf_path)

With:
  from worksheet_html_renderer import render_worksheet_html, build_print_packet_html
  html = render_worksheet_html(kind, data_dict)
  write .html file
"""

import os, re, sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPTS_DIR, "..", "src"))

# Map PIL render function prefix → HTML kind string
RENDER_MAP = {
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

def migrate_script(filepath):
    with open(filepath) as f:
        content = f.read()
    
    original = content
    changed = False
    
    # ── Step 1: Replace import ──
    import_match = re.match(r'from worksheet_renderer import (.+?)(?:\n|$)', content, re.MULTILINE)
    if import_match:
        old_import = import_match.group(0)
        # Figure out which kinds are being used
        imported = import_match.group(1)
        # Replace with HTML import
        new_import = 'from worksheet_html_renderer import render_worksheet_html, build_print_packet_html  # was: PIL renderer (deprecated)'
        content = content.replace(old_import, new_import + '\n')
        changed = True
    
    # ── Step 2: Replace render calls ──
    # Pattern: render_X_to_image(ws, path) and render_X_to_pdf(ws, path)
    # We need to know which kind each call maps to
    
    for pil_prefix, html_kind in RENDER_MAP.items():
        # Pattern: render_X_to_image(ws_var, path_var) and render_X_to_pdf(ws_var, path_var)
        # The ws_var is typically a factory result or worksheet object
        
        # Find pairs: _to_image then _to_pdf (with same ws)
        pattern_img = rf'{pil_prefix}_to_image\((\w+),\s*(.+?)\)'
        pattern_pdf = rf'{pil_prefix}_to_pdf\((\w+),\s*(.+?)\)'
        
        # For each match, replace both with HTML generation
        img_matches = list(re.finditer(pattern_img, content))
        pdf_matches = list(re.finditer(pattern_pdf, content))
        
        if img_matches or pdf_matches:
            # Build replacement: instead of render_X_to_image(ws, "path.png")
            # → render_worksheet_html("kind", data, "") → write to "path.html"
            for m in img_matches:
                ws_var = m.group(1)
                png_path = m.group(2).strip().strip('"\'')
                html_path = png_path.rsplit('.', 1)[0] + '.html'
                
                # Try to infer the data dict from the ws variable
                # Common patterns in these scripts:
                #   ws = WorksheetFactory.create("key", payload) → payload is already the dict
                #   ws = factory_result → has .model_dump() or is a dataclass
                
                replacement = (
                    f"# HTML render (was: {pil_prefix}_to_image → .png)\n"
                    f"    html_data = {ws_var}.model_dump() if hasattr({ws_var}, 'model_dump') else vars({ws_var})\n"
                    f'    _html = render_worksheet_html("{html_kind}", html_data)\n'
                    f'    if _html:\n'
                    f'        with open("{html_path}", "w") as f:\n'
                    f'            f.write(_html)'
                )
                
                # Try to find the exact line and replace
                original_line = m.group(0)
                content = content.replace(original_line, replacement, 1)
            
            # Remove PDF calls entirely (HTML replaces both formats)
            for m in pdf_matches:
                pdf_line = m.group(0)
                # Replace with a comment
                content = content.replace(pdf_line, f"    # PDF output replaced by HTML — see .html file above", 1)
            
            changed = True
    
    if changed and content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False


if __name__ == "__main__":
    count = 0
    for fname in sorted(os.listdir(SCRIPTS_DIR)):
        if not fname.endswith('.py') or fname.startswith('_') or fname.startswith('screenshot'):
            continue
        fpath = os.path.join(SCRIPTS_DIR, fname)
        if migrate_script(fpath):
            print(f"  Migrated: {fname}")
            count += 1
    print(f"\nDone. {count} scripts migrated.")