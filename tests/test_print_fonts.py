"""Printed pages embed their typefaces: Andika for the child, Recursive for the adult."""

from __future__ import annotations

import pytest

from src import print_fonts
from src.weekdoc import WeekDoc
from src.weekdoc.render import render_packet, render_prep_sheet, render_teacher_guide
from src.worksheet_html_renderer import build_print_packet_html
from tests.weekdoc_fixtures import minimal_week


def test_every_font_file_and_license_is_present():
    for files in print_fonts._FILES.values():
        for name, _weight in files:
            assert (print_fonts.FONT_DIR / name).stat().st_size > 5_000, name
    for licence in ("OFL-Andika.txt", "OFL-Recursive.txt"):
        assert "SIL Open Font License" in (print_fonts.FONT_DIR / licence).read_text()


def test_faces_are_embedded_as_data():
    for audience, family in (("child", "Andika"), ("adult", "Recursive")):
        css = print_fonts.font_face_css(audience)
        assert css.count("@font-face") == 2 and css.count("url(data:font/woff2;base64,") == 2
        assert f"font-family: '{family}'" in css


def test_the_audience_picks_the_typeface():
    child = build_print_packet_html([("Monday", "<p>x</p>")])
    adult = build_print_packet_html([("", "<p>x</p>")], audience="adult")
    assert "font-family: 'Andika'" in child and "'Recursive'" not in child
    assert "font-family: 'Recursive'" in adult and "'Andika'" not in adult
    with pytest.raises(ValueError):
        build_print_packet_html([("", "<p>x</p>")], audience="teen")  # type: ignore[arg-type]


def test_hosted_documents_use_the_right_typeface():
    week = WeekDoc.model_validate(minimal_week())
    assert "font-family: 'Andika'" in render_packet(week)
    assert "font-family: 'Recursive'" in render_prep_sheet(week)
    assert "font-family: 'Recursive'" in render_teacher_guide(week)


def test_a_missing_font_file_fails_loudly(tmp_path, monkeypatch):
    monkeypatch.setattr(print_fonts, "FONT_DIR", tmp_path)
    print_fonts.font_face_css.cache_clear()
    try:
        with pytest.raises(FileNotFoundError):
            print_fonts.font_face_css("child")
    finally:
        print_fonts.font_face_css.cache_clear()
