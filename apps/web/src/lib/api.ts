// API client for the web app

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { getSession, signOut } from 'next-auth/react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });

    // Request interceptor for auth
    this.client.interceptors.request.use(
      async (config: InternalAxiosRequestConfig) => {
        // In a real app, you'd get the token from next-auth session
        // const session = await getSession();
        // if (session?.accessToken) {
        //   config.headers.Authorization = `Bearer ${session.accessToken}`;
        // }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          if (typeof window !== 'undefined') {
            await signOut({ callbackUrl: '/login' });
          }
        }
        return Promise.reject(this.formatError(error));
      }
    );
  }

  private formatError(error: AxiosError): Error {
    if (error.response?.data) {
      const data = error.response.data as { message?: string; error?: string };
      return new Error(data.message || data.error || error.message);
    }
    return error;
  }

  // Generic request methods
  async get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
    const response = await this.client.get<T>(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.put<T>(url, data);
    return response.data;
  }

  async patch<T>(url: string, data?: unknown): Promise<T> {
    const response = await this.client.patch<T>(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url);
    return response.data;
  }

  // File upload
  async upload<T>(url: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<T>(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          onProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total));
        }
      },
    });
    return response.data;
  }
}

export const api = new ApiClient();

// ============================================
// TYPED API ENDPOINTS
// ============================================

// Organizations
export const organizationsApi = {
  getCurrent: () => api.get<{ id: string; name: string; slug: string; plan: string }>('/organizations/current'),
  update: (data: Partial<{ name: string; logoUrl: string; settings: Record<string, unknown> }>) =>
    api.patch('/organizations/current', data),
  getUsers: (params?: { page?: number; pageSize?: number }) =>
    api.get<{ data: any[]; total: number; page: number; pageSize: number; totalPages: number }>('/organizations/current/users', params),
  inviteUser: (email: string, role: string) => api.post('/organizations/current/users/invite', { email, role }),
  updateUserRole: (userId: string, role: string) => api.patch(`/organizations/current/users/${userId}`, { role }),
  removeUser: (userId: string) => api.delete(`/organizations/current/users/${userId}`),
};

// Campaigns
export const campaignsApi = {
  list: (params?: { page?: number; pageSize?: number; status?: string; search?: string }) =>
    api.get<{ data: any[]; total: number; page: number; pageSize: number; totalPages: number }>('/campaigns', params),
  get: (id: string) => api.get(`/campaigns/${id}`),
  create: (data: any) => api.post('/campaigns', data),
  update: (id: string, data: any) => api.patch(`/campaigns/${id}`, data),
  delete: (id: string) => api.delete(`/campaigns/${id}`),
  start: (id: string) => api.post(`/campaigns/${id}/start`),
  pause: (id: string) => api.post(`/campaigns/${id}/pause`),
  stop: (id: string) => api.post(`/campaigns/${id}/stop`),
  validate: (id: string) => api.post(`/campaigns/${id}/validate`),
  getMetrics: (id: string) => api.get(`/campaigns/${id}/metrics`),
  getAnalytics: (id: string, params?: { period?: string; days?: number }) =>
    api.get(`/campaigns/${id}/analytics`, params),
  bulkAction: (data: { campaignIds: string[]; action: string }) => api.post('/campaigns/bulk', data),
};

// Customers
export const customersApi = {
  list: (params?: {
    page?: number;
    pageSize?: number;
    campaignId?: string;
    status?: string;
    interestLevel?: string;
    search?: string;
    sortBy?: string;
    sortOrder?: string;
  }) => api.get<{ data: any[]; total: number; page: number; pageSize: number; totalPages: number }>('/customers', params),
  get: (id: string) => api.get(`/customers/${id}`),
  create: (data: any) => api.post('/customers', data),
  update: (id: string, data: any) => api.patch(`/customers/${id}`, data),
  delete: (id: string) => api.delete(`/customers/${id}`),
  import: (file: File, options?: { skipDuplicates?: boolean; updateExisting?: boolean; campaignId?: string }) =>
    api.upload('/customers/import', file),
  export: (params?: { campaignId?: string; format?: 'csv' | 'xlsx' }) =>
    api.get('/customers/export', { ...params, responseType: 'blob' }),
  bulkAction: (data: { customerIds: string[]; action: string; campaignId?: string; callbackDate?: string }) =>
    api.post('/customers/bulk', data),
  getByCampaign: (campaignId: string, params?: { page?: number; pageSize?: number; status?: string }) =>
    api.get<{ data: any[]; total: number }>(`/campaigns/${campaignId}/customers`, params),
  addToCampaign: (campaignId: string, customerIds: string[]) =>
    api.post(`/campaigns/${campaignId}/customers`, { customerIds }),
  removeFromCampaign: (campaignId: string, customerIds: string[]) =>
    api.delete(`/campaigns/${campaignId}/customers`, { data: { customerIds } }),
};

// Calls
export const callsApi = {
  list: (params?: {
    page?: number;
    pageSize?: number;
    campaignId?: string;
    customerId?: string;
    status?: string;
    dateFrom?: string;
    dateTo?: string;
  }) => api.get<{ data: any[]; total: number; page: number; pageSize: number; totalPages: number }>('/calls', params),
  get: (id: string) => api.get(`/calls/${id}`),
  getTranscript: (id: string) => api.get(`/calls/${id}/transcript`),
  getRecording: (id: string) => api.get(`/calls/${id}/recording`, { responseType: 'blob' }),
  getLiveCalls: (campaignId: string) => api.get(`/campaigns/${campaignId}/calls/live`),
  retry: (id: string) => api.post(`/calls/${id}/retry`),
  cancel: (id: string) => api.post(`/calls/${id}/cancel`),
};

// Callbacks
export const callbacksApi = {
  list: (params?: {
    page?: number;
    pageSize?: number;
    campaignId?: string;
    customerId?: string;
    status?: string;
    dateFrom?: string;
    dateTo?: string;
  }) => api.get<{ data: any[]; total: number; page: number; pageSize: number; totalPages: number }>('/callbacks', params),
  get: (id: string) => api.get(`/callbacks/${id}`),
  create: (data: any) => api.post('/callbacks', data),
  update: (id: string, data: any) => api.patch(`/callbacks/${id}`, data),
  delete: (id: string) => api.delete(`/callbacks/${id}`),
  complete: (id: string, outcome: string) => api.post(`/callbacks/${id}/complete`, { outcome }),
  getDue: (campaignId: string) => api.get(`/campaigns/${campaignId}/callbacks/due`),
};

// Analytics
export const analyticsApi = {
  getDashboard: (organizationId: string) => api.get(`/analytics/dashboard?organizationId=${organizationId}`),
  getCampaignAnalytics: (campaignId: string, params?: { period?: string; days?: number }) =>
    api.get(`/analytics/campaigns/${campaignId}`, params),
  getOrganizationAnalytics: (organizationId: string, params?: { period?: string; days?: number }) =>
    api.get(`/analytics/organizations/${organizationId}`, params),
  exportReport: (type: string, params?: Record<string, unknown>) =>
    api.get(`/analytics/export/${type}`, { ...params, responseType: 'blob' }),
};

// Integrations
export const integrationsApi = {
  list: (organizationId: string) => api.get(`/integrations?organizationId=${organizationId}`),
  get: (id: string) => api.get(`/integrations/${id}`),
  create: (data: any) => api.post('/integrations', data),
  update: (id: string, data: any) => api.patch(`/integrations/${id}`, data),
  delete: (id: string) => api.delete(`/integrations/${id}`),
  test: (id: string) => api.post(`/integrations/${id}/test`),
  sync: (id: string) => api.post(`/integrations/${id}/sync`),
  getGoogleAuthUrl: (type: 'sheets' | 'drive', campaignId?: string) =>
    api.get(`/integrations/google/auth-url`, { params: { type, campaignId } }),
  handleGoogleCallback: (code: string, state: string) =>
    api.post('/integrations/google/callback', { code, state }),
};

// Settings
export const settingsApi = {
  getProfile: () => api.get('/settings/profile'),
  updateProfile: (data: any) => api.patch('/settings/profile', data),
  changePassword: (data: { currentPassword: string; newPassword: string }) =>
    api.post('/settings/password', data),
  getNotifications: (params?: { page?: number; pageSize?: number; unreadOnly?: boolean }) =>
    api.get('/settings/notifications', params),
  markNotificationRead: (id: string) => api.patch(`/settings/notifications/${id}/read`),
  markAllNotificationsRead: () => api.post('/settings/notifications/read-all'),
  getPreferences: () => api.get('/settings/preferences'),
  updatePreferences: (data: any) => api.patch('/settings/preferences', data),
};

// Suppression List
export const suppressionApi = {
  list: (organizationId: string, params?: { page?: number; pageSize?: number; activeOnly?: boolean }) =>
    api.get('/suppressions', { params: { organizationId, ...params } }),
  add: (data: { phone: string; reason: string; campaignId?: string; expiresAt?: string }) =>
    api.post('/suppressions', data),
  remove: (id: string) => api.delete(`/suppressions/${id}`),
  check: (phone: string) => api.get('/suppressions/check', { params: { phone } }),
  import: (file: File) => api.upload('/suppressions/import', file),
};

// Consent Records
export const consentApi = {
  list: (organizationId: string, params?: { page?: number; pageSize?: number; status?: string }) =>
    api.get('/consent', { params: { organizationId, ...params } }),
  record: (data: { phone: string; status: string; method: string; proofUrl?: string; campaignId?: string }) =>
    api.post('/consent', data),
  revoke: (id: string) => api.post(`/consent/${id}/revoke`),
};

// Webhooks (for Twilio, etc.)
export const webhooksApi = {
  twilio: {
    voice: (data: any) => api.post('/webhooks/twilio/voice', data),
    status: (data: any) => api.post('/webhooks/twilio/status', data),
    recording: (data: any) => api.post('/webhooks/twilio/recording', data),
    transcription: (data: any) => api.post('/webhooks/twilio/transcription', data),
  },
  google: {
    sheets: (data: any) => api.post('/webhooks/google/sheets', data),
  },
  n8n: {
    callback: (data: any) => api.post('/webhooks/n8n/callback', data),
  },
};