# Google Sheets Service - Handles Google Sheets API integration

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import json
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from app.models.campaign import Campaign
from app.models.call import Call
from app.models.customer import Customer
from app.models.integration import Integration
from app.models.enums import IntegrationType, SyncStatus
from app.core.config import settings


class GoogleSheetsService:
    def __init__(self, db):
        self.db = db
        self.sheets_client = None
        self.drive_client = None

    async def _get_client(self, integration: Integration) -> gspread.Client:
        """Get authenticated gspread client"""
        if self.sheets_client:
            return self.sheets_client

        config = integration.config
        if isinstance(config, str):
            config = json.loads(config)

        credentials = Credentials.from_service_account_info(
            config,
            scopes=settings.GOOGLE_SHEETS_SCOPES,
        )

        self.sheets_client = gspread.authorize(credentials)
        return self.sheets_client

    async def _get_drive_client(self, integration: Integration):
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

    async def sync_call(self, call: Call) -> bool:
        """Sync a completed call to Google Sheets"""
        campaign = call.campaign
        if not campaign or not campaign.sheets_sync_enabled or not campaign.sheets_spreadsheet_id:
            return False

        # Get Google Sheets integration
        integration = await self.db.scalar(
            select(Integration).where(
                and_(
                    Integration.campaign_id == campaign.id,
                    Integration.type == IntegrationType.GOOGLE_SHEETS,
                    Integration.is_active == True,
                )
            )
        )

        if not integration:
            return False

        try:
            client = await self._get_client(integration)
            spreadsheet = client.open_by_key(campaign.sheets_spreadsheet_id)
            worksheet = spreadsheet.worksheet(campaign.sheets_sheet_name)

            # Prepare row data
            row_data = self._prepare_call_row(call)

            # Find existing row or append new
            if call.sheets_row_index:
                try:
                    worksheet.update(f"A{call.sheets_row_index}:P{call.sheets_row_index}", [row_data])
                except Exception:
                    # Row might be deleted, append new
                    call.sheets_row_index = None

            if not call.sheets_row_index:
                # Append new row
                worksheet.append_row(row_data, value_input_option="USER_ENTERED")
                # Get the new row index (last row)
                all_values = worksheet.get_all_values()
                call.sheets_row_index = len(all_values)

            # Update call record
            call.sheets_synced = True
            call.sheets_sync_at = datetime.utcnow()
            call.sheets_sync_status = SyncStatus.SYNCED
            call.sheets_sync_error = None
            await self.db.commit()

            # Log sync
            await self._log_sync(integration, "SYNC_CALL", "Call", str(call.id), SyncStatus.SYNCED)

            return True

        except Exception as e:
            call.sheets_sync_status = SyncStatus.FAILED
            call.sheets_sync_error = str(e)
            await self.db.commit()

            await self._log_sync(
                integration, "SYNC_CALL", "Call", str(call.id), SyncStatus.FAILED, error=str(e)
            )
            return False

    async def sync_customer(self, customer: Customer, campaign_id: UUID) -> bool:
        """Sync customer to Google Sheets (if needed for reference)"""
        # This could be used to maintain a customer reference sheet
        return True

    async def sync_campaign_customers(self, campaign: Campaign) -> Dict[str, Any]:
        """Sync all campaign customers to Google Sheets"""
        integration = await self.db.scalar(
            select(Integration).where(
                and_(
                    Integration.campaign_id == campaign.id,
                    Integration.type == IntegrationType.GOOGLE_SHEETS,
                    Integration.is_active == True,
                )
            )
        )

        if not integration:
            return {"success": False, "error": "No Google Sheets integration"}

        try:
            client = await self._get_client(integration)
            spreadsheet = client.open_by_key(campaign.sheets_spreadsheet_id)

            # Get or create customers worksheet
            try:
                worksheet = spreadsheet.worksheet("Customers")
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet("Customers", rows=1000, cols=20)

            # Get all campaign customers
            from app.models.campaign_customer import CampaignCustomer
            campaign_customers = await self.db.execute(
                select(CampaignCustomer)
                .options(selectinload(CampaignCustomer.customer))
                .where(CampaignCustomer.campaign_id == campaign.id)
            )
            customers = [cc.customer for cc in campaign_customers.scalars().all()]

            # Prepare headers
            headers = [
                "Customer ID", "First Name", "Last Name", "Email", "Phone",
                "Company", "Location", "Language", "Status", "Interest Level",
                "Call Attempts", "Last Call", "Next Callback", "Tags", "Added At"
            ]

            # Clear and write headers
            worksheet.clear()
            worksheet.append_row(headers, value_input_option="USER_ENTERED")

            # Write customer data
            rows = []
            for cc in customers:
                rows.append([
                    str(cc.id), cc.first_name, cc.last_name, cc.email or "",
                    cc.phone, cc.company or "", cc.location or "",
                    cc.language, cc.status.value, cc.interest_level.value,
                    cc.call_attempts,
                    cc.last_call_at.isoformat() if cc.last_call_at else "",
                    cc.next_callback_at.isoformat() if cc.next_callback_at else "",
                    ", ".join(cc.tags),
                    cc.created_at.isoformat(),
                ])

            if rows:
                worksheet.append_rows(rows, value_input_option="USER_ENTERED")

            return {"success": True, "synced": len(rows)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _prepare_call_row(self, call: Call) -> List[str]:
        """Prepare call data for Google Sheets row"""
        customer = call.customer
        return [
            str(call.customer_id),                    # Customer ID
            f"{customer.first_name} {customer.last_name}",  # Name
            customer.phone,                            # Phone
            call.status.value,                         # Call Status
            str(call.duration or 0),                   # Call Duration
            call.ended_at.isoformat() if call.ended_at else "",  # Call Date
            call.summary or "",                        # AI Summary
            call.transcript_text or "",                # Full Transcript
            call.interest_level.value,                 # Interest Level
            call.customer_intent or "",                # Customer Intent
            ", ".join(call.objections) if call.objections else "",  # Objection
            "Yes" if any("callback" in q.lower() for q in call.questions_asked) else "No",  # Callback Required
            "",  # Callback Date (would be filled from callback record)
            call.disposition or "",                    # Final Outcome
            call.recording_url or "",                  # Recording URL
            str(call.customer.call_attempts),          # Attempts
            datetime.utcnow().isoformat(),             # Last Updated
        ]

    async def create_spreadsheet_structure(self, integration: Integration, campaign: Campaign) -> bool:
        """Create the initial spreadsheet structure with proper headers"""
        try:
            client = await self._get_client(integration)
            spreadsheet = client.open_by_key(campaign.sheets_spreadsheet_id)

            # Create Calls sheet
            try:
                calls_sheet = spreadsheet.worksheet(campaign.sheets_sheet_name)
                calls_sheet.clear()
            except gspread.WorksheetNotFound:
                calls_sheet = spreadsheet.add_worksheet(campaign.sheets_sheet_name, rows=10000, cols=20)

            # Headers for calls sheet
            calls_headers = [
                "Customer ID", "Name", "Phone", "Call Status", "Call Duration",
                "Call Date", "AI Summary", "Full Transcript", "Interest Level",
                "Customer Intent", "Objection", "Callback Required", "Callback Date",
                "Final Outcome", "Recording URL", "Attempts", "Last Updated"
            ]
            calls_sheet.append_row(calls_headers, value_input_option="USER_ENTERED")

            # Format header row
            calls_sheet.format("A1:Q1", {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
                "horizontalAlignment": "CENTER",
            })

            # Create Customers sheet
            try:
                customers_sheet = spreadsheet.worksheet("Customers")
                customers_sheet.clear()
            except gspread.WorksheetNotFound:
                customers_sheet = spreadsheet.add_worksheet("Customers", rows=1000, cols=20)

            customers_headers = [
                "Customer ID", "First Name", "Last Name", "Email", "Phone",
                "Company", "Location", "Language", "Status", "Interest Level",
                "Call Attempts", "Last Call", "Next Callback", "Tags", "Added At"
            ]
            customers_sheet.append_row(customers_headers, value_input_option="USER_ENTERED")
            customers_sheet.format("A1:O1", {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
            })

            # Create Summary sheet
            try:
                summary_sheet = spreadsheet.worksheet("Summary")
                summary_sheet.clear()
            except gspread.WorksheetNotFound:
                summary_sheet = spreadsheet.add_worksheet("Summary", rows=100, cols=10)

            summary_headers = ["Metric", "Value"]
            summary_sheet.append_row(summary_headers, value_input_option="USER_ENTERED")

            return True

        except Exception as e:
            return False

    async def update_summary_sheet(self, campaign: Campaign) -> bool:
        """Update the summary sheet with campaign metrics"""
        integration = await self.db.scalar(
            select(Integration).where(
                and_(
                    Integration.campaign_id == campaign.id,
                    Integration.type == IntegrationType.GOOGLE_SHEETS,
                    Integration.is_active == True,
                )
            )
        )

        if not integration:
            return False

        try:
            from app.services.campaign_service import CampaignService
            campaign_service = CampaignService(self.db)
            metrics = await campaign_service.get_metrics(campaign.id, campaign.organization_id)

            client = await self._get_client(integration)
            spreadsheet = client.open_by_key(campaign.sheets_spreadsheet_id)
            summary_sheet = spreadsheet.worksheet("Summary")

            # Clear and write summary
            summary_sheet.clear()
            summary_data = [
                ["Metric", "Value"],
                ["Campaign", campaign.name],
                ["Status", campaign.status.value],
                ["Total Customers", metrics.total_customers],
                ["Total Calls", metrics.total_calls],
                ["Completed Calls", metrics.completed_calls],
                ["Failed Calls", metrics.failed_calls],
                ["Answered Calls", metrics.answered_calls],
                ["Interested Customers", metrics.interested_count],
                ["Callbacks Scheduled", metrics.callback_count],
                ["Opt-outs", metrics.opt_out_count],
                ["Average Duration (s)", metrics.average_duration],
                ["Success Rate (%)", metrics.success_rate],
                ["Answer Rate (%)", metrics.answer_rate],
                ["Last Updated", datetime.utcnow().isoformat()],
            ]
            summary_sheet.append_rows(summary_data, value_input_option="USER_ENTERED")

            return True
        except Exception:
            return False

    async def _log_sync(
        self,
        integration: Integration,
        operation: str,
        entity_type: str,
        entity_id: str,
        status: SyncStatus,
        error: Optional[str] = None,
    ):
        """Log sync operation"""
        from app.models.sync_log import SyncLog
        log = SyncLog(
            integration_id=integration.id,
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            error=error,
            completed_at=datetime.utcnow() if status in [SyncStatus.SYNCED, SyncStatus.FAILED] else None,
        )
        self.db.add(log)
        await self.db.commit()