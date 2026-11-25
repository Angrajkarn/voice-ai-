import { createUserWithEmailAndPassword, signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup, updateProfile, sendEmailVerification, signOut } from 'firebase/auth';
import { firebaseAuth } from './firebase';
import { api } from './api';

export type VoiceAIUser = {
  id: string;
  email: string;
  name: string | null;
  organization_id: string;
  role: string;
  avatar_url?: string | null;
  organization_name?: string | null;
};

export type VoiceAISession = {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  user: VoiceAIUser;
};

const SESSION_KEY = 'voiceai_access_token';
const USER_KEY = 'voiceai_user';

async function persistSession(session: VoiceAISession) {
  if (typeof window === 'undefined') return;
  sessionStorage.setItem(SESSION_KEY, session.access_token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(session.user));
  const response = await fetch('/api/auth/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: session.access_token }),
    credentials: 'same-origin',
  });
  if (!response.ok) {
    sessionStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem(USER_KEY);
    throw new Error('Your account was verified, but the secure browser session could not be created. Please try again.');
  }
}

async function exchangeFirebaseSession(workspaceName?: string): Promise<VoiceAISession> {
  if (!firebaseAuth?.currentUser) throw new Error('Firebase is not configured or the user is not signed in.');
  const idToken = await firebaseAuth.currentUser.getIdToken(true);
  const session = await api.post<VoiceAISession>('/auth/firebase/session', { id_token: idToken, workspace_name: workspaceName });
  await persistSession(session);
  return session;
}

export function getStoredVoiceAIUser(): VoiceAIUser | null {
  if (typeof window === 'undefined') return null;
  try {
    const value = sessionStorage.getItem(USER_KEY);
    return value ? JSON.parse(value) as VoiceAIUser : null;
  } catch {
    return null;
  }
}

export async function registerWithEmail(name: string, email: string, password: string, workspace: string) {
  if (!firebaseAuth) throw new Error('Firebase configuration is missing. Add the NEXT_PUBLIC_FIREBASE_* environment variables.');
  const credential = await createUserWithEmailAndPassword(firebaseAuth, email, password);
  await updateProfile(credential.user, { displayName: name });
  await sendEmailVerification(credential.user);
  return { verificationRequired: true, exchange: () => exchangeFirebaseSession(workspace) };
}

export async function loginWithEmail(email: string, password: string) {
  if (!firebaseAuth) throw new Error('Firebase configuration is missing. Add the NEXT_PUBLIC_FIREBASE_* environment variables.');
  await signInWithEmailAndPassword(firebaseAuth, email, password);
  if (!firebaseAuth.currentUser?.emailVerified) throw new Error('Please verify your email address before signing in.');
  return exchangeFirebaseSession();
}

export async function loginWithGoogle(workspaceName?: string) {
  if (!firebaseAuth) throw new Error('Firebase configuration is missing. Add the NEXT_PUBLIC_FIREBASE_* environment variables.');
  await signInWithPopup(firebaseAuth, new GoogleAuthProvider());
  return exchangeFirebaseSession(workspaceName);
}

export async function logoutVoiceAI() {
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem(USER_KEY);
    await fetch('/api/auth/session', { method: 'DELETE', credentials: 'same-origin' }).catch(() => undefined);
  }
  if (firebaseAuth) await signOut(firebaseAuth);
}
