/**
 * Helpers for the print screen specs (M10.7). New file on purpose: other streams edit the shared
 * fixtures in parallel. Seeds a child whose week plan points at a REAL stored week.
 */
import type { APIRequestContext } from '@playwright/test';
import { execFileSync } from 'child_process';
import { resolve } from 'path';
import { BACKEND, createStudent } from './api';
import { uniqueId } from './parent';
import type { Child } from './e2e-hardening';

const DB_FILE = process.env.PLAYWRIGHT_DB_FILE ?? '/tmp/playwright-test.db';
const ROOT = resolve(__dirname, '../../..');

export interface PrintChild extends Child {
  planId: string;
}

/**
 * A child with a plan walked to `status` (default `ready`) whose finished week is stored.
 * `structured` has all three documents; `legacy` is an older packet with only the pages.
 * The plan's week is far in the future so it is always the child's latest plan: Monday
 * 2099-01-05 to Friday 2099-01-09.
 */
export async function printChild(
  request: APIRequestContext,
  prefix: string,
  opts: {
    kind?: 'structured' | 'legacy';
    status?: string;
    printDeadline?: string;
  } = {}
): Promise<PrintChild> {
  const id = uniqueId(prefix);
  const name = `Kid${id.replace(/[^a-z0-9]/gi, '')}`;
  const lastName = 'Quillfeather';
  await createStudent(request, id, { name: `${name} ${lastName}`, birthday: '2018-03-04' });
  const packetId = `pk_${id}`;
  const out = execFileSync(
    `${ROOT}/venv/bin/python`,
    [
      `${ROOT}/scripts/e2e_seed_print.py`,
      'week',
      id,
      packetId,
      opts.kind ?? 'structured',
      opts.status ?? 'ready',
      '2099-01-05',
      opts.printDeadline ?? '',
    ],
    { env: { ...process.env, CURRICULUM_DB_PATH: DB_FILE }, encoding: 'utf-8', stdio: 'pipe' }
  );
  const planId = out.trim().split('\n').pop()!;
  return { id, name, lastName, packetId, planId };
}

/** What the real API says this child's card is (`print`, `done`, ...). */
export async function nextActionOf(request: APIRequestContext, studentId: string) {
  const res = await request.get(`${BACKEND}/this-week`);
  const body = await res.json();
  return body.children.find((c: { student_id: string }) => c.student_id === studentId)
    ?.next_action as string | undefined;
}
