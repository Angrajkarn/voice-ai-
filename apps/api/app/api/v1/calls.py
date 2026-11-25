# Call API routes

from datetime import datetime
from uuid import UUID

from app.core.dependencies import get_current_organization, get_current_user
from app.db.session import get_db
from app.models.enums import CallStatus
from app.models.organization import Organization
from app.models.user import User
from app.schemas.call import CallCreate, CallResponse
from app.services.call_service import CallService
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/calls", tags=["calls"])


@router.get("", response_model=dict)
async def list_calls(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    campaign_id: UUID | None = None,
    customer_id: UUID | None = None,
    status: str | None = None,
    direction: str | None = None,
    interest_level: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallService(db)
    calls, total = await service.list(
        page=page,
        page_size=page_size,
        campaign_id=campaign_id,
        customer_id=customer_id,
        status=status,
        direction=direction,
        interest_level=interest_level,
        date_from=date_from,
        date_to=date_to,
    )
    return {
        "data": calls,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallService(db)
    call = await service.get_by_id(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    # Verify organization access
    if call.campaign.organization_id != organization.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return call


@router.get("/{call_id}/transcript")
async def get_call_transcript(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallService(db)
    call = await service.get_by_id(call_id)
    if not call or call.campaign.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Call not found")

    from app.models.call_transcript import CallTranscript
    transcript = await db.scalar(
        select(CallTranscript).where(CallTranscript.call_id == call_id)
    )
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    return transcript


@router.get("/{call_id}/recording")
async def get_call_recording(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallService(db)
    call = await service.get_by_id(call_id)
    if not call or call.campaign.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Call not found")

    from app.models.call_recording import CallRecording
    recording = await db.scalar(
        select(CallRecording).where(CallRecording.call_id == call_id)
    )
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Return signed URL or redirect
    return {"url": recording.url, "expires_at": recording.expires_at}


@router.get("/campaign/{campaign_id}/live", response_model=list[CallResponse])
async def get_live_calls(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallService(db)
    # Verify campaign belongs to organization
    from app.models.campaign import Campaign
    campaign = await db.scalar(
        select(Campaign).where(
            and_(Campaign.id == campaign_id, Campaign.organization_id == organization.id)
        )
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    calls = await service.get_live_calls(campaign_id)
    return calls


@router.post("/{call_id}/retry")
async def retry_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallService(db)
    call = await service.get_by_id(call_id)
    if not call or call.campaign.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Call not found")

    # Create new call for retry
    new_call = await service.create(CallCreate(
        call_sid=None,
        campaign_id=call.campaign_id,
        customer_id=call.customer_id,
        direction=call.direction,
        from_number=call.from_number,
        to_number=call.to_number,
    ))

    return {"call_id": str(new_call.id), "message": "Retry call queued"}


@router.post("/{call_id}/cancel")
async def cancel_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = CallService(db)
    call = await service.get_by_id(call_id)
    if not call or call.campaign.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Call not found")

    if call.status not in [CallStatus.QUEUED, CallStatus.INITIATING, CallStatus.RINGING]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel call in status: {call.status}")

    call.status = CallStatus.CANCELLED
    await db.commit()

    return {"message": "Call cancelled"}