"""
Sports Reporter — Week Series
Grade K-1 | English/Language Arts + Math | Causal Arc:
  Learn a sport's rules -> report on a real game -> learn another sport's rules ->
  report on a second real game -> compare both stories -> assemble the finished column

Narrator: Christopher himself, as "Rookie Reporter Christopher" — he keeps a running reporter's
notebook all week. Each day adds one entry (~1.5 paragraphs) built from sentence-starter scaffolds,
so the writing load stays light day to day even though the finished piece is long by Friday.

Grounded in real events (per parent request — no fantasy framing this week):
  - Christopher's own first baseball game of the season (personal/family event, generic details —
    the passage and notebook page are templated so the parent/child fill in the specifics together)
  - NFL: Buffalo Bills 36, Houston Texans 31 (Sept 13, 2026) — Josh Allen threw a 34-yard
    game-winning TD pass to Joshua Palmer with 1:36 remaining in a back-and-forth game
  - NFL: Las Vegas Raiders 27, Miami Dolphins 13 (Sept 13, 2026) — Raiders never trailed; opened
    with a 16-play, 93-yard, 8:58 drive; Kirk Cousins threw 3 TD passes, Ashton Jeanty ran for
    102 yards + 2 TDs

Output: single printable HTML document — sports_reporter_week_series/sports_reporter_week.html
Pacing: ~2 hours/day this week (parent request, above the student's usual ~90 min/day default).

Standards (Virginia SOL):
  Monday    — ENGLISH K.c.2.a (describe personal experience), ENGLISH 1.1.w.1.a (recount events),
              MATH K.6 (single-step sums to 10)
  Tuesday   — ENGLISH 1.1.ri.1.a (literal/inferential questions), ENGLISH 1.1.w.1.a (recount events),
              MATH 1.1.6 (addition/subtraction within 20)
  Wednesday — ENGLISH 1.1.ri.1.a, ENGLISH 1.1.w.1.a, MATH 1.1.10 (nonstandard units of length)
  Thursday  — ENGLISH 1.1.ri.3.a (compare two texts on same topic), ENGLISH 1.1.w.1.c (opinion +
              reason), MATH 1.1.6 (subtraction within 20)
  Friday    — ENGLISH K.w.1.a / 1.1.w.1.a (capstone recount), ENGLISH K.rl.1.c (oral sequential
              retell), MATH K.11 (collect/represent data — pictograph)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html


def generate_sports_reporter_week_series():
    output_dir = Path("sports_reporter_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []  # (day_label, html_fragment)

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — Play Ball! (his own baseball game)
    # Standards: ENGLISH K.c.2.a, ENGLISH 1.1.w.1.a, MATH K.6
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: Play Ball — My First Game of the Season",
            "passage_title": "Meet Rookie Reporter Christopher",
            "instructions": (
                "Before reading: talk with a grown-up for two minutes about your game this "
                "weekend — what position did you play, and who did you play against?\n\n"
                "Hands-on activity (after this page): head outside and play catch, or walk the "
                "bases if you can mark some out with rocks, cones, or towels."
            ),
            "passage": (
                "Every big sports story starts with someone who watches closely and writes down "
                "what happened. This week, YOU are the reporter. Your first assignment is the "
                "easiest one of all — you already lived it! This weekend, you played in your very "
                "first baseball game of the season.\n\n"
                "Before a reporter can write about a game, they have to know the rules. In "
                "baseball, each team takes turns batting and fielding. A batter tries to hit the "
                "ball and run around the bases — first base, second base, third base, and home "
                "plate. If a runner makes it all the way around without being stopped, that is a "
                "run!\n\n"
                "There are two main ways to get an OUT. If a fielder catches your hit ball before "
                "it touches the ground, that's an out. If a fielder tags you with the ball before "
                "you reach a base, that's an out too. Each team gets three outs in an INNING "
                "before it becomes the other team's turn to bat.\n\n"
                "A HIT means the batter reached a base safely. A HOME RUN is the best hit of all — "
                "it means the ball flew so far, often over the fence, that the batter could run "
                "around every base at once. Now that you know the rules, it's time to write your "
                "very first sports story — about your own game!"
            ),
            "vocabulary": [
                {
                    "term": "home run",
                    "definition": "A hit so good the batter runs all the way around every base without stopping — often the ball flies over the fence!",
                },
                {
                    "term": "out",
                    "definition": "When a batter or runner is stopped and their turn ends. A team gets three outs before it's the other team's turn to bat.",
                },
                {
                    "term": "inning",
                    "definition": "A round of the game where both teams get a turn to bat.",
                },
                {
                    "term": "base",
                    "definition": "A safe spot a runner can stand on — first, second, third, or home plate.",
                },
                {
                    "term": "hit",
                    "definition": "When a batter hits the ball and reaches a base safely.",
                },
            ],
            "questions": [
                {
                    "prompt": "What are two different ways a batter or runner can get an OUT?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What is the difference between a HIT and a HOME RUN?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Math: If your team got 3 outs in the first inning and 3 outs in the second inning, how many outs is that altogether?",
                    "response_lines": 1,
                },
                {
                    "prompt": "LET'S DISCUSS: Real sports reporters ask players questions after the game, like 'How did you feel when...?' What is one question you would want a reporter to ask YOU about your game this weekend?",
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    add(
        "writingScaffoldWorksheet",
        {
            "title": "Monday: My Game Day Story — Reporter's Notebook, Entry 1",
            "instructions": (
                "This is page one of your reporter's notebook — it will grow every day this "
                "week! Write or dictate your answers in complete sentences, just like a real "
                "reporter."
            ),
            "topic": "My First Game of the Season",
            "sections": [
                {
                    "label": "The Facts (Who, What, When, Where)",
                    "starter": "This weekend I played baseball. I was on the ______ team. We played against ______.",
                    "lines": 3,
                },
                {
                    "label": "The Biggest Play",
                    "starter": "The most exciting part of the game was when...",
                    "lines": 3,
                },
                {
                    "label": "How I Felt",
                    "starter": "When it happened, I felt...",
                    "lines": 2,
                },
            ],
        },
        "Monday",
    )

    add(
        "matchingWorksheet",
        {
            "title": "Monday: Baseball Words — Matching",
            "instructions": "Draw a line from each baseball word on the left to its meaning on the right.",
            "left_items": ["Out", "Base", "Hit", "Home run", "Inning"],
            "right_items": [
                "When a batter or runner is stopped and their turn ends",
                "A safe spot a runner can stand on",
                "When a batter hits the ball and reaches a base safely",
                "A hit so good the runner circles every base",
                "A round of the game where both teams bat",
            ],
        },
        "Monday",
    )

    # =========================================================================
    # TUESDAY — Down to the Wire (Bills 36, Texans 31)
    # Standards: ENGLISH 1.1.ri.1.a, ENGLISH 1.1.w.1.a, MATH 1.1.6
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: Down to the Wire — The Bills' Last-Minute Win",
            "passage_title": "The Two-Minute Drill",
            "instructions": (
                "Hands-on activity: Set up 4 cones, cups, or books in a line, about 5 giant "
                "steps apart. Toss a ball and try to move it past each marker in 4 tries — "
                "that's your own version of 4 downs! On your last try, have a grown-up count "
                "down from 30 seconds so you can feel the two-minute-drill pressure."
            ),
            "passage": (
                "Football teams do not get unlimited chances to move the ball. Every time a team "
                "has the ball, they get four tries — called DOWNS — to move it 10 yards forward. "
                "Succeed, and they earn a brand-new set of four downs. Run out of downs without "
                "gaining 10 yards, and the other team gets the ball.\n\n"
                "Scoring works in points. A TOUCHDOWN — carrying or catching the ball into the "
                "end zone — is worth 6 points, plus 1 more for a kick right after, so 7 in all. A "
                "FIELD GOAL, when a kicker boots the ball through the goalposts, is worth 3 "
                "points.\n\n"
                "The clock matters just as much as the plays. Near the end of a close game, teams "
                "race against time — sometimes called the TWO-MINUTE DRILL. Every second counts, "
                "and a single big play can change the whole game.\n\n"
                "That is exactly what happened this weekend. The Buffalo Bills were playing the "
                "Houston Texans, and the score went back and forth all afternoon. With only 1 "
                "minute and 36 seconds left on the clock, quarterback Josh Allen threw a 34-yard "
                "touchdown pass to Joshua Palmer. That single play was the difference — the Bills "
                "won, 36 to 31!"
            ),
            "vocabulary": [
                {
                    "term": "quarterback",
                    "definition": "The player who usually throws the ball to a teammate to try to move it down the field.",
                },
                {
                    "term": "field goal",
                    "definition": "When a kicker boots the ball through the goalposts — worth 3 points.",
                },
                {
                    "term": "two-minute drill",
                    "definition": "Playing fast and carefully at the end of a close game, when every second counts.",
                },
                {
                    "term": "down",
                    "definition": "One of four tries a team gets to move the ball 10 yards. Succeed, and you earn a fresh set of four.",
                },
                {
                    "term": "touchdown",
                    "definition": "Carrying or catching the ball into the end zone — worth 6 points, plus 1 more for a kick right after.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is a DOWN? How many does a team get to move the ball 10 yards?",
                    "response_lines": 2,
                },
                {
                    "prompt": "How many points is a touchdown worth (with the extra kick)? How many for a field goal?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Math: A team scores two touchdowns, each with the extra point (7 points each). How many points is that altogether?",
                    "response_lines": 1,
                },
                {
                    "prompt": "What happened with 1 minute and 36 seconds left in the Bills' game?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: Why do you think the clock matters so much at the end of a close game? If you were losing with only 2 minutes left, what would you want your team to do?",
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "writingScaffoldWorksheet",
        {
            "title": "Tuesday: Down to the Wire — Reporter's Notebook, Entry 2",
            "instructions": (
                "Add page two to your notebook! Use what you read to help you write like a real "
                "sports reporter — set the scene, describe the big play, then explain why it "
                "mattered."
            ),
            "topic": "The Bills' Game-Winning Drive",
            "sections": [
                {
                    "label": "Set the Scene",
                    "starter": "The Buffalo Bills were playing the Houston Texans. The score went back and forth all afternoon.",
                    "lines": 2,
                },
                {
                    "label": "The Big Play",
                    "starter": "With only 1 minute and 36 seconds left, quarterback Josh Allen threw the ball to Joshua Palmer. It was a 34-yard touchdown pass!",
                    "lines": 3,
                },
                {
                    "label": "Why It Mattered",
                    "starter": "This play mattered because...",
                    "lines": 3,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "tChartWorksheet",
        {
            "title": "Tuesday: Touchdown or Field Goal? — Sorting Points",
            "instructions": "Sort each clue into the correct column below — does it describe a TOUCHDOWN or a FIELD GOAL?",
            "columns": ["Touchdown", "Field Goal"],
            "word_bank": [
                "Worth 6 points, plus 1 for the kick",
                "Worth 3 points",
                "A kicker boots it through the goalposts",
                "A player carries or catches the ball into the end zone",
                "Worth the most points of the two",
                "A shorter score that can still help you win",
            ],
            "row_count": 3,
        },
        "Tuesday",
    )

    # =========================================================================
    # WEDNESDAY — Fast Start, Big Win (Raiders 27, Dolphins 13)
    # Standards: ENGLISH 1.1.ri.1.a, ENGLISH 1.1.w.1.a, MATH 1.1.10
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: Fast Start, Big Win — The Raiders Never Trailed",
            "passage_title": "How a Drive Moves Down the Field",
            "instructions": (
                "Hands-on activity: Mark a start line and measure out a pretend 'drive' in your "
                "yard or a hallway using giant steps. Walk it in chunks like a real drive — stop "
                "every 5-10 steps and call out 'first down!' when you've gone far enough."
            ),
            "passage": (
                "A team can move the ball two ways. RUSHING means running with the ball in your "
                "hands. PASSING means throwing it to a teammate. Every set of downs a team keeps "
                "the ball, from the first play to the last, is called a DRIVE. Gain 10 yards "
                "during a drive, and you earn a FIRST DOWN — a fresh set of four tries.\n\n"
                "Some drives are quick. Others are long, patient marches that eat up the clock "
                "play after play. This weekend, the Las Vegas Raiders played the Miami Dolphins "
                "and showed just how powerful a long drive can be. Right from the opening kickoff, "
                "the Raiders never trailed the entire game.\n\n"
                "Their very first drive lasted 16 plays and covered 93 yards — and it took almost "
                "9 minutes off the clock before they scored! Quarterback Kirk Cousins threw for "
                "three touchdowns, and running back Ashton Jeanty rushed for 102 yards and 2 more "
                "touchdowns. Rushing and passing both did their job that day. The final score was "
                "Raiders 27, Dolphins 13.\n\n"
                "That is a very different kind of exciting than the Bills' game from Tuesday. "
                "Instead of one late, dramatic play, the Raiders controlled the whole game from "
                "start to finish, one steady down at a time."
            ),
            "vocabulary": [
                {
                    "term": "rushing",
                    "definition": "Moving the ball by running with it in your hands.",
                },
                {
                    "term": "passing",
                    "definition": "Moving the ball by throwing it to a teammate.",
                },
                {
                    "term": "drive",
                    "definition": "A team's turn with the ball, made up of one down after another, trying to score.",
                },
                {
                    "term": "first down",
                    "definition": "Earned when a team gains 10 yards — it resets their downs back to a fresh set of four.",
                },
            ],
            "questions": [
                {
                    "prompt": "What are the two ways a team can move the ball, according to the passage?",
                    "response_lines": 2,
                },
                {
                    "prompt": "How long (in plays and yards) was the Raiders' opening drive? About how many minutes did it take off the clock?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Math/measuring: Take 10 giant steps outside. About how many 10-step chunks do you think it would take to cover a drive like the Raiders' 93 yards? There's no exact answer — just estimate!",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: The Raiders 'never trailed' the whole game, while the Bills' game went back and forth. Which style do you think is more exciting to watch — and why?",
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "writingScaffoldWorksheet",
        {
            "title": "Wednesday: Fast Start, Big Win — Reporter's Notebook, Entry 3",
            "instructions": (
                "Add page three! This story is different from yesterday's — it isn't about one "
                "big final play, it's about a team taking its time and controlling the whole "
                "game."
            ),
            "topic": "The Raiders' Long Opening Drive",
            "sections": [
                {
                    "label": "Set the Scene",
                    "starter": "The Las Vegas Raiders played the Miami Dolphins. Right from the start, the Raiders never trailed.",
                    "lines": 2,
                },
                {
                    "label": "The Big Play",
                    "starter": "The Raiders' first drive lasted 16 plays and covered 93 yards, using almost 9 minutes of the clock! Quarterback Kirk Cousins and running back Ashton Jeanty both helped move the ball.",
                    "lines": 3,
                },
                {
                    "label": "Why It Mattered",
                    "starter": "This drive mattered because...",
                    "lines": 3,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "barGraphWorksheet",
        {
            "title": "Wednesday: How a Long Drive Adds Up",
            "instructions": (
                "This bar graph shows an EXAMPLE of how a 93-yard drive — like the Raiders' real "
                "opening drive against the Dolphins — could add up bit by bit across four sets "
                "of downs. Read the bars, then answer the questions."
            ),
            "categories": [
                "1st Set of Downs",
                "2nd Set of Downs",
                "3rd Set of Downs",
                "4th Set of Downs",
            ],
            "values": [25, 20, 20, 28],
            "y_max": 30,
            "y_step": 5,
            "x_label": "Sets of downs in the drive",
            "y_label": "Yards gained",
            "show_values": True,
            "questions": [
                {"prompt": "Which set of downs gained the most yards?", "response_lines": 1},
                {
                    "prompt": "Add the first two bars together. How many yards is that?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Add all four bars together. Does it match the Raiders' real 93-yard drive?",
                    "response_lines": 1,
                },
            ],
        },
        "Wednesday",
    )

    # =========================================================================
    # THURSDAY — Two Different Wins (comparison, no new game)
    # Standards: ENGLISH 1.1.ri.3.a, ENGLISH 1.1.w.1.c, MATH 1.1.6
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: Two Different Wins — Comparing the Bills and the Raiders",
            "passage_title": "Two Games, Two Kinds of Exciting",
            "instructions": (
                "Before reading, look back at Tuesday's and Wednesday's notebook pages together.\n\n"
                "Hands-on activity: design your own pretend scoreboard for an imaginary game — "
                "draw two team names and boxes for the score, then fill in numbers for a game "
                "YOU make up."
            ),
            "passage": (
                "This week you reported on two real NFL games from the same weekend — and both "
                "teams won! But the two games did not feel the same at all. The Bills needed a "
                "dramatic, last-minute play. The Raiders controlled the game from start to "
                "finish.\n\n"
                "One way to compare two games is the MARGIN — how many points separated the "
                "winning and losing team at the end. The Bills won 36 to 31, a margin of just 5 "
                "points. The Raiders won 27 to 13, a margin of 14 points. A smaller margin usually "
                "means a tighter, more nail-biting game.\n\n"
                "Sports reporters deal in both FACTS and OPINIONS. A fact is something you can "
                "prove is true — like a final score. An opinion is what someone thinks or feels — "
                "it can't be proven true or false, but a good opinion gives a reason. 'The Bills "
                "won 36-31' is a fact. 'That was the best game of the week' is an opinion.\n\n"
                "Today, you get to write your very own opinion column — which game would YOU "
                "rather have watched live, and why?"
            ),
            "vocabulary": [
                {
                    "term": "margin",
                    "definition": "How many points separate the winning and losing team at the end of the game.",
                },
                {
                    "term": "fact",
                    "definition": "Something that can be proven true, like a final score.",
                },
                {
                    "term": "opinion",
                    "definition": "What someone thinks or feels — it can't be proven true or false, but a good opinion gives a reason.",
                },
            ],
            "questions": [
                {
                    "prompt": "Math: The Bills won 36-31. What is the margin (36 minus 31)?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Math: The Raiders won 27-13. What is the margin (27 minus 13)?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which game had the closer margin? What does that tell you about how exciting the ending probably was?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Give one FACT and one OPINION about a game from this week.",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: Is a close, back-and-forth game always more exciting than a game where one team is in control the whole time? Can you think of a reason someone might disagree with you?",
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    add(
        "writingScaffoldWorksheet",
        {
            "title": "Thursday: Which Game Would You Rather Watch? — Reporter's Notebook, Entry 4",
            "instructions": (
                "Today's notebook entry is an OPINION piece — you get to say what YOU think, as "
                "long as you give a reason. Real sports columnists do this all the time!"
            ),
            "topic": "My Sports Opinion Column",
            "sections": [
                {
                    "label": "My Opinion",
                    "starter": "If I had to pick one game to watch live, I would pick...",
                    "lines": 2,
                },
                {
                    "label": "My Reason",
                    "starter": "I would pick that game because...",
                    "lines": 3,
                },
                {
                    "label": "A Fact That Supports Me",
                    "starter": "Here is one fact from the game that backs up my opinion:",
                    "lines": 2,
                },
            ],
        },
        "Thursday",
    )

    add(
        "featureMatrixWorksheet",
        {
            "title": "Thursday: Bills vs. Raiders — What Do You Remember?",
            "instructions": (
                "Put a check mark in every box that is true for each game. Look back at "
                "Tuesday's and Wednesday's reading cards if you need a clue!"
            ),
            "items": ["Bills 36, Texans 31", "Raiders 27, Dolphins 13"],
            "properties": [
                "Won with a big play in the final 2 minutes",
                "Never trailed during the whole game",
                "Featured one long, clock-eating drive",
                "Won by 5 points or fewer",
                "The same team led from start to finish",
            ],
        },
        "Thursday",
    )

    # =========================================================================
    # FRIDAY — Rookie Reporter's Big Recap (capstone, no new game)
    # Standards: ENGLISH K.w.1.a / 1.1.w.1.a, ENGLISH K.rl.1.c, MATH K.11
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: Rookie Reporter's Big Recap",
            "passage_title": "Putting It All Together",
            "instructions": (
                "No new game today — it's time to be an editor!\n\n"
                "Hands-on/capstone activity: gather all four of this week's notebook pages, your "
                "drawings, and your feature-matrix page. Staple or tape them together in order to "
                "make your own mini newspaper. Add a big headline on the front."
            ),
            "passage": (
                "This week, Rookie Reporter Christopher covered four sports stories: your own "
                "baseball game, the Buffalo Bills' last-minute win, the Las Vegas Raiders' "
                "wire-to-wire win, and a column comparing the two. That's a lot of writing for one "
                "week — and it all adds up to one long finished piece, page by page.\n\n"
                "Before a story is finished, an EDITOR reads it over, checks it, and helps put all "
                "the pieces together in the right order. Today, YOU are the editor of your own "
                "notebook.\n\n"
                "Every finished news story needs a HEADLINE — a big, short title at the top that "
                "grabs the reader's attention and tells them what the story is about. Reporters "
                "usually write their headline LAST, after they already know how the whole story "
                "turns out. Some newspapers also print a COLUMN — a regular piece of writing, "
                "often sharing opinions, from the same writer every week. You already wrote one on "
                "Thursday!\n\n"
                "Now it's time to look back at everything you wrote, pick your best headline, and "
                "read your whole sports week out loud — just like a reporter presenting the news."
            ),
            "vocabulary": [
                {
                    "term": "column",
                    "definition": "A regular piece of writing, often sharing opinions, by the same writer.",
                },
                {
                    "term": "headline",
                    "definition": "The big, short title at the top of a news story that grabs your attention and tells you what it's about.",
                },
                {
                    "term": "editor",
                    "definition": "Someone who reads a story, checks it over, and helps put all the pieces together in the right order.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is a headline, and why do reporters often write it LAST, after they know the whole story?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Look back at your four notebook entries. Which one was your favorite to write, and why?",
                    "response_lines": 3,
                },
                {
                    "prompt": "Retell your whole sports week in order, from Monday to Thursday, in 1-2 sentences each.",
                    "response_lines": 4,
                },
                {
                    "prompt": "LET'S DISCUSS: Now that you've been a reporter for a whole week, what is one question you'd want to ask a REAL sports reporter about their job?",
                    "response_lines": 0,
                },
            ],
        },
        "Friday",
    )

    add(
        "writingScaffoldWorksheet",
        {
            "title": "Friday: My Newspaper's Big Headline — Reporter's Notebook, Entry 5",
            "instructions": "This is the last page of your notebook. Write a headline for your whole week, then a short wrap-up paragraph.",
            "topic": "Wrapping Up My Sports Week",
            "sections": [
                {
                    "label": "My Headline",
                    "starter": "(Write a short, exciting title for your week of sports stories.)",
                    "lines": 2,
                },
                {
                    "label": "My Wrap-Up",
                    "starter": "This week I wrote about my own baseball game, the Buffalo Bills, and the Las Vegas Raiders. My favorite story was...",
                    "lines": 4,
                },
            ],
        },
        "Friday",
    )

    add(
        "pictographWorksheet",
        {
            "title": "Friday: Rate My Week — Pictograph",
            "instructions": "Give each day's story a star rating from 1 to 5 — draw that many stars in the row! Then answer the questions below.",
            "symbol": "⭐",
            "per_symbol": 1,
            "unit_label": "stars",
            "blank": True,
            "max_symbols": 5,
            "rows": [
                {"label": "Monday: My Baseball Game"},
                {"label": "Tuesday: The Bills' Comeback"},
                {"label": "Wednesday: The Raiders' Fast Start"},
                {"label": "Thursday: Comparing the Two Games"},
            ],
            "questions": [
                {
                    "prompt": "Which day got the most stars? Why did you rate it that way?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Which day got the fewest stars? What would have made it more exciting to write about?",
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
            "title": "End-of-Week Parent Feedback — Sports Reporter Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this feedback sheet after the week wraps up. Your notes help "
                "shape next week's lessons."
            ),
            "passage": (
                "This week used real sports events as the engine for a serialized creative-"
                "nonfiction writing project — a 'reporter's notebook' that built one page at a "
                "time so a 6-year-old's short writing stamina never had to carry a whole essay in "
                "one sitting. Monday grounded the week in Christopher's own first baseball game of "
                "the season. Tuesday and Wednesday covered two real, contrasting NFL wins from the "
                "same weekend — the Bills' last-second comeback and the Raiders' wire-to-wire "
                "control. Thursday pulled both stories together into a compare/contrast and his "
                "first opinion piece. Friday assembled all four entries into one finished, "
                "illustrated 'newspaper.'\n\n"
                "Christopher himself was the recurring narrator this week — 'Rookie Reporter "
                "Christopher' — rather than a fictional character, since the week was deliberately "
                "kept grounded in real events.\n\n"
                "Key concepts to check for genuine understanding — not just recall:\n"
                "1) He can recount a personal event in order (who/what/when/where, then the big "
                "moment, then how he felt).\n"
                "2) He understands downs, touchdowns, and field goals well enough to explain them "
                "in his own words.\n"
                "3) He can tell the difference between a fact and an opinion, and give a reason "
                "for an opinion.\n"
                "4) He can compare two real events and name specific similarities/differences "
                "(not just 'they were both fun').\n\n"
                "Common misconceptions to watch for:\n"
                "* Thinking every score is a touchdown — reinforce that a field goal (3 pts) is a "
                "different, smaller score.\n"
                "* Confusing 'fact' with 'true statement I agree with' — an opinion can still be "
                "reasonable even if you'd pick the other answer.\n"
                "* Expecting the bar-graph drive numbers to be the Raiders' literal real play-by-"
                "play — they are an illustrative example that happens to total the real 93 yards, "
                "not an actual reported down-by-down record.\n\n"
                "Suggested follow-on activities: watch a few minutes of a real game together and "
                "have him call out 'down!' or 'touchdown!' when he spots one; keep the reporter's "
                "notebook habit going with a non-sports topic next week; ask him to 'edit' a "
                "sibling's or parent's story out loud."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": "A close final score does not always mean the whole game was close — check whether he can tell 'margin at the end' apart from 'how the game felt throughout' (see Thursday).",
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in after the week — which idea did Christopher grasp best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": "Keep the reporter's-notebook format but on a different real topic he chooses — it's a reusable structure for painless serialized writing.",
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
                    "prompt": "By Friday, could Christopher retell the whole week's arc in order without prompting?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Did the ~2 hour/day pacing work, or should next week return to the usual ~90 minutes?",
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
        pages, packet_title="Sports Reporter Week — Creative Writing for Christopher"
    )
    out_path = output_dir / "sports_reporter_week.html"
    out_path.write_text(html, encoding="utf-8")

    # Teacher guide
    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Sports Reporter Week — Teacher Guide</title>
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
    .pacing { background: #eef2ff; border-left: 4px solid #4338ca; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
  </style>
</head>
<body>

<div class="page">
  <h1>Sports Reporter Week — Teacher / Parent Guide</h1>
  <p><strong>Theme:</strong> Real sports, serialized creative-nonfiction writing &nbsp;|&nbsp;
  <strong>Audience:</strong> Christopher, age 6, K-1 &nbsp;|&nbsp;
  <strong>Narrator:</strong> Christopher himself, as "Rookie Reporter Christopher"</p>
  <p><strong>Causal Arc:</strong> Learn baseball's rules &rarr; report his own game &rarr; learn
  football's rules &rarr; report the Bills' comeback &rarr; report the Raiders' wire-to-wire win
  &rarr; compare both &rarr; assemble the finished "newspaper"</p>
  <p><strong>Pacing note:</strong> Built to ~2 hours/day per this week's specific parent request —
  above Christopher's usual ~90 minute/day default. Each day is reading + notebook writing +
  one application/math page + a hands-on activity described in the reading page's instructions.</p>

  <h2>Monday — Play Ball (his own baseball game)</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1 (Two ways to get an out):</strong> A fielder catches the hit ball before it touches the ground, OR a fielder tags the runner with the ball before they reach a base.</p>
    <p><strong>Q2 (Hit vs. home run):</strong> A hit means reaching a base safely. A home run means the ball is hit far enough (often over the fence) that the batter circles every base at once.</p>
    <p><strong>Q3 (Math — outs):</strong> 3 + 3 = 6 outs altogether.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"What question would you want a reporter to ask YOU about your game?"</em></p>
    <p>Open-ended — accept anything on-topic. If he's stuck, model a few: "How did you feel when you got up to bat?" or "What was the hardest part?" This previews the interview-style thinking that shows up again Friday.</p>
  </div>
  <h3>Matching Answer Key</h3>
  <div class="answer-box">
    <p>Out &rarr; When a batter or runner is stopped and their turn ends</p>
    <p>Base &rarr; A safe spot a runner can stand on</p>
    <p>Hit &rarr; When a batter hits the ball and reaches a base safely</p>
    <p>Home run &rarr; A hit so good the runner circles every base</p>
    <p>Inning &rarr; A round of the game where both teams bat</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Kids sometimes think ANY hit ball that isn't caught is automatically a home run. Reinforce that a home run specifically means circling ALL the bases on that one play — most hits are singles or doubles.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>If you have any photos or a program from his actual game, look at them together while he dictates the notebook entry — concrete details (uniform color, teammates' names) make the writing much richer.</p>
  </div>

  <h2 class="tue">Tuesday — Down to the Wire (Bills 36, Texans 31)</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box tue">
    <p><strong>Q1 (Down):</strong> A down is one of four tries a team gets to move the ball 10 yards. They get four downs; succeed and they earn a fresh set.</p>
    <p><strong>Q2 (Points):</strong> Touchdown = 6 points + 1 for the extra kick = 7 total. Field goal = 3 points.</p>
    <p><strong>Q3 (Math):</strong> 7 + 7 = 14 points.</p>
    <p><strong>Q4 (The play):</strong> With 1:36 left, Josh Allen threw a 34-yard touchdown pass to Joshua Palmer, which won the game for the Bills, 36-31.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Why does the clock matter so much at the end of a close game?"</em></p>
    <p>Expected reasoning: once time runs out, no more scoring is possible, so every remaining second is a scoring opportunity that will never come back. Teams losing late often play faster and take more risks because they're running out of chances.</p>
  </div>
  <h3>T-Chart Answer Key</h3>
  <div class="answer-box tue">
    <p><strong>Touchdown:</strong> Worth 6 points plus 1 for the kick; a player carries or catches the ball into the end zone; worth the most points of the two.</p>
    <p><strong>Field Goal:</strong> Worth 3 points; a kicker boots it through the goalposts; a shorter score that can still help you win.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Kids often assume a team only gets ONE try to move 10 yards. Emphasize the "four tries" framing — that's why teams sometimes take a smaller gain on early downs and save a bigger play for later.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Watch a two-minute-drill clip of any close NFL finish together and have him call out "down!" each time a new play starts, and "touchdown!" or "field goal!" when a score happens.</p>
  </div>
</div>

<div class="page">
  <h2 class="wed">Wednesday — Fast Start, Big Win (Raiders 27, Dolphins 13)</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1 (Two ways to move the ball):</strong> Rushing (running with it) and passing (throwing it to a teammate).</p>
    <p><strong>Q2 (The drive):</strong> 16 plays, 93 yards, almost 9 minutes off the clock.</p>
    <p><strong>Q3 (Measuring):</strong> Personal estimate — guide him toward "about 9 or 10 chunks of 10 steps," and note there's no single right answer since step length varies.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Which style is more exciting — never trailing, or a back-and-forth game?"</em></p>
    <p>Both are legitimate answers. A back-and-forth game has more suspense about the OUTCOME; a wire-to-wire win can be exciting to watch for skill and control. The goal is a reasoned answer, not a "correct" one — this previews Thursday's fact-vs-opinion lesson.</p>
  </div>
  <h3>Bar Graph Answer Key</h3>
  <div class="answer-box wed">
    <p><strong>Q1:</strong> The 4th set of downs gained the most (28 yards).</p>
    <p><strong>Q2:</strong> 25 + 20 = 45 yards.</p>
    <p><strong>Q3:</strong> 25 + 20 + 20 + 28 = 93 yards — yes, it matches the Raiders' real drive total! (Remind him the per-down split is an illustrative example, not the actual reported play-by-play — only the 93-yard total and rough time/play count are real.)</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Don't let the bar-graph numbers get repeated back as if they were the real reported play-by-play — they're a teaching example built to total the real 93 yards. The real facts are: 16 plays, 93 yards, ~8:58 elapsed.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Measure an actual 93-yard-equivalent distance somewhere familiar (about the length of a football field minus one end zone) using a bike, wagon, or just a long walk, to make the number concrete.</p>
  </div>

  <h2 class="thu">Thursday — Two Different Wins (comparison)</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1 (Bills margin):</strong> 36 - 31 = 5.</p>
    <p><strong>Q2 (Raiders margin):</strong> 27 - 13 = 14.</p>
    <p><strong>Q3 (Closer margin):</strong> The Bills' game had the closer margin (5 points), which usually means a tighter, more suspenseful ending.</p>
    <p><strong>Q4 (Fact vs. opinion):</strong> Accept any correctly-labeled pair, e.g. Fact: "The Raiders won 27-13." Opinion: "The Raiders' game was more fun to watch because they were never in danger of losing."</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Is a close game always more exciting than a wire-to-wire one?"</em></p>
    <p>No single right answer. Model disagreement respectfully: "Some people love the suspense of a close game; others love watching a team play so well that the outcome feels certain early. Both are valid opinions if you can explain why."</p>
  </div>
  <h3>Feature Matrix Answer Key</h3>
  <div class="answer-box thu">
    <p><strong>Bills 36, Texans 31:</strong> Won with a big play in the final 2 minutes &#10003;; Won by 5 points or fewer &#10003;. (Never trailed the whole game, one long clock-eating drive, and led start-to-finish are all FALSE — the game went back and forth.)</p>
    <p><strong>Raiders 27, Dolphins 13:</strong> Never trailed during the whole game &#10003;; Featured one long clock-eating drive &#10003;; The same team led from start to finish &#10003;. (Won with a big play in the final 2 minutes and won by 5 points or fewer are FALSE — margin was 14, and the win was not a late dramatic play.)</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Watch for him treating his own preference as a "fact." Gently redirect: "That's your opinion — what's one FACT that supports it?" reinforces the distinction taught in the reading passage.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Make a two-column "Fact / Opinion" list about something totally unrelated to sports (dinner, a TV show, a book) to show the skill transfers beyond this week's topic.</p>
  </div>
</div>

<div class="page">
  <h2 class="fri">Friday — Rookie Reporter's Big Recap (Capstone)</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1 (Headline last):</strong> A headline is the big, short title at the top of a story. Reporters write it last because they need to know the whole story first to sum it up well.</p>
    <p><strong>Q2 (Favorite entry):</strong> Personal response — any entry, with a reason, is a full-credit answer.</p>
    <p><strong>Q3 (Retell the week):</strong> Expect roughly: Monday — his own baseball game; Tuesday — the Bills' last-second win over the Texans; Wednesday — the Raiders' long opening drive and wire-to-wire win over the Dolphins; Thursday — comparing the two and writing an opinion. Sequence matters more than polish here.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"What would you want to ask a real sports reporter about their job?"</em></p>
    <p>Open-ended. If he's stuck, offer prompts: "How do you remember everything that happened?" or "What do you do when you don't like how the game ended?"</p>
  </div>
  <h3>Pictograph Answer Key</h3>
  <div class="answer-box fri">
    <p>No fixed "correct" ratings — this is a self-assessment. Look for a reasoned answer to both follow-up questions (why the top-rated day earned it, and what would have made the lowest-rated day better) rather than a specific star count.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"Editing" can feel like criticism to a 6-year-old. Frame Friday's assembly step as celebration, not correction — he is a proud author collecting his finished work, not fixing mistakes.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Read the finished "newspaper" out loud to another family member as a mini presentation — this satisfies the oral, sequential-retell standard and gives the week's writing a real audience.</p>
  </div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2 class="fri">Week Summary — Causal Chain</h2>
  <p>The week followed this build:</p>
  <ol style="padding-left: 20px; font-size: 10pt; line-height: 2;">
    <li><strong>Monday:</strong> Learn baseball's core rules, then recount his own real game — the personal, low-stakes on-ramp into the week's writing habit.</li>
    <li><strong>Tuesday:</strong> Learn football's downs/scoring/clock rules, then report the Bills' real last-second win — a dramatic, single-play story.</li>
    <li><strong>Wednesday:</strong> Learn how a drive advances, then report the Raiders' real wire-to-wire win — a patient, cumulative story, a deliberate contrast to Tuesday.</li>
    <li><strong>Thursday:</strong> Compare both real games using margin, fact, and opinion — his first opinion piece, backed by a chosen fact.</li>
    <li><strong>Friday:</strong> No new content — assemble, headline, and present the finished, four-entry piece as one long, completed work.</li>
  </ol>
  <p style="margin-top: 10px;">By Friday, Christopher should be able to retell all four stories in order and explain, with a reason, which one he liked best — while the actual writing load on any single day never exceeded a few guided sentences.</p>
</div>

</body>
</html>"""

    guide_path = output_dir / "sports_reporter_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print("\nSuccessfully generated Sports Reporter Week.")
    print(f"Student packet:  {out_path}")
    print(f"Teacher guide:   {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Mon p1 — Reading: Play Ball — My First Game of the Season",
        "Mon p2 — Writing Scaffold: My Game Day Story (Notebook Entry 1)",
        "Mon p3 — Matching: Baseball Words",
        "Tue p1 — Reading: Down to the Wire — The Bills' Last-Minute Win",
        "Tue p2 — Writing Scaffold: The Bills' Game-Winning Drive (Notebook Entry 2)",
        "Tue p3 — T-Chart: Touchdown or Field Goal?",
        "Wed p1 — Reading: Fast Start, Big Win — The Raiders Never Trailed",
        "Wed p2 — Writing Scaffold: The Raiders' Long Opening Drive (Notebook Entry 3)",
        "Wed p3 — Bar Graph: How a Long Drive Adds Up",
        "Thu p1 — Reading: Two Different Wins — Comparing the Bills and the Raiders",
        "Thu p2 — Writing Scaffold: Which Game Would You Rather Watch? (Notebook Entry 4)",
        "Thu p3 — Feature Matrix: Bills vs. Raiders",
        "Fri p1 — Reading: Rookie Reporter's Big Recap",
        "Fri p2 — Writing Scaffold: My Newspaper's Big Headline (Notebook Entry 5)",
        "Fri p3 — Pictograph: Rate My Week",
        "         — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")


if __name__ == "__main__":
    generate_sports_reporter_week_series()
