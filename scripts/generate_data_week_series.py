"""
Data Detectives — Week Series
Grade 1-2 | Science + Data & Graphing | Causal Arc:
  Observe & Count -> Record Data in a Table -> Show Data as a Pictograph ->
  Show & Read Data as a Bar Graph -> Run a Full Experiment and Graph the Results

Narrator: Dot the Ladybug, introduced on Monday. A tiny scientist who loves counting
her spots — and everything else. Dot teaches that a scientist is a "data detective":
someone who observes, counts, records, graphs, and then reads what the graph is telling them.

Heavy focus: MAKING graphs (blank grids + blank pictographs the student fills in from
data they collect) and READING graphs (pre-filled pictographs and bar graphs with
"most / least / how many more / how many altogether" interpretation questions).

Standards:
  Monday    — CCSS 1.MD.C.4 (organize & represent data), NGSS SEP: Analyzing & Interpreting Data
              (observe, count, record data in a tally table)
  Tuesday   — CCSS 2.MD.D.10 (draw a picture graph), 1.MD.C.4 (ask/answer questions about data)
  Wednesday — CCSS 2.MD.D.10 (draw a bar graph up to four categories), NGSS K-2: fair test
  Thursday  — CCSS 2.MD.D.10 / 1.MD.C.4 (read bar graph & pictograph: how many more, total)
  Friday    — CCSS 2.MD.D.10 (capstone: collect, graph, and interpret own experiment data)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html


def generate_data_week_series():
    output_dir = Path("data_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []  # (day_label, html_fragment)

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — Scientists Observe and Count (collect data in a table)
    # CCSS 1.MD.C.4 · NGSS SEP: Analyzing & Interpreting Data
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: Data Detectives",
            "passage_title": "Meet Dot the Ladybug!",
            "instructions": (
                "Before reading: Go outside or look out a window for two minutes. "
                "Count how many birds, cars, or clouds you see. Come back and tell someone your number!"
            ),
            "passage": (
                "Meet Dot! Dot is a little red ladybug with six black spots. Dot loves to count. "
                "First she counts her own spots: one, two, three, four, five, six! Then she counts "
                "everything else she sees.\n\n"
                "Dot says, 'A scientist is a data detective.' What is data? Data is facts you collect "
                "by watching and counting. When you count how many red cars drive by, that number is data!\n\n"
                "Dot has a smart trick for counting. She uses tally marks. Each thing she counts gets "
                "one little line: | . When she gets to five, she draws a line across the group, like this: "
                "||||. Tally marks help her count fast without losing her place.\n\n"
                "Dot writes her tally marks in a table. A table has rows and boxes to keep data neat and "
                "tidy. When Dot's table is full, she can look at it and see what she found out. "
                "'Good scientists write it down,' says Dot. 'If you do not record your data, you might "
                "forget it!'"
            ),
            "vocabulary": [
                {
                    "term": "tally mark",
                    "definition": "A little line ( | ) you draw to count one thing. Five is drawn as ||||.",
                },
                {
                    "term": "data",
                    "definition": "Facts you collect by watching and counting.",
                },
                {
                    "term": "scientist",
                    "definition": "A person who observes, counts, and finds out how things work.",
                },
                {
                    "term": "table",
                    "definition": "Rows and boxes that keep your data neat and easy to read.",
                },
                {
                    "term": "record",
                    "definition": "To write your data down so you do not forget it.",
                },
            ],
            "questions": [
                {"prompt": "What is data? Give one example.", "response_lines": 2},
                {"prompt": "Why does Dot use tally marks when she counts?", "response_lines": 2},
                {
                    "prompt": "Why does a good scientist write down (record) their data?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: If Dot counted 20 bugs but did not write it down, "
                        "and then took a nap, what might happen? Why is recording data so important?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    add(
        "tChartWorksheet",
        {
            "title": "Monday: My Counting Experiment",
            "instructions": (
                "Be a data detective like Dot! Pick ONE thing from the word bank to hunt for around "
                "your home or yard. Write what you counted on the left. On the right, make a tally mark "
                "( | ) for each one you find. Then write the total number. Fill in as many rows as you can!"
            ),
            "columns": ["What I Counted", "Tally Marks and Total"],
            "row_count": 8,
            "word_bank": [
                "Windows",
                "Doors",
                "Red things",
                "Round things",
                "Chairs",
                "Books",
                "Spoons",
                "Shoes",
            ],
        },
        "Monday",
    )

    # =========================================================================
    # TUESDAY — Pictographs (read one, then make one)
    # CCSS 2.MD.D.10 · 1.MD.C.4
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: Picture Graphs",
            "passage_title": "Dot Draws Her Data",
            "instructions": (
                "Read with Dot. Then get ready to read and make picture graphs on the next two pages."
            ),
            "passage": (
                "Dot counted lots of data. Now she wants to SHOW it so everyone can see it fast. "
                "So Dot made a pictograph. A pictograph is a graph that uses pictures to show data.\n\n"
                "In Dot's pictograph, each little picture stands for a number. Every pictograph has a "
                "key at the top. The key tells you what one picture is worth. Dot's key says: each "
                "ladybug picture = 1 ladybug. So if a row has 5 ladybug pictures, that means 5 ladybugs!\n\n"
                "Pictographs are easy to read. The row with the MOST pictures is the biggest group. "
                "The row with the FEWEST pictures is the smallest group. You can even count how many "
                "MORE one row has than another by looking at the extra pictures.\n\n"
                "Sometimes a scientist has BIG numbers. Then each picture can stand for 2, or 5, or 10! "
                "Always read the key first. The key is the secret code for the whole graph. "
                "'Read the key, then you can read me,' sings Dot."
            ),
            "vocabulary": [
                {
                    "term": "pictograph",
                    "definition": "A graph that uses pictures to show data. Also called a picture graph.",
                },
                {
                    "term": "key",
                    "definition": "The part of a graph that tells you what one picture is worth.",
                },
                {
                    "term": "most",
                    "definition": "The biggest group — the row with the most pictures.",
                },
                {
                    "term": "fewest",
                    "definition": "The smallest group — the row with the fewest pictures.",
                },
                {
                    "term": "row",
                    "definition": "A line of pictures that goes across, one for each group.",
                },
            ],
            "questions": [
                {"prompt": "What does a pictograph use to show data?", "response_lines": 1},
                {"prompt": "Why should you always read the key first?", "response_lines": 2},
                {
                    "prompt": "In a pictograph, how can you tell which group is the biggest?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Dot's key says each picture = 2 bugs. A row has 4 pictures. "
                        "How many bugs is that? What if the key changed to each picture = 5?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "pictographWorksheet",
        {
            "title": "Tuesday: Read Dot's Ladybug Graph",
            "instructions": (
                "Dot counted the ladybugs she saw each day. Read her pictograph, then answer the "
                "questions. Read the key first!"
            ),
            "symbol": "🐞",
            "per_symbol": 1,
            "unit_label": "ladybugs",
            "rows": [
                {"label": "Monday", "symbols": 5},
                {"label": "Tuesday", "symbols": 3},
                {"label": "Wednesday", "symbols": 6},
                {"label": "Thursday", "symbols": 2},
                {"label": "Friday", "symbols": 4},
            ],
            "questions": [
                {"prompt": "Which day did Dot see the MOST ladybugs?", "response_lines": 1},
                {"prompt": "Which day did Dot see the FEWEST ladybugs?", "response_lines": 1},
                {
                    "prompt": "How many MORE ladybugs did Dot see on Wednesday than on Thursday?",
                    "response_lines": 1,
                },
                {
                    "prompt": "How many ladybugs did Dot see on Monday and Tuesday put together?",
                    "response_lines": 1,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "pictographWorksheet",
        {
            "title": "Tuesday: Make Your Own Pictograph",
            "instructions": (
                "Dot counted the flowers in her garden: 4 Roses, 6 Tulips, and 3 Daisies. "
                "Show her data! Draw one 🌸 in the row for each flower she counted. "
                "The key tells you each 🌸 = 1 flower."
            ),
            "symbol": "🌸",
            "per_symbol": 1,
            "unit_label": "flower",
            "blank": True,
            "max_symbols": 8,
            "rows": [
                {"label": "Roses (4)"},
                {"label": "Tulips (6)"},
                {"label": "Daisies (3)"},
            ],
            "questions": [
                {
                    "prompt": "After you draw it: which flower has the LONGEST row? What does that mean?",
                    "response_lines": 2,
                },
            ],
        },
        "Tuesday",
    )

    # =========================================================================
    # WEDNESDAY — Bar Graphs (do an experiment, then make a bar graph)
    # CCSS 2.MD.D.10 · NGSS K-2: fair test
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: Bar Graphs",
            "passage_title": "Dot Builds Bars",
            "instructions": (
                "Read with Dot. Then do the Ramp Race experiment and turn your data into a bar graph!"
            ),
            "passage": (
                "Dot learned a new way to show data: a bar graph. A bar graph uses bars instead of "
                "pictures. A bar is a tall rectangle you color in. The taller the bar, the bigger "
                "the number!\n\n"
                "A bar graph has two sides called axes. The bottom axis tells you the groups you are "
                "counting, like Low, Medium, and High. The side axis has numbers that go up: "
                "1, 2, 3, and more. To read a bar, you look at how high it reaches on the number side.\n\n"
                "Every good graph also has a title at the top. The title tells you what the graph is "
                "about. Without a title, you would not know what all the bars mean!\n\n"
                "Dot loves bar graphs because you can see the answer with your eyes. The tallest bar "
                "jumps right out at you. 'One quick look,' says Dot, 'and I know which group won!'"
            ),
            "vocabulary": [
                {
                    "term": "bar graph",
                    "definition": "A graph that uses tall bars to show data. Taller bars mean bigger numbers.",
                },
                {
                    "term": "bar",
                    "definition": "A rectangle you color in. Its height shows how many.",
                },
                {
                    "term": "axis",
                    "definition": "A side of the graph. The bottom shows the groups; the side shows the numbers.",
                },
                {
                    "term": "title",
                    "definition": "The name at the top of a graph that tells what it is about.",
                },
                {
                    "term": "tallest",
                    "definition": "The highest bar — it shows the biggest number.",
                },
            ],
            "questions": [
                {"prompt": "In a bar graph, what does a taller bar mean?", "response_lines": 1},
                {
                    "prompt": "What do the two axes tell you? (bottom axis and side axis)",
                    "response_lines": 2,
                },
                {"prompt": "Why does every graph need a title?", "response_lines": 2},
                {
                    "prompt": (
                        "LET'S DISCUSS: Dot says a bar graph lets you 'see the answer with your eyes.' "
                        "Is a bar graph or a big list of numbers easier to read quickly? Why?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "tChartWorksheet",
        {
            "title": "Wednesday: Ramp Race — Collect Your Data",
            "instructions": (
                "EXPERIMENT: Prop a book or board to make a ramp. Roll a toy car (or ball) down it. "
                "Do it three times: a LOW ramp (1 book), a MEDIUM ramp (2 books), and a HIGH ramp "
                "(3 books). Each time, count how many BIG STEPS the car rolls. Write your steps here. "
                "Keep everything else the same so it is a fair test!"
            ),
            "columns": ["Ramp Height", "How Far It Rolled (big steps)"],
            "row_count": 3,
            "word_bank": ["Low ramp", "Medium ramp", "High ramp"],
        },
        "Wednesday",
    )

    add(
        "barGraphWorksheet",
        {
            "title": "Wednesday: Ramp Race — Make a Bar Graph",
            "instructions": (
                "Now show your Ramp Race data! Color one bar for each ramp. Make each bar as tall as "
                "the number of steps the car rolled. Count the lines on the side to get it just right."
            ),
            "categories": ["Low ramp", "Medium ramp", "High ramp"],
            "y_max": 10,
            "y_step": 1,
            "x_label": "Ramp Height",
            "y_label": "How far it rolled (steps)",
            "height_in": 2.6,
            "questions": [
                {
                    "prompt": "Which ramp made the car roll the FARTHEST? Circle its bar.",
                    "response_lines": 1,
                },
                {
                    "prompt": "What happened to the car's distance as the ramp got higher?",
                    "response_lines": 2,
                },
            ],
        },
        "Wednesday",
    )

    # =========================================================================
    # THURSDAY — Reading & Comparing Graphs (interpret bar graph AND pictograph)
    # CCSS 2.MD.D.10 · 1.MD.C.4
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: Reading Graphs Like a Scientist",
            "passage_title": "What Is the Graph Telling You?",
            "instructions": (
                "Read with Dot. Then read a bar graph and a pictograph on the next two pages and "
                "answer the questions."
            ),
            "passage": (
                "Making a graph is only half the job. A data detective must also READ the graph to "
                "find out what it means. Dot asks herself four questions every time.\n\n"
                "First: Which group is the MOST? That is the tallest bar or the longest row. "
                "Second: Which group is the LEAST? That is the shortest bar or the shortest row.\n\n"
                "Third: How many MORE does one group have than another? To find out, Dot finds each "
                "number and subtracts the smaller from the bigger. If one bar is 8 and another is 5, "
                "then 8 take away 5 is 3 more.\n\n"
                "Fourth: How many ALTOGETHER? Dot adds up all the groups to get the total. "
                "When you can answer these four questions, you truly understand your data. "
                "'A graph is a story,' says Dot. 'Reading it tells you what happened!'"
            ),
            "vocabulary": [
                {
                    "term": "compare",
                    "definition": "To look at two groups and see how they are different — more or less.",
                },
                {
                    "term": "how many more",
                    "definition": "The difference between two groups. Subtract the smaller from the bigger.",
                },
                {
                    "term": "altogether",
                    "definition": "The total when you add all the groups up.",
                },
                {
                    "term": "least",
                    "definition": "The smallest group — the shortest bar or row.",
                },
                {
                    "term": "difference",
                    "definition": "How far apart two numbers are. You find it by subtracting.",
                },
            ],
            "questions": [
                {
                    "prompt": "What are the four questions Dot asks when she reads a graph?",
                    "response_lines": 3,
                },
                {
                    "prompt": "To find how many MORE one bar has than another, what do you do?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Dot says 'a graph is a story.' What story might a graph of your "
                        "bedtime each night tell? What would the tallest bar mean?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    add(
        "barGraphWorksheet",
        {
            "title": "Thursday: Read the Seed Graph",
            "instructions": (
                "Dot planted the same seeds in three spots. This bar graph shows how many seeds "
                "sprouted in each spot. Read the bars, then answer the questions."
            ),
            "categories": ["Shade", "Some sun", "Full sun"],
            "values": [2, 5, 8],
            "y_max": 10,
            "y_step": 1,
            "x_label": "Where the seeds grew",
            "y_label": "Seeds that sprouted",
            "height_in": 2.6,
            "show_values": False,
            "questions": [
                {"prompt": "Which spot had the MOST seeds sprout?", "response_lines": 1},
                {"prompt": "Which spot had the FEWEST seeds sprout?", "response_lines": 1},
                {
                    "prompt": "How many MORE seeds sprouted in Full sun than in Shade?",
                    "response_lines": 1,
                },
                {
                    "prompt": "How many seeds sprouted ALTOGETHER in all three spots?",
                    "response_lines": 1,
                },
                {
                    "prompt": "What does this graph tell you that plants need to grow well?",
                    "response_lines": 2,
                },
            ],
        },
        "Thursday",
    )

    add(
        "pictographWorksheet",
        {
            "title": "Thursday: Read the Garden Bug Graph",
            "instructions": (
                "Dot counted the bugs in the garden. Careful — this key is tricky! "
                "Each 🐛 stands for 2 bugs. Read the key, then answer the questions."
            ),
            "symbol": "🐛",
            "per_symbol": 2,
            "unit_label": "bugs",
            "rows": [
                {"label": "Ants", "symbols": 4},
                {"label": "Bees", "symbols": 2},
                {"label": "Worms", "symbols": 3},
            ],
            "questions": [
                {"prompt": "How many ANTS did Dot find? (each picture = 2!)", "response_lines": 1},
                {"prompt": "How many BEES did Dot find?", "response_lines": 1},
                {"prompt": "How many MORE ants were there than bees?", "response_lines": 1},
                {"prompt": "How many bugs did Dot find ALTOGETHER?", "response_lines": 1},
            ],
        },
        "Thursday",
    )

    # =========================================================================
    # FRIDAY — Capstone: Be a Data Scientist (full cycle)
    # CCSS 2.MD.D.10 — collect, graph, and interpret your own data
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: Be a Data Scientist!",
            "passage_title": "Dot's Big Experiment",
            "instructions": (
                "Read with Dot. Then do the Paper Airplane Contest, record your data, graph it, "
                "and read your own graph. You are a real data detective now!"
            ),
            "passage": (
                "This week Dot learned every step a data detective takes. Today she does them ALL. "
                "Dot follows five steps.\n\n"
                "Step 1: ASK a question. Dot asks, 'Which paper airplane flies the farthest?'\n"
                "Step 2: DO an experiment. Dot folds three planes and flies each one.\n"
                "Step 3: RECORD the data. Dot writes down how far each plane flew in a table.\n\n"
                "Step 4: GRAPH the data. Dot makes a bar graph so she can see it fast.\n"
                "Step 5: READ the graph. Dot finds the tallest bar and answers her question!\n\n"
                "'Ask, do, record, graph, read,' says Dot. 'That is how a scientist finds an answer.' "
                "Now it is your turn to fly some planes and graph what happens. Ready, data detective?"
            ),
            "vocabulary": [
                {
                    "term": "experiment",
                    "definition": "A test you do to find out the answer to a question.",
                },
                {
                    "term": "question",
                    "definition": "What you want to find out. Every experiment starts with one.",
                },
                {
                    "term": "fair test",
                    "definition": "Keeping everything the same except the one thing you are testing.",
                },
                {
                    "term": "graph",
                    "definition": "A picture of your data that makes it easy to read.",
                },
                {
                    "term": "results",
                    "definition": "What you found out after your experiment — your data.",
                },
            ],
            "questions": [
                {
                    "prompt": "What are Dot's five steps? (Ask, Do, Record, Graph, Read)",
                    "response_lines": 3,
                },
                {"prompt": "What question is Dot trying to answer today?", "response_lines": 1},
                {
                    "prompt": (
                        "LET'S DISCUSS: To make it a FAIR test, what should stay the same each time you "
                        "throw a plane? (Think: who throws it, from where, how hard.)"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Friday",
    )

    add(
        "tChartWorksheet",
        {
            "title": "Friday: Paper Airplane Contest — Record Your Data",
            "instructions": (
                "EXPERIMENT: Fold three paper airplanes — a Dart, a Glider, and a Wide-wing. "
                "Throw each one from the same spot. Count how many BIG STEPS each plane flew. "
                "Throw each plane one time and write your data here. Remember: keep it a fair test!"
            ),
            "columns": ["Airplane", "How Far It Flew (big steps)"],
            "row_count": 3,
            "word_bank": ["Dart", "Glider", "Wide-wing"],
        },
        "Friday",
    )

    add(
        "barGraphWorksheet",
        {
            "title": "Friday: Paper Airplane Contest — Graph and Read It",
            "instructions": (
                "Show your airplane data! Color one bar for each plane, as tall as the number of steps "
                "it flew. Then read YOUR OWN graph to answer the questions below."
            ),
            "categories": ["Dart", "Glider", "Wide-wing"],
            "y_max": 12,
            "y_step": 2,
            "x_label": "Paper Airplane",
            "y_label": "How far it flew (steps)",
            "height_in": 2.6,
            "questions": [
                {
                    "prompt": "Which airplane flew the FARTHEST? Circle its bar.",
                    "response_lines": 1,
                },
                {"prompt": "Which airplane flew the SHORTEST distance?", "response_lines": 1},
                {
                    "prompt": "How many MORE steps did your farthest plane fly than your shortest plane?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Look at your graph. What is the ANSWER to Dot's question?",
                    "response_lines": 2,
                },
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
            "title": "End-of-Week Parent Feedback — Data Detectives Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this after the week wraps up. Your notes help shape next week's lessons."
            ),
            "passage": (
                "This week built the full data cycle for a 1st-2nd grade scientist, one step per day. "
                "Monday introduced observing, counting with tally marks, and recording data in a table. "
                "Tuesday taught pictographs — reading a graph with a simple key, then drawing one. "
                "Wednesday introduced bar graphs, axes, and titles, paired with the hands-on Ramp Race "
                "experiment. Thursday focused on READING graphs: most, least, how many more (subtract), "
                "and how many altogether (add), using both a bar graph and a trickier pictograph where "
                "each picture stood for 2. Friday tied it together — the child ran a full Paper Airplane "
                "experiment, recorded data, built a bar graph, and interpreted their own results.\n\n"
                "Dot the Ladybug narrated the week as a friendly 'data detective,' repeating the mantra "
                "'Ask, do, record, graph, read.'\n\n"
                "Key skills to check for real understanding — not just recall:\n"
                "1) A graph needs a title and (for pictographs) a key.\n"
                "2) Taller bar / longer row = bigger number.\n"
                "3) 'How many more' is a subtraction; 'altogether' is addition.\n"
                "4) On a scaled pictograph (each picture = 2), you must multiply, not just count pictures.\n"
                "5) A fair test keeps everything the same except the one thing being tested.\n\n"
                "Common bumps to watch for:\n"
                "- Counting pictures instead of using the key when each picture = 2.\n"
                "- Making bars different widths, or not starting bars at the bottom line (zero).\n"
                "- Forgetting to title the graph or label what each bar/row is.\n\n"
                "Follow-on ideas: graph the weather for five days; graph how many minutes of reading "
                "each night; re-run the Ramp Race changing only the surface (carpet vs. floor)."
            ),
            "vocabulary": [
                {
                    "term": "Key Skill to Confirm",
                    "definition": "On a pictograph where each picture = 2, the child multiplies (does not just count pictures).",
                },
                {
                    "term": "Strongest Skill This Week",
                    "definition": "(Fill in after the week — which step did the child grasp best: count, record, make, or read?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": "Measurement — using rulers and units so the data we graph is even more exact.",
                },
            ],
            "questions": [
                {
                    "prompt": (
                        "Overall, how well did the child grasp making and reading graphs? "
                        "(1 = struggled, 5 = strong)"
                    ),
                    "response_lines": 1,
                },
                {
                    "prompt": "Which experiment (Ramp Race or Paper Airplanes) created the most excitement?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "Could the child answer 'how many more?' by subtracting, and 'altogether?' by adding?"
                    ),
                    "response_lines": 2,
                },
                {
                    "prompt": "Was the scaled pictograph (each picture = 2) tricky? How did it go?",
                    "response_lines": 2,
                },
                {"prompt": "Skills or vocabulary to revisit next week:", "response_lines": 2},
            ],
        },
        "Friday",
    )

    # =========================================================================
    # Assemble & write
    # =========================================================================

    html = build_print_packet_html(
        pages, packet_title="Data Detectives Week — Science & Graphing for Grades 1-2"
    )
    out_path = output_dir / "data_week.html"
    out_path.write_text(html, encoding="utf-8")

    guide_path = output_dir / "data_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print("\nSuccessfully generated Data Detectives Week.")
    print(f"Student packet:  {out_path}")
    print(f"Teacher guide:   {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Mon p1 — Reading: Data Detectives (meet Dot; tally marks, tables)",
        "Mon p2 — T-Chart: My Counting Experiment (collect tally data)",
        "Tue p1 — Reading: Picture Graphs (pictographs & the key)",
        "Tue p2 — Pictograph (READ): Dot's Ladybug Graph + questions",
        "Tue p3 — Pictograph (MAKE): draw the flower data",
        "Wed p1 — Reading: Bar Graphs (bars, axes, title)",
        "Wed p2 — T-Chart: Ramp Race experiment (collect data)",
        "Wed p3 — Bar Graph (MAKE): graph the Ramp Race data",
        "Thu p1 — Reading: Reading Graphs Like a Scientist (most/least/more/altogether)",
        "Thu p2 — Bar Graph (READ): Seed graph + questions",
        "Thu p3 — Pictograph (READ): Garden bugs, each picture = 2 + questions",
        "Fri p1 — Reading: Be a Data Scientist (ask-do-record-graph-read)",
        "Fri p2 — T-Chart: Paper Airplane Contest (collect data)",
        "Fri p3 — Bar Graph (MAKE + READ): graph & interpret your own results",
        "        — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")


# =============================================================================
# Teacher / Parent Guide (self-contained HTML, day-color headings)
# =============================================================================

TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Data Detectives Week — Teacher Guide</title>
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
    .misconception { background: #fff3cd; border-left: 4px solid #d97706; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .extension { background: #e8f5e9; border-left: 4px solid #15803d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .discuss { background: #fce7f3; border-left: 4px solid #9d174d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .vary { background: #eef2ff; border-left: 4px solid #4338ca; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 9.5pt; }
  </style>
</head>
<body>

<div class="page">
  <h1>Data Detectives Week &mdash; Teacher / Parent Guide</h1>
  <p><strong>Theme:</strong> Science &amp; Graphing &nbsp;|&nbsp; <strong>Audience:</strong> Grades 1&ndash;2 &nbsp;|&nbsp;
  <strong>Narrator:</strong> Dot the Ladybug</p>
  <p><strong>Causal Arc:</strong> Observe &amp; Count &rarr; Record in a Table &rarr; Pictograph &rarr; Bar Graph &rarr; Full Experiment &amp; Interpret</p>
  <p><strong>Standards:</strong> CCSS.Math 1.MD.C.4 &amp; 2.MD.D.10 (represent and interpret data); NGSS K&ndash;2 science practices (planning investigations; analyzing &amp; interpreting data).</p>
  <div class="vary">
    <p><strong>Many activities are open-ended experiments</strong> (Ramp Race, Paper Airplanes) and the "make a graph" pages. For those, there is no single answer key &mdash; instead, check that the child's bars/pictures match the numbers they recorded in their data table, that bars start at the bottom line (zero) and are the same width, and that the graph has a title and labels.</p>
  </div>

  <h2>Monday &mdash; Data Detectives (Observe, Count, Record)</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1 (Data):</strong> Data is facts you collect by watching and counting. Example: the number of red cars that drive by, how many birds you see, etc.</p>
    <p><strong>Q2 (Tally marks):</strong> They help you count quickly and keep your place; grouping by fives ( |||| ) makes big counts easy.</p>
    <p><strong>Q3 (Recording):</strong> So you do not forget the data. Scientists must be able to look back at what they found.</p>
  </div>
  <h3>Counting Experiment (T-Chart)</h3>
  <div class="answer-box">
    <p>Open-ended. Child picks one thing to count and records tally marks + a total per row. Check that the total matches the tally marks (count the fives). Great chance to reinforce counting by fives.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"If Dot counted 20 bugs but did not write it down&hellip;"</em> &mdash; She would likely forget the exact number. Reinforce: recording data is what separates guessing from real science.</p>
  </div>
  <h3>Misconception to Watch</h3>
  <div class="misconception">
    <p>Some children draw the fifth tally as a separate line instead of the cross-line ( |||| ). Model the group-of-five so totals are easy to read.</p>
  </div>
  <h3>Extension</h3>
  <div class="extension">
    <p>Count two things at once (e.g., cars vs. trucks for 5 minutes) to set up tomorrow's idea of comparing groups on a graph.</p>
  </div>

  <h2 class="tue">Tuesday &mdash; Pictographs</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box tue">
    <p><strong>Q1:</strong> Pictures (a pictograph uses pictures to show data).</p>
    <p><strong>Q2:</strong> The key tells what one picture is worth &mdash; without it you can't know the real numbers.</p>
    <p><strong>Q3:</strong> The group with the most pictures / the longest row is the biggest.</p>
  </div>
  <h3>Read Dot's Ladybug Graph (each &#128028; = 1)</h3>
  <div class="answer-box tue">
    <p><strong>Most:</strong> Wednesday (6). &nbsp; <strong>Fewest:</strong> Thursday (2).</p>
    <p><strong>How many more Wed than Thu:</strong> 6 &minus; 2 = <strong>4</strong>.</p>
    <p><strong>Monday + Tuesday:</strong> 5 + 3 = <strong>8</strong>.</p>
  </div>
  <h3>Make Your Own Pictograph</h3>
  <div class="answer-box tue">
    <p>Roses = 4 &#127800;, Tulips = 6 &#127800;, Daisies = 3 &#127800;. Longest row = Tulips (the most flowers). Check that the child draws exactly the right number in each row.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>Key = 2 bugs, row has 4 pictures &rarr;</em> 4 &times; 2 = <strong>8 bugs</strong>. If the key were 5 each: 4 &times; 5 = <strong>20</strong>. Plants the seed for Thursday's scaled pictograph.</p>
  </div>
  <h3>Misconception to Watch</h3>
  <div class="misconception">
    <p>Children may ignore the key and just count pictures. Keep pointing back to the key: "What is one picture worth?"</p>
  </div>
  <h3>Extension</h3>
  <div class="extension">
    <p>Turn Monday's counting data into a pictograph on scrap paper &mdash; their own data becomes a graph.</p>
  </div>
</div>

<div class="page">
  <h2 class="wed">Wednesday &mdash; Bar Graphs (Ramp Race)</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1:</strong> A taller bar means a bigger number (more).</p>
    <p><strong>Q2:</strong> Bottom axis = the groups you are counting; side axis = the numbers (how many).</p>
    <p><strong>Q3:</strong> The title tells you what the graph is about, so the bars have meaning.</p>
  </div>
  <h3>Ramp Race Experiment + Bar Graph</h3>
  <div class="answer-box wed">
    <p><strong>Open-ended data.</strong> Typical result: the higher the ramp, the farther the car rolls, so bars increase Low &rarr; Medium &rarr; High. Check that each bar's height matches the steps recorded in the data table, bars are equal width, and each starts at the zero line.</p>
    <p><em>Graph Q's:</em> Farthest = usually the High ramp. As the ramp got higher, the car rolled farther (more starting height &rarr; more speed &rarr; more distance).</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>Graph vs. a list of numbers:</em> The bar graph is faster &mdash; the tallest bar is visible instantly, while a list must be read and compared number by number.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Bars floating above the line, uneven widths, or gaps of different sizes. Also stress the <em>fair test</em>: same car, same push (just release it), only the ramp height changes.</p>
  </div>
  <h3>Extension</h3>
  <div class="extension">
    <p>Re-run with the SAME ramp height but a different surface (carpet vs. wood). Add those bars &mdash; which surface let the car roll farther?</p>
  </div>

  <h2 class="thu">Thursday &mdash; Reading &amp; Comparing Graphs</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1 (Four questions):</strong> Which is the most? Which is the least? How many more? How many altogether?</p>
    <p><strong>Q2 (How many more):</strong> Find both numbers and subtract the smaller from the bigger.</p>
  </div>
  <h3>Seed Bar Graph (Shade 2, Some sun 5, Full sun 8)</h3>
  <div class="answer-box thu">
    <p><strong>Most:</strong> Full sun (8). &nbsp; <strong>Fewest:</strong> Shade (2).</p>
    <p><strong>More Full sun than Shade:</strong> 8 &minus; 2 = <strong>6</strong>.</p>
    <p><strong>Altogether:</strong> 2 + 5 + 8 = <strong>15</strong>.</p>
    <p><strong>What plants need:</strong> more sunlight helps more seeds sprout / grow.</p>
  </div>
  <h3>Garden Bug Pictograph (each &#128027; = 2)</h3>
  <div class="answer-box thu">
    <p><strong>Ants:</strong> 4 &times; 2 = <strong>8</strong>. &nbsp; <strong>Bees:</strong> 2 &times; 2 = <strong>4</strong>. &nbsp; <strong>Worms:</strong> 3 &times; 2 = 6.</p>
    <p><strong>More ants than bees:</strong> 8 &minus; 4 = <strong>4</strong>.</p>
    <p><strong>Altogether:</strong> 8 + 4 + 6 = <strong>18</strong> bugs.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"A graph is a story."</em> A bedtime graph's tallest bar = the night with the latest bedtime. Encourage the child to narrate what the graph "says" happened.</p>
  </div>
  <h3>Misconception to Watch</h3>
  <div class="misconception">
    <p>On the bug pictograph, children often answer 4, 2, 3 (the picture counts) instead of 8, 4, 6. Anchor every answer to the key: "each picture = 2, so&hellip;"</p>
  </div>
  <h3>Extension</h3>
  <div class="extension">
    <p>Ask "how many fewer bees than ants?" and "how many more ants than worms?" to practice comparison in both directions.</p>
  </div>
</div>

<div class="page">
  <h2 class="fri">Friday &mdash; Be a Data Scientist (Capstone)</h2>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1 (Five steps):</strong> Ask &rarr; Do &rarr; Record &rarr; Graph &rarr; Read.</p>
    <p><strong>Q2 (Question):</strong> "Which paper airplane flies the farthest?"</p>
  </div>
  <h3>Paper Airplane Contest (data table + bar graph)</h3>
  <div class="answer-box fri">
    <p><strong>Open-ended data.</strong> Check the full cycle: the data table has a distance for each plane; the bar graph's bars match those numbers (equal width, starting at zero, titled); and the child reads their OWN graph to answer.</p>
    <p><em>Graph Q's:</em> Farthest / shortest = whichever plane the child's bars show. "How many more" = subtract the shortest from the farthest. The ANSWER to Dot's question = the name of the tallest bar.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>Fair test:</em> same person throwing, same starting line, same amount of push, same paper size. Only the plane design changes.</p>
  </div>
  <h3>Misconception to Watch</h3>
  <div class="misconception">
    <p>Throwing planes different numbers of times or from different spots, then comparing &mdash; that is not a fair test. One throw each from the same line keeps it fair (or best-of-three, but the same for every plane).</p>
  </div>
  <h3>Extension</h3>
  <div class="extension">
    <p>Throw each plane THREE times and graph the best distance &mdash; introduces the idea of repeating a trial for more trustworthy data.</p>
  </div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2 class="fri">Week Summary &mdash; The Data Cycle</h2>
  <ol style="padding-left: 20px; font-size: 10pt; line-height: 1.9;">
    <li><strong>Monday:</strong> Observe and count; record data with tally marks in a table.</li>
    <li><strong>Tuesday:</strong> Show data as a pictograph; read the key; make one.</li>
    <li><strong>Wednesday:</strong> Show data as a bar graph; axes, title; graph a real experiment.</li>
    <li><strong>Thursday:</strong> Read graphs &mdash; most, least, how many more (subtract), altogether (add); scaled key.</li>
    <li><strong>Friday:</strong> Run a full experiment &mdash; ask, do, record, graph, read &mdash; and interpret your own results.</li>
  </ol>
  <p style="margin-top: 10px;">By Friday, the child should be able to collect a small set of data, build a titled bar graph or pictograph whose sizes match the data, and answer "which is most/least," "how many more," and "how many altogether."</p>
</div>

</body>
</html>"""


if __name__ == "__main__":
    generate_data_week_series()
