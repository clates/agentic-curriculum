/**
 * Creating an account: invite code, emailed 6-digit code, then signed in. Invites are made with the
 * real command line tool; the backend writes its mail to an outbox file the tests read.
 */
import {
  test,
  expect,
  PASSWORD,
  createInvite,
  latestCode,
  mailCount,
  sessionCookie,
  signIn,
} from '../fixtures/auth';
import { expectNoViolations, expectNoBannedWords, uniqueId } from '../fixtures/parent';
import { expectNoHorizontalScroll } from '../fixtures/e2e-hardening';
import type { Page } from '@playwright/test';

async function register(page: Page, email: string) {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Create an account' }).click();
  await page.getByLabel('Family name').fill('The Testers');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password', { exact: true }).fill(PASSWORD);
  await page.getByLabel('Password again').fill(PASSWORD);
  await page.getByLabel('Invite code').fill(createInvite());
  await page.getByRole('button', { name: 'Create account' }).click();
  await expect(page.getByRole('heading', { name: 'Check your email' })).toBeVisible();
}

const newEmail = () => `${uniqueId('fam')}@example.com`.toLowerCase();

test.describe('Creating an account', () => {
  test('register, enter the emailed code and land on This week', async ({ page }) => {
    const email = newEmail();
    await register(page, email);
    const code = await latestCode(email);
    const field = page.getByLabel('6-digit code');
    await field.fill(`${code.slice(0, 3)} ${code.slice(3)}`); // pasted with a space, as mail shows it
    await expect(field).toHaveValue(code);
    await field.fill('');
    await field.pressSequentially(`${code.slice(0, 3)} -${code.slice(3)}9`); // typed, one extra digit
    await expect(field).toHaveValue(code);
    await page.getByRole('button', { name: 'Confirm' }).click();
    await expect(page).toHaveURL(/\/week$/);
    expect((await sessionCookie(page.context()))?.httpOnly).toBe(true);
  });

  test('a wrong code says so and the right one still works', async ({ page }) => {
    const email = newEmail();
    await register(page, email);
    const code = await latestCode(email);
    await page.getByLabel('6-digit code').fill(code === '000000' ? '111111' : '000000');
    await page.getByRole('button', { name: 'Confirm' }).click();
    await expect(page.locator('#main').getByRole('alert')).toHaveText('That code didn’t work');
    await page.getByLabel('6-digit code').fill(code);
    await page.getByRole('button', { name: 'Confirm' }).click();
    await expect(page).toHaveURL(/\/week$/);
  });

  test('"Send a new code" confirms and mails another code', async ({ page }) => {
    const email = newEmail();
    await register(page, email);
    await expect(async () => {
      await page.getByRole('button', { name: 'Send a new code' }).click();
      expect(mailCount(email)).toBeGreaterThan(1); // the cooldown is a few seconds in this project
    }).toPass({ timeout: 30_000, intervals: [3_000] });
    await expect(page.getByRole('status')).toHaveText('A new code is on its way.');
    await page.getByLabel('6-digit code').fill(await latestCode(email));
    await page.getByRole('button', { name: 'Confirm' }).click();
    await expect(page).toHaveURL(/\/week$/);
  });

  test('signing in to an unverified account shows the code step', async ({ page }) => {
    const email = newEmail();
    await register(page, email);
    await page.goto('/login');
    await signIn(page, { username: email, password: PASSWORD });
    await expect(page.getByRole('heading', { name: 'Check your email' })).toBeVisible();
    await page.getByLabel('6-digit code').fill(await latestCode(email));
    await page.getByRole('button', { name: 'Confirm' }).click();
    await expect(page).toHaveURL(/\/week$/);
  });

  test('a bad invite code gets a plain message and no account', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: 'Create an account' }).click();
    await page.getByLabel('Family name').fill('The Testers');
    await page.getByLabel('Email').fill(newEmail());
    await page.getByLabel('Password', { exact: true }).fill(PASSWORD);
    await page.getByLabel('Password again').fill(PASSWORD);
    await page.getByLabel('Invite code').fill('NOTACODE22');
    await page.getByRole('button', { name: 'Create account' }).click();
    await expect(page.locator('#main').getByRole('alert')).toHaveText(
      'That invite code didn’t work.'
    );
  });

  test('both new steps are accessible and do not scroll sideways at 360px', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 740 });
    await page.goto('/login');
    await page.getByRole('button', { name: 'Create an account' }).click();
    await expect(page.getByRole('heading', { name: 'Create your account' })).toBeVisible();
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await expectNoHorizontalScroll(page, 'create an account');
    await register(page, newEmail());
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await expectNoHorizontalScroll(page, 'check your email');
  });
});
