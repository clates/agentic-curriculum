# Examples

Curated, shareable output from this repo — safe to open, print, or send to someone who wants to see
what the system produces before installing anything.

These are **public artifacts**. Everything else the app generates lands in gitignored
`<theme>_week_series/` directories and stays local.

| Example | Grade | Subject | Files |
|---------|-------|---------|-------|
| [Weather Week](weather-week/) | K–1 | Science | [student packet](weather-week/weather_week.html) · [teacher guide](weather-week/weather_week_teacher_guide.html) |
| [Data Detectives Week](data-week/) | 1–2 | Science + Data & Graphing | [student packet](data-week/data_week.html) · [teacher guide](data-week/data_week_teacher_guide.html) |
| [Matter Week](matter-week/) | K–1 | Science | [student packet](matter-week/matter_week.html) · [teacher guide](matter-week/matter_week_teacher_guide.html) |
| [Sky and Space Week](sky-week/) | K–1 | Science | [student packet](sky-week/sky_week.html) · [teacher guide](sky-week/sky_week_teacher_guide.html) |
| [Money Week](money-week/) | K–1 | Math + Social Studies | [student packet](money-week/money_week.html) · [teacher guide](money-week/money_week_teacher_guide.html) |
| [Game Theory Week](game-theory-week/) | 1–2 | Games, Logic & Math | [student packet](game-theory-week/game_theory_week.html) · [teacher guide](game-theory-week/game_theory_week_teacher_guide.html) |
| [Test-Taking Strategies](test-taking-strategies/) | K–1 | Study Skills | [student packet](test-taking-strategies/test_taking_strategies.html) · [teacher guide](test-taking-strategies/test_taking_strategies_teacher_guide.html) |

Most are five-day weeks. **Game Theory** is a "mixed lesson" week — the family plays a short game
each day, then reads a passage dissecting the concept behind it. **Test-Taking Strategies** is a
deliberate two-day mini-unit, included to show that a "week" is a default, not a requirement.

Open any `.html` file in a browser. The student packet opens the print dialog automatically —
that is the intended output: paper on a table in front of a kid.

## How these were made

Each example is the output of a tracked generator script, and re-running the script reproduces the
file byte for byte:

```bash
venv/bin/python scripts/generate_weather_week_series.py   # -> weather_week_series/
venv/bin/python scripts/generate_data_week_series.py      # -> data_week_series/
# ...and likewise for matter, sky, money, game_theory, test_taking_strategies
```

The scripts themselves were written by Claude Code via the `/generate-week` skill. See
[Make your own week](../README.md#make-your-own-week) in the root README.

## Adding an example

Only add output you would be happy for a stranger to read. Copy the generated packet and teacher
guide into `examples/<theme>-week/`, add a row to the table above, and confirm the generator script
that produced it is committed — an example whose script is missing cannot be reproduced or fixed.

Use a `-week` (hyphen) directory name, not `_week_series` — the underscore form is gitignored.
