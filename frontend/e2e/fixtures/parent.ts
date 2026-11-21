import AxeBuilder from '@axe-core/playwright';
import type { Page } from '@playwright/test';
import { expect } from './test';
import { BANNED_WORDS } from '../../lib/bannedWords';

/** Axe (WCAG A/AA) must find nothing on the current screen. */
export async function expectNoViolations(page: Page) {
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
  expect(
    results.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target).join(' | ')}`)
  ).toEqual([]);
}

/** No technical term may appear in the text a parent can read. */
export async function expectNoBannedWords(page: Page) {
  const text = await page.locator('body').innerText();
  const hits = BANNED_WORDS.filter((w) =>
    new RegExp(`(^|[^\\w])${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}($|[^\\w])`, 'i').test(text)
  );
  expect(hits, 'technical terms on a parent screen').toEqual([]);
}

/** A name unique to one test run, so parallel specs sharing one database never collide. */
export function uniqueId(prefix: string): string {
  return `${prefix}_${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
}
