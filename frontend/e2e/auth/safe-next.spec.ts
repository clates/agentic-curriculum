/** `safeNext` decides where sign-in sends you next. Pure function, no browser page needed. */
import { test, expect } from '@playwright/test';
import { safeNext, DEFAULT_LANDING, NEW_FAMILY_LANDING } from '../../lib/auth';

const hostile = [
  '//evil.example',
  'https://evil.example',
  '/\\evil.example',
  '/\t/evil.example',
  '/\n/evil.example',
  '/\r/evil.example',
  '/\u0000/evil.example',
  '/..//evil.example',
  '/.//evil.example',
  '/a/..//evil.example',
  '/%2e%2e//evil.example',
  '/%2E%2E//evil.example',
  '/a/%2e%2e//evil.example',
  '/.%2e//evil.example',
  '/%2e././/evil.example',
  '/login',
  '/login/x',
  '/api/students',
  '/',
  '',
  'week',
];

test.describe('safeNext', () => {
  for (const bad of hostile) {
    test(`falls back for ${JSON.stringify(bad)}`, () => {
      expect(safeNext(bad)).toBe(DEFAULT_LANDING);
    });
  }

  test('no result can be read by a browser as another site', () => {
    for (const bad of [...hostile, '/%2f/evil.example', '/ /evil.example', '/a//b']) {
      const out = safeNext(bad);
      expect(out).toMatch(/^\/(?![/\\])/);
      expect(new URL(out, 'http://site.test').origin).toBe('http://site.test');
    }
  });

  test('keeps real pages, with their query and anchor', () => {
    expect(safeNext('/week')).toBe('/week');
    expect(safeNext('/week/check-in/abc')).toBe('/week/check-in/abc');
    expect(safeNext('/how-its-going?child=abc#top')).toBe('/how-its-going?child=abc#top');
    expect(safeNext('/a/../week')).toBe('/week');
  });

  test('a given fallback replaces the default landing page for every refusal', () => {
    for (const bad of hostile) expect(safeNext(bad, NEW_FAMILY_LANDING)).toBe(NEW_FAMILY_LANDING);
    expect(safeNext('/how-its-going', NEW_FAMILY_LANDING)).toBe('/how-its-going');
  });
});
