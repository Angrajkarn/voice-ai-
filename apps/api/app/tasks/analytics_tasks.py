# Analytics computation tasks

from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, and_
from typing: List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta, date
import asyncio

from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@shared_task
def update_daily_analytics():
    """Update daily analytics aggregates"""
    async def _update():
        async with AsyncSessionLocal() as db:
            from app.models.call import Call
            from app.models.campaign import Campaign
            from app.models.enums import CallStatus, InterestLevel
            from app.models.analytics_daily import DailyAnalytics  # Would need to create this model

            # This would update materialized views or summary tables
            # For now, return a placeholder
            return {"status": "updated", "timestamp": datetime.utcnow().isoformat()}

    return asyncio.run(_update())


@shared_task
def generate_campaign_reports():
    """Generate scheduled campaign reports"""
    async def _generate():
        async with AsyncSessionLocal() as db:
            from app.models.campaign import Campaign
            from app.models.enums import CampaignStatus

            # Get campaigns that need reports
            campaigns = await db.execute(
                select(Campaign).where(
                    and_(
                        Campaign.status.in_([CampaignStatus.RUNNING, CampaignStatus.COMPLETED]),
                        # Add logic for report scheduling
                    )
                )
            )

            reports = []
            for campaign in campaigns.scalars().all():
                # Generate report (would use analytics service)
                reports.append({
                    "campaign_id": str(campaign.id),
                    "report_generated": True,
                })

            return {"reports_generated": len(reports)}

    return asyncio.run(_generate())


@shared_task(bind=True, max_retries=3)
def export_analytics_report(self, export_params: Dict[str, Any]):
    """Export analytics report asynchronously"""
    async def _export():
        async with AsyncSessionLocal() as db:
            from app.services.analytics_service import AnalyticsService

            service = AnalyticsService(db)
            content = await service.export_report(
                export_params["report_type"],
                UUID(export_params["organization_id"]),
                UUID(export_params["campaign_id"]) if export_params.get("campaign_id") else None,
                date.fromisoformat(export_params["date_from"]) if export_params.get("date_from") else None,
                date.fromisoformat(export_params["date_to"]) if export_params.get("date_to") else None,
            )

            # In production, upload to cloud storage and return signed URL
            return {"size": len(content), "format": export_params.get("format", "csv")}

    try:
        return asyncio.run(_export())
    except Exception as exc:
        raise self.retry(exc=exc)