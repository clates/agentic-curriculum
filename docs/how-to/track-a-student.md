# Track a student over time in the web app

This guide shows you how to run the web app on your own computer, so it can record what your
student mastered and adjust each new plan. Generating plans calls a paid model API, so you need an
OpenRouter API key. An `OPENAI_API_KEY` for any OpenAI-compatible service also works.

You also need Node.js and the project set up as in
[Your first week](../tutorials/your-first-week.md), steps 1 to 3.

## Start it

```bash
export OPENROUTER_API_KEY="sk-or-..."   # every option is listed in .env.example

# Terminal 1: the API
cd src && ../venv/bin/uvicorn main:app --reload

# Terminal 2: the web interface
cd frontend && npm install && npm run dev
```

Open <http://localhost:3000>.

## Run one week

1. Under **Students**, add your student.
2. Under **Plans**, generate a weekly plan for them.
3. Teach the week.
4. Under **Plans**, open that plan and choose **Provide Feedback**. Rate how well they grasped it,
   and say whether the workload was too much or too little.

The next plan uses that feedback. To see where the student stands, open **Progress**. It only
shows data; feedback in step 4 is the only place progress is recorded.

## If the student list is empty

`curriculum.db` seeds one sample student. If you deleted it, run
`venv/bin/python src/ingest_standards.py` again or add a student under **Students**.

Related: [The weekly loop](../explanation/the-weekly-loop.md) describes how the hosted app runs
these steps on a schedule.
