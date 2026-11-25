# Integration Service - Manages third-party integrations

import json

from openai import AsyncOpenAI
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from datetime import datetime
from typing import Any
from uuid import UUID

from app.models.enums import IntegrationType, SyncStatus
from app.core.crypto import decrypt_secret, encrypt_secret
from app.models.integration import Integration
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationUpdate,
)
from app.services.google_sheets_service import GoogleSheetsService
from app.services.openai_service import OpenAIService
from app.services.twilio_service import TwilioService
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession


class IntegrationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.twilio = TwilioService()
        self.google_sheets = GoogleSheetsService(db)
        self.openai = OpenAIService()

    async def create(self, data: IntegrationCreate, organization_id: UUID) -> Integration:
        payload = data.model_dump()
        config = dict(payload.get("config") or {})
        if payload["type"] == IntegrationType.TWILIO:
            if not config.get("account_sid", "").startswith("AC") or not config.get("auth_token") or not config.get("phone_number", "").startswith("+"):
                raise ValueError("Enter a valid Twilio Account SID, Auth Token and E.164 phone number.")
            config["auth_token"] = encrypt_secret(str(config["auth_token"]))
            payload["config"] = config
        integration = Integration(**payload, organization_id=organization_id)
        self.db.add(integration)
        await self.db.commit()
        await self.db.refresh(integration)
        return integration

    async def get_by_id(self, integration_id: UUID, organization_id: UUID) -> Integration | None:
        result = await self.db.execute(
            select(Integration).where(
                and_(
                    Integration.id == integration_id,
                    Integration.organization_id == organization_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list(self, organization_id: UUID, integration_type: IntegrationType | None = None) -> list[Integration]:
        query = select(Integration).where(Integration.organization_id == organization_id)
        if integration_type:
            query = query.where(Integration.type == integration_type)
        result = await self.db.execute(query.order_by(Integration.created_at.desc()))
        return list(result.scalars().all())

    async def update(self, integration_id: UUID, organization_id: UUID, data: IntegrationUpdate) -> Integration | None:
        integration = await self.get_by_id(integration_id, organization_id)
        if not integration:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if integration.type == IntegrationType.TWILIO and update_data.get("config") is not None:
            config = {**(integration.config or {}), **update_data["config"]}
            if config.get("auth_token") and not str(config["auth_token"]).startswith("enc:v1:"):
                config["auth_token"] = encrypt_secret(str(config["auth_token"]))
            update_data["config"] = config
        for key, value in update_data.items(): setattr(integration, key, value)

        await self.db.commit()
        await self.db.refresh(integration)
        return integration

    async def delete(self, integration_id: UUID, organization_id: UUID) -> bool:
        integration = await self.get_by_id(integration_id, organization_id)
        if not integration:
            return False

        await self.db.delete(integration)
        await self.db.commit()
        return True

    async def test_integration(self, integration_id: UUID, organization_id: UUID) -> dict[str, Any]:
        integration = await self.get_by_id(integration_id, organization_id)
        if not integration:
            return {"success": False, "error": "Integration not found"}

        try:
            if integration.type == IntegrationType.TWILIO:
                return await self._test_twilio(integration)
            elif integration.type == IntegrationType.GOOGLE_SHEETS:
                return await self._test_google_sheets(integration)
            elif integration.type == IntegrationType.OPENAI:
                return await self._test_openai(integration)
            elif integration.type == IntegrationType.GOOGLE_DRIVE:
                return await self._test_google_drive(integration)
            elif integration.type == IntegrationType.N8N:
                return await self._test_n8n(integration)
            else:
                return {"success": False, "error": "Unknown integration type"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_twilio(self, integration: Integration) -> dict[str, Any]:
        config = integration.config
        if isinstance(config, str):
            config = json.loads(config)

        client = Client(config.get("account_sid"), decrypt_secret(config.get("auth_token", "")))
        try:
            account = client.api.accounts(config.get("account_sid")).fetch()
            phone_number = config.get("phone_number", "")
            if not phone_number.startswith("+"): return {"success": False, "error": "Outgoing caller ID must use E.164 format, e.g. +14155550123."}
            return {"success": True, "message": f"Twilio connected: {account.friendly_name}. Caller ID: {phone_number}."}
        except TwilioRestException as e:
            return {"success": False, "error": f"Twilio error: {e.msg}"}

    async def _test_google_sheets(self, integration: Integration) -> dict[str, Any]:
        try:
            await self.google_sheets._get_client(integration)
            # Try to list spreadsheets (limited)
            return {"success": True, "message": "Google Sheets authentication successful"}
        except Exception as e:
            return {"success": False, "error": f"Google Sheets error: {e!s}"}

    async def _test_openai(self, integration: Integration) -> dict[str, Any]:
        config = integration.config
        if isinstance(config, str):
            config = json.loads(config)

        try:
            client = AsyncOpenAI(api_key=config.get("api_key"))
            # Test with a simple completion
            await client.chat.completions.create(
                model=config.get("model", "gpt-4o"),
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5,
            )
            return {"success": True, "message": "OpenAI API connection successful"}
        except Exception as e:
            return {"success": False, "error": f"OpenAI error: {e!s}"}

    async def _test_google_drive(self, integration: Integration) -> dict[str, Any]:
        try:
            from app.services.google_drive_service import GoogleDriveService
            drive_service = GoogleDriveService(self.db)
            client = await drive_service._get_client(integration)
            # Test by getting root folder
            client.files().get(fileId="root", fields="id").execute()
            return {"success": True, "message": "Google Drive authentication successful"}
        except Exception as e:
            return {"success": False, "error": f"Google Drive error: {e!s}"}

    async def _test_n8n(self, integration: Integration) -> dict[str, Any]:
        config = integration.config
        if isinstance(config, str):
            config = json.loads(config)

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                headers = {}
                if config.get("api_key"):
                    headers["X-N8N-API-KEY"] = config["api_key"]
                response = await client.get(f"{config.get('webhook_url', '').replace('/webhook', '')}/healthz", headers=headers)
                if response.status_code == 200:
                    return {"success": True, "message": "n8n connection successful"}
                else:
                    return {"success": False, "error": f"n8n returned status {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"n8n error: {e!s}"}

    async def sync_integration(self, integration_id: UUID, organization_id: UUID) -> dict[str, Any]:
        integration = await self.get_by_id(integration_id, organization_id)
        if not integration:
            return {"success": False, "error": "Integration not found"}

        integration.last_sync_at = datetime.utcnow()
        integration.last_sync_status = SyncStatus.RETRYING
        await self.db.commit()

        try:
            if integration.type == IntegrationType.GOOGLE_SHEETS and integration.campaign_id:
                # Sync campaign data to sheets
                from app.services.campaign_service import CampaignService
                campaign_service = CampaignService(self.db)
                campaign = await campaign_service.get_by_id(integration.campaign_id, organization_id)
                if campaign:
                    result = await self.google_sheets.sync_campaign_customers(campaign)
                    integration.last_sync_status = SyncStatus.SYNCED if result.get("success") else SyncStatus.FAILED
                    integration.last_sync_error = None if result.get("success") else result.get("error")
            else:
                integration.last_sync_status = SyncStatus.SYNCED

            await self.db.commit()
            return {"success": True, "status": integration.last_sync_status.value}

        except Exception as e:
            integration.last_sync_status = SyncStatus.FAILED
            integration.last_sync_error = str(e)
            await self.db.commit()
            return {"success": False, "error": str(e)}