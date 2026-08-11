"""
Game Theory — Week Series
Grade 1-2 | Games, Logic & Math | Causal Arc: Win Conditions -> Cooperation vs. Competition
-> Basic Probability -> Hidden Information -> Strategy (capstone)

Format: a "mixed lesson" week. Each day the family PLAYS a short game first (setup + play in
under 45 min, using household items), then reads a passage that dissects one game-theory concept
from that game, then does an application worksheet. The game instructions live in each reading
worksheet's ``instructions`` field (Before / During / After), the same slot the science weeks use
for the outdoor activity.

Narrator: Ace the Fox, a clever game-night host who always thinks one move ahead. Introduced on
Monday. Games: a "Game Night Olympics" of four micro-games (Tic-Tac-Toe, Rock-Paper-Scissors,
Coin-Flip Call-It, Race to 20) on Mon to frame the week; then Block Tower two-round (Tue), Mystery
Bag (Wed), Go Fish (Thu), and "Don't Take the Last One" / Nim (Fri).

Output: game_theory_week_series/game_theory_week.html (+ teacher guide)

Standards (Virginia SOL, verified against curriculum.db):
  Monday    — VA.COMPUTER_SCIENCE.1.CS-VA-2017-1.5 / 2.CS-VA-2017-2.5 (categorize/compare items by
              attributes); VA.ENGLISH.1.1.ri.1.a / 2.2.ri.1.a (literal & inferential questions).
  Tuesday   — VA.MATH.1.1.13 (sort & classify objects by one or two attributes);
              VA.COMPUTER_SCIENCE.1.CS-VA-2017-1.5 / 2.5; VA.ENGLISH.2.2.c (oral collaboration).
  Wednesday — VA.MATH.2.2.14 (use data from probability experiments to predict outcomes);
              VA.MATH.1.1.12 / 2.2.15 (collect, represent & interpret pictographs and bar graphs);
              VA.COMPUTER_SCIENCE.1.CS-VA-2017-1.11 / 2.11 (organize data to make a prediction).
  Thursday  — VA.ENGLISH.1.1.ri.1.a (inferential who/what/why questions);
              VA.ENGLISH.2.2.rv.1.a / 2.2.rv.1.h (acquire & use new vocabulary).
  Friday    — VA.COMPUTER_SCIENCE.2.CS-VA-2017-2.1 (construct step-by-step instructions/algorithms
              = a strategy is a plan); VA.MATH.2.2.16 (patterns); VA.ENGLISH.2.2.w.2.a (plan writing).
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html


def generate_game_theory_week_series():
    output_dir = Path("game_theory_week_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []  # (day_label, html_fragment)

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # MONDAY — Win Conditions ("How do you win?")
    # Game first: Tic-Tac-Toe. Standards: CS 1.5/2.5 (categorize), ENGLISH 1.1.ri/2.2.ri.
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Monday: How Do You Win?",
            "passage_title": "Meet Ace — and the Game Night Olympics",
            "instructions": (
                "PLAY FIRST — GAME NIGHT OLYMPICS (about 20 minutes): Play these four quick games with "
                "a grown-up, and after EACH one ask, 'How did you win that game?'  "
                "1) TIC-TAC-TOE — draw a 3-by-3 grid; first to get three marks in a row wins.  "
                "2) ROCK-PAPER-SCISSORS — best of five; whoever wins the most throws wins.  "
                "3) COIN-FLIP CALL-IT — call 'heads' or 'tails' before a grown-up flips a coin; guess "
                "right to win.  "
                "4) RACE TO 20 — take turns rolling one die and adding up your points; first to reach "
                "20 wins.  "
                "Then read the passage."
            ),
            "passage": (
                "Meet Ace the Fox! Ace has bright orange fur, a big bushy tail, and an even bigger "
                "smile. Every game night, all the animals in the forest gather at Ace's den to play "
                "games together. This week, Ace has a big plan. 'By Friday,' he says, 'you will be able "
                "to look at ANY game, figure out how to win it, and make a smart plan to try. That is "
                "what a real game player learns to do!'\n\n"
                "Ace says every game — even a tiny, quick one — begins with the same big question: how "
                "do you win? The way you win a game is called the win condition. A win condition is the "
                "goal, the thing you must do to become the winner. In Tic-Tac-Toe, the win condition is "
                "getting three of your marks in a row. In Race to 20, it is being the first to reach 20 "
                "points. In Coin-Flip Call-It, it is guessing the flip correctly. Every game has its "
                "own win condition — and some are easy to win with skill, while others come down to "
                "luck!\n\n"
                "Ace says the very first thing a smart player should ask is, 'What is the win "
                "condition?' If you do not know how to win, it is very hard to win! Once you know the "
                "goal, you can make good moves that help you reach it. A player who knows the win "
                "condition can plan ahead. A player who forgets the goal might waste their turns.\n\n"
                "Sometimes a game ends and nobody reaches the win condition at all. In Tic-Tac-Toe, if "
                "every box is full but no one has three in a row, the game is a tie. A tie means the "
                "game is over and there is no winner — everybody is even. Ace does not mind a tie. 'A "
                "tie just means it was a fair, close game,' he says. 'We can always play again — and "
                "all week long, we will learn the tricks that help you win!'"
            ),
            "vocabulary": [
                {
                    "term": "goal",
                    "definition": "The thing you are trying to do or reach.",
                },
                {
                    "term": "tie",
                    "definition": "When a game ends and nobody wins — everyone is even.",
                },
                {
                    "term": "win condition",
                    "definition": "The way you win a game — the goal you must reach to be the winner.",
                },
                {
                    "term": "turn",
                    "definition": "Your chance to make a move before the next player goes.",
                },
                {
                    "term": "player",
                    "definition": "A person or animal who is playing the game.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is a 'win condition'? Explain it in your own words.",
                    "response_lines": 2,
                },
                {"prompt": "What is the win condition in Tic-Tac-Toe?", "response_lines": 1},
                {
                    "prompt": "Why does Ace say the first question a smart player asks is 'How do you win?'",
                    "response_lines": 2,
                },
                {"prompt": "What is a tie? Can a game end with no winner?", "response_lines": 2},
                {
                    "prompt": (
                        "LET'S DISCUSS: Think of a game you love. What is its win condition? Is there a "
                        "game where you win by NOT doing something (like not laughing, or not moving)?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Monday",
    )

    add(
        "matchingWorksheet",
        {
            "title": "Monday: Match the Game to How You Win",
            "instructions": (
                "Every game has a win condition. Draw a line from each game on the left to the correct "
                "way to win it on the right. The right side is mixed up — read carefully! (The top four "
                "are the games from your Game Night Olympics.)"
            ),
            "left_items": [
                "Tic-Tac-Toe",
                "Rock-Paper-Scissors",
                "Coin-Flip Call-It",
                "Race to 20",
                "Hide-and-Seek",
                "Musical Chairs",
            ],
            # Right column is intentionally shuffled (a derangement — no row self-aligns) so this
            # is a real matching puzzle.
            "right_items": [
                "Win the most throws (best of five)",
                "Guess the coin flip correctly",
                "Be the last player sitting in a chair",
                "Get three of your marks in a row",
                "Be the first to reach 20 points",
                "Find all of the players who are hiding",
            ],
        },
        "Monday",
    )

    # =========================================================================
    # TUESDAY — Cooperation vs. Competition
    # Game first: Block Tower (two rounds). Standards: MATH 1.1.13 (sort), CS 1.5/2.5, ENGLISH 2.2.c.
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Tuesday: Playing With or Playing Against",
            "passage_title": "Two Ways to Play",
            "instructions": (
                "PLAY FIRST (about 20 minutes): Play the Block Tower game two ways with blocks or cups. "
                "ROUND 1 — Competition: each player builds their OWN tower; the tallest tower before it "
                "falls wins. ROUND 2 — Cooperation: work TOGETHER to build ONE tower as tall as you can "
                "before it falls. AFTER you play, talk about how the two rounds felt different. Then read."
            ),
            "passage": (
                "On game night, Ace the Fox noticed something interesting. In some games, the animals "
                "played against each other. In other games, they worked together. 'These are two "
                "different ways to play,' said Ace.\n\n"
                "When you play against other players and try to beat them, that is competition. In a "
                "competition, only one player or one team can win. When you race to build the tallest "
                "tower, or try to win at Tic-Tac-Toe, you are competing. Competition can be exciting, "
                "and it pushes you to try your very best!\n\n"
                "When you work with other players to reach the same goal, that is cooperation. In a "
                "cooperative game, everyone wins together or everyone loses together — you are all on "
                "the same team. When the animals build one big tower together, they share ideas and "
                "help each other. If the tower stands tall, everybody cheers, because everybody won!\n\n"
                "Ace says both ways of playing are good. Competition helps you try hard and get better. "
                "Cooperation helps you make friends and solve problems as a team. The smart thing is to "
                "know which kind of game you are playing. In a competition, you keep your best moves to "
                "yourself. But in a cooperation, you share your best ideas so the whole team can win. "
                "And remember — even when we compete, we can still be kind. A good player is a good "
                "sport, whether they win or lose."
            ),
            "vocabulary": [
                {
                    "term": "opponent",
                    "definition": "A player you are playing against in a competition.",
                },
                {
                    "term": "cooperation",
                    "definition": "When players work together for the same goal. Everyone wins or loses together.",
                },
                {
                    "term": "good sport",
                    "definition": "A player who is kind and fair whether they win or lose.",
                },
                {
                    "term": "competition",
                    "definition": "When players play against each other and try to win. Only one can win.",
                },
                {
                    "term": "team",
                    "definition": "A group of players who work together toward the same goal.",
                },
            ],
            "questions": [
                {"prompt": "What is competition? Give an example.", "response_lines": 2},
                {
                    "prompt": "What is cooperation? How is it different from competition?",
                    "response_lines": 2,
                },
                {
                    "prompt": "In the Block Tower game, which round was cooperation and which was competition?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "Why does Ace say you keep your best moves secret in a competition, but share "
                        "them in a cooperation?"
                    ),
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Can a game be BOTH? Think of a game where two teams compete, "
                        "but players on the same team must cooperate to win (like soccer)."
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Tuesday",
    )

    add(
        "tChartWorksheet",
        {
            "title": "Tuesday: Working Together or Playing to Win?",
            "instructions": (
                "Read each activity in the Word Bank. Decide: is it about working together "
                "(cooperation) or playing to win (competition)? Write each one in the correct column."
            ),
            "columns": ["Working Together", "Playing to Win"],
            "row_count": 6,
            # Word bank shuffled so it is not pre-sorted; answer key is in the teacher guide.
            "word_bank": [
                "Playing Tic-Tac-Toe",
                "Building one block tower as tall as you can",
                "A game of tag",
                "Doing a jigsaw puzzle together",
                "Racing to the mailbox and back",
                "Cleaning up all the toys before the timer beeps",
                "A spelling bee",
                "A team of ants carrying one big crumb",
                "Seeing who can jump the highest",
                "Rowing a boat together",
            ],
        },
        "Tuesday",
    )

    # =========================================================================
    # WEDNESDAY — Basic Probability (chance & luck)
    # Game first: Mystery Bag. Standards: MATH 2.2.14, MATH 1.1.12 / 2.2.15, CS 1.11 / 2.11.
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Wednesday: How Likely Is It?",
            "passage_title": "The Mystery Bag",
            "instructions": (
                "PLAY FIRST (about 15 minutes): Put 5 RED, 3 BLUE, and 2 YELLOW objects (blocks, beads, "
                "or crayons — 10 total) into a bag you cannot see into. First, GUESS which color you "
                "will pull the most. Then take turns: without looking, pull one out, make a tally mark "
                "for its color, and put it back. Do this 10 times. KEEP your tally — you will graph it "
                "on the next page! Then read the passage."
            ),
            "passage": (
                "Ace the Fox reached into his mystery bag and pulled out a red marble. 'I thought I "
                "would!' he laughed. 'There are more red marbles in the bag than any other color, so "
                "red is more likely to come out.'\n\n"
                "Probability is how we talk about how likely something is to happen. Some things are "
                "very likely — they will probably happen. Some things are unlikely — they probably "
                "will not happen. And some things are impossible — they can never happen at all. If a "
                "bag is full of mostly red marbles, pulling a red one is likely. If there is only one "
                "blue marble, pulling blue is unlikely.\n\n"
                "Many games use chance, which is another word for luck. When you roll a die, spin a "
                "spinner, or pull from a bag, you cannot know for sure what you will get. But you can "
                "make a smart guess! If you know what is in the bag, you can predict which color you "
                "will probably pull the most. A good player uses what they know to make the best guess "
                "they can.\n\n"
                "Ace also knows that luck is not the whole story. Some games are all luck, like "
                "flipping a coin. Some games are all skill, like a spelling test. And many games mix "
                "both luck and skill — you might get lucky with your dice, but you still have to choose "
                "good moves. 'That,' says Ace, 'is what makes games so much fun. You never know exactly "
                "what will happen!'"
            ),
            "vocabulary": [
                {
                    "term": "chance",
                    "definition": "Another word for luck — when you cannot know for sure what will happen.",
                },
                {
                    "term": "unlikely",
                    "definition": "Something that probably will NOT happen.",
                },
                {
                    "term": "probability",
                    "definition": "How likely something is to happen.",
                },
                {
                    "term": "predict",
                    "definition": "To make a smart guess about what will happen next.",
                },
                {
                    "term": "likely",
                    "definition": "Something that will probably happen.",
                },
            ],
            "questions": [
                {"prompt": "What does 'probability' mean?", "response_lines": 2},
                {
                    "prompt": "Give one thing that is LIKELY and one thing that is UNLIKELY when you pull from the mystery bag.",
                    "response_lines": 2,
                },
                {
                    "prompt": "Before you played, which color did you guess would come out the most? Were you right?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What is the difference between a game of all luck and a game of all skill? Name one of each.",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: If a bag has 9 red marbles and 1 green marble, and you close "
                        "your eyes and pull one, which color will you probably get? Could you still pull "
                        "the green one?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Wednesday",
    )

    add(
        "barGraphWorksheet",
        {
            "title": "Wednesday: Graph Your Mystery Bag",
            "instructions": (
                "Look at your tally marks from the Mystery Bag game. Color in one square for each time "
                "you pulled that color. Then answer the questions to read your graph."
            ),
            "categories": ["Red", "Blue", "Yellow"],
            # No `values` -> blank grid the student fills in from their own tally.
            "y_max": 10,
            "y_step": 1,
            "x_label": "Marble Color",
            "y_label": "How many times pulled",
            "height_in": 2.6,
            "questions": [
                {"prompt": "Which color did you pull the MOST times?", "response_lines": 1},
                {"prompt": "Which color did you pull the FEWEST times?", "response_lines": 1},
                {
                    "prompt": "The bag had 5 red, 3 blue, and 2 yellow. Does your graph look like what you expected? Why do you think red came up the most?",
                    "response_lines": 2,
                },
            ],
        },
        "Wednesday",
    )

    # =========================================================================
    # THURSDAY — Hidden Information
    # Game first: Go Fish. Standards: ENGLISH 1.1.ri.1.a, 2.2.rv.1.a / 2.2.rv.1.h.
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Thursday: What You Can't See",
            "passage_title": "The Secret in Your Hand",
            "instructions": (
                "PLAY FIRST (about 15 minutes): Play Go Fish with a grown-up (use a regular deck of "
                "cards). Deal 5 to 7 cards to each player. Hold your cards so nobody else can see them! "
                "Take turns asking, 'Do you have a ___?' to collect matching pairs. AFTER you play, "
                "notice: you could not see the other player's cards. Then read the passage."
            ),
            "passage": (
                "When Ace the Fox plays Go Fish, he holds his cards up close so nobody can peek. "
                "'These are my cards,' he says. 'Only I know what I am holding!' The cards you cannot "
                "see are called hidden information.\n\n"
                "Hidden information is anything in a game that you do not get to see or know. In Go "
                "Fish, your opponent's cards are hidden from you, and your cards are hidden from them. "
                "In hide-and-seek, where the players are hiding is hidden information. In a memory "
                "game, the cards are turned face-down, so what is on them is hidden until you flip "
                "them.\n\n"
                "When there is hidden information, you cannot know everything for sure. So what do good "
                "players do? They watch closely, they remember, and they make smart guesses. If Ace "
                "asks, 'Do you have any sevens?' and you say no, Ace remembers that. Later, that little "
                "clue helps him guess what you might be holding. Paying attention turns hidden "
                "information into good guesses.\n\n"
                "Not every game has hidden information. In Tic-Tac-Toe, you can see the whole board — "
                "nothing is hidden at all! Games where you can see everything are called open games. "
                "Ace likes both kinds. 'When everything is out in the open, it is a game of pure "
                "thinking,' he says. 'But when some things are hidden, you have to be a detective!'"
            ),
            "vocabulary": [
                {
                    "term": "clue",
                    "definition": "A small piece of information that helps you make a smart guess.",
                },
                {
                    "term": "open game",
                    "definition": "A game where you can see everything, with nothing hidden.",
                },
                {
                    "term": "hidden information",
                    "definition": "Something in a game that you cannot see or know.",
                },
                {
                    "term": "remember",
                    "definition": "To keep something in your mind so you can use it later.",
                },
                {
                    "term": "opponent",
                    "definition": "The player you are playing against.",
                },
            ],
            "questions": [
                {
                    "prompt": "What is hidden information? Give one example from a game.",
                    "response_lines": 2,
                },
                {"prompt": "In Go Fish, whose cards are hidden from you?", "response_lines": 1},
                {
                    "prompt": "When there is hidden information, what do good players do to make smart guesses?",
                    "response_lines": 2,
                },
                {"prompt": "What is an 'open game'? Name one.", "response_lines": 2},
                {
                    "prompt": (
                        "LET'S DISCUSS: Why would it be no fun if you could see your opponent's cards in "
                        "Go Fish? What would happen to the game?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Thursday",
    )

    add(
        "frayerModelWorksheet",
        {
            "title": "Thursday: Word Detective — Hidden Information",
            "instructions": (
                "Fill in each box about our new word: HIDDEN INFORMATION. Use what you learned from Go "
                "Fish and from the reading to help you."
            ),
            "quadrant_labels": [
                "What it means",
                "Games that have it",
                "What a smart player does about it",
                "Draw a picture of it",
            ],
            "entries": [
                # Empty quadrants -> the renderer draws answer lines for the student to fill in.
                {"word": "Hidden Information", "quadrants": {}},
            ],
        },
        "Thursday",
    )

    # =========================================================================
    # FRIDAY — Strategy (Capstone): thinking ahead
    # Game first: "Don't Take the Last One" (Nim). Standards: CS 2.1 (algorithms), MATH 2.2.16,
    # ENGLISH 2.2.w.2.a.
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Friday: Making a Plan to Win",
            "passage_title": "Ace's Biggest Idea: Strategy",
            "instructions": (
                "PLAY FIRST (about 15 minutes): Play 'Don't Take the Last One.' Line up 10 small "
                "objects (coins, beans, or blocks). Take turns. On your turn, take 1, 2, or 3 objects. "
                "Whoever is FORCED to take the very last object LOSES. Play a few rounds and see if you "
                "can find a trick to win every time! Then read the capstone passage."
            ),
            "passage": (
                "It was the last game night of the week, and Ace the Fox had one more idea to share. "
                "'Now that you know about win conditions, competition, luck, and hidden information,' he "
                "said, 'you are ready for the biggest idea of all: strategy!'\n\n"
                "A strategy is a plan you make to reach your win condition. It is like a set of steps "
                "you follow to give yourself the best chance to win. A player without a plan just makes "
                "random moves. But a player with a strategy thinks ahead: 'If I do this, what will "
                "happen next? And then what should I do after that?'\n\n"
                "Good strategies use everything Ace taught this week. First, know your win condition, so "
                "you know what you are aiming for. Next, decide if you should compete or cooperate. "
                "Then, think about luck — what might happen by chance, and how you can be ready. "
                "Finally, use hidden information wisely: watch for clues, and do not give away your own "
                "secrets.\n\n"
                "In the 'Don't Take the Last One' game, a good strategy is to think backward from the "
                "end. If you can leave your opponent with just one object, they must take it and lose! "
                "Thinking ahead like this is what strategy is all about. 'A game is not just luck,' said "
                "Ace with a wink. 'The player who makes the best plan usually comes out on top. Now — "
                "who wants to play again?'"
            ),
            "vocabulary": [
                {
                    "term": "plan",
                    "definition": "A set of steps you decide to follow before you act.",
                },
                {
                    "term": "think ahead",
                    "definition": "To imagine what will happen next before you make your move.",
                },
                {
                    "term": "strategy",
                    "definition": "A plan you make to reach your win condition and get the best chance to win.",
                },
                {
                    "term": "backward",
                    "definition": "Thinking from the END of the game back to the start to find a smart move.",
                },
                {
                    "term": "random",
                    "definition": "Doing something with no plan — just picking any move at all.",
                },
            ],
            "questions": [
                {"prompt": "What is a strategy?", "response_lines": 2},
                {
                    "prompt": "How is a player with a strategy different from a player who makes random moves?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "A good strategy uses FOUR big ideas from this week. Write each one. "
                        "(Hints: How do you ___? Play with or ___? Luck or ___? What can't you ___?)"
                    ),
                    "response_lines": 4,
                },
                {
                    "prompt": "In 'Don't Take the Last One,' what is one good strategy? Why does it work?",
                    "response_lines": 3,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Is it possible to have a great strategy and STILL lose? Can luck "
                        "beat a good plan sometimes? When?"
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
            "title": "Friday: My Game Plan",
            "instructions": (
                "You are the game expert now! Pick a game you love. Fill in each part below to write "
                "your very own Game Plan. Use full sentences and the new words you learned this week."
            ),
            "topic": "My Favorite Game and My Strategy",
            "sections": [
                {"label": "My Game", "starter": "My favorite game to play is...", "lines": 2},
                {
                    "label": "The Win Condition",
                    "starter": "To win this game, you have to...",
                    "lines": 2,
                },
                {
                    "label": "Luck or Skill?",
                    "starter": "This game uses (luck / skill / both) because...",
                    "lines": 2,
                },
                {
                    "label": "My Strategy",
                    "starter": "My plan to win is... First I..., then I...",
                    "lines": 3,
                },
                {
                    "label": "Being a Good Sport",
                    "starter": "If I lose, I will... If I win, I will...",
                    "lines": 2,
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
            "title": "End-of-Week Parent Feedback — Game Theory Week",
            "passage_title": "Week Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this feedback sheet after the week wraps up. Your notes help shape "
                "next week's lessons."
            ),
            "passage": (
                "This week introduced core game-theory ideas through a play-first, discuss-after "
                "rhythm. Each day the family played a short game (under 45 minutes to set up and play), "
                "then read a passage that pulled one big idea out of that game, then completed an "
                "application worksheet.\n\n"
                "Monday established the WIN CONDITION — every game has a goal, and the first thing a "
                "smart player asks is 'How do you win?' (game: Tic-Tac-Toe). Tuesday contrasted "
                "COMPETITION and COOPERATION — playing against versus playing with others (game: the "
                "two-round Block Tower). Wednesday introduced BASIC PROBABILITY — likely, unlikely, and "
                "chance — and had Christopher run a real experiment and graph the results (game: the "
                "Mystery Bag). Thursday explored HIDDEN INFORMATION — what you cannot see, and how good "
                "players use clues and memory (game: Go Fish). Friday tied everything together with "
                "STRATEGY — a plan to reach your win condition, thinking ahead and even thinking "
                "backward (game: 'Don't Take the Last One').\n\n"
                "Ace the Fox narrated the whole week as a friendly game-night host who thinks one move "
                "ahead, giving concrete, relatable examples for each concept.\n\n"
                "Key concepts to check for genuine understanding — not just recall:\n"
                "1) A win condition is the GOAL of a game; different games have different ones.\n"
                "2) Competition = playing against; cooperation = playing with. Many games mix both.\n"
                "3) Probability describes how LIKELY something is — some outcomes are more likely.\n"
                "4) Hidden information is what you cannot see; smart players use clues and memory.\n"
                "5) A strategy is a PLAN (a set of steps) to reach the win condition.\n\n"
                "Common misconceptions to watch for:\n"
                "• 'Winning is the only good outcome' — reinforce ties, good sportsmanship, and that "
                "cooperative games mean everyone wins together.\n"
                "• 'If it is luck, my choices do not matter' — many games MIX luck and skill; good "
                "moves still matter even when dice are involved.\n"
                "• 'A good plan means I will always win' — luck and an opponent's choices can still "
                "change the result; a strategy improves your chances, it does not guarantee a win.\n\n"
                "Suggested follow-on activities: on your next real game night, pause before playing and "
                "ask Christopher to name the win condition, whether it is cooperative or competitive, "
                "and how much is luck versus skill. Try inventing a brand-new game together and writing "
                "down its rules and win condition."
            ),
            "vocabulary": [
                {
                    "term": "Key Misconception to Watch",
                    "definition": "A good strategy improves your CHANCES — it does not guarantee a win. Luck and the opponent still matter.",
                },
                {
                    "term": "Strongest Concept This Week",
                    "definition": "(Fill in after the week — which idea did Christopher grasp best?)",
                },
                {
                    "term": "Next Week's Hook",
                    "definition": "Fairness & rules — what makes a game fair? How do we handle it when someone breaks a rule or a game feels unfair?",
                },
            ],
            "questions": [
                {
                    "prompt": "Overall comfort with the week's content — how well did Christopher grasp the concepts? (1 = struggled throughout, 5 = strong grasp)",
                    "response_lines": 1,
                },
                {
                    "prompt": "Which day's game generated the most curiosity or questions?",
                    "response_lines": 2,
                },
                {
                    "prompt": "By Friday, could Christopher name a game's win condition and describe a simple strategy for it?",
                    "response_lines": 2,
                },
                {
                    "prompt": "How did game night go as a teaching tool? Did the play-first, discuss-after order work well?",
                    "response_lines": 2,
                },
                {"prompt": "Concepts or vocabulary to revisit next week:", "response_lines": 2},
            ],
        },
        "Friday",
    )

    # =========================================================================
    # Assemble & write
    # =========================================================================

    html = build_print_packet_html(
        pages, packet_title="Game Theory Week — Game Night for Christopher"
    )
    out_path = output_dir / "game_theory_week.html"
    out_path.write_text(html, encoding="utf-8")

    guide_path = output_dir / "game_theory_week_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print("\nSuccessfully generated Game Theory Week.")
    print(f"Student packet:  {out_path}")
    print(f"Teacher guide:   {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Mon p1 — Reading: How Do You Win? (Game Night Olympics: 4 micro-games) — WIN CONDITIONS",
        "Mon p2 — Matching: Match the Game to How You Win",
        "Tue p1 — Reading: Playing With or Playing Against (Block Tower) — COOPERATION vs COMPETITION",
        "Tue p2 — T-Chart: Working Together or Playing to Win?",
        "Wed p1 — Reading: How Likely Is It? (Mystery Bag) — PROBABILITY",
        "Wed p2 — Bar Graph: Graph Your Mystery Bag (make + read)",
        "Thu p1 — Reading: What You Can't See (Go Fish) — HIDDEN INFORMATION",
        "Thu p2 — Frayer Model: Word Detective — Hidden Information",
        "Fri p1 — Reading: Making a Plan to Win (Don't Take the Last One) — STRATEGY",
        "Fri p2 — Writing Scaffold: My Game Plan",
        "        — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")


# =============================================================================
# TEACHER GUIDE — emitted alongside the packet (output dir is gitignored; this
# script must reproduce the whole week).
# =============================================================================

TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Game Theory Week — Teacher Guide</title>
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
    .setup { background: #eef2ff; border-left: 4px solid #4338ca; padding: 6px 10px; margin: 4px 0 10px; border-radius: 0 4px 4px 0; font-size: 10pt; }
  </style>
</head>
<body>

<div class="page">
  <h1>Game Theory Week — Teacher / Parent Guide</h1>
  <p><strong>Theme:</strong> Game Theory &nbsp;|&nbsp; <strong>Audience:</strong> Christopher, grade 1&ndash;2 &nbsp;|&nbsp;
  <strong>Narrator:</strong> Ace the Fox</p>
  <p><strong>Causal Arc:</strong> Win Conditions &rarr; Cooperation vs. Competition &rarr; Basic Probability &rarr; Hidden Information &rarr; Strategy</p>
  <p><strong>How the week works:</strong> Each day is a <em>mixed lesson</em>. PLAY the day's game first
  (every game sets up and plays in well under 45 minutes with household items), THEN read the passage
  and do the worksheet. The concept always comes out of a game the child has just experienced.</p>

  <h2>Monday — How Do You Win? (Win Conditions)</h2>
  <div class="setup"><strong>Games — Game Night Olympics (~20 min):</strong> Play four quick
  micro-games and, after each, ask "how did you win that one?"  (1) <strong>Tic-Tac-Toe</strong> —
  3&times;3 grid, three in a row (skill; can end in a tie). (2) <strong>Rock-Paper-Scissors</strong> —
  best of five (hidden until the reveal &rarr; foreshadows Thursday). (3) <strong>Coin-Flip
  Call-It</strong> — call heads/tails before the flip (pure luck &rarr; foreshadows Wednesday).
  (4) <strong>Race to 20</strong> — roll a die and add up; first to 20 (luck + choices &rarr;
  foreshadows Friday). The point: every game, big or small, has a win condition, and this week is
  about learning to spot it and plan for it.</div>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1 (Win condition):</strong> The win condition is the way you win a game — the goal you must reach to be the winner.</p>
    <p><strong>Q2 (Tic-Tac-Toe):</strong> Get three of your own marks (three X's or three O's) in a row — across, down, or diagonally.</p>
    <p><strong>Q3 (Ask first):</strong> If you do not know how to win, you cannot aim your moves at the goal. Knowing the win condition lets you plan ahead instead of wasting turns.</p>
    <p><strong>Q4 (Tie):</strong> A tie is when the game ends with no winner and everyone is even. Yes — a game (like Tic-Tac-Toe) can end with no winner.</p>
  </div>
  <h3>Matching Answer Key</h3>
  <div class="answer-box">
    <p>Tic-Tac-Toe &rarr; Get three of your marks in a row</p>
    <p>Rock-Paper-Scissors &rarr; Win the most throws (best of five)</p>
    <p>Coin-Flip Call-It &rarr; Guess the coin flip correctly</p>
    <p>Race to 20 &rarr; Be the first to reach 20 points</p>
    <p>Hide-and-Seek &rarr; Find all of the players who are hiding</p>
    <p>Musical Chairs &rarr; Be the last player sitting in a chair</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Is there a game where you win by NOT doing something?"</em></p>
    <p>Yes — lots! Freeze dance / statues (win by not moving), the quiet game (win by not talking), "don't laugh," or Jenga (you lose if the tower falls on your turn). These have a <em>negative</em> win condition. Great chance to notice that goals can be "do X" or "avoid X."</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"The winner is whoever goes first / whoever is oldest." Redirect to the actual rule: the win condition is defined by the game, not by who the player is. Also normalize the tie — a tie is a real, fair outcome, not a failure.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Play Tic-Tac-Toe a few times, then ask: "Is it possible to never lose?" Show that if both players play carefully, it always ends in a tie. First peek at strategy — sets up Friday.</p>
  </div>

  <h2 class="tue">Tuesday — Playing With or Against (Cooperation vs. Competition)</h2>
  <div class="setup"><strong>Game — Block Tower, two rounds (~20 min):</strong> Round 1 (competition):
  each player builds their own tower; tallest standing tower wins. Round 2 (cooperation): build ONE
  tower together, as tall as possible before it topples. Contrast how the two rounds feel.</div>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box tue">
    <p><strong>Q1 (Competition):</strong> Playing against other players and trying to beat them; only one player or team can win. (Any example: a race, Tic-Tac-Toe.)</p>
    <p><strong>Q2 (Cooperation):</strong> Working together toward the same goal; everyone wins or loses together. Different from competition because you are on the same team, not against each other.</p>
    <p><strong>Q3 (Which round):</strong> Round 1 (each own tower) = competition. Round 2 (one shared tower) = cooperation.</p>
    <p><strong>Q4 (Secret vs. share):</strong> In competition, sharing your best move helps your opponent beat you, so you keep it secret. In cooperation, your teammates' success IS your success, so sharing your best idea helps everyone win.</p>
  </div>
  <h3>T-Chart Answer Key</h3>
  <div class="answer-box tue">
    <p><strong>Working Together (Cooperation):</strong> Building one block tower as tall as you can; Doing a jigsaw puzzle together; Cleaning up all the toys before the timer beeps; A team of ants carrying one big crumb; Rowing a boat together.</p>
    <p><strong>Playing to Win (Competition):</strong> Playing Tic-Tac-Toe; A game of tag; Racing to the mailbox and back; A spelling bee; Seeing who can jump the highest.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Can a game be both?"</em></p>
    <p>Yes — team games like soccer, relay races, or capture the flag: teammates COOPERATE with each other while the two teams COMPETE. This "cooperate within, compete between" idea is a big real-life theme (families, classrooms, sports).</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"Cooperation means there is no winner, so it's boring / not a real game." Emphasize that in cooperative games the players win TOGETHER against the challenge (the falling tower, the timer). The goal and the win are still real.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Play the same simple activity (e.g., a card-flip counting game) once competitively and once cooperatively. Ask Christopher which felt better and why — there is no wrong answer; the point is noticing the difference.</p>
  </div>
</div>

<div class="page">
  <h2 class="wed">Wednesday — How Likely Is It? (Basic Probability)</h2>
  <div class="setup"><strong>Game — Mystery Bag (~15 min):</strong> 5 red + 3 blue + 2 yellow objects
  (10 total) in an opaque bag. Christopher GUESSES the most-likely color first, then draws-tally-replace
  ten times. Keep the tally for the bar graph on the next page. (Replacing each draw keeps the odds
  steady — important for the prediction to hold.)</div>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box wed">
    <p><strong>Q1 (Probability):</strong> Probability is how likely something is to happen.</p>
    <p><strong>Q2 (Likely/unlikely):</strong> Likely: pulling RED (most marbles). Unlikely: pulling YELLOW (fewest marbles). Accept any correct pairing based on the counts.</p>
    <p><strong>Q3 (Prediction):</strong> Personal response. The strong prediction is red (5 of 10). Discuss whether the actual tally matched — with only 10 draws it usually leans red but may not be exact.</p>
    <p><strong>Q4 (Luck vs. skill):</strong> All luck: flipping a coin, rolling a die (you cannot control it). All skill: a spelling test (your effort decides). Many games mix both.</p>
  </div>
  <h3>Bar Graph — What to Check</h3>
  <div class="answer-box wed">
    <p>This is a MAKE-a-graph page — Christopher colors one square per tally mark, so bars will vary. Check that: (a) each bar's height matches the tally count, (b) the tallest bar is usually Red, and (c) the graph reading answers are consistent with the bars he drew. Expected shape (over many trials): Red &gt; Blue &gt; Yellow, mirroring 5 &gt; 3 &gt; 2.</p>
    <p><strong>Q3 (why red most):</strong> There are more red marbles than any other color, so red is the most likely to be pulled. Real results may wobble because 10 draws is a small sample.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"9 red and 1 green — which will you probably pull? Could you still pull green?"</em></p>
    <p>You will almost certainly pull red (very likely). But green is still POSSIBLE, just unlikely — it is not impossible. Key idea: likely does not mean certain, and unlikely does not mean impossible.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"It didn't come out exactly 5-3-2, so the prediction was wrong." With only 10 draws, results wobble around the expected amounts. More draws (try 30&ndash;40) get closer to the true ratio. Also watch the gambler's idea that a color is "due" — each draw is independent.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Repeat the experiment with 30 draws and tally again — the bars should line up closer to 5:3:2. Or change the bag (e.g., 8 red, 2 blue) and predict BEFORE drawing how the graph will change.</p>
  </div>

  <h2 class="thu">Thursday — What You Can't See (Hidden Information)</h2>
  <div class="setup"><strong>Game — Go Fish (~15 min):</strong> Deal 5&ndash;7 cards each; hold your
  hand hidden. Ask for ranks to make pairs; "Go Fish" when the opponent lacks the card. Point out that
  each player's hand is hidden information.</div>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box thu">
    <p><strong>Q1 (Hidden information):</strong> Anything in a game you cannot see or know. Example: your opponent's cards in Go Fish; face-down memory cards; where players hide in hide-and-seek.</p>
    <p><strong>Q2 (Go Fish):</strong> Your opponent's cards are hidden from you (and yours from them).</p>
    <p><strong>Q3 (Good players):</strong> They watch closely, remember what has happened, and use clues to make smart guesses.</p>
    <p><strong>Q4 (Open game):</strong> A game where you can see everything, nothing hidden — e.g., Tic-Tac-Toe or Checkers.</p>
  </div>
  <h3>Frayer Model — Model Answers</h3>
  <div class="answer-box thu">
    <p><strong>What it means:</strong> Something in a game you cannot see or know.</p>
    <p><strong>Games that have it:</strong> Go Fish, memory/matching, hide-and-seek, Guess Who, Battleship.</p>
    <p><strong>What a smart player does:</strong> Pays attention, remembers clues, makes smart guesses, and hides their own information.</p>
    <p><strong>Draw a picture:</strong> Accept any reasonable drawing — e.g., a hand of cards held up so no one can see, or face-down cards. (This box is open-ended.)</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Why would seeing your opponent's cards ruin Go Fish?"</em></p>
    <p>If you could see everything, there would be no guessing — you would just take every pair instantly and the game would be over with no thinking or fun. Hidden information is what makes the game a challenge and keeps it exciting.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"Hidden information means cheating / peeking is allowed." Clarify the opposite: the information is <em>supposed</em> to stay hidden; the skill is making good guesses WITHOUT seeing. Peeking breaks the game.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Play a quick round of "20 Questions" — the answer is hidden information, and yes/no questions are clues that narrow it down. Notice how each answer removes possibilities.</p>
  </div>
</div>

<div class="page">
  <h2 class="fri">Friday — Making a Plan to Win (Strategy — Capstone)</h2>
  <div class="setup"><strong>Game — "Don't Take the Last One" / Nim (~15 min):</strong> Line up 10
  objects. Players alternate taking 1, 2, or 3. Whoever must take the LAST object loses. Encourage
  Christopher to hunt for a repeatable winning trick.</div>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box fri">
    <p><strong>Q1 (Strategy):</strong> A plan you make to reach your win condition — a set of steps that gives you the best chance to win.</p>
    <p><strong>Q2 (Strategy vs. random):</strong> A strategist thinks ahead ("if I do this, then what?") and aims moves at the goal; a random player just picks any move with no plan.</p>
    <p><strong>Q3 (Four ideas):</strong> Win condition, cooperation vs. competition, luck/probability, and hidden information.</p>
    <p><strong>Q4 (Nim strategy):</strong> Think backward: try to leave your opponent with exactly 1 object, so they must take it and lose. (Deeper trick, optional: leave a multiple of 4 — 8, then 4 — because whatever they take (1&ndash;3), you take enough to return to a multiple of 4.)</p>
  </div>
  <h3>Writing Scaffold — What to Check</h3>
  <div class="answer-box fri">
    <p>Open-ended — Christopher picks any game. Look for: a correctly stated win condition, a reasonable luck/skill judgment, and a strategy written as STEPS ("first..., then..."). The step-by-step form is the standard being practiced (a strategy = an algorithm). Encourage full sentences and this week's vocabulary.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Can a great strategy still lose? Can luck beat a plan?"</em></p>
    <p>Yes. In games with chance (dice, cards), bad luck can beat a good plan on any single game. A good strategy improves your ODDS over many games, but does not guarantee any one win. In pure-skill games with no luck (Tic-Tac-Toe, Nim), a perfect strategy cannot be beaten by luck — only by a mistake.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"A strategy guarantees a win." Reinforce that strategy improves your chances; luck and the opponent's choices still matter. Also: "strategy is just for grown-ups / hard games" — even Tic-Tac-Toe has one.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Play Nim starting from different pile sizes and let Christopher discover which starting position lets the first player force a win. Or invent a brand-new game together and write down its rules, win condition, and one strategy.</p>
  </div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2 class="fri">Week Summary — The Building Blocks of a Good Player</h2>
  <p>The week built one idea on the next:</p>
  <ol style="padding-left: 20px; font-size: 10pt; line-height: 2;">
    <li><strong>Monday:</strong> Every game has a <strong>win condition</strong> — always ask "how do I win?" first.</li>
    <li><strong>Tuesday:</strong> Games are <strong>competitive or cooperative</strong> (or both) — know which you are playing.</li>
    <li><strong>Wednesday:</strong> <strong>Probability</strong> — some outcomes are more likely; use what you know to predict.</li>
    <li><strong>Thursday:</strong> <strong>Hidden information</strong> — you cannot see everything; use clues and memory.</li>
    <li><strong>Friday:</strong> <strong>Strategy</strong> ties it together — a step-by-step plan to reach your win condition.</li>
  </ol>
  <p style="margin-top: 10px;">By Friday, Christopher should be able to look at any game and name its win condition, say whether it is cooperative or competitive and how much is luck vs. skill, and describe a simple strategy — the habits of a thoughtful player and a thoughtful person.</p>
</div>

</body>
</html>"""


if __name__ == "__main__":
    generate_game_theory_week_series()
