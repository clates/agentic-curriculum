"""
Body Team — Week Series: "Rudy's Rounds"
Grade 2–3 content for an advanced K–1 reader | Science (life science: human body) |
Causal Arc: Lungs load oxygen into the blood → the heart pumps that blood everywhere →
            the gut loads food fuel into the same blood → the liver and kidneys clean it →
            the brain coaches the whole team (capstone: what every organ does in one sprint)

Narrator: Rudy the Red Blood Cell, introduced on Monday. A tiny living cell who thinks of himself
as a delivery truck: he hauls oxygen from the lungs to every part of the body, riding the
"blood river" that also carries food fuel and trash. Each day he visits the next organ on his route.

Day shape (~2 hours): reading + Words to Know + a demo (~1 hour), then the application sheet and
the hands-on / outdoor activity in each reading's instructions (~1 hour).

Standards (Virginia SOL, verified against curriculum.db). Note: Virginia's K–3 science standards
have no human organ-systems standard; the week anchors to 1.1.5 (animals, including humans, have
structures that perform specific functions) and teaches it at 2nd–3rd grade depth.
  Monday    — VA.SCIENCE.1.1.5.a, 1.1.5.b, VA.SCIENCE.2.2.1 (models: bottle lung)
  Tuesday   — VA.SCIENCE.1.1.5.b, VA.SCIENCE.3.3.1 (measure, record, graph data),
              VA.MATH.2.2.15 (bar graphs)
  Wednesday — VA.SCIENCE.1.1.5.a, 1.1.5.b, VA.SCIENCE.2.2.1 (measure length; models)
  Thursday  — VA.SCIENCE.1.1.5.a, 1.1.5.b, VA.SCIENCE.3.3.1 (models: filter demo)
  Friday    — VA.SCIENCE.K.k.5.a (senses correspond to body structures), 1.1.5.b,
              VA.SCIENCE.3.3.1 (data, conclusions), VA.MATH.2.2.15 (capstone)

Output: body_week_series/
  body_week.html                (student packet)
  body_week_teacher_guide.html  (materials, answer keys, discussion guidance, misconceptions)
  body_explorer.html            (interactive pan-and-zoom body, one animated scene per day;
                                 built by scripts/body_week_explorer.py)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("scripts"))

from body_week_explorer import build_html as build_explorer_html
from worksheet_html_renderer import build_print_packet_html, render_worksheet_html

# Seeds every shuffle (vocabulary, matching, sequencing, word banks), so the packet and the
# answer keys are reproducible run to run.
random.seed(20261116)


def shuffled(items: list) -> list:
    out = list(items)
    random.shuffle(out)
    return out


def generate_body_week_series():
    output_dir = Path("body_week_series")
    output_dir.mkdir(exist_ok=True)
    pages: list[tuple[str, str]] = []

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — Meet Rudy: the Lungs load the oxygen
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: Meet Rudy — Breathe In!",
            "passage_title": "Rudy's First Pickup",
            "instructions": (
                "Before reading: Sit very still while a grown-up times 1 minute. Count every "
                "breath you take (in AND out counts as one). Write the number in the margin.\n\n"
                "During reading: Put one hand on your belly and one on your chest. Breathe in "
                "slowly. Which hand moves more?\n\n"
                "After reading: Build a bottle lung with a grown-up (see the Teacher Guide). Then "
                "go outside, race to the far end of the yard and back, and count your breaths for "
                "1 minute again. Did the number change?"
            ),
            "passage": (
                "Hi there! I'm Rudy the Red Blood Cell. I'm a cell — one of the tiny living "
                "building blocks your whole body is made of. You have trillions of cells, and "
                "I'm one of the hardest workers. I'm so small that thousands of me could fit on "
                "the period at the end of this sentence.\n\n"
                "I think of myself as a delivery truck. My cargo is OXYGEN, a gas in the air that "
                "every cell in your body needs to stay alive. I ride in a river called BLOOD, "
                "which flows through tubes all over your body. This week you'll ride along with "
                "me on my rounds. Every stop is an ORGAN: a body part made of many cells that do "
                "one big job together. Organs work as a team, like players on a football team.\n\n"
                "My first stop is always the LUNGS, where I load up. You have two lungs in your "
                "chest. They feel like soft sponges. Your left lung is a little smaller than your "
                "right one, to leave room for your heart.\n\n"
                "Here's how the air gets to me. Under your lungs is a strong, flat muscle called "
                "the DIAPHRAGM. When it pulls down, it makes room in your chest, and air rushes in "
                "through your nose or mouth. The air zooms down your WINDPIPE, which splits into "
                "smaller and smaller tubes, like the branches of an upside-down tree. At the very "
                "ends are millions of tiny AIR SACS that look like bunches of grapes.\n\n"
                "That's where I'm parked! The walls of the air sacs are so thin that oxygen slips "
                "right through them and onto me. At the same time, I drop off a waste gas called "
                "CARBON DIOXIDE that the cells made. When your diaphragm relaxes, the air "
                "carrying that carbon dioxide gets pushed back out. Breathe in: load oxygen. "
                "Breathe out: dump the trash. You do it about 20 times a minute, even while you "
                "sleep!\n\n"
                "My truck is full. Now I need something to push me all over your body. "
                "Tomorrow, you'll meet the strongest pump you own."
            ),
            "vocabulary": shuffled(
                [
                    {
                        "term": "cell",
                        "definition": "A tiny living building block. Your body is made of "
                        "trillions of them.",
                    },
                    {
                        "term": "organ",
                        "definition": "A body part made of many cells that do one big job "
                        "together, like the lungs or the heart.",
                    },
                    {
                        "term": "oxygen",
                        "definition": "A gas in the air that every cell needs to stay alive.",
                    },
                    {
                        "term": "carbon dioxide",
                        "definition": "A waste gas your cells make. You breathe it out.",
                    },
                    {
                        "term": "diaphragm",
                        "definition": "The flat muscle under your lungs. When it pulls down, air "
                        "rushes in.",
                    },
                    {
                        "term": "air sacs",
                        "definition": "Millions of tiny bubbles at the ends of the lung tubes, "
                        "where oxygen moves into the blood.",
                    },
                    {
                        "term": "windpipe",
                        "definition": "The tube that carries air from your throat down to your "
                        "lungs.",
                    },
                ]
            ),
            "questions": [
                {"prompt": "What gas does Rudy pick up in the lungs?", "response_lines": 1},
                {
                    "prompt": "What muscle pulls down to make air rush into your lungs?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Why is your left lung a little smaller than your right one?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Did you take more breaths after racing across the yard? Why do "
                    "you think so?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: Fish need oxygen too, but they don't have lungs "
                    "and they live underwater. Where do you think a fish gets its oxygen?",
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    mon_chain = [
        (
            "Your diaphragm pulls down and makes more room in your chest.",
            "Air rushes in through your nose or mouth and fills your lungs.",
        ),
        (
            "Fresh air reaches the tiny air sacs at the ends of the lung tubes.",
            "Oxygen slips through the thin walls and onto Rudy in the blood.",
        ),
        (
            "Rudy drops off carbon dioxide in the air sacs.",
            "You breathe the carbon dioxide out.",
        ),
        (
            "You race across the yard, so your muscles need more oxygen.",
            "You breathe faster and deeper.",
        ),
        (
            "Dust floats into your nose.",
            "Nose hairs and sticky mucus trap it, or you sneeze it out.",
        ),
    ]
    add(
        "causeEffectWorksheet",
        {
            "title": "Monday: The Breathing Chain",
            "instructions": (
                "Each box on the left is a CAUSE: something that happens. Write the EFFECT: "
                "what happens next because of it. Use your bottle lung to check your thinking!"
            ),
            "pairs": [{"cause": c, "effect_lines": 1} for c, _ in mon_chain],
        },
        "Monday",
    )

    # =========================================================================
    # TUESDAY — The Heart: the pump that moves Rudy
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: The Pump",
            "passage_title": "Rudy Rides the Heart",
            "instructions": (
                "Before reading: Squeeze a tennis ball as hard as you can, then let go. Do it "
                "again and again for 10 seconds. That's about how hard your heart squeezes, every "
                "second of every day.\n\n"
                "During reading: Find your pulse. Press two fingers (not your thumb) on the inside "
                "of your wrist, below your thumb, or on the side of your neck. Feel the bumps?\n\n"
                "After reading: Make a stethoscope from a paper-towel tube. Press one end gently "
                "on a grown-up's chest, a little left of the middle, and put your ear to the "
                "other end. Listen for 'lub-dub!' Then do the Pulse Lab."
            ),
            "passage": (
                "Rudy here, loaded with oxygen from the lungs! But a delivery truck needs an "
                "engine. Mine is your HEART.\n\n"
                "Your heart is a muscle about the size of your fist. It sits in the middle of your "
                "chest, tipped a little to the left. Every time it squeezes, it shoves blood out "
                "into tubes. That squeeze is one HEARTBEAT. A kid's heart beats about 90 times a "
                "minute when resting, and it never takes a day off.\n\n"
                "Inside, your heart has four rooms called CHAMBERS. It's really two pumps side by "
                "side. The right side sends me to the lungs to load oxygen. Then I come back, and "
                "the left side — the strongest part — blasts me out to the whole body.\n\n"
                "Between the rooms are VALVES, little one-way doors that keep blood from sloshing "
                "backward. When the doors snap shut, they make the sound doctors listen for: "
                "lub-dub, lub-dub.\n\n"
                "I travel through three kinds of tubes called blood vessels. ARTERIES carry me "
                "away from the heart. VEINS bring me back. In between are CAPILLARIES, so skinny "
                "that red blood cells like me have to go through in single file! That's where I "
                "hand my oxygen to the hungry cells. If you laid all of a grown-up's blood vessels "
                "end to end, they would wrap around the whole Earth more than twice.\n\n"
                "The push you felt in your wrist is your PULSE. It's the bump of blood in an "
                "artery each time your heart squeezes. When you run, your muscles need more "
                "oxygen, so your heart speeds up to deliver me faster, and you breathe faster "
                "to load me faster. The lungs and heart are teammates!\n\n"
                "One more thing: blood is always red, even in your veins. Veins only look blue "
                "through your skin. Tomorrow I'll pick up a different kind of cargo: food!"
            ),
            "vocabulary": shuffled(
                [
                    {
                        "term": "heart",
                        "definition": "A muscle about the size of your fist that pumps blood "
                        "all over your body.",
                    },
                    {
                        "term": "heartbeat",
                        "definition": "One squeeze of the heart.",
                    },
                    {
                        "term": "chamber",
                        "definition": "One of the four rooms inside the heart.",
                    },
                    {
                        "term": "valve",
                        "definition": "A one-way door inside the heart. Closing valves make "
                        "the 'lub-dub' sound.",
                    },
                    {
                        "term": "artery",
                        "definition": "A blood vessel that carries blood AWAY from the heart.",
                    },
                    {
                        "term": "vein",
                        "definition": "A blood vessel that carries blood BACK to the heart.",
                    },
                    {
                        "term": "pulse",
                        "definition": "The bump you feel in an artery each time your heart "
                        "beats.",
                    },
                ]
            ),
            "questions": [
                {"prompt": "About how big is your heart?", "response_lines": 1},
                {
                    "prompt": "Which side of the heart sends Rudy out to the whole body?",
                    "response_lines": 1,
                },
                {"prompt": "What makes the 'lub-dub' sound?", "response_lines": 1},
                {
                    "prompt": "Arteries carry blood ________ the heart. Veins carry blood "
                    "________ to the heart.",
                    "response_lines": 1,
                },
                {
                    "prompt": "LET'S DISCUSS: When you run, your heart beats faster AND you "
                    "breathe faster. Why do both speed up at the same time?",
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    tue_conditions = [
        "Sitting still",
        "After 30 jumping jacks",
        "After resting 2 minutes",
        "Lying down",
    ]
    add(
        "barGraphWorksheet",
        {
            "title": "Tuesday: Pulse Lab",
            "instructions": (
                "Find your pulse. A grown-up says 'GO' and 'STOP' after 15 seconds while you "
                "count the bumps. Do it four times, in this order: sitting still, right after 30 "
                "jumping jacks, after resting 2 minutes, and lying down. Color one bar for each. "
                "Before you start, PREDICT which bar will be tallest."
            ),
            "categories": tue_conditions,
            "y_max": 50,
            "y_step": 5,
            "x_label": "What I was doing",
            "y_label": "Heartbeats in 15 seconds",
            "height_in": 3.2,
            "questions": [
                {"prompt": "My prediction: the tallest bar will be ________________"},
                {"prompt": "Which bar was tallest? Why did your heart beat faster then?"},
                {"prompt": "Did your heart slow back down after resting 2 minutes?"},
                {"prompt": "Every number needs a unit. Your bars measure heartbeats in ______."},
            ],
        },
        "Tuesday",
    )

    # =========================================================================
    # WEDNESDAY — Stomach & intestines: loading food fuel into the blood
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: The Fuel Factory",
            "passage_title": "Down the Food Tube",
            "instructions": (
                "Before reading: Chew one plain cracker 30 times without swallowing. Does it "
                "start to taste a little sweet? Saliva is already breaking it down!\n\n"
                "During reading: Put your fingers lightly on your throat and swallow. Feel the "
                "squeeze go down?\n\n"
                "After reading: Make a zip-bag stomach with a grown-up (see the Teacher Guide). "
                "Then go outside with a tape measure and a long string. Measure out 20 feet and "
                "stretch it across the yard: that's how long a grown-up's small intestine is!"
            ),
            "passage": (
                "Rudy reporting! My job is hauling oxygen. But your cells need another delivery "
                "too: FUEL, made from the food you eat. Fuel doesn't ride on me. It floats in the "
                "blood river all around me. Today we'll see how food gets turned into fuel. "
                "This is called DIGESTION, and it's a long trip.\n\n"
                "Stop 1 is your MOUTH. Your teeth chop food into tiny bits. SALIVA (spit) makes "
                "it soft and starts breaking it down. That's why a cracker tastes sweet if you "
                "chew it long enough!\n\n"
                "Stop 2 is the ESOPHAGUS, a stretchy tube from your throat to your stomach. Its "
                "walls squeeze the food down in waves, like toothpaste moving through a tube. It "
                "squeezes so well that astronauts can eat floating upside down in space.\n\n"
                "Stop 3 is the STOMACH, a stretchy, muscly bag. It mixes food with strong acid "
                "and churns it for a few hours until it turns into a thick soup. A slimy lining "
                "keeps the acid from hurting the stomach itself.\n\n"
                "Stop 4 is the most important one for me: the SMALL INTESTINE. It's a skinny "
                "tube all coiled up in your belly. A grown-up's is about 20 feet long! Its inside "
                "is covered with millions of tiny fingers called VILLI. They soak up the "
                "NUTRIENTS — the useful parts of food — and pass them into the blood river. "
                "That's the fuel pickup! The blood carries it to every cell.\n\n"
                "Stop 5 is the LARGE INTESTINE. It's shorter but wider. It soaks up most of "
                "the leftover water. What's left over is waste, and it leaves your body when "
                "you go to the bathroom.\n\n"
                "Now the blood river is full of fuel. But it's also picking up trash from the "
                "cells. Tomorrow, meet the clean-up crew!"
            ),
            "vocabulary": shuffled(
                [
                    {
                        "term": "digestion",
                        "definition": "Breaking food down into nutrients the body can use.",
                    },
                    {
                        "term": "saliva",
                        "definition": "Spit. It makes food soft and starts breaking it down.",
                    },
                    {
                        "term": "esophagus",
                        "definition": "The squeezing tube that carries food from your throat "
                        "to your stomach.",
                    },
                    {
                        "term": "stomach",
                        "definition": "A stretchy, muscly bag that churns food with acid into "
                        "a thick soup.",
                    },
                    {
                        "term": "small intestine",
                        "definition": "A long, coiled tube where nutrients soak into the " "blood.",
                    },
                    {
                        "term": "large intestine",
                        "definition": "A shorter, wider tube that soaks up leftover water.",
                    },
                    {
                        "term": "nutrients",
                        "definition": "The useful parts of food that give cells fuel and help "
                        "you grow.",
                    },
                ]
            ),
            "questions": [
                {
                    "prompt": "Name two things that happen to food in your mouth.",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which tube squeezes food down to your stomach?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Where do most nutrients soak into the blood?",
                    "response_lines": 1,
                },
                {
                    "prompt": "What does the large intestine soak up?",
                    "response_lines": 1,
                },
                {
                    "prompt": "LET'S DISCUSS: Astronauts eat while floating upside down. How "
                    "does their food still get to their stomachs?",
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    wed_journey = [
        "Teeth chop the food into tiny bits.",
        "Saliva makes the food soft and starts breaking it down.",
        "The esophagus squeezes the food down to the stomach.",
        "The stomach churns the food with acid into a thick soup.",
        "Villi in the small intestine soak nutrients into the blood.",
        "The large intestine soaks up the leftover water.",
        "Waste leaves the body when you go to the bathroom.",
    ]
    wed_steps = shuffled(
        [{"text": text, "correct_order": i} for i, text in enumerate(wed_journey, 1)]
    )
    add(
        "sequencingWorksheet",
        {
            "title": "Wednesday: The Food's Journey",
            "activity_name": "Digestion",
            "instructions": (
                "These steps got mixed up! Write 1 in the box for what happens first, 2 for what "
                "happens next, all the way to 7. Then point to where each step happens on your "
                "own body."
            ),
            "steps": wed_steps,
        },
        "Wednesday",
    )

    # =========================================================================
    # THURSDAY — Liver & kidneys: the clean-up crew
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: The Clean-Up Crew",
            "passage_title": "Rudy Goes Through the Car Wash",
            "instructions": (
                "Before reading: Drink a full glass of water. Your clean-up crew needs water to "
                "wash the trash away.\n\n"
                "During reading: Find your organs! Put your right hand on your right side, just "
                "under your ribs: that's your liver. Put both hands on your back, just above "
                "your waist: your kidneys are right under them.\n\n"
                "After reading: Do the filter demo with a grown-up (see the Teacher Guide). "
                "Pour muddy, glittery water through a coffee filter. What gets through? What "
                "gets stuck?"
            ),
            "passage": (
                "Rudy here, and I'm on a dirty stretch of road. Your cells take the oxygen and "
                "fuel we deliver, and they make trash called WASTE, just like a kitchen does "
                "when you cook. The waste goes into the blood river. If nobody cleaned it out, "
                "you would get very sick. Time for the clean-up crew!\n\n"
                "First up is your LIVER, the biggest organ inside your body. It sits on your "
                "right side, tucked under your ribs, and it's about the size of a football. The "
                "liver has hundreds of jobs. It pulls harmful stuff out of the blood and makes "
                "it safe. It stores extra fuel to use later. It even makes a green juice called "
                "BILE that helps your small intestine break down fatty foods, like butter. And "
                "here's something amazing: if part of a liver is removed, it can grow back!\n\n"
                "Next are your two KIDNEYS. Each one is shaped like a bean and is about the size "
                "of your fist. They sit in your back, one on each side of your spine. The kidneys "
                "are FILTERS. As I float through, they keep the good stuff in the blood — like me! "
                "— and pull out waste and extra water. That makes URINE, which is the scientific "
                "name for pee.\n\n"
                "A grown-up's kidneys push about a bathtub full of liquid through their filters "
                "every day. But they are choosy: they send almost all of it back into the blood, "
                "and only a little becomes urine. The urine drips down two thin tubes into the "
                "BLADDER, a stretchy bag that holds it until you go to the bathroom.\n\n"
                "Here's a body clue: pale yellow pee means you're drinking plenty of water. "
                "Dark yellow pee means your crew could use more!\n\n"
                "Clean blood, full of oxygen and fuel. My team is working great. But who's in "
                "charge of all of us? Tomorrow, meet the Head Coach."
            ),
            "vocabulary": shuffled(
                [
                    {
                        "term": "waste",
                        "definition": "Trash your cells make. The blood carries it away.",
                    },
                    {
                        "term": "liver",
                        "definition": "The biggest organ inside your body. It cleans the blood, "
                        "stores fuel, and makes bile.",
                    },
                    {
                        "term": "bile",
                        "definition": "A green juice from the liver that helps break down fatty "
                        "food.",
                    },
                    {
                        "term": "kidney",
                        "definition": "One of two bean-shaped filters in your back that take "
                        "waste and extra water out of the blood.",
                    },
                    {
                        "term": "filter",
                        "definition": "Something that lets some things through and stops "
                        "others.",
                    },
                    {
                        "term": "urine",
                        "definition": "Waste and extra water the kidneys take out of the blood. "
                        "Also called pee.",
                    },
                    {
                        "term": "bladder",
                        "definition": "A stretchy bag that holds urine until you go to the "
                        "bathroom.",
                    },
                ]
            ),
            "questions": [
                {
                    "prompt": "What is the biggest organ inside your body?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Name one job the liver does.",
                    "response_lines": 1,
                },
                {
                    "prompt": "What do the kidneys take out of the blood?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Where does urine wait until you go to the bathroom?",
                    "response_lines": 1,
                },
                {
                    "prompt": "LET'S DISCUSS: The coffee filter let water AND tiny bits of "
                    "dirt through. Real kidneys keep good things, like Rudy, in the blood. What "
                    "would happen if your kidneys let all the red blood cells slip out?",
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    thu_jobs = [
        ("Lungs", "load oxygen into the blood"),
        ("Diaphragm", "pulls down so air rushes in"),
        ("Heart", "pumps blood all over the body"),
        ("Stomach", "churns food into a thick soup"),
        ("Small intestine", "soaks nutrients into the blood"),
        ("Liver", "cleans the blood and makes bile"),
        ("Kidneys", "filter waste out to make urine"),
        ("Bladder", "holds urine until bathroom time"),
    ]
    thu_right = shuffled([job for _, job in thu_jobs])
    add(
        "matchingWorksheet",
        {
            "title": "Thursday: Who Does This Job?",
            "instructions": (
                "Rudy's whole team so far! Draw a line from each organ to its job. Then tell a "
                "grown-up which organ Rudy visits FIRST on every trip, and why."
            ),
            "left_items": [organ for organ, _ in thu_jobs],
            "right_items": thu_right,
        },
        "Thursday",
    )

    # =========================================================================
    # FRIDAY — The Brain: Head Coach (capstone)
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: The Head Coach",
            "passage_title": "Rudy's Favorite Stop",
            "instructions": (
                "Before reading: Do the Ruler Drop (see the Reaction Lab page). How fast can "
                "your brain tell your fingers to grab?\n\n"
                "During reading: Every time Rudy names a sense, point to the body part that "
                "does it.\n\n"
                "After reading: Go outside. Sprint as fast as you can for 20 seconds, then "
                "stop. Feel your breathing and your pulse. Can you name every teammate that "
                "just went to work?"
            ),
            "passage": (
                "Rudy here, on my favorite delivery of all: your BRAIN. It's only about the "
                "size of two fists, but it uses about one fifth of all the oxygen I carry. That's "
                "because it never stops working. The brain is the Head Coach of your body team.\n\n"
                "Your brain is soft, so it's protected by your SKULL, a hard bone helmet. A long "
                "bundle of NERVES called the SPINAL CORD runs from your brain down your back, "
                "inside your backbone. Nerves branch out from it to every part of you, like "
                "radio wires on a football team. Messages zip along them faster than a race "
                "car.\n\n"
                "Some messages come IN. Your SENSES send them: your eyes see, your ears hear, "
                "your nose smells, your tongue tastes, and your skin feels. Other messages go "
                "OUT, telling your muscles to move. When you catch a ball, your eyes send 'Ball "
                "coming!' to the brain, and the brain sends 'Close your hands!' to your fingers, "
                "all in a blink.\n\n"
                "Some plays you call yourself, like kicking a ball. But the brain also runs "
                "plays without asking you. The bottom part, called the BRAIN STEM, keeps your "
                "diaphragm breathing and your heart beating, even while you sleep. And some "
                "super-fast moves called REFLEXES happen before you even think, like jerking "
                "your hand away from something hot.\n\n"
                "Now watch the whole team on one play. You sprint for a touchdown. Your brain "
                "tells your legs to run. Your leg muscles burn through oxygen and fuel. Your "
                "brain speeds up your breathing, so your lungs load me faster, and speeds up "
                "your heart, so I race around faster. The fuel your gut packed into the blood "
                "this morning keeps your muscles going. Your liver and kidneys keep cleaning "
                "up the extra waste. Touchdown!\n\n"
                "That's my route: lungs, heart, out to the body, and back again, about once "
                "every minute, all day and all night. Thanks for riding along, teammate!"
            ),
            "vocabulary": shuffled(
                [
                    {
                        "term": "brain",
                        "definition": "The Head Coach. It gets messages from the senses and "
                        "tells the body what to do.",
                    },
                    {
                        "term": "skull",
                        "definition": "The hard bone helmet that protects your brain.",
                    },
                    {
                        "term": "nerves",
                        "definition": "Thin wires that carry messages between the brain and "
                        "the body.",
                    },
                    {
                        "term": "spinal cord",
                        "definition": "A thick bundle of nerves that runs down your back, "
                        "inside your backbone.",
                    },
                    {
                        "term": "senses",
                        "definition": "Seeing, hearing, smelling, tasting, and touching. They "
                        "send messages to the brain.",
                    },
                    {
                        "term": "brain stem",
                        "definition": "The bottom part of the brain. It keeps you breathing "
                        "and your heart beating.",
                    },
                    {
                        "term": "reflex",
                        "definition": "A super-fast move your body makes before you even "
                        "think, like pulling away from something hot.",
                    },
                ]
            ),
            "questions": [
                {"prompt": "What protects your brain?", "response_lines": 1},
                {
                    "prompt": "What carries messages between your brain and your body?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Name two jobs your brain does without you even thinking about "
                    "them.",
                    "response_lines": 1,
                },
                {
                    "prompt": "LET'S DISCUSS: You can hold your breath for a little while, but "
                    "never forever. Who wins in the end, you or your brain stem? Why is that a "
                    "good thing?",
                    "response_lines": 0,
                },
            ],
        },
        "Friday",
    )

    fri_tries = ["Try 1", "Try 2", "Try 3", "Other hand"]
    add(
        "barGraphWorksheet",
        {
            "title": "Friday: Reaction Lab — The Ruler Drop",
            "instructions": (
                "A grown-up holds a ruler by the top end so the 0 end hangs between your thumb "
                "and finger (not touching). Without warning, they let go. Catch it as fast as "
                "you can! Read the number right above your fingers. That's how far the ruler fell "
                "before your brain made your fingers grab. Do 3 tries, then try with your other "
                "hand. Color a bar for each. SHORTER bars mean a FASTER brain!"
            ),
            "categories": fri_tries,
            "y_max": 30,
            "y_step": 5,
            "x_label": "Which try",
            "y_label": "How far the ruler fell (centimeters)",
            "height_in": 3.0,
            "questions": [
                {"prompt": "Which try was fastest? (Look for the SHORTEST bar.)"},
                {"prompt": "Did you get faster with practice? How can you tell?"},
                {"prompt": "Which sense told your brain the ruler was falling?"},
                {
                    "prompt": "Your best catch: ______ centimeters. (Remember: every number "
                    "needs a unit!)"
                },
            ],
        },
        "Friday",
    )

    fri_crews = [
        ("Air Crew", ["lungs", "diaphragm", "windpipe"]),
        ("Pump Crew", ["heart", "arteries", "veins"]),
        ("Fuel Crew", ["stomach", "esophagus", "small intestine"]),
        ("Clean-Up Crew", ["liver", "kidneys", "bladder"]),
        ("Coaching Staff", ["brain", "nerves", "spinal cord"]),
    ]
    add(
        "treeMapWorksheet",
        {
            "title": "Friday: Rudy's Body Team",
            "instructions": (
                "Every organ has a spot on the team. Write each word from the word bank under "
                "the crew it belongs to. Each crew gets three. Then tell a grown-up what each "
                "crew does for Rudy."
            ),
            "root_label": "Rudy's Body Team",
            "branches": [{"name": crew, "blank_count": 3} for crew, _ in fri_crews],
            "columns": 3,
            "word_bank": shuffled([word for _, words in fri_crews for word in words]),
        },
        "Friday",
    )

    # Each [answer] becomes a numbered gap; the answers dict is built from the same text.
    fri_route_text = (
        "My name is Rudy, and I am a red blood [cell]. I start my trip in the [lungs], "
        "where I load up on [oxygen]. Then the [heart] squeezes and pumps me out through "
        "the [arteries]. I drop off oxygen to cells all over the body.\n"
        "The blood river I ride in also carries fuel. Food gets broken down in the "
        "[stomach], and the nutrients soak into the blood in the [small intestine].\n"
        "Cells make waste, so the [liver] and the [kidneys] clean the blood. The whole time, "
        "the [brain] is the Head Coach, telling my teammates what to do. Then I ride the "
        "[veins] back to the heart and start again!"
    )
    fri_segments: list[dict] = []
    fri_answers: dict[str, str] = {}
    for p_i, para in enumerate(fri_route_text.split("\n")):
        if p_i:
            fri_segments.append({"newline": True})
        for piece in re.split(r"(\[[^\]]+\])", para):
            if piece.startswith("["):
                gap = len(fri_answers) + 1
                fri_answers[str(gap)] = piece[1:-1]
                fri_segments.append({"gap": gap})
            elif piece:
                fri_segments.append({"text": piece})
    add(
        "fillInBlankWorksheet",
        {
            "title": "Friday: Rudy's Whole Route (Capstone)",
            "instructions": (
                "Rudy is telling the story of his whole trip. Fill in each blank with a word from "
                "the word bank. Every word is used once."
            ),
            "segments": fri_segments,
            "answers": fri_answers,
            "word_bank": list(fri_answers.values()),
        },
        "Friday",
    )

    # =========================================================================
    # PARENT FEEDBACK & TEACHING NOTES
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "End-of-Week Parent Feedback — Body Team Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this sheet after the week wraps up. Your notes shape next week's "
                "lessons."
            ),
            "passage": (
                "This week followed one red blood cell, Rudy, around the body. Each organ was "
                "taught as a stop on his route, so every day built on the last one:\n\n"
                "MONDAY — Lungs: oxygen loads into the blood in the air sacs; the diaphragm "
                "drives breathing. TUESDAY — Heart: a two-sided pump; arteries, veins and "
                "capillaries; pulse rises with exercise (Pulse Lab bar graph). WEDNESDAY — "
                "Digestion: mouth to large intestine; nutrients soak into the blood in the small "
                "intestine. THURSDAY — Liver and kidneys clean the blood; urine and the bladder. "
                "FRIDAY — The brain coaches the team through nerves and the spinal cord; senses "
                "in, muscle commands out; automatic jobs like breathing and heartbeat.\n\n"
                "KEY IDEAS to check: 1) Blood is a delivery system — oxygen from the lungs, fuel "
                "from the gut. 2) Organs work as a team; exercise changes several at once. "
                "3) Each organ's shape fits its job (thin air sacs, one-way valves, long "
                "intestine, filtering kidneys).\n\n"
                "COMMON MISCONCEPTIONS: blood in veins is blue; we breathe in oxygen and breathe "
                "out 'nothing'; the stomach does all of digestion; the heart is on the far left "
                "of the chest."
            ),
            "questions": [
                {
                    "prompt": "Overall grasp of the week (1 = struggled, 5 = strong):",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which organ or demo sparked the most questions or excitement?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Could he explain Rudy's route from lungs to heart to body and "
                    "back without help?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Pulse Lab and Ruler Drop: did he label numbers with units "
                    "(beats, centimeters) on his own?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Body topics to explore next (bones and muscles? skin? germs and "
                    "the immune system?):",
                    "response_lines": 2,
                },
            ],
        },
        "Friday",
    )

    html = build_print_packet_html(pages, packet_title="Body Team Week — Rudy's Rounds")
    out_path = output_dir / "body_week.html"
    out_path.write_text(html, encoding="utf-8")

    # =========================================================================
    # Teacher guide — keys are computed from the same data the pages use
    # =========================================================================

    def li(items: list[str]) -> str:
        return "".join(f"<li>{x}</li>" for x in items)

    keys = {
        "MON_CHAIN": li(f"{c} &rarr; <strong>{e}</strong>" for c, e in mon_chain),
        "WED_SEQ": li(
            f"Box with &ldquo;{s['text']}&rdquo; &rarr; <strong>{s['correct_order']}</strong>"
            for s in wed_steps
        ),
        "THU_MATCH": li(
            f"{organ} &rarr; &ldquo;{job}&rdquo; (right-hand item {thu_right.index(job) + 1})"
            for organ, job in thu_jobs
        ),
        "FRI_TREE": li(f"<strong>{crew}:</strong> {', '.join(words)}" for crew, words in fri_crews),
        "FRI_ROUTE": li(f"({gap}) {word}" for gap, word in fri_answers.items()),
    }

    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Body Team Week — Teacher Guide</title>
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
    ul, ol { padding-left: 18px; margin-bottom: 8px; }
    .answer-box { background: #f0f4ff; border-left: 4px solid #1d4ed8; padding: 6px 10px; margin: 4px 0 10px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .answer-box.tue { background: #f0fff4; border-color: #15803d; }
    .answer-box.wed { background: #f5f0ff; border-color: #7c3aed; }
    .answer-box.thu { background: #fff7f0; border-color: #c2410c; }
    .answer-box.fri { background: #f0fff8; border-color: #0f766e; }
    .demo { background: #eef2f7; border-left: 4px solid #475569; padding: 6px 10px; margin: 4px 0 10px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .misconception { background: #fff3cd; border-left: 4px solid #d97706; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .extension { background: #e8f5e9; border-left: 4px solid #15803d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .discuss { background: #fce7f3; border-left: 4px solid #9d174d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
  </style>
</head>
<body>

<div class="page">
  <h1>Body Team Week &mdash; Teacher / Parent Guide</h1>
  <p><strong>Narrator:</strong> Rudy the Red Blood Cell, a tiny &ldquo;delivery truck&rdquo; for oxygen</p>
  <p><strong>Causal arc:</strong> Lungs load oxygen &rarr; the heart pumps it everywhere &rarr; the gut loads food fuel &rarr; the liver and kidneys clean the blood &rarr; the brain coaches the whole team</p>
  <p><strong>Standards:</strong> VA.SCIENCE.1.1.5 a&ndash;b (structures perform specific functions; needs for air, food and water), K.k.5.a (senses &harr; body structures), 2.2.1 / 3.3.1 (models, measuring, data), VA.MATH.2.2.15 (bar graphs). Virginia's K&ndash;3 standards have no organ-systems standard, so this week teaches 1.1.5 at 2nd&ndash;3rd grade depth.</p>
  <p><strong>Accuracy note for the parent:</strong> red blood cells carry oxygen (and some carbon dioxide), not food. The passages keep that straight: fuel and waste travel in the blood &ldquo;river&rdquo; Rudy rides in, not on Rudy.</p>
  <p><strong>Interactive companion:</strong> open <code>body_explorer.html</code> (same folder) in any browser or on a tablet. Each day has a button that flies to that day&rsquo;s organ and animates its job; <em>Sprint</em> speeds the heart and lungs together, and Friday has an on-screen Ruler Drop. A good fit for the end of the reading block, after the demo.</p>
  <h3>Materials for the week</h3>
  <ul>
    <li><strong>Mon:</strong> a plastic water bottle (16&ndash;20 oz), 2 balloons, scissors, a rubber band, a timer</li>
    <li><strong>Tue:</strong> a tennis ball, a paper-towel tube, a timer</li>
    <li><strong>Wed:</strong> plain crackers, a zip-top bag, water, a splash of lemon juice or vinegar, an old sock or knee-high, a bowl, about 25 feet of string, a tape measure</li>
    <li><strong>Thu:</strong> a coffee filter, a cup or funnel, a jar of water, a spoonful of dirt, glitter or ground pepper</li>
    <li><strong>Fri:</strong> a 30 cm ruler</li>
  </ul>

  <h2>Monday &mdash; Meet Rudy: Breathe In!</h2>
  <h3>Demo &mdash; Bottle lung</h3>
  <div class="demo">
    <p>Grown-up: cut the bottom off the bottle. Push one balloon into the neck and stretch its mouth over the bottle's opening (that's a lung). Tie a knot in the second balloon, cut off the top third, and stretch the rest over the open bottom (that's the diaphragm). Pull the knot down: the inside balloon inflates. Push up: it deflates. Point out that pulling the diaphragm DOWN makes air rush IN.</p>
  </div>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1:</strong> Oxygen. <strong>Q2:</strong> The diaphragm. <strong>Q3:</strong> To leave room for the heart. <strong>Q4:</strong> Usually yes. Running muscles need more oxygen, so he breathes faster to load Rudy faster. A typical resting rate at age 6 is about 18&ndash;25 breaths a minute.</p>
  </div>
  <h3>Breathing Chain &mdash; Answer Key</h3>
  <div class="answer-box"><ol>{{MON_CHAIN}}</ol><p><em>Accept the idea in his own words.</em></p></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p>Fish use <strong>gills</strong>. Water washes over thin, feathery gills, and oxygen dissolved in the water slips into the fish's blood, just like it slips through the air sacs. Same job, different organ. Whales and dolphins are the twist: they have lungs and must come up to breathe air.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>&ldquo;We breathe in oxygen and breathe out nothing,&rdquo; or &ldquo;the lungs suck in air by themselves.&rdquo; Lungs have no muscle of their own; the diaphragm does the pulling. The bottle lung makes this concrete.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Lung capacity jar: fill a large jar with water, turn it upside down in a sink of water, and slip a bendy straw under it. One big breath out through the straw pushes water out of the jar. Mark the line, then try again after 10 jumping jacks.</p>
  </div>

  <h2 class="tue">Tuesday &mdash; The Pump</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box tue">
    <p><strong>Q1:</strong> About the size of his fist. <strong>Q2:</strong> The left side. <strong>Q3:</strong> The valves (one-way doors) snapping shut. <strong>Q4:</strong> Arteries carry blood <em>away from</em> the heart; veins carry it <em>back</em>.</p>
  </div>
  <h3>Pulse Lab &mdash; What to Expect</h3>
  <div class="answer-box tue">
    <p>Counts vary. A resting 6-year-old's heart beats about 75&ndash;115 times a minute, which is roughly <strong>19&ndash;29 beats in 15 seconds</strong>. After 30 jumping jacks expect a jump of 8&ndash;15 beats; after 2 minutes of rest it should fall most of the way back; lying down is usually the lowest. The tallest bar should be &ldquo;After 30 jumping jacks.&rdquo; Unit question: <strong>beats in 15 seconds</strong> (accept &ldquo;heartbeats&rdquo;).</p>
    <p><em>Tip:</em> the neck pulse (beside the windpipe, under the jaw) is easier for small fingers than the wrist. If he loses count, let him tap the table with each beat while you count.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p>Working muscles need more oxygen. The heart speeds up to <em>deliver</em> Rudy faster, and the lungs speed up to <em>load</em> him faster. If only one sped up, the other would be the bottleneck, like a fast truck waiting at a slow loading dock. This teamwork idea is the spine of the week.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>&ldquo;Blood in veins is blue.&rdquo; Blood is always red: bright red with oxygen, darker red without. Veins look blue because of how light passes through skin. Also, the heart is near the middle of the chest, only tipped left, not far to the side.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Pump race: give him a turkey baster or squeeze bottle and a bowl of water. How many squeezes to move one cup of water to another bowl? A grown-up's heart moves about 5 liters of blood a minute (more than a big soda bottle) with about 70 squeezes.</p>
  </div>
</div>

<div class="page">
  <h2 class="wed">Wednesday &mdash; The Fuel Factory</h2>
  <h3>Demo &mdash; Zip-bag stomach and sock intestine</h3>
  <div class="demo">
    <p>Crumble 3&ndash;4 crackers into a zip-top bag (teeth). Add a few spoonfuls of water (saliva) and a splash of lemon juice or vinegar (stomach acid). Seal and squish for 2 minutes (churning) until it's soup. Over a bowl, snip a bottom corner and squeeze the soup into an old sock (small intestine). Squeeze the sock: liquid seeps through the fabric into the bowl. That's the nutrients soaking out into the blood. The lumpy stuff left in the sock is waste headed for the large intestine.</p>
    <p><strong>String measure:</strong> lay out 20 feet of string (small intestine) and 5 feet (large intestine) in the yard. Have him lie next to it: the small intestine is more than four of him. His own is shorter than a grown-up's but still several times his height.</p>
  </div>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1:</strong> Teeth chop it; saliva makes it soft and starts breaking it down. <strong>Q2:</strong> The esophagus. <strong>Q3:</strong> The small intestine. <strong>Q4:</strong> Leftover water.</p>
  </div>
  <h3>The Food's Journey &mdash; Answer Key</h3>
  <div class="answer-box wed"><p>Numbers to write, in the order the boxes appear on his sheet:</p><ol>{{WED_SEQ}}</ol></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p>Gravity isn't what moves food down. The esophagus squeezes in waves (peristalsis), like squeezing toothpaste, so it works upside down and in space. Try it: he can swallow a sip of water while lying on the couch with his head lower than his stomach (supervised, small sip).</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>&ldquo;The stomach does all the digesting.&rdquo; Digestion starts in the mouth, and most nutrients are absorbed in the small intestine. Also: the food tube and the windpipe are different tubes. A flap called the epiglottis covers the windpipe when you swallow, which is why we don't talk with our mouths full.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Villi model: compare a flat paper towel to a crumpled one or a terry-cloth washcloth. Dip each corner in colored water and see which soaks up more. Folds and fingers mean more surface for soaking up nutrients.</p>
  </div>

  <h2 class="thu">Thursday &mdash; The Clean-Up Crew</h2>
  <h3>Demo &mdash; Coffee-filter kidney</h3>
  <div class="demo">
    <p>Stir a spoonful of dirt and a pinch of glitter or pepper into a jar of water (blood with waste). Pour it through a coffee filter set in a cup. Big bits stay behind; water and the tiniest bits get through. Real kidneys are far choosier: they keep blood cells and useful nutrients in the blood and let only waste and extra water out. That's the point of the discussion question.</p>
  </div>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1:</strong> The liver. <strong>Q2:</strong> Any one: cleans harmful stuff from the blood, stores fuel, makes bile, can grow back. <strong>Q3:</strong> Waste and extra water. <strong>Q4:</strong> In the bladder.</p>
  </div>
  <h3>Who Does This Job? &mdash; Answer Key</h3>
  <div class="answer-box thu"><ol>{{THU_MATCH}}</ol><p>Oral question: Rudy visits the <strong>lungs</strong> first, to load oxygen before he delivers anything.</p></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p>If red blood cells leaked out, there would be fewer trucks to carry oxygen, and he'd feel very tired. A good filter keeps the useful things and removes only the trash. That's what makes kidneys special. (Blood in urine is one of the things doctors check for.)</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>&ldquo;Kidneys are in the front of the belly.&rdquo; They're toward the back, just under the ribs on either side of the spine. Also, skin is technically the body's largest organ overall; the liver is the largest <em>inside</em> the body. He may enjoy that distinction.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Water tally: track every glass of water he drinks for a day on a tally chart, along with the color of his urine (pale, medium, dark). Does more water mean paler? A real data set from his own body.</p>
  </div>
</div>

<div class="page">
  <h2 class="fri">Friday &mdash; The Head Coach (Capstone)</h2>
  <h3>Demo &mdash; Ruler drop</h3>
  <div class="demo">
    <p>Hold a 30 cm ruler at the top so the 0 end hangs between his open thumb and finger. Drop it without warning (vary the wait). Read the centimeter mark just above his fingers. Typical kid catches land around 15&ndash;25 cm. For your reference, the fall distance converts to reaction time: 5 cm &asymp; 0.10 s, 10 cm &asymp; 0.14 s, 15 cm &asymp; 0.17 s, 20 cm &asymp; 0.20 s, 25 cm &asymp; 0.23 s, 30 cm &asymp; 0.25 s. If he misses entirely, record 30 and say so.</p>
  </div>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1:</strong> The skull. <strong>Q2:</strong> Nerves (and the spinal cord). <strong>Q3:</strong> Any two: keeping you breathing, keeping your heart beating, reflexes like pulling away from something hot.</p>
  </div>
  <h3>Reaction Lab &mdash; What to Look For</h3>
  <div class="answer-box fri">
    <p>Fastest try = shortest bar. Many kids improve across tries (practice), and the other hand is often slower. The sense is <strong>sight</strong> (eyes). The best catch should be written with its unit: <strong>centimeters</strong>.</p>
  </div>
  <h3>Rudy's Body Team &mdash; Answer Key</h3>
  <div class="answer-box fri"><ul>{{FRI_TREE}}</ul><p><em>Accept a defensible swap if he explains it. For example, the esophagus is muscle that moves food, and the brain stem runs the Air Crew's breathing.</em></p></div>
  <h3>Rudy's Whole Route &mdash; Answer Key</h3>
  <div class="answer-box fri"><ol style="columns: 2;">{{FRI_ROUTE}}</ol></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p>The brain stem wins. As carbon dioxide builds up, it forces a breath, so you can't hold your breath until you pass out from choice. That's a safety feature: the most important jobs (breathing, heartbeat) are never left to us to remember. Tie it back to Monday's diaphragm: the brain stem is what tells it to pull.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>&ldquo;The brain only does what I tell it to.&rdquo; Most of its work is automatic. Also, the senses don't &ldquo;see&rdquo; or &ldquo;hear&rdquo; on their own; the eyes and ears collect the signal, and the brain makes sense of it.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Touchdown narration: have him do a 20-second sprint, then narrate the play like a sports announcer, naming every organ that went to work (brain &rarr; legs, lungs, heart, gut fuel, clean-up crew). Record it on a phone and replay it at dinner.</p>
  </div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2>Week Summary</h2>
  <ol style="padding-left: 20px; font-size: 10pt; line-height: 2;">
    <li><strong>Monday:</strong> Cells build organs; the lungs load oxygen; the diaphragm drives breathing.</li>
    <li><strong>Tuesday:</strong> The heart is two pumps; arteries out, veins back, capillaries in between; pulse data.</li>
    <li><strong>Wednesday:</strong> Digestion turns food into nutrients that soak into the blood.</li>
    <li><strong>Thursday:</strong> The liver and kidneys clean the blood; urine and the bladder.</li>
    <li><strong>Friday:</strong> The brain coaches the team through nerves; senses in, commands out; automatic jobs.</li>
  </ol>
  <p style="margin-top: 10px;">By Friday he should be able to trace Rudy's loop (lungs &rarr; heart &rarr; body &rarr; back) and name what each crew adds to or removes from the blood.</p>
</div>

</body>
</html>"""
    for name, value in keys.items():
        TEACHER_GUIDE = TEACHER_GUIDE.replace("{{" + name + "}}", value)
    assert "{{" not in TEACHER_GUIDE
    guide_path = output_dir / "body_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")
    explorer_path = output_dir / "body_explorer.html"
    explorer_path.write_text(build_explorer_html(), encoding="utf-8")

    print(f"Generated {len(pages)} pages -> {output_dir}/")
    print(f"Student packet: {out_path}")
    print(f"Teacher guide:  {guide_path}")
    print(f"Body explorer:  {explorer_path}")
    labels = [
        "Mon p1 — Reading: Meet Rudy — Breathe In! (lungs, diaphragm)",
        "Mon p2 — Cause & Effect: The Breathing Chain",
        "Tue p1 — Reading: The Pump (heart, vessels, pulse)",
        "Tue p2 — Bar Graph: Pulse Lab",
        "Wed p1 — Reading: The Fuel Factory (digestion)",
        "Wed p2 — Sequencing: The Food's Journey",
        "Thu p1 — Reading: The Clean-Up Crew (liver, kidneys, bladder)",
        "Thu p2 — Matching: Who Does This Job?",
        "Fri p1 — Reading: The Head Coach (brain, nerves, senses)",
        "Fri p2 — Bar Graph: Reaction Lab — The Ruler Drop",
        "Fri p3 — Tree Map: Rudy's Body Team",
        "Fri p4 — Fill in the Blank: Rudy's Whole Route (capstone)",
        "       — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"  {label}")


if __name__ == "__main__":
    generate_body_week_series()
