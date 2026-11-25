'use client';
import * as React from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Activity, Users, Phone, CheckCircle2, XCircle, Clock3, Target, Flame, RefreshCw, Plus, CalendarDays, Radio, AlertCircle } from 'lucide-react';
import { ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip, Legend, AreaChart, Area, Line, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { cn, formatDuration, formatRelativeTime, getStatusColor } from '@/lib/utils';
import { api, callsApi, campaignsApi } from '@/lib/api';

type Row = Record<string, any>;
type Day = { date: string; total_calls: number; completed_calls: number; failed_calls: number; hot_leads: number; warm_leads: number; cold_leads: number };
const n = (v: unknown) => Number(v ?? 0);
const fmt = (v: unknown) => n(v).toLocaleString('en-IN');
const customerName = (c: Row) => c.customer?.name || [c.customer?.first_name, c.customer?.last_name].filter(Boolean).join(' ') || c.customer_name || 'Unknown customer';

export default function DashboardPage() {
  const [days, setDays] = React.useState('30');
  const [statusFilter, setStatusFilter] = React.useState('all');
  const [campaignFilter, setCampaignFilter] = React.useState('all');
  const [analytics, setAnalytics] = React.useState<Row | null>(null);
  const [calls, setCalls] = React.useState<Row[]>([]);
  const [activeCalls, setActiveCalls] = React.useState<Row[]>([]);
  const [campaigns, setCampaigns] = React.useState<Row[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [refreshing, setRefreshing] = React.useState(false);
  const [error, setError] = React.useState('');
  const [updatedAt, setUpdatedAt] = React.useState<Date | null>(null);

  const load = React.useCallback(async (quiet = false) => {
    if (quiet) setRefreshing(true); else setLoading(true);
    const dateFrom = new Date(Date.now() - Number(days) * 86400000).toISOString();
    const dateTo = new Date().toISOString();
    const results = await Promise.allSettled([
      api.get<Row>('/analytics/organization', { period: 'daily', days: Number(days) }),
      callsApi.list({ page: 1, pageSize: 100, campaignId: campaignFilter === 'all' ? undefined : campaignFilter, dateFrom, dateTo }),
      callsApi.list({ page: 1, pageSize: 100, status: 'IN_PROGRESS', campaignId: campaignFilter === 'all' ? undefined : campaignFilter }),
      campaignsApi.list({ page: 1, pageSize: 100 }),
    ]);
    const [a, c, live, cp] = results;
    if (a.status === 'fulfilled') setAnalytics(a.value);
    if (c.status === 'fulfilled') setCalls(Array.isArray(c.value?.data) ? c.value.data : []);
    if (live.status === 'fulfilled') setActiveCalls(Array.isArray(live.value?.data) ? live.value.data : []);
    if (cp.status === 'fulfilled') setCampaigns(Array.isArray(cp.value?.data) ? cp.value.data : []);
    const failed = results.filter((r) => r.status === 'rejected').length;
    setError(failed === 4 ? 'The workspace API could not be reached. Check your connection and sign-in session.' : failed ? 'Some live data could not be loaded. Available API data is still shown.' : '');
    if (!failed) setUpdatedAt(new Date());
    setLoading(false); setRefreshing(false);
  }, [days, campaignFilter]);

  React.useEffect(() => {
    void load();
    const timer = window.setInterval(() => void load(true), 15000);
    return () => window.clearInterval(timer);
  }, [load]);

  const summary = analytics?.summary ?? {};
  const trend: Day[] = Array.isArray(analytics?.data) ? analytics.data : [];
  const recent = calls.filter((c) => statusFilter === 'all' || String(c.status || '').toUpperCase() === statusFilter).slice(0, 10);
  const kpis = [
    { label: 'Total customers', value: summary.total_customers, note: 'All workspace records', icon: Users, color: 'text-blue-600 bg-blue-500/10' },
    { label: 'Total calls', value: summary.total_calls, note: 'All-time calls', icon: Phone, color: 'text-indigo-600 bg-indigo-500/10' },
    { label: 'Completed calls', value: summary.completed_calls, note: `${n(summary.call_success_rate).toFixed(1)}% completion rate`, icon: CheckCircle2, color: 'text-emerald-600 bg-emerald-500/10' },
    { label: 'Failed calls', value: summary.failed_calls, note: 'Failed / unanswered outcomes', icon: XCircle, color: 'text-rose-600 bg-rose-500/10' },
    { label: 'Answered calls', value: summary.answered_calls, note: `${n(summary.answer_rate).toFixed(1)}% answer rate`, icon: Phone, color: 'text-cyan-600 bg-cyan-500/10' },
    { label: 'Interested leads', value: summary.interested_customers, note: `${n(summary.conversion_rate).toFixed(1)}% conversion rate`, icon: Target, color: 'text-amber-600 bg-amber-500/10' },
    { label: 'Hot leads', value: summary.hot_leads, note: 'Customers marked hot', icon: Flame, color: 'text-orange-600 bg-orange-500/10' },
    { label: 'Scheduled callbacks', value: summary.callbacks_scheduled, note: 'Awaiting follow-up', icon: Clock3, color: 'text-violet-600 bg-violet-500/10' },
  ];
  const total = trend.reduce((s, d) => s + n(d.total_calls), 0);
  const completed = trend.reduce((s, d) => s + n(d.completed_calls), 0);
  const failed = trend.reduce((s, d) => s + n(d.failed_calls), 0);
  const outcomes = [{ name: 'Completed', value: completed }, { name: 'Failed', value: failed }, { name: 'Other', value: Math.max(0, total - completed - failed) }].filter((x) => x.value > 0);
  const leads = [
    { name: 'Hot', leads: trend.reduce((s, d) => s + n(d.hot_leads), 0) },
    { name: 'Warm', leads: trend.reduce((s, d) => s + n(d.warm_leads), 0) },
    { name: 'Cold', leads: trend.reduce((s, d) => s + n(d.cold_leads), 0) },
  ];

  return <DashboardLayout><div className="mx-auto w-full max-w-[1600px] space-y-7">
    <header className="relative overflow-hidden rounded-[28px] border border-primary/15 bg-gradient-to-br from-primary/[0.10] via-base-100 to-secondary/[0.09] p-6 shadow-sm sm:p-7 xl:flex-row xl:items-end xl:justify-between">
      <div><div className="flex flex-wrap items-center gap-2"><h1 className="text-3xl font-bold tracking-[-.04em] sm:text-4xl">Workspace overview</h1><Badge variant={!loading && !error ? 'success' : 'outline'}>{loading ? 'Connecting' : error ? 'Data issue' : 'API connected'}</Badge></div><p className="mt-1 text-muted-foreground">Your calling operation at a glance. Every metric below comes from your workspace API.</p><p className="mt-1 text-xs text-muted-foreground">{updatedAt ? `Last updated ${updatedAt.toLocaleTimeString()}` : 'Waiting for API data'} · Auto-refresh every 15 seconds</p></div>
      <div className="flex flex-wrap items-center gap-2">
        <label className="flex h-10 items-center gap-2 rounded-md border bg-background px-3 text-sm"><CalendarDays className="h-4 w-4 text-muted-foreground" /><span className="sr-only">Reporting period</span><select aria-label="Reporting period" className="bg-transparent outline-none" value={days} onChange={(e) => setDays(e.target.value)}><option value="7">Last 7 days</option><option value="30">Last 30 days</option><option value="90">Last 90 days</option><option value="365">Last 12 months</option></select></label>
        <label className="flex h-10 items-center rounded-md border bg-background px-3 text-sm"><span className="sr-only">Call status</span><select aria-label="Call status filter" className="max-w-[145px] bg-transparent outline-none" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}><option value="all">All statuses</option><option value="COMPLETED">Completed</option><option value="FAILED">Failed</option><option value="NO_ANSWER">No answer</option><option value="BUSY">Busy</option><option value="IN_PROGRESS">In progress</option></select></label>
        <label className="flex h-10 items-center rounded-md border bg-background px-3 text-sm"><span className="sr-only">Campaign</span><select aria-label="Campaign filter" className="max-w-[170px] bg-transparent outline-none" value={campaignFilter} onChange={(e) => setCampaignFilter(e.target.value)}><option value="all">All campaigns</option>{campaigns.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label>
        <Button variant="outline" size="sm" onClick={() => void load(true)} disabled={refreshing}><RefreshCw className={cn('mr-2 h-4 w-4', refreshing && 'animate-spin')} />Refresh</Button>
        <Button size="sm" onClick={() => window.location.assign('/dashboard/campaigns')}><Plus className="mr-2 h-4 w-4" />New campaign</Button>
      </div>
    </header>
    {error && <div role="alert" className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"><AlertCircle className="h-4 w-4 shrink-0" />{error}</div>}

    <section aria-label="Workspace KPI metrics" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {kpis.map((item) => { const Icon = item.icon; return <Card key={item.label} className="rounded-2xl border-base-300/70 bg-base-100 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md"><CardContent className="flex items-start justify-between gap-3 p-5"><div className="min-w-0"><p className="text-sm text-muted-foreground">{item.label}</p><p className="mt-2 text-3xl font-bold tabular-nums">{loading && !analytics ? '—' : fmt(item.value)}</p><p className="mt-1 text-xs text-muted-foreground">{item.note}</p></div><div className={cn('rounded-xl p-3', item.color)}><Icon className="h-5 w-5" /></div></CardContent></Card>; })}
    </section>

    <section className="grid gap-4 xl:grid-cols-3">
      <Card className="rounded-2xl border-base-300/70 bg-base-100 shadow-sm xl:col-span-2"><CardHeader className="flex flex-row items-center justify-between space-y-0"><div><CardTitle>Calling activity</CardTitle><p className="mt-1 text-sm text-muted-foreground">Daily call volume and outcomes · selected period</p></div><Badge variant="outline">{fmt(total)} calls</Badge></CardHeader><CardContent className="h-[320px]">{trend.length ? <ResponsiveContainer width="100%" height="100%"><AreaChart data={trend} margin={{ top: 8, right: 12, left: -16, bottom: 0 }}><defs><linearGradient id="callsFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#6366f1" stopOpacity={0.28} /><stop offset="100%" stopColor="#6366f1" stopOpacity={0.02} /></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="date" tickFormatter={(v) => new Date(v).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })} minTickGap={24} /><YAxis allowDecimals={false} /><Tooltip labelFormatter={(v) => new Date(String(v)).toLocaleDateString('en-IN')} /><Legend /><Area type="monotone" dataKey="total_calls" name="Total calls" stroke="#6366f1" fill="url(#callsFill)" strokeWidth={2} /><Line type="monotone" dataKey="completed_calls" name="Completed" stroke="#16a34a" strokeWidth={2} dot={false} /><Line type="monotone" dataKey="failed_calls" name="Failed" stroke="#ef4444" strokeWidth={2} dot={false} /></AreaChart></ResponsiveContainer> : <div className="flex h-full items-center justify-center text-sm text-muted-foreground">{loading ? 'Loading database analytics…' : 'No call activity recorded for this period.'}</div>}</CardContent></Card>
      <Card className="rounded-2xl border-base-300/70 bg-base-100 shadow-sm"><CardHeader><CardTitle>Call outcome mix</CardTitle><p className="text-sm text-muted-foreground">Actual analytics records in this period</p></CardHeader><CardContent className="h-[320px]">{outcomes.length ? <ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={outcomes} dataKey="value" nameKey="name" innerRadius={68} outerRadius={104} paddingAngle={3}>{outcomes.map((x, i) => <Cell key={x.name} fill={['#16a34a', '#ef4444', '#64748b'][i]} />)}</Pie><Tooltip formatter={(v) => fmt(v)} /><Legend /></PieChart></ResponsiveContainer> : <div className="flex h-full items-center justify-center text-sm text-muted-foreground">{loading ? 'Loading outcomes…' : 'No call outcomes to display yet.'}</div>}</CardContent></Card>
    </section>

    <section className="grid gap-4 xl:grid-cols-3">
      <Card className="rounded-2xl border-base-300/70 bg-base-100 shadow-sm xl:col-span-2"><CardHeader><CardTitle>Lead quality</CardTitle><p className="text-sm text-muted-foreground">Hot, warm, and cold leads from call analytics</p></CardHeader><CardContent className="h-[280px]">{leads.some((x) => x.leads > 0) ? <ResponsiveContainer width="100%" height="100%"><BarChart data={leads} margin={{ top: 8, right: 12, left: -16, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip formatter={(v) => fmt(v)} /><Bar dataKey="leads" name="Leads" fill="#f59e0b" radius={[6, 6, 0, 0]} /></BarChart></ResponsiveContainer> : <div className="flex h-full items-center justify-center text-sm text-muted-foreground">{loading ? 'Loading lead analytics…' : 'No lead outcomes recorded in this period.'}</div>}</CardContent></Card>
      <Card className="rounded-2xl border-base-300/70 bg-base-100 shadow-sm"><CardHeader className="flex flex-row items-center justify-between space-y-0"><div><CardTitle>Live agent activity</CardTitle><p className="mt-1 text-sm text-muted-foreground">Calls currently marked in progress by the API</p></div><Radio className="h-5 w-5 text-emerald-600" /></CardHeader><CardContent><div className="flex items-end gap-2"><span className="text-4xl font-bold tabular-nums">{loading && !updatedAt ? '—' : activeCalls.length}</span><span className="pb-1 text-sm text-muted-foreground">active calls</span></div><div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground"><span className={cn('h-2 w-2 rounded-full', error ? 'bg-amber-500' : 'animate-pulse bg-emerald-500')} />{error ? 'Live status may be delayed' : 'Live status from calls API'}</div><div className="mt-5 space-y-3">{activeCalls.slice(0, 4).map((c) => <div key={c.id} className="flex items-center justify-between gap-3 border-t pt-3 text-sm"><div className="min-w-0"><p className="truncate font-medium">{customerName(c)}</p><p className="truncate text-xs text-muted-foreground">{c.to_number || c.phone || 'Number unavailable'}</p></div><Badge variant="outline">In progress</Badge></div>)}{!loading && activeCalls.length === 0 && <p className="border-t pt-3 text-sm text-muted-foreground">No calls are currently marked in progress.</p>}</div></CardContent></Card>
    </section>

    <Card className="rounded-2xl border-base-300/70 bg-base-100 shadow-sm"><CardHeader className="flex flex-row items-center justify-between"><div><CardTitle>Campaign performance</CardTitle><p className="mt-1 text-sm text-muted-foreground">Campaign records returned by your workspace API</p></div><Button variant="outline" size="sm" onClick={() => window.location.assign('/dashboard/campaigns')}>View campaigns</Button></CardHeader><CardContent className="p-0">{campaigns.length ? <div className="overflow-x-auto"><Table><TableHeader><TableRow><TableHead>Campaign</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Customers</TableHead><TableHead className="text-right">Completed</TableHead><TableHead className="text-right">Interested</TableHead><TableHead className="text-right">Completion</TableHead></TableRow></TableHeader><TableBody>{campaigns.slice(0, 8).map((c) => { const customers = n(c.total_customers ?? c.customer_count); const done = n(c.completed_calls ?? c.completed); const status = String(c.status || 'UNKNOWN').toUpperCase(); return <TableRow key={c.id}><TableCell className="font-medium">{c.name || 'Untitled campaign'}</TableCell><TableCell><Badge variant={status === 'RUNNING' ? 'success' : status === 'PAUSED' ? 'warning' : status === 'COMPLETED' ? 'default' : 'outline'}>{status}</Badge></TableCell><TableCell className="text-right tabular-nums">{fmt(customers)}</TableCell><TableCell className="text-right tabular-nums">{fmt(done)}</TableCell><TableCell className="text-right tabular-nums">{fmt(c.interested_count ?? c.interested)}</TableCell><TableCell className="text-right tabular-nums">{customers ? `${(done / customers * 100).toFixed(1)}%` : '0.0%'}</TableCell></TableRow>; })}</TableBody></Table></div> : <div className="px-6 py-12 text-center text-sm text-muted-foreground">{loading ? 'Loading campaigns…' : 'No campaigns have been created in this workspace yet.'}</div>}</CardContent></Card>

    <Card className="rounded-2xl border-base-300/70 bg-base-100 shadow-sm"><CardHeader className="flex flex-row items-center justify-between"><div><CardTitle>Recent calls</CardTitle><p className="mt-1 text-sm text-muted-foreground">Latest call records from the selected period</p></div><Badge variant="outline">{recent.length} shown</Badge></CardHeader><CardContent className="p-0">{recent.length ? <div className="overflow-x-auto"><Table><TableHeader><TableRow><TableHead>Customer</TableHead><TableHead>Phone</TableHead><TableHead>Campaign</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Duration</TableHead><TableHead>Interest</TableHead><TableHead>Time</TableHead></TableRow></TableHeader><TableBody>{recent.map((c) => { const status = String(c.status || 'UNKNOWN').toUpperCase(); return <TableRow key={c.id}><TableCell className="font-medium">{customerName(c)}</TableCell><TableCell>{c.to_number || c.customer?.phone || '—'}</TableCell><TableCell>{c.campaign?.name || c.campaign_name || '—'}</TableCell><TableCell><Badge variant={getStatusColor(status).includes('green') ? 'success' : getStatusColor(status).includes('red') ? 'destructive' : 'outline'}>{status.replaceAll('_', ' ')}</Badge></TableCell><TableCell className="text-right font-mono">{n(c.duration) > 0 ? formatDuration(n(c.duration)) : '—'}</TableCell><TableCell>{String(c.interest_level || '—').toUpperCase()}</TableCell><TableCell>{c.created_at ? formatRelativeTime(c.created_at) : '—'}</TableCell></TableRow>; })}</TableBody></Table></div> : <div className="px-6 py-12 text-center text-sm text-muted-foreground">{loading ? 'Loading calls…' : 'No calls match the selected filters.'}</div>}</CardContent></Card>
    <p className="flex items-center gap-2 text-xs text-muted-foreground"><Activity className="h-3.5 w-3.5" />Metrics and charts use workspace API responses. This page does not generate sample or mock records.</p>
  </div></DashboardLayout>;
}
