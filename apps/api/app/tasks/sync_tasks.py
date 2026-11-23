# Sync tasks for Google Sheets and other integrations

from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_
from typing: List
from uuid import UUID
from datetime import datetime
import asyncio

from app.core.config import settings
from app.services.google_sheets_service import GoogleSheetsService
from app.models.integration import Integration
from app.models.enums import IntegrationType, SyncStatus
from app.models.call import Call
from app.models.campaign import Campaign


engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@shared_task
def sync_all_campaigns():
    """Sync all campaigns with Google Sheets enabled"""
    async def _sync():
        async with AsyncSessionLocal() as db:
            # Get campaigns with sheets sync enabled
            campaigns = await db.execute(
                select(Campaign).where(
                    and_(
                        Campaign.sheets_sync_enabled == True,
                        Campaign.sheets_auto_sync == True,
                        Campaign.sheets_spreadsheet_id.isnot(None),
                        Campaign.status.in_(["RUNNING", "PAUSED", "COMPLETED"]),
                    )
                )
            )

            results = []
            for campaign in campaigns.scalars().all():
                # Get pending calls to sync
                calls = await db.execute(
                    select(Call).where(
                        and_(
                            Call.campaign_id == campaign.id,
                            Call.sheets_synced == False,
                            Call.status == "COMPLETED",
                        )
                    ).limit(settings.SHEETS_SYNC_BATCH_SIZE)
                )

                synced = 0
                for call in calls.scalars().all():
                    sheets_service = GoogleSheetsService(db)
                    success = await sheets_service.sync_call(call)
                    if success:
                        synced += 1

                # Update summary sheet
                await sheets_service.update_summary_sheet(campaign)

                results.append({
                    "campaign_id": str(campaign.id),
                    "synced": synced,
                })

            return {"campaigns_synced": len(results), "details": results}

    return asyncio.run(_sync())


@shared_task(bind=True, max_retries=3)
def sync_call_to_sheets(self, call_id: str):
    """Sync a specific call to Google Sheets"""
    async def _sync():
        async with AsyncSessionLocal() as db:
            from app.services.call_service import CallService
            call_service = CallService(db)
            call = await call_service.get_by_id(UUID(call_id))
            if not call:
                return {"status": "not_found"}

            if call.sheets_synced:
                return {"status": "already_synced"}

            sheets_service = GoogleSheetsService(db)
            success = await sheets_service.sync_call(call)
            return {"status": "synced" if success else "failed"}

    try:
        return asyncio.run(_sync())
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def sync_campaign_customers(campaign_id: str):
    """Sync campaign customers to Google Sheets"""
    async def _sync():
        async with AsyncSessionLocal() as db:
            campaign = await db.scalar(
                select(Campaign).where(Campaign.id == UUID(campaign_id))
            )
            if not campaign:
                return {"status": "not_found"}

            sheets_service = GoogleSheetsService(db)
            result = await sheets_service.sync_campaign_customers(campaign)
            return result

    return asyncio.run(_sync())


@shared_task(bind=True, max_retries=3)
def retry_failed_syncs(self):
    """Retry failed sync operations"""
    async def _retry():
        async with AsyncSessionLocal() as db:
            from app.models.sync_log import SyncLog
            from app.models.enums import SyncStatus

            failed_syncs = await db.execute(
                select(SyncLog).where(
                    and_(
                        SyncLog.status == SyncStatus.FAILED,
                        SyncLog.retry_count < settings.SHEETS_SYNC_RETRY_ATTEMPTS,
                    )
                ).limit(50)
            )

            retried = 0
            for sync_log in failed_syncs.scalars().all():
                sync_log.status = SyncStatus.RETRYING
                sync_log.retry_count += 1
                # Re-queue based on operation type
                if sync_log.operation == "SYNC_CALL":
                    from app.tasks.sync_tasks import sync_call_to_sheets
                    sync_call_to_sheets.delay(sync_log.entity_id)
                elif sync_log.operation == "SYNC_CUSTOMER":
                    # Retry customer sync
                    pass
                retried += 1

            await db.commit()
            return {"retried": retried}

    try:
        return asyncio.run(_retry())
    except Exception as exc:
        raise self.retry(exc=exc)