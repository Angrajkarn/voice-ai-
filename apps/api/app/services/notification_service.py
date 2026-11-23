# Notification Service - Handles user notifications

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.models.notification import Notification
from app.models.enums import NotificationType


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: UUID,
        organization_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[dict] = None,
        campaign_id: Optional[UUID] = None,
        call_id: Optional[UUID] = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            organization_id=organization_id,
            type=notification_type,
            title=title,
            message=message,
            data=data or {},
            campaign_id=campaign_id,
            call_id=call_id,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def create_hot_lead_notification(self, call) -> Notification:
        """Create notification for hot lead"""
        # Get campaign owner/managers
        from app.models.user import User
        from app.models.enums import UserRole

        managers = await self.db.execute(
            select(User).where(
                and_(
                    User.organization_id == call.campaign.organization_id,
                    User.role.in_([UserRole.ADMIN, UserRole.MANAGER]),
                    User.is_active == True,
                )
            )
        )

        notifications = []
        for user in managers.scalars().all():
            notification = await self.create(
                user_id=user.id,
                organization_id=call.campaign.organization_id,
                notification_type=NotificationType.HOT_LEAD,
                title=f"Hot Lead: {call.customer.first_name} {call.customer.last_name}",
                message=f"Customer showed high interest during call. Summary: {call.summary[:100]}...",
                data={
                    "call_id": str(call.id),
                    "customer_id": str(call.customer_id),
                    "campaign_id": str(call.campaign_id),
                    "interest_level": call.interest_level.value,
                },
                campaign_id=call.campaign_id,
                call_id=call.id,
            )
            notifications.append(notification)

        return notifications[0] if notifications else None

    async def create_callback_notification(self, callback) -> Notification:
        """Create notification for scheduled callback"""
        if callback.assignee_id:
            return await self.create(
                user_id=callback.assignee_id,
                organization_id=callback.campaign.organization_id,
                notification_type=NotificationType.CALLBACK_SCHEDULED,
                title=f"Callback Scheduled: {callback.customer.first_name} {callback.customer.last_name}",
                message=f"Callback scheduled for {callback.scheduled_at.strftime('%Y-%m-%d %H:%M')}",
                data={
                    "callback_id": str(callback.id),
                    "customer_id": str(callback.customer_id),
                    "scheduled_at": callback.scheduled_at.isoformat(),
                },
                campaign_id=callback.campaign_id,
            )

    async def create_human_followup_notification(self, call) -> Notification:
        """Create notification for human follow-up required"""
        from app.models.user import User
        from app.models.enums import UserRole

        managers = await self.db.execute(
            select(User).where(
                and_(
                    User.organization_id == call.campaign.organization_id,
                    User.role.in_([UserRole.ADMIN, UserRole.MANAGER]),
                    User.is_active == True,
                )
            )
        )

        notifications = []
        for user in managers.scalars().all():
            notification = await self.create(
                user_id=user.id,
                organization_id=call.campaign.organization_id,
                notification_type=NotificationType.HUMAN_FOLLOWUP_REQUIRED,
                title=f"Human Follow-up Required: {call.customer.first_name} {call.customer.last_name}",
                message=f"AI flagged call for human follow-up. Reason: {call.human_followup_reason}",
                data={
                    "call_id": str(call.id),
                    "customer_id": str(call.customer_id),
                    "reason": call.human_followup_reason,
                },
                campaign_id=call.campaign_id,
                call_id=call.id,
            )
            notifications.append(notification)

        return notifications[0] if notifications else None

    async def list_notifications(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
    ) -> tuple[List[Notification], int]:
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read == False)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        query = query.order_by(Notification.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        notifications = result.scalars().all()

        return list(notifications), total

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> Optional[Notification]:
        notification = await self.db.scalar(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id,
                )
            )
        )
        if not notification:
            return None

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_all_read(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                )
            )
        )
        notifications = result.scalars().all()

        for n in notifications:
            n.is_read = True
            n.read_at = datetime.utcnow()

        await self.db.commit()
        return len(notifications)

    async def get_unread_count(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(Notification.id)).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False,
                )
            )
        )
        return result.scalar() or 0