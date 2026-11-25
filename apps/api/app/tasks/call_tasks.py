# Call processing tasks

from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, and_, func
from uuid import UUID
from datetime import datetime
import asyncio

from app.core.config import settings
from app.models.campaign import Campaign
from app.models.call import Call
from app.models.enums import CampaignStatus
from app.services.call_service import CallService


# Create async engine for tasks
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_campaign_calls(self, campaign_id: str):
    """Process queued calls for a campaign"""
    async def _process():
        async with AsyncSessionLocal() as db:
            call_service = CallService(db)
            campaign = await db.get(Campaign, UUID(campaign_id))
            if not campaign or campaign.status != CampaignStatus.RUNNING:
                return {"status": "skipped", "reason": "Campaign not running"}

            # Check if within calling hours
            if not call_service._is_within_calling_window(campaign):
                return {"status": "skipped", "reason": "Outside calling hours"}

            # Check daily call limit
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            calls_today = await db.scalar(
                select(func.count(Call.id)).where(
                    and_(Call.campaign_id == UUID(campaign_id), Call.initiated_at >= today_start)
                )
            ) or 0
            if calls_today >= campaign.max_calls_per_day:
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
    """Process one due outbound call per running campaign on each beat tick."""
    async def _process():
        async with AsyncSessionLocal() as db:
            campaigns = await db.execute(select(Campaign).where(Campaign.status == CampaignStatus.RUNNING))
            results, call_service = [], CallService(db)
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            for campaign in campaigns.scalars().all():
                if not call_service._is_within_calling_window(campaign): continue
                calls_today = await db.scalar(select(func.count(Call.id)).where(and_(Call.campaign_id == campaign.id, Call.initiated_at >= today_start))) or 0
                if calls_today >= campaign.max_calls_per_day: continue
                last_initiated = await db.scalar(select(func.max(Call.initiated_at)).where(and_(Call.campaign_id == campaign.id, Call.initiated_at.is_not(None))))
                if last_initiated and (now - last_initiated.replace(tzinfo=None)).total_seconds() < campaign.delay_between_calls: continue
                call = await call_service.get_next_queued_call(campaign.id)
                if not call: continue
                success = await call_service.initiate_call(call.id)
                results.append({"campaign_id": str(campaign.id), "call_id": str(call.id), "success": success})
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