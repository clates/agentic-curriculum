"""Topic options (M6.3): the vetted topic list and the deterministic distinctness gate.

The parent picks between three TOPICS (what the week is about: weather, a sports reporter week,
ocean animals). The skills are the same under all three and come from the curriculum engine, so
the three topics must be clearly different from each other and from what the child has just had.

The gate is plain code, no model: it normalises words, groups them into themes (a theme is a
family of words about one subject, for example "dinosaur / fossil / T. rex") and rejects:

* two options that share a main word or a theme (title, topic and hook are all checked for themes)
* an option that repeats a recent topic of this child (same word or same theme)

When the model cannot pass the gate, ``template_options`` builds three options from the curated
list below, again deterministically (seeded, interests first, recent topics excluded).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Iterable, Sequence

MAX_TITLE_WORDS = 6
MAX_TITLE_CHARS = 40
MAX_TOPIC_WORDS = 3

# Words that say nothing about the subject of a week; ignored when comparing topics.
GENERIC = frozenset(
    """a an and the of to in on at for with from by or as is are be your you our my their
    week weeks day days adventure adventures challenge challenges lab labs club clubs quest quests
    mission missions explorer explorers explore detective detectives investigator investigators
    world worlds time times big little super fun amazing great story stories tales tale journey
    journeys project projects zone school class makers maker builders builder hunt hunters hunter
    secret secrets mystery mysteries science math reading writing words expedition journal files
    diary notes field guide workshop desk studio crew boss owner production practice watch watchers""".split()
)


@dataclass(frozen=True)
class Topic:
    key: str
    label: str  # the topic in a few words: "Weather"
    words: tuple[str, ...]  # words that mean this theme (singular stems)
    titles: tuple[str, ...]  # at most 6 words each
    hook: str  # one sentence, {name} is the child's first name
    activities: str  # {name} too; says how the week works


def _t(key, label, words, titles, hook, activities) -> Topic:
    return Topic(key, label, tuple(words.split()), tuple(titles), hook, activities)


TOPICS: tuple[Topic, ...] = (
    _t(
        "weather",
        "Weather",
        "weather storm cloud rain rainbow thunder lightning forecast tornado "
        "hurricane snow wind",
        ("Weather Watchers", "Be the Town Forecaster"),
        "{name} tracks the sky and predicts tomorrow's weather.",
        "{name} keeps a weather log, reads and writes forecasts, and uses numbers from the sky.",
    ),
    _t(
        "sports",
        "Sports reporting",
        "sport reporter soccer football basketball baseball team "
        "athlete game score stadium coach",
        ("Sports Desk Reporter", "Game Day Reporter"),
        "{name} reports live from the big game.",
        "{name} writes match reports, reads scoreboards and works out the stats.",
    ),
    _t(
        "ocean",
        "Ocean animals",
        "ocean sea whale dolphin shark octopus coral reef fish jellyfish "
        "turtle marine underwater",
        ("Ocean Animal Expedition", "Deep Sea Animal Files"),
        "{name} dives down to meet the animals of the sea.",
        "{name} reads about sea creatures and uses what they learn to write, count and compare.",
    ),
    _t(
        "space",
        "Space",
        "space planet moon star rocket astronaut galaxy comet orbit mars solar " "telescope",
        ("Mission to Mars", "Rocket Launch Week"),
        "{name} plans a trip to another planet.",
        "{name} plots a journey through space, reading and writing mission notes along the way.",
    ),
    _t(
        "dinosaurs",
        "Dinosaurs",
        "dinosaur fossil trex rex jurassic paleontologist dig bone " "prehistoric",
        ("Dinosaur Dig Site", "Fossil Hunters"),
        "{name} uncovers giant creatures from long ago.",
        "{name} reads fossil facts and uses them for writing and number puzzles.",
    ),
    _t(
        "baking",
        "Baking",
        "bake baking cookie cake bread kitchen recipe cook cooking chef pie " "dough oven",
        ("Bakery Boss", "Kitchen Recipe Test"),
        "{name} runs a bakery and tests every recipe.",
        "{name} reads and writes recipes and measures like a real baker.",
    ),
    _t(
        "farm",
        "Farm life",
        "farm barn tractor harvest crop cow chicken pig sheep orchard " "garden seed plant",
        ("Barnyard Chores", "Harvest Time on the Farm"),
        "{name} runs a farm from seed to harvest.",
        "{name} plans a farm, counts the harvest and writes about each day's work.",
    ),
    _t(
        "castles",
        "Castles and knights",
        "castle knight dragon king queen medieval kingdom sword " "armor fortress",
        ("Castle Under Siege", "Knights of the Round Table"),
        "{name} defends a castle and keeps the kingdom's records.",
        "{name} reads legends and solves castle problems with numbers and words.",
    ),
    _t(
        "detective",
        "Detective cases",
        "detective clue case suspect crime sleuth evidence " "fingerprint spy",
        ("Mystery at Midnight", "Clue Hunters Club"),
        "{name} cracks a case by following clues.",
        "{name} reads clues closely, writes case notes and checks each fact.",
    ),
    _t(
        "art",
        "Art and comics",
        "art comic draw drawing paint painting cartoon artist gallery " "sketch color",
        ("Comic Book Studio", "The Young Artist Gallery"),
        "{name} makes a comic or artwork from scratch.",
        "{name} plans, writes and illustrates a small comic, practicing skills along the way.",
    ),
    _t(
        "music",
        "Music",
        "music song band instrument drum guitar piano rhythm concert singer " "orchestra",
        ("Band Practice Week", "Songwriter Studio"),
        "{name} puts a band together for the big night.",
        "{name} writes lyrics, counts rhythms and reads about musicians.",
    ),
    _t(
        "robots",
        "Robots",
        "robot machine engineer invention invent gadget circuit coding code " "computer",
        ("Robot Workshop", "Inventor's Workbench"),
        "{name} designs a robot and tests how it works.",
        "{name} plans inventions, measures parts and writes up each test.",
    ),
    _t(
        "rainforest",
        "Rainforest",
        "rainforest jungle amazon monkey parrot jaguar canopy tropical " "toucan",
        ("Rainforest Expedition", "Jungle Canopy Journal"),
        "{name} ventures deep into the jungle.",
        "{name} keeps an explorer's journal and studies the animals and plants.",
    ),
    _t(
        "pirates",
        "Pirates",
        "pirate treasure ship captain island map sail sailor voyage parrot",
        ("Pirate Treasure Hunt", "Captain's Treasure Map"),
        "{name} follows a treasure map across the waves.",
        "{name} reads map clues, counts treasure and writes the captain's log.",
    ),
    _t(
        "mountains",
        "Mountains",
        "mountain climb climbing hike hiking peak volcano canyon trail " "camp camping",
        ("Mountain Trail Camp", "Summit Climb Diary"),
        "{name} plans a climb to the very top.",
        "{name} plans the trail, reads about mountains and records the journey.",
    ),
    _t(
        "cities",
        "Cities and travel",
        "city travel train airport bridge skyscraper country passport " "flight tour",
        ("Passport to Everywhere", "Around the World Trip"),
        "{name} plans a trip across the world.",
        "{name} reads about faraway places and plans routes, costs and postcards.",
    ),
    _t(
        "insects",
        "Bugs and insects",
        "insect bug butterfly bee ant beetle spider ladybug " "caterpillar",
        ("Bug Hunt Field Guide", "The Secret Life of Bees"),
        "{name} studies the tiniest creatures around.",
        "{name} observes bugs, draws field notes and counts what they find.",
    ),
    _t(
        "cars",
        "Vehicles",
        "car truck race racing vehicle train plane airplane boat bicycle bike " "speed motor",
        ("Race Day Pit Crew", "Build a Racing Team"),
        "{name} joins a pit crew and races to the finish.",
        "{name} reads about vehicles, times laps and writes race reports.",
    ),
    _t(
        "pets",
        "Pets and vets",
        "pet dog cat puppy kitten hamster vet veterinarian " "shelter",
        ("Pet Care Clinic", "Shelter Pet Rescue"),
        "{name} runs a pet clinic and looks after every patient.",
        "{name} writes care plans, reads about animals and keeps the clinic's numbers.",
    ),
    _t(
        "body",
        "The human body",
        "body heart brain bone muscle lung doctor health hospital " "nutrition",
        ("Inside the Human Body", "Doctor on Duty"),
        "{name} explores how the body works.",
        "{name} reads about the body, measures and records, and explains it back.",
    ),
    _t(
        "ancient",
        "Ancient Egypt",
        "egypt egyptian pharaoh pyramid mummy nile hieroglyph ancient " "tomb",
        ("Secrets of the Pyramids", "Pharaoh for a Week"),
        "{name} uncovers the secrets of the pyramids.",
        "{name} decodes picture writing, reads ancient history and solves digs with numbers.",
    ),
    _t(
        "gardening",
        "Backyard nature",
        "nature backyard pond bird forest tree leaf flower wildlife " "hiking creek",
        ("Backyard Nature Journal", "Bird Watchers Club"),
        "{name} becomes the expert on the wildlife outside the door.",
        "{name} observes nature, records data and writes up discoveries.",
    ),
    _t(
        "theater",
        "Putting on a play",
        "play theater theatre stage actor drama puppet script " "performance",
        ("Opening Night Theater", "Puppet Show Production"),
        "{name} writes and stages a show.",
        "{name} writes a script, practices reading aloud and plans the tickets and set.",
    ),
    _t(
        "money",
        "Running a shop",
        "shop store market money coin price customer business " "lemonade entrepreneur bank",
        ("Lemonade Stand Boss", "Corner Shop Owner"),
        "{name} opens a shop and keeps the books.",
        "{name} prices goods, makes change and writes signs and orders.",
    ),
)

TOPICS_BY_KEY = {t.key: t for t in TOPICS}


def _stem(word: str) -> str:
    w = word.lower().strip("'")
    if w.endswith("'s"):
        w = w[:-2]
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith(("ches", "shes", "sses", "xes")):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    if len(w) > 5 and w.endswith("ing"):
        return w[:-3]
    return w


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z]+(?:'[a-z]+)?", (text or "").lower())]


def content_stems(text: str) -> set[str]:
    """The words of ``text`` that carry its subject (stemmed, generic words removed)."""
    out = set()
    for tok in _tokens(text):
        if tok in GENERIC:
            continue
        stem = _stem(tok)
        if len(stem) > 2 and stem not in GENERIC:
            out.add(stem)
    return out


_THEME_OF_STEM: dict[str, set[str]] = {}
for _topic in TOPICS:
    for _w in _topic.words:
        _THEME_OF_STEM.setdefault(_stem(_w), set()).add(_topic.key)


def themes_of(text: str) -> set[str]:
    """Theme keys whose word families appear in ``text`` (every token, generic ones included)."""
    found: set[str] = set()
    for tok in _tokens(text):
        found |= _THEME_OF_STEM.get(_stem(tok), set())
    return found


@dataclass(frozen=True)
class OptionText:
    topic: str
    title: str
    hook: str = ""


def _main_stems(o: OptionText) -> set[str]:
    return content_stems(o.topic) | content_stems(o.title)


def _themes(o: OptionText) -> set[str]:
    return themes_of(o.topic) | themes_of(o.title) | themes_of(o.hook)


def distinctness_problems(options: Sequence[OptionText], recent: Iterable[str] = ()) -> list[str]:
    """Plain-language reasons the topics fail the gate (empty list: they pass)."""
    problems: list[str] = []
    for i in range(len(options)):
        for j in range(i + 1, len(options)):
            a, b = options[i], options[j]
            shared = _main_stems(a) & _main_stems(b)
            if shared:
                problems.append(
                    f"options {i + 1} and {j + 1} share the word {sorted(shared)[0]!r}; "
                    "give each option a completely different topic"
                )
                continue
            theme = _themes(a) & _themes(b)
            if theme:
                problems.append(
                    f"options {i + 1} and {j + 1} are both about {sorted(theme)[0]}; "
                    "the three topics must not overlap"
                )
    for text in recent:
        r_stems, r_themes = content_stems(text), themes_of(text)
        for i, o in enumerate(options):
            if _main_stems(o) & r_stems or _themes(o) & r_themes:
                problems.append(
                    f"option {i + 1} repeats a recent topic ({text!r}); choose something new"
                )
    return problems


def title_problems(title: str) -> str | None:
    words = title.split()
    if len(words) > MAX_TITLE_WORDS:
        return f"title must be at most {MAX_TITLE_WORDS} words (got {len(words)}): {title!r}"
    if len(title) > MAX_TITLE_CHARS:
        return f"title must be at most {MAX_TITLE_CHARS} characters: {title!r}"
    return None


def _digest(seed: str, key: str) -> str:
    return hashlib.sha256(f"{seed}|{key}".encode()).hexdigest()


def vetted_menu(
    seed: str, interests: Sequence[str] = (), recent: Iterable[str] = (), size: int = 8
) -> list[Topic]:
    """Vetted topics to offer, seeded, with recent themes removed and interest matches first."""
    recent_themes: set[str] = set()
    for text in recent:
        recent_themes |= themes_of(text)
    interest_themes: set[str] = set()
    for text in interests:
        interest_themes |= themes_of(text)
    pool = [t for t in TOPICS if t.key not in recent_themes]
    pool.sort(key=lambda t: (0 if t.key in interest_themes else 1, _digest(seed, t.key)))
    return pool[:size]


def template_options(
    seed: str,
    first_name: str,
    interests: Sequence[str] = (),
    recent: Iterable[str] = (),
) -> list[Topic]:
    """Three curated topics from three different themes, deterministic for ``seed``."""
    recent = list(recent)
    picks: list[Topic] = []
    for t in vetted_menu(seed, interests, recent, size=len(TOPICS)):
        candidate = [*picks, t]
        texts = [
            OptionText(x.label, x.titles[0], x.hook.format(name=first_name)) for x in candidate
        ]
        if not distinctness_problems(texts):
            picks = candidate
        if len(picks) == 3:
            break
    if len(picks) < 3:  # everything recent: relax the recent filter, keep the options distinct
        for t in sorted(TOPICS, key=lambda t: _digest(seed, t.key)):
            if t in picks:
                continue
            texts = [
                OptionText(x.label, x.titles[0], x.hook.format(name=first_name))
                for x in [*picks, t]
            ]
            if not distinctness_problems(texts):
                picks.append(t)
            if len(picks) == 3:
                break
    return picks
