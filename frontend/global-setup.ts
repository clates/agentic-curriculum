import { spawn, execSync } from 'child_process';
import { execFileSync } from 'child_process';
import { writeFileSync } from 'fs';
import { resolve } from 'path';

const PID_FILE = '/tmp/playwright-backend.pid';
const DB_FILE = process.env.PLAYWRIGHT_DB_FILE ?? '/tmp/playwright-test.db';
const BACKEND_PORT = 8182;
const POLL_INTERVAL_MS = 500;
const MAX_WAIT_MS = 30_000;

function killExistingBackend(): void {
  try {
    const pids = execSync(`lsof -ti:${BACKEND_PORT}`, { encoding: 'utf8' }).trim();
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

  killExistingBackend();

  execFileSync(
    `${projectRoot}/venv/bin/python`,
    [`${projectRoot}/scripts/e2e_seed.py`, 'init_db'],
    { stdio: 'pipe', env: { ...process.env, CURRICULUM_DB_PATH: DB_FILE } }
  );

  const uvicorn = spawn(
    `${projectRoot}/venv/bin/uvicorn`,
    ['main:app', '--port', String(BACKEND_PORT)],
    {
      cwd: `${projectRoot}/src`,
      env: { ...process.env, CURRICULUM_DB_PATH: DB_FILE },
      detached: true,
      stdio: 'ignore',
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
