"""Rendering helpers for Worksheet objects."""

from __future__ import annotations

import math
import random
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
        HandwritingWorksheet,
        AlphabetWorksheet,
        PixelCopyWorksheet,
        MatchingWorksheet,
        SequencingWorksheet,
        TChartWorksheet,
        FillBlankWorksheet,
        WordSortWorksheet,
    )
except ImportError:  # Fallback when executed outside package context
    CURRENT_DIR = os.path.dirname(__file__)
    if CURRENT_DIR not in sys.path:
        sys.path.insert(0, CURRENT_DIR)
    from worksheets import ReadingWorksheet, Worksheet, format_vertical_problem  # type: ignore
    from worksheets import (
        VennDiagramWorksheet,
        FeatureMatrixWorksheet,
        OddOneOutWorksheet,
        TreeMapWorksheet,
        HandwritingWorksheet,
        AlphabetWorksheet,
        PixelCopyWorksheet,
        MatchingWorksheet,
        SequencingWorksheet,
        TChartWorksheet,
        FillBlankWorksheet,
        WordSortWorksheet,
    )  # type: ignore

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


def _prepare_sprite(image_path: str, size: int) -> Image.Image | None:
    """Load and resize a sprite, preserving pixel art if small."""
    if not os.path.exists(image_path):
        return None
    try:
        img = Image.open(image_path).convert("RGBA")
        if img.width < size or img.height < size:
            # Upscale small images using NEAREST to keep pixel art crisp
            scale = size / max(img.width, img.height)
            new_size = (int(img.width * scale), int(img.height * scale))
            return img.resize(new_size, Image.Resampling.NEAREST)
        else:
            # Downscale large images using LANCZOS
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            return img
    except Exception:
        return None


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

        for item_idx, item in enumerate(row.items):
            item_x = items_x_start + item_idx * item_spacing

            # Determine content dimensions
            content_w, content_h = 0, 0
            max_sprite_h = item_line_height - 10
            sprite = _prepare_sprite(item.image_path, max_sprite_h) if item.image_path else None
            if sprite:
                content_w, content_h = sprite.size

            if item.text:
                text_w = _text_width(item_font, item.text)
                content_w = max(content_w, text_w)
                content_h = max(content_h, item_line_height - 10)

            # Draw box around each item
            box_padding = 10
            box_x1 = item_x - box_padding
            box_y1 = y - 5
            box_x2 = item_x + content_w + box_padding
            box_y2 = y + item_line_height - 10

            draw.rectangle((box_x1, box_y1, box_x2, box_y2), outline="black", width=2)

            if sprite:
                image.paste(sprite, (int(item_x), int(y)), sprite)
                if item.text:
                    # Draw text below image if both exist (though usually one or the other)
                    draw.text(
                        (item_x, y + sprite.height + 2), item.text, font=item_font, fill="black"
                    )
            elif item.text:
                draw.text((item_x, y), item.text, font=item_font, fill="black")

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

    return output


def _draw_primary_lines(
    draw: ImageDraw.ImageDraw,
    x_start: float,
    x_end: float,
    y_start: float,
    line_height: int = 60,
    line_color: tuple[int, int, int] = (150, 150, 150),
    bottom_rail: bool = False,
) -> None:
    """Draw handwriting paper style lines (Solid, Dashed, Solid)."""
    top_y = y_start
    mid_y = y_start + (line_height // 2)
    bot_y = y_start + line_height

    # Draw Top (Solid)
    draw.line([(x_start, top_y), (x_end, top_y)], fill=line_color, width=2)

    # Draw Bottom
    if bottom_rail:
        # Draw thick short segments (underscores) to encourage tighter spacing
        segment_len = 40
        gap_len = 15
        for x in range(int(x_start), int(x_end), segment_len + gap_len):
            draw.line(
                [(x, bot_y), (min(x + segment_len, x_end), bot_y)],
                fill=line_color,
                width=4,
            )
    else:
        # Draw Bottom (Solid)
        draw.line([(x_start, bot_y), (x_end, bot_y)], fill=line_color, width=2)

    # Draw Middle (Dashed)
    dash_len = 10
    for x in range(int(x_start), int(x_end), dash_len * 2):
        draw.line(
            [(x, mid_y), (min(x + dash_len, x_end), mid_y)],
            fill=line_color,
            width=1,
        )


def _render_handwriting_image(
    worksheet: HandwritingWorksheet,
    *,
    width: int = 1050,
    margin: int = 72,
) -> Image.Image:
    """Render a handwriting worksheet to an image."""
    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    label_font = _load_font(32, bold=True)
    sub_label_font = _load_font(18)

    title_height = _line_height(title_font, extra=4)
    meta_line_height = _line_height(meta_font, extra=2)
    instruction_line_height = _line_height(instruction_font, extra=4)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    # Header height
    header_height = margin + title_height + meta_line_height * 2 + 20
    if instruction_lines:
        header_height += len(instruction_lines) * instruction_line_height + 10

    # Grid settings
    row_height = 240
    total_height = header_height + worksheet.rows * row_height + margin

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    # Header
    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    y += title_height

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

    if instruction_lines:
        for line in instruction_lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += instruction_line_height
        y += 10

    # Grid items
    col_width = content_width // worksheet.cols
    sprite_size = 140

    for i, item in enumerate(worksheet.items[: worksheet.rows * worksheet.cols]):
        row = i // worksheet.cols
        col = i % worksheet.cols

        cell_x = margin + col * col_width
        cell_y = y + row * row_height

        # Image
        sprite = _prepare_sprite(item.image_path, sprite_size) if item.image_path else None
        if sprite:
            offset_x = (sprite_size - sprite.width) // 2
            offset_y = (sprite_size - sprite.height) // 2
            image.paste(sprite, (int(cell_x + offset_x), int(cell_y + offset_y)), sprite)

        # Text label
        text_x = cell_x + sprite_size + 20
        text_y = cell_y + 30
        draw.text((text_x, text_y), item.text, font=label_font, fill="black")

        if item.sub_label:
            draw.text((text_x, text_y + 40), item.sub_label, font=sub_label_font, fill="gray")

        # Handwriting lines
        line_start_x = text_x
        line_end_x = cell_x + col_width - 20
        line_start_y = cell_y + sprite_size - 35
        bottom_rail = worksheet.metadata.get("bottom_rail", False) if worksheet.metadata else False
        _draw_primary_lines(
            draw,
            line_start_x,
            line_end_x,
            line_start_y,
            line_height=80,
            bottom_rail=bottom_rail,
        )

    return image


def _render_pixel_copy_image(
    worksheet: PixelCopyWorksheet,
    *,
    width: int = 1050,
    margin: int = 72,
) -> Image.Image:
    """Render a pixel copy worksheet to an image."""
    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)

    title_height = _line_height(title_font, extra=4)
    meta_line_height = _line_height(meta_font, extra=2)
    instruction_line_height = _line_height(instruction_font, extra=4)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    box_size = (content_width - 60) // 2
    header_height = margin + title_height + meta_line_height * 2 + 20
    if instruction_lines:
        header_height += len(instruction_lines) * instruction_line_height + 20

    total_height = header_height + box_size + margin + 40

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    # Header
    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    y += title_height

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

    if instruction_lines:
        for line in instruction_lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += instruction_line_height
        y += 20

    # Grid Setup
    grid_size = worksheet.grid_size
    cell_size = box_size / grid_size

    # Left side: Reference Image
    left_x = margin
    if worksheet.image_path and os.path.exists(worksheet.image_path):
        try:
            source = Image.open(worksheet.image_path).convert("RGBA")
            bg = Image.new("RGBA", source.size, "WHITE")
            bg.alpha_composite(source)
            pixelated = bg.resize((grid_size, grid_size), Image.Resampling.NEAREST)
            scaled = pixelated.resize((box_size, box_size), Image.Resampling.NEAREST)
            image.paste(scaled, (int(left_x), int(y)))
        except Exception:
            draw.rectangle((left_x, y, left_x + box_size, y + box_size), outline="black")
    else:
        draw.rectangle((left_x, y, left_x + box_size, y + box_size), outline="black")

    # Right side: Empty Grid
    right_x = margin + box_size + 60
    draw.rectangle((right_x, y, right_x + box_size, y + box_size), outline="black", width=2)

    # Draw grid lines
    for i in range(grid_size + 1):
        offset = i * cell_size
        draw.line([(left_x + offset, y), (left_x + offset, y + box_size)], fill="black", width=1)
        draw.line([(right_x + offset, y), (right_x + offset, y + box_size)], fill="black", width=1)
        draw.line([(left_x, y + offset), (left_x + box_size, y + offset)], fill="black", width=1)
        draw.line([(right_x, y + offset), (right_x + box_size, y + offset)], fill="black", width=1)

    return image


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


def render_handwriting_to_image(worksheet: HandwritingWorksheet, output_path: str | Path) -> Path:
    """Render handwriting worksheet to a PNG image."""
    image = _render_handwriting_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_handwriting_to_pdf(worksheet: HandwritingWorksheet, output_path: str | Path) -> Path:
    """Render handwriting worksheet to a PDF."""
    image = _render_handwriting_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


def render_pixel_copy_to_image(worksheet: PixelCopyWorksheet, output_path: str | Path) -> Path:
    """Render pixel copy worksheet to a PNG image."""
    image = _render_pixel_copy_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_pixel_copy_to_pdf(worksheet: PixelCopyWorksheet, output_path: str | Path) -> Path:
    """Render pixel copy worksheet to a PDF."""
    image = _render_pixel_copy_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


def _render_alphabet_image(
    worksheet: AlphabetWorksheet,
    *,
    width: int = 1050,
    margin: int = 72,
) -> Image.Image:
    """Render an alphabet worksheet to an image."""
    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    centerpiece_font = _load_font(200, bold=True)
    reading_header_font = _load_font(32, bold=True)
    reading_word_font = _load_font(40)
    trace_font = _load_font(80)

    title_height = _line_height(title_font, extra=4)
    meta_line_height = _line_height(meta_font, extra=2)
    instruction_line_height = _line_height(instruction_font, extra=4)

    content_width = width - 2 * margin

    # Calculate total height (approximate)
    header_height = margin + title_height + meta_line_height * 2 + 20
    if worksheet.instructions:
        header_height += (
            _line_height(instruction_font)
            * len(_wrap_text(worksheet.instructions, instruction_font, content_width))
            + 20
        )

    centerpiece_height = 250
    handwriting_section_height = 550
    reading_section_height = 400

    total_height = (
        header_height
        + centerpiece_height
        + handwriting_section_height
        + reading_section_height
        + margin
    )

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    # Header
    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    y += title_height

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

    if worksheet.instructions:
        lines = _wrap_text(worksheet.instructions, instruction_font, content_width)
        for line in lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += instruction_line_height
        y += 20

    # Centerpiece and Character
    centerpiece_text = f"{worksheet.letter} {worksheet.letter.lower()}"
    text_w = _text_width(centerpiece_font, centerpiece_text)

    # Position centerpiece slightly left of center to make room for character
    text_x = margin + (content_width // 2) - (text_w // 2) - 50
    draw.text((text_x, y + 20), centerpiece_text, font=centerpiece_font, fill="black")

    if worksheet.character_image_path:
        sprite_size = 220
        sprite = _prepare_sprite(worksheet.character_image_path, sprite_size)
        if sprite:
            image.paste(sprite, (int(width - margin - sprite.width), int(y + 20)), sprite)

    y += centerpiece_height

    # Handwriting Lines
    y += 20
    line_spacing = 130

    # Line 1: Trace-a-long (Uppercase, Fading)
    line_y = y
    _draw_primary_lines(draw, margin, width - margin, line_y, line_height=80)

    trace_char_upper = worksheet.letter
    trace_x = margin + 20
    for i in range(4):
        # Calculate fade: 0 (black) to ~180 (light gray)
        alpha = int(i * 60)
        color = (alpha, alpha, alpha)
        draw.text((trace_x, line_y + 5), trace_char_upper, font=trace_font, fill=color)
        trace_x += _text_width(trace_font, trace_char_upper) + 60

    # Line 2: Trace-a-long (Lowercase, Fading)
    line_y += line_spacing
    _draw_primary_lines(draw, margin, width - margin, line_y, line_height=80)

    trace_char_lower = worksheet.letter.lower()
    trace_x = margin + 20
    for i in range(4):
        alpha = int(i * 60)
        color = (alpha, alpha, alpha)
        draw.text((trace_x, line_y + 5), trace_char_lower, font=trace_font, fill=color)
        trace_x += _text_width(trace_font, trace_char_lower) + 60

    # Line 3: Free practice (Frame)
    line_y += line_spacing
    _draw_primary_lines(draw, margin, width - margin, line_y, line_height=80)

    # Line 4: Spacing practice (Double-underscores)
    line_y += line_spacing
    underscore_y = line_y + 60
    for x in range(margin + 40, width - margin - 40, 150):
        draw.text((x, underscore_y), "__  __", font=reading_word_font, fill="black")

    y = line_y + line_spacing

    # Reading Sections
    y += 40
    col_width = content_width // 2

    # Section: Starts with
    draw.text(
        (margin, y), f"Starts with {worksheet.letter}", font=reading_header_font, fill="black"
    )
    word_y = y + 50
    for word in worksheet.starting_words[:4]:
        draw.text((margin + 20, word_y), f"• {word}", font=reading_word_font, fill="black")
        word_y += 60

    # Section: Contains
    draw.text(
        (margin + col_width, y),
        f"Contains {worksheet.letter}",
        font=reading_header_font,
        fill="black",
    )
    word_y = y + 50
    for word in worksheet.containing_words[:4]:
        draw.text(
            (margin + col_width + 20, word_y), f"• {word}", font=reading_word_font, fill="black"
        )
        word_y += 60

    return image


def render_alphabet_to_image(worksheet: AlphabetWorksheet, output_path: str | Path) -> Path:
    """Render alphabet worksheet to a PNG image."""
    image = _render_alphabet_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_alphabet_to_pdf(worksheet: AlphabetWorksheet, output_path: str | Path) -> Path:
    """Render alphabet worksheet to a PDF."""
    image = _render_alphabet_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


def _render_matching_image(
    worksheet: MatchingWorksheet,
    *,
    width: int = 1050,
    margin: int = 72,
) -> Image.Image:
    """Render a matching worksheet to an image."""
    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    word_font = _load_font(48, bold=True)

    title_height = _line_height(title_font, extra=4)
    meta_line_height = _line_height(meta_font, extra=2)
    instruction_line_height = _line_height(instruction_font, extra=4)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    max_rows = max(len(worksheet.left_items), len(worksheet.right_items))
    row_height = 200
    header_height = margin + title_height + meta_line_height * 2 + 20
    if instruction_lines:
        header_height += len(instruction_lines) * instruction_line_height + 20

    total_height = header_height + max_rows * row_height + margin

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    # Header
    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    y += title_height

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

    if instruction_lines:
        for line in instruction_lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += instruction_line_height
        y += 20

    # Content
    sprite_size = 140
    dot_radius = 8
    left_x = margin + 30
    right_x = width - margin - 30
    left_dot_x = left_x + 220
    right_dot_x = right_x - 220

    for i in range(max_rows):
        row_y_center = y + i * row_height + row_height // 2

        # Left Column
        if i < len(worksheet.left_items):
            item = worksheet.left_items[i]
            if item.text:
                draw.text((left_x, row_y_center - 30), item.text, font=word_font, fill="black")
            sprite = _prepare_sprite(item.image_path, sprite_size) if item.image_path else None
            if sprite:
                image.paste(sprite, (int(left_x), int(row_y_center - sprite.height // 2)), sprite)

            # Left Dot
            draw.ellipse(
                [
                    left_dot_x - dot_radius,
                    row_y_center - dot_radius,
                    left_dot_x + dot_radius,
                    row_y_center + dot_radius,
                ],
                fill="black",
            )

        # Right Column
        if i < len(worksheet.right_items):
            item = worksheet.right_items[i]
            if item.text:
                draw.text(
                    (right_x - _text_width(word_font, item.text), row_y_center - 30),
                    item.text,
                    font=word_font,
                    fill="black",
                )
            sprite = _prepare_sprite(item.image_path, sprite_size) if item.image_path else None
            if sprite:
                if item.as_shadow:
                    # Create silhouette
                    mask = sprite.getchannel("A")
                    sprite = Image.new("RGBA", sprite.size, "BLACK")
                    sprite.putalpha(mask)
                image.paste(
                    sprite,
                    (int(right_x - sprite.width), int(row_y_center - sprite.height // 2)),
                    sprite,
                )

            # Right Dot
            draw.ellipse(
                [
                    right_dot_x - dot_radius,
                    row_y_center - dot_radius,
                    right_dot_x + dot_radius,
                    row_y_center + dot_radius,
                ],
                fill="black",
            )

        # Row Separator (programmatic dash)
        if i < max_rows - 1:
            sep_y = y + (i + 1) * row_height
            for dot_x in range(margin, width - margin, 40):
                draw.line([(dot_x, sep_y), (dot_x + 20, sep_y)], fill=(220, 220, 220), width=2)

    return image


def render_matching_to_image(worksheet: MatchingWorksheet, output_path: str | Path) -> Path:
    """Render matching worksheet to a PNG image."""
    image = _render_matching_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_matching_to_pdf(worksheet: MatchingWorksheet, output_path: str | Path) -> Path:
    """Render matching worksheet to a PDF."""
    image = _render_matching_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


# ---------------------------------------------------------------------------
# Sequencing worksheet renderer
# ---------------------------------------------------------------------------


def _render_sequencing_image(
    worksheet: SequencingWorksheet,
    *,
    width: int = 1050,
    margin: int = 72,
) -> Image.Image:
    """Render a sequencing (cut-and-order) worksheet to a PIL Image.

    Each step is displayed as a dashed-border card with:
    - A number box in the top-left (blank for students, filled for answer key)
    - Optional image on the left inside the card
    - Step text on the right inside the card
    - Dashed border and scissors icon hint at the top to indicate cut-out cards

    Cards are arranged in a 2-column grid.
    """
    COLS = 2
    CARD_PADDING = 16
    SPRITE_SIZE = 100
    NUM_BOX_SIZE = 40
    DASH_COLOR = (100, 100, 100)
    CARD_BG = (252, 252, 252)
    BORDER_COLOR = (60, 60, 60)

    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    step_font = _load_font(26, bold=True)
    num_font = _load_font(22, bold=True)
    activity_font = _load_font(28, bold=True)
    scissors_font = _load_font(18, italic=True)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    title_h = _line_height(title_font, extra=4)
    meta_h = _line_height(meta_font, extra=2)
    instr_h = _line_height(instruction_font, extra=4)
    activity_h = _line_height(activity_font, extra=8)

    # Header height
    header_height = (
        margin
        + title_h
        + meta_h * 2
        + 10
        + len(instruction_lines) * instr_h
        + 10
        + activity_h
        + 16  # scissors hint line
        + 20
    )

    # Card dimensions
    col_width = content_width // COLS
    # Card height: padding top/bottom + max(sprite_size, text lines)
    max_text_width = col_width - CARD_PADDING * 3 - SPRITE_SIZE - NUM_BOX_SIZE - 8
    # Estimate worst-case text height
    sample_lines = max(
        len(_wrap_text(step.text, step_font, max(max_text_width, 80))) for step in worksheet.steps
    )
    step_lh = _line_height(step_font, extra=6)
    card_inner_height = max(SPRITE_SIZE, sample_lines * step_lh)
    card_height = card_inner_height + CARD_PADDING * 2 + 10  # extra for num box row

    rows_needed = math.ceil(len(worksheet.steps) / COLS)
    total_height = header_height + rows_needed * (card_height + 20) + margin

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    # ---- Header ----
    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    y += title_h

    name_text = "Name: ____________"
    date_text = "Date: ____________"
    draw.text((margin, y), name_text, font=meta_font, fill="black")
    draw.text(
        (width - margin - _text_width(meta_font, date_text), y),
        date_text,
        font=meta_font,
        fill="black",
    )
    y += meta_h * 2

    for line in instruction_lines:
        draw.text((margin, y), line, font=instruction_font, fill=(80, 80, 80))
        y += instr_h
    y += 10

    draw.text(
        (margin, y), f"Activity: {worksheet.activity_name}", font=activity_font, fill=(30, 30, 120)
    )
    y += activity_h

    # Scissors hint
    scissors_hint = (
        "✂  - - - Cut here - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
    )
    draw.text((margin, y), scissors_hint, font=scissors_font, fill=(160, 160, 160))
    y += 16 + 20

    # ---- Cards ----
    for idx, step in enumerate(worksheet.steps):
        col = idx % COLS
        row = idx // COLS

        card_x = margin + col * col_width
        card_y = y + row * (card_height + 20)
        card_w = col_width - 12  # small gap between columns
        card_h = card_height

        # Card background
        draw.rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            fill=CARD_BG,
        )

        # Dashed border
        dash = 10
        gap = 6
        # Top and bottom edges
        for edge_y in [card_y, card_y + card_h]:
            x_pos = card_x
            while x_pos < card_x + card_w:
                draw.line(
                    [(x_pos, edge_y), (min(x_pos + dash, card_x + card_w), edge_y)],
                    fill=DASH_COLOR,
                    width=2,
                )
                x_pos += dash + gap
        # Left and right edges
        for edge_x in [card_x, card_x + card_w]:
            y_pos = card_y
            while y_pos < card_y + card_h:
                draw.line(
                    [(edge_x, y_pos), (edge_x, min(y_pos + dash, card_y + card_h))],
                    fill=DASH_COLOR,
                    width=2,
                )
                y_pos += dash + gap

        # Number box (top-left inside card)
        nb_x = card_x + CARD_PADDING
        nb_y = card_y + CARD_PADDING
        draw.rectangle(
            [nb_x, nb_y, nb_x + NUM_BOX_SIZE, nb_y + NUM_BOX_SIZE],
            outline=BORDER_COLOR,
            width=2,
        )
        if worksheet.show_answers and step.correct_order is not None:
            num_str = str(step.correct_order)
            nw = _text_width(num_font, num_str)
            nh = _line_height(num_font, extra=0)
            draw.text(
                (nb_x + (NUM_BOX_SIZE - nw) // 2, nb_y + (NUM_BOX_SIZE - nh) // 2),
                num_str,
                font=num_font,
                fill=(200, 30, 30),
            )

        content_x = nb_x + NUM_BOX_SIZE + 10
        content_y = card_y + CARD_PADDING

        # Optional image
        if step.image_path:
            sprite = _prepare_sprite(step.image_path, SPRITE_SIZE)
            if sprite:
                image.paste(
                    sprite, (content_x, content_y), sprite if sprite.mode == "RGBA" else None
                )
                content_x += SPRITE_SIZE + CARD_PADDING

        # Step text (wrapped)
        remaining_w = card_x + card_w - content_x - CARD_PADDING
        text_lines = _wrap_text(step.text, step_font, max(remaining_w, 60))
        ty = content_y + max(0, (card_inner_height - len(text_lines) * step_lh) // 2)
        for tline in text_lines:
            draw.text((content_x, ty), tline, font=step_font, fill="black")
            ty += step_lh

    return image


def render_sequencing_to_image(worksheet: SequencingWorksheet, output_path: str | Path) -> Path:
    """Render sequencing worksheet to a PNG image."""
    image = _render_sequencing_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_sequencing_to_pdf(worksheet: SequencingWorksheet, output_path: str | Path) -> Path:
    """Render sequencing worksheet to a PDF."""
    image = _render_sequencing_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


# =============================================================================
# T-Chart renderer
# =============================================================================

_T_CHART_ROW_HEIGHT = 36
_T_CHART_HEADER_FILL = (240, 240, 240)
_T_CHART_BORDER = 2
_T_CHART_ANSWER_COLOR = (200, 30, 30)


def _render_t_chart_image(worksheet: TChartWorksheet) -> Image.Image:
    """Render a TChartWorksheet to a PIL Image."""
    width: int = 1050
    margin: int = 72

    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    header_font = _load_font(26, bold=True)
    answer_font = _load_font(20, italic=True)
    word_bank_label_font = _load_font(24, bold=True)
    word_bank_font = _load_font(22)

    title_lh = _line_height(title_font, extra=4)
    meta_lh = _line_height(meta_font, extra=2)
    instruction_lh = _line_height(instruction_font, extra=4)
    col_header_lh = _line_height(header_font, extra=8)
    word_bank_lh = _line_height(word_bank_font, extra=4)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    num_cols = len(worksheet.columns)
    col_width = content_width // num_cols
    table_width = col_width * num_cols
    table_body_height = worksheet.row_count * _T_CHART_ROW_HEIGHT

    word_bank_lines: list[str] = []
    word_bank_section_height = 0
    if worksheet.word_bank:
        wb_label_lh = _line_height(word_bank_label_font, extra=4)
        wb_text = ", ".join(worksheet.word_bank)
        word_bank_lines = _wrap_text(wb_text, word_bank_font, content_width)
        word_bank_section_height = wb_label_lh + len(word_bank_lines) * word_bank_lh + 20

    total_height = (
        margin
        + title_lh
        + meta_lh * 2
        + 12
        + len(instruction_lines) * instruction_lh
        + 20
        + col_header_lh
        + table_body_height
        + 24
        + word_bank_section_height
        + margin
    )

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    name_w = _text_width(meta_font, name_text)
    date_w = _text_width(meta_font, date_text)
    right_edge = width - margin
    draw.text((right_edge - name_w, y), name_text, font=meta_font, fill="black")
    draw.text((right_edge - date_w, y + meta_lh), date_text, font=meta_font, fill="black")
    y += title_lh + 12

    for line in instruction_lines:
        draw.text((margin, y), line, font=instruction_font, fill="black")
        y += instruction_lh
    y += 20

    table_x = margin
    table_top = y

    for col_idx, col in enumerate(worksheet.columns):
        cell_x = table_x + col_idx * col_width
        draw.rectangle(
            (cell_x, table_top, cell_x + col_width, table_top + col_header_lh),
            fill=_T_CHART_HEADER_FILL,
            outline=None,
        )
        label_w = _text_width(header_font, col.label)
        label_x = cell_x + (col_width - label_w) // 2
        label_y = table_top + (col_header_lh - _line_height(header_font, extra=0)) // 2
        draw.text((label_x, label_y), col.label, font=header_font, fill="black")

    draw.rectangle(
        (table_x, table_top, table_x + table_width, table_top + col_header_lh),
        outline="black",
        width=_T_CHART_BORDER,
    )
    for col_idx in range(1, num_cols):
        div_x = table_x + col_idx * col_width
        draw.line(
            (div_x, table_top, div_x, table_top + col_header_lh),
            fill="black",
            width=_T_CHART_BORDER,
        )

    body_top = table_top + col_header_lh
    for row_idx in range(worksheet.row_count):
        row_y = body_top + row_idx * _T_CHART_ROW_HEIGHT
        line_y = row_y + _T_CHART_ROW_HEIGHT
        draw.line((table_x, line_y, table_x + table_width, line_y), fill="black", width=1)
        if worksheet.show_answers:
            for col_idx, col in enumerate(worksheet.columns):
                if row_idx < len(col.answers):
                    cell_x = table_x + col_idx * col_width + 8
                    text_y = row_y + (_T_CHART_ROW_HEIGHT - _line_height(answer_font, extra=0)) // 2
                    draw.text(
                        (cell_x, text_y),
                        col.answers[row_idx],
                        font=answer_font,
                        fill=_T_CHART_ANSWER_COLOR,
                    )

    for col_idx in range(1, num_cols):
        div_x = table_x + col_idx * col_width
        draw.line(
            (div_x, body_top, div_x, body_top + table_body_height),
            fill="black",
            width=_T_CHART_BORDER,
        )

    table_bottom = body_top + table_body_height
    draw.rectangle(
        (table_x, table_top, table_x + table_width, table_bottom),
        outline="black",
        width=_T_CHART_BORDER,
    )
    y = table_bottom + 24

    if worksheet.word_bank:
        wb_label_lh = _line_height(word_bank_label_font, extra=4)
        draw.text((margin, y), "Word Bank:", font=word_bank_label_font, fill="black")
        y += wb_label_lh
        for line in word_bank_lines:
            draw.text((margin, y), line, font=word_bank_font, fill="black")
            y += word_bank_lh

    return image


def render_t_chart_to_image(worksheet: TChartWorksheet, output_path: str | Path) -> Path:
    """Render T-chart worksheet to a PNG image."""
    image = _render_t_chart_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_t_chart_to_pdf(worksheet: TChartWorksheet, output_path: str | Path) -> Path:
    """Render T-chart worksheet to a PDF."""
    image = _render_t_chart_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


# =============================================================================
# Fill-in-the-blank renderer
# =============================================================================

_FIB_GAP_WIDTH = 130
_FIB_GAP_UNDERLINE_OFFSET = -6
_FIB_GAP_NUMBER_YOFFSET = -2
_FIB_GAP_TRAIL = 8
_FIB_ANSWER_COLOR = (200, 30, 30)
_FIB_GAP_NUMBER_COLOR = (130, 130, 130)


def _fib_layout_passage(
    segments,
    margin: int,
    content_width: int,
    body_font,
    gap_number_font,
    answer_font,
    answers: dict,
    show_answers: bool,
    draw,
    start_y: int,
) -> int:
    """Layout fill-in-the-blank passage segments. Pass draw=None for dry-run."""
    lh = _line_height(body_font)
    x = margin
    y = start_y
    right_edge = margin + content_width

    for seg in segments:
        if seg.newline:
            y += int(lh * 1.5)
            x = margin
        elif seg.text is not None:
            words = seg.text.split()
            for word in words:
                word_with_space = word + " "
                word_w = _text_width(body_font, word_with_space)
                if x + word_w > right_edge and x > margin:
                    y += lh
                    x = margin
                if draw is not None:
                    draw.text((x, y), word_with_space, font=body_font, fill="black")
                x += word_w
        elif seg.gap is not None:
            gap_num = seg.gap
            gap_w = _FIB_GAP_WIDTH
            if x + gap_w > right_edge and x > margin:
                y += lh
                x = margin
            if draw is not None:
                underline_y = y + lh + _FIB_GAP_UNDERLINE_OFFSET
                draw.line((x, underline_y, x + gap_w, underline_y), fill="black", width=2)
                num_text = f"({gap_num})"
                num_w = _text_width(gap_number_font, num_text)
                num_x = x + (gap_w - num_w) // 2
                draw.text(
                    (num_x, y + _FIB_GAP_NUMBER_YOFFSET),
                    num_text,
                    font=gap_number_font,
                    fill=_FIB_GAP_NUMBER_COLOR,
                )
                if show_answers:
                    ans_key = str(gap_num)
                    if ans_key in answers:
                        ans_text = answers[ans_key]
                        ans_w = _text_width(answer_font, ans_text)
                        ans_x = x + (gap_w - ans_w) // 2
                        ans_y = y + lh - _line_height(answer_font) - 2
                        draw.text(
                            (ans_x, ans_y), ans_text, font=answer_font, fill=_FIB_ANSWER_COLOR
                        )
            x += gap_w + _FIB_GAP_TRAIL

    y += lh
    return y


def _render_fill_in_blank_image(worksheet: FillBlankWorksheet) -> Image.Image:
    """Render a FillBlankWorksheet to a PIL Image using two-pass layout."""
    width = 1050
    margin = 72
    content_width = width - 2 * margin

    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    body_font = _load_font(24)
    gap_number_font = _load_font(16)
    answer_font = _load_font(20)
    word_bank_label_font = _load_font(24, bold=True)
    word_bank_body_font = _load_font(22)

    title_lh = _line_height(title_font, extra=4)
    meta_lh = _line_height(meta_font, extra=2)
    instruction_lh = _line_height(instruction_font, extra=4)
    wb_label_lh = _line_height(word_bank_label_font, extra=4)
    wb_body_lh = _line_height(word_bank_body_font, extra=4)

    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)
    header_height = max(title_lh, meta_lh * 2)

    # Pass 1: dry run to measure total height
    y = margin + header_height + 12 + len(instruction_lines) * instruction_lh + 20
    y = _fib_layout_passage(
        worksheet.segments,
        margin,
        content_width,
        body_font,
        gap_number_font,
        answer_font,
        worksheet.answers,
        worksheet.show_answers,
        None,
        y,
    )
    y += 20
    if worksheet.word_bank:
        y += wb_label_lh
        items = [f"{i + 1}. {word}" for i, word in enumerate(worksheet.word_bank)]
        wb_x = margin
        for item in items:
            item_w = _text_width(word_bank_body_font, item + "   ")
            if wb_x + item_w > margin + content_width and wb_x > margin:
                y += wb_body_lh
                wb_x = margin
            wb_x += item_w
        y += wb_body_lh
    total_height = y + margin

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    # Pass 2: draw
    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    name_w = _text_width(meta_font, name_text)
    date_w = _text_width(meta_font, date_text)
    right_edge = width - margin
    draw.text((right_edge - name_w, y), name_text, font=meta_font, fill="black")
    draw.text((right_edge - date_w, y + meta_lh), date_text, font=meta_font, fill="black")
    y += header_height + 12

    for line in instruction_lines:
        draw.text((margin, y), line, font=instruction_font, fill="black")
        y += instruction_lh
    y += 20

    y = _fib_layout_passage(
        worksheet.segments,
        margin,
        content_width,
        body_font,
        gap_number_font,
        answer_font,
        worksheet.answers,
        worksheet.show_answers,
        draw,
        y,
    )
    y += 20

    if worksheet.word_bank:
        draw.text((margin, y), "Word Bank:", font=word_bank_label_font, fill="black")
        y += wb_label_lh
        items = [f"{i + 1}. {word}" for i, word in enumerate(worksheet.word_bank)]
        wb_x = margin
        for item in items:
            item_with_space = item + "   "
            item_w = _text_width(word_bank_body_font, item_with_space)
            if wb_x + item_w > margin + content_width and wb_x > margin:
                y += wb_body_lh
                wb_x = margin
            draw.text((wb_x, y), item_with_space, font=word_bank_body_font, fill="black")
            wb_x += item_w

    return image


def render_fill_in_blank_to_image(worksheet: FillBlankWorksheet, output_path: str | Path) -> Path:
    """Render fill-in-the-blank worksheet to a PNG image."""
    image = _render_fill_in_blank_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_fill_in_blank_to_pdf(worksheet: FillBlankWorksheet, output_path: str | Path) -> Path:
    """Render fill-in-the-blank worksheet to a PDF."""
    image = _render_fill_in_blank_image(worksheet)
    rgb_image = image.convert("RGB")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rgb_image.save(output, format="PDF")
    return output


# =============================================================================
# Word sort renderer
# =============================================================================


def _ws_draw_dashed_hline(draw, x_start, x_end, y, fill, width=2, dash=10, gap=5):
    x = x_start
    on = True
    while x < x_end:
        if on:
            seg_end = min(x + dash, x_end)
            draw.line((x, y, seg_end, y), fill=fill, width=width)
            x += dash
        else:
            x += gap
        on = not on


def _ws_draw_dashed_vline(draw, y_start, y_end, x, fill, width=2, dash=10, gap=5):
    y = y_start
    on = True
    while y < y_end:
        if on:
            seg_end = min(y + dash, y_end)
            draw.line((x, y, x, seg_end), fill=fill, width=width)
            y += dash
        else:
            y += gap
        on = not on


def _ws_draw_dashed_rect(draw, x0, y0, x1, y1, fill, width=2, dash=10, gap=5):
    _ws_draw_dashed_hline(draw, x0, x1, y0, fill=fill, width=width, dash=dash, gap=gap)
    _ws_draw_dashed_hline(draw, x0, x1, y1, fill=fill, width=width, dash=dash, gap=gap)
    _ws_draw_dashed_vline(draw, y0, y1, x0, fill=fill, width=width, dash=dash, gap=gap)
    _ws_draw_dashed_vline(draw, y0, y1, x1, fill=fill, width=width, dash=dash, gap=gap)


def _render_word_sort_image(worksheet: WordSortWorksheet) -> Image.Image:
    """Render a WordSortWorksheet to a PIL Image."""
    width: int = 1050
    margin: int = 72
    content_width = width - 2 * margin
    box_gap = 12
    tile_width = 200
    tile_height = 52
    tile_gap = 12

    _DARK_GRAY = "#555555"
    _DARK_BLUE = "#1a1a8c"
    _GRAY = "#999999"
    _LABEL_LINE_COLOR = (180, 180, 180)

    title_font = _load_font(36, bold=True)
    meta_font = _load_font(24)
    instruction_font = _load_font(22, italic=True)
    category_label_font = _load_font(24, bold=True)
    tile_text_font = _load_font(22, bold=True)
    scissors_font = _load_font(18, italic=True)

    title_lh = _line_height(title_font, extra=4)
    meta_lh = _line_height(meta_font, extra=2)
    instruction_lh = _line_height(instruction_font, extra=4)
    category_label_lh = _line_height(category_label_font, extra=8)
    tile_text_lh = _line_height(tile_text_font, extra=4)
    scissors_lh = _line_height(scissors_font, extra=4)

    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    tiles_shuffled = list(worksheet.tiles)
    random.seed(42)
    random.shuffle(tiles_shuffled)

    n_cats = len(worksheet.categories)
    if n_cats <= 3:
        cat_rows = 1
        cats_per_row = n_cats
    else:
        cat_rows = 2
        cats_per_row = 2

    box_width = (content_width - (cats_per_row - 1) * box_gap) // cats_per_row
    tiles_per_cat = math.ceil(len(worksheet.tiles) / n_cats)
    slot_height = tile_text_lh + 12
    box_content_height = tiles_per_cat * slot_height
    box_height = max(120, category_label_lh + 8 + box_content_height + 16)
    cat_zone_height = cat_rows * box_height + (cat_rows - 1) * box_gap

    tiles_per_row = max(1, (content_width + tile_gap) // (tile_width + tile_gap))
    tile_rows = math.ceil(len(tiles_shuffled) / tiles_per_row)
    tile_zone_height = tile_rows * tile_height + max(0, tile_rows - 1) * tile_gap
    divider_height = scissors_lh + 10 + 20

    total_height = (
        margin
        + title_lh
        + meta_lh
        + 10
        + len(instruction_lines) * instruction_lh
        + 20
        + cat_zone_height
        + 24
        + divider_height
        + 20
        + tile_zone_height
        + margin
    )

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    name_w = _text_width(meta_font, name_text)
    date_w = _text_width(meta_font, date_text)
    right_edge = width - margin
    draw.text((right_edge - name_w, y), name_text, font=meta_font, fill="black")
    draw.text((right_edge - date_w, y + meta_lh), date_text, font=meta_font, fill="black")
    y += title_lh + 10

    for line in instruction_lines:
        draw.text((margin, y), line, font=instruction_font, fill="black")
        y += instruction_lh
    y += 20

    for row_idx in range(cat_rows):
        start_cat = row_idx * cats_per_row
        end_cat = min(start_cat + cats_per_row, n_cats)
        row_cats = worksheet.categories[start_cat:end_cat]
        for col_idx, category in enumerate(row_cats):
            bx0 = margin + col_idx * (box_width + box_gap)
            by0 = y
            bx1 = bx0 + box_width
            by1 = by0 + box_height
            _ws_draw_dashed_rect(draw, bx0, by0, bx1, by1, fill=_DARK_GRAY, width=2, dash=10, gap=6)
            label_y = by0 + 10
            label_w = _text_width(category_label_font, category)
            label_x = bx0 + (box_width - label_w) // 2
            draw.text((label_x, label_y), category, font=category_label_font, fill="black")
            sep_y = label_y + category_label_lh
            draw.line((bx0 + 4, sep_y, bx1 - 4, sep_y), fill=_LABEL_LINE_COLOR, width=1)
            if worksheet.show_answers:
                cat_tiles = [t for t in worksheet.tiles if t.category == category]
                tile_y = sep_y + 8
                for tile in cat_tiles:
                    draw.text((bx0 + 12, tile_y), tile.text, font=tile_text_font, fill=_DARK_BLUE)
                    tile_y += tile_text_lh + 12
        y += box_height + box_gap

    y -= box_gap
    y += 24

    scissors_text = "\u2702  Cut out the tiles below and sort them into the boxes above."
    sci_w = _text_width(scissors_font, scissors_text)
    sci_x = margin + (content_width - sci_w) // 2
    draw.text((sci_x, y), scissors_text, font=scissors_font, fill=_GRAY)
    y += scissors_lh + 10
    _ws_draw_dashed_hline(
        draw, margin, margin + content_width, y, fill=_GRAY, width=2, dash=8, gap=4
    )
    y += 40

    for tile_idx, tile in enumerate(tiles_shuffled):
        col = tile_idx % tiles_per_row
        row = tile_idx // tiles_per_row
        tx0 = margin + col * (tile_width + tile_gap)
        ty0 = y + row * (tile_height + tile_gap)
        tx1 = tx0 + tile_width
        ty1 = ty0 + tile_height
        _ws_draw_dashed_rect(draw, tx0, ty0, tx1, ty1, fill=_DARK_GRAY, width=2, dash=8, gap=4)
        tw = _text_width(tile_text_font, tile.text)
        th = _line_height(tile_text_font, extra=0)
        draw.text(
            (tx0 + (tile_width - tw) // 2, ty0 + (tile_height - th) // 2),
            tile.text,
            font=tile_text_font,
            fill="black",
        )

    return image


def render_word_sort_to_image(worksheet: WordSortWorksheet, output_path: str | Path) -> Path:
    """Render word sort worksheet to a PNG image."""
    image = _render_word_sort_image(worksheet)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


def render_word_sort_to_pdf(worksheet: WordSortWorksheet, output_path: str | Path) -> Path:
    """Render word sort worksheet to a PDF."""
    image = _render_word_sort_image(worksheet)
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
    "render_handwriting_to_image",
    "render_handwriting_to_pdf",
    "render_alphabet_to_image",
    "render_alphabet_to_pdf",
    "render_pixel_copy_to_image",
    "render_pixel_copy_to_pdf",
    "render_matching_to_image",
    "render_matching_to_pdf",
    "render_sequencing_to_image",
    "render_sequencing_to_pdf",
    "render_t_chart_to_image",
    "render_t_chart_to_pdf",
    "render_fill_in_blank_to_image",
    "render_fill_in_blank_to_pdf",
    "render_word_sort_to_image",
    "render_word_sort_to_pdf",
]


# ---------------------------------------------------------------------------
# Story Map renderer
# ---------------------------------------------------------------------------

try:
    from .worksheets import StoryMapWorksheet
except ImportError:
    from worksheets import StoryMapWorksheet  # type: ignore

_STORY_MAP_COLORS = [
    (173, 216, 230),  # light blue
    (144, 238, 144),  # light green
    (255, 218, 185),  # peach
    (221, 160, 221),  # plum
    (255, 255, 153),  # light yellow
]


def _render_story_map_image(worksheet: StoryMapWorksheet) -> Image.Image:
    """Render a StoryMapWorksheet to a PIL Image."""
    width: int = 1050
    margin: int = 60

    title_font = _load_font(36, bold=True)
    meta_font = _load_font(22)
    instruction_font = _load_font(20, italic=True)
    label_font = _load_font(24, bold=True)
    prompt_font = _load_font(18, italic=True)
    story_title_font = _load_font(22)

    title_lh = _line_height(title_font, extra=4)
    meta_lh = _line_height(meta_font, extra=2)
    instruction_lh = _line_height(instruction_font, extra=4)
    label_lh = _line_height(label_font, extra=8)
    prompt_lh = _line_height(prompt_font, extra=4)
    line_spacing = 32  # height per blank writing line

    content_width = width - 2 * margin

    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    # Calculate field heights
    def field_height(f) -> int:
        h = label_lh
        if f.prompt:
            prompt_wrapped = _wrap_text(f.prompt, prompt_font, content_width - 20)
            h += len(prompt_wrapped) * prompt_lh
        h += f.lines * line_spacing + 16
        return h

    story_title_h = 44 if worksheet.story_title_field else 0
    fields_height = sum(field_height(f) + 12 for f in worksheet.fields)

    total_height = (
        margin
        + title_lh
        + meta_lh * 2
        + 10
        + len(instruction_lines) * instruction_lh
        + 16
        + story_title_h
        + fields_height
        + margin
    )

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    draw.text(
        (width - margin - _text_width(meta_font, name_text), y),
        name_text,
        font=meta_font,
        fill="black",
    )
    draw.text(
        (width - margin - _text_width(meta_font, date_text), y + meta_lh),
        date_text,
        font=meta_font,
        fill="black",
    )
    y += title_lh + 10

    for line in instruction_lines:
        draw.text((margin, y), line, font=instruction_font, fill="black")
        y += instruction_lh
    y += 16

    if worksheet.story_title_field:
        draw.text((margin, y), "Story Title: ", font=story_title_font, fill="black")
        prefix_w = _text_width(story_title_font, "Story Title: ")
        line_x1 = margin + prefix_w
        line_x2 = width - margin
        line_y = y + _line_height(story_title_font, extra=0) - 4
        draw.line([(line_x1, line_y), (line_x2, line_y)], fill="black", width=2)
        y += story_title_h

    for i, f in enumerate(worksheet.fields):
        color = _STORY_MAP_COLORS[i % len(_STORY_MAP_COLORS)]
        fh = field_height(f)
        # Draw box
        draw.rectangle(
            (margin, y, margin + content_width, y + fh),
            outline=(100, 100, 100),
            width=2,
        )
        # Header band
        draw.rectangle(
            (margin, y, margin + content_width, y + label_lh),
            fill=color,
            outline=(100, 100, 100),
            width=2,
        )
        label_x = margin + (content_width - _text_width(label_font, f.label)) // 2
        draw.text((label_x, y + 4), f.label, font=label_font, fill="black")
        inner_y = y + label_lh + 4

        if f.prompt:
            prompt_lines = _wrap_text(f.prompt, prompt_font, content_width - 20)
            for pl in prompt_lines:
                draw.text((margin + 10, inner_y), pl, font=prompt_font, fill=(80, 80, 80))
                inner_y += prompt_lh

        # Blank lines or answer text
        if worksheet.show_answers and f.value:
            answer_lines = _wrap_text(f.value, prompt_font, content_width - 20)
            for al in answer_lines:
                draw.text((margin + 10, inner_y), al, font=prompt_font, fill=(60, 60, 180))
                inner_y += prompt_lh
        else:
            for _ in range(f.lines):
                line_y = inner_y + line_spacing - 6
                draw.line(
                    [(margin + 10, line_y), (margin + content_width - 10, line_y)],
                    fill=(180, 180, 180),
                    width=1,
                )
                inner_y += line_spacing

        y += fh + 12

    return image


def render_story_map_to_image(worksheet: StoryMapWorksheet, output_path: str) -> str:
    """Render story map worksheet to a PNG image."""
    image = _render_story_map_image(worksheet)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="PNG")
    return str(out)


def render_story_map_to_pdf(worksheet: StoryMapWorksheet, output_path: str) -> str:
    """Render story map worksheet to a PDF."""
    image = _render_story_map_image(worksheet)
    rgb = image.convert("RGB")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(out, format="PDF")
    return str(out)


# ---------------------------------------------------------------------------
# Labeled Diagram renderer
# ---------------------------------------------------------------------------

try:
    from .worksheets import LabeledDiagramWorksheet
except ImportError:
    from worksheets import LabeledDiagramWorksheet  # type: ignore


def _render_labeled_diagram_image(worksheet: LabeledDiagramWorksheet) -> Image.Image:
    """Render a LabeledDiagramWorksheet to a PIL Image."""
    width: int = 1050
    margin: int = 60

    title_font = _load_font(36, bold=True)
    meta_font = _load_font(22)
    instruction_font = _load_font(20, italic=True)
    num_font = _load_font(20, bold=True)
    answer_font = _load_font(22)
    wb_label_font = _load_font(22, bold=True)
    wb_font = _load_font(20)

    title_lh = _line_height(title_font, extra=4)
    meta_lh = _line_height(meta_font, extra=2)
    instruction_lh = _line_height(instruction_font, extra=4)
    answer_lh = _line_height(answer_font, extra=4)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    diagram_h = 320
    diagram_w = content_width

    wb_label_lh = _line_height(wb_label_font, extra=4)
    wb_section_h = (wb_label_lh + _line_height(wb_font, extra=4) + 20) if worksheet.word_bank else 0

    n = len(worksheet.labels)
    rows = math.ceil(n / 2)
    blanks_h = rows * (answer_lh + 8) + 20

    total_height = (
        margin
        + title_lh
        + meta_lh * 2
        + 10
        + len(instruction_lines) * instruction_lh
        + 16
        + diagram_h
        + 20
        + wb_section_h
        + blanks_h
        + margin
    )

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    draw.text(
        (width - margin - _text_width(meta_font, name_text), y),
        name_text,
        font=meta_font,
        fill="black",
    )
    draw.text(
        (width - margin - _text_width(meta_font, date_text), y + meta_lh),
        date_text,
        font=meta_font,
        fill="black",
    )
    y += title_lh + 10

    for line in instruction_lines:
        draw.text((margin, y), line, font=instruction_font, fill="black")
        y += instruction_lh
    y += 16

    diag_x, diag_y = margin, y

    if worksheet.image_path and os.path.exists(worksheet.image_path):
        try:
            img = Image.open(worksheet.image_path).convert("RGBA")
            bg = Image.new("RGBA", img.size, "WHITE")
            bg.alpha_composite(img)
            bg = bg.convert("RGB")
            bg.thumbnail((diagram_w, diagram_h), Image.Resampling.LANCZOS)
            image.paste(bg, (diag_x + (diagram_w - bg.width) // 2, int(diag_y)))
        except Exception:
            pass

    # Placeholder box
    draw.rectangle(
        (diag_x, diag_y, diag_x + diagram_w, diag_y + diagram_h),
        fill=(248, 248, 255),
        outline=(160, 160, 160),
        width=2,
    )
    place_label = "[ Diagram ]"
    pw = _text_width(instruction_font, place_label)
    draw.text(
        (diag_x + (diagram_w - pw) // 2, diag_y + diagram_h // 2 - 12),
        place_label,
        font=instruction_font,
        fill=(180, 180, 180),
    )

    # Numbered callout circles spread across diagram
    n_labels = len(worksheet.labels)
    for idx, lbl in enumerate(worksheet.labels):
        frac = (idx + 0.5) / max(n_labels, 1)
        cx = int(diag_x + frac * diagram_w)
        cy = int(diag_y + diagram_h * 0.35 + (idx % 2) * diagram_h * 0.3)
        r = 14
        draw.ellipse(
            (cx - r, cy - r, cx + r, cy + r), fill=(100, 149, 237), outline=(60, 100, 200), width=2
        )
        num_str = str(lbl.number)
        nw = _text_width(num_font, num_str)
        nh = _line_height(num_font, extra=0)
        draw.text((cx - nw // 2, cy - nh // 2), num_str, font=num_font, fill="white")

    y = diag_y + diagram_h + 20

    if worksheet.word_bank:
        words = [lbl.answer for lbl in worksheet.labels]
        shuffled = words[:]
        random.shuffle(shuffled)
        draw.text((margin, y), "Word Bank:", font=wb_label_font, fill="black")
        y += wb_label_lh
        draw.text((margin, y), "   ".join(shuffled), font=wb_font, fill=(50, 50, 130))
        y += _line_height(wb_font, extra=4) + 20

    col_w = content_width // 2
    for idx, lbl in enumerate(worksheet.labels):
        col = idx % 2
        row = idx // 2
        bx = margin + col * col_w
        by = y + row * (answer_lh + 8)
        num_str = f"{lbl.number}. "
        draw.text((bx, by), num_str, font=answer_font, fill="black")
        nw = _text_width(answer_font, num_str)
        if worksheet.show_answers:
            draw.text((bx + nw, by), lbl.answer, font=answer_font, fill=(60, 60, 180))
        else:
            line_y = by + answer_lh - 4
            draw.line([(bx + nw, line_y), (bx + col_w - 20, line_y)], fill="black", width=2)

    return image


def render_labeled_diagram_to_image(worksheet: LabeledDiagramWorksheet, output_path: str) -> str:
    """Render labeled diagram worksheet to a PNG image."""
    image = _render_labeled_diagram_image(worksheet)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="PNG")
    return str(out)


def render_labeled_diagram_to_pdf(worksheet: LabeledDiagramWorksheet, output_path: str) -> str:
    """Render labeled diagram worksheet to a PDF."""
    image = _render_labeled_diagram_image(worksheet).convert("RGB")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="PDF")
    return str(out)


# ---------------------------------------------------------------------------
# Frayer Model renderer
# ---------------------------------------------------------------------------

try:
    from .worksheets import FrayerModelWorksheet
except ImportError:
    from worksheets import FrayerModelWorksheet  # type: ignore


def _render_frayer_model_image(worksheet: FrayerModelWorksheet) -> Image.Image:
    """Render a FrayerModelWorksheet to a PIL Image."""
    width: int = 1050
    margin: int = 60

    title_font = _load_font(36, bold=True)
    meta_font = _load_font(22)
    instruction_font = _load_font(20, italic=True)
    q_label_font = _load_font(18, bold=True)
    concept_font = _load_font(26, bold=True)
    content_font = _load_font(18)

    title_lh = _line_height(title_font, extra=4)
    meta_lh = _line_height(meta_font, extra=2)
    instruction_lh = _line_height(instruction_font, extra=4)
    content_lh = _line_height(content_font, extra=4)

    content_width = width - 2 * margin
    instruction_lines = _wrap_text(worksheet.instructions, instruction_font, content_width)

    n_entries = len(worksheet.entries)
    # single entry: large diagram; multiple: two-per-row
    if n_entries <= 1:
        diagram_size = min(content_width, 800)
        cols = 1
    else:
        diagram_size = (content_width - 20) // 2
        cols = 2

    rows = math.ceil(n_entries / cols)
    diagrams_h = rows * (diagram_size + 20)

    total_height = (
        margin
        + title_lh
        + meta_lh * 2
        + 10
        + len(instruction_lines) * instruction_lh
        + 16
        + diagrams_h
        + margin
    )

    image = Image.new("RGB", (width, int(total_height)), color="white")
    draw = ImageDraw.Draw(image)

    y = margin
    draw.text((margin, y), worksheet.title, font=title_font, fill="black")
    name_text = "Name: ____________"
    date_text = "Date: ____________"
    draw.text(
        (width - margin - _text_width(meta_font, name_text), y),
        name_text,
        font=meta_font,
        fill="black",
    )
    draw.text(
        (width - margin - _text_width(meta_font, date_text), y + meta_lh),
        date_text,
        font=meta_font,
        fill="black",
    )
    y += title_lh + 10

    for line in instruction_lines:
        draw.text((margin, y), line, font=instruction_font, fill="black")
        y += instruction_lh
    y += 16

    ql = worksheet.quadrant_labels
    q_colors = [
        (173, 216, 230),  # top-left: light blue
        (255, 218, 185),  # top-right: peach
        (144, 238, 144),  # bottom-left: light green
        (255, 255, 153),  # bottom-right: light yellow
    ]

    for entry_idx, entry in enumerate(worksheet.entries):
        col = entry_idx % cols
        row = entry_idx // cols
        if cols == 1:
            dx = margin + (content_width - diagram_size) // 2
        else:
            dx = margin + col * (diagram_size + 20)
        dy = y + row * (diagram_size + 20)
        ds = diagram_size

        half = ds // 2
        cx = dx + half
        cy = dy + half

        # Draw 4 quadrants
        quadrants = [
            (dx, dy, dx + half, dy + half, 0),  # top-left
            (dx + half, dy, dx + ds, dy + half, 1),  # top-right
            (dx, dy + half, dx + half, dy + ds, 2),  # bottom-left
            (dx + half, dy + half, dx + ds, dy + ds, 3),  # bottom-right
        ]

        for qx1, qy1, qx2, qy2, qi in quadrants:
            draw.rectangle(
                (qx1, qy1, qx2, qy2), fill=q_colors[qi], outline=(100, 100, 100), width=2
            )
            # Quadrant label
            ql_text = ql[qi]
            lw = _text_width(q_label_font, ql_text)
            lx = qx1 + (qx2 - qx1 - lw) // 2
            draw.text((lx, qy1 + 6), ql_text, font=q_label_font, fill=(60, 60, 60))

            # Content
            inner_y = qy1 + _line_height(q_label_font, extra=4) + 8
            inner_w = qx2 - qx1 - 20
            show = worksheet.show_answers

            if qi == 0:
                text = entry.definition
            elif qi == 1:
                text = (
                    "\n".join(f"• {c}" for c in entry.characteristics)
                    if entry.characteristics
                    else None
                )
            elif qi == 2:
                text = "\n".join(f"• {e}" for e in entry.examples) if entry.examples else None
            else:
                text = (
                    "\n".join(f"• {ne}" for ne in entry.non_examples)
                    if entry.non_examples
                    else None
                )

            if show and text:
                for text_line in text.split("\n"):
                    wrapped = _wrap_text(text_line, content_font, inner_w)
                    for wl in wrapped:
                        if inner_y + content_lh < qy2 - 4:
                            draw.text((qx1 + 10, inner_y), wl, font=content_font, fill="black")
                            inner_y += content_lh
            else:
                # Blank lines
                for _ in range(3):
                    line_y = inner_y + 20
                    if line_y < qy2 - 8:
                        draw.line(
                            [(qx1 + 10, line_y), (qx2 - 10, line_y)], fill=(180, 180, 180), width=1
                        )
                        inner_y += 28

        # Outer border
        draw.rectangle((dx, dy, dx + ds, dy + ds), outline=(80, 80, 80), width=3)
        # Cross lines
        draw.line([(cx, dy), (cx, dy + ds)], fill=(80, 80, 80), width=3)
        draw.line([(dx, cy), (dx + ds, cy)], fill=(80, 80, 80), width=3)

        # Center oval with concept
        oval_rx, oval_ry = 90, 40
        draw.ellipse(
            (cx - oval_rx, cy - oval_ry, cx + oval_rx, cy + oval_ry),
            fill="white",
            outline=(60, 60, 60),
            width=3,
        )
        cw = _text_width(concept_font, entry.concept)
        ch = _line_height(concept_font, extra=0)
        draw.text((cx - cw // 2, cy - ch // 2), entry.concept, font=concept_font, fill="black")

    return image


def render_frayer_model_to_image(worksheet: FrayerModelWorksheet, output_path: str) -> str:
    """Render Frayer model worksheet to a PNG image."""
    image = _render_frayer_model_image(worksheet)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="PNG")
    return str(out)


def render_frayer_model_to_pdf(worksheet: FrayerModelWorksheet, output_path: str) -> str:
    """Render Frayer model worksheet to a PDF."""
    image = _render_frayer_model_image(worksheet).convert("RGB")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="PDF")
    return str(out)
