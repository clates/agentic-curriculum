/**
 * Hosted (structured WeekDoc) week printing, through the app's /api proxy in a real page.
 *
 * GET /students/{id}/weekly-packets/{pid}/print?doc=packet|guide|prep renders on demand from the
 * stored week. Backend pytest covers the renderers (tests/test_week_print_endpoints.py); this
 * proves the same documents arrive intact through the Next proxy and display in a browser.
 * Desktop project only: this is paper, not a phone screen.
 */
import type { Page } from '@playwright/test';
import { test, expect } from '../fixtures/test';
import { createPacket, createStudent } from '../fixtures/api';
import {
  Child,
  WEATHER_WEEK,
  WEEKDAYS,
  expectNoHorizontalScroll,
  newChild,
} from '../fixtures/e2e-hardening';
import { uniqueId } from '../fixtures/parent';

const printUrl = (c: Child, doc?: string) =>
  `/api/students/${c.id}/weekly-packets/${c.packetId}/print${doc ? `?doc=${doc}` : ''}`;

async function open(page: Page, url: string) {
  const res = await page.goto(url);
  expect(res, `no response for ${url}`).not.toBeNull();
  return res!;
}

const texts = (page: Page, selector: string) =>
  page.locator(selector).evaluateAll((els) => els.map((e) => (e.textContent ?? '').trim()));

test.describe('Hosted week print documents (structured week)', () => {
  let child: Child;

  test.beforeAll(async ({ request }) => {
    child = await newChild(request, 'pr', { packet: 'week' });
  });

  test('the packet loads as HTML and holds every day’s worksheets', async ({ page }) => {
    const res = await open(page, printUrl(child, 'packet'));
    expect(res.status()).toBe(200);
    expect(res.headers()['content-type']).toContain('text/html');

    const expected = WEATHER_WEEK.days.flatMap((d) => d.worksheets.map((w) => w.data.title!));
    expect(expected).toHaveLength(11);
    const rendered = await texts(page, '.ws-title');
    expect(rendered).toEqual(expected);

    // One header per worksheet carries its weekday; every weekday is present.
    const dayLabels = await texts(page, '.day-header-label');
    for (const day of WEEKDAYS) {
      const want = WEATHER_WEEK.days.find((d) => d.day === day)!.worksheets.length;
      expect(
        dayLabels.filter((l) => l === day),
        `${day} worksheets`
      ).toHaveLength(want);
    }

    // No answer key leaks into the student's packet.
    await expect(page.locator('body')).not.toContainText('Answer Key');
  });

  test('the packet is the default document and equals ?doc=packet', async ({ request }) => {
    const bare = await request.get(printUrl(child));
    const explicit = await request.get(printUrl(child, 'packet'));
    expect(bare.status()).toBe(200);
    expect(await bare.text()).toBe(await explicit.text());
  });

  test('the teacher guide has an answer key for each day, Monday to Friday', async ({ page }) => {
    const res = await open(page, printUrl(child, 'guide'));
    expect(res.status()).toBe(200);
    await expect(
      page.getByRole('heading', { name: 'Weather Week — Teacher / Parent Guide' })
    ).toBeVisible();

    const headings = await texts(page, 'h2, h3');
    for (const day of WEEKDAYS) {
      const idx = headings.findIndex((h) => h.startsWith(`${day} —`));
      expect(idx, `a "${day} —" section`).toBeGreaterThanOrEqual(0);
      // The day's own section holds an answer key before the next weekday begins.
      const next = headings.findIndex(
        (h, i) => i > idx && /^(Monday|Tuesday|Wednesday|Thursday|Friday) —/.test(h)
      );
      const section = headings.slice(idx + 1, next === -1 ? undefined : next);
      expect(
        section.some((h) => h.includes('Answer Key')),
        `an answer key under ${day}`
      ).toBe(true);
    }
    await expect(
      page.getByRole('heading', { name: /^Answer Key — Reading Questions$/ })
    ).toHaveCount(5);
  });

  test('the prep sheet lists every prep check', async ({ page }) => {
    const res = await open(page, printUrl(child, 'prep'));
    expect(res.status()).toBe(200);
    await expect(page.locator('.pc-card')).toHaveCount(WEATHER_WEEK.prep_checks.length);
    const prompts = await texts(page, '.pc-prompt');
    expect(prompts).toEqual(
      WEATHER_WEEK.prep_checks.map((c) =>
        c.prompt.replace(/&amp;/g, '&').replace(/\{\{student_name\}\}/g, child.name)
      )
    );
    const tops = await texts(page, '.pc-top');
    for (const day of WEEKDAYS) expect(tops.some((t) => t.startsWith(day))).toBe(true);
  });

  for (const doc of ['packet', 'guide', 'prep']) {
    test(`${doc}: the child's first name is used and no placeholder or last name shows`, async ({
      page,
    }) => {
      await open(page, printUrl(child, doc));
      const html = await page.content();
      expect(html).not.toContain('{{student_name}}');
      expect(html).not.toContain('{{');
      expect(html).not.toContain(child.lastName);
      if (doc === 'packet') {
        await expect(page).toHaveTitle(`Weather Week — Science for ${child.name}`);
      }
    });

    test(`${doc}: nothing overflows sideways at print width`, async ({ page }) => {
      await page.setViewportSize({ width: 816, height: 1056 }); // US Letter at 96 dpi
      await open(page, printUrl(child, doc));
      await expectNoHorizontalScroll(page, `${doc} on screen`);
      await page.emulateMedia({ media: 'print' });
      await expectNoHorizontalScroll(page, `${doc} in print media`);
    });
  }

  test('an unknown packet is a 404', async ({ request }) => {
    const res = await request.get(`/api/students/${child.id}/weekly-packets/no_such_packet/print`);
    expect(res.status()).toBe(404);
  });

  test('another child cannot print this packet', async ({ request }) => {
    const other = await newChild(request, 'po');
    const res = await request.get(
      `/api/students/${other.id}/weekly-packets/${child.packetId}/print?doc=guide`
    );
    expect(res.status()).toBe(404);
  });

  test('an unknown document name is rejected', async ({ request }) => {
    const res = await request.get(printUrl(child, 'bogus'));
    expect(res.status()).toBe(422);
  });

  test('a legacy packet has no teacher guide or prep sheet (404)', async ({ request }) => {
    const legacyId = uniqueId('pl');
    await createStudent(request, legacyId, { name: 'Legacy Kid', birthday: '2018-03-04' });
    const packetId = `pk_${legacyId}`;
    await createPacket(request, legacyId, packetId);
    for (const doc of ['guide', 'prep']) {
      const res = await request.get(
        `/api/students/${legacyId}/weekly-packets/${packetId}/print?doc=${doc}`
      );
      expect(res.status(), doc).toBe(404);
      expect(await res.text()).toContain('no structured week');
    }
  });
});
