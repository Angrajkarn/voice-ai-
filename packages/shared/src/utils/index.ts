// Shared utility functions for AI Voice Calling Platform

import CryptoJS from 'crypto-js';
import { z } from 'zod';

// ============================================
// ENCRYPTION UTILITIES
// ============================================

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || 'default-key-change-in-production';

export function encrypt(text: string): string {
  return CryptoJS.AES.encrypt(text, ENCRYPTION_KEY).toString();
}

export function decrypt(ciphertext: string): string {
  const bytes = CryptoJS.AES.decrypt(ciphertext, ENCRYPTION_KEY);
  return bytes.toString(CryptoJS.enc.Utf8);
}

export function encryptObject<T extends Record<string, unknown>>(obj: T): T {
  const encrypted: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      encrypted[key] = encrypt(value);
    } else if (typeof value === 'object' && value !== null) {
      encrypted[key] = encryptObject(value as Record<string, unknown>);
    } else {
      encrypted[key] = value;
    }
  }
  return encrypted as T;
}

export function decryptObject<T extends Record<string, unknown>>(obj: T): T {
  const decrypted: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      try {
        decrypted[key] = decrypt(value);
      } catch {
        decrypted[key] = value; // Not encrypted, keep as-is
      }
    } else if (typeof value === 'object' && value !== null) {
      decrypted[key] = decryptObject(value as Record<string, unknown>);
    } else {
      decrypted[key] = value;
    }
  }
  return decrypted as T;
}

// ============================================
// PHONE NUMBER UTILITIES
// ============================================

/**
 * Normalize phone number to E.164 format
 * Handles Indian numbers (+91) and international formats
 */
export function normalizePhoneNumber(phone: string, defaultCountryCode = '91'): string {
  // Remove all non-digits except +
  const cleaned = phone.replace(/[^\d+]/g, '');

  // Already in E.164 format
  if (cleaned.startsWith('+')) {
    return cleaned;
  }

  // Indian mobile number (10 digits starting with 6-9)
  if (cleaned.length === 10 && /^[6-9]\d{9}$/.test(cleaned)) {
    return `+${defaultCountryCode}${cleaned}`;
  }

  // Indian number with country code (12 digits starting with 91)
  if (cleaned.length === 12 && cleaned.startsWith('91') && /^91[6-9]\d{9}$/.test(cleaned)) {
    return `+${cleaned}`;
  }

  // Default: assume it needs country code
  return `+${defaultCountryCode}${cleaned}`;
}

/**
 * Format phone number for display
 */
export function formatPhoneForDisplay(phone: string): string {
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

/**
 * Mask phone number for privacy (show only last 4 digits)
 */
export function maskPhoneNumber(phone: string): string {
  if (phone.length <= 4) return '****';
  const visible = phone.slice(-4);
  const masked = '*'.repeat(phone.length - 4);
  return masked + visible;
}

/**
 * Validate Indian mobile number
 */
export function isValidIndianMobile(phone: string): boolean {
  const normalized = normalizePhoneNumber(phone);
  return /^\+91[6-9]\d{9}$/.test(normalized);
}

// ============================================
// DATE/TIME UTILITIES
// ============================================

import { format, parseISO, isWithinInterval, startOfDay, endOfDay, addDays, setHours, setMinutes } from 'date-fns';
import { toZonedTime, fromZonedTime, formatInTimeZone } from 'date-fns-tz';

/**
 * Check if current time is within calling window for a timezone
 */
export function isWithinCallingWindow(
  callingWindowStart: string, // HH:mm
  callingWindowEnd: string,   // HH:mm
  timezone: string,
  date = new Date()
): boolean {
  const zonedDate = toZonedTime(date, timezone);
  const [startHour, startMin] = callingWindowStart.split(':').map(Number);
  const [endHour, endMin] = callingWindowEnd.split(':').map(Number);

  const windowStart = setMinutes(setHours(zonedDate, startHour), startMin);
  const windowEnd = setMinutes(setHours(zonedDate, endHour), endMin);

  return isWithinInterval(zonedDate, { start: windowStart, end: windowEnd });
}

/**
 * Get next valid calling time
 */
export function getNextCallingTime(
  callingWindowStart: string,
  callingWindowEnd: string,
  timezone: string,
  skipWeekends: boolean,
  fromDate = new Date()
): Date {
  let next = toZonedTime(fromDate, timezone);
  const [startHour, startMin] = callingWindowStart.split(':').map(Number);

  // If before window today, set to window start today
  if (next.getHours() < startHour || (next.getHours() === startHour && next.getMinutes() < startMin)) {
    next = setMinutes(setHours(next, startHour), startMin);
  } else {
    // Move to next day
    next = addDays(next, 1);
    next = setMinutes(setHours(next, startHour), startMin);
  }

  // Skip weekends if needed
  if (skipWeekends) {
    while (next.getDay() === 0 || next.getDay() === 6) {
      next = addDays(next, 1);
      next = setMinutes(setHours(next, startHour), startMin);
    }
  }

  return fromZonedTime(next, timezone);
}

/**
 * Format date for display in timezone
 */
export function formatInTimezone(date: Date | string, pattern: string, timezone: string): string {
  const d = typeof date === 'string' ? parseISO(date) : date;
  return formatInTimeZone(d, timezone, pattern);
}

// ============================================
// VALIDATION UTILITIES
// ============================================

/**
 * Safe parse with default
 */
export function safeParse<T>(schema: z.ZodSchema<T>, data: unknown, defaultValue: T): T {
  const result = schema.safeParse(data);
  return result.success ? result.data : defaultValue;
}

/**
 * Validate and transform phone numbers in bulk
 */
export function validateAndNormalizePhones(
  phones: string[],
  defaultCountryCode = '91'
): { valid: string[]; invalid: string[] } {
  const valid: string[] = [];
  const invalid: string[] = [];

  for (const phone of phones) {
    try {
      const normalized = normalizePhoneNumber(phone, defaultCountryCode);
      // Basic validation: must be valid E.164
      if (/^\+[1-9]\d{1,14}$/.test(normalized)) {
        valid.push(normalized);
      } else {
        invalid.push(phone);
      }
    } catch {
      invalid.push(phone);
    }
  }

  return { valid, invalid };
}

// ============================================
// CSV/EXCEL UTILITIES
// ============================================

export interface CSVColumnMap {
  [key: string]: string; // CSV header -> internal field
}

export const DEFAULT_CUSTOMER_CSV_MAP: CSVColumnMap = {
  'first_name': 'firstName',
  'firstname': 'firstName',
  'first name': 'firstName',
  'last_name': 'lastName',
  'lastname': 'lastName',
  'last name': 'lastName',
  'email': 'email',
  'phone': 'phone',
  'phone_number': 'phone',
  'phone number': 'phone',
  'mobile': 'phone',
  'company': 'company',
  'location': 'location',
  'city': 'location',
  'language': 'language',
  'timezone': 'timezone',
  'tags': 'tags',
};

/**
 * Parse CSV row to customer object
 */
export function parseCustomerFromCSV(
  row: Record<string, string>,
  columnMap: CSVColumnMap = DEFAULT_CUSTOMER_CSV_MAP
): Record<string, unknown> {
  const customer: Record<string, unknown> = {};

  for (const [csvHeader, field] of Object.entries(columnMap)) {
    // Find matching column (case-insensitive)
    const matchedKey = Object.keys(row).find(
      k => k.toLowerCase().trim() === csvHeader.toLowerCase()
    );

    if (matchedKey && row[matchedKey]) {
      let value: unknown = row[matchedKey].trim();

      // Special handling for certain fields
      if (field === 'phone') {
        value = normalizePhoneNumber(value as string);
      } else if (field === 'tags') {
        value = (value as string).split(',').map(t => t.trim()).filter(Boolean);
      }

      customer[field] = value;
    }
  }

  return customer;
}

// ============================================
// SLUG GENERATION
// ============================================

export function generateSlug(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function generateUniqueSlug(baseSlug: string, existingSlugs: string[]): string {
  let slug = baseSlug;
  let counter = 1;

  while (existingSlugs.includes(slug)) {
    slug = `${baseSlug}-${counter}`;
    counter++;
  }

  return slug;
}

// ============================================
// PAGINATION UTILITIES
// ============================================

export interface PaginationParams {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export function paginate<T>(
  items: T[],
  params: PaginationParams
): PaginatedResult<T> {
  const { page = 1, pageSize = 20, sortBy, sortOrder = 'desc' } = params;

  let sorted = [...items];
  if (sortBy) {
    sorted.sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[sortBy];
      const bVal = (b as Record<string, unknown>)[sortBy];
      if (aVal === bVal) return 0;
      if (aVal == null) return sortOrder === 'asc' ? -1 : 1;
      if (bVal == null) return sortOrder === 'asc' ? 1 : -1;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const comparison = String(aVal).localeCompare(String(bVal));
      return sortOrder === 'asc' ? comparison : -comparison;
      return 0;
    });
  }

  const total = sorted.length;
  const totalPages = Math.ceil(total / pageSize);
  const start = (page - 1) * pageSize;
  const data = sorted.slice(start, start + pageSize);

  return {
    data,
    total,
    page,
    pageSize,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1,
  };
}

// ============================================
// ERROR HANDLING
// ============================================

export class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 400,
    public readonly details?: unknown
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: unknown) {
    super(message, 'VALIDATION_ERROR', 400, details);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} not found: ${id}`, 'NOT_FOUND', 404);
    this.name = 'NotFoundError';
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 'UNAUTHORIZED', 401);
    this.name = 'UnauthorizedError';
  }
}

export class ForbiddenError extends AppError {
  constructor(message = 'Forbidden') {
    super(message, 'FORBIDDEN', 403);
    this.name = 'ForbiddenError';
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super(message, 'CONFLICT', 409);
    this.name = 'ConflictError';
  }
}

export class RateLimitError extends AppError {
  constructor(message = 'Rate limit exceeded', public readonly retryAfter?: number) {
    super(message, 'RATE_LIMIT', 429);
    this.name = 'RateLimitError';
  }
}

export class ExternalServiceError extends AppError {
  constructor(service: string, message: string, public readonly originalError?: Error) {
    super(`${service} error: ${message}`, 'EXTERNAL_SERVICE_ERROR', 502, { service, originalError: originalError?.message });
    this.name = 'ExternalServiceError';
  }
}

// ============================================
// RETRY UTILITIES
// ============================================

export interface RetryOptions {
  maxAttempts: number;
  baseDelay: number; // ms
  maxDelay: number; // ms
  backoffMultiplier: number;
  retryableErrors?: string[];
}

export const DEFAULT_RETRY_OPTIONS: RetryOptions = {
  maxAttempts: 3,
  baseDelay: 1000,
  maxDelay: 30000,
  backoffMultiplier: 2,
  retryableErrors: ['ECONNRESET', 'ETIMEDOUT', 'ENOTFOUND', 'EAI_AGAIN', 'RATE_LIMIT', 'EXTERNAL_SERVICE_ERROR'],
};

/**
 * Execute function with exponential backoff retry
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: Partial<RetryOptions> = {}
): Promise<T> {
  const opts = { ...DEFAULT_RETRY_OPTIONS, ...options };
  let lastError: Error;

  for (let attempt = 1; attempt <= opts.maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      // Check if error is retryable
      const isRetryable = opts.retryableErrors?.some(e =>
        error instanceof AppError && error.code === e
      ) || false;

      if (!isRetryable || attempt === opts.maxAttempts) {
        throw error;
      }

      // Calculate delay with jitter
      const delay = Math.min(
        opts.baseDelay * Math.pow(opts.backoffMultiplier, attempt - 1),
        opts.maxDelay
      );
      const jitter = delay * 0.1 * Math.random();

      await new Promise(resolve => setTimeout(resolve, delay + jitter));
    }
  }

  throw lastError!;
}

// ============================================
// RANDOM/ID GENERATION
// ============================================

export function generateId(prefix = ''): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).slice(2, 8);
  return `${prefix}${prefix ? '_' : ''}${timestamp}${random}`;
}

export function generateOTP(length = 6): string {
  return Math.floor(10 ** (length - 1) + Math.random() * 9 * 10 ** (length - 1)).toString();
}

// ============================================
// FILE UTILITIES
// ============================================

export function getFileExtension(filename: string): string {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2).toLowerCase();
}

export function isAllowedFileType(filename: string, allowedTypes: string[]): boolean {
  const ext = getFileExtension(filename);
  return allowedTypes.includes(ext);
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ============================================
// COLOR UTILITIES (for dashboard)
// ============================================

export const STATUS_COLORS: Record<string, string> = {
  // Campaign status
  DRAFT: 'gray',
  READY: 'blue',
  RUNNING: 'green',
  PAUSED: 'yellow',
  COMPLETED: 'green',
  STOPPED: 'red',

  // Call status
  QUEUED: 'gray',
  INITIATING: 'blue',
  RINGING: 'yellow',
  IN_PROGRESS: 'green',

  BUSY: 'orange',
  NO_ANSWER: 'gray',
  VOICEMAIL: 'purple',
  INVALID_NUMBER: 'red',
  BLOCKED: 'red',
  CANCELLED: 'gray',

  // Customer status
  NEW: 'blue',
  CONTACTED: 'green',
  HOT_LEAD: 'red',
  WARM_LEAD: 'yellow',
  COLD_LEAD: 'gray',
  NOT_INTERESTED: 'red',
  CALLBACK_REQUESTED: 'purple',
  DO_NOT_CALL: 'red',
  OPTED_OUT: 'red',

  // Interest level
  HOT: 'red',
  WARM: 'yellow',
  COLD: 'blue',
  UNKNOWN: 'gray',

  // Sync status
  PENDING: 'yellow',
  SYNCED: 'green',
  RETRYING: 'blue',
};

export function getStatusColor(status: string): string {
  return STATUS_COLORS[status] || 'gray';
}

// ============================================
// PERMISSION UTILITIES
// ============================================

export const ROLE_HIERARCHY: Record<string, number> = {
  SUPER_ADMIN: 5,
  ADMIN: 4,
  MANAGER: 3,
  AGENT: 2,
  VIEWER: 1,
};

export function hasPermission(userRole: string, requiredRole: string): boolean {
  return (ROLE_HIERARCHY[userRole] || 0) >= (ROLE_HIERARCHY[requiredRole] || 0);
}

export function canAccessOrganization(userOrgId: string, targetOrgId: string, userRole: string): boolean {
  if (userRole === 'SUPER_ADMIN') return true;
  return userOrgId === targetOrgId;
}