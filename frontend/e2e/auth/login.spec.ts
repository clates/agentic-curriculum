/**
 * Login (M7 stopgap): runs on the phone against a backend started with AUTH_REQUIRED=1.
 * Accounts are made with the real command line tool; every test has its own account and address.
 */
import { test, expect, signIn, sessionCookie, PASSWORD, COOKIE } from '../fixtures/auth';
import { expectNoViolations, expectNoBannedWords } from '../fixtures/parent';
import { shot } from '../fixtures/shots';

test.describe('Landing and signing in', () => {
  test('the first page is the login form, accessibly and in plain words', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();
    await expect(page.getByLabel('Username')).toBeFocused();
    await expect(page.getByLabel('Username')).toHaveAttribute('autocomplete', 'username');
    await expect(page.getByLabel('Password', { exact: true })).toHaveAttribute(
      'autocomplete',
      'current-password'
    );
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm7-login-landing');
  });

  test('signing in lands on This week', async ({ page, account }) => {
    await page.goto('/');
    await signIn(page, account);
    await expect(page).toHaveURL(/\/week$/);
    await expect(page.getByRole('heading', { name: 'No children yet' })).toBeVisible();
    const cookie = await sessionCookie(page.context());
    expect(cookie?.httpOnly).toBe(true);
    expect(cookie?.sameSite).toBe('Lax');
    await shot(page, 'm7-login-signed-in');
  });

  test('the username ignores capital letters and spaces around it', async ({ page, account }) => {
    await page.goto('/login');
    await signIn(page, { ...account, username: `  ${account.username.toUpperCase()} ` });
    await expect(page).toHaveURL(/\/week$/);
  });

  test('a wrong password gets a calm message, keeps the username and returns focus', async ({
    page,
    account,
  }) => {
    await page.goto('/login');
    await signIn(page, { ...account, password: 'not the right one' });
    await expect(page.locator('#login-message')).toHaveText('That didn’t match. Try again.');
    await expect(page.getByLabel('Username')).toHaveValue(account.username);
    await expect(page.getByLabel('Password', { exact: true })).toBeFocused();
    await expect(page.getByLabel('Password', { exact: true })).toHaveValue('');
    expect(await sessionCookie(page.context())).toBeUndefined();
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm7-login-wrong');
  });

  test('an unknown username gets exactly the same message', async ({ page }) => {
    await page.goto('/login');
    await signIn(page, { username: 'nobody_here', password: PASSWORD });
    await expect(page.locator('#login-message')).toHaveText('That didn’t match. Try again.');
  });

  test('show and hide the password', async ({ page }) => {
    await page.goto('/login');
    const field = page.getByLabel('Password', { exact: true });
    await field.fill('secret words here');
    await expect(field).toHaveAttribute('type', 'password');
    await page.getByRole('button', { name: 'Show password' }).click();
    await expect(field).toHaveAttribute('type', 'text');
    await page.getByRole('button', { name: 'Hide password' }).click();
    await expect(field).toHaveAttribute('type', 'password');
  });

  test('keyboard only: type, Tab, type, Enter', async ({ page, account }) => {
    await page.goto('/login');
    await expect(page.getByLabel('Username')).toBeFocused();
    await page.keyboard.type(account.username);
    await page.keyboard.press('Tab');
    await expect(page.getByLabel('Password', { exact: true })).toBeFocused();
    await page.keyboard.type(account.password);
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL(/\/week$/);
  });

  test('loading: the button is disabled and says so while the sign-in is sent', async ({
    page,
    account,
  }) => {
    let release: () => void = () => {};
    const gate = new Promise<void>((r) => (release = r));
    await page.route('**/api/auth/login', async (route) => {
      await gate;
      await route.continue();
    });
    await page.goto('/login');
    await signIn(page, account);
    const button = page.getByRole('button', { name: 'Signing in…' });
    await expect(button).toBeDisabled();
    await expectNoViolations(page);
    await shot(page, 'm7-login-loading');
    release();
    await expect(page).toHaveURL(/\/week$/);
  });

  test('error with retry: a failed call says so plainly and Try again works', async ({
    page,
    account,
  }) => {
    let fail = true;
    await page.route('**/api/auth/login', async (route) => {
      if (fail) await route.fulfill({ status: 502, json: { error: 'down' } });
      else await route.continue();
    });
    await page.goto('/login');
    await signIn(page, account);
    await expect(page.locator('#login-message')).toContainText('We couldn’t sign you in just now');
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm7-login-error');
    fail = false;
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page).toHaveURL(/\/week$/);
  });
});

test.describe('Going to a page you were not signed in for', () => {
  test('a deep link goes to the login and comes back to the same page after signing in', async ({
    page,
    account,
  }) => {
    await page.goto('/week/check-in/some-child');
    await expect(page).toHaveURL(/\/login\?next=%2Fweek%2Fcheck-in%2Fsome-child$/);
    await signIn(page, account);
    await expect(page).toHaveURL(/\/week\/check-in\/some-child$/);
  });

  test('a link that would leave the site is ignored after signing in', async ({
    page,
    account,
    baseURL,
  }) => {
    // Raw query strings, exactly as an attacker would write them: browsers drop tabs and
    // newlines inside a URL and read a backslash as a slash, so these all mean "//evil.example".
    const raw = [
      '/%09/evil.example',
      '/%0a/evil.example',
      '/%0d/evil.example',
      '/%5cevil.example',
      '/%09%5cevil.example',
      '//evil.example',
      'https://evil.example',
      '/%00/evil.example',
      '/..//evil.example',
      '/.//evil.example',
      '/a/..//evil.example',
      '/%2e%2e//evil.example',
      '/%2E%2E//evil.example',
      '/a/%2e%2e//evil.example',
      '/.%2e//evil.example',
      '/%2f/evil.example',
    ];
    for (const bad of raw) {
      await page.context().clearCookies();
      await page.goto(`/login?next=${bad}`);
      await signIn(page, account);
      await expect(page).toHaveURL(`${baseURL}/week`);
      expect(new URL(page.url()).origin).toBe(new URL(baseURL!).origin);
    }
  });

  test('a link to a page on this site keeps its query and anchor', async ({ page, account }) => {
    await page.goto('/login?next=%2Fhow-its-going%3Fchild%3Dabc%23top');
    await signIn(page, account);
    await expect(page).toHaveURL(/\/how-its-going\?child=abc#top$/);
  });

  test('without a session the API says 401 in JSON, and the health check stays open', async ({
    request,
  }) => {
    const students = await request.get('/api/students');
    expect(students.status()).toBe(401);
    expect(await students.json()).toEqual({ detail: 'not_authenticated' });
    expect((await request.get('/api/this-week')).status()).toBe(401);
    expect((await request.post('/api/students', { data: {} })).status()).toBe(401);
    expect((await request.get('/api/health')).status()).toBe(200);
    expect((await request.get('/api/version')).status()).toBe(200);
  });

  test('a stale session cookie sends the page back to the login, then on to where it was', async ({
    page,
    account,
    baseURL,
  }) => {
    await page.context().addCookies([{ name: COOKIE, value: 'stale-or-forged', url: baseURL! }]);
    await page.goto('/week');
    await expect(page).toHaveURL(/\/login\?next=%2Fweek$/);
    await expect(page.getByLabel('Username')).toBeVisible();
    await signIn(page, account);
    await expect(page).toHaveURL(/\/week$/);
  });

  test('a session that ends on the server while a page is open goes back to the login', async ({
    page,
    account,
    playwright,
    baseURL,
  }) => {
    await page.goto('/login');
    await signIn(page, account);
    await expect(page.getByRole('heading', { name: 'No children yet' })).toBeVisible();
    const token = (await sessionCookie(page.context()))!.value;
    // End that session from the side, as the owner disabling the account would.
    const side = await playwright.request.newContext({ baseURL });
    const out = await side.post('/api/auth/logout', { headers: { cookie: `${COOKIE}=${token}` } });
    expect(out.ok()).toBe(true);
    await side.dispose();
    await page.getByRole('link', { name: 'How it’s going' }).first().click();
    await expect(page).toHaveURL(/\/login\?next=/);
    await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();
  });
});

test.describe('Signing out', () => {
  test('Sign out ends the session and the next visit needs the login again', async ({
    page,
    account,
  }) => {
    await page.goto('/login');
    await signIn(page, account);
    await expect(page).toHaveURL(/\/week$/);
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm7-login-sign-out-control');
    await page.getByRole('button', { name: 'Sign out' }).click();
    await expect(page).toHaveURL(/\/login$/);
    expect(await sessionCookie(page.context())).toBeUndefined();
    await page.goto('/week');
    await expect(page).toHaveURL(/\/login\?next=%2Fweek$/);
  });
});

test.describe('Too many wrong tries', () => {
  test('four wrong tries, then a calm wait; after the wait the right password works', async ({
    page,
    account,
  }) => {
    await page.goto('/login');
    for (let i = 0; i < 4; i++) {
      await signIn(page, { ...account, password: `wrong password ${i}` });
      await expect(page.locator('#login-message')).toHaveText('That didn’t match. Try again.');
    }
    await signIn(page, account); // the right password, but the wait has started
    const alert = page.locator('#login-message');
    await expect(alert).toHaveText(/^Too many tries\. Please wait \d+ seconds?\.$/);
    await expect(page.getByRole('button', { name: 'Sign in' })).toBeDisabled();
    expect(await sessionCookie(page.context())).toBeUndefined();
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm7-login-locked');
    // The short test-only backoff makes the wait about 3 seconds.
    await page.getByLabel('Password', { exact: true }).fill(account.password);
    await expect(page.getByRole('button', { name: 'Sign in' })).toBeEnabled({ timeout: 10_000 });
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page).toHaveURL(/\/week$/);
  });

  test('the API answers 429 with a Retry-After, and never says whether the name exists', async ({
    request,
    account,
  }) => {
    const ip = '10.99.1.1';
    const post = (username: string, password: string) =>
      request.post('/api/auth/login', {
        data: { username, password },
        headers: { 'x-forwarded-for': ip },
      });
    for (const name of [account.username, `ghost_${account.username}`]) {
      for (let i = 0; i < 4; i++) expect((await post(name, 'wrong password!!')).status()).toBe(401);
      const locked = await post(name, account.password);
      expect(locked.status()).toBe(429);
      expect(Number(locked.headers()['retry-after'])).toBeGreaterThan(0);
      expect((await locked.json()).detail).toBe('too_many_attempts');
    }
  });

  test('someone guessing from one address cannot lock the owner out from another', async ({
    request,
    account,
  }) => {
    const as = (ip: string, password: string) =>
      request.post('/api/auth/login', {
        data: { username: account.username, password },
        headers: { 'x-forwarded-for': ip },
      });
    for (let i = 0; i < 6; i++) await as('10.77.0.1', 'wrong password!!');
    expect((await as('10.77.0.1', account.password)).status()).toBe(429);
    const owner = await as('10.77.0.2', account.password);
    expect(owner.status()).toBe(200);
    expect(owner.headers()['set-cookie']).toMatch(/HttpOnly/i);
    expect(owner.headers()['set-cookie']).toMatch(/SameSite=lax/i);
  });

  test('a sign-in from another website is refused', async ({ request, account }) => {
    const r = await request.post('/api/auth/login', {
      data: { username: account.username, password: account.password },
      headers: { origin: 'https://evil.example' },
    });
    expect(r.status()).toBe(403);
  });

  test('the address used for the lock is the one our own proxy added, not one the visitor wrote', async ({
    request,
    account,
  }) => {
    const ours = '10.88.0.1';
    const post = (invented: string, password: string) =>
      request.post('/api/auth/login', {
        data: { username: account.username, password },
        // what a front proxy produces when a visitor sends their own X-Forwarded-For
        headers: { 'x-forwarded-for': `${invented}, ${ours}` },
      });
    for (let i = 0; i < 4; i++) {
      expect((await post(`198.51.100.${i + 1}`, 'wrong password!!')).status()).toBe(401);
    }
    // a fifth made-up leftmost address does not escape the lock on the real one
    expect((await post('198.51.100.200', account.password)).status()).toBe(429);
  });
});

test.describe('Busy and oversized requests', () => {
  test('a busy answer is calm and has a Try again that works', async ({ page, account }) => {
    let busy = true;
    await page.route('**/api/auth/login', async (route) => {
      if (busy)
        await route.fulfill({
          status: 503,
          headers: { 'retry-after': '3' },
          json: { detail: 'busy', retry_after: 3 },
        });
      else await route.continue();
    });
    await page.goto('/login');
    await signIn(page, account);
    await expect(page.locator('#login-message')).toHaveText(
      'Busy right now. Please try again in a moment.'
    );
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await shot(page, 'm7-login-busy');
    busy = false;
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page).toHaveURL(/\/week$/);
  });

  test('a sign-in body over 16 KiB is refused with 413 before it is read', async ({ request }) => {
    const r = await request.post('/api/auth/login', {
      data: { username: 'a', password: 'x'.repeat(20_000) },
    });
    expect(r.status()).toBe(413);
  });

  test('a mistyped value is never echoed back in an error', async ({ request }) => {
    const r = await request.post('/api/auth/login', { data: { username: 'only-a-name-here' } });
    expect(r.status()).toBe(422);
    expect(await r.text()).not.toContain('only-a-name-here');
  });
});
