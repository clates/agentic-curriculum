"""
Kitchen Science — Week Series
Grade K–1 | Science | Causal Arc: Predict (sink or float) → Observe (light through materials)
  → Find the cause (vibrations make sound) → Fair test (pushes, pulls, and ramps)
  → The whole scientist loop (fast and slow changes)

Every day is one hands-on experiment built from household items (or a quick grocery run). The
science skill grows across the week: Monday a scientist PREDICTS, Tuesday they OBSERVE and sort,
Wednesday they look for the CAUSE, Thursday they run a FAIR TEST that changes one thing, and
Friday they put every step together.

Narrator: Professor Rex, a T. rex scientist, introduced on Monday. His arms are too short to
reach the lab table, so he needs a helper — the student — to run every experiment for him.

Output (kitchen_science_week_series/):
  kitchen_science_week.html              — student packet (13 pages)
  kitchen_science_week_teacher_guide.html — Parent Experiment Guide: shopping list, safety, and
                                            per-day setup, the science explained for grown-ups,
                                            answer keys, and talking points

Standards (Virginia SOL):
  Monday    — VA.SCIENCE.K.k.1, VA.SCIENCE.K.k.3.d, VA.SCIENCE.1.1.3.a
              (make predictions from observations; relative size and weight; objects are made of
              materials with different properties)
  Tuesday   — VA.SCIENCE.1.1.3.c, VA.SCIENCE.K.k.8.b, VA.SCIENCE.K.k.1
              (type and amount of material determine how much light passes through; shadows form
              when light is blocked; classify by a single property)
  Wednesday — VA.SCIENCE.1.1.2.b, VA.SCIENCE.K.k.5.a
              (objects may vibrate and produce sound; senses correspond to body structures)
  Thursday  — VA.SCIENCE.K.k.2.a, VA.SCIENCE.K.k.2.b, VA.SCIENCE.K.k.2.c, VA.SCIENCE.1.1.1
              (pushes and pulls cause motion, change direction, and strength matters; conduct
              investigations to produce data; recognize unexpected results — air pressure
              holds a card under an upside-down cup of water)
  Friday    — VA.SCIENCE.K.k.10.c, VA.SCIENCE.K.k.10.d, VA.SCIENCE.K.k.4.c, VA.SCIENCE.1.1.1
              (changes can be observed and measured; changes may be fast or slow; water occurs in
              different phases — melting ice and cloud-in-a-jar condensation; use physical
              models to demonstrate natural processes; capstone: the full investigation cycle)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html


def generate_kitchen_science_week_series():
    output_dir = Path("kitchen_science_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []  # (day_label, html_fragment)

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — Sink or Float? (Scientists PREDICT)
    # Standards: K.k.1, K.k.3.d, 1.1.3.a
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: Sink or Float?",
            "passage_title": "Meet Professor Rex — the Scientist Who Needs a Helper!",
            "instructions": (
                "Before reading: Fill a big bowl or the sink with water. Gather the 8 things on the "
                "next page, but do NOT put them in the water yet!\n\n"
                "Read the story with a grown-up. Then fill in the PREDICT boxes on the next page "
                "before you test anything."
            ),
            "passage": (
                "Meet Professor Rex! Rex is a T. rex, and he is a scientist. He has big feet, sharp "
                "teeth, and a very big brain full of questions. But Rex has one problem. His arms "
                "are too short to reach the lab table! So Rex needs a helper. That helper is YOU.\n\n"
                "'Scientists ask questions,' says Rex. 'Today our question is: will it sink or will "
                "it float?' Something that sinks drops down to the bottom of the water. Something "
                "that floats stays on top.\n\n"
                "Before a scientist tests, they make a prediction. A prediction is a smart guess "
                "about what will happen. It is okay if your prediction is wrong! A wrong prediction "
                "means you learned something new.\n\n"
                "Here is a tricky thing Rex found out. Big things do not always sink, and small "
                "things do not always float. A big apple floats! A tiny penny sinks! What matters is "
                "how heavy a thing is for its size, and what it is made of. An apple has lots of "
                "air inside it. A penny is made of solid metal.\n\n"
                "'Now, helper,' Rex roars, 'drop them in one at a time. Let's find out!'"
            ),
            "vocabulary": [
                {
                    "term": "float",
                    "definition": "To stay on top of the water.",
                },
                {
                    "term": "scientist",
                    "definition": "A person who asks questions and tests things to find answers.",
                },
                {
                    "term": "sink",
                    "definition": "To drop down to the bottom of the water.",
                },
                {
                    "term": "material",
                    "definition": "What a thing is made of — like metal, wood, plastic, or fruit.",
                },
                {
                    "term": "prediction",
                    "definition": "A smart guess about what will happen, made BEFORE you test.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is a prediction? When do you make one — before or after you test?",
                    "response_lines": 2,
                },
                {
                    "prompt": "The apple is big but it floats. Why?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Which of your predictions was wrong? What surprised you?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: An orange floats in its peel. What do you think happens "
                        "if we peel it and drop it in again? Make a prediction — then try it!"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    add(
        "featureMatrixWorksheet",
        {
            "title": "Monday: Sink or Float? — Predict, Then Test",
            "instructions": (
                "STEP 1 — PREDICT: For each thing, check ONE predict box: will it float or sink? "
                "STEP 2 — TEST: Gently drop it in the water. "
                "STEP 3 — RESULT: Check what really happened. Circle any you got wrong — "
                "those are the best ones to talk about!"
            ),
            "items": [
                "Penny",
                "Apple",
                "Grape",
                "Ice cube",
                "Metal spoon",
                "Plastic bottle cap",
                "Pebble",
                "Orange (with peel)",
            ],
            "properties": [
                "PREDICT: Float",
                "PREDICT: Sink",
                "RESULT: Float",
                "RESULT: Sink",
            ],
        },
        "Monday",
    )

    # =========================================================================
    # TUESDAY — Light Detectives (Scientists OBSERVE)
    # Standards: 1.1.3.c, K.k.8.b, K.k.1
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: Light Detectives",
            "passage_title": "Does Light Go Through It?",
            "instructions": (
                "Hands-on activity: Make the room dark. Shine a flashlight at a white wall. "
                "Hold each material from the word bank on the next page in the beam. "
                "Look at the wall: is there a bright spot, a fuzzy shadow, or a dark shadow?\n\n"
                "Never shine the flashlight into anyone's eyes."
            ),
            "passage": (
                "Professor Rex turned off the lights. 'Today we are light detectives,' he whispered. "
                "'A detective looks very carefully. In science, looking carefully is called "
                "observing.'\n\n"
                "Rex shined a flashlight at the wall. Then he asked you to hold things in the beam "
                "of light, one at a time.\n\n"
                "Some things let almost all the light pass through. You can see right through them, "
                "like a clear glass or plastic wrap. These things are transparent.\n\n"
                "Some things let only a little light through. The light looks soft and fuzzy, like "
                "light through wax paper. These things are translucent.\n\n"
                "Some things block all the light. Cardboard and a book are like this. These things "
                "are opaque. When an opaque thing blocks the light, it makes a dark shape on the "
                "wall. That dark shape is a shadow.\n\n"
                "Then Rex had a sneaky idea. 'Fold the wax paper. Now fold it again!' The more "
                "layers you add, the less light gets through. 'So it is not just WHAT the material "
                "is,' said Rex. 'It is also HOW MUCH of it there is!'"
            ),
            "vocabulary": [
                {
                    "term": "opaque",
                    "definition": "Blocks all the light. You cannot see through it at all.",
                },
                {
                    "term": "observe",
                    "definition": "To look (and listen, and feel) very carefully.",
                },
                {
                    "term": "shadow",
                    "definition": "A dark shape made when something blocks the light.",
                },
                {
                    "term": "transparent",
                    "definition": "Lets almost all the light through. You can see through it clearly.",
                },
                {
                    "term": "translucent",
                    "definition": "Lets some light through, but it looks fuzzy.",
                },
            ],
            "questions": [
                {
                    "prompt": "Name one thing that was transparent and one thing that was opaque.",
                    "response_lines": 2,
                },
                {
                    "prompt": "What makes a shadow?",
                    "response_lines": 1,
                },
                {
                    "prompt": "What happened to the light when you folded the wax paper again and again?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Your hand makes a dark shadow, so it is opaque — right? "
                        "Now press the flashlight against the tips of your fingers in the dark. "
                        "What do you see? Is your hand really opaque?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "wordSortWorksheet",
        {
            "title": "Tuesday: Light Detectives — Sort Your Materials",
            "instructions": (
                "Test each material with your flashlight. Then write it in the box that matches "
                "what you OBSERVED on the wall."
            ),
            "categories": [
                {"label": "Transparent — light goes through"},
                {"label": "Translucent — some light, fuzzy"},
                {"label": "Opaque — blocks light, dark shadow"},
            ],
            "tiles": [
                "Wax paper",
                "Cardboard",
                "Clear glass cup",
                "Tissue paper",
                "Aluminum foil",
                "Plastic wrap",
                "Coffee filter",
                "Book",
                "Clear water bottle",
                "Wooden spoon",
            ],
        },
        "Tuesday",
    )

    # =========================================================================
    # WEDNESDAY — Good Vibrations (Scientists find the CAUSE)
    # Standards: 1.1.2.b, K.k.5.a
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: Good Vibrations",
            "passage_title": "What Makes a Sound?",
            "instructions": (
                "Before reading: Put your fingers gently on the front of your throat and hum. "
                "What do you feel?\n\n"
                "Hands-on activity: Make a rubber band guitar (stretch rubber bands around an open "
                "box or plastic container) and a rice drum (plastic wrap pulled tight over a bowl, "
                "with a few grains of rice on top). Use them to answer the questions."
            ),
            "passage": (
                "ROAR! Professor Rex let out a big roar. Then he asked, 'Where does a sound come "
                "from?' Put your fingers on your throat and hum. Can you feel a buzzy, shaky "
                "feeling? That shaking is called a vibration.\n\n"
                "A vibration is a very fast back-and-forth shake. It can be so fast that you cannot "
                "see it. Every sound starts with something that vibrates. The vibration shakes the "
                "air, and the shaking air travels to your ears. Your ears are the part of your body "
                "that hears.\n\n"
                "Pluck a rubber band on your guitar. You can see it wiggle! When it stops wiggling, "
                "the sound stops too. A tight, thin rubber band makes a high sound. A loose, thick "
                "rubber band makes a low sound.\n\n"
                "Now tap the plastic wrap on your rice drum. The rice jumps! You cannot see the "
                "plastic shake, but the jumping rice shows you it is vibrating.\n\n"
                "'So the vibration is the CAUSE,' said Rex, 'and the sound is the EFFECT. "
                "No shake, no sound!'"
            ),
            "vocabulary": [
                {
                    "term": "effect",
                    "definition": "What happens because of a cause.",
                },
                {
                    "term": "vibration",
                    "definition": "A very fast back-and-forth shake. Every sound starts with one.",
                },
                {
                    "term": "high and low",
                    "definition": "How a sound can be — like a squeaky mouse (high) or a big drum (low).",
                },
                {
                    "term": "cause",
                    "definition": "The thing that makes something else happen.",
                },
                {
                    "term": "ears",
                    "definition": "The part of your body you use to hear sounds.",
                },
            ],
            "questions": [
                {
                    "prompt": "What did you feel on your throat when you hummed?",
                    "response_lines": 1,
                },
                {
                    "prompt": "What starts every sound?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Why did the rice jump when you tapped the drum?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Hold the rice drum near a pot and bang the pot with a spoon "
                        "— but do NOT touch the drum. Does the rice still jump? How did the "
                        "vibration get there?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "causeEffectWorksheet",
        {
            "title": "Wednesday: Good Vibrations — Cause and Effect",
            "instructions": (
                "Try each cause with your guitar, drum, or voice. Then write or draw the effect — "
                "what happened?"
            ),
            "pairs": [
                {
                    "cause": "I plucked a rubber band on my guitar.",
                    "effect": "",
                    "effect_lines": 1,
                },
                {
                    "cause": "I put my hand on the rubber band to stop it shaking.",
                    "effect": "",
                    "effect_lines": 1,
                },
                {
                    "cause": "I stretched the rubber band tighter and plucked it again.",
                    "effect": "",
                    "effect_lines": 1,
                },
                {
                    "cause": "I tapped the plastic wrap on my rice drum.",
                    "effect": "",
                    "effect_lines": 1,
                },
                {
                    "cause": "I covered my ears and Rex roared.",
                    "effect": "",
                    "effect_lines": 1,
                },
            ],
        },
        "Wednesday",
    )

    # =========================================================================
    # THURSDAY — Push, Pull, Zoom! (Scientists run a FAIR TEST)
    # Standards: K.k.2.a, K.k.2.b, K.k.2.c, 1.1.1
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: Push, Pull, Zoom!",
            "passage_title": "How Do We Make a Car Go Farther?",
            "instructions": (
                "Hands-on activity: You need one toy car, a hard floor, a stack of books, and a "
                "flat board or big piece of cardboard for a ramp. Put a strip of tape on the floor "
                "as your starting line.\n\n"
                "After reading, run the ramp test on the next page. Measure how far the car goes "
                "by counting your heel-to-toe footsteps.\n\n"
                "Then, over the sink, try Rex's magic cup trick and fill in the Lab Report."
            ),
            "passage": (
                "Professor Rex loves cars. 'VROOM!' he roared. 'Today's question is: how can we "
                "make a car go farther?'\n\n"
                "A car will not move by itself. It needs a push or a pull. A push moves something "
                "away from you. A pull moves something toward you. A push or a pull is called a "
                "force.\n\n"
                "Give the car a gentle push. It rolls a little way. Now give it a hard push. "
                "Zoom! It goes much farther. A stronger push makes a bigger change in how a thing "
                "moves. You can also push the car from the side to make it turn and go a new "
                "direction.\n\n"
                "Next, Rex built a ramp. When the car rolls down a ramp, nobody pushes it. Earth "
                "pulls it down! That pull is called gravity. A taller ramp lets gravity speed the "
                "car up more.\n\n"
                "'But helper,' said Rex, 'to be fair, we must only change ONE thing. Same car. Same "
                "floor. Same starting spot. We only change how many books are under the ramp.' "
                "Scientists call this a fair test.\n\n"
                "Then Rex showed one more trick. He filled a cup with water, put a card on top, "
                "and flipped it upside down over the sink. The water stayed in the cup! 'What is "
                "holding the card up?' he asked. 'Air!' Air is all around us, and it pushes on "
                "everything. That push is called air pressure. Air can push, too!"
            ),
            "vocabulary": [
                {
                    "term": "pull",
                    "definition": "A force that moves something toward you.",
                },
                {
                    "term": "fair test",
                    "definition": "A test where you change only ONE thing and keep everything else the same.",
                },
                {
                    "term": "force",
                    "definition": "A push or a pull.",
                },
                {
                    "term": "gravity",
                    "definition": "The pull that makes things fall down toward the Earth.",
                },
                {
                    "term": "push",
                    "definition": "A force that moves something away from you.",
                },
                {
                    "term": "air pressure",
                    "definition": "The push of the air all around us. Air pushes on everything!",
                },
            ],
            "questions": [
                {
                    "prompt": "What happened when you pushed the car gently? What about hard?",
                    "response_lines": 2,
                },
                {
                    "prompt": "How can you make the car change direction?",
                    "response_lines": 1,
                },
                {
                    "prompt": "In our ramp test, what is the ONE thing we change?",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Your friend tests a car on a 1-book ramp on the carpet and "
                        "a 3-book ramp on the kitchen floor. The 3-book car wins. Was that a fair "
                        "test? How would you fix it?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    add(
        "tChartWorksheet",
        {
            "title": "Thursday: Ramp Test — Record Your Data",
            "instructions": (
                "Write 1, 2, 3, and 4 in the first column (books under the ramp). Predict how many "
                "footsteps the car will roll. Then let the car go — do not push it! — and count "
                "the real footsteps. Do each test twice. In the last row, write which ramp won."
            ),
            "columns": ["Books under ramp", "I predict (footsteps)", "Test 1", "Test 2"],
            "row_count": 5,
        },
        "Thursday",
    )

    add(
        "writingScaffoldWorksheet",
        {
            "title": "Thursday: Lab Report — The Magic Cup",
            "instructions": (
                "Do this over the sink! Fill a cup with water all the way to the top. Lay a card "
                "flat on top. Hold the card with your hand and flip the cup upside down. Now let "
                "go of the card. Write or draw in each part. A grown-up can help you write."
            ),
            "topic": "What will happen to the card and the water?",
            "sections": [
                {
                    "label": "ASK",
                    "starter": "If I let go of the card, will the water fall out?",
                    "lines": 0,
                },
                {"label": "I PREDICT", "starter": "I think the water will", "lines": 2},
                {
                    "label": "I OBSERVE (write or draw)",
                    "starter": "When I let go, the card",
                    "lines": 3,
                },
                {"label": "I LEARNED", "starter": "The card stayed up because the air", "lines": 2},
                {
                    "label": "TRY IT AGAIN",
                    "starter": "Now fill the cup only HALF full. Does it still work?",
                    "lines": 2,
                },
            ],
        },
        "Thursday",
    )

    # =========================================================================
    # FRIDAY — Fast and Slow Changes (Capstone: the whole scientist loop)
    # Standards: K.k.10.c, K.k.10.d, K.k.4.c, 1.1.1
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: Dino Volcano — Fast and Slow Changes",
            "passage_title": "Professor Rex's Big Experiment",
            "instructions": (
                "Capstone activity: Put an ice cube on a plate at the START of the lesson. Then "
                "make a cloud in a jar with a grown-up (the Lab Report page). Last, build a dino "
                "volcano on a baking sheet. Check the ice cube when the volcano is done.\n\n"
                "Use the Steps of a Scientist page to put the volcano experiment in order."
            ),
            "passage": (
                "'This week you learned to predict, observe, find a cause, and run a fair test,' "
                "said Professor Rex. 'Today we use ALL of them!'\n\n"
                "First, the cloud jar. Warm water turned into water vapor, a gas you cannot see. "
                "Cold ice on the lid cooled the vapor, and it turned back into tiny drops of "
                "water. Millions of tiny drops make a cloud, just like in the sky!\n\n"
                "Next, the volcano. Pour vinegar onto the baking soda and watch. FIZZ! Foam "
                "spills over like lava. The bubbles are full of a gas that is brand new. That "
                "change took just seconds. It was a fast change, and you cannot turn the bubbles "
                "back into baking soda!\n\n"
                "Now look at your ice cube. It is melting, but slowly. That took many minutes. It "
                "is a slow change. A banana takes days to turn brown, which is even slower.\n\n"
                "Last, a scientist records what happened and makes a conclusion. 'Fizz is fast, "
                "melting is slow,' said Rex. 'Helper, you are a real scientist now!'"
            ),
            "vocabulary": [
                {
                    "term": "slow change",
                    "definition": "A change that takes minutes, days, or even years — like ice melting or a banana browning.",
                },
                {
                    "term": "conclusion",
                    "definition": "What you learned from your test, using what you saw.",
                },
                {
                    "term": "gas",
                    "definition": "Matter like air that spreads out to fill space. The fizz bubbles are full of it.",
                },
                {
                    "term": "fast change",
                    "definition": "A change that happens in seconds — like the volcano fizzing.",
                },
                {
                    "term": "water vapor",
                    "definition": "Water as a gas. It floats in the air and you cannot see it.",
                },
            ],
            "questions": [
                {
                    "prompt": "What did you predict would happen? What really happened?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Was the fizz a fast change or a slow change? What about the ice cube?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Can you turn the melted water back into ice? Can you turn the fizz back into baking soda?",
                    "response_lines": 1,
                },
                {
                    "prompt": "What made the cloud in the jar: warm water, cold ice, or both?",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Which experiment this week was your favorite? Tell a "
                        "grown-up about it using these words: I PREDICTED... I OBSERVED... "
                        "I LEARNED..."
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Friday",
    )

    add(
        "writingScaffoldWorksheet",
        {
            "title": "Friday: Lab Report — Cloud in a Jar",
            "instructions": (
                "A grown-up pours the hot water. You put the ice on the lid and watch! "
                "Write or draw in each part. A grown-up can help you write."
            ),
            "topic": "Can we make a real cloud inside a jar?",
            "sections": [
                {
                    "label": "ASK",
                    "starter": "What happens when warm, wet air meets something cold?",
                    "lines": 0,
                },
                {"label": "I PREDICT", "starter": "I think the jar will", "lines": 2},
                {
                    "label": "I OBSERVE (write or draw)",
                    "starter": "Inside the jar I saw",
                    "lines": 3,
                },
                {
                    "label": "I OBSERVE — the lid",
                    "starter": "When we lifted the lid, the cloud",
                    "lines": 2,
                },
                {"label": "I LEARNED", "starter": "A cloud is made of", "lines": 2},
            ],
        },
        "Friday",
    )

    add(
        "sequencingWorksheet",
        {
            "title": "Friday: Steps of a Scientist",
            "activity_name": "Professor Rex's Dino Volcano",
            "instructions": (
                "Cut out the steps. Put them in the order a scientist would do them, then glue them "
                "onto another sheet of paper. Write the number in each box."
            ),
            # Shuffled — correct order lives in the parent guide.
            "steps": [
                {"text": "TEST: Pour the vinegar into the volcano cup.", "correct_order": 3},
                {
                    "text": "CONCLUDE: Say what we learned — the fizz was a FAST change.",
                    "correct_order": 6,
                },
                {"text": "ASK: What happens when baking soda meets vinegar?", "correct_order": 1},
                {"text": "RECORD: Draw the volcano and the ice cube.", "correct_order": 5},
                {"text": "PREDICT: I think it will ______.", "correct_order": 2},
                {"text": "OBSERVE: Watch the foam bubble and spill over.", "correct_order": 4},
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
            "title": "End-of-Week Parent Feedback — Kitchen Science Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this feedback sheet after the week wraps up. "
                "Your notes help shape next week's lessons."
            ),
            "passage": (
                "This week was built around five hands-on experiments, and the real lesson ran "
                "underneath them: how a scientist thinks. Monday's sink-or-float test practiced "
                "making a prediction BEFORE testing. Tuesday's flashlight test practiced careful "
                "observation and sorting materials by one property (how much light passes "
                "through). Wednesday's rubber band guitar and rice drum looked for a cause — "
                "vibrations — behind an effect — sound. Thursday's ramp race introduced the fair "
                "test: change one thing, keep everything else the same, and measure. The "
                "upside-down cup showed that air pushes too. Friday's cloud in a jar showed water "
                "changing from gas to liquid, and the dino volcano used every step together and "
                "compared fast and slow changes.\n\n"
                "Key ideas to check for genuine understanding — not just recall:\n"
                "1) A prediction comes before the test, and a wrong prediction is useful.\n"
                "2) Whether something floats depends on how heavy it is for its size, not size alone.\n"
                "3) Every sound starts with a vibration.\n"
                "4) A stronger push makes a bigger change in motion; a fair test changes one thing; "
                "air is real stuff that pushes too.\n"
                "5) Water changes form (ice melts, vapor condenses into a cloud); some changes are "
                "fast, some slow, and some cannot be undone."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": "'Heavy things sink and light things float.' A heavy log floats and a light paperclip sinks — it is weight for its SIZE that matters.",
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in after the week — which idea did Christopher grasp best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": "Invent a fair test of his own: which paper towel brand soaks up the most water?",
                },
            ],
            "questions": [
                {
                    "prompt": "Overall comfort with the week's content (1 = struggled throughout, 5 = strong grasp):",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which experiment generated the most excitement or questions?",
                    "response_lines": 2,
                },
                {
                    "prompt": "By Friday, did Christopher make predictions without being asked?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Could he explain why a test was or wasn't fair?",
                    "response_lines": 2,
                },
                {"prompt": "Experiments to repeat or topics to revisit:", "response_lines": 2},
            ],
        },
        "Friday",
    )

    # =========================================================================
    # Assemble & write
    # =========================================================================

    html = build_print_packet_html(
        pages, packet_title="Kitchen Science Week — Experiments with Professor Rex"
    )
    out_path = output_dir / "kitchen_science_week.html"
    out_path.write_text(html, encoding="utf-8")

    # Parent Experiment Guide — the parent-audience companion to the packet
    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Kitchen Science Week — Parent Experiment Guide</title>
  <style>
    @page { size: letter; margin: 0.4in 0.5in; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Trebuchet MS', Arial, sans-serif; font-size: 10pt; color: #111; line-height: 1.36; }
    @media screen { body { background: #b0b0b0; padding: 24px; } .page { background: white; max-width: 7.5in; margin: 0 auto 28px; padding: 0.4in 0.45in; box-shadow: 0 4px 18px rgba(0,0,0,.28); min-height: 10.3in; } }
    @media print { body { background: white; padding: 0; } .page { padding: 0; box-shadow: none; } * { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
    .page { page-break-after: always; break-after: page; }
    .page:last-child { page-break-after: avoid; break-after: avoid; }
    h1 { font-size: 18pt; color: #1d4ed8; border-bottom: 3px solid #1d4ed8; padding-bottom: 5px; margin-bottom: 10px; }
    h2 { font-size: 13pt; color: #fff; background: #1d4ed8; padding: 5px 10px; border-radius: 3px; margin: 4px 0 8px; }
    h2.tue { background: #15803d; }
    h2.wed { background: #7c3aed; }
    h2.thu { background: #c2410c; }
    h2.fri { background: #0f766e; }
    h2.gen { background: #374151; }
    h3 { font-size: 9.5pt; font-weight: bold; color: #444; margin: 6px 0 2px; text-transform: uppercase; letter-spacing: 0.04em; }
    p, li { font-size: 9.5pt; margin-bottom: 3px; }
    ul, ol { padding-left: 18px; margin-bottom: 6px; }
    .meta { font-size: 9.5pt; color: #444; margin-bottom: 6px; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .box { padding: 4px 9px; margin: 2px 0 5px; border-radius: 0 4px 4px 0; font-size: 9.5pt; border-left: 4px solid; }
    .materials { background: #f3f4f6; border-color: #374151; }
    .materials ul { list-style: none; padding-left: 0; }
    .materials li::before { content: "\\2610  "; }
    .science { background: #eef6ff; border-color: #0369a1; }
    .answer-box { background: #f0f4ff; border-color: #1d4ed8; }
    .answer-box.tue { background: #f0fff4; border-color: #15803d; }
    .answer-box.wed { background: #f5f0ff; border-color: #7c3aed; }
    .answer-box.thu { background: #fff7f0; border-color: #c2410c; }
    .answer-box.fri { background: #f0fff8; border-color: #0f766e; }
    .safety { background: #fee2e2; border-color: #b91c1c; }
    .misconception { background: #fff3cd; border-color: #d97706; }
    .extension { background: #e8f5e9; border-color: #15803d; }
    .discuss { background: #fce7f3; border-color: #9d174d; }
    table.overview { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 4px 0 10px; }
    table.overview th, table.overview td { border: 1px solid #ccc; padding: 4px 6px; text-align: left; vertical-align: top; }
    table.overview th { background: #374151; color: #fff; }
  </style>
</head>
<body>

<!-- ===================================================================== -->
<div class="page">
  <h1>Kitchen Science Week — Parent Experiment Guide</h1>
  <p class="meta"><strong>Audience:</strong> Christopher, age 6, K–1 &nbsp;|&nbsp;
  <strong>Narrator:</strong> Professor Rex, a T. rex scientist whose arms are too short to reach the
  lab table, so your child does every experiment for him &nbsp;|&nbsp; <strong>Time:</strong> about
  90 minutes a day, experiment included</p>

  <p>These pages go with the student packet. Each day has one experiment and two student pages: a
  story to read together, then a page your child fills in <em>during</em> the experiment. This
  guide tells you what to buy, how to set up, what is really going on (in grown-up terms), and
  what answers to look for.</p>

  <h2 class="gen">The week at a glance</h2>
  <table class="overview">
    <tr><th>Day</th><th>Experiment</th><th>Science idea</th><th>Scientist skill</th></tr>
    <tr><td>Mon</td><td>Sink or Float</td><td>Floating depends on weight for size and material</td><td>Predict</td></tr>
    <tr><td>Tue</td><td>Flashlight Detectives</td><td>Transparent, translucent, opaque; shadows</td><td>Observe and sort</td></tr>
    <tr><td>Wed</td><td>Rubber Band Guitar &amp; Rice Drum</td><td>Every sound starts with a vibration</td><td>Find the cause</td></tr>
    <tr><td>Thu</td><td>Toy Car Ramp Race + Magic Upside-Down Cup</td><td>Pushes, pulls, gravity, stronger force = bigger change; air pushes too (air pressure)</td><td>Fair test</td></tr>
    <tr><td>Fri</td><td>Cloud in a Jar + Dino Volcano + Melting Ice</td><td>Water changes form (melting, condensation); fast and slow changes</td><td>All of them together</td></tr>
  </table>

  <h2 class="gen">Shopping &amp; gathering list</h2>
  <div class="two-col">
    <div class="box materials">
      <p><strong>Probably already in the house</strong></p>
      <ul>
        <li>Large bowl or a sink, towels</li>
        <li>Penny, metal spoon, pebble, plastic bottle cap</li>
        <li>Ice cubes</li>
        <li>Flashlight (a phone light works)</li>
        <li>Wax paper, plastic wrap, aluminum foil</li>
        <li>Tissue paper or a tissue, coffee filter</li>
        <li>Cardboard, a book, wooden spoon, clear glass</li>
        <li>Open box or plastic food container</li>
        <li>Uncooked rice (a spoonful)</li>
        <li>A pot and a metal spoon</li>
        <li>Toy car, stack of books, tape</li>
        <li>Plastic cup or short glass, an index card or playing card, a drinking straw</li>
        <li>Clear glass jar with a metal lid (pasta-sauce or mason jar)</li>
        <li>Board, baking sheet, or stiff cardboard (ramp)</li>
        <li>Plastic cup, baking sheet or tray</li>
      </ul>
    </div>
    <div class="box materials">
      <p><strong>Quick store run if needed</strong></p>
      <ul>
        <li>1 apple, 1 orange, a few grapes</li>
        <li>Rubber bands — mixed thick &amp; thin</li>
        <li>Baking soda (1 box)</li>
        <li>White vinegar (1 bottle)</li>
        <li>Dish soap</li>
        <li>Food coloring (red/orange for lava)</li>
        <li>Play dough or sand (to shape the volcano), optional</li>
        <li>Banana (for the slow-change comparison)</li>
        <li>Aerosol hairspray (for the cloud jar), or use a match instead (see Friday)</li>
        <li>Black construction paper (optional backdrop for the cloud)</li>
        <li>Balloon + empty plastic bottle (optional Friday extension)</li>
      </ul>
      <p style="margin-top:6px;">Swapping is fine. Any small object can join Monday's test, and any
      household material can join Tuesday's.</p>
    </div>
  </div>

</div>

<div class="page">
  <h2 class="gen">Safety for the whole week</h2>
  <div class="box safety">
    <ul>
      <li><strong>Water play:</strong> stay at the bowl the whole time. Wipe up spills right away.</li>
      <li><strong>Small items</strong> (penny, grapes, rice, bottle caps) are choking hazards. Keep them away from younger siblings.</li>
      <li><strong>Flashlights:</strong> never into eyes. LED lights get warm. Only press against fingertips for a few seconds.</li>
      <li><strong>Rubber bands:</strong> no snapping toward faces.</li>
      <li><strong>Cloud jar:</strong> a grown-up pours the hot water. Use hairspray <em>or</em> a match, <strong>never both</strong>, since hairspray is flammable.</li>
      <li><strong>Vinegar</strong> stings eyes. Do the volcano on a tray and keep hands away from faces. If it gets in an eye, rinse with water.</li>
    </ul>
  </div>

  <h2 class="gen">How to run any experiment</h2>
  <p><strong>Let your child do the hands-on part.</strong> Professor Rex "can't reach," so the
  child pours, drops, plucks, and measures. You ask questions. The most useful habit to build is
  <strong>predict out loud before every test</strong>, then compare. When a prediction is wrong,
  celebrate it ("Ooh, you found a surprise!"). Wrong predictions teach the most.</p>

  <h2 class="gen">By the end of the week</h2>
  <p>Christopher should be able to make a prediction before testing without being asked, say what made a test fair or unfair, and retell one experiment using <em>predicted / observed / learned</em>. Those habits matter more than any single fact from the week.</p>
</div>

<!-- ===================================================================== -->
<div class="page">
  <h2>Monday — Sink or Float? &nbsp;<span style="font-weight:normal;font-size:10pt;">Skill: Predict</span></h2>
  <p class="meta">Standards: VA K.1 (predictions from observations), K.3.d (relative size and weight), 1.3.a (materials and properties)</p>

  <h3>What you need</h3>
  <div class="box materials"><p>Big bowl or sink of water, towel, penny, apple, grape, ice cube, metal spoon, plastic bottle cap, pebble, orange (keep the peel on for now).</p></div>

  <h3>Run it</h3>
  <ol>
    <li>Read the Rex story together <em>before</em> anything touches the water.</li>
    <li>For each object, your child picks one PREDICT box on the chart. Ask "why do you think so?" Listen for reasons: "it's heavy," "it's small," "it's metal."</li>
    <li>Your child drops each object in gently. Then they check a RESULT box.</li>
    <li>Circle any wrong predictions and talk about them first.</li>
    <li>For the LET'S DISCUSS question, peel the orange and test again.</li>
  </ol>

  <h3>What's really happening</h3>
  <div class="box science">
    <p>Whether something floats comes down to <strong>density</strong>: how much mass is packed into its size compared with water. If an object is less dense than water, the water pushes it up hard enough to hold it on top (this is buoyancy). If it is more dense, it sinks. That's why size alone fails as a rule. An apple is about 25% air trapped in its flesh, so it floats even though it's big. A grape is small, but it's packed with juice and sugar, so it's a little denser than water and usually sinks.</p>
    <p>The orange is the star. Its peel is full of tiny air pockets, like a built-in life jacket. Peel it, and the fruit underneath is denser than water, so it sinks. Same orange, different result. It's a perfect example of "what it's made of matters."</p>
    <p><em>For a 6-year-old,</em> "how heavy it is for its size" is the right phrase. You don't need the word density yet.</p>
  </div>

  <h3>Answer key</h3>
  <div class="box answer-box">
    <p><strong>Chart (typical results):</strong> Float: apple, ice cube, plastic bottle cap, orange with peel. Sink: penny, grape, metal spoon, pebble.<br>
    <em>Real objects vary. Some grapes float, and a bottle cap sinks if it tips and fills with water. Always accept what your child actually observed. Trusting evidence over the answer key is the lesson.</em></p>
    <p><strong>Q1:</strong> A smart guess about what will happen. You make it BEFORE you test.</p>
    <p><strong>Q2:</strong> It has lots of air inside it, so it is light for its size.</p>
    <p><strong>Q3:</strong> Personal answer. Ask what clue fooled them.</p>
  </div>

  <h3>LET'S DISCUSS guidance</h3>
  <div class="box discuss"><p><em>"What happens if we peel the orange?"</em> Get a prediction first. Most kids guess it will float better, since it's lighter now. It sinks! Point to the peel and let your child squish it and look closely: the peel is spongy and full of air, and that's what was holding the orange up.</p></div>

  <h3>Misconceptions to watch</h3>
  <div class="box misconception"><p>"Big/heavy things sink, small/light things float." The apple and the grape break this rule, so linger there. Also: "it floated because it's flat." Shape can matter (boats), but only because the shape holds air. See the extension.</p></div>

  <h3>Go further</h3>
  <div class="box extension"><p><strong>Foil boat challenge:</strong> Squeeze a square of foil into a tight ball. It sinks. Now shape the same square into a little boat. It floats! Load pennies in one at a time. How many can it hold before it sinks? (Same material, different shape. The boat shape holds air.)</p></div>
</div>

<!-- ===================================================================== -->
<div class="page">
  <h2 class="tue">Tuesday — Light Detectives &nbsp;<span style="font-weight:normal;font-size:10pt;">Skill: Observe &amp; sort</span></h2>
  <p class="meta">Standards: VA 1.3.c (type and amount of material determine how much light passes through), K.8.b (shadows when light is blocked), K.1 (classify by one property)</p>

  <h3>What you need</h3>
  <div class="box materials"><p>Flashlight, a light-colored wall in a darkened room, wax paper, cardboard, clear glass cup, tissue paper, aluminum foil, plastic wrap, coffee filter, a book, a clear (empty) water bottle, a wooden spoon.</p></div>

  <h3>Run it</h3>
  <ol>
    <li>Darken the room. Your child holds the flashlight about an arm's length from the wall.</li>
    <li>You hold each material in the beam, halfway between the light and the wall. (Or swap jobs.) Ask: "Bright spot, fuzzy light, or dark shadow?"</li>
    <li>Your child writes each word in the matching box on the sort page.</li>
    <li>Fold the wax paper in half and test. Then fold it again, and again. Watch the wall get darker.</li>
    <li>Finish with the fingertip test from LET'S DISCUSS.</li>
  </ol>

  <h3>What's really happening</h3>
  <div class="box science">
    <p>When light hits a material, three things can happen: it passes straight through, it gets scattered in many directions, or it gets absorbed or reflected back. <strong>Transparent</strong> materials let light pass straight through, so you can see clear images through them. <strong>Translucent</strong> materials scatter light. Some gets through, but it's jumbled, so you see a glow but no clear image. <strong>Opaque</strong> materials stop the light entirely. Because light travels in straight lines, an opaque object leaves a light-free zone behind it: a shadow.</p>
    <p>The folded wax paper shows the second half of the standard. It's not only the <em>type</em> of material but the <em>amount</em>. Each layer scatters and absorbs a bit more, so enough layers of a translucent material start to act opaque.</p>
    <p>The glowing fingertips: skin and flesh are actually translucent to red light. Blue and green light get absorbed by blood and tissue, and red light scatters through. That's why fingers glow red. A thick hand is opaque enough to make a shadow, but thin fingertips aren't. It's the "amount of material" idea again, using your own body!</p>
  </div>

  <h3>Answer key</h3>
  <div class="box answer-box tue">
    <p><strong>Sort:</strong> Transparent: clear glass cup, plastic wrap, clear water bottle. Translucent: wax paper, tissue paper, coffee filter. Opaque: cardboard, aluminum foil, book, wooden spoon.<br><em>Thin tissue or a crinkly bottle may look different in your light. Go with your child's observation if they can describe what they saw.</em></p>
    <p><strong>Q1:</strong> Any correct pair (e.g., plastic wrap / cardboard). <strong>Q2:</strong> Something blocking the light. <strong>Q3:</strong> Less and less light got through, and the wall got darker.</p>
  </div>

  <h3>LET'S DISCUSS guidance</h3>
  <div class="box discuss"><p><em>"Is your hand really opaque?"</em> Mostly. A whole hand makes a dark shadow. But fingertips glow red, so a little light gets through. Nice answer to steer toward: "It depends how thick it is," which is exactly what the wax paper showed.</p></div>

  <h3>Misconceptions to watch</h3>
  <div class="box misconception"><p>"Shadows are made of something," or "the shadow is a reflection." A shadow is just a place where light <em>isn't</em>. Move the object closer to the flashlight and the shadow grows. Move it closer to the wall and it shrinks and sharpens. Light is blocked, not copied.</p></div>

  <h3>Go further</h3>
  <div class="box extension"><p><strong>Shadow puppet show:</strong> Cut dinosaur shapes from cardboard (opaque) and tape them to straws. Add a wax-paper "ghost" (translucent) for a spooky effect. Put on a Professor Rex show on the wall.</p></div>
</div>

<!-- ===================================================================== -->
<div class="page">
  <h2 class="wed">Wednesday — Good Vibrations &nbsp;<span style="font-weight:normal;font-size:10pt;">Skill: Find the cause</span></h2>
  <p class="meta">Standards: VA 1.2.b (objects may vibrate and produce sound), K.5.a (senses correspond to body structures — ears)</p>

  <h3>What you need</h3>
  <div class="box materials"><p><strong>Guitar:</strong> an open box (tissue box, shoebox) or plastic food container, 3–4 rubber bands of different thicknesses. <strong>Drum:</strong> a bowl, plastic wrap pulled very tight (a rubber band around the rim helps), a spoonful of uncooked rice. <strong>Noise maker:</strong> a pot and a metal spoon.</p></div>

  <h3>Run it</h3>
  <ol>
    <li>Start with the throat hum: fingers on the throat, hum, then stop. Buzz on, buzz off.</li>
    <li>Build the guitar together. Stretch the bands across the opening. Pluck and <em>watch</em> them blur as they wiggle.</li>
    <li>Build the drum. Sprinkle the rice on top and tap the wrap gently.</li>
    <li>Work through the cause-and-effect page one row at a time. Your child does each cause, then writes or draws the effect.</li>
    <li>LET'S DISCUSS: hold the drum about a foot from the pot and bang the pot. Watch the rice.</li>
  </ol>

  <h3>What's really happening</h3>
  <div class="box science">
    <p>Sound is a vibration traveling through a material. When a rubber band wiggles, it shoves the air molecules next to it back and forth. They bump the next ones, and so on, in a wave that reaches the ear. Inside the ear, the eardrum is a thin membrane that vibrates in step, and the brain reads that as sound. Your rice drum is a model of an eardrum. The plastic wrap is the membrane, and the rice makes its invisible shaking visible.</p>
    <p><strong>Pitch</strong> (high vs. low) comes from how fast something vibrates. Tighter and thinner bands vibrate faster, which gives a higher pitch. Looser and thicker bands vibrate slower, which gives a lower pitch. Stop the vibration with a hand and the sound stops instantly, which is the clearest proof that vibration is the cause.</p>
    <p>Banging the pot without touching the drum shows that sound travels through air. The pot's vibration crosses the gap and shakes the wrap. That's the same trip a roar takes to reach your ears.</p>
  </div>

  <h3>Answer key</h3>
  <div class="box answer-box wed">
    <p><strong>Cause → Effect:</strong> (1) Plucked band → it wiggled and made a sound. (2) Hand on band → the shaking stopped and the sound stopped. (3) Tighter band → the sound got higher. (4) Tapped drum → the rice jumped/bounced. (5) Covered ears → the roar sounded quieter (less vibration reached the ears).<br><em>Drawn answers count. A picture of jumping rice is a full answer.</em></p>
    <p><strong>Q1:</strong> A buzzy, shaky feeling (vibration). <strong>Q2:</strong> A vibration. <strong>Q3:</strong> The plastic wrap was vibrating/shaking and bounced the rice up.</p>
  </div>

  <h3>LET'S DISCUSS guidance</h3>
  <div class="box discuss"><p><em>"Does the rice jump if you only bang the pot?"</em> Often yes, a little, if the wrap is tight and the bang is loud and close. If it doesn't, move closer or bang harder. The point to land: "The shaking traveled through the air to the drum, just like it travels to your ears."</p></div>

  <h3>Misconceptions to watch</h3>
  <div class="box misconception"><p>"Loud means high." Kids often mix up loudness (how big the vibration is, so pluck harder) with pitch (how fast it vibrates, so make the band tighter). Try one at a time: pluck the same band softly and then hard (same pitch, louder). Then tighten it (higher pitch).</p></div>

  <h3>Go further</h3>
  <div class="box extension"><p><strong>Water glass xylophone:</strong> Fill 5 glasses with different amounts of water and tap each gently with a spoon. Line them up from lowest to highest note. Can you play a simple tune?</p></div>
</div>

<!-- ===================================================================== -->
<div class="page">
  <h2 class="thu">Thursday — Push, Pull, Zoom! &nbsp;<span style="font-weight:normal;font-size:10pt;">Skill: Fair test</span></h2>
  <p class="meta">Standards: VA K.2.a–c (pushes and pulls cause motion, change direction, and strength matters), 1.1 (conduct investigations to produce data)</p>

  <h3>What you need</h3>
  <div class="box materials"><p>One toy car (rolls freely), a hard floor (not carpet), 4 books of similar thickness, a ramp (board, baking sheet, or stiff cardboard), masking or painter's tape for a start line.</p></div>

  <h3>Run it</h3>
  <ol>
    <li><strong>Push warm-up (5 min):</strong> Gentle push vs. hard push from the tape line. Then push the rolling car from the side to make it turn. Then tie a string to it and pull.</li>
    <li><strong>Ramp setup:</strong> Lay the ramp on 1 book, with the bottom touching the start line. Your child writes 1, 2, 3, 4 in the first column of the chart.</li>
    <li>Before each run, your child writes a prediction in footsteps.</li>
    <li>Hold the car at the very top and <strong>let go, no pushing</strong>. Mark where it stops, then count heel-to-toe footsteps from the end of the ramp.</li>
    <li>Run each height twice. Add a book and repeat. In the last row, write which ramp won.</li>
  </ol>

  <h3>What's really happening</h3>
  <div class="box science">
    <p>A <strong>force</strong> is a push or a pull, and forces change motion: they start it, stop it, speed it up, or turn it. A bigger force makes a bigger change. That's why the hard push sends the car farther. On the ramp, the force is <strong>gravity</strong> pulling the car down. A taller ramp gives gravity a longer drop to work with, so the car reaches the floor faster and rolls farther before <strong>friction</strong> (the rubbing between wheels, axles, and floor) slows it to a stop. Carpet adds more friction, which is why the floor surface must stay the same.</p>
    <p>The big idea of the day is the <strong>fair test</strong>, also called controlling variables. You change one thing on purpose (ramp height), measure one result (distance), and keep everything else the same: same car, same floor, same release spot, no pushing. Running each test twice shows that results wobble a bit, and that's normal in real science. Footsteps are a fine kid-sized unit. The point is that every test uses the same unit.</p>
  </div>

  <h3>Answer key</h3>
  <div class="box answer-box thu">
    <p><strong>Data chart:</strong> Distances will vary with your car and floor. Look for the <em>pattern</em>: more books → farther roll, at least up to 3–4 books. (A very steep ramp can make the car crash or bounce at the bottom. If that happens, it's an "unusual result" worth talking about, not a mistake.) Last row: the highest ramp usually wins.</p>
    <p><strong>Q1:</strong> Gentle push → it went a little way. Hard push → it went farther/faster. <strong>Q2:</strong> Push it from the side (or pull it with a string). <strong>Q3:</strong> How many books are under the ramp (how tall it is).</p>
  </div>

  <h3>LET'S DISCUSS guidance</h3>
  <div class="box discuss"><p><em>"Carpet with 1 book vs. kitchen floor with 3 books — fair?"</em> No. Two things changed, the floor <em>and</em> the height, so we can't tell which one made the difference. Fix: test both heights on the same floor. If your child gets this, they've understood the hardest idea of the week.</p></div>

  <h3>Misconceptions to watch</h3>
  <div class="box misconception"><p>"The car keeps going because it has 'push' stored in it, and it stops when the push runs out." In reality, a moving car would keep rolling forever if nothing slowed it. Friction is a force that stops it. Try rolling the car on carpet vs. a smooth floor to show friction at work.</p></div>

  <h3>Go further</h3>
  <div class="box extension"><p><strong>Balloon rocket:</strong> Thread a straw onto a long string tied between two chairs. Blow up a balloon (don't tie it), tape it to the straw, and let go. Air rushing out the back <em>pushes</em> the balloon forward. Does a bigger balloon go farther? (Another fair test!)</p></div>
</div>

<!-- ===================================================================== -->
<div class="page">
  <h2 class="thu">Thursday, part 2 — The Magic Upside-Down Cup &nbsp;<span style="font-weight:normal;font-size:10pt;">Air pressure</span></h2>
  <p class="meta">Standards: VA K.2.a (pushes can cause, or here prevent, motion), 1.1 (recognize unusual or unexpected results). About 15 minutes, after the ramp test.</p>

  <h3>What you need</h3>
  <div class="box materials"><p>A plastic cup or short, smooth-rimmed glass; an index card, playing card, or square of thin cardboard a bit bigger than the rim; water; the kitchen sink (or a big bowl or bathtub to catch spills); a drinking straw.</p></div>

  <h3>Run it</h3>
  <ol>
    <li><strong>Practice once yourself first.</strong> It works best with a smooth rim and a flat card.</li>
    <li>Your child fills the cup to the very top and lays the card flat on it.</li>
    <li>Press the card down with a flat palm, flip the cup over quickly above the sink, and hold it upside down.</li>
    <li>Get a prediction out loud: "When I take my hand away, what happens?" Then let go of the card. It stays, and the water stays in.</li>
    <li>Your child fills in the Lab Report, then tries the "half full" retest. It usually still works, which surprises everyone.</li>
    <li><strong>Straw bonus:</strong> dip a straw in water, put a finger over the top, and lift it out. The water stays in the straw. Lift the finger and it drops out.</li>
  </ol>

  <h3>What's really happening</h3>
  <div class="box science">
    <p>We live at the bottom of an ocean of air. The air above us has weight, and it presses on everything from every direction: up, down, and sideways. That push is <strong>air pressure</strong>. It's about 14.7 pounds on every square inch, but we never notice because it pushes equally on all sides of us.</p>
    <p>Under the upside-down cup, the air in the room pushes <em>up</em> on the card. Pushing <em>down</em> on the card is only the weight of the water, which is much smaller. Nothing from outside can get in to push down from inside the cup, because the card seals the rim. So the upward air push wins, and the card stays. The water's surface tension helps by making a thin seal around the edge. With a half-full cup, the water sags a tiny bit when you let go, which stretches the trapped air. Stretched air pushes less, so the air outside still wins.</p>
    <p>The straw works the same way. With your finger sealing the top, air can only push up from the bottom. Lift your finger, air pushes from the top too, and gravity pulls the water out.</p>
    <p><em>For a 6-year-old:</em> "Air is all around us and it pushes on everything. Under the card, the air's push is stronger than the water's weight." That ties directly to the day's push-and-pull idea.</p>
  </div>

  <h3>Answer key — Lab Report</h3>
  <div class="box answer-box thu">
    <p><strong>I predict:</strong> Any prediction is fine. Most kids say the water will spill. <strong>I observe:</strong> The card stayed on and the water stayed in the cup. <strong>I learned:</strong> The air pushed up on the card (air pressure held it). <strong>Try it again:</strong> Usually yes, it still works half full.</p>
    <p><strong>Reading (vocabulary):</strong> air pressure = the push of the air all around us.</p>
  </div>

  <h3>If it doesn't work</h3>
  <div class="box misconception"><p>The usual culprits: a bendy or curled card, a chipped or uneven rim, or tilting the cup sideways. Use a fresh, flat card, keep the cup level, and try again. A failed run is a great real-science moment: "What changed? Let's fix one thing and retest." That's the fair-test habit from the ramp race.</p></div>

  <h3>Misconceptions to watch</h3>
  <div class="box misconception"><p>"The water is glued to the card," or "the card is sucking the water up." Nothing sucks. The air <em>pushes</em> from below. Kids also tend to think air is "nothing." Reinforce that air is real stuff with weight that can push. A follow-up: squeeze an empty, capped plastic bottle and feel the air push back.</p></div>

  <h3>Go further</h3>
  <div class="box extension"><p><strong>Sideways test:</strong> Once the card holds, carefully turn the cup sideways over the sink. Does it still hold? (Often yes, briefly. Air pushes from every direction, not just up.)</p></div>
</div>

<!-- ===================================================================== -->
<div class="page">
  <h2 class="fri">Friday, part 1 — Cloud in a Jar &nbsp;<span style="font-weight:normal;font-size:10pt;">Water changes form</span></h2>
  <p class="meta">Standards: VA K.4.c (water occurs in different phases), 1.1 (use physical models to demonstrate natural processes). About 15 minutes. Do it first, before the volcano.</p>

  <h3>What you need</h3>
  <div class="box materials"><p>A clear glass jar with a metal lid (a pasta-sauce or mason jar), hot tap water or water heated in a kettle (hot but <em>not</em> boiling), a handful of ice cubes, aerosol hairspray (or one match: grown-up only), black paper behind the jar to make the cloud easier to see. Optional: a flashlight.</p></div>

  <h3>Safety</h3>
  <div class="box safety"><p><strong>A grown-up handles the hot water and the match.</strong> Use hairspray <em>or</em> a match, <strong>never both</strong>: hairspray is flammable. Use a sturdy glass jar. A thin glass can crack with very hot water, so warm the jar with tap water first.</p></div>

  <h3>Run it</h3>
  <ol>
    <li>Put the black paper behind where the jar will stand. Your child reads the ASK on the Lab Report and makes a prediction.</li>
    <li><strong>Grown-up:</strong> pour about 1 inch of hot water into the jar and swirl it to warm the sides.</li>
    <li>Turn the lid upside down (like a little dish) and set it on top of the jar. Your child piles ice cubes in it. Wait about 20 seconds.</li>
    <li>Lift the lid quickly, give one short spray of hairspray into the jar (or drop in a just-blown-out match), and put the iced lid straight back on.</li>
    <li>Watch: a swirling, misty cloud fills the top of the jar within a minute. Shining a flashlight through the side makes it pop.</li>
    <li>After observing, lift the lid. The cloud drifts out, and your child can wave a hand through it. Finish the Lab Report.</li>
  </ol>

  <h3>What's really happening</h3>
  <div class="box science">
    <p>The hot water <strong>evaporates</strong> fast, so the air in the jar fills with invisible water vapor (water as a gas). The ice on the lid chills the air at the top of the jar. Cold air can't hold as much water vapor, so the vapor <strong>condenses</strong>, turning back into tiny drops of liquid water. Each drop is far too small to fall, so they float together as a visible cloud.</p>
    <p>The hairspray (or match smoke) is the secret ingredient. Water vapor needs tiny specks to condense onto, called <strong>condensation nuclei</strong>. Real clouds form on dust, sea salt, pollen, and smoke drifting in the sky. Without specks the jar still fogs a little, but the cloud is much thinner. Try it both ways if your child is curious. That's another fair test!</p>
    <p>Connect it to the ice cube on the plate: <em>ice melting</em> is solid → liquid; the <em>cloud</em> is gas → liquid. Same water, different forms. This is a <strong>model</strong>. It's not the sky, but it works the same way the sky does, which is exactly what scientists use models for.</p>
  </div>

  <h3>Answer key</h3>
  <div class="box answer-box fri">
    <p><strong>Lab Report.</strong> <em>I predict:</em> any prediction. <em>I observe:</em> a cloud/fog/mist swirling at the top of the jar, sometimes water drops on the lid underside. <em>The lid:</em> the cloud floated out of the jar. <em>I learned:</em> a cloud is made of tiny drops of water.</p>
    <p><strong>Friday reading Q4 ("What made the cloud?"):</strong> Both: warm water made water vapor, and the cold ice turned it back into tiny drops.</p>
  </div>

  <h3>Misconceptions to watch</h3>
  <div class="box misconception"><p>"The cloud is smoke," or "it's steam." Visible mist is <em>liquid</em> water drops. The water vapor itself is invisible. The hairspray or smoke is only a tiny helper the drops form on. And clouds aren't "fluffy cotton." Your child just put a hand through one and felt it: a little cool and damp.</p></div>

  <h3>Go further</h3>
  <div class="box extension"><p><strong>Cloud spotting:</strong> On the next cloudy day, go outside and look up. "That's millions of tiny water drops, just like our jar." Or breathe on a cold window or mirror. The fog is your breath's water vapor condensing, a cloud you made yourself.</p></div>
</div>

<!-- ===================================================================== -->
<div class="page">
  <h2 class="fri">Friday, part 2 — Dino Volcano: Fast &amp; Slow Changes &nbsp;<span style="font-weight:normal;font-size:10pt;">Skill: The whole loop</span></h2>
  <p class="meta">Standards: VA K.10.c–d (changes can be observed and measured; fast or slow), K.4.c (water in different phases), 1.1 (full investigation)</p>

  <h3>What you need</h3>
  <div class="box materials"><p>Baking sheet or tray, a small plastic cup, play dough / sand / a crumpled foil mound to build the volcano around the cup, 2 tablespoons baking soda, about ½ cup white vinegar, a squirt of dish soap, a few drops of red or orange food coloring, 1 ice cube on a plate. Optional: a banana to leave out for a few days.</p></div>

  <h3>Run it</h3>
  <ol>
    <li><strong>First:</strong> put the ice cube on a plate and note the time.</li>
    <li>Build the volcano around the cup on the tray. Into the cup: baking soda, dish soap, food coloring.</li>
    <li>Walk the scientist steps out loud. ASK the question. Your child PREDICTS. Then they pour the vinegar (TEST) and you both OBSERVE.</li>
    <li>Do it again! Scoop out the foam, add fresh baking soda, and pour again. Kids love a second eruption.</li>
    <li>Check the ice cube. Compare how long each change took.</li>
    <li>Do the Steps of a Scientist cut-and-order page, then the LET'S DISCUSS retell.</li>
  </ol>

  <h3>What's really happening</h3>
  <div class="box science">
    <p>Baking soda (sodium bicarbonate, a base) and vinegar (acetic acid) react together. Their molecules rearrange into new substances: water, sodium acetate, and <strong>carbon dioxide gas</strong>. The gas forms bubbles, the dish soap traps them into a thick foam, and the foam overflows. That's the "lava." This is a <strong>chemical change</strong>. New stuff is made and you can't get the baking soda back. It's also a <strong>fast change</strong>, taking seconds.</p>
    <p>The ice cube melting is a <strong>physical change</strong>, from solid water to liquid water (a change of phase). It's still water, and you can freeze it again. It's also a <strong>slower change</strong>, taking minutes. The banana going brown over days is slower still. For K–1 the standard focuses on <em>fast vs. slow</em> and on <em>observing and measuring</em> change. "Can you undo it?" is a bonus idea, so introduce it lightly.</p>
    <p>The capstone point: your child used every skill from the week in one experiment. Ask a question, predict, test, observe, record, conclude.</p>
  </div>

  <h3>Answer key</h3>
  <div class="box answer-box fri">
    <p><strong>Steps of a Scientist (correct order):</strong> 1 ASK → 2 PREDICT → 3 TEST → 4 OBSERVE → 5 RECORD → 6 CONCLUDE. <em>(Observe and record sometimes swap in real life. Accept 4/5 in either order if your child can explain why.)</em></p>
    <p><strong>Q1:</strong> Personal answer. <strong>Q2:</strong> Fizz = fast change. Ice melting = slow change. <strong>Q3:</strong> Yes, you can freeze the water back into ice. No, you can't turn the fizz back into baking soda.</p>
  </div>

  <h3>LET'S DISCUSS guidance</h3>
  <div class="box discuss"><p><em>"I predicted… I observed… I learned…"</em> This is a spoken retell of any experiment from the week. It's the best single check of whether the scientist loop stuck. Prompt gently if a step goes missing ("What did you think would happen first?"). If your child is excited, let them teach a sibling or grandparent the whole experiment.</p></div>

  <h3>Misconceptions to watch</h3>
  <div class="box misconception"><p>"The bubbles are air," or "the volcano is boiling." The bubbles are a <em>new</em> gas (carbon dioxide) made by the reaction, and the foam isn't hot. Let your child touch the cooled foam to check. Real volcanoes erupt molten rock, so it's fine to say our volcano is a <em>model</em>: it looks like an eruption, but it works differently.</p></div>

  <h3>Go further</h3>
  <div class="box extension"><p><strong>Balloon blow-up:</strong> Pour ½ cup vinegar into an empty plastic bottle. Use a funnel or folded paper to put 2 tablespoons of baking soda inside a balloon. Stretch the balloon over the bottle's mouth, then lift it so the soda drops in. The gas you made inflates the balloon. That proves the bubbles really are a gas taking up space.</p></div>

</div>

</body>
</html>"""

    guide_path = output_dir / "kitchen_science_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print("\nSuccessfully generated Kitchen Science Week.")
    print(f"Student packet:          {out_path}")
    print(f"Parent experiment guide: {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Mon p1 — Reading: Sink or Float? (meet Professor Rex)",
        "Mon p2 — Feature Matrix: Predict, Then Test",
        "Tue p1 — Reading: Light Detectives",
        "Tue p2 — Word Sort: Transparent / Translucent / Opaque",
        "Wed p1 — Reading: Good Vibrations",
        "Wed p2 — Cause and Effect: Vibrations and Sound",
        "Thu p1 — Reading: Push, Pull, Zoom!",
        "Thu p2 — T-Chart: Ramp Test Data",
        "Thu p3 — Lab Report: The Magic Cup (air pressure)",
        "Fri p1 — Reading: Dino Volcano — Fast and Slow Changes (Capstone)",
        "Fri p2 — Lab Report: Cloud in a Jar",
        "Fri p3 — Sequencing: Steps of a Scientist",
        "         — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")


if __name__ == "__main__":
    generate_kitchen_science_week_series()
