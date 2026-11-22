/**
 * Helpers for the E2E hardening specs (print coverage, card destinations, recorded check-ins).
 * New file on purpose: other streams edit the shared fixtures in parallel.
 */
import type { APIRequestContext, Page } from '@playwright/test';
import { readFileSync } from 'fs';
import { resolve } from 'path';
import { BACKEND, createPacket, createStudent, seedPlan, seedWeek } from './api';
import { expect, test } from './test';
import { uniqueId } from './parent';

export interface WeekDocFixture {
  days: { day: string; worksheets: { id: string; kind: string; data: { title?: string } }[] }[];
  prep_checks: { id: string; day: string; prompt: string; pass_criteria: string }[];
}

/** The same weather_week WeekDoc that scripts/e2e_seed.py create_week stores. */
export const WEATHER_WEEK: WeekDocFixture = JSON.parse(
  readFileSync(resolve(__dirname, '../../../tests/fixtures/weekdoc/weather_week.json'), 'utf-8')
);

export const WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

export interface Child {
  id: string;
  /** Unique first name, so a card/chip can be found among every child in the shared database. */
  name: string;
  lastName: string;
  packetId: string;
}

/** A child with a unique first name and a fixed, recognisable last name. */
export async function newChild(
  request: APIRequestContext,
  prefix: string,
  opts: { packet?: 'none' | 'legacy' | 'week'; plan?: string } = {}
): Promise<Child> {
  const id = uniqueId(prefix);
  const name = `Kid${id.replace(/[^a-z0-9]/gi, '')}`;
  const lastName = 'Quillfeather';
  await createStudent(request, id, { name: `${name} ${lastName}`, birthday: '2018-03-04' });
  const packetId = `pk_${id}`;
  if (opts.packet === 'week') seedWeek(id, packetId);
  else if (opts.packet === 'legacy') await createPacket(request, id, packetId);
  if (opts.plan) seedPlan(id, opts.plan);
  return { id, name, lastName, packetId };
}

/** The feedback row the real API stored for a packet. */
export async function storedFeedback(
  request: APIRequestContext,
  studentId: string,
  packetId: string
): Promise<Record<string, unknown>> {
  const res = await request.get(
    `${BACKEND}/students/${studentId}/weekly-packets/${packetId}/feedback`
  );
  expect(res.ok(), 'feedback GET').toBeTruthy();
  return res.json();
}

/** The page must not scroll sideways. */
export async function expectNoHorizontalScroll(page: Page, label = 'page') {
  const { scrollWidth, clientWidth, wide } = await page.evaluate(() => {
    const clientWidth = document.documentElement.clientWidth;
    const wide = [...document.querySelectorAll('body *')]
      .map((e) => ({
        el: `${e.tagName.toLowerCase()}.${String(e.className).slice(0, 60)} "${(e.textContent ?? '').trim().slice(0, 30)}"`,
        right: Math.round(e.getBoundingClientRect().right),
      }))
      .filter((x) => x.right > clientWidth)
      .slice(0, 8);
    return { scrollWidth: document.documentElement.scrollWidth, clientWidth, wide };
  });
  // Name the elements that stick out, so a failure on another machine (different fonts) is diagnosable.
  expect(
    scrollWidth,
    `${label} scrolls sideways; past the edge: ${JSON.stringify(wide)}`
  ).toBeLessThanOrEqual(clientWidth);
}

/**
 * Identity for a journey's fixed student, unique per `--repeat-each` round.
 *
 * Journeys use fixed ids and names so their spec reads like a story. With `--repeat-each`, every
 * round shares one database, so state from round 1 (a generated week, a submitted feedback, a
 * renamed child, extra "pending" cards) breaks round 2. Round 0 keeps the original id and name, so
 * a normal run is unchanged; later rounds get their own child. Call from `beforeAll`.
 */
export function repeatIdentity(id: string, name: string): { id: string; name: string } {
  const round = test.info().repeatEachIndex;
  if (round === 0) return { id, name };
  return {
    id: `${id}_r${round}`, // valid for the edit form (lowercase letters, digits, underscores)
    name: name.replace(/Student$/, `Learner${String.fromCharCode(64 + round)}`),
  };
}

/**
 * Pick one child on How it's going. The radios are visually hidden and the screen may still be
 * hydrating, so a click can land before React listens: retry the click until the choice sticks.
 */
export async function chooseChild(page: Page, name: string) {
  const radio = page.getByRole('radio', { name, exact: true });
  await expect(radio).toBeAttached({ timeout: 20_000 });
  await expect(async () => {
    await page.locator('label', { has: radio }).click();
    await expect(radio).toBeChecked({ timeout: 1_000 });
  }).toPass({ timeout: 15_000 });
}
