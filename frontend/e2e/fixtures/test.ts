import { test as base, expect } from '@playwright/test';

/**
 * Shared `test` for every journey spec.
 *
 * Any uncaught page error fails the test that caused it. A journey that "passes" while the page
 * throws behind the scenes (e.g. React #185, an infinite render loop) is not a passing journey.
 */
export const test = base.extend<{ failOnPageError: void }>({
  failOnPageError: [
    async ({ page }, use) => {
      const errors: string[] = [];
      page.on('pageerror', (err) => errors.push(err.message));
      await use();
      expect(errors, 'uncaught errors were thrown in the page').toEqual([]);
    },
    { auto: true },
  ],
});

export { expect };
