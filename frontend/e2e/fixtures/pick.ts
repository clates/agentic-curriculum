/**
 * Helpers for the pick-one-of-three specs (M10.6). New file on purpose: other streams edit the
 * shared fixtures in parallel.
 */
import type { APIRequestContext, Page } from '@playwright/test';
import { execFileSync } from 'child_process';
import { resolve } from 'path';
import { STUB_BASE_URL } from '../llm-stub/config';
import { BACKEND, createStudent, seedPlan, seedProgress } from './api';
import { expect } from './test';
import { uniqueId } from './parent';

const PROJECT_ROOT = resolve(__dirname, '../../..');
const DB_FILE = process.env.PLAYWRIGHT_DB_FILE ?? '/tmp/playwright-test.db';

function seed(cmd: string, ...args: string[]): string {
  return execFileSync(
    `${PROJECT_ROOT}/venv/bin/python`,
    [`${PROJECT_ROOT}/scripts/e2e_seed.py`, cmd, ...args],
    { stdio: 'pipe', env: { ...process.env, CURRICULUM_DB_PATH: DB_FILE }, encoding: 'utf-8' }
  );
}

/** The three ideas scripts/e2e_seed.py create_plan writes, by option. */
export const SEEDED = {
  a: { title: 'Gentle Garden Week', effort: 'About 15 minutes a day' },
  b: { title: 'Kitchen Math Lab', effort: 'About 25 minutes a day' },
  c: { title: 'Backyard Detectives', effort: 'About 35 minutes a day' },
} as const;

/** The ideas the stub writes for a child's first generation (src outline.mjs, TITLES[0]). */
export const STUB_FIRST_TITLES = ['Number Detectives', 'Garden Scientists', 'Story Builders'];

export interface PickChild {
  id: string;
  /** Unique first name, so the card can be found among every child in the shared database. */
  name: string;
  lastName: string;
}

export type OutlineScenario = 'repair' | 'fail-once' | 'slow';

/** A child (born 2018, so about third grade) whose week plan is already in `status`. */
export async function pickChild(
  request: APIRequestContext,
  prefix: string,
  opts: { status: string; scenario?: OutlineScenario; progress?: boolean }
): Promise<PickChild> {
  const id = uniqueId(prefix);
  const name = `Kid${id.replace(/[^a-z0-9]/gi, '')}`;
  const lastName = 'Quillfeather';
  await createStudent(request, id, {
    name: `${name} ${lastName}`,
    birthday: '2018-03-04',
    stubScenario: opts.scenario ? `outline=${opts.scenario}` : undefined,
  });
  if (opts.progress) seedProgress(id);
  seedPlan(id, opts.status);
  return { id, name, lastName };
}

export interface PlanApi {
  plan_id: string;
  first_name: string;
  status: string;
  picked_option: string | null;
  outlines: { option_id: string; title: string; hook: string; skills: string[] }[] | null;
  regenerations_used: number;
  regenerations_left: number;
}

/** The week plan exactly as the real API reports it. */
export async function planOf(request: APIRequestContext, id: string): Promise<PlanApi> {
  const res = await request.get(`${BACKEND}/students/${id}/week-plan`);
  expect(res.ok(), 'week-plan GET').toBeTruthy();
  return res.json();
}

export function expirePlan(id: string): void {
  seed('expire_plan', id);
}

export interface LoopEvent {
  type: string;
  from: string;
  to: string;
  payload: Record<string, string>;
  key: string | null;
}

/** The loop events the backend recorded for the child's current plan. */
export function loopEvents(id: string): LoopEvent[] {
  return JSON.parse(seed('loop_events', id)) as LoopEvent[];
}

export interface OutlineCall {
  kind: 'outline' | 'outline-repair';
  scenario: string | null;
}

/** Outline calls (and repairs) the stub saw for one child. */
export async function outlineCalls(
  request: APIRequestContext,
  studentId: string
): Promise<OutlineCall[]> {
  const res = await request.get(`${STUB_BASE_URL}/__requests?student=${studentId}`);
  const all = (await res.json()).requests as OutlineCall[];
  return all.filter((c) => c.kind === 'outline' || c.kind === 'outline-repair');
}

/** The three idea cards on the pick screen. */
export const ideaCards = (page: Page) => page.locator('[data-testid="idea-card"]');

/** Press Tab until `selector` has focus (a real keyboard path, bounded). */
export async function tabTo(page: Page, selector: string, max = 25) {
  for (let i = 0; i < max; i++) {
    if (await page.evaluate((s) => document.activeElement?.matches(s) ?? false, selector)) return;
    await page.keyboard.press('Tab');
  }
  throw new Error(`Tab never reached ${selector}`);
}

/** The error box on screen (Next's empty route announcer also has role=alert; skip it). */
export const errorBox = (page: Page) => page.getByRole('alert').filter({ hasText: /\S/ });
