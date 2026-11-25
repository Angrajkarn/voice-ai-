import { NextRequest, NextResponse } from 'next/server';

const COOKIE_NAME = 'voiceai_session';
const API_ORIGIN = (process.env.PYTHON_API_URL || 'https://voice-ai-backend-oxwx.onrender.com').replace(/\/$/, '');

export async function middleware(request: NextRequest) {
  const token = request.cookies.get(COOKIE_NAME)?.value;
  const loginUrl = new URL('/login', request.url);
  loginUrl.searchParams.set('next', request.nextUrl.pathname + request.nextUrl.search);

  if (!token) return NextResponse.redirect(loginUrl);

  try {
    const verification = await fetch(`${API_ORIGIN}/api/v1/auth/me`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' },
      cache: 'no-store',
    });

    if (verification.ok) return NextResponse.next();

    if (verification.status === 401 || verification.status === 403) {
      const response = NextResponse.redirect(loginUrl);
      response.cookies.set(COOKIE_NAME, '', {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        path: '/',
        maxAge: 0,
      });
      return response;
    }

    return NextResponse.json({ error: 'Authentication service is temporarily unavailable.' }, { status: 503 });
  } catch {
    return NextResponse.json({ error: 'Unable to verify your session. Please retry when the API is available.' }, { status: 503 });
  }
}

export const config = { matcher: ['/dashboard/:path*'] };
