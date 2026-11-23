# Enums for the AI Voice Calling Platform

import enum


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    AGENT = "AGENT"
    VIEWER = "VIEWER"


class OrganizationPlan(str, enum.Enum):
    FREE = "FREE"
    STARTER = "STARTER"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"


class CallStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    INITIATING = "INITIATING"
    RINGING = "RINGING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BUSY = "BUSY"
    NO_ANSWER = "NO_ANSWER"
    VOICEMAIL = "VOICEMAIL"
    INVALID_NUMBER = "INVALID_NUMBER"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class CallDirection(str, enum.Enum):
    OUTBOUND = "OUTBOUND"
    INBOUND = "INBOUND"


class CustomerStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    HOT_LEAD = "HOT_LEAD"
    WARM_LEAD = "WARM_LEAD"
    COLD_LEAD = "COLD_LEAD"
    NOT_INTERESTED = "NOT_INTERESTED"
    CALLBACK_REQUESTED = "CALLBACK_REQUESTED"
    DO_NOT_CALL = "DO_NOT_CALL"
    INVALID_NUMBER = "INVALID_NUMBER"
    OPTED_OUT = "OPTED_OUT"


class InterestLevel(str, enum.Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    UNKNOWN = "UNKNOWN"


class SyncStatus(str, enum.Enum):
    PENDING = "PENDING"
    SYNCED = "SYNCED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class IntegrationType(str, enum.Enum):
    GOOGLE_SHEETS = "GOOGLE_SHEETS"
    GOOGLE_DRIVE = "GOOGLE_DRIVE"
    TWILIO = "TWILIO"
    OPENAI = "OPENAI"
    N8N = "N8N"


class NotificationType(str, enum.Enum):
    CALL_COMPLETED = "CALL_COMPLETED"
    HOT_LEAD = "HOT_LEAD"
    CALLBACK_SCHEDULED = "CALLBACK_SCHEDULED"
    HUMAN_FOLLOWUP_REQUIRED = "HUMAN_FOLLOWUP_REQUIRED"
    OPT_OUT = "OPT_OUT"
    CAMPAIGN_COMPLETED = "CAMPAIGN_COMPLETED"
    SYNC_FAILED = "SYNC_FAILED"
    ERROR = "ERROR"


class ConsentStatus(str, enum.Enum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    PENDING = "PENDING"
    REVOKED = "REVOKED"


class CallbackStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    NO_ANSWER = "NO_ANSWER"


class SuppressionReason(str, enum.Enum):
    OPT_OUT = "OPT_OUT"
    DND = "DND"
    INVALID = "INVALID"
    MANUAL = "MANUAL"


class SuppressionSource(str, enum.Enum):
    CAMPAIGN = "CAMPAIGN"
    MANUAL = "MANUAL"
    IMPORT = "IMPORT"
    WEBHOOK = "WEBHOOK"


class ConsentMethod(str, enum.Enum):
    VERBAL = "VERBAL"
    SMS = "SMS"
    EMAIL = "EMAIL"
    WEB_FORM = "WEB_FORM"
    CALL_RECORDING = "CALL_RECORDING"