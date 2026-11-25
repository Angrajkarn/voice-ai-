'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  LayoutDashboard, Users, Bot, Activity, History, FileText, Mic,
  Table, Settings, BarChart3, Zap, Shield, Menu, X, ChevronLeft,
  ChevronRight, Headphones, Sparkles
} from 'lucide-react';

const navigation = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard, group: 'WORKSPACE' },
  { name: 'Customers', href: '/dashboard/customers', icon: Users, group: 'WORKSPACE' },
  { name: 'Campaigns', href: '/dashboard/campaigns', icon: Zap, group: 'WORKSPACE' },
  { name: 'AI Agent', href: '/dashboard/ai-agent', icon: Bot, group: 'VOICE OPERATIONS' },
  { name: 'Live Calls', href: '/dashboard/live-calls', icon: Activity, group: 'VOICE OPERATIONS' },
  { name: 'Call History', href: '/dashboard/calls', icon: History, group: 'VOICE OPERATIONS' },
  { name: 'Transcripts', href: '/dashboard/transcripts', icon: FileText, group: 'VOICE OPERATIONS' },
  { name: 'Recordings', href: '/dashboard/recordings', icon: Mic, group: 'VOICE OPERATIONS' },
  { name: 'Callbacks', href: '/dashboard/callbacks', icon: Table, group: 'VOICE OPERATIONS' },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3, group: 'INSIGHTS & ADMIN' },
  { name: 'Integrations', href: '/dashboard/integrations', icon: Shield, group: 'INSIGHTS & ADMIN' },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings, group: 'INSIGHTS & ADMIN' },
];

function NavItems({ collapsed, onNavigate }: { collapsed: boolean; onNavigate?: () => void }) {
  const pathname = usePathname();
  let previousGroup = '';
  return <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Main navigation">
    {navigation.map((item) => {
      const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href + '/'));
      const showGroup = item.group !== previousGroup;
      previousGroup = item.group;
      return <React.Fragment key={item.name}>
        {showGroup && !collapsed && <p className="mb-2 mt-5 px-3 text-[9px] font-bold tracking-[.2em] text-base-content/35 first:mt-1">{item.group}</p>}
        {showGroup && collapsed && <div className="mx-3 my-3 border-t border-base-300" />}
        <Link href={item.href} onClick={onNavigate} title={collapsed ? item.name : undefined} aria-current={isActive ? 'page' : undefined}
          className={cn('group relative mb-1 flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium transition-all duration-200',
            isActive ? 'bg-primary/12 text-primary shadow-sm' : 'text-base-content/55 hover:bg-base-200 hover:text-base-content',
            collapsed && 'justify-center px-2')}>
          {isActive && <span className="absolute bottom-2 left-0 top-2 w-[3px] rounded-r-full bg-primary" />}
          <item.icon className={cn('h-[17px] w-[17px] shrink-0 transition-transform group-hover:scale-105', isActive && 'text-primary')} />
          {!collapsed && <span className="flex-1">{item.name}</span>}
          {!collapsed && item.name === 'AI Agent' && <span className="rounded-md border border-base-300 px-1.5 py-0.5 text-[8px] font-semibold tracking-wide text-base-content/35">BETA</span>}
        </Link>
      </React.Fragment>;
    })}
  </nav>;
}

export function Sidebar({ collapsed = false, onToggle }: { collapsed?: boolean; onToggle: () => void }) {
  return <aside className={cn('fixed left-0 top-0 z-40 hidden h-screen border-r border-base-300/80 bg-base-100/95 transition-all duration-300 lg:block', collapsed ? 'w-20' : 'w-64')}>
    <div className="flex h-full flex-col">
      <div className={cn('flex h-[72px] items-center border-b border-base-300/80 px-5', collapsed ? 'justify-center' : 'justify-between')}>
        {!collapsed && <Link href="/dashboard" className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-primary to-secondary text-primary-content shadow-lg shadow-primary/20"><Headphones className="h-5 w-5" /></span><span className="text-[17px] font-bold tracking-tight">voice<span className="text-primary">ai</span></span></Link>}
        {collapsed && <Link href="/dashboard" aria-label="VoiceAI home" className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-primary to-secondary text-primary-content"><Headphones className="h-5 w-5" /></Link>}
        {!collapsed && <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg text-base-content/45" onClick={onToggle} aria-label="Collapse sidebar"><ChevronLeft className="h-4 w-4" /></Button>}
        {collapsed && <Button variant="ghost" size="icon" className="absolute -right-3 top-[84px] h-7 w-7 rounded-full border border-base-300 bg-base-100 shadow-sm" onClick={onToggle} aria-label="Expand sidebar"><ChevronRight className="h-3.5 w-3.5" /></Button>}
      </div>
      <NavItems collapsed={collapsed} />
      {!collapsed && <div className="m-3 rounded-2xl border border-primary/15 bg-gradient-to-br from-primary/[0.09] to-secondary/[0.08] p-3.5">
        <div className="mb-2 flex items-center gap-2 text-primary"><Sparkles className="h-4 w-4" /><span className="text-[11px] font-bold">VoiceAI workspace</span></div>
        <p className="text-[10px] leading-5 text-base-content/55">Your calls, campaigns and customer insights in one place.</p>
        <a href="https://github.com/Angrajkarn/voice-ai-#readme" target="_blank" rel="noreferrer" className="mt-2 inline-block text-[10px] font-semibold text-primary hover:underline">Read documentation ↗</a>
      </div>}
      {collapsed && <div className="p-3 text-center"><a href="https://github.com/Angrajkarn/voice-ai-#readme" target="_blank" rel="noreferrer" aria-label="Documentation" className="text-base-content/40 hover:text-primary"><Shield className="mx-auto h-4 w-4" /></a></div>}
      <div className="border-t border-base-300 px-4 py-3"><p className="text-center text-[9px] font-medium tracking-wide text-base-content/30">{collapsed ? 'VAI' : 'VOICEAI · WORKSPACE'}</p></div>
    </div>
  </aside>;
}

export function MobileSidebarTrigger({ onOpen }: { onOpen: () => void }) {
  return <Button variant="ghost" size="icon" className="rounded-xl lg:hidden" onClick={onOpen} aria-label="Open menu"><Menu className="h-5 w-5" /></Button>;
}

export function MobileSidebar({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  return <>
    {isOpen && <button type="button" className="fixed inset-0 z-40 bg-black/55 backdrop-blur-sm lg:hidden" onClick={onClose} aria-label="Close navigation" />}
    <aside className={cn('fixed left-0 top-0 z-50 flex h-screen w-[min(84vw,300px)] flex-col border-r border-base-300 bg-base-100 shadow-2xl transition-transform duration-300 lg:hidden', isOpen ? 'translate-x-0' : '-translate-x-full')}>
      <div className="flex h-[72px] items-center justify-between border-b border-base-300 px-5">
        <Link href="/dashboard" onClick={onClose} className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-primary to-secondary text-primary-content"><Headphones className="h-5 w-5" /></span><span className="text-[17px] font-bold">voice<span className="text-primary">ai</span></span></Link>
        <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close menu"><X className="h-5 w-5" /></Button>
      </div>
      <NavItems collapsed={false} onNavigate={onClose} />
    </aside>
  </>;
}
