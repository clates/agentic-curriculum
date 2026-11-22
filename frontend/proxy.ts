import { NextResponse, type NextRequest } from 'next/server';
import { SESSION_COOKIE, loginRequired } from '@/lib/auth';

/**
 * Sends a visitor without a session to /login, remembering where they were going.
 *
 * Only active when AUTH_REQUIRED is on (read here on the server, at request time). It checks that
 * the cookie exists, nothing more: the backend is the one that says whether a session is real, and
 * a refused call from the page sends the person back here. /api/* stays open so the app's own
 * health check and the sign-in call reach the backend, which protects every other route itself.
 */
export function proxy(request: NextRequest) {
  if (!loginRequired()) return NextResponse.next();

  const { pathname, search } = request.nextUrl;
  if (pathname === '/login' || pathname.startsWith('/api/')) return NextResponse.next();
  if (request.cookies.get(SESSION_COOKIE)?.value) return NextResponse.next();

  const url = request.nextUrl.clone();
  url.pathname = '/login';
  url.search = '';
  if (pathname !== '/') url.searchParams.set('next', pathname + search);
  return NextResponse.redirect(url);
}

export const config = {
  // Everything except Next's own assets and files in public/ (anything with a file extension).
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.[a-zA-Z0-9]+$).*)'],
};
