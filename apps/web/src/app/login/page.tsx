'use client';

import Link from 'next/link';
import { useState } from 'react';
import { AudioLines, ArrowLeft, ArrowRight, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [notice, setNotice] = useState('');
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
          <form className="mt-9 space-y-5" onSubmit={(e)=>{e.preventDefault();setNotice('Sign-in is not active yet: the authentication API has not been enabled on this deployment. No credentials were sent or stored.')}}>
            <label className="block"><span className="mb-2 block text-sm font-medium text-slate-300">Work email</span><span className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[.04] px-4 focus-within:border-cyan-300/50"><Mail size={17} className="text-slate-500"/><input type="email" required placeholder="you@company.com" className="h-13 min-w-0 flex-1 bg-transparent py-4 text-sm outline-none placeholder:text-slate-600"/></span></label>
            <label className="block"><span className="mb-2 block text-sm font-medium text-slate-300">Password</span><span className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[.04] px-4 focus-within:border-cyan-300/50"><LockKeyhole size={17} className="text-slate-500"/><input type={showPassword?'text':'password'} required placeholder="Enter your password" className="h-13 min-w-0 flex-1 bg-transparent py-4 text-sm outline-none placeholder:text-slate-600"/><button type="button" aria-label="Toggle password visibility" onClick={()=>setShowPassword(!showPassword)} className="text-slate-500 hover:text-white">{showPassword?<EyeOff size={17}/>:<Eye size={17}/>}</button></span></label>
            <div className="flex justify-end"><span className="text-xs text-slate-500">Forgot password? Contact your workspace administrator.</span></div>
            <button className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-300 via-blue-400 to-violet-400 px-5 py-4 text-sm font-bold text-[#07111f] shadow-lg shadow-cyan-500/10 transition hover:-translate-y-0.5" type="submit">Continue <ArrowRight size={17}/></button>
          </form>
          {notice && <p role="status" className="mt-5 rounded-xl border border-amber-300/20 bg-amber-300/[.07] p-4 text-xs leading-6 text-amber-100">{notice}</p>}
          <p className="mt-8 text-center text-sm text-slate-400">New to VoiceAI? <Link href="/signup" className="font-semibold text-cyan-300 hover:text-white">Create an account</Link></p>
          <p className="mt-10 text-center text-[11px] leading-5 text-slate-600">Authentication is not enabled on this deployment yet. This page is the sign-in design preview.</p>
        </div>
      </section>
    </main>
  );
}
