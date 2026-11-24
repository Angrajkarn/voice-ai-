# Google Drive Service - Handles Google Drive API integration for recordings

import io
import json
from datetime import datetime

from app.core.config import settings
from app.models.call_recording import CallRecording
from app.models.enums import SyncStatus
from app.models.integration import Integration
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


class GoogleDriveService:
    def __init__(self, db):
        self.db = db
        self.drive_client = None

    async def _get_client(self, integration: Integration):
        """Get authenticated Google Drive client"""
        if self.drive_client:
            return self.drive_client

        config = integration.config
        if isinstance(config, str):
            config = json.loads(config)

        credentials = Credentials.from_service_account_info(
            config,
            scopes=settings.GOOGLE_DRIVE_SCOPES,
        )

        self.drive_client = build("drive", "v3", credentials=credentials)
        return self.drive_client

    async def upload_recording(
        self,
        recording: CallRecording,
        audio_data: bytes,
        integration: Integration,
    ) -> str | None:
        """Upload call recording to Google Drive"""
        try:
            client = await self._get_client(integration)
            config = integration.config
            if isinstance(config, str):
                config = json.loads(config)

            folder_id = config.get("folder_id") or "root"

            # Create file metadata
            file_metadata = {
                "name": f"call_{recording.call_id}_{recording.provider_id}.{recording.format}",
                "parents": [folder_id],
                "description": f"Call recording for call {recording.call_id}",
            }

            # Upload file
            media = MediaIoBaseUpload(
                io.BytesIO(audio_data),
                mimetype=f"audio/{recording.format}",
                resumable=True,
            )

            file = client.files().create(
                body=file_metadata,
                media_body=media,
                fields="id,webViewLink",
            ).execute()

            # Update recording record
            recording.drive_file_id = file.get("id")
            recording.drive_synced_at = datetime.utcnow()
            recording.drive_sync_status = SyncStatus.SYNCED
            recording.url = file.get("webViewLink")

            await self.db.commit()

            return file.get("id")

        except Exception:
            recording.drive_sync_status = SyncStatus.FAILED
            await self.db.commit()
            return None

    async def create_folder_structure(self, integration: Integration, campaign_name: str) -> str | None:
        """Create folder structure for campaign recordings"""
        try:
            client = await self._get_client(integration)

            # Create main campaign folder
            folder_metadata = {
                "name": f"VoiceAI_Recordings_{campaign_name}",
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = client.files().create(body=folder_metadata, fields="id").execute()
            return folder.get("id")

        except Exception:
            return None

    async def delete_recording(self, drive_file_id: str, integration: Integration) -> bool:
        """Delete recording from Google Drive"""
        try:
            client = await self._get_client(integration)
            client.files().delete(fileId=drive_file_id).execute()
            return True
        except Exception:
            return False

    async def get_recording_url(self, drive_file_id: str, integration: Integration) -> str | None:
        """Get shareable link for recording"""
        try:
            client = await self._get_client(integration)
            file = client.files().get(fileId=drive_file_id, fields="webViewLink").execute()
            return file.get("webViewLink")
        except Exception:
            return None