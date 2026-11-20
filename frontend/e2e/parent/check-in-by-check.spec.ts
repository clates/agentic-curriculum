/**
 * M10.5b: the optional check-by-check Friday form on a phone, against the real API.
 * Partial answers are allowed; nothing answered falls back to the quick rating.
 */
import { test, expect } from '../fixtures/test';
import { BACKEND, createPacket, createStudent, seedPlan, seedWeek } from '../fixtures/api';
import { expectNoBannedWords, expectNoViolations, uniqueId } from '../fixtures/parent';
import { shot } from '../fixtures/shots';

async function seedChild(request: Parameters<typeof createStudent>[0], kind: 'week' | 'plain') {
  const id = uniqueId('cb');
  const name = `Kid${id.replace(/[^a-z0-9]/gi, '')}`;
  await createStudent(request, id, { name: `${name} Testerson`, birthday: '2018-03-04' });
  const packetId = `pk_${id}`;
  if (kind === 'week') seedWeek(id, packetId);
  else await createPacket(request, id, packetId);
  seedPlan(id, 'awaiting_feedback');
  return { id, name, packetId };
}

test.describe('Friday check-in: check by check (real API)', () => {
  test('answer some, skip the rest, send: only the answers are recorded', async ({
    page,
    request,
  }) => {
    const { id, packetId, name } = await seedChild(request, 'week');
    await page.goto(`/week/check-in/${id}`);
    await page.getByRole('link', { name: 'Check each skill instead' }).click({ timeout: 20_000 });

    await expect(page.getByText('Check 1 of 10')).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole('heading', { level: 1 })).toContainText(name);
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-5b-card');

    await page.getByRole('button', { name: 'Got it' }).click();
    await expect(page.getByText('Check 2 of 10')).toBeVisible();
    await page.getByRole('button', { name: 'Missed' }).click();
    for (let n = 3; n <= 10; n++) {
      await expect(page.getByText(`Check ${n} of 10`)).toBeVisible();
      await page.getByRole('button', { name: 'Skip this one' }).click();
    }

    await expect(page.getByRole('heading', { name: 'Ready to send?' })).toBeVisible();
    await expect(page.getByText('You answered 2 of 10 checks.')).toBeVisible();
    await page.getByText('Too much', { exact: true }).click();
    await expectNoViolations(page);
    await shot(page, 'm10-5b-review');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByRole('status')).toContainText('Thank you!');
    await shot(page, 'm10-5b-done');

    const saved = await (
      await request.get(`${BACKEND}/students/${id}/weekly-packets/${packetId}/feedback`)
    ).json();
    expect(saved.check_results).toEqual({ 'chk-1': 'got_it', 'chk-2': 'missed' });
    expect(saved.quantity_feedback).toBe(-2);
  });

  test('answering nothing cannot send and points to the quick rating', async ({
    page,
    request,
  }) => {
    const { id } = await seedChild(request, 'week');
    await page.goto(`/week/check-in/${id}/by-check`);
    for (let n = 1; n <= 10; n++) {
      await page.getByRole('button', { name: 'Skip this one' }).click({ timeout: 20_000 });
    }
    await expect(
      page.getByText('Answer at least one check, or use the quick rating')
    ).toBeVisible();
    await expect(page.getByRole('button', { name: 'Send' })).toHaveCount(0);
    await expectNoViolations(page);
    await page.getByRole('link', { name: 'Use the quick rating instead' }).click();
    await expect(page.getByRole('button', { name: 'Send' })).toBeVisible();
    await expect(page.getByText('Got it', { exact: true })).toBeVisible();
  });

  test('a week with no check list falls back to the quick rating', async ({ page, request }) => {
    const { id } = await seedChild(request, 'plain');
    await page.goto(`/week/check-in/${id}`);
    await expect(page.getByRole('button', { name: 'Send' })).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole('link', { name: 'Check each skill instead' })).toHaveCount(0);
    await page.goto(`/week/check-in/${id}/by-check`);
    await expect(page.getByRole('heading', { name: 'No checks for this week' })).toBeVisible({
      timeout: 20_000,
    });
    await expectNoViolations(page);
    await shot(page, 'm10-5b-nochecks');
    await expect(page.getByRole('link', { name: 'Use the quick rating instead' })).toBeVisible();
  });

  test('a failure loading the checks shows a plain message with a retry', async ({
    page,
    request,
  }) => {
    const { id } = await seedChild(request, 'week');
    await page.route('**/api/students/*/weekly-packets/*/checks', (r) =>
      r.fulfill({ status: 500, body: 'x' })
    );
    await page.goto(`/week/check-in/${id}/by-check`);
    await expect(page.locator('main [role="alert"]')).toContainText('We couldn’t load this', {
      timeout: 20_000,
    });
    await expect(page.getByRole('button', { name: 'Try again' })).toBeVisible();
    await expectNoViolations(page);
  });
});
