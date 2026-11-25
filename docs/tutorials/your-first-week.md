# Your first week

In this tutorial we will install the project, print a science week that is already written, and
then have Claude Code write a new week on volcanoes. It takes about twenty minutes, most of it
waiting for the volcano week.

You need a Mac or Linux terminal, `git`, [`uv`](https://docs.astral.sh/uv/) and
[Claude Code](https://claude.com/claude-code). No API key is needed.

## 1. Get the code

```bash
git clone https://github.com/clates/agentic-curriculum.git
cd agentic-curriculum
```

## 2. Install it

```bash
uv venv --python 3.15 --seed venv
venv/bin/pip install -r requirements.txt
```

The last line it prints starts with `Successfully installed`.

## 3. Build the standards database

```bash
venv/bin/python src/ingest_standards.py
```

There is now a file called `curriculum.db` in the folder:

```bash
ls curriculum.db
```

## 4. Print a week that is already written

```bash
venv/bin/python scripts/generate_weather_week_series.py
open weather_week_series/weather_week.html      # on Linux: xdg-open
```

A browser opens on Monday's page of a kindergarten-to-first-grade weather week, and the print
dialog appears. Cancel it for now and scroll: there are five days. Notice the character who
narrates every day. Their story carries the child from Monday to Friday.

Now open the teacher guide next to it:

```bash
open weather_week_series/weather_week_teacher_guide.html
```

It has the answers, a discussion question for each day and the mistakes children commonly make.

## 5. Describe your student

```bash
cp student_profile.example.json student_profile.json
```

Open `student_profile.json` in any editor. Change the age, grade, reading level and interests to
match your student, and save it. This file never leaves your computer.

## 6. Ask Claude Code for a week

Start Claude Code in the same folder:

```bash
claude
```

Type:

```
/generate-week volcanoes
```

Claude looks up standards for your student's grade, plans five days and writes every passage and
question. This takes several minutes. When it finishes, Claude tells you the paths of two files:
the student packet and the teacher guide.

## 7. Look at your week

Open the student packet Claude named. It has the same shape as the weather week: five
days, a narrator, and a teacher guide with an answer key. This week was written for your student's
grade.

## 8. Change one thing

Back in Claude Code, type:

```
Make Tuesday's passage shorter.
```

Claude rewrites the week, and Tuesday is shorter. Reload the page in the browser to see it.

## What we did

We installed the project, built the standards database, printed a ready-made week, and had Claude
write and then change a new week for one particular child.

Next:

- [Get a better week from `/generate-week`](../how-to/write-a-better-week.md): prompts that work
- [Why a week is a script](../explanation/why-a-week-is-a-script.md): what Claude actually made
- [Included weeks](../reference/included-weeks.md): everything you can print today
