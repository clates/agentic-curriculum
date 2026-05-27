import { test, expect } from '@playwright/test';
import { createStudent } from './fixtures/api';

const BACKEND = process.env.BACKEND_URL ?? 'http://localhost:8182';

// ---------------------------------------------------------------------------
// Student management — empty state
// ---------------------------------------------------------------------------
test.describe('Student management — empty state', () => {
  test('"Add Student" button is always present on the students page', async ({ page }) => {
    await page.goto('/students');
    // The page may have students from other describe blocks — just verify
    // the "Add Student" header button is always present.
    await expect(page.getByRole('button', { name: 'Add Student' }).first()).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Student management — creating a student
// ---------------------------------------------------------------------------
test.describe('Student management — creating a student', () => {
  test('"Add Student" header button opens the modal titled "Add New Student"', async ({ page }) => {
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await expect(page.getByRole('dialog').getByText('Add New Student')).toBeVisible();
  });

  test('shows validation error for Student ID with invalid characters', async ({ page }) => {
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await page.getByLabel('Student ID').fill('Invalid ID!');
    await page.getByLabel('Full Name').fill('Test');
    await page.getByLabel('Birthday').fill('2018-01-01');
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(
      page.getByText('Use lowercase letters, numbers, and underscores only')
    ).toBeVisible();
  });

  test('shows validation error for missing required fields', async ({ page }) => {
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByText('Student ID is required')).toBeVisible();
    await expect(page.getByText('Name is required')).toBeVisible();
  });

  test('shows validation error for a badly formatted birthday', async ({ page }) => {
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await page.getByLabel('Student ID').fill('test_bad_bday');
    await page.getByLabel('Full Name').fill('Test Name');
    await page.getByLabel('Birthday').fill('not-a-date');
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByText('Format: YYYY-MM-DD')).toBeVisible();
  });

  test('successfully creates a student and it appears in the list', async ({ page }) => {
    const uniqueId = `e2e_create_${Date.now()}`;
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await page.getByLabel('Student ID').fill(uniqueId);
    await page.getByLabel('Full Name').fill('Created Student');
    await page.getByLabel('Birthday').fill('2018-01-15');
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(page.getByText('Created Student')).toBeVisible();
  });

  test('Cancel button closes the modal without creating', async ({ page }) => {
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await page.getByRole('button', { name: 'Cancel' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('Escape key closes the modal', async ({ page }) => {
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Student management — editing a student
// ---------------------------------------------------------------------------
test.describe('Student management — editing a student', () => {
  test.describe.configure({ mode: 'serial' });
  const STUDENT_ID = 'e2e_edit_student_p5q6';
  const STUDENT_NAME = 'Edit Target Student';

  test.beforeAll(async ({ request }) => {
    // Create if doesn't exist (400 = already exists, that's fine)
    await createStudent(request, STUDENT_ID, {
      name: STUDENT_NAME,
      birthday: '2018-08-01',
    }).catch(() => {});
    // Unconditionally restore name (handles re-run where a previous test renamed it)
    await request.put(`${BACKEND}/student/${STUDENT_ID}`, {
      data: { metadata: { name: STUDENT_NAME, birthday: '2018-08-01' } },
    });
  });

  test('"Edit" button opens the modal titled "Edit Student"', async ({ page }) => {
    await page.goto('/students');
    const row = page.getByRole('heading', { name: STUDENT_NAME }).locator('../../..');
    await row.getByRole('button', { name: 'Edit' }).click();
    await expect(page.getByRole('dialog').getByText('Edit Student')).toBeVisible();
  });

  test('Student ID field is disabled (cannot be changed)', async ({ page }) => {
    await page.goto('/students');
    const row = page.getByRole('heading', { name: STUDENT_NAME }).locator('../../..');
    await row.getByRole('button', { name: 'Edit' }).click();
    await expect(page.getByLabel('Student ID')).toBeDisabled();
  });

  test('pre-populates all editable fields from existing data', async ({ page }) => {
    await page.goto('/students');
    const row = page.getByRole('heading', { name: STUDENT_NAME }).locator('../../..');
    await row.getByRole('button', { name: 'Edit' }).click();
    await expect(page.getByLabel('Full Name')).toHaveValue(STUDENT_NAME);
    await expect(page.getByLabel('Birthday')).toHaveValue('2018-08-01');
  });

  test("saving updates the student's name in the list", async ({ page }) => {
    await page.goto('/students');
    const row = page.getByRole('heading', { name: STUDENT_NAME }).locator('../../..');
    await row.getByRole('button', { name: 'Edit' }).click();
    await page.getByLabel('Full Name').fill('Renamed Student');
    await page.getByRole('button', { name: 'Update Student' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(page.getByText('Renamed Student')).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Student management — deleting a student
// ---------------------------------------------------------------------------
test.describe('Student management — deleting a student', () => {
  test.describe.configure({ mode: 'serial' });
  const STUDENT_ID = 'e2e_delete_student_r7s8';
  const STUDENT_NAME = 'Delete Target Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, {
      name: STUDENT_NAME,
      birthday: '2018-09-01',
    }).catch(() => {});
  });

  test('"Delete" button opens the confirmation modal', async ({ page }) => {
    await page.goto('/students');
    const row = page.getByRole('heading', { name: STUDENT_NAME }).locator('../../..');
    await row.getByRole('button', { name: 'Delete' }).click();
    await expect(page.getByRole('dialog').getByText('Delete Student')).toBeVisible();
  });

  test('Cancel button closes confirmation without deleting', async ({ page }) => {
    await page.goto('/students');
    const row = page.getByRole('heading', { name: STUDENT_NAME }).locator('../../..');
    await row.getByRole('button', { name: 'Delete' }).click();
    await page.getByRole('button', { name: 'Cancel' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(page.getByText(STUDENT_NAME)).toBeVisible();
  });

  test('confirming delete removes the student from the list', async ({ page }) => {
    await page.goto('/students');
    const row = page.getByRole('heading', { name: STUDENT_NAME }).locator('../../..');
    await row.getByRole('button', { name: 'Delete' }).click();
    await page.getByRole('button', { name: 'Delete Student' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(page.getByText(STUDENT_NAME)).not.toBeVisible();
  });
});
