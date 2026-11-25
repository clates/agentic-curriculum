import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8181';

// Request headers passed to the backend when present. Login needs the session cookie and the facts
// the backend uses to judge a request it cannot see for itself (it only ever talks to this proxy).
const REQUEST_HEADERS = [
  'Content-Type',
  'Authorization',
  'Cookie',
  'Origin',
  'Referer',
  'Sec-Fetch-Site',
  'User-Agent',
];
// Response headers passed back when present (file downloads and caching).
const RESPONSE_HEADERS = [
  'Content-Type',
  'Content-Disposition',
  'Content-Length',
  'Cache-Control',
  'ETag',
];

function copyHeaders(from: Headers, names: string[], to: Record<string, string>) {
  for (const name of names) {
    const value = from.get(name);
    if (value) to[name] = value;
  }
}

/**
 * Catch-all API route that proxies requests to the backend
 * This eliminates CORS issues and allows us to only expose port 3000
 */
async function handler(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const pathname = (await params).path.join('/');

  // Validate pathname doesn't contain suspicious patterns
  if (pathname.includes('..') || pathname.startsWith('/')) {
    return NextResponse.json({ error: 'Invalid path' }, { status: 400 });
  }

  // Sign-in bodies are tiny; refuse a big one before reading it.
  if (pathname.startsWith('auth/') && Number(request.headers.get('Content-Length') ?? 0) > 16384) {
    return NextResponse.json({ detail: 'request_too_large' }, { status: 413 });
  }

  const url = new URL(`${BACKEND_URL}/${pathname}`);
  request.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.append(key, value);
  });

  try {
    const headers: Record<string, string> = {};
    copyHeaders(request.headers, REQUEST_HEADERS, headers);
    // The backend trusts the client address and protocol only because the connection comes from
    // this machine. The RIGHTMOST entry is the hop our own front proxy appended; the ones to its
    // left were supplied by the client and can say anything.
    const forwarded = (request.headers.get('X-Forwarded-For') ?? '')
      .split(',')
      .map((part) => part.trim())
      .filter(Boolean);
    const clientIp = forwarded[forwarded.length - 1] || request.headers.get('X-Real-IP')?.trim();
    if (clientIp) headers['X-Curriculum-Client-IP'] = clientIp;
    headers['X-Forwarded-Proto'] =
      request.headers.get('X-Forwarded-Proto')?.split(',')[0]?.trim() ||
      request.nextUrl.protocol.replace(':', '');
    const host = request.headers.get('X-Forwarded-Host') || request.headers.get('Host');
    if (host) headers['X-Forwarded-Host'] = host;

    const backendResponse = await fetch(url.toString(), {
      method: request.method,
      headers,
      // Only include body for requests that can have one
      ...(request.body &&
        request.method !== 'GET' &&
        request.method !== 'HEAD' && {
          body: await request.text(),
        }),
    });

    const responseHeaders: Record<string, string> = {};
    copyHeaders(backendResponse.headers, RESPONSE_HEADERS, responseHeaders);

    // Sessions: pass every Set-Cookie through untouched (there can be several).
    const setCookies = backendResponse.headers.getSetCookie();
    const withCookies = (response: NextResponse) => {
      setCookies.forEach((value) => response.headers.append('Set-Cookie', value));
      return response;
    };

    // 204 No Content must not carry a body
    if (backendResponse.status === 204) {
      return withCookies(new NextResponse(null, { status: 204, headers: responseHeaders }));
    }

    copyHeaders(backendResponse.headers, ['Retry-After'], responseHeaders);

    // As an ArrayBuffer, so binary downloads come through intact
    const data = await backendResponse.arrayBuffer();
    return withCookies(
      new NextResponse(data, { status: backendResponse.status, headers: responseHeaders })
    );
  } catch (error) {
    console.error('Backend proxy error:', error);
    return NextResponse.json({ error: 'Failed to connect to backend' }, { status: 502 });
  }
}

export { handler as GET, handler as POST, handler as PUT, handler as DELETE, handler as PATCH };
