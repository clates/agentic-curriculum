"""
Geography — Continents, Oceans & Countries — Week Series
Grade K-1 | History/Social Science (Geography strand) | Causal Arc:
  Maps & Globes (land vs. water) -> The 7 Continents -> The 5 Oceans
  -> Countries & Their Animals -> Capstone: A Trip Around the World

Narrator: Ridley the Raptor, a velociraptor bush pilot who flies a little yellow
airplane called "The Compass Rose" all around the world. Introduced Monday.

Design note: this week leans hard into "interactive, hands-on" per the parent's
request. Each day still follows the Instructional Pair pattern (reading +
application worksheet), but adds a THIRD page — a Game & Manipulative page —
built from composable content blocks (richText, cutCards). Those pages describe
a physical game (hopscotch, bean-bag toss, a passport stamp rally) AND a step in
a running project: painting/building one big World Map poster across the week
that becomes the game board for Friday's capstone "Trip Around the World" game.

Standards (Virginia SOL, History/Social Science):
  Monday    — VA.HISTORY.K.k.7  (maps vs. globes; land and water)
  Tuesday   — VA.HISTORY.1.1.6  (continents/oceans on maps & globes; cardinal
              directions); VA.HISTORY.K.k.6 (positional/directional words)
  Wednesday — VA.HISTORY.1.1.6  (oceans on maps & globes);
              VA.HISTORY.1.1.7  (landforms and bodies of water)
  Thursday  — VA.HISTORY.1.1.6  (using maps to locate places; map symbols)
  Friday    — VA.HISTORY.1.1.6, VA.HISTORY.1.1.7, VA.HISTORY.K.k.7 (capstone
              synthesis of maps, globes, continents, oceans, countries)

Output: geography_week_series/geography_week.html
        geography_week_series/geography_week_teacher_guide.html
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import (
    build_print_packet_html,
    render_page,
    render_worksheet_html,
)


def generate_geography_week_series():
    output_dir = Path("geography_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []  # (day_label, html_fragment)

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    def add_game_page(
        day_label: str,
        sections: list[dict],
        cards: list[str] | None = None,
        card_columns: int | None = None,
    ) -> None:
        blocks: list[tuple[str, dict]] = [("richText", {"sections": sections})]
        if cards:
            blocks.append(
                ("cutCards", {"cards": cards, "columns": card_columns or min(len(cards), 4)})
            )
        fragment = render_page(blocks, {"day_label": day_label}, layout="classic")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — Maps, Globes, Land & Water
    # Standards: VA.HISTORY.K.k.7 — maps vs. globes; land and water
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: Maps, Globes, and Our Watery World",
            "passage_title": "Meet Ridley — and the Difference Between a Map and a Globe",
            "instructions": (
                "Before reading: find a ball or an orange. Pretend it's Earth. "
                "Now imagine peeling it and pressing the peel flat on the table. "
                "Does it lay flat easily, or does it have to stretch and tear a little?"
            ),
            "passage": (
                "Meet Ridley the Raptor! Ridley is a bright green velociraptor who loves to fly. "
                "Every day this week, Ridley climbs into a little yellow airplane called "
                "The Compass Rose and zooms off on a new adventure. 'Where in the world will I go "
                "today?' Ridley squawks, checking a big round globe hanging by the cockpit seat.\n\n"
                "Before Ridley can visit anywhere, Ridley needs to know what Earth actually looks "
                "like. A globe is a round model of Earth — it spins, just like the real planet does! "
                "A map is a flat picture of Earth, like a photo taken from way up in space and laid "
                "out flat on paper. Maps and globes both show the same thing — where the land and "
                "water are — but a globe never lies about shape or size. A flat map has to squish "
                "and stretch a little to lay the round Earth flat, kind of like peeling an orange "
                "and pressing the peel down on a table.\n\n"
                "Ridley looked closely at the globe. Some parts were green and brown — that's LAND, "
                "the solid ground we walk on, build houses on, and grow gardens on. Other parts were "
                "blue — that's WATER, like oceans, seas, rivers, and lakes. 'Wow,' Ridley said, "
                "spinning the globe slowly, 'there's so much more blue than green!' Ridley was "
                "right. Water covers most of our planet — almost three-fourths of it! Only a little "
                "more than one-fourth of Earth is land.\n\n"
                "Ridley buckled into The Compass Rose and took off toward the clouds. 'This week, "
                "we're going to fly all around the whole world,' Ridley announced. 'We'll visit "
                "every continent, cross every ocean, and land in some amazing countries. Let's go "
                "find out what's out there!'"
            ),
            "vocabulary": [
                {
                    "term": "map",
                    "definition": "A flat picture of Earth, or part of Earth, drawn on paper.",
                },
                {
                    "term": "globe",
                    "definition": "A round model of Earth that spins, just like the real planet.",
                },
                {
                    "term": "land",
                    "definition": "The solid ground on Earth — where we walk, build, and grow gardens.",
                },
                {
                    "term": "water",
                    "definition": "Oceans, seas, rivers, and lakes — the wet parts of Earth.",
                },
                {
                    "term": "Earth",
                    "definition": "The planet we live on — covered mostly in water, with patches of land.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is the difference between a map and a globe?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Which covers more of Earth — land or water? About how much?",
                    "response_lines": 2,
                },
                {"prompt": "Name two things Ridley plans to visit this week.", "response_lines": 1},
                {
                    "prompt": (
                        "LET'S DISCUSS: Why do you think a flat map has to 'stretch' parts of the "
                        "world to make it fit on paper? Would you rather use a map or a globe to "
                        "figure out how big a country really is?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    add(
        "wordSortWorksheet",
        {
            "title": "Monday: Land or Water? — Word Sort",
            "instructions": (
                "Look at each word in the word bank. Write it in the correct box — "
                "does it belong with LAND or WATER?"
            ),
            "categories": [{"label": "Land"}, {"label": "Water"}],
            "tiles": [
                "Ocean",
                "Mountain",
                "River",
                "Desert",
                "Lake",
                "Forest",
                "Sea",
                "Island",
                "Pond",
                "Valley",
            ],
        },
        "Monday",
    )

    add_game_page(
        "Monday",
        sections=[
            {
                "heading": "🌎 Play: Beach-Ball Globe Toss",
                "text": (
                    "A quick game to prove Ridley's point — Earth really is mostly water! "
                    "If you have an inflatable globe beach ball, use that. No globe ball? Draw big "
                    "blue and green/brown blobs on any ball with a marker instead."
                ),
                "bullets": [
                    "Materials: a globe beach ball (or any ball marked with land/water blobs), paper and pencil for tally marks.",
                    "1. Stand across from a grown-up and toss the ball back and forth.",
                    "2. Whoever catches it looks at where their RIGHT thumb landed — is it touching land or water?",
                    "3. Call out 'Land!' or 'Water!' and make a tally mark. Play 10 rounds.",
                    "4. Count the tallies together. Which had more? (Water should win — just like the reading said!)",
                ],
            },
            {
                "heading": "🗺️ Build: Start the Big World Map",
                "text": (
                    "This is the first step of a project that grows all week — by Friday you'll "
                    "have a full world map to play the capstone game on!"
                ),
                "bullets": [
                    "Materials: a big piece of butcher paper or poster board, blue paint or a blue crayon/marker.",
                    "1. Color or paint the whole poster blue — this is our ocean background.",
                    "2. Let it dry flat somewhere safe. We'll add land on Tuesday!",
                    "3. Keep it, along with this week's cut-out cards, in one folder or envelope all week.",
                ],
            },
        ],
    )

    # =========================================================================
    # TUESDAY — The Seven Continents
    # Standards: VA.HISTORY.1.1.6 (continents/oceans, cardinal directions);
    #            VA.HISTORY.K.k.6 (positional words)
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: The Seven Continents",
            "passage_title": "Flying to Every Corner of the World",
            "instructions": (
                "Read about the seven continents with Ridley. Then answer the questions. "
                "Keep a real map or globe nearby if you have one — it makes question 4 much easier!"
            ),
            "passage": (
                "Ridley soared high above the clouds in The Compass Rose. 'Time to meet the seven "
                "continents!' Ridley announced. A continent is one of Earth's seven giant pieces of "
                "land. Let's fly to each one!\n\n"
                "First, Ridley flew over ASIA — the biggest continent of all! Millions and millions "
                "of people live there, and it stretches so far that it touches EUROPE to its west "
                "and the Pacific Ocean to its east. Right next to Asia, connected like a puzzle "
                "piece, sits EUROPE — a smaller continent packed with many countries close together.\n\n"
                "Flying south, Ridley reached AFRICA, the second-biggest continent, sitting below "
                "Europe across a narrow sea. Africa is home to hot deserts and green rainforests. "
                "Far across the wide Atlantic Ocean to the west, Ridley found NORTH AMERICA — home "
                "sweet home! Just below it, connected by a thin strip of land, is SOUTH AMERICA, "
                "where the giant Amazon Rainforest grows.\n\n"
                "Down at the very bottom of the globe, colder than any freezer, sits ANTARCTICA — a "
                "whole continent covered in ice, near the South Pole. And out in the ocean near "
                "Asia, all by itself, floats AUSTRALIA — the smallest continent, and the only one "
                "that is also just one single country!\n\n"
                "'Seven continents, seven amazing places,' Ridley chirped, checking each one off the "
                "map. 'And every single one is surrounded by water. Tomorrow, let's explore those "
                "oceans!'"
            ),
            "vocabulary": [
                {"term": "continent", "definition": "One of Earth's seven giant pieces of land."},
                {
                    "term": "north",
                    "definition": "The direction toward the top of a map — toward the North Pole.",
                },
                {
                    "term": "south",
                    "definition": "The direction toward the bottom of a map — toward the South Pole.",
                },
                {
                    "term": "east",
                    "definition": "The direction to the right on most maps, where the sun rises.",
                },
                {
                    "term": "west",
                    "definition": "The direction to the left on most maps, where the sun sets.",
                },
            ],
            "questions": [
                {"prompt": "How many continents are there? Name two of them.", "response_lines": 2},
                {
                    "prompt": "Which continent is the biggest? Which is the smallest?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Which continent is covered in ice and has no countries?",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "Get a real map or globe. Which ocean touches North America on the east "
                        "side? Which one touches it on the west side?"
                    ),
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Australia is the only continent that is also just one "
                        "country. Every other continent has many countries on it. Why do you think "
                        "that might be?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "matchingWorksheet",
        {
            "title": "Tuesday: The Seven Continents — Read & Connect",
            "instructions": (
                "Read each continent and its clue out loud together, then trace the line "
                "connecting them — great practice for tomorrow's hopscotch game!"
            ),
            "left_items": [
                "Asia",
                "Africa",
                "North America",
                "South America",
                "Antarctica",
                "Europe",
                "Australia",
            ],
            "right_items": [
                "The biggest continent — home to billions of people",
                "The second-biggest continent — deserts and rainforests",
                "Home to the United States, Canada, and Mexico",
                "Home of the giant Amazon Rainforest",
                "Covered in ice near the South Pole — no countries here",
                "Many small countries packed close together",
                "The smallest continent — also just one country, with kangaroos!",
            ],
        },
        "Tuesday",
    )

    add_game_page(
        "Tuesday",
        sections=[
            {
                "heading": "🦶 Play: Continent Hopscotch",
                "text": "Get moving and learn continent names and directions at the same time.",
                "bullets": [
                    "Materials: sidewalk chalk (outside) or painter's tape (inside), the continent cards below.",
                    "1. Draw or tape 7 spaces in a row or a grid. Put one continent card in each space.",
                    "2. Call out a continent name — hop to it! Take turns calling and hopping.",
                    "3. Bonus round: call out a direction instead, like 'Hop to the continent EAST of Africa!' (Answer: Asia).",
                    "4. Play until every continent has been hopped to at least twice.",
                ],
            },
            {
                "heading": "🗺️ Build: Add the Continents to Your Map",
                "text": "Grow yesterday's ocean poster into a real world map.",
                "bullets": [
                    "Materials: yesterday's blue poster, scissors, glue, a real map or globe to copy shapes from.",
                    "1. Cut out the 7 continent cards below (or trace rough continent shapes onto colored paper and cut those out instead).",
                    "2. Using a real map or globe as your guide, glue each continent onto the correct spot on your blue poster.",
                    "3. Leave the water spaces blue and empty — we'll label the oceans tomorrow.",
                ],
            },
        ],
        cards=[
            "🌏 ASIA",
            "🌍 AFRICA",
            "🌎 NORTH AMERICA",
            "🌎 SOUTH AMERICA",
            "🧊 ANTARCTICA",
            "🌍 EUROPE",
            "🦘 AUSTRALIA",
        ],
        card_columns=4,
    )

    # =========================================================================
    # WEDNESDAY — The Five Oceans
    # Standards: VA.HISTORY.1.1.6 (oceans on maps/globes);
    #            VA.HISTORY.1.1.7 (landforms and bodies of water)
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: The Five Oceans",
            "passage_title": "Water, Water, Everywhere!",
            "instructions": (
                "Read about the five oceans with Ridley. Then answer the questions below."
            ),
            "passage": (
                "The next morning, Ridley flew The Compass Rose straight out over open water. "
                "'Yesterday we found land. Today, let's explore water!' Ridley announced. Earth has "
                "five oceans, and every one of them connects to the others — it's almost like one "
                "giant World Ocean!\n\n"
                "The biggest and deepest ocean is the PACIFIC OCEAN. It's so enormous that it "
                "touches Asia, Australia, and both North and South America all at once! Next is the "
                "ATLANTIC OCEAN, the second-biggest, sitting right between the Americas on one side "
                "and Europe and Africa on the other — ships have crossed it for hundreds of years.\n\n"
                "The INDIAN OCEAN is the warmest ocean of all, touching Africa, Asia, and Australia. "
                "Way up at the very top of the world, circling the North Pole, is the smallest and "
                "iciest ocean — the ARCTIC OCEAN. It's so cold that huge chunks of it freeze solid! "
                "And down at the very bottom, wrapping all the way around icy Antarctica, is the "
                "SOUTHERN OCEAN — a very cold ocean too, and the newest one added to our maps.\n\n"
                "'Water, water, everywhere!' Ridley laughed, flying low over the waves of the "
                "Pacific. 'Oceans give us more than half of the air we breathe, they're home to "
                "whales and sharks and coral reefs, and they connect every continent together. "
                "Tomorrow, let's land somewhere and meet some animals!'"
            ),
            "vocabulary": [
                {
                    "term": "ocean",
                    "definition": "A giant body of salt water that covers most of Earth.",
                },
                {
                    "term": "Pacific Ocean",
                    "definition": "The biggest and deepest ocean — touches Asia, Australia, and the Americas.",
                },
                {
                    "term": "Atlantic Ocean",
                    "definition": "The second-biggest ocean — between the Americas and Europe/Africa.",
                },
                {
                    "term": "Indian Ocean",
                    "definition": "The warmest ocean — touches Africa, Asia, and Australia.",
                },
                {
                    "term": "Arctic Ocean",
                    "definition": "The smallest, iciest ocean — at the very top of the world.",
                },
                {
                    "term": "Southern Ocean",
                    "definition": "A very cold ocean that circles icy Antarctica at the bottom of the world.",
                },
            ],
            "questions": [
                {"prompt": "How many oceans are there on Earth? Name three.", "response_lines": 2},
                {
                    "prompt": "Which ocean is the biggest? Which is the smallest?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Which ocean is the warmest? Which oceans are the coldest?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Name one continent that touches the Pacific Ocean.",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Ridley said the oceans are almost like 'one giant World "
                        "Ocean' since they all connect. Do you think a fish could swim from the "
                        "Pacific Ocean all the way to the Atlantic Ocean without ever touching land? "
                        "How?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "featureMatrixWorksheet",
        {
            "title": "Wednesday: The Five Oceans — What Do You Know?",
            "instructions": (
                "Put a check mark in every box that describes each ocean. "
                "Use your reading card for clues!"
            ),
            "items": [
                "Pacific Ocean",
                "Atlantic Ocean",
                "Indian Ocean",
                "Arctic Ocean",
                "Southern Ocean",
            ],
            "properties": [
                "Biggest Ocean",
                "Smallest Ocean",
                "Warmest Ocean",
                "Very Cold, Icy Water",
                "Surrounds Antarctica",
                "Between the Americas & Europe/Africa",
            ],
        },
        "Wednesday",
    )

    add_game_page(
        "Wednesday",
        sections=[
            {
                "heading": "🎒 Play: Ocean Bean-Bag Toss",
                "text": "Use yesterday's hopscotch continents and toss your way through the oceans between them.",
                "bullets": [
                    "Materials: bean bags or rolled-up socks, the ocean cards below, yesterday's continent hopscotch spaces.",
                    "1. Spread the 5 ocean cards on the floor around and between your continent spaces.",
                    "2. Toss a bean bag toward the ocean cards. Whichever one it lands nearest, call out a fact you remember about that ocean.",
                    "3. Take turns. Extra challenge: try to land on all 5 oceans before your grown-up does!",
                ],
            },
            {
                "heading": "🗺️ Build: Label the Oceans on Your Map",
                "text": "Finish filling in the blue water spaces on your growing world map poster.",
                "bullets": [
                    "Materials: your map poster with continents glued on, the ocean cards below, glue.",
                    "1. Cut out the 5 ocean name cards below.",
                    "2. Glue each one onto the correct blue water space on your poster — Pacific, Atlantic, Indian, Arctic, Southern.",
                    "3. Your map now shows every continent and every ocean. Tomorrow we add countries!",
                ],
            },
        ],
        cards=["🌊 PACIFIC", "🌊 ATLANTIC", "🌊 INDIAN", "🧊 ARCTIC", "🧊 SOUTHERN"],
        card_columns=5,
    )

    # =========================================================================
    # THURSDAY — Countries and Their Animals
    # Standards: VA.HISTORY.1.1.6 — using maps to locate places; map symbols
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: Countries and Their Animals",
            "passage_title": "Six Countries, Six Amazing Animals",
            "instructions": (
                "Read about the six countries with Ridley. Then answer the questions below."
            ),
            "passage": (
                "Ridley landed The Compass Rose on a grassy runway. 'Continents are huge, and "
                "oceans are huge — but did you know continents are divided into smaller pieces "
                "called countries?' A country is a part of a continent with its own name, its own "
                "flag, its own government, and usually its own special language. North America "
                "alone has countries like the United States, Canada, and Mexico!\n\n"
                "Ridley's passport was ready for stamps. First stop: the UNITED STATES, in North "
                "America, where the bald eagle soars over mountains and prairies. Next, Ridley flew "
                "south to BRAZIL, in South America, home to the mighty jaguar prowling through the "
                "Amazon Rainforest. Across the Atlantic Ocean, Ridley landed in FRANCE, in Europe, "
                "where the rooster is a proud national symbol and the Eiffel Tower rises over the "
                "city of Paris.\n\n"
                "Then it was off to KENYA, in Africa, where lions roam wide-open grasslands called "
                "savannas. Ridley flew all the way to CHINA, in Asia, to visit giant pandas munching "
                "on bamboo. The last stop was AUSTRALIA, where kangaroos bounce across the outback "
                "— remember, Australia is a continent AND a country, all in one!\n\n"
                "'Six countries, six amazing animals, six stamps in my passport!' Ridley cheered. "
                "'And guess what — Antarctica doesn't have any countries at all. It's too icy and "
                "cold for anyone to live there full-time. Only scientists and penguins visit!' "
                "Tomorrow, Ridley would put it all together for one last big trip around the whole "
                "world."
            ),
            "vocabulary": [
                {
                    "term": "country",
                    "definition": "A part of a continent with its own name, flag, government, and often its own language.",
                },
                {
                    "term": "passport",
                    "definition": "A little booklet that shows which countries you have visited.",
                },
                {
                    "term": "savanna",
                    "definition": "Wide, open grassland — found in Africa, home to lions and giraffes.",
                },
                {
                    "term": "outback",
                    "definition": "The wide, dry, wild countryside of Australia — home to kangaroos.",
                },
                {
                    "term": "rainforest",
                    "definition": "A thick, green, rainy forest — like the Amazon in Brazil — where jaguars live.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is a country? How is it different from a continent?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Name two countries Ridley visited and the continent each one is on.",
                    "response_lines": 2,
                },
                {
                    "prompt": "Which animal lives in Kenya? Which lives in China?",
                    "response_lines": 1,
                },
                {"prompt": "Why doesn't Antarctica have any countries?", "response_lines": 2},
                {
                    "prompt": (
                        "LET'S DISCUSS: Australia is both a continent and a country. Can you think "
                        "of why that might make Australia a little different from every other place "
                        "Ridley visited this week?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    add(
        "treeMapWorksheet",
        {
            "title": "Thursday: Countries & Animals — Tree Map",
            "instructions": (
                "Each country and its special animal belongs on one continent's branch. "
                "Sort the word bank into the correct branch — use your reading card for clues!"
            ),
            "root_label": "World Countries & Animals",
            "branches": [
                {"label": "North America", "slot_count": 1},
                {"label": "South America", "slot_count": 1},
                {"label": "Europe", "slot_count": 1},
                {"label": "Africa", "slot_count": 1},
                {"label": "Asia", "slot_count": 1},
                {"label": "Australia", "slot_count": 1},
            ],
            "columns": 3,
            "word_bank": [
                "China — Giant Panda",
                "France — Rooster",
                "Australia — Kangaroo",
                "United States — Bald Eagle",
                "Kenya — Lion",
                "Brazil — Jaguar",
            ],
        },
        "Thursday",
    )

    add_game_page(
        "Thursday",
        sections=[
            {
                "heading": "🛂 Play: Passport Stamp Rally",
                "text": "Make your very own passport, then visit all six countries to fill it up.",
                "bullets": [
                    "Materials: a sheet of paper folded in half or quarters (and stapled) to make a little booklet, a marker or a real stamp pad.",
                    "1. On the cover, write your name and draw a small self-portrait — that's your passport photo!",
                    "2. Give each inside page a country name from this week's reading.",
                    "3. For each country, say its animal out loud, then draw or stamp a mark on that page — you've 'visited'!",
                    "4. Six countries, six stamps — a full passport by the end.",
                ],
            },
            {
                "heading": "🗺️ Build: Add Countries to Your Map",
                "text": "Almost done! Add today's countries and animals to your growing world map poster.",
                "bullets": [
                    "Materials: your map poster, the country cards below, glue.",
                    "1. Cut out the 6 country/animal cards below.",
                    "2. Glue each one onto the correct continent on your poster.",
                    "3. Your map is nearly finished — tomorrow you'll use it to play the big capstone game!",
                ],
            },
        ],
        cards=[
            "🇺🇸 USA — Eagle",
            "🇧🇷 BRAZIL — Jaguar",
            "🇫🇷 FRANCE — Rooster",
            "🇰🇪 KENYA — Lion",
            "🇨🇳 CHINA — Panda",
            "🇦🇺 AUSTRALIA — Kangaroo",
        ],
        card_columns=3,
    )

    # =========================================================================
    # FRIDAY — Capstone: A Trip Around the World
    # Standards: VA.HISTORY.1.1.6, VA.HISTORY.1.1.7, VA.HISTORY.K.k.7
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: A Trip Around the World",
            "passage_title": "Putting It All Together",
            "instructions": (
                "Read the capstone passage with Ridley. Then answer the questions below."
            ),
            "passage": (
                "It was the last day of Ridley's big adventure. 'Let's put it all together!' Ridley "
                "said, spreading a giant map across the cockpit floor of The Compass Rose. 'This "
                "week we learned that maps and globes both show the same Earth — just in different "
                "ways. We found all SEVEN CONTINENTS, from giant Asia to icy Antarctica. We crossed "
                "all FIVE OCEANS, from the huge Pacific to the freezing Arctic. And we landed in SIX "
                "COUNTRIES, meeting a bald eagle, a jaguar, a rooster, a lion, a giant panda, and a "
                "kangaroo along the way!'\n\n"
                "Ridley pulled out the stamped passport and the big colorful map, now covered in "
                "continents, oceans, and flags. 'Every piece fits together like a puzzle,' Ridley "
                "said. 'Oceans surround continents. Continents are made of countries. And every "
                "country is home to animals, people, and places that make it special.'\n\n"
                "Why does any of this matter? Knowing your way around a map helps you understand "
                "the whole world — where your food comes from, where your favorite animals live, "
                "and how far away places really are. It even helps you plan your own adventures "
                "someday, just like Ridley!\n\n"
                "'One last trip before we land,' Ridley announced, buckling in for takeoff. 'Let's "
                "fly all the way around the world one more time — and see how much we remember!'"
            ),
            "vocabulary": [
                {"term": "continent", "definition": "One of Earth's seven giant pieces of land."},
                {"term": "ocean", "definition": "One of Earth's five giant bodies of salt water."},
                {
                    "term": "country",
                    "definition": "A part of a continent with its own name, flag, and government.",
                },
                {
                    "term": "map",
                    "definition": "A flat picture of Earth, or part of Earth, drawn on paper.",
                },
                {
                    "term": "globe",
                    "definition": "A round model of Earth that spins, just like the real planet.",
                },
            ],
            "questions": [
                {"prompt": "How many continents are there? How many oceans?", "response_lines": 1},
                {
                    "prompt": "Name one country, the continent it's on, and one animal that lives there.",
                    "response_lines": 2,
                },
                {"prompt": "What's the difference between a map and a globe?", "response_lines": 2},
                {
                    "prompt": "Why does Ridley say 'every piece fits together like a puzzle'?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Of all the continents, oceans, and countries you learned "
                        "about this week, which one would you most want to visit for real? Why?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Friday",
    )

    add(
        "oddOneOutWorksheet",
        {
            "title": "Friday: Odd One Out — Continents, Oceans & Countries",
            "instructions": (
                "Look at each group. Circle the one that does NOT belong. "
                "Tell a grown-up why — is it a continent, an ocean, a country, an animal, or a tool?"
            ),
            "rows": [
                {"items": ["Asia", "Africa", "Pacific Ocean", "Europe"], "reasoning_lines": 1},
                {
                    "items": ["United States", "Brazil", "Atlantic Ocean", "China"],
                    "reasoning_lines": 1,
                },
                {"items": ["Kangaroo", "Panda", "Lion", "Australia"], "reasoning_lines": 1},
                {"items": ["Pacific", "Atlantic", "Indian", "Kenya"], "reasoning_lines": 1},
                {"items": ["Map", "Globe", "Passport", "Ocean"], "reasoning_lines": 1},
                {
                    "items": ["North America", "South America", "Antarctica", "France"],
                    "reasoning_lines": 1,
                },
            ],
        },
        "Friday",
    )

    add_game_page(
        "Friday",
        sections=[
            {
                "heading": "🌍 Capstone Game: The Great Big Trip Around the World",
                "text": (
                    "Play this game on the finished map you've built all week — the perfect way to "
                    "review everything Ridley taught!"
                ),
                "bullets": [
                    "Materials: your finished world map poster, your passport, this week's cut-out cards shuffled into one 'trivia' pile, a die or number cards 1-6, a small toy or button for a game piece.",
                    "1. Set your game piece on North America — home base.",
                    "2. Take turns rolling the die (or drawing a number) and hopping that many continents/oceans across your map, in any direction a grown-up helps you pick.",
                    "3. Wherever you land, draw a trivia card and answer it together — an ocean fact, a continent fact, or a country-and-animal fact from this week.",
                    "4. Answer correctly and stamp your passport for that stop!",
                    "5. Keep going until every country has a stamp — then celebrate with a 'world tour' dance party!",
                ],
            },
            {
                "heading": "🎉 Wrap-Up: Show and Tell",
                "text": "Finish the week by showing off everything you built.",
                "bullets": [
                    "Show a grown-up (or a video call with family) your finished map and full passport.",
                    "Pick your favorite continent, ocean, and country from the whole week and explain why.",
                ],
            },
        ],
    )

    # =========================================================================
    # PARENT FEEDBACK & TEACHING NOTES
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "End-of-Week Parent Feedback — Geography Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this feedback sheet after the week wraps up. "
                "Your notes help shape next week's lessons."
            ),
            "passage": (
                "This week followed a causal arc through world geography. Monday established that "
                "maps and globes both represent Earth, and that water covers most of the planet. "
                "Tuesday introduced all seven continents and practiced positional/cardinal-direction "
                "words. Wednesday added the five oceans that surround and connect those continents. "
                "Thursday zoomed in from continents to countries, meeting one animal per country "
                "across six of the seven continents (Antarctica has none). Friday synthesized "
                "everything into one capstone review game played on a map Christopher built, piece "
                "by piece, across the whole week.\n\n"
                "Ridley the Raptor appeared throughout the week as a friendly pilot-narrator, giving "
                "concrete, adventure-framed examples for each concept. Each day also built one piece "
                "of a running world-map poster and paired it with a physical game (globe toss, "
                "hopscotch, bean-bag toss, passport rally, and a capstone board game) so the content "
                "stayed hands-on rather than desk-only, per the week's design brief.\n\n"
                "Key concepts to check for genuine understanding — not just recall:\n"
                "1) A map and a globe show the same Earth, just in different forms.\n"
                "2) There are 7 continents and 5 oceans, and every continent touches at least one ocean.\n"
                "3) A country is a smaller piece of land inside a continent — countries are not "
                "the same size or kind of thing as continents.\n"
                "4) Antarctica has no countries because it is too cold for anyone to live there "
                "year-round.\n\n"
                "Common misconceptions to watch for:\n"
                "• 'Continents and countries are the same thing' — a continent can contain many "
                "countries (Africa alone has over 50!).\n"
                "• 'Flat maps show every country's true size' — flat maps stretch and squish shapes "
                "(Monday's orange-peel demo addresses this directly); a globe is the more accurate "
                "shape and size reference.\n"
                "• 'Australia is only a continent OR only a country' — it's genuinely both, which "
                "trips kids up because nowhere else works that way.\n\n"
                "Suggested follow-on activities: keep the finished world map poster up and add a "
                "sticky-note pin every time you read a book, watch a show, or eat a food from a new "
                "country; look up your own town on a real map together and trace the route to a "
                "place you'd like to visit."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": "A continent is not the same as a country — continents contain many countries (Africa has 50+).",
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in after the week — which idea did Christopher grasp best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": "Landforms and weather by region — why do deserts, rainforests, and icy places all exist on the same planet?",
                },
            ],
            "questions": [
                {
                    "prompt": "Overall comfort with the week's content — how well did Christopher grasp the concepts? (1 = struggled throughout, 5 = strong grasp of all concepts)",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which day's game or activity was the biggest hit?",
                    "response_lines": 2,
                },
                {
                    "prompt": "By Friday, could Christopher name all 7 continents and 5 oceans without prompting?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Did the finished world map and passport hold Christopher's interest as a keepsake, or would a smaller/simpler version work better next time?",
                    "response_lines": 2,
                },
                {"prompt": "Topics or vocabulary to revisit next week:", "response_lines": 2},
            ],
        },
        "Friday",
    )

    # =========================================================================
    # Assemble & write
    # =========================================================================

    html = build_print_packet_html(
        pages, packet_title="Geography Week — Continents, Oceans & Countries for Christopher"
    )
    out_path = output_dir / "geography_week.html"
    out_path.write_text(html, encoding="utf-8")

    # Teacher guide
    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Geography Week — Teacher Guide</title>
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
    .game-note { background: #eef9ff; border-left: 4px solid #0284c7; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .materials { background: #fafafa; border: 1.5px dashed #999; border-radius: 6px; padding: 8px 12px; margin: 8px 0 14px; font-size: 10pt; }
    .materials strong { display: block; margin-bottom: 4px; }
  </style>
</head>
<body>

<div class="page">
  <h1>Geography Week — Teacher / Parent Guide</h1>
  <p><strong>Theme:</strong> Continents, Oceans &amp; Countries &nbsp;|&nbsp; <strong>Audience:</strong> Christopher, age 6, K-1 &nbsp;|&nbsp;
  <strong>Narrator:</strong> Ridley the Raptor</p>
  <p><strong>Causal Arc:</strong> Maps &amp; Globes &rarr; The 7 Continents &rarr; The 5 Oceans &rarr; Countries &amp; Animals &rarr; Capstone Trip Around the World</p>

  <div class="materials">
    <strong>Materials Checklist for the Whole Week (gather before Monday)</strong>
    Butcher paper or poster board &middot; blue paint or blue crayon/marker &middot; scissors &middot; glue stick
    &middot; a ball (ideally an inflatable globe beach ball) &middot; sidewalk chalk or painter's tape
    &middot; bean bags or rolled-up socks &middot; paper for a folded passport booklet &middot; a stapler
    &middot; a die or number cards 1-6 &middot; a small toy or button for a game piece &middot; a real map or
    globe for reference (a phone map app works in a pinch).
  </div>

  <h2>Monday — Maps, Globes, Land &amp; Water</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1 (Map vs. globe):</strong> A globe is a round model of Earth that spins like the real planet. A map is a flat picture of Earth on paper — flat maps have to stretch or squish shapes a little to lay the round Earth out flat.</p>
    <p><strong>Q2 (Land vs. water):</strong> Water covers most of Earth — almost three-fourths. Land is a little more than one-fourth.</p>
    <p><strong>Q3 (Week preview):</strong> Continents, oceans, and countries (any two).</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Why does a flat map have to stretch parts of the world?"</em></p>
    <p>Earth is a sphere; paper is flat. You cannot flatten a round surface without some stretching or tearing, the same way an orange peel cracks when pressed flat. A globe keeps true shapes and sizes; a flat map trades some accuracy for the convenience of folding it up and carrying it around.</p>
  </div>
  <h3>Word Sort Answer Key</h3>
  <div class="answer-box">
    <p><strong>Land:</strong> Mountain, Desert, Forest, Island, Valley</p>
    <p><strong>Water:</strong> Ocean, River, Lake, Sea, Pond</p>
  </div>
  <h3>Game Notes — Beach-Ball Globe Toss</h3>
  <div class="game-note">
    <p>No inflatable globe on hand? A regular ball marked with a permanent marker works fine — just make sure water (blue) clearly outweighs land (green/brown) so the 10-round tally comes out realistic. This is a probability warm-up as much as a geography one: more blue on the ball means more "water" catches, which mirrors the real 71%/29% split.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Students sometimes think a globe is "just a toy version" of a map, rather than the more accurate one. Reinforce that the globe is the truer shape/size reference; the flat map is the convenient-but-distorted one.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Actually try the orange-peel demo from the pre-reading prompt if you skipped it: peel an orange in one long strip and try to press it flat. It cracks and stretches — exactly what happens to map projections of Earth.</p>
  </div>

  <h2 class="tue">Tuesday — The Seven Continents</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box tue">
    <p><strong>Q1 (Count/names):</strong> Seven continents: Asia, Africa, North America, South America, Antarctica, Europe, Australia.</p>
    <p><strong>Q2 (Biggest/smallest):</strong> Asia is biggest; Australia is smallest.</p>
    <p><strong>Q3 (Icy, no countries):</strong> Antarctica.</p>
    <p><strong>Q4 (Directions):</strong> The Atlantic Ocean touches North America on the east side; the Pacific Ocean touches it on the west side.</p>
  </div>
  <h3>Matching Answer Key</h3>
  <div class="answer-box tue">
    <p>Asia &rarr; biggest continent, billions of people. Africa &rarr; second-biggest, deserts and rainforests. North America &rarr; USA, Canada, Mexico. South America &rarr; Amazon Rainforest. Antarctica &rarr; icy, no countries. Europe &rarr; many small countries close together. Australia &rarr; smallest continent, also one country, kangaroos.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Why does Australia get to be just one country while every other continent has many?"</em></p>
    <p>There's no single "right" answer — accept any reasonable idea (it's surrounded entirely by ocean with no land borders to divide it from neighbors; it was settled/organized differently than continents where many groups lived close together over a long history). The goal is reasoning practice, not a fact recall.</p>
  </div>
  <h3>Game Notes — Continent Hopscotch</h3>
  <div class="game-note">
    <p>The directional "bonus round" is the real standards payoff here (VA.HISTORY.K.k.6 and 1.1.6). Keep a real map taped up nearby during the game so Christopher can check north/south/east/west against something concrete rather than guessing.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Kids often think Europe and Asia are two separate, unconnected landmasses like North and South America. They're actually one connected landmass (sometimes called "Eurasia") that we simply treat as two continents by cultural convention. This is a fun "even grown-ups argue about it" aside if it comes up.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Size-order challenge: without looking, try to put the 7 continent cards in order from biggest to smallest, then check against a real map. (Order: Asia, Africa, North America, South America, Antarctica, Europe, Australia.)</p>
  </div>
</div>

<div class="page">
  <h2 class="wed">Wednesday — The Five Oceans</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1 (Count/names):</strong> Five oceans: Pacific, Atlantic, Indian, Arctic, Southern.</p>
    <p><strong>Q2 (Biggest/smallest):</strong> Pacific is biggest; Arctic is smallest.</p>
    <p><strong>Q3 (Warmest/coldest):</strong> Indian Ocean is warmest; Arctic and Southern are the coldest/iciest.</p>
    <p><strong>Q4 (Pacific neighbor):</strong> Any of: Asia, Australia, North America, South America.</p>
  </div>
  <h3>Feature Matrix Answer Key</h3>
  <div class="answer-box wed">
    <p><strong>Pacific:</strong> Biggest Ocean.</p>
    <p><strong>Atlantic:</strong> Between the Americas &amp; Europe/Africa.</p>
    <p><strong>Indian:</strong> Warmest Ocean.</p>
    <p><strong>Arctic:</strong> Smallest Ocean; Very Cold, Icy Water.</p>
    <p><strong>Southern:</strong> Very Cold, Icy Water; Surrounds Antarctica.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Could a fish swim from the Pacific to the Atlantic without touching land?"</em></p>
    <p>Yes! Because all five oceans connect into one continuous body of water, a sea creature could in principle swim around Antarctica (through the Southern Ocean) or around the tip of South America/Africa and reach any other ocean without ever crossing land — this is exactly how many whale species migrate.</p>
  </div>
  <h3>Game Notes — Ocean Bean-Bag Toss</h3>
  <div class="game-note">
    <p>If floor space is tight, shrink the layout — even 5 sheets of paper labeled with ocean names on a table works. The point is retrieving one fact per ocean out loud, not toss accuracy.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Kids often assume "five oceans" means five totally separate pools of water, like five different bathtubs. Reinforce the "one giant World Ocean" framing from the passage — the five names are just how we divide up one connected body of water.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Trace a real sea voyage: pick an animal (a sea turtle, a humpback whale) and look up a real migration route online or in a book. Which oceans does it cross?</p>
  </div>

  <h2 class="thu">Thursday — Countries and Their Animals</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1 (Country vs. continent):</strong> A country is a smaller part of a continent with its own name, flag, and government; a continent is the whole giant landmass a country sits on.</p>
    <p><strong>Q2 (Countries/continents):</strong> Any two of: USA/North America, Brazil/South America, France/Europe, Kenya/Africa, China/Asia, Australia/Australia.</p>
    <p><strong>Q3 (Animals):</strong> Kenya &rarr; lion. China &rarr; giant panda.</p>
    <p><strong>Q4 (Antarctica):</strong> It is too icy and cold for anyone to live there full-time; only scientists and penguins visit.</p>
  </div>
  <h3>Tree Map Answer Key</h3>
  <div class="answer-box thu">
    <p>North America &rarr; United States — Bald Eagle. South America &rarr; Brazil — Jaguar. Europe &rarr; France — Rooster. Africa &rarr; Kenya — Lion. Asia &rarr; China — Giant Panda. Australia &rarr; Australia — Kangaroo.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Why is Australia different, being both a continent and a country?"</em></p>
    <p>Every other continent is divided into many countries; Australia is surrounded entirely by ocean with no neighbors to divide it up, so the whole continent became one country. There's no single correct answer — reward any logical reasoning.</p>
  </div>
  <h3>Game Notes — Passport Stamp Rally</h3>
  <div class="game-note">
    <p>Keep the passport! It's a nice callback prop for Friday's capstone game and a fun keepsake. If a real ink stamp isn't available, a smiley-face sticker or a marker doodle works just as well as the "stamp."</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"Every country has just one kind of animal, and it only lives there." Gently clarify: these are famous/symbolic animals associated with each country, not the only animals that live there, and most of these animals live in more than one country too (lions live in several African countries, for example).</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Pick one of the six countries and look up its real flag together. What colors and shapes does it use? Add a tiny drawing of the flag next to that country on the map poster.</p>
  </div>
</div>

<div class="page">
  <h2 class="fri">Friday — Capstone: A Trip Around the World</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1 (Counts):</strong> 7 continents, 5 oceans.</p>
    <p><strong>Q2 (Country/continent/animal):</strong> Any correct trio from the week, e.g. Kenya / Africa / lion.</p>
    <p><strong>Q3 (Map vs. globe):</strong> A globe is a round, accurate model of Earth; a map is a flat, portable picture that has to stretch shapes a little.</p>
    <p><strong>Q4 (Puzzle metaphor):</strong> Oceans surround and connect continents; continents contain countries; countries are home to particular animals, people, and places — every layer nests inside the next, like puzzle pieces fitting together.</p>
  </div>
  <h3>Odd One Out Answer Key</h3>
  <div class="answer-box fri">
    <p><strong>Row 1:</strong> Pacific Ocean (the rest are continents).</p>
    <p><strong>Row 2:</strong> Atlantic Ocean (the rest are countries).</p>
    <p><strong>Row 3:</strong> Australia (the rest are animals; Australia is a place — though a fair debate, since Australia is also a country!).</p>
    <p><strong>Row 4:</strong> Kenya (the rest are oceans).</p>
    <p><strong>Row 5:</strong> Ocean (the rest are tools/items you use to find or record places you've been).</p>
    <p><strong>Row 6:</strong> France (the rest are continents).</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Which place would you most want to visit for real?"</em></p>
    <p>Purely a personal-response question — use it to gauge which day's content stuck with Christopher most and to plan a real-world follow-up (a library book, a documentary clip, a themed dinner) about that place.</p>
  </div>
  <h3>Game Notes — Capstone Board Game</h3>
  <div class="game-note">
    <p>This game only works as well as the map/passport built across the week, so budget a few extra minutes Friday to finish any unglued pieces before playing. If the week's cut-out cards got scattered, any of the week's vocabulary works as an improvised trivia question — the format matters far more than a fixed question bank.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>By Friday, check that "continent," "ocean," and "country" haven't blurred into one interchangeable word for "a big place." The Odd One Out worksheet is the direct check for this — if Christopher struggles with it, it's worth a quick verbal review (not re-reading) of each term's definition before moving on.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Keep the map poster up on a wall after this week ends. Add a new sticky-note pin any time a book, show, food, or person connects to a new place — turning one week's project into an ongoing family geography habit.</p>
  </div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2 class="fri">Week Summary — Causal Chain</h2>
  <p>The week followed this chain of ideas, each nesting inside the last:</p>
  <ol style="padding-left: 20px; font-size: 10pt; line-height: 2;">
    <li><strong>Monday:</strong> Maps and globes both represent Earth; water covers most of the planet.</li>
    <li><strong>Tuesday:</strong> Earth's land is divided into 7 continents, each in a different direction from the others.</li>
    <li><strong>Wednesday:</strong> Earth's water is divided into 5 connected oceans that surround and link the continents.</li>
    <li><strong>Thursday:</strong> Continents are divided further into countries, each with its own identity and symbolic animal.</li>
    <li><strong>Friday:</strong> All four layers — maps/globes, continents, oceans, countries — fit together into one world, reviewed through a capstone game on a map Christopher built by hand.</li>
  </ol>
  <p style="margin-top: 10px;">By Friday, Christopher should be able to name most of the 7 continents and 5 oceans unprompted, and explain that a country is a smaller piece of land inside a continent — not a synonym for one.</p>
</div>

</body>
</html>"""

    guide_path = output_dir / "geography_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print("\nSuccessfully generated Geography Week.")
    print(f"Student packet:  {out_path}")
    print(f"Teacher guide:   {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Mon p1 — Reading: Maps, Globes, and Our Watery World",
        "Mon p2 — Word Sort: Land or Water?",
        "Mon p3 — Game & Build: Beach-Ball Globe Toss + Start the Map",
        "Tue p1 — Reading: The Seven Continents",
        "Tue p2 — Matching: The Seven Continents",
        "Tue p3 — Game & Build: Continent Hopscotch + Add Continents",
        "Wed p1 — Reading: The Five Oceans",
        "Wed p2 — Feature Matrix: The Five Oceans",
        "Wed p3 — Game & Build: Ocean Bean-Bag Toss + Label Oceans",
        "Thu p1 — Reading: Countries and Their Animals",
        "Thu p2 — Tree Map: Countries & Animals",
        "Thu p3 — Game & Build: Passport Stamp Rally + Add Countries",
        "Fri p1 — Reading: A Trip Around the World (Capstone)",
        "Fri p2 — Odd One Out: Continents, Oceans & Countries",
        "Fri p3 — Capstone Game: The Great Big Trip Around the World",
        "         — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")


if __name__ == "__main__":
    generate_geography_week_series()
