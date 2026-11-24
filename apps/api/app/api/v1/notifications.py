# Notification API routes (for internal use)

from uuid import UUID

from app.core.dependencies import get_current_organization, get_current_user
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.services.notification_service import NotificationService
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=dict)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    service = NotificationService(db)
    notifications, total = await service.list_notifications(
        current_user.id, page, page_size, unread_only
    )
    return {
        "data": notifications,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    count = await service.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    notification = await service.mark_read(notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    count = await service.mark_all_read(current_user.id)
    return {"message": f"Marked {count} notifications as read", "count": count}