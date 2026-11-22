/**
 * What a check-in actually stores. A "Thank you!" on screen proves nothing; these read the
 * feedback back from the real API (backend on its own port, not through any mock) and assert the
 * recorded values, for every rating, every workload and the by-check answers, and that Send fires
 * exactly one request.
 */
import { test, expect } from '../fixtures/test';
import { newChild, storedFeedback } from '../fixtures/e2e-hardening';

const FEEDBACK = '**/api/students/*/weekly-packets/*/feedback';

test.describe('Quick check-in: stored values', () => {
  const MATRIX = [
    { label: 'Got it', rating: 'smooth', workloadLabel: 'Too little', workload: 2 },
    { label: 'Shaky', rating: 'mixed', workloadLabel: 'Just right', workload: 0 },
    { label: 'Lost it', rating: 'rough', workloadLabel: 'Too much', workload: -2 },
  ];

  for (const m of MATRIX) {
    test(`"${m.label}" + "${m.workloadLabel}" is stored as ${m.rating} / ${m.workload}`, async ({
      page,
      request,
    }) => {
      const kid = await newChild(request, 'qr', { packet: 'legacy', plan: 'awaiting_feedback' });
      await page.goto(`/week/check-in/${kid.id}`);
      await page.getByText(m.label, { exact: true }).click({ timeout: 20_000 });
      await page.getByText(m.workloadLabel, { exact: true }).click();

      const sent = page.waitForRequest(
        (r) => r.method() === 'POST' && r.url().includes('/feedback')
      );
      await page.getByRole('button', { name: 'Send' }).click();
      const body = (await sent).postDataJSON();
      expect(body).toEqual({ quick_rating: m.rating, workload: m.workload });
      await expect(page.getByRole('status')).toContainText('Thank you!');

      const saved = await storedFeedback(request, kid.id, kid.packetId);
      expect(saved.quick_rating).toBe(m.rating);
      expect(saved.quantity_feedback).toBe(m.workload);
    });
  }

  test('without a workload, none is stored', async ({ page, request }) => {
    const kid = await newChild(request, 'qn', { packet: 'legacy', plan: 'awaiting_feedback' });
    await page.goto(`/week/check-in/${kid.id}`);
    await page.getByText('Shaky', { exact: true }).click({ timeout: 20_000 });
    const sent = page.waitForRequest((r) => r.method() === 'POST' && r.url().includes('/feedback'));
    await page.getByRole('button', { name: 'Send' }).click();
    expect((await sent).postDataJSON()).toEqual({ quick_rating: 'mixed' });
    await expect(page.getByRole('status')).toContainText('Thank you!');
    const saved = await storedFeedback(request, kid.id, kid.packetId);
    expect(saved.quick_rating).toBe('mixed');
    expect(saved.quantity_feedback ?? null).toBeNull();
  });

  test('Send fires one request even when tapped twice quickly', async ({ page, request }) => {
    test.fail(
      true,
      'quick check-in: QuickCheckIn.tsx has no in-flight guard, so a double tap POSTs /feedback twice (the backend ignores the exact repeat); issue #211'
    );
    const kid = await newChild(request, 'qd', { packet: 'legacy', plan: 'awaiting_feedback' });
    let posts = 0;
    await page.route(FEEDBACK, async (route) => {
      if (route.request().method() === 'POST') {
        posts += 1;
        await new Promise((r) => setTimeout(r, 400)); // keep the first one in flight
      }
      await route.continue();
    });
    await page.goto(`/week/check-in/${kid.id}`);
    await page.getByText('Got it', { exact: true }).click({ timeout: 20_000 });
    const send = page.getByRole('button', { name: 'Send' });
    await send.dblclick();
    await expect(page.getByRole('status')).toContainText('Thank you!');
    expect(posts).toBe(1);
    expect((await storedFeedback(request, kid.id, kid.packetId)).quick_rating).toBe('smooth');
  });
});

test.describe('Check by check: stored values and skip semantics', () => {
  test('all three results are stored against the right checks; skipped ones are absent', async ({
    page,
    request,
  }) => {
    const kid = await newChild(request, 'br', { packet: 'week', plan: 'awaiting_feedback' });
    await page.goto(`/week/check-in/${kid.id}/by-check`);
    await expect(page.getByText('Check 1 of 10')).toBeVisible({ timeout: 20_000 });
    await page.getByRole('button', { name: 'Got it' }).click(); // chk-1
    await page.getByRole('button', { name: 'Skip this one' }).click(); // chk-2 skipped
    await page.getByRole('button', { name: 'Shaky' }).click(); // chk-3
    await page.getByRole('button', { name: 'Missed' }).click(); // chk-4
    for (let n = 5; n <= 10; n++) await page.getByRole('button', { name: 'Skip this one' }).click();
    await page.getByText('Just right', { exact: true }).click();

    const sent = page.waitForRequest((r) => r.method() === 'POST' && r.url().includes('/feedback'));
    await page.getByRole('button', { name: 'Send' }).click();
    expect((await sent).postDataJSON()).toEqual({
      check_results: { 'chk-1': 'got_it', 'chk-3': 'shaky', 'chk-4': 'missed' },
      workload: 0,
    });
    await expect(page.getByRole('status')).toContainText('Thank you!');

    const saved = await storedFeedback(request, kid.id, kid.packetId);
    expect(saved.check_results).toEqual({ 'chk-1': 'got_it', 'chk-3': 'shaky', 'chk-4': 'missed' });
    expect(saved.quantity_feedback).toBe(0);
  });

  test('going back and changing an answer stores the last choice, and Skip never erases one', async ({
    page,
    request,
  }) => {
    const kid = await newChild(request, 'bb', { packet: 'week', plan: 'awaiting_feedback' });
    await page.goto(`/week/check-in/${kid.id}/by-check`);
    await expect(page.getByText('Check 1 of 10')).toBeVisible({ timeout: 20_000 });
    await page.getByRole('button', { name: 'Missed' }).click(); // chk-1 = missed
    await page.getByRole('button', { name: 'Back' }).click();
    await expect(page.getByText('Check 1 of 10')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Missed' })).toHaveAttribute(
      'aria-pressed',
      'true'
    );
    await page.getByRole('button', { name: 'Got it' }).click(); // changed to got_it
    await page.getByRole('button', { name: 'Back' }).click();
    await page.getByRole('button', { name: 'Skip this one' }).click(); // skip over an answered one
    for (let n = 2; n <= 10; n++) await page.getByRole('button', { name: 'Skip this one' }).click();
    await expect(page.getByText('You answered 1 of 10 checks.')).toBeVisible();
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByRole('status')).toContainText('Thank you!');
    const saved = await storedFeedback(request, kid.id, kid.packetId);
    expect(saved.check_results).toEqual({ 'chk-1': 'got_it' });
    expect(saved.quantity_feedback ?? null).toBeNull(); // no workload chosen, none stored
  });

  test('a failed send keeps every answer and a retry records them', async ({ page, request }) => {
    const kid = await newChild(request, 'bf', { packet: 'week', plan: 'awaiting_feedback' });
    let fail = true;
    await page.route(FEEDBACK, (r) =>
      fail && r.request().method() === 'POST' ? r.fulfill({ status: 500, body: 'x' }) : r.continue()
    );
    await page.goto(`/week/check-in/${kid.id}/by-check`);
    await expect(page.getByText('Check 1 of 10')).toBeVisible({ timeout: 20_000 });
    await page.getByRole('button', { name: 'Shaky' }).click();
    for (let n = 2; n <= 10; n++) await page.getByRole('button', { name: 'Skip this one' }).click();
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.locator('main [role="alert"]')).toContainText('We couldn’t send that');
    await expect(page.getByText('You answered 1 of 10 checks.')).toBeVisible();
    fail = false;
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByRole('status')).toContainText('Thank you!');
    const saved = await storedFeedback(request, kid.id, kid.packetId);
    expect(saved.check_results).toEqual({ 'chk-1': 'shaky' });
  });
});
