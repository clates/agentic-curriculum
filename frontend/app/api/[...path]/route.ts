import { NextRequest, NextResponse } from 'next/server';

// Get backend URL from environment variable or default to localhost:8000
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

/**
 * Catch-all API route that proxies requests to the backend
 * This eliminates CORS issues and allows us to only expose port 3000
 */
async function handler(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  // In Next.js 16, params is a Promise
  const { path } = await params;
  const pathname = Array.isArray(path) ? path.join('/') : path;

  // Construct the backend URL
  const url = new URL(`${BACKEND_URL}/${pathname}`);
  
  // Forward query parameters
  request.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.append(key, value);
  });

  try {
    // Forward the request to the backend
    const backendResponse = await fetch(url.toString(), {
      method: request.method,
      headers: {
        'Content-Type': request.headers.get('Content-Type') || 'application/json',
        // Forward other relevant headers
        ...(request.headers.get('Authorization') && {
          Authorization: request.headers.get('Authorization')!,
        }),
      },
      // Forward body for POST, PUT, PATCH, DELETE
      ...(request.method !== 'GET' && request.method !== 'HEAD' && {
        body: await request.text(),
      }),
    });

    // Get the response body
    const data = await backendResponse.text();

    // Return the response with the same status and headers
    return new NextResponse(data, {
      status: backendResponse.status,
      headers: {
        'Content-Type': backendResponse.headers.get('Content-Type') || 'application/json',
      },
    });
  } catch (error) {
    console.error('Backend proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 502 }
    );
  }
}

export { handler as GET, handler as POST, handler as PUT, handler as DELETE, handler as PATCH };
