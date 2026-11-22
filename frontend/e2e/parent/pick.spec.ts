/**
 * M10.6: pick one of three ideas for next week. Real API and the static LLM stub throughout
 * (the stub writes the outlines for "fresh ideas"); nothing about the loop is mocked except where
 * a spec says so to force a failure.
 *
 * What these prove beyond "the screen renders": the choice is recorded by the backend (loop state
 * and the stored option), a double tap sends one request, an expired set can be replaced within a
 * cap, and a failed model call leaves the week as it was.
 */
import { test, expect } from '../fixtures/test';
import { expectNoBannedWords, expectNoViolations } from '../fixtures/parent';
import { expectNoHorizontalScroll } from '../fixtures/e2e-hardening';
import { shot } from '../fixtures/shots';
import { BACKEND } from '../fixtures/api';
import {
  SEEDED,
  STUB_FIRST_TITLES,
  errorBox,
  expirePlan,
  ideaCards,
  loopEvents,
  outlineCalls,
  pickChild,
  planOf,
  tabTo,
} from '../fixtures/pick';

const PICK_URL = '**/api/students/*/week-plan/pick';

async function openPick(page: import('@playwright/test').Page, id: string, name: string) {
  await page.goto(`/week/pick/${id}`);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(`Pick ${name}’s next week`, {
    timeout: 20_000,
  });
}

/** Click "Use this one" and wait for the confirm step (the click is retried until hydrated). */
async function openConfirm(page: import('@playwright/test').Page) {
  await expect(async () => {
    await page.getByRole('button', { name: 'Use this one' }).click();
    await expect(page.getByRole('button', { name: 'Yes, use this one' })).toBeVisible({
      timeout: 1_000,
    });
  }).toPass({ timeout: 15_000 });
}

test.describe('Pick one of three: the happy path', () => {
  test('from This week to the writing state, recorded by the backend', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'pk', { status: 'awaiting_pick' });

    // 1. This week offers the ideas.
    await page.goto('/week');
    const card = page.locator('[data-testid="child-card"]', { hasText: kid.name });
    await expect(card).toHaveAttribute('data-next-action', 'pick', { timeout: 20_000 });
    await card.getByRole('link', { name: 'See the ideas' }).click();
    await expect(page).toHaveURL(new RegExp(`/week/pick/${kid.id}$`), { timeout: 30_000 });

    // 2. Three ideas, each with its hook and effort; first name only; nothing technical.
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(
      `Pick ${kid.name}’s next week`
    );
    await expect(ideaCards(page)).toHaveCount(3);
    for (const idea of Object.values(SEEDED)) {
      const c = ideaCards(page).filter({ hasText: idea.title });
      await expect(c).toHaveCount(1);
      await expect(c).toContainText(idea.effort);
    }
    await expect(ideaCards(page).filter({ hasText: 'Plant, count and sketch' })).toBeVisible();
    await expect(page.locator('body')).not.toContainText(kid.lastName);
    await expect(page.locator('body')).not.toContainText('VA.MATH');
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-ideas');

    // 3. One clear default (our pick, on level); choose a different one instead.
    await expect(page.getByRole('radio', { name: /Kitchen Math Lab/ })).toBeChecked();
    await expect(ideaCards(page).filter({ hasText: 'Our pick' })).toHaveCount(1);
    await ideaCards(page).filter({ hasText: SEEDED.c.title }).click();
    await expect(page.getByRole('radio', { name: /Backyard Detectives/ })).toBeChecked();

    // 4. Confirm step names the choice and what it covers; nothing is sent yet.
    let posts = 0;
    await page.route(PICK_URL, (route) => {
      posts += 1;
      return route.continue();
    });
    await openConfirm(page);
    await expect(page.getByRole('heading', { name: 'Use “Backyard Detectives”?' })).toBeFocused();
    await expect(page.getByText('Counting and measuring')).toBeVisible();
    await expect(page.getByText('Once we start, it can’t be changed.')).toBeVisible();
    expect(posts).toBe(0);
    expect((await planOf(request, kid.id)).status).toBe('awaiting_pick');
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-confirm');

    // 5. Confirm: exactly one request with the chosen option, then back to This week, writing.
    const sent = page.waitForRequest((r) => r.method() === 'POST' && r.url().includes('/pick'));
    await page.getByRole('button', { name: 'Yes, use this one' }).click();
    const body = (await sent).postDataJSON();
    const before = await planOf(request, kid.id);
    expect(body).toEqual({ option: 'c', plan_id: before.plan_id });
    await expect(page).toHaveURL(/\/week$/, { timeout: 30_000 });
    const after = page.locator('[data-testid="child-card"]', { hasText: kid.name });
    await expect(after).toHaveAttribute('data-next-action', 'writing');
    await expect(after.getByRole('heading', { level: 2 })).toHaveText(
      `Writing ${kid.name}’s next week`
    );
    await expect(after.getByRole('link')).toHaveCount(0);
    await shot(page, 'm10-6-writing');
    expect(posts).toBe(1);

    // 6. The backend agrees: the loop moved on and the choice is recorded.
    const plan = await planOf(request, kid.id);
    expect(plan.status).toBe('authoring');
    expect(plan.picked_option).toBe('c');
    const events = loopEvents(kid.id).filter((e) => e.type === 'pick_made');
    expect(events).toHaveLength(1);
    expect(events[0]).toMatchObject({
      from: 'awaiting_pick',
      to: 'authoring',
      payload: { option_id: 'c' },
    });

    // 7. It stays that way after a reload.
    await page.reload();
    await expect(page.locator('[data-testid="child-card"]', { hasText: kid.name })).toHaveAttribute(
      'data-next-action',
      'writing',
      { timeout: 20_000 }
    );
  });

  test('"Back to the ideas" leaves the confirm step and sends nothing', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'pb', { status: 'awaiting_pick' });
    await openPick(page, kid.id, kid.name);
    await expect(ideaCards(page)).toHaveCount(3);
    await openConfirm(page);
    await page.getByRole('button', { name: 'Back to the ideas' }).click();
    await expect(ideaCards(page)).toHaveCount(3);
    expect((await planOf(request, kid.id)).status).toBe('awaiting_pick');
  });
});

test.describe('Pick one of three: a double tap and a repeat do not double-submit', () => {
  test('tapping Yes twice quickly sends one request', async ({ page, request }) => {
    const kid = await pickChild(request, 'pd', { status: 'awaiting_pick' });
    let posts = 0;
    await page.route(PICK_URL, async (route) => {
      posts += 1;
      await new Promise((r) => setTimeout(r, 500)); // keep the first one in flight
      await route.continue();
    });
    await openPick(page, kid.id, kid.name);
    await openConfirm(page);
    await page.getByRole('button', { name: 'Yes, use this one' }).dblclick();
    await expect(page).toHaveURL(/\/week$/, { timeout: 30_000 });
    expect(posts).toBe(1);
    const plan = await planOf(request, kid.id);
    expect(plan.picked_option).toBe('b');
    expect(loopEvents(kid.id).filter((e) => e.type === 'pick_made')).toHaveLength(1);
  });

  test('the API: the same pick twice is a no-op; a different pick afterwards is a clear 409', async ({
    request,
  }) => {
    const kid = await pickChild(request, 'pa', { status: 'awaiting_pick' });
    const { plan_id } = await planOf(request, kid.id);
    const url = `${BACKEND}/students/${kid.id}/week-plan/pick`;

    const first = await request.post(url, { data: { option: 'a', plan_id } });
    expect(first.status()).toBe(200);
    expect((await first.json()).already_picked).toBe(false);

    const again = await request.post(url, { data: { option: 'a', plan_id } });
    expect(again.status()).toBe(200);
    expect((await again.json()).already_picked).toBe(true);
    expect(loopEvents(kid.id).filter((e) => e.type === 'pick_made')).toHaveLength(1);

    const other = await request.post(url, { data: { option: 'c', plan_id } });
    expect(other.status()).toBe(409);
    const detail = (await other.json()).detail;
    expect(detail.code).toBe('already_picked');
    expect(detail.message).toContain('already chose');
    const plan = await planOf(request, kid.id);
    expect(plan).toMatchObject({ status: 'authoring', picked_option: 'a' });

    expect((await request.post(url, { data: { option: 'z' } })).status()).toBe(422);
    const stale = await request.post(`${BACKEND}/students/${kid.id}/week-plan/pick`, {
      data: { option: 'a', plan_id: 'wp_not_this_one' },
    });
    expect(stale.status()).toBe(409);
  });

  test('a choice made on another device is explained, not overwritten', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'px', { status: 'awaiting_pick' });
    await openPick(page, kid.id, kid.name);
    await ideaCards(page).filter({ hasText: SEEDED.c.title }).click();
    await openConfirm(page);
    // Meanwhile, someone else picks a different one.
    const { plan_id } = await planOf(request, kid.id);
    await request.post(`${BACKEND}/students/${kid.id}/week-plan/pick`, {
      data: { option: 'a', plan_id },
    });
    await page.getByRole('button', { name: 'Yes, use this one' }).click();
    await expect(errorBox(page)).toContainText('You already chose');
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    expect((await planOf(request, kid.id)).picked_option).toBe('a');
  });
});

test.describe('Expired ideas: fresh ideas', () => {
  test('expired -> "Get fresh ideas" -> new ideas -> pick one', async ({ page, request }) => {
    const kid = await pickChild(request, 'ex', { status: 'expired', progress: true });
    await page.goto('/week');
    const card = page.locator('[data-testid="child-card"]', { hasText: kid.name });
    await expect(card).toHaveAttribute('data-next-action', 'pick', { timeout: 20_000 });
    await card.getByRole('link', { name: 'Get fresh ideas' }).click();
    await expect(page).toHaveURL(new RegExp(`/week/pick/${kid.id}$`), { timeout: 30_000 });
    await expect(page.getByText('Those ideas ran out of time.')).toBeVisible();
    await expect(ideaCards(page)).toHaveCount(0);
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-expired');

    await page.getByRole('button', { name: 'Get fresh ideas' }).click();
    await expect(ideaCards(page).first()).toBeVisible({ timeout: 30_000 });

    // New ideas, written by the model call, not the seeded ones.
    await expect(ideaCards(page)).toHaveCount(3);
    for (const title of STUB_FIRST_TITLES)
      await expect(ideaCards(page).filter({ hasText: title })).toHaveCount(1);
    for (const old of Object.values(SEEDED)) {
      await expect(page.getByText(old.title)).toHaveCount(0);
    }
    await expect(page.locator('body')).not.toContainText(/VA\.[A-Z]+\./);
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-fresh-ideas');

    const plan = await planOf(request, kid.id);
    expect(plan.status).toBe('awaiting_pick');
    expect(plan.regenerations_used).toBe(1);
    expect(plan.outlines?.map((o) => o.title)).toEqual(STUB_FIRST_TITLES);
    expect((await outlineCalls(request, kid.id)).map((c) => c.kind)).toEqual(['outline']);
    expect(loopEvents(kid.id).map((e) => e.type)).toEqual([
      'feedback_submitted',
      'outlines_ready',
      'pick_expired',
      'outlines_regenerate',
      'outlines_ready',
    ]);

    // And the new set can be picked.
    await openConfirm(page);
    await page.getByRole('button', { name: 'Yes, use this one' }).click();
    await expect(page).toHaveURL(/\/week$/, { timeout: 30_000 });
    await expect(page.locator('[data-testid="child-card"]', { hasText: kid.name })).toHaveAttribute(
      'data-next-action',
      'writing'
    );
    expect((await planOf(request, kid.id)).status).toBe('authoring');
  });

  test('a model reply that fails the gate is repaired and the parent never sees it', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'er', { status: 'expired', scenario: 'repair' });
    await openPick(page, kid.id, kid.name);
    await page.getByRole('button', { name: 'Get fresh ideas' }).click();
    await expect(ideaCards(page).first()).toBeVisible({ timeout: 30_000 });
    await expect(ideaCards(page)).toHaveCount(3);
    expect((await outlineCalls(request, kid.id)).map((c) => c.kind)).toEqual([
      'outline',
      'outline-repair',
    ]);
    await expect(errorBox(page)).toHaveCount(0);
  });

  test('the allowance: two sets of fresh ideas, then a plain message and no button', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'cap', { status: 'awaiting_pick' });
    await openPick(page, kid.id, kid.name);
    await expect(page.getByText('Two more sets available')).toBeVisible();

    const fresh = page.getByRole('button', { name: 'Show me different ideas' });
    await fresh.click();
    await expect(page.getByText('One more set available')).toBeVisible({ timeout: 30_000 });
    await expect(ideaCards(page)).toHaveCount(3);
    await shot(page, 'm10-6-one-left');

    await fresh.click();
    const limit = page.getByTestId('fresh-limit');
    await expect(limit).toBeVisible({ timeout: 30_000 });
    await expect(limit).toContainText('That’s all the fresh ideas for this week.');
    await expect(limit).toContainText('We’ll have new ones after your next check-in.');
    await expect(fresh).toHaveCount(0);
    await expect(ideaCards(page)).toHaveCount(3); // the current ideas can still be picked
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-limit');

    // The API enforces it too, with the same plain words, and makes no model call past the cap.
    const callsBefore = (await outlineCalls(request, kid.id)).length;
    const refused = await request.post(`${BACKEND}/students/${kid.id}/week-plan/regenerate`, {
      data: {},
    });
    expect(refused.status()).toBe(409);
    expect((await refused.json()).detail.code).toBe('limit_reached');
    expect((await outlineCalls(request, kid.id)).length).toBe(callsBefore);
    const plan = await planOf(request, kid.id);
    expect(plan.regenerations_used).toBe(2);
    expect(plan.regenerations_left).toBe(0);
  });

  test('an expired set at the cap says so and offers no way to ask again', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'cx', { status: 'awaiting_pick' });
    const url = `${BACKEND}/students/${kid.id}/week-plan/regenerate`;
    expect((await request.post(url, { data: {} })).status()).toBe(200);
    expect((await request.post(url, { data: {} })).status()).toBe(200);
    expirePlan(kid.id);

    await openPick(page, kid.id, kid.name);
    await expect(page.getByText('Those ideas ran out of time.')).toBeVisible();
    await expect(page.getByTestId('fresh-limit')).toContainText('That’s all the fresh ideas');
    await expect(page.getByRole('button', { name: 'Get fresh ideas' })).toHaveCount(0);
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-expired-limit');
  });
});

test.describe('Pick one of three: loading, errors and other states', () => {
  test('loading state while the ideas load, then the ideas', async ({ page, request }) => {
    const kid = await pickChild(request, 'ld', { status: 'awaiting_pick' });
    await page.route('**/api/students/*/week-plan', async (route) => {
      await new Promise((r) => setTimeout(r, 1500));
      await route.continue();
    });
    await page.goto(`/week/pick/${kid.id}`);
    await expect(page.getByRole('status')).toContainText('Loading');
    await expectNoViolations(page);
    await shot(page, 'm10-6-loading');
    await expect(ideaCards(page)).toHaveCount(3, { timeout: 20_000 });
  });

  test('loading state while fresh ideas are written', async ({ page, request }) => {
    const kid = await pickChild(request, 'lf', { status: 'expired', scenario: 'slow' });
    await openPick(page, kid.id, kid.name);
    await page.getByRole('button', { name: 'Get fresh ideas' }).click();
    await expect(page.getByRole('status')).toContainText('Writing fresh ideas');
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-6-writing-fresh');
    await expect(ideaCards(page)).toHaveCount(3, { timeout: 30_000 });
  });

  test('an error loading the ideas shows a plain message and Try again works', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'el', { status: 'awaiting_pick' });
    let fail = true;
    await page.route('**/api/students/*/week-plan', (route) =>
      fail ? route.fulfill({ status: 500, body: 'boom' }) : route.continue()
    );
    await page.goto(`/week/pick/${kid.id}`);
    const alert = errorBox(page);
    await expect(alert).toContainText('We couldn’t load this', { timeout: 20_000 });
    await expect(page.locator('body')).not.toContainText('boom');
    await expect(page.locator('body')).not.toContainText('500');
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-load-error');
    fail = false;
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(ideaCards(page)).toHaveCount(3, { timeout: 20_000 });
  });

  test('an error saving the choice keeps the week as it was and Yes works again', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'es', { status: 'awaiting_pick' });
    let fail = true;
    await page.route(PICK_URL, (route) =>
      fail ? route.fulfill({ status: 500, body: 'boom' }) : route.continue()
    );
    await openPick(page, kid.id, kid.name);
    await openConfirm(page);
    await page.getByRole('button', { name: 'Yes, use this one' }).click();
    await expect(errorBox(page)).toContainText('We couldn’t save your choice');
    await expect(errorBox(page)).toContainText('Nothing was lost. Please try again.');
    await expect(page.locator('body')).not.toContainText('boom');
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-choose-error');
    expect((await planOf(request, kid.id)).status).toBe('awaiting_pick');

    fail = false;
    await page.getByRole('button', { name: 'Yes, use this one' }).click();
    await expect(page).toHaveURL(/\/week$/, { timeout: 30_000 });
    expect((await planOf(request, kid.id)).status).toBe('authoring');
  });

  test('an error writing fresh ideas: plain message, nothing used up, Try again works', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'ef', { status: 'expired', scenario: 'fail-once' });
    await openPick(page, kid.id, kid.name);
    await page.getByRole('button', { name: 'Get fresh ideas' }).click();
    await expect(errorBox(page)).toBeVisible({ timeout: 60_000 });
    const alert = errorBox(page);
    await expect(alert).toContainText('We couldn’t write new ideas');
    await expect(alert).toContainText('Nothing was lost. Please try again.');
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-fresh-error');

    // One try plus four repairs were made, the week is untouched, no allowance was spent.
    expect((await outlineCalls(request, kid.id)).map((c) => c.kind)).toEqual([
      'outline',
      'outline-repair',
      'outline-repair',
      'outline-repair',
      'outline-repair',
    ]);
    const plan = await planOf(request, kid.id);
    expect(plan).toMatchObject({ status: 'expired', regenerations_used: 0, regenerations_left: 2 });

    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(ideaCards(page)).toHaveCount(3, { timeout: 30_000 });
    expect((await planOf(request, kid.id)).status).toBe('awaiting_pick');
  });

  test('empty states: unknown child, still writing, check in first, already chosen', async ({
    page,
    request,
  }) => {
    await page.goto('/week/pick/nobody_here');
    await expect(page.getByRole('heading', { name: 'We couldn’t find that child' })).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByRole('link', { name: 'Back to this week' })).toBeVisible();
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-unknown-child');

    const writing = await pickChild(request, 'ew', { status: 'outlining' });
    await openPick(page, writing.id, writing.name);
    await expect(page.getByRole('status')).toContainText('We’re writing the ideas');
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-writing-ideas');

    const early = await pickChild(request, 'ec', { status: 'awaiting_feedback' });
    await openPick(page, early.id, early.name);
    await expect(page.getByRole('heading', { name: 'Not ready to pick yet' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Check in' })).toHaveAttribute(
      'href',
      `/week/check-in/${early.id}`
    );
    await expectNoViolations(page);
    await shot(page, 'm10-6-not-ready');

    const done = await pickChild(request, 'ep', { status: 'authoring' });
    await openPick(page, done.id, done.name);
    await expect(
      page.getByRole('heading', { name: `${done.name}’s next week is on its way` })
    ).toBeVisible();
    await expect(
      page.getByText('You chose “Kitchen Math Lab”. We’re writing it now.')
    ).toBeVisible();
    await expect(ideaCards(page)).toHaveCount(0);
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-6-already-chosen');
  });
});

test.describe('Pick one of three: keyboard, accessibility, small screens', () => {
  test('choose and confirm without a pointer', async ({ page, request }) => {
    const kid = await pickChild(request, 'kb', { status: 'awaiting_pick' });
    await openPick(page, kid.id, kid.name);
    await expect(ideaCards(page)).toHaveCount(3);

    await tabTo(page, 'input[type=radio][name=idea]');
    await expect(page.getByRole('radio', { name: /Kitchen Math Lab/ })).toBeFocused();
    await page.keyboard.press('ArrowDown'); // next idea
    await expect(page.getByRole('radio', { name: /Backyard Detectives/ })).toBeChecked();
    await page.keyboard.press('ArrowUp');
    await page.keyboard.press('ArrowUp');
    await expect(page.getByRole('radio', { name: /Gentle Garden Week/ })).toBeChecked();

    await tabTo(page, 'button');
    await expect(page.getByRole('button', { name: 'Use this one' })).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(page.getByRole('heading', { name: 'Use “Gentle Garden Week”?' })).toBeFocused();

    await tabTo(page, 'button');
    await expect(page.getByRole('button', { name: 'Yes, use this one' })).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL(/\/week$/, { timeout: 30_000 });
    const plan = await planOf(request, kid.id);
    expect(plan).toMatchObject({ status: 'authoring', picked_option: 'a' });
  });

  test.describe('on a 320px-wide phone', () => {
    test.use({ viewport: { width: 320, height: 640 } });

    test('nothing scrolls sideways in any state', async ({ page, request }) => {
      const open = await pickChild(request, 'w3', { status: 'awaiting_pick' });
      await openPick(page, open.id, open.name);
      await expect(ideaCards(page)).toHaveCount(3);
      await expectNoHorizontalScroll(page, 'ideas');
      await expectNoViolations(page);
      await shot(page, 'm10-6-320-ideas');

      await openConfirm(page);
      await expectNoHorizontalScroll(page, 'confirm');
      await expectNoViolations(page);
      await shot(page, 'm10-6-320-confirm');

      const expired = await pickChild(request, 'w3e', { status: 'expired' });
      await openPick(page, expired.id, expired.name);
      await expect(page.getByText('Those ideas ran out of time.')).toBeVisible();
      await expectNoHorizontalScroll(page, 'expired');
      await expectNoViolations(page);

      const done = await pickChild(request, 'w3d', { status: 'authoring' });
      await openPick(page, done.id, done.name);
      await expect(page.getByText('We’re writing it now.')).toBeVisible();
      await expectNoHorizontalScroll(page, 'already chosen');
    });
  });
});
