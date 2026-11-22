"""M6.3: the deterministic topic distinctness gate and the vetted topic list."""

import re

import pytest

from topic_gate import (
    TOPICS,
    OptionText,
    content_stems,
    distinctness_problems,
    template_options,
    themes_of,
    title_problems,
    vetted_menu,
)


def o(topic, title, hook=""):
    return OptionText(topic, title, hook)


GOOD = [
    o("Weather", "Weather Watchers", "Track the sky."),
    o("Sports reporting", "Game Day Reporter", "Report from the game."),
    o("Ocean animals", "Deep Sea Files", "Meet sea creatures."),
]


def test_three_different_topics_pass():
    assert distinctness_problems(GOOD) == []


def test_a_shared_main_noun_is_rejected_even_when_plural_or_in_the_title():
    bad = [GOOD[0], o("Animal care", "Pet Doctor"), o("Ocean animals", "Deep Sea Files")]
    problems = distinctness_problems(bad)
    assert problems and "share the word 'animal'" in problems[0]


def test_generic_words_do_not_count_as_shared():
    two = [o("Weather", "Weather Adventure Week"), o("Space", "Space Adventure Week")]
    assert distinctness_problems(two) == []


def test_a_shared_theme_with_different_words_is_rejected():
    # dinosaurs and fossils never share a word but are one theme
    bad = [o("Dinosaurs", "Dino Dig Site"), o("Fossils", "Bone Hunters Club"), GOOD[1]]
    assert "both about dinosaurs" in distinctness_problems(bad)[0]


def test_the_old_failure_dinosaurs_and_cookies_in_every_option():
    bad = [
        o("Dino Days", "Dino Days", "Dinosaurs bake cookies."),
        o("Cookie Fossils", "Cookie Fossil Lab", "Bake fossil cookies."),
        o("Dino Bakery", "Dino Bakery", "Cookies for dinosaurs."),
    ]
    assert distinctness_problems(bad)


def test_hook_themes_count():
    bad = [GOOD[0], o("Baking", "Bakery Boss", "Bake through a thunder storm."), GOOD[2]]
    assert any("both about weather" in p for p in distinctness_problems(bad))


def test_repeating_a_recent_topic_is_rejected_by_word_or_theme():
    assert distinctness_problems(GOOD, recent=["Rainy day weather"])  # theme/word
    assert distinctness_problems(GOOD, recent=["Whale watching"])  # ocean theme
    assert distinctness_problems(GOOD, recent=["Mission to Mars"]) == []


def test_the_recent_repeat_message_names_the_option():
    msg = distinctness_problems(GOOD, recent=["Weather"])[0]
    assert "option 1 repeats a recent topic" in msg


@pytest.mark.parametrize(
    "title,ok",
    [
        ("Weather Watchers", True),
        ("One two three four five six", True),
        ("One two three four five six seven", False),
        ("A" * 41, False),
    ],
)
def test_title_limits(title, ok):
    assert (title_problems(title) is None) is ok


def test_stems_and_themes():
    assert content_stems("The Whales' Songs") == {"whale", "song"}
    assert "weather" in themes_of("thunderstorms") or "weather" in themes_of("thunder storm")
    assert themes_of("zzz") == set()


def test_curated_topics_are_well_formed_and_do_not_overlap_each_other():
    keys = [t.key for t in TOPICS]
    assert len(keys) == len(set(keys)) >= 20
    for t in TOPICS:
        assert not title_problems(t.titles[0]) and all(not title_problems(x) for x in t.titles)
        assert len(t.hook.split(". ")) == 1 and "{name}" in t.hook
        assert not re.search(r"standard|mastery|json|lorem", t.activities, re.I)
    for a in TOPICS:
        for b in TOPICS:
            if a.key < b.key:
                # any two curated topics can sit in one set (the fallback relies on it)
                assert (
                    distinctness_problems(
                        [o(a.label, a.titles[0], a.hook), o(b.label, b.titles[0], b.hook)]
                    )
                    == []
                ), (a.key, b.key)


def test_template_options_are_deterministic_distinct_and_skip_recent():
    a = template_options("seed", "Mira", recent=["Weather", "Space"])
    assert a == template_options("seed", "Mira", recent=["Weather", "Space"])
    assert len(a) == 3
    texts = [o(t.label, t.titles[0], t.hook.format(name="Mira")) for t in a]
    assert distinctness_problems(texts, recent=["Weather", "Space"]) == []
    assert a != template_options("another seed", "Mira", recent=["Weather", "Space"])


def test_template_options_prefer_the_childs_interests():
    picks = template_options("s", "Mira", interests=["dinosaurs", "baking", "soccer"])
    assert {t.key for t in picks} == {"dinosaurs", "baking", "sports"}


def test_no_interests_still_gives_three_options():
    assert len(template_options("s", "Mira")) == 3
    assert len(vetted_menu("s")) == 8


def test_even_with_everything_recent_three_distinct_options_come_back():
    everything = [t.label for t in TOPICS]
    assert len(template_options("s", "Mira", recent=everything)) == 3
