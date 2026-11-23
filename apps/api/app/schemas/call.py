# Call schemas

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.enums import CallStatus, CallDirection, InterestLevel, SyncStatus


class TranscriptSegment(BaseModel):
    speaker: str = Field(..., pattern=r'^(ai|customer|system)$')
    text: str
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1)
    language: str = Field(default="en-IN")


class CallBase(BaseModel):
    call_sid: Optional[str] = Field(None, max_length=50)
    direction: CallDirection = CallDirection.OUTBOUND
    status: CallStatus = CallStatus.QUEUED
    from_number: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$')
    to_number: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$')


class CallCreate(CallBase):
    campaign_id: UUID
    customer_id: UUID
    agent_id: Optional[UUID] = None


class CallUpdate(BaseModel):
    status: Optional[CallStatus] = None
    initiated_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=0)
    billable_duration: Optional[int] = Field(None, ge=0)
    disposition: Optional[str] = Field(None, max_length=50)
    failure_reason: Optional[str] = None
    hangup_source: Optional[str] = Field(None, max_length=50)
    interest_level: Optional[InterestLevel] = None
    customer_intent: Optional[str] = None
    objections: Optional[List[str]] = None
    questions_asked: Optional[List[str]] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = Field(None, pattern=r'^(positive|neutral|negative)$')
    requires_human_followup: Optional[bool] = None
    human_followup_reason: Optional[str] = None
    recording_url: Optional[str] = None
    recording_sid: Optional[str] = None
    transcript_url: Optional[str] = None
    transcript_text: Optional[str] = None
    transcript_segments: Optional[List[TranscriptSegment]] = None
    sheets_synced: Optional[bool] = None
    sheets_sync_at: Optional[datetime] = None
    sheets_sync_status: Optional[SyncStatus] = None
    sheets_sync_error: Optional[str] = None
    sheets_row_index: Optional[int] = None


class CallResponse(CallBase):
    id: UUID
    queued_at: datetime
    initiated_at: Optional[datetime]
    answered_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration: Optional[int]
    billable_duration: Optional[int]
    disposition: Optional[str]
    failure_reason: Optional[str]
    hangup_source: Optional[str]
    interest_level: InterestLevel
    customer_intent: Optional[str]
    objections: List[str]
    questions_asked: List[str]
    summary: Optional[str]
    sentiment: Optional[str]
    requires_human_followup: bool
    human_followup_reason: Optional[str]
    recording_url: Optional[str]
    recording_sid: Optional[str]
    transcript_url: Optional[str]
    transcript_text: Optional[str]
    transcript_segments: List[TranscriptSegment]
    sheets_synced: bool
    sheets_sync_at: Optional[datetime]
    sheets_sync_status: SyncStatus
    sheets_sync_error: Optional[str]
    sheets_row_index: Optional[int]
    campaign_id: UUID
    customer_id: UUID
    agent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CallTranscriptResponse(BaseModel):
    id: UUID
    call_id: UUID
    full_text: str
    segments: List[TranscriptSegment]
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
    drive_file_id: Optional[str]
    drive_synced_at: Optional[datetime]
    drive_sync_status: SyncStatus
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True