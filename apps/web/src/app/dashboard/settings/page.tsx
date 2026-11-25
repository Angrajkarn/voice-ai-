'use client';

import * as React from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Building2, UserRound, Bell, ShieldCheck, Save, RefreshCw, Check, Clock3 } from 'lucide-react';

type Profile = { id: string; name: string | null; email: string; role: string; avatar_url?: string | null; created_at?: string; last_login_at?: string | null; organization_id: string };
type Workspace = { id: string; name: string; slug: string; plan: string; created_at?: string; is_active?: boolean };
type Notice = { id: string; title?: string; message?: string; body?: string; type?: string; created_at?: string; is_read?: boolean };

function Field({ label, value, onChange, placeholder }: { label: string; value: string; onChange: (value: string) => void; placeholder?: string }) {
  return <label className="block space-y-2"><span className="text-xs font-semibold text-base-content/65">{label}</span><input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className="h-11 w-full rounded-xl border border-base-300 bg-base-200/50 px-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15" /></label>;
}

export default function SettingsPage() {
  const [profile, setProfile] = React.useState<Profile | null>(null);
  const [workspace, setWorkspace] = React.useState<Workspace | null>(null);
  const [notices, setNotices] = React.useState<Notice[]>([]);
  const [name, setName] = React.useState('');
  const [workspaceName, setWorkspaceName] = React.useState('');
  const [loading, setLoading] = React.useState(true);
  const [savingProfile, setSavingProfile] = React.useState(false);
  const [savingWorkspace, setSavingWorkspace] = React.useState(false);
  const [message, setMessage] = React.useState('');
  const [error, setError] = React.useState('');

  const load = React.useCallback(async () => {
    try {
      setError('');
      const [p, w, n] = await Promise.all([
        api.get<Profile>('/settings/profile'),
        api.get<Workspace>('/settings/organization'),
        api.get<{ data: Notice[] }>('/notifications', { page: 1, pageSize: 8 }),
      ]);
      setProfile(p); setName(p.name || ''); setWorkspace(w); setWorkspaceName(w.name || '');
      setNotices(Array.isArray(n.data) ? n.data : []);
    } catch (e) { setError(e instanceof Error ? e.message : 'Unable to load account settings.'); }
    finally { setLoading(false); }
  }, []);

  React.useEffect(() => { void load(); }, [load]);

  async function saveProfile(event: React.FormEvent) {
    event.preventDefault(); setSavingProfile(true); setMessage(''); setError('');
    try {
      const updated = await api.patch<Profile>('/settings/profile', { name: name.trim() });
      setProfile((current) => current ? { ...current, ...updated } : updated);
      sessionStorage.setItem('voiceai_user', JSON.stringify({ ...profile, ...updated }));
      setMessage('Profile updated successfully.');
    } catch (e) { setError(e instanceof Error ? e.message : 'Profile could not be saved.'); }
    finally { setSavingProfile(false); }
  }

  async function saveWorkspace(event: React.FormEvent) {
    event.preventDefault(); setSavingWorkspace(true); setMessage(''); setError('');
    try {
      const updated = await api.patch<Workspace>('/settings/organization', { name: workspaceName.trim() });
      setWorkspace((current) => current ? { ...current, ...updated } : updated);
      setMessage('Workspace details updated.');
    } catch (e) { setError(e instanceof Error ? e.message : 'Workspace could not be saved.'); }
    finally { setSavingWorkspace(false); }
  }

  async function markAllRead() {
    try { await api.post('/notifications/read-all'); setNotices((items) => items.map((item) => ({ ...item, is_read: true }))); }
    catch (e) { setError(e instanceof Error ? e.message : 'Notifications could not be updated.'); }
  }

  return <DashboardLayout><div className="mx-auto max-w-[1280px] space-y-7">
    <header className="flex flex-wrap items-end justify-between gap-4">
      <div><p className="text-[10px] font-bold uppercase tracking-[.22em] text-primary">Account control center</p><h1 className="mt-2 text-3xl font-bold tracking-tight">Profile & settings</h1><p className="mt-2 max-w-2xl text-sm text-base-content/55">Manage your identity, workspace details and real account notifications.</p></div>
      <Button variant="outline" onClick={() => { setLoading(true); void load(); }} disabled={loading}><RefreshCw className={'mr-2 h-4 w-4 ' + (loading ? 'animate-spin' : '')}/>Refresh data</Button>
    </header>
    {error && <div role="alert" className="rounded-xl border border-error/25 bg-error/5 px-4 py-3 text-sm text-error">{error}</div>}
    {message && <div role="status" className="flex items-center gap-2 rounded-xl border border-success/25 bg-success/5 px-4 py-3 text-sm text-success"><Check className="h-4 w-4"/>{message}</div>}
    <div className="grid gap-5 xl:grid-cols-[1.1fr_.9fr]">
      <div className="space-y-5">
        <Card className="overflow-hidden border-base-300/80 shadow-sm"><div className="h-1 bg-gradient-to-r from-primary via-secondary to-primary"/><CardHeader><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-primary/10 text-primary"><UserRound className="h-5 w-5"/></span><div><CardTitle>Personal profile</CardTitle><p className="mt-1 text-xs text-base-content/50">Your authenticated VoiceAI identity</p></div></div></CardHeader><CardContent>
          {loading && !profile ? <p className="py-6 text-sm text-base-content/50">Loading account from API…</p> : profile ? <form onSubmit={saveProfile} className="space-y-5">
            <div className="flex items-center gap-4 rounded-2xl bg-base-200/60 p-4"><div className="grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-primary to-secondary text-lg font-bold text-primary-content">{(name || profile.email).split(/\s+/).slice(0,2).map(x=>x[0]).join('').toUpperCase()}</div><div className="min-w-0"><p className="truncate font-semibold">{name || 'Your profile'}</p><p className="truncate text-xs text-base-content/55">{profile.email}</p><Badge variant="outline" className="mt-2">{profile.role.replaceAll('_',' ')}</Badge></div></div>
            <Field label="Display name" value={name} onChange={setName} placeholder="Your name"/>
            <div className="grid gap-3 sm:grid-cols-2"><div className="rounded-xl border border-base-300 p-3"><p className="text-[10px] font-semibold uppercase tracking-wide text-base-content/45">Email address</p><p className="mt-1 truncate text-sm font-medium">{profile.email}</p><p className="mt-1 text-[10px] text-base-content/40">Managed by Firebase Authentication</p></div><div className="rounded-xl border border-base-300 p-3"><p className="text-[10px] font-semibold uppercase tracking-wide text-base-content/45">Access role</p><p className="mt-1 text-sm font-medium">{profile.role.replaceAll('_',' ')}</p><p className="mt-1 text-[10px] text-base-content/40">Assigned by workspace access</p></div></div>
            <Button type="submit" disabled={savingProfile || !name.trim()}><Save className="mr-2 h-4 w-4"/>{savingProfile ? 'Saving…' : 'Save profile'}</Button>
          </form> : <p className="text-sm text-base-content/50">Profile data is not available.</p>}
        </CardContent></Card>
        <Card className="border-base-300/80 shadow-sm"><CardHeader><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-secondary/10 text-secondary"><Building2 className="h-5 w-5"/></span><div><CardTitle>Workspace details</CardTitle><p className="mt-1 text-xs text-base-content/50">Organization information stored by the backend</p></div></div></CardHeader><CardContent>
          {workspace ? <form onSubmit={saveWorkspace} className="space-y-4"><Field label="Workspace name" value={workspaceName} onChange={setWorkspaceName} placeholder="Workspace name"/><div className="grid gap-3 sm:grid-cols-2"><div className="rounded-xl border border-base-300 p-3"><p className="text-[10px] font-semibold uppercase tracking-wide text-base-content/45">Workspace slug</p><p className="mt-1 text-sm font-medium">{workspace.slug}</p></div><div className="rounded-xl border border-base-300 p-3"><p className="text-[10px] font-semibold uppercase tracking-wide text-base-content/45">Current plan</p><p className="mt-1 text-sm font-medium">{workspace.plan}</p></div></div><Button type="submit" variant="outline" disabled={savingWorkspace || !workspaceName.trim()}><Save className="mr-2 h-4 w-4"/>{savingWorkspace ? 'Saving…' : 'Update workspace'}</Button></form> : <p className="text-sm text-base-content/50">Loading workspace…</p>}
        </CardContent></Card>
      </div>
      <div className="space-y-5">
        <Card className="border-base-300/80 shadow-sm"><CardHeader><div className="flex items-center justify-between"><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-warning/10 text-warning"><Bell className="h-5 w-5"/></span><div><CardTitle>Workspace notifications</CardTitle><p className="mt-1 text-xs text-base-content/50">Events delivered by the notifications API</p></div></div><Button variant="ghost" size="sm" onClick={() => void markAllRead()}>Mark all read</Button></div></CardHeader><CardContent className="space-y-1">
          {notices.length === 0 ? <div className="rounded-xl bg-base-200/50 px-4 py-10 text-center"><Bell className="mx-auto h-6 w-6 text-base-content/30"/><p className="mt-2 text-sm font-medium">No notifications yet</p><p className="mt-1 text-xs text-base-content/45">Real campaign, call and integration events will appear here.</p></div> : notices.map((item) => <div key={item.id} className="flex gap-3 rounded-xl px-3 py-3 hover:bg-base-200/60"><span className={'mt-1.5 h-2 w-2 shrink-0 rounded-full ' + (item.is_read ? 'bg-base-content/20' : 'bg-primary')}/><div className="min-w-0 flex-1"><p className="text-sm font-semibold">{item.title || item.type?.replaceAll('_',' ') || 'Workspace event'}</p><p className="mt-1 line-clamp-2 text-xs text-base-content/55">{item.message || item.body || 'A workspace event was recorded.'}</p><p className="mt-1 text-[10px] text-base-content/35">{item.created_at ? new Date(item.created_at).toLocaleString() : ''}</p></div>{!item.is_read && <Badge variant="outline">New</Badge>}</div>)}
        </CardContent></Card>
        <Card className="border-base-300/80 shadow-sm"><CardHeader><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-success/10 text-success"><ShieldCheck className="h-5 w-5"/></span><div><CardTitle>Security & access</CardTitle><p className="mt-1 text-xs text-base-content/50">Current account facts from the server</p></div></div></CardHeader><CardContent className="space-y-3">
          <div className="flex items-center justify-between gap-3"><span className="text-xs text-base-content/55">Account status</span><Badge variant="success">Authenticated</Badge></div>
          <div className="flex items-center justify-between gap-3"><span className="text-xs text-base-content/55">User ID</span><span className="max-w-[190px] truncate font-mono text-[10px] text-base-content/55">{profile?.id || '—'}</span></div>
          <div className="flex items-center justify-between gap-3"><span className="text-xs text-base-content/55">Last sign-in</span><span className="text-xs font-medium">{profile?.last_login_at ? new Date(profile.last_login_at).toLocaleString() : 'Not provided'}</span></div>
          <div className="flex items-center gap-2 border-t border-base-300 pt-3 text-[11px] leading-5 text-base-content/45"><Clock3 className="h-4 w-4 shrink-0"/>Password and email authentication are managed by Firebase. This panel does not claim to change credentials.</div>
        </CardContent></Card>
      </div>
    </div>
  </div></DashboardLayout>;
}
