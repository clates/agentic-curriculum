/** Login helpers shared by the proxy (server) and the login screen (browser). */

export const SESSION_COOKIE = 'curriculum_session';
export const DEFAULT_LANDING = '/week';

/**
 * Where to go after signing in: the page they asked for, if it is a page on this site.
 *
 * Browsers strip tabs and newlines inside a URL and read a backslash as a slash, so `/\t/evil.com`
 * means `//evil.com`. So: refuse any control character or backslash outright, then resolve the
 * value the way a browser would and require it to stay on the same origin. Anything that could
 * loop (`/login`) or is not a page (`/api/...`) falls back to the default landing page.
 */
export function safeNext(raw: string | null | undefined): string {
  if (!raw || !raw.startsWith('/') || /[\u0000-\u001f\u007f\\]/.test(raw)) return DEFAULT_LANDING;
  let url: URL;
  try {
    url = new URL(raw, 'http://x.invalid');
  } catch {
    return DEFAULT_LANDING;
  }
  if (url.origin !== 'http://x.invalid') return DEFAULT_LANDING;
  const path = url.pathname;
  if (path === '/' || path === '/login' || path.startsWith('/login/') || path.startsWith('/api/')) {
    return DEFAULT_LANDING;
  }
  return path + url.search + url.hash;
}

/** Is the login screen required? A server-side read (never NEXT_PUBLIC), so it can change per run. */
export function loginRequired(): boolean {
  return ['1', 'true', 'yes', 'on'].includes((process.env['AUTH_REQUIRED'] ?? '').toLowerCase());
}
