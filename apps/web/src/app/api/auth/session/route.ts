import { NextRequest, NextResponse } from 'next/server';

const COOKIE_NAME = 'voiceai_session';
const SESSION_MAX_AGE = 30 * 60;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as { token?: string };
    if (!body.token || typeof body.token !== 'string' || body.token.length < 40) {
      return NextResponse.json({ error: 'A valid session token is required.' }, { status: 400 });
    }
    const response = NextResponse.json({ authenticated: true });
    response.cookies.set(COOKIE_NAME, body.token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: SESSION_MAX_AGE,
    });
    return response;
  } catch {
    return NextResponse.json({ error: 'Invalid session request.' }, { status: 400 });
  }
}

export async function DELETE() {
  const response = NextResponse.json({ authenticated: false });
  response.cookies.set(COOKIE_NAME, '', {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: 0,
  });
  return response;
}
