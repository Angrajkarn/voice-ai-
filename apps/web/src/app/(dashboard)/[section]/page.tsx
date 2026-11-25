'use client';

import * as React from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, Radio, Bot, FileText, Mic, BarChart3, Plug, Settings, PhoneCall, CalendarClock } from 'lucide-react';

type SectionConfig = { title: string; description: string; endpoint?: string; icon: React.ElementType; refresh?: boolean; empty?: string };

const sections: Record<string, SectionConfig> = {
  'ai-agent': { title: 'AI Agent', description: 'Configure the voice agent that handles your customer conversations.', icon: Bot, empty: 'The AI agent management API is not exposed by the current backend yet. Connect the agent service before enabling production controls.' },
  'live-calls': { title: 'Live calls', description: 'Monitor calls currently being processed by your campaigns.', endpoint: '/calls?page=1&pageSize=50', icon: Radio, refresh: true, empty: 'No active calls were returned by the API.' },
  calls: { title: 'Call history', description: 'Review call outcomes, durations and customer interactions.', endpoint: '/calls?page=1&pageSize=50', icon: PhoneCall, refresh: true },
  transcripts: { title: 'Transcripts', description: 'Open call conversations and review their transcript records.', endpoint: '/calls?page=1&pageSize=50', icon: FileText, refresh: true, empty: 'No calls with transcript data were returned.' },
  recordings: { title: 'Recordings', description: 'Find calls and open their associated audio recordings.', endpoint: '/calls?page=1&pageSize=50', icon: Mic, refresh: true, empty: 'No calls with recording data were returned.' },
  callbacks: { title: 'Callbacks', description: 'Track scheduled follow-ups and callback outcomes.', endpoint: '/callbacks?page=1&pageSize=50', icon: CalendarClock, refresh: true },
  analytics: { title: 'Analytics', description: 'Explore organization performance and calling trends.', icon: BarChart3, refresh: true, empty: 'Analytics are not available for this organization yet.' },
  integrations: { title: 'Integrations', description: 'Manage connected services for your VoiceAI workspace.', icon: Plug, empty: 'No integrations are connected to this workspace yet.' },
  settings: { title: 'Settings', description: 'Manage your account profile and workspace preferences.', icon: Settings, empty: 'No profile settings were returned.' },
};

function recordsFrom(payload: any): any[] {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.items)) return payload.items;
  if (payload && typeof payload === 'object') return [payload];
  return [];
}

function readable(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

export default function SectionPage() {
  const params = useParams<{ section: string }>();
  const section = params.section;
  const config = sections[section];
  const [records, setRecords] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');
  const [lastUpdated, setLastUpdated] = React.useState<Date | null>(null);

  const load = React.useCallback(async () => {
    if (!config) { setLoading(false); return; }
    if (!config.endpoint && !['analytics', 'integrations', 'settings'].includes(section)) {
      setRecords([]); setLoading(false); return;
    }
    try {
      setError('');
      let payload: any;
      if (config.endpoint) payload = await api.get<any>(config.endpoint);
      else if (section === 'settings') payload = await api.get<any>('/settings/profile');
      else if (section === 'analytics') payload = await api.get<any>('/analytics/organization', { period: 'daily', days: 30 });
      else {
        const org = await api.get<any>('/organizations/current');
        if (!org?.id) throw new Error('Your workspace could not be resolved. Please sign in again.');
        payload = await api.get<any>('/integrations', { organizationId: org.id });
      }
      setRecords(recordsFrom(payload));
      setLastUpdated(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load this section.');
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, [config, section]);

  React.useEffect(() => {
    setLoading(true);
    void load();
    if (!config?.refresh) return;
    const timer = window.setInterval(() => void load(), 30000);
    return () => window.clearInterval(timer);
  }, [load, config?.refresh]);

  if (!config) {
    return <DashboardLayout><div className="mx-auto max-w-3xl py-16 text-center"><h1 className="text-2xl font-semibold">Section not found</h1><p className="mt-2 text-muted-foreground">Choose a section from the navigation.</p><Button className="mt-6" onClick={() => window.location.assign('/')}>Back to overview</Button></div></DashboardLayout>;
  }

  const Icon = config.icon;
  const columns = records.length ? Object.keys(records[0]).filter(key => !['__v'].includes(key)).slice(0, 6) : [];

  return (
    <DashboardLayout>
      <div className="mx-auto w-full max-w-[1600px] space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex items-start gap-3">
            <div className="rounded-xl border bg-card p-3"><Icon className="h-6 w-6 text-primary" /></div>
            <div><p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">Workspace</p><h1 className="mt-1 text-3xl font-semibold tracking-tight">{config.title}</h1><p className="mt-1 text-sm text-muted-foreground">{config.description}</p></div>
          </div>
          <div className="flex items-center gap-3">
            {lastUpdated && <span className="text-xs text-muted-foreground">Updated {lastUpdated.toLocaleTimeString()}</span>}
            <Button variant="outline" size="sm" onClick={() => { setLoading(true); void load(); }} disabled={loading}><RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />Refresh</Button>
          </div>
        </div>

        {error && <div role="alert" className="rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"><strong>Could not load live data.</strong> {error}</div>}

        <Card className="overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between border-b">
            <div><CardTitle className="text-base">{config.title} records</CardTitle><p className="mt-1 text-sm text-muted-foreground">{config.refresh ? 'Automatically refreshes every 30 seconds' : 'Live data from your workspace API'}</p></div>
            <Badge variant="outline">{loading ? 'Loading' : `${records.length} records`}</Badge>
          </CardHeader>
          <CardContent className="p-0">
            {loading && records.length === 0 ? <div className="p-10 text-center text-sm text-muted-foreground">Loading workspace data…</div>
              : records.length === 0 ? <div className="px-6 py-14 text-center"><div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-muted"><Icon className="h-5 w-5 text-muted-foreground" /></div><p className="font-medium">Nothing to show yet</p><p className="mx-auto mt-1 max-w-lg text-sm text-muted-foreground">{config.empty || 'No records match this view. New records will appear here when your workspace receives activity.'}</p></div>
              : <div className="overflow-x-auto"><table className="w-full min-w-[720px] text-sm"><thead className="bg-muted/40 text-left text-xs uppercase tracking-wide text-muted-foreground"><tr>{columns.map(key => <th key={key} className="px-5 py-3 font-medium">{key.replace(/([A-Z])/g, ' $1').replaceAll('_', ' ')}</th>)}</tr></thead><tbody>{records.map((record, index) => <tr key={String(record.id || record.uuid || index)} className="border-t transition-colors hover:bg-muted/30">{columns.map(key => <td key={key} className="max-w-[280px] truncate px-5 py-4" title={readable(record[key])}>{readable(record[key])}</td>)}</tr>)}</tbody></table></div>}
          </CardContent>
        </Card>
        {['calls', 'live-calls', 'transcripts', 'recordings'].includes(section) && <p className="text-xs text-muted-foreground">Call records are loaded from the Calls API. Detailed transcript and recording playback depend on the individual call having those assets and the API returning their identifiers.</p>}
      </div>
    </DashboardLayout>
  );
}
