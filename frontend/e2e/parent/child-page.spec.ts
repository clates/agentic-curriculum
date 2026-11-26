/**
 * The family dashboard: a page per child with the weeks already written (and their documents) and
 * a plain-words picture of what the child knows. Reached from the This week card.
 */
import { test, expect } from '../fixtures/test';
import { createStudent, seedProgress, seedWeek } from '../fixtures/api';
import { expectNoHorizontalScroll, newChild } from '../fixtures/e2e-hardening';
import { expectNoBannedWords, expectNoViolations, uniqueId } from '../fixtures/parent';

const NEWER = '2026-01-12';
const OLDER = '2026-01-05';

test.describe('A page for each child', () => {
  test('lists the written weeks newest first, each with its documents', async ({
    page,
    request,
  }) => {
    const kid = await newChild(request, 'cp');
    seedWeek(kid.id, `${kid.packetId}_old`, OLDER);
    seedWeek(kid.id, `${kid.packetId}_new`, NEWER);
    await page.goto(`/children/${kid.id}`);

    await expect(page.getByRole('heading', { level: 1 })).toHaveText(kid.name, {
      timeout: 20_000,
    });
    await expect(page.locator('main')).not.toContainText(kid.lastName);
    const weeks = page.getByTestId('past-week');
    await expect(weeks).toHaveCount(2);
    await expect(weeks.nth(0)).toContainText('January 12');
    await expect(weeks.nth(1)).toContainText('January 5');
    await expect(weeks.nth(0)).toContainText('Weather Week');
    for (const [i, pk] of [`${kid.packetId}_new`, `${kid.packetId}_old`].entries()) {
      const row = weeks.nth(i);
      await expect(row.getByRole('link')).toHaveText([
        `${kid.name}’s pages`,
        'Teacher guide',
        'Prep sheet',
      ]);
      await expect(row.getByRole('link').first()).toHaveAttribute(
        'href',
        `/api/students/${kid.id}/weekly-packets/${pk}/print?doc=packet`
      );
      await expect(row.getByRole('link').nth(1)).toHaveAttribute('href', /doc=guide$/);
      await expect(row.getByRole('link').nth(2)).toHaveAttribute('href', /doc=prep$/);
      await expect(row.getByRole('link').first()).toHaveAttribute('target', '_blank');
    }
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await expectNoHorizontalScroll(page, 'child page');
  });

  test('coverage shows per-subject counts in words', async ({ page, request }) => {
    const id = uniqueId('cpcov');
    const name = `Kid${id.replace(/[^a-z0-9]/gi, '')}`;
    await createStudent(request, id, { name: `${name} Testerson`, birthday: '2018-03-04' });
    seedProgress(id);
    await page.goto(`/children/${id}`);
    const bars = page.getByTestId('coverage-subject');
    await expect(bars.first()).toBeVisible({ timeout: 20_000 });
    const text = (await bars.allInnerTexts()).join('\n');
    expect(text).toMatch(/\d+ solid/);
    expect(text).toMatch(/\d+ still to come/);
    await expect(page.locator('main')).not.toContainText(/[A-Z]{2,}\.\d/);
    await expectNoViolations(page);
    await expectNoBannedWords(page);
    await expectNoHorizontalScroll(page, 'coverage');
  });

  test('a child with no history shows an empty past-weeks state', async ({ page, request }) => {
    const kid = await newChild(request, 'cpnew');
    await page.goto(`/children/${kid.id}`);
    await expect(page.getByTestId('past-weeks-empty')).toBeVisible({ timeout: 20_000 });
    await expect(page.getByTestId('past-week')).toHaveCount(0);
    await expect(page.getByTestId('coverage-subject').first()).not.toContainText(/[1-9] solid/);
    await expectNoViolations(page);
  });

  test('an unknown child says so, in plain words', async ({ page }) => {
    await page.goto('/children/no-such-child');
    await expect(page.getByRole('heading', { name: 'We couldn’t find that child' })).toBeVisible({
      timeout: 20_000,
    });
    await expectNoViolations(page);
  });

  test('works at 360px', async ({ page, request }) => {
    await page.setViewportSize({ width: 360, height: 740 });
    const kid = await newChild(request, 'cp360');
    seedWeek(kid.id, kid.packetId, OLDER);
    seedProgress(kid.id);
    await page.goto(`/children/${kid.id}`);
    await expect(page.getByTestId('past-week')).toHaveCount(1, { timeout: 20_000 });
    await expectNoHorizontalScroll(page, 'child page at 360px');
    await expectNoViolations(page);
  });

  test('the This week card links to the child page', async ({ page, request }) => {
    const kid = await newChild(request, 'cplink', { plan: 'ready' });
    await page.goto('/week');
    const card = page.locator('[data-testid="child-card"]', { hasText: kid.name });
    await expect(card).toBeVisible({ timeout: 20_000 });
    await expect(card.getByRole('link', { name: 'How it’s going' })).toHaveAttribute(
      'href',
      `/children/${kid.id}#coverage`
    );
    await card.getByRole('link', { name: 'Past weeks' }).click();
    await expect(page).toHaveURL(new RegExp(`/children/${kid.id}#past-weeks$`));
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(kid.name);
  });

  test('/children/new still shows the add-a-child form', async ({ page }) => {
    await page.goto('/children/new');
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Add a child', {
      timeout: 20_000,
    });
    await expect(page.getByText('We couldn’t find that child')).toHaveCount(0);
  });
});
