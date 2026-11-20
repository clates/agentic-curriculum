import type { Page } from '@playwright/test';
import { mkdirSync } from 'fs';

/** Save a screenshot when SCREENS_DIR is set (used to produce the proof screenshots). */
export async function shot(page: Page, name: string): Promise<void> {
  const dir = process.env.SCREENS_DIR;
  if (!dir) return;
  mkdirSync(dir, { recursive: true });
  await page.screenshot({ path: `${dir}/${name}.png`, fullPage: true });
}
