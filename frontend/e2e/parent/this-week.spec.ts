/**
 * M10.4: 'This week' against the real API with throwaway seeded children, on a phone.
 * Each loop state shows the one next step for that child.
 */
import { test, expect } from '../fixtures/test';
import { createStudent, seedPlan } from '../fixtures/api';
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
      else
        await expect(
          card.getByRole('link').filter({ hasNotText: /^(Past weeks|How it’s going)$/ })
        ).toHaveCount(0);
      await expect(page.locator('body')).not.toContainText('Testerson'); // first name only
      await expectNoViolations(page);
      await expectNoBannedWords(page);
      await shot(page, `m10-4-${c.status}`);
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
