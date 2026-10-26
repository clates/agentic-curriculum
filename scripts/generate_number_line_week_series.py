"""
Number Line — Week Series
Grade 1 | Mathematics | Causal Arc: The number line is a road (order, one more / one less) →
Hop forward to add → Hop backward to subtract → Hop to the Ten Stop & count up (addition and
subtraction are partners) → The Big Race: story problems and the equal sign

Narrator: Kip the Kangaroo, introduced on Monday. Kip hops along a 0–20 number line all week;
every operation is modelled as hops, and every practice page is a number line.
Output: number_line_week_series/number_line_week.html (+ teacher guide)

Standards (Virginia SOL):
  Monday    — 1.1.1a, 1.1.1c  (count forward / backward on 0–20; number before and after)
  Tuesday   — 1.1.6, 1.1.7b   (addition within 20 as hops forward; order of addends)
  Wednesday — 1.1.6, 1.1.1c   (subtraction within 20 as hops backward)
  Thursday  — 1.1.7a, 2.2.5a  (bridging through ten; part-whole; addition/subtraction as inverses)
  Friday    — 1.1.6, 1.1.15   (capstone: single-step story problems; = means "the same as")
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html

MINUS = "−"


def counted_hops(start: int, end: int) -> list[dict]:
    """One arc per unit step from start to end, labelled 1, 2, 3… so the hops can be counted."""
    direction = 1 if end > start else -1
    return [
        {"from": start + i * direction, "to": start + (i + 1) * direction, "label": str(i + 1)}
        for i in range(abs(end - start))
    ]


def ten_stop_hops(start: int, end: int) -> list[dict]:
    """Two arcs: start → 10, then 10 → end, labelled with the signed hop size."""
    sign = "+" if end > start else MINUS
    return [
        {"from": start, "to": 10, "label": f"{sign}{abs(10 - start)}"},
        {"from": 10, "to": end, "label": f"{sign}{abs(end - 10)}"},
    ]


def generate_number_line_week_series():
    output_dir = Path("number_line_week_series")
    output_dir.mkdir(exist_ok=True)
    pages: list[tuple[str, str]] = []

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — The Number Road
    # Standards: 1.1.1a, 1.1.1c — counting forward/backward, before and after
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: Meet Kip and the Number Road",
            "passage_title": "Meet Kip the Kangaroo!",
            "instructions": (
                "Hands-on first (25 min): Build a GIANT number line! Run a strip of painter's tape "
                "across the floor and mark 21 spots, one big step apart. Put a sticky note on each "
                "spot: 0, 1, 2 … 20. Theodore is Kip: stand on 0 and hop forward, saying each "
                "number, then hop back to 0 saying them backward. Then play Hide-and-Seek: while "
                "Theodore closes his eyes, flip one sticky note over. What number is hiding? Keep "
                "the tape line up all week."
            ),
            "passage": (
                "Meet Kip the Kangaroo! Kip has big feet and a long, strong tail. Kip loves to "
                "hop. This week, Kip hops on a special road. It is called a number line.\n\n"
                "A number line is a road made of numbers. The numbers go in order: 0, 1, 2, 3, "
                "all the way to 20. Each number has its own spot. The spots are all the same "
                "distance apart.\n\n"
                "When Kip hops one spot to the right, the number gets one bigger. That is one "
                "more. When Kip hops one spot to the left, the number gets one smaller. That is "
                "one less.\n\n"
                "Kip is on 7. One hop to the right lands on 8. One hop to the left lands on 6. "
                "8 is the number after 7. 6 is the number before 7."
            ),
            "questions": [
                {"prompt": "What is Kip's number road called?", "response_lines": 1},
                {
                    "prompt": "Kip is on 12. He hops one spot to the right. Where does he land?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Kip is on 12. He hops one spot to the left. Where does he land?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which way do the numbers get bigger — right or left?",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Kip's friend says the number line stops at 20. Does it? "
                        "What would Kip land on if he hopped one more time past 20?"
                    ),
                    "response_lines": 0,
                },
            ],
            "vocabulary": [
                {"term": "one less", "definition": "the number one spot to the left"},
                {"term": "number line", "definition": "a road of numbers in order"},
                {"term": "after", "definition": "the number that comes next"},
                {"term": "one more", "definition": "the number one spot to the right"},
                {"term": "before", "definition": "the number that comes just ahead of it"},
            ],
        },
        "Monday",
    )

    mon_fix = [
        (0, 10, [3, 6, 9], "Count from 0 to 10. Fill in the missing numbers."),
        (0, 10, [1, 4, 5, 8], "Count from 0 to 10 again. More numbers fell off!"),
        (5, 15, [7, 10, 11, 14], "This road starts at 5. Count on from 5."),
        (10, 20, [12, 13, 16, 19], "This road starts at 10. Count on to 20."),
        (0, 20, [2, 7, 11, 15, 18], "The whole road! Count from 0 to 20."),
        (0, 20, [5, 10, 14, 17, 20], "Count BACKWARD from 20 out loud first. Then fill in."),
    ]
    add(
        "numberLineWorksheet",
        {
            "title": "Fix Kip's Number Road",
            "instructions": (
                "Oh no — some numbers fell off Kip's road! Write each missing number in its box."
            ),
            "tasks": [
                {"start": s, "end": e, "step": 1, "hidden_positions": h, "prompt": p}
                for s, e, h, p in mon_fix
            ],
        },
        "Monday",
    )

    mon_hops = [
        # (lo, hi, start, end, prompt)
        (0, 10, 4, 5, "Kip is on 4 and hops 1 to the right. What is 1 more than 4?"),
        (0, 10, 9, 8, "Kip is on 9 and hops 1 to the left. What is 1 less than 9?"),
        (10, 20, 16, 18, "Kip is on 16 and hops 2 to the right. What is 2 more than 16?"),
        (10, 20, 20, 18, "Kip is on 20 and hops 2 to the left. What is 2 less than 20?"),
    ]
    add(
        "numberLineWorksheet",
        {
            "title": "One Hop Right, One Hop Left",
            "instructions": (
                "Kip starts on the dot. Follow his hops with your finger. Write the number where "
                "Kip lands in the box."
            ),
            "tasks": [
                {
                    "start": lo,
                    "end": hi,
                    "step": 1,
                    "mark_positions": [a],
                    "hidden_positions": [b],
                    "jumps": counted_hops(a, b),
                    "prompt": p,
                }
                for lo, hi, a, b, p in mon_hops
            ]
            + [
                {
                    "start": 5,
                    "end": 15,
                    "step": 1,
                    "mark_positions": [14],
                    "hidden_positions": [13, 15],
                    "prompt": "Your turn! Kip is on 14. Write the number BEFORE and AFTER 14.",
                }
            ],
        },
        "Monday",
    )

    # =========================================================================
    # TUESDAY — Hop Forward to Add
    # Standards: 1.1.6, 1.1.7b — addition within 20; addends in any order
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: Hop Forward to Add",
            "passage_title": "Kip Learns to Add",
            "instructions": (
                "Hands-on first (25 min): Go outside and draw a sidewalk-chalk number line from 0 "
                "to 20, with a big step between numbers. Play Kangaroo Add: Theodore picks a start "
                "number from 0 to 10, rolls a die, and hops FORWARD that many, counting each hop "
                'out loud. Then say the whole number sentence: "7 plus 4 equals 11!" Play 6 '
                "rounds. Rainy day? Use Monday's tape line."
            ),
            "passage": (
                "Kip has a new trick. Kip can add by hopping forward!\n\n"
                "To add 6 + 3, Kip starts on 6. The first number tells Kip where to start. The "
                "second number tells Kip how many hops to take. Kip hops forward: 7, 8, 9. Kip "
                "lands on 9. So 6 + 3 = 9.\n\n"
                "Count the hops, not the spot where you start. Kip stands on 6, but 6 is not a "
                "hop. His first hop lands on 7. That is hop number one.\n\n"
                "Here is a smart Kip trick. To add 2 + 9, Kip starts on the bigger number, 9. Then "
                "he only needs 2 hops: 10, 11. So 2 + 9 = 11, and 9 + 2 = 11 too. You can add "
                "numbers in any order and get the same sum!"
            ),
            "questions": [
                {"prompt": "To add 5 + 4, what number does Kip start on?", "response_lines": 1},
                {
                    "prompt": "How many hops does Kip take for 5 + 4? Where does he land?",
                    "response_lines": 1,
                },
                {"prompt": "Kip stands on 6. Does 6 count as a hop?", "response_lines": 1},
                {
                    "prompt": "For 3 + 12, which number should Kip start on to save hops?",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Kip wants to add 7 + 0. How many hops does he take? "
                        "Where does he land?"
                    ),
                    "response_lines": 0,
                },
            ],
            "vocabulary": [
                {"term": "sum", "definition": "the answer when you add"},
                {"term": "forward", "definition": "hopping to the right, toward bigger numbers"},
                {"term": "add", "definition": "put together to make more"},
                {"term": "hop", "definition": "one jump from a spot to the next spot"},
                {"term": "start", "definition": "the spot Kip stands on before he hops"},
            ],
        },
        "Tuesday",
    )

    tue_read = [(0, 10, 4, 3), (0, 10, 5, 5), (0, 20, 9, 4), (0, 20, 11, 6), (0, 20, 8, 7)]
    add(
        "numberLineWorksheet",
        {
            "title": "Count Kip's Hops",
            "instructions": (
                "Kip starts on the dot. Count his hops — the numbers on top help you. Write where "
                "Kip lands in the box."
            ),
            "tasks": [
                {
                    "start": lo,
                    "end": hi,
                    "step": 1,
                    "mark_positions": [a],
                    "hidden_positions": [a + b],
                    "jumps": counted_hops(a, a + b),
                    "prompt": f"{a} + {b} = ?   Start on {a}. Count {b} hops.",
                }
                for lo, hi, a, b in tue_read
            ],
        },
        "Tuesday",
    )

    tue_draw = [(6, 5), (10, 7), (7, 6), (12, 8)]
    add(
        "numberLineWorksheet",
        {
            "title": "Draw the Hops: Adding",
            "instructions": (
                "Kip starts on the dot. Draw each hop as a little rainbow over the line, then "
                "write the sum on the blank. Last one: no dot! Use the smart Kip trick."
            ),
            "tasks": [
                {
                    "start": 0,
                    "end": 20,
                    "step": 1,
                    "mark_positions": [a],
                    "hop_space": True,
                    "prompt": f"{a} + {b} = ______",
                }
                for a, b in tue_draw
            ]
            + [
                {
                    "start": 0,
                    "end": 20,
                    "step": 1,
                    "hop_space": True,
                    "prompt": "3 + 9 = ______   (Start on the BIGGER number!)",
                }
            ],
        },
        "Tuesday",
    )

    # =========================================================================
    # WEDNESDAY — Hop Backward to Subtract
    # Standards: 1.1.6, 1.1.1c — subtraction within 20; counting backward
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: Hop Backward to Subtract",
            "passage_title": "Kip Hops the Other Way",
            "instructions": (
                "Hands-on first (25 min): Rocket Countdown! Tape a paper strip up a door frame and "
                "write 0 at the floor up to 20 at the top — a number line can stand up tall. A toy "
                'rocket (or any toy) starts at the top number you call out. Say "Minus 5!" and '
                "Theodore moves it DOWN 5 spots, counting back. Then go to the floor tape line "
                "and hop backward (carefully!) to solve 3 more: 12 − 4, 15 − 6, 20 − 7."
            ),
            "passage": (
                "Today Kip hops the other way. When Kip hops backward, to the left, he is "
                "subtracting.\n\n"
                "To solve 12 − 4, Kip starts on 12. The first number tells Kip where to start. "
                "The second number tells how many hops to take back. Kip hops back: 11, 10, 9, 8. "
                "Kip lands on 8. So 12 − 4 = 8.\n\n"
                "Subtracting means taking away. Each hop back takes away one. The number gets "
                "smaller with every hop.\n\n"
                "Watch out! Kip can not swap the numbers when he subtracts. 12 − 4 is not the "
                "same as 4 − 12. Kip must always start on the first number."
            ),
            "questions": [
                {"prompt": "Which way does Kip hop to subtract?", "response_lines": 1},
                {
                    "prompt": "To solve 15 − 3, where does Kip start? Where does he land?",
                    "response_lines": 1,
                },
                {
                    "prompt": "When Kip subtracts, does the number get bigger or smaller?",
                    "response_lines": 1,
                },
                {
                    "prompt": "Kip is on 10 and hops back 10 times. Where does he land?",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Kip says, \"Adding ALWAYS makes a number bigger, and "
                        'subtracting ALWAYS makes it smaller." Is he right? Think about 9 + 0 '
                        "and 9 − 0."
                    ),
                    "response_lines": 0,
                },
            ],
            "vocabulary": [
                {"term": "minus", "definition": "the − sign; it means take away"},
                {"term": "backward", "definition": "hopping to the left, toward smaller numbers"},
                {"term": "difference", "definition": "the answer when you subtract"},
                {"term": "subtract", "definition": "take away to make less"},
                {"term": "take away", "definition": "remove some; another way to say subtract"},
            ],
        },
        "Wednesday",
    )

    wed_read = [(0, 10, 9, 3), (0, 20, 14, 4), (0, 20, 17, 5), (0, 20, 13, 6), (0, 20, 20, 7)]
    add(
        "numberLineWorksheet",
        {
            "title": "Count the Backward Hops",
            "instructions": (
                "Kip starts on the dot and hops BACKWARD. Count his hops. Write where Kip lands in "
                "the box."
            ),
            "tasks": [
                {
                    "start": lo,
                    "end": hi,
                    "step": 1,
                    "mark_positions": [a],
                    "hidden_positions": [a - b],
                    "jumps": counted_hops(a, a - b),
                    "prompt": f"{a} {MINUS} {b} = ?   Start on {a}. Count {b} hops back.",
                }
                for lo, hi, a, b in wed_read
            ],
        },
        "Wednesday",
    )

    wed_draw = [(11, 3), (16, 6), (15, 7), (19, 8), (12, 9)]
    add(
        "numberLineWorksheet",
        {
            "title": "Draw the Hops: Subtracting",
            "instructions": (
                "Kip starts on the dot. Draw each hop BACKWARD as a little rainbow, then write the "
                "difference on the blank."
            ),
            "tasks": [
                {
                    "start": 0,
                    "end": 20,
                    "step": 1,
                    "mark_positions": [a],
                    "hop_space": True,
                    "prompt": f"{a} {MINUS} {b} = ______",
                }
                for a, b in wed_draw
            ],
        },
        "Wednesday",
    )

    # =========================================================================
    # THURSDAY — The Ten Stop & Fact Families
    # Standards: 1.1.7a, 2.2.5a — part-whole within 10; addition/subtraction as inverses
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: The Ten Stop",
            "passage_title": "Kip's Favorite Spot",
            "instructions": (
                "Hands-on first (25 min): Clothesline number line! Tie string between two chairs "
                "and clip on index cards 0 to 20 with clothespins. Make 10 a bright color — that "
                "is the Ten Stop. Scramble the cards and let Theodore clip them back in order. "
                'Then a clothespin is Kip: say "8 + 5" and slide Kip to the Ten Stop first (how '
                "many hops? 2), then the rest (3). Do 6 problems, half adding and half "
                "subtracting (try 7 + 6, 9 + 4, 8 + 8, 13 − 4, 15 − 6, 12 − 5)."
            ),
            "passage": (
                "Kip has a favorite spot on the number line. It is 10! Kip calls it the Ten "
                "Stop.\n\n"
                "Kip likes to hop to the Ten Stop first. To solve 8 + 5, Kip hops 2 to get to 10. "
                "He has 3 hops left, because 2 + 3 = 5. From 10, three more is 13. So "
                "8 + 5 = 13.\n\n"
                "The Ten Stop works going backward too. To solve 13 − 5, Kip hops back 3 to get to "
                "10. He has 2 hops left. From 10, two back is 8. So 13 − 5 = 8.\n\n"
                "Did you see it? 8 + 5 = 13 and 13 − 5 = 8. They use the same three numbers: 5, "
                "8, and 13. Subtracting undoes adding! Facts that share the same three numbers "
                "are a fact family."
            ),
            "questions": [
                {"prompt": "What number is Kip's Ten Stop?", "response_lines": 1},
                {"prompt": "Kip is on 9. How many hops to the Ten Stop?", "response_lines": 1},
                {
                    "prompt": (
                        "To solve 7 + 6, Kip hops 3 to get to 10. How many hops are left? "
                        "Where does he land?"
                    ),
                    "response_lines": 1,
                },
                {
                    "prompt": "8 + 5 = 13. What subtraction fact uses the same three numbers?",
                    "response_lines": 1,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Kip is on 6. He wants to get to 14, but he doesn't know "
                        "how many hops it takes. How could he find out?"
                    ),
                    "response_lines": 0,
                },
            ],
            "vocabulary": [
                {
                    "term": "count up",
                    "definition": "hop forward to find how far apart two numbers are",
                },
                {"term": "fact family", "definition": "facts that use the same three numbers"},
                {"term": "Ten Stop", "definition": "Kip's name for 10, a handy place to stop"},
                {"term": "undo", "definition": "go back to where you started"},
            ],
        },
        "Thursday",
    )

    thu_ten = [(8, 13), (9, 15), (13, 8), (15, 8)]

    def ten_prompt(a: int, b: int) -> str:
        op, n = ("+", b - a) if b > a else (MINUS, a - b)
        return f"{a} {op} {n} = ?   Hop to the Ten Stop first, then the rest."

    add(
        "numberLineWorksheet",
        {
            "title": "Hop to the Ten Stop",
            "instructions": (
                "Kip makes two big hops: one to the Ten Stop, then the rest. Write where Kip lands "
                "in the box. On the last one, draw Kip's two hops yourself!"
            ),
            "tasks": [
                {
                    "start": 0,
                    "end": 20,
                    "step": 1,
                    "mark_positions": [a],
                    "hidden_positions": [b],
                    "jumps": ten_stop_hops(a, b),
                    "prompt": ten_prompt(a, b),
                }
                for a, b in thu_ten
            ]
            + [
                {
                    "start": 0,
                    "end": 20,
                    "step": 1,
                    "mark_positions": [6],
                    "hop_space": True,
                    "prompt": "6 + 8 = ______  (Hop 6 + ___ = 10, then 10 + ___ more.)",
                }
            ],
        },
        "Thursday",
    )

    thu_mystery = [(6, 10), (9, 15), (12, 20), (7, 16), (5, 13)]
    add(
        "numberLineWorksheet",
        {
            "title": "Mystery Hops: Count Up",
            "instructions": (
                "Kip made one giant mystery hop. Count the spots from where he started to where "
                "he landed. Then fill in both blanks — they are the same number!"
            ),
            "tasks": [
                {
                    "start": 0,
                    "end": 20,
                    "step": 1,
                    "mark_positions": [a, b],
                    "jumps": [{"from": a, "to": b, "label": "?"}],
                    "prompt": f"{a} + ____ = {b}   and   {b} {MINUS} {a} = ____",
                }
                for a, b in thu_mystery
            ],
        },
        "Thursday",
    )

    families = [(8, 5), (9, 6), (7, 4), (10, 8), (6, 6), (9, 8)]
    partners = [
        f"{a + b} {MINUS} {b} = {a}" if (a, b) != (9, 8) else f"{a + b} {MINUS} {a} = {b}"
        for a, b in families
    ]
    partner_order = [3, 0, 5, 4, 1, 2]  # shuffled so row i never lines up with its partner
    add(
        "matchingWorksheet",
        {
            "title": "Fact Family Partners",
            "instructions": (
                "Every adding fact has a subtracting partner that uses the same three numbers. "
                "Draw a line to each partner. Not sure? Check it on your number line!"
            ),
            "left_items": [f"{a} + {b} = {a + b}" for a, b in families],
            "right_items": [partners[i] for i in partner_order],
        },
        "Thursday",
    )

    # =========================================================================
    # FRIDAY — Kip's Big Race (capstone)
    # Standards: 1.1.6, 1.1.15 — story problems within 20; the equal sign
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: Kip's Big Race",
            "passage_title": "Race to 20!",
            "instructions": (
                "Hands-on first (30 min): Play Kip's Big Race on the floor tape line! Make 12 "
                "cards: +1, +2, +3, +4, +5, +6, −1, −2, −3, −4, +10, and TEN STOP (go straight to "
                "10). Two racers start on 0 — Theodore and a parent or a stuffed animal. Take turns "
                'drawing a card, say the number sentence out loud ("6 + 4 = 10"), then hop. A '
                "card that would go below 0 or past 20 means you stay put. First racer to land "
                "EXACTLY on 20 wins!"
            ),
            "passage": (
                "Today is the Big Race! Kip and his friend Dot the Dingo race on the number line. "
                "The finish line is 20.\n\n"
                "Kip starts on 0 and hops forward 9. Then he hops forward 6 more. 9 + 6 = 15. "
                "Kip is on 15!\n\n"
                "Oh no! Kip trips on a rock and slides back 4. 15 − 4 = 11. Now Kip is on 11.\n\n"
                "Dot is on 13. She hops forward 7. 13 + 7 = 20. Dot reaches the finish line! Kip "
                "needs 9 more hops to finish. 11 + 9 = 20.\n\n"
                "The equal sign = means \"the same as.\" Dot's 13 + 7 and Kip's 11 + 9 both land on "
                "20. So 13 + 7 = 11 + 9. That is true!"
            ),
            "questions": [
                {"prompt": "After 9 + 6, what number is Kip on?", "response_lines": 1},
                {
                    "prompt": "Kip slides back 4 from 15. Is that adding or subtracting?",
                    "response_lines": 1,
                },
                {
                    "prompt": "How many hops does Kip need to get from 11 to 20?",
                    "response_lines": 1,
                },
                {"prompt": "What does the equal sign = mean?", "response_lines": 1},
                {
                    "prompt": (
                        "LET'S DISCUSS: Is 10 + 5 = 5 + 10 true? Is 10 + 5 = 20 − 5 true? How "
                        "could Kip check on the number line?"
                    ),
                    "response_lines": 0,
                },
            ],
            "vocabulary": [
                {"term": "story problem", "definition": "a math problem told as a little story"},
                {"term": "equal sign =", "definition": 'means "the same as"'},
                {
                    "term": "number sentence",
                    "definition": "math written with numbers, like 9 + 6 = 15",
                },
                {"term": "true", "definition": "both sides of = land on the same spot"},
            ],
        },
        "Friday",
    )

    fri_story = [
        (7, "Kip is on 7. He hops forward 8. Where does he land?   7 + 8 = ____"),
        (18, f"Dot is on 18. She hops back 6. Where does she land?   18 {MINUS} 6 = ____"),
        (
            None,
            "Kip must make 12 hops. He has made 5. How many hops are left?   ____ ○ ____ = ____",
        ),
        (9, "Kip ate 16 leaves. Dot ate 9. How many MORE did Kip eat? (Count up from 9.)  ____"),
        (20, "Kip is on 20. He hops back 10, then back 3 more. Where is he?  ____"),
    ]
    add(
        "numberLineWorksheet",
        {
            "title": "Race Day Story Problems",
            "instructions": (
                "Read each story with a grown-up. Draw the hops on the number line, then write the "
                "answer. On number 3, write your own number sentence — put + or − in the circle."
            ),
            "tasks": [
                {
                    "start": 0,
                    "end": 20,
                    "step": 1,
                    "mark_positions": [m] if m is not None else [],
                    "hop_space": True,
                    "prompt": p,
                }
                for m, p in fri_story
            ],
        },
        "Friday",
    )

    fri_equal = [
        "Is 8 + 4 the same as 10 + 2? Hop both on the line.   Circle:  YES   NO",
        "Is 9 + 5 the same as 7 + 6? Hop both on the line.   Circle:  YES   NO",
        "7 + 7 = 10 + ____",
        f"15 {MINUS} 5 = 6 + ____",
        f"20 {MINUS} 3 = 9 + ____",
    ]
    add(
        "numberLineWorksheet",
        {
            "title": "Same As! The Equal Sign",
            "instructions": (
                'The equal sign means "the same as." Hop the left side and the right side on the '
                "same number line. If they land on the same spot, it's true!"
            ),
            "tasks": [
                {"start": 0, "end": 20, "step": 1, "hop_space": True, "prompt": p}
                for p in fri_equal
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
            "title": "Parent Feedback & Teaching Notes",
            "instructions": "For the parent/teacher — fill in at the end of the week.",
            "passage_title": "Number Line Week Reflection",
            "passage": (
                "This week Theodore used a 0–20 number line for everything: counting forward and "
                "backward, adding as hops forward, subtracting as hops back, hopping through the "
                "Ten Stop, counting up to find a missing number, and checking if both sides of an "
                "equal sign land on the same spot. Use these notes to plan next week."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": (
                        "Counting the starting spot as hop one (8 + 3 = 10). Did this show up? "
                        "On which days?"
                    ),
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in — which number line idea clicked best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": (
                        "Bigger roads: an open number line to 100, hopping by tens "
                        "(23 + 10, 23 + 20)."
                    ),
                },
            ],
            "questions": [
                {
                    "prompt": (
                        "Overall comfort with adding and subtracting within 20 on the number "
                        "line (1 = struggled throughout, 5 = confident and quick):"
                    ),
                    "response_lines": 1,
                },
                {
                    "prompt": "Which hands-on number line did Theodore enjoy most? (tape, chalk, "
                    "rocket strip, clothesline, Big Race)",
                    "response_lines": 1,
                },
                {
                    "prompt": "Could he hop backward to subtract without mixing up the direction?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Did the Ten Stop make sense, or did he prefer counting one hop at a "
                    "time?",
                    "response_lines": 2,
                },
                {"prompt": "Facts or skills to revisit next week:", "response_lines": 2},
            ],
        },
        "Friday",
    )

    html = build_print_packet_html(pages, packet_title="Number Line Week — Math for Theodore")
    out_path = output_dir / "number_line_week.html"
    out_path.write_text(html, encoding="utf-8")

    # ── Answer keys, computed from the same data the pages were built from ────

    def li(items: list[str]) -> str:
        return "".join(f"<li>{x}</li>" for x in items)

    keys = {
        "MON_FIX": li([", ".join(map(str, h)) for _, _, h, _ in mon_fix]),
        "MON_HOPS": li([str(b) for _, _, _, b, _ in mon_hops] + ["13 and 15"]),
        "TUE_READ": li([f"{a} + {b} = {a + b}" for _, _, a, b in tue_read]),
        "TUE_DRAW": li(
            [f"{a} + {b} = {a + b}" for a, b in tue_draw] + ["3 + 9 = 12 (start on 9, hop 3)"]
        ),
        "WED_READ": li([f"{a} &minus; {b} = {a - b}" for _, _, a, b in wed_read]),
        "WED_DRAW": li([f"{a} &minus; {b} = {a - b}" for a, b in wed_draw]),
        "THU_TEN": li(
            [
                f"{a} {'+' if b > a else '&minus;'} {abs(b - a)} = {b} "
                f"(hop {abs(10 - a)} to 10, then {abs(b - 10)} more)"
                for a, b in thu_ten
            ]
            + ["6 + 8 = 14 (6 + 4 = 10, then 10 + 4 = 14)"]
        ),
        "THU_MYSTERY": li(
            [
                f"{a} + {b - a} = {b} &nbsp;and&nbsp; {b} &minus; {a} = {b - a}"
                for a, b in thu_mystery
            ]
        ),
        "THU_MATCH": li(
            [
                f"{a} + {b} = {a + b} &rarr; {partners[i].replace(MINUS, '&minus;')}"
                for i, (a, b) in enumerate(families)
            ]
        ),
    }

    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Number Line Week — Teacher Guide</title>
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
    .answer-box ol { margin-bottom: 0; }
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
  <h1>Number Line Week — Teacher / Parent Guide</h1>
  <p><strong>Subject:</strong> Math — addition &amp; subtraction within 20 &nbsp;|&nbsp;
  <strong>Audience:</strong> Theodore, Grade 1 &nbsp;|&nbsp; <strong>Narrator:</strong> Kip the Kangaroo</p>
  <p><strong>Arc:</strong> The number road &rarr; hop forward to add &rarr; hop backward to subtract
  &rarr; the Ten Stop &amp; fact families &rarr; story problems and the equal sign</p>
  <p><strong>The one rule all week:</strong> the first number is where Kip <em>stands</em>; the hops
  are what you <em>count</em>. Standing on 8 is not a hop.</p>

  <h3>Number lines to build this week (keep them up!)</h3>
  <ul>
    <li><strong>Mon — Floor tape line</strong> 0&ndash;20, one big step per number. Reused Wed and Fri.</li>
    <li><strong>Tue — Sidewalk chalk line</strong> outside, with dice for Kangaroo Add.</li>
    <li><strong>Wed — Rocket strip</strong> taped up a door frame: a vertical number line, 0 at the floor.</li>
    <li><strong>Thu — Clothesline</strong> with clothespinned index cards and a bright Ten Stop card.</li>
    <li><strong>Fri — Kip's Big Race</strong> card game on the tape line (race to land exactly on 20).</li>
  </ul>
  <p>Bonus ideas any day: a toy car driving along a ruler or tape measure (a real-world number line);
  a staircase where each step is a number; a "ten frame" sticker on the 10 spot of every line.</p>

  <h2>Monday — The Number Road</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1:</strong> A number line. <strong>Q2:</strong> 13. <strong>Q3:</strong> 11.
    <strong>Q4:</strong> To the right.</p>
  </div>
  <h3>Fix Kip's Number Road (missing numbers, in order)</h3>
  <div class="answer-box"><ol>{{MON_FIX}}</ol></div>
  <h3>One Hop Right, One Hop Left</h3>
  <div class="answer-box"><ol>{{MON_HOPS}}</ol></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Does the number line stop at 20?"</em> No — the arrow on the end means it keeps going: 21,
    22, 23… forever. Our paper road just stops at 20 because the page ends. (Bonus: the left arrow
    hints that there's something before 0, too — no need to teach it, just enjoy the wondering.)</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Skipping or doubling a number when counting backward across a decade (…12, 11, <em>9</em>…).
    Have Theodore point to each tick as he says it — one touch, one word.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Number Line Hide-and-Seek, harder: flip over <em>two</em> neighbouring sticky notes, or call out
    "I'm thinking of the number after 14 and before 16."</p>
  </div>

  <h2 class="tue">Tuesday — Hop Forward to Add</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box tue">
    <p><strong>Q1:</strong> 5. <strong>Q2:</strong> 4 hops; lands on 9. <strong>Q3:</strong> No — 6 is
    where he stands; the first hop lands on 7. <strong>Q4:</strong> 12 — it's bigger, so only 3 hops.</p>
  </div>
  <h3>Count Kip's Hops</h3>
  <div class="answer-box tue"><ol>{{TUE_READ}}</ol></div>
  <h3>Draw the Hops: Adding</h3>
  <div class="answer-box tue"><ol>{{TUE_DRAW}}</ol></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"7 + 0?"</em> Zero hops — Kip doesn't move, so he lands right where he started: 7. Adding
    zero changes nothing. Ask: "What about 0 + 7?" (Start on 0 and hop 7, or use the smart trick and
    start on 7 with no hops.)</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p><strong>The off-by-one error:</strong> saying "6" as hop one and landing on 8 for 6 + 3. Fix:
    say the start number with a little "stand" (no hop), then count "one, two, three" as the feet land.
    The numbered arcs on <em>Count Kip's Hops</em> model exactly this.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Roll two dice and add them on the chalk line — the sum is never more than 12. Then try a die and
    a start card from 10&ndash;14 for sums up to 20.</p>
  </div>

  <h2 class="wed">Wednesday — Hop Backward to Subtract</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1:</strong> Backward (to the left). <strong>Q2:</strong> Starts on 15, lands on 12.
    <strong>Q3:</strong> Smaller. <strong>Q4:</strong> 0.</p>
  </div>
  <h3>Count the Backward Hops</h3>
  <div class="answer-box wed"><ol>{{WED_READ}}</ol></div>
  <h3>Draw the Hops: Subtracting</h3>
  <div class="answer-box wed"><ol>{{WED_DRAW}}</ol></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Adding always makes bigger?"</em> Not quite! 9 + 0 = 9 and 9 &minus; 0 = 9 — zero hops means
    no change. Adding or subtracting a number bigger than zero does make it bigger or smaller.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Hopping the right number of times but in the wrong direction (12 &minus; 4 = 16). Anchor it:
    "minus is moving toward 0." On the rocket strip, subtracting is always going <em>down</em>.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Countdown launch: start the rocket on 20 and subtract the number on a die each turn. How many
    rolls until blast-off at 0? (If a roll would go below 0, it has to wait for a smaller roll.)</p>
  </div>

  <h2 class="thu">Thursday — The Ten Stop &amp; Fact Families</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1:</strong> 10. <strong>Q2:</strong> 1 hop. <strong>Q3:</strong> 3 hops left; lands on
    13. <strong>Q4:</strong> 13 &minus; 5 = 8 (or 13 &minus; 8 = 5).</p>
  </div>
  <h3>Hop to the Ten Stop</h3>
  <div class="answer-box thu"><ol>{{THU_TEN}}</ol></div>
  <h3>Mystery Hops: Count Up</h3>
  <div class="answer-box thu"><ol>{{THU_MYSTERY}}</ol></div>
  <h3>Fact Family Partners</h3>
  <div class="answer-box thu"><ul>{{THU_MATCH}}</ul>
  <p><em>The last pair is the trickiest: 9 + 8 = 17 partners with 17 &minus; 9 = 8 — the same family,
  taking away the other part.</em></p></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"6 to 14 — how many hops?"</em> Count up: 6 to the Ten Stop is 4, 10 to 14 is 4 more, so 8
    hops. This is a subtraction (14 &minus; 6 = 8) solved by adding up (6 + ? = 14). Celebrate either
    description — that both are right is the whole point of today.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Losing track of the second hop: after 8 + 2 = 10 he may add the full 5 again (landing on 15).
    Have him hold up 5 fingers and fold down 2 for the first hop — the fingers still up are the rest.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Pick any three numbers from a fact family (say 4, 9, 13) and have Theodore write all four facts,
    checking each on the clothesline.</p>
  </div>

  <h2 class="fri">Friday — Kip's Big Race</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1:</strong> 15. <strong>Q2:</strong> Subtracting (he went back). <strong>Q3:</strong> 9
    hops. <strong>Q4:</strong> "The same as."</p>
  </div>
  <h3>Race Day Story Problems</h3>
  <div class="answer-box fri"><ol>
    <li>7 + 8 = 15</li>
    <li>18 &minus; 6 = 12</li>
    <li>12 &minus; 5 = 7 (also accept 5 + 7 = 12 with good reasoning)</li>
    <li>7 more (count up from 9 to 16; 16 &minus; 9 = 7)</li>
    <li>7 (20 &minus; 10 = 10, then 10 &minus; 3 = 7)</li>
  </ol></div>
  <h3>Same As! The Equal Sign</h3>
  <div class="answer-box fri"><ol>
    <li>YES — both land on 12.</li>
    <li>NO — 9 + 5 = 14 but 7 + 6 = 13.</li>
    <li>4 (both sides land on 14)</li>
    <li>4 (both sides land on 10)</li>
    <li>8 (both sides land on 17)</li>
  </ol></div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p>Both are true: 10 + 5, 5 + 10, and 20 &minus; 5 all land on 15. Many children think "=" means
    "here comes the answer," so 10 + 5 = 20 &minus; 5 looks wrong to them. Hop each side on the line
    and point at the shared landing spot.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>On "7 + 7 = 10 + ____" the most common wrong answer is 14 (writing the answer to the left side).
    Read it as "7 + 7 is the same as 10 plus what?"</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Have Theodore invent his own Big Race card and story problem for Kip, then you solve it on the
    tape line while he checks you.</p>
  </div>
</div>

</body>
</html>"""
    for name, value in keys.items():
        TEACHER_GUIDE = TEACHER_GUIDE.replace("{{" + name + "}}", value)
    guide_path = output_dir / "number_line_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print(f"Generated {len(pages)} pages -> {output_dir}/")
    labels = [
        "Mon p1 — Reading: Meet Kip and the Number Road",
        "Mon p2 — Number Line: Fix Kip's Number Road",
        "Mon p3 — Number Line: One Hop Right, One Hop Left",
        "Tue p1 — Reading: Hop Forward to Add",
        "Tue p2 — Number Line: Count Kip's Hops",
        "Tue p3 — Number Line: Draw the Hops (Adding)",
        "Wed p1 — Reading: Hop Backward to Subtract",
        "Wed p2 — Number Line: Count the Backward Hops",
        "Wed p3 — Number Line: Draw the Hops (Subtracting)",
        "Thu p1 — Reading: The Ten Stop",
        "Thu p2 — Number Line: Hop to the Ten Stop",
        "Thu p3 — Number Line: Mystery Hops (Count Up)",
        "Thu p4 — Matching: Fact Family Partners",
        "Fri p1 — Reading: Kip's Big Race (Capstone)",
        "Fri p2 — Number Line: Race Day Story Problems",
        "Fri p3 — Number Line: Same As! The Equal Sign",
        "         Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"  {label}")
    print(f"Teacher guide -> {guide_path}")


if __name__ == "__main__":
    generate_number_line_week_series()
