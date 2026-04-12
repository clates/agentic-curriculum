import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import random

# Ensure we can import from src
sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_worksheet_to_image,
    render_worksheet_to_pdf,
    render_reading_worksheet_to_image,
    render_reading_worksheet_to_pdf,
)

random.seed(42)

TIMER_INSTRUCTIONS = (
    "Time: ____________   |   Best Time: ____________\n"
    "Ready, set, go! Solve each problem as fast as you can. Write your time when you finish!"
)


def generate_math_week_series():
    output_dir = "math_week_series"
    os.makedirs(output_dir, exist_ok=True)

    # =========================================================================
    # MONDAY — Addition Facts (Sums to 10)
    # =========================================================================

    # Monday Reading Card
    mon_reading = {
        "title": "Monday: Addition",
        "passage_title": "What Is Addition?",
        "passage": (
            "Addition means putting groups together to find a total. "
            "When you have 3 apples and someone gives you 2 more, you ADD to find out how many you have altogether. "
            "3 + 2 = 5! The answer to an addition problem is called the SUM. "
            "You can always count forward to add — start at the bigger number and count up.\n\n"
            "Here is a trick: the order of the numbers does not matter in addition! "
            "3 + 5 gives the same answer as 5 + 3. Both equal 8. "
            "This is called the Commutative Property, but you can just call it the 'flip trick.' "
            "Today you will practice adding numbers with sums up to 10. "
            "Try to remember the answers so they come to you quickly — that is called knowing your facts!"
        ),
        "instructions": "Read about addition. Then answer the questions.",
        "questions": [
            {"prompt": "What does addition mean? Use your own words.", "response_lines": 2},
            {"prompt": "What is the 'flip trick'? Give an example.", "response_lines": 2},
            {"prompt": "What is the SUM of 4 + 3? How did you figure it out?", "response_lines": 2},
        ],
        "vocabulary": [
            {
                "term": "Addition",
                "definition": "Putting two or more groups together to find a total.",
            },
            {"term": "Sum", "definition": "The answer you get when you add numbers together."},
            {
                "term": "Flip Trick",
                "definition": "The order of numbers in addition does not change the answer (3+5 = 5+3).",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", mon_reading)
    render_reading_worksheet_to_image(ws, f"{output_dir}/01_monday_reading_card.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/01_monday_reading_card.pdf")

    # Monday Drill — 12 addition problems, sums to 10
    mon_problems = [
        {"operand_one": 1, "operand_two": 2, "operator": "+"},
        {"operand_one": 3, "operand_two": 3, "operator": "+"},
        {"operand_one": 2, "operand_two": 5, "operator": "+"},
        {"operand_one": 4, "operand_two": 1, "operator": "+"},
        {"operand_one": 6, "operand_two": 2, "operator": "+"},
        {"operand_one": 0, "operand_two": 7, "operator": "+"},
        {"operand_one": 5, "operand_two": 3, "operator": "+"},
        {"operand_one": 1, "operand_two": 9, "operator": "+"},
        {"operand_one": 4, "operand_two": 4, "operator": "+"},
        {"operand_one": 2, "operand_two": 8, "operator": "+"},
        {"operand_one": 3, "operand_two": 7, "operator": "+"},
        {"operand_one": 5, "operand_two": 5, "operator": "+"},
    ]
    random.shuffle(mon_problems)
    mon_drill = {
        "title": "Monday Drill: Addition Facts",
        "instructions": TIMER_INSTRUCTIONS,
        "problems": mon_problems,
        "metadata": {"drill_type": "timed"},
    }
    ws = WorksheetFactory.create("two_operand", mon_drill)
    render_worksheet_to_image(ws, f"{output_dir}/02_monday_drill.png")
    render_worksheet_to_pdf(ws, f"{output_dir}/02_monday_drill.pdf")

    # Monday Parent Feedback Sheet
    mon_feedback = {
        "title": "Monday: Parent Feedback — Addition",
        "passage_title": "Today's Focus & Teaching Notes",
        "passage": (
            "Today's goal was to build fluency with addition facts that sum to 10. "
            "If your child counted on their fingers, that is completely normal — gently encourage them to "
            "try starting from the larger number and counting up just the smaller amount (e.g. for 3+6, start at 6 and count '7, 8, 9'). "
            "This 'count-on' strategy is a key bridge to memorization.\n\n"
            "For the timed drill: record today's time in the Best Time box. Every day this week there will be a new drill — "
            "the goal is to beat yesterday's personal best, not to compete with anyone else. "
            "Celebrate effort and improvement, not perfection. "
            "Watch for: reversing digits in the answer (writing 9 as 6), skipping a number while counting on, "
            "or hesitation on +0 and +1 facts (these should become automatic quickly)."
        ),
        "instructions": "Please fill in the feedback after the lesson.",
        "questions": [
            {
                "prompt": "How comfortable was your child with addition facts today? (1 = struggled, 5 = nailed it)",
                "response_lines": 1,
            },
            {
                "prompt": "What was today's drill time? Did they beat a previous time?",
                "response_lines": 1,
            },
            {
                "prompt": "Any specific facts or concepts they struggled with? Note them here.",
                "response_lines": 2,
            },
            {"prompt": "Any wins or moments of confidence to celebrate?", "response_lines": 2},
        ],
        "vocabulary": [
            {
                "term": "Count-On Strategy",
                "definition": "Start at the bigger number and count up the smaller one.",
            },
            {
                "term": "Fluency",
                "definition": "Knowing math facts quickly and accurately, without needing to count every time.",
            },
            {
                "term": "Personal Best",
                "definition": "Beating your own previous time or score — the only competition that matters!",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", mon_feedback)
    render_reading_worksheet_to_image(ws, f"{output_dir}/03_monday_parent_feedback.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/03_monday_parent_feedback.pdf")

    # =========================================================================
    # TUESDAY — Subtraction Facts (Within 10)
    # =========================================================================

    # Tuesday Reading Card
    tue_reading = {
        "title": "Tuesday: Subtraction",
        "passage_title": "What Is Subtraction?",
        "passage": (
            "Subtraction means taking away from a group to find what is left. "
            "If you have 8 grapes and eat 3 of them, you SUBTRACT to find out how many remain. "
            "8 − 3 = 5. The answer to a subtraction problem is called the DIFFERENCE. "
            "One way to subtract is to count backward — start at the bigger number and count down.\n\n"
            "Here is something important: subtraction is the OPPOSITE of addition. "
            "If you know that 4 + 6 = 10, then you already know that 10 − 6 = 4! "
            "Addition and subtraction are partners. "
            "Today you will practice subtracting from numbers up to 10. "
            "Try using what you already know about addition to help you."
        ),
        "instructions": "Read about subtraction. Then answer the questions.",
        "questions": [
            {"prompt": "What does subtraction mean? Use your own words.", "response_lines": 2},
            {
                "prompt": "What is the DIFFERENCE in 9 − 4? How did you solve it?",
                "response_lines": 2,
            },
            {"prompt": "How can knowing 3 + 5 = 8 help you solve 8 − 5?", "response_lines": 2},
        ],
        "vocabulary": [
            {"term": "Subtraction", "definition": "Taking away from a group to find what is left."},
            {
                "term": "Difference",
                "definition": "The answer you get when you subtract one number from another.",
            },
            {
                "term": "Count-Back",
                "definition": "Start at the bigger number and count down to subtract.",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", tue_reading)
    render_reading_worksheet_to_image(ws, f"{output_dir}/04_tuesday_reading_card.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/04_tuesday_reading_card.pdf")

    # Tuesday Drill — 12 subtraction problems, within 10
    tue_problems = [
        {"operand_one": 5, "operand_two": 2, "operator": "-"},
        {"operand_one": 9, "operand_two": 3, "operator": "-"},
        {"operand_one": 7, "operand_two": 4, "operator": "-"},
        {"operand_one": 10, "operand_two": 6, "operator": "-"},
        {"operand_one": 8, "operand_two": 5, "operator": "-"},
        {"operand_one": 6, "operand_two": 1, "operator": "-"},
        {"operand_one": 4, "operand_two": 4, "operator": "-"},
        {"operand_one": 10, "operand_two": 3, "operator": "-"},
        {"operand_one": 7, "operand_two": 7, "operator": "-"},
        {"operand_one": 9, "operand_two": 5, "operator": "-"},
        {"operand_one": 6, "operand_two": 2, "operator": "-"},
        {"operand_one": 8, "operand_two": 1, "operator": "-"},
    ]
    random.shuffle(tue_problems)
    tue_drill = {
        "title": "Tuesday Drill: Subtraction Facts",
        "instructions": TIMER_INSTRUCTIONS,
        "problems": tue_problems,
        "metadata": {"drill_type": "timed"},
    }
    ws = WorksheetFactory.create("two_operand", tue_drill)
    render_worksheet_to_image(ws, f"{output_dir}/05_tuesday_drill.png")
    render_worksheet_to_pdf(ws, f"{output_dir}/05_tuesday_drill.pdf")

    # Tuesday Parent Feedback Sheet
    tue_feedback = {
        "title": "Tuesday: Parent Feedback — Subtraction",
        "passage_title": "Today's Focus & Teaching Notes",
        "passage": (
            "Today's goal was fluency with subtraction facts within 10. "
            "The key connection to reinforce is that subtraction is the reverse of addition — "
            "if your child already knows their addition facts from Monday, they have a huge head start. "
            "Try asking: 'You know 3 + 7 = 10, so what is 10 − 7?' to show the relationship explicitly.\n\n"
            "For the count-back strategy: some children find it easier to 'count up from the smaller number' "
            "to the larger (e.g. for 9 − 6, think '6... 7, 8, 9 — that's 3!'). "
            "Either strategy is valid. Watch for: confusion with zero (anything minus itself = 0), "
            "and accidental switching of operands (trying to do 3 − 9 instead of 9 − 3). "
            "Compare today's drill time to Monday's — even if the operations are different, "
            "tracking the timer builds the habit of focused, efficient work."
        ),
        "instructions": "Please fill in the feedback after the lesson.",
        "questions": [
            {
                "prompt": "How comfortable was your child with subtraction facts today? (1 = struggled, 5 = nailed it)",
                "response_lines": 1,
            },
            {
                "prompt": "Today's drill time vs. Monday's time — any improvement in focus or speed?",
                "response_lines": 1,
            },
            {
                "prompt": "Did they use count-back, count-up, or addition facts to subtract? Which worked best?",
                "response_lines": 2,
            },
            {
                "prompt": "Any specific subtraction facts that need more practice?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Count-Up Strategy",
                "definition": "Start at the smaller number and count up to the bigger one to find the difference.",
            },
            {
                "term": "Inverse Operations",
                "definition": "Addition and subtraction undo each other — they are opposites.",
            },
            {
                "term": "Zero Property",
                "definition": "Any number minus itself equals zero (e.g. 7 − 7 = 0).",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", tue_feedback)
    render_reading_worksheet_to_image(ws, f"{output_dir}/06_tuesday_parent_feedback.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/06_tuesday_parent_feedback.pdf")

    # =========================================================================
    # WEDNESDAY — Fact Families
    # =========================================================================

    # Wednesday Reading Card
    wed_reading = {
        "title": "Wednesday: Fact Families",
        "passage_title": "The Fact Family House",
        "passage": (
            "A fact family is a group of three numbers that work together to make four math facts. "
            "Take the numbers 3, 4, and 7. Watch what they can do:\n"
            "3 + 4 = 7     4 + 3 = 7     7 − 3 = 4     7 − 4 = 3\n"
            "Those four facts are a FACT FAMILY! The three numbers live together like a family in a house. "
            "The biggest number always goes at the top of the house (it is the sum or the whole). "
            "The two smaller numbers are the parts.\n\n"
            "Knowing one fact from a family means you already know all four! "
            "If you know 5 + 2 = 7, you can figure out 2 + 5, 7 − 2, and 7 − 5 without any extra work. "
            "Today's drill uses numbers from the same fact families. "
            "See if you can spot which numbers belong together!"
        ),
        "instructions": "Read about fact families. Then answer the questions.",
        "questions": [
            {
                "prompt": "What is a fact family? How many facts does one family make?",
                "response_lines": 2,
            },
            {
                "prompt": "Write all four facts for the family with 2, 6, and 8.",
                "response_lines": 3,
            },
            {
                "prompt": "If 9 − 4 = 5, what is 9 − 5? How do you know without counting?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Fact Family",
                "definition": "A set of three numbers that create four related addition and subtraction facts.",
            },
            {
                "term": "Whole",
                "definition": "The biggest number in a fact family — the total or sum.",
            },
            {
                "term": "Parts",
                "definition": "The two smaller numbers in a fact family that add up to the whole.",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", wed_reading)
    render_reading_worksheet_to_image(ws, f"{output_dir}/07_wednesday_reading_card.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/07_wednesday_reading_card.pdf")

    # Wednesday Drill — 12 problems using fact family triplets
    # Triplets: (2,6,8), (3,4,7), (1,5,6), (4,5,9)
    wed_problems = [
        # Family: 2, 6, 8
        {"operand_one": 2, "operand_two": 6, "operator": "+"},
        {"operand_one": 8, "operand_two": 2, "operator": "-"},
        # Family: 3, 4, 7
        {"operand_one": 3, "operand_two": 4, "operator": "+"},
        {"operand_one": 7, "operand_two": 3, "operator": "-"},
        # Family: 1, 5, 6
        {"operand_one": 1, "operand_two": 5, "operator": "+"},
        {"operand_one": 6, "operand_two": 5, "operator": "-"},
        # Family: 4, 5, 9
        {"operand_one": 4, "operand_two": 5, "operator": "+"},
        {"operand_one": 9, "operand_two": 4, "operator": "-"},
        # Flip side of each family
        {"operand_one": 6, "operand_two": 2, "operator": "+"},
        {"operand_one": 8, "operand_two": 6, "operator": "-"},
        {"operand_one": 5, "operand_two": 4, "operator": "+"},
        {"operand_one": 9, "operand_two": 5, "operator": "-"},
    ]
    random.shuffle(wed_problems)
    wed_drill = {
        "title": "Wednesday Drill: Fact Families",
        "instructions": TIMER_INSTRUCTIONS,
        "problems": wed_problems,
        "metadata": {"drill_type": "timed"},
    }
    ws = WorksheetFactory.create("two_operand", wed_drill)
    render_worksheet_to_image(ws, f"{output_dir}/08_wednesday_drill.png")
    render_worksheet_to_pdf(ws, f"{output_dir}/08_wednesday_drill.pdf")

    # Wednesday Parent Feedback Sheet
    wed_feedback = {
        "title": "Wednesday: Parent Feedback — Fact Families",
        "passage_title": "Today's Focus & Teaching Notes",
        "passage": (
            "Today's goal was understanding the relationship between addition and subtraction through fact families. "
            "This is one of the most powerful early math concepts — once a child truly 'sees' that three numbers "
            "create four facts, their recall speed doubles because they only need to memorize half as much.\n\n"
            "A great hands-on activity: draw a triangle on paper, write the 'whole' at the top and the two 'parts' "
            "at the bottom corners. Cover any one number and ask your child to figure out the missing one. "
            "On the timed drill today, the problems are intentionally grouped by family — your child may notice "
            "the pattern mid-drill and speed up. That 'aha' moment is the goal! "
            "Watch for: treating each problem as completely new (not connecting 3+4 to 7−3), "
            "and confusion about which number is the 'whole' in a subtraction problem."
        ),
        "instructions": "Please fill in the feedback after the lesson.",
        "questions": [
            {
                "prompt": "How comfortable was your child with fact families today? (1 = struggled, 5 = nailed it)",
                "response_lines": 1,
            },
            {
                "prompt": "Today's drill time — new personal best? Note their time here.",
                "response_lines": 1,
            },
            {
                "prompt": "Did they notice the fact family pattern during the drill? Describe their reaction.",
                "response_lines": 2,
            },
            {
                "prompt": "Which fact family triplets were hardest? Which felt automatic?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Fact Family Triangle",
                "definition": "A triangle with the whole at the top and two parts at the bottom — cover any corner to find a missing number.",
            },
            {
                "term": "Related Facts",
                "definition": "The four addition and subtraction sentences made from one fact family.",
            },
            {
                "term": "Missing Number",
                "definition": "The unknown in a math sentence — e.g. 7 − ___ = 4.",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", wed_feedback)
    render_reading_worksheet_to_image(ws, f"{output_dir}/09_wednesday_parent_feedback.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/09_wednesday_parent_feedback.pdf")

    # =========================================================================
    # THURSDAY — Multiplication as Repeated Addition
    # =========================================================================

    # Thursday Reading Card
    thu_reading = {
        "title": "Thursday: Multiplication",
        "passage_title": "Groups of Things: The Secret of Multiplication",
        "passage": (
            "Multiplication is a fast way to add the SAME number over and over. "
            "Imagine you have 3 bags, and each bag holds 4 apples. "
            "You could add: 4 + 4 + 4 = 12. Or you could multiply: 3 × 4 = 12. Same answer, less writing!\n\n"
            "The multiplication symbol × means 'groups of.' So 3 × 4 means '3 groups of 4.' "
            "Today we will practice using addition to SHOW multiplication. "
            "When you add 2 + 2 + 2, that is the same as 3 × 2. "
            "When you add 5 + 5, that is the same as 2 × 5. "
            "Today's drill uses doubles and equal groups — see how fast you can add equal groups together! "
            "You are already doing multiplication, even if it looks like addition."
        ),
        "instructions": "Read about multiplication as repeated addition. Then answer the questions.",
        "questions": [
            {
                "prompt": "What does 4 × 3 mean in words? Write it as an addition problem too.",
                "response_lines": 2,
            },
            {
                "prompt": "What is 5 + 5 + 5? What multiplication fact does that equal?",
                "response_lines": 2,
            },
            {
                "prompt": "Why is multiplication a useful shortcut? Explain in your own words.",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Multiplication",
                "definition": "A fast way to add the same number multiple times.",
            },
            {
                "term": "Groups of",
                "definition": "What the × symbol means — 3 × 4 means 3 groups of 4.",
            },
            {
                "term": "Repeated Addition",
                "definition": "Adding the same number over and over: 2+2+2 = 3×2.",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", thu_reading)
    render_reading_worksheet_to_image(ws, f"{output_dir}/10_thursday_reading_card.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/10_thursday_reading_card.pdf")

    # Thursday Drill — 10 problems: doubles and equal-group additions
    # Each problem represents a "groups of" multiplication fact
    # Instructions call out the connection explicitly
    thu_problems = [
        # 2 groups of... (doubles)
        {"operand_one": 2, "operand_two": 2, "operator": "+"},  # 2×2
        {"operand_one": 3, "operand_two": 3, "operator": "+"},  # 2×3
        {"operand_one": 4, "operand_two": 4, "operator": "+"},  # 2×4
        {"operand_one": 5, "operand_two": 5, "operator": "+"},  # 2×5
        {"operand_one": 6, "operand_two": 6, "operator": "+"},  # 2×6
        # Slightly larger equal groups (building toward 3×, 4×, 5×)
        {"operand_one": 3, "operand_two": 6, "operator": "+"},  # partial 3×3... = 9
        {"operand_one": 4, "operand_two": 8, "operator": "+"},  # partial 3×4
        {"operand_one": 5, "operand_two": 10, "operator": "+"},  # partial 3×5
        {"operand_one": 2, "operand_two": 8, "operator": "+"},  # 2×5 extended
        {"operand_one": 6, "operand_two": 4, "operator": "+"},  # mixed equal groups
    ]
    random.shuffle(thu_problems)
    thu_drill = {
        "title": "Thursday Drill: Equal Groups (Repeated Addition)",
        "instructions": (
            "Time: ____________   |   Best Time: ____________\n"
            "Each problem is a 'groups of' puzzle! Solve fast — you are doing multiplication!"
        ),
        "problems": thu_problems,
        "metadata": {"drill_type": "timed"},
    }
    ws = WorksheetFactory.create("two_operand", thu_drill)
    render_worksheet_to_image(ws, f"{output_dir}/11_thursday_drill.png")
    render_worksheet_to_pdf(ws, f"{output_dir}/11_thursday_drill.pdf")

    # Thursday Parent Feedback Sheet
    thu_feedback = {
        "title": "Thursday: Parent Feedback — Multiplication as Repeated Addition",
        "passage_title": "Today's Focus & Teaching Notes",
        "passage": (
            "Today's goal was introducing multiplication conceptually through repeated addition and equal groups. "
            "At age 6, we are not expecting memorized times tables — we want the child to understand WHAT "
            "multiplication means so that when they do encounter the × symbol formally, it makes sense.\n\n"
            "Great extension activity: use physical objects (coins, blocks, crackers). "
            "Put out 3 groups of 4 objects and count together. Then write '4 + 4 + 4 = 12' and '3 × 4 = 12' side by side. "
            "On the timed drill, doubles (2+2, 3+3, etc.) should be the fastest problems — these become "
            "the anchor facts for the 2× table. Celebrate if your child starts saying 'that's just doubling!' "
            "Watch for: adding the wrong number of groups, and confusing the × symbol with +."
        ),
        "instructions": "Please fill in the feedback after the lesson.",
        "questions": [
            {
                "prompt": "How comfortable was your child with the 'groups of' concept today? (1 = struggled, 5 = nailed it)",
                "response_lines": 1,
            },
            {
                "prompt": "Today's drill time — new personal best? How are the doubles coming along?",
                "response_lines": 1,
            },
            {
                "prompt": "Did they make the connection between addition and multiplication? Describe.",
                "response_lines": 2,
            },
            {
                "prompt": "What physical objects or examples clicked best for explaining equal groups?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Doubles",
                "definition": "Adding a number to itself — e.g. 4+4=8. These become the 2× multiplication table.",
            },
            {
                "term": "Equal Groups",
                "definition": "Groups that all contain the same number of items — the foundation of multiplication.",
            },
            {
                "term": "Times Table",
                "definition": "A list of multiplication facts for one number — e.g. the 2s: 2, 4, 6, 8, 10...",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", thu_feedback)
    render_reading_worksheet_to_image(ws, f"{output_dir}/12_thursday_parent_feedback.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/12_thursday_parent_feedback.pdf")

    # =========================================================================
    # FRIDAY — Mixed Review (All Operations)
    # =========================================================================

    # Friday Reading Card
    fri_reading = {
        "title": "Friday: Mixed Review",
        "passage_title": "Math Champion Week: You Did It!",
        "passage": (
            "You have had an incredible week of math! Think about everything you have learned:\n"
            "On Monday you practiced ADDITION — putting groups together to find a sum. "
            "On Tuesday you practiced SUBTRACTION — taking away to find the difference. "
            "On Wednesday you discovered FACT FAMILIES — how three numbers make four facts. "
            "On Thursday you explored MULTIPLICATION — the secret shortcut for equal groups.\n\n"
            "Today is your final challenge: a MIXED drill with both addition and subtraction. "
            "READ the sign carefully on every problem — a + means add, a − means subtract. "
            "This is the most important skill of all: paying attention to WHAT the problem is asking. "
            "Today is also your best chance to set a new personal record on the timer. "
            "You know these facts — trust yourself, stay focused, and go for it!"
        ),
        "instructions": "Read about your math week. Then answer the questions.",
        "questions": [
            {
                "prompt": "Name all four operations you learned about this week. Write one example of each.",
                "response_lines": 3,
            },
            {
                "prompt": "What is a fact family? Write the four facts for 3, 5, and 8.",
                "response_lines": 3,
            },
            {
                "prompt": "What is the most important thing to check before solving any math problem?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {"term": "Addition (+)", "definition": "Putting groups together to find the sum."},
            {"term": "Subtraction (−)", "definition": "Taking away to find the difference."},
            {
                "term": "Mixed Review",
                "definition": "A practice session that includes more than one type of operation.",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", fri_reading)
    render_reading_worksheet_to_image(ws, f"{output_dir}/13_friday_reading_card.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/13_friday_reading_card.pdf")

    # Friday Drill — 12 mixed +/− problems, slightly harder numbers (sums/minuends to 18)
    fri_problems = [
        {"operand_one": 7, "operand_two": 5, "operator": "+"},
        {"operand_one": 14, "operand_two": 6, "operator": "-"},
        {"operand_one": 8, "operand_two": 9, "operator": "+"},
        {"operand_one": 13, "operand_two": 7, "operator": "-"},
        {"operand_one": 6, "operand_two": 7, "operator": "+"},
        {"operand_one": 11, "operand_two": 4, "operator": "-"},
        {"operand_one": 9, "operand_two": 8, "operator": "+"},
        {"operand_one": 16, "operand_two": 9, "operator": "-"},
        {"operand_one": 5, "operand_two": 8, "operator": "+"},
        {"operand_one": 15, "operand_two": 8, "operator": "-"},
        {"operand_one": 7, "operand_two": 6, "operator": "+"},
        {"operand_one": 12, "operand_two": 5, "operator": "-"},
    ]
    random.shuffle(fri_problems)
    fri_drill = {
        "title": "Friday Drill: Mixed Review — Personal Best Challenge!",
        "instructions": (
            "Time: ____________   |   Best Time: ____________\n"
            "Read the sign on every problem! Can you beat this week's best time? GO!"
        ),
        "problems": fri_problems,
        "metadata": {"drill_type": "timed"},
    }
    ws = WorksheetFactory.create("two_operand", fri_drill)
    render_worksheet_to_image(ws, f"{output_dir}/14_friday_drill.png")
    render_worksheet_to_pdf(ws, f"{output_dir}/14_friday_drill.pdf")

    # Friday Parent Feedback Sheet
    fri_feedback = {
        "title": "Friday: Parent Feedback — Mixed Review & Week Wrap-Up",
        "passage_title": "Week Summary & Teaching Notes",
        "passage": (
            "Congratulations on completing a full week of structured math! Today's mixed drill is intentionally "
            "harder — problems go up to 18 to see how your child handles slightly larger numbers. "
            "The most important thing to observe today is whether they READ the operation sign before solving. "
            "Many children default to always adding — a subtraction sign they miss is the most common error.\n\n"
            "For the timed drill today: this is the big personal-best attempt for the whole week. "
            "Build excitement around it! Looking ahead: next week you can continue building on fact families "
            "by introducing 'missing number' problems (7 + ___ = 10), and on multiplication by exploring "
            "skip counting by 2s, 5s, and 10s. The doubles from Thursday are the direct bridge to the 2× table."
        ),
        "instructions": "Please fill in the weekly wrap-up feedback.",
        "questions": [
            {
                "prompt": "How comfortable was your child with mixed +/− problems today? (1 = struggled, 5 = nailed it)",
                "response_lines": 1,
            },
            {
                "prompt": "Final drill time this week — did they set a personal best? Record all 5 times if you have them.",
                "response_lines": 2,
            },
            {
                "prompt": "Which of the four topics this week was strongest? Which needs the most review?",
                "response_lines": 2,
            },
            {
                "prompt": "Overall notes — energy levels, engagement, any topics to revisit next week?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Missing Addend",
                "definition": "The unknown number in an addition problem: 6 + ___ = 10. Great next step!",
            },
            {
                "term": "Skip Counting",
                "definition": "Counting by 2s, 5s, or 10s — the foundation of the times tables.",
            },
            {
                "term": "Personal Best",
                "definition": "Your fastest time this week — something to try to beat next week!",
            },
        ],
    }
    ws = WorksheetFactory.create("reading_comprehension", fri_feedback)
    render_reading_worksheet_to_image(ws, f"{output_dir}/15_friday_parent_feedback.png")
    render_reading_worksheet_to_pdf(ws, f"{output_dir}/15_friday_parent_feedback.pdf")

    print(f"Successfully generated Math Week series in '{output_dir}/'")
    print("15 worksheets created (5 days × 3 sheets each):")
    print("  Mon: 01_monday_reading_card, 02_monday_drill, 03_monday_parent_feedback")
    print("  Tue: 04_tuesday_reading_card, 05_tuesday_drill, 06_tuesday_parent_feedback")
    print("  Wed: 07_wednesday_reading_card, 08_wednesday_drill, 09_wednesday_parent_feedback")
    print("  Thu: 10_thursday_reading_card, 11_thursday_drill, 12_thursday_parent_feedback")
    print("  Fri: 13_friday_reading_card, 14_friday_drill, 15_friday_parent_feedback")


if __name__ == "__main__":
    generate_math_week_series()
