# Fix common problems

## Install fails with `ModuleNotFoundError` or a build error

Your Python is probably older than 3.12. Check it with `python3 --version`. If it is, recreate the
environment with a version `uv` downloads for you:

```bash
rm -rf venv && uv venv --python 3.15 --seed venv && venv/bin/pip install -r requirements.txt
```

## `/generate-week` can't find standards

The standards database is missing. Build it (it takes a few seconds):

```bash
venv/bin/python src/ingest_standards.py
```

## A generator script fails with `No HTML renderer for kind=...`

The week uses a worksheet type that can't go in a printed packet. Paste the error into Claude Code
and ask it to swap the type. To see which types can be printed, check
[Worksheet types](../reference/included-weeks.md#worksheet-types).

## The web app shows no students

The sample student was deleted. Run `venv/bin/python src/ingest_standards.py` again, or add a
student on the **Students** page.
