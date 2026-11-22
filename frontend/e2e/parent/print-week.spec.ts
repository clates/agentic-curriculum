/**
 * M10.7: the print screen, on a phone, against the real API (a stored structured week).
 * This week -> Print it -> three documents opened in new tabs -> "I've printed it" -> all set.
 */
import type { Locator, Page } from '@playwright/test';
import { test, expect } from '../fixtures/test';
import { BACKEND } from '../fixtures/api';
import { WEATHER_WEEK, WEEKDAYS, expectNoHorizontalScroll } from '../fixtures/e2e-hardening';
import { expectNoBannedWords, expectNoViolations } from '../fixtures/parent';
import { PrintChild, nextActionOf, printChild } from '../fixtures/print';
import { shot } from '../fixtures/shots';

const texts = (page: Page, selector: string) =>
  page.locator(selector).evaluateAll((els) => els.map((e) => (e.textContent ?? '').trim()));

/** Click a link that opens a new tab; return that tab once its document has loaded. */
async function openPopup(page: Page, link: Locator) {
  const [popup] = await Promise.all([page.waitForEvent('popup'), link.click()]);
  await popup.waitForLoadState('load');
  return popup;
}

const docLink = (page: Page, doc: 'packet' | 'guide' | 'prep') =>
  page.getByTestId(`doc-${doc}`).getByRole('link', { name: /^Open to print/ });

test.describe('Print screen: the happy path (real week, real API)', () => {
  test('This week -> Print it -> open all three documents -> I’ve printed it -> all set', async ({
    page,
    request,
  }) => {
    const kid = await printChild(request, 'pw');
    await page.goto('/week');
    const card = page.locator('[data-testid="child-card"]', { hasText: kid.name });
    await expect(card).toHaveAttribute('data-next-action', 'print', { timeout: 20_000 });
    await card.getByRole('link', { name: 'Print it' }).click();

    await expect(page).toHaveURL(new RegExp(`/week/print/${kid.id}$`), { timeout: 30_000 });
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(`Print ${kid.name}’s week`);
    await expect(page.getByTestId('week-title')).toHaveText('Weather Week');
    await expect(page.locator('main')).toContainText(
      'Covers Monday, January 5 to Friday, January 9'
    );
    await expect(page.getByTestId('doc-packet')).toBeVisible();
    await expect(page.locator('main')).not.toContainText(kid.lastName);
    // Three labelled documents, in the order we say to print them.
    await expect(
      page.getByRole('list', { name: 'Documents to print' }).getByRole('heading')
    ).toHaveText([`1. ${kid.name}’s pages`, '2. Your teacher guide', '3. Your prep sheet']);
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-7-ready');

    // 1. The student packet: every day's worksheets, no answer key, the child's first name.
    const base = `/api/students/${kid.id}/weekly-packets/${kid.packetId}/print`;
    const packet = await openPopup(page, docLink(page, 'packet'));
    expect(packet.url()).toContain(`${base}?doc=packet`);
    const expected = WEATHER_WEEK.days.flatMap((d) => d.worksheets.map((w) => w.data.title!));
    expect(await texts(packet, '.ws-title')).toEqual(expected);
    const dayLabels = await texts(packet, '.day-header-label');
    for (const day of WEEKDAYS) expect(dayLabels).toContain(day);
    await expect(packet.locator('body')).not.toContainText('Answer Key');
    await expect(packet).toHaveTitle(`Weather Week — Science for ${kid.name}`);
    const packetHtml = await packet.content();
    expect(packetHtml).not.toContain('{{student_name}}');
    expect(packetHtml).not.toContain(kid.lastName);
    await packet.close();

    // 2. The teacher guide: an answer key for every day.
    const guide = await openPopup(page, docLink(page, 'guide'));
    expect(guide.url()).toContain(`${base}?doc=guide`);
    await expect(
      guide.getByRole('heading', { name: /^Answer Key — Reading Questions$/ })
    ).toHaveCount(5);
    const headings = await texts(guide, 'h2, h3');
    for (const day of WEEKDAYS)
      expect(
        headings.some((h) => h.startsWith(`${day} —`)),
        `${day} section`
      ).toBe(true);
    const guideHtml = await guide.content();
    expect(guideHtml).not.toContain('{{student_name}}');
    expect(guideHtml).not.toContain(kid.lastName);
    await guide.close();

    // 3. The prep sheet: every check, with the first name filled in.
    const prep = await openPopup(page, docLink(page, 'prep'));
    expect(prep.url()).toContain(`${base}?doc=prep`);
    await expect(prep.locator('.pc-card')).toHaveCount(WEATHER_WEEK.prep_checks.length);
    expect(await texts(prep, '.pc-prompt')).toEqual(
      WEATHER_WEEK.prep_checks.map((c) =>
        c.prompt.replace(/&amp;/g, '&').replace(/\{\{student_name\}\}/g, kid.name)
      )
    );
    const prepHtml = await prep.content();
    expect(prepHtml).not.toContain('{{student_name}}');
    expect(prepHtml).not.toContain(kid.lastName);
    await prep.close();

    // Opening documents does not by itself mark the week printed.
    expect(await nextActionOf(request, kid.id)).toBe('print');

    await page.getByRole('button', { name: 'I’ve printed it' }).click();
    await expect(page.getByRole('status').filter({ hasText: 'You’re all set' })).toBeVisible();
    await expect(page.getByRole('status')).toContainText(`${kid.name}’s week is printed`);
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-7-confirmed');

    // The server agrees, and the card on This week is now the all-set card.
    await expect.poll(() => nextActionOf(request, kid.id)).toBe('done');
    await page.getByRole('link', { name: 'Back to this week' }).last().click();
    const done = page.locator('[data-testid="child-card"]', { hasText: kid.name });
    await expect(done).toHaveAttribute('data-next-action', 'done', { timeout: 20_000 });
    await expect(done.getByRole('heading')).toHaveText(`${kid.name} is all set`);
    await expect(done.getByRole('link')).toHaveCount(0);
    await shot(page, 'm10-7-this-week-all-set');
  });

  test('a double tap on “I’ve printed it” sends one request', async ({ page, request }) => {
    const kid = await printChild(request, 'pd');
    let posts = 0;
    await page.route('**/api/students/*/week-plans/*/printed', async (route) => {
      posts += 1;
      await new Promise((r) => setTimeout(r, 400)); // keep the first one in flight
      await route.continue();
    });
    await page.goto(`/week/print/${kid.id}`);
    const confirm = page.getByRole('button', { name: 'I’ve printed it' });
    await expect(confirm).toBeEnabled({ timeout: 20_000 });
    await confirm.dblclick();
    await expect(page.getByRole('status').filter({ hasText: 'You’re all set' })).toBeVisible();
    expect(posts).toBe(1);
    expect(await nextActionOf(request, kid.id)).toBe('done');
  });

  test('marking printed through the server twice is harmless; a week not ready is refused', async ({
    request,
  }) => {
    const kid = await printChild(request, 'pa');
    const url = `${BACKEND}/students/${kid.id}/week-plans/${kid.planId}/printed`;
    expect((await request.post(url)).status()).toBe(200);
    const again = await request.post(url);
    expect(again.status()).toBe(200);
    expect((await again.json()).already_printed).toBe(true);

    const early = await printChild(request, 'pa', { status: 'authoring' });
    const refused = await request.post(
      `${BACKEND}/students/${early.id}/week-plans/${early.planId}/printed`
    );
    expect(refused.status()).toBe(409);
    expect(await nextActionOf(request, early.id)).toBe('writing');
  });
});

test.describe('Print screen: other states', () => {
  const NOT_READY: { status: string; reason: RegExp }[] = [
    { status: 'awaiting_feedback', reason: /Check in on .+ last week first/ },
    { status: 'authoring', reason: /We’re still writing .+ week/ },
    { status: 'awaiting_pick', reason: /Pick .+ next week first/ },
  ];
  for (const s of NOT_READY) {
    test(`a child whose week is "${s.status}" is sent back to This week with the reason`, async ({
      page,
      request,
    }) => {
      const kid = await printChild(request, 'pn', { status: s.status });
      await page.goto(`/week/print/${kid.id}`);
      await expect(page.getByRole('heading', { name: 'Nothing to print yet' })).toBeVisible({
        timeout: 20_000,
      });
      await expect(page.locator('main')).toContainText(s.reason);
      await expect(page.getByRole('link', { name: /Open to print/ })).toHaveCount(0);
      await expect(page.getByRole('button', { name: 'I’ve printed it' })).toHaveCount(0);
      await expectNoViolations(page);
      await expectNoBannedWords(page);
      await shot(page, `m10-7-not-ready-${s.status}`);
      await page.getByRole('link', { name: 'Back to this week' }).last().click();
      await expect(page).toHaveURL(/\/week$/);
    });
  }

  test('an already printed week says so and still opens the documents', async ({
    page,
    request,
  }) => {
    const kid = await printChild(request, 'pp', { status: 'printed' });
    await page.goto(`/week/print/${kid.id}`);
    await expect(
      page.getByRole('status').filter({ hasText: 'This week is already printed' })
    ).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByRole('button', { name: 'I’ve printed it' })).toHaveCount(0);
    await expect(page.getByRole('link', { name: /^Open to print/ })).toHaveCount(3);
    const guide = await openPopup(page, docLink(page, 'guide'));
    await expect(guide.getByRole('heading', { name: /Teacher \/ Parent Guide/ })).toBeVisible();
    await guide.close();
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-7-already-printed');
    expect(await nextActionOf(request, kid.id)).toBe('done');
  });

  test('an older (non-structured) week offers only the pages, with no guide or prep sheet', async ({
    page,
    request,
  }) => {
    const kid = await printChild(request, 'pl', { kind: 'legacy' });
    await page.goto(`/week/print/${kid.id}`);
    await expect(page.getByTestId('doc-packet')).toBeVisible({ timeout: 20_000 });
    await expect(page.getByRole('link', { name: /^Open to print/ })).toHaveCount(1);
    await expect(page.getByTestId('doc-guide')).toHaveCount(0);
    await expect(page.getByTestId('doc-prep')).toHaveCount(0);
    await expect(page.locator('main')).toContainText('only has your child’s pages');
    await expect(docLink(page, 'packet')).toHaveAttribute(
      'href',
      `/api/students/${kid.id}/weekly-packets/${kid.packetId}/print?doc=packet`
    );
    // The seeded older packet has no HTML pages on disk, so the server says so plainly (as it
    // does today for the legacy print route); the screen's job is to offer only what exists.
    const guide = await request.get(
      `${BACKEND}/students/${kid.id}/weekly-packets/${kid.packetId}/print?doc=guide`
    );
    expect(guide.status()).toBe(404);
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-7-legacy');
  });

  test('the print-by day is shown in plain words, and a passed one is said gently', async ({
    page,
    request,
  }) => {
    const future = await printChild(request, 'pf', { printDeadline: '2099-01-04' });
    await page.goto(`/week/print/${future.id}`);
    await expect(page.getByTestId('deadline')).toHaveText('Print by Sunday, January 4', {
      timeout: 20_000,
    });
    await expectNoViolations(page);
    await shot(page, 'm10-7-deadline');

    const late = await printChild(request, 'pf', { printDeadline: '2020-01-05' });
    await page.goto(`/week/print/${late.id}`);
    await expect(page.getByTestId('deadline')).toContainText(
      'The print-by day (Sunday, January 5) has passed. You can still print it now.',
      { timeout: 20_000 }
    );
    await expect(page.getByRole('link', { name: /^Open to print/ })).toHaveCount(3);
    await expect(page.getByRole('button', { name: 'I’ve printed it' })).toBeEnabled();
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-7-deadline-passed');
  });

  test('an unknown child gets a plain message and a way back', async ({ page }) => {
    await page.goto('/week/print/nobody_here');
    await expect(page.getByRole('heading', { name: 'We couldn’t find that child' })).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByRole('link', { name: 'Back to this week' })).toBeVisible();
    await expectNoViolations(page);
  });

  test('while the documents load, a polite loading state shows, then the screen', async ({
    page,
    request,
  }) => {
    const kid = await printChild(request, 'pg');
    await page.route('**/print-info', async (route) => {
      await new Promise((r) => setTimeout(r, 1500));
      await route.continue();
    });
    await page.goto(`/week/print/${kid.id}`);
    await expect(page.getByRole('status')).toContainText('Loading the documents', {
      timeout: 20_000,
    });
    await expectNoViolations(page);
    await shot(page, 'm10-7-loading');
    await expect(page.getByTestId('doc-packet')).toBeVisible({ timeout: 20_000 });
  });

  test('if the documents will not load, a plain error with a retry that works', async ({
    page,
    request,
  }) => {
    const kid = await printChild(request, 'pe');
    let fail = true;
    await page.route('**/print-info', (route) =>
      fail ? route.fulfill({ status: 500, body: 'boom' }) : route.continue()
    );
    await page.goto(`/week/print/${kid.id}`);
    const alert = page.locator('main [role="alert"]');
    await expect(alert).toContainText('We couldn’t load the documents', { timeout: 20_000 });
    await expect(page.getByRole('button', { name: 'I’ve printed it' })).toHaveCount(0);
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-7-error-documents');
    fail = false;
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page.getByTestId('doc-packet')).toBeVisible({ timeout: 20_000 });
    await expect(alert).toHaveCount(0);
  });

  test('if the week list will not load, the same plain error and retry', async ({
    page,
    request,
  }) => {
    const kid = await printChild(request, 'pt');
    let fail = true;
    await page.route('**/api/this-week', (route) =>
      fail ? route.fulfill({ status: 500, body: 'boom' }) : route.continue()
    );
    await page.goto(`/week/print/${kid.id}`);
    await expect(page.locator('main [role="alert"]')).toContainText('We couldn’t load this', {
      timeout: 20_000,
    });
    fail = false;
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page.getByTestId('doc-packet')).toBeVisible({ timeout: 20_000 });
  });

  test('if saving “I’ve printed it” fails, nothing is lost and trying again works', async ({
    page,
    request,
  }) => {
    const kid = await printChild(request, 'ps');
    let fail = true;
    await page.route('**/api/students/*/week-plans/*/printed', (route) =>
      fail ? route.fulfill({ status: 500, body: 'boom' }) : route.continue()
    );
    await page.goto(`/week/print/${kid.id}`);
    await page.getByRole('button', { name: 'I’ve printed it' }).click({ timeout: 20_000 });
    await expect(page.locator('main [role="alert"]')).toContainText('We couldn’t save that');
    await expect(page.getByRole('link', { name: /^Open to print/ })).toHaveCount(3); // still there
    expect(await nextActionOf(request, kid.id)).toBe('print');
    await expectNoViolations(page);
    await shot(page, 'm10-7-error-confirm');
    fail = false;
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page.getByRole('status').filter({ hasText: 'You’re all set' })).toBeVisible();
    expect(await nextActionOf(request, kid.id)).toBe('done');
  });
});

test.describe('Print screen: keyboard and small phones', () => {
  test('keyboard only: reach each Open to print link, open one, and confirm', async ({
    page,
    request,
  }) => {
    const kid = await printChild(request, 'pk');
    await page.goto(`/week/print/${kid.id}`);
    await expect(page.getByTestId('doc-packet')).toBeVisible({ timeout: 20_000 });

    const focusedName = () =>
      page.evaluate(() => {
        const el = document.activeElement as HTMLElement | null;
        return (el?.textContent ?? '').trim();
      });
    const tabTo = async (match: RegExp) => {
      for (let i = 0; i < 30; i++) {
        await page.keyboard.press('Tab');
        if (match.test(await focusedName())) return;
      }
      throw new Error(`never focused ${match}`);
    };

    await tabTo(/^Open to print.*pages/);
    const [popup] = await Promise.all([page.waitForEvent('popup'), page.keyboard.press('Enter')]);
    await popup.waitForLoadState('load');
    expect(popup.url()).toContain('?doc=packet');
    await popup.close();
    await page.bringToFront();

    await tabTo(/^Open to print.*guide/i);
    await tabTo(/^Open to print.*prep/i);
    await tabTo(/^I’ve printed it$/);
    await page.keyboard.press('Enter');
    await expect(page.getByRole('status').filter({ hasText: 'You’re all set' })).toBeVisible();
    expect(await nextActionOf(request, kid.id)).toBe('done');
  });

  test.describe('a 320px-wide phone', () => {
    test.use({ viewport: { width: 320, height: 640 } });
    const cases: { label: string; opts: Parameters<typeof printChild>[2] }[] = [
      { label: 'ready, deadline passed', opts: { printDeadline: '2020-01-05' } },
      { label: 'printed', opts: { status: 'printed' } },
      { label: 'older week', opts: { kind: 'legacy' } },
      { label: 'not ready', opts: { status: 'authoring' } },
    ];
    for (const c of cases) {
      test(`nothing scrolls sideways: ${c.label}`, async ({ page, request }) => {
        const kid: PrintChild = await printChild(request, 'p3', c.opts);
        await page.goto(`/week/print/${kid.id}`);
        await expect(page.getByRole('heading').first()).toBeVisible({ timeout: 20_000 });
        await expect(page.getByText('Loading the documents')).toHaveCount(0, { timeout: 20_000 });
        await expectNoHorizontalScroll(page, c.label);
        await expectNoViolations(page);
        await shot(page, `m10-7-320-${c.label.replace(/\W+/g, '-')}`);
      });
    }
  });
});
