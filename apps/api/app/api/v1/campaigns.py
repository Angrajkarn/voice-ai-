# Campaign API routes

from typing import Any
from uuid import UUID

from app.core.dependencies import get_current_organization, get_current_user
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.campaign import (
    CampaignBulkAction,
    CampaignCreate,
    CampaignMetrics,
    CampaignResponse,
    CampaignUpdate,
)
from app.services.campaign_service import CampaignService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=dict)
async def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    search: str | None = None,
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    campaigns, total = await service.list(
        organization_id=organization.id,
        page=page,
        page_size=page_size,
        status=status,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {
        "data": campaigns,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    campaign = await service.create(data, current_user.id, organization.id)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    campaign = await service.get_by_id(campaign_id, organization.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    campaign = await service.update(campaign_id, organization.id, data)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    success = await service.delete(campaign_id, organization.id)
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")


@router.post("/{campaign_id}/start", response_model=CampaignResponse)
async def start_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    campaign = await service.start(campaign_id, organization.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != "RUNNING":
        raise HTTPException(status_code=400, detail=f"Cannot start campaign in status: {campaign.status}")
    return campaign


@router.post("/{campaign_id}/pause", response_model=CampaignResponse)
async def pause_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    campaign = await service.pause(campaign_id, organization.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/{campaign_id}/stop", response_model=CampaignResponse)
async def stop_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    campaign = await service.stop(campaign_id, organization.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/{campaign_id}/validate", response_model=dict)
async def validate_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    result = await service.validate(campaign_id, organization.id)
    return result


@router.get("/{campaign_id}/metrics", response_model=CampaignMetrics)
async def get_campaign_metrics(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    metrics = await service.get_metrics(campaign_id, organization.id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return metrics


@router.post("/bulk", response_model=dict)
async def bulk_campaign_action(
    data: CampaignBulkAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CampaignService(db)
    results: dict[str, Any] = {"success": 0, "failed": 0, "errors": []}

    for campaign_id in data.campaign_ids:
        try:
            if data.action == "start":
                await service.start(campaign_id, organization.id)
            elif data.action == "pause":
                await service.pause(campaign_id, organization.id)
            elif data.action == "stop":
                await service.stop(campaign_id, organization.id)
            elif data.action == "delete":
                await service.delete(campaign_id, organization.id)
            results["success"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"campaign_id": str(campaign_id), "error": str(e)})

    return results