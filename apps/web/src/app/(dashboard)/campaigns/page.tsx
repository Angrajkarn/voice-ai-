'use client';

import * as React from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { cn, getStatusColor } from '@/lib/utils';
import {
  Plus,
  Search,
  Play,
  Pause,
  Square,
  RotateCcw,
  Trash2,
  Edit,
  Eye,
  BarChart2,
  Settings,
  Zap,
  Clock,
  Users,
  CheckCircle,
  XCircle,
} from 'lucide-react';

const mockCampaigns = [
  { id: '1', name: 'Product Launch Campaign', description: 'Calling customers about our new AI product launch', status: 'RUNNING', purpose: 'Introduce new AI-powered product features', customers: 450, completed: 320, interested: 89, callbacks: 23, successRate: 71.1, createdAt: '2025-01-01' },
  { id: '2', name: 'Q4 Promotions', description: 'Year-end promotional offers', status: 'PAUSED', purpose: 'Promote Q4 discounts and offers', customers: 320, completed: 180, interested: 45, callbacks: 12, successRate: 56.3, createdAt: '2024-11-15' },
  { id: '3', name: 'Renewal Reminders', description: 'Annual subscription renewal calls', status: 'COMPLETED', purpose: 'Remind customers about subscription renewals', customers: 200, completed: 195, interested: 67, callbacks: 8, successRate: 97.5, createdAt: '2024-10-01' },
  { id: '4', name: 'New Feature Announcement', description: 'Announcing new dashboard features', status: 'DRAFT', purpose: 'Inform customers about new features', customers: 150, completed: 0, interested: 0, callbacks: 0, successRate: 0, createdAt: '2025-01-10' },
  { id: '5', name: 'Customer Satisfaction Survey', description: 'Post-call satisfaction surveys', status: 'STOPPED', purpose: 'Gather customer feedback', customers: 100, completed: 45, interested: 12, callbacks: 3, successRate: 45.0, createdAt: '2024-12-01' },
];

const statusActions: Record<string, { icon: React.ReactNode; label: string; variant: 'default' | 'outline' | 'ghost' }[]> = {
  DRAFT: [{ icon: <Play className="h-4 w-4" />, label: 'Start', variant: 'default' }, { icon: <Edit className="h-4 w-4" />, label: 'Edit', variant: 'outline' }, { icon: <Trash2 className="h-4 w-4" />, label: 'Delete', variant: 'ghost' }],
  READY: [{ icon: <Play className="h-4 w-4" />, label: 'Start', variant: 'default' }, { icon: <Pause className="h-4 w-4" />, label: 'Pause', variant: 'outline' }, { icon: <Edit className="h-4 w-4" />, label: 'Edit', variant: 'ghost' }],
  RUNNING: [{ icon: <Pause className="h-4 w-4" />, label: 'Pause', variant: 'default' }, { icon: <Square className="h-4 w-4" />, label: 'Stop', variant: 'outline' }, { icon: <BarChart2 className="h-4 w-4" />, label: 'Monitor', variant: 'ghost' }],
  PAUSED: [{ icon: <Play className="h-4 w-4" />, label: 'Resume', variant: 'default' }, { icon: <Square className="h-4 w-4" />, label: 'Stop', variant: 'outline' }, { icon: <Edit className="h-4 w-4" />, label: 'Edit', variant: 'ghost' }],
  COMPLETED: [{ icon: <RotateCcw className="h-4 w-4" />, label: 'Restart', variant: 'outline' }, { icon: <BarChart2 className="h-4 w-4" />, label: 'View Report', variant: 'ghost' }],
  STOPPED: [{ icon: <RotateCcw className="h-4 w-4" />, label: 'Restart', variant: 'default' }, { icon: <Edit className="h-4 w-4" />, label: 'Edit', variant: 'outline' }],
};

export default function CampaignsPage() {
  const [search, setSearch] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState('all');
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [editingCampaign, setEditingCampaign] = React.useState<any>(null);
  const [activeTab, setActiveTab] = React.useState<'list' | 'create'>('list');

  const filteredCampaigns = mockCampaigns.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.description?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'all' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'success' | 'warning' | 'destructive' | 'default' | 'outline'> = {
      RUNNING: 'success',
      PAUSED: 'warning',
      COMPLETED: 'default',
      STOPPED: 'destructive',
      DRAFT: 'outline',
      READY: 'success',
    };
    return (
      <Badge variant={variants[status] || 'outline'}>
        {status}
      </Badge>
    );
  };

  const handleAction = (action: string, campaign: any) => {
    console.log(action, campaign);
    // Implement actual actions
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Campaigns</h1>
            <p className="text-muted-foreground">Manage your AI voice calling campaigns</p>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Campaign
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create New Campaign</DialogTitle>
              </DialogHeader>
              <form className="space-y-6 p-4" onSubmit={e => { e.preventDefault(); setDialogOpen(false); }}>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-1.5 sm:col-span-2">
                    <Label htmlFor="name">Campaign Name *</Label>
                    <Input id="name" placeholder="e.g., Product Launch Q1 2025" required />
                  </div>
                  <div className="space-y-1.5 sm:col-span-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea id="description" placeholder="Brief description of this campaign" rows={2} />
                  </div>
                  <div className="space-y-1.5 sm:col-span-2">
                    <Label htmlFor="purpose">Purpose *</Label>
                    <Textarea id="purpose" placeholder="What is this campaign about? What are you trying to achieve?" rows={3} required />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="aiInstructions">AI Instructions *</Label>
                    <Textarea
                      id="aiInstructions"
                      placeholder="Detailed instructions for the AI agent on how to handle calls..."
                      rows={4}
                      required
                    />
                  </div>
                  <div className="space-y-1.5 sm:col-span-2">
                    <Label htmlFor="openingScript">Opening Script *</Label>
                    <Textarea
                      id="openingScript"
                      placeholder="Hello {firstName}, I'm an AI assistant calling on behalf of..."
                      rows={3}
                      required
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="knowledgeBase">Knowledge Base</Label>
                    <Textarea
                      id="knowledgeBase"
                      placeholder="Product info, pricing, FAQs, common objections and responses..."
                      rows={4}
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="voiceId">Voice</Label>
                    <Select defaultValue="alloy">
                      <SelectTrigger id="voiceId">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="alloy">Alloy</SelectItem>
                        <SelectItem value="echo">Echo</SelectItem>
                        <SelectItem value="fable">Fable</SelectItem>
                        <SelectItem value="onyx">Onyx</SelectItem>
                        <SelectItem value="nova">Nova</SelectItem>
                        <SelectItem value="shimmer">Shimmer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="language">Primary Language</Label>
                    <Select defaultValue="en-IN">
                      <SelectTrigger id="language">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en-IN">English (India)</SelectItem>
                        <SelectItem value="hi-IN">Hindi</SelectItem>
                        <SelectItem value="hinglish">Hinglish</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="maxCallsPerDay">Max Calls/Day</Label>
                    <Input id="maxCallsPerDay" type="number" defaultValue={100} min={1} max={10000} />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="delayBetweenCalls">Delay Between Calls (seconds)</Label>
                    <Input id="delayBetweenCalls" type="number" defaultValue={30} min={0} max={3600} />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="maxRetryAttempts">Max Retry Attempts</Label>
                    <Input id="maxRetryAttempts" type="number" defaultValue={3} min={0} max={10} />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="callingWindowStart">Calling Window Start</Label>
                    <Input id="callingWindowStart" type="time" defaultValue="09:00" />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="callingWindowEnd">Calling Window End</Label>
                    <Input id="callingWindowEnd" type="time" defaultValue="18:00" />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="callingTimezone">Timezone</Label>
                    <Input id="callingTimezone" defaultValue="Asia/Kolkata" />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="skipWeekends">Skip Weekends</Label>
                    <Select defaultValue="true">
                      <SelectTrigger id="skipWeekends">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="true">Yes</SelectItem>
                        <SelectItem value="false">No</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                  <Button type="submit">Create Campaign</Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Search & Filter */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search campaigns..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="DRAFT">Draft</SelectItem>
                  <SelectItem value="READY">Ready</SelectItem>
                  <SelectItem value="RUNNING">Running</SelectItem>
                  <SelectItem value="PAUSED">Paused</SelectItem>
                  <SelectItem value="COMPLETED">Completed</SelectItem>
                  <SelectItem value="STOPPED">Stopped</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Campaigns Table */}
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
                {filteredCampaigns.map(campaign => (
                  <TableRow key={campaign.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{campaign.name}</p>
                        <p className="text-sm text-muted-foreground">{campaign.purpose}</p>
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(campaign.status)}</TableCell>
                    <TableCell className="text-right">{campaign.customers}</TableCell>
                    <TableCell className="text-right text-green-600">{campaign.completed}</TableCell>
                    <TableCell className="text-right text-orange-600">{campaign.interested}</TableCell>
                    <TableCell className="text-right text-indigo-600">{campaign.callbacks}</TableCell>
                    <TableCell className="text-right font-medium">
                      {campaign.successRate > 0 ? campaign.successRate.toFixed(1) + '%' : '-'}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        {statusActions[campaign.status]?.map((action, i) => (
                          <Button
                            key={i}
                            variant={action.variant}
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => handleAction(action.label, campaign)}
                          >
                            {action.icon}
                          </Button>
                        ))}
                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => handleAction('Analytics', campaign)}>
                          <BarChart2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Summary Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Campaigns</p>
                  <p className="text-3xl font-bold">{mockCampaigns.length}</p>
                </div>
                <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                  <Zap className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Active (Running)</p>
                  <p className="text-3xl font-bold">{mockCampaigns.filter(c => c.status === 'RUNNING').length}</p>
                </div>
                <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl">
                  <Play className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Paused</p>
                  <p className="text-3xl font-bold">{mockCampaigns.filter(c => c.status === 'PAUSED').length}</p>
                </div>
                <div className="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-xl">
                  <Pause className="h-6 w-6 text-yellow-600" />
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Completed</p>
                  <p className="text-3xl font-bold">{mockCampaigns.filter(c => c.status === 'COMPLETED').length}</p>
                </div>
                <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl">
                  <CheckCircle className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}