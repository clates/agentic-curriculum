/**
 * Journey 2 — Plan the week
 *
 * The parent asks for a week of lessons for their child, waits for it to generate, and reviews
 * the result: one card per pending week, and a detail view that reads like a lesson plan.
 *
 * Generation runs the real backend against the static LLM stub (e2e/llm-stub), so every plan's
 * content is known: an "E2E STUB WEEK: ..." overview, "Stub <Day> focus", "Stub <Day> objective".
 */
import { test, expect } from '../fixtures/test';
import { createStudent, createPacket } from '../fixtures/api';
import { stubCalls } from '../fixtures/stub';

const WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

type Page = import('@playwright/test').Page;

/** Fill and submit the "Generate Weekly Plan" dialog (already open). */
async function submitGenerateDialog(page: Page, grade: string, subject: string) {
  const dialog = page.getByRole('dialog');
  await dialog.getByLabel('Grade Level').selectOption({ label: grade });
  await dialog.getByLabel('Subject').selectOption({ label: subject });
  await dialog.getByRole('button', { name: 'Generate Plan', exact: true }).click();
}

async function openPendingPlan(page: Page, name: string) {
  await page.goto('/plans');
  await page.getByRole('heading', { name, exact: true }).click();
  const dialog = page.getByRole('dialog');
  await expect(dialog.getByText('Plan Details')).toBeVisible();
  return dialog;
}

test.describe('2.1 Generate a week', () => {
  test.describe.configure({ mode: 'serial' });
  const STUDENT_ID = 'e2e-generate-week-q7r8';
  const NAME = 'Generate Week Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: NAME, birthday: '2017-02-01' });
  });

  test('from the dashboard, "Generate Plan" produces a five-day week', async ({
    page,
    request,
  }) => {
    await page.goto('/dashboard');
    const card = page.getByRole('heading', { name: NAME, exact: true }).locator('../../..');
    await card.getByRole('button', { name: 'Generate Plan' }).click();
    await submitGenerateDialog(page, '3rd Grade', 'Math');
    await expect(page.getByRole('dialog')).not.toBeVisible();

    const modal = await openPendingPlan(page, NAME);
    await expect(modal.getByText(/E2E STUB WEEK: .*Math/)).toBeVisible();
    for (const day of WEEKDAYS) {
      await expect(modal.getByText(`Stub ${day} focus`)).toBeVisible();
      await expect(modal.getByText(`Stub ${day} objective`, { exact: false })).toBeVisible();
    }

    // One scaffold call, then one lesson call per day, all served by the stub.
    const calls = await stubCalls(request, { student: STUDENT_ID });
    expect(calls.filter((c) => c.kind === 'scaffold')).toHaveLength(1);
    expect(calls.filter((c) => c.kind === 'day').map((c) => c.day)).toEqual(
      expect.arrayContaining(WEEKDAYS)
    );
    expect(calls).toHaveLength(6);
  });

  // The Day 1 fallback in #134 appears when a lesson call fails or is unusable. With every call
  // answered by the stub it does not, so this passes today and guards against Monday being
  // special-cased. The fallback itself (on a different day) is covered by 2.1b below.
  test('every day has real content — no generic fallback on Day 1 (#134)', async ({ page }) => {
    const modal = await openPendingPlan(page, NAME);
    await expect(modal.getByText('Stub Monday objective', { exact: false })).toBeVisible();
    await expect(modal.getByText(/Learn about:/)).toHaveCount(0);
    await expect(modal.getByText('Introduce the concept')).toHaveCount(0);
  });

  test('generating the same week twice warns instead of toasting success (#137)', async ({
    page,
  }) => {
    // Desired behaviour per #137. Today POST /generate_weekly_plan silently replaces the existing
    // packet (plan_id = plan_<student>_<monday>, saved with INSERT OR REPLACE) and the UI toasts
    // success, so this fails. Remove test.fail() when #137 is fixed.
    test.fail(true, '#137: duplicate generation is silently accepted');

    await page.goto('/plans');
    await page.getByRole('button', { name: 'Generate New Plan' }).click();
    const dialog = page.getByRole('dialog');
    await dialog.getByLabel('Student').selectOption({ label: NAME });
    await submitGenerateDialog(page, '3rd Grade', 'Math');
    await expect(page.getByText(/already (exists|have)/i)).toBeVisible({ timeout: 5000 });
  });
});

test.describe('2.1b A day the model gets wrong', () => {
  const STUDENT_ID = 'e2e-generate-broken-day-s9t0';
  const NAME = 'Broken Day Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, {
      name: NAME,
      birthday: '2017-04-01',
      stubScenario: 'broken-day=Wednesday',
    });
  });

  test('a day with an unusable reply falls back to a generic lesson; the other days are untouched', async ({
    page,
    request,
  }) => {
    await page.goto('/plans');
    await page.getByRole('button', { name: 'Generate New Plan' }).click();
    await page.getByRole('dialog').getByLabel('Student').selectOption({ label: NAME });
    await submitGenerateDialog(page, '3rd Grade', 'Math');
    await expect(page.getByRole('dialog')).not.toBeVisible();

    const modal = await openPendingPlan(page, NAME);
    for (const day of WEEKDAYS.filter((d) => d !== 'Wednesday')) {
      await expect(modal.getByText(`Stub ${day} objective`, { exact: false })).toBeVisible();
    }
    // Wednesday keeps the scaffold's focus but gets the deterministic generic lesson. Nothing
    // tells the parent this day is a fallback.
    await expect(modal.getByText('Stub Wednesday focus')).toBeVisible();
    await expect(modal.getByText('Stub Wednesday objective', { exact: false })).toHaveCount(0);
    await expect(modal.getByText(/^Learn about: /)).toHaveCount(1);
    await expect(modal.getByText('Introduce the concept')).toHaveCount(1);

    const calls = await stubCalls(request, { student: STUDENT_ID });
    expect(calls.find((c) => c.day === 'Wednesday')?.scenario).toBe('broken-day');
  });
});

test.describe('2.2 A child with no plan yet', () => {
  test.beforeAll(async ({ request }) => {
    await createStudent(request, 'e2e-feedback-empty-a1b2', {
      name: 'Empty State Student',
      birthday: '2018-01-01',
    });
  });

  test('has no pending card on the plans page', async ({ page }) => {
    await page.goto('/plans');
    await expect(page.getByText('Empty State Student')).not.toBeVisible();
  });
});

test.describe('2.3 Review a pending week', () => {
  const STUDENT_ID = 'e2e-feedback-modal-e5f6';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;
  const NAME = 'Detail Modal Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: NAME, birthday: '2018-03-01' });
    await createPacket(request, STUDENT_ID, PACKET_ID);
  });

  const openPlan = async (page: import('@playwright/test').Page) => {
    await page.goto('/plans');
    await page.getByRole('heading', { name: NAME }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    return page.getByRole('dialog');
  };

  test('the pending card summarises subject, grade, and number of days', async ({ page }) => {
    await page.goto('/plans');
    const card = page.getByRole('heading', { name: NAME }).locator('../../..');
    await expect(card.getByText('Mathematics')).toBeVisible();
    await expect(card.getByText('3')).toBeVisible(); // grade_level
    await expect(card.locator('text=Days').locator('..').getByText('2')).toBeVisible();
  });

  test('opening the card shows who, which week, subject, and grade', async ({ page }) => {
    const modal = await openPlan(page);
    await expect(modal.getByText('Plan Details')).toBeVisible();
    await expect(modal.getByText(NAME)).toBeVisible();
    await expect(modal.getByText('Mathematics')).toBeVisible();
    await expect(modal.getByText('Grade Level').locator('..').getByText('3')).toBeVisible();
  });

  test('each day reads as a lesson: focus, objective, procedure', async ({ page }) => {
    const modal = await openPlan(page);
    await expect(modal.getByText('Monday')).toBeVisible();
    await expect(modal.getByText('Introduction', { exact: true })).toBeVisible();
    await expect(modal.getByText('Understand fractions')).toBeVisible();
    await expect(modal.getByText('Read introduction')).toBeVisible();
  });

  test('the detail view closes with Close, Escape, or a backdrop click', async ({ page }) => {
    await openPlan(page);
    await page.getByRole('button', { name: 'Close', exact: true }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();

    await openPlan(page);
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();

    await openPlan(page);
    await page.mouse.click(10, 10);
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });
});
