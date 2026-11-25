# agentic-curriculum

**A workbench for building a week of school.**

You tell Claude Code a topic, such as volcanoes, fractions or ancient Egypt, and it writes a
complete five-day lesson week for your student: a printable packet of worksheets, and a teacher
guide with the answers, discussion prompts and common misconceptions. Every day is aligned to
real published education standards, which it looks up rather than invents.

It isn't a worksheet website. It's a tool that writes curriculum for one child in particular:
yours.

> **See one before you install anything:**
> [`examples/weather-week/weather_week.html`](examples/weather-week/weather_week.html), a
> kindergarten-to-first-grade science week, and its
> [teacher guide](examples/weather-week/weather_week_teacher_guide.html).

## Two ways to use it

| | What you get | What you need |
|---|---|---|
| **Print and write weeks** | Print the included weeks; have Claude Code write new ones on any topic | Python and [Claude Code](https://claude.com/claude-code). No API key |
| **Track a student over time** | A web app that records what your student mastered and adjusts the next plan | Also an OpenRouter API key and Node.js |

Most people only need the first.

## Start here

**[Your first week](docs/tutorials/your-first-week.md)**: install, print a ready-made week, then
have Claude write one for your student. About twenty minutes.

## Then

- [Get a better week from `/generate-week`](docs/how-to/write-a-better-week.md)
- [Track a student over time](docs/how-to/track-a-student.md)
- [Included weeks and worksheet types](docs/reference/included-weeks.md)
- [Why a week is a script](docs/explanation/why-a-week-is-a-script.md)
- [Fix common problems](docs/how-to/fix-common-problems.md)

All documentation: [`docs/`](docs/README.md). Changing the code:
[`CONTRIBUTING.md`](CONTRIBUTING.md).
