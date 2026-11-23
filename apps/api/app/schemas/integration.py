# Integration schemas

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.enums import IntegrationType, SyncStatus


class IntegrationBase(BaseModel):
    type: IntegrationType
    name: str = Field(..., min_length=1, max_length=100)
    config: Dict[str, Any] = Field(default_factory=dict)


class IntegrationCreate(IntegrationBase):
    campaign_id: Optional[UUID] = None


class IntegrationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class IntegrationResponse(IntegrationBase):
    id: UUID
    is_active: bool
    last_sync_at: Optional[datetime]
    last_sync_status: SyncStatus
    last_sync_error: Optional[str]
    organization_id: UUID
    campaign_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IntegrationTest(BaseModel):
    integration_id: UUID


class GoogleSheetsConfig(BaseModel):
    spreadsheet_id: str
    sheet_name: str = "Calls"
    credentials: Dict[str, str]  # client_email, private_key, project_id


class GoogleDriveConfig(BaseModel):
    folder_id: Optional[str] = None
    credentials: Dict[str, str]


class TwilioConfig(BaseModel):
    account_sid: str
    auth_token: str
    phone_number: str
    application_sid: Optional[str] = None


class OpenAIConfig(BaseModel):
    api_key: str
    model: str = "gpt-4o"
    realtime_model: str = "gpt-4o-realtime-preview"
    tts_model: str = "tts-1"
    tts_voice: str = "alloy"


class N8NConfig(BaseModel):
    webhook_url: str
    api_key: Optional[str] = None