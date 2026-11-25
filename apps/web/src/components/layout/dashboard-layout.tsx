'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar, MobileSidebar, MobileSidebarTrigger } from '@/components/ui/sidebar';
import { cn } from '@/lib/utils';
import { Bell, Moon, Sun, User, LogOut, Settings, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel,
  DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Toaster } from '@/components/ui/toaster';
import Link from 'next/link';
import { useTheme } from 'next-themes';
import { api } from '@/lib/api';
import { getStoredVoiceAIUser, logoutVoiceAI, type VoiceAIUser } from '@/lib/firebase-auth';

interface DashboardLayoutProps { children: React.ReactNode }

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = React.useState(false);
  const [profile, setProfile] = React.useState<VoiceAIUser | null>(null);
  const [profileLoading, setProfileLoading] = React.useState(true);
  const [loggingOut, setLoggingOut] = React.useState(false);
  const { theme, setTheme } = useTheme();
  const router = useRouter();

  React.useEffect(() => {
    let active = true;
    setProfile(getStoredVoiceAIUser());
    api.get<VoiceAIUser>('/auth/me')
      .then((user) => {
        if (!active) return;
        setProfile(user);
        sessionStorage.setItem('voiceai_user', JSON.stringify(user));
      })
      .catch(() => {
        if (active && !sessionStorage.getItem('voiceai_access_token')) router.replace('/login');
      })
      .finally(() => { if (active) setProfileLoading(false); });
    return () => { active = false; };
  }, [router]);

  async function handleLogout() {
    setLoggingOut(true);
    try { await logoutVoiceAI(); }
    finally { router.replace('/login'); router.refresh(); }
  }

  const displayName = profile?.name?.trim() || profile?.email?.split('@')[0] || (profileLoading ? 'Loading profile…' : 'Account');
  const initials = displayName.split(/\s+/).slice(0, 2).map((part) => part[0]?.toUpperCase()).join('') || 'U';

  return (
    <div className="min-h-screen bg-base-200/50">
      <MobileSidebar isOpen={mobileSidebarOpen} onClose={() => setMobileSidebarOpen(false)} />
      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
      <div className={cn('min-h-screen transition-all duration-300 lg:pl-64', sidebarCollapsed && 'lg:pl-16')}>
        <header className="navbar sticky top-0 z-30 h-16 min-h-16 border-b border-base-300 bg-base-100/90 px-4 backdrop-blur-xl">
          <MobileSidebarTrigger onOpen={() => setMobileSidebarOpen(true)} />
          <div className="flex-1" />
          <Button variant="ghost" size="icon" onClick={() => setTheme(theme === 'voiceai' ? 'voiceai-light' : 'voiceai')} aria-label="Toggle theme">
            {theme === 'voiceai-light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
          </Button>
          <Button variant="ghost" size="icon" aria-label="Notifications"><Bell className="h-5 w-5" /></Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-10 gap-2 rounded-xl px-2">
                <span className="avatar placeholder"><span className="grid h-8 w-8 place-items-center rounded-full bg-primary/15 text-xs font-bold text-primary">{initials}</span></span>
                <span className="hidden max-w-36 text-left sm:block"><span className="block truncate text-xs font-semibold">{displayName}</span><span className="block truncate text-[10px] text-base-content/55">{profile?.email || 'Signed-in account'}</span></span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-64 border-base-300 bg-base-100" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col gap-1">
                  <p className="text-sm font-semibold">{displayName}</p>
                  <p className="text-xs text-base-content/60">{profile?.email || 'Loading account…'}</p>
                  <p className="flex items-center gap-1 text-xs text-base-content/50"><Building2 size={12}/>{profile?.organization_name || 'Workspace'}</p>
                  {profile?.role && <span className="badge badge-outline mt-1 w-fit">{profile.role.replaceAll('_', ' ')}</span>}
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild><Link href="/dashboard/settings"><User className="mr-2 h-4 w-4" />Profile</Link></DropdownMenuItem>
              <DropdownMenuItem asChild><Link href="/dashboard/settings"><Settings className="mr-2 h-4 w-4" />Settings</Link></DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem disabled={loggingOut} className="text-error focus:text-error" onClick={handleLogout}><LogOut className="mr-2 h-4 w-4" />{loggingOut ? 'Signing out…' : 'Log out'}</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>
        <main className="p-4 lg:p-6">{children}</main>
      </div>
      <Toaster />
    </div>
  );
}
