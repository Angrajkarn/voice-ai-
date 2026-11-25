# Campaign schemas

from datetime import datetime
from uuid import UUID

from app.models.enums import CampaignStatus
from pydantic import BaseModel, Field, field_validator


class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    purpose: str = Field(..., min_length=1, max_length=1000)
    ai_instructions: str = Field(..., min_length=1, max_length=10000)
    opening_script: str = Field(..., min_length=1, max_length=2000)
    knowledge_base: str | None = Field(None, max_length=20000)
    voice_id: str = Field(default="Google.en-IN-Wavenet-D", min_length=1, max_length=80)
    language: str = Field(default="en-IN", pattern=r'^(en-IN|hi-IN|hinglish|en-US|en-GB)$')
    supported_languages: list[str] = Field(default=["en-IN", "hi-IN", "hinglish"], min_length=1)
    max_calls_per_day: int = Field(default=100, ge=1, le=10000)
    max_retry_attempts: int = Field(default=3, ge=0, le=10)
    delay_between_calls: int = Field(default=30, ge=0, le=3600)
    calling_window_start: str = Field(default="09:00", pattern=r'^([01]\d|2[0-3]):([0-5]\d)$')
    calling_window_end: str = Field(default="18:00", pattern=r'^([01]\d|2[0-3]):([0-5]\d)$')
    calling_timezone: str = Field(default="Asia/Kolkata", pattern=r'^[A-Za-z]+\/[A-Za-z_]+$')
    skip_weekends: bool = True
    skip_holidays: bool = False
    allow_callbacks: bool = True
    callback_window_start: str = Field(default="09:00", pattern=r'^([01]\d|2[0-3]):([0-5]\d)$')
    callback_window_end: str = Field(default="18:00", pattern=r'^([01]\d|2[0-3]):([0-5]\d)$')
    max_callback_days: int = Field(default=7, ge=1, le=90)
    sheets_sync_enabled: bool = False
    sheets_spreadsheet_id: str | None = Field(None, max_length=100)
    sheets_sheet_name: str = Field(default="Calls", min_length=1, max_length=100)
    sheets_auto_sync: bool = True

    @field_validator("voice_id")
    @classmethod
    def validate_twilio_voice(cls, value: str) -> str:
        allowed = {*(f"Google.en-IN-Wavenet-{x}" for x in "ABCDEF"), *(f"Google.hi-IN-Wavenet-{x}" for x in "ABCDEF"), "Polly.Aditi", "Polly.Kajal-Neural", "Polly.Raveena", "Polly.Joanna", "Polly.Matthew", "Polly.Amy", "Polly.Brian"}
        if value not in allowed:
            raise ValueError("Choose a supported Twilio voice from the voice selector.")
        return value
    @field_validator('calling_window_end')
    @classmethod
    def validate_window(cls, v, info):
        if 'calling_window_start' in info.data:
            start = info.data['calling_window_start']
            if v <= start:
                raise ValueError('calling_window_end must be after calling_window_start')
        if 'callback_window_start' in info.data and 'callback_window_end' in info.data:
            cb_start = info.data['callback_window_start']
            cb_end = info.data['callback_window_end']
            if cb_end <= cb_start:
                raise ValueError('callback_window_end must be after callback_window_start')
        return v


class CampaignCreate(CampaignBase):
    customer_ids: list[UUID] = Field(default_factory=list, max_length=1000)


class CampaignUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    purpose: str | None = Field(None, min_length=1, max_length=1000)
    ai_instructions: str | None = Field(None, min_length=1, max_length=10000)
    opening_script: str | None = Field(None, min_length=1, max_length=2000)
    knowledge_base: str | None = Field(None, max_length=20000)
    voice_id: str | None = Field(None, min_length=1, max_length=80)
    language: str | None = Field(None, pattern=r'^(en-IN|hi-IN|hinglish|en-US|en-GB)$')
    supported_languages: list[str] | None = None
    max_calls_per_day: int | None = Field(None, ge=1, le=10000)
    max_retry_attempts: int | None = Field(None, ge=0, le=10)
    delay_between_calls: int | None = Field(None, ge=0, le=3600)
    calling_window_start: str | None = Field(None, pattern=r'^([01]\d|2[0-3]):([0-5]\d)$')
    calling_window_end: str | None = Field(None, pattern=r'^([01]\d|2[0-3]):([0-5]\d)$')
    calling_timezone: str | None = Field(None, pattern=r'^[A-Za-z]+\/[A-Za-z_]+$')
    skip_weekends: bool | None = None
    skip_holidays: bool | None = None
    allow_callbacks: bool | None = None
    callback_window_start: str | None = Field(None, pattern=r'^([01]\d|2[0-3]):([0-5]\d)$')
    callback_window_end: str | None = Field(None, pattern=r'^([01]\d|2[0-3]):([0-5]\d)$')
    max_callback_days: int | None = Field(None, ge=1, le=90)
    sheets_sync_enabled: bool | None = None
    sheets_spreadsheet_id: str | None = Field(None, max_length=100)
    sheets_sheet_name: str | None = Field(None, min_length=1, max_length=100)
    sheets_auto_sync: bool | None = None
    status: CampaignStatus | None = None
    @field_validator("voice_id")
    @classmethod
    def validate_update_twilio_voice(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {*(f"Google.en-IN-Wavenet-{x}" for x in "ABCDEF"), *(f"Google.hi-IN-Wavenet-{x}" for x in "ABCDEF"), "Polly.Aditi", "Polly.Kajal-Neural", "Polly.Raveena", "Polly.Joanna", "Polly.Matthew", "Polly.Amy", "Polly.Brian"}
        if value not in allowed:
            raise ValueError("Choose a supported Twilio voice from the voice selector.")
        return value


class CampaignResponse(CampaignBase):
    id: UUID
    status: CampaignStatus
    started_at: datetime | None
    paused_at: datetime | None
    completed_at: datetime | None
    stopped_at: datetime | None
    total_customers: int
    completed_calls: int
    failed_calls: int
    interested_count: int
    callback_count: int
    opt_out_count: int
    organization_id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignValidate(BaseModel):
    campaign_id: UUID


class CampaignBulkAction(BaseModel):
    campaign_ids: list[UUID] = Field(..., min_length=1, max_length=100)
    action: str = Field(..., pattern=r'^(start|pause|stop|delete)$')


class CampaignMetrics(BaseModel):
    total_customers: int
    total_calls: int
    completed_calls: int
    failed_calls: int
    answered_calls: int
    interested_count: int
    callback_count: int
    opt_out_count: int
    average_duration: float
    success_rate: float
    answer_rate: float