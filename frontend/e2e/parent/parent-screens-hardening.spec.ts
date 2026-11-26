/**
 * Gaps found reviewing every parent screen: keyboard-only use, a 320px-wide phone, two children,
 * and the copy for each loop state. Real API throughout, except where a state cannot be reached
 * through the loop (needs_attention) and is served as a canned reply.
 */
import { test, expect } from '../fixtures/test';
import { createStudent, seedProgress } from '../fixtures/api';
import { expectNoBannedWords, expectNoViolations, uniqueId } from '../fixtures/parent';
import { chooseChild, expectNoHorizontalScroll, newChild } from '../fixtures/e2e-hardening';

test.describe('Keyboard only: the quick check-in', () => {
  test('rate, choose workload and Send without a pointer', async ({ page, request }) => {
    const kid = await newChild(request, 'kb', { packet: 'legacy', plan: 'awaiting_feedback' });
    await page.goto(`/week/check-in/${kid.id}`);
    await expect(page.getByRole('heading', { level: 1 })).toContainText(kid.name, {
      timeout: 20_000,
    });
    const focused = () =>
      page.evaluate(() => {
        const el = document.activeElement as HTMLInputElement | null;
        return el ? `${el.tagName}:${el.type ?? ''}:${el.name ?? ''}:${el.value ?? ''}` : '';
      });

    // Tab from the top of the page until the first rating gets focus (the back link comes first).
    let n = 0;
    while (!(await focused()).startsWith('INPUT:radio:overall')) {
      await page.keyboard.press('Tab');
      expect(++n, 'tabs needed to reach the rating').toBeLessThan(8);
    }
    await expect(page.getByRole('button', { name: 'Send' })).toBeDisabled();

    await page.keyboard.press('ArrowDown'); // Got it -> Shaky
    await expect(page.getByRole('radio', { name: /Shaky/ })).toBeChecked();
    // The focus ring is visible on the choice that has focus.
    await expect(page.locator('label:has(input:focus-visible)')).toHaveCount(1);

    await page.keyboard.press('Tab'); // into the workload group
    expect(await focused()).toContain('radio:workload');
    await page.keyboard.press('ArrowRight'); // Too little -> Just right
    await expect(page.getByRole('radio', { name: 'Just right' })).toBeChecked();

    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', { name: 'Send' })).toBeFocused();
    await expectNoViolations(page);
    await page.keyboard.press('Enter');
    await expect(page.getByRole('status')).toContainText('Thank you!');

    const saved = await (
      await request.get(`/api/students/${kid.id}/weekly-packets/${kid.packetId}/feedback`)
    ).json();
    expect(saved.quick_rating).toBe('mixed');
    expect(saved.quantity_feedback).toBe(0);
  });

  test('the check-by-check cards answer, skip and send from the keyboard', async ({
    page,
    request,
  }) => {
    const kid = await newChild(request, 'kc', { packet: 'week', plan: 'awaiting_feedback' });
    await page.goto(`/week/check-in/${kid.id}/by-check`);
    await expect(page.getByText('Check 1 of 10')).toBeVisible({ timeout: 20_000 });
    await page.getByRole('button', { name: 'Got it' }).focus();
    await page.keyboard.press('Enter'); // answer card 1
    await expect(page.getByText('Check 2 of 10')).toBeVisible();
    await page.getByRole('button', { name: 'Skip this one' }).focus();
    for (let i = 2; i <= 10; i++) {
      await page.keyboard.press('Enter');
    }
    await expect(page.getByRole('heading', { name: 'Ready to send?' })).toBeVisible();
    await page.getByRole('button', { name: 'Send' }).focus();
    await page.keyboard.press('Space');
    await expect(page.getByRole('status')).toContainText('Thank you!');
  });
});

test.describe('A 320px-wide phone: nothing scrolls sideways', () => {
  test.use({ viewport: { width: 320, height: 640 } });

  test('This week, with every loop state on screen', async ({ page, request }) => {
    const states = ['awaiting_feedback', 'awaiting_pick', 'expired', 'ready', 'outlining'];
    const kids = [];
    for (const s of states) kids.push(await newChild(request, 'w3', { plan: s }));
    await page.goto('/week');
    for (const k of kids) {
      await expect(page.locator('[data-testid="child-card"]', { hasText: k.name })).toBeVisible({
        timeout: 20_000,
      });
    }
    await expectNoHorizontalScroll(page, '/week');
    await expectNoViolations(page);
  });

  test('the quick check-in, before and after sending', async ({ page, request }) => {
    const kid = await newChild(request, 'w3q', { packet: 'legacy', plan: 'awaiting_feedback' });
    await page.goto(`/week/check-in/${kid.id}`);
    await expect(page.getByRole('button', { name: 'Send' })).toBeVisible({ timeout: 20_000 });
    await expectNoHorizontalScroll(page, 'quick check-in');
    await page.getByText('Lost it', { exact: true }).click();
    await page.getByText('Too little', { exact: true }).click();
    await expectNoHorizontalScroll(page, 'quick check-in chosen');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByRole('status')).toContainText('Thank you!');
    await expectNoHorizontalScroll(page, 'quick check-in done');
  });

  test('the check-by-check card, review and done screens', async ({ page, request }) => {
    const kid = await newChild(request, 'w3b', { packet: 'week', plan: 'awaiting_feedback' });
    await page.goto(`/week/check-in/${kid.id}/by-check`);
    await expect(page.getByText('Check 1 of 10')).toBeVisible({ timeout: 20_000 });
    await expectNoHorizontalScroll(page, 'by-check card');
    await page.getByRole('button', { name: 'Got it' }).click();
    for (let n = 2; n <= 10; n++) await page.getByRole('button', { name: 'Skip this one' }).click();
    await expect(page.getByRole('heading', { name: 'Ready to send?' })).toBeVisible();
    await expectNoHorizontalScroll(page, 'by-check review');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByRole('status')).toContainText('Thank you!');
    await expectNoHorizontalScroll(page, 'by-check done');
  });

  test('How it’s going, with progress and with the child picker', async ({ page, request }) => {
    const a = await newChild(request, 'w3p');
    seedProgress(a.id);
    await newChild(request, 'w3p');
    await page.goto('/how-its-going');
    await chooseChild(page, a.name);
    await expect(page.getByTestId('progress-sentence')).toContainText(a.name, { timeout: 20_000 });
    await expectNoHorizontalScroll(page, 'progress');
    await expectNoViolations(page);
  });

  test('the empty and error states of both lists', async ({ page }) => {
    await page.route('**/api/this-week', (r) => r.fulfill({ json: { children: [] } }));
    await page.goto('/week');
    await expect(page.getByRole('heading', { name: 'No children yet' })).toBeVisible();
    await expectNoHorizontalScroll(page, '/week empty');
    await page.route('**/api/students', (r) => r.fulfill({ status: 500, body: 'x' }));
    await page.goto('/how-its-going');
    await expect(page.locator('main [role="alert"]')).toBeVisible({ timeout: 25_000 });
    await expectNoHorizontalScroll(page, 'progress error');
  });
});

test.describe('Two children in one family', () => {
  test('This week shows one card each, with the right step and the right link', async ({
    page,
    request,
  }) => {
    const a = await newChild(request, 'ta', { packet: 'legacy', plan: 'awaiting_feedback' });
    const b = await newChild(request, 'tb', { plan: 'ready' });
    await page.goto('/week');
    const cardA = page.locator('[data-testid="child-card"]', { hasText: a.name });
    const cardB = page.locator('[data-testid="child-card"]', { hasText: b.name });
    await expect(cardA).toBeVisible({ timeout: 20_000 });
    await expect(cardA).toHaveAttribute('data-next-action', 'check_in');
    await expect(cardB).toHaveAttribute('data-next-action', 'print');
    await expect(cardA.getByRole('link', { name: 'Check in' })).toHaveAttribute(
      'href',
      `/week/check-in/${a.id}`
    );
    await expect(cardB.getByRole('link', { name: 'Print it' })).toHaveAttribute(
      'href',
      `/week/print/${b.id}`
    );
    // Neither card shows the other child's name or any last name.
    await expect(cardA).not.toContainText(b.name);
    await expect(cardB).not.toContainText(a.name);
    await expect(page.locator('body')).not.toContainText(a.lastName);
    await expectNoViolations(page);
  });

  test('checking in for one child leaves the other child’s week alone', async ({
    page,
    request,
  }) => {
    const a = await newChild(request, 'tc', { packet: 'legacy', plan: 'awaiting_feedback' });
    const b = await newChild(request, 'td', { packet: 'legacy', plan: 'awaiting_feedback' });
    await page.goto(`/week/check-in/${b.id}`);
    await expect(page.getByRole('heading', { level: 1 })).toContainText(b.name, {
      timeout: 20_000,
    });
    await page.getByText('Got it', { exact: true }).click();
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByRole('status')).toContainText('Thank you!');
    const fb = (kid: { id: string; packetId: string }) =>
      request.get(`/api/students/${kid.id}/weekly-packets/${kid.packetId}/feedback`);
    expect((await (await fb(b)).json()).quick_rating).toBe('smooth');
    const other = await fb(a);
    // Nothing was recorded for the other child.
    expect(other.ok() ? ((await other.json()).quick_rating ?? null) : null).toBeNull();
  });

  test('How it’s going has a child picker; each child shows only their own progress', async ({
    page,
    request,
  }) => {
    const a = await newChild(request, 'pa');
    const b = await newChild(request, 'pb');
    seedProgress(a.id);
    await page.goto('/how-its-going');
    await chooseChild(page, a.name);
    await expect(page.getByTestId('progress-sentence')).toContainText(`${a.name} has`);
    await chooseChild(page, b.name);
    await expect(
      page.getByRole('heading', { name: `Nothing to show for ${b.name} yet` })
    ).toBeVisible();
    await expect(page.locator('body')).not.toContainText(`${a.name} has`);
    await chooseChild(page, a.name);
    await expect(page.getByTestId('progress-sentence')).toContainText(`${a.name} has`);
    await expectNoBannedWords(page);
  });
});

test.describe('Loop-state copy', () => {
  const COPY = [
    ['awaiting_feedback', 'A quick check-in helps us plan what comes next.'],
    ['outlining', 'This takes a few minutes. We’ll let you know when it’s ready.'],
    ['awaiting_pick', 'Three ideas are ready for you.'],
    ['expired', 'Those ideas ran out of time. We’ll write fresh ones.'],
    ['authoring', 'This takes a few minutes. We’ll let you know when it’s ready.'],
    ['ready', 'Print it and you’re set for Monday.'],
    ['printed', 'Nothing to do right now.'],
  ] as const;

  for (const [status, body] of COPY) {
    test(`"${status}" tells the parent: ${body}`, async ({ page, request }) => {
      const kid = await newChild(request, 'cp', { plan: status });
      await page.goto('/week');
      const card = page.locator('[data-testid="child-card"]', { hasText: kid.name });
      await expect(card).toBeVisible({ timeout: 20_000 });
      await expect(card).toContainText(body);
      await expect(card).not.toContainText('closer look'); // no alarm without a flag
    });
  }

  test('a week that needs attention says so calmly and asks for nothing', async ({ page }) => {
    await page.route('**/api/this-week', (r) =>
      r.fulfill({
        json: {
          children: [
            {
              student_id: 'zed',
              first_name: 'Zed',
              plan_id: 'p1',
              week_start: '2099-01-05',
              next_action: 'writing',
              options_expired: false,
              needs_attention: true,
              pick_deadline: null,
              print_deadline: null,
              packet_id: null,
              feedback_packet_id: null,
            },
          ],
        },
      })
    );
    await page.goto('/week');
    const card = page.locator('[data-testid="child-card"]', { hasText: 'Zed' });
    await expect(card).toContainText('You don’t need to do anything.', { timeout: 20_000 });
    await expect(
      card.getByRole('link').filter({ hasNotText: /^(Past weeks|How it’s going)$/ })
    ).toHaveCount(0);
    await expectNoViolations(page);
    await expectNoBannedWords(page);
  });

  test('a child with no packet yet reads the week-of date as plain words', async ({
    page,
    request,
  }) => {
    const id = uniqueId('cd');
    await createStudent(request, id, { name: 'Dated Child', birthday: '2018-03-04' });
    await page.goto('/week');
    await expect(page.getByText(/Week of [A-Z][a-z]+ \d{1,2}/).first()).toBeVisible({
      timeout: 20_000,
    });
  });
});

test.describe('Desktop width: the header navigation replaces the tab bar', () => {
  test('the header links mark the current page and reach the other screens', async ({
    page,
    isMobile,
  }) => {
    test.skip(isMobile, 'phone-width uses the tab bar, covered in parent-shell.spec.ts');
    await page.route('**/api/this-week', (r) => r.fulfill({ json: { children: [] } }));
    await page.goto('/week');
    await expect(page.getByTestId('tab-bar')).toBeHidden();
    const nav = page.getByRole('navigation', { name: 'Main' }).first();
    await expect(nav.locator('a[aria-current="page"]')).toHaveText('This week');
    await nav.getByRole('link', { name: 'How it’s going' }).click();
    await expect(page).toHaveURL(/\/how-its-going$/, { timeout: 30_000 });
    await expect(
      page.getByRole('navigation', { name: 'Main' }).first().locator('a[aria-current="page"]')
    ).toHaveText('How it’s going');
    await expectNoViolations(page);
  });
});
