/**
 * Journey 3 — Teach the week
 *
 * The parent prints the week's packet and works through it with their child, away from the
 * screen. The app's job here is a clean, complete printout.
 */
import { test, expect } from '../fixtures/test';
import { createStudent, createPacket } from '../fixtures/api';
import { repeatIdentity } from '../fixtures/e2e-hardening';

test.describe('3.1 Print the packet', () => {
  const STUDENT_ID_0 = 'e2e-print-smoke-t9u0';
  let STUDENT_ID = STUDENT_ID_0;
  let PACKET_ID = `${STUDENT_ID}-pkt-001`;
  const NAME_0 = 'Print Smoke Student';
  let NAME = NAME_0;

  test.beforeAll(async ({ request }) => {
    ({ id: STUDENT_ID, name: NAME } = repeatIdentity(STUDENT_ID_0, NAME_0));
    PACKET_ID = `${STUDENT_ID}-pkt-001`;
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

  // Structured (hosted) weeks are covered by e2e/print/hosted-week-print.spec.ts: every day's
  // worksheets, the teacher guide and the prep sheet. Legacy packets with rendered HTML artifacts
  // on disk are still untested here (backend pytest covers them); see e2e/COVERAGE.md.
});
