'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AudioLines, ArrowLeft, ArrowRight, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, Sparkles } from 'lucide-react';
import { loginWithEmail, loginWithGoogle } from '@/lib/firebase-auth';

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleGoogleSignIn() {
    setNotice('');
    setLoading(true);
    try {
      await loginWithGoogle();
      router.replace('/dashboard');
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Google sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleEmailSignIn(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice('');
    setLoading(true);
    try {
      await loginWithEmail(email, password);
      router.replace('/dashboard');
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative flex min-h-screen overflow-hidden bg-[#080d19] text-white">
      <div className="pointer-events-none absolute -left-40 top-0 h-[520px] w-[520px] rounded-full bg-cyan-500/10 blur-[130px]" />
      <div className="pointer-events-none absolute -bottom-48 right-0 h-[600px] w-[600px] rounded-full bg-violet-600/10 blur-[140px]" />
      <aside className="relative hidden w-[46%] flex-col justify-between border-r border-white/[.08] bg-gradient-to-br from-[#0d1a2d] via-[#10162b] to-[#111026] p-12 lg:flex">
        <Link href="/" className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl border border-cyan-300/30 bg-cyan-300/10 text-cyan-200"><AudioLines size={23}/></span><span className="text-xl font-semibold tracking-tight">voice<span className="text-cyan-300">ai</span></span></Link>
        <div className="relative z-10 max-w-lg">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/[.06] px-3 py-2 text-[10px] font-bold tracking-[.2em] text-cyan-200"><Sparkles size={13}/> YOUR VOICE OPERATIONS, IN ONE PLACE</div>
          <h1 className="text-5xl font-semibold leading-[1.08] tracking-[-.06em] xl:text-6xl">Every call has a story. <span className="bg-gradient-to-r from-cyan-200 via-blue-300 to-violet-300 bg-clip-text text-transparent">Know what happens next.</span></h1>
          <p className="mt-7 max-w-md text-base leading-8 text-slate-400">Bring campaigns, customer conversations and operational insights together in one intelligent workspace.</p>
          <div className="mt-10 flex items-center gap-3 text-sm text-slate-300"><ShieldCheck className="text-cyan-300" size={18}/> Designed for accountable voice automation</div>
        </div>
        <p className="text-xs text-slate-500">© {new Date().getFullYear()} VoiceAI. All rights reserved.</p>
      </aside>
      <section className="relative z-10 flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-[440px]">
          <Link href="/" className="mb-12 inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-white"><ArrowLeft size={16}/> Back to home</Link>
          <div className="mb-8 lg:hidden"><span className="inline-flex h-12 w-12 items-center justify-center rounded-xl border border-cyan-300/30 bg-cyan-300/10 text-cyan-200"><AudioLines size={24}/></span></div>
          <p className="text-xs font-bold tracking-[.2em] text-cyan-300">WELCOME BACK</p>
          <h2 className="mt-3 text-4xl font-semibold tracking-[-.05em]">Sign in to VoiceAI</h2>
          <p className="mt-3 text-sm leading-6 text-slate-400">Access your workspace and keep every conversation moving.</p>

          <button type="button" onClick={handleGoogleSignIn} disabled={loading} className="mt-8 flex w-full items-center justify-center gap-3 rounded-xl border border-white/15 bg-white/[.05] px-5 py-4 text-sm font-semibold text-white transition hover:bg-white/[.1] disabled:cursor-wait disabled:opacity-60">
            <svg aria-hidden="true" viewBox="0 0 48 48" className="h-5 w-5"><path fill="#FFC107" d="M43.6 24.5c0-1.4-.1-2.8-.4-4.1H24v7.8h11a9.4 9.4 0 0 1-4.1 6.2v5.1h6.6c3.9-3.6 6.1-8.8 6.1-15Z"/><path fill="#34A853" d="M24 44c5.5 0 10.1-1.8 13.5-4.9l-6.6-5.1c-1.8 1.2-4.1 2-6.9 2-5.3 0-9.8-3.6-11.4-8.4H5.8v5.3A20 20 0 0 0 24 44Z"/><path fill="#4A90E2" d="M12.6 27.6a12 12 0 0 1 0-7.2v-5.3H5.8a20 20 0 0 0 0 17.8l6.8-5.3Z"/><path fill="#EA4335" d="M24 12c3 0 5.7 1 7.8 3.1l5.9-5.9C34.1 5.9 29.5 4 24 4A20 20 0 0 0 5.8 15.1l6.8 5.3C14.2 15.6 18.7 12 24 12Z"/></svg>
            {loading ? 'Signing in…' : 'Continue with Google'}
          </button>
          <div className="my-6 flex items-center gap-4 text-[11px] font-medium uppercase tracking-[.15em] text-slate-600"><span className="h-px flex-1 bg-white/10"/><span>or use email</span><span className="h-px flex-1 bg-white/10"/></div>

          <form className="space-y-5" onSubmit={handleEmailSignIn}>
            <label className="block"><span className="mb-2 block text-sm font-medium text-slate-300">Work email</span><span className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[.04] px-4 focus-within:border-cyan-300/50"><Mail size={17} className="text-slate-500"/><input type="email" required value={email} onChange={(event)=>setEmail(event.target.value)} placeholder="you@company.com" className="h-13 min-w-0 flex-1 bg-transparent py-4 text-sm outline-none placeholder:text-slate-600"/></span></label>
            <label className="block"><span className="mb-2 block text-sm font-medium text-slate-300">Password</span><span className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[.04] px-4 focus-within:border-cyan-300/50"><LockKeyhole size={17} className="text-slate-500"/><input type={showPassword?'text':'password'} required value={password} onChange={(event)=>setPassword(event.target.value)} placeholder="Enter your password" className="h-13 min-w-0 flex-1 bg-transparent py-4 text-sm outline-none placeholder:text-slate-600"/><button type="button" aria-label="Toggle password visibility" onClick={()=>setShowPassword(!showPassword)} className="text-slate-500 hover:text-white">{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></span></label>
            <button disabled={loading} className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400 px-5 py-4 text-sm font-bold text-[#07111f] shadow-lg shadow-cyan-500/10 transition hover:-translate-y-0.5 disabled:opacity-60" type="submit">Continue <ArrowRight size={17}/></button>
          </form>
          {notice && <p role="alert" className="mt-5 rounded-xl border border-amber-300/20 bg-amber-300/[.07] p-4 text-xs leading-6 text-amber-100">{notice}</p>}
          <p className="mt-8 text-center text-sm text-slate-400">New to VoiceAI? <Link href="/signup" className="font-semibold text-cyan-300 hover:text-white">Create an account</Link></p>
        </div>
      </section>
    </main>
  );
}
