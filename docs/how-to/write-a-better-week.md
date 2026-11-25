# Get a better week from `/generate-week`

This guide shows you how to steer Claude Code toward a week that fits your student, and how to fix
a week that came back wrong. It assumes the project is installed. If it isn't, follow
[Your first week](../tutorials/your-first-week.md) first.

## Describe the student once

Copy `student_profile.example.json` to `student_profile.json` and fill it in. Write the notes as
you would for a substitute teacher, for example "gets frustrated by long blocks of text". Claude
reads this file every time it writes a week. If the file is missing, Claude asks for the details
and writes the file itself.

## Say more than the topic

`/generate-week <topic>` works on its own, but a sentence of intent gives a better week:

| When you want to… | Say something like |
|---|---|
| Just get a week | `/generate-week volcanoes` |
| Aim at a specific kid | `/generate-week volcanoes for a 2nd grader who reads well but hates writing` |
| Target a weakness | `/generate-week fractions — she keeps missing word problems, lean on visual models` |
| Keep it hands-on | `/generate-week bugs — heavy on outdoor observation, light on worksheets` |
| Reuse a week that worked | `Take the weather week and redo it for a 4th grader.` |

## Choose a topic from the standards

If you don't know what to teach next, ask before you pick a topic:

```
What science standards is a 1st grader supposed to hit? Suggest three themes.
```

Claude answers from `curriculum.db`, the same standards it aligns the week to.

## Fix what came back

Read the packet, then name the problem in one sentence. Claude rewrites the week in place.

- `Day 3 is too hard. Simpler vocabulary, then regenerate.`
- `Tuesday's passage is too long.`
- `Add a hands-on activity on Thursday.`
- `The word bank gives away the answers.`

Two or three rounds is normal.

## Keep a week worth sharing

Copy its output into `examples/<theme>-week/`, with a hyphen and not an underscore, and commit it
together with its script. See [`examples/README.md`](../../examples/README.md).

Related:

- [Why a week is a script](../explanation/why-a-week-is-a-script.md)
- [Worksheet types](../reference/included-weeks.md#worksheet-types)
