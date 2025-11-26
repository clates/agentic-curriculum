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
except ImportError:  # Fallback when executed outside package context
    CURRENT_DIR = os.path.dirname(__file__)
    if CURRENT_DIR not in sys.path:
        sys.path.insert(0, CURRENT_DIR)
    from worksheets import ReadingWorksheet, Worksheet, format_vertical_problem  # type: ignore

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


def _wrap_text(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_width: int) -> list[str]:
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


def _wrap_paragraphs(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont, max_width: int) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []
    paragraphs = [block.replace("\n", " ").strip() for block in normalized.split("\n\n") if block.strip()]
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
        max(len(line) for line in lines) if lines else 0
        for lines, _ in formatted_blocks
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
        definition_lines = _wrap_text(entry.definition or "", body_font, remaining_width) if entry.definition else []
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

    questions_height = sum(len(lines) * body_line_height + resp * answer_line_height for lines, resp in question_blocks)
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
                draw.line((line_start, baseline, margin + content_width, baseline), fill="black", width=2)
                y += answer_line_height
                for _ in range(response_lines - 1):
                    baseline = y + answer_line_height - int(answer_line_height * 0.4)
                    draw.line((margin, baseline, margin + content_width, baseline), fill="black", width=2)
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


__all__ = [
    "render_worksheet_to_image",
    "render_worksheet_to_pdf",
    "render_reading_worksheet_to_image",
    "render_reading_worksheet_to_pdf",
]
