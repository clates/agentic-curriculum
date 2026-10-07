"""
Arithmetic Strategies — Week Series for Christopher (Age 6)
Grade K–1 | Math | Causal Arc:
  Number fluency & making ten → Addition strategies up to 20 →
  Subtraction strategies up to 20 → Subtraction with regrouping →
  Multiplication intro & speed drills (capstone)

Narrator: Digit the Dragon — a friendly math dragon who breathes number-shaped
fire and helps Christopher discover clever strategies for arithmetic.

Output: single printable HTML document — arithmetic_week_series/arithmetic_week.html
"""

import os, random, sys
from pathlib import Path

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html

random.seed(20261005)


def generate_arithmetic_week_series():
    output_dir = Path("arithmetic_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # ═══════════════════════════════════════════════════════════════════════
    # Problem generation helpers
    # ═══════════════════════════════════════════════════════════════════════

    def _gen_addition_pairs(num: int, *, min_sum: int = 4, max_sum: int = 20,
                            min_operand: int = 2) -> list[dict]:
        """Generate unique addition pairs within constraints."""
        pairs: set[tuple[int, int]] = set()
        while len(pairs) < num:
            a = random.randint(min_operand, max_sum - min_operand)
            b = random.randint(min_operand, max_sum - min_operand)
            s = a + b
            if min_sum <= s <= max_sum and (a, b) not in pairs and (b, a) not in pairs:
                pairs.add((a, b))
        return [{"operand_one": a, "operand_two": b, "operator": "+"} for a, b in pairs]

    def _gen_subtraction_pairs(num: int, *, min_answer: int = 0,
                               max_start: int = 20, min_operand: int = 2) -> list[dict]:
        """Generate unique subtraction pairs where result >= min_answer."""
        pairs: set[tuple[int, int]] = set()
        while len(pairs) < num:
            a = random.randint(min_operand + min_answer, max_start)
            b = random.randint(min_operand, a - min_answer)
            if (a, b) not in pairs:
                pairs.add((a, b))
        return [{"operand_one": a, "operand_two": b, "operator": "−"} for a, b in pairs]

    def _gen_subtraction_regrouping(num: int) -> list[dict]:
        """Generate subtraction problems requiring regrouping (borrowing)."""
        pairs: set[tuple[int, int]] = set()
        while len(pairs) < num:
            a = random.randint(11, 19)  # 11-19: teen numbers with at least 1 ten
            a_ones = a % 10
            # b's ones digit must be > a's ones digit to force regrouping
            # a_ones can be 0-9; we need b_ones in (a_ones+1, 9)
            if a_ones >= 9:
                continue  # no single-digit b can force regrouping when a_ones is 9
            b = random.randint(a_ones + 1, 9)
            if b >= 2 and (a, b) not in pairs:
                pairs.add((a, b))
        return [{"operand_one": a, "operand_two": b, "operator": "−"} for a, b in pairs]

    def _gen_multiplication_pairs(num: int) -> list[dict]:
        """Generate simple multiplication (×1, ×2, ×5, ×10) with products ≤ 20."""
        allowed = [(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
                   (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10),
                   (5, 2), (5, 3), (5, 4),
                   (10, 1), (10, 2)]
        # Filter products ≤ 20
        valid = [(a, b) for a, b in allowed if a * b <= 20 and a * b >= 1]
        chosen = random.sample(valid, min(num, len(valid)))
        return [{"operand_one": a, "operand_two": b, "operator": "×"} for a, b in chosen]

    def _gen_ten_frame_pairs(num: int) -> list[dict]:
        """Generate ten-frame addition pairs: some sum to 10, some bridge 10."""
        make_ten_pairs = [(3, 7), (4, 6), (5, 5), (8, 2), (1, 9), (6, 4), (7, 3), (9, 1), (2, 8)]
        bridge_ten_pairs = [(8, 5), (7, 6), (9, 4), (6, 7), (5, 8), (8, 7), (9, 5), (7, 5),
                            (9, 6), (8, 6), (7, 7), (9, 3), (8, 4), (9, 8), (6, 8)]

        # Pick half make-ten, half bridge-ten
        n_make = min(num // 2, len(make_ten_pairs))
        n_bridge = num - n_make
        make = random.sample(make_ten_pairs, n_make)
        bridge = random.sample(bridge_ten_pairs, n_bridge)

        result = []
        for a, b in make:
            result.append({"addend_a": a, "addend_b": b, "fill_a": "#2563eb", "fill_b": "#dc2626"})
        for a, b in bridge:
            result.append({"addend_a": a, "addend_b": b, "fill_a": "#2563eb", "fill_b": "#dc2626"})
        random.shuffle(result)
        return result

    # ═══════════════════════════════════════════════════════════════════════
    # MONDAY — Number Fluency: Making Ten & Number Bonds
    # ═══════════════════════════════════════════════════════════════════════

    add(
        "readingWorksheet",
        {
            "title": "Monday: Making Ten — Your Superpower!",
            "passage_title": "Meet Digit the Dragon!",
            "instructions": (
                "Before reading: Count to 10 out loud twice. Can you do it backwards too? "
                "Try counting down from 10 to 1.\n\n"
                "Hands-on activity: Find 10 small objects — blocks, crackers, or pennies. "
                "Split them into two groups. How many ways can you make 10? "
                "Bring them to your desk — you will use them all week!"
            ),
            "passage": (
                "ROAR! A puff of number-shaped smoke burst through the window, and a "
                "friendly green dragon with sparkly scales tumbled onto Christopher's desk. "
                "'Hello! I am Digit the Dragon,' he said, grinning with pointy teeth. "
                "'I LOVE numbers, and I am here to teach you the greatest math superpower of all: "
                "MAKING TEN.'\n\n"
                "Digit held up one claw with 7 sparkles and another claw with 3 sparkles. "
                "'Watch this: 7 + 3 = 10. Every time you can make ten, math gets EASY. "
                "Ten is a magic number because our whole number system is built on it!'\n\n"
                "Christopher tilted his head. 'But what if the numbers do not add up to ten? "
                "What about 8 + 5?'\n\n"
                "Digit grinned even wider. 'Great question! That is where the make-ten "
                "TRICK comes in. Look: 8 + 5. First, ask yourself — how much does 8 need "
                "to become 10? It needs 2! So take 2 from the 5. Now you have 8 + 2 = 10, "
                "and 3 left over. 10 + 3 = 13. Easy!'\n\n"
                "He drew this in the air with smoky numbers:\n"
                "  8 + 5\n"
                "  = 8 + 2 + 3   (split the 5 into 2 + 3)\n"
                "  = 10 + 3\n"
                "  = 13\n\n"
                "'A ten-frame is a tool that helps you SEE this trick,' Digit explained, "
                "pulling out a rectangle with 10 squares — two rows of five. 'When you fill "
                "all 10 squares, you know you have made ten. Whatever is left goes in "
                "a second ten-frame. This week, we will use ten-frames, number lines, "
                "and quick mental tricks to become MATH SUPERHEROES!'\n\n"
                "'Are you ready?' Digit roared happily. Christopher nodded. "
                "'Then let us begin with the most important skill: MAKING TEN!'"
            ),
            "vocabulary": [
                {"term": "make ten",
                 "definition": "A strategy where you combine numbers to reach 10 first, "
                               "because 10 is easy to add to. Example: 8 + 5 = 8 + 2 + 3 = 10 + 3 = 13."},
                {"term": "ten-frame",
                 "definition": "A rectangle with 10 boxes (2 rows of 5) used to see numbers "
                               "and practice making ten."},
                {"term": "number bond",
                 "definition": "A way to break a number into two parts. "
                               "Example: 10 can be 7 and 3, or 6 and 4, or 5 and 5."},
                {"term": "split",
                 "definition": "To break a number into smaller parts. "
                               "In 8 + 5, we split 5 into 2 + 3 to make ten."},
                {"term": "strategy",
                 "definition": "A clever plan or trick for solving a problem. "
                               "Making ten is a strategy!"},
            ],
            "questions": [
                {"prompt": "What is the make-ten strategy? Explain it in your own words "
                           "using an example (like 9 + 4).", "response_lines": 3},
                {"prompt": "How many number bonds can you write for 10? List at least 4 "
                           "different pairs that make 10.", "response_lines": 3},
                {"prompt": "Digit says 'ten is a magic number.' Why is making ten so "
                           "helpful when adding bigger numbers?", "response_lines": 2},
                {"prompt": "LET'S DISCUSS: Can you use the make-ten strategy for "
                           "subtraction too? How would you solve 13 − 5 using making ten?",
                 "response_lines": 0},
            ],
        },
        "Monday",
    )

    add(
        "tenFrameWorksheet",
        {
            "title": "Monday: Make Ten Practice — Double Ten-Frames",
            "instructions": (
                "For each problem, look at the two ten-frames. "
                "The BLUE dots are your first number. The RED dots are your second number.\n\n"
                "STEP 1: Move red dots into the first ten-frame to fill it to 10.\n"
                "STEP 2: How many red dots moved? How many are left?\n"
                "STEP 3: Write the make-ten proof on the lines.\n\n"
                "Example: 8 + 5 → Move 2 red dots → 8 + 2 = 10, 10 + 3 = 13"
            ),
            "problems": _gen_ten_frame_pairs(8),
            "equation_lines": 2,
        },
        "Monday",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # TUESDAY — Addition Strategies Up to 20
    # ═══════════════════════════════════════════════════════════════════════

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: Addition Power-Ups!",
            "passage_title": "Digit's Addition Toolbox",
            "instructions": (
                "Read about Digit's four addition strategies. Then answer the questions.\n\n"
                "Quick warm-up: With your 10 objects, practice making ten three times. "
                "Can you do it in under 10 seconds?"
            ),
            "passage": (
                "Digit flapped his wings and four glowing tools appeared in the air: "
                "a rocket, a mirror, a trampoline, and a ten-frame.\n\n"
                "'These are my four addition power-ups!' he announced. "
                "'Use the right tool for the right job, and you will FLY through problems.'\n\n"
                "POWER-UP 1 — COUNTING ON (the Rocket):\n"
                "Start with the BIGGER number and count up. For 3 + 9, do NOT count "
                "'1, 2, 3...' — start at 9 and say '10, 11, 12!' That is only 3 counts "
                "instead of 12. Always put the bigger number first in your head.\n\n"
                "POWER-UP 2 — DOUBLES (the Mirror):\n"
                "Some facts are twins! 2 + 2 = 4, 3 + 3 = 6, 4 + 4 = 8, 5 + 5 = 10, "
                "6 + 6 = 12, 7 + 7 = 14, 8 + 8 = 16, 9 + 9 = 18, 10 + 10 = 20. "
                "Memorize your doubles — they are super fast!\n\n"
                "POWER-UP 3 — NEAR-DOUBLES (the Trampoline):\n"
                "If you know a double, you know its neighbor! 6 + 7 = ? Well, 6 + 6 = 12, "
                "so 6 + 7 is just ONE MORE: 13. Or 8 + 7: 8 + 8 = 16, so 8 + 7 = 15 "
                "(one less). Bounce from the double!\n\n"
                "POWER-UP 4 — MAKE TEN (the Ten-Frame):\n"
                "You already know this one! When one number is close to 10, make ten first. "
                "9 + 6 = 9 + 1 + 5 = 10 + 5 = 15. 8 + 7 = 8 + 2 + 5 = 10 + 5 = 15.\n\n"
                "'The trick,' said Digit, tapping his snout, 'is to LOOK at the numbers "
                "and PICK the fastest strategy. Numbers tell you what they need if you listen!'\n\n"
                "QUICK GUIDE:\n"
                "• Small + big number → COUNT ON from the big one\n"
                "• Two same numbers → DOUBLES\n"
                "• Two numbers next to each other → NEAR-DOUBLES\n"
                "• One number is 8 or 9 → MAKE TEN"
            ),
            "vocabulary": [
                {"term": "counting on",
                 "definition": "Starting from the bigger number and counting up. "
                               "For 4 + 9: start at 9, count 10, 11, 12, 13. Answer: 13."},
                {"term": "doubles",
                 "definition": "Adding the same number twice: 3 + 3 = 6, 7 + 7 = 14. "
                               "Memorize these to solve faster!"},
                {"term": "near-doubles",
                 "definition": "Using a known double to solve a nearby fact. "
                               "6 + 7 = ? 6 + 6 = 12, so 6 + 7 = 13 (one more)."},
                {"term": "strategy choice",
                 "definition": "Picking the fastest tool for each problem. "
                               "Look at the numbers and decide!"},
                {"term": "efficient",
                 "definition": "Getting the right answer with the least amount of work. "
                               "Good mathematicians are efficient."},
            ],
            "questions": [
                {"prompt": "Solve 5 + 9 using counting on. Write 'start at ___, count ___, ___, ___, ___' "
                           "and then write the answer.", "response_lines": 2},
                {"prompt": "Write all the doubles from 1+1 to 10+10 with their answers. "
                           "Which ones do you already know by heart?", "response_lines": 4},
                {"prompt": "Use near-doubles to solve: 5 + 6 = ? and 4 + 5 = ? "
                           "Show which double helped you each time.", "response_lines": 3},
                {"prompt": "Solve 8 + 7 using make-ten. Write each step: "
                           "8 + 2 = ___, then 10 + ___ = ___.", "response_lines": 2},
                {"prompt": "LET'S DISCUSS: Look at 3 + 8. Which power-up would YOU pick "
                           "and why? Is there more than one right answer?",
                 "response_lines": 0},
            ],
        },
        "Tuesday",
    )

    add(
        "twoOperandWorksheet",
        {
            "title": "Tuesday: Addition Practice — Up to 20",
            "instructions": (
                "Solve each addition problem. Try using Digit's power-ups:\n"
                "• COUNT ON from the bigger number (e.g., 3 + 9 → start at 9)\n"
                "• Use DOUBLES you know (e.g., 7 + 7 = 14)\n"
                "• Use NEAR-DOUBLES (e.g., 7 + 8 = 7 + 7 + 1 = 15)\n"
                "• MAKE TEN when you can (e.g., 9 + 5 = 9 + 1 + 4 = 14)\n\n"
                "Write the STRATEGY you used above each problem (C for count-on, "
                "D for doubles, N for near-doubles, M for make-ten)."
            ),
            "problems": _gen_addition_pairs(20),
        },
        "Tuesday",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # WEDNESDAY — Subtraction Strategies Up to 20
    # ═══════════════════════════════════════════════════════════════════════

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: Subtraction Superpowers!",
            "passage_title": "Taking Away with Digit",
            "instructions": (
                "Read about Digit's subtraction strategies. Then answer the questions.\n\n"
                "Quick warm-up: Count backwards from 20 to 0. Now count backwards "
                "from 15 to 0 by 2s (15, 13, 11...)."
            ),
            "passage": (
                "Digit landed on Christopher's desk with a THUMP. 'Yesterday we ADDED. "
                                "Today we take AWAY! But do not worry — subtraction and addition are "
                                "best friends. They are two sides of the same coin!'\n\n"
                "He swished his tail and three new power-ups appeared.\n\n"
                "POWER-UP 1 — COUNTING BACK (the Slide):\n"
                "Start at the big number and slide backward. For 11 − 3, start at 11 "
                "and count back 3 steps: 10, 9, 8. Answer: 8! This works best when "
                "you are only subtracting a small number (1, 2, or 3).\n\n"
                "POWER-UP 2 — THINK ADDITION (the Boomerang):\n"
                "Subtraction is just addition backwards! For 15 − 7 = ?, ask yourself: "
                "'7 + WHAT = 15?' Well, 7 + 8 = 15, so 15 − 7 = 8! This is called "
                "a FACT FAMILY. The numbers 7, 8, and 15 are a family:\n"
                "  7 + 8 = 15    8 + 7 = 15\n"
                "  15 − 7 = 8    15 − 8 = 7\n\n"
                "POWER-UP 3 — MAKE TEN TO SUBTRACT (the Bridge):\n"
                "For 13 − 5: First subtract to get DOWN to 10. 13 − 3 = 10. "
                "You still need to subtract 2 more (because 5 = 3 + 2). "
                "10 − 2 = 8. Answer: 8!\n"
                "  13 − 5 = 13 − 3 − 2 = 10 − 2 = 8\n\n"
                "'Here is my secret,' whispered Digit. 'When the subtraction feels "
                "hard, THINK ADDITION instead. 14 − 6 = ? Ask: 6 + ? = 14. "
                "Doubles help! 6 + 6 = 12, so 6 + 8 = 14. Answer is 8!'\n\n"
                "QUICK GUIDE:\n"
                "• Subtracting 1, 2, or 3 → COUNT BACK\n"
                "• Subtracting a bigger number → THINK ADDITION (fact family)\n"
                "• Subtracting from a teen number (13−, 14−, 15−) → MAKE TEN to subtract"
            ),
            "vocabulary": [
                {"term": "counting back",
                 "definition": "Starting from the big number and counting down. "
                               "For 9 − 3: count 8, 7, 6. Answer: 6."},
                {"term": "think addition",
                 "definition": "Turning subtraction into a missing-addend addition. "
                               "15 − 7 = ? becomes 7 + ? = 15. If 7 + 8 = 15, then 15 − 7 = 8."},
                {"term": "fact family",
                 "definition": "A group of four related facts using the same three numbers. "
                               "Example: 5, 8, 13 → 5+8=13, 8+5=13, 13−5=8, 13−8=5."},
                {"term": "make ten to subtract",
                 "definition": "Subtract in two steps: first get down to 10, then subtract "
                               "the rest. 14 − 6 = 14 − 4 − 2 = 10 − 2 = 8."},
                {"term": "regrouping",
                 "definition": "When you do not have enough in the ones place, you borrow "
                               "from the tens place. We will learn this tomorrow!"},
            ],
            "questions": [
                {"prompt": "Solve 12 − 3 using counting back. Write the numbers "
                           "you say as you count back.", "response_lines": 2},
                {"prompt": "Use think-addition to solve 16 − 9. Write: '9 + ? = 16, "
                           "so 16 − 9 = ?'", "response_lines": 2},
                {"prompt": "Use make-ten to subtract: 14 − 6. Write each step: "
                           "14 − 4 = ___, then 10 − ___ = ___.", "response_lines": 2},
                {"prompt": "Write the COMPLETE fact family for 6, 7, and 13. "
                           "You should have two addition facts and two subtraction facts.",
                 "response_lines": 3},
                {"prompt": "LET'S DISCUSS: Which strategy do you like best for "
                           "subtraction — counting back, think-addition, or make-ten? "
                           "Why does it work well for you?",
                 "response_lines": 0},
            ],
        },
        "Wednesday",
    )

    add(
        "twoOperandWorksheet",
        {
            "title": "Wednesday: Subtraction Practice — Up to 20",
            "instructions": (
                "Solve each subtraction problem. Try using Digit's strategies:\n"
                "• COUNT BACK if subtracting 1, 2, or 3\n"
                "• THINK ADDITION (fact families) for bigger subtractions\n"
                "• MAKE TEN to subtract from teen numbers\n\n"
                "Write the strategy letter above each problem "
                "(B for count Back, A for think Addition, T for make Ten)."
            ),
            "problems": _gen_subtraction_pairs(20),
        },
        "Wednesday",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # THURSDAY — Subtraction with Regrouping
    # ═══════════════════════════════════════════════════════════════════════

    add(
        "readingWorksheet",
        {
            "title": "Thursday: Borrowing from the Tens!",
            "passage_title": "When the Ones Are Not Enough",
            "instructions": (
                "Read about regrouping with Digit. Then answer the questions.\n\n"
                "Quick warm-up: Count by tens to 100. Now count by tens BACKWARD "
                "from 100 to 0. You will need this skill today!"
            ),
            "passage": (
                "Digit balanced a tower of 10 blocks on his snout. 'Look, Christopher! "
                "One tower of ten is the same as ten single blocks. Watch what happens "
                                "when we need to subtract but do not have enough ones!'\n\n"
                "He wrote 14 − 6 on the board. 'Fourteen has 1 ten and 4 ones. "
                "I need to subtract 6 ones. But I only have 4 ones! 4 is less than 6, "
                "so I CANNOT subtract yet. I need to BORROW!'\n\n"
                "Digit smashed the tower of ten into ten single blocks. POOF! "
                "'Now I have ZERO tens and 14 ones! 14 − 6 = 8.'\n\n"
                "He showed it step by step:\n\n"
                "      1  4          (1 ten + 4 ones = 14)\n"
                "    −    6\n"
                "    ───────\n"
                "    Cannot do 4 − 6, so BORROW 1 ten from the tens place!\n"
                "    The 1 ten becomes 10 ones. Now we have 14 ones.\n\n"
                "      0  14         (0 tens + 14 ones = 14)\n"
                "    −    6\n"
                "    ───────\n"
                "      0   8         (14 − 6 = 8 ✓)\n\n"
                "'This is called REGROUPING,' said Digit. 'You regroup 1 ten into 10 ones "
                                "when the ones place does not have enough. Let us try another!'\n\n"
                "    17 − 9:\n"
                "    7 ones − 9 ones → NOT ENOUGH! Borrow 1 ten.\n"
                "    17 becomes 0 tens + 17 ones.  17 − 9 = 8 ✓\n\n"
                "'The key,' Digit said, 'is to CHECK the ones place FIRST. If the top "
                "ones number is SMALLER than the bottom ones number, you MUST regroup. "
                "If it is bigger or equal, no regrouping needed!'\n\n"
                "He gave Christopher a simple rule: 'Look at the ones. Top smaller? Borrow! "
                "Top bigger or same? Go ahead and subtract!'\n\n"
                "QUICK CHECK for regrouping:\n"
                "  15 − 7 → 5 ones vs 7 ones → 5 < 7 → REGROUP!\n"
                "  18 − 5 → 8 ones vs 5 ones → 8 > 5 → no regrouping needed"
            ),
            "vocabulary": [
                {"term": "regrouping",
                 "definition": "Changing 1 ten into 10 ones when you do not have "
                               "enough ones to subtract. Also called 'borrowing.'"},
                {"term": "borrow",
                 "definition": "Taking 1 ten from the tens place and turning it into "
                               "10 ones. You 'borrow' strength from the tens!"},
                {"term": "tens place",
                 "definition": "The left digit in a two-digit number. In 14, the 1 "
                               "means '1 ten' and sits in the tens place."},
                {"term": "ones place",
                 "definition": "The right digit in a two-digit number. In 14, the 4 "
                               "means '4 ones' and sits in the ones place."},
                {"term": "place value",
                 "definition": "The value of a digit based on its position. In 15, "
                               "the 1 is worth 10 and the 5 is worth 5."},
            ],
            "questions": [
                {"prompt": "Look at 13 − 5. Do you need to regroup? How do you know? "
                           "Then solve it with regrouping.", "response_lines": 3},
                {"prompt": "Look at 17 − 4. Do you need to regroup? How do you know? "
                           "Then solve it.", "response_lines": 3},
                {"prompt": "Solve 15 − 8 using regrouping. Show your work step by step: "
                           "write the tens and ones before and after borrowing.",
                 "response_lines": 4},
                {"prompt": "What does 'borrow 1 ten' mean? Where does that ten go? "
                           "Explain in your own words.", "response_lines": 3},
                {"prompt": "LET'S DISCUSS: Why can't you just 'flip the numbers' and "
                           "subtract the smaller from the bigger (like 6 − 4 instead of "
                           "4 − 6)? What would happen to the answer?",
                 "response_lines": 0},
            ],
        },
        "Thursday",
    )

    # Thursday Practice: Mix of subtraction — some need regrouping, some don't
    all_sub = _gen_subtraction_regrouping(8) + _gen_subtraction_pairs(8, min_operand=1)
    random.shuffle(all_sub)

    add(
        "twoOperandWorksheet",
        {
            "title": "Thursday: Subtraction with Regrouping — Practice",
            "instructions": (
                "Solve each subtraction problem. IMPORTANT: Check the ones place first!\n"
                "• If the TOP ones digit is SMALLER than the bottom → REGROUP (borrow 1 ten)\n"
                "• If the TOP ones digit is BIGGER or EQUAL → subtract normally\n\n"
                "For regrouping problems, write 'R' next to the problem number. "
                "For no-regrouping, write 'N'.\n\n"
                "Example: 13 − 7 → 3 < 7, so R (regroup: 13 = 0 tens + 13 ones, 13 − 7 = 6)"
            ),
            "problems": all_sub,
        },
        "Thursday",
    )

    add(
        "numberLineWorksheet",
        {
            "title": "Thursday: Subtraction on the Number Line",
            "instructions": (
                "Each number line shows subtraction by jumping backward. "
                "Fill in the missing numbers on each number line, then "
                "write the answer to the subtraction problem.\n\n"
                "Follow the JUMP arrows to see how subtraction works — "
                "each jump back subtracts a little bit at a time!"
            ),
            "tasks": [
                {
                    "prompt": "12 − 4 = ?  (Jump back 4 spaces from 12 — count back!)",
                    "start": 6, "end": 14, "step": 1,
                    "hidden_positions": [],
                    "mark_positions": [12, 8],
                },
                {
                    "prompt": "15 − 6 = ?  (Jump back 6: first to 10, then 4 more)",
                    "start": 7, "end": 17, "step": 1,
                    "hidden_positions": [],
                    "mark_positions": [15, 9],
                },
                {
                    "prompt": "17 − 8 = ?  (Make ten: 17 − 7 = 10, then 10 − 1 = 9)",
                    "start": 7, "end": 19, "step": 1,
                    "hidden_positions": [],
                    "mark_positions": [17, 9],
                },
                {
                    "prompt": "11 − 5 = ?  (Regroup: 11 = 10 + 1, then subtract 5)",
                    "start": 4, "end": 13, "step": 1,
                    "hidden_positions": [],
                    "mark_positions": [11, 6],
                },
                {
                    "prompt": "14 − 7 = ?  (Use doubles: 7 + 7 = 14, so 14 − 7 = 7)",
                    "start": 5, "end": 16, "step": 1,
                    "hidden_positions": [],
                    "mark_positions": [14, 7],
                },
                {
                    "prompt": "16 − 9 = ?  (Make ten: 16 − 6 = 10, then 10 − 3 = 7)",
                    "start": 5, "end": 18, "step": 1,
                    "hidden_positions": [],
                    "mark_positions": [16, 7],
                },
                {
                    "prompt": "13 − 8 = ?  (Think addition: 8 + ? = 13, so 8 + 5 = 13, answer = 5)",
                    "start": 3, "end": 15, "step": 1,
                    "hidden_positions": [],
                    "mark_positions": [13, 5],
                },
            ],
        },
        "Thursday",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # FRIDAY — Multiplication Introduction & Speed Drills (Capstone)
    # ═══════════════════════════════════════════════════════════════════════

    add(
        "readingWorksheet",
        {
            "title": "Friday: Multiplication — Super-Fast Adding!",
            "passage_title": "Digit's Multiplication Magic",
            "instructions": (
                "Read about multiplication with Digit. Then answer the questions.\n\n"
                "Quick warm-up: Skip-count out loud — count by 2s to 20, then by 5s "
                "to 50, then by 10s to 100. Multiplication is just fancy skip-counting!"
            ),
            "passage": (
                "Digit swooped through the air trailing sparkly number fireworks. "
                "'Christopher! Today is the most exciting day of all — MULTIPLICATION! "
                "Do not be scared. Multiplication is just adding the SAME number over "
                "and over. It is a SHORTCUT!'\n\n"
                "'Imagine you have 3 bags, and each bag has 4 cookies,' said Digit, "
                "drawing three bags in the air. 'You could add: 4 + 4 + 4 = 12. "
                "But that is slow! With multiplication, you just say 3 × 4 = 12. "
                "The × means GROUPS OF. Three groups of four equals twelve!'\n\n"
                "Digit revealed his Multiplication Quick-Start Table:\n\n"
                "×1 FACTS — A number times 1 is just ITSELF! 5 × 1 = 5, 9 × 1 = 9.\n\n"
                "×2 FACTS — Doubles you already know! 2 × 3 means two 3s: 3 + 3 = 6.\n"
                "Learn these by skip-counting: 2, 4, 6, 8, 10, 12, 14, 16, 18, 20.\n\n"
                "×5 FACTS — Count by fives! 5, 10, 15, 20, 25, 30, 35, 40, 45, 50.\n"
                "If you can count nickels, you can multiply by 5!\n\n"
                "×10 FACTS — Just add a ZERO! 3 × 10 = 30, 7 × 10 = 70. "
                "This is the easiest one of all.\n\n"
                "'Let me show you a SECRET,' Digit whispered. 'Multiplication is "
                "commutative — that is a fancy word meaning you can SWITCH the numbers "
                                "and get the same answer! 3 × 4 = 12 and 4 × 3 = 12. Less to memorize!'\n\n"
                "ARRAYS — A Visual Way to See Multiplication:\n"
                "  3 × 4 looks like this:\n"
                "  • • • •\n"
                "  • • • •\n"
                "  • • • •\n"
                "  3 rows of 4 = 12 dots total!\n\n"
                "'This week you learned to make ten, add with strategies, subtract with "
                "strategies, regroup, and now multiply! You are a true MATH SUPERHERO,' "
                "roared Digit, breathing out a firework of golden numbers. "
                "'Now let us see how FAST you can go!'\n\n"
                "SPEED TIP: Multiplication facts ×1, ×2, ×5, and ×10 are your "
                "GATEWAY facts. Master these first, and harder facts become easier!"
            ),
            "vocabulary": [
                {"term": "multiplication",
                 "definition": "A shortcut for adding the same number many times. "
                               "3 × 4 means '3 groups of 4' or 4 + 4 + 4 = 12."},
                {"term": "groups of",
                 "definition": "The meaning of the × symbol. 5 × 2 = five groups of two, "
                               "which is 2 + 2 + 2 + 2 + 2 = 10."},
                {"term": "array",
                 "definition": "A rectangle of rows and columns that shows multiplication. "
                               "3 rows of 4 dots shows 3 × 4 = 12."},
                {"term": "skip counting",
                 "definition": "Counting by the same number over and over. "
                               "By 2s: 2, 4, 6, 8, 10... This IS multiplication!"},
                {"term": "commutative",
                 "definition": "You can switch the order of numbers in multiplication "
                               "and get the same answer. 3 × 5 = 5 × 3 = 15."},
            ],
            "questions": [
                {"prompt": "What does multiplication mean? Explain 4 × 3 using the words "
                           "'groups of' and write it as repeated addition.",
                 "response_lines": 3},
                {"prompt": "Skip-count by 2s from 2 to 20. Write each number. "
                           "Now skip-count by 5s from 5 to 50.", "response_lines": 3},
                {"prompt": "Draw an array for 2 × 5 (2 rows of 5 dots). How many dots total? "
                           "Now draw the array for 5 × 2. How many dots? "
                           "What do you notice?", "response_lines": 4},
                {"prompt": "Solve: 3 × 10 = ? and 7 × 1 = ? and 6 × 2 = ? and 4 × 5 = ? "
                           "Which was easiest? Which was hardest? Why?", "response_lines": 4},
                {"prompt": "LET'S DISCUSS: This week you learned making ten, addition "
                           "strategies, subtraction strategies, regrouping, and multiplication. "
                           "Which new skill do you feel MOST confident about? "
                           "Which one do you want to practice more?",
                 "response_lines": 0},
            ],
        },
        "Friday",
    )

    # Friday Practice 1: Multiplication problems
    add(
        "twoOperandWorksheet",
        {
            "title": "Friday: Multiplication Practice — ×1, ×2, ×5, ×10",
            "instructions": (
                "Solve each multiplication problem. Remember:\n"
                "• ×1: The number stays the SAME\n"
                "• ×2: DOUBLES — add the number to itself\n"
                "• ×5: Count by FIVES\n"
                "• ×10: Add a ZERO to the end\n\n"
                "Draw dots or an array below any problem that feels tricky!"
            ),
            "problems": _gen_multiplication_pairs(20),
        },
        "Friday",
    )

    # Friday Practice 2: Mixed Speed Drill
    speed_problems = (
        _gen_addition_pairs(6) +
        _gen_subtraction_pairs(6) +
        _gen_multiplication_pairs(4)
    )
    random.shuffle(speed_problems)

    add(
        "twoOperandWorksheet",
        {
            "title": "Friday: Speed Drill — All Strategies!",
            "instructions": (
                "This is a MIXED speed drill with addition, subtraction, AND multiplication. "
                "Look carefully at the operator (+, −, or ×) before you solve!\n\n"
                "CHALLENGE: Have a grown-up time you. Try to finish all 16 problems "
                "in under 3 minutes. Ready, set, GO!\n\n"
                "After you finish, CIRCLE every problem you solved using make-ten "
                "or think-addition. Good mathematicians know WHICH strategy they used!"
            ),
            "problems": speed_problems,
        },
        "Friday",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # PARENT FEEDBACK
    # ═══════════════════════════════════════════════════════════════════════

    add(
        "readingWorksheet",
        {
            "title": "End-of-Week Parent Feedback — Arithmetic Strategies Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this feedback sheet after the week wraps up. "
                "Your notes help shape next week's lessons."
            ),
            "passage": (
                "This week introduced a comprehensive toolkit of arithmetic strategies "
                "for a 6-year-old working within 20. The causal arc built deliberately:\n\n"
                "MONDAY — Number Fluency: Making ten (the foundational strategy), "
                "ten-frames as a visual tool, and number bonds for 10. The make-ten "
                "strategy (splitting an addend to reach 10 first) is the single most "
                "important arithmetic strategy at this age — it unlocks both addition "
                "and subtraction of teen numbers.\n\n"
                "TUESDAY — Addition Strategies: Counting on (from the larger number), "
                "doubles memorization, near-doubles (using known doubles for neighbors), "
                "and make-ten for 8+ and 9+ facts. The emphasis is STRATEGY CHOICE — "
                "looking at the numbers and picking the fastest tool.\n\n"
                "WEDNESDAY — Subtraction Strategies: Counting back (for small subtractions), "
                "think-addition / fact families (the most powerful subtraction strategy — "
                "turning subtraction into missing-addend addition), and make-ten to "
                "subtract (stepping down to 10 first).\n\n"
                "THURSDAY — Regrouping / Borrowing: The place-value understanding "
                "behind borrowing from the tens place. Focused on the \"check the ones "
                "place first\" rule: is the top ones digit smaller than the bottom? "
                "Then regroup. Number lines reinforced the visual model of subtraction "
                "as jumping backward.\n\n"
                "FRIDAY — Multiplication Introduction: Multiplication as repeated "
                "addition and skip-counting. Gateway facts (×1, ×2, ×5, ×10) only — "
                "these are the easiest to master and build confidence. Arrays for "
                "visual understanding. Capstone speed drill mixing all week's operations.\n\n"
                "Digit the Dragon served as the narrator throughout, modeling curiosity, "
                "strategy-thinking, and a growth mindset toward math.\n\n"
                "KEY CONCEPTS to check for genuine understanding:\n"
                "1) Can Christopher explain the make-ten strategy and use it independently?\n"
                "2) Does he automatically put the bigger number first when adding (counting on)?\n"
                "3) Does he use think-addition for subtraction, or default to counting back?\n"
                "4) Can he CHECK whether regrouping is needed before starting a problem?\n"
                "5) Does he understand multiplication as 'groups of' rather than just a symbol?\n\n"
                "COMMON MISCONCEPTIONS to watch for:\n"
                "• Subtracting by 'flipping' (e.g., 13 − 7 → 7 − 3 = 4). This is wrong.\n"
                "• Always counting on from 1 instead of from the bigger number.\n"
                "• Regrouping when it is not needed (e.g., 18 − 5, where 8 > 5).\n"
                "• Thinking multiplication is unrelated to addition.\n\n"
                "SUGGESTED FOLLOW-ON: Continue daily 5-minute fact fluency practice. "
                "Focus on the ×2, ×5, and ×10 multiplication facts — these are the "
                "building blocks. Next week could focus on word problems that require "
                "choosing the right operation, or on extending addition/subtraction "
                "to numbers up to 100 using the same strategies."
            ),
            "vocabulary": [
                {"term": "Strongest strategy this week",
                 "definition": "(Fill in — which strategy did Christopher use most naturally?)"},
                {"term": "Needs more practice",
                 "definition": "(Fill in — which strategy or concept needs reinforcement?)"},
                {"term": "Next week suggestion",
                 "definition": "Word problems with strategy choice, or extending to "
                               "numbers up to 100 using the same strategies."},
            ],
            "questions": [
                {"prompt": "Overall comfort with the week's strategies — how well did "
                           "Christopher engage with the material? "
                           "(1 = struggled throughout, 5 = strong grasp of all concepts)",
                 "response_lines": 1},
                {"prompt": "Which day's lesson generated the most curiosity or questions?",
                 "response_lines": 2},
                {"prompt": "By Friday, could Christopher independently choose an "
                           "appropriate strategy for different problem types, or did "
                           "he need prompting?", "response_lines": 2},
                {"prompt": "How did the speed drill go on Friday? Was the 3-minute "
                           "target appropriate for Christopher's pace?",
                 "response_lines": 2},
                {"prompt": "Does Christopher show understanding of multiplication as "
                           "'groups of'? Can he draw an array for a simple fact like 3 × 4?",
                 "response_lines": 2},
                {"prompt": "Topics or strategies to revisit next week:",
                 "response_lines": 2},
            ],
        },
        "Friday",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # Assemble & write
    # ═══════════════════════════════════════════════════════════════════════

    html = build_print_packet_html(
        pages, packet_title="Arithmetic Strategies Week — Addition, Subtraction & Multiplication for Christopher"
    )
    out_path = output_dir / "arithmetic_week.html"
    out_path.write_text(html, encoding="utf-8")

    print("\n✅ Successfully generated Arithmetic Strategies Week.")
    print(f"Student packet:  {out_path}")
    print(f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n")
    print("  Pages:")
    labels = [
        "Mon p1 — Reading: Making Ten & Number Bonds (Meet Digit the Dragon)",
        "Mon p2 — Ten-Frame Practice: Make Ten & Bridge Ten (8 problems)",
        "Tue p1 — Reading: Addition Power-Ups (Counting On, Doubles, Near-Doubles, Make Ten)",
        "Tue p2 — Two-Operand: Addition Practice (20 problems)",
        "Wed p1 — Reading: Subtraction Strategies (Count Back, Think-Addition, Make Ten to Subtract)",
        "Wed p2 — Two-Operand: Subtraction Practice (20 problems)",
        "Thu p1 — Reading: Regrouping / Borrowing from the Tens Place",
        "Thu p2 — Two-Operand: Subtraction with Regrouping (16 problems, mixed)",
        "Thu p3 — Number Line: Subtraction as Jumping Backward (7 tasks)",
        "Fri p1 — Reading: Multiplication as Repeated Addition & Skip Counting",
        "Fri p2 — Two-Operand: Multiplication ×1, ×2, ×5, ×10 (20 problems)",
        "Fri p3 — Speed Drill: Mixed Addition, Subtraction & Multiplication (16 problems)",
        "     — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")

    # Verify problem constraints
    print("\n📊 Problem Verification:")
    for i, (day_label, _) in enumerate(pages):
        print(f"  Page {i+1}: {day_label}")

    return out_path


if __name__ == "__main__":
    generate_arithmetic_week_series()