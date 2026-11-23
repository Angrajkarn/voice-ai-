# Callback API routes

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing: List, Optional
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.schemas.callback import CallbackCreate, CallbackUpdate, CallbackResponse, CallbackComplete
from app.services.callback_service import CallbackService
from app.core.dependencies import get_current_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization

router = APIRouter(prefix="/callbacks", tags=["callbacks"])


@router.get("", response_model=dict)
async def list_callbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    campaign_id: Optional[UUID] = None,
    customer_id: Optional[UUID] = None,
    status: Optional[str] = None,
    assignee_id: Optional[UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallbackService(db)
    callbacks, total = await service.list(
        page=page,
        page_size=page_size,
        campaign_id=campaign_id,
        customer_id=customer_id,
        status=status,
        assignee_id=assignee_id,
        date_from=date_from,
        date_to=date_to,
    )
    return {
        "data": callbacks,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("", response_model=CallbackResponse, status_code=status.HTTP_201_CREATED)
async def create_callback(
    data: CallbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallbackService(db)
    callback = await service.create(data)
    return callback


@router.get("/{callback_id}", response_model=CallbackResponse)
async def get_callback(
    callback_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallbackService(db)
    callback = await service.get_by_id(callback_id)
    if not callback:
        raise HTTPException(status_code=404, detail="Callback not found")
    if callback.campaign.organization_id != organization.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return callback


@router.patch("/{callback_id}", response_model=CallbackResponse)
async def update_callback(
    callback_id: UUID,
    data: CallbackUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallbackService(db)
    callback = await service.update(callback_id, data)
    if not callback:
        raise HTTPException(status_code=404, detail="Callback not found")
    return callback


@router.delete("/{callback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_callback(
    callback_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallbackService(db)
    success = await service.delete(callback_id)
    if not success:
        raise HTTPException(status_code=404, detail="Callback not found")


@router.post("/{callback_id}/complete", response_model=CallbackResponse)
async def complete_callback(
    callback_id: UUID,
    data: CallbackComplete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallbackService(db)
    callback = await service.complete(callback_id, data.outcome)
    if not callback:
        raise HTTPException(status_code=404, detail="Callback not found")
    return callback


@router.get("/campaign/{campaign_id}/due", response_model=List[CallbackResponse])
async def get_due_callbacks(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallbackService(db)
    # Verify campaign belongs to organization
    from app.models.campaign import Campaign
    campaign = await db.scalar(
        select(Campaign).where(
            and_(Campaign.id == campaign_id, Campaign.organization_id == organization.id)
        )
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    callbacks = await service.get_due_callbacks(campaign_id)
    return callbacks


@router.get("/campaign/{campaign_id}/upcoming", response_model=List[CallbackResponse])
async def get_upcoming_callbacks(
    campaign_id: UUID,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallbackService(db)
    campaign = await db.scalar(
        select(Campaign).where(
            and_(Campaign.id == campaign_id, Campaign.organization_id == organization.id)
        )
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    callbacks = await service.get_upcoming_callbacks(campaign_id, hours)
    return callbacks