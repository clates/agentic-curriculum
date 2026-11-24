/**
 * M10.4: 'This week' against the real API with throwaway seeded children, on a phone.
 * Each loop state shows the one next step for that child.
 */
import { test, expect } from '../fixtures/test';
import { BACKEND, createStudent, seedPlan } from '../fixtures/api';
import { failJob } from '../fixtures/pick';
import { expectNoHorizontalScroll } from '../fixtures/e2e-hardening';
import { expectNoBannedWords, expectNoViolations, uniqueId } from '../fixtures/parent';
import { shot } from '../fixtures/shots';

const CASES = [
  {
    status: 'awaiting_feedback',
    action: 'check_in',
    title: /How was .+ week\?/,
    button: 'Check in',
  },
  { status: 'outlining', action: 'writing', title: /Writing .+ next week/, button: null },
  { status: 'awaiting_pick', action: 'pick', title: /Pick .+ next week/, button: 'See the ideas' },
  { status: 'expired', action: 'pick', title: /Pick .+ next week/, button: 'Get fresh ideas' },
  { status: 'authoring', action: 'writing', title: /Writing .+ next week/, button: null },
  { status: 'ready', action: 'print', title: /.+ week is ready/, button: 'Print it' },
  { status: 'printed', action: 'done', title: /.+ is all set/, button: null },
];

test.describe('This week (real API)', () => {
  for (const c of CASES) {
    test(`a child whose week is "${c.status}" gets one next step`, async ({ page, request }) => {
      const id = uniqueId('tw');
      const name = `Kid${id.replace(/[^a-z0-9]/gi, '')}`;
      await createStudent(request, id, { name: `${name} Testerson`, birthday: '2018-03-04' });
      seedPlan(id, c.status);

      await page.goto('/week');
      const card = page.locator('[data-testid="child-card"]', { hasText: name });
      await expect(card).toBeVisible({ timeout: 20_000 });
      await expect(card).toHaveAttribute('data-next-action', c.action);
      await expect(card.getByRole('heading')).toHaveText(c.title);
      if (c.button) await expect(card.getByRole('link', { name: c.button })).toBeVisible();
      else await expect(card.getByRole('link')).toHaveCount(0);
      await expect(page.locator('body')).not.toContainText('Testerson'); // first name only
      await expectNoViolations(page);
      await expectNoBannedWords(page);
      await shot(page, `m10-4-${c.status}`);
    });
  }

  for (const kind of ['outline', 'author'] as const) {
    test(`a week whose ${kind} job died says we hit a problem, and clears once it is retried`, async ({
      page,
      request,
    }) => {
      const id = uniqueId('tw');
      const name = `Kid${id.replace(/[^a-z0-9]/gi, '')}`;
      await createStudent(request, id, { name: `${name} Testerson`, birthday: '2018-03-04' });
      seedPlan(id, kind === 'outline' ? 'outlining' : 'authoring');
      failJob(id, kind); // a rejected model key, through the real worker

      await page.goto('/week');
      const card = page.locator('[data-testid="child-card"]', { hasText: name });
      await expect(card).toBeVisible({ timeout: 20_000 });
      await expect(card).toHaveAttribute('data-needs-attention', 'true');
      await expect(card.getByRole('heading')).toHaveText(`We hit a problem writing ${name}’s week`);
      await expect(card).toContainText('We’re on it. You don’t need to do anything.');
      await expect(card).not.toContainText('Writing');
      await expect(card.getByRole('link')).toHaveCount(0);
      await expect(page.locator('body')).not.toContainText(/401|OPENROUTER|LLMAuth|outline_failed/);
      await expectNoViolations(page);
      await expectNoBannedWords(page);
      await page.setViewportSize({ width: 360, height: 800 });
      await expectNoHorizontalScroll(page);
      await shot(page, `this-week-problem-${kind}`);

      // the operator retries the dead job from the console's API: the card goes back to "writing"
      const overview = await (await request.get(`${BACKEND}/loop-admin/overview`)).json();
      const mine = overview.children.find((c: { student_id: string }) => c.student_id === id);
      const retry = await request.post(`${BACKEND}/loop-admin/jobs/${mine.plan.jobs[0].id}/retry`);
      expect(retry.ok()).toBeTruthy();
      await page.reload();
      const again = page.locator('[data-testid="child-card"]', { hasText: name });
      await expect(again.getByRole('heading')).toHaveText(`Writing ${name}’s next week`, {
        timeout: 20_000,
      });
      await expect(again).not.toHaveAttribute('data-needs-attention', 'true');
    });
  }

  test('an error from the server shows a plain message with a retry', async ({ page }) => {
    await page.route('**/api/this-week', (r) => r.fulfill({ status: 500, body: 'x' }));
    await page.goto('/week');
    await expect(page.locator('main [role="alert"]')).toContainText('We couldn’t load this', {
      timeout: 20_000,
    });
    await expect(page.getByRole('button', { name: 'Try again' })).toBeVisible();
  });
});
