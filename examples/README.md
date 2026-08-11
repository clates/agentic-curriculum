# Examples

Curated, shareable output from this repo — safe to open, print, or send to someone who wants to see
what the system produces before installing anything.

These are **public artifacts**. Everything else the app generates lands in gitignored
`<theme>_week_series/` directories and stays local.

| Example | Grade | Subject | Files |
|---------|-------|---------|-------|
| [Weather Week](weather-week/) | K–1 | Science | [student packet](weather-week/weather_week.html) · [teacher guide](weather-week/weather_week_teacher_guide.html) |
| [Data Detectives Week](data-week/) | 1–2 | Science + Data & Graphing | [student packet](data-week/data_week.html) · [teacher guide](data-week/data_week_teacher_guide.html) |

Open any `.html` file in a browser. The student packet opens the print dialog automatically —
that is the intended output: paper on a table in front of a kid.

## How these were made

Each example is the output of a tracked generator script, and re-running the script reproduces the
file byte for byte:

```bash
venv/bin/python scripts/generate_weather_week_series.py   # -> weather_week_series/
venv/bin/python scripts/generate_data_week_series.py      # -> data_week_series/
```

The scripts themselves were written by Claude Code via the `/generate-week` skill. See
[Make your own week](../README.md#make-your-own-week) in the root README.

## Adding an example

Only add output you would be happy for a stranger to read. Copy the generated packet and teacher
guide into `examples/<theme>-week/`, add a row to the table above, and confirm the generator script
that produced it is committed — an example whose script is missing cannot be reproduced or fixed.

Use a `-week` (hyphen) directory name, not `_week_series` — the underscore form is gitignored.
