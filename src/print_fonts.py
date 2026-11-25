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
from typing import Literal

Audience = Literal["child", "adult"]

FONT_DIR = Path(__file__).resolve().parent / "fonts"

_FALLBACK = "'Trebuchet MS', Arial, sans-serif"
_FAMILY: dict[str, str] = {"child": "Andika", "adult": "Recursive"}
_FILES: dict[str, tuple[tuple[str, int], ...]] = {
    "Andika": (("Andika-Regular.woff2", 400), ("Andika-Bold.woff2", 700)),
    "Recursive": (("Recursive-Regular.woff2", 400), ("Recursive-Bold.woff2", 700)),
}


def _family(audience: Audience) -> str:
    try:
        return _FAMILY[audience]
    except KeyError:
        raise ValueError(f"audience must be 'child' or 'adult', not {audience!r}") from None


def font_stack(audience: Audience) -> str:
    """The CSS ``font-family`` value for ``audience``, with system fallbacks."""
    return f"'{_family(audience)}', {_FALLBACK}"


@cache
def font_face_css(audience: Audience) -> str:
    """``@font-face`` rules for ``audience``'s typeface, with the font data inline.

    Raises ``FileNotFoundError`` if a font file is missing: a packaging mistake (fonts not copied
    into the image) should fail loudly, not print every page in a fallback face."""
    family = _family(audience)
    rules = []
    for filename, weight in _FILES[family]:
        data = base64.b64encode((FONT_DIR / filename).read_bytes()).decode("ascii")
        rules.append(
            f"@font-face {{ font-family: '{family}'; font-style: normal; font-weight: {weight}; "
            f"font-display: block; src: url(data:font/woff2;base64,{data}) format('woff2'); }}"
        )
    return "\n".join(rules) + "\n"
