/** Login helpers shared by the proxy (server) and the login screen (browser). */

export const SESSION_COOKIE = 'curriculum_session';
export const DEFAULT_LANDING = '/week';
/** Where a family that has just confirmed its email starts, unless it was sent somewhere. */
export const NEW_FAMILY_LANDING = '/welcome';

/**
 * Where to go after signing in: the page they asked for, if it is a page on this site.
 *
 * Browsers strip tabs and newlines inside a URL and read a backslash as a slash, so `/\t/evil.com`
 * means `//evil.com`. So: refuse any control character or backslash outright, then resolve the
 * value the way a browser would and require it to stay on the same origin. Anything that could
 * loop (`/login`) or is not a page (`/api/...`) falls back to `fallback` (the default landing page
 * unless given).
 */
export function safeNext(raw: string | null | undefined, fallback = DEFAULT_LANDING): string {
  if (!raw || !raw.startsWith('/') || /[\u0000-\u001f\u007f\\]/.test(raw)) return fallback;
  let url: URL;
  try {
    url = new URL(raw, 'http://x.invalid');
  } catch {
    return fallback;
  }
  if (url.origin !== 'http://x.invalid') return fallback;
  const path = url.pathname;
  // Dot segments are resolved above, so `/..//evil.com` has become the path `//evil.com`, which a
  // browser reads as another site. Check the RESULT, not just the input.
  if (path.startsWith('//')) return fallback;
  if (path === '/' || path === '/login' || path.startsWith('/login/') || path.startsWith('/api/')) {
    return fallback;
  }
  const result = path + url.search + url.hash;
  return /^\/(?![/\\])/.test(result) ? result : fallback;
}

/** Is the login screen required? A server-side read (never NEXT_PUBLIC), so it can change per run. */
export function loginRequired(): boolean {
  return ['1', 'true', 'yes', 'on'].includes((process.env['AUTH_REQUIRED'] ?? '').toLowerCase());
}
