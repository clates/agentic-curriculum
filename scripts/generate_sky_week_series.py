"""
Sky and Space — Week Series
Grade K–1 | Science | Causal Arc: Sun as Our Star → The Moon → Stars and the Night Sky → Day and Night Patterns → Putting It All Together

Narrator: Luna the Little Owl, introduced on Monday. A young owl who watches the sky from
sunrise to sunrise, noticing everything that moves, glows, and changes overhead.
Output: single printable HTML document — sky_week_series/sky_week.html

Standards (Virginia SOL):
  Monday    — VA.SCIENCE.K.k.8, VA.SCIENCE.K.k.8.a, VA.SCIENCE.1.1.6, VA.SCIENCE.1.1.6.a
              (the Sun: our star, source of light and warmth, warms Earth's land, air, and water)
  Tuesday   — VA.SCIENCE.K.k.8.b, VA.SCIENCE.K.k.8.c, VA.SCIENCE.1.1.6.b
              (shadows: how shadows form, temperature in sun vs. shade, sun's position changes during the day)
  Wednesday — VA.SCIENCE.K.k.9, VA.SCIENCE.K.k.9.c
              (the Moon: patterns in nature, day and night, the Moon's appearance and phases overview)
  Thursday  — VA.SCIENCE.K.k.9, VA.SCIENCE.K.k.9.a, VA.SCIENCE.K.k.9.c
              (stars and the night sky: patterns in nature, day/night cycle, star patterns)
  Friday    — VA.SCIENCE.K.k.9, VA.SCIENCE.K.k.9.c, VA.SCIENCE.1.1.6, VA.SCIENCE.1.1.6.a, VA.SCIENCE.1.1.6.b
              (capstone: day and night patterns, Earth's rotation, everything in the sky has a pattern)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html


def generate_sky_week_series():
    output_dir = Path("sky_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — The Sun: Our Nearest Star
    # Standards: VA.SCIENCE.K.k.8, VA.SCIENCE.K.k.8.a, VA.SCIENCE.1.1.6, VA.SCIENCE.1.1.6.a
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: The Sun — Our Nearest Star",
            "passage_title": "Meet Luna — and the Great Ball of Fire!",
            "instructions": (
                "Before reading: Go outside and look at the sky. "
                "Feel the warmth on your skin. Is it warm in the sun and cooler in the shade? "
                "Come inside and share what you felt."
            ),
            "passage": (
                "Meet Luna the Little Owl! Luna has soft brown feathers, enormous golden eyes, "
                "and a tiny curved beak. Every single night — and even during the day — "
                "Luna watches the sky. 'The sky is always changing,' Luna hoots to herself. "
                "'Something up there is always moving or glowing or making a shadow!'\n\n"
                "The most important object in our sky is the Sun. The Sun is a star — "
                "a giant ball of burning gas that glows with incredible light and heat. "
                "It is so big that more than one million Earths could fit inside it! "
                "But it looks small in our sky because it is very, very far away. "
                "Even so, the Sun is the closest star to Earth, which is why it looks "
                "so much bigger and brighter than any other star we see.\n\n"
                "The Sun gives Earth two very important things: light and warmth. "
                "Sunlight travels from the Sun all the way to Earth in about eight minutes — "
                "even though the Sun is so far away! When sunlight reaches Earth, "
                "it warms the land, the water, and the air. Without the Sun, "
                "our planet would be a frozen, dark ball in space. "
                "There would be no plants, no animals, and no people.\n\n"
                "'I am so grateful for the Sun,' Luna hooted, blinking her golden eyes "
                "in the morning light. 'Even I, a night owl, need the Sun to keep our "
                "world alive. Every living thing on Earth depends on it!'"
            ),
            "vocabulary": [
                {
                    "term": "Sun",
                    "definition": "A star — a giant ball of burning gas — that gives Earth light and warmth.",
                },
                {
                    "term": "star",
                    "definition": "A giant ball of burning gas in space that makes its own light and heat.",
                },
                {
                    "term": "light",
                    "definition": "Energy from the Sun that lets us see during the day and helps plants grow.",
                },
                {
                    "term": "warmth",
                    "definition": "Heat energy from the Sun that warms Earth's land, water, and air.",
                },
                {
                    "term": "energy",
                    "definition": "The power that makes things work — the Sun sends light and heat energy to Earth.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is the Sun? Use the word 'star' in your answer.",
                    "response_lines": 2,
                },
                {
                    "prompt": "Name the two important things the Sun gives to Earth.",
                    "response_lines": 2,
                },
                {
                    "prompt": "What would happen to Earth if the Sun disappeared? Use evidence from the passage.",
                    "response_lines": 3,
                },
                {
                    "prompt": "LET'S DISCUSS: The Sun is a star, but other stars look tiny at night. Why do you think the Sun looks so much bigger and brighter than the other stars in the sky?",
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    add(
        "featureMatrixWorksheet",
        {
            "title": "Monday: What Does the Sun Do? — Feature Matrix",
            "instructions": (
                "Put a check mark in every box that is true for each object. "
                "Think carefully — not every box will be checked!"
            ),
            "items": ["The Sun", "A Rock", "A Plant", "The Moon"],
            "properties": [
                "Makes its own light",
                "Gives warmth to Earth",
                "Is a star",
                "Can be seen in daytime sky",
                "Needs sunlight to survive",
            ],
        },
        "Monday",
    )

    # =========================================================================
    # TUESDAY — Shadows and the Sun's Journey
    # Standards: VA.SCIENCE.K.k.8.b, VA.SCIENCE.K.k.8.c, VA.SCIENCE.1.1.6.b
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: Shadows and the Sun's Journey",
            "passage_title": "Why Do Shadows Change? Luna Investigates!",
            "instructions": (
                "Before reading: Go outside in the morning. "
                "Stand in the sunshine and look at your shadow. Which direction does it point? "
                "If you can, check your shadow again at noon. Is it longer or shorter?"
            ),
            "passage": (
                "Luna was curious about shadows. One morning, she stood on a fence post "
                "and noticed her shadow stretching out long behind her. "
                "'Why is my shadow so long now but short at lunchtime?' she wondered.\n\n"
                "A shadow forms when something blocks the Sun's light. "
                "When an object — like a tree, a building, or an owl on a fence — "
                "stands in sunlight, it blocks some of the light from passing through. "
                "The dark area on the other side of the object, where the light cannot reach, "
                "is the shadow. The shadow is always on the opposite side of the object "
                "from the Sun.\n\n"
                "Here is something fascinating: the Sun does not stay in the same place in the sky! "
                "In the morning, the Sun is low in the east. It slowly moves across the sky "
                "and is highest at noon — right in the middle of the day. "
                "By evening, the Sun is low in the west. "
                "Because the Sun changes its position, shadows change too.\n\n"
                "In the morning and evening, when the Sun is low, shadows are LONG. "
                "At noon, when the Sun is high overhead, shadows are SHORT — "
                "almost straight under your feet! "
                "'So my shadow is like a clock!' Luna hooted happily. "
                "She also noticed something else: objects standing in sunlight feel WARM, "
                "but objects in the shadow feel COOLER. "
                "Sunlight carries heat energy — shade blocks that energy from reaching the ground."
            ),
            "vocabulary": [
                {
                    "term": "shadow",
                    "definition": "A dark area made when an object blocks the Sun's light from reaching a surface.",
                },
                {
                    "term": "blocks",
                    "definition": "When an object stops light from passing through, creating a shadow.",
                },
                {
                    "term": "position",
                    "definition": "Where the Sun is in the sky — low in the east in the morning, high at noon, low in the west at night.",
                },
                {
                    "term": "east",
                    "definition": "The direction where the Sun rises each morning.",
                },
                {
                    "term": "west",
                    "definition": "The direction where the Sun sets each evening.",
                },
            ],
            "questions": [
                {
                    "prompt": "How does a shadow form? What must happen for a shadow to appear?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Why are shadows longer in the morning than at noon?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Why is it cooler in a shadow than in direct sunlight?",
                    "response_lines": 2,
                },
                {
                    "prompt": "If you see a very short shadow under a tree, what time of day do you think it is? Why?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: Luna says her shadow is like a clock. How can you use your own shadow to tell something about the time of day? Try it today!",
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "tChartWorksheet",
        {
            "title": "Tuesday: Sun vs. Shade — T-Chart",
            "instructions": (
                "Write or draw ideas in the correct column. "
                "Think about temperature, light, shadows, and plants. "
                "Use the word bank below to get started — add your own ideas too!"
            ),
            "columns": ["In the Sunshine", "In the Shade"],
            "row_count": 7,
            "word_bank": [
                "Warm",
                "Cool",
                "Bright light",
                "Dark shadow",
                "Long shadow",
                "Short shadow",
                "Shadow disappears",
                "Feels hot to touch",
                "Good place to rest",
            ],
        },
        "Tuesday",
    )

    # =========================================================================
    # WEDNESDAY — The Moon: Our Nighttime Neighbor
    # Standards: VA.SCIENCE.K.k.9, VA.SCIENCE.K.k.9.c
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: The Moon — Our Nighttime Neighbor",
            "passage_title": "What Is That Glowing Ball in the Night Sky?",
            "instructions": (
                "Read about the Moon with Luna. Then answer the questions below.\n\n"
                "Outdoor activity: Tonight, go outside after dark and look for the Moon. "
                "Is it a full circle, a half circle, or just a thin sliver? "
                "Draw what you see in the space on your worksheet."
            ),
            "passage": (
                "Luna loved the Moon more than almost anything. Every night, she would look up "
                "at its glowing face and hoot softly. 'You are not a star,' she said to the Moon, "
                "'but you are so bright! How do you make all that light?'\n\n"
                "Here is the secret: the Moon makes NO light of its own. "
                "The Moon is a big ball of rock — much smaller than Earth — "
                "that travels around our planet. The beautiful glow we see is really "
                "reflected sunlight. Just like a mirror bounces light across a room, "
                "the Moon's rocky surface bounces sunlight back to us on Earth. "
                "So the Moon is lit up by the Sun, even at night!\n\n"
                "The Moon orbits — travels around — Earth about once every four weeks. "
                "As it travels, the part of the Moon that is lit by the Sun "
                "looks different from Earth each night. "
                "Sometimes we see the whole lit side — a full moon, a big bright circle. "
                "Sometimes we see only half — a half moon. "
                "Sometimes we see just a thin sliver — a crescent moon. "
                "And sometimes the Moon's lit side faces away from Earth "
                "and we can barely see it at all — a new moon.\n\n"
                "Luna watched the Moon go through all its shapes over many nights. "
                "'The Moon follows a pattern,' she hooted with delight. "
                "'It always changes from new moon to crescent to half to full and back again. "
                "Every month, the same pattern! Patterns in the sky are so wonderful.'"
            ),
            "vocabulary": [
                {
                    "term": "Moon",
                    "definition": "A large ball of rock that travels around Earth and reflects sunlight.",
                },
                {
                    "term": "reflected light",
                    "definition": "Light that bounces off a surface — the Moon glows because it reflects sunlight.",
                },
                {
                    "term": "orbit",
                    "definition": "To travel around another object in a curved path — the Moon orbits Earth.",
                },
                {
                    "term": "phase",
                    "definition": "One of the different shapes the Moon appears to have as it orbits Earth.",
                },
                {
                    "term": "full moon",
                    "definition": "When we can see the entire lit side of the Moon — it looks like a bright circle.",
                },
                {
                    "term": "crescent",
                    "definition": "A thin curved sliver shape — the Moon looks like this when only a small part of its lit side faces Earth.",
                },
            ],
            "questions": [
                {
                    "prompt": "Does the Moon make its own light? Where does moonlight really come from?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Name two moon shapes (phases) described in the passage.",
                    "response_lines": 2,
                },
                {
                    "prompt": "Why does the Moon seem to change shape over the month?",
                    "response_lines": 3,
                },
                {
                    "prompt": "Luna says the Moon follows a pattern. What is that pattern?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: The Moon has no air or water and makes no light of its own — but we can see it clearly at night. Could you see the Moon if the Sun did not exist? Why or why not?",
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "matchingWorksheet",
        {
            "title": "Wednesday: Moon Phases — Matching",
            "instructions": (
                "Draw a line from each moon phase name on the left to its correct description on the right."
            ),
            "left_items": [
                "Full Moon",
                "New Moon",
                "Crescent Moon",
                "Half Moon",
                "Reflected light",
                "Orbit",
            ],
            "right_items": [
                "The whole lit side faces Earth — a bright circle",
                "The lit side faces away — barely visible",
                "A thin curved sliver of the Moon is visible",
                "Half of the lit side faces Earth",
                "Sunlight bouncing off the Moon's rocky surface",
                "The Moon's path as it travels around Earth",
            ],
        },
        "Wednesday",
    )

    # =========================================================================
    # THURSDAY — Stars and the Night Sky
    # Standards: VA.SCIENCE.K.k.9, VA.SCIENCE.K.k.9.a, VA.SCIENCE.K.k.9.c
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: Stars and the Night Sky",
            "passage_title": "Thousands of Suns — Luna Looks at the Stars",
            "instructions": (
                "Read about stars with Luna. Then answer the questions below.\n\n"
                "Nighttime activity: On a clear night, go outside after dark with a grown-up. "
                "Count how many stars you can see in a small patch of sky. "
                "Can you find a group of stars that makes a pattern or picture?"
            ),
            "passage": (
                "Luna opened her huge golden eyes wide. On a clear, moonless night, "
                "the sky above her was absolutely covered with tiny points of light. "
                "'How many stars are there?' she whispered in awe.\n\n"
                "Stars are giant balls of burning gas — just like our Sun! "
                "They look tiny because they are incredibly far away. "
                "If you could travel at the speed of light, it would take over four years "
                "just to reach the closest star beyond our Sun. "
                "Our Sun is a medium-sized, yellow star. Some stars are much bigger and "
                "brighter. Some are smaller and dimmer. Stars can look white, yellowish, "
                "orange, or even bluish, depending on how hot they are.\n\n"
                "Long ago, people looked at groups of stars and imagined shapes connecting them — "
                "like connect-the-dots in the sky. These star pictures are called constellations. "
                "Famous constellations include the Big Dipper, which looks like a giant "
                "ladle or spoon, and Orion the Hunter, which has three stars in a row "
                "that form his belt. People used constellations for navigation — "
                "sailors used the stars to find their way across the ocean at night.\n\n"
                "Stars seem to slowly move across the sky through the night, "
                "following a pattern just like the Sun and Moon. "
                "Luna watched one bright star rise in the east after sunset, "
                "arc slowly across the sky, and sink in the west before dawn. "
                "'Everything in the sky follows a pattern,' she thought with wonder. "
                "'The Sun, the Moon, the stars — they all rise in the east and set in the west.'"
            ),
            "vocabulary": [
                {
                    "term": "stars",
                    "definition": "Giant balls of burning gas very far away in space — our Sun is a star.",
                },
                {
                    "term": "constellation",
                    "definition": "A group of stars that form a pattern or picture in the night sky.",
                },
                {
                    "term": "Big Dipper",
                    "definition": "A famous constellation that looks like a big ladle or spoon.",
                },
                {
                    "term": "navigation",
                    "definition": "Finding your way from one place to another — sailors used stars to navigate at sea.",
                },
                {
                    "term": "rise",
                    "definition": "When the Sun, Moon, or stars appear to come up in the east part of the sky.",
                },
                {
                    "term": "set",
                    "definition": "When the Sun, Moon, or stars appear to sink down in the west part of the sky.",
                },
            ],
            "questions": [
                {
                    "prompt": "What are stars made of? How are they like and different from our Sun?",
                    "response_lines": 3,
                },
                {
                    "prompt": "What is a constellation? Give one example from the passage.",
                    "response_lines": 2,
                },
                {
                    "prompt": "How did sailors long ago use the stars? Why were constellations useful?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What pattern do stars follow in the night sky — in which direction do they rise and set?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: Stars look tiny but they are actually enormous — some are bigger than our entire solar system. Why do you think they look so small from Earth?",
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    add(
        "oddOneOutWorksheet",
        {
            "title": "Thursday: Sky Objects — Odd One Out",
            "instructions": (
                "Look at each row of sky words. Circle the one that does NOT belong with the others. "
                "Write or tell a grown-up why!"
            ),
            "rows": [
                {
                    "items": ["The Sun", "The Moon", "A Rock on the Ground", "A Star"],
                    "reasoning_lines": 1,
                },
                {
                    "items": ["Full Moon", "Crescent Moon", "Half Moon", "The Sun"],
                    "reasoning_lines": 1,
                },
                {
                    "items": ["Makes its own light", "Reflects sunlight", "Is a star", "Burns gas"],
                    "reasoning_lines": 1,
                },
                {
                    "items": ["Big Dipper", "Orion", "The Moon", "Constellation"],
                    "reasoning_lines": 1,
                },
                {
                    "items": [
                        "Rises in the east",
                        "Sets in the west",
                        "Stays still all day",
                        "Moves across the sky",
                    ],
                    "reasoning_lines": 1,
                },
            ],
        },
        "Thursday",
    )

    # =========================================================================
    # FRIDAY — Day and Night Patterns (Capstone)
    # Standards: VA.SCIENCE.K.k.9, VA.SCIENCE.K.k.9.c, VA.SCIENCE.1.1.6, VA.SCIENCE.1.1.6.a, VA.SCIENCE.1.1.6.b
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: Day and Night — Why Does the Sky Change?",
            "passage_title": "Luna's Big Discovery: Earth Never Stops Spinning!",
            "instructions": (
                "Read the capstone passage with Luna. Then answer all the questions.\n\n"
                "Capstone activity: Use a flashlight and a globe or round ball. "
                "Shine the flashlight on one side of the ball — that side is 'day.' "
                "Slowly spin the ball — watch as the lit side (day) and dark side (night) rotate. "
                "That is exactly what happens on Earth every 24 hours!"
            ),
            "passage": (
                "By Friday, Luna had watched the sky all week and she was full of questions. "
                "'The Sun rises every morning and sets every evening. The Moon comes out at night. "
                "The stars move across the sky. WHY does everything keep moving?' she hooted.\n\n"
                "The secret is that EARTH is spinning! Earth rotates — turns like a spinning top — "
                "once every 24 hours. That is why a day and a night together last exactly 24 hours. "
                "As Earth spins, the side facing the Sun has daytime — bright, warm, and full of light. "
                "The side facing away from the Sun has nighttime — dark and cooler. "
                "The Sun does not actually move across our sky; it just looks that way because "
                "WE are spinning around!\n\n"
                "In the morning, your part of Earth rotates toward the Sun — that is sunrise. "
                "The Sun appears in the east, and shadows are long. "
                "By noon, your part of Earth faces the Sun directly — the Sun looks highest in the sky "
                "and shadows are shortest. In the evening, your part of Earth rotates away — "
                "that is sunset. The Sun disappears in the west.\n\n"
                "At night, the Moon and stars come out because the bright Sun is no longer "
                "washing out their faint light. The Moon reflects the Sun's light across space "
                "to light up our night. Stars glow with their own light, millions of miles away.\n\n"
                "Luna ruffled her feathers happily. 'Now I understand! "
                "The Sun heats our world. Shadows show where the Sun's light is blocked. "
                "The Moon glows by reflecting the Sun. Stars are distant suns. "
                "And day and night are caused by Earth spinning once every 24 hours. "
                "Everything in the sky follows a pattern — and I have watched them all!'"
            ),
            "vocabulary": [
                {
                    "term": "rotation",
                    "definition": "Earth spinning on its axis — one full rotation takes 24 hours and causes day and night.",
                },
                {
                    "term": "day",
                    "definition": "The time when your part of Earth faces the Sun — bright, warm, and light outside.",
                },
                {
                    "term": "night",
                    "definition": "The time when your part of Earth faces away from the Sun — dark and cooler outside.",
                },
                {
                    "term": "sunrise",
                    "definition": "When Earth rotates so your area turns toward the Sun — the Sun appears in the east.",
                },
                {
                    "term": "sunset",
                    "definition": "When Earth rotates so your area turns away from the Sun — the Sun disappears in the west.",
                },
                {
                    "term": "pattern",
                    "definition": "Something that repeats in a predictable way — day and night follow a 24-hour pattern.",
                },
            ],
            "questions": [
                {
                    "prompt": "What causes day and night on Earth? Use the word 'rotation' in your answer.",
                    "response_lines": 3,
                },
                {
                    "prompt": "Why does the Sun appear to move across the sky during the day, even though the Sun is not actually moving?",
                    "response_lines": 3,
                },
                {
                    "prompt": "Why can't we see stars during the daytime?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Connect the whole week: explain the chain Sun → shadows → Moon → stars → day and night. What ties them all together?",
                    "response_lines": 4,
                },
                {
                    "prompt": "LET'S DISCUSS: If Earth stopped spinning, one side would always be day and the other side would always be night. What do you think would happen to the plants and animals on each side?",
                    "response_lines": 0,
                },
            ],
        },
        "Friday",
    )

    add(
        "treeMapWorksheet",
        {
            "title": "Friday: The Sky — Tree Map Capstone",
            "instructions": (
                "Sort each sky word from the word bank into the correct branch. "
                "Each word belongs in only one branch — think carefully!"
            ),
            "root_label": "Things in the Sky",
            "branches": [
                {"label": "The Sun", "slot_count": 4},
                {"label": "The Moon", "slot_count": 4},
                {"label": "Stars", "slot_count": 4},
            ],
            "columns": 3,
            "word_bank": [
                "Makes its own light",
                "Reflects sunlight",
                "Giant ball of burning gas",
                "Has phases (shapes)",
                "Our nearest star",
                "Constellations",
                "Orbits Earth",
                "Warms Earth's surface",
                "Can only be seen at night",
                "Rises in the east",
                "Used for navigation",
                "Makes shadows on Earth",
            ],
        },
        "Friday",
    )

    # =========================================================================
    # PARENT FEEDBACK & TEACHING NOTES
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "End-of-Week Parent Feedback — Sky and Space Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this feedback sheet after the week wraps up. "
                "Your notes help shape next week's lessons."
            ),
            "passage": (
                "This week followed a causal arc through the sky and space. "
                "Monday established the Sun as our nearest star and the source of Earth's "
                "light and warmth. Tuesday explored how the Sun's changing position creates "
                "shadows of different lengths, and how objects in sunlight are warmer than "
                "objects in shade. Wednesday introduced the Moon — a rocky body that reflects "
                "sunlight and orbits Earth, showing changing phases over a month. "
                "Thursday zoomed out to the wider night sky: stars as distant suns, "
                "constellations as patterns people have named, and the shared east-to-west "
                "motion of all sky objects. Friday unified everything with Earth's rotation — "
                "the reason day follows night every 24 hours, shadows change direction, "
                "and the Sun appears to move across the sky.\n\n"
                "Luna the Little Owl appeared throughout the week as a curious narrator "
                "watching the sky from dusk to dawn, giving Christopher a character who "
                "experiences the sky from a unique bird's-eye perspective.\n\n"
                "Key concepts to check for genuine understanding — not just recall:\n"
                "1) The Sun is a STAR — our nearest one.\n"
                "2) The Moon makes NO light of its own; it reflects sunlight.\n"
                "3) Shadows change because the Sun's position in the sky changes (not because the Sun moves — Earth rotates).\n"
                "4) Stars are distant suns — they only look small because they are far away.\n"
                "5) Day and night are caused by Earth's rotation, not the Sun moving.\n\n"
                "Common misconceptions to watch for:\n"
                "- 'The Sun moves across the sky' — It only appears to move; Earth is spinning.\n"
                "- 'The Moon makes its own light' — It reflects sunlight; no Sun means no visible Moon.\n"
                "- 'Stars disappear in the daytime' — They are still there; sunlight is just too bright to see them.\n"
                "- 'The Moon changes shape' — Its shape doesn't change; we see different amounts of its lit side.\n\n"
                "Suggested follow-on activities: track moon phases on a calendar for one month; "
                "use a flashlight and globe to model day and night; make a sundial and track "
                "shadow movement through the day."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": "The Sun does NOT move across the sky — Earth rotates, making the Sun APPEAR to move.",
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in after the week — which idea did Christopher grasp best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": "Seasons — why does the Sun feel hotter in summer? How does Earth's tilt change how much sunlight reaches us?",
                },
            ],
            "questions": [
                {
                    "prompt": "Overall comfort with the week's content — how well did Christopher grasp the concepts? (1 = struggled throughout, 5 = strong grasp of all concepts)",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which day's activity or concept sparked the most curiosity or questions from Christopher?",
                    "response_lines": 2,
                },
                {
                    "prompt": "By Friday, could Christopher explain why we have day and night (Earth's rotation)? Could he explain why the Moon glows?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Did any real sky events happen during the week (a visible Moon phase, a clear starry night, a long morning shadow) that connected to the lessons?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Topics or vocabulary to revisit next week:",
                    "response_lines": 2,
                },
            ],
        },
        "Friday",
    )

    # =========================================================================
    # Assemble & write
    # =========================================================================

    html = build_print_packet_html(
        pages, packet_title="Sky and Space Week — Science for Christopher"
    )
    out_path = output_dir / "sky_week.html"
    out_path.write_text(html, encoding="utf-8")

    # Teacher guide
    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Sky and Space Week — Teacher Guide</title>
  <style>
    @page { size: letter; margin: 0.5in 0.6in; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Trebuchet MS', Arial, sans-serif; font-size: 11pt; color: #111; line-height: 1.55; }
    @media screen { body { background: #b0b0b0; padding: 24px; } .page { background: white; max-width: 7.5in; margin: 0 auto 28px; padding: 0.45in 0.5in; box-shadow: 0 4px 18px rgba(0,0,0,.28); min-height: 10.3in; } }
    @media print { body { background: white; padding: 0; } .page { padding: 0; box-shadow: none; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
    .page { page-break-after: always; break-after: page; }
    .page:last-child { page-break-after: avoid; break-after: avoid; }
    h1 { font-size: 18pt; color: #1d4ed8; border-bottom: 3px solid #1d4ed8; padding-bottom: 5px; margin-bottom: 12px; }
    h2 { font-size: 13pt; color: #fff; background: #1d4ed8; padding: 5px 10px; border-radius: 3px; margin: 14px 0 6px; }
    h2.tue { background: #15803d; }
    h2.wed { background: #7c3aed; }
    h2.thu { background: #c2410c; }
    h2.fri { background: #0f766e; }
    h3 { font-size: 10.5pt; font-weight: bold; color: #444; margin: 8px 0 3px; text-transform: uppercase; letter-spacing: 0.04em; }
    p, li { font-size: 10pt; margin-bottom: 5px; }
    ul { padding-left: 18px; margin-bottom: 8px; }
    .answer-box { background: #f0f4ff; border-left: 4px solid #1d4ed8; padding: 6px 10px; margin: 4px 0 10px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .answer-box.tue { background: #f0fff4; border-color: #15803d; }
    .answer-box.wed { background: #f5f0ff; border-color: #7c3aed; }
    .answer-box.thu { background: #fff7f0; border-color: #c2410c; }
    .answer-box.fri { background: #f0fff8; border-color: #0f766e; }
    .misconception { background: #fff3cd; border-left: 4px solid #d97706; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .extension { background: #e8f5e9; border-left: 4px solid #15803d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .discuss { background: #fce7f3; border-left: 4px solid #9d174d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
  </style>
</head>
<body>

<div class="page">
  <h1>Sky and Space Week — Teacher / Parent Guide</h1>
  <p><strong>Theme:</strong> Sky and Space (Sun, Moon, Stars, Day &amp; Night) &nbsp;|&nbsp;
  <strong>Audience:</strong> Christopher, age 6, K&ndash;1 &nbsp;|&nbsp;
  <strong>Narrator:</strong> Luna the Little Owl</p>
  <p><strong>Causal Arc:</strong> Sun as Our Nearest Star &rarr; Shadows &amp; Sun&#8217;s Journey &rarr; The Moon &amp; Its Phases &rarr; Stars &amp; Constellations &rarr; Earth&#8217;s Rotation &amp; Day/Night Patterns</p>
  <p><strong>Standards covered:</strong> VA.SCIENCE.K.k.8, K.k.8.a&ndash;c, K.k.9, K.k.9.a, K.k.9.c, 1.1.6, 1.1.6.a&ndash;b</p>

  <h2>Monday &mdash; The Sun: Our Nearest Star</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1 (What is the Sun):</strong> The Sun is a star &mdash; a giant ball of burning gas that gives Earth light and heat/warmth.</p>
    <p><strong>Q2 (Two important things):</strong> Light and warmth (heat energy).</p>
    <p><strong>Q3 (Without the Sun):</strong> Earth would be a frozen, dark ball in space. There would be no plants, no animals, no people. Accept any answer citing lack of light or warmth leading to no life.</p>
  </div>
  <h3>Feature Matrix Answer Key</h3>
  <div class="answer-box">
    <p><strong>The Sun:</strong> Makes its own light &#10003;, Gives warmth to Earth &#10003;, Is a star &#10003;, Can be seen in daytime sky &#10003;</p>
    <p><strong>A Rock:</strong> Can be seen in daytime sky &#10003; (only if in sun — accept either)</p>
    <p><strong>A Plant:</strong> Needs sunlight to survive &#10003;, Can be seen in daytime sky &#10003;</p>
    <p><strong>The Moon:</strong> Can be seen in daytime sky &#10003; (sometimes, at certain phases — discuss this!)</p>
    <p><em>Note: The Moon row is intentionally thought-provoking — the Moon IS sometimes visible in daytime. Use this as a teaching moment.</em></p>
  </div>
  <h3>LET&#8217;S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Why does the Sun look bigger and brighter than other stars?"</em></p>
    <p>Because the Sun is MUCH closer to Earth than any other star. Distance makes objects appear smaller and dimmer. Other stars are billions of miles farther away. You can demonstrate with a flashlight: close up it&#8217;s blinding; across the room it&#8217;s just a small bright dot.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Children often think "the Sun is not a star" because stars only come out at night. Reinforce: the Sun IS a star &mdash; it just looks different because it&#8217;s so much closer. All those tiny stars in the night sky are suns, just very far away.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Sun warmth experiment: Place two identical small cups of water outside &mdash; one in direct sunlight, one in shade. After 20 minutes, test the temperature with a finger (or thermometer). Which is warmer? Discuss why sunlight carries heat energy.</p>
  </div>

  <h2 class="tue">Tuesday &mdash; Shadows and the Sun&#8217;s Journey</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box tue">
    <p><strong>Q1 (Shadow formation):</strong> A shadow forms when an object blocks the Sun&#8217;s light. The Sun shines on an object, the object stops the light, and a dark area (shadow) appears on the other side.</p>
    <p><strong>Q2 (Long morning shadows):</strong> In the morning, the Sun is low in the sky (in the east). When the Sun is low, it casts long shadows. At noon, the Sun is high overhead, so shadows fall almost straight down and are very short.</p>
    <p><strong>Q3 (Cooler in shade):</strong> Sunlight carries heat energy. A shadow blocks sunlight from reaching the ground, so the ground in the shade does not receive that heat energy and stays cooler.</p>
    <p><strong>Q4 (Time of day):</strong> If a shadow is very short (almost straight under the tree), it is probably around noon, when the Sun is highest in the sky.</p>
  </div>
  <h3>T-Chart Guidance</h3>
  <div class="answer-box tue">
    <p><strong>In the Sunshine:</strong> Warm, Bright light, Short shadow (at noon), Feels hot to touch, Makes things dry faster</p>
    <p><strong>In the Shade:</strong> Cool, Dark shadow, Long shadow (morning/evening), Good place to rest, Stays moist longer</p>
    <p><em>Accept any reasonable answers that distinguish temperature and light between the two columns.</em></p>
  </div>
  <h3>LET&#8217;S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"How can you use your shadow like a clock?"</em></p>
    <p>Short shadow = near noon (Sun is high). Long shadow pointing west = morning (Sun is in the east behind you). Long shadow pointing east = afternoon/evening (Sun is in the west behind you). Ancient people really did use shadow sticks (sundials) to tell time! Try making one together today.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Children often say "the shadow moves because the wind blows it." Correct this: shadows move because the SUN&#8217;S POSITION changes (which happens because Earth rotates &mdash; this connects to Friday&#8217;s lesson). Wind has nothing to do with shadow direction.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Shadow stick sundial: Push a pencil or stick vertically into a lump of clay on white paper. Trace the shadow line and mark the time every hour from morning to afternoon. By end of day you will have a working sundial showing how shadow length and direction change throughout the day.</p>
  </div>
</div>

<div class="page">
  <h2 class="wed">Wednesday &mdash; The Moon: Our Nighttime Neighbor</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1 (Moonlight source):</strong> No, the Moon makes no light of its own. Moonlight is reflected sunlight &mdash; the Moon&#8217;s rocky surface bounces sunlight back to Earth, like a mirror.</p>
    <p><strong>Q2 (Two phases):</strong> Any two of: full moon (bright circle), half moon, crescent moon (thin sliver), new moon (barely visible).</p>
    <p><strong>Q3 (Why phases change):</strong> As the Moon orbits Earth, we see different amounts of its lit side. When the fully lit side faces Earth = full moon. When only part of the lit side faces us = crescent or half moon.</p>
    <p><strong>Q4 (Pattern):</strong> New moon &rarr; crescent &rarr; half moon &rarr; full moon &rarr; back to new moon. This repeats about every four weeks (one month).</p>
  </div>
  <h3>Matching Answer Key</h3>
  <div class="answer-box wed">
    <p>Full Moon &rarr; The whole lit side faces Earth &mdash; a bright circle</p>
    <p>New Moon &rarr; The lit side faces away &mdash; barely visible</p>
    <p>Crescent Moon &rarr; A thin curved sliver of the Moon is visible</p>
    <p>Half Moon &rarr; Half of the lit side faces Earth</p>
    <p>Reflected light &rarr; Sunlight bouncing off the Moon&#8217;s rocky surface</p>
    <p>Orbit &rarr; The Moon&#8217;s path as it travels around Earth</p>
  </div>
  <h3>LET&#8217;S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Could you see the Moon if the Sun did not exist?"</em></p>
    <p>No! If the Sun didn&#8217;t exist, there would be no sunlight to reflect off the Moon, so the Moon would be a dark, invisible rock. We only see the Moon because the Sun lights it up. This question reinforces Monday&#8217;s lesson &mdash; the Sun is the source of essentially all visible light in our sky.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"The Moon changes shape" &mdash; It does NOT. The Moon is always a sphere. What changes is how much of the lit half we can see from Earth. A helpful analogy: hold a ball under a lamp and walk around it &mdash; the lit portion you see changes, but the ball itself doesn&#8217;t change shape.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Moon phase calendar: Print or draw a 28-day calendar. Each night for four weeks, go outside (weather permitting) and draw the Moon&#8217;s shape. By the end, Christopher will have personally observed the complete phase cycle.</p>
  </div>

  <h2 class="thu">Thursday &mdash; Stars and the Night Sky</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1 (Stars vs. Sun):</strong> Stars are giant balls of burning gas &mdash; just like our Sun. The Sun IS a star. Differences: our Sun is close (so it looks big and bright); other stars are incredibly far away (so they look tiny). Some stars are bigger or smaller than the Sun; stars can be different colors depending on temperature.</p>
    <p><strong>Q2 (Constellation):</strong> A group of stars forming a picture or pattern. Examples from passage: Big Dipper (looks like a ladle/spoon), Orion (has three stars in his belt).</p>
    <p><strong>Q3 (Sailors):</strong> Sailors used constellations to navigate &mdash; to find their way across the ocean at night. Constellations were like a map in the sky; they appeared in predictable positions.</p>
    <p><strong>Q4 (Star pattern):</strong> Stars rise in the east and set in the west, following the same path across the sky that the Sun follows during the day.</p>
  </div>
  <h3>Odd One Out Answer Key</h3>
  <div class="answer-box thu">
    <p><strong>Row 1:</strong> A Rock on the Ground &mdash; it is not in the sky.</p>
    <p><strong>Row 2:</strong> The Sun &mdash; the others are all moon phases; the Sun is not a moon phase.</p>
    <p><strong>Row 3:</strong> Reflects sunlight &mdash; the others all describe a star (makes own light, is a star, burns gas); the Moon reflects light but does not make its own.</p>
    <p><strong>Row 4:</strong> The Moon &mdash; the others are all constellations or the concept of a constellation; the Moon is not a constellation.</p>
    <p><strong>Row 5:</strong> Stays still all day &mdash; the Sun (and stars/Moon) do not stay still; they appear to move across the sky.</p>
  </div>
  <h3>LET&#8217;S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Why do stars look so small if they&#8217;re actually enormous?"</em></p>
    <p>Distance! Some stars are thousands of times bigger than our Sun, but they are so far away that they look like tiny dots. Good analogy: a car&#8217;s headlights look tiny from a mile away. Hold up a small coin close to your eye &mdash; it can "block" a huge building in the distance. Distance shrinks apparent size dramatically.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"Stars are only out at night" &mdash; Stars are always there, day and night. We just can&#8217;t see them in the daytime because the Sun is so much closer and brighter that its light floods the sky. On the Moon (no atmosphere), you can see stars even when the Sun is up.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Constellation viewer: Poke holes in a piece of black paper in the pattern of the Big Dipper. Hold it up to a lamp or window light &mdash; the light shines through the holes like stars. Try to make your own constellation by poking holes in a pattern that tells a story.</p>
  </div>
</div>

<div class="page">
  <h2 class="fri">Friday &mdash; Day and Night Patterns (Capstone)</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1 (Day and night cause):</strong> Earth&#8217;s rotation causes day and night. Earth rotates (spins) once every 24 hours. The side facing the Sun has day; the side facing away has night.</p>
    <p><strong>Q2 (Sun appearing to move):</strong> The Sun does not actually move across our sky &mdash; WE are moving. Earth rotates, so our viewpoint shifts. From Earth, it looks like the Sun is moving, but it is really Earth spinning beneath us.</p>
    <p><strong>Q3 (No stars in daytime):</strong> The Sun&#8217;s light is so bright that it lights up the whole sky (atmosphere scatters sunlight), making it too bright to see the faint light from distant stars. Stars are still there &mdash; they are just invisible in the bright daytime sky.</p>
    <p><strong>Q4 (Full week chain):</strong> The Sun (our star) is the source of energy. It makes light that casts shadows on Earth (shadows change as Earth rotates, changing the Sun&#8217;s apparent position). The Sun also lights up the Moon through reflected light, which we see at night. Stars are other distant suns. Earth&#8217;s rotation (24-hour cycle) creates day and night, makes shadows change, and explains why the Sun, Moon, and stars all appear to rise in the east and set in the west.</p>
  </div>
  <h3>Tree Map Answer Key</h3>
  <div class="answer-box fri">
    <p><strong>The Sun (4):</strong> Makes its own light, Our nearest star, Warms Earth&#8217;s surface, Makes shadows on Earth</p>
    <p><strong>The Moon (4):</strong> Reflects sunlight, Has phases (shapes), Orbits Earth, Can only be seen at night (note: discuss &mdash; can sometimes be seen in daytime!)</p>
    <p><strong>Stars (4):</strong> Giant ball of burning gas, Constellations, Rises in the east, Used for navigation</p>
    <p><em>Note: "Rises in the east" technically applies to Sun and Moon too &mdash; if Christopher puts it in a different branch, discuss why that&#8217;s also reasonable. Encourage thinking about why all sky objects share this motion (Earth&#8217;s rotation).</em></p>
  </div>
  <h3>LET&#8217;S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"If Earth stopped spinning, what would happen to each side?"</em></p>
    <p>The day side would get hotter and hotter &mdash; the Sun would beat down endlessly. The night side would get colder and colder &mdash; no sunlight to warm it. Most life as we know it would perish. This is a wonderful creative thinking exercise. There is no single right answer &mdash; encourage logical consequences. (Real note: Earth is very slowly slowing its rotation, but the effect over millions of years is tiny.)</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"The Sun moves around Earth" &mdash; Earth rotates on its axis, making the Sun appear to move. Earth also orbits (goes around) the Sun once a year, but that&#8217;s a separate motion. For day and night, it is Earth&#8217;s daily rotation that matters. Use the flashlight-and-globe demo to make this concrete.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Day-and-night model: In a dark room, hold a flashlight steady (this is the Sun). Have Christopher slowly spin a globe or ball (this is Earth). Watch how one side stays lit (day) while the other is dark (night). Ask: "Where is your house right now? Is it day or night there?" Then tilt the ball slightly &mdash; that&#8217;s the setup for next week&#8217;s seasons lesson!</p>
  </div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2 class="fri">Week Summary &mdash; Causal Chain</h2>
  <p>The week followed this chain of causes:</p>
  <ol style="padding-left: 20px; font-size: 10pt; line-height: 2;">
    <li><strong>Monday:</strong> The Sun is a star &mdash; our nearest one. It provides light and heat energy that warms Earth&#8217;s land, air, and water.</li>
    <li><strong>Tuesday:</strong> The Sun&#8217;s light casts shadows. Shadows change length and direction as the Sun appears to move across the sky (rising in the east, setting in the west). Objects in sunlight are warmer than objects in shade.</li>
    <li><strong>Wednesday:</strong> The Moon orbits Earth and reflects sunlight. As it orbits, we see different amounts of its lit side &mdash; this creates a repeating monthly pattern of phases.</li>
    <li><strong>Thursday:</strong> Stars are distant suns. They form patterns (constellations) that repeat nightly. Like the Sun and Moon, stars rise in the east and set in the west.</li>
    <li><strong>Friday:</strong> Everything is explained by Earth&#8217;s rotation (24 hours = one day). Earth spinning causes day/night, makes the Sun appear to move, and is why all sky objects rise in the east and set in the west.</li>
  </ol>
  <p style="margin-top: 10px;">By Friday, Christopher should be able to explain day and night using Earth&#8217;s rotation, describe the Moon as a reflector of sunlight, and name at least one constellation &mdash; and connect all of these to the same underlying cause: Earth spinning in the light of our star, the Sun.</p>
</div>

</body>
</html>"""

    guide_path = output_dir / "sky_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print("\nSuccessfully generated Sky and Space Week.")
    print(f"Student packet:  {out_path}")
    print(f"Teacher guide:   {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Mon p1 — Reading: The Sun — Our Nearest Star",
        "Mon p2 — Feature Matrix: What Does the Sun Do?",
        "Tue p1 — Reading: Shadows and the Sun's Journey",
        "Tue p2 — T-Chart: Sun vs. Shade",
        "Wed p1 — Reading: The Moon — Our Nighttime Neighbor",
        "Wed p2 — Matching: Moon Phases",
        "Thu p1 — Reading: Stars and the Night Sky",
        "Thu p2 — Odd One Out: Sky Objects",
        "Fri p1 — Reading: Day and Night — Why Does the Sky Change? (Capstone)",
        "Fri p2 — Tree Map: Things in the Sky Capstone",
        "         — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")


if __name__ == "__main__":
    generate_sky_week_series()
