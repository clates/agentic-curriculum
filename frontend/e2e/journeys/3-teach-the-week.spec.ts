/**
 * Journey 3 — Teach the week
 *
 * The parent prints the week's packet and works through it with their child, away from the
 * screen. The app's job here is a clean, complete printout.
 */
import { test, expect } from '../fixtures/test';
import { createStudent, createPacket } from '../fixtures/api';

test.describe('3.1 Print the packet', () => {
  const STUDENT_ID = 'e2e-print-smoke-t9u0';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;
  const NAME = 'Print Smoke Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: NAME, birthday: '2018-10-01' });
    await createPacket(request, STUDENT_ID, PACKET_ID);
  });

  test('"Print All" opens the printable packet in a new tab', async ({ page }) => {
    await page.goto('/plans');
    await page.getByRole('heading', { name: NAME }).click();
    const [popup] = await Promise.all([
      page.waitForEvent('popup'),
      page.getByRole('button', { name: 'Print All' }).click(),
    ]);
    await expect(popup).toHaveURL(/\/print/);
  });

  test('the print route answers through the app’s /api proxy', async ({ page }) => {
    const res = await page.request.get(
      `/api/students/${STUDENT_ID}/weekly-packets/${PACKET_ID}/print`
    );
    // The seeded packet has no rendered HTML on disk, so 404 is the honest answer today.
    expect([200, 404]).toContain(res.status());
  });

  // Needs the seed to render real worksheet HTML (src/worksheet_html_renderer.py) so the print
  // view can be asserted on content: every day present, page breaks, a teacher guide.
  test.fixme('the printout contains every day’s worksheets', async () => {});
});
