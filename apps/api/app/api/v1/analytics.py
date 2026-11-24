# Analytics API routes

from datetime import date
from uuid import UUID

from app.core.dependencies import get_current_organization, get_current_user
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.analytics import (
    CampaignAnalytics,
    DashboardMetrics,
    OrganizationAnalytics,
)
from app.services.analytics_service import AnalyticsService
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = AnalyticsService(db)
    return await service.get_dashboard_metrics(organization.id)


@router.get("/campaigns/{campaign_id}", response_model=CampaignAnalytics)
async def get_campaign_analytics(
    campaign_id: UUID,
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = AnalyticsService(db)
    try:
        return await service.get_campaign_analytics(campaign_id, period, days)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/organization", response_model=OrganizationAnalytics)
async def get_organization_analytics(
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = AnalyticsService(db)
    return await service.get_organization_analytics(organization.id, period, days)


@router.get("/export/{report_type}")
async def export_report(
    report_type: str,
    campaign_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = AnalyticsService(db)
    content = await service.export_report(
        report_type,
        organization.id,
        campaign_id,
        date_from,
        date_to,
    )

    media_type = "text/csv" if format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = f"{report_type}_export.{format}"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )