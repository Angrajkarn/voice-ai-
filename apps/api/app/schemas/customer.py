# Customer schemas

from datetime import datetime
from typing import Any
from uuid import UUID

from app.models.enums import CustomerStatus, InterestLevel
from pydantic import BaseModel, EmailStr, Field


class CustomerBase(BaseModel):
    external_id: str | None = Field(None, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$')  # E.164 format
    phone_raw: str | None = Field(None, max_length=50)
    company: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=100)
    language: str = Field(default="en-IN", pattern=r'^(en-IN|hi-IN|hinglish|en-US|en-GB)$')
    timezone: str = Field(default="Asia/Kolkata", pattern=r'^[A-Za-z]+\/[A-Za-z_]+$')
    tags: list[str] = Field(default_factory=list)
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    max_call_attempts: int = Field(default=3, ge=1, le=10)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    external_id: str | None = Field(None, max_length=100)
    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, pattern=r'^\+[1-9]\d{1,14}$')
    phone_raw: str | None = Field(None, max_length=50)
    company: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=100)
    language: str | None = Field(None, pattern=r'^(en-IN|hi-IN|hinglish|en-US|en-GB)$')
    timezone: str | None = Field(None, pattern=r'^[A-Za-z]+\/[A-Za-z_]+$')
    tags: list[str] | None = None
    custom_fields: dict[str, Any] | None = None
    status: CustomerStatus | None = None
    interest_level: InterestLevel | None = None
    max_call_attempts: int | None = Field(None, ge=1, le=10)
    do_not_call: bool | None = None


class CustomerResponse(CustomerBase):
    id: UUID
    status: CustomerStatus
    interest_level: InterestLevel
    call_attempts: int
    last_call_at: datetime | None
    next_callback_at: datetime | None
    last_call_status: str | None
    last_call_duration: int | None
    final_disposition: str | None
    do_not_call: bool
    opted_out_at: datetime | None
    opt_out_reason: str | None
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerImport(BaseModel):
    customers: list[CustomerCreate] = Field(..., min_length=1, max_length=5000)
    skip_duplicates: bool = True
    update_existing: bool = False


class CustomerBulkAction(BaseModel):
    customer_ids: list[UUID] = Field(..., min_length=1, max_length=1000)
    action: str = Field(..., pattern=r'^(add_to_campaign|remove_from_campaign|mark_do_not_call|schedule_callback|delete)$')
    campaign_id: UUID | None = None
    callback_date: datetime | None = None