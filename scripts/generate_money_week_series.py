"""
Money — Week Series
Grade K–1 | Math + Social Studies | Causal Arc:
  What is money & why do we use it? → Coins & their values → Counting a collection of coins →
  Earning & saving money → Needs vs. Wants & making smart choices

Narrator: Penny the Piggy Bank, introduced on Monday. A cheerful pink piggy bank who collects
coins and helps Christopher understand how money works in everyday life.
Output: single printable HTML document — money_week_series/money_week.html

Standards (Virginia SOL):
  Monday    — VA.HISTORY.K.k.8, VA.HISTORY.1.1.8
                (what money is; why people use it; goods and services)
  Tuesday   — VA.MATH.K.k.7
                (recognize penny, nickel, dime, quarter; equivalencies)
  Wednesday — VA.MATH.1.1.8, VA.MATH.K.k.6
                (determine value of a collection of like coins; single-step coin problems)
  Thursday  — VA.HISTORY.K.k.8, VA.MATH.1.1.6
                (earning and saving money; single-step money story problems within 20)
  Friday    — VA.HISTORY.1.1.8, VA.MATH.1.1.8
                (capstone: needs vs. wants; prioritizing choices; counting mixed like-coin sets)
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html


def generate_money_week_series():
    output_dir = Path("money_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — What Is Money and Why Do We Use It?
    # Standards: VA.HISTORY.K.k.8, VA.HISTORY.1.1.8
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: What Is Money?",
            "passage_title": "Meet Penny — and Why Money Matters!",
            "instructions": (
                "Before reading: Look around your home for a few coins or ask a grown-up to "
                "show you some. Hold them in your hand. How do they feel? Are they the same size? "
                "Bring them back to your desk and set them aside — you will need them later this week!"
            ),
            "passage": (
                "Meet Penny the Piggy Bank! Penny is a shiny pink piggy bank with a big smile "
                "and a slot on her back just wide enough for a coin. She sits on Christopher's "
                "bookshelf and every day she says, 'Put a little money in me and watch it grow!'\n\n"
                "But what exactly IS money? Money is anything that people agree to use to buy "
                "and sell things. Long ago, people traded things they had for things they needed — "
                "a farmer might trade a bag of apples for a pair of shoes. That is called bartering. "
                "But bartering was tricky! What if the shoemaker did not want apples that day? "
                "People needed something that everyone agreed was valuable — so coins and paper "
                "bills were invented.\n\n"
                "Today we use money to buy goods and services. A good is something you can hold "
                "and take home — like a toy, a book, an apple, or a pair of shoes. A service is "
                "something someone does for you — like a haircut, a doctor's visit, or a teacher "
                "teaching a lesson. When you pay for a good or service, you give money, and the "
                "other person gives you what you asked for.\n\n"
                "'Every coin in my belly once helped someone buy something important,' Penny "
                "oinked happily. 'Money makes trading much easier for everyone!'"
            ),
            "vocabulary": [
                {
                    "term": "money",
                    "definition": "Coins and bills that people agree to use to buy and sell things.",
                },
                {
                    "term": "bartering",
                    "definition": "Trading one thing for another without using money — like swapping apples for shoes.",
                },
                {
                    "term": "goods",
                    "definition": "Things you can hold and take home that you buy with money, like food, toys, or clothes.",
                },
                {
                    "term": "services",
                    "definition": "Things people do for you that you pay for, like a haircut or a doctor's visit.",
                },
                {
                    "term": "trade",
                    "definition": "Giving something to get something else in return — buying is a kind of trade.",
                },
            ],
            "questions": [
                {
                    "prompt": "Why did people invent money? What problem did it solve?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What is the difference between a good and a service? Give one example of each.",
                    "response_lines": 3,
                },
                {
                    "prompt": "What is bartering? Can you think of a time you traded something with a friend?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: If you had a bag of apples and needed new shoes, how would you use bartering to get them? What problems might come up?",
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    add(
        "tChartWorksheet",
        {
            "title": "Monday: Goods and Services — T-Chart",
            "instructions": (
                "Read each item in the word bank. Is it a good (something you hold and take home) "
                "or a service (something someone does for you)? Write each item in the correct column."
            ),
            "columns": ["Goods", "Services"],
            "row_count": 8,
            "word_bank": [
                "Haircut",
                "Apple",
                "Library book",
                "Doctor visit",
                "Soccer ball",
                "Pizza delivery",
                "Toy car",
                "Piano lesson",
                "Backpack",
                "Lawn mowing",
            ],
        },
        "Monday",
    )

    # =========================================================================
    # TUESDAY — Coins and Their Values
    # Standards: VA.MATH.K.k.7
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: Coins and Their Values",
            "passage_title": "Penny Introduces Her Coin Friends",
            "instructions": (
                "Read about each coin with Penny. If you have real coins, pick them up as Penny "
                "introduces each one and look carefully at both sides.\n\n"
                "Hands-on activity: Sort your coins into four piles — pennies, nickels, dimes, "
                "and quarters. Which pile has the most coins? Which single coin is worth the most?"
            ),
            "passage": (
                "Penny shook herself and four coins tumbled out onto the table. 'Let me introduce "
                "you to my four best friends!' she said proudly.\n\n"
                "'First, meet the PENNY. A penny is a small copper-colored coin worth ONE cent. "
                "That means it takes 100 pennies to make one dollar! On the front is Abraham Lincoln, "
                "the 16th president of the United States. On the back is the Lincoln Memorial. "
                "Pennies are worth 1 cent — we write that as 1¢.'\n\n"
                "'Next is the NICKEL. A nickel is a bigger, silver-colored coin worth FIVE cents. "
                "One nickel equals five pennies — you would need five pennies to match one nickel! "
                "Thomas Jefferson is on the front, and Monticello (his home) is on the back. '5¢.'\n\n"
                "'Now meet the DIME. The dime is the SMALLEST coin, but do not let its size fool you "
                "— it is worth TEN cents! One dime equals two nickels, or ten pennies. "
                "Franklin Roosevelt is on the front, and a torch with an olive branch is on the back. '10¢.'\n\n"
                "'Finally, the QUARTER. A quarter is a large, silver coin worth TWENTY-FIVE cents. "
                "It takes four quarters to make one dollar. George Washington is on the front. '25¢.'\n\n"
                "Penny smiled. 'Now you know all four of my coin friends. Remember: penny = 1¢, "
                "nickel = 5¢, dime = 10¢, quarter = 25¢. Say it with me!'"
            ),
            "vocabulary": [
                {
                    "term": "cent (¢)",
                    "definition": "The smallest unit of money in the United States. 100 cents = 1 dollar.",
                },
                {
                    "term": "penny",
                    "definition": "A copper-colored coin worth 1 cent. 100 pennies = $1.",
                },
                {
                    "term": "nickel",
                    "definition": "A silver coin worth 5 cents. 5 pennies = 1 nickel.",
                },
                {
                    "term": "dime",
                    "definition": "The smallest coin, worth 10 cents. 10 pennies or 2 nickels = 1 dime.",
                },
                {
                    "term": "quarter",
                    "definition": "A large silver coin worth 25 cents. 4 quarters = $1 (one dollar).",
                },
            ],
            "questions": [
                {
                    "prompt": "List all four coins from least to greatest value. Write the name and the value (in cents) for each.",
                    "response_lines": 3,
                },
                {
                    "prompt": "How many pennies equal one nickel? How many pennies equal one dime?",
                    "response_lines": 2,
                },
                {
                    "prompt": "The dime is the smallest coin but it is worth more than a penny or a nickel. Does size tell us the value of a coin? Explain.",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: Why do you think coins have pictures of famous people on them? What person would YOU put on a coin and why?",
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "featureMatrixWorksheet",
        {
            "title": "Tuesday: Coin Comparison — Feature Matrix",
            "instructions": (
                "Put a check mark in every box that describes each coin. "
                "Use your reading card to find the clues — look carefully!"
            ),
            "items": ["Penny", "Nickel", "Dime", "Quarter"],
            "properties": [
                "Copper color",
                "Silver color",
                "Worth less than 10¢",
                "Worth 10¢ or more",
                "Smallest coin by size",
                "Has a president on the front",
                "Worth exactly 5 pennies",
                "Takes 4 to make a dollar",
            ],
        },
        "Tuesday",
    )

    # =========================================================================
    # WEDNESDAY — Counting Coins
    # Standards: VA.MATH.1.1.8, VA.MATH.K.k.6
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: Counting Coins",
            "passage_title": "How to Count a Pile of Coins",
            "instructions": (
                "Read about counting coins with Penny. Then practice with real coins if you have them.\n\n"
                "Hands-on activity: Ask a grown-up to make three coin piles for you — "
                "one pile of only pennies, one pile of only nickels, one pile of only dimes. "
                "Count each pile and find the total value. Which pile is worth the most?"
            ),
            "passage": (
                "Penny had a very important lesson. 'Knowing what each coin is worth is great,' "
                "she said, 'but what about when you have a BUNCH of coins? How do you count them?'\n\n"
                "The key is to start with the coin that is worth the MOST, and count down. "
                "But today, Penny wants to practice counting piles of the SAME coin — that is "
                "the first step before mixing coins together.\n\n"
                "COUNTING PENNIES: Each penny is 1¢. Count them one by one: 1¢, 2¢, 3¢... "
                "If you have 7 pennies, you have 7¢. Easy!\n\n"
                "COUNTING NICKELS: Each nickel is 5¢. Count by FIVES: 5¢, 10¢, 15¢, 20¢... "
                "If you have 4 nickels, count: 5, 10, 15, 20 — you have 20¢!\n\n"
                "COUNTING DIMES: Each dime is 10¢. Count by TENS: 10¢, 20¢, 30¢, 40¢... "
                "If you have 6 dimes, count: 10, 20, 30, 40, 50, 60 — you have 60¢!\n\n"
                "COUNTING QUARTERS: Each quarter is 25¢. Count by TWENTY-FIVES: 25¢, 50¢, 75¢, 100¢. "
                "100¢ is the same as ONE DOLLAR, written as $1.00!\n\n"
                "'The trick,' said Penny with a wink, 'is to know your skip-counting! "
                "Count by 1s for pennies, 5s for nickels, 10s for dimes, and 25s for quarters.' "
                "Christopher practiced counting and found he had exactly 35¢ in his nickel pile. "
                "'Seven nickels!' he shouted. Penny rattled happily."
            ),
            "vocabulary": [
                {
                    "term": "value",
                    "definition": "How much a coin is worth — the number of cents.",
                },
                {
                    "term": "count by fives",
                    "definition": "Saying numbers in jumps of five: 5, 10, 15, 20 ... Used to count nickels.",
                },
                {
                    "term": "count by tens",
                    "definition": "Saying numbers in jumps of ten: 10, 20, 30, 40 ... Used to count dimes.",
                },
                {
                    "term": "dollar ($1.00)",
                    "definition": "One hundred cents. Four quarters, ten dimes, twenty nickels, or 100 pennies all equal one dollar.",
                },
                {
                    "term": "total",
                    "definition": "The final amount you get when you add all the coins together.",
                },
            ],
            "questions": [
                {
                    "prompt": "You have 5 nickels. Count by fives to find the total. How many cents is that?",
                    "response_lines": 2,
                },
                {
                    "prompt": "You have 8 dimes. Count by tens to find the total. How many cents is that?",
                    "response_lines": 2,
                },
                {
                    "prompt": "You have 4 quarters. Count by twenty-fives. How many cents is that? What is another word for that amount?",
                    "response_lines": 2,
                },
                {
                    "prompt": "If you have 9 pennies and your friend has 2 nickels, who has more money? How do you know?",
                    "response_lines": 3,
                },
                {
                    "prompt": "LET'S DISCUSS: Why is it smart to count the highest-value coins first when you have a mixed pile? What might happen if you counted the pennies first?",
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "causeEffectWorksheet",
        {
            "title": "Wednesday: Coin Counting — What's the Total?",
            "instructions": (
                "Each cause shows a pile of coins. Write the effect — what is the total value? "
                "Count by the right skip-counting rule for each coin type. Show your work!"
            ),
            "pairs": [
                {
                    "cause": "You have 6 pennies. Count by 1s.",
                    "effect": "",
                    "effect_lines": 2,
                },
                {
                    "cause": "You have 3 nickels. Count by 5s: 5¢, ___, ___",
                    "effect": "",
                    "effect_lines": 2,
                },
                {
                    "cause": "You have 7 dimes. Count by 10s: 10¢, 20¢, ___, ___, ___, ___, ___",
                    "effect": "",
                    "effect_lines": 2,
                },
                {
                    "cause": "You have 2 quarters. Count by 25s: 25¢, ___",
                    "effect": "",
                    "effect_lines": 2,
                },
                {
                    "cause": "You save 10 dimes. How many cents is that? Is it enough for a $1.00 snack?",
                    "effect": "",
                    "effect_lines": 2,
                },
            ],
        },
        "Wednesday",
    )

    # =========================================================================
    # THURSDAY — Earning and Saving Money
    # Standards: VA.HISTORY.K.k.8, VA.MATH.1.1.6
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: Earning and Saving Money",
            "passage_title": "How Does Money Get Into Penny?",
            "instructions": (
                "Read about earning and saving with Penny. Then answer the questions below.\n\n"
                "Real-life activity: With a grown-up, talk about three jobs or chores you could do "
                "at home to earn coins. Write them on a sticky note and put it on your desk "
                "as a reminder — you are now officially in the earning business!"
            ),
            "passage": (
                "Penny sighed happily as Christopher dropped three coins into her slot — clink, "
                "clink, CLINK! 'Where did you get those?' she asked. 'I helped my mom fold laundry,' "
                "said Christopher proudly. 'She gave me 15 cents!' Penny grinned. 'That is EARNING!'\n\n"
                "Earning money means doing a job or chore and receiving money as payment. "
                "People earn money in many ways — parents go to work, kids do chores, "
                "and sometimes people sell things they have made or grown. "
                "The money you earn is called your income.\n\n"
                "But what do you DO with money once you earn it? You have two choices: "
                "spend it now, or save it for later. Saving means keeping money so you can "
                "use it in the future — usually for something bigger. "
                "When you put money in a piggy bank, that is saving!\n\n"
                "'I love it when people save,' said Penny. 'A little bit every day adds up fast. "
                "If you save just 5 pennies a day, after 10 days you will have 50 pennies — "
                "that is 50 cents! After 20 days, 100 pennies — that is a whole dollar!'\n\n"
                "Christopher added up his savings in his head. He had 12 cents on Monday, "
                "earned 15 cents on Thursday, and was going to earn 10 more cents this weekend. "
                "'How much will I have total?' he asked. Penny rattled with excitement. "
                "'Let us figure it out together: 12 + 15 = 27, and 27 + 10 = 37. Thirty-seven cents!'"
            ),
            "vocabulary": [
                {
                    "term": "earning",
                    "definition": "Getting money by doing a job or chore — working in exchange for payment.",
                },
                {
                    "term": "income",
                    "definition": "The money you earn from doing a job or providing a service.",
                },
                {
                    "term": "saving",
                    "definition": "Keeping money set aside to use later, instead of spending it right away.",
                },
                {
                    "term": "spending",
                    "definition": "Using money to buy something right now.",
                },
                {
                    "term": "piggy bank",
                    "definition": "A container — often shaped like a pig — used to save coins at home.",
                },
            ],
            "questions": [
                {
                    "prompt": "What does it mean to earn money? Give two examples of ways a child can earn money.",
                    "response_lines": 3,
                },
                {
                    "prompt": "What is the difference between spending and saving? Which one fills up Penny?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Christopher saves 5 pennies every day. How much will he have after 6 days? Show your counting.",
                    "response_lines": 3,
                },
                {
                    "prompt": "If Christopher has 12 cents and earns 8 more cents for setting the table, how much money does he have now?",
                    "response_lines": 2,
                },
                {
                    "prompt": "LET'S DISCUSS: If you had 20 cents, would you spend it right away on a small treat, or save it for something bigger? What would you save up for?",
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    add(
        "matchingWorksheet",
        {
            "title": "Thursday: Money Words — Matching",
            "instructions": (
                "Draw a line from each money word on the left to its correct meaning on the right."
            ),
            "left_items": [
                "Earning",
                "Saving",
                "Spending",
                "Income",
                "Bartering",
                "Goods",
            ],
            "right_items": [
                "Doing a job and receiving money as payment",
                "Keeping money to use in the future",
                "Using money to buy something now",
                "The money you receive from doing a job",
                "Trading one thing for another without money",
                "Things you can hold and take home that you buy",
            ],
        },
        "Thursday",
    )

    # =========================================================================
    # FRIDAY — Needs vs. Wants (Capstone)
    # Standards: VA.HISTORY.1.1.8, VA.MATH.1.1.8
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: Needs vs. Wants — Making Smart Choices",
            "passage_title": "How Does Penny Help Christopher Decide What to Buy?",
            "instructions": (
                "Read the capstone passage with Penny. Then answer the questions.\n\n"
                "Capstone activity: Before starting, look around the room and name three things "
                "you NEED and three things you WANT. After the lesson, check your list — "
                "did you get them right? Would you change any answers now?"
            ),
            "passage": (
                "It was Friday and Christopher had 75 cents saved in Penny the Piggy Bank. "
                "'I want to spend some of it!' he said. Penny gave him a knowing look. "
                "'Before you spend,' she said wisely, 'let me teach you the most important "
                "money lesson of all: the difference between NEEDS and WANTS.'\n\n"
                "A NEED is something you must have to live a safe and healthy life. "
                "Food, water, clothing, shelter (a home to live in), and healthcare are all needs. "
                "Without these things, you could not survive or stay healthy. "
                "Families always pay for needs first.\n\n"
                "A WANT is something you would LIKE to have but do not absolutely need to survive. "
                "Toys, video games, candy, and fancy sneakers are wants. "
                "Wants are not bad — it is wonderful to enjoy nice things — but they come AFTER needs.\n\n"
                "'Here is the tricky part,' said Penny. 'Money is limited. You cannot have "
                "everything, so you must CHOOSE. Every time you decide to buy one thing, "
                "you give up buying something else. That is called a trade-off.'\n\n"
                "Christopher looked at his 75 cents. He wanted to buy a toy car (50¢), "
                "a bag of apple slices (25¢), and a sticker book (40¢). "
                "He only had 75¢. 'The apple slices are food — that is a need,' he said slowly. "
                "'I will buy those first. Then I have 50¢ left, just enough for the toy car. "
                "I will save up more for the sticker book another week!' "
                "Penny rattled with pride. 'Now THAT is a smart money choice!'"
            ),
            "vocabulary": [
                {
                    "term": "need",
                    "definition": "Something you must have to stay safe and healthy — food, water, clothing, shelter, healthcare.",
                },
                {
                    "term": "want",
                    "definition": "Something you would like to have but do not need to survive — toys, candy, extra clothes.",
                },
                {
                    "term": "limited",
                    "definition": "Not having an unlimited amount — money is limited, so you must choose how to use it.",
                },
                {
                    "term": "trade-off",
                    "definition": "When you choose one thing and give up something else because you cannot have both.",
                },
                {
                    "term": "choice",
                    "definition": "Deciding between two or more options — good money choices put needs before wants.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is the difference between a need and a want? Give two examples of each.",
                    "response_lines": 3,
                },
                {
                    "prompt": "What is a trade-off? Give an example using money.",
                    "response_lines": 3,
                },
                {
                    "prompt": "Christopher had 75¢. He spent 25¢ on apple slices and 50¢ on a toy car. How much does he have left? Show your work.",
                    "response_lines": 2,
                },
                {
                    "prompt": "Why should needs always come before wants when spending money?",
                    "response_lines": 2,
                },
                {
                    "prompt": "This week you learned: what money is, coin values, counting coins, earning and saving, and needs vs. wants. Which lesson was your favorite and why?",
                    "response_lines": 3,
                },
                {
                    "prompt": "LET'S DISCUSS: If your family had exactly $10 left this week, what would you spend it on — and what would you leave off the list? How did you decide?",
                    "response_lines": 0,
                },
            ],
        },
        "Friday",
    )

    add(
        "wordSortWorksheet",
        {
            "title": "Friday: Needs and Wants — Capstone Word Sort",
            "instructions": (
                "Read each item in the word bank. Is it a NEED (must have to survive) "
                "or a WANT (nice to have, but not necessary)? "
                "Write each item in the correct box. Some might surprise you!"
            ),
            "categories": [{"label": "Needs"}, {"label": "Wants"}],
            "tiles": [
                "Vegetables",
                "Video game",
                "Clean water",
                "Stuffed animal",
                "Winter coat",
                "Candy bar",
                "Doctor visit",
                "Fancy shoes",
                "A safe home",
                "New bicycle",
                "Bread",
                "Movie ticket",
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
            "title": "End-of-Week Parent Feedback — Money Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this feedback sheet after the week wraps up. "
                "Your notes help shape next week's lessons."
            ),
            "passage": (
                "This week followed a causal arc through the fundamentals of money. "
                "Monday introduced what money IS — solving the problem of bartering — and "
                "established the difference between goods and services. Tuesday focused on the "
                "four US coins (penny, nickel, dime, quarter), their values, and key equivalencies. "
                "Wednesday built on coin knowledge with counting collections of like coins using "
                "skip-counting strategies. Thursday introduced earning and saving, and practiced "
                "single-step addition within 20 using money story problems. Friday brought "
                "everything together with the needs vs. wants framework and real-world "
                "decision-making under a budget constraint.\n\n"
                "Penny the Piggy Bank served as the narrator throughout, experiencing each "
                "concept from the perspective of a cheerful coin-collector who models good "
                "saving and spending habits.\n\n"
                "Key concepts to check for genuine understanding — not just recall:\n"
                "1) Why money was invented (bartering problems) — not just 'people use money to buy things.'\n"
                "2) The DIME is the smallest coin but worth more than a penny or nickel.\n"
                "3) Skip-counting rules (x1 for pennies, x5 for nickels, x10 for dimes, x25 for quarters).\n"
                "4) The difference between earning (doing work) and saving (keeping for later).\n"
                "5) Needs MUST come before wants when money is limited — and that trade-offs are real.\n\n"
                "Common misconceptions to watch for:\n"
                "• 'Bigger coin = more valuable' — the dime disproves this; value and size are unrelated.\n"
                "• 'Wants are bad' — they are not! The point is priority, not prohibition.\n"
                "• 'Saving means hiding money' — saving is intentional and purposeful, not just setting aside.\n\n"
                "Suggested follow-on activities: keep a simple weekly savings log; visit a grocery "
                "store and practice identifying needs vs. wants in the aisles; let Christopher "
                "earn and save toward a specific goal, tracking progress on a chart."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": "A bigger coin does NOT mean more value — the dime (smallest) is worth more than the penny and nickel.",
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in after the week — which idea did Christopher grasp best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": "Counting mixed coins — what happens when you have a quarter AND some dimes AND nickels in one pile?",
                },
            ],
            "questions": [
                {
                    "prompt": "Overall comfort with money concepts — how well did Christopher grasp the week's ideas? (1 = struggled throughout, 5 = strong grasp of all concepts)",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which day's lesson generated the most curiosity or questions?",
                    "response_lines": 2,
                },
                {
                    "prompt": "By Friday, could Christopher correctly count a small pile of like coins using skip-counting?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Did Christopher show understanding of needs vs. wants in a real-life moment during the week (e.g., at a store, or when asking for something)?",
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
        pages, packet_title="Money Week — Math & Social Studies for Christopher"
    )
    out_path = output_dir / "money_week.html"
    out_path.write_text(html, encoding="utf-8")

    # Teacher guide
    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Money Week — Teacher Guide</title>
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
  <h1>Money Week — Teacher / Parent Guide</h1>
  <p><strong>Theme:</strong> Money &nbsp;|&nbsp; <strong>Audience:</strong> Christopher, age 6, K&ndash;1 &nbsp;|&nbsp;
  <strong>Narrator:</strong> Penny the Piggy Bank</p>
  <p><strong>Subjects:</strong> Math (VA.MATH.K.k.7, VA.MATH.1.1.8, VA.MATH.K.k.6, VA.MATH.1.1.6) + Social Studies (VA.HISTORY.K.k.8, VA.HISTORY.1.1.8)</p>
  <p><strong>Causal Arc:</strong> What is money &rarr; Coins &amp; their values &rarr; Counting coins &rarr; Earning &amp; saving &rarr; Needs vs. Wants &amp; smart choices</p>

  <h2>Monday &mdash; What Is Money?</h2>
  <h3>Standards: VA.HISTORY.K.k.8, VA.HISTORY.1.1.8</h3>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1 (Why money was invented):</strong> People invented money to solve the problems of bartering. With bartering, both people had to want what the other person had at the same time. Money is something everyone agrees has value, so you can trade it for anything.</p>
    <p><strong>Q2 (Goods vs. services):</strong> A good is something you can hold and take home (physical object). A service is something someone does for you. Examples of goods: toy, apple, book. Examples of services: haircut, doctor visit, piano lesson. Accept any reasonable examples.</p>
    <p><strong>Q3 (Bartering):</strong> Bartering is trading without money. Personal response — accept any real-life trading example (e.g., swapping snacks, sharing toys).</p>
  </div>
  <h3>T-Chart Answer Key</h3>
  <div class="answer-box">
    <p><strong>Goods:</strong> Apple, Library book, Soccer ball, Toy car, Backpack</p>
    <p><strong>Services:</strong> Haircut, Doctor visit, Pizza delivery, Piano lesson, Lawn mowing</p>
    <p><em>Note: "Pizza delivery" could spark discussion — the pizza itself is a good, but the delivery is a service. Accept either column for the delivery item if the child can explain their reasoning.</em></p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"If you had apples and needed shoes, how would bartering work? What problems might come up?"</em></p>
    <p>Key insight: The shoemaker must ALSO want apples right now (double coincidence of wants). What if apples are plentiful but the shoemaker wants meat? This is why money — a universally accepted medium of exchange — was such an important invention. Encourage the child to imagine several barter scenarios to feel the friction.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Children often think money is "just paper" or coins with no intrinsic value, or conversely that gold and silver have some magical value. The key concept: money works because <em>everyone agrees it works</em> — it is a social technology built on trust and shared agreement.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Barter game: Give the child five small objects (a crayon, a sticker, a block, etc.). Give a parent/sibling five different objects. Try to "barter" to get something you want. Talk about how hard it is to find an exact match. Then introduce a "pretend money" token (poker chip or button) and see how much easier trading becomes.</p>
  </div>

  <h2 class="tue">Tuesday &mdash; Coins and Their Values</h2>
  <h3>Standards: VA.MATH.K.k.7</h3>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box tue">
    <p><strong>Q1 (Coins least to greatest):</strong> Penny (1&cent;), Nickel (5&cent;), Dime (10&cent;), Quarter (25&cent;).</p>
    <p><strong>Q2 (Equivalencies):</strong> 5 pennies = 1 nickel. 10 pennies = 1 dime.</p>
    <p><strong>Q3 (Size vs. value):</strong> No — size does NOT tell us the value of a coin. The dime is the smallest coin but is worth 10&cent;, more than the penny (1&cent;) or nickel (5&cent;). The appearance and value of a coin are set by the government, not by size.</p>
  </div>
  <h3>Feature Matrix Answer Key</h3>
  <div class="answer-box tue">
    <p><strong>Penny:</strong> Copper color &check;, Worth less than 10&cent; &check;, Has a president on the front &check;</p>
    <p><strong>Nickel:</strong> Silver color &check;, Worth less than 10&cent; &check;, Has a president on the front &check;, Worth exactly 5 pennies &check;</p>
    <p><strong>Dime:</strong> Silver color &check;, Worth 10&cent; or more &check;, Smallest coin by size &check;, Has a president on the front &check;</p>
    <p><strong>Quarter:</strong> Silver color &check;, Worth 10&cent; or more &check;, Has a president on the front &check;, Takes 4 to make a dollar &check;</p>
    <p><em>Note on "Has a president on the front": All four coins feature a historical president or leader. Roosevelt on the dime is technically a president. All four should be checked for this property.</em></p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Why do coins have pictures of famous people? Who would YOU put on a coin?"</em></p>
    <p>Coins honor people considered important to a nation's history or values. The people on US coins were chosen by Congress. There is no single right answer for who the child would choose — the goal is creative reasoning and discussion about what makes a person worth honoring. Ask: what did that person do? Why does it matter?</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>The "big coin = more money" confusion is extremely common at age 6. Use physical coins to demonstrate repeatedly: hold a dime and a nickel side by side. The nickel looks bigger but the dime is worth more. Reinforce: <em>the government decides value — not the size or weight of the metal.</em></p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Coin rubbings: Place real coins under a piece of paper and rub a crayon over them to reveal the images. Label each rubbing with the coin's name and value. Then sort the rubbings from least to greatest value and tape them in order on a strip of paper to make a "value line."</p>
  </div>
</div>

<div class="page">
  <h2 class="wed">Wednesday &mdash; Counting Coins</h2>
  <h3>Standards: VA.MATH.1.1.8, VA.MATH.K.k.6</h3>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1 (5 nickels):</strong> Count by 5s: 5, 10, 15, 20, 25. Total = 25&cent;.</p>
    <p><strong>Q2 (8 dimes):</strong> Count by 10s: 10, 20, 30, 40, 50, 60, 70, 80. Total = 80&cent;.</p>
    <p><strong>Q3 (4 quarters):</strong> Count by 25s: 25, 50, 75, 100. Total = 100&cent; = $1.00 (one dollar).</p>
    <p><strong>Q4 (9 pennies vs. 2 nickels):</strong> 9 pennies = 9&cent;. 2 nickels = 10&cent;. The friend with 2 nickels has more money (10&cent; &gt; 9&cent;). Key insight: more coins does not always mean more money.</p>
  </div>
  <h3>Cause-and-Effect Answer Key</h3>
  <div class="answer-box wed">
    <p><strong>6 pennies:</strong> 1, 2, 3, 4, 5, 6 &rarr; Total = 6&cent;</p>
    <p><strong>3 nickels:</strong> 5, 10, 15 &rarr; Total = 15&cent;</p>
    <p><strong>7 dimes:</strong> 10, 20, 30, 40, 50, 60, 70 &rarr; Total = 70&cent;</p>
    <p><strong>2 quarters:</strong> 25, 50 &rarr; Total = 50&cent;</p>
    <p><strong>10 dimes:</strong> 10 &times; 10 = 100&cent; = $1.00. Yes, exactly enough for a $1.00 snack.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Why start with the highest-value coin? What if you counted pennies first?"</em></p>
    <p>Starting high keeps the numbers manageable and reduces error. If you count pennies first in a mixed pile, you might lose track of which coins you have counted. More importantly, this builds the habit needed for later multi-coin counting. Connect to real-world cashier behavior: cashiers always handle large bills/coins first.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"More coins = more money" — nine pennies feel like more than two nickels, but 9&cent; &lt; 10&cent;. Use physical coins whenever possible. Have the child count each pile and write the total before comparing. Let the numbers do the talking.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Piggy bank challenge: Put a random pile of only one coin type (e.g., all nickels) in front of the child — anywhere from 3 to 12 coins. Set a 30-second timer and see if they can skip-count to the total before time runs out. Gradually increase the number of coins as fluency grows.</p>
  </div>

  <h2 class="thu">Thursday &mdash; Earning and Saving Money</h2>
  <h3>Standards: VA.HISTORY.K.k.8, VA.MATH.1.1.6</h3>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1 (Earning):</strong> Earning money means doing a job or chore and receiving money as payment. Examples for a child: folding laundry, sweeping the floor, watering plants, feeding a pet, setting the table. Accept any reasonable home-chore examples.</p>
    <p><strong>Q2 (Spending vs. saving):</strong> Spending is using money to buy something right now. Saving is keeping money to use later (for something bigger). Saving fills up Penny the Piggy Bank.</p>
    <p><strong>Q3 (5 pennies &times; 6 days):</strong> 5, 10, 15, 20, 25, 30 &rarr; 30&cent; after 6 days.</p>
    <p><strong>Q4 (12&cent; + 8&cent;):</strong> 12 + 8 = 20&cent;.</p>
  </div>
  <h3>Matching Answer Key</h3>
  <div class="answer-box thu">
    <p>Earning &rarr; Doing a job and receiving money as payment</p>
    <p>Saving &rarr; Keeping money to use in the future</p>
    <p>Spending &rarr; Using money to buy something now</p>
    <p>Income &rarr; The money you receive from doing a job</p>
    <p>Bartering &rarr; Trading one thing for another without money</p>
    <p>Goods &rarr; Things you can hold and take home that you buy</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Would you spend 20 cents on a small treat now, or save it for something bigger?"</em></p>
    <p>There is no wrong answer — this is about the child's values and future-thinking skills. If they say spend: ask what they would buy and why. If they say save: ask what they are saving for and how long it will take. The goal is deliberate decision-making, not a morality lesson about spending being bad.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Children may think "saving" means hiding money somewhere or that it is only for big purchases. Clarify: saving is <em>any</em> intentional decision to keep money for later use, even if it is just for next week. Also reinforce: money in a piggy bank is still yours — it has not been "used up."</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Savings goal chart: Help the child pick one item they want to save for (even something small, like a 50&cent; sticker pack). Draw a simple bar or thermometer chart with the goal amount at the top. Each time they earn coins, color in the amount earned. This makes abstract saving visible and motivating.</p>
  </div>
</div>

<div class="page">
  <h2 class="fri">Friday &mdash; Needs vs. Wants (Capstone)</h2>
  <h3>Standards: VA.HISTORY.1.1.8, VA.MATH.1.1.8</h3>
  <h3>Answer Key &mdash; Reading Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1 (Needs vs. wants):</strong> A need is something required for survival and health (food, water, clothing, shelter, healthcare). A want is something desirable but not essential (toys, candy, fancy things). Examples: Needs = vegetables, a coat; Wants = video game, candy bar. Accept reasonable examples.</p>
    <p><strong>Q2 (Trade-off):</strong> A trade-off is giving up one thing to get another because you cannot have both. Money example: If you spend 50&cent; on a toy, you cannot also spend that 50&cent; on a snack — you had to choose one and give up the other.</p>
    <p><strong>Q3 (75&cent; &minus; 25&cent; &minus; 50&cent;):</strong> 75 &minus; 25 = 50, then 50 &minus; 50 = 0. Christopher has 0&cent; left.</p>
    <p><strong>Q4 (Needs before wants):</strong> Money is limited. If you spend on wants first, you might not have enough left for things you truly need to stay healthy and safe. Families must prioritize to make sure essential items are covered before extras.</p>
    <p><strong>Q5 (Favorite lesson):</strong> Personal response — accept any well-reasoned answer.</p>
  </div>
  <h3>Word Sort Answer Key</h3>
  <div class="answer-box fri">
    <p><strong>Needs:</strong> Vegetables, Clean water, Winter coat, Doctor visit, A safe home, Bread</p>
    <p><strong>Wants:</strong> Video game, Stuffed animal, Candy bar, Fancy shoes, New bicycle, Movie ticket</p>
    <p><em>Note: "Fancy shoes" are a WANT (basic shoes are a need, but fancy/expensive ones are a want). "New bicycle" could spark discussion — basic transportation might be a need in some situations. Accept either column for bicycle if the child can explain their reasoning. "Stuffed animal" may feel like a need for emotional comfort — acknowledge the feeling and guide toward the distinction between physical necessity and emotional comfort.</em></p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"If your family had exactly $10 left this week, what would you spend it on?"</em></p>
    <p>This is the week's capstone reasoning exercise. Guide: start with needs first (food, any essential item). Then see if wants fit in the remaining budget. Key insight: the order matters — needs first, then wants with what is left. Discuss: who in the family has input in this decision? How do different family members' needs get balanced? This is a real-world budgeting simulation.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"Wants are bad." Correct this gently — wants are not bad! Enjoying nice things is perfectly fine when needs are covered and money permits. The lesson is about <em>sequence and priority</em>, not about denying enjoyment. A healthy relationship with money includes room for wants.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Grocery store needs/wants hunt: On the next grocery trip, give the child a small notebook. As items go into the cart, they write "N" for need or "W" for want next to each one. After shopping, count the Ns and Ws. What percentage of the cart was needs? Talk about why families might also include a few wants (treats, special items) in a grocery run.</p>
  </div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2 class="fri">Week Summary &mdash; Causal Chain</h2>
  <p>The week followed this chain of concepts:</p>
  <ol style="padding-left: 20px; font-size: 10pt; line-height: 2;">
    <li><strong>Monday:</strong> Bartering problems &rarr; money invented as a universal medium of exchange; goods vs. services distinction.</li>
    <li><strong>Tuesday:</strong> The four US coins and their values; size does not equal value; key equivalencies.</li>
    <li><strong>Wednesday:</strong> Counting collections of like coins using skip-counting; more coins &ne; more money.</li>
    <li><strong>Thursday:</strong> Earning money through work; saving vs. spending; single-step addition money problems.</li>
    <li><strong>Friday:</strong> Needs vs. wants; trade-offs; applying all week's concepts to a real budget scenario.</li>
  </ol>
  <p style="margin-top: 10px;">By Friday, Christopher should be able to identify all four coins and their values, count a pile of like coins, explain the difference between earning and saving, and correctly sort everyday items into needs vs. wants — and explain why the order matters when money is limited.</p>
</div>

</body>
</html>"""

    guide_path = output_dir / "money_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print("\nSuccessfully generated Money Week.")
    print(f"Student packet:  {out_path}")
    print(f"Teacher guide:   {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Mon p1 — Reading: What Is Money? (Meet Penny the Piggy Bank)",
        "Mon p2 — T-Chart: Goods and Services",
        "Tue p1 — Reading: Coins and Their Values",
        "Tue p2 — Feature Matrix: Coin Comparison",
        "Wed p1 — Reading: Counting Coins",
        "Wed p2 — Cause and Effect: Coin Counting Totals",
        "Thu p1 — Reading: Earning and Saving Money",
        "Thu p2 — Matching: Money Words",
        "Fri p1 — Reading: Needs vs. Wants (Capstone)",
        "Fri p2 — Word Sort: Needs and Wants",
        "         — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")


if __name__ == "__main__":
    generate_money_week_series()
