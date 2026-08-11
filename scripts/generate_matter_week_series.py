"""
Matter — Week Series
Grade K–1 | Science | Causal Arc: What is Matter? → Solids → Liquids → Gases → Matter Changes State

Narrator: Marco the Matter Mole, introduced on Monday. A curious underground mole who tunnels
through rock (solid), swims through puddles (liquid), and breathes the air (gas) — so he
experiences all three states of matter every day.

Output: single printable HTML document — matter_week_series/matter_week.html

Standards (Virginia SOL):
  Monday    — VA.SCIENCE.K.k.3, VA.SCIENCE.1.1.3.a
              (matter has physical properties; materials can be described)
  Tuesday   — VA.SCIENCE.K.k.3.a–d, VA.SCIENCE.1.1.3.a
              (properties of solids: color, shape, texture, size/weight)
  Wednesday — VA.SCIENCE.K.k.4, VA.SCIENCE.K.k.4.c
              (water has properties; water in different phases — liquid focus)
  Thursday  — VA.SCIENCE.K.k.4.c, VA.SCIENCE.1.1.3.a
              (gases are a state of matter; air as a gas with properties)
  Friday    — VA.SCIENCE.K.k.4.c, VA.SCIENCE.K.k.10, VA.SCIENCE.K.k.10.a
              (capstone: matter changes state; heating/cooling cause changes)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html


def generate_matter_week_series():
    output_dir = Path("matter_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []  # (day_label, html_fragment)

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — What Is Matter?
    # Standards: VA.SCIENCE.K.k.3, VA.SCIENCE.1.1.3.a
    # (matter is everything around us; materials have physical properties)
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: What Is Matter?",
            "passage_title": "Meet Marco — Everything Is Matter!",
            "instructions": (
                "Before reading: Go on a quick 'matter hunt' outside or around the room. "
                "Point to three objects and name them. They are all made of matter! "
                "Come back and share what you found before we read about Marco."
            ),
            "passage": (
                "Meet Marco the Mole! Marco has velvety dark fur, tiny pink paws, and a twitchy "
                "nose that can smell things underground. Every day, Marco tunnels through the soil, "
                "swims through puddles, and breathes in the fresh air — and this week he is going "
                "to teach us something amazing: EVERYTHING around us is made of matter!\n\n"
                "Matter is anything that takes up space and has mass. Mass means it has some "
                "weight — you can feel it if you pick it up. Look around the room. The chair "
                "you sit on is matter. The water you drink is matter. Even the air you breathe "
                "is matter! If you can touch it, feel it, smell it, or measure it, it is matter.\n\n"
                "Scientists sort matter into three groups called states of matter. The three "
                "states are: solid, liquid, and gas. Solids have a shape that stays the same "
                "unless you break or cut them. Liquids flow and take the shape of whatever "
                "container you put them in. Gases spread out to fill all the space they are in.\n\n"
                "Marco knows all three states from his daily adventures. 'The dirt I tunnel "
                "through is a solid,' he says. 'The puddle I splash in is a liquid. And the "
                "air I breathe is a gas!' This week we will explore each state of matter with "
                "Marco — and discover how matter can even change from one state to another!"
            ),
            "vocabulary": [
                {
                    "term": "matter",
                    "definition": "Anything that takes up space and has mass — everything around us is made of matter.",
                },
                {
                    "term": "mass",
                    "definition": "How much material is in an object — things with mass have weight when you pick them up.",
                },
                {
                    "term": "solid",
                    "definition": "A state of matter with a shape that stays the same, like a rock or a crayon.",
                },
                {
                    "term": "liquid",
                    "definition": "A state of matter that flows and takes the shape of its container, like water or juice.",
                },
                {
                    "term": "gas",
                    "definition": "A state of matter that spreads out to fill all the space it is in, like air.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is matter? Name two things in the room that are made of matter.",
                    "response_lines": 2,
                },
                {
                    "prompt": "What are the three states of matter? List all three.",
                    "response_lines": 2,
                },
                {
                    "prompt": "Marco experiences all three states of matter every day. What solid, liquid, and gas does he encounter?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: Is a shadow made of matter? What about a smell? How can you tell if something is matter or not?",
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    add(
        "wordSortWorksheet",
        {
            "title": "Monday: Sorting Matter — Word Sort",
            "instructions": (
                "Look at each word in the word bank. Is it a solid, a liquid, or a gas? "
                "Write it in the correct box. Use the definitions from your reading to help!"
            ),
            "categories": [
                {"label": "Solid"},
                {"label": "Liquid"},
                {"label": "Gas"},
            ],
            "tiles": [
                "Rock",
                "Milk",
                "Steam",
                "Ice cube",
                "Juice",
                "Air",
                "Pencil",
                "Rain water",
                "Oxygen",
                "Book",
                "Honey",
                "Smoke",
            ],
        },
        "Monday",
    )

    # =========================================================================
    # TUESDAY — All About Solids
    # Standards: VA.SCIENCE.K.k.3.a–d, VA.SCIENCE.1.1.3.a
    # (physical properties of solids: color, shape, texture, size/weight)
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: All About Solids",
            "passage_title": "Marco Explores the Underground — Solids Have Their Own Shape!",
            "instructions": (
                "Before reading: Pick up three small objects (a crayon, an eraser, a coin). "
                "Notice their shape, color, and texture. Do they change shape in your hand? "
                "Keep thinking about this as you read about solids with Marco."
            ),
            "passage": (
                "Marco was digging his tunnel when he hit something hard. 'A pebble!' he squeaked. "
                "He held it in his paw and noticed it was round, smooth, and gray. He set it down "
                "and it kept its shape — it did not spread out or flow away. 'Solids are amazing,' "
                "Marco thought. 'They always keep their own shape!'\n\n"
                "A solid is a state of matter with a definite shape and a definite size. "
                "'Definite' means it stays the same. If you pick up a rock and put it in a jar, "
                "the rock is still the same shape — the rock does not become jar-shaped. "
                "Solids do not flow like water. You cannot pour a crayon into a cup!\n\n"
                "We can describe solids using their physical properties. Physical properties "
                "are things you can observe with your senses. Color is a property — the pebble "
                "is gray. Shape is a property — the pebble is round. Texture is a property — "
                "the pebble is smooth. Size and weight are properties — a pebble is small and "
                "light, while a boulder is large and heavy.\n\n"
                "Even though you can change a solid by cutting it or breaking it, most properties "
                "stay the same. If you break a gray rock in half, both pieces are still gray! "
                "The color did not change. Marco discovered that knowing a solid's properties "
                "helps him figure out what it is and how to use it in his underground home."
            ),
            "vocabulary": [
                {
                    "term": "solid",
                    "definition": "A state of matter with a definite (fixed) shape and size — it does not flow.",
                },
                {
                    "term": "physical property",
                    "definition": "Something you can observe about matter using your senses — color, shape, texture, or size.",
                },
                {
                    "term": "texture",
                    "definition": "How something feels when you touch it — rough, smooth, bumpy, soft, or hard.",
                },
                {
                    "term": "definite",
                    "definition": "Fixed and not changing — a solid has a definite shape that stays the same.",
                },
            ],
            "questions": [
                {
                    "prompt": "What makes a solid different from a liquid? Use the word 'shape' in your answer.",
                    "response_lines": 2,
                },
                {
                    "prompt": "Name four physical properties you can use to describe a solid.",
                    "response_lines": 2,
                },
                {
                    "prompt": "If you break a gray rock in half, what happens to its color? What does this tell us?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: Could you make a solid into a different shape without breaking it? Can you think of any solid that changes shape easily — and is it still a solid?",
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "featureMatrixWorksheet",
        {
            "title": "Tuesday: Describing Solids — Feature Matrix",
            "instructions": (
                "Put a check mark in every box that describes each solid. "
                "Think carefully about each property! More than one solid can share a property."
            ),
            "items": ["Rock", "Crayon", "Sponge", "Coin", "Cotton ball"],
            "properties": [
                "Hard",
                "Soft",
                "Smooth",
                "Rough/bumpy",
                "Can be held in one hand",
                "Has a fixed shape",
            ],
        },
        "Tuesday",
    )

    # =========================================================================
    # WEDNESDAY — All About Liquids
    # Standards: VA.SCIENCE.K.k.4, VA.SCIENCE.K.k.4.c
    # (water has properties; water as a liquid state; liquids take shape of container)
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: All About Liquids",
            "passage_title": "Marco Finds a Puddle — Liquids Flow and Change Shape!",
            "instructions": (
                "Hands-on activity: Before reading, fill a small cup with water. "
                "Pour it into a bowl. What happened? Did the water change shape? "
                "Now pour it back into the cup. This is the big idea for today's lesson!"
            ),
            "passage": (
                "One morning, Marco crawled out of his tunnel and found a big rain puddle. "
                "He splashed his paw in — the water rippled and moved. He picked up a pawful "
                "of water and it dripped right through his claws. 'Liquids do not hold their "
                "shape!' he noticed. 'They flow wherever there is space!'\n\n"
                "A liquid is a state of matter that flows and takes the shape of whatever "
                "container it is in. Water in a round bowl looks round. The same water poured "
                "into a tall, thin bottle looks long and thin. The amount of water does not "
                "change — but its shape does, because liquids flow. This is very different "
                "from a solid, which keeps its shape no matter what container it is in.\n\n"
                "Water is the most important liquid on Earth. Water has many special properties. "
                "It is clear and colorless when pure. It has no smell. It can be poured, "
                "splashed, and dripped. Water flows downhill — if you spill water on a tilted "
                "table, it runs to the lowest point. Water can also be found in many places: "
                "in rivers, in the ocean, in puddles, in our bodies, and even in the food we eat!\n\n"
                "'Water is everywhere,' Marco said happily, shaking the droplets from his fur. "
                "'And it is always the same water — just in different containers and places.'"
            ),
            "vocabulary": [
                {
                    "term": "liquid",
                    "definition": "A state of matter that flows and takes the shape of whatever container it is in.",
                },
                {
                    "term": "flow",
                    "definition": "To move smoothly from place to place — liquids flow; solids do not.",
                },
                {
                    "term": "container",
                    "definition": "An object that holds something inside it — a cup, a bowl, or a bottle.",
                },
                {
                    "term": "property",
                    "definition": "A describing word for matter — like color, smell, texture, or whether something flows.",
                },
            ],
            "questions": [
                {
                    "prompt": "How is a liquid different from a solid? What happens to a liquid's shape in different containers?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Name three places you can find water as a liquid.",
                    "response_lines": 2,
                },
                {
                    "prompt": "What happens to water when it is on a tilted surface? Why?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: If you pour juice into a container shaped like a star, does the juice become star-shaped? Is the juice still the same amount? What does this tell you about liquids?",
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "causeEffectWorksheet",
        {
            "title": "Wednesday: Liquids — Cause and Effect",
            "instructions": (
                "Each cause describes something that happens to a liquid. "
                "Write the effect — what happens next? Remember what you learned about how liquids behave."
            ),
            "pairs": [
                {
                    "cause": "You pour water from a round cup into a tall, narrow bottle.",
                    "effect": "",
                    "effect_lines": 2,
                },
                {
                    "cause": "You spill water on a tilted table.",
                    "effect": "",
                    "effect_lines": 2,
                },
                {
                    "cause": "You hold a handful of water in your open palm.",
                    "effect": "",
                    "effect_lines": 2,
                },
                {
                    "cause": "You pour orange juice into a bowl shaped like a star.",
                    "effect": "",
                    "effect_lines": 2,
                },
            ],
        },
        "Wednesday",
    )

    # =========================================================================
    # THURSDAY — All About Gases
    # Standards: VA.SCIENCE.K.k.4.c, VA.SCIENCE.1.1.3.a
    # (gases as a state of matter; air is a gas with properties; gases fill space)
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: All About Gases",
            "passage_title": "Marco Breathes Deep — Gases Fill Every Space!",
            "instructions": (
                "Outdoor activity: Go outside and take a slow, deep breath. "
                "Hold a pinwheel or a piece of tissue up — can you see the air moving? "
                "Blow gently on your hand. That moving air is a gas! Come back inside and "
                "think about this as you read with Marco."
            ),
            "passage": (
                "Marco climbed up out of the ground and took a big, deep breath. He could not "
                "see the air, but he could feel it on his fur and smell the flowers in it. "
                "'Air is a gas,' he thought. 'And even though I cannot see it, it is definitely matter!'\n\n"
                "A gas is a state of matter that has no fixed shape and no fixed size. "
                "Gases spread out to fill ALL of the space inside any container. If you blow "
                "air into a balloon, the air spreads out to fill every corner of the balloon. "
                "If you open the balloon, the air spreads out into the whole room! "
                "Gases will always fill their container completely.\n\n"
                "Air is the gas we know best. Air is all around us — we cannot see it, but "
                "we know it is there because we can feel the wind when it moves, we can blow "
                "bubbles in water with it, and we can inflate a ball or a tire with it. "
                "Air is actually a mixture of many gases: mostly nitrogen, some oxygen "
                "(the part we breathe), and small amounts of other gases.\n\n"
                "Other gases you might know: steam that comes off hot food is water vapor "
                "(water as a gas). Carbon dioxide is the gas you breathe OUT. Helium is the "
                "gas that makes balloons float. All of these gases are invisible, but they "
                "are real matter — they take up space! Marco puffed out his cheeks with a "
                "big mouthful of air. 'I have a gas inside me right now,' he laughed."
            ),
            "vocabulary": [
                {
                    "term": "gas",
                    "definition": "A state of matter with no fixed shape or size — it spreads out to fill all available space.",
                },
                {
                    "term": "air",
                    "definition": "The mixture of gases all around us — mostly nitrogen and oxygen.",
                },
                {
                    "term": "water vapor",
                    "definition": "Water in its gas form — the invisible steam that rises from hot water.",
                },
                {
                    "term": "carbon dioxide",
                    "definition": "A gas you breathe out after your body uses oxygen.",
                },
                {
                    "term": "invisible",
                    "definition": "Cannot be seen — gases are usually invisible, but they are still real matter.",
                },
            ],
            "questions": [
                {
                    "prompt": "What makes a gas different from a solid and a liquid? What does a gas do when put in a container?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Even though you cannot see air, how do you know it is there? Give two pieces of evidence.",
                    "response_lines": 2,
                },
                {
                    "prompt": "Name three gases besides air that are mentioned in the passage.",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: If a gas always fills its container completely — what happens to the gas when you open a jar or pop a balloon? Where does the gas go?",
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    add(
        "oddOneOutWorksheet",
        {
            "title": "Thursday: States of Matter — Odd One Out",
            "instructions": (
                "Look at the four items in each row. Three of them belong to the same group. "
                "Circle the one that does NOT belong, and tell a grown-up why!"
            ),
            "rows": [
                {
                    "items": ["Rock", "Marble", "Air", "Wood block"],
                    "reasoning_lines": 1,
                },
                {
                    "items": ["Water", "Milk", "Juice", "Pebble"],
                    "reasoning_lines": 1,
                },
                {
                    "items": ["Steam", "Carbon dioxide", "Honey", "Oxygen"],
                    "reasoning_lines": 1,
                },
                {
                    "items": ["Ice cube", "Balloon air", "Helium", "Water vapor"],
                    "reasoning_lines": 1,
                },
                {
                    "items": [
                        "Flows easily",
                        "Keeps its own shape",
                        "Can be poured",
                        "Takes shape of container",
                    ],
                    "reasoning_lines": 1,
                },
            ],
        },
        "Thursday",
    )

    # =========================================================================
    # FRIDAY — Matter Changes State (Capstone)
    # Standards: VA.SCIENCE.K.k.4.c, VA.SCIENCE.K.k.10, VA.SCIENCE.K.k.10.a
    # (water in different phases; change occurs over time; matter changes)
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: Matter Changes State",
            "passage_title": "Marco's Big Experiment — Heating and Cooling Change Matter!",
            "instructions": (
                "Capstone hands-on: Put an ice cube in a glass. Watch it change over 10 minutes. "
                "What state is it at the start? What state does it become? If you could heat it "
                "even more, what do you think would happen next? "
                "Then read the passage with Marco!"
            ),
            "passage": (
                "Marco found an ice cube on the kitchen counter and watched it carefully. "
                "First it was a solid — cold and hard with a definite shape. Then, as the room "
                "warmed it up, it started to change. 'It is melting!' Marco squeaked. "
                "The solid ice was becoming a liquid puddle!\n\n"
                "Matter can change from one state to another when you add heat or take heat away. "
                "When you add heat to a solid, it can MELT and become a liquid. "
                "When water is heated even more — to very high temperatures — it can EVAPORATE "
                "and become a gas called water vapor. You can see this as steam rising from "
                "a hot pot on the stove.\n\n"
                "Cooling does the opposite! When you take heat away from a liquid, it can "
                "FREEZE and become a solid. Water in a freezer turns to ice because the freezer "
                "takes heat away. When water vapor in the air cools down, it can CONDENSE and "
                "become liquid water — this is how morning dew forms on grass!\n\n"
                "The most amazing thing is that the matter is still the same. Water, ice, "
                "and steam are all made of the exact same material — just in different states! "
                "Only the amount of heat changes which state the water is in. "
                "Marco stared at the tiny puddle where the ice cube used to be. "
                "'It did not disappear,' he said with wonder. 'It just changed state!'"
            ),
            "vocabulary": [
                {
                    "term": "melt",
                    "definition": "When a solid is heated and changes into a liquid — like ice melting into water.",
                },
                {
                    "term": "freeze",
                    "definition": "When a liquid is cooled and changes into a solid — like water turning into ice.",
                },
                {
                    "term": "evaporate",
                    "definition": "When a liquid is heated and changes into a gas — like water turning into steam.",
                },
                {
                    "term": "condense",
                    "definition": "When a gas cools down and changes into a liquid — like steam turning back into water drops.",
                },
                {
                    "term": "state of matter",
                    "definition": "One of the three forms matter can take: solid, liquid, or gas.",
                },
                {
                    "term": "heat",
                    "definition": "Energy that causes matter to warm up — adding or removing heat changes the state of matter.",
                },
            ],
            "questions": [
                {
                    "prompt": "What happens when you add heat to a solid? What is this change called?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What happens when you take heat away from a liquid? Give a real-life example.",
                    "response_lines": 2,
                },
                {
                    "prompt": "Ice, water, and steam are all the same material. What is different about them?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Describe the full chain of changes you could make to a single ice cube using only heat: start with ice and end with steam.",
                    "response_lines": 3,
                },
                {
                    "prompt": "LET'S DISCUSS: When ice melts in your juice and the juice gets watery, is that the same kind of change? Does the matter disappear, or does it just become something else?",
                    "response_lines": 0,
                },
            ],
        },
        "Friday",
    )

    add(
        "treeMapWorksheet",
        {
            "title": "Friday: States of Matter — Tree Map Capstone",
            "instructions": (
                "Sort each word from the word bank into the correct branch. "
                "Each word belongs in only one branch — think carefully!"
            ),
            "root_label": "States of Matter",
            "branches": [
                {"label": "Solid", "slot_count": 4},
                {"label": "Liquid", "slot_count": 4},
                {"label": "Gas", "slot_count": 4},
            ],
            "columns": 3,
            "word_bank": [
                "Rock",
                "Water",
                "Air",
                "Ice cube",
                "Juice",
                "Steam",
                "Wood",
                "Milk",
                "Oxygen",
                "Crayon",
                "Honey",
                "Carbon dioxide",
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
            "title": "End-of-Week Parent Feedback — Matter Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this feedback sheet after the week wraps up. "
                "Your notes help shape next week's lessons."
            ),
            "passage": (
                "This week followed a causal arc through the states of matter. "
                "Monday introduced matter itself — the idea that everything has mass and takes "
                "up space — and met Marco the Mole, our narrator. Tuesday explored solids and "
                "their physical properties (color, shape, texture, size, weight), with the key "
                "idea that solids keep a definite shape. Wednesday explored liquids and how they "
                "flow to fill any container, using water as the central example. Thursday "
                "explored gases — that they are invisible matter that expands to fill all "
                "available space, with air as the primary example. Friday pulled everything "
                "together with state changes: melting, freezing, evaporation, and condensation "
                "show that the same matter can exist in different states depending on temperature.\n\n"
                "Marco the Matter Mole appeared throughout the week, tunneling through solids, "
                "splashing in liquids, and breathing gases — giving Christopher a concrete, "
                "living-world perspective on abstract science concepts.\n\n"
                "Key concepts to check for genuine understanding — not just recall:\n"
                "1) Matter is anything with mass that takes up space — including invisible things like air.\n"
                "2) Solids keep their shape; liquids take the shape of their container; gases fill all space.\n"
                "3) Physical properties (color, shape, texture, size) let us describe and sort solids.\n"
                "4) Water is the same material whether it is ice, liquid water, or steam — only state changes.\n"
                "5) Heating adds energy that causes state changes; cooling removes energy.\n\n"
                "Common misconceptions to watch for:\n"
                "• 'Gases are not matter' — air and other gases are real matter; they have mass (blow up a "
                "ball and it gets heavier).\n"
                "• 'Ice disappears when it melts' — matter is conserved; the liquid water is still there.\n"
                "• 'Steam is visible' — visible steam is actually tiny liquid droplets; true water vapor is "
                "invisible.\n"
                "• 'Soft things are not solids' — sponges and cotton balls are solids; hardness is one "
                "property, not the definition of a solid.\n\n"
                "Suggested follow-on activities: explore non-Newtonian fluids (cornstarch + water) — "
                "is oobleck a solid or a liquid? Make ice pops and observe all three states of water. "
                "Find five solids, five liquids, and five gases around the house together."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": "Air IS matter — gases have mass even though we cannot see them. A balloon full of air is heavier than a flat balloon.",
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in after the week — which idea did Christopher grasp best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": "Mixtures and materials — what happens when you mix solids together, or mix a solid into a liquid? Can you always separate them?",
                },
            ],
            "questions": [
                {
                    "prompt": "Overall comfort with the week's content — how well did Christopher grasp the three states of matter? (1 = struggled throughout, 5 = strong grasp of all concepts)",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which day's lesson or hands-on activity generated the most curiosity or questions?",
                    "response_lines": 2,
                },
                {
                    "prompt": "By Friday, could Christopher explain the difference between a solid, a liquid, and a gas — and name a real example of each?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Did Christopher connect the ice-cube observation (or any everyday example) to the lesson on state changes?",
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

    html = build_print_packet_html(pages, packet_title="Matter Week — Science for Christopher")
    out_path = output_dir / "matter_week.html"
    out_path.write_text(html, encoding="utf-8")

    # -------------------------------------------------------------------------
    # Teacher guide
    # -------------------------------------------------------------------------
    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Matter Week — Teacher Guide</title>
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
  <h1>Matter Week — Teacher / Parent Guide</h1>
  <p><strong>Theme:</strong> Matter: Solids, Liquids, and Gases &nbsp;|&nbsp; <strong>Audience:</strong> Christopher, age 6, K&ndash;1 &nbsp;|&nbsp;
  <strong>Narrator:</strong> Marco the Matter Mole</p>
  <p><strong>Causal Arc:</strong> What Is Matter? &rarr; Solids (properties) &rarr; Liquids (flow, containers) &rarr; Gases (invisible, fill space) &rarr; Matter Changes State (heat adds/removes energy)</p>

  <h2>Monday &mdash; What Is Matter?</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1 (What is matter):</strong> Matter is anything that takes up space and has mass. Accept any two objects from the room &mdash; chair, desk, crayon, window, water bottle, etc.</p>
    <p><strong>Q2 (Three states):</strong> Solid, liquid, and gas.</p>
    <p><strong>Q3 (Marco&rsquo;s examples):</strong> Solid = dirt/soil he tunnels through. Liquid = puddle he splashes in. Gas = air he breathes.</p>
  </div>
  <h3>LET&rsquo;S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>&ldquo;Is a shadow made of matter? What about a smell?&rdquo;</em></p>
    <p>Neither a shadow nor a smell is matter. A shadow is the absence of light &mdash; it has no mass and takes up no space. A smell is caused by tiny particles (molecules) that float through air &mdash; the molecules themselves are matter, but the &ldquo;smell&rdquo; is just information detected by your nose. Encourage Christopher to argue both sides before revealing the answer.</p>
  </div>
  <h3>Word Sort Answer Key</h3>
  <div class="answer-box">
    <p><strong>Solid:</strong> Rock, Ice cube, Pencil, Book</p>
    <p><strong>Liquid:</strong> Milk, Juice, Rain water, Honey</p>
    <p><strong>Gas:</strong> Steam, Air, Oxygen, Smoke</p>
    <p><em>Note: &ldquo;Ice cube&rdquo; is a solid (frozen water). &ldquo;Steam&rdquo; is a gas (water vapor). If Christopher says ice is a liquid because it &ldquo;comes from water,&rdquo; that is a great teaching moment for state changes (Friday&rsquo;s topic).</em></p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>&ldquo;Only things I can hold are matter.&rdquo; Air and other gases are matter even though they are invisible. Ask: &ldquo;Can you feel wind? Can you blow up a balloon? Then air must be real!&rdquo;</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Matter scavenger hunt: walk through three rooms and make a tally chart &mdash; how many solids, liquids, and gases can you find and name? Try to find at least 10 solids, 3 liquids, and 2 gases.</p>
  </div>

  <h2 class="tue">Tuesday &mdash; All About Solids</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box tue">
    <p><strong>Q1 (Solid vs. liquid):</strong> A solid has a definite shape that stays the same &mdash; it does not flow. A liquid changes shape to match its container.</p>
    <p><strong>Q2 (Four properties):</strong> Any four of: color, shape, texture (rough/smooth), size (big/small), weight (heavy/light), hardness.</p>
    <p><strong>Q3 (Breaking the rock):</strong> The color stays the same &mdash; both pieces are still gray. This tells us that most physical properties stay the same when you change the size of a solid.</p>
  </div>
  <h3>Feature Matrix Answer Key</h3>
  <div class="answer-box tue">
    <p><strong>Rock:</strong> Hard &#10003;, Smooth &#10003; (most pebbles), Has a fixed shape &#10003;</p>
    <p><strong>Crayon:</strong> Hard &#10003;, Smooth &#10003;, Can be held in one hand &#10003;, Has a fixed shape &#10003;</p>
    <p><strong>Sponge:</strong> Soft &#10003;, Rough/bumpy &#10003; (many sponges), Can be held in one hand &#10003;, Has a fixed shape &#10003;</p>
    <p><strong>Coin:</strong> Hard &#10003;, Smooth &#10003;, Can be held in one hand &#10003;, Has a fixed shape &#10003;</p>
    <p><strong>Cotton ball:</strong> Soft &#10003;, Can be held in one hand &#10003;, Has a fixed shape &#10003;</p>
    <p><em>Note: All five are solids, so all have &ldquo;Has a fixed shape&rdquo; checked. Sponge and cotton ball are soft solids &mdash; use this to address the misconception that &ldquo;soft = not a solid.&rdquo;</em></p>
  </div>
  <h3>LET&rsquo;S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>&ldquo;Could you make a solid into a different shape without breaking it?&rdquo;</em></p>
    <p>Some solids (like clay or modeling dough) can be molded into new shapes &mdash; but they are still solids because the clay holds its new shape. Ask: is clay still a solid after you squish it? (Yes!) Contrast with ice, which must MELT (change state) to become shapeless. Playdough is a great real example to explore this gray area.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>&ldquo;Soft things are not solids.&rdquo; Hardness is a property of some solids, not the definition. A sponge, a cotton ball, and a pillow are all solids because they hold their shape &mdash; you do not pour them into a container and have them change shape.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Property sort: gather 8&ndash;10 small objects (coins, erasers, rocks, buttons, sponge pieces). Make a chart with columns: Color, Hard/Soft, Smooth/Rough, Small/Large. Fill in one row per object. Then sort the objects into two groups based on one chosen property &mdash; who can explain how they sorted?</p>
  </div>
</div>

<div class="page">
  <h2 class="wed">Wednesday &mdash; All About Liquids</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1 (Liquid vs. solid):</strong> A liquid flows and takes the shape of its container; a solid keeps its own shape. The same liquid in a round bowl looks round; in a tall bottle it looks tall and thin.</p>
    <p><strong>Q2 (Places to find water):</strong> Any three of: rivers, ocean, puddles, our bodies, food we eat, rain, ponds, lakes, bottles, cups.</p>
    <p><strong>Q3 (Tilted surface):</strong> Water flows downhill to the lowest point because liquids always flow toward the lowest available space.</p>
  </div>
  <h3>Cause-and-Effect Answer Key</h3>
  <div class="answer-box wed">
    <p><strong>Cause 1 &rarr; Effect:</strong> The water changes shape to fit the tall, narrow bottle &mdash; it looks long and thin instead of round.</p>
    <p><strong>Cause 2 &rarr; Effect:</strong> The water flows downhill to the lowest end of the tilted table.</p>
    <p><strong>Cause 3 &rarr; Effect:</strong> The water flows out between your fingers and drips down &mdash; liquids cannot hold their shape in an open hand.</p>
    <p><strong>Cause 4 &rarr; Effect:</strong> The juice takes the star shape of the bowl &mdash; it fills the container and matches its shape.</p>
  </div>
  <h3>LET&rsquo;S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>&ldquo;Does juice in a star-shaped container become star-shaped? Is it still the same amount?&rdquo;</em></p>
    <p>Yes to both! The juice takes the star shape but the amount does not change &mdash; this is conservation of volume. Pour juice between differently shaped containers to demonstrate that the volume stays constant even though the shape changes. This is a Piagetian conservation concept that 6-year-olds are just developing &mdash; be patient if Christopher says &ldquo;it&rsquo;s more&rdquo; in the taller container.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>&ldquo;There is more water in the tall, thin container than in the short, wide one.&rdquo; This is a classic conservation-of-volume misconception. Demonstrate by pouring back and forth between containers, confirming the amount is the same. The shape changed; the amount did not.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Container experiment: find 4&ndash;5 different-shaped containers (cup, bowl, jar, pitcher). Pour the same measured amount of water into each. Observe how the water looks different in each container. Confirm the same amount by pouring each back into a measuring cup.</p>
  </div>

  <h2 class="thu">Thursday &mdash; All About Gases</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1 (Gas properties):</strong> A gas has no fixed shape and no fixed size; it spreads out to fill all the space in its container. Contrast: solid = fixed shape; liquid = fixed volume but takes container shape; gas = no fixed shape or volume.</p>
    <p><strong>Q2 (Evidence for air):</strong> Any two of: feel wind when it moves; blow bubbles in water; inflate a ball or tire; pinwheel spins; feel it on skin when you blow; sound travels through it.</p>
    <p><strong>Q3 (Three gases named):</strong> Water vapor (steam), carbon dioxide, helium.</p>
  </div>
  <h3>Odd One Out Answer Key</h3>
  <div class="answer-box thu">
    <p><strong>Row 1:</strong> Air &mdash; the others (Rock, Marble, Wood block) are solids; Air is a gas.</p>
    <p><strong>Row 2:</strong> Pebble &mdash; the others (Water, Milk, Juice) are liquids; Pebble is a solid.</p>
    <p><strong>Row 3:</strong> Honey &mdash; the others (Steam, Carbon dioxide, Oxygen) are gases; Honey is a liquid.</p>
    <p><strong>Row 4:</strong> Ice cube &mdash; the others (Balloon air, Helium, Water vapor) are gases; Ice cube is a solid.</p>
    <p><strong>Row 5:</strong> &ldquo;Keeps its own shape&rdquo; &mdash; this describes a solid; the others (Flows easily, Can be poured, Takes shape of container) describe liquids or gases.</p>
  </div>
  <h3>LET&rsquo;S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>&ldquo;When you pop a balloon, where does the gas go?&rdquo;</em></p>
    <p>The gas spreads out into the room. It does not disappear &mdash; it just mixes with the rest of the air in the room. Gases always expand to fill their container. The &ldquo;container&rdquo; is now the room. Ask: &ldquo;Could you catch it again?&rdquo; (Not easily, because it is now mixed with all the room air &mdash; but it is still there!)</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>&ldquo;Steam is a gas you can see.&rdquo; The visible white cloud above a boiling pot is actually tiny liquid water droplets &mdash; condensed water vapor. True water vapor (gas) is completely invisible. The gas becomes visible only when it has cooled enough to condense into droplets. This is subtle &mdash; just plant the seed.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Gas in a bottle: put a balloon over the mouth of an empty plastic bottle. Squeeze the bottle &mdash; the balloon inflates. Release &mdash; it deflates. What is inflating the balloon? (Air &mdash; a gas &mdash; that was in the bottle.) This proves air is real matter that can be pushed and moves around.</p>
  </div>
</div>

<div class="page">
  <h2 class="fri">Friday &mdash; Matter Changes State (Capstone)</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1 (Solid + heat):</strong> When you add heat to a solid it melts and becomes a liquid. This change is called melting.</p>
    <p><strong>Q2 (Liquid &minus; heat):</strong> When you take heat away from a liquid it freezes and becomes a solid. Real-life example: water in the freezer becomes ice.</p>
    <p><strong>Q3 (Ice/water/steam):</strong> Ice, water, and steam are the same material (water). What is different is the state &mdash; which depends on the amount of heat. Ice is cold (solid), liquid water is at room/warm temperature, steam is very hot (gas).</p>
    <p><strong>Q4 (Ice &rarr; steam chain):</strong> Ice (solid, cold) &rarr; add heat &rarr; melts to liquid water &rarr; add more heat &rarr; evaporates to steam/water vapor (gas).</p>
  </div>
  <h3>Tree Map Answer Key</h3>
  <div class="answer-box fri">
    <p><strong>Solid (4):</strong> Rock, Ice cube, Wood, Crayon</p>
    <p><strong>Liquid (4):</strong> Water, Juice, Milk, Honey</p>
    <p><strong>Gas (4):</strong> Air, Steam, Oxygen, Carbon dioxide</p>
  </div>
  <h3>LET&rsquo;S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>&ldquo;When ice melts in your juice, does the matter disappear?&rdquo;</em></p>
    <p>No! The ice becomes liquid water and mixes with the juice. The matter is still there &mdash; it just changed state (solid ice &rarr; liquid water). The juice gets watery because more liquid (the melted ice) was added. This is a great conservation-of-matter moment. Ask Christopher: &ldquo;Where did the ice go?&rdquo; Accept &ldquo;it turned into water&rdquo; as the key insight.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>&ldquo;The ice disappeared.&rdquo; Matter cannot disappear &mdash; it only changes form. Melted ice becomes liquid water. Evaporated water becomes invisible gas. Reinforce: we cannot make matter appear from nothing or make it vanish. This is the law of conservation of matter (simplified for K&ndash;1 as &ldquo;matter does not disappear&rdquo;).</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Three-state water exploration: (1) observe an ice cube (solid); (2) let it melt into liquid water; (3) with supervision, heat a small amount of water in a pot and watch steam rise. At each stage, ask: &ldquo;What state is it now? What changed?&rdquo; Draw a simple diagram showing ice &rarr; water &rarr; steam with arrows labeled &ldquo;add heat.&rdquo;</p>
  </div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2 class="fri">Week Summary &mdash; Causal Chain</h2>
  <p>The week followed this chain of ideas:</p>
  <ol style="padding-left: 20px; font-size: 10pt; line-height: 2;">
    <li><strong>Monday:</strong> Everything is matter (has mass and takes up space); matter comes in three states: solid, liquid, gas.</li>
    <li><strong>Tuesday:</strong> Solids have a definite shape and can be described by physical properties (color, shape, texture, size, weight).</li>
    <li><strong>Wednesday:</strong> Liquids have no fixed shape; they flow and take the shape of their container; water flows downhill.</li>
    <li><strong>Thursday:</strong> Gases have no fixed shape or size; they spread out to fill all available space; air is an invisible but real gas.</li>
    <li><strong>Friday:</strong> Adding or removing heat causes matter to change state: melt (solid &rarr; liquid), freeze (liquid &rarr; solid), evaporate (liquid &rarr; gas), condense (gas &rarr; liquid).</li>
  </ol>
  <p style="margin-top: 10px;">By Friday, Christopher should be able to name all three states of matter, give a real example of each, and explain what happens to ice when it is heated and what happens to water when it is put in the freezer &mdash; connecting the change to heat energy.</p>
</div>

</body>
</html>"""

    guide_path = output_dir / "matter_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print("\nSuccessfully generated Matter Week.")
    print(f"Student packet:  {out_path}")
    print(f"Teacher guide:   {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Mon p1 — Reading: What Is Matter? (Meet Marco the Mole)",
        "Mon p2 — Word Sort: Solid / Liquid / Gas",
        "Tue p1 — Reading: All About Solids",
        "Tue p2 — Feature Matrix: Describing Solids",
        "Wed p1 — Reading: All About Liquids",
        "Wed p2 — Cause and Effect: How Liquids Behave",
        "Thu p1 — Reading: All About Gases",
        "Thu p2 — Odd One Out: States of Matter",
        "Fri p1 — Reading: Matter Changes State (Capstone)",
        "Fri p2 — Tree Map: States of Matter Capstone",
        "         — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")


if __name__ == "__main__":
    generate_matter_week_series()
