'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import {
  Bell, Moon, Sun, User, LogOut, Settings, Building2, CheckCheck,
  Command, Search, ChevronDown, Activity, CircleHelp
} from 'lucide-react';
import { Sidebar, MobileSidebar, MobileSidebarTrigger } from '@/components/ui/sidebar';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel,
  DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Toaster } from '@/components/ui/toaster';
import { api } from '@/lib/api';
import { getStoredVoiceAIUser, logoutVoiceAI, type VoiceAIUser } from '@/lib/firebase-auth';

interface DashboardLayoutProps { children: React.ReactNode }
type Notice = { id: string; title?: string; message?: string; body?: string; type?: string; created_at?: string; is_read?: boolean; read_at?: string };

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = React.useState(false);
  const [profile, setProfile] = React.useState<VoiceAIUser | null>(null);
  const [profileLoading, setProfileLoading] = React.useState(true);
  const [loggingOut, setLoggingOut] = React.useState(false);
  const [notices, setNotices] = React.useState<Notice[]>([]);
  const [unreadCount, setUnreadCount] = React.useState(0);
  const [apiOnline, setApiOnline] = React.useState<boolean | null>(null);
  const { theme, setTheme } = useTheme();
  const router = useRouter();
  const pathname = usePathname();

  const refreshHeaderData = React.useCallback(async () => {
    const results = await Promise.allSettled([
      api.get<VoiceAIUser>('/auth/me'),
      api.get<{ unread_count: number }>('/notifications/unread-count'),
      api.get<{ data: Notice[] }>('/notifications', { page: 1, pageSize: 6 }),
    ]);
    if (results[0].status === 'fulfilled') {
      setProfile(results[0].value);
      sessionStorage.setItem('voiceai_user', JSON.stringify(results[0].value));
      setApiOnline(true);
    } else setApiOnline(false);
    if (results[1].status === 'fulfilled') setUnreadCount(Number(results[1].value.unread_count || 0));
    if (results[2].status === 'fulfilled') setNotices(Array.isArray(results[2].value.data) ? results[2].value.data : []);
    setProfileLoading(false);
  }, []);

  React.useEffect(() => {
    setProfile(getStoredVoiceAIUser());
    void refreshHeaderData();
    const timer = window.setInterval(() => void refreshHeaderData(), 15000);
    return () => window.clearInterval(timer);
  }, [refreshHeaderData]);

  async function handleLogout() {
    setLoggingOut(true);
    try { await logoutVoiceAI(); }
    finally { router.replace('/login'); router.refresh(); }
  }

  async function markRead(id: string) {
    try {
      await api.patch('/notifications/' + id + '/read');
      setNotices((items) => items.map((item) => item.id === id ? { ...item, is_read: true } : item));
      setUnreadCount((count) => Math.max(0, count - 1));
    } catch { /* Keep the unread state if the API rejects the update. */ }
  }

  async function markAllRead() {
    try {
      await api.post('/notifications/read-all');
      setNotices((items) => items.map((item) => ({ ...item, is_read: true })));
      setUnreadCount(0);
    } catch { /* Keep the unread state if the API rejects the update. */ }
  }

  const displayName = profile?.name?.trim() || profile?.email?.split('@')[0] || (profileLoading ? 'Loading…' : 'Account');
  const initials = displayName.split(/\s+/).slice(0, 2).map((part) => part[0]?.toUpperCase()).join('') || 'U';
  const sectionName = pathname === '/dashboard' ? 'Overview' : pathname.split('/').filter(Boolean).at(-1)?.replaceAll('-', ' ') || 'Workspace';

  return (
    <div className="min-h-screen bg-base-200/50">
      <MobileSidebar isOpen={mobileSidebarOpen} onClose={() => setMobileSidebarOpen(false)} />
      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
      <div className={cn('min-h-screen transition-[padding] duration-300 lg:pl-64', sidebarCollapsed && 'lg:pl-20')}>
        <header className="sticky top-0 z-30 flex h-[72px] items-center gap-3 border-b border-base-300/80 bg-base-100/85 px-4 backdrop-blur-2xl lg:px-7">
          <MobileSidebarTrigger onOpen={() => setMobileSidebarOpen(true)} />
          <div className="hidden min-w-0 items-center gap-2 text-sm md:flex">
            <span className="text-base-content/45">Workspace</span>
            <span className="text-base-content/25">/</span>
            <span className="truncate font-semibold capitalize text-base-content">{sectionName}</span>
          </div>
          <div className="flex-1" />
          <div className="hidden items-center gap-2 rounded-full border border-base-300 bg-base-200/70 px-3 py-1.5 text-[11px] font-medium text-base-content/65 sm:flex">
            <span className={cn('h-1.5 w-1.5 rounded-full', apiOnline === true ? 'bg-emerald-500 shadow-[0_0_0_3px_rgba(16,185,129,.12)]' : apiOnline === false ? 'bg-rose-500' : 'bg-amber-400')} />
            {apiOnline === true ? 'API connected' : apiOnline === false ? 'API unavailable' : 'Connecting'}
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative h-10 w-10 rounded-xl" aria-label="Notifications">
                <Bell className="h-[18px] w-[18px]" />
                {unreadCount > 0 && <span className="absolute right-1 top-1 grid h-[17px] min-w-[17px] place-items-center rounded-full bg-primary px-1 text-[9px] font-bold text-primary-content">{unreadCount > 99 ? '99+' : unreadCount}</span>}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[min(92vw,380px)] border-base-300 bg-base-100 p-0">
              <div className="flex items-center justify-between border-b border-base-300 px-4 py-3">
                <div><p className="text-sm font-semibold">Notifications</p><p className="text-xs text-base-content/50">{unreadCount} unread · refreshes every 15 sec</p></div>
                {unreadCount > 0 && <button onClick={() => void markAllRead()} className="text-xs font-semibold text-primary hover:underline">Mark all read</button>}
              </div>
              <div className="max-h-[360px] overflow-y-auto">
                {notices.length === 0 ? <p className="px-4 py-8 text-center text-sm text-base-content/50">No notifications from your workspace yet.</p> : notices.map((notice) => (
                  <div key={notice.id} className={cn('flex gap-3 border-b border-base-300/60 px-4 py-3 last:border-0', !notice.is_read && 'bg-primary/[0.04]')}>
                    <span className={cn('mt-1.5 h-2 w-2 shrink-0 rounded-full', notice.is_read ? 'bg-base-content/20' : 'bg-primary')} />
                    <div className="min-w-0 flex-1"><p className="text-sm font-medium">{notice.title || notice.type?.replaceAll('_', ' ') || 'Workspace update'}</p><p className="mt-0.5 line-clamp-2 text-xs text-base-content/60">{notice.message || notice.body || 'A new workspace event was recorded.'}</p><p className="mt-1 text-[10px] text-base-content/40">{notice.created_at ? new Date(notice.created_at).toLocaleString() : ''}</p></div>
                    {!notice.is_read && <button onClick={() => void markRead(notice.id)} className="self-center text-[10px] font-semibold text-primary">Read</button>}
                  </div>
                ))}
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button variant="ghost" size="icon" className="h-10 w-10 rounded-xl" onClick={() => setTheme(theme === 'voiceai' ? 'voiceai-light' : 'voiceai')} aria-label="Toggle theme">
            {theme === 'voiceai-light' ? <Moon className="h-[18px] w-[18px]" /> : <Sun className="h-[18px] w-[18px]" />}
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-10 gap-2 rounded-xl px-2 hover:bg-base-200">
                <span className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-primary to-secondary text-xs font-bold text-primary-content">{initials}</span>
                <span className="hidden max-w-40 truncate text-sm font-semibold sm:block">{displayName}</span>
                <ChevronDown className="hidden h-3.5 w-3.5 text-base-content/45 sm:block" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-64 border-base-300 bg-base-100" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex items-center gap-3 py-1">
                  <span className="grid h-10 w-10 place-items-center rounded-full bg-primary/10 text-sm font-bold text-primary">{initials}</span>
                  <div className="min-w-0"><p className="truncate text-sm font-semibold">{displayName}</p><p className="truncate text-xs text-base-content/55">{profile?.email || 'Signed-in account'}</p></div>
                </div>
                <p className="mt-3 flex items-center gap-2 text-xs text-base-content/55"><Building2 size={13}/>{profile?.organization_name || 'Workspace'}{profile?.role ? ' · ' + profile.role.replaceAll('_', ' ') : ''}</p>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild><Link href="/dashboard/settings"><User className="mr-2 h-4 w-4" />Profile & settings</Link></DropdownMenuItem>
              <DropdownMenuItem asChild><Link href="/dashboard/integrations"><Settings className="mr-2 h-4 w-4" />Integrations</Link></DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem disabled={loggingOut} className="text-error focus:text-error" onClick={handleLogout}><LogOut className="mr-2 h-4 w-4" />{loggingOut ? 'Signing out…' : 'Log out'}</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>
        <main className="px-4 py-6 lg:px-7 lg:py-8">{children}</main>
      </div>
      <Toaster />
    </div>
  );
}
