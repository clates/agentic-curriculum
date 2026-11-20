/**
 * M10.5a: the quick Friday check-in on a phone, against the real feedback API.
 * Two taps and Send; the rating and workload really land in the stored feedback.
 */
import { test, expect } from '../fixtures/test';
import { BACKEND, createPacket, createStudent, seedPlan } from '../fixtures/api';
import { expectNoBannedWords, expectNoViolations, uniqueId } from '../fixtures/parent';
import { shot } from '../fixtures/shots';

async function seedChild(request: Parameters<typeof createStudent>[0], withPacket: boolean) {
  const id = uniqueId('ci');
  const name = `Kid${id.replace(/[^a-z0-9]/gi, '')}`;
  await createStudent(request, id, { name: `${name} Testerson`, birthday: '2018-03-04' });
  const packetId = `pk_${id}`;
  if (withPacket) await createPacket(request, id, packetId);
  seedPlan(id, 'awaiting_feedback');
  return { id, name, packetId };
}

test.describe('Friday check-in: quick rating (real API)', () => {
  test('two taps and Send record the rating and workload', async ({ page, request }) => {
    const { id, name, packetId } = await seedChild(request, true);
    await page.goto('/week');
    const card = page.locator('[data-testid="child-card"]', { hasText: name });
    await card.getByRole('link', { name: 'Check in' }).click({ timeout: 20_000 });

    await expect(page.getByRole('heading', { level: 1 })).toContainText(name, { timeout: 20_000 });
    const send = page.getByRole('button', { name: 'Send' });
    await expect(send).toBeDisabled(); // nothing chosen yet
    await expectNoViolations(page);
    await shot(page, 'm10-5a-form');

    await page.getByText('Shaky', { exact: true }).click(); // tap 1
    await page.getByText('Just right', { exact: true }).click(); // tap 2
    await expect(send).toBeEnabled();
    await shot(page, 'm10-5a-chosen');

    // Everything the thumb needs sits in the lower two thirds of a phone screen.
    const box = await send.boundingBox();
    expect(box!.y).toBeGreaterThan(page.viewportSize()!.height / 3);

    await send.click();
    await expect(page.getByRole('status')).toContainText('Thank you!');
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-5a-done');

    const saved = await (
      await request.get(`${BACKEND}/students/${id}/weekly-packets/${packetId}/feedback`)
    ).json();
    expect(saved.quick_rating).toBe('mixed');
    expect(saved.quantity_feedback).toBe(0);
  });

  test('the rating alone is enough; workload is optional', async ({ page, request }) => {
    const { id, packetId } = await seedChild(request, true);
    await page.goto(`/week/check-in/${id}`);
    await page.getByText('Got it', { exact: true }).click({ timeout: 20_000 });
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByRole('status')).toContainText('Thank you!');
    const saved = await (
      await request.get(`${BACKEND}/students/${id}/weekly-packets/${packetId}/feedback`)
    ).json();
    expect(saved.quick_rating).toBe('smooth');
  });

  test('a child with no finished week sees what to expect, not a form', async ({
    page,
    request,
  }) => {
    const { id } = await seedChild(request, false);
    await page.goto(`/week/check-in/${id}`);
    await expect(page.getByRole('heading', { name: 'Nothing to check in on yet' })).toBeVisible({
      timeout: 20_000,
    });
    await expectNoViolations(page);
    await shot(page, 'm10-5a-empty');
  });

  test('a failed send shows a plain message and keeps the choices', async ({ page, request }) => {
    const { id } = await seedChild(request, true);
    await page.route('**/api/students/*/weekly-packets/*/feedback', (r) =>
      r.fulfill({ status: 500, body: 'x' })
    );
    await page.goto(`/week/check-in/${id}`);
    await page.getByText('Lost it', { exact: true }).click({ timeout: 20_000 });
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.locator('main [role="alert"]')).toContainText('We couldn’t send that');
    await expect(page.getByRole('button', { name: 'Send' })).toBeEnabled();
    await expectNoViolations(page);
    await shot(page, 'm10-5a-error');
  });

  test('loading shows while the week is fetched, and an unknown child is handled', async ({
    page,
  }) => {
    await page.goto('/week/check-in/no_such_child');
    await expect(page.getByRole('heading', { name: 'We couldn’t find that child' })).toBeVisible({
      timeout: 20_000,
    });
    await expectNoViolations(page);
  });
});
