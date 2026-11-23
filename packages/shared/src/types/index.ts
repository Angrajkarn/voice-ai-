// Shared TypeScript types for AI Voice Calling Platform

export type UserRole = 'SUPER_ADMIN' | 'ADMIN' | 'MANAGER' | 'AGENT' | 'VIEWER';
export type OrganizationPlan = 'FREE' | 'STARTER' | 'PROFESSIONAL' | 'ENTERPRISE';
export type CampaignStatus = 'DRAFT' | 'READY' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'STOPPED';
export type CallStatus = 'QUEUED' | 'INITIATING' | 'RINGING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'BUSY' | 'NO_ANSWER' | 'VOICEMAIL' | 'INVALID_NUMBER' | 'BLOCKED' | 'CANCELLED';
export type CallDirection = 'OUTBOUND' | 'INBOUND';
export type CustomerStatus = 'NEW' | 'CONTACTED' | 'HOT_LEAD' | 'WARM_LEAD' | 'COLD_LEAD' | 'NOT_INTERESTED' | 'CALLBACK_REQUESTED' | 'DO_NOT_CALL' | 'INVALID_NUMBER' | 'OPTED_OUT';
export type InterestLevel = 'HOT' | 'WARM' | 'COLD' | 'UNKNOWN';
export type SyncStatus = 'PENDING' | 'SYNCED' | 'FAILED' | 'RETRYING';
export type IntegrationType = 'GOOGLE_SHEETS' | 'GOOGLE_DRIVE' | 'TWILIO' | 'OPENAI' | 'N8N';
export type NotificationType = 'CALL_COMPLETED' | 'HOT_LEAD' | 'CALLBACK_SCHEDULED' | 'HUMAN_FOLLOWUP_REQUIRED' | 'OPT_OUT' | 'CAMPAIGN_COMPLETED' | 'SYNC_FAILED' | 'ERROR';
export type ConsentStatus = 'GRANTED' | 'DENIED' | 'PENDING' | 'REVOKED';

export interface User {
  id: string;
  email: string;
  name: string | null;
  avatarUrl: string | null;
  role: UserRole;
  isActive: boolean;
  lastLoginAt: Date | null;
  createdAt: Date;
  updatedAt: Date;
  organizationId: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  logoUrl: string | null;
  plan: OrganizationPlan;
  planExpiresAt: Date | null;
  settings: Record<string, unknown>;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Customer {
  id: string;
  externalId: string | null;
  firstName: string;
  lastName: string;
  email: string | null;
  phone: string; // E.164 format
  phoneRaw: string | null;
  company: string | null;
  location: string | null;
  language: string;
  timezone: string;
  tags: string[];
  customFields: Record<string, unknown>;
  status: CustomerStatus;
  interestLevel: InterestLevel;
  callAttempts: number;
  maxCallAttempts: number;
  lastCallAt: Date | null;
  nextCallbackAt: Date | null;
  lastCallStatus: CallStatus | null;
  lastCallDuration: number | null;
  finalDisposition: string | null;
  doNotCall: boolean;
  optedOutAt: Date | null;
  optOutReason: string | null;
  organizationId: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Campaign {
  id: string;
  name: string;
  description: string | null;
  purpose: string;
  aiInstructions: string;
  openingScript: string;
  knowledgeBase: string;
  voiceId: string;
  language: string;
  supportedLanguages: string[];
  maxCallsPerDay: number;
  maxRetryAttempts: number;
  delayBetweenCalls: number;
  callingWindowStart: string;
  callingWindowEnd: string;
  callingTimezone: string;
  skipWeekends: boolean;
  skipHolidays: boolean;
  allowCallbacks: boolean;
  callbackWindowStart: string;
  callbackWindowEnd: string;
  maxCallbackDays: number;
  sheetsSyncEnabled: boolean;
  sheetsSpreadsheetId: string | null;
  sheetsSheetName: string;
  sheetsAutoSync: boolean;
  status: CampaignStatus;
  startedAt: Date | null;
  pausedAt: Date | null;
  completedAt: Date | null;
  stoppedAt: Date | null;
  totalCustomers: number;
  completedCalls: number;
  failedCalls: number;
  interestedCount: number;
  callbackCount: number;
  optOutCount: number;
  organizationId: string;
  ownerId: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Call {
  id: string;
  callSid: string | null;
  direction: CallDirection;
  status: CallStatus;
  fromNumber: string;
  toNumber: string;
  queuedAt: Date;
  initiatedAt: Date | null;
  answeredAt: Date | null;
  endedAt: Date | null;
  duration: number | null;
  billableDuration: number | null;
  disposition: string | null;
  failureReason: string | null;
  hangupSource: string | null;
  interestLevel: InterestLevel;
  customerIntent: string | null;
  objections: string[];
  questionsAsked: string[];
  summary: string | null;
  sentiment: string | null;
  requiresHumanFollowup: boolean;
  humanFollowupReason: string | null;
  recordingUrl: string | null;
  recordingSid: string | null;
  transcriptUrl: string | null;
  transcriptText: string | null;
  transcriptSegments: TranscriptSegment[];
  sheetsSynced: boolean;
  sheetsSyncAt: Date | null;
  sheetsSyncStatus: SyncStatus;
  sheetsSyncError: string | null;
  sheetsRowIndex: number | null;
  campaignId: string;
  customerId: string;
  agentId: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface TranscriptSegment {
  speaker: 'ai' | 'customer' | 'system';
  text: string;
  startTime: number;
  endTime: number;
  confidence: number;
  language: string;
}

export interface Callback {
  id: string;
  status: 'SCHEDULED' | 'COMPLETED' | 'CANCELLED' | 'FAILED' | 'NO_ANSWER';
  scheduledAt: Date;
  scheduledTimezone: string;
  reminderSent: boolean;
  reminderSentAt: Date | null;
  sourceCallId: string | null;
  customerNotes: string | null;
  aiNotes: string | null;
  campaignId: string;
  customerId: string;
  assigneeId: string | null;
  resultCallId: string | null;
  completedAt: Date | null;
  outcome: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface Integration {
  id: string;
  type: IntegrationType;
  name: string;
  config: Record<string, unknown>;
  isActive: boolean;
  lastSyncAt: Date | null;
  lastSyncStatus: SyncStatus;
  lastSyncError: string | null;
  organizationId: string;
  campaignId: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface SyncLog {
  id: string;
  integrationId: string;
  operation: string;
  entityType: string;
  entityId: string;
  status: SyncStatus;
  error: string | null;
  requestData: Record<string, unknown> | null;
  responseData: Record<string, unknown> | null;
  retryCount: number;
  completedAt: Date | null;
  createdAt: Date;
}

export interface AutomationLog {
  id: string;
  campaignId: string;
  triggerType: string;
  triggerData: Record<string, unknown>;
  actionType: string;
  actionData: Record<string, unknown>;
  status: 'PENDING' | 'COMPLETED' | 'FAILED';
  error: string | null;
  completedAt: Date | null;
  createdAt: Date;
}

export interface SuppressionList {
  id: string;
  phone: string;
  reason: 'OPT_OUT' | 'DND' | 'INVALID' | 'MANUAL';
  source: 'CAMPAIGN' | 'MANUAL' | 'IMPORT' | 'WEBHOOK';
  campaignId: string | null;
  organizationId: string;
  customerId: string | null;
  expiresAt: Date | null;
  isActive: boolean;
  addedBy: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface ConsentRecord {
  id: string;
  phone: string;
  status: ConsentStatus;
  method: 'VERBAL' | 'SMS' | 'EMAIL' | 'WEB_FORM' | 'CALL_RECORDING';
  proofUrl: string | null;
  proofExpiresAt: Date | null;
  campaignId: string | null;
  customerId: string | null;
  organizationId: string;
  grantedAt: Date | null;
  revokedAt: Date | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  data: Record<string, unknown>;
  isRead: boolean;
  readAt: Date | null;
  userId: string;
  organizationId: string;
  campaignId: string | null;
  callId: string | null;
  createdAt: Date;
}

export interface AuditLog {
  id: string;
  action: string;
  entityType: string;
  entityId: string;
  oldData: Record<string, unknown> | null;
  newData: Record<string, unknown> | null;
  metadata: Record<string, unknown>;
  userId: string | null;
  organizationId: string;
  createdAt: Date;
}

// API Response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface DashboardMetrics {
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
}

// Campaign validation
export interface CampaignValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

// Call queue types
export interface CallQueueJob {
  id: string;
  campaignId: string;
  customerId: string;
  priority: number;
  scheduledAt: Date;
  attempts: number;
  maxAttempts: number;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
}

// AI Agent types
export interface AIAgentConfig {
  instructions: string;
  openingScript: string;
  knowledgeBase: string;
  voiceId: string;
  language: string;
  supportedLanguages: string[];
  temperature: number;
  maxTokens: number;
}

export interface ConversationContext {
  campaignId: string;
  customerId: string;
  customerName: string;
  customerPhone: string;
  callId: string;
  language: string;
  history: ConversationMessage[];
}

export interface ConversationMessage {
  role: 'system' | 'assistant' | 'user';
  content: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

// Google Sheets types
export interface SheetsRowData {
  customerId: string;
  name: string;
  phone: string;
  callStatus: string;
  callDuration: number;
  callDate: string;
  aiSummary: string;
  fullTranscript: string;
  interestLevel: string;
  customerIntent: string;
  objection: string;
  callbackRequired: boolean;
  callbackDate: string | null;
  finalOutcome: string;
  recordingUrl: string;
  attempts: number;
  lastUpdated: string;
}

export interface SheetsSyncConfig {
  spreadsheetId: string;
  sheetName: string;
  credentials: GoogleCredentials;
  columnMapping: Record<string, string>;
}

export interface GoogleCredentials {
  clientEmail: string;
  privateKey: string;
  projectId: string;
}

// Twilio types
export interface TwilioConfig {
  accountSid: string;
  authToken: string;
  phoneNumber: string;
  applicationSid?: string;
}

export interface TwilioWebhookPayload {
  CallSid: string;
  AccountSid: string;
  From: string;
  To: string;
  CallStatus: string;
  Direction: string;
  Duration?: string;
  RecordingUrl?: string;
  RecordingSid?: string;
  TranscriptionText?: string;
  TranscriptionSid?: string;
  Digits?: string;
  SpeechResult?: string;
  Confidence?: string;
}

// OpenAI types
export interface OpenAIConfig {
  apiKey: string;
  model: string;
  realtimeModel?: string;
  ttsModel?: string;
  ttsVoice?: string;
}

export interface RealtimeSessionConfig {
  model: string;
  voice: string;
  instructions: string;
  inputAudioFormat: 'pcm16' | 'g711_ulaw' | 'g711_alaw';
  outputAudioFormat: 'pcm16' | 'g711_ulaw' | 'g711_alaw';
  turnDetection: {
    type: 'server_vad';
    threshold: number;
    prefixPaddingMs: number;
    silenceDurationMs: number;
  };
  tools: RealtimeTool[];
}

export interface RealtimeTool {
  type: 'function';
  name: string;
  description: string;
  parameters: Record<string, unknown>;
}

// Webhook types
export interface WebhookEvent {
  id: string;
  type: string;
  data: Record<string, unknown>;
  timestamp: Date;
  signature: string;
}

// File upload types
export interface UploadedFile {
  filename: string;
  mimetype: string;
  size: number;
  buffer: Buffer;
  path?: string;
}

// Import/Export types
export interface CustomerImportResult {
  successful: number;
  failed: number;
  duplicates: number;
  errors: ImportError[];
}

export interface ImportError {
  row: number;
  field: string;
  value: string;
  error: string;
}

// Analytics types
export interface CallAnalytics {
  date: string;
  totalCalls: number;
  completedCalls: number;
  failedCalls: number;
  answeredCalls: number;
  busyCalls: number;
  noAnswerCalls: number;
  voicemailCalls: number;
  averageDuration: number;
  totalDuration: number;
  hotLeads: number;
  warmLeads: number;
  coldLeads: number;
  callbacksScheduled: number;
  optOuts: number;
}

export interface CampaignAnalytics {
  campaignId: string;
  campaignName: string;
  period: 'daily' | 'weekly' | 'monthly';
  data: CallAnalytics[];
  summary: {
    totalCalls: number;
    successRate: number;
    answerRate: number;
    conversionRate: number;
    averageDuration: number;
    totalInterested: number;
    totalCallbacks: number;
    totalOptOuts: number;
  };
}