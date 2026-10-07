/**
 * Journey 2 — Plan the week
 *
 * The parent asks for a week of lessons for their child, waits for it to generate, and reviews
 * the result: one card per pending week, and a detail view that reads like a lesson plan.
 */
import { test, expect } from '../fixtures/test';
import { createStudent, createPacket } from '../fixtures/api';

test.describe('2.1 Generate a week', () => {
  // Needs a fake OpenAI-compatible server in global-setup so the real generator runs end to end
  // (scaffold call + one call per day) without a paid key. Until then the whole step is pending.
  test.fixme('from the dashboard, "Generate Plan" produces a five-day week', async () => {});
  test.fixme('every day has real content — no generic fallback on Day 1 (#134)', async () => {});
  test.fixme('generating the same week twice warns instead of toasting success (#137)', async () => {});
});

test.describe('2.2 A child with no plan yet', () => {
  test.beforeAll(async ({ request }) => {
    await createStudent(request, 'e2e-feedback-empty-a1b2', {
      name: 'Empty State Student',
      birthday: '2018-01-01',
    });
  });

  test('has no pending card on the plans page', async ({ page }) => {
    await page.goto('/plans');
    await expect(page.getByText('Empty State Student')).not.toBeVisible();
  });
});

test.describe('2.3 Review a pending week', () => {
  const STUDENT_ID = 'e2e-feedback-modal-e5f6';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;
  const NAME = 'Detail Modal Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: NAME, birthday: '2018-03-01' });
    await createPacket(request, STUDENT_ID, PACKET_ID);
  });

  const openPlan = async (page: import('@playwright/test').Page) => {
    await page.goto('/plans');
    await page.getByRole('heading', { name: NAME }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    return page.getByRole('dialog');
  };

  test('the pending card summarises subject, grade, and number of days', async ({ page }) => {
    await page.goto('/plans');
    const card = page.getByRole('heading', { name: NAME }).locator('../../..');
    await expect(card.getByText('Mathematics')).toBeVisible();
    await expect(card.getByText('3')).toBeVisible(); // grade_level
    await expect(card.locator('text=Days').locator('..').getByText('2')).toBeVisible();
  });

  test('opening the card shows who, which week, subject, and grade', async ({ page }) => {
    const modal = await openPlan(page);
    await expect(modal.getByText('Plan Details')).toBeVisible();
    await expect(modal.getByText(NAME)).toBeVisible();
    await expect(modal.getByText('Mathematics')).toBeVisible();
    await expect(modal.getByText('Grade Level').locator('..').getByText('3')).toBeVisible();
  });

  test('each day reads as a lesson: focus, objective, procedure', async ({ page }) => {
    const modal = await openPlan(page);
    await expect(modal.getByText('Monday')).toBeVisible();
    await expect(modal.getByText('Introduction', { exact: true })).toBeVisible();
    await expect(modal.getByText('Understand fractions')).toBeVisible();
    await expect(modal.getByText('Read introduction')).toBeVisible();
  });

  test('the detail view closes with Close, Escape, or a backdrop click', async ({ page }) => {
    await openPlan(page);
    await page.getByRole('button', { name: 'Close', exact: true }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();

    await openPlan(page);
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();

    await openPlan(page);
    await page.mouse.click(10, 10);
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });
});
