# Consent Records API routes

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing: Optional
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.services.consent_service import ConsentService
from app.core.dependencies import get_current_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization

router = APIRouter(prefix="/consent", tags=["consent"])


@router.get("", response_model=dict)
async def list_consents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = ConsentService(db)
    consents, total = await service.list_consents(organization.id, page, page_size, status)
    return {
        "data": consents,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/status/{phone}")
async def get_consent_status(
    phone: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = ConsentService(db)
    consent_status = await service.get_consent_status(phone, organization.id)
    return {"phone": phone, "consent_status": consent_status.value if consent_status else None}


@router.post("", status_code=status.HTTP_201_CREATED)
async def record_consent(
    phone: str,
    status: str,
    method: str,
    campaign_id: Optional[UUID] = None,
    customer_id: Optional[UUID] = None,
    proof_url: Optional[str] = None,
    proof_expires_at: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = ConsentService(db)
    try:
        expires = datetime.fromisoformat(proof_expires_at) if proof_expires_at else None
        consent = await service.record_consent(
            phone=phone,
            status=status,
            method=method,
            organization_id=organization.id,
            campaign_id=campaign_id,
            customer_id=customer_id,
            proof_url=proof_url,
            proof_expires_at=expires,
        )
        return consent
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{consent_id}/revoke")
async def revoke_consent(
    consent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = ConsentService(db)
    consent = await service.revoke_consent(consent_id, organization.id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found")
    return consent