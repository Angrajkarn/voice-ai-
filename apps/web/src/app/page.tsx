"use client";

import Link from 'next/link';
import { useState } from 'react';
import {
  ArrowRight, AudioLines, BarChart3, Bot, Check, CirclePlay,
  Headphones, Menu, MessageSquareText, Radio, ShieldCheck, Sparkles, Workflow, X,
} from 'lucide-react';

const features = [
  { icon: Bot, number: '01', title: 'Voice agents that do more', body: 'Design natural, goal-oriented conversations with configurable agent workflows and clear escalation paths.' },
  { icon: Workflow, number: '02', title: 'Campaigns, orchestrated', body: 'Coordinate audiences, calling schedules, retries and follow-ups from a single operating layer.' },
  { icon: AudioLines, number: '03', title: 'Every conversation, visible', body: 'Bring call outcomes, transcripts, recordings and customer context into one review experience.' },
  { icon: BarChart3, number: '04', title: 'Decisions backed by data', body: 'Understand campaign performance with operational KPIs, filters and actionable reporting.' },
];

const steps = [
  { n: '01', title: 'Connect your workflow', body: 'Bring in customer data and configure the systems your team already uses.' },
  { n: '02', title: 'Shape the conversation', body: 'Define your agent’s objective, approved guidance, voice and escalation rules.' },
  { n: '03', title: 'Launch with control', body: 'Manage campaigns, monitor activity and review outcomes as they happen.' },
];

export default function HomePage() {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <main className="va-site min-h-screen overflow-hidden bg-[#080d19] text-white">
      <div className="va-noise" aria-hidden="true" />
      <header className="va-nav-wrap">
        <div className="va-nav mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-8">
          <Link href="/" className="flex items-center gap-3" aria-label="VoiceAI home">
            <span className="va-brand-mark"><AudioLines size={22} strokeWidth={2.2} /></span>
            <span className="text-[19px] font-semibold tracking-[-.04em]">voice<span className="text-cyan-300">ai</span><span className="ml-1 text-[10px] font-medium tracking-[.18em] text-slate-500">PLATFORM</span></span>
          </Link>
          <nav className="hidden items-center gap-8 text-[13px] font-medium text-slate-300 md:flex">
            <a className="va-nav-link" href="#platform">Platform</a><a className="va-nav-link" href="#how-it-works">How it works</a><a className="va-nav-link" href="#trust">Trust & control</a>
          </nav>
          <div className="hidden items-center gap-3 md:flex">
            <Link href="/dashboard" className="px-4 py-2 text-sm font-medium text-slate-300 transition hover:text-white">Workspace</Link>
            <Link href="/dashboard" className="va-button va-button-small">Explore workspace <ArrowRight size={15} /></Link>
          </div>
          <button aria-label={menuOpen ? 'Close navigation' : 'Open navigation'} onClick={() => setMenuOpen(!menuOpen)} className="rounded-lg border border-white/10 p-2 text-slate-200 md:hidden">{menuOpen ? <X size={20} /> : <Menu size={20} />}</button>
        </div>
        {menuOpen && <div className="border-t border-white/10 bg-[#0b1323] px-6 py-5 md:hidden"><nav className="flex flex-col gap-4 text-sm text-slate-200"><a href="#platform" onClick={() => setMenuOpen(false)}>Platform</a><a href="#how-it-works" onClick={() => setMenuOpen(false)}>How it works</a><a href="#trust" onClick={() => setMenuOpen(false)}>Trust & control</a><Link href="/dashboard">Open workspace <ArrowRight className="inline" size={14} /></Link></nav></div>}
      </header>

      <section className="va-hero relative isolate">
        <div className="va-hero-glow va-glow-one" /><div className="va-hero-glow va-glow-two" />
        <div className="mx-auto grid max-w-7xl items-center gap-14 px-6 pb-24 pt-16 lg:grid-cols-[1.02fr_.98fr] lg:px-8 lg:pb-32 lg:pt-24">
          <div className="relative z-10">
            <div className="va-eyebrow"><span className="va-eyebrow-dot" /><Sparkles size={13} /> THE NEXT INTERFACE FOR CUSTOMER CONVERSATIONS</div>
            <h1 className="va-headline mt-7 max-w-3xl text-[clamp(3.2rem,6.2vw,5.8rem)] font-semibold leading-[.99] tracking-[-.065em]">Make every<br className="hidden sm:block" /> conversation <span className="va-gradient-text">count.</span></h1>
            <p className="mt-7 max-w-xl text-[16px] leading-8 text-slate-400 sm:text-[18px]">A powerful voice AI operations platform to orchestrate calls, understand conversations and turn customer interactions into meaningful outcomes.</p>
            <div className="mt-9 flex flex-wrap items-center gap-3">
              <Link href="/dashboard" className="va-button">Explore the platform <ArrowRight size={17} /></Link>
              <a href="#platform" className="va-button-ghost"><CirclePlay size={17} /> Discover how it works</a>
            </div>
            <div className="mt-10 flex flex-wrap items-center gap-x-7 gap-y-3 text-xs font-medium text-slate-500"><span className="flex items-center gap-2"><Check size={14} className="text-cyan-300" /> Campaign orchestration</span><span className="flex items-center gap-2"><Check size={14} className="text-cyan-300" /> Conversation intelligence</span><span className="flex items-center gap-2"><Check size={14} className="text-cyan-300" /> Operational control</span></div>
          </div>

          <div className="va-visual relative mx-auto w-full max-w-[590px]">
            <div className="va-orbit va-orbit-a" /><div className="va-orbit va-orbit-b" /><div className="va-orbit-core"><div className="va-core-inner"><AudioLines size={42} strokeWidth={1.5} /></div></div>
            <div className="va-float-card va-float-top"><span className="va-mini-icon"><Radio size={15} /></span><span><b>Voice intelligence</b><small>One connected workspace</small></span><span className="va-pulse" /></div>
            <div className="va-float-card va-float-bottom"><span className="va-mini-icon va-mini-purple"><MessageSquareText size={15} /></span><span><b>Conversation insights</b><small>Context beyond the call</small></span><ArrowRight size={15} className="ml-auto text-slate-500" /></div>
            <div className="va-visual-caption"><span className="va-caption-line" /> VOICE AI · CONNECTED OPERATIONS</div>
          </div>
        </div>
        <div className="va-bottom-line" />
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-24 lg:px-8">
        <div className="va-proof-strip grid grid-cols-2 gap-6 rounded-2xl px-6 py-7 md:grid-cols-4 md:px-9">
          <div><p className="va-proof-label">ONE WORKSPACE</p><p className="va-proof-value">Unified</p><p className="va-proof-sub">Customer operations</p></div>
          <div><p className="va-proof-label">VOICE WORKFLOWS</p><p className="va-proof-value">Flexible</p><p className="va-proof-sub">Agent orchestration</p></div>
          <div><p className="va-proof-label">CALL INTELLIGENCE</p><p className="va-proof-value">Connected</p><p className="va-proof-sub">Records & insights</p></div>
          <div><p className="va-proof-label">OPERATIONAL CONTROL</p><p className="va-proof-value">Visible</p><p className="va-proof-sub">From launch to outcome</p></div>
        </div>
      </section>

      <section id="platform" className="mx-auto max-w-7xl scroll-mt-24 px-6 pb-28 lg:px-8">
        <div className="va-section-kicker"><span /> THE PLATFORM</div>
        <div className="mt-5 flex flex-col justify-between gap-5 md:flex-row md:items-end"><h2 className="va-section-title max-w-2xl">The complete picture.<br /><span className="va-muted-gradient">Without the complexity.</span></h2><p className="max-w-md text-sm leading-7 text-slate-400">Bring the moving parts of voice operations together. Give your team the context and control to do its best work.</p></div>
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{features.map(({icon:Icon,number,title,body})=><article className="va-feature-card group" key={number}><div className="flex items-center justify-between"><span className="va-feature-icon"><Icon size={20} /></span><span className="text-xs tracking-[.16em] text-slate-600">{number}</span></div><h3 className="mt-8 text-[17px] font-semibold tracking-tight">{title}</h3><p className="mt-3 text-[13px] leading-6 text-slate-400">{body}</p><div className="va-feature-line" /></article>)}</div>
      </section>

      <section id="how-it-works" className="va-process-section scroll-mt-24 border-y border-white/[.07]">
        <div className="mx-auto max-w-7xl px-6 py-24 lg:px-8">
          <div className="va-section-kicker"><span /> HOW IT WORKS</div><h2 className="va-section-title mt-5 max-w-2xl">From first setup<br />to <span className="va-gradient-text">better conversations.</span></h2>
          <div className="mt-14 grid gap-10 md:grid-cols-3">{steps.map((step,i)=><div className="va-step" key={step.n}><div className="flex items-center gap-4"><span className="va-step-number">{step.n}</span>{i !== 2 && <span className="hidden h-px flex-1 bg-gradient-to-r from-cyan-300/30 to-transparent md:block" />}</div><h3 className="mt-6 text-lg font-semibold">{step.title}</h3><p className="mt-3 max-w-sm text-sm leading-7 text-slate-400">{step.body}</p></div>)}</div>
        </div>
      </section>

      <section id="trust" className="mx-auto max-w-7xl scroll-mt-24 px-6 py-24 lg:px-8">
        <div className="va-trust-panel"><div className="va-trust-orb" /><div className="relative z-10 max-w-2xl"><div className="va-section-kicker"><span /> BUILT FOR RESPONSIBLE OPERATIONS</div><h2 className="mt-5 text-3xl font-semibold leading-tight tracking-[-.04em] sm:text-4xl">Powerful automation.<br /><span className="va-gradient-text">Human accountability.</span></h2><p className="mt-5 max-w-xl text-sm leading-7 text-slate-400">Keep consent, customer preferences, suppression and opt-out handling central to your calling workflows. Build automation with clear oversight and operational visibility.</p><div className="mt-7 flex flex-wrap gap-5 text-xs text-slate-300"><span className="flex items-center gap-2"><ShieldCheck size={15} className="text-cyan-300" /> Consent-aware workflows</span><span className="flex items-center gap-2"><Headphones size={15} className="text-cyan-300" /> Human hand-off</span></div></div><div className="va-trust-symbol"><ShieldCheck size={70} strokeWidth={1} /></div></div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-24 lg:px-8"><div className="va-cta flex flex-col items-start justify-between gap-8 p-8 sm:p-12 md:flex-row md:items-center"><div><div className="va-section-kicker"><span /> YOUR NEXT MOVE</div><h2 className="mt-4 text-3xl font-semibold tracking-[-.04em] sm:text-4xl">Bring your voice operations<br className="hidden sm:block" /> into focus.</h2><p className="mt-4 text-sm text-slate-400">Explore the VoiceAI workspace and see how the pieces fit together.</p></div><Link href="/dashboard" className="va-button shrink-0">Explore workspace <ArrowRight size={17} /></Link></div></section>

      <footer className="border-t border-white/[.08]"><div className="mx-auto flex max-w-7xl flex-col gap-5 px-6 py-8 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between lg:px-8"><Link href="/" className="flex items-center gap-2 font-semibold text-slate-300"><span className="va-brand-mark va-brand-mark-small"><AudioLines size={15} /></span> voice<span className="text-cyan-300">ai</span></Link><span>AI voice operations, designed for clarity.</span><span>© {new Date().getFullYear()} VoiceAI. All rights reserved.</span></div></footer>
      <style jsx global>{`
        .va-site{font-family:Arial,Helvetica,sans-serif;position:relative}
        .va-noise{position:absolute;inset:0;pointer-events:none;opacity:.12;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.17'/%3E%3C/svg%3E")}
        .va-nav-wrap{position:relative;z-index:30;border-bottom:1px solid rgba(255,255,255,.07);background:rgba(8,13,25,.78);backdrop-filter:blur(18px)}
        .va-brand-mark{display:grid;width:39px;height:39px;place-items:center;border:1px solid rgba(103,232,249,.35);border-radius:12px;background:linear-gradient(145deg,rgba(34,211,238,.2),rgba(99,102,241,.2));color:#8be9f5;box-shadow:0 0 30px rgba(34,211,238,.1)}
        .va-brand-mark-small{width:27px;height:27px;border-radius:8px}
        .va-nav-link{transition:color .2s}.va-nav-link:hover{color:#fff}
        .va-button{display:inline-flex;align-items:center;justify-content:center;gap:10px;border-radius:10px;padding:14px 19px;background:linear-gradient(105deg,#22d3ee,#6484ff 58%,#a78bfa);color:#06111e;font-size:13px;font-weight:700;box-shadow:0 8px 32px rgba(34,211,238,.16);transition:transform .25s,box-shadow .25s}
        .va-button:hover{transform:translateY(-2px);box-shadow:0 12px 38px rgba(34,211,238,.28)}
        .va-button-small{padding:11px 15px;font-size:12px}
        .va-button-ghost{display:inline-flex;align-items:center;gap:9px;border:1px solid rgba(255,255,255,.14);border-radius:10px;padding:13px 17px;color:#d7e1ef;font-size:13px;transition:background .2s,border .2s}.va-button-ghost:hover{background:rgba(255,255,255,.06);border-color:rgba(103,232,249,.35)}
        .va-hero{background:radial-gradient(ellipse at 70% 30%,rgba(25,75,135,.16),transparent 50%),linear-gradient(180deg,#080d19 0%,#0a1222 100%)}
        .va-hero-glow{position:absolute;z-index:-1;border-radius:999px;filter:blur(75px);pointer-events:none}.va-glow-one{width:420px;height:420px;right:5%;top:5%;background:rgba(34,211,238,.11);animation:va-drift 9s ease-in-out infinite alternate}.va-glow-two{width:320px;height:320px;left:20%;bottom:0;background:rgba(99,102,241,.1);animation:va-drift 12s ease-in-out infinite alternate-reverse}
        .va-eyebrow{display:inline-flex;align-items:center;gap:9px;border:1px solid rgba(103,232,249,.18);border-radius:99px;background:rgba(34,211,238,.055);padding:9px 13px;color:#9debf3;font-size:9px;font-weight:700;letter-spacing:.16em}
        .va-eyebrow-dot{width:6px;height:6px;border-radius:50%;background:#67e8f9;box-shadow:0 0 12px #67e8f9;animation:va-blink 2s infinite}
        .va-headline{color:#f4f7fb}.va-gradient-text{background:linear-gradient(100deg,#8be9f5 5%,#7b9bff 55%,#c4a5fd 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
        .va-visual{height:440px;display:grid;place-items:center;isolation:isolate}
        .va-orbit{position:absolute;border:1px solid rgba(125,211,252,.15);border-radius:50%;transform:rotate(-25deg);animation:va-rotate 30s linear infinite}
        .va-orbit-a{width:370px;height:270px}.va-orbit-b{width:480px;height:350px;transform:rotate(35deg);border-color:rgba(167,139,250,.14);animation-direction:reverse}
        .va-orbit:before,.va-orbit:after{content:'';position:absolute;width:7px;height:7px;border-radius:50%;background:#67e8f9;box-shadow:0 0 18px 3px rgba(103,232,249,.65)}.va-orbit:before{top:15%;left:20%}.va-orbit:after{bottom:12%;right:20%;background:#a78bfa;box-shadow:0 0 18px 3px rgba(167,139,250,.55)}
        .va-orbit-core{width:174px;height:174px;display:grid;place-items:center;border-radius:50%;background:radial-gradient(circle,rgba(34,211,238,.18),rgba(99,102,241,.07) 55%,transparent 70%);box-shadow:0 0 90px rgba(34,211,238,.1);animation:va-float 5s ease-in-out infinite}
        .va-core-inner{display:grid;width:104px;height:104px;place-items:center;border:1px solid rgba(125,211,252,.35);border-radius:32px;background:linear-gradient(145deg,rgba(20,184,220,.22),rgba(79,70,229,.2));color:#a5f3fc;box-shadow:inset 0 0 35px rgba(34,211,238,.12),0 20px 70px rgba(0,0,0,.35)}
        .va-float-card{position:absolute;z-index:3;display:flex;align-items:center;gap:12px;min-width:220px;border:1px solid rgba(255,255,255,.13);border-radius:13px;background:rgba(13,24,42,.83);padding:13px 15px;box-shadow:0 20px 60px rgba(0,0,0,.32);backdrop-filter:blur(16px);animation:va-float 5.5s ease-in-out infinite}
        .va-float-card b{display:block;font-size:11px;font-weight:600;color:#e7eef8}.va-float-card small{display:block;margin-top:4px;font-size:9px;color:#8191a8}.va-float-top{top:48px;right:0}.va-float-bottom{bottom:54px;left:0;animation-delay:-2.4s}
        .va-mini-icon{display:grid;width:32px;height:32px;place-items:center;border-radius:9px;background:rgba(34,211,238,.12);color:#67e8f9}.va-mini-purple{background:rgba(167,139,250,.13);color:#c4b5fd}.va-pulse{width:7px;height:7px;margin-left:auto;border-radius:50%;background:#4ade80;box-shadow:0 0 12px #4ade80}
        .va-visual-caption{position:absolute;bottom:4px;display:flex;align-items:center;gap:10px;color:#62738a;font-size:8px;letter-spacing:.2em}.va-caption-line{width:25px;height:1px;background:#67e8f9}
        .va-bottom-line{height:1px;background:linear-gradient(90deg,transparent,rgba(103,232,249,.28),rgba(167,139,250,.2),transparent)}
        .va-proof-strip{border:1px solid rgba(255,255,255,.09);background:linear-gradient(120deg,rgba(255,255,255,.045),rgba(255,255,255,.015));box-shadow:0 20px 80px rgba(0,0,0,.13)}
        .va-proof-label{font-size:8px;font-weight:700;letter-spacing:.16em;color:#718198}.va-proof-value{margin-top:8px;font-size:22px;font-weight:600;letter-spacing:-.04em;color:#e8f1fb}.va-proof-sub{margin-top:3px;font-size:10px;color:#8290a4}
        .va-section-kicker{display:flex;align-items:center;gap:10px;color:#8de7f2;font-size:9px;font-weight:700;letter-spacing:.2em}.va-section-kicker span{width:20px;height:1px;background:#67e8f9;box-shadow:0 0 10px #67e8f9}
        .va-section-title{font-size:clamp(2.3rem,4.5vw,3.7rem);font-weight:600;line-height:1.08;letter-spacing:-.055em;color:#f1f5fa}.va-muted-gradient{background:linear-gradient(90deg,#8292a9,#bac5d6);-webkit-background-clip:text;background-clip:text;color:transparent}
        .va-feature-card{position:relative;overflow:hidden;min-height:245px;border:1px solid rgba(255,255,255,.09);border-radius:15px;background:linear-gradient(145deg,rgba(255,255,255,.045),rgba(255,255,255,.012));padding:23px;transition:transform .3s,border-color .3s,background .3s}.va-feature-card:hover{transform:translateY(-5px);border-color:rgba(103,232,249,.3);background:linear-gradient(145deg,rgba(34,211,238,.07),rgba(255,255,255,.018))}.va-feature-icon{display:grid;width:42px;height:42px;place-items:center;border:1px solid rgba(103,232,249,.18);border-radius:12px;background:rgba(34,211,238,.08);color:#8de7f2}.va-feature-line{position:absolute;bottom:0;left:23px;width:0;height:2px;background:linear-gradient(90deg,#22d3ee,#a78bfa);transition:width .35s}.va-feature-card:hover .va-feature-line{width:calc(100% - 46px)}
        .va-process-section{background:radial-gradient(ellipse at 50% 0,rgba(45,74,125,.13),transparent 65%),rgba(255,255,255,.015)}.va-step-number{display:grid;width:43px;height:43px;place-items:center;border:1px solid rgba(103,232,249,.3);border-radius:12px;color:#8de7f2;font-size:12px;font-weight:700;background:rgba(34,211,238,.06)}
        .va-trust-panel{position:relative;overflow:hidden;display:flex;min-height:320px;align-items:center;justify-content:space-between;gap:35px;border:1px solid rgba(103,232,249,.14);border-radius:22px;background:linear-gradient(115deg,rgba(16,35,58,.95),rgba(20,23,49,.92));padding:45px}
        .va-trust-orb{position:absolute;width:450px;height:450px;right:0;top:-160px;border-radius:50%;background:radial-gradient(circle,rgba(34,211,238,.13),rgba(99,102,241,.06) 42%,transparent 70%);pointer-events:none}.va-trust-symbol{display:grid;width:155px;height:155px;flex-shrink:0;place-items:center;border:1px solid rgba(103,232,249,.2);border-radius:42px;background:linear-gradient(145deg,rgba(34,211,238,.1),rgba(99,102,241,.1));color:#9debf3;box-shadow:0 0 80px rgba(34,211,238,.08);transform:rotate(8deg)}
        .va-cta{border:1px solid rgba(103,232,249,.2);border-radius:20px;background:radial-gradient(ellipse at 80% 30%,rgba(34,211,238,.12),transparent 45%),linear-gradient(110deg,rgba(18,37,60,.95),rgba(21,25,52,.95))}
        @keyframes va-rotate{to{transform:rotate(335deg)}}@keyframes va-float{0%,100%{translate:0 0}50%{translate:0 -10px}}@keyframes va-drift{to{translate:25px -20px;scale:1.12}}@keyframes va-blink{0%,100%{opacity:1}50%{opacity:.35}}
        @media(max-width:640px){.va-visual{height:340px}.va-orbit-a{width:280px;height:205px}.va-orbit-b{width:340px;height:255px}.va-float-top{right:-5px;top:25px}.va-float-bottom{left:-5px;bottom:28px}.va-float-card{min-width:195px;padding:10px}.va-trust-panel{padding:28px}.va-trust-symbol{width:90px;height:90px;border-radius:25px}.va-trust-symbol svg{width:48px;height:48px}}
        @media(prefers-reduced-motion:reduce){.va-site *,.va-site *:before,.va-site *:after{animation-duration:.01ms!important;animation-iteration-count:1!important;scroll-behavior:auto!important;transition-duration:.01ms!important}}
      `}</style>
    </main>
  );
}
