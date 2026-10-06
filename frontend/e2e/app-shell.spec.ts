/**
 * The app shell: what every journey walks through. Every page loads cleanly with its own title,
 * fits the screen, and can reach every other page, on desktop and on a phone.
 *
 * Runs in both the `desktop` and `mobile` projects (see playwright.config.ts).
 */
import { test, expect } from './fixtures/test';

const PAGES = [
  { path: '/dashboard', link: 'Dashboard', title: /Parent Dashboard/ },
  { path: '/students', link: 'Students', title: /^Students/ },
  { path: '/plans', link: 'Plans', title: /^Weekly Plans/ },
  { path: '/progress', link: 'Progress Map', title: /^Progress Map/ },
];

test.describe('Every page', () => {
  for (const { path, title } of PAGES) {
    test(`${path} loads with its own title and no horizontal scroll`, async ({ page }) => {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveTitle(title);
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth
      );
      expect(overflow, 'page is wider than the viewport').toBeLessThanOrEqual(0);
    });
  }

  test('/ sends the parent to the dashboard', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/\/dashboard$/);
  });
});

test.describe('Navigation', () => {
  test('every page is reachable from the header', async ({ page, isMobile }) => {
    await page.goto('/dashboard');
    for (const { path, link } of PAGES) {
      if (isMobile) {
        const toggle = page.getByRole('button', { name: 'Open navigation' });
        await toggle.click();
        await expect(toggle).toHaveAttribute('aria-expanded', 'true');
        await page.locator('#mobile-nav-panel').getByRole('link', { name: link }).click();
        await expect(page.locator('#mobile-nav-panel')).toHaveCount(0);
      } else {
        await page.getByRole('navigation').getByRole('link', { name: link }).click();
      }
      await expect(page).toHaveURL(new RegExp(`${path}$`));
    }
  });

  test('the current page is marked in the header', async ({ page, isMobile }) => {
    await page.goto('/plans');
    if (isMobile) await page.getByRole('button', { name: 'Open navigation' }).click();
    await expect(page.locator('a[aria-current="page"]:visible')).toHaveText('Plans');
  });
});
