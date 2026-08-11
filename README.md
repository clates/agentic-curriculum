# agentic-curriculum

**A workbench for building a week of school.**

You tell Claude Code a topic — volcanoes, fractions, ancient Egypt — and it writes a complete
five-day lesson week for your student: a printable packet of worksheets, plus a teacher guide with
the answers, discussion prompts, and common misconceptions. Every day is aligned to real published
education standards, which it looks up rather than invents.

It is not a worksheet website. It is a tool that writes curriculum, aimed at one kid in particular:
yours.

> **See it before you install anything:** open
> [`examples/weather-week/weather_week.html`](examples/weather-week/weather_week.html) — a real
> K–1 science week — and its
> [teacher guide](examples/weather-week/weather_week_teacher_guide.html).

---

## Two ways to use this

Pick the one that matches what you want. **Most people only ever need the first.**

| | What you get | What it costs you |
|---|---|---|
| **Print & author weeks** | Print the included weeks; have Claude Code write new ones on any topic | Python + [Claude Code](https://claude.com/claude-code). No API key. |
| **Track a student over time** | The above, plus a web app that records what your student mastered and adapts next week's plan | Adds an OpenAI API key, two servers, and Node.js |

The second path needs the first to be set up anyway, so start at the top and stop whenever you have
what you need.

---

## Setup

You need **Python 3.11, 3.12, or 3.13**. Newer versions will fail to install (a dependency doesn't
build on 3.14+). If your system Python is too new, [`uv`](https://docs.astral.sh/uv/) will fetch a
correct one for you.

```bash
git clone https://github.com/clates/agentic-curriculum.git
cd agentic-curriculum

# Create the virtual environment (it must live here, at the repo root)
uv venv --python 3.12 --seed venv        # or: python3.12 -m venv venv
venv/bin/pip install -r requirements.txt

# Build the standards database — this is what lessons get aligned against
venv/bin/python src/ingest_standards.py
```

That last step creates `curriculum.db` from the standards in `standards_data/`. **Don't skip it** —
it is where Claude looks up "what is a 1st grader supposed to learn about weather," and week
authoring depends on it.

---

## Print a week right now

```bash
venv/bin/python scripts/generate_weather_week_series.py
```

Open `weather_week_series/weather_week.html` in any browser. The print dialog opens by itself.
You now have five days of science worksheets and a teacher guide.

Every week in this repo works the same way: **the week is a Python script**, and running it
regenerates the whole packet. See [what's already written](#weeks-already-written).

---

## Make your own week

This is the part worth understanding. You describe a topic; Claude Code writes the week.

**You need [Claude Code](https://claude.com/claude-code) installed, and the setup above done.**

### 1. Tell it about your student — once

```bash
cp student_profile.example.json student_profile.json
```

Open it and fill in your student's age, grade, reading level, interests, and anything a substitute
teacher would want to know ("gets frustrated by long blocks of text"). Claude reads this every time
it writes a week, and sizes the work to fit.

This file is gitignored — it describes a real child and never leaves your machine. If you skip this
step, Claude will simply ask you for the details the first time you generate a week.

### 2. Ask for a week

Open Claude Code in this directory and type:

```
/generate-week volcanoes
```

Then wait. It takes a few minutes, because it is genuinely writing the content — not assembling it
from templates. Behind the scenes it:

1. **Looks up real standards** for your student's grade and subject in `curriculum.db`
2. **Designs a five-day arc** where each day depends on the one before, ending in a Friday capstone
3. **Writes every passage and question itself**, with a recurring narrator character to hold a
   young student's attention across the week
4. **Emits two files** — the student packet and a teacher guide with a full answer key

### 3. Prompts worth stealing

`/generate-week <topic>` is the whole interface, but you get much better weeks by saying more.
Copy any of these and adapt:

| When you want to… | Say something like |
|---|---|
| Just get a week | `/generate-week volcanoes` |
| Aim at a specific kid | `/generate-week volcanoes for a 2nd grader who reads well but hates writing` |
| Target a weakness | `/generate-week fractions — she keeps missing word problems, lean on visual models` |
| Keep it hands-on | `/generate-week bugs — heavy on outdoor observation, light on worksheets` |
| Fix what came back | `Day 3 is too hard. Simpler vocabulary, then regenerate.` |
| Reuse a week that worked | `Take the weather week and redo it for a 4th grader.` |
| Decide what to teach next | `What science standards is a 1st grader supposed to hit? Suggest three themes.` |

The last one matters more than it looks: you can ask questions about the standards database in
plain English before committing to a topic.

### 4. Expect to iterate

The first version will not be perfect. Read the packet, then say what's wrong — "Tuesday's passage
is too long," "add a hands-on activity Thursday," "the word bank gives away the answers." It
regenerates in place. This is the normal workflow, not a sign something went wrong.

### Why the output is a *script*, not a document

Claude doesn't hand you a finished PDF. It writes `scripts/generate_volcanoes_week_series.py`,
a small program that produces the week.

That is deliberate, and it is the whole design:

- **Reproducible** — regenerate the identical packet a year from now, after you've lost the printout
- **Adjustable** — change one question without regenerating everything else
- **Reviewable** — a week is a code change, so you can see exactly what changed between versions
- **Shareable** — the script is a few dozen KB; the week it makes is not

Generated output is gitignored on purpose. **The script is the artifact.** Curated weeks worth
sharing get copied into [`examples/`](examples/).

---

## Track a student over time

> **This path requires an OpenAI API key.** Progress is recorded *against a generated weekly plan*,
> and generating those plans is the one feature that calls a paid API. Everything above is free.

The app learns what your student has and hasn't mastered, and feeds that into the next plan.

```bash
export OPENAI_API_KEY="sk-..."

# Terminal 1 — the API
cd src && ../venv/bin/uvicorn main:app --reload

# Terminal 2 — the web interface
cd frontend && npm install && npm run dev
```

Open <http://localhost:3000>.

**The loop:**

1. **Students** → add your student
2. **Plans** → generate a weekly plan for them
3. Teach the week
4. **Plans** → pick that plan → **Provide Feedback** → rate how well they grasped it, and whether
   the workload was too much or too little
5. Next week's plan adjusts — mastered standards move aside, shaky ones come back around, and the
   number of activities goes up or down to match

**Progress** shows a read-only map of where your student sits in the curriculum. It's a view, not
somewhere you enter data — step 4 is where progress gets recorded.

---

## What's in the box

### Weeks already written

Each is a tracked script you can run today, or hand to Claude as a starting point for a remix.

| Week | Grade | Subject | Format |
|---|---|---|---|
| `generate_weather_week_series.py` | K–1 | Science | Printable packet + teacher guide |
| `generate_data_week_series.py` | 1–2 | Science + Data & Graphing | Printable packet + teacher guide |
| `generate_biomes_week_series.py` | 1 | Science | PNG/PDF worksheets |
| `generate_math_week_series.py` | K–1 | Mathematics | PNG/PDF worksheets |
| `generate_motion_week_series.py` | K–1 | Science | PNG/PDF worksheets |

Run any of them with `venv/bin/python scripts/<name>`. The first two are the current format;
the others predate it and emit individual image files instead of a single packet.

`scripts/` also holds earlier themed sets (Minecraft, Star Wars, phonics, farm animals, and more)
from before the generator skill existed. They still run — they just don't follow the current
structure.

### Worksheet types

Twenty types are available; ten can appear in a printable packet — reading comprehension, feature
matrix, tree map, odd-one-out, matching, cause & effect, Frayer model, word sort, writing scaffold,
and T-chart. The rest (handwriting, pixel art, alphabet tracing, number lines, Venn diagrams,
sequencing, story maps, labeled diagrams, fill-in-the-blank, two-operand math) render as images.

Full table with technical details: [`AGENTS.md` §3](AGENTS.md#3-supported-worksheet-types).

---

## Going deeper

| Document | What's in it |
|---|---|
| [`examples/`](examples/) | Curated, printable sample weeks |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Development setup, tests, Docker, code style, PR workflow |
| [`AGENTS.md`](AGENTS.md) | Worksheet types, pedagogy patterns, renderer internals |
| [`docs/WORKSHEET_PEDAGOGY.md`](docs/WORKSHEET_PEDAGOGY.md) | The teaching principles behind the worksheet designs |
| [`api_reference.yaml`](api_reference.yaml) | Full OpenAPI spec (also live at `/docs` when the server runs) |
| [`CLAUDE.md`](CLAUDE.md) | Conventions Claude Code follows in this repo |

---

## Troubleshooting

**`ModuleNotFoundError` or a Pillow build failure during install** — your Python is too new. Check
with `python3 --version`; if it's 3.14+, use the `uv venv --python 3.12` line above.

**`/generate-week` can't find standards** — you skipped `venv/bin/python src/ingest_standards.py`.
Run it; it takes a few seconds and creates `curriculum.db`.

**A generator script fails with `No HTML renderer for kind=...`** — the week references a worksheet
type that can't be printed in a packet. Tell Claude Code the error and it will swap the type.

**The web app shows no students** — `curriculum.db` seeds one sample student. If you deleted it,
re-run `ingest_standards.py`, or add a student through the **Students** page.
