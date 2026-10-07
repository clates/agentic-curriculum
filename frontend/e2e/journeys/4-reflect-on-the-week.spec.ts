/**
 * Journey 4 — Reflect on the week
 *
 * After teaching the week, the parent records how it went: how well the child mastered it and
 * whether the workload was right. They can revise that for a while, then it locks. The feedback
 * shows up on the child's progress map.
 */
import { test, expect } from '../fixtures/test';
import { createStudent, createPacket, submitFeedback, backdateFeedback } from '../fixtures/api';

test.describe('4.1 Give feedback on a finished week', () => {
  test.describe.configure({ mode: 'serial' });
  const STUDENT_ID = 'e2e-feedback-submit-k1l2';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;
  const NAME = 'Submit Feedback Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: NAME, birthday: '2018-06-01' });
    await createPacket(request, STUDENT_ID, PACKET_ID);
  });

  const openFeedback = async (page: import('@playwright/test').Page) => {
    await page.goto('/plans');
    await page.getByRole('heading', { name: NAME, exact: true }).click();
    await page.getByRole('button', { name: 'Provide Feedback' }).click();
  };

  test('a week without feedback offers "Provide Feedback"', async ({ page }) => {
    await openFeedback(page);
    await expect(page.getByRole('dialog').getByText('Provide Feedback')).toBeVisible();
  });

  test('submit stays disabled until both mastery and workload are rated', async ({ page }) => {
    await openFeedback(page);
    const submit = page.getByRole('button', { name: 'Submit Feedback', exact: true });
    await expect(submit).toBeDisabled();

    const mastered = page.getByRole('button', { name: 'Mastered' });
    await mastered.click();
    await expect(mastered).toHaveClass(/ring-2/);
    await expect(submit).toBeDisabled();

    const justRight = page.getByRole('button', { name: 'Just Right' });
    await justRight.click();
    await expect(justRight).toHaveClass(/ring-2/);
    await expect(submit).toBeEnabled();
  });

  test('the parent can back out with Cancel, Escape, or a backdrop click', async ({ page }) => {
    await openFeedback(page);
    await page.getByRole('button', { name: 'Cancel' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();

    await openFeedback(page);
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();

    await openFeedback(page);
    await page.mouse.click(10, 10);
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('submitting moves the week to Completed, where it can be edited', async ({ page }) => {
    await openFeedback(page);
    await page.getByRole('button', { name: 'Mastered' }).click();
    await page.getByRole('button', { name: 'Just Right' }).click();
    await page.getByRole('button', { name: 'Submit Feedback', exact: true }).click();

    await page.locator('table tr').filter({ hasText: NAME }).click();
    await expect(page.getByRole('button', { name: 'Edit Feedback', exact: true })).toBeVisible();
  });

  test.fixme('double-clicking submit sends feedback once', async () => {});
});

test.describe('4.2 Revise recent feedback', () => {
  test.describe.configure({ mode: 'serial' });
  const STUDENT_ID = 'e2e-feedback-resubmit-m3n4';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;
  const NAME = 'Resubmit Feedback Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: NAME, birthday: '2018-07-01' });
    await createPacket(request, STUDENT_ID, PACKET_ID);
    await submitFeedback(request, STUDENT_ID, PACKET_ID, { mastery: 'DEVELOPING', quantity: 2 });
  });

  const openEdit = async (page: import('@playwright/test').Page) => {
    await page.goto('/plans');
    await page.locator('table tr').filter({ hasText: NAME }).click();
    await page.getByRole('button', { name: 'Edit Feedback', exact: true }).click();
  };

  test('"Edit Feedback" reopens the form with the earlier ratings selected', async ({ page }) => {
    await openEdit(page);
    await expect(page.getByRole('dialog').getByText('Edit Feedback')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Developing' })).toHaveClass(/ring-2/);
    await expect(page.getByRole('button', { name: 'Too Little' })).toHaveClass(/ring-2/);
    await expect(page.getByRole('button', { name: 'Update Feedback' })).toBeVisible();
  });

  test('changing a rating and saving succeeds', async ({ page }) => {
    await openEdit(page);
    await page.getByRole('button', { name: 'Mastered' }).click();
    await page.getByRole('button', { name: 'Just Right' }).click();
    await page.getByRole('button', { name: 'Update Feedback' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });
});

test.describe('4.3 Old feedback is locked', () => {
  const STUDENT_ID = 'e2e-feedback-locked-i9j0';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;
  const NAME = 'Locked Feedback Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: NAME, birthday: '2018-05-01' });
    await createPacket(request, STUDENT_ID, PACKET_ID);
    await submitFeedback(request, STUDENT_ID, PACKET_ID, { mastery: 'DEVELOPING', quantity: 1 });
    backdateFeedback(PACKET_ID, '2026-01-01T00:00:00Z');
  });

  test('feedback older than three weeks shows a disabled "Feedback Submitted"', async ({
    page,
  }) => {
    await page.goto('/plans');
    await page.locator('table tr').filter({ hasText: NAME }).click();
    const btn = page.getByRole('button', { name: 'Feedback Submitted' });
    await expect(btn).toBeVisible();
    await expect(btn).toBeDisabled();
  });
});

test.describe('4.4 See it on the progress map', () => {
  const STUDENT_ID = 'e2e-progress-map-w1x2';
  const NAME = 'Progress Map Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: NAME, birthday: '2018-11-01' });
  });

  test('choosing a child and subject draws their curriculum map', async ({ page }) => {
    await page.goto('/progress');
    const selects = page.locator('select');
    await selects.nth(0).selectOption({ label: NAME });
    await selects.nth(1).selectOption({ label: 'Math' });
    await expect(page.getByText('Select a student and subject')).not.toBeVisible();
    await expect(page.locator('.react-flow__node').first()).toBeVisible();
  });

  // Feedback on a seeded packet only touches the synthetic "overall" standard. Asserting that a
  // real standard turns "Mastered" needs packets seeded with real standard IDs.
  test.fixme('standards rated Mastered in feedback show as Mastered on the map', async () => {});
});
