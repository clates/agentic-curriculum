"""
Weather — Week Series
Grade K–1 | Science | Causal Arc: Sun's Energy → Atmosphere & Clouds → Water Cycle → Wind & Pressure → Weather Patterns & Forecasting

Narrator: Zara the Zebra Finch, introduced on Monday. A small speckled bird who flies through
every kind of weather and notices how the sky changes each day.
Output: single printable HTML document — weather_week_series/weather_week.html

Standards (Virginia SOL):
  Monday    — K.9, K.9.a   (weather conditions: sun, clouds, temperature)
  Tuesday   — K.9.a, K.9.b (cloud types, precipitation)
  Wednesday — K.9.c, 1.6   (water cycle: evaporation, condensation, precipitation)
  Thursday  — K.9.b, 1.6.a (wind: direction, speed, pressure)
  Friday    — K.9, K.9.a–d (capstone: weather patterns, forecasting, weather tools)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html


def generate_weather_week_series():
    output_dir = Path("weather_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []  # (day_label, html_fragment)

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — The Sun Heats Our World
    # Standards: K.9, K.9.a — weather conditions, role of the sun
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: The Sun Heats Our World",
            "passage_title": "Meet Zara — and Why the Sun Matters!",
            "instructions": (
                "Before reading: Go outside for two minutes. Stand in the sun, then in the shade. "
                "Feel the difference! Come back inside and share what you noticed."
            ),
            "passage": (
                "Meet Zara the Zebra Finch! Zara is a small speckled bird with an orange beak and "
                "a striped tail. Every morning, Zara wakes up on her branch and checks the sky before "
                "she flies out to find seeds. 'What will the weather be like today?' she chirps.\n\n"
                "Zara knows that everything about weather starts with the Sun. The Sun is a giant ball "
                "of burning gas far away in space, and it sends energy all the way to Earth as light "
                "and heat. When sunlight reaches Earth, it warms the ground, the water, and the air "
                "above it. The more directly the Sun shines on a spot, the warmer it gets.\n\n"
                "On a sunny day, Zara feels warm and cozy in the sunlight. The air around her is "
                "warmer too, which means the air temperature is high. Temperature tells us how warm "
                "or cold the air feels. We measure temperature with a thermometer. When there are "
                "no clouds and the Sun shines all day, we call that a clear or sunny day.\n\n"
                "But the Sun's energy does more than just warm us up — it also drives everything else "
                "about weather. Without the Sun, there would be no wind, no rain, and no clouds. "
                "Every storm, every rainbow, and every gentle breeze on Earth starts with the energy "
                "our Sun provides. 'It all begins with the Sun,' Zara tweets to herself as she spreads "
                "her wings and soars into the bright blue sky."
            ),
            "vocabulary": [
                {
                    "term": "weather",
                    "definition": "What the air outside is like right now — sunny, cloudy, rainy, windy, or snowy.",
                },
                {
                    "term": "temperature",
                    "definition": "How warm or cold the air is. We measure temperature with a thermometer.",
                },
                {
                    "term": "thermometer",
                    "definition": "A tool that shows how warm or cold the air is.",
                },
                {
                    "term": "energy",
                    "definition": "The power the Sun sends to Earth as light and heat.",
                },
                {
                    "term": "sunny",
                    "definition": "A day with no clouds blocking the Sun, so the sky looks bright blue and clear.",
                },
            ],
            "questions": [
                {
                    "prompt": "Where does all of Earth's weather energy come from?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What is temperature, and what tool do we use to measure it?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What did you notice when you stood in the sun vs. the shade before the lesson?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: If the Sun suddenly turned off, what do you think would happen to the weather on Earth? Explain your thinking!",
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    add(
        "wordSortWorksheet",
        {
            "title": "Monday: Sunny Days and Cloudy Days — Word Sort",
            "instructions": (
                "Look at each weather word in the word bank. "
                "Write it in the correct box — does it go with Sunny Weather or Cloudy / Rainy Weather?"
            ),
            "categories": [{"label": "Sunny Weather"}, {"label": "Cloudy / Rainy Weather"}],
            "tiles": [
                "Bright sky",
                "Rain puddles",
                "Warm air",
                "Gray clouds",
                "Clear sky",
                "Thunderstorm",
                "Rainbows",
                "Cool shade",
                "Hot sidewalk",
                "Wet grass",
            ],
        },
        "Monday",
    )

    # =========================================================================
    # TUESDAY — Clouds and Precipitation
    # Standards: K.9.a, K.9.b — clouds as water droplets, types of precipitation
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: Clouds and Precipitation",
            "passage_title": "What Are Clouds Made Of?",
            "instructions": (
                "Read about clouds with Zara. Then answer the questions below.\n\n"
                "Outdoor observation: Look up at the sky today. Are there clouds? "
                "Are they fluffy and white, thin and wispy, or flat and gray? "
                "Remember what you saw for the feature matrix activity."
            ),
            "passage": (
                "Zara was zooming through the sky when she flew right through a low, "
                "soft cloud. 'It feels like flying through a cold, wet fog!' she chirped in surprise. "
                "That is exactly what clouds are — millions of tiny water droplets or ice crystals "
                "floating together in the air. Clouds form when warm, wet air rises and cools down. "
                "As the air cools, the water vapor in it turns into tiny droplets — that is called "
                "condensation. Those droplets clump together to make a cloud.\n\n"
                "Not all clouds look the same! Cumulus clouds are the big, puffy, white clouds "
                "that look like cotton balls piled up in the sky. They usually mean fair, sunny weather. "
                "Stratus clouds are flat, gray sheets that spread out low across the sky like a blanket. "
                "They often bring light rain or drizzle. Cirrus clouds are thin, wispy streaks high up "
                "in the sky, made of ice crystals. They look like feathers or horse tails.\n\n"
                "When clouds hold too much water, the water falls back to Earth as precipitation. "
                "Precipitation is any form of water that falls from clouds. It can be rain (liquid), "
                "snow (frozen flakes), sleet (frozen rain drops), or hail (balls of ice). "
                "Zara loves flying after a rain shower — the air smells fresh and clean, "
                "and sometimes a beautiful rainbow appears when sunlight shines through the raindrops!"
            ),
            "vocabulary": [
                {
                    "term": "cloud",
                    "definition": "Millions of tiny water droplets or ice crystals floating together in the air.",
                },
                {
                    "term": "condensation",
                    "definition": "When water vapor in warm air cools down and turns into tiny droplets — how clouds form.",
                },
                {
                    "term": "precipitation",
                    "definition": "Any water that falls from clouds to the ground — rain, snow, sleet, or hail.",
                },
                {
                    "term": "cumulus",
                    "definition": "Puffy, white, cotton-ball clouds — usually mean fair weather.",
                },
                {
                    "term": "stratus",
                    "definition": "Flat, gray, blanket-like clouds that often bring drizzle or light rain.",
                },
                {
                    "term": "cirrus",
                    "definition": "Thin, wispy, feathery clouds high in the sky, made of ice crystals.",
                },
            ],
            "questions": [
                {"prompt": "What are clouds made of? How do they form?", "response_lines": 3},
                {
                    "prompt": "Describe the three cloud types from the passage. Which one usually means good weather?",
                    "response_lines": 3,
                },
                {
                    "prompt": "Name four types of precipitation. How are rain and snow different?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: If you see dark, flat stratus clouds rolling in, what do you think the weather will be like soon? Would you change any plans because of it?",
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "featureMatrixWorksheet",
        {
            "title": "Tuesday: Cloud Types — What Do You Know?",
            "instructions": (
                "Put a check mark in every box that describes each cloud type. "
                "Use your reading card to help — look for clues in the passage!"
            ),
            "items": ["Cumulus", "Stratus", "Cirrus"],
            "properties": [
                "Puffy and white",
                "Flat and gray",
                "Thin and wispy",
                "High in the sky",
                "Low in the sky",
                "Made of ice crystals",
                "Brings fair weather",
                "Brings rain or drizzle",
            ],
        },
        "Tuesday",
    )

    # =========================================================================
    # WEDNESDAY — The Water Cycle
    # Standards: K.9.c, 1.6 — evaporation, condensation, precipitation
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: The Water Cycle",
            "passage_title": "Water's Amazing Journey — Up and Down, Again and Again",
            "instructions": (
                "Read about the water cycle with Zara. Then answer the questions below.\n\n"
                "Hands-on activity: Pour a small puddle of water on the sidewalk in the sun. "
                "Check it every 15 minutes. Where does the water go? "
                "What happened — was the water cycle at work?"
            ),
            "passage": (
                "Zara watched a rain puddle on the sidewalk every morning for a week. "
                "'The puddle was big on Monday,' she chirped, 'but by Wednesday it was gone! "
                "Where did all that water go?' The answer is the water cycle — "
                "one of the most important patterns in all of nature.\n\n"
                "The water cycle has three main steps. Step 1 is EVAPORATION. "
                "The Sun heats water in puddles, ponds, lakes, rivers, and oceans. "
                "That heat turns liquid water into an invisible gas called water vapor, "
                "which floats up into the air. This is what happened to Zara's puddle!\n\n"
                "Step 2 is CONDENSATION. As the water vapor floats higher into the sky, "
                "the air up there is colder. Cold air cannot hold as much water vapor, "
                "so the vapor cools down and turns back into tiny liquid droplets. "
                "Those droplets clump together — and they form clouds!\n\n"
                "Step 3 is PRECIPITATION. When clouds collect enough water droplets, "
                "the drops get heavy and fall back to Earth as rain, snow, sleet, or hail. "
                "The water soaks into the ground, fills rivers and lakes, "
                "and then the whole cycle begins again with evaporation. "
                "'So the water in this puddle,' said Zara with wide eyes, "
                "'might have once been in the ocean, then in a cloud, and now it is back on the ground! "
                "And it will do that journey over and over, forever.'"
            ),
            "vocabulary": [
                {
                    "term": "water cycle",
                    "definition": "The never-ending journey of water from Earth's surface up into the sky and back down again.",
                },
                {
                    "term": "evaporation",
                    "definition": "When heat turns liquid water into water vapor — an invisible gas that rises into the air.",
                },
                {
                    "term": "water vapor",
                    "definition": "Water in its gas form — invisible, it rises into the sky when liquid water is heated.",
                },
                {
                    "term": "condensation",
                    "definition": "When water vapor cools down and turns back into tiny liquid droplets to form clouds.",
                },
                {
                    "term": "precipitation",
                    "definition": "Water that falls from clouds to the ground — rain, snow, sleet, or hail.",
                },
            ],
            "questions": [
                {
                    "prompt": "What are the three steps of the water cycle? List them in order.",
                    "response_lines": 3,
                },
                {"prompt": "What is evaporation? What causes it?", "response_lines": 2},
                {
                    "prompt": "What causes condensation to happen up in the sky?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Why do the same water molecules keep going through the cycle over and over?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: Zara says the water in a puddle might once have been in the ocean. Do you think that is really true? Could water from a cloud over your town have started in the Pacific Ocean?",
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "causeEffectWorksheet",
        {
            "title": "Wednesday: Water Cycle — Cause and Effect",
            "instructions": (
                "Each cause describes something that happens in the water cycle. "
                "Write the effect — what happens next? Use your reading card if you need a clue."
            ),
            "pairs": [
                {
                    "cause": "The Sun heats a puddle of water on the sidewalk.",
                    "effect": "",
                    "effect_lines": 2,
                },
                {
                    "cause": "Water vapor rises high into the cold upper air.",
                    "effect": "",
                    "effect_lines": 2,
                },
                {
                    "cause": "A cloud collects enough water droplets to become heavy.",
                    "effect": "",
                    "effect_lines": 2,
                },
                {
                    "cause": "Rain falls on a mountain and flows into a river.",
                    "effect": "",
                    "effect_lines": 2,
                },
            ],
        },
        "Wednesday",
    )

    # =========================================================================
    # THURSDAY — Wind and Air Pressure
    # Standards: K.9.b, 1.6.a — wind direction, speed, how pressure differences cause wind
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: Wind and Air Pressure",
            "passage_title": "Why Does the Wind Blow?",
            "instructions": (
                "Read about wind with Zara. Then answer the questions below.\n\n"
                "Outdoor activity: Go outside and lick your finger. Hold it up in the air. "
                "The side that feels cooler is the direction the wind is coming FROM. "
                "Which direction is the wind blowing today?"
            ),
            "passage": (
                "Zara spread her wings and felt a strong gust of wind. It lifted her higher in the "
                "sky without her even flapping! 'Wind is so helpful,' she sang, 'but where does it "
                "come from?' The answer starts with temperature.\n\n"
                "Remember that the Sun does not heat all parts of Earth equally. "
                "Land heats up faster than water, and dark surfaces warm faster than light ones. "
                "When a patch of ground gets warm, the air above it gets warm too. "
                "Warm air is lighter than cool air, so warm air RISES — like a hot-air balloon. "
                "As the warm air rises, it leaves behind an area of lower air pressure. "
                "Air pressure is the weight of air pressing down on the ground.\n\n"
                "Cool air nearby is heavier and has higher pressure. "
                "High-pressure air always moves toward low-pressure areas — "
                "it rushes in to fill the space left by the rising warm air. "
                "THAT rushing movement of air is the WIND. The bigger the difference in pressure, "
                "the stronger the wind blows.\n\n"
                "We measure wind with special tools. An anemometer measures wind SPEED "
                "— how fast the wind is blowing, in miles per hour. "
                "A weather vane shows wind DIRECTION — the direction the wind is coming FROM. "
                "If a weather vane points north, the wind is blowing FROM the north (called a north wind). "
                "Zara loved riding the warm thermals — rising columns of warm air — "
                "that helped her soar across the sky without tiring her wings!"
            ),
            "vocabulary": [
                {
                    "term": "wind",
                    "definition": "Moving air — caused when high-pressure air rushes into a low-pressure area.",
                },
                {
                    "term": "air pressure",
                    "definition": "The weight of air pressing down on the ground. Warm air has low pressure; cool air has high pressure.",
                },
                {
                    "term": "anemometer",
                    "definition": "A weather tool that measures wind speed — how fast the wind is blowing.",
                },
                {
                    "term": "weather vane",
                    "definition": "A weather tool that spins and points to show the direction the wind is coming from.",
                },
                {
                    "term": "thermal",
                    "definition": "A rising column of warm air — birds like Zara ride thermals to soar without flapping.",
                },
            ],
            "questions": [
                {
                    "prompt": "What causes wind? Explain in your own words using 'warm air' and 'pressure'.",
                    "response_lines": 3,
                },
                {
                    "prompt": "What is the difference between an anemometer and a weather vane?",
                    "response_lines": 3,
                },
                {
                    "prompt": "If the weather vane points south, which direction is the wind blowing FROM?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Why can Zara soar without flapping when she finds a thermal?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: On a hot summer day at the beach, the sand heats up faster than the ocean. Which way do you think the wind blows — from land to sea, or from sea to land? Why?",
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    add(
        "matchingWorksheet",
        {
            "title": "Thursday: Weather Tools and Wind Words — Matching",
            "instructions": (
                "Draw a line from each weather word or tool on the left to its correct meaning on the right."
            ),
            "left_items": [
                "Anemometer",
                "Weather vane",
                "Air pressure",
                "Thermal",
                "Wind",
                "High pressure",
            ],
            "right_items": [
                "Measures how fast the wind is blowing",
                "Points to show where wind comes FROM",
                "The weight of air pressing on the ground",
                "A rising column of warm air birds ride",
                "Moving air caused by pressure differences",
                "Found where air is cool and heavy",
            ],
        },
        "Thursday",
    )

    # =========================================================================
    # FRIDAY — Weather Patterns and Forecasting (Capstone)
    # Standards: K.9, K.9.a–d — putting it all together, weather forecasting
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: Weather Patterns and Forecasting",
            "passage_title": "How Do Meteorologists Predict the Weather?",
            "instructions": (
                "Read the capstone passage with Zara. Then answer the questions.\n\n"
                "Capstone activity: Before starting, write down today's weather without looking at a "
                "forecast. After the lesson, look up tomorrow's forecast online or on TV. "
                "What weather tools helped the meteorologist make that prediction?"
            ),
            "passage": (
                "Zara had been watching the sky all week and she felt like she was getting very good "
                "at guessing what the weather would do next. 'I think I am becoming a meteorologist!' "
                "she chirped proudly. A meteorologist is a scientist who studies weather and makes "
                "forecasts — predictions about what the weather will be like in the future.\n\n"
                "Meteorologists have learned that weather follows patterns. "
                "A weather pattern is when the same kind of weather happens in the same way, over and over. "
                "For example, in many parts of the United States, summer afternoons often bring "
                "thunderstorms — because the hot ground heats the air, which rises, forms big storm clouds, "
                "and then the rain falls. That is the water cycle and wind working together!\n\n"
                "Meteorologists use many special tools to collect data about the weather. "
                "A thermometer measures temperature. A rain gauge is a small container that collects "
                "and measures how much rain has fallen. An anemometer measures wind speed. "
                "A barometer measures air pressure — when pressure drops quickly, a storm is often coming! "
                "Weather satellites in space take pictures of clouds over huge areas of Earth, "
                "and weather stations on the ground send data to computers every hour.\n\n"
                "All of these measurements are put together into giant computer models that predict "
                "how the atmosphere will change over the next few days. That is how meteorologists "
                "can tell you whether to bring an umbrella tomorrow. "
                "Zara ruffled her feathers and looked at the clouds building in the west. "
                "'I predict rain by evening,' she tweeted — and she was right!"
            ),
            "vocabulary": [
                {
                    "term": "meteorologist",
                    "definition": "A scientist who studies weather and makes forecasts.",
                },
                {
                    "term": "forecast",
                    "definition": "A prediction about what the weather will be like in the future.",
                },
                {
                    "term": "weather pattern",
                    "definition": "Weather that repeats in a predictable way — like summer afternoon thunderstorms.",
                },
                {
                    "term": "rain gauge",
                    "definition": "A tool that collects and measures how much rain has fallen.",
                },
                {
                    "term": "barometer",
                    "definition": "A tool that measures air pressure — a quick pressure drop often means a storm is coming.",
                },
                {
                    "term": "data",
                    "definition": "Measurements and facts collected by weather tools — meteorologists use data to make forecasts.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is a meteorologist? What is a weather forecast?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Name four weather tools described in the passage. What does each one measure?",
                    "response_lines": 4,
                },
                {
                    "prompt": "What does it mean for weather to follow a 'pattern'? Give one example from the passage.",
                    "response_lines": 3,
                },
                {
                    "prompt": "How do all of this week's topics — Sun, clouds, water cycle, and wind — work together to create a thunderstorm? Explain the chain!",
                    "response_lines": 4,
                },
                {
                    "prompt": "LET'S DISCUSS: If a barometer reading drops sharply in the morning, what should you predict for the afternoon — and would you change any outdoor plans?",
                    "response_lines": 0,
                },
            ],
        },
        "Friday",
    )

    add(
        "treeMapWorksheet",
        {
            "title": "Friday: Weather Tools — Tree Map Capstone",
            "instructions": (
                "Sort each weather word or tool from the word bank into the correct branch. "
                "Each item belongs in only one branch — think about what it measures or describes!"
            ),
            "root_label": "Weather Science",
            "branches": [
                {"label": "Measuring Tools", "slot_count": 4},
                {"label": "Water Cycle Steps", "slot_count": 3},
                {"label": "Cloud Types", "slot_count": 3},
            ],
            "columns": 3,
            "word_bank": [
                "Thermometer",
                "Evaporation",
                "Cumulus",
                "Rain gauge",
                "Condensation",
                "Stratus",
                "Anemometer",
                "Precipitation",
                "Cirrus",
                "Barometer",
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
            "title": "End-of-Week Parent Feedback — Weather Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this feedback sheet after the week wraps up. "
                "Your notes help shape next week's lessons."
            ),
            "passage": (
                "This week followed a causal arc through Earth's weather. "
                "Monday established that all weather energy comes from the Sun, and introduced "
                "the idea of temperature. Tuesday explored how clouds form through condensation "
                "and the different types of precipitation. Wednesday traced the full water cycle "
                "— evaporation, condensation, precipitation — as a continuous loop powered by the Sun. "
                "Thursday explained wind as the movement of air from high pressure to low pressure, "
                "caused by unequal heating. Friday pulled everything together with weather patterns "
                "and forecasting — how meteorologists use tools and data to predict the weather.\n\n"
                "Zara the Zebra Finch appeared throughout the week as a friendly narrator, "
                "experiencing the weather from a bird's-eye view that gave concrete, relatable examples "
                "for each concept.\n\n"
                "Key concepts to check for genuine understanding — not just recall:\n"
                "1) The Sun is the ultimate energy source for all weather.\n"
                "2) Clouds form through condensation, not just 'water in the sky'.\n"
                "3) The water cycle is continuous — the same water molecules keep cycling.\n"
                "4) Wind is caused by pressure differences, not just 'air moving'.\n"
                "5) Meteorologists use multiple tools and look for patterns — forecasting is data-driven.\n\n"
                "Common misconceptions to watch for:\n"
                "• 'Rain comes from the ocean' (partially true, but water vapor can come from any liquid water).\n"
                "• 'Clouds are made of steam' (they are made of tiny liquid droplets or ice, not steam).\n"
                "• 'Wind blows toward the warmer area' (wind blows FROM high pressure INTO low pressure — "
                "toward the warmer, less dense air).\n\n"
                "Suggested follow-on activities: keep a five-day weather journal; look up the local "
                "barometer reading each morning and see if low pressure really does predict rain; "
                "watch a TV weather forecast together and identify all the tools and maps used."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": "Clouds are NOT made of steam — they are made of tiny liquid water droplets or ice crystals formed through condensation.",
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in after the week — which idea did Christopher grasp best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": "Seasons and climate — why do some places get more sun? How does the Sun's angle change throughout the year?",
                },
            ],
            "questions": [
                {
                    "prompt": "Overall comfort with the week's content — how well did Christopher grasp the concepts? (1 = struggled throughout, 5 = strong grasp of all concepts)",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which day's lesson generated the most curiosity or questions?",
                    "response_lines": 2,
                },
                {
                    "prompt": "By Friday, could Christopher explain the full chain: Sun → evaporation → cloud → rain → wind?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Did any weather events happen during the week (a real rain shower, wind, clouds) that you connected to the lessons in real time?",
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

    html = build_print_packet_html(pages, packet_title="Weather Week — Science for Christopher")
    out_path = output_dir / "weather_week.html"
    out_path.write_text(html, encoding="utf-8")

    # Teacher guide
    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Weather Week — Teacher Guide</title>
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
  <h1>Weather Week — Teacher / Parent Guide</h1>
  <p><strong>Theme:</strong> Weather &nbsp;|&nbsp; <strong>Audience:</strong> Christopher, age 6, K–1 &nbsp;|&nbsp;
  <strong>Narrator:</strong> Zara the Zebra Finch</p>
  <p><strong>Causal Arc:</strong> Sun's Energy &rarr; Atmosphere &amp; Clouds &rarr; Water Cycle &rarr; Wind &amp; Pressure &rarr; Weather Patterns &amp; Forecasting</p>

  <h2>Monday — The Sun Heats Our World</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1 (Energy source):</strong> All of Earth's weather energy comes from the Sun. It sends light and heat energy to Earth.</p>
    <p><strong>Q2 (Temperature):</strong> Temperature is how warm or cold the air is. We measure it with a thermometer.</p>
    <p><strong>Q3 (Outdoor observation):</strong> Personal response — student should note feeling warmer in sunlight and cooler in shade. Guide them to connect this to the passage's explanation of direct sunlight warming surfaces.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"If the Sun turned off, what would happen to the weather?"</em></p>
    <p>Expected reasoning: No energy = no evaporation, no wind, no rain. Earth would get very cold very quickly. All weather would stop. There is no single right answer here — encourage logical chaining of causes.</p>
  </div>
  <h3>Word Sort Answer Key</h3>
  <div class="answer-box">
    <p><strong>Sunny:</strong> Bright sky, Warm air, Clear sky, Rainbows, Hot sidewalk</p>
    <p><strong>Cloudy/Rainy:</strong> Rain puddles, Gray clouds, Thunderstorm, Cool shade, Wet grass</p>
    <p><em>Note: "Rainbows" appear after rain (so rainy could be argued) but rainbows require sunlight — accept either category with good reasoning.</em></p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Students often think the Sun "warms the air directly." Emphasize that the Sun first warms the GROUND and WATER, and the ground/water then warms the air above it. This matters for understanding wind formation on Thursday.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Set up two small cups of water in the same spot — one covered with black paper, one uncovered white. Check the temperature of each after 20 minutes of sunlight. Why is the black cup warmer? (Darker surfaces absorb more solar energy.)</p>
  </div>

  <h2 class="tue">Tuesday — Clouds and Precipitation</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box tue">
    <p><strong>Q1 (Cloud formation):</strong> Clouds are made of millions of tiny water droplets or ice crystals. They form when warm, wet air rises, cools, and the water vapor undergoes condensation — turning into droplets that clump together.</p>
    <p><strong>Q2 (Cloud types):</strong> Cumulus = puffy, white, fair weather. Stratus = flat, gray, light rain or drizzle. Cirrus = thin, wispy, high up, made of ice. Cumulus usually means good weather.</p>
    <p><strong>Q3 (Precipitation):</strong> Rain (liquid), snow (frozen flakes), sleet (frozen rain drops), hail (balls of ice). Rain is liquid; snow is solid frozen water crystals — different temperatures cause different forms.</p>
  </div>
  <h3>Feature Matrix Answer Key</h3>
  <div class="answer-box tue">
    <p><strong>Cumulus:</strong> Puffy and white ✓, Brings fair weather ✓, Low in the sky ✓</p>
    <p><strong>Stratus:</strong> Flat and gray ✓, Low in the sky ✓, Brings rain or drizzle ✓</p>
    <p><strong>Cirrus:</strong> Thin and wispy ✓, High in the sky ✓, Made of ice crystals ✓</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"If you see dark stratus clouds rolling in, what will the weather be like?"</em></p>
    <p>Expected: Rain or drizzle is likely soon. Students may want to bring an umbrella, move activities indoors, or cover outdoor plants. The goal is to practice applying cloud-type knowledge to real-world decisions.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"Clouds are made of steam." Correct this clearly: clouds are tiny LIQUID droplets (or ice crystals), not steam. Steam is invisible hot water vapor. When you see a visible cloud, condensation has already happened.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Cloud journaling: Print or draw the three cloud types. For three consecutive days, go outside and draw which cloud type you see. Did the clouds correctly predict the weather that followed?</p>
  </div>
</div>

<div class="page">
  <h2 class="wed">Wednesday — The Water Cycle</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1 (Three steps):</strong> 1) Evaporation — Sun heats water, turns it to vapor. 2) Condensation — vapor rises, cools, forms clouds. 3) Precipitation — water falls as rain/snow/sleet/hail.</p>
    <p><strong>Q2 (Evaporation):</strong> Evaporation is when heat turns liquid water into invisible water vapor gas. Heat from the Sun causes it.</p>
    <p><strong>Q3 (Condensation cause):</strong> Higher in the sky, the air is colder. Cold air cannot hold as much water vapor, so the vapor cools and turns back into liquid droplets — condensation.</p>
    <p><strong>Q4 (Continuous cycle):</strong> The same water keeps cycling because it is never destroyed — it just changes form (liquid → gas → liquid again) and location, driven by the Sun's energy.</p>
  </div>
  <h3>Cause-and-Effect Answer Key</h3>
  <div class="answer-box wed">
    <p><strong>Cause 1 → Effect:</strong> The water evaporates — turns into invisible water vapor and rises into the air.</p>
    <p><strong>Cause 2 → Effect:</strong> The vapor cools down and condenses into tiny water droplets, forming a cloud.</p>
    <p><strong>Cause 3 → Effect:</strong> The droplets become too heavy and fall as precipitation — rain, snow, sleet, or hail.</p>
    <p><strong>Cause 4 → Effect:</strong> The water soaks into the ground, refills lakes and rivers, and the water cycle begins again with evaporation.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Could water from a cloud over your town have started in the Pacific Ocean?"</em></p>
    <p>Yes! Winds carry water vapor thousands of miles. Ocean water evaporates, vapor travels inland, condenses into clouds, and falls as rain far from the original source. This is a wonderful real-world demonstration that the water cycle operates at a global scale.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Students may think rain "comes from clouds" as though clouds are containers that get filled with new water. Clarify that clouds ARE condensed water vapor — the water was already in the atmosphere before the cloud formed.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Mini water cycle in a bag: Put a small amount of water in a sealed clear plastic bag and tape it to a sunny window. Over several hours, watch evaporation (water disappearing from the bottom), condensation (drops on the top of the bag), and "precipitation" (drops running back down). Narrate each step as Zara would!</p>
  </div>

  <h2 class="thu">Thursday — Wind and Air Pressure</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1 (Cause of wind):</strong> The Sun heats the ground unevenly. Warm ground heats the air above it. Warm air is lighter and rises, creating a low-pressure area. Nearby cool, heavy high-pressure air rushes in to fill that space — that rushing air is wind.</p>
    <p><strong>Q2 (Anemometer vs. weather vane):</strong> Anemometer measures wind SPEED (how fast). Weather vane shows wind DIRECTION (which way the wind is coming from).</p>
    <p><strong>Q3 (Wind direction):</strong> If the weather vane points south, the wind is blowing FROM the south — a south wind.</p>
    <p><strong>Q4 (Thermal):</strong> A thermal is a column of rising warm air. Zara can spread her wings and let the rising air carry her upward without having to flap — the air does the lifting work.</p>
  </div>
  <h3>Matching Answer Key</h3>
  <div class="answer-box thu">
    <p>Anemometer → Measures how fast the wind is blowing</p>
    <p>Weather vane → Points to show where wind comes FROM</p>
    <p>Air pressure → The weight of air pressing on the ground</p>
    <p>Thermal → A rising column of warm air birds ride</p>
    <p>Wind → Moving air caused by pressure differences</p>
    <p>High pressure → Found where air is cool and heavy</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"At the beach, which way does the wind blow — land to sea or sea to land?"</em></p>
    <p>During a hot day, the sand heats faster than the water (land is hotter, lower pressure). The sea air is cooler (higher pressure) and blows toward the lower-pressure land — this is called a sea breeze. Wind blows FROM the sea TO the land. At night, it reverses (land cools faster than sea).</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Students often say "wind blows toward the hot area" — technically true, but the mechanism is: hot air rises (creating LOW pressure), and wind blows FROM high pressure INTO low pressure. The wind is moving INTO the hot area, but it is the pressure difference that causes the movement, not the heat directly.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Make a simple weather vane: tape a paper arrow to a straw and push the straw into a lump of clay or an eraser. Take it outside and observe which direction the arrow points (it points INTO the wind, showing the wind's source direction). Compare to a weather app to check accuracy.</p>
  </div>
</div>

<div class="page">
  <h2 class="fri">Friday — Weather Patterns and Forecasting (Capstone)</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1 (Meteorologist / Forecast):</strong> A meteorologist is a scientist who studies weather and makes forecasts. A forecast is a prediction about what the weather will be like in the future.</p>
    <p><strong>Q2 (Four tools):</strong> Thermometer = temperature; Rain gauge = how much rain fell; Anemometer = wind speed; Barometer = air pressure. (Also: weather vane = wind direction; weather satellite = cloud images from space.)</p>
    <p><strong>Q3 (Weather pattern):</strong> A pattern is weather that repeats predictably. Example from passage: summer afternoons often bring thunderstorms because hot ground heats air → warm air rises → storm clouds form → rain falls.</p>
    <p><strong>Q4 (Chain: Sun → thunderstorm):</strong> Sun heats the ground → ground heats the air → warm air evaporates water from surfaces → moist warm air rises (wind) → air cools at altitude → condensation forms clouds → water accumulates in cloud → precipitation falls as rain → back to ground. Accept any reasonable causal chain connecting all four topics.</p>
  </div>
  <h3>Tree Map Answer Key</h3>
  <div class="answer-box fri">
    <p><strong>Measuring Tools (4):</strong> Thermometer, Rain gauge, Anemometer, Barometer</p>
    <p><strong>Water Cycle Steps (3):</strong> Evaporation, Condensation, Precipitation</p>
    <p><strong>Cloud Types (3):</strong> Cumulus, Stratus, Cirrus</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"If the barometer drops sharply, what do you predict for the afternoon?"</em></p>
    <p>A rapid drop in air pressure means a low-pressure system is approaching — which typically brings cloudy skies, wind, and rain or storms. Practical decisions: bring an umbrella, move outdoor activities earlier, close windows. This is a great opportunity to check a real barometer app and make a real prediction together.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"Weather forecasts are just guesses." Clarify that forecasts are data-driven predictions based on measurements and computer models — they are much more accurate than guessing, especially for 1–3 days out. The more data tools we have, the better the forecast.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Five-day weather journal: Each morning for one week, record temperature, cloud type, wind direction, and precipitation. At the end of the week, look back — can you identify a pattern? Compare your observations to the official forecast each day and score accuracy.</p>
  </div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2 class="fri">Week Summary — Causal Chain</h2>
  <p>The week followed this chain of causes:</p>
  <ol style="padding-left: 20px; font-size: 10pt; line-height: 2;">
    <li><strong>Monday:</strong> The Sun provides all weather energy; heats the ground, air, and water.</li>
    <li><strong>Tuesday:</strong> Heat causes evaporation; rising moist air cools and condenses into clouds; clouds produce precipitation.</li>
    <li><strong>Wednesday:</strong> The full water cycle — evaporation → condensation → precipitation → repeat.</li>
    <li><strong>Thursday:</strong> Uneven heating creates pressure differences; air moves from high to low pressure = wind.</li>
    <li><strong>Friday:</strong> All these forces together create weather patterns; meteorologists measure and predict them.</li>
  </ol>
  <p style="margin-top: 10px;">By Friday, Christopher should be able to trace the path from sunlight on the ground to a rainstorm without prompting — and name at least four weather tools.</p>
</div>

</body>
</html>"""

    guide_path = output_dir / "weather_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print("\nSuccessfully generated Weather Week.")
    print(f"Student packet:  {out_path}")
    print(f"Teacher guide:   {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Mon p1 — Reading: The Sun Heats Our World",
        "Mon p2 — Word Sort: Sunny vs. Cloudy/Rainy Weather",
        "Tue p1 — Reading: Clouds and Precipitation",
        "Tue p2 — Feature Matrix: Cloud Types",
        "Wed p1 — Reading: The Water Cycle",
        "Wed p2 — Cause and Effect: Water Cycle Stages",
        "Thu p1 — Reading: Wind and Air Pressure",
        "Thu p2 — Matching: Weather Tools and Wind Words",
        "Fri p1 — Reading: Weather Patterns and Forecasting (Capstone)",
        "Fri p2 — Tree Map: Weather Science Capstone",
        "         — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")


if __name__ == "__main__":
    generate_weather_week_series()
