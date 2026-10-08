import { test as base, expect } from '@playwright/test';
import { stubProblems } from './stub';

/**
 * Shared `test` for every journey spec.
 *
 * Any uncaught page error fails the test that caused it. A journey that "passes" while the page
 * throws behind the scenes (e.g. React #185, an infinite render loop) is not a passing journey.
 */
export const test = base.extend<{ failOnPageError: void; failOnStubProblems: void }>({
  failOnPageError: [
    async ({ page }, use) => {
      const errors: string[] = [];
      page.on('pageerror', (err) => errors.push(err.message));
      await use();
      expect(errors, 'uncaught errors were thrown in the page').toEqual([]);
    },
    { auto: true },
  ],
  // The backend must only ever talk to the static stub, and the stub must recognise everything it
  // is asked. An unrecognised prompt or a stray API key means the hermetic setup is broken.
  failOnStubProblems: [
    async ({ request }, use) => {
      await use();
      expect(
        await stubProblems(request),
        'LLM stub saw unrecognised or unauthorised calls'
      ).toEqual([]);
    },
    { auto: true },
  ],
});

export { expect };
