/**
 * First run and "Add a child" with login on: a new family lands on /welcome, fills in the child
 * form and sees the child's card on This week; up to five children; a family that has children is
 * never held on /welcome.
 */
import type { Page } from '@playwright/test';
import { test, expect, PASSWORD, createInvite, latestCode, signIn } from '../fixtures/auth';
import type { Account } from '../fixtures/auth';
import { expectNoViolations, expectNoBannedWords, uniqueId } from '../fixtures/parent';
import { expectNoHorizontalScroll } from '../fixtures/e2e-hardening';

async function registerAndVerify(page: Page) {
  const email = `${uniqueId('fam')}@example.com`.toLowerCase();
  await page.goto('/login');
  await page.getByRole('button', { name: 'Create an account' }).click();
  await page.getByLabel('Family name').fill('The Testers');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password', { exact: true }).fill(PASSWORD);
  await page.getByLabel('Password again').fill(PASSWORD);
  await page.getByLabel('Invite code').fill(createInvite());
  await page.getByRole('button', { name: 'Create account' }).click();
  await page.getByLabel('6-digit code').fill(await latestCode(email));
  await page.getByRole('button', { name: 'Confirm' }).click();
}

async function fillChild(page: Page, name: string) {
  await page.getByLabel('First name').fill(name);
  await page.getByLabel('Interests').fill('dinosaurs, baking , ,soccer');
  await page.getByLabel('Math grade').selectOption('2');
  await page.getByLabel('Reading and writing grade').selectOption('0');
  await page.getByRole('button', { name: 'Save and plan the week' }).click();
}

async function signedInFamily(page: Page, account: Account) {
  await page.goto('/login');
  await signIn(page, account);
  await expect(page).toHaveURL(/\/(welcome|week)$/);
}

const addChildViaApi = (page: Page, name: string) =>
  page.request.post('/api/children', {
    data: { name, interests: [], math_grade: 1, la_grade: 1, notes: '' },
  });

test.describe('Welcome and adding children', () => {
  test('register, verify, land on /welcome, add a child and see their card', async ({ page }) => {
    await registerAndVerify(page);
    await expect(page).toHaveURL(/\/welcome$/);
    await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
    await expect(
      page.getByText("These are starting points. We'll calibrate after the first few activities.")
    ).toBeVisible();
    await expect(page.getByText(/An AI service reads what you write here/)).toBeVisible();
    const sent = page.waitForRequest((r) => r.method() === 'POST' && r.url().endsWith('/children'));
    await fillChild(page, 'Maya');
    expect((await sent).postDataJSON()).toEqual({
      name: 'Maya',
      interests: ['dinosaurs', 'baking', 'soccer'],
      math_grade: 2,
      la_grade: 0,
      notes: '',
    });
    await expect(page).toHaveURL(/\/week$/);
    await expect(page.getByTestId('child-card').filter({ hasText: 'Maya' })).toBeVisible();
  });

  test('interests over the limits get a specific message and send nothing', async ({
    page,
    account,
  }) => {
    await signedInFamily(page, account);
    await page.goto('/welcome');
    let posts = 0;
    page.on('request', (r) => {
      if (r.method() === 'POST' && r.url().endsWith('/children')) posts += 1;
    });
    await page.getByLabel('First name').fill('Maya');
    const interests = page.getByLabel('Interests');
    const save = page.getByRole('button', { name: 'Save and plan the week' });

    await interests.fill('a, b, c, d, e, f, g, h, i');
    await save.click();
    await expect(page.getByText('Please list up to 8 interests.')).toBeVisible();
    await expect(interests).toHaveAttribute('aria-invalid', 'true');
    await expect(interests).toHaveAttribute('aria-describedby', /child-interests-error/);
    await expectNoViolations(page);

    await interests.fill(`dinosaurs, ${'x'.repeat(41)}`);
    await save.click();
    await expect(page.getByText(/Each interest can be up to 40 characters/)).toBeVisible();
    await expect(interests).toHaveAttribute('aria-invalid', 'true');
    expect(posts).toBe(0);

    await interests.fill('dinosaurs, baking');
    await expect(interests).not.toHaveAttribute('aria-invalid', 'true');
    await save.click();
    await expect(page).toHaveURL(/\/week$/);
  });

  test('a 422 from the server says something in the form needs fixing', async ({
    page,
    account,
  }) => {
    await signedInFamily(page, account);
    await page.goto('/welcome');
    await page.route('**/api/children', (route) =>
      route.fulfill({ status: 422, json: { detail: [] } })
    );
    await fillChild(page, 'Maya');
    await expect(page.locator('#main').getByRole('alert')).toContainText(
      'Something in the form needs fixing'
    );
    await expect(page).toHaveURL(/\/welcome$/);
  });

  test('a new family can sign out from /welcome', async ({ page, account }) => {
    await signedInFamily(page, account);
    await page.goto('/welcome');
    await page.getByRole('button', { name: 'Sign out' }).click();
    await expect(page).toHaveURL(/\/login$/);
  });

  test('a signed-in family with no children is sent to /welcome from This week', async ({
    page,
    account,
  }) => {
    await signedInFamily(page, account);
    // The empty state must not flash while the redirect is pending.
    await page.addInitScript(() => {
      const w = window as unknown as { sawEmpty?: boolean };
      new MutationObserver(() => {
        if (document.body?.innerText.includes('No children yet')) w.sawEmpty = true;
      }).observe(document, { childList: true, subtree: true, characterData: true });
    });
    await page.goto('/week');
    await expect(page).toHaveURL(/\/welcome$/);
    expect(await page.evaluate(() => (window as unknown as { sawEmpty?: boolean }).sawEmpty)).toBe(
      undefined
    );
  });

  test('"Add a child" adds a second child; at five the button is gone and a sixth is refused', async ({
    page,
    account,
  }) => {
    await signedInFamily(page, account);
    expect((await addChildViaApi(page, 'Ada')).status()).toBe(201);
    await page.goto('/week');
    await page.getByRole('link', { name: 'Add a child' }).click();
    await expect(page).toHaveURL(/\/children\/new$/);
    await fillChild(page, 'Ben');
    await expect(page).toHaveURL(/\/week$/);
    await expect(page.getByTestId('child-card')).toHaveCount(2);
    await expect(page.getByTestId('child-card').filter({ hasText: 'Ben' })).toBeVisible();

    // The fifth arrives from another tab while the form for a sixth is open.
    for (const n of ['Cy', 'Di']) await addChildViaApi(page, n);
    await page.goto('/week');
    await expect(page.getByTestId('child-card')).toHaveCount(4);
    await page.getByRole('link', { name: 'Add a child' }).click();
    await page.getByLabel('First name').fill('Eve');
    await addChildViaApi(page, 'Eve');
    await page.getByRole('button', { name: 'Save and plan the week' }).click();
    await expect(page.locator('#main').getByRole('alert')).toContainText('up to five children');

    await page.goto('/week');
    await expect(page.getByTestId('child-card')).toHaveCount(5);
    await expect(page.getByRole('link', { name: 'Add a child' })).toHaveCount(0);
    const sixth = await addChildViaApi(page, 'Fay');
    expect(sixth.status()).toBe(409);
    expect(await sixth.json()).toEqual({ detail: 'too_many_children' });
    await page.goto('/children/new');
    await expect(page.getByText(/up to five children/)).toBeVisible();
    await expect(page.getByLabel('First name')).toHaveCount(0);
  });

  test('from the Children tab, adding a child goes to /children/new and back to Children', async ({
    page,
    account,
  }) => {
    await signedInFamily(page, account);
    await addChildViaApi(page, 'Ada');
    await page.goto('/week');
    await page.getByTestId('tab-bar').getByRole('link', { name: 'Children' }).click();
    await expect(page).toHaveURL(/\/students$/);
    await page.getByRole('link', { name: 'Add a child' }).first().click();
    await expect(page).toHaveURL(/\/children\/new\?from=students$/);
    await expect(page.getByLabel('Math grade')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Add Student' })).toHaveCount(0);
    await expect(page.locator('#main').getByRole('link', { name: 'Children' })).toHaveAttribute(
      'href',
      '/students'
    );
    await fillChild(page, 'Ben');
    await expect(page).toHaveURL(/\/students$/);
    await expect(page.getByRole('heading', { name: 'Ben', exact: true })).toBeVisible();
  });

  test('a family with children opening /welcome is sent to This week', async ({
    page,
    account,
  }) => {
    await signedInFamily(page, account);
    await addChildViaApi(page, 'Ada');
    await page.goto('/welcome');
    await expect(page).toHaveURL(/\/week$/);
  });

  test('/welcome and /children/new are accessible and do not scroll sideways at 360px', async ({
    page,
    account,
  }) => {
    await page.setViewportSize({ width: 360, height: 740 });
    await signedInFamily(page, account);
    await page.goto('/welcome');
    await expect(page.getByRole('heading', { name: 'Welcome' })).toBeVisible();
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await expectNoHorizontalScroll(page, 'welcome');
    await addChildViaApi(page, 'Ada');
    await page.goto('/children/new');
    await expect(page.getByLabel('First name')).toBeVisible();
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await expectNoHorizontalScroll(page, 'add a child');
  });
});
