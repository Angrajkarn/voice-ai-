import { createUserWithEmailAndPassword, signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup, updateProfile, sendEmailVerification, signOut } from 'firebase/auth';
import { firebaseAuth } from './firebase';
import { api } from './api';

export type VoiceAISession = {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  user: { id: string; email: string; name: string | null; organization_id: string; role: string };
};

async function exchangeFirebaseSession(workspaceName?: string): Promise<VoiceAISession> {
  if (!firebaseAuth?.currentUser) throw new Error('Firebase is not configured or the user is not signed in.');
  const idToken = await firebaseAuth.currentUser.getIdToken(true);
  const session = await api.post<VoiceAISession>('/auth/firebase/session', { id_token: idToken, workspace_name: workspaceName });
  if (typeof window !== 'undefined') sessionStorage.setItem('voiceai_access_token', session.access_token);
  return session;
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

export async function loginWithGoogle() {
  if (!firebaseAuth) throw new Error('Firebase configuration is missing. Add the NEXT_PUBLIC_FIREBASE_* environment variables.');
  await signInWithPopup(firebaseAuth, new GoogleAuthProvider());
  return exchangeFirebaseSession();
}

export async function logoutVoiceAI() {
  if (typeof window !== 'undefined') sessionStorage.removeItem('voiceai_access_token');
  if (firebaseAuth) await signOut(firebaseAuth);
}
