'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AudioLines, ArrowRight, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, Sparkles } from 'lucide-react';
import { loginWithEmail, loginWithGoogle } from '@/lib/firebase-auth';

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(false);
  const getDestination = () => {
    const nextPath = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('next') : null;
    return nextPath?.startsWith('/dashboard') ? nextPath : '/dashboard';
  };

  async function handleGoogleSignIn() {
    setNotice(''); setLoading(true);
    try { await loginWithGoogle(); router.replace(getDestination()); router.refresh(); }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Google sign-in failed. Please try again.'); }
    finally { setLoading(false); }
  }

  async function handleEmailSignIn(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setNotice(''); setLoading(true);
    try { await loginWithEmail(email, password); router.replace(getDestination()); router.refresh(); }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Sign-in failed. Please try again.'); }
    finally { setLoading(false); }
  }

  return (
    <main className="grid min-h-screen bg-base-100 text-base-content lg:grid-cols-[.95fr_1.05fr]">
      <aside className="relative hidden flex-col justify-between overflow-hidden border-r border-base-300 bg-base-200 p-12 lg:flex">
        <div className="absolute -left-32 top-10 h-96 w-96 rounded-full bg-primary/10 blur-3xl"/>
        <Link href="/" className="relative flex items-center gap-3 text-xl font-bold"><span className="grid h-11 w-11 place-items-center rounded-xl bg-primary text-primary-content"><AudioLines size={23}/></span>voice<span className="-ml-3 text-primary">ai</span></Link>
        <div className="relative z-10 max-w-xl"><div className="badge badge-outline gap-2 border-primary/30 text-primary"><Sparkles size={13}/> YOUR VOICE OPERATIONS</div><h1 className="mt-7 text-5xl font-black leading-tight tracking-[-.05em] xl:text-6xl">Every call has a story. <span className="text-primary">Know what happens next.</span></h1><p className="mt-7 max-w-md leading-8 text-base-content/60">Bring campaigns, customer conversations and operational insights together in one intelligent workspace.</p><div className="mt-9 flex items-center gap-3 text-sm text-base-content/70"><ShieldCheck size={18} className="text-success"/> Protected workspace access</div></div>
        <p className="text-xs text-base-content/40">© {new Date().getFullYear()} VoiceAI. All rights reserved.</p>
      </aside>
      <section className="flex items-center justify-center px-5 py-12 sm:px-8">
        <div className="w-full max-w-md">
          <Link href="/" className="mb-10 inline-flex items-center gap-2 text-sm text-base-content/55 hover:text-primary">← Back to home</Link>
          <div className="card border border-base-300 bg-base-100 shadow-xl"><div className="card-body p-7 sm:p-9">
            <div className="mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-primary/10 text-primary lg:hidden"><AudioLines size={24}/></div>
            <div className="badge badge-outline w-fit border-primary/30 text-primary">WELCOME BACK</div>
            <h2 className="mt-2 text-3xl font-bold tracking-tight">Sign in to VoiceAI</h2>
            <p className="text-sm leading-6 text-base-content/60">Access your own workspace and keep every conversation moving.</p>
            <button type="button" onClick={handleGoogleSignIn} disabled={loading} className="btn btn-outline mt-5 h-12 min-h-12 w-full rounded-xl border-base-300 normal-case"><svg aria-hidden="true" viewBox="0 0 48 48" className="h-5 w-5"><path fill="#FFC107" d="M43.6 24.5c0-1.4-.1-2.8-.4-4.1H24v7.8h11a9.4 9.4 0 0 1-4.1 6.2v5.1h6.6c3.9-3.6 6.1-8.8 6.1-15Z"/><path fill="#34A853" d="M24 44c5.5 0 10.1-1.8 13.5-4.9l-6.6-5.1c-1.8 1.2-4.1 2-6.9 2-5.3 0-9.8-3.6-11.4-8.4H5.8v5.3A20 20 0 0 0 24 44Z"/><path fill="#4A90E2" d="M12.6 27.6a12 12 0 0 1 0-7.2v-5.3H5.8a20 20 0 0 0 0 17.8l6.8-5.3Z"/><path fill="#EA4335" d="M24 12c3 0 5.7 1 7.8 3.1l5.9-5.9C34.1 5.9 29.5 4 24 4A20 20 0 0 0 5.8 15.1l6.8 5.3C14.2 15.6 18.7 12 24 12Z"/></svg>{loading ? 'Signing in…' : 'Continue with Google'}</button>
            <div className="divider text-xs text-base-content/40">OR USE EMAIL</div>
            <form className="space-y-4" onSubmit={handleEmailSignIn}>
              <label className="form-control w-full"><span className="label-text mb-2 text-sm font-medium">Work email</span><div className="input input-bordered flex h-12 items-center gap-3 rounded-xl"><Mail size={17} className="text-base-content/45"/><input type="email" required value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="you@company.com" className="grow bg-transparent outline-none"/></div></label>
              <label className="form-control w-full"><span className="label-text mb-2 text-sm font-medium">Password</span><div className="input input-bordered flex h-12 items-center gap-3 rounded-xl"><LockKeyhole size={17} className="text-base-content/45"/><input type={showPassword?'text':'password'} required value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="Enter your password" className="grow bg-transparent outline-none"/><button type="button" aria-label="Toggle password visibility" onClick={()=>setShowPassword(!showPassword)} className="text-base-content/45 hover:text-primary">{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></div></label>
              <button disabled={loading} className="btn btn-primary h-12 min-h-12 w-full rounded-xl">{loading ? <span className="loading loading-spinner loading-sm"/> : <>Sign in <ArrowRight size={17}/></>}</button>
            </form>
            {notice && <div role="alert" className="alert alert-error mt-4 text-sm">{notice}</div>}
            <p className="mt-4 text-center text-sm text-base-content/60">New to VoiceAI? <Link href="/signup" className="font-semibold text-primary hover:underline">Create an account</Link></p>
          </div></div>
          <p className="mt-6 text-center text-xs text-base-content/40">Your workspace data is available only after your account is authenticated.</p>
        </div>
      </section>
    </main>
  );
}
