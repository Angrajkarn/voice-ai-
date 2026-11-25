'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AudioLines, ArrowRight, Building2, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, Sparkles, UserRound } from 'lucide-react';
import { loginWithGoogle, registerWithEmail } from '@/lib/firebase-auth';

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [workspace, setWorkspace] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [notice, setNotice] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleGoogleSignup() {
    setNotice(''); setLoading(true);
    try { await loginWithGoogle(workspace.trim() || undefined); router.replace('/dashboard'); router.refresh(); }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Google sign-up failed. Please try again.'); }
    finally { setLoading(false); }
  }

  async function handleEmailSignup(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setNotice(''); setLoading(true);
    try {
      await registerWithEmail(name.trim(), email.trim(), password, workspace.trim());
      setSuccess(true);
      setNotice('Account created. Check your email and verify your address, then return to sign in. Your workspace is provisioned after the verified sign-in.');
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Account creation failed. Please try again.'); }
    finally { setLoading(false); }
  }

  return (
    <main className="grid min-h-screen bg-base-100 text-base-content lg:grid-cols-[.95fr_1.05fr]">
      <aside className="relative hidden flex-col justify-between overflow-hidden border-r border-base-300 bg-base-200 p-12 lg:flex">
        <div className="absolute -left-32 top-10 h-96 w-96 rounded-full bg-secondary/10 blur-3xl"/>
        <Link href="/" className="relative flex items-center gap-3 text-xl font-bold"><span className="grid h-11 w-11 place-items-center rounded-xl bg-primary text-primary-content"><AudioLines size={23}/></span>voice<span className="-ml-3 text-primary">ai</span></Link>
        <div className="relative z-10 max-w-xl"><div className="badge badge-outline gap-2 border-primary/30 text-primary"><Sparkles size={13}/> START WITH A CLEARER SIGNAL</div><h1 className="mt-7 text-5xl font-black leading-tight tracking-[-.05em] xl:text-6xl">Build conversations that <span className="text-primary">move business forward.</span></h1><p className="mt-7 max-w-md leading-8 text-base-content/60">Create a connected space for voice agents, calling campaigns and the customer insights behind every interaction.</p><div className="mt-9 flex items-center gap-3 text-sm text-base-content/70"><ShieldCheck size={18} className="text-success"/> Consent-aware operations</div></div>
        <p className="text-xs text-base-content/40">© {new Date().getFullYear()} VoiceAI. All rights reserved.</p>
      </aside>
      <section className="flex items-center justify-center px-5 py-12 sm:px-8">
        <div className="w-full max-w-md">
          <Link href="/" className="mb-8 inline-flex items-center gap-2 text-sm text-base-content/55 hover:text-primary">← Back to home</Link>
          <div className="card border border-base-300 bg-base-100 shadow-xl"><div className="card-body p-7 sm:p-9">
            <div className="badge badge-outline w-fit border-primary/30 text-primary">GET STARTED</div>
            <h2 className="mt-2 text-3xl font-bold tracking-tight">Create your workspace</h2>
            <p className="text-sm leading-6 text-base-content/60">Start with Google or create an account using your email.</p>
            <button type="button" onClick={handleGoogleSignup} disabled={loading} className="btn btn-outline mt-4 h-12 min-h-12 w-full rounded-xl border-base-300 normal-case"><span className="text-lg font-bold">G</span>{loading ? 'Opening Google…' : 'Continue with Google'}</button>
            <div className="divider text-xs text-base-content/40">OR USE EMAIL</div>
            <form className="space-y-3" onSubmit={handleEmailSignup}>
              <label className="form-control w-full"><span className="label-text mb-1.5 text-sm font-medium">Your name</span><div className="input input-bordered flex h-11 items-center gap-3 rounded-xl"><UserRound size={16} className="text-base-content/45"/><input required value={name} onChange={(e)=>setName(e.target.value)} placeholder="Full name" className="grow bg-transparent outline-none"/></div></label>
              <label className="form-control w-full"><span className="label-text mb-1.5 text-sm font-medium">Work email</span><div className="input input-bordered flex h-11 items-center gap-3 rounded-xl"><Mail size={16} className="text-base-content/45"/><input type="email" required value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="you@company.com" className="grow bg-transparent outline-none"/></div></label>
              <label className="form-control w-full"><span className="label-text mb-1.5 text-sm font-medium">Company / workspace</span><div className="input input-bordered flex h-11 items-center gap-3 rounded-xl"><Building2 size={16} className="text-base-content/45"/><input required value={workspace} onChange={(e)=>setWorkspace(e.target.value)} placeholder="Your company name" className="grow bg-transparent outline-none"/></div></label>
              <label className="form-control w-full"><span className="label-text mb-1.5 text-sm font-medium">Create password</span><div className="input input-bordered flex h-11 items-center gap-3 rounded-xl"><LockKeyhole size={16} className="text-base-content/45"/><input type={showPassword?'text':'password'} minLength={8} required value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="At least 8 characters" className="grow bg-transparent outline-none"/><button type="button" aria-label="Toggle password visibility" onClick={()=>setShowPassword(!showPassword)} className="text-base-content/45 hover:text-primary">{showPassword?<EyeOff size={16}/>:<Eye size={16}/>}</button></div></label>
              <button type="submit" disabled={loading || success} className="btn btn-primary mt-2 h-12 min-h-12 w-full rounded-xl">{loading ? <span className="loading loading-spinner loading-sm"/> : <>Create account <ArrowRight size={17}/></>}</button>
            </form>
            {notice && <div role="alert" className={success ? 'alert alert-success mt-4 text-sm' : 'alert alert-error mt-4 text-sm'}>{notice}</div>}
            <p className="mt-4 text-center text-sm text-base-content/60">Already have an account? <Link href="/login" className="font-semibold text-primary hover:underline">Sign in</Link></p>
          </div></div>
        </div>
      </section>
    </main>
  );
}
