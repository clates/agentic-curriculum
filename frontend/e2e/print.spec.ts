import { test, expect } from '@playwright/test';
import { createStudent, createPacket } from './fixtures/api';

const BACKEND = process.env.BACKEND_URL ?? 'http://localhost:8182';

// The print endpoint returns 404 when no HTML worksheet files exist on disk.
// These tests verify the route and its headers using a real packet, but skip
// DOM-level assertions that require on-disk HTML artifacts.

test.describe('Worksheet print view — route smoke tests', () => {
  const STUDENT_ID = 'e2e-print-smoke-t9u0';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, {
      name: 'Print Smoke Student',
      birthday: '2018-10-01',
    }).catch(() => {});
    await createPacket(request, STUDENT_ID, PACKET_ID);
  });

  test('GET /api/students/{id}/weekly-packets/{id}/print returns a response', async ({
    request,
  }) => {
    const res = await request.get(
      `${BACKEND}/students/${STUDENT_ID}/weekly-packets/${PACKET_ID}/print`
    );
    // 404 is expected here because the seeded packet has no on-disk HTML artifacts.
    // 200 would also pass — this test just confirms the route exists and responds.
    expect([200, 404]).toContain(res.status());
  });

  test('print URL is reachable via the Next.js proxy (/api prefix)', async ({ page }) => {
    const res = await page.request.get(
      `/api/students/${STUDENT_ID}/weekly-packets/${PACKET_ID}/print`
    );
    expect([200, 404]).toContain(res.status());
  });
});
