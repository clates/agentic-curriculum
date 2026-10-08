import { spawn, execSync } from 'child_process';
import { execFileSync } from 'child_process';
import { openSync, writeFileSync } from 'fs';
import { resolve } from 'path';
import { STUB_BASE_URL, STUB_LOG_FILE, STUB_PID_FILE, STUB_PORT } from './e2e/llm-stub/config';

const PID_FILE = '/tmp/playwright-backend.pid';
const DB_FILE = process.env.PLAYWRIGHT_DB_FILE ?? '/tmp/playwright-test.db';
const BACKEND_PORT = 8182;
const POLL_INTERVAL_MS = 500;
const MAX_WAIT_MS = 30_000;

function killOnPort(port: number): void {
  try {
    const pids = execSync(`lsof -ti:${port}`, { encoding: 'utf8' }).trim();
    if (pids) {
      pids.split('\n').forEach((pid) => {
        try {
          execSync(`kill ${pid.trim()}`);
        } catch {
          /* already gone */
        }
      });
      // Wait briefly for port to free up
      execSync(`sleep 1`);
    }
  } catch {
    // No process on port, nothing to kill
  }
}

/** Start the static LLM/ntfy stub (127.0.0.1 only) and wait until it answers. */
async function startLlmStub(): Promise<void> {
  killOnPort(STUB_PORT);
  const log = openSync(STUB_LOG_FILE, 'w');
  const stub = spawn(process.execPath, [resolve(__dirname, 'e2e/llm-stub/server.mjs')], {
    env: { ...process.env, E2E_LLM_STUB_PORT: String(STUB_PORT) },
    detached: true,
    stdio: ['ignore', log, log],
  });
  let spawnError: Error | null = null;
  stub.on('error', (err) => {
    spawnError = err;
  });
  const pid = stub.pid;
  stub.unref();

  const deadline = Date.now() + 10_000;
  while (Date.now() < deadline) {
    if (spawnError) throw new Error(`LLM stub failed to start: ${(spawnError as Error).message}`);
    try {
      const res = await fetch(`${STUB_BASE_URL}/__requests`);
      if (res.ok) {
        if (pid !== undefined) writeFileSync(STUB_PID_FILE, String(pid));
        return;
      }
    } catch {
      // not ready yet
    }
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error(`LLM stub did not start on port ${STUB_PORT} (see ${STUB_LOG_FILE})`);
}

async function waitForBackend(getSpawnError: () => Error | null): Promise<void> {
  const deadline = Date.now() + MAX_WAIT_MS;
  while (Date.now() < deadline) {
    const err = getSpawnError();
    if (err) throw new Error(`Backend failed to start: ${err.message}`);
    try {
      const res = await fetch(`http://localhost:${BACKEND_PORT}/`);
      if (res.ok) return;
    } catch {
      // not ready yet
    }
    await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
  }
  throw new Error(`Backend did not start within ${MAX_WAIT_MS}ms`);
}

export default async function globalSetup(): Promise<void> {
  const projectRoot = resolve(__dirname, '..');

  killOnPort(BACKEND_PORT);
  await startLlmStub();

  execFileSync(
    `${projectRoot}/venv/bin/python`,
    [`${projectRoot}/scripts/e2e_seed.py`, 'init_db'],
    { stdio: 'pipe', env: { ...process.env, CURRICULUM_DB_PATH: DB_FILE } }
  );

  const backendLog = openSync('/tmp/playwright-backend.log', 'w');
  const uvicorn = spawn(
    `${projectRoot}/venv/bin/uvicorn`,
    ['main:app', '--port', String(BACKEND_PORT)],
    {
      cwd: `${projectRoot}/src`,
      env: {
        ...process.env,
        CURRICULUM_DB_PATH: DB_FILE,
        // Hermetic by construction: these OVERRIDE anything inherited from the developer's shell
        // (a real OpenRouter/OpenAI key, the real ntfy topic). The backend can only reach the stub.
        OPENAI_BASE_URL: `${STUB_BASE_URL}/v1`,
        OPENAI_API_KEY: 'e2e-stub-not-a-real-key',
        OPENAI_MODEL: 'e2e-stub',
        NTFY_URL: `${STUB_BASE_URL}/ntfy`,
      },
      detached: true,
      stdio: ['ignore', backendLog, backendLog],
    }
  );

  let spawnError: Error | null = null;
  uvicorn.on('error', (err) => {
    spawnError = err;
  });

  const pid = uvicorn.pid;
  uvicorn.unref();
  await waitForBackend(() => spawnError);
  if (pid !== undefined) {
    writeFileSync(PID_FILE, String(pid));
  }
}
