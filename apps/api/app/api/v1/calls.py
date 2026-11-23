# Call API routes

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing: List, Optional
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.schemas.call import CallCreate, CallUpdate, CallResponse
from app.services.call_service import CallService
from app.core.dependencies import get_current_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization

router = APIRouter(prefix="/calls", tags=["calls"])


@router.get("", response_model=dict)
async def list_calls(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    campaign_id: Optional[UUID] = None,
    customer_id: Optional[UUID] = None,
    status: Optional[str] = None,
    direction: Optional[str] = None,
    interest_level: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
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


@router.get("/campaign/{campaign_id}/live", response_model=List[CallResponse])
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

    if call.status not in ["QUEUED", "INITIATING", "RINGING"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel call in status: {call.status}")

    call.status = "CANCELLED"
    await db.commit()

    return {"message": "Call cancelled"}