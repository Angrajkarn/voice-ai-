'use client';

import * as React from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { cn, formatPhoneNumber, getStatusColor } from '@/lib/utils';
import {
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  Phone,
  Mail,
  User,
  Building2,
  MapPin,
  MoreHorizontal,
  Edit,
  Trash2,
  Eye,
} from 'lucide-react';

const mockCustomers = [
  { id: '1', firstName: 'Rahul', lastName: 'Sharma', email: 'rahul.sharma@example.com', phone: '+919876543210', company: 'TechCorp Solutions', location: 'Bangalore', status: 'HOT_LEAD', interestLevel: 'HOT', language: 'en-IN', callAttempts: 2, lastCallAt: '2025-01-10T10:30:00Z', nextCallbackAt: null },
  { id: '2', firstName: 'Priya', lastName: 'Patel', email: 'priya.patel@example.com', phone: '+919876543211', company: 'InnovateLabs', location: 'Mumbai', status: 'WARM_LEAD', interestLevel: 'WARM', language: 'hinglish', callAttempts: 1, lastCallAt: '2025-01-09T14:15:00Z', nextCallbackAt: '2025-01-15T11:00:00Z' },
  { id: '3', firstName: 'Amit', lastName: 'Kumar', email: 'amit.kumar@example.com', phone: '+919876543212', company: 'DataDriven Inc', location: 'Delhi', status: 'COLD_LEAD', interestLevel: 'COLD', language: 'hi-IN', callAttempts: 3, lastCallAt: '2025-01-08T09:45:00Z', nextCallbackAt: null },
  { id: '4', firstName: 'Sneha', lastName: 'Reddy', email: 'sneha.reddy@example.com', phone: '+919876543213', company: 'CloudScale', location: 'Hyderabad', status: 'HOT_LEAD', interestLevel: 'HOT', language: 'en-IN', callAttempts: 1, lastCallAt: '2025-01-10T16:20:00Z', nextCallbackAt: null },
  { id: '5', firstName: 'Vikram', lastName: 'Singh', email: 'vikram.singh@example.com', phone: '+919876543214', company: 'GrowthHub', location: 'Pune', status: 'NEW', interestLevel: 'UNKNOWN', language: 'hinglish', callAttempts: 0, lastCallAt: null, nextCallbackAt: null },
  { id: '6', firstName: 'Anjali', lastName: 'Gupta', email: 'anjali.gupta@example.com', phone: '+919876543215', company: 'FinTech Pro', location: 'Chennai', status: 'NOT_INTERESTED', interestLevel: 'COLD', language: 'en-IN', callAttempts: 2, lastCallAt: '2025-01-07T11:30:00Z', nextCallbackAt: null },
  { id: '7', firstName: 'Rohit', lastName: 'Verma', email: 'rohit.verma@example.com', phone: '+919876543216', company: 'EduTech Solutions', location: 'Kolkata', status: 'CALLBACK_REQUESTED', interestLevel: 'WARM', language: 'en-IN', callAttempts: 1, lastCallAt: '2025-01-09T15:45:00Z', nextCallbackAt: '2025-01-14T10:00:00Z' },
  { id: '8', firstName: 'Kavya', lastName: 'Nair', email: 'kavya.nair@example.com', phone: '+919876543217', company: 'HealthFirst', location: 'Kochi', status: 'DO_NOT_CALL', interestLevel: 'UNKNOWN', language: 'en-IN', callAttempts: 0, lastCallAt: null, nextCallbackAt: null },
];

export default function CustomersPage() {
  const [search, setSearch] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState('all');
  const [page, setPage] = React.useState(1);
  const [pageSize, setPageSize] = React.useState(10);
  const [selectedCustomers, setSelectedCustomers] = React.useState<string[]>([]);
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [editingCustomer, setEditingCustomer] = React.useState<any>(null);

  const filteredCustomers = mockCustomers.filter(c => {
    const matchesSearch = c.firstName.toLowerCase().includes(search.toLowerCase()) ||
      c.lastName.toLowerCase().includes(search.toLowerCase()) ||
      c.phone.includes(search) ||
      c.email?.toLowerCase().includes(search.toLowerCase()) ||
      c.company?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'all' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const paginatedCustomers = filteredCustomers.slice((page - 1) * pageSize, page * pageSize);
  const totalPages = Math.ceil(filteredCustomers.length / pageSize);

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedCustomers(paginatedCustomers.map(c => c.id));
    } else {
      setSelectedCustomers([]);
    }
  };

  const handleSelect = (id: string, checked: boolean) => {
    setSelectedCustomers(prev => checked ? [...prev, id] : prev.filter(i => i !== id));
  };

  const openEditDialog = (customer: any) => {
    setEditingCustomer(customer);
    setDialogOpen(true);
  };

  const closeDialog = () => {
    setDialogOpen(false);
    setEditingCustomer(null);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Customers</h1>
            <p className="text-muted-foreground">Manage your customer database</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
            <Button variant="outline" size="sm">
              <Upload className="mr-2 h-4 w-4" />
              Import CSV
            </Button>
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Customer
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                  <DialogTitle>{editingCustomer ? 'Edit Customer' : 'Add New Customer'}</DialogTitle>
                </DialogHeader>
                <form className="space-y-4">
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="space-y-1.5">
                      <Label htmlFor="firstName">First Name *</Label>
                      <Input id="firstName" defaultValue={editingCustomer?.firstName} required />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="lastName">Last Name *</Label>
                      <Input id="lastName" defaultValue={editingCustomer?.lastName} required />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="email">Email</Label>
                      <Input id="email" type="email" defaultValue={editingCustomer?.email} />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="phone">Phone *</Label>
                      <Input id="phone" defaultValue={editingCustomer?.phone} required placeholder="+919876543210" />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="company">Company</Label>
                      <Input id="company" defaultValue={editingCustomer?.company} />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="location">Location</Label>
                      <Input id="location" defaultValue={editingCustomer?.location} />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="language">Language</Label>
                      <Select defaultValue={editingCustomer?.language || 'en-IN'}>
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
                      <Label htmlFor="status">Status</Label>
                      <Select defaultValue={editingCustomer?.status || 'NEW'}>
                        <SelectTrigger id="status">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="NEW">New</SelectItem>
                          <SelectItem value="HOT_LEAD">Hot Lead</SelectItem>
                          <SelectItem value="WARM_LEAD">Warm Lead</SelectItem>
                          <SelectItem value="COLD_LEAD">Cold Lead</SelectItem>
                          <SelectItem value="NOT_INTERESTED">Not Interested</SelectItem>
                          <SelectItem value="CALLBACK_REQUESTED">Callback Requested</SelectItem>
                          <SelectItem value="DO_NOT_CALL">Do Not Call</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 pt-4">
                    <Button type="button" variant="outline" onClick={closeDialog}>Cancel</Button>
                    <Button type="submit">{editingCustomer ? 'Update' : 'Create'}</Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Search & Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search customers..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="NEW">New</SelectItem>
                  <SelectItem value="HOT_LEAD">Hot Lead</SelectItem>
                  <SelectItem value="WARM_LEAD">Warm Lead</SelectItem>
                  <SelectItem value="COLD_LEAD">Cold Lead</SelectItem>
                  <SelectItem value="NOT_INTERESTED">Not Interested</SelectItem>
                  <SelectItem value="CALLBACK_REQUESTED">Callback Requested</SelectItem>
                  <SelectItem value="DO_NOT_CALL">Do Not Call</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm">
                <Filter className="mr-2 h-4 w-4" />
                Filters
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Customers Table */}
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <input
                        type="checkbox"
                        checked={selectedCustomers.length === paginatedCustomers.length && paginatedCustomers.length > 0}
                        onChange={event => handleSelectAll(event.target.checked)}
                        className="rounded border-input"
                      />
                    </TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Company</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Interest</TableHead>
                    <TableHead className="text-right">Attempts</TableHead>
                    <TableHead>Last Call</TableHead>
                    <TableHead className="w-12"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paginatedCustomers.map(customer => (
                    <TableRow key={customer.id}>
                      <TableCell>
                        <input
                          type="checkbox"
                          checked={selectedCustomers.includes(customer.id)}
                          onChange={e => handleSelect(customer.id, e.target.checked)}
                          className="rounded border-input"
                        />
                      </TableCell>
                      <TableCell className="font-medium">{customer.firstName} {customer.lastName}</TableCell>
                      <TableCell>
                        <div className="flex flex-col gap-1">
                          <span className="flex items-center gap-1 text-sm">
                            <Phone className="h-3 w-3" />
                            {formatPhoneNumber(customer.phone)}
                          </span>
                          {customer.email && (
                            <span className="flex items-center gap-1 text-sm text-muted-foreground">
                              <Mail className="h-3 w-3" />
                              {customer.email}
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{customer.company}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {customer.location}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusColor(customer.status).includes('red') ? 'destructive' : getStatusColor(customer.status).includes('green') ? 'success' : getStatusColor(customer.status).includes('yellow') ? 'warning' : getStatusColor(customer.status).includes('purple') ? 'default' : 'outline'}>
                          {customer.status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={customer.interestLevel === 'HOT' ? 'destructive' : customer.interestLevel === 'WARM' ? 'warning' : customer.interestLevel === 'COLD' ? 'info' : 'outline'}>
                          {customer.interestLevel}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right font-mono">{customer.callAttempts}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {customer.lastCallAt ? new Date(customer.lastCallAt).toLocaleDateString() : '-'}
                      </TableCell>
                      <TableCell>
                        <Button variant="ghost" size="icon" onClick={() => openEditDialog(customer)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between p-4 border-t">
              <p className="text-sm text-muted-foreground">
                Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, filteredCustomers.length)} of {filteredCustomers.length} customers
              </p>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
                <span className="px-3 text-sm">{page} / {totalPages}</span>
                <Button variant="outline" size="sm" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}