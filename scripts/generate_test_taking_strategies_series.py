"""
Test-Taking Strategies — 2-Day Mini-Unit
Grade K-1 | Study Skills | Arc: Read Carefully & Pace Yourself -> Eliminate, Check, and Stay Calm

Narrator: Ollie the Owl, a spectacled "Test-Taking Detective" with a magnifying glass, introduced
on Day 1. Ollie treats each test like a mystery to solve rather than something to fear.

Standards: N/A — this is a general test-readiness / executive-function skill unit, not tied to a
specific content-area SOL standard.

Output: single printable HTML document — test_taking_strategies_series/test_taking_strategies.html
This is intentionally a short 2-day unit, not a full 5-day week.
"""

import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("src"))

from worksheet_html_renderer import build_print_packet_html, render_worksheet_html


def generate_test_taking_strategies_series():
    output_dir = Path("test_taking_strategies_series")
    output_dir.mkdir(exist_ok=True)

    pages: list[tuple[str, str]] = []  # (day_label, html_fragment)

    def add(kind: str, data: dict, day_label: str) -> None:
        fragment = render_worksheet_html(kind, data, day_label)
        if fragment is None:
            raise ValueError(f"No HTML renderer for kind={kind!r}")
        pages.append((day_label, fragment))

    # =========================================================================
    # DAY 1 — Read Carefully & Pace Yourself
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Day 1: Meet Ollie and Get Ready to Test",
            "passage_title": "Meet Ollie the Owl — Your Test-Taking Detective",
            "instructions": (
                "Read about Ollie's first detective tricks. Then answer the questions below."
            ),
            "passage": (
                "Meet Ollie the Owl! Ollie is a wise old owl with big round glasses and a "
                "magnifying glass that never leaves his side. Ollie loves solving mysteries — and "
                "today, he has a new case: helping you become a Test-Taking Detective!\n\n"
                "'A test is not something to be scared of,' Ollie hoots. 'A test is just a chance "
                "to show everyone what you already know. Think of it like a treasure hunt — and "
                "I'm going to teach you the clues that help you find every answer!'\n\n"
                "Ollie's first detective trick is reading the DIRECTIONS. Directions are the "
                "sentences at the top of a page that tell you exactly what to do. Before answering "
                "anything, Ollie always reads the directions twice and hunts for CLUE WORDS — "
                "important words like 'circle,' 'underline,' 'choose one,' or 'choose all that "
                "apply.' Missing a clue word is the most common mistake a test detective can make!\n\n"
                "Ollie's second trick is reading the WHOLE question before answering. 'Many "
                "detectives get tricked,' Ollie warns, 'because they stop reading halfway through "
                "and guess too soon. Always read every single word, all the way to the question "
                "mark!'\n\n"
                "Ollie's third trick is PACING — using your time wisely. Before starting, Ollie "
                "glances at how many questions are on the page. If one question feels too tricky, "
                "Ollie doesn't freeze — he puts a small mark next to it, skips it, and comes back "
                "after finishing the easier ones. That way, no time is wasted stuck on just one "
                "clue.\n\n"
                "Finally, Ollie always takes one slow, deep breath before he begins. 'A calm "
                "detective thinks clearly,' he says. 'It's okay to feel a little nervous — "
                "everyone does! Just breathe, remember you've been practicing, and do your very "
                "best.'\n\n"
                "With his glasses polished and his mind calm, Ollie the Owl was ready for any "
                "test that came his way. Are you ready to be a detective too?"
            ),
            "vocabulary": [
                {
                    "term": "calm",
                    "definition": (
                        "Feeling relaxed and ready to think clearly — taking a deep breath helps "
                        "you feel this way."
                    ),
                },
                {
                    "term": "skip and return",
                    "definition": (
                        "Marking a hard question, moving on, and coming back to it later instead "
                        "of getting stuck."
                    ),
                },
                {
                    "term": "clue words",
                    "definition": (
                        "Important words in directions, like 'circle' or 'choose all that "
                        "apply,' that tell you exactly what to do."
                    ),
                },
                {
                    "term": "pace",
                    "definition": (
                        "Using your time wisely during a test — not rushing, but not stuck "
                        "either."
                    ),
                },
                {
                    "term": "directions",
                    "definition": (
                        "The instructions at the top of a page that explain what you're supposed "
                        "to do."
                    ),
                },
            ],
            "questions": [
                {
                    "prompt": (
                        "What are 'clue words,' and why does Ollie hunt for them in the "
                        "directions?"
                    ),
                    "response_lines": 2,
                },
                {
                    "prompt": "Why does Ollie always read the WHOLE question before answering?",
                    "response_lines": 2,
                },
                {
                    "prompt": "What does Ollie do when he finds a question that feels too tricky?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Ollie says feeling a little nervous before a test is "
                        "normal. What is one thing you could do to feel calmer if you started to "
                        "feel nervous during a test?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Day 1",
    )

    add(
        "wordSortWorksheet",
        {
            "title": "Day 1: Smart Test Habits vs. Testing Traps — Word Sort",
            "instructions": (
                "Look at each card below. Write it in the correct box — is it a Smart Test "
                "Habit that helps you, or a Testing Trap that hurts you?"
            ),
            "categories": [{"label": "Smart Test Habits"}, {"label": "Testing Traps"}],
            "tiles": [
                "Skip the directions",
                "Read the whole question",
                "Rush through without checking",
                "Look for clue words",
                "Answer only half the question",
                "Take a slow breath before starting",
                "Guess before reading the question",
                "Skip a hard question and come back",
                "Stay stuck on one hard question",
                "Read the directions twice",
            ],
        },
        "Day 1",
    )

    # =========================================================================
    # DAY 2 — Eliminate, Check, and Stay Calm
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "Day 2: Smart Test Moves",
            "passage_title": "Ollie's Next Case: Elimination, Checking, and Staying Calm",
            "instructions": (
                "Read about Ollie's next two detective tricks. Then answer the questions below."
            ),
            "passage": (
                "Ollie the Owl had one wing wrapped around his magnifying glass, ready for his "
                "next detective case. 'Yesterday you learned to read carefully and pace "
                "yourself,' he hooted. 'Today, I'll teach you two of my favorite detective tricks "
                "— and how to handle those nervous jitters, too!'\n\n"
                "Ollie's first trick today is PROCESS OF ELIMINATION. When a question has "
                "several choices and you're not sure of the answer, Ollie doesn't panic. "
                "Instead, he looks at each choice and crosses out any answer he KNOWS is wrong. "
                "'If I can rule out two silly answers,' Ollie explains, 'I only have to choose "
                "between the two that are left — and that makes it much easier to pick the "
                "right one!'\n\n"
                "Ollie's second trick is CHECKING YOUR WORK. Right before he turns in a test, "
                "Ollie always goes back to the very first page and rereads every question one "
                "more time. He makes sure he didn't skip any, and he double-checks that his "
                "answers actually match the questions being asked. 'Checking is like a detective "
                "examining the clues one last time before closing the case,' Ollie says. 'It "
                "catches mistakes I might have rushed past the first time.'\n\n"
                "Sometimes, even the best detectives feel nervous. Maybe your tummy feels "
                "fluttery, or your hands feel a little shaky. Ollie says that's completely "
                "normal — it just means you care about doing well! When Ollie feels nervous, he "
                "pauses, takes three slow breaths, and reminds himself, 'I have practiced. I "
                "know a lot. I will do my best, and that is enough.' Saying kind, calm words to "
                "yourself is called POSITIVE SELF-TALK, and it helps quiet those nervous "
                "feelings so your brain can think clearly again.\n\n"
                "Ollie closed his notebook with a satisfied nod. 'Elimination narrows the "
                "mystery. Checking catches the clues you missed. And a calm mind solves every "
                "case. Now you have all my detective secrets — go show everyone what you "
                "know!'"
            ),
            "vocabulary": [
                {
                    "term": "nervous",
                    "definition": (
                        "A fluttery or shaky feeling before or during a test — it's normal and "
                        "just means you care about doing well."
                    ),
                },
                {
                    "term": "rule out",
                    "definition": "To decide that an answer choice is definitely wrong, so you don't pick it.",
                },
                {
                    "term": "positive self-talk",
                    "definition": (
                        "Saying kind, calm words to yourself, like 'I have practiced, I will do "
                        "my best,' to help you feel less nervous."
                    ),
                },
                {
                    "term": "checking your work",
                    "definition": (
                        "Going back over your answers before turning in a test to catch mistakes "
                        "and make sure every question is answered."
                    ),
                },
                {
                    "term": "process of elimination",
                    "definition": (
                        "Crossing out answer choices you know are wrong so you can focus on the "
                        "choices that are left."
                    ),
                },
            ],
            "questions": [
                {
                    "prompt": (
                        "What is 'process of elimination,' and how does it help Ollie pick an "
                        "answer when he's not sure?"
                    ),
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "Why does Ollie check his work before turning in a test? What is he "
                        "looking for?"
                    ),
                    "response_lines": 2,
                },
                {
                    "prompt": "What does Ollie do when he starts to feel nervous during a test?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "LET'S DISCUSS: Ollie says feeling nervous just means 'you care about "
                        "doing well.' Can you think of a kind, calm thing you could say to "
                        "yourself before your next test?"
                    ),
                    "response_lines": 0,
                },
            ],
        },
        "Day 2",
    )

    add(
        "matchingWorksheet",
        {
            "title": "Day 2: Detective Tricks — Matching",
            "instructions": (
                "Draw a line from each detective trick on the left to its meaning on the right. "
                "This mixes in tricks from both days!"
            ),
            "left_items": [
                "Process of Elimination",
                "Checking Your Work",
                "Positive Self-Talk",
                "Clue Words",
                "Pacing",
                "Skip and Return",
            ],
            "right_items": [
                "Crossing out answers you know are wrong to narrow down your choices",
                "Important words in the directions that tell you exactly what to do",
                "Marking a hard question, moving on, and coming back to it later",
                "Saying kind, calm words to yourself to feel less nervous",
                "Using your time wisely so you don't get stuck on one question",
                "Going back over your answers before turning in the test",
            ],
        },
        "Day 2",
    )

    # =========================================================================
    # PARENT FEEDBACK & TEACHING NOTES
    # =========================================================================

    add(
        "readingWorksheet",
        {
            "title": "End-of-Unit Parent Feedback — Test-Taking Strategies",
            "passage_title": "Unit Summary & Teaching Notes for the Parent",
            "instructions": (
                "Please complete this feedback sheet after the two days wrap up. Your notes help "
                "shape future study-skills lessons."
            ),
            "passage": (
                "This short unit covered five core test-taking strategies through Ollie the Owl, "
                "a detective narrator. Day 1 established the 'before and during' habits: reading "
                "directions carefully, hunting for clue words, reading the whole question, "
                "pacing yourself across the page, and skipping a hard question to return to it "
                "later. Day 2 added two active problem-solving tricks — process of elimination "
                "and checking your work — plus one emotional-regulation tool: positive "
                "self-talk for managing normal pre-test nerves.\n\n"
                "Key concepts to check for genuine understanding — not just recall:\n"
                "1) A test is a chance to show what you know, not something to fear.\n"
                "2) Directions and clue words matter as much as the questions themselves.\n"
                "3) Skipping a hard question and returning to it is a strategy, not giving up.\n"
                "4) Process of elimination narrows choices even without knowing the answer "
                "outright.\n"
                "5) Checking your work is a distinct final step, not the same as answering "
                "carefully the first time.\n\n"
                "Common misconceptions to watch for:\n"
                "• 'Skipping a question means I failed it' (it's a pacing tool — you come back).\n"
                "• 'Feeling nervous means something is wrong' (it's normal; the goal is managing "
                "it, not eliminating it).\n"
                "• 'Checking work just means rereading my own handwriting' (it means rereading "
                "the question too, to confirm the answer actually matches what was asked).\n\n"
                "Suggested follow-on activities: time a short practice worksheet together and "
                "talk through pacing out loud; play a 'rule it out' game with silly multiple-"
                "choice questions; practice one calming phrase together before the next real "
                "test or quiz."
            ),
            "vocabulary": [
                {
                    "term": "Strongest Concept",
                    "definition": "(Fill in after the unit — which strategy did Christopher grasp best?)",
                },
                {
                    "term": "Key Misconception to Watch",
                    "definition": (
                        "Skipping a hard question is a pacing strategy, not a failure — make "
                        "sure the 'return to it later' habit actually sticks."
                    ),
                },
                {
                    "term": "Next Step",
                    "definition": (
                        "Apply these five strategies to a real, low-stakes practice worksheet or "
                        "quiz within the next week to reinforce the habits."
                    ),
                },
            ],
            "questions": [
                {
                    "prompt": (
                        "Overall comfort with the strategies — how well did Christopher grasp "
                        "them? (1 = struggled throughout, 5 = strong grasp of all five)"
                    ),
                    "response_lines": 1,
                },
                {
                    "prompt": "Which strategy seemed to click fastest? Which needs more practice?",
                    "response_lines": 2,
                },
                {
                    "prompt": (
                        "Could Christopher explain, in his own words, what to do when he doesn't "
                        "know an answer right away?"
                    ),
                    "response_lines": 2,
                },
                {
                    "prompt": "Did he show any signs of test anxiety during practice? How did he respond?",
                    "response_lines": 2,
                },
                {
                    "prompt": "Strategies or vocabulary to revisit before the next real test:",
                    "response_lines": 2,
                },
            ],
        },
        "Day 2",
    )

    # =========================================================================
    # Assemble & write
    # =========================================================================

    html = build_print_packet_html(
        pages, packet_title="Test-Taking Strategies — A 2-Day Mini-Unit for Christopher"
    )
    out_path = output_dir / "test_taking_strategies.html"
    out_path.write_text(html, encoding="utf-8")

    # Teacher guide
    TEACHER_GUIDE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Test-Taking Strategies — Teacher Guide</title>
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
    h2.day2 { background: #15803d; }
    h3 { font-size: 10.5pt; font-weight: bold; color: #444; margin: 8px 0 3px; text-transform: uppercase; letter-spacing: 0.04em; }
    p, li { font-size: 10pt; margin-bottom: 5px; }
    ul, ol { padding-left: 18px; margin-bottom: 8px; }
    .answer-box { background: #f0f4ff; border-left: 4px solid #1d4ed8; padding: 6px 10px; margin: 4px 0 10px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .answer-box.day2 { background: #f0fff4; border-color: #15803d; }
    .misconception { background: #fff3cd; border-left: 4px solid #d97706; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .extension { background: #e8f5e9; border-left: 4px solid #15803d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
    .discuss { background: #fce7f3; border-left: 4px solid #9d174d; padding: 6px 10px; margin: 4px 0 8px; border-radius: 0 4px 4px 0; font-size: 10pt; }
  </style>
</head>
<body>

<div class="page">
  <h1>Test-Taking Strategies — Teacher / Parent Guide</h1>
  <p><strong>Theme:</strong> Test-Taking Strategies &nbsp;|&nbsp; <strong>Audience:</strong> Christopher, age 6, K-1 &nbsp;|&nbsp;
  <strong>Narrator:</strong> Ollie the Owl, Test-Taking Detective</p>
  <p><strong>Arc:</strong> Read Carefully &amp; Pace Yourself &rarr; Eliminate, Check, and Stay Calm</p>
  <p><strong>Note:</strong> This is a short 2-day study-skills mini-unit, not a full 5-day content week.</p>

  <h2>Day 1 — Read Carefully &amp; Pace Yourself</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box">
    <p><strong>Q1 (Clue words):</strong> Clue words are important words in the directions — like "circle," "underline," or "choose all that apply" — that tell you exactly what to do. Missing one is a common mistake, so Ollie hunts for them before answering.</p>
    <p><strong>Q2 (Whole question):</strong> Stopping halfway through a question often leads to guessing wrong. Reading all the way to the question mark makes sure you understand what is actually being asked.</p>
    <p><strong>Q3 (Tricky question):</strong> Ollie marks it, skips it, and comes back to it after finishing the easier questions, so he doesn't waste time stuck on one clue.</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"What could you do to feel calmer if you got nervous during a test?"</em></p>
    <p>Expected reasoning: taking a slow breath, remembering you've practiced, or reminding yourself it's okay to skip a hard question. There is no single right answer — encourage the child to name a concrete, repeatable action rather than just "feel less nervous."</p>
  </div>
  <h3>Word Sort Answer Key</h3>
  <div class="answer-box">
    <p><strong>Smart Test Habits:</strong> Read the whole question, Look for clue words, Take a slow breath before starting, Skip a hard question and come back, Read the directions twice</p>
    <p><strong>Testing Traps:</strong> Skip the directions, Rush through without checking, Answer only half the question, Guess before reading the question, Stay stuck on one hard question</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>Children often treat "skipping a question" as the same as giving up. Reinforce that Ollie always marks it and returns — skipping is a deliberate pacing move, not a failure.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Give a short, low-stakes practice page with a timer. Before starting, have Christopher say out loud what the directions ask for and circle any clue words. Afterward, ask which question (if any) he skipped and came back to.</p>
  </div>
</div>

<div class="page">
  <h2 class="day2">Day 2 — Eliminate, Check, and Stay Calm</h2>
  <h3>Answer Key — Reading Questions</h3>
  <div class="answer-box day2">
    <p><strong>Q1 (Process of elimination):</strong> Crossing out answer choices you know are wrong narrows the remaining choices, making it easier to pick the right one even without knowing it outright.</p>
    <p><strong>Q2 (Checking your work):</strong> Ollie rereads every question one more time before turning in a test, making sure nothing was skipped and that each answer actually matches its question — catching mistakes made while rushing the first time.</p>
    <p><strong>Q3 (Feeling nervous):</strong> Ollie pauses, takes three slow breaths, and uses positive self-talk ("I have practiced, I will do my best") to calm down and think clearly again.</p>
  </div>
  <h3>Matching Answer Key</h3>
  <div class="answer-box day2">
    <p>Process of Elimination &rarr; Crossing out answers you know are wrong to narrow down your choices</p>
    <p>Checking Your Work &rarr; Going back over your answers before turning in the test</p>
    <p>Positive Self-Talk &rarr; Saying kind, calm words to yourself to feel less nervous</p>
    <p>Clue Words &rarr; Important words in the directions that tell you exactly what to do</p>
    <p>Pacing &rarr; Using your time wisely so you don't get stuck on one question</p>
    <p>Skip and Return &rarr; Marking a hard question, moving on, and coming back to it later</p>
  </div>
  <h3>LET'S DISCUSS Guidance</h3>
  <div class="discuss">
    <p><em>"Can you think of a kind, calm thing you could say to yourself before your next test?"</em></p>
    <p>Any short, positive, first-person statement counts ("I know a lot," "I've practiced this," "I can do my best"). The goal is building a personal, repeatable phrase he can recall under mild stress — not a perfect script.</p>
  </div>
  <h3>Misconceptions to Watch</h3>
  <div class="misconception">
    <p>"Checking my work" is sometimes treated as just rereading handwriting for neatness. Clarify it means rereading the *question* too, to confirm the chosen answer actually responds to what was asked.</p>
  </div>
  <h3>Extension Activity</h3>
  <div class="extension">
    <p>Play a quick "rule it out" game: ask a silly multiple-choice question (e.g., "Which of these is a fruit — a rock, an apple, a shoe, or a cloud?") and have Christopher cross out the choices he knows are wrong before picking.</p>
  </div>

  <hr style="margin: 18px 0; border-color: #ccc;">
  <h2 class="day2">Unit Summary — The Five Strategies</h2>
  <ol>
    <li><strong>Read directions &amp; hunt for clue words</strong> before answering anything.</li>
    <li><strong>Read the whole question</strong>, all the way to the question mark.</li>
    <li><strong>Pace yourself</strong> — skip a hard question and return to it later.</li>
    <li><strong>Use process of elimination</strong> to narrow down uncertain answers.</li>
    <li><strong>Check your work</strong> and use positive self-talk to stay calm.</li>
  </ol>
  <p style="margin-top: 10px;">By the end of Day 2, Christopher should be able to name at least three of these five strategies unprompted and describe what to do when stuck on a hard question.</p>
</div>

</body>
</html>"""

    guide_path = output_dir / "test_taking_strategies_teacher_guide.html"
    guide_path.write_text(TEACHER_GUIDE, encoding="utf-8")

    print("\nSuccessfully generated Test-Taking Strategies mini-unit.")
    print(f"Student packet:  {out_path}")
    print(f"Teacher guide:   {guide_path}")
    print(
        f"  {len(pages)} pages — open the packet in a browser and print (dialog opens automatically)\n"
    )
    print("  Pages:")
    labels = [
        "Day 1 p1 — Reading: Meet Ollie and Get Ready to Test",
        "Day 1 p2 — Word Sort: Smart Test Habits vs. Testing Traps",
        "Day 2 p1 — Reading: Smart Test Moves",
        "Day 2 p2 — Matching: Detective Tricks",
        "         — Parent Feedback & Teaching Notes",
    ]
    for label in labels:
        print(f"    {label}")


if __name__ == "__main__":
    generate_test_taking_strategies_series()
