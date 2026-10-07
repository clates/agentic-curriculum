/**
 * Journey 5 — Keep going
 *
 * Week after week, the parent comes back to the dashboard. It should give an honest picture of
 * where each child stands, and the next week's plan should respond to what the parent reported.
 *
 * Most of this journey is still ahead of the product. The pending steps below are the target.
 */
import { test, expect } from '../fixtures/test';
import { createStudent, createPacket } from '../fixtures/api';

test.describe('5.1 The dashboard tells the truth', () => {
  const STUDENT_ID = 'e2e-dashboard-y3z4';
  const NAME = 'Dashboard Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: NAME, birthday: '2019-04-01' });
    await createPacket(request, STUDENT_ID, `${STUDENT_ID}-pkt-001`);
  });

  test('each child has a card with a "Generate Plan" action', async ({ page }) => {
    await page.goto('/dashboard');
    const card = page.getByRole('heading', { name: NAME }).locator('../../..');
    await expect(card).toBeVisible();
    await expect(card.getByRole('button', { name: 'Generate Plan' })).toBeVisible();
  });

  // Progress currently counts a synthetic "overall" standard (showing "1/1, 100%") and rounds
  // 1015/1016 up to "100% Complete".
  test.fixme('progress counts real standards and never rounds up to 100%', async () => {});
  // "Worksheets Ready" counts every worksheet ever generated, not the ones still waiting to be used.
  test.fixme('"Worksheets Ready" counts only weeks that are still pending', async () => {});
  test.fixme('past weeks look different from the current week', async () => {});
});

test.describe('5.2 The next week adapts', () => {
  // Depends on the fake LLM server from Journey 2.1.
  test.fixme('after "Too Much" feedback, the next week has fewer activities', async () => {});
  test.fixme('standards rated Mastered are not re-taught next week', async () => {});
});
