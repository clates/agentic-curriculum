# Included weeks and worksheet types

## Weeks

Each week is a tracked script in `scripts/`. Run one with `venv/bin/python scripts/<name>`. Output
goes to `<theme>_week_series/` at the repo root, which git ignores.

| Script | Grade | Subject | Output |
|---|---|---|---|
| `generate_weather_week_series.py` | K–1 | Science | Printable packet and teacher guide |
| `generate_data_week_series.py` | 1–2 | Science, data and graphing | Printable packet and teacher guide |
| `generate_matter_week_series.py` | K–1 | Science | Printable packet and teacher guide |
| `generate_sky_week_series.py` | K–1 | Science | Printable packet and teacher guide |
| `generate_money_week_series.py` | K–1 | Math, social studies | Printable packet and teacher guide |
| `generate_game_theory_week_series.py` | 1–2 | Games, logic, math | Printable packet and teacher guide. Each day is built around a family game |
| `generate_test_taking_strategies_series.py` | K–1 | Study skills | Printable packet and teacher guide. Two days, not five |
| `generate_biomes_week_series.py` | 1 | Science | PNG and PDF worksheets |
| `generate_math_week_series.py` | K–1 | Mathematics | PNG and PDF worksheets |
| `generate_motion_week_series.py` | K–1 | Science | PNG and PDF worksheets |

The first seven use the current packet format and can be read without running anything in
[`examples/`](../../examples/). The last three are older: they write separate image files.

`scripts/` also holds earlier themed sets (Minecraft, Star Wars, phonics, farm animals and others)
written before `/generate-week` existed. They run, but don't follow the current structure.

## Worksheet types

| Can go in a printed packet | Image output only |
|---|---|
| reading comprehension, feature matrix, tree map, odd-one-out, matching, cause and effect, Frayer model, word sort, writing scaffold, T-chart | handwriting, pixel art, alphabet tracing, number lines, Venn diagrams, sequencing, story maps, labeled diagrams, fill-in-the-blank, two-operand math |

Fields and renderers for each type: [`AGENTS.md` §3](../../AGENTS.md#3-supported-worksheet-types)
and [Worksheet types](worksheet-types.md).
