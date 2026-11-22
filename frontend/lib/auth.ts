/** Login helpers shared by the proxy (server) and the login screen (browser). */

export const SESSION_COOKIE = 'curriculum_session';
export const DEFAULT_LANDING = '/week';

/**
 * Where to go after signing in: the page they asked for, if it is a page on this site.
 * Anything that could leave the site (`//host`, `/\host`, a full URL) or loop (`/login`) is dropped.
 */
export function safeNext(raw: string | null | undefined): string {
  if (!raw || !raw.startsWith('/') || raw.startsWith('//') || raw.includes('\\')) {
    return DEFAULT_LANDING;
  }
  const path = raw.split(/[?#]/)[0];
  if (path === '/' || path === '/login' || path.startsWith('/login/') || path.startsWith('/api/')) {
    return DEFAULT_LANDING;
  }
  return raw;
}

/** Is the login screen required? A server-side read (never NEXT_PUBLIC), so it can change per run. */
export function loginRequired(): boolean {
  return ['1', 'true', 'yes', 'on'].includes((process.env['AUTH_REQUIRED'] ?? '').toLowerCase());
}
