/**
 * Parent shell (M10.1): runs on the mobile project. The tab bar works, every state a screen can be
 * in (loading, empty, error, filled) passes axe, and no technical term reaches the page.
 */
import AxeBuilder from '@axe-core/playwright';
import type { Page } from '@playwright/test';
import { test, expect } from './fixtures/test';
import { BANNED_WORDS } from '../lib/bannedWords';
import { execFileSync } from 'child_process';
import { shot } from './fixtures/shots';

async function expectNoViolations(page: Page) {
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
  expect(
    results.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target).join(' | ')}`)
  ).toEqual([]);
}

export async function expectNoBannedWords(page: Page) {
  const text = await page.locator('body').innerText();
  const hits = BANNED_WORDS.filter((w) =>
    new RegExp(`(^|[^\\w])${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|[^\\w])`, 'i').test(text)
  );
  expect(hits, 'technical terms on a parent screen').toEqual([]);
}

test.describe('Parent shell', () => {
  test('This week shows an empty state with a next step, accessibly', async ({ page }) => {
    await page.route('**/api/students', (route) => route.fulfill({ json: [] }));
    await page.goto('/week');
    await expect(page.getByRole('heading', { name: 'No children yet' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Add a child' })).toBeVisible();
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-1-empty');
  });

  test('This week shows a loading state, then content', async ({ page }) => {
    let release: () => void = () => {};
    const gate = new Promise<void>((r) => (release = r));
    await page.route('**/api/students', async (route) => {
      await gate;
      await route.fulfill({ json: [] });
    });
    await page.goto('/week');
    await expect(page.getByRole('status')).toContainText('Loading');
    await expectNoViolations(page);
    await shot(page, 'm10-1-loading');
    release();
    await expect(page.getByRole('heading', { name: 'No children yet' })).toBeVisible();
  });

  test('This week shows a plain error with a retry that works', async ({ page }) => {
    let fail = true;
    await page.route('**/api/students', (route) =>
      fail ? route.fulfill({ status: 500, body: 'boom' }) : route.fulfill({ json: [] })
    );
    await page.goto('/week');
    await expect(page.locator('main [role="alert"]')).toContainText('We couldn’t load this', {
      timeout: 20_000,
    });
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm10-1-error');
    fail = false;
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page.getByRole('heading', { name: 'No children yet' })).toBeVisible();
  });

  test('the tab bar is at the bottom, marks the current tab and reaches the other tabs', async ({
    page,
  }) => {
    await page.route('**/api/students', (route) => route.fulfill({ json: [] }));
    await page.goto('/week');
    const bar = page.getByTestId('tab-bar');
    await expect(bar).toBeVisible();
    const box = await bar.boundingBox();
    const viewport = page.viewportSize()!;
    expect(box!.y + box!.height).toBeGreaterThanOrEqual(viewport.height - 1);
    await expect(bar.locator('a[aria-current="page"]')).toHaveText('This week');
    await bar.getByRole('link', { name: 'Children' }).click();
    await expect(page).toHaveURL(/\/students$/, { timeout: 30_000 });
  });
});

test('the banned-words lint passes on all parent copy', () => {
  const out = execFileSync(process.execPath, ['scripts/lint-copy.mjs'], { encoding: 'utf8' });
  expect(out).toContain('clean');
});
