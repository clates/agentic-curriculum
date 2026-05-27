import { spawn } from 'child_process';
import { writeFileSync } from 'fs';
import { resolve } from 'path';

const PID_FILE = '/tmp/playwright-backend.pid';
const DB_FILE = process.env.PLAYWRIGHT_DB_FILE ?? '/tmp/playwright-test.db';
const BACKEND_PORT = 8182;
const POLL_INTERVAL_MS = 500;
const MAX_WAIT_MS = 30_000;

async function waitForBackend(): Promise<void> {
  const deadline = Date.now() + MAX_WAIT_MS;
  while (Date.now() < deadline) {
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
  const uvicorn = spawn(
    `${projectRoot}/venv/bin/uvicorn`,
    ['src.main:app', '--port', String(BACKEND_PORT)],
    {
      cwd: projectRoot,
      env: { ...process.env, CURRICULUM_DB_PATH: DB_FILE },
      detached: true,
      stdio: 'ignore',
    }
  );

  uvicorn.unref();
  writeFileSync(PID_FILE, String(uvicorn.pid));
  await waitForBackend();
}
