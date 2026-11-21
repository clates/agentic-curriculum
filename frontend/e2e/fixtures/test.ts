import { test as base, expect } from '@playwright/test';
import { stubProblems } from './stub';

/**
 * Shared `test` for every journey spec.
 *
 * Any uncaught page error fails the test that caused it. A journey that "passes" while the page
 * throws behind the scenes (e.g. React #185, an infinite render loop) is not a passing journey.
 */
export const test = base.extend<{
  failOnPageError: void;
  failOnStubProblems: void;
  traceApi: void;
}>({
  traceApi: [
    async ({ page }, use, testInfo) => {
      const log: string[] = [];
      const t0 = Date.now();
      const starts = new Map<string, number>();
      page.on('request', (r) => {
        if (r.url().includes('/api/')) starts.set(r.url() + r.method(), Date.now());
      });
      page.on('requestfinished', async (r) => {
        const s = starts.get(r.url() + r.method());
        if (s) log.push(`${Date.now() - t0}ms ${r.method()} ${r.url()} ${Date.now() - s}ms`);
      });
      page.on('requestfailed', (r) =>
        log.push(`${Date.now() - t0}ms FAILED ${r.url()} ${r.failure()?.errorText}`)
      );
      page.on('response', (r) => {
        if (r.url().includes('/api/') && r.status() >= 400)
          log.push(`${Date.now() - t0}ms HTTP ${r.status()} ${r.url()}`);
      });
      await use();
      if (testInfo.errors.length > 0) {
        const pending = [...starts.entries()].map(([k, v]) => `${k} started ${v - t0}ms`);
        const dlg = await Promise.race([
          page
            .getByRole('dialog')
            .innerText({ timeout: 500 })
            .catch(() => 'no dialog'),
          new Promise<string>((r) => setTimeout(() => r('timeout'), 1500)),
        ]);
        console.log(
          `TRACE-API ${testInfo.title}\nDIALOG: ${dlg}\nSTARTED: ${pending.join('\n')}\n` +
            log.join('\n')
        );
      }
    },
    { auto: true },
  ],
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
