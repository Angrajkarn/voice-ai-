# Maintenance tasks

import asyncio
from datetime import datetime, timedelta

from app.core.config import settings
from celery import shared_task
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@shared_task
def cleanup_old_data():
    """Clean up old data based on retention policies"""
    async def _cleanup():
        async with AsyncSessionLocal() as db:
            from app.models.audit_log import AuditLog
            from app.models.automation_log import AutomationLog
            from app.models.call import Call
            from app.models.enums import CallStatus
            from app.models.notification import Notification
            from app.models.sync_log import SyncLog

            cutoff_30_days = datetime.utcnow() - timedelta(days=30)
            cutoff_90_days = datetime.utcnow() - timedelta(days=90)
            cutoff_1_year = datetime.utcnow() - timedelta(days=365)

            results = {}

            # Clean up completed/failed calls older than 90 days
            result = await db.execute(
                delete(Call).where(
                    and_(
                        Call.status.in_([CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.CANCELLED]),
                        Call.created_at < cutoff_90_days,
                    )
                )
            )
            results["calls_deleted"] = result.rowcount

            # Clean up audit logs older than 1 year
            result = await db.execute(
                delete(AuditLog).where(AuditLog.created_at < cutoff_1_year)
            )
            results["audit_logs_deleted"] = result.rowcount

            # Clean up sync logs older than 30 days
            result = await db.execute(
                delete(SyncLog).where(SyncLog.created_at < cutoff_30_days)
            )
            results["sync_logs_deleted"] = result.rowcount

            # Clean up automation logs older than 90 days
            result = await db.execute(
                delete(AutomationLog).where(AutomationLog.created_at < cutoff_90_days)
            )
            results["automation_logs_deleted"] = result.rowcount

            # Clean up read notifications older than 30 days
            result = await db.execute(
                delete(Notification).where(
                    and_(
                        Notification.is_read == True,
                        Notification.read_at < cutoff_30_days,
                    )
                )
            )
            results["notifications_deleted"] = result.rowcount

            await db.commit()
            return results

    return asyncio.run(_cleanup())


@shared_task
def archive_completed_campaigns():
    """Archive campaigns that have been completed for a while"""
    async def _archive():
        async with AsyncSessionLocal() as db:
            from app.models.campaign import Campaign
            from app.models.enums import CampaignStatus

            cutoff = datetime.utcnow() - timedelta(days=30)

            campaigns = await db.execute(
                select(Campaign).where(
                    and_(
                        Campaign.status == CampaignStatus.COMPLETED,
                        Campaign.completed_at < cutoff,
                    )
                )
            )

            archived = 0
            for campaign in campaigns.scalars().all():
                # In production, move to archive table or cold storage
                archived += 1

            return {"archived": archived}

    return asyncio.run(_archive())


@shared_task
def check_integration_health():
    """Check health of all active integrations"""
    async def _check():
        async with AsyncSessionLocal() as db:
            from app.models.enums import SyncStatus
            from app.models.integration import Integration
            from app.services.integration_service import IntegrationService

            integrations = await db.execute(
                select(Integration).where(Integration.is_active == True)
            )

            results = []
            for integration in integrations.scalars().all():
                service = IntegrationService(db)
                test_result = await service.test_integration(integration.id, integration.organization_id)

                integration.last_sync_at = datetime.utcnow()
                integration.last_sync_status = SyncStatus.SYNCED if test_result.get("success") else SyncStatus.FAILED
                integration.last_sync_error = test_result.get("error")

                results.append({
                    "integration_id": str(integration.id),
                    "type": integration.type.value,
                    "healthy": test_result.get("success"),
                })

            await db.commit()
            return {"checked": len(results), "results": results}

    return asyncio.run(_check())


@shared_task
def update_campaign_statistics():
    """Update campaign statistics counters"""
    async def _update():
        async with AsyncSessionLocal() as db:
            from app.models.call import Call
            from app.models.callback import Callback
            from app.models.campaign import Campaign
            from app.models.customer import Customer
            from app.models.enums import (
                CallbackStatus,
                CallStatus,
                CustomerStatus,
                InterestLevel,
            )
            from sqlalchemy import func, select

            campaigns = await db.execute(select(Campaign))

            updated = 0
            for campaign in campaigns.scalars().all():
                # Total calls
                # Completed calls
                completed_calls = await db.scalar(
                    select(func.count(Call.id)).where(
                        and_(Call.campaign_id == campaign.id, Call.status == CallStatus.COMPLETED)
                    )
                ) or 0

                # Failed calls
                failed_calls = await db.scalar(
                    select(func.count(Call.id)).where(
                        and_(Call.campaign_id == campaign.id, Call.status.in_([
                            CallStatus.FAILED, CallStatus.BUSY, CallStatus.NO_ANSWER,
                            CallStatus.VOICEMAIL, CallStatus.INVALID_NUMBER
                        ]))
                    )
                ) or 0

                # Interested
                interested = await db.scalar(
                    select(func.count(Call.id)).where(
                        and_(Call.campaign_id == campaign.id, Call.interest_level.in_([InterestLevel.HOT, InterestLevel.WARM]))
                    )
                ) or 0

                # Callbacks
                callbacks = await db.scalar(
                    select(func.count(Callback.id)).where(
                        and_(Callback.campaign_id == campaign.id, Callback.status == CallbackStatus.SCHEDULED)
                    )
                ) or 0

                # Opt-outs
                opt_outs = await db.scalar(
                    select(func.count(Customer.id)).where(
                        and_(
                            Customer.campaigns.any(Campaign.id == campaign.id),
                            Customer.status == CustomerStatus.OPTED_OUT,
                        )
                    )
                ) or 0

                campaign.total_customers = await db.scalar(
                    select(func.count()).select_from(
                        select(1).where(Campaign.id == campaign.id).join(Campaign.campaign_customers).subquery()
                    )
                ) or 0
                campaign.completed_calls = completed_calls
                campaign.failed_calls = failed_calls
                campaign.interested_count = interested
                campaign.callback_count = callbacks
                campaign.opt_out_count = opt_outs

                updated += 1

            await db.commit()
            return {"updated": updated}

    return asyncio.run(_update())