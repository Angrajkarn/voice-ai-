# Callback Service

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.models.callback import Callback
from app.models.campaign import Campaign
from app.models.customer import Customer
from app.models.call import Call
from app.models.enums import CallbackStatus, CallStatus
from app.schemas.callback import CallbackCreate, CallbackUpdate
from app.services.call_service import CallService
from app.core.config import settings


class CallbackService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.call_service = CallService(db)

    async def create(self, data: CallbackCreate) -> Callback:
        callback = Callback(
            **data.model_dump(),
        )
        self.db.add(callback)
        await self.db.commit()
        await self.db.refresh(callback)
        return callback

    async def get_by_id(self, callback_id: UUID) -> Optional[Callback]:
        result = await self.db.execute(
            select(Callback)
            .options(
                selectinload(Callback.campaign),
                selectinload(Callback.customer),
                selectinload(Callback.assignee),
                selectinload(Callback.source_call),
                selectinload(Callback.result_call),
            )
            .where(Callback.id == callback_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        campaign_id: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        status: Optional[str] = None,
        assignee_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[List[Callback], int]:
        query = select(Callback)

        if campaign_id:
            query = query.where(Callback.campaign_id == campaign_id)

        if customer_id:
            query = query.where(Callback.customer_id == customer_id)

        if status:
            query = query.where(Callback.status == status)

        if assignee_id:
            query = query.where(Callback.assignee_id == assignee_id)

        if date_from:
            query = query.where(Callback.scheduled_at >= date_from)

        if date_to:
            query = query.where(Callback.scheduled_at <= date_to)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Apply sorting and pagination
        query = query.order_by(Callback.scheduled_at.asc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        callbacks = result.scalars().all()

        return list(callbacks), total

    async def update(self, callback_id: UUID, data: CallbackUpdate) -> Optional[Callback]:
        callback = await self.get_by_id(callback_id)
        if not callback:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(callback, key, value)

        await self.db.commit()
        await self.db.refresh(callback)
        return callback

    async def delete(self, callback_id: UUID) -> bool:
        callback = await self.get_by_id(callback_id)
        if not callback:
            return False

        await self.db.delete(callback)
        await self.db.commit()
        return True

    async def complete(self, callback_id: UUID, outcome: str) -> Optional[Callback]:
        callback = await self.get_by_id(callback_id)
        if not callback:
            return None

        callback.status = CallbackStatus.COMPLETED
        callback.completed_at = datetime.utcnow()
        callback.outcome = outcome

        # Update customer
        customer = callback.customer
        customer.status = "CONTACTED"

        await self.db.commit()
        await self.db.refresh(callback)
        return callback

    async def get_due_callbacks(self, campaign_id: Optional[UUID] = None) -> List[Callback]:
        """Get callbacks that are due to be made"""
        now = datetime.utcnow()

        query = select(Callback).where(
            and_(
                Callback.status == CallbackStatus.SCHEDULED,
                Callback.scheduled_at <= now,
            )
        )

        if campaign_id:
            query = query.where(Callback.campaign_id == campaign_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_upcoming_callbacks(self, campaign_id: UUID, hours: int = 24) -> List[Callback]:
        """Get callbacks scheduled in the next N hours"""
        now = datetime.utcnow()
        future = now + timedelta(hours=hours)

        result = await self.db.execute(
            select(Callback)
            .where(
                and_(
                    Callback.campaign_id == campaign_id,
                    Callback.status == CallbackStatus.SCHEDULED,
                    Callback.scheduled_at >= now,
                    Callback.scheduled_at <= future,
                )
            )
            .order_by(Callback.scheduled_at.asc())
        )
        return list(result.scalars().all())

    async def send_reminders(self) -> int:
        """Send reminders for callbacks due in the next 15 minutes"""
        now = datetime.utcnow()
        reminder_time = now + timedelta(minutes=settings.CALLBACK_REMINDER_MINUTES)

        callbacks = await self.db.execute(
            select(Callback).where(
                and_(
                    Callback.status == CallbackStatus.SCHEDULED,
                    Callback.reminder_sent == False,
                    Callback.scheduled_at <= reminder_time,
                    Callback.scheduled_at > now,
                )
            )
        )

        count = 0
        for callback in callbacks.scalars().all():
            callback.reminder_sent = True
            callback.reminder_sent_at = datetime.utcnow()
            count += 1

        await self.db.commit()
        return count

    async def process_due_callbacks(self) -> int:
        """Process due callbacks by creating new calls"""
        due_callbacks = await self.get_due_callbacks()
        processed = 0

        for callback in due_callbacks:
            # Check if campaign is still running
            campaign = callback.campaign
            if campaign.status != "RUNNING":
                continue

            # Check if customer is still callable
            customer = callback.customer
            if customer.do_not_call or customer.status == "OPTED_OUT":
                callback.status = CallbackStatus.CANCELLED
                continue

            # Check calling window
            if not self._is_within_calling_window(campaign):
                continue

            # Create new call for callback
            call = await self.call_service.create(
                CallCreate(
                    campaign_id=campaign.id,
                    customer_id=customer.id,
                    direction="OUTBOUND",
                    from_number=campaign.integrations[0].config.get("phone_number") if campaign.integrations else "+15551234567",
                    to_number=customer.phone,
                )
            )

            callback.result_call_id = call.id
            processed += 1

        await self.db.commit()
        return processed

    def _is_within_calling_window(self, campaign: Campaign) -> bool:
        """Check if current time is within campaign's calling window"""
        import pytz
        tz = pytz.timezone(campaign.calling_timezone)
        now = datetime.now(tz)

        start_hour, start_min = map(int, campaign.calling_window_start.split(":"))
        end_hour, end_min = map(int, campaign.calling_window_end.split(":"))

        current_minutes = now.hour * 60 + now.minute
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min

        if current_minutes < start_minutes or current_minutes > end_minutes:
            return False

        if campaign.skip_weekends and now.weekday() >= 5:
            return False

        return True