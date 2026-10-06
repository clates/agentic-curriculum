/**
 * Journey 1 — Onboard a student
 *
 * A parent opens the app for the first time, adds their child, and sees that child on the
 * dashboard ready for a first plan. Later they correct a detail or remove a student they
 * added by mistake.
 */
import { test, expect } from '../fixtures/test';
import { createStudent } from '../fixtures/api';

const BACKEND = process.env.BACKEND_URL ?? 'http://localhost:8182';

test.describe('1.1 Add a child', () => {
  test('the parent can always find "Add Student"', async ({ page }) => {
    await page.goto('/students');
    await expect(page.getByRole('button', { name: 'Add Student' }).first()).toBeVisible();
  });

  test('"Add Student" opens the "Add New Student" form', async ({ page }) => {
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await expect(page.getByRole('dialog').getByText('Add New Student')).toBeVisible();
  });

  test('the form explains a malformed Student ID', async ({ page }) => {
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

  test('the form flags missing ID and name', async ({ page }) => {
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByText('Student ID is required')).toBeVisible();
    await expect(page.getByText('Name is required')).toBeVisible();
  });

  test('the form flags a missing birthday', async ({ page }) => {
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await page.getByLabel('Student ID').fill('test_no_bday');
    await page.getByLabel('Full Name').fill('Test Name');
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByText('Format: YYYY-MM-DD')).toBeVisible();
  });

  test('the parent can back out with Cancel or Escape', async ({ page }) => {
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await page.getByRole('button', { name: 'Cancel' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();

    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('a valid child is created and shows up on the students list and the dashboard', async ({
    page,
  }) => {
    const id = `e2e_onboard_${Date.now()}`;
    const name = `Onboarded Child ${id}`;
    await page.goto('/students');
    await page.getByRole('button', { name: 'Add Student' }).first().click();
    await page.getByLabel('Student ID').fill(id);
    await page.getByLabel('Full Name').fill(name);
    await page.getByLabel('Birthday').fill('2018-01-15');
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(page.getByText(name)).toBeVisible();

    await page.goto('/dashboard');
    await expect(page.getByRole('heading', { name })).toBeVisible();
  });

  // The birthday is the only age signal the parent gives us, yet the dashboard card shows "—"
  // where grade/age belong and plan generation asks for a grade from scratch every time.
  test.fixme('the dashboard card shows the child’s age-appropriate grade', async () => {});
});

test.describe('1.2 Correct a child’s details', () => {
  test.describe.configure({ mode: 'serial' });
  const STUDENT_ID = 'e2e_edit_student_p5q6';
  const STUDENT_NAME = 'Edit Target Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: STUDENT_NAME, birthday: '2018-08-01' });
    // Restore the name in case a previous run renamed it
    await request.put(`${BACKEND}/student/${STUDENT_ID}`, {
      data: { metadata: { name: STUDENT_NAME, birthday: '2018-08-01' } },
    });
  });

  const openEdit = async (page: import('@playwright/test').Page) => {
    await page.goto('/students');
    const row = page.getByRole('heading', { name: STUDENT_NAME }).locator('../../..');
    await row.getByRole('button', { name: 'Edit' }).click();
  };

  test('"Edit" opens the form pre-filled, with the ID locked', async ({ page }) => {
    await openEdit(page);
    await expect(page.getByRole('dialog').getByText('Edit Student')).toBeVisible();
    await expect(page.getByLabel('Student ID')).toBeDisabled();
    await expect(page.getByLabel('Full Name')).toHaveValue(STUDENT_NAME);
    await expect(page.getByLabel('Birthday')).toHaveValue('2018-08-01');
  });

  test('saving a new name updates the list', async ({ page }) => {
    await openEdit(page);
    await page.getByLabel('Full Name').fill('Renamed Student');
    await page.getByRole('button', { name: 'Update Student' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(page.getByText('Renamed Student')).toBeVisible();
  });
});

test.describe('1.3 Remove a student', () => {
  test.describe.configure({ mode: 'serial' });
  const STUDENT_ID = 'e2e_delete_student_r7s8';
  const STUDENT_NAME = 'Delete Target Student';

  test.beforeAll(async ({ request }) => {
    await createStudent(request, STUDENT_ID, { name: STUDENT_NAME, birthday: '2018-09-01' });
  });

  const openDelete = async (page: import('@playwright/test').Page) => {
    await page.goto('/students');
    const row = page.getByRole('heading', { name: STUDENT_NAME }).locator('../../..');
    await row.getByRole('button', { name: 'Delete' }).click();
  };

  test('"Delete" asks for confirmation, and Cancel keeps the student', async ({ page }) => {
    await openDelete(page);
    await expect(
      page.getByRole('dialog').getByRole('heading', { name: 'Delete Student' })
    ).toBeVisible();
    await page.getByRole('button', { name: 'Cancel' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(page.getByText(STUDENT_NAME)).toBeVisible();
  });

  test('confirming removes the student', async ({ page }) => {
    await openDelete(page);
    await page.getByRole('button', { name: 'Delete Student' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    await expect(page.getByText(STUDENT_NAME)).not.toBeVisible();
  });
});
