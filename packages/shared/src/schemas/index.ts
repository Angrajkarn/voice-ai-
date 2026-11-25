// Zod validation schemas for AI Voice Calling Platform

import { z } from 'zod';

// ============================================
// PRIMITIVE SCHEMAS
// ============================================

export const phoneSchema = z.string().regex(/^\+[1-9]\d{1,14}$/, 'Phone must be in E.164 format (e.g., +15551234567)');
export const emailSchema = z.string().email('Invalid email format');
export const urlSchema = z.string().url('Invalid URL format');
export const uuidSchema = z.string().uuid('Invalid UUID format');
export const cuidSchema = z.string().cuid('Invalid CUID format');
export const dateTimeSchema = z.string().datetime('Invalid ISO 8601 datetime');
export const dateSchema = z.string().date('Invalid date format (YYYY-MM-DD)');
export const timeSchema = z.string().regex(/^([01]\d|2[0-3]):([0-5]\d)$/, 'Invalid time format (HH:mm)');
export const languageSchema = z.enum(['en-IN', 'hi-IN', 'hinglish', 'en-US', 'en-GB']);
export const timezoneSchema = z.string().regex(/^[A-Za-z]+\/[A-Za-z_]+$/, 'Invalid IANA timezone');

// ============================================
// ENUM SCHEMAS
// ============================================

export const userRoleSchema = z.enum(['SUPER_ADMIN', 'ADMIN', 'MANAGER', 'AGENT', 'VIEWER']);
export const organizationPlanSchema = z.enum(['FREE', 'STARTER', 'PROFESSIONAL', 'ENTERPRISE']);
export const campaignStatusSchema = z.enum(['DRAFT', 'READY', 'RUNNING', 'PAUSED', 'COMPLETED', 'STOPPED']);
export const callStatusSchema = z.enum(['QUEUED', 'INITIATING', 'RINGING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'BUSY', 'NO_ANSWER', 'VOICEMAIL', 'INVALID_NUMBER', 'BLOCKED', 'CANCELLED']);
export const callDirectionSchema = z.enum(['OUTBOUND', 'INBOUND']);
export const customerStatusSchema = z.enum(['NEW', 'CONTACTED', 'HOT_LEAD', 'WARM_LEAD', 'COLD_LEAD', 'NOT_INTERESTED', 'CALLBACK_REQUESTED', 'DO_NOT_CALL', 'INVALID_NUMBER', 'OPTED_OUT']);
export const interestLevelSchema = z.enum(['HOT', 'WARM', 'COLD', 'UNKNOWN']);
export const syncStatusSchema = z.enum(['PENDING', 'SYNCED', 'FAILED', 'RETRYING']);
export const integrationTypeSchema = z.enum(['GOOGLE_SHEETS', 'GOOGLE_DRIVE', 'TWILIO', 'OPENAI', 'N8N']);
export const notificationTypeSchema = z.enum(['CALL_COMPLETED', 'HOT_LEAD', 'CALLBACK_SCHEDULED', 'HUMAN_FOLLOWUP_REQUIRED', 'OPT_OUT', 'CAMPAIGN_COMPLETED', 'SYNC_FAILED', 'ERROR']);
export const consentStatusSchema = z.enum(['GRANTED', 'DENIED', 'PENDING', 'REVOKED']);
export const callbackStatusSchema = z.enum(['SCHEDULED', 'COMPLETED', 'CANCELLED', 'FAILED', 'NO_ANSWER']);
export const suppressionReasonSchema = z.enum(['OPT_OUT', 'DND', 'INVALID', 'MANUAL']);
export const suppressionSourceSchema = z.enum(['CAMPAIGN', 'MANUAL', 'IMPORT', 'WEBHOOK']);
export const consentMethodSchema = z.enum(['VERBAL', 'SMS', 'EMAIL', 'WEB_FORM', 'CALL_RECORDING']);

// ============================================
// CORE ENTITY SCHEMAS
// ============================================

export const userSchema = z.object({
  id: cuidSchema,
  email: emailSchema,
  name: z.string().min(1).max(100).nullable(),
  avatarUrl: urlSchema.nullable(),
  role: userRoleSchema,
  isActive: z.boolean(),
  lastLoginAt: dateTimeSchema.nullable(),
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
  organizationId: cuidSchema,
});

export const organizationSchema = z.object({
  id: cuidSchema,
  name: z.string().min(1).max(100),
  slug: z.string().min(1).max(50).regex(/^[a-z0-9-]+$/),
  logoUrl: urlSchema.nullable(),
  plan: organizationPlanSchema,
  planExpiresAt: dateTimeSchema.nullable(),
  settings: z.record(z.unknown()),
  isActive: z.boolean(),
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
});

export const customerSchema = z.object({
  id: cuidSchema,
  externalId: z.string().max(100).nullable(),
  firstName: z.string().min(1).max(50),
  lastName: z.string().min(1).max(50),
  email: emailSchema.nullable(),
  phone: phoneSchema,
  phoneRaw: z.string().max(50).nullable(),
  company: z.string().max(100).nullable(),
  location: z.string().max(100).nullable(),
  language: languageSchema,
  timezone: timezoneSchema,
  tags: z.array(z.string().max(50)),
  customFields: z.record(z.unknown()),
  status: customerStatusSchema,
  interestLevel: interestLevelSchema,
  callAttempts: z.number().int().min(0),
  maxCallAttempts: z.number().int().min(1).max(10),
  lastCallAt: dateTimeSchema.nullable(),
  nextCallbackAt: dateTimeSchema.nullable(),
  lastCallStatus: callStatusSchema.nullable(),
  lastCallDuration: z.number().int().min(0).nullable(),
  finalDisposition: z.string().max(200).nullable(),
  doNotCall: z.boolean(),
  optedOutAt: dateTimeSchema.nullable(),
  optOutReason: z.string().max(500).nullable(),
  organizationId: cuidSchema,
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
});

export const campaignSchema = z.object({
  id: cuidSchema,
  name: z.string().min(1).max(100),
  description: z.string().max(500).nullable(),
  purpose: z.string().min(1).max(1000),
  aiInstructions: z.string().min(1).max(10000),
  openingScript: z.string().min(1).max(2000),
  knowledgeBase: z.string().max(20000),
  voiceId: z.string().min(1).max(50),
  language: languageSchema,
  supportedLanguages: z.array(languageSchema).min(1),
  maxCallsPerDay: z.number().int().min(1).max(10000),
  maxRetryAttempts: z.number().int().min(0).max(10),
  delayBetweenCalls: z.number().int().min(0).max(3600),
  callingWindowStart: timeSchema,
  callingWindowEnd: timeSchema,
  callingTimezone: timezoneSchema,
  skipWeekends: z.boolean(),
  skipHolidays: z.boolean(),
  allowCallbacks: z.boolean(),
  callbackWindowStart: timeSchema,
  callbackWindowEnd: timeSchema,
  maxCallbackDays: z.number().int().min(1).max(90),
  sheetsSyncEnabled: z.boolean(),
  sheetsSpreadsheetId: z.string().max(100).nullable(),
  sheetsSheetName: z.string().min(1).max(100),
  sheetsAutoSync: z.boolean(),
  status: campaignStatusSchema,
  startedAt: dateTimeSchema.nullable(),
  pausedAt: dateTimeSchema.nullable(),
  completedAt: dateTimeSchema.nullable(),
  stoppedAt: dateTimeSchema.nullable(),
  totalCustomers: z.number().int().min(0),
  completedCalls: z.number().int().min(0),
  failedCalls: z.number().int().min(0),
  interestedCount: z.number().int().min(0),
  callbackCount: z.number().int().min(0),
  optOutCount: z.number().int().min(0),
  organizationId: cuidSchema,
  ownerId: cuidSchema,
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
});

export const callSchema = z.object({
  id: cuidSchema,
  callSid: z.string().max(50).nullable(),
  direction: callDirectionSchema,
  status: callStatusSchema,
  fromNumber: phoneSchema,
  toNumber: phoneSchema,
  queuedAt: dateTimeSchema,
  initiatedAt: dateTimeSchema.nullable(),
  answeredAt: dateTimeSchema.nullable(),
  endedAt: dateTimeSchema.nullable(),
  duration: z.number().int().min(0).nullable(),
  billableDuration: z.number().int().min(0).nullable(),
  disposition: z.string().max(50).nullable(),
  failureReason: z.string().max(500).nullable(),
  hangupSource: z.string().max(50).nullable(),
  interestLevel: interestLevelSchema,
  customerIntent: z.string().max(500).nullable(),
  objections: z.array(z.string().max(200)),
  questionsAsked: z.array(z.string().max(500)),
  summary: z.string().max(5000).nullable(),
  sentiment: z.enum(['positive', 'neutral', 'negative']).nullable(),
  requiresHumanFollowup: z.boolean(),
  humanFollowupReason: z.string().max(1000).nullable(),
  recordingUrl: urlSchema.nullable(),
  recordingSid: z.string().max(50).nullable(),
  transcriptUrl: urlSchema.nullable(),
  transcriptText: z.string().max(50000).nullable(),
  transcriptSegments: z.array(z.object({
    speaker: z.enum(['ai', 'customer', 'system']),
    text: z.string(),
    startTime: z.number().min(0),
    endTime: z.number().min(0),
    confidence: z.number().min(0).max(1),
    language: languageSchema,
  })),
  sheetsSynced: z.boolean(),
  sheetsSyncAt: dateTimeSchema.nullable(),
  sheetsSyncStatus: syncStatusSchema,
  sheetsSyncError: z.string().max(1000).nullable(),
  sheetsRowIndex: z.number().int().min(1).nullable(),
  campaignId: cuidSchema,
  customerId: cuidSchema,
  agentId: cuidSchema.nullable(),
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
});

export const transcriptSegmentSchema = z.object({
  speaker: z.enum(['ai', 'customer', 'system']),
  text: z.string(),
  startTime: z.number().min(0),
  endTime: z.number().min(0),
  confidence: z.number().min(0).max(1),
  language: languageSchema,
});

export const callTranscriptSchema = z.object({
  id: cuidSchema,
  callId: cuidSchema,
  fullText: z.string(),
  segments: z.array(transcriptSegmentSchema),
  language: languageSchema,
  wordCount: z.number().int().min(0),
  duration: z.number().min(0),
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
});

export const callRecordingSchema = z.object({
  id: cuidSchema,
  callId: cuidSchema,
  url: urlSchema,
  provider: z.string().max(50),
  providerId: z.string().max(100),
  format: z.string().max(20),
  duration: z.number().min(0),
  sizeBytes: z.number().int().min(0),
  channels: z.number().int().min(1).max(2),
  sampleRate: z.number().int().min(8000).max(48000),
  driveFileId: z.string().max(100).nullable(),
  driveSyncedAt: dateTimeSchema.nullable(),
  driveSyncStatus: syncStatusSchema,
  expiresAt: dateTimeSchema.nullable(),
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
});

export const callbackSchema = z.object({
  id: cuidSchema,
  status: callbackStatusSchema,
  scheduledAt: dateTimeSchema,
  scheduledTimezone: timezoneSchema,
  reminderSent: z.boolean(),
  reminderSentAt: dateTimeSchema.nullable(),
  sourceCallId: cuidSchema.nullable(),
  customerNotes: z.string().max(2000).nullable(),
  aiNotes: z.string().max(2000).nullable(),
  campaignId: cuidSchema,
  customerId: cuidSchema,
  assigneeId: cuidSchema.nullable(),
  resultCallId: cuidSchema.nullable(),
  completedAt: dateTimeSchema.nullable(),
  outcome: z.string().max(500).nullable(),
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
});

export const integrationSchema = z.object({
  id: cuidSchema,
  type: integrationTypeSchema,
  name: z.string().min(1).max(100),
  config: z.record(z.unknown()),
  isActive: z.boolean(),
  lastSyncAt: dateTimeSchema.nullable(),
  lastSyncStatus: syncStatusSchema,
  lastSyncError: z.string().max(1000).nullable(),
  organizationId: cuidSchema,
  campaignId: cuidSchema.nullable(),
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
});

export const syncLogSchema = z.object({
  id: cuidSchema,
  integrationId: cuidSchema,
  operation: z.string().max(100),
  entityType: z.string().max(100),
  entityId: z.string().max(100),
  status: syncStatusSchema,
  error: z.string().max(2000).nullable(),
  requestData: z.record(z.unknown()).nullable(),
  responseData: z.record(z.unknown()).nullable(),
  retryCount: z.number().int().min(0),
  completedAt: dateTimeSchema.nullable(),
  createdAt: dateTimeSchema,
});

export const automationLogSchema = z.object({
  id: cuidSchema,
  campaignId: cuidSchema,
  triggerType: z.string().max(100),
  triggerData: z.record(z.unknown()),
  actionType: z.string().max(100),
  actionData: z.record(z.unknown()),
  status: z.enum(['PENDING', 'COMPLETED', 'FAILED']),
  error: z.string().max(2000).nullable(),
  completedAt: dateTimeSchema.nullable(),
  createdAt: dateTimeSchema,
});

export const suppressionListSchema = z.object({
  id: cuidSchema,
  phone: phoneSchema,
  reason: suppressionReasonSchema,
  source: suppressionSourceSchema,
  campaignId: cuidSchema.nullable(),
  organizationId: cuidSchema,
  customerId: cuidSchema.nullable(),
  expiresAt: dateTimeSchema.nullable(),
  isActive: z.boolean(),
  addedBy: z.string().max(100).nullable(),
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
});

export const consentRecordSchema = z.object({
  id: cuidSchema,
  phone: phoneSchema,
  status: consentStatusSchema,
  method: consentMethodSchema,
  proofUrl: urlSchema.nullable(),
  proofExpiresAt: dateTimeSchema.nullable(),
  campaignId: cuidSchema.nullable(),
  customerId: cuidSchema.nullable(),
  organizationId: cuidSchema,
  grantedAt: dateTimeSchema.nullable(),
  revokedAt: dateTimeSchema.nullable(),
  createdAt: dateTimeSchema,
  updatedAt: dateTimeSchema,
});

export const notificationSchema = z.object({
  id: cuidSchema,
  type: notificationTypeSchema,
  title: z.string().min(1).max(200),
  message: z.string().min(1).max(1000),
  data: z.record(z.unknown()),
  isRead: z.boolean(),
  readAt: dateTimeSchema.nullable(),
  userId: cuidSchema,
  organizationId: cuidSchema,
  campaignId: cuidSchema.nullable(),
  callId: cuidSchema.nullable(),
  createdAt: dateTimeSchema,
});

export const auditLogSchema = z.object({
  id: cuidSchema,
  action: z.string().max(100),
  entityType: z.string().max(100),
  entityId: z.string().max(100),
  oldData: z.record(z.unknown()).nullable(),
  newData: z.record(z.unknown()).nullable(),
  metadata: z.record(z.unknown()),
  userId: cuidSchema.nullable(),
  organizationId: cuidSchema,
  createdAt: dateTimeSchema,
});

// ============================================
// INPUT/CREATE SCHEMAS (for API requests)
// ============================================

export const createUserSchema = userSchema.omit({ id: true, createdAt: true, updatedAt: true, lastLoginAt: true });
export const updateUserSchema = createUserSchema.partial();

export const createOrganizationSchema = organizationSchema.omit({ id: true, createdAt: true, updatedAt: true, slug: true });
export const updateOrganizationSchema = createOrganizationSchema.partial();

export const createCustomerSchema = customerSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  callAttempts: true,
  lastCallAt: true,
  nextCallbackAt: true,
  lastCallStatus: true,
  lastCallDuration: true,
  finalDisposition: true,
  optedOutAt: true,
  optOutReason: true,
});
export const updateCustomerSchema = createCustomerSchema.partial();

export const createCampaignSchema = campaignSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  startedAt: true,
  pausedAt: true,
  completedAt: true,
  stoppedAt: true,
  totalCustomers: true,
  completedCalls: true,
  failedCalls: true,
  interestedCount: true,
  callbackCount: true,
  optOutCount: true,
});
export const updateCampaignSchema = createCampaignSchema.partial();

export const createCallSchema = callSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  callSid: true,
  initiatedAt: true,
  answeredAt: true,
  endedAt: true,
  duration: true,
  billableDuration: true,
  disposition: true,
  failureReason: true,
  hangupSource: true,
  interestLevel: true,
  customerIntent: true,
  objections: true,
  questionsAsked: true,
  summary: true,
  sentiment: true,
  requiresHumanFollowup: true,
  humanFollowupReason: true,
  recordingUrl: true,
  recordingSid: true,
  transcriptUrl: true,
  transcriptText: true,
  transcriptSegments: true,
  sheetsSynced: true,
  sheetsSyncAt: true,
  sheetsSyncStatus: true,
  sheetsSyncError: true,
  sheetsRowIndex: true,
});

export const createCallbackSchema = callbackSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  reminderSent: true,
  reminderSentAt: true,
  sourceCallId: true,
  resultCallId: true,
  completedAt: true,
  outcome: true,
});

export const createIntegrationSchema = integrationSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  lastSyncAt: true,
  lastSyncStatus: true,
  lastSyncError: true,
});

export const createSuppressionSchema = suppressionListSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const createConsentSchema = consentRecordSchema.omit({
  id: true,
  createdAt: true,
  updatedAt: true,
  grantedAt: true,
  revokedAt: true,
});

// ============================================
// QUERY/PAGINATION SCHEMAS
// ============================================

export const paginationSchema = z.object({
  page: z.number().int().min(1).default(1),
  pageSize: z.number().int().min(1).max(100).default(20),
  sortBy: z.string().max(50).optional(),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
});

export const customerFiltersSchema = z.object({
  status: customerStatusSchema.optional(),
  interestLevel: interestLevelSchema.optional(),
  language: languageSchema.optional(),
  search: z.string().max(100).optional(),
  hasCallback: z.boolean().optional(),
  doNotCall: z.boolean().optional(),
  dateFrom: dateSchema.optional(),
  dateTo: dateSchema.optional(),
});

export const campaignFiltersSchema = z.object({
  status: campaignStatusSchema.optional(),
  search: z.string().max(100).optional(),
  dateFrom: dateSchema.optional(),
  dateTo: dateSchema.optional(),
});

export const callFiltersSchema = z.object({
  status: callStatusSchema.optional(),
  direction: callDirectionSchema.optional(),
  interestLevel: interestLevelSchema.optional(),
  dateFrom: dateSchema.optional(),
  dateTo: dateSchema.optional(),
  campaignId: cuidSchema.optional(),
  customerId: cuidSchema.optional(),
});

// ============================================
// BULK OPERATIONS SCHEMAS
// ============================================

export const bulkCustomerImportSchema = z.object({
  customers: z.array(createCustomerSchema).min(1).max(5000),
  skipDuplicates: z.boolean().default(true),
  updateExisting: z.boolean().default(false),
});

export const bulkCampaignActionSchema = z.object({
  campaignIds: z.array(cuidSchema).min(1).max(100),
  action: z.enum(['start', 'pause', 'stop', 'delete']),
});

export const bulkCustomerActionSchema = z.object({
  customerIds: z.array(cuidSchema).min(1).max(1000),
  action: z.enum(['add_to_campaign', 'remove_from_campaign', 'mark_do_not_call', 'schedule_callback', 'delete']),
  campaignId: cuidSchema.optional(),
  callbackDate: dateTimeSchema.optional(),
});

// ============================================
// EXPORT TYPES
// ============================================

export type UserInput = z.infer<typeof createUserSchema>;
export type UserUpdate = z.infer<typeof updateUserSchema>;
export type OrganizationInput = z.infer<typeof createOrganizationSchema>;
export type OrganizationUpdate = z.infer<typeof updateOrganizationSchema>;
export type CustomerInput = z.infer<typeof createCustomerSchema>;
export type CustomerUpdate = z.infer<typeof updateCustomerSchema>;
export type CampaignInput = z.infer<typeof createCampaignSchema>;
export type CampaignUpdate = z.infer<typeof updateCampaignSchema>;
export type CallInput = z.infer<typeof createCallSchema>;
export type CallbackInput = z.infer<typeof createCallbackSchema>;
export type IntegrationInput = z.infer<typeof createIntegrationSchema>;
export type SuppressionInput = z.infer<typeof createSuppressionSchema>;
export type ConsentInput = z.infer<typeof createConsentSchema>;
export type SchemaPaginationParams = z.infer<typeof paginationSchema>;
export type CustomerFilters = z.infer<typeof customerFiltersSchema>;
export type CampaignFilters = z.infer<typeof campaignFiltersSchema>;
export type CallFilters = z.infer<typeof callFiltersSchema>;
export type BulkCustomerImport = z.infer<typeof bulkCustomerImportSchema>;
export type BulkCampaignAction = z.infer<typeof bulkCampaignActionSchema>;
export type BulkCustomerAction = z.infer<typeof bulkCustomerActionSchema>;