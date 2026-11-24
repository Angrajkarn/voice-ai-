# Callback schemas

from datetime import datetime
from uuid import UUID

from app.models.enums import CallbackStatus
from pydantic import BaseModel, Field


class CallbackBase(BaseModel):
    status: CallbackStatus = CallbackStatus.SCHEDULED
    scheduled_at: datetime
    scheduled_timezone: str = Field(default="Asia/Kolkata", pattern=r'^[A-Za-z]+\/[A-Za-z_]+$')
    customer_notes: str | None = None
    ai_notes: str | None = None


class CallbackCreate(CallbackBase):
    campaign_id: UUID
    customer_id: UUID
    source_call_id: UUID | None = None
    assignee_id: UUID | None = None


class CallbackUpdate(BaseModel):
    status: CallbackStatus | None = None
    scheduled_at: datetime | None = None
    scheduled_timezone: str | None = Field(None, pattern=r'^[A-Za-z]+\/[A-Za-z_]+$')
    reminder_sent: bool | None = None
    reminder_sent_at: datetime | None = None
    customer_notes: str | None = None
    ai_notes: str | None = None
    assignee_id: UUID | None = None
    result_call_id: UUID | None = None
    completed_at: datetime | None = None
    outcome: str | None = Field(None, max_length=500)


class CallbackResponse(CallbackBase):
    id: UUID
    reminder_sent: bool
    reminder_sent_at: datetime | None
    source_call_id: UUID | None
    campaign_id: UUID
    customer_id: UUID
    assignee_id: UUID | None
    result_call_id: UUID | None
    completed_at: datetime | None
    outcome: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CallbackComplete(BaseModel):
    outcome: str = Field(..., min_length=1, max_length=500)