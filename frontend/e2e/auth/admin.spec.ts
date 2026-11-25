/**
 * The admin panel and the Admin link: only an account with the admin permission sees them.
 * Runs in the login project (AUTH_REQUIRED=1); accounts are made and granted with the real CLI.
 */
import { test, expect, signIn, grant } from '../fixtures/auth';
import { expectNoViolations } from '../fixtures/parent';
import { expectNoHorizontalScroll } from '../fixtures/e2e-hardening';

test.describe('Admin', () => {
  test('a parent without admin sees no Admin link and is sent home from /admin and /loop', async ({
    page,
    account,
  }) => {
    await page.goto('/login');
    await signIn(page, account);
    await expect(page).toHaveURL(/\/week$/);
    await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Admin' })).toHaveCount(0);

    for (const path of ['/admin', '/loop']) {
      await page.goto(path);
      await expect(page).toHaveURL(/\/dashboard$/); // "/" redirects there
      await expect(page.getByRole('heading', { name: 'Loop console' })).toHaveCount(0);
    }
  });

  test('an admin sees the Admin link, opens the panel and reaches the loop console', async ({
    page,
    account,
  }) => {
    grant(account.username, 'admin');
    await page.goto('/login');
    await signIn(page, account);
    await expect(page).toHaveURL(/\/week$/);
    await page.getByRole('link', { name: 'Admin' }).click();
    await expect(page).toHaveURL(/\/admin$/);
    await expect(page.getByRole('heading', { name: 'Loop console' })).toBeVisible();
    await expect(
      page.getByText('Drive any child\u2019s week through each step of the loop.')
    ).toBeVisible();
    await page.getByRole('link', { name: 'Loop console' }).click();
    await expect(page).toHaveURL(/\/loop$/);
    await expect(page.getByRole('heading', { name: 'Loop console', level: 1 })).toBeVisible();
  });

  test('the console API answers 404 to a non-admin', async ({ page, account }) => {
    await page.goto('/login');
    await signIn(page, account);
    await expect(page).toHaveURL(/\/week$/);
    const res = await page.request.get('/api/loop-admin/overview');
    expect(res.status()).toBe(404);
  });

  test('the admin panel is accessible and does not scroll sideways at 360px', async ({
    page,
    account,
  }) => {
    grant(account.username, 'admin');
    await page.goto('/login');
    await signIn(page, account);
    await expect(page).toHaveURL(/\/week$/);
    await page.goto('/admin');
    await expect(page.getByRole('heading', { name: 'Loop console' })).toBeVisible();
    await expectNoViolations(page);
    await page.setViewportSize({ width: 360, height: 800 });
    await expectNoHorizontalScroll(page);
  });
});
