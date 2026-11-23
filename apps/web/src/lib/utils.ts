// Utility functions for the web app

import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (minutes < 60) return `${minutes}m ${remainingSeconds}s`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

export function formatPhoneNumber(phone: string): string {
  // E.164 to readable format
  if (phone.startsWith('+91') && phone.length === 13) {
    const num = phone.slice(3);
    return `+91 ${num.slice(0, 5)} ${num.slice(5)}`;
  }
  if (phone.startsWith('+1') && phone.length === 12) {
    const num = phone.slice(2);
    return `+1 (${num.slice(0, 3)}) ${num.slice(3, 6)}-${num.slice(6)}`;
  }
  return phone;
}

export function maskPhoneNumber(phone: string): string {
  if (phone.length <= 4) return '****';
  return '*'.repeat(phone.length - 4) + phone.slice(-4);
}

export function formatDate(date: Date | string, options?: Intl.DateTimeFormatOptions): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    ...options,
  });
}

export function formatDateTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatRelativeTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(d);
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    // Campaign
    DRAFT: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    READY: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    RUNNING: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    PAUSED: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    COMPLETED: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    STOPPED: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',

    // Call
    QUEUED: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    INITIATING: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    RINGING: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    IN_PROGRESS: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    COMPLETED: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    FAILED: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    BUSY: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    NO_ANSWER: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    VOICEMAIL: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    INVALID_NUMBER: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    BLOCKED: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    CANCELLED: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',

    // Customer
    NEW: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    CONTACTED: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    HOT_LEAD: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    WARM_LEAD: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    COLD_LEAD: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    NOT_INTERESTED: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    CALLBACK_REQUESTED: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    DO_NOT_CALL: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    INVALID_NUMBER: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    OPTED_OUT: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',

    // Interest
    HOT: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    WARM: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    COLD: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    UNKNOWN: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',

    // Sync
    PENDING: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    SYNCED: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    FAILED: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    RETRYING: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  };
  return colors[status] || 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300';
}

export function getInterestColor(level: string): string {
  return getStatusColor(level);
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + '...';
}

export function generateId(): string {
  return Math.random().toString(36).slice(2, 11);
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

export function downloadFile(data: Blob, filename: string): void {
  const url = URL.createObjectURL(data);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function parseCSV(csvText: string): Record<string, string>[] {
  const lines = csvText.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
  return lines.slice(1).map(line => {
    const values = line.split(',').map(v => v.trim().replace(/"/g, ''));
    const obj: Record<string, string> = {};
    headers.forEach((header, i) => {
      obj[header] = values[i] || '';
    });
    return obj;
  });
}

export function convertToCSV(data: Record<string, unknown>[]): string {
  if (data.length === 0) return '';
  const headers = Object.keys(data[0]);
  const rows = data.map(row =>
    headers.map(header => {
      const value = row[header];
      if (value === null || value === undefined) return '';
      const str = String(value);
      return str.includes(',') || str.includes('"') || str.includes('\n')
        ? `"${str.replace(/"/g, '""')}"`
        : str;
    }).join(',')
  );
  return [headers.join(','), ...rows].join('\n');
}