import { APIRequestContext } from '@playwright/test';
import { execFileSync } from 'child_process';
import { resolve } from 'path';

const BACKEND = process.env.BACKEND_URL ?? 'http://localhost:8182';
const DB_FILE = process.env.PLAYWRIGHT_DB_FILE ?? '/tmp/playwright-test.db';
const PROJECT_ROOT = resolve(__dirname, '../../..');

function seedScript(cmd: string, ...args: string[]): void {
  try {
    execFileSync(
      `${PROJECT_ROOT}/venv/bin/python`,
      [`${PROJECT_ROOT}/scripts/e2e_seed.py`, cmd, ...args],
      {
        stdio: 'pipe',
        env: { ...process.env, CURRICULUM_DB_PATH: DB_FILE },
      }
    );
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    throw new Error(`seedScript "${cmd}" failed: ${msg}`);
  }
}

export async function createStudent(
  request: APIRequestContext,
  id: string,
  opts: { name: string; birthday: string }
): Promise<void> {
  const res = await request.post(`${BACKEND}/students`, {
    data: {
      student_id: id,
      metadata: { name: opts.name, birthday: opts.birthday },
    },
  });
  if (!res.ok()) {
    throw new Error(`createStudent failed: ${res.status()} ${await res.text()}`);
  }
}

export async function createPacket(
  _request: APIRequestContext,
  studentId: string,
  packetId: string
): Promise<{ packet_id: string }> {
  // Packet creation requires DB-level seeding because the HTTP endpoint
  // does not accept pre-formed packet IDs; use e2e_seed.py directly.
  seedScript('create_packet', studentId, packetId);
  return { packet_id: packetId };
}

export async function submitFeedback(
  request: APIRequestContext,
  studentId: string,
  packetId: string,
  ratings: { mastery: string; quantity: number }
): Promise<void> {
  const res = await request.post(
    `${BACKEND}/students/${studentId}/weekly-packets/${packetId}/feedback`,
    {
      data: {
        mastery_feedback: { overall: ratings.mastery },
        quantity_feedback: ratings.quantity,
      },
    }
  );
  if (!res.ok()) {
    throw new Error(`submitFeedback failed: ${res.status()} ${await res.text()}`);
  }
}

export function backdateFeedback(packetId: string, isoTimestamp: string): void {
  seedScript('backdate_feedback', packetId, isoTimestamp);
}
