// Database client and utilities for AI Voice Calling Platform

import { PrismaClient } from '@prisma/client';
import type { PaginationParams, PaginatedResult } from '../utils';

// ============================================
// PRISMA CLIENT SINGLETON
// ============================================

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development'
      ? ['query', 'error', 'warn']
      : ['error'],
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

// ============================================
// TRANSACTION HELPERS
// ============================================

/**
 * Execute multiple operations in a transaction
 */
export async function transaction<T>(
  fn: (tx: PrismaClient) => Promise<T>
): Promise<T> {
  return prisma.$transaction(fn);
}

/**
 * Execute raw SQL in a transaction
 */
export async function rawTransaction<T>(
  queries: Array<{ sql: string; args?: unknown[] }>
): Promise<T[]> {
  return prisma.$transaction(
    queries.map(q => prisma.$queryRawUnsafe(q.sql, ...(q.args || [])))
  ) as Promise<T[]>;
}

// ============================================
// COMMON QUERY HELPERS
// ============================================

/**
 * Find by ID with error handling
 */
export async function findByIdOrThrow<T>(
  model: keyof PrismaClient,
  id: string,
  errorMessage?: string
): Promise<T> {
  const delegate = prisma[model] as any;
  const record = await delegate.findUnique({ where: { id } });
  if (!record) {
    throw new Error(errorMessage || `${String(model)} not found: ${id}`);
  }
  return record as T;
}

/**
 * Find first with error handling
 */
export async function findFirstOrThrow<T>(
  model: keyof PrismaClient,
  where: Record<string, unknown>,
  errorMessage?: string
): Promise<T> {
  const delegate = prisma[model] as any;
  const record = await delegate.findFirst({ where });
  if (!record) {
    throw new Error(errorMessage || `${String(model)} not found`);
  }
  return record as T;
}

/**
 * Soft delete (set deletedAt)
 */
export async function softDelete(
  model: keyof PrismaClient,
  id: string
): Promise<void> {
  const delegate = prisma[model] as any;
  await delegate.update({
    where: { id },
    data: { deletedAt: new Date() },
  });
}

/**
 * Bulk create with skip duplicates
 */
export async function bulkCreate<T>(
  model: keyof PrismaClient,
  data: T[],
  skipDuplicates = true
): Promise<number> {
  const delegate = prisma[model] as any;
  const result = await delegate.createMany({
    data,
    skipDuplicates,
  });
  return result.count;
}

/**
 * Bulk update
 */
export async function bulkUpdate<T>(
  model: keyof PrismaClient,
  where: Record<string, unknown>,
  data: Partial<T>
): Promise<number> {
  const delegate = prisma[model] as any;
  const result = await delegate.updateMany({ where, data });
  return result.count;
}

// ============================================
// PAGINATION HELPERS
// ============================================

/**
 * Get paginated results with count
 */
export async function paginateQuery<T>(
  model: keyof PrismaClient,
  params: PaginationParams,
  where?: Record<string, unknown>,
  include?: Record<string, unknown>,
  orderBy?: Record<string, 'asc' | 'desc'>
): Promise<PaginatedResult<T>> {
  const delegate = prisma[model] as any;
  const { page = 1, pageSize = 20, sortBy, sortOrder = 'desc' } = params;

  const [data, total] = await Promise.all([
    delegate.findMany({
      where,
      include,
      orderBy: sortBy ? { [sortBy]: sortOrder } : orderBy,
      skip: (page - 1) * pageSize,
      take: pageSize,
    }),
    delegate.count({ where }),
  ]);

  const totalPages = Math.ceil(total / pageSize);

  return {
    data: data as T[],
    total,
    page,
    pageSize,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1,
  };
}

/**
 * Cursor-based pagination (for large datasets)
 */
export async function paginateWithCursor<T>(
  model: keyof PrismaClient,
  cursor: string | undefined,
  limit: number,
  where?: Record<string, unknown>,
  orderBy?: Record<string, 'asc' | 'desc'>
): Promise<{ data: T[]; nextCursor: string | null }> {
  const delegate = prisma[model] as any;
  const data = await delegate.findMany({
    where,
    orderBy,
    take: limit + 1,
    cursor: cursor ? { id: cursor } : undefined,
  });

  let nextCursor: string | null = null;
  if (data.length > limit) {
    const nextItem = data.pop() as any;
    nextCursor = nextItem.id;
  }

  return { data: data as T[], nextCursor };
}

// ============================================
// AGGREGATION HELPERS
// ============================================

/**
 * Get dashboard metrics for a campaign
 */
export async function getCampaignMetrics(campaignId: string): Promise<{
  totalCustomers: number;
  totalCalls: number;
  completedCalls: number;
  failedCalls: number;
  answeredCalls: number;
  interestedCount: number;
  callbackCount: number;
  optOutCount: number;
  averageDuration: number;
  successRate: number;
  answerRate: number;
}> {
  const [
    totalCustomers,
    totalCalls,
    completedCalls,
    failedCalls,
    answeredCalls,
    interestedCount,
    callbackCount,
    optOutCount,
    avgDuration,
  ] = await Promise.all([
    prisma.campaignCustomer.count({ where: { campaignId } }),
    prisma.call.count({ where: { campaignId } }),
    prisma.call.count({ where: { campaignId, status: 'COMPLETED' } }),
    prisma.call.count({ where: { campaignId, status: { in: ['FAILED', 'BUSY', 'NO_ANSWER', 'VOICEMAIL', 'INVALID_NUMBER'] } } }),
    prisma.call.count({ where: { campaignId, status: { in: ['COMPLETED', 'BUSY', 'NO_ANSWER', 'VOICEMAIL'] } } }),
    prisma.call.count({ where: { campaignId, interestLevel: { in: ['HOT', 'WARM'] } } }),
    prisma.callback.count({ where: { campaignId, status: 'SCHEDULED' } }),
    prisma.customer.count({ where: { campaigns: { some: { campaignId } }, status: 'OPTED_OUT' } }),
    prisma.call.aggregate({
      where: { campaignId, duration: { not: null } },
      _avg: { duration: true },
    }),
  ]);

  const averageDuration = avgDuration._avg.duration || 0;
  const successRate = totalCalls > 0 ? (completedCalls / totalCalls) * 100 : 0;
  const answerRate = totalCalls > 0 ? (answeredCalls / totalCalls) * 100 : 0;

  return {
    totalCustomers,
    totalCalls,
    completedCalls,
    failedCalls,
    answeredCalls,
    interestedCount,
    callbackCount,
    optOutCount,
    averageDuration: Math.round(averageDuration),
    successRate: Math.round(successRate * 100) / 100,
    answerRate: Math.round(answerRate * 100) / 100,
  };
}

/**
 * Get organization-wide dashboard metrics
 */
export async function getOrganizationMetrics(organizationId: string): Promise<{
  totalCustomers: number;
  totalCalls: number;
  completedCalls: number;
  failedCalls: number;
  answeredCalls: number;
  interestedCustomers: number;
  hotLeads: number;
  callbacksScheduled: number;
  optOuts: number;
  averageCallDuration: number;
  callSuccessRate: number;
  answerRate: number;
  conversionRate: number;
}> {
  const [
    totalCustomers,
    totalCalls,
    completedCalls,
    failedCalls,
    answeredCalls,
    interestedCustomers,
    hotLeads,
    callbacksScheduled,
    optOuts,
    avgDuration,
    totalInterested,
  ] = await Promise.all([
    prisma.customer.count({ where: { organizationId } }),
    prisma.call.count({ where: { campaign: { organizationId } } }),
    prisma.call.count({ where: { campaign: { organizationId }, status: 'COMPLETED' } }),
    prisma.call.count({ where: { campaign: { organizationId }, status: { in: ['FAILED', 'BUSY', 'NO_ANSWER', 'VOICEMAIL', 'INVALID_NUMBER'] } } }),
    prisma.call.count({ where: { campaign: { organizationId }, status: { in: ['COMPLETED', 'BUSY', 'NO_ANSWER', 'VOICEMAIL'] } } }),
    prisma.customer.count({ where: { organizationId, interestLevel: { in: ['HOT', 'WARM'] } } }),
    prisma.customer.count({ where: { organizationId, interestLevel: 'HOT' } }),
    prisma.callback.count({ where: { campaign: { organizationId }, status: 'SCHEDULED' } }),
    prisma.customer.count({ where: { organizationId, status: 'OPTED_OUT' } }),
    prisma.call.aggregate({
      where: { campaign: { organizationId }, duration: { not: null } },
      _avg: { duration: true },
    }),
    prisma.call.count({ where: { campaign: { organizationId }, interestLevel: { in: ['HOT', 'WARM'] } } }),
  ]);

  const averageCallDuration = Math.round(avgDuration._avg.duration || 0);
  const callSuccessRate = totalCalls > 0 ? Math.round((completedCalls / totalCalls) * 10000) / 100 : 0;
  const answerRate = totalCalls > 0 ? Math.round((answeredCalls / totalCalls) * 10000) / 100 : 0;
  const conversionRate = totalCalls > 0 ? Math.round((totalInterested / totalCalls) * 10000) / 100 : 0;

  return {
    totalCustomers,
    totalCalls,
    completedCalls,
    failedCalls,
    answeredCalls,
    interestedCustomers,
    hotLeads,
    callbacksScheduled,
    optOuts,
    averageCallDuration,
    callSuccessRate,
    answerRate,
    conversionRate,
  };
}

/**
 * Get daily call analytics for a campaign
 */
export async function getDailyCallAnalytics(
  campaignId: string,
  days = 30
): Promise<Array<{
  date: string;
  totalCalls: number;
  completedCalls: number;
  failedCalls: number;
  answeredCalls: number;
  averageDuration: number;
  hotLeads: number;
  warmLeads: number;
  coldLeads: number;
  callbacksScheduled: number;
  optOuts: number;
}>> {
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  startDate.setHours(0, 0, 0, 0);

  const calls = await prisma.call.findMany({
    where: {
      campaignId,
      createdAt: { gte: startDate },
    },
    select: {
      createdAt: true,
      status: true,
      duration: true,
      interestLevel: true,
    },
  });

  const callbacks = await prisma.callback.findMany({
    where: {
      campaignId,
      createdAt: { gte: startDate },
      status: 'SCHEDULED',
    },
    select: { scheduledAt: true },
  });

  const optOuts = await prisma.customer.findMany({
    where: {
      campaigns: { some: { campaignId } },
      optedOutAt: { gte: startDate },
    },
    select: { optedOutAt: true },
  });

  // Group by date
  const dailyData = new Map<string, {
    totalCalls: number;
    completedCalls: number;
    failedCalls: number;
    answeredCalls: number;
    totalDuration: number;
    durationCount: number;
    hotLeads: number;
    warmLeads: number;
    coldLeads: number;
    callbacksScheduled: number;
    optOuts: number;
  }>();

  // Initialize all days
  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    const key = date.toISOString().split('T')[0];
    dailyData.set(key, {
      totalCalls: 0,
      completedCalls: 0,
      failedCalls: 0,
      answeredCalls: 0,
      totalDuration: 0,
      durationCount: 0,
      hotLeads: 0,
      warmLeads: 0,
      coldLeads: 0,
      callbacksScheduled: 0,
      optOuts: 0,
    });
  }

  // Aggregate calls
  for (const call of calls) {
    const key = call.createdAt.toISOString().split('T')[0];
    const day = dailyData.get(key);
    if (day) {
      day.totalCalls++;
      if (call.status === 'COMPLETED') day.completedCalls++;
      if (['FAILED', 'BUSY', 'NO_ANSWER', 'VOICEMAIL', 'INVALID_NUMBER'].includes(call.status)) {
        day.failedCalls++;
      }
      if (['COMPLETED', 'BUSY', 'NO_ANSWER', 'VOICEMAIL'].includes(call.status)) {
        day.answeredCalls++;
      }
      if (call.duration) {
        day.totalDuration += call.duration;
        day.durationCount++;
      }
      if (call.interestLevel === 'HOT') day.hotLeads++;
      else if (call.interestLevel === 'WARM') day.warmLeads++;
      else if (call.interestLevel === 'COLD') day.coldLeads++;
    }
  }

  // Aggregate callbacks
  for (const cb of callbacks) {
    const key = cb.scheduledAt.toISOString().split('T')[0];
    const day = dailyData.get(key);
    if (day) day.callbacksScheduled++;
  }

  // Aggregate opt-outs
  for (const optOut of optOuts) {
    if (optOut.optedOutAt) {
      const key = optOut.optedOutAt.toISOString().split('T')[0];
      const day = dailyData.get(key);
      if (day) day.optOuts++;
    }
  }

  // Convert to array
  return Array.from(dailyData.entries()).map(([date, data]) => ({
    date,
    totalCalls: data.totalCalls,
    completedCalls: data.completedCalls,
    failedCalls: data.failedCalls,
    answeredCalls: data.answeredCalls,
    averageDuration: data.durationCount > 0 ? Math.round(data.totalDuration / data.durationCount) : 0,
    hotLeads: data.hotLeads,
    warmLeads: data.warmLeads,
    coldLeads: data.coldLeads,
    callbacksScheduled: data.callbacksScheduled,
    optOuts: data.optOuts,
  }));
}

// ============================================
// SEARCH HELPERS
// ============================================

/**
 * Search customers with filters
 */
export async function searchCustomers(
  organizationId: string,
  filters: {
    query?: string;
    status?: string[];
    interestLevel?: string[];
    language?: string;
    hasCallback?: boolean;
    doNotCall?: boolean;
    page?: number;
    pageSize?: number;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }
): Promise<PaginatedResult<any>> {
  const where: Record<string, unknown> = { organizationId };

  if (filters.query) {
    where.OR = [
      { firstName: { contains: filters.query, mode: 'insensitive' } },
      { lastName: { contains: filters.query, mode: 'insensitive' } },
      { phone: { contains: filters.query } },
      { email: { contains: filters.query, mode: 'insensitive' } },
      { company: { contains: filters.query, mode: 'insensitive' } },
    ];
  }

  if (filters.status?.length) {
    where.status = { in: filters.status };
  }

  if (filters.interestLevel?.length) {
    where.interestLevel = { in: filters.interestLevel };
  }

  if (filters.language) {
    where.language = filters.language;
  }

  if (filters.hasCallback) {
    where.nextCallbackAt = { not: null };
  }

  if (filters.doNotCall !== undefined) {
    where.doNotCall = filters.doNotCall;
  }

  return paginateQuery('customer', {
    page: filters.page || 1,
    pageSize: filters.pageSize || 20,
    sortBy: filters.sortBy || 'createdAt',
    sortOrder: filters.sortOrder || 'desc',
  }, where);
}

// ============================================
// CLEANUP / MAINTENANCE
// ============================================

/**
 * Clean up old queue jobs
 */
export async function cleanupOldQueueJobs(olderThanDays = 30): Promise<number> {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - olderThanDays);

  const result = await prisma.call.deleteMany({
    where: {
      status: { in: ['COMPLETED', 'FAILED', 'CANCELLED'] },
      createdAt: { lt: cutoff },
    },
  });

  return result.count;
}

/**
 * Archive completed campaigns
 */
export async function archiveOldCampaigns(olderThanDays = 90): Promise<number> {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - olderThanDays);

  const result = await prisma.campaign.updateMany({
    where: {
      status: { in: ['COMPLETED', 'STOPPED'] },
      updatedAt: { lt: cutoff },
    },
    data: { status: 'COMPLETED' }, // Already completed, just ensuring
  });

  return result.count;
}

// ============================================
// GRACEFUL SHUTDOWN
// ============================================

export async function disconnectDatabase(): Promise<void> {
  await prisma.$disconnect();
}

process.on('beforeExit', async () => {
  await disconnectDatabase();
});