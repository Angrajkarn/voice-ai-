# Customer schemas

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.enums import CustomerStatus, InterestLevel
import re


class CustomerBase(BaseModel):
    external_id: Optional[str] = Field(None, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$')  # E.164 format
    phone_raw: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    language: str = Field(default="en-IN", pattern=r'^(en-IN|hi-IN|hinglish|en-US|en-GB)$')
    timezone: str = Field(default="Asia/Kolkata", pattern=r'^[A-Za-z]+\/[A-Za-z_]+$')
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    max_call_attempts: int = Field(default=3, ge=1, le=10)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    external_id: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+[1-9]\d{1,14}$')
    phone_raw: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    language: Optional[str] = Field(None, pattern=r'^(en-IN|hi-IN|hinglish|en-US|en-GB)$')
    timezone: Optional[str] = Field(None, pattern=r'^[A-Za-z]+\/[A-Za-z_]+$')
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    status: Optional[CustomerStatus] = None
    interest_level: Optional[InterestLevel] = None
    max_call_attempts: Optional[int] = Field(None, ge=1, le=10)
    do_not_call: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: UUID
    status: CustomerStatus
    interest_level: InterestLevel
    call_attempts: int
    last_call_at: Optional[datetime]
    next_callback_at: Optional[datetime]
    last_call_status: Optional[str]
    last_call_duration: Optional[int]
    final_disposition: Optional[str]
    do_not_call: bool
    opted_out_at: Optional[datetime]
    opt_out_reason: Optional[str]
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerImport(BaseModel):
    customers: List[CustomerCreate] = Field(..., min_length=1, max_length=5000)
    skip_duplicates: bool = True
    update_existing: bool = False


class CustomerBulkAction(BaseModel):
    customer_ids: List[UUID] = Field(..., min_length=1, max_length=1000)
    action: str = Field(..., pattern=r'^(add_to_campaign|remove_from_campaign|mark_do_not_call|schedule_callback|delete)$')
    campaign_id: Optional[UUID] = None
    callback_date: Optional[datetime] = None