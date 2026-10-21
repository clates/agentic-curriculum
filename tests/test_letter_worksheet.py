"""Tests for the HTML letter worksheet renderer (incoming letter, reply frame, envelope)."""

from src.worksheet_html_renderer import (
    HTML_SUPPORTED_KINDS,
    render_worksheet_html,
)

FULL_LETTER = {
    "title": "A Letter from Tobin",
    "style": "parchment",
    "incoming": {
        "place_date": "Rogue Encampment, Day 3",
        "greeting": "Dear Hero,",
        "body": "My name is Tobin.\n\nWhich class should I choose?\n\nPlease tell me WHY.",
        "closing": "Your friend,",
        "signature": "Tobin",
    },
    "reply": {
        "greeting": "Dear ________,",
        "paragraphs": [
            {"starter": "I think you should choose the", "lines": 2},
            {"starter": "One reason is because", "lines": 3},
        ],
        "closing_options": ["Your friend,", "From,"],
    },
    "word_bank": ["Tobin", "because"],
    "checklist": ["I started with a capital letter.", "I signed my name.", "I used because."],
}


def _render(data: dict, day: str = "Wednesday") -> str:
    html = render_worksheet_html("letterWorksheet", data, day)
    assert html is not None
    return html


def test_letter_kind_is_registered():
    assert "letterWorksheet" in HTML_SUPPORTED_KINDS


def test_full_letter_renders_incoming_reply_and_extras():
    html = _render(FULL_LETTER)
    # Incoming letter: one <p> per blank-line-separated paragraph, plus sign-off.
    assert html.count("<p>") == 3
    assert "Dear Hero," in html
    assert "Rogue Encampment, Day 3" in html
    assert 'class="lt-signature">Tobin<' in html
    # Reply frame: starters, one ruled line per requested line, and closing choices.
    assert "One reason is because" in html
    assert html.count('class="lt-line"') == 5
    assert html.count('class="lt-choice"') == 2
    assert 'class="lt-sign-line"' in html
    # Spelling helpers and self-edit checklist.
    assert html.count('class="lt-tile"') == 2
    assert html.count('class="lt-check-box"') == 3
    assert "Check your letter" in html


def test_parchment_adds_wax_seal_with_signature_initial():
    html = _render(FULL_LETTER)
    assert 'class="lt-card parchment"' in html
    assert 'class="lt-seal">T<' in html


def test_plain_style_has_no_seal_and_uses_day_palette():
    html = _render({**FULL_LETTER, "style": "plain"}, "Monday")
    assert 'class="lt-seal"' not in html
    assert "background:#dbeafe" in html  # Monday light accent


def test_reply_only_letter_omits_incoming_card():
    html = _render({"title": "Write a Letter", "reply": {"paragraphs": [{"lines": 4}]}})
    assert 'class="lt-card' not in html
    assert html.count('class="lt-line"') == 4
    assert "Dear ________________," in html  # default greeting


def test_incoming_only_letter_omits_reply_frame():
    html = _render({"title": "Read a Letter", "incoming": "Just a plain body string."})
    assert "Just a plain body string." in html
    assert 'class="lt-reply"' not in html
    assert 'class="lt-sign-line"' not in html


def test_no_extras_box_when_word_bank_and_checklist_absent():
    html = _render({"incoming": {"body": "Hi"}})
    assert 'class="lt-extras"' not in html


def test_envelope_is_opt_in_and_starts_a_new_page():
    assert 'class="lt-envelope"' not in _render(FULL_LETTER)
    html = _render({**FULL_LETTER, "envelope": True})
    assert 'class="lt-envelope"' in html
    assert "<svg" in html and "stroke-dasharray" in html  # dashed fold lines
    assert "Make an Envelope" in html


def test_envelope_prefills_to_and_from():
    html = _render({**FULL_LETTER, "envelope": {"to": "Tobin", "from": "Deckard Cain"}})
    assert ">Tobin</text>" in html
    assert ">Deckard Cain</text>" in html


def test_letter_text_is_html_escaped():
    html = _render(
        {
            "incoming": {"body": "<script>alert(1)</script>", "signature": "A & B"},
            "envelope": {"to": "<b>x</b>"},
        }
    )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "A &amp; B" in html
    assert "&lt;b&gt;x&lt;/b&gt;" in html
