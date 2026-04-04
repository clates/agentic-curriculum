"""Utilities for generating pixel copy worksheet data structures."""

from __future__ import annotations

from dataclasses import dataclass

from .base import BaseWorksheet


@dataclass
class PixelCopyWorksheet(BaseWorksheet):
    """Worksheet for pixel copy practice."""

    title: str
    instructions: str
    image_path: str
    grid_size: int = 24
    metadata: dict | None = None

    def to_markdown(self) -> str:
        """Return a Markdown representation of the pixel copy worksheet."""
        return f"# {self.title}\n\n{self.instructions}\n\n[Pixel Grid: {self.grid_size}x{self.grid_size}]"


def generate_pixel_copy_worksheet(
    *,
    image_path: str,
    title: str = "Pixel Copy",
    instructions: str = "Look at the colors on the left. Copy them to the grid on the right!",
    grid_size: int = 24,
    metadata: dict | None = None,
) -> PixelCopyWorksheet:
    """Create a pixel copy worksheet.

    Args:
        image_path: Path to the image to pixelate.
        title: Worksheet title.
        instructions: Instructions for students.
        grid_size: Number of cells per side.
        metadata: Optional metadata dictionary.

    Returns:
        PixelCopyWorksheet instance.
    """
    if not image_path:
        raise ValueError("image_path is required")

    return PixelCopyWorksheet(
        title=title,
        instructions=instructions,
        image_path=image_path,
        grid_size=grid_size,
        metadata=metadata or {},
    )


__all__ = [
    "PixelCopyWorksheet",
    "generate_pixel_copy_worksheet",
]
