import { readFileSync, existsSync } from 'fs';

const PID_FILE = '/tmp/playwright-backend.pid';

export default async function globalTeardown(): Promise<void> {
  if (!existsSync(PID_FILE)) return;
  const pid = parseInt(readFileSync(PID_FILE, 'utf-8').trim(), 10);
  if (!isNaN(pid)) {
    try {
      process.kill(pid, 'SIGTERM');
    } catch {
      // process may have already exited
    }
  }
}
