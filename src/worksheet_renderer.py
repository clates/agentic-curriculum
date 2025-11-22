"""Rendering helpers for Worksheet objects."""
from __future__ import annotations

import math
import textwrap
from pathlib import Path
from typing import cast

from PIL import Image, ImageDraw, ImageFont

from .worksheets import Worksheet, format_vertical_problem

_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
)

_MONO_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
)


def _load_font(size: int, *, monospace: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = _MONO_FONT_CANDIDATES if monospace else _FONT_CANDIDATES
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
    instruction_height = 0
    instruction_lines: list[str] = []
    if worksheet.instructions:
        instruction_lines = textwrap.wrap(worksheet.instructions, width=70) or [worksheet.instructions]
        instruction_height = len(instruction_lines) * _line_height(instruction_font, extra=4)

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
        for line in instruction_lines:
            draw.text((margin, y), line, font=instruction_font, fill="black")
            y += _line_height(instruction_font, extra=4)

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


__all__ = [
    "render_worksheet_to_image",
    "render_worksheet_to_pdf",
]
