import { NextRequest, NextResponse } from 'next/server';

// Get backend URL from environment variable or default to localhost:8000
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

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

    // Get the response body
    const data = await backendResponse.text();

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

    // Return the response with the same status and forwarded headers
    return new NextResponse(data, {
      status: backendResponse.status,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('Backend proxy error:', error);
    return NextResponse.json({ error: 'Failed to connect to backend' }, { status: 502 });
  }
}

export { handler as GET, handler as POST, handler as PUT, handler as DELETE, handler as PATCH };
