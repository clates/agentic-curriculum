/**
 * Helpers for the login project (e2e/auth/**): its own backend and database, started with
 * AUTH_REQUIRED=1 (see playwright.config.ts).
 *
 * Every test gets its own account and its own client address, so lockout state never leaks between
 * tests running in parallel. The address travels the same way a real visitor's does: as
 * X-Forwarded-For into the Next proxy, which forwards it to the backend.
 */
import { execFileSync } from 'child_process';
import { resolve } from 'path';
import type { BrowserContext, Page } from '@playwright/test';
import { test as base, expect } from './test';
import { uniqueId } from './parent';

const BACKEND_PORT = Number(process.env.E2E_AUTH_BACKEND_PORT ?? 8184);
const DB_FILE = process.env.E2E_AUTH_DB_FILE ?? `/tmp/playwright-auth-${BACKEND_PORT}.db`;
const ROOT = resolve(__dirname, '../../..');

export const PASSWORD = 'correct horse battery';
export const COOKIE = 'curriculum_session';

export interface Account {
  username: string;
  password: string;
}

/** Make an account the way the owner does on the server: with the command line tool. */
export function createAccount(prefix = 'parent'): Account {
  const username = uniqueId(prefix).toLowerCase();
  execFileSync(`${ROOT}/venv/bin/python`, ['-m', 'auth', 'create-user', username], {
    cwd: `${ROOT}/src`,
    env: {
      ...process.env,
      PYTHONPATH: `${ROOT}/src`,
      CURRICULUM_DB_PATH: DB_FILE,
      AUTH_NEW_PASSWORD: PASSWORD,
    },
    stdio: 'pipe',
  });
  return { username, password: PASSWORD };
}

/** Give an account a permission the way the owner does: `python -m auth grant`. */
export function grant(username: string, permission = 'admin') {
  execFileSync(`${ROOT}/venv/bin/python`, ['-m', 'auth', 'grant', username, permission], {
    cwd: `${ROOT}/src`,
    env: { ...process.env, PYTHONPATH: `${ROOT}/src`, CURRICULUM_DB_PATH: DB_FILE },
    stdio: 'pipe',
  });
}

/** A made-up client address, unique to one test. */
export function uniqueIp(): string {
  const r = () => Math.floor(Math.random() * 254) + 1;
  return `10.${r()}.${r()}.${r()}`;
}

export const test = base.extend<{ account: Account; clientIp: string }>({
  clientIp: [
    async ({ context }, use) => {
      const ip = uniqueIp();
      await context.setExtraHTTPHeaders({ 'x-forwarded-for': ip });
      await use(ip);
    },
    { auto: true },
  ],
  account: async ({}, use) => {
    await use(createAccount());
  },
});

export { expect };

/** Type the credentials and press Sign in. */
export async function signIn(page: Page, who: { username: string; password: string }) {
  await page.getByLabel('Username').fill(who.username);
  await page.getByLabel('Password', { exact: true }).fill(who.password);
  await page.getByRole('button', { name: 'Sign in' }).click();
}

export async function sessionCookie(context: BrowserContext) {
  return (await context.cookies()).find((c) => c.name === COOKIE);
}
