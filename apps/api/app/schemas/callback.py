# Callback schemas

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.enums import CallbackStatus


class CallbackBase(BaseModel):
    status: CallbackStatus = CallbackStatus.SCHEDULED
    scheduled_at: datetime
    scheduled_timezone: str = Field(default="Asia/Kolkata", pattern=r'^[A-Za-z]+\/[A-Za-z_]+$')
    customer_notes: Optional[str] = None
    ai_notes: Optional[str] = None


class CallbackCreate(CallbackBase):
    campaign_id: UUID
    customer_id: UUID
    source_call_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None


class CallbackUpdate(BaseModel):
    status: Optional[CallbackStatus] = None
    scheduled_at: Optional[datetime] = None
    scheduled_timezone: Optional[str] = Field(None, pattern=r'^[A-Za-z]+\/[A-Za-z_]+$')
    reminder_sent: Optional[bool] = None
    reminder_sent_at: Optional[datetime] = None
    customer_notes: Optional[str] = None
    ai_notes: Optional[str] = None
    assignee_id: Optional[UUID] = None
    result_call_id: Optional[UUID] = None
    completed_at: Optional[datetime] = None
    outcome: Optional[str] = Field(None, max_length=500)


class CallbackResponse(CallbackBase):
    id: UUID
    reminder_sent: bool
    reminder_sent_at: Optional[datetime]
    source_call_id: Optional[UUID]
    campaign_id: UUID
    customer_id: UUID
    assignee_id: Optional[UUID]
    result_call_id: Optional[UUID]
    completed_at: Optional[datetime]
    outcome: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CallbackComplete(BaseModel):
    outcome: str = Field(..., min_length=1, max_length=500)