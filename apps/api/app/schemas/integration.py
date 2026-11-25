# Integration schemas

from datetime import datetime
from typing import Any
from uuid import UUID

from app.models.enums import IntegrationType, SyncStatus
from pydantic import BaseModel, Field, field_serializer


class IntegrationBase(BaseModel):
    type: IntegrationType
    name: str = Field(..., min_length=1, max_length=100)
    config: dict[str, Any] = Field(default_factory=dict)


class IntegrationCreate(IntegrationBase):
    campaign_id: UUID | None = None


class IntegrationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    config: dict[str, Any] | None = None
    is_active: bool | None = None


class IntegrationResponse(IntegrationBase):
    id: UUID
    is_active: bool
    last_sync_at: datetime | None
    last_sync_status: SyncStatus
    last_sync_error: str | None
    organization_id: UUID
    campaign_id: UUID | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("config")
    def redact_config(self, config: dict[str, Any]) -> dict[str, Any]:
        sensitive = {"auth_token", "client_secret", "refresh_token", "private_key", "api_key", "token"}
        def redact(value: Any) -> Any:
            if isinstance(value, dict):
                return {key: ("********" if key.lower() in sensitive and item else redact(item)) for key, item in value.items()}
            if isinstance(value, list):
                return [redact(item) for item in value]
            return value
        return redact(config or {})
    class Config:
        from_attributes = True


class IntegrationTest(BaseModel):
    integration_id: UUID


class GoogleSheetsConfig(BaseModel):
    spreadsheet_id: str
    sheet_name: str = "Calls"
    credentials: dict[str, str]  # client_email, private_key, project_id


class GoogleDriveConfig(BaseModel):
    folder_id: str | None = None
    credentials: dict[str, str]


class TwilioConfig(BaseModel):
    account_sid: str
    auth_token: str
    phone_number: str
    application_sid: str | None = None


class OpenAIConfig(BaseModel):
    api_key: str
    model: str = "gpt-4o"
    realtime_model: str = "gpt-4o-realtime-preview"
    tts_model: str = "tts-1"
    tts_voice: str = "alloy"


class N8NConfig(BaseModel):
    webhook_url: str
    api_key: str | None = None