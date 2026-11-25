'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { loginWithGoogle } from '@/lib/firebase-auth';
import { AudioLines, ArrowLeft, ArrowRight, Building2, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, Sparkles, UserRound } from 'lucide-react';

export default function SignupPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleGoogleSignup() {
    setNotice('');
    setLoading(true);
    try {
      await loginWithGoogle();
      router.replace('/dashboard');
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Google sign-up failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }
  return (
    <main className="relative flex min-h-screen overflow-hidden bg-[#080d19] text-white">
      <div className="pointer-events-none absolute -left-40 top-0 h-[520px] w-[520px] rounded-full bg-cyan-500/10 blur-[130px]" />
      <div className="pointer-events-none absolute -bottom-48 right-0 h-[600px] w-[600px] rounded-full bg-violet-600/10 blur-[140px]" />
      <aside className="relative hidden w-[43%] flex-col justify-between border-r border-white/[.08] bg-gradient-to-br from-[#0d1a2d] via-[#10162b] to-[#111026] p-12 lg:flex">
        <Link href="/" className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl border border-cyan-300/30 bg-cyan-300/10 text-cyan-200"><AudioLines size={23}/></span><span className="text-xl font-semibold tracking-tight">voice<span className="text-cyan-300">ai</span></span></Link>
        <div className="relative z-10 max-w-lg">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/[.06] px-3 py-2 text-[10px] font-bold tracking-[.2em] text-cyan-200"><Sparkles size={13}/> START WITH A CLEARER SIGNAL</div>
          <h1 className="text-5xl font-semibold leading-[1.08] tracking-[-.06em] xl:text-6xl">Build conversations that <span className="bg-gradient-to-r from-cyan-200 via-blue-300 to-violet-300 bg-clip-text text-transparent">move business forward.</span></h1>
          <p className="mt-7 max-w-md text-base leading-8 text-slate-400">Create a unified space for voice agents, calling campaigns and the customer insights behind every interaction.</p>
          <div className="mt-10 space-y-4 text-sm text-slate-300"><p className="flex items-center gap-3"><ShieldCheck size={18} className="text-cyan-300"/> Consent-aware operations</p><p className="flex items-center gap-3"><Sparkles size={18} className="text-cyan-300"/> One connected workspace</p></div>
        </div>
        <p className="text-xs text-slate-500">© {new Date().getFullYear()} VoiceAI. All rights reserved.</p>
      </aside>
      <section className="relative z-10 flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-[460px]">
          <Link href="/" className="mb-10 inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-white"><ArrowLeft size={16}/> Back to home</Link>
          <div className="mb-7 lg:hidden"><span className="inline-flex h-12 w-12 items-center justify-center rounded-xl border border-cyan-300/30 bg-cyan-300/10 text-cyan-200"><AudioLines size={24}/></span></div>
          <p className="text-xs font-bold tracking-[.2em] text-cyan-300">GET STARTED</p>
          <h2 className="mt-3 text-4xl font-semibold tracking-[-.05em]">Create your account</h2>
          <p className="mt-3 text-sm leading-6 text-slate-400">Set up your VoiceAI workspace in a few steps.</p>
          <button type="button" onClick={handleGoogleSignup} disabled={loading} className="mt-8 flex w-full items-center justify-center gap-3 rounded-xl border border-white/15 bg-white/[.05] px-5 py-4 text-sm font-semibold text-white transition hover:bg-white/[.1] disabled:cursor-wait disabled:opacity-60">
            <svg aria-hidden="true" viewBox="0 0 48 48" className="h-5 w-5"><path fill="#FFC107" d="M43.6 24.5c0-1.4-.1-2.8-.4-4.1H24v7.8h11a9.4 9.4 0 0 1-4.1 6.2v5.1h6.6c3.9-3.6 6.1-8.8 6.1-15Z"/><path fill="#34A853" d="M24 44c5.5 0 10.1-1.8 13.5-4.9l-6.6-5.1c-1.8 1.2-4.1 2-6.9 2-5.3 0-9.8-3.6-11.4-8.4H5.8v5.3A20 20 0 0 0 24 44Z"/><path fill="#4A90E2" d="M12.6 27.6a12 12 0 0 1 0-7.2v-5.3H5.8a20 20 0 0 0 0 17.8l6.8-5.3Z"/><path fill="#EA4335" d="M24 12c3 0 5.7 1 7.8 3.1l5.9-5.9C34.1 5.9 29.5 4 24 4A20 20 0 0 0 5.8 15.1l6.8 5.3C14.2 15.6 18.7 12 24 12Z"/></svg>
            {loading ? 'Opening Google…' : 'Continue with Google'}
          </button>
          <div className="my-6 flex items-center gap-4 text-[11px] font-medium uppercase tracking-[.15em] text-slate-600"><span className="h-px flex-1 bg-white/10"/><span>or create with email</span><span className="h-px flex-1 bg-white/10"/></div>
          <form className="mt-8 space-y-4" onSubmit={(e)=>{e.preventDefault();setNotice('Account creation is not active yet: the registration API has not been enabled on this deployment. No credentials were sent or stored.')}}>
            <label className="block"><span className="mb-2 block text-sm font-medium text-slate-300">Your name</span><span className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[.04] px-4 focus-within:border-cyan-300/50"><UserRound size={17} className="text-slate-500"/><input required placeholder="Full name" className="min-w-0 flex-1 bg-transparent py-3.5 text-sm outline-none placeholder:text-slate-600"/></span></label>
            <label className="block"><span className="mb-2 block text-sm font-medium text-slate-300">Work email</span><span className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[.04] px-4 focus-within:border-cyan-300/50"><Mail size={17} className="text-slate-500"/><input type="email" required placeholder="you@company.com" className="min-w-0 flex-1 bg-transparent py-3.5 text-sm outline-none placeholder:text-slate-600"/></span></label>
            <label className="block"><span className="mb-2 block text-sm font-medium text-slate-300">Company / workspace</span><span className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[.04] px-4 focus-within:border-cyan-300/50"><Building2 size={17} className="text-slate-500"/><input required placeholder="Your company name" className="min-w-0 flex-1 bg-transparent py-3.5 text-sm outline-none placeholder:text-slate-600"/></span></label>
            <label className="block"><span className="mb-2 block text-sm font-medium text-slate-300">Create password</span><span className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[.04] px-4 focus-within:border-cyan-300/50"><LockKeyhole size={17} className="text-slate-500"/><input type={showPassword?'text':'password'} minLength={8} required placeholder="At least 8 characters" className="min-w-0 flex-1 bg-transparent py-3.5 text-sm outline-none placeholder:text-slate-600"/><button type="button" aria-label="Toggle password visibility" onClick={()=>setShowPassword(!showPassword)} className="text-slate-500 hover:text-white">{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></span></label>
            <button type="submit" className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400 px-5 py-4 text-sm font-bold text-[#07111f] shadow-lg shadow-cyan-500/10 transition hover:-translate-y-0.5">Create workspace <ArrowRight size={17}/></button>
          </form>
          {notice && <p role="alert" className="mt-5 rounded-xl border border-amber-300/20 bg-amber-300/[.07] p-4 text-xs leading-6 text-amber-100">{notice}</p>}
          <p className="mt-7 text-center text-sm text-slate-400">Already have an account? <Link href="/login" className="font-semibold text-cyan-300 hover:text-white">Sign in</Link></p>
          <p className="mt-8 text-center text-[11px] leading-5 text-slate-600">Registration is not enabled on this deployment yet. This page is the account-creation design preview.</p>
        </div>
      </section>
    </main>
  );
}
