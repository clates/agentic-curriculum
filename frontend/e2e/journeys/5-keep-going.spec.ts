/**
 * Journey 5 — Keep going
 *
 * Week after week, the parent comes back to the dashboard. It should give an honest picture of
 * where each child stands, and the next week's plan should respond to what the parent reported.
 *
 * Most of this journey is still ahead of the product. The pending steps below are the target.
 */
import { test, expect } from '../fixtures/test';
import { createStudent, createPacket, submitFeedback } from '../fixtures/api';
import { repeatIdentity } from '../fixtures/e2e-hardening';
import { stubCalls, waitForNtfy } from '../fixtures/stub';

test.describe('5.1 The dashboard tells the truth', () => {
  const STUDENT_ID_0 = 'e2e-dashboard-y3z4';
  let STUDENT_ID = STUDENT_ID_0;
  const NAME_0 = 'Dashboard Student';
  let NAME = NAME_0;

  test.beforeAll(async ({ request }) => {
    ({ id: STUDENT_ID, name: NAME } = repeatIdentity(STUDENT_ID_0, NAME_0));
    // No packet: a child with a pending week gets "Submit Feedback" instead of "Generate Plan".
    await createStudent(request, STUDENT_ID, { name: NAME, birthday: '2019-04-01' });
  });

  test('each child has a card with a "Generate Plan" action', async ({ page }) => {
    await page.goto('/dashboard');
    const card = page.getByRole('heading', { name: NAME }).locator('../../..');
    await expect(card).toBeVisible();
    await expect(card.getByRole('button', { name: 'Generate Plan' })).toBeVisible();
  });

  // Progress currently counts a synthetic "overall" standard (showing "1/1, 100%") and rounds
  // 1015/1016 up to "100% Complete".
  // Unblocked by: real standard ids in feedback (mastery_feedback.overall is synthetic); not built, no card.
  test.fixme('progress counts real standards and never rounds up to 100%', async () => {});
  // "Worksheets Ready" counts every worksheet ever generated, not the ones still waiting to be used.
  // Unblocked by: a per-family stats endpoint. The stat is computed over every child in the shared test
  // database, so a real-API assertion would not be deterministic; the product behavior also does not exist yet.
  test.fixme('"Worksheets Ready" counts only weeks that are still pending', async () => {});
  // Unblocked by: a design for past weeks (no card, no UI today).
  test.fixme('past weeks look different from the current week', async () => {});
});

test.describe('5.2 The next week adapts', () => {
  // One worker runs beforeAll once: feedback must be submitted (and generation triggered) once.
  test.describe.configure({ mode: 'serial' });
  const FED_ID_0 = 'e2e-next-week-fed-a5b6';
  let FED_ID = FED_ID_0;
  const FED_NAME_0 = 'Next Week Student';
  let FED_NAME = FED_NAME_0;
  const BASE_ID_0 = 'e2e-next-week-base-c7d8';
  let BASE_ID = BASE_ID_0;
  const BASE_NAME_0 = 'Steady Workload Student';
  let BASE_NAME = BASE_NAME_0;
  const HEAVY_ID_0 = 'e2e-next-week-heavy-e9f0';
  let HEAVY_ID = HEAVY_ID_0;
  const HEAVY_NAME_0 = 'Heavy Workload Student';
  let HEAVY_NAME = HEAVY_NAME_0;

  test.beforeAll(async ({ request }) => {
    ({ id: FED_ID, name: FED_NAME } = repeatIdentity(FED_ID_0, FED_NAME_0));
    ({ id: BASE_ID, name: BASE_NAME } = repeatIdentity(BASE_ID_0, BASE_NAME_0));
    ({ id: HEAVY_ID, name: HEAVY_NAME } = repeatIdentity(HEAVY_ID_0, HEAVY_NAME_0));
    for (const [id, name, birthday] of [
      [FED_ID, FED_NAME, '2017-05-01'],
      [BASE_ID, BASE_NAME, '2017-06-01'],
      [HEAVY_ID, HEAVY_NAME, '2017-07-01'],
    ]) {
      await createStudent(request, id, { name, birthday });
      await createPacket(request, id, `${id}-pkt-001`);
    }
    // Feedback kicks off background generation of the next plans (trio_generator). The LLM and
    // ntfy calls it makes land on the static stub, never on a real service.
    await submitFeedback(request, FED_ID, `${FED_ID}-pkt-001`, {
      mastery: 'MASTERED',
      quantity: 0,
    });
    await submitFeedback(request, BASE_ID, `${BASE_ID}-pkt-001`, {
      mastery: 'MASTERED',
      quantity: 0,
    });
    // quantity -2 is "Too Much" in the feedback form.
    await submitFeedback(request, HEAVY_ID, `${HEAVY_ID}-pkt-001`, {
      mastery: 'MASTERED',
      quantity: -2,
    });
  });

  test('after feedback, three fresh plans are generated and the parent is notified', async ({
    page,
    request,
  }) => {
    await waitForNtfy(request, `Plans ready for ${FED_NAME}`);

    const calls = await stubCalls(request, { student: FED_ID });
    const scaffolds = calls.filter((c) => c.kind === 'scaffold');
    expect(scaffolds).toHaveLength(3);
    expect(new Set(scaffolds.map((c) => c.subject)).size).toBe(3); // three different subjects
    expect(calls.filter((c) => c.kind === 'day')).toHaveLength(15); // five days each

    // The generated week is waiting on the plans page, with the stub's content.
    await page.goto('/plans');
    await page.getByRole('heading', { name: FED_NAME, exact: true }).click();
    await expect(page.getByRole('dialog').getByText(/E2E STUB WEEK/)).toBeVisible();
  });

  test('after "Too Much" feedback, the next week asks for fewer activities', async ({
    request,
  }) => {
    await waitForNtfy(request, `Plans ready for ${BASE_NAME}`);
    await waitForNtfy(request, `Plans ready for ${HEAVY_NAME}`);

    // The canned reply does not change with the request, so this asserts what the product asked
    // the model for: the scaffold prompt's per-day activity target.
    const asked = async (id: string) =>
      (await stubCalls(request, { student: id, kind: 'scaffold' })).map((c) => c.activities);
    expect(await asked(BASE_ID)).toEqual([3, 3, 3]);
    expect(await asked(HEAVY_ID)).toEqual([2, 2, 2]);
  });

  // Mastery feedback currently lands on a synthetic "overall" standard, and the stub's replies do
  // not depend on which standards were already taught, so there is nothing to observe yet.
  // Unblocked by: real standard ids in feedback plus a stub that varies its reply by taught standards.
  test.fixme('standards rated Mastered are not re-taught next week', async () => {});
});
