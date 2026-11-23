# Suppression List API routes

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing: Optional
from uuid import UUID
from fastapi.responses import Response

from app.db.session import get_db
from app.services.suppression_service import SuppressionService
from app.core.dependencies import get_current_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization

router = APIRouter(prefix="/suppressions", tags=["suppressions"])


@router.get("", response_model=dict)
async def list_suppressions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = SuppressionService(db)
    suppressions, total = await service.list_suppressions(
        organization.id, page, page_size, active_only
    )
    return {
        "data": suppressions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("/check")
async def check_suppression(
    phone: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = SuppressionService(db)
    is_suppressed = await service.is_suppressed(phone, organization.id)
    return {"phone": phone, "suppressed": is_suppressed}


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_suppression(
    phone: str,
    reason: str = "MANUAL",
    campaign_id: Optional[UUID] = None,
    expires_at: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = SuppressionService(db)
    try:
        from datetime import datetime
        expires = datetime.fromisoformat(expires_at) if expires_at else None
        suppression = await service.add_to_suppression(
            phone=phone,
            reason=reason,
            organization_id=organization.id,
            campaign_id=campaign_id,
            expires_at=expires,
            added_by=str(current_user.id),
        )
        return suppression
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{suppression_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_suppression(
    suppression_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = SuppressionService(db)
    success = await service.remove_from_suppression(suppression_id, organization.id)
    if not success:
        raise HTTPException(status_code=404, detail="Suppression not found")


@router.post("/import", response_model=dict)
async def import_suppressions(
    file: UploadFile = File(...),
    reason: str = "IMPORT",
    source: str = "IMPORT",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = SuppressionService(db)
    content = await file.read()
    return await service.bulk_import(content, organization.id, reason, source)


@router.get("/export")
async def export_suppressions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = SuppressionService(db)
    content = await service.export_suppressions(organization.id)

    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=suppressions_export.csv"},
    )