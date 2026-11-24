/**
 * The loop console (/loop): see where each child's week is and push it one step.
 *
 * Real API and the static LLM stub; nothing is mocked. There is no worker in this suite, so a
 * queued job stays queued: what is asserted is that the right step happened and the right job was
 * queued, through the same loop code the real loop uses.
 */
import type { Page } from '@playwright/test';
import { test, expect } from '../fixtures/test';
import { expectNoViolations } from '../fixtures/parent';
import { expectNoHorizontalScroll } from '../fixtures/e2e-hardening';
import { shot } from '../fixtures/shots';
import { STUB_FIRST_TITLES, loopEvents, pickChild, planOf } from '../fixtures/pick';
import { seedWeek } from '../fixtures/api';

const card = (page: Page, id: string) =>
  page.locator(`[data-testid="loop-child"][data-student="${id}"]`);
const step = (page: Page, id: string, key: string) =>
  card(page, id).locator(`[data-step="${key}"]`);

async function open(page: Page, id: string) {
  await page.goto('/loop');
  await expect(card(page, id)).toBeVisible({ timeout: 20_000 });
}

test.describe('Loop console', () => {
  test('a week waiting on its check-in can be skipped past, and the outlines are queued', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'loopskip', { status: 'awaiting_feedback' });
    await open(page, kid.id);
    await expect(step(page, kid.id, 'feedback')).toHaveAttribute('data-state', 'current');
    await expect(card(page, kid.id).getByRole('button', { name: 'Pick A' })).toHaveCount(0);

    await card(page, kid.id).getByRole('button', { name: 'Skip check-in' }).click();

    await expect(step(page, kid.id, 'outlines')).toHaveAttribute('data-state', 'current');
    await expect(step(page, kid.id, 'feedback')).toHaveAttribute('data-state', 'done');
    await expect(card(page, kid.id).locator('[data-testid="loop-job"]')).toHaveCount(1);
    await expect(card(page, kid.id).locator('[data-testid="loop-job"]')).toContainText('outline');
    expect((await planOf(request, kid.id)).status).toBe('outlining');
    await shot(page, 'loop-console-outlining');
  });

  test('picking an idea moves the week to authoring and queues exactly one author job', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'looppick', { status: 'awaiting_pick' });
    await open(page, kid.id);
    await expect(card(page, kid.id).locator('[data-testid="loop-idea"]')).toHaveCount(3);
    await expect(step(page, kid.id, 'pick')).toHaveAttribute('data-state', 'current');

    await card(page, kid.id).getByRole('button', { name: 'Pick B' }).click();

    await expect(step(page, kid.id, 'author')).toHaveAttribute('data-state', 'current');
    await expect(card(page, kid.id).getByText('picked', { exact: true })).toBeVisible();
    await expect(card(page, kid.id).locator('[data-testid="loop-job"]')).toHaveCount(1);
    await expect(card(page, kid.id).locator('[data-testid="loop-job"]')).toContainText('author');
    const plan = await planOf(request, kid.id);
    expect([plan.status, plan.picked_option]).toEqual(['authoring', 'b']);
    expect(loopEvents(kid.id).some((e) => e.type === 'pick_made')).toBe(true);
    await shot(page, 'loop-console-authoring');
  });

  test('fresh ideas can be asked for past the parent cap', async ({ page, request }) => {
    const kid = await pickChild(request, 'loopfresh', { status: 'awaiting_pick', progress: true });
    await open(page, kid.id);
    for (let i = 0; i < 3; i++) {
      // a parent gets two per week; the console does not stop at two
      await card(page, kid.id).getByRole('button', { name: 'Fresh ideas' }).click();
      if (i === 0) {
        for (const title of STUB_FIRST_TITLES)
          await expect(card(page, kid.id).getByText(title).first()).toBeVisible({
            timeout: 20_000,
          });
      }
      await expect(card(page, kid.id).getByText('Working…')).toHaveCount(0, { timeout: 20_000 });
    }
    await expect(card(page, kid.id).getByRole('alert')).toHaveCount(0);
    await expect(card(page, kid.id).locator('[data-testid="loop-idea"]')).toHaveCount(3);
  });

  test('feed forward shows which skills the engine would pick, and why', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'loopff', { status: 'awaiting_pick', progress: true });
    await open(page, kid.id);
    await card(page, kid.id).getByRole('button', { name: 'Preview feed forward' }).click();
    const panel = card(page, kid.id).locator('[data-testid="feed-forward"]');
    await expect(panel).toContainText('Week of', { timeout: 20_000 });
    expect(await panel.locator('li').count()).toBeGreaterThan(0);
  });

  test('a child’s weeks can be reset after a confirm, and started again', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'loopreset', { status: 'awaiting_pick' });
    await open(page, kid.id);
    await card(page, kid.id)
      .getByRole('button', { name: /Reset this child.s weeks/ })
      .click();
    await expect(card(page, kid.id).getByText('No week yet')).toHaveCount(0); // not yet: asks first
    await card(page, kid.id).getByRole('button', { name: 'Yes, reset' }).click();
    await expect(card(page, kid.id).getByText('No week yet')).toBeVisible();
    await expect(card(page, kid.id).getByRole('button', { name: 'Skip check-in' })).toBeDisabled();

    await card(page, kid.id).getByRole('button', { name: 'Start a new week' }).click();
    await expect(step(page, kid.id, 'feedback')).toHaveAttribute('data-state', 'current');
  });

  test('an action that is not possible is disabled and says why', async ({ page, request }) => {
    const kid = await pickChild(request, 'loopwhy', { status: 'ready' });
    await open(page, kid.id);
    const pick = card(page, kid.id).getByRole('button', { name: 'Skip check-in' });
    await expect(pick).toBeDisabled();
    await expect(pick).toHaveAttribute('title', /check-in/);
    await expect(card(page, kid.id).getByRole('button', { name: 'Mark printed' })).toBeEnabled();
  });

  test('the console is accessible and does not scroll sideways, even on a phone', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'loopa11y', { status: 'awaiting_pick' });
    await open(page, kid.id);
    await expectNoViolations(page);
    await expectNoHorizontalScroll(page);
    await page.setViewportSize({ width: 360, height: 800 });
    await expectNoHorizontalScroll(page);
    await shot(page, 'loop-console-phone');
  });

  test('each idea shows which skills it covers before you pick it', async ({ page, request }) => {
    const kid = await pickChild(request, 'loopskills', { status: 'awaiting_pick' });
    await open(page, kid.id);
    const idea = card(page, kid.id).locator('[data-testid="loop-idea"]').first();
    await expect(idea).toContainText('Short hands-on tasks');
    await idea.getByText(/1 skill/).click();
    await expect(idea.locator('[data-testid="idea-skills"] li')).toHaveCount(1);
    await expect(idea).toContainText('As the parent sees it: Counting and measuring');
  });

  test('a written week can be reviewed: verdict, documents, day by day, skills', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'loopreview', { status: 'ready' });
    seedWeek(kid.id, `e2e_${kid.id}`);
    await open(page, kid.id);
    const weeks = card(page, kid.id).locator('[data-testid="loop-weeks"]');
    await expect(weeks).toContainText('Week of');
    await weeks.getByRole('button', { name: 'Review this week' }).click();
    const review = card(page, kid.id).locator('[data-testid="week-review"]');
    await expect(review).toContainText('Weather Week', { timeout: 20_000 });
    await expect(review.locator('[data-testid="review-verdict"]')).toHaveText(
      /Looks good|thing(s)? to fix/
    );
    await expect(review.locator('[data-testid="review-days"] tbody tr')).toHaveCount(5);
    await expect(review.locator('[data-testid="review-flags"]')).toContainText('No time estimates');
    const links = review.getByRole('link', { name: /^Open / });
    await expect(links).toHaveCount(3);
    for (const href of await links.evaluateAll((as) => as.map((a) => a.getAttribute('href')))) {
      const res = await page.request.get(href!);
      expect(res.status(), href!).toBe(200);
      expect(await res.text()).toContain('<html');
    }
    await shot(page, 'loop-console-review');
    await weeks.getByRole('button', { name: 'Hide review' }).click();
    await expect(review).toHaveCount(0);
  });

  test('the review stays accessible and does not scroll the page sideways on a phone', async ({
    page,
    request,
  }) => {
    const kid = await pickChild(request, 'loopreviewa11y', { status: 'ready' });
    seedWeek(kid.id, `e2e_${kid.id}`);
    await open(page, kid.id);
    await card(page, kid.id).getByRole('button', { name: 'Review this week' }).click();
    await expect(card(page, kid.id).locator('[data-testid="week-review"]')).toContainText(
      'Weather Week',
      { timeout: 20_000 }
    );
    await expectNoViolations(page);
    await page.setViewportSize({ width: 360, height: 800 });
    await expectNoHorizontalScroll(page);
    await shot(page, 'loop-console-review-phone');
  });
});
