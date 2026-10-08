/**
 * Static, dependency-free stand-in for the OpenAI-compatible LLM API and the ntfy push endpoint.
 *
 * Why: E2E journeys must assert on known data, and no test may ever reach a real LLM (cost,
 * latency, nondeterminism) or the real ntfy topic. global-setup starts this server, then spawns
 * the backend with OPENAI_BASE_URL / NTFY_URL pinned to it.
 *
 * Endpoints (127.0.0.1 only):
 *   POST /v1/chat/completions   canned OpenAI chat-completion envelope; content from fixtures/
 *   POST /ntfy                  records a push notification
 *   GET  /__requests            recorded calls; optional ?student=ID&kind=scaffold|day|ntfy|...
 *   POST /__reset               clears the recorded calls
 *
 * Classification is by prompt content (see src/agent.py for the prompts):
 *   scaffold  "weekly lesson plan scaffold"                  -> fixtures/scaffold.json
 *   day       "Create a lesson plan for the following ..."   -> fixtures/day.json
 * Anything else -> HTTP 500 plus a logged error, never a guess. Specs fail on any such record.
 *
 * Attribution and scenarios ride in the student's `parent_notes` (they appear in every prompt):
 *   e2e-student:<id>                  tags the recorded call with the student id
 *   e2e-stub:broken-day=<Weekday>     that day's reply is invalid JSON (exercises the fallback)
 * See e2e/fixtures/api.ts createStudent().
 */
import { createServer } from 'node:http';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const PORT = Number(process.env.E2E_LLM_STUB_PORT ?? 8183);
const HOST = '127.0.0.1';
const FIXTURES = join(dirname(fileURLToPath(import.meta.url)), 'fixtures');
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
const EXPECTED_KEY_PREFIX = 'e2e-stub-';

const fixture = (name) => readFileSync(join(FIXTURES, name), 'utf8');
const render = (text, vars) =>
  text.replace(/\{\{(\w+)\}\}/g, (_, key) => (key in vars ? vars[key] : `{{${key}}}`));

let recorded = [];
let counter = 0;

function record(entry) {
  const full = { id: ++counter, at: new Date().toISOString(), ...entry };
  recorded.push(full);
  console.log(JSON.stringify(full));
  return full;
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

function sendJson(res, status, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(status, {
    'content-type': 'application/json',
    'content-length': Buffer.byteLength(body),
  });
  res.end(body);
}

function completion(model, content) {
  return {
    id: `chatcmpl-e2e-stub-${counter}`,
    object: 'chat.completion',
    created: Math.floor(Date.now() / 1000),
    model: model ?? 'e2e-stub',
    choices: [{ index: 0, message: { role: 'assistant', content }, finish_reason: 'stop' }],
    usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
  };
}

function describePrompt(prompt) {
  return {
    student: /e2e-student:([\w-]+)/.exec(prompt)?.[1] ?? null,
    subject: /^Subject: (.+)$/m.exec(prompt)?.[1]?.trim() ?? null,
    grade: /^Grade Level: (\d+)/m.exec(prompt)?.[1] ?? null,
    brokenDay: /e2e-stub:broken-day=(\w+)/.exec(prompt)?.[1] ?? null,
  };
}

function scaffoldReply(prompt, meta) {
  const listText =
    /Available Standards \(may use 1 or more\):\n([\s\S]*?)\n\nParent Constraints/.exec(
      prompt
    )?.[1];
  const standards = JSON.parse(listText ?? 'null');
  if (!Array.isArray(standards) || standards.length === 0) {
    throw new Error('scaffold prompt had no parseable standards list');
  }
  const template = JSON.parse(fixture('scaffold.json'));
  const vars = { subject: meta.subject ?? 'Unknown', grade: meta.grade ?? '?' };
  return {
    weekly_overview: render(template.weekly_overview, vars),
    daily_assignments: DAYS.map((day, i) => ({
      day,
      standard_ids: [standards[i % standards.length].id],
      focus: render(template.focus[day], vars),
    })),
  };
}

function dayReply(prompt, meta) {
  const day = /Day Focus: Stub (\w+) focus/.exec(prompt)?.[1];
  if (!DAYS.includes(day)) throw new Error('day prompt had no "Day Focus: Stub <Weekday> focus"');
  const vars = { day, subject: meta.subject ?? 'Unknown', grade: meta.grade ?? '?' };
  if (meta.brokenDay === day)
    return { day, raw: render(fixture('invalid-day.txt'), vars), scenario: 'broken-day' };
  return { day, raw: render(fixture('day.json'), vars), scenario: null };
}

async function handleChat(req, res) {
  const auth = req.headers.authorization ?? '';
  const key = auth.replace(/^Bearer\s+/i, '');
  if (!key.startsWith(EXPECTED_KEY_PREFIX)) {
    // A real-looking key reached the stub: the backend env pinning is broken. Never echo the key.
    record({ kind: 'bad-auth', note: 'API key did not look like the E2E stub key' });
    console.error('E2E STUB ERROR: unexpected API key presented to the stub');
    return sendJson(res, 401, {
      error: { message: 'e2e stub: unexpected API key', type: 'e2e_stub_bad_auth' },
    });
  }

  let body;
  try {
    body = JSON.parse(await readBody(req));
  } catch {
    record({ kind: 'unrecognised', note: 'request body was not JSON' });
    return sendJson(res, 500, {
      error: { message: 'e2e stub: body was not JSON', type: 'e2e_stub_unrecognised_request' },
    });
  }

  const prompt = (body.messages ?? []).map((m) => String(m.content ?? '')).join('\n');
  const meta = describePrompt(prompt);

  try {
    if (prompt.includes('weekly lesson plan scaffold')) {
      const reply = scaffoldReply(prompt, meta);
      record({ kind: 'scaffold', student: meta.student, subject: meta.subject, grade: meta.grade });
      return sendJson(res, 200, completion(body.model, JSON.stringify(reply)));
    }
    if (prompt.includes('Create a lesson plan for the following educational standard')) {
      const { day, raw, scenario } = dayReply(prompt, meta);
      record({
        kind: 'day',
        student: meta.student,
        subject: meta.subject,
        grade: meta.grade,
        day,
        scenario,
      });
      return sendJson(res, 200, completion(body.model, raw));
    }
    throw new Error('prompt matched no known request type');
  } catch (err) {
    const message = `e2e stub: unrecognised request: ${err.message}`;
    record({ kind: 'unrecognised', note: err.message, promptHead: prompt.slice(0, 200) });
    console.error(`E2E STUB ERROR: ${message}`);
    return sendJson(res, 500, { error: { message, type: 'e2e_stub_unrecognised_request' } });
  }
}

async function handleNtfy(req, res) {
  const message = await readBody(req);
  record({
    kind: 'ntfy',
    title: req.headers.title ?? null,
    priority: req.headers.priority ?? null,
    message,
  });
  sendJson(res, 200, { id: `e2e-stub-${counter}`, event: 'message' });
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url ?? '/', `http://${HOST}`);
  try {
    if (req.method === 'POST' && url.pathname === '/v1/chat/completions')
      return await handleChat(req, res);
    if (req.method === 'POST' && url.pathname === '/ntfy') return await handleNtfy(req, res);
    if (req.method === 'GET' && url.pathname === '/__requests') {
      const student = url.searchParams.get('student');
      const kind = url.searchParams.get('kind');
      const requests = recorded.filter(
        (r) => (!student || r.student === student) && (!kind || r.kind === kind)
      );
      return sendJson(res, 200, { requests });
    }
    if (req.method === 'POST' && url.pathname === '/__reset') {
      recorded = [];
      return sendJson(res, 200, { ok: true });
    }
    record({ kind: 'unrecognised', note: `${req.method} ${url.pathname}` });
    console.error(`E2E STUB ERROR: unrecognised route ${req.method} ${url.pathname}`);
    return sendJson(res, 500, {
      error: {
        message: `e2e stub: no route for ${req.method} ${url.pathname}`,
        type: 'e2e_stub_unrecognised_request',
      },
    });
  } catch (err) {
    console.error('E2E STUB ERROR', err);
    return sendJson(res, 500, { error: { message: String(err), type: 'e2e_stub_internal' } });
  }
});

server.listen(PORT, HOST, () => console.log(`e2e llm stub listening on http://${HOST}:${PORT}`));
for (const sig of ['SIGTERM', 'SIGINT']) process.on(sig, () => server.close(() => process.exit(0)));
