'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  LayoutDashboard,
  Users,
  Phone,
  Bot,
  Activity,
  History,
  FileText,
  Mic,
  Table,
  Settings,
  BarChart3,
  Zap,
  Shield,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

const navigation = [
  { name: 'Overview', href: '/', icon: LayoutDashboard },
  { name: 'Customers', href: '/customers', icon: Users },
  { name: 'Campaigns', href: '/campaigns', icon: Zap },
  { name: 'AI Agent', href: '/ai-agent', icon: Bot },
  { name: 'Live Calls', href: '/live-calls', icon: Activity },
  { name: 'Call History', href: '/calls', icon: History },
  { name: 'Transcripts', href: '/transcripts', icon: FileText },
  { name: 'Recordings', href: '/recordings', icon: Mic },
  { name: 'Callbacks', href: '/callbacks', icon: Table },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Integrations', href: '/integrations', icon: Shield },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar({ collapsed = false, onToggle }: { collapsed?: boolean; onToggle: () => void }) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen border-r bg-card transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className={cn('flex h-16 items-center justify-between border-b px-4', collapsed && 'justify-center')}>
          {!collapsed && (
            <Link href="/" className="flex items-center space-x-2">
              <Phone className="h-8 w-8 text-primary" />
              <span className="font-bold text-xl">VoiceAI</span>
            </Link>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className={cn('h-8 w-8', collapsed && 'ml-auto')}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-3 overflow-y-auto" aria-label="Main navigation">
          {navigation.map((item) => {
            const isActive = (item.href === '/' ? pathname === '/' : pathname === item.href || pathname.startsWith(item.href + '/'));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                  collapsed && 'justify-center'
                )}
                title={collapsed ? item.name : undefined}
                aria-current={isActive ? 'page' : undefined}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                {!collapsed && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className={cn('border-t p-3', collapsed && 'hidden')}>
          <div className="rounded-lg bg-muted p-3 text-center">
            <p className="text-xs text-muted-foreground">
              Need help? <a href="https://github.com/Angrajkarn/voice-ai-#readme" target="_blank" rel="noreferrer" className="text-primary hover:underline">Documentation</a>
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export function MobileSidebarTrigger({ onOpen }: { onOpen: () => void }) {
  return (
    <Button variant="ghost" size="icon" className="lg:hidden" onClick={onOpen} aria-label="Open menu">
      <Menu className="h-5 w-5" />
    </Button>
  );
}

export function MobileSidebar({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const pathname = usePathname();

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-screen w-64 border-r bg-card lg:hidden transition-transform duration-300',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col">
          <div className="flex h-16 items-center justify-between border-b px-4">
            <Link href="/" className="flex items-center space-x-2" onClick={onClose}>
              <Phone className="h-8 w-8 text-primary" />
              <span className="font-bold text-xl">VoiceAI</span>
            </Link>
            <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close menu">
              <X className="h-5 w-5" />
            </Button>
          </div>

          <nav className="flex-1 space-y-1 p-3 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = item.href === '/' ? pathname === '/' : pathname === item.href || pathname.startsWith(item.href + '/');
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <item.icon className="h-5 w-5" aria-hidden="true" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </aside>
    </>
  );
}