/**
 * Every This week card either offers a button that leads somewhere real, or no button at all.
 * The button's href is /week/<next_action with '_' -> '-'>/<student id>.
 *
 * The check-in, pick and print screens all exist, so every card button lands on a real screen.
 */
import { test, expect } from '../fixtures/test';
import { newChild } from '../fixtures/e2e-hardening';

interface State {
  status: string;
  action: string;
  button: string | null;
  /** the path segment the button must point at, if any */
  segment: string | null;
  /** what the destination must show once it is built */
  arrives?: RegExp;
  unbuilt?: string;
}

const STATES: State[] = [
  {
    status: 'awaiting_feedback',
    action: 'check_in',
    button: 'Check in',
    segment: 'check-in',
    arrives: /How was .+ week\?/,
  },
  { status: 'outlining', action: 'writing', button: null, segment: null },
  {
    status: 'awaiting_pick',
    action: 'pick',
    button: 'See the ideas',
    segment: 'pick',
    arrives: /Pick .+ next week/,
  },
  {
    status: 'expired',
    action: 'pick',
    button: 'Get fresh ideas',
    segment: 'pick',
    arrives: /Pick .+ next week/,
  },
  { status: 'authoring', action: 'writing', button: null, segment: null },
  {
    status: 'ready',
    action: 'print',
    button: 'Print it',
    segment: 'print',
    arrives: /^Print .+’s week$/,
  },
  { status: 'printed', action: 'done', button: null, segment: null },
];

test.describe('This week: where each card’s button leads', () => {
  for (const s of STATES) {
    test(`"${s.status}" ${s.button ? `button "${s.button}" leads to a real screen` : 'offers no button'}`, async ({
      page,
      request,
    }) => {
      if (s.unbuilt) test.fail(true, s.unbuilt);
      const kid = await newChild(request, 'dl', { plan: s.status });

      await page.goto('/week');
      const card = page.locator('[data-testid="child-card"]', { hasText: kid.name });
      await expect(card).toBeVisible({ timeout: 20_000 });
      await expect(card).toHaveAttribute('data-next-action', s.action);

      if (!s.button) {
        await expect(card.getByRole('link')).toHaveText(['Past weeks', 'Skills by subject']);
        await expect(card.getByRole('button')).toHaveCount(0);
        return;
      }

      const link = card.getByRole('link', { name: s.button });
      await expect(link).toHaveAttribute('href', `/week/${s.segment}/${kid.id}`);

      // Server answer first (the status the browser would get), then a real click.
      const direct = await request.get(`/week/${s.segment}/${kid.id}`);
      expect(direct.status(), `GET /week/${s.segment}/${kid.id}`).not.toBe(404);

      await link.click();
      await expect(page).toHaveURL(new RegExp(`/week/${s.segment}/${kid.id}$`), {
        timeout: 30_000,
      });
      await expect(page.getByRole('heading', { name: 'Page not found' })).toHaveCount(0);
      if (s.arrives) await expect(page.getByRole('heading', { level: 1 })).toHaveText(s.arrives);
    });
  }
});
