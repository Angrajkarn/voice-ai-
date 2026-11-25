'use client';

import * as React from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import {
  Users,
  Phone,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  Target,
  RefreshCw,
  Plus,
  Download,
  Filter,
  Calendar,
} from 'lucide-react';
import { cn, formatDuration, formatRelativeTime, getStatusColor } from '@/lib/utils';
import { api, callsApi, campaignsApi } from '@/lib/api';

const mockMetrics = [
  { name: 'Total Customers', value: '1,234', change: '+12%', icon: Users, color: 'text-blue-600', bgColor: 'bg-blue-100 dark:bg-blue-900/30' },
  { name: 'Total Calls', value: '3,456', change: '+8%', icon: Phone, color: 'text-green-600', bgColor: 'bg-green-100 dark:bg-green-900/30' },
  { name: 'Completed', value: '2,890', change: '+15%', icon: CheckCircle, color: 'text-emerald-600', bgColor: 'bg-emerald-100 dark:bg-emerald-900/30' },
  { name: 'Failed', value: '234', change: '-5%', icon: XCircle, color: 'text-red-600', bgColor: 'bg-red-100 dark:bg-red-900/30' },
  { name: 'Answered', value: '3,120', change: '+10%', icon: Phone, color: 'text-purple-600', bgColor: 'bg-purple-100 dark:bg-purple-900/30' },
  { name: 'Interested', value: '445', change: '+22%', icon: Target, color: 'text-orange-600', bgColor: 'bg-orange-100 dark:bg-orange-900/30' },
  { name: 'Hot Leads', value: '128', change: '+18%', icon: TrendingUp, color: 'text-red-600', bgColor: 'bg-red-100 dark:bg-red-900/30' },
  { name: 'Callbacks', value: '67', change: '+3%', icon: Clock, color: 'text-indigo-600', bgColor: 'bg-indigo-100 dark:bg-indigo-900/30' },
];

export default function DashboardPage() {
  const [activeTab, setActiveTab] = React.useState<'overview' | 'campaigns' | 'recent'>('overview');
  const [metrics, setMetrics] = React.useState(mockMetrics.map((item) => ({ ...item, value: '—', change: 'Live' })));
  const [recentCalls, setRecentCalls] = React.useState<any[]>([]);
  const [campaigns, setCampaigns] = React.useState<any[]>([]);
  const [dataLoading, setDataLoading] = React.useState(true);
  const [dataError, setDataError] = React.useState('');

  React.useEffect(() => {
    let mounted = true;
    const loadDashboard = async () => {
      const [analyticsResult, callsResult, campaignsResult] = await Promise.allSettled([
        api.get<any>('/analytics/dashboard'),
        callsApi.list({ page: 1, pageSize: 50 }),
        campaignsApi.list({ page: 1, pageSize: 50 }),
      ]);
      if (!mounted) return;
      const analyticsPayload: any = analyticsResult.status === 'fulfilled' ? analyticsResult.value : {};
      const callsPayload: any = callsResult.status === 'fulfilled' ? callsResult.value : {};
      const campaignPayload: any = campaignsResult.status === 'fulfilled' ? campaignsResult.value : {};
      const callRows = Array.isArray(callsPayload?.data) ? callsPayload.data : [];
      const campaignRows = Array.isArray(campaignPayload?.data) ? campaignPayload.data : [];
      const totalCustomers = Number(analyticsPayload?.total_customers || 0);
      const totalCalls = Number(analyticsPayload?.total_calls || 0);
      const completed = Number(analyticsPayload?.completed_calls || 0);
      const failed = Number(analyticsPayload?.failed_calls || 0);
      const answered = Number(analyticsPayload?.answered_calls || 0);
      const interested = Number(analyticsPayload?.interested_customers || 0);
      const hot = Number(analyticsPayload?.hot_leads || 0);
      const callbackCount = Number(analyticsPayload?.callbacks_scheduled || 0);
      const values = [totalCustomers, totalCalls, completed, failed, answered, interested, hot, callbackCount];
      setMetrics(mockMetrics.map((item, index) => ({ ...item, value: values[index].toLocaleString('en-IN'), change: 'Live' })));
      setRecentCalls(callRows.slice(0, 8).map((call: any) => ({
        customer: call.customer?.name || call.customer_name || call.customerName || 'Unknown customer',
        phone: call.to_number || call.phone || call.customer?.phone || '—',
        campaign: call.campaign?.name || call.campaign_name || '—',
        status: String(call.status || 'UNKNOWN').toUpperCase(),
        duration: Number(call.duration_seconds || call.duration || 0),
        interest: String(call.interest_level || call.interest || 'UNKNOWN').toUpperCase(),
        time: call.created_at ? formatRelativeTime(call.created_at) : '—',
      })));
      setCampaigns(campaignRows.slice(0, 5).map((campaign: any) => ({
        name: campaign.name || 'Untitled campaign',
        status: String(campaign.status || 'DRAFT').toUpperCase(),
        customers: Number(campaign.total_customers ?? campaign.customer_count ?? 0),
        completed: Number(campaign.completed_calls ?? campaign.completed ?? 0),
        interested: Number(campaign.interested_count ?? campaign.interested ?? 0),
        callbacks: Number(campaign.callback_count ?? campaign.callbacks ?? 0),
      })));
      const failures = [analyticsResult, callsResult, campaignsResult].filter(result => result.status === 'rejected').length;
      setDataError(failures === 3 ? 'The API could not load dashboard data. Check your backend connection and sign-in.' : failures ? 'Some dashboard data could not be loaded; available sections are shown.' : '');
      setDataLoading(false);
    };
    void loadDashboard();
    const timer = window.setInterval(loadDashboard, 30000);
    return () => { mounted = false; window.clearInterval(timer); };
  }, []);

  return (
    <DashboardLayout>
      <div className="mx-auto w-full max-w-[1600px] space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">Overview of your AI voice calling campaigns</p>
            <p className="mt-1 text-xs text-muted-foreground">{dataLoading ? "Connecting to workspace…" : "Refreshes automatically every 30 seconds"}{dataError ? ` · ${dataError}` : ""}</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Calendar className="mr-2 h-4 w-4" />
              Last 30 days
            </Button>
            <Button variant="outline" size="sm">
              <Filter className="mr-2 h-4 w-4" />
              Filters
            </Button>
            <Button size="sm" onClick={() => window.location.assign('/campaigns')}>
              <Plus className="mr-2 h-4 w-4" />
              New Campaign
            </Button>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => (
            <Card key={metric.name} className="relative overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{metric.name}</p>
                    <p className="text-3xl font-bold mt-1">{metric.value}</p>
                    <div className="flex items-center gap-1 mt-2">
                      <span className={cn('text-sm font-medium', metric.change === 'Live' || metric.change.startsWith('+') ? 'text-green-600' : 'text-red-600')}>
                        {metric.change}
                      </span>
                      <span className="text-sm text-muted-foreground">vs last period</span>
                    </div>
                  </div>
                  <div className={cn('p-3 rounded-xl', metric.bgColor)}>
                    <metric.icon className={cn('h-6 w-6', metric.color)} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Tabs for different views */}
        <div className="space-y-4">
          <div className="flex gap-2 border-b">
            <button
              onClick={() => setActiveTab('overview')}
              className={cn(
                'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'overview'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('campaigns')}
              className={cn(
                'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'campaigns'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              Campaigns
            </button>
            <button
              onClick={() => setActiveTab('recent')}
              className={cn(
                'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'recent'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              Recent Calls
            </button>
          </div>

          {activeTab === 'overview' && (
            <div className="grid gap-4 lg:grid-cols-2">
              {/* Campaign Performance */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Campaign Performance</CardTitle>
                  <Badge variant="success">Live</Badge>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {campaigns.map((campaign) => (
                      <div key={campaign.name} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{campaign.name}</span>
                          <Badge variant={campaign.status === 'RUNNING' ? 'success' : campaign.status === 'PAUSED' ? 'warning' : campaign.status === 'COMPLETED' ? 'default' : 'outline'}>
                            {campaign.status}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-muted-foreground">Customers</p>
                            <p className="font-medium">{campaign.customers}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Completed</p>
                            <p className="font-medium text-green-600">{campaign.completed}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Interested</p>
                            <p className="font-medium text-orange-600">{campaign.interested}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Callbacks</p>
                            <p className="font-medium text-indigo-600">{campaign.callbacks}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Call Status Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Call Status Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { label: 'Completed', value: 2890, color: 'bg-green-500', percentage: 83.6 },
                      { label: 'No Answer', value: 345, color: 'bg-gray-500', percentage: 10.0 },
                      { label: 'Busy', value: 123, color: 'bg-orange-500', percentage: 3.6 },
                      { label: 'Voicemail', value: 56, color: 'bg-purple-500', percentage: 1.6 },
                      { label: 'Failed', value: 42, color: 'bg-red-500', percentage: 1.2 },
                    ].map((item) => (
                      <div key={item.label} className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span>{item.label}</span>
                          <span className="font-medium">{item.value} ({item.percentage}%)</span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className={cn('h-full rounded-full transition-all duration-500', item.color)}
                            style={{ width: `${item.percentage}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'campaigns' && (
            <Card>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Campaign</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Customers</TableHead>
                      <TableHead className="text-right">Completed</TableHead>
                      <TableHead className="text-right">Interested</TableHead>
                      <TableHead className="text-right">Callbacks</TableHead>
                      <TableHead className="text-right">Success Rate</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {campaigns.map((campaign) => (
                      <TableRow key={campaign.name}>
                        <TableCell className="font-medium">{campaign.name}</TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              campaign.status === 'RUNNING' ? 'success' :
                              campaign.status === 'PAUSED' ? 'warning' :
                              campaign.status === 'COMPLETED' ? 'default' : 'outline'
                            }
                          >
                            {campaign.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">{campaign.customers}</TableCell>
                        <TableCell className="text-right text-green-600">{campaign.completed}</TableCell>
                        <TableCell className="text-right text-orange-600">{campaign.interested}</TableCell>
                        <TableCell className="text-right text-indigo-600">{campaign.callbacks}</TableCell>
                        <TableCell className="text-right font-medium">
                          {campaign.customers > 0 ? ((campaign.completed / campaign.customers) * 100).toFixed(1) : 0}%
                        </TableCell>
                        <TableCell>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <RefreshCw className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}

          {activeTab === 'recent' && (
            <Card>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Customer</TableHead>
                      <TableHead>Phone</TableHead>
                      <TableHead>Campaign</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Duration</TableHead>
                      <TableHead>Interest</TableHead>
                      <TableHead>Time</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {recentCalls.map((call) => (
                      <TableRow key={`${call.customer}-${call.time}`}>
                        <TableCell className="font-medium">{call.customer}</TableCell>
                        <TableCell>{call.phone}</TableCell>
                        <TableCell>{call.campaign}</TableCell>
                        <TableCell>
                          <Badge variant={getStatusColor(call.status).includes('green') ? 'success' : getStatusColor(call.status).includes('red') ? 'destructive' : getStatusColor(call.status).includes('yellow') ? 'warning' : getStatusColor(call.status).includes('purple') ? 'default' : 'outline'}>
                            {call.status.replace('_', ' ')}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          {call.duration > 0 ? formatDuration(call.duration) : '-'}
                        </TableCell>
                        <TableCell>
                          <Badge variant={call.interest === 'HOT' ? 'destructive' : call.interest === 'WARM' ? 'warning' : call.interest === 'COLD' ? 'info' : 'outline'}>
                            {call.interest}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-muted-foreground">{call.time}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}