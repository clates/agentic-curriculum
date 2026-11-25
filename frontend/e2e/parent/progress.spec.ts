/**
 * M10.8: plain-language progress on a phone, against the real API with a seeded child.
 * Has down / working on / coming up, plus the last four weeks. No standard ids on screen.
 */
import type { Page } from '@playwright/test';
import { test, expect } from '../fixtures/test';
import { createStudent, seedProgress } from '../fixtures/api';
import { expectNoBannedWords, expectNoViolations, uniqueId } from '../fixtures/parent';
import { shot } from '../fixtures/shots';

/** Open one child's progress. The picker only exists when the family has several children; with
 * one child that child is already showing, so there is nothing to tap. */
async function openChild(page: Page, name: string) {
  const chip = page.getByRole('radio', { name, exact: true });
  await expect(page.getByRole('heading', { name: 'How it’s going' })).toBeVisible({
    timeout: 20_000,
  });
  await expect(
    page.getByTestId('progress-sentence').or(page.locator('main h2')).first()
  ).toBeVisible({
    timeout: 20_000,
  });
  if (await chip.count()) await chip.check({ force: true });
}

async function seedChild(request: Parameters<typeof createStudent>[0], prefix: string) {
  const id = uniqueId(prefix);
  const name = `Kid${id.replace(/[^a-z0-9]/gi, '')}`;
  await createStudent(request, id, { name: `${name} Testerson`, birthday: '2018-03-04' });
  return { id, name };
}

test.describe('How it’s going (real API)', () => {
  test('shows what the child has down, is working on and has coming up', async ({
    page,
    request,
  }) => {
    const { id, name } = await seedChild(request, 'pg');
    seedProgress(id);

    await page.goto('/how-its-going');
    await openChild(page, name); // several children share the test database: pick ours

    await expect(page.getByTestId('progress-sentence')).toContainText(
      `${name} has 2 skills going well`,
      { timeout: 20_000 }
    );
    await expect(page.getByRole('heading', { name: `What ${name} has down` })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'What we are working on' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Coming up' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'The last four weeks' })).toBeVisible();
    await expect(page.getByText('4 skills checked')).toBeVisible();
    await expect(page.getByText('Was tricky last time, so it is worth another go')).toBeVisible();

    // No curriculum ids and no technical terms anywhere on the page.
    await expect(page.locator('body')).not.toContainText(/\bVA\.[A-Z]+\./);
    await expect(page.locator('body')).not.toContainText('Testerson');
    await expectNoBannedWords(page);
    await expectNoViolations(page);
    await shot(page, 'm10-8-progress');
  });

  test('a child with no history sees what will appear and when', async ({ page, request }) => {
    const { name } = await seedChild(request, 'pn');
    await page.goto('/how-its-going');
    await openChild(page, name);
    await expect(
      page.getByRole('heading', { name: `Nothing to show for ${name} yet` })
    ).toBeVisible();
    await expectNoViolations(page);
    await shot(page, 'm10-8-empty');
  });

  test('no children shows an empty state with a way forward', async ({ page }) => {
    await page.route('**/api/students', (r) => r.fulfill({ json: [] }));
    await page.goto('/how-its-going');
    await expect(page.getByRole('heading', { name: 'No children yet' })).toBeVisible({
      timeout: 20_000,
    });
    await expect(page.getByRole('link', { name: 'Add a child' })).toBeVisible();
    await expectNoViolations(page);
  });

  test('a failure gets a plain message and a retry that works', async ({ page }) => {
    let fail = true;
    await page.route('**/api/students', (r) =>
      r.fulfill({
        json: [
          {
            student_id: 'erin',
            progress_blob: null,
            plan_rules_blob: null,
            metadata_blob: JSON.stringify({ name: 'Erin Tester', birthday: '2018-01-01' }),
          },
        ],
      })
    );
    await page.route('**/api/students/erin/progress-summary', (r) =>
      fail
        ? r.fulfill({ status: 500, body: 'x' })
        : r.fulfill({
            json: {
              student_name: 'Erin',
              summary: 'Erin has no progress recorded yet.',
              solid: [],
              shaky: [],
              needs_work: [],
              due_for_review: [],
              last_four_weeks: {
                skills_checked: 0,
                went_well: [],
                still_shaky: [],
                needs_work: [],
              },
            },
          })
    );
    await page.goto('/how-its-going');
    await expect(page.locator('main [role="alert"]')).toContainText('We couldn’t load this', {
      timeout: 25_000,
    });
    await expectNoViolations(page);
    await shot(page, 'm10-8-error');
    fail = false;
    await page.getByRole('button', { name: 'Try again' }).click();
    await expect(page.getByRole('heading', { name: 'Nothing to show for Erin yet' })).toBeVisible();
  });

  test('the tab bar reaches it from This week', async ({ page }) => {
    await page.goto('/week');
    await page.getByTestId('tab-bar').getByRole('link', { name: 'How it’s going' }).click();
    await expect(page).toHaveURL(/\/how-its-going$/, { timeout: 30_000 });
    await expect(page.getByTestId('tab-bar').locator('a[aria-current="page"]')).toHaveText(
      'How it’s going'
    );
  });
});
