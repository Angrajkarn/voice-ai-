import { NextRequest } from 'next/server';

export const dynamic = 'force-dynamic';

const API_ORIGIN = (process.env.PYTHON_API_URL || 'https://voice-ai-qveo.onrender.com').replace(/\/$/, '');

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const upstreamUrl = `${API_ORIGIN}/api/v1/${path.map(encodeURIComponent).join('/')}${request.nextUrl.search}`;
  const headers = new Headers();
  for (const name of ['accept', 'content-type', 'authorization', 'cookie', 'x-request-id']) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  try {
    const upstream = await fetch(upstreamUrl, {
      method: request.method,
      headers,
      body: ['GET', 'HEAD'].includes(request.method) ? undefined : await request.arrayBuffer(),
      cache: 'no-store',
      redirect: 'manual',
    });
    const contentType = upstream.headers.get('content-type') || '';
    const body = await upstream.arrayBuffer();

    // API clients expect JSON. Convert upstream HTML error pages into a useful JSON response.
    if (contentType.includes('text/html')) {
      return Response.json(
        { error: 'The API returned an HTML page instead of JSON.', code: 'UPSTREAM_NOT_JSON', upstreamStatus: upstream.status },
        { status: 502 },
      );
    }

    const responseHeaders = new Headers();
    for (const name of ['content-type', 'content-disposition', 'cache-control']) {
      const value = upstream.headers.get(name);
      if (value) responseHeaders.set(name, value);
    }
    return new Response(body, { status: upstream.status, headers: responseHeaders });
  } catch (error) {
    return Response.json(
      { error: 'Unable to reach the VoiceAI API. Check PYTHON_API_URL and the backend service.', code: 'API_PROXY_ERROR' },
      { status: 502 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const HEAD = proxy;
