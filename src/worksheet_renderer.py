"""Rendering helpers for Worksheet objects."""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from typing import cast

from PIL import Image, ImageDraw, ImageFont

try:
    from .worksheets import ReadingWorksheet, Worksheet, format_vertical_problem
    from .worksheets import (
        VennDiagramWorksheet,
        FeatureMatrixWorksheet,
        OddOneOutWorksheet,
        TreeMapWorksheet,
    )
except ImportError:  # Fallback when executed outside package context
    CURRENT_DIR = os.path.dirname(__file__)
    if CURRENT_DIR not in sys.path:
        sys.path.insert(0, CURRENT_DIR)
    from worksheets import ReadingWorksheet, Worksheet, format_vertical_problem  # type: ignore
    from worksheets import VennDiagramWorksheet, FeatureMatrixWorksheet, OddOneOutWorksheet, TreeMapWorksheet  # type: ignore

_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
)

_FONT_BOLD_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)

_FONT_ITALIC_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
)

_MONO_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
)


def _load_font(
    size: int,
    *,
    monospace: bool = False,
    bold: bool = False,
    italic: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if monospace:
        candidates = _MONO_FONT_CANDIDATES
    elif bold:
        candidates = _FONT_BOLD_CANDIDATES
    elif italic:
        candidates = _FONT_ITALIC_CANDIDATES
    else:
        candidates = _FONT_CANDIDATES
    for path in candidates:
        font_path = Path(path)
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)
    return ImageFont.load_default()


def _line_height(font: ImageFont.FreeTypeFont | ImageFont.ImageFont, extra: int = 10) -> int:
    """Estimate a line height for the given font."""

    height: int
    metrics = getattr(font, "getmetrics", None)
    if callable(metrics):
        ascent, descent = cast(tuple[int, int], metrics())
        height = ascent + descent
    else:
        bbox = font.getbbox("Ag")
        height = int(bbox[3] - bbox[1])
    return height + extra


def _text_width(font: ImageFont.FreeTypeFont | ImageFont.ImageFont, text: str) -> int:
    bbox = font.getbbox(text or " ")
    return int(bbox[2] - bbox[0])


def _wrap_text(
    text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_width: int
) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    words = stripped.split()
    if not words:
        return []

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if _text_width(font, candidate) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _wrap_paragraphs(
    text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_width: int
) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []
    paragraphs = [
        block.replace("\n", " ").strip() for block in normalized.split("\n\n") if block.strip()
    ]
    if not paragraphs:
        return []

    lines: list[str] = []
    for idx, paragraph in enumerate(paragraphs):
        wrapped = _wrap_text(paragraph, font, max_width)
        lines.extend(wrapped)
        if idx < len(paragraphs) - 1:
            lines.append("")
    return lines


def _render_image(
    worksheet: Worksheet,
    *,
    default_width: int = 900,
    margin: int = 64,
    columns: int = 5,
) -> Image.Image:
    title_font = _load_font(40)
    meta_font = _load_font(24)
    instruction_font = _load_font(22)
    problem_font = _load_font(30, monospace=True)

    title_height = _line_height(title_font)
    meta_height = _line_height(meta_font, extra=6)

    formatted_blocks = [format_vertical_problem(problem) for problem in worksheet.problems]
    if not formatted_blocks:
        raise ValueError("Worksheet must contain at least one problem")

    char_width = problem_font.getbbox("0")[2] - problem_font.getbbox("0")[0]
    block_char_width = max(
        max(len(line) for line in lines) if lines else 0 for lines, _ in formatted_blocks
    )
    line_char_width = max((width + 2) for _, width in formatted_blocks)
    block_char_width = max(block_char_width, line_char_width)
    cell_width = int(block_char_width * char_width) + 20
    column_gap = 40
    columns = max(1, min(columns, len(formatted_blocks)))
    rows = math.ceil(len(formatted_blocks) / columns)

    problem_line_height = _line_height(problem_font, extra=0)
    lines_per_block = len(formatted_blocks[0][0])
    line_padding = int(problem_line_height * 1.5)
    block_height = problem_line_height * lines_per_block + line_padding
    row_gap = problem_line_height * 2

    grid_width = columns * cell_width + (columns - 1) * column_gap
    grid_height = rows * block_height + (rows - 1) * row_gap

    total_width = max(default_width, margin * 2 + grid_width)
    content_width = total_width - 2 * margin
    instruction_lines: list[str] = []
    instruction_height = 0
    if worksheet.instructions:
        instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)
        line_height = _line_height(instruction_font, extra=4)
        instruction_height = len(instruction_lines) * line_height
    total_height = margin * 2 + title_height + meta_height + instruction_height + 30 + grid_height

    image = Image.new("RGB", (total_width, total_height), color="white")
    draw = ImageDraw.Draw(image)

    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    y += title_height

    # Name / Date / Score row
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    score_text = "Score: ____ / ____"
    field_spacing = (
        total_width
        - 2 * margin
        - draw.textlength(name_text, font=meta_font)
        - draw.textlength(date_text, font=meta_font)
        - draw.textlength(score_text, font=meta_font)
    )
    field_gap = max(20, field_spacing // 2)
    x = margin
    draw.text((x, y), name_text, font=meta_font, fill="black")
    x += draw.textlength(name_text, font=meta_font) + field_gap
    draw.text((x, y), date_text, font=meta_font, fill="black")
    x += draw.textlength(date_text, font=meta_font) + field_gap
    draw.text((x, y), score_text, font=meta_font, fill="black")
    y += meta_height

    if instruction_lines:
        y += 10
        line_height = _line_height(instruction_font, extra=4)
        for line in instruction_lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += line_height

    y += 20
    problem_start_y = y

    for index, (lines, operand_width) in enumerate(formatted_blocks):
        row = index // columns
        col = index % columns
        block_x = margin + col * (cell_width + column_gap)
        block_y = problem_start_y + row * (block_height + row_gap)
        for line_idx, line in enumerate(lines):
            draw.text(
                (block_x, block_y + line_idx * problem_line_height),
                line,
                font=problem_font,
                fill="black",
            )
        digit_offset = draw.textlength("  ", font=problem_font)
        line_start = block_x + digit_offset
        line_end = line_start + operand_width * char_width
        line_y = block_y + lines_per_block * problem_line_height - int(problem_line_height * 0.15)
        draw.line((line_start, line_y, line_end, line_y), fill="black", width=3)

    return image


def render_worksheet_to_image(worksheet: Worksheet, output_path: str | Path) -> Path:
    """Render worksheet to a PNG image."""
    image = _render_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_worksheet_to_pdf(worksheet: Worksheet, output_path: str | Path) -> Path:
    """Render worksheet to a PDF using Pillow."""
    image = _render_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


def _render_reading_image(
    worksheet: ReadingWorksheet,
    *,
    width: int = 1050,
    margin: int = 72,
) -> Image.Image:
    if not worksheet.questions:
        raise ValueError("Reading worksheet requires at least one question")

    passage_title_font = _load_font(44, bold=True)
    meta_font = _load_font(24)
    section_font = _load_font(28)
    body_font = _load_font(24)
    bold_body_font = _load_font(24, bold=True)
    instruction_font = _load_font(24, italic=True)

    passage_title_height = _line_height(passage_title_font, extra=4)
    meta_line_height = _line_height(meta_font, extra=2)
    name_block_height = meta_line_height * 2
    header_height = max(passage_title_height, name_block_height)
    instruction_line_height = _line_height(instruction_font, extra=4)
    section_height = _line_height(section_font, extra=6)
    body_line_height = _line_height(body_font, extra=6)
    answer_line_height = max(24, int(body_line_height * 0.9))
    section_gap = body_line_height

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)
    passage_lines = _wrap_paragraphs(worksheet.passage, body_font, content_width)

    question_blocks: list[tuple[list[str], int]] = []
    for idx, question in enumerate(worksheet.questions, start=1):
        prompt_lines = _wrap_text(question.prompt, body_font, content_width) or [""]
        prefix = f"{idx}. "
        indent = " " * len(prefix)
        prompt_lines[0] = f"{prefix}{prompt_lines[0]}".rstrip()
        for line_idx in range(1, len(prompt_lines)):
            prompt_lines[line_idx] = f"{indent}{prompt_lines[line_idx]}"
        question_blocks.append((prompt_lines, max(1, question.response_lines)))

    vocab_blocks: list[dict] = []
    for entry in worksheet.vocabulary:
        term_text = f"{entry.term}:"
        term_width = _text_width(bold_body_font, f"{term_text} ")
        remaining_width = max(50, content_width - term_width)
        definition_lines = (
            _wrap_text(entry.definition or "", body_font, remaining_width)
            if entry.definition
            else []
        )
        vocab_blocks.append(
            {
                "term_text": term_text,
                "term_width": term_width,
                "definition_lines": definition_lines,
                "needs_response": entry.definition is None,
                "response_lines": max(1, entry.response_lines),
            }
        )

    total_height = margin + header_height + body_line_height // 2
    if instruction_lines:
        total_height += len(instruction_lines) * instruction_line_height + section_gap // 2
    total_height += max(1, len(passage_lines)) * body_line_height + section_gap

    questions_height = sum(
        len(lines) * body_line_height + resp * answer_line_height for lines, resp in question_blocks
    )
    questions_height += max(0, len(question_blocks) - 1) * (body_line_height // 2)
    total_height += section_height + questions_height + section_gap

    if vocab_blocks:
        vocab_height = 0
        for block in vocab_blocks:
            lines = block["definition_lines"]
            vocab_height += body_line_height  # term line
            if lines:
                vocab_height += max(0, len(lines) - 1) * body_line_height
            if block["needs_response"]:
                vocab_height += block["response_lines"] * answer_line_height
            vocab_height += body_line_height // 3
        total_height += section_height + vocab_height + section_gap + body_line_height

    total_height += margin
    total_height = int(total_height)
    image = Image.new("RGB", (width, total_height), color="white")
    draw = ImageDraw.Draw(image)

    y = margin
    draw.text((margin, y), worksheet.passage_title, font=passage_title_font, fill="black")
    x_right = width - margin
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    name_width = draw.textlength(name_text, font=meta_font)
    date_width = draw.textlength(date_text, font=meta_font)
    draw.text((x_right - name_width, y), name_text, font=meta_font, fill="black")
    draw.text((x_right - date_width, y + meta_line_height), date_text, font=meta_font, fill="black")
    y += header_height
    y += body_line_height // 2

    if instruction_lines:
        for line in instruction_lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += instruction_line_height
        y += section_gap // 2

    for line in passage_lines or [worksheet.passage.strip()]:
        if not line:
            y += body_line_height // 2
            continue
        draw.text((margin, y), line, font=body_font, fill="black")
        y += body_line_height
    y += section_gap

    draw.text((margin, y), "Questions", font=section_font, fill="black")
    y += section_height
    for lines, response_lines in question_blocks:
        for line in lines:
            draw.text((margin, y), line, font=body_font, fill="black")
            y += body_line_height
        for _ in range(response_lines):
            baseline = y + answer_line_height // 2
            draw.line((margin, baseline, margin + content_width, baseline), fill="black", width=2)
            y += answer_line_height
        y += body_line_height // 2
    y += section_gap // 2

    if vocab_blocks:
        draw.text((margin, y), "Vocabulary", font=section_font, fill="black")
        y += section_height
        for block in vocab_blocks:
            term_text = block["term_text"]
            term_width = block["term_width"]
            definition_lines = block["definition_lines"]
            needs_response = block["needs_response"]
            response_lines = block["response_lines"]

            draw.text((margin, y), term_text, font=bold_body_font, fill="black")
            line_start = margin + term_width
            if definition_lines:
                draw.text((line_start, y), definition_lines[0], font=body_font, fill="black")
                for extra_line in definition_lines[1:]:
                    y += body_line_height
                    draw.text((line_start, y), extra_line, font=body_font, fill="black")
            if needs_response:
                baseline = y + body_line_height - int(body_line_height * 0.3)
                draw.line(
                    (line_start, baseline, margin + content_width, baseline), fill="black", width=2
                )
                y += answer_line_height
                for _ in range(response_lines - 1):
                    baseline = y + answer_line_height - int(answer_line_height * 0.4)
                    draw.line(
                        (margin, baseline, margin + content_width, baseline), fill="black", width=2
                    )
                    y += answer_line_height
            else:
                y += body_line_height

            y += body_line_height // 3

        y += body_line_height

    return image


def render_reading_worksheet_to_image(worksheet: ReadingWorksheet, output_path: str | Path) -> Path:
    image = _render_reading_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_reading_worksheet_to_pdf(worksheet: ReadingWorksheet, output_path: str | Path) -> Path:
    image = _render_reading_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


def _render_venn_diagram_image(
    worksheet: VennDiagramWorksheet,
    *,
    width: int = 1050,
    margin: int = 72,
) -> Image.Image:
    """Render a Venn diagram worksheet to an image."""
    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    label_font = _load_font(28, bold=True)
    overlap_label_font = _load_font(24, bold=True)
    body_font = _load_font(22)
    word_bank_font = _load_font(24)

    title_height = _line_height(title_font, extra=4)
    meta_line_height = _line_height(meta_font, extra=2)
    instruction_line_height = _line_height(instruction_font, extra=4)
    label_height = _line_height(label_font, extra=4)
    overlap_label_height = _line_height(overlap_label_font, extra=2)
    body_line_height = _line_height(body_font, extra=4)
    word_bank_height = _line_height(word_bank_font, extra=4)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    # Calculate circle dimensions
    base_radius = max(180, (content_width // 2) - 40)
    circle_radius = min(260, base_radius)
    diagram_height = circle_radius * 2 + 120  # Extra breathing room for labels

    # Calculate total height
    total_height = margin + title_height + meta_line_height * 2 + body_line_height // 2
    if instruction_lines:
        total_height += len(instruction_lines) * instruction_line_height + body_line_height // 2
    total_height += diagram_height + body_line_height

    # Add space for pre-filled items
    max_items = max(
        len(worksheet.left_items), len(worksheet.right_items), len(worksheet.both_items)
    )
    if max_items > 0:
        total_height += label_height + max_items * body_line_height + body_line_height

    # Word bank section
    if worksheet.word_bank:
        total_height += label_height
        word_bank_text = ", ".join(entry.text for entry in worksheet.word_bank)
        word_bank_lines = _wrap_text(word_bank_text, word_bank_font, content_width)
        total_height += len(word_bank_lines) * word_bank_height + body_line_height

    total_height += margin
    total_height = int(total_height)

    image = Image.new("RGB", (width, total_height), color="white")
    draw = ImageDraw.Draw(image)

    y = margin

    # Title
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    y += title_height

    # Name / Date row
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    draw.text((margin, y), name_text, font=meta_font, fill="black")
    draw.text(
        (width - margin - _text_width(meta_font, date_text), y),
        date_text,
        font=meta_font,
        fill="black",
    )
    y += meta_line_height * 2

    # Instructions
    if instruction_lines:
        for line in instruction_lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += instruction_line_height
        y += body_line_height // 2

    # Draw Venn diagram circles
    left_center_x = margin + circle_radius
    right_center_x = width - margin - circle_radius
    center_distance = right_center_x - left_center_x
    diagram_center_x = (left_center_x + right_center_x) // 2
    circle_center_y = y + circle_radius + 20

    # Draw circles (outline only)
    left_bbox = (
        left_center_x - circle_radius,
        circle_center_y - circle_radius,
        left_center_x + circle_radius,
        circle_center_y + circle_radius,
    )
    right_bbox = (
        right_center_x - circle_radius,
        circle_center_y - circle_radius,
        right_center_x + circle_radius,
        circle_center_y + circle_radius,
    )
    draw.ellipse(left_bbox, outline="black", width=3)
    draw.ellipse(right_bbox, outline="black", width=3)

    # Draw labels
    both_label_x = diagram_center_x
    label_top_y = circle_center_y - circle_radius + 25
    # Position overlap label near top of intersection for readability
    half_distance = center_distance / 2
    overlap_depth = math.sqrt(max(circle_radius**2 - half_distance**2, 0))
    overlap_top_y = circle_center_y - overlap_depth
    overlap_label_y = overlap_top_y + 10

    draw.text(
        (left_center_x - _text_width(label_font, worksheet.left_label) // 2, label_top_y),
        worksheet.left_label,
        font=label_font,
        fill="black",
    )
    draw.text(
        (right_center_x - _text_width(label_font, worksheet.right_label) // 2, label_top_y),
        worksheet.right_label,
        font=label_font,
        fill="black",
    )
    overlap_text_width = _text_width(overlap_label_font, worksheet.both_label)
    overlap_text_x = both_label_x - overlap_text_width // 2
    overlap_padding = 6
    draw.rectangle(
        (
            overlap_text_x - overlap_padding,
            overlap_label_y - overlap_padding,
            overlap_text_x + overlap_text_width + overlap_padding,
            overlap_label_y + overlap_label_height + overlap_padding,
        ),
        fill="white",
    )
    draw.text(
        (overlap_text_x, overlap_label_y),
        worksheet.both_label,
        font=overlap_label_font,
        fill="black",
    )

    y = circle_center_y + circle_radius + 50

    # Pre-filled items section
    if worksheet.left_items or worksheet.right_items or worksheet.both_items:
        y += body_line_height // 2
        col_width = content_width // 3

        # Column headers
        draw.text((margin, y), f"{worksheet.left_label}:", font=label_font, fill="black")
        draw.text(
            (margin + col_width, y), f"{worksheet.both_label}:", font=label_font, fill="black"
        )
        draw.text(
            (margin + col_width * 2, y), f"{worksheet.right_label}:", font=label_font, fill="black"
        )
        y += label_height

        for i in range(max_items):
            if i < len(worksheet.left_items):
                draw.text((margin, y), f"• {worksheet.left_items[i]}", font=body_font, fill="black")
            if i < len(worksheet.both_items):
                draw.text(
                    (margin + col_width, y),
                    f"• {worksheet.both_items[i]}",
                    font=body_font,
                    fill="black",
                )
            if i < len(worksheet.right_items):
                draw.text(
                    (margin + col_width * 2, y),
                    f"• {worksheet.right_items[i]}",
                    font=body_font,
                    fill="black",
                )
            y += body_line_height

        y += body_line_height

    # Word bank section
    if worksheet.word_bank:
        draw.text((margin, y), "Word Bank:", font=label_font, fill="black")
        y += label_height

        word_bank_text = ", ".join(entry.text for entry in worksheet.word_bank)
        word_bank_lines = _wrap_text(word_bank_text, word_bank_font, content_width)
        for line in word_bank_lines:
            draw.text((margin, y), line, font=word_bank_font, fill="black")
            y += word_bank_height

    return image


def render_venn_diagram_to_image(worksheet: VennDiagramWorksheet, output_path: str | Path) -> Path:
    """Render Venn diagram worksheet to a PNG image."""
    image = _render_venn_diagram_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_venn_diagram_to_pdf(worksheet: VennDiagramWorksheet, output_path: str | Path) -> Path:
    """Render Venn diagram worksheet to a PDF."""
    image = _render_venn_diagram_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


def _render_feature_matrix_image(
    worksheet: FeatureMatrixWorksheet,
    *,
    width: int = 1050,
    margin: int = 72,
) -> Image.Image:
    """Render a feature matrix worksheet to an image."""
    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    header_font = _load_font(22, bold=True)
    body_font = _load_font(22)

    title_height = _line_height(title_font, extra=4)
    meta_line_height = _line_height(meta_font, extra=2)
    instruction_line_height = _line_height(instruction_font, extra=4)
    row_height = _line_height(body_font, extra=8)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    # Calculate column widths
    num_cols = len(worksheet.properties) + 1  # +1 for item name column
    item_col_width = max(150, content_width // (num_cols + 1))  # Wider first column
    prop_col_width = (content_width - item_col_width) // max(1, len(worksheet.properties))

    # Calculate total height
    total_height = margin + title_height + meta_line_height * 2 + row_height // 2
    if instruction_lines:
        total_height += len(instruction_lines) * instruction_line_height + row_height // 2
    total_height += row_height  # Header row
    total_height += len(worksheet.items) * row_height
    total_height += margin

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    y = margin

    # Title
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    y += title_height

    # Name / Date row
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    draw.text((margin, y), name_text, font=meta_font, fill="black")
    draw.text(
        (width - margin - _text_width(meta_font, date_text), y),
        date_text,
        font=meta_font,
        fill="black",
    )
    y += meta_line_height * 2

    # Instructions
    if instruction_lines:
        for line in instruction_lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += instruction_line_height
        y += row_height // 2

    # Draw table
    table_x = margin
    table_y = y

    # Header row
    draw.text((table_x + 5, table_y + 4), "Item", font=header_font, fill="black")
    x = table_x + item_col_width
    for prop in worksheet.properties:
        # Center property text
        prop_width = _text_width(header_font, prop)
        prop_x = x + (prop_col_width - prop_width) // 2
        draw.text((prop_x, table_y + 4), prop, font=header_font, fill="black")
        x += prop_col_width

    # Draw header border
    draw.line(
        (table_x, table_y + row_height, table_x + content_width, table_y + row_height),
        fill="black",
        width=2,
    )
    y = table_y + row_height

    # Data rows
    for item in worksheet.items:
        # Item name
        item_text = item.name
        if _text_width(body_font, item_text) > item_col_width - 10:
            # Truncate with ellipsis if too long
            while (
                _text_width(body_font, item_text + "...") > item_col_width - 10
                and len(item_text) > 1
            ):
                item_text = item_text[:-1]
            item_text += "..."
        draw.text((table_x + 5, y + 4), item_text, font=body_font, fill="black")

        # Checkboxes
        x = table_x + item_col_width
        for prop in worksheet.properties:
            checkbox_size = 18
            checkbox_x = x + (prop_col_width - checkbox_size) // 2
            checkbox_y = y + (row_height - checkbox_size) // 2

            # Draw checkbox
            draw.rectangle(
                (checkbox_x, checkbox_y, checkbox_x + checkbox_size, checkbox_y + checkbox_size),
                outline="black",
                width=2,
            )

            # Fill if answered
            if (
                worksheet.show_answers
                and item.checked_properties
                and prop in item.checked_properties
            ):
                # Draw checkmark
                draw.line(
                    (
                        checkbox_x + 3,
                        checkbox_y + checkbox_size // 2,
                        checkbox_x + checkbox_size // 3,
                        checkbox_y + checkbox_size - 4,
                    ),
                    fill="black",
                    width=2,
                )
                draw.line(
                    (
                        checkbox_x + checkbox_size // 3,
                        checkbox_y + checkbox_size - 4,
                        checkbox_x + checkbox_size - 3,
                        checkbox_y + 4,
                    ),
                    fill="black",
                    width=2,
                )

            x += prop_col_width

        # Row separator
        y += row_height
        draw.line((table_x, y, table_x + content_width, y), fill="gray", width=1)

    # Vertical lines
    x = table_x + item_col_width
    for _ in worksheet.properties:
        draw.line((x, table_y, x, y), fill="gray", width=1)
        x += prop_col_width

    # Outer border
    draw.rectangle((table_x, table_y, table_x + content_width, y), outline="black", width=2)

    return image


def render_feature_matrix_to_image(
    worksheet: FeatureMatrixWorksheet, output_path: str | Path
) -> Path:
    """Render feature matrix worksheet to a PNG image."""
    image = _render_feature_matrix_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_feature_matrix_to_pdf(
    worksheet: FeatureMatrixWorksheet, output_path: str | Path
) -> Path:
    """Render feature matrix worksheet to a PDF."""
    image = _render_feature_matrix_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


def _render_odd_one_out_image(
    worksheet: OddOneOutWorksheet,
    *,
    width: int = 1050,
    margin: int = 72,
) -> Image.Image:
    """Render an odd-one-out worksheet to an image."""
    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    item_font = _load_font(28)
    number_font = _load_font(24, bold=True)
    answer_font = _load_font(20, italic=True)
    body_font = _load_font(22)

    title_height = _line_height(title_font, extra=4)
    meta_line_height = _line_height(meta_font, extra=2)
    instruction_line_height = _line_height(instruction_font, extra=4)
    item_line_height = _line_height(item_font, extra=10)
    reasoning_line_height = _line_height(body_font, extra=6)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    # Calculate total height
    total_height = margin + title_height + meta_line_height * 2 + reasoning_line_height // 2
    if instruction_lines:
        total_height += (
            len(instruction_lines) * instruction_line_height + reasoning_line_height // 2
        )

    for _ in worksheet.rows:
        total_height += item_line_height + 10  # Items row
        if worksheet.show_answers:
            total_height += reasoning_line_height * 2  # Answer + explanation
        else:
            total_height += reasoning_line_height * (
                worksheet.reasoning_lines + 1
            )  # "Why?" + lines
        total_height += reasoning_line_height  # Gap between rows

    total_height += margin

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    y = margin

    # Title
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    y += title_height

    # Name / Date row
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    draw.text((margin, y), name_text, font=meta_font, fill="black")
    draw.text(
        (width - margin - _text_width(meta_font, date_text), y),
        date_text,
        font=meta_font,
        fill="black",
    )
    y += meta_line_height * 2

    # Instructions
    if instruction_lines:
        for line in instruction_lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += instruction_line_height
        y += reasoning_line_height // 2

    # Rows
    for idx, row in enumerate(worksheet.rows, start=1):
        # Row number
        number_text = f"{idx}."
        draw.text((margin, y), number_text, font=number_font, fill="black")

        # Items spread across width
        items_x_start = margin + 40
        items_area_width = content_width - 40
        item_spacing = items_area_width // len(row.items)

        for item_idx, item_text in enumerate(row.items):
            item_x = items_x_start + item_idx * item_spacing
            # Draw box around each item
            text_width = _text_width(item_font, item_text)
            box_padding = 10
            box_x1 = item_x - box_padding
            box_y1 = y - 5
            box_x2 = item_x + text_width + box_padding
            box_y2 = y + item_line_height - 10

            draw.rectangle((box_x1, box_y1, box_x2, box_y2), outline="black", width=2)
            draw.text((item_x, y), item_text, font=item_font, fill="black")

        y += item_line_height + 10

        if worksheet.show_answers and row.odd_item:
            answer_text = f"Answer: {row.odd_item}"
            draw.text((margin + 40, y), answer_text, font=answer_font, fill="black")
            y += reasoning_line_height
            if row.explanation:
                explanation_text = f"Reason: {row.explanation}"
                explanation_lines = _wrap_text(explanation_text, answer_font, content_width - 40)
                for line in explanation_lines:
                    draw.text((margin + 40, y), line, font=answer_font, fill="black")
                    y += reasoning_line_height
        else:
            # "Why?" prompt
            draw.text((margin + 40, y), "Why?", font=body_font, fill="black")
            y += reasoning_line_height

            # Blank lines for reasoning
            for _ in range(worksheet.reasoning_lines):
                baseline = y + reasoning_line_height // 2
                draw.line((margin + 40, baseline, width - margin, baseline), fill="black", width=1)
                y += reasoning_line_height

        y += reasoning_line_height  # Gap between rows

    return image


def render_odd_one_out_to_image(worksheet: OddOneOutWorksheet, output_path: str | Path) -> Path:
    """Render odd-one-out worksheet to a PNG image."""
    image = _render_odd_one_out_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_odd_one_out_to_pdf(worksheet: OddOneOutWorksheet, output_path: str | Path) -> Path:
    """Render odd-one-out worksheet to a PDF."""
    image = _render_odd_one_out_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


def _render_tree_map_image(
    worksheet: TreeMapWorksheet,
    *,
    width: int = 1050,
    margin: int = 72,
) -> Image.Image:
    """Render a tree map worksheet to an image."""
    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    root_font = _load_font(32, bold=True)
    branch_font = _load_font(26, bold=True)
    body_font = _load_font(22)
    word_bank_font = _load_font(24)

    title_height = _line_height(title_font, extra=4)
    meta_line_height = _line_height(meta_font, extra=2)
    instruction_line_height = _line_height(instruction_font, extra=4)
    root_height = _line_height(root_font, extra=6)
    branch_height = _line_height(branch_font, extra=4)
    slot_height = _line_height(body_font, extra=8)
    word_bank_height = _line_height(word_bank_font, extra=4)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    # Calculate total height
    total_height = margin + title_height + meta_line_height * 2 + slot_height // 2
    if instruction_lines:
        total_height += len(instruction_lines) * instruction_line_height + slot_height // 2

    total_height += root_height + 30  # Root label + gap

    # Branches section
    max_slots = max((len(b.slots) for b in worksheet.branches), default=3)
    branch_section_height = branch_height + max_slots * slot_height + 30
    total_height += branch_section_height

    # Word bank section
    if worksheet.word_bank:
        total_height += branch_height
        word_bank_text = ", ".join(worksheet.word_bank)
        word_bank_lines = _wrap_text(word_bank_text, word_bank_font, content_width)
        total_height += len(word_bank_lines) * word_bank_height + slot_height

    total_height += margin

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    y = margin

    # Title
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    y += title_height

    # Name / Date row
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    draw.text((margin, y), name_text, font=meta_font, fill="black")
    draw.text(
        (width - margin - _text_width(meta_font, date_text), y),
        date_text,
        font=meta_font,
        fill="black",
    )
    y += meta_line_height * 2

    # Instructions
    if instruction_lines:
        for line in instruction_lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += instruction_line_height
        y += slot_height // 2

    # Root label (centered with box)
    root_text_width = _text_width(root_font, worksheet.root_label)
    root_x = (width - root_text_width) // 2
    root_box_padding = 15
    draw.rectangle(
        (
            root_x - root_box_padding,
            y,
            root_x + root_text_width + root_box_padding,
            y + root_height,
        ),
        outline="black",
        width=3,
    )
    draw.text((root_x, y + 3), worksheet.root_label, font=root_font, fill="black")
    root_center_x = width // 2
    root_bottom_y = y + root_height
    y += root_height + 15

    # Draw vertical line from root
    draw.line((root_center_x, root_bottom_y, root_center_x, y + 10), fill="black", width=2)
    y += 10

    # Calculate branch positions
    num_branches = len(worksheet.branches)
    if num_branches > 0:
        branch_spacing = content_width // num_branches
        branch_start_x = margin + branch_spacing // 2

        # Draw horizontal connector line
        if num_branches > 1:
            left_branch_x = branch_start_x
            right_branch_x = branch_start_x + (num_branches - 1) * branch_spacing
            draw.line((left_branch_x, y, right_branch_x, y), fill="black", width=2)

        # Draw branches
        branches_y = y + 10
        for idx, branch in enumerate(worksheet.branches):
            branch_x = branch_start_x + idx * branch_spacing

            # Vertical line to branch
            draw.line((branch_x, y, branch_x, branches_y), fill="black", width=2)

            # Branch label (centered with box)
            label_width = _text_width(branch_font, branch.label)
            label_x = branch_x - label_width // 2
            label_box_padding = 8
            draw.rectangle(
                (
                    label_x - label_box_padding,
                    branches_y,
                    label_x + label_width + label_box_padding,
                    branches_y + branch_height,
                ),
                outline="black",
                width=2,
            )
            draw.text((label_x, branches_y + 2), branch.label, font=branch_font, fill="black")

            # Slots under branch
            slot_y = branches_y + branch_height + 10
            slot_width = min(branch_spacing - 20, 180)
            for slot in branch.slots:
                if slot.text:
                    # Pre-filled slot
                    slot_text = slot.text
                    text_width = _text_width(body_font, slot_text)
                    text_x = branch_x - text_width // 2
                    draw.text((text_x, slot_y), slot_text, font=body_font, fill="black")
                else:
                    # Blank line
                    line_x1 = branch_x - slot_width // 2
                    line_x2 = branch_x + slot_width // 2
                    line_y = slot_y + slot_height - 10
                    draw.line((line_x1, line_y, line_x2, line_y), fill="black", width=2)
                slot_y += slot_height

        y = branches_y + branch_height + max_slots * slot_height + 20

    # Word bank section
    if worksheet.word_bank:
        draw.text((margin, y), "Word Bank:", font=branch_font, fill="black")
        y += branch_height

        word_bank_text = ", ".join(worksheet.word_bank)
        word_bank_lines = _wrap_text(word_bank_text, word_bank_font, content_width)
        for line in word_bank_lines:
            draw.text((margin, y), line, font=word_bank_font, fill="black")
            y += word_bank_height

    return image


def render_tree_map_to_image(worksheet: TreeMapWorksheet, output_path: str | Path) -> Path:
    """Render tree map worksheet to a PNG image."""
    image = _render_tree_map_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_tree_map_to_pdf(worksheet: TreeMapWorksheet, output_path: str | Path) -> Path:
    """Render tree map worksheet to a PDF."""
    image = _render_tree_map_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


__all__ = [
    "render_worksheet_to_image",
    "render_worksheet_to_pdf",
    "render_reading_worksheet_to_image",
    "render_reading_worksheet_to_pdf",
    "render_venn_diagram_to_image",
    "render_venn_diagram_to_pdf",
    "render_feature_matrix_to_image",
    "render_feature_matrix_to_pdf",
    "render_odd_one_out_to_image",
    "render_odd_one_out_to_pdf",
    "render_tree_map_to_image",
    "render_tree_map_to_pdf",
]
