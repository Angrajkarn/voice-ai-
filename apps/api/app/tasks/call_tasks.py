# Call processing tasks

from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_
from typing import List
from uuid import UUID
from datetime import datetime, timedelta
import asyncio

from app.core.config import settings
from app.db.session import Base
from app.models.campaign import Campaign
from app.models.call import Call
from app.models.campaign_customer import CampaignCustomer
from app.models.enums import CallStatus, CampaignStatus
from app.services.call_service import CallService
from app.services.campaign_service import CampaignService


# Create async engine for tasks
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_campaign_calls(self, campaign_id: str):
    """Process queued calls for a campaign"""
    async def _process():
        async with AsyncSessionLocal() as db:
            campaign_service = CampaignService(db)
            call_service = CallService(db)

            campaign = await campaign_service.get_by_id(UUID(campaign_id), None)
            if not campaign or campaign.status != CampaignStatus.RUNNING:
                return {"status": "skipped", "reason": "Campaign not running"}

            # Check if within calling hours
            if not call_service._is_within_calling_window(campaign):
                return {"status": "skipped", "reason": "Outside calling hours"}

            # Check daily call limit
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            calls_today = await db.scalar(
                select(Call).where(
                    and_(
                        Call.campaign_id == UUID(campaign_id),
                        Call.created_at >= today_start,
                    )
                )
            )
            if calls_today and len(calls_today) >= campaign.max_calls_per_day:
                return {"status": "skipped", "reason": "Daily call limit reached"}

            # Get next queued call
            call = await call_service.get_next_queued_call(UUID(campaign_id))
            if not call:
                return {"status": "completed", "reason": "No queued calls"}

            # Initiate call
            success = await call_service.initiate_call(call.id)
            return {"status": "initiated" if success else "failed", "call_id": str(call.id)}

    try:
        return asyncio.run(_process())
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def retry_failed_calls():
    """Retry failed calls across all running campaigns"""
    async def _retry():
        async with AsyncSessionLocal() as db:
            campaign_service = CampaignService(db)
            call_service = CallService(db)

            # Get running campaigns
            campaigns = await db.execute(
                select(Campaign).where(Campaign.status == CampaignStatus.RUNNING)
            )
            campaigns = campaigns.scalars().all()

            total_retried = 0
            for campaign in campaigns:
                retried = await call_service.retry_failed_calls(campaign.id, campaign.max_retry_attempts)
                total_retried += retried

            return {"retried": total_retried}

    return asyncio.run(_retry())


@shared_task(bind=True, max_retries=3)
def initiate_outbound_call(self, call_id: str):
    """Initiate a specific outbound call"""
    async def _initiate():
        async with AsyncSessionLocal() as db:
            call_service = CallService(db)
            success = await call_service.initiate_call(UUID(call_id))
            return {"success": success}

    try:
        return asyncio.run(_initiate())
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def process_call_queue():
    """Process call queue for all running campaigns"""
    async def _process():
        async with AsyncSessionLocal() as db:
            campaign_service = CampaignService(db)

            campaigns = await db.execute(
                select(Campaign).where(Campaign.status == CampaignStatus.RUNNING)
            )
            campaigns = campaigns.scalars().all()

            results = []
            for campaign in campaigns:
                # Check daily limit
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                calls_today = await db.scalar(
                    select(Call).where(
                        and_(
                            Call.campaign_id == campaign.id,
                            Call.created_at >= today_start,
                        )
                    )
                )

                if calls_today and len(calls_today) >= campaign.max_calls_per_day:
                    continue

                # Process calls for this campaign
                call_service = CallService(db)
                for _ in range(5):  # Process up to 5 calls per campaign per run
                    call = await call_service.get_next_queued_call(campaign.id)
                    if not call:
                        break

                    success = await call_service.initiate_call(call.id)
                    results.append({"campaign_id": str(campaign.id), "call_id": str(call.id), "success": success})

                    # Respect delay between calls
                    if campaign.delay_between_calls > 0:
                        await asyncio.sleep(campaign.delay_between_calls)

            return {"processed": len(results), "results": results}

    return asyncio.run(_process())


@shared_task(bind=True, max_retries=3)
def handle_call_completion(self, call_id: str):
    """Handle post-call completion tasks"""
    async def _complete():
        async with AsyncSessionLocal() as db:
            call_service = CallService(db)
            call = await call_service.get_by_id(UUID(call_id))
            if not call:
                return {"status": "not_found"}

            # Trigger post-call automation
            await call_service._trigger_post_call_automation(call)
            return {"status": "completed"}

    try:
        return asyncio.run(_complete())
    except Exception as exc:
        raise self.retry(exc=exc)