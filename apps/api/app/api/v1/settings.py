# Settings API routes

from uuid import UUID

from app.core.dependencies import get_current_organization, get_current_user
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationResponse, OrganizationUpdate
from app.schemas.user import UserResponse, UserUpdate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/password")
async def change_password(
    current_password: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify current password (would use proper password hashing)
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    if not pwd_context.verify(current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.password_hash = pwd_context.hash(new_password)
    await db.commit()

    return {"message": "Password changed successfully"}


@router.get("/organization", response_model=OrganizationResponse)
async def get_organization_settings(
    organization: Organization = Depends(get_current_organization),
):
    return organization


@router.patch("/organization", response_model=OrganizationResponse)
async def update_organization_settings(
    data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(organization, key, value)
    await db.commit()
    await db.refresh(organization)
    return organization


@router.get("/notifications")
async def get_notifications(
    page: int = 1,
    page_size: int = 20,
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.notification_service import NotificationService
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


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.notification_service import NotificationService
    service = NotificationService(db)
    notification = await service.mark_read(notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.notification_service import NotificationService
    service = NotificationService(db)
    count = await service.mark_all_read(current_user.id)
    return {"message": f"Marked {count} notifications as read"}