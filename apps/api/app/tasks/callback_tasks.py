# Callback processing tasks

from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing: List
from uuid import UUID
from datetime import datetime
import asyncio

from app.core.config import settings
from app.services.callback_service import CallbackService
from app.services.call_service import CallService


engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@shared_task
def process_due_callbacks():
    """Process callbacks that are due to be made"""
    async def _process():
        async with AsyncSessionLocal() as db:
            callback_service = CallbackService(db)
            processed = await callback_service.process_due_callbacks()
            return {"processed": processed}

    return asyncio.run(_process())


@shared_task
def send_callback_reminders():
    """Send reminders for upcoming callbacks"""
    async def _send():
        async with AsyncSessionLocal() as db:
            callback_service = CallbackService(db)
            sent = await callback_service.send_reminders()
            return {"reminders_sent": sent}

    return asyncio.run(_send())


@shared_task(bind=True, max_retries=3)
def execute_callback(self, callback_id: str):
    """Execute a specific callback by creating a call"""
    async def _execute():
        async with AsyncSessionLocal() as db:
            callback_service = CallbackService(db)
            callback = await callback_service.get_by_id(UUID(callback_id))
            if not callback:
                return {"status": "not_found"}

            # Check if campaign is running
            if callback.campaign.status != "RUNNING":
                return {"status": "skipped", "reason": "Campaign not running"}

            # Check calling window
            if not callback_service._is_within_calling_window(callback.campaign):
                return {"status": "skipped", "reason": "Outside calling window"}

            # Check customer is callable
            if callback.customer.do_not_call or callback.customer.status == "OPTED_OUT":
                callback.status = "CANCELLED"
                await db.commit()
                return {"status": "cancelled", "reason": "Customer opted out"}

            # Create call
            call_service = CallService(db)
            call = await call_service.create({
                "campaign_id": callback.campaign_id,
                "customer_id": callback.customer_id,
                "direction": "OUTBOUND",
                "from_number": callback.campaign.integrations[0].config.get("phone_number") if callback.campaign.integrations else "+15551234567",
                "to_number": callback.customer.phone,
            })

            callback.result_call_id = call.id
            callback.status = "INITIATED"
            await db.commit()

            # Initiate call
            success = await call_service.initiate_call(call.id)
            return {"status": "initiated" if success else "failed", "call_id": str(call.id)}

    try:
        return asyncio.run(_execute())
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def check_callback_outcomes():
    """Check outcomes of completed callback calls"""
    async def _check():
        async with AsyncSessionLocal() as db:
            from app.models.callback import Callback
            from app.models.enums import CallbackStatus, CallStatus
            from sqlalchemy import select

            # Get callbacks with result calls that completed
            callbacks = await db.execute(
                select(Callback).where(
                    and_(
                        Callback.result_call_id.isnot(None),
                        Callback.status == CallbackStatus.SCHEDULED,
                    )
                ).join(Callback.result_call)
                .where(Call.status.in_([CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.NO_ANSWER, CallStatus.BUSY]))
            )

            updated = 0
            for callback in callbacks.scalars().all():
                result_call = callback.result_call
                if result_call.status == CallStatus.COMPLETED:
                    callback.status = CallbackStatus.COMPLETED
                    callback.completed_at = datetime.utcnow()
                    callback.outcome = result_call.summary or "Completed"
                elif result_call.status in [CallStatus.FAILED, CallStatus.NO_ANSWER, CallStatus.BUSY]:
                    callback.status = CallbackStatus.FAILED
                    callback.completed_at = datetime.utcnow()
                    callback.outcome = f"Call {result_call.status.value.lower()}"
                updated += 1

            await db.commit()
            return {"updated": updated}

    return asyncio.run(_check())