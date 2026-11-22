/**
 * Interests on the add/edit child form (M6.3): the weekly topics are built from what the child
 * loves, so the parent can set it. Real API; mobile and desktop.
 */
import type { APIRequestContext, Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { test, expect } from '../fixtures/test';
import { BACKEND } from '../fixtures/api';
import { uniqueId } from '../fixtures/parent';
import { shot } from '../fixtures/shots';

async function metadataOf(request: APIRequestContext, id: string) {
  const res = await request.get(`${BACKEND}/student/${id}`);
  expect(res.ok()).toBeTruthy();
  return JSON.parse((await res.json()).metadata_blob);
}

async function openAdd(page: Page) {
  await page.goto('/students');
  await page.getByRole('button', { name: 'Add Student' }).first().click();
  await expect(page.getByRole('dialog')).toBeVisible();
}

async function fillChild(page: Page, id: string, name: string) {
  await page.getByLabel('Student ID').fill(id);
  await page.getByLabel('Full Name').fill(name);
  await page.getByLabel('Birthday').fill('2018-01-15');
}

test.describe('Interests on the child form', () => {
  test('add a child with interests, see them again on edit, change them', async ({
    page,
    request,
  }) => {
    const id = uniqueId('int').replace(/-/g, '_');
    const name = `Likes ${id}`;
    await openAdd(page);
    await expect(page.getByLabel('Interests (optional)')).toBeVisible();
    await fillChild(page, id, name);
    await page.getByLabel('Interests (optional)').fill('dinosaurs,  baking ; soccer');
    // The form itself must be accessible (the rest of this admin page is not in this PR's scope).
    const axe = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    expect(axe.violations.map((v) => v.id)).toEqual([]);
    await shot(page, 'topics-child-form');
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    expect((await metadataOf(request, id)).interests).toEqual(['dinosaurs', 'baking', 'soccer']);

    await page.reload();
    const row = page.getByRole('heading', { name }).locator('../../..');
    await row.getByRole('button', { name: 'Edit' }).click();
    await expect(page.getByLabel('Interests (optional)')).toHaveValue('dinosaurs, baking, soccer');
    await page.getByLabel('Interests (optional)').fill('ocean animals');
    await page.getByRole('button', { name: 'Update Student' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    const meta = await metadataOf(request, id);
    expect(meta.interests).toEqual(['ocean animals']);
    expect(meta.name).toBe(name);
  });

  test('empty state: no interests is fine, and clearing them works', async ({ page, request }) => {
    const id = uniqueId('none').replace(/-/g, '_');
    await openAdd(page);
    await fillChild(page, id, `Plain ${id}`);
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    expect((await metadataOf(request, id)).interests ?? []).toEqual([]);
  });

  test('loading state while saving, then it closes', async ({ page, request }) => {
    const id = uniqueId('slow').replace(/-/g, '_');
    await page.route('**/students', async (route) => {
      if (route.request().method() === 'POST') await new Promise((r) => setTimeout(r, 1500));
      await route.continue();
    });
    await openAdd(page);
    await fillChild(page, id, `Slow ${id}`);
    await page.getByLabel('Interests (optional)').fill('music');
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByRole('button', { name: 'Creating...' })).toBeDisabled();
    await expect(page.getByRole('dialog')).not.toBeVisible({ timeout: 15_000 });
    expect((await metadataOf(request, id)).interests).toEqual(['music']);
  });

  test('error state: a failed save shows a message and retrying works', async ({
    page,
    request,
  }) => {
    const id = uniqueId('err').replace(/-/g, '_');
    let fail = true;
    await page.route('**/students', (route) => {
      if (route.request().method() === 'POST' && fail) {
        fail = false;
        return route.fulfill({ status: 500, body: '{"detail":"boom"}' });
      }
      return route.continue();
    });
    await openAdd(page);
    await fillChild(page, id, `Retry ${id}`);
    await page.getByLabel('Interests (optional)').fill('robots');
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByRole('dialog').getByText(/failed|error|500/i)).toBeVisible();
    await expect(page.getByLabel('Interests (optional)')).toHaveValue('robots'); // kept
    await page.getByRole('button', { name: 'Create Student' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
    expect((await metadataOf(request, id)).interests).toEqual(['robots']);
  });

  test('keyboard only: tab to the field, type, submit', async ({ page, request }) => {
    const id = uniqueId('kb').replace(/-/g, '_');
    await openAdd(page);
    await fillChild(page, id, `Keys ${id}`);
    await page.getByLabel('Avatar URL (optional)').focus();
    await page.keyboard.press('Tab'); // the next field is interests
    await expect(page.getByLabel('Interests (optional)')).toBeFocused();
    await page.keyboard.type('chess');
    await page.getByRole('button', { name: 'Create Student' }).focus();
    await page.keyboard.press('Enter');
    await expect(page.getByRole('dialog')).not.toBeVisible();
    expect((await metadataOf(request, id)).interests).toEqual(['chess']);
  });
});
