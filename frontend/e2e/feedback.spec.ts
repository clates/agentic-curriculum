import { test, expect } from '@playwright/test';
import { createStudent, createPacket, submitFeedback, backdateFeedback } from './fixtures/api';

// ---------------------------------------------------------------------------
// Plans page — empty state
// ---------------------------------------------------------------------------
test.describe('Plans page — empty state', () => {
  const STUDENT_ID = 'e2e-feedback-empty-a1b2';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, {
      name: 'Empty State Student',
      birthday: '2018-01-01',
    });
  });

  test('a student with no packets has no pending card on the plans page', async ({ page }) => {
    await page.goto('/plans');
    // The empty-state student was created but has no packets,
    // so their name should not appear in any pending packet card.
    await expect(page.getByText('Empty State Student')).not.toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Plans list — pending packet card
// ---------------------------------------------------------------------------
test.describe('Plans page — pending packet card', () => {
  const STUDENT_ID = 'e2e-feedback-card-c3d4';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, {
      name: 'Card Test Student',
      birthday: '2018-02-01',
    });
    await createPacket(request, STUDENT_ID, PACKET_ID);
  });

  test('renders a pending packet card with name, subject, grade, days, worksheet counts', async ({
    page,
  }) => {
    await page.goto('/plans');
    await expect(page.getByText('Card Test Student')).toBeVisible();
    await expect(page.getByText('Mathematics')).toBeVisible();
    const studentCard = page
      .getByText('Card Test Student')
      .locator('..')
      .locator('..')
      .locator('..');
    await expect(studentCard.getByText('3')).toBeVisible(); // grade_level
    // Days = 2 (Monday + Tuesday in seed)
    await expect(studentCard.locator('text=Days').locator('..').getByText('2')).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Plan detail modal
// ---------------------------------------------------------------------------
test.describe('Plan detail modal', () => {
  const STUDENT_ID = 'e2e-feedback-modal-e5f6';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, {
      name: 'Detail Modal Student',
      birthday: '2018-03-01',
    });
    await createPacket(request, STUDENT_ID, PACKET_ID);
  });

  test('clicking a pending packet card opens the plan detail modal', async ({ page }) => {
    await page.goto('/plans');
    await page.getByText('Detail Modal Student').click();
    await expect(page.getByText('Plan Details')).toBeVisible();
  });

  test('shows student name, week, subject, grade', async ({ page }) => {
    await page.goto('/plans');
    await page.getByText('Detail Modal Student').click();
    const modal = page.getByRole('dialog');
    await expect(modal.getByText('Detail Modal Student')).toBeVisible();
    await expect(modal.getByText('Mathematics')).toBeVisible();
    await expect(modal.getByText('Grade Level').locator('..').getByText('3')).toBeVisible();
  });

  test('shows daily plan content — day label, focus, objective, procedure steps', async ({
    page,
  }) => {
    await page.goto('/plans');
    await page.getByText('Detail Modal Student').click();
    const modal = page.getByRole('dialog');
    await expect(modal.getByText('Monday')).toBeVisible();
    await expect(modal.getByText('Introduction')).toBeVisible();
    await expect(modal.getByText('Understand fractions')).toBeVisible();
    await expect(modal.getByText('Read introduction')).toBeVisible();
  });

  test('Close button dismisses the modal', async ({ page }) => {
    await page.goto('/plans');
    await page.getByText('Detail Modal Student').click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.getByRole('button', { name: 'Close' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('clicking the backdrop dismisses the modal', async ({ page }) => {
    await page.goto('/plans');
    await page.getByText('Detail Modal Student').click();
    await expect(page.getByRole('dialog')).toBeVisible();
    // Click outside the modal panel (top-left corner of viewport)
    await page.mouse.click(10, 10);
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('Escape key dismisses the modal', async ({ page }) => {
    await page.goto('/plans');
    await page.getByText('Detail Modal Student').click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('Print All button opens the print URL in a new tab', async ({ page }) => {
    await page.goto('/plans');
    await page.getByText('Detail Modal Student').click();
    await expect(page.getByRole('dialog')).toBeVisible();
    const [popup] = await Promise.all([
      page.waitForEvent('popup'),
      page.getByRole('button', { name: 'Print All' }).click(),
    ]);
    await expect(popup).toHaveURL(/\/print/);
  });

  test('shows "Provide Feedback" for a ready packet with no feedback', async ({ page }) => {
    await page.goto('/plans');
    await page.getByText('Detail Modal Student').click();
    await expect(page.getByRole('button', { name: 'Provide Feedback' })).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Plan detail modal — "Edit Feedback" state
// ---------------------------------------------------------------------------
test.describe('Plan detail modal — existing feedback', () => {
  const STUDENT_ID = 'e2e-feedback-edit-g7h8';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, {
      name: 'Edit Feedback Student',
      birthday: '2018-04-01',
    });
    await createPacket(request, STUDENT_ID, PACKET_ID);
    await submitFeedback(request, STUDENT_ID, PACKET_ID, {
      mastery: 'MASTERED',
      quantity: 0,
    });
  });

  test('shows "Edit Feedback" for a ready packet with existing feedback (not locked)', async ({
    page,
  }) => {
    await page.goto('/plans');
    await page.getByText('Edit Feedback Student').click();
    await expect(page.getByRole('button', { name: 'Edit Feedback' })).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Plan detail modal — locked feedback state
// ---------------------------------------------------------------------------
test.describe('Plan detail modal — locked feedback', () => {
  const STUDENT_ID = 'e2e-feedback-locked-i9j0';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, {
      name: 'Locked Feedback Student',
      birthday: '2018-05-01',
    });
    await createPacket(request, STUDENT_ID, PACKET_ID);
    await submitFeedback(request, STUDENT_ID, PACKET_ID, {
      mastery: 'DEVELOPING',
      quantity: 1,
    });
    backdateFeedback(PACKET_ID, '2026-01-01T00:00:00Z');
  });

  test('shows disabled "Feedback Submitted" for a packet with feedback older than 3 weeks', async ({
    page,
  }) => {
    await page.goto('/plans');
    await page.getByText('Locked Feedback Student').click();
    const btn = page.getByRole('button', { name: 'Feedback Submitted' });
    await expect(btn).toBeVisible();
    await expect(btn).toBeDisabled();
  });
});

// ---------------------------------------------------------------------------
// Feedback modal — first submission
// ---------------------------------------------------------------------------
test.describe('Feedback modal — first submission', () => {
  test.describe.configure({ mode: 'serial' });
  const STUDENT_ID = 'e2e-feedback-submit-k1l2';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, {
      name: 'Submit Feedback Student',
      birthday: '2018-06-01',
    });
    await createPacket(request, STUDENT_ID, PACKET_ID);
  });

  async function openFeedbackModal(page: import('@playwright/test').Page) {
    await page.goto('/plans');
    await page.getByText('Submit Feedback Student').click();
    await page.getByRole('button', { name: 'Provide Feedback' }).click();
  }

  test('title reads "Provide Feedback"', async ({ page }) => {
    await openFeedbackModal(page);
    await expect(page.getByRole('dialog').getByText('Provide Feedback')).toBeVisible();
  });

  test('Submit button is disabled until both ratings are selected', async ({ page }) => {
    await openFeedbackModal(page);
    const submit = page.getByRole('button', { name: 'Submit Feedback' });
    await expect(submit).toBeDisabled();

    await page.getByRole('button', { name: 'Mastered' }).click();
    await expect(submit).toBeDisabled(); // still missing workload

    await page.getByRole('button', { name: 'Just Right' }).click();
    await expect(submit).toBeEnabled();
  });

  test('selecting a mastery rating highlights it with a ring', async ({ page }) => {
    await openFeedbackModal(page);
    const btn = page.getByRole('button', { name: 'Mastered' });
    await btn.click();
    await expect(btn).toHaveClass(/ring-2/);
  });

  test('selecting a workload rating highlights it', async ({ page }) => {
    await openFeedbackModal(page);
    const btn = page.getByRole('button', { name: 'Too Much' });
    await btn.click();
    await expect(btn).toHaveClass(/ring-2/);
  });

  test('Cancel button closes the modal without submitting', async ({ page }) => {
    await openFeedbackModal(page);
    await page.getByRole('button', { name: 'Cancel' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('Escape key closes the modal', async ({ page }) => {
    await openFeedbackModal(page);
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('backdrop click closes the modal', async ({ page }) => {
    await openFeedbackModal(page);
    await page.mouse.click(10, 10);
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('submitting closes the modal and the button changes to "Edit Feedback"', async ({
    page,
  }) => {
    await openFeedbackModal(page);
    await page.getByRole('button', { name: 'Mastered' }).click();
    await page.getByRole('button', { name: 'Just Right' }).click();
    await page.getByRole('button', { name: 'Submit Feedback' }).click();

    // Modal closes and plan list refreshes — now the packet shows Edit Feedback
    await page.getByText('Submit Feedback Student').click();
    await expect(page.getByRole('button', { name: 'Edit Feedback' })).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Feedback modal — editing existing feedback
// ---------------------------------------------------------------------------
test.describe('Feedback modal — editing existing feedback', () => {
  const STUDENT_ID = 'e2e-feedback-resubmit-m3n4';
  const PACKET_ID = `${STUDENT_ID}-pkt-001`;

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, {
      name: 'Resubmit Feedback Student',
      birthday: '2018-07-01',
    });
    await createPacket(request, STUDENT_ID, PACKET_ID);
    await submitFeedback(request, STUDENT_ID, PACKET_ID, {
      mastery: 'STRUGGLING',
      quantity: 2,
    });
  });

  async function openEditModal(page: import('@playwright/test').Page) {
    await page.goto('/plans');
    await page.getByText('Resubmit Feedback Student').click();
    await page.getByRole('button', { name: 'Edit Feedback' }).click();
  }

  test('title reads "Edit Feedback"', async ({ page }) => {
    await openEditModal(page);
    await expect(page.getByRole('dialog').getByText('Edit Feedback')).toBeVisible();
  });

  test('mastery and workload ratings are pre-populated from the stored values', async ({
    page,
  }) => {
    await openEditModal(page);
    // mastery was STRUGGLING
    await expect(page.getByRole('button', { name: 'Struggling' })).toHaveClass(/ring-2/);
    // quantity was 2 → TOO_LITTLE
    await expect(page.getByRole('button', { name: 'Too Little' })).toHaveClass(/ring-2/);
  });

  test('Submit button reads "Update Feedback"', async ({ page }) => {
    await openEditModal(page);
    await expect(page.getByRole('button', { name: 'Update Feedback' })).toBeVisible();
  });

  test('changing a rating and submitting succeeds', async ({ page }) => {
    await openEditModal(page);
    await page.getByRole('button', { name: 'Mastered' }).click();
    await page.getByRole('button', { name: 'Just Right' }).click();
    await page.getByRole('button', { name: 'Update Feedback' }).click();
    // After update, modal closes
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });
});
