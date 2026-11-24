# Call schemas

from datetime import datetime
from uuid import UUID

from app.models.enums import CallDirection, CallStatus, InterestLevel, SyncStatus
from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    speaker: str = Field(..., pattern=r'^(ai|customer|system)$')
    text: str
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1)
    language: str = Field(default="en-IN")


class CallBase(BaseModel):
    call_sid: str | None = Field(None, max_length=50)
    direction: CallDirection = CallDirection.OUTBOUND
    status: CallStatus = CallStatus.QUEUED
    from_number: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$')
    to_number: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$')


class CallCreate(CallBase):
    campaign_id: UUID
    customer_id: UUID
    agent_id: UUID | None = None


class CallUpdate(BaseModel):
    status: CallStatus | None = None
    initiated_at: datetime | None = None
    answered_at: datetime | None = None
    ended_at: datetime | None = None
    duration: int | None = Field(None, ge=0)
    billable_duration: int | None = Field(None, ge=0)
    disposition: str | None = Field(None, max_length=50)
    failure_reason: str | None = None
    hangup_source: str | None = Field(None, max_length=50)
    interest_level: InterestLevel | None = None
    customer_intent: str | None = None
    objections: list[str] | None = None
    questions_asked: list[str] | None = None
    summary: str | None = None
    sentiment: str | None = Field(None, pattern=r'^(positive|neutral|negative)$')
    requires_human_followup: bool | None = None
    human_followup_reason: str | None = None
    recording_url: str | None = None
    recording_sid: str | None = None
    transcript_url: str | None = None
    transcript_text: str | None = None
    transcript_segments: list[TranscriptSegment] | None = None
    sheets_synced: bool | None = None
    sheets_sync_at: datetime | None = None
    sheets_sync_status: SyncStatus | None = None
    sheets_sync_error: str | None = None
    sheets_row_index: int | None = None


class CallResponse(CallBase):
    id: UUID
    queued_at: datetime
    initiated_at: datetime | None
    answered_at: datetime | None
    ended_at: datetime | None
    duration: int | None
    billable_duration: int | None
    disposition: str | None
    failure_reason: str | None
    hangup_source: str | None
    interest_level: InterestLevel
    customer_intent: str | None
    objections: list[str]
    questions_asked: list[str]
    summary: str | None
    sentiment: str | None
    requires_human_followup: bool
    human_followup_reason: str | None
    recording_url: str | None
    recording_sid: str | None
    transcript_url: str | None
    transcript_text: str | None
    transcript_segments: list[TranscriptSegment]
    sheets_synced: bool
    sheets_sync_at: datetime | None
    sheets_sync_status: SyncStatus
    sheets_sync_error: str | None
    sheets_row_index: int | None
    campaign_id: UUID
    customer_id: UUID
    agent_id: UUID | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CallTranscriptResponse(BaseModel):
    id: UUID
    call_id: UUID
    full_text: str
    segments: list[TranscriptSegment]
    language: str
    word_count: int
    duration: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CallRecordingResponse(BaseModel):
    id: UUID
    call_id: UUID
    url: str
    provider: str
    provider_id: str
    format: str
    duration: float
    size_bytes: int
    channels: int
    sample_rate: int
    drive_file_id: str | None
    drive_synced_at: datetime | None
    drive_sync_status: SyncStatus
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True