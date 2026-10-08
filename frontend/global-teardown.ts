import { readFileSync, existsSync } from 'fs';
import { STUB_PID_FILE } from './e2e/llm-stub/config';

const PID_FILES = ['/tmp/playwright-backend.pid', STUB_PID_FILE];

export default async function globalTeardown(): Promise<void> {
  for (const file of PID_FILES) {
    if (!existsSync(file)) continue;
    const pid = parseInt(readFileSync(file, 'utf-8').trim(), 10);
    if (!isNaN(pid)) {
      try {
        process.kill(pid, 'SIGTERM');
      } catch {
        // process may have already exited
      }
    }
  }
}
