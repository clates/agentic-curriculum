# Why a week is a script

When Claude Code writes a week, it doesn't hand back a PDF. It writes a small Python program,
`scripts/generate_<theme>_week_series.py`, and that program produces the packet and the teacher
guide. Every passage, question and answer is inside the script. The HTML it writes is a by-product.

## What a script gives you that a document doesn't

**It can be reproduced.** A year from now, after the printout is lost, running the script gives
the identical packet. The standards database and the renderer are in the repo too, so nothing
outside it is needed.

**It can be adjusted.** Changing one question is a one-line edit. A document would have to be
regenerated, and every other page could change with it.

**It can be reviewed.** A new or changed week is a code change, so a diff shows exactly what moved
between two versions. That matters most for the main way weeks fail: naming a standard without
actually teaching it. A reviewer can check each standard ID in the docstring against what the days
contain.

**It is small.** A script is a few dozen kilobytes. The week it produces, with its images, is not.

## What it costs

Someone who just wants a printout has to run a command first. The
[`examples/`](../../examples/) folder exists for that reason: weeks good enough to share have their
output committed there, so they can be read without installing anything.

Generated output is otherwise ignored by git. If the output were committed alongside the script,
the two could drift apart, and nobody could tell which one was the real week.

## How this differs from the hosted app

The hosted app doesn't write scripts. There, a model writes each
week as structured data (a "week document"), which the server validates and renders; see
[Why hosted weeks are data](hosted-weeks-are-data.md). The reasons differ. On your own machine,
you are the one who runs the code Claude wrote. On a shared server, nothing a model writes may run.
