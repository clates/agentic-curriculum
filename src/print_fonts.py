"""Typefaces embedded in printable pages, so a printed week never fetches anything over the network.

Andika (SIL) is for text the child reads: single-story a and g, plain i and l, made for beginning
readers. Recursive (Linear, proportional) is for text the adult reads: teacher guide and prep sheet.
Both are under the SIL Open Font License; the license files sit next to the fonts in ``src/fonts/``.
Andika files are Google Fonts' Latin subset, unmodified. Recursive files are static 400 and 700
instances of Google Fonts' Latin subset.
"""

from __future__ import annotations

import base64
from functools import cache
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent / "fonts"

KID_FAMILY = "'Andika', 'Trebuchet MS', Arial, sans-serif"
ADULT_FAMILY = "'Recursive', 'Trebuchet MS', Arial, sans-serif"

_FACES = {
    "Andika": (("Andika-Regular.woff2", 400), ("Andika-Bold.woff2", 700)),
    "Recursive": (("Recursive-Regular.woff2", 400), ("Recursive-Bold.woff2", 700)),
}


@cache
def font_face_css(family: str) -> str:
    """``@font-face`` rules for ``family`` with the font data inline. Empty if a file is missing,
    so the page falls back to the next family in the stack rather than failing to render."""
    rules = []
    for filename, weight in _FACES[family]:
        path = FONT_DIR / filename
        if not path.is_file():
            return ""
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        rules.append(
            f"@font-face {{ font-family: '{family}'; font-style: normal; font-weight: {weight}; "
            f"font-display: block; src: url(data:font/woff2;base64,{data}) format('woff2'); }}"
        )
    return "\n".join(rules) + "\n"
