import { NextRequest, NextResponse } from 'next/server';

// Get backend URL from environment variable or default to localhost:8000
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8181';

/**
 * Catch-all API route that proxies requests to the backend
 * This eliminates CORS issues and allows us to only expose port 3000
 */
async function handler(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  // In Next.js 15+, params is a Promise
  const { path } = await params;
  const pathname = Array.isArray(path) ? path.join('/') : path;

  // Validate pathname doesn't contain suspicious patterns
  if (pathname.includes('..') || pathname.startsWith('/')) {
    return NextResponse.json({ error: 'Invalid path' }, { status: 400 });
  }

  // Sign-in bodies are tiny; refuse a big one before reading it.
  if (pathname.startsWith('auth/') && Number(request.headers.get('Content-Length') ?? 0) > 16384) {
    return NextResponse.json({ detail: 'request_too_large' }, { status: 413 });
  }

  // Construct the backend URL
  const url = new URL(`${BACKEND_URL}/${pathname}`);

  // Forward query parameters
  request.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.append(key, value);
  });

  try {
    // Build request headers - only forward if present
    const headers: HeadersInit = {};
    if (request.headers.get('Content-Type')) {
      headers['Content-Type'] = request.headers.get('Content-Type')!;
    }
    if (request.headers.get('Authorization')) {
      headers['Authorization'] = request.headers.get('Authorization')!;
    }

    // Login: the session cookie, and the facts the backend needs to judge a request it cannot see
    // for itself (it only ever talks to this proxy). It trusts the client address and protocol
    // only because the connection comes from this machine.
    const cookie = request.headers.get('Cookie');
    if (cookie) headers['Cookie'] = cookie;
    const origin = request.headers.get('Origin');
    if (origin) headers['Origin'] = origin;
    const referer = request.headers.get('Referer');
    if (referer) headers['Referer'] = referer;
    const fetchSite = request.headers.get('Sec-Fetch-Site');
    if (fetchSite) headers['Sec-Fetch-Site'] = fetchSite;
    const userAgent = request.headers.get('User-Agent');
    if (userAgent) headers['User-Agent'] = userAgent;
    // The RIGHTMOST entry is the hop our own front proxy appended; the ones to its left were
    // supplied by the client and can say anything.
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

    // Forward the request to the backend
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

    // Build response headers - forward all important headers from backend
    const responseHeaders: HeadersInit = {};

    // Forward Content-Type if present (critical for file downloads)
    const contentType = backendResponse.headers.get('Content-Type');
    if (contentType) {
      responseHeaders['Content-Type'] = contentType;
    }

    // Forward other important headers for file downloads and caching
    const contentDisposition = backendResponse.headers.get('Content-Disposition');
    if (contentDisposition) {
      responseHeaders['Content-Disposition'] = contentDisposition;
    }

    const contentLength = backendResponse.headers.get('Content-Length');
    if (contentLength) {
      responseHeaders['Content-Length'] = contentLength;
    }

    const cacheControl = backendResponse.headers.get('Cache-Control');
    if (cacheControl) {
      responseHeaders['Cache-Control'] = cacheControl;
    }

    const etag = backendResponse.headers.get('ETag');
    if (etag) {
      responseHeaders['ETag'] = etag;
    }

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

    const retryAfter = backendResponse.headers.get('Retry-After');
    if (retryAfter) responseHeaders['Retry-After'] = retryAfter;

    // Get the response body as ArrayBuffer to ensure binary data is preserved
    const data = await backendResponse.arrayBuffer();

    // Return the response with the same status and forwarded headers
    return withCookies(
      new NextResponse(data, {
        status: backendResponse.status,
        headers: responseHeaders,
      })
    );
  } catch (error) {
    console.error('Backend proxy error:', error);
    return NextResponse.json({ error: 'Failed to connect to backend' }, { status: 502 });
  }
}

export { handler as GET, handler as POST, handler as PUT, handler as DELETE, handler as PATCH };
