# Call Service

import builtins
from datetime import datetime
from uuid import UUID

from app.models.call import Call
from app.core.crypto import decrypt_secret
from app.models.campaign import Campaign
from app.models.call_recording import CallRecording
from app.models.call_transcript import CallTranscript
from app.models.enums import (
    CallDirection,
    CallStatus,
    InterestLevel,
)
from app.schemas.call import CallCreate, CallUpdate
from app.schemas.callback import CallbackCreate
from app.services.twilio_service import TwilioService
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class CallService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.twilio = TwilioService()

    async def create(self, data: CallCreate) -> Call:
        call = Call(
            **data.model_dump(),
            queued_at=datetime.utcnow(),
        )
        self.db.add(call)
        await self.db.commit()
        await self.db.refresh(call)
        return call

    async def get_by_id(self, call_id: UUID) -> Call | None:
        result = await self.db.execute(
            select(Call)
            .options(
                selectinload(Call.campaign),
                selectinload(Call.customer),
                selectinload(Call.agent),
                selectinload(Call.transcript),
                selectinload(Call.recording),
            )
            .where(Call.id == call_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        campaign_id: UUID | None = None,
        customer_id: UUID | None = None,
        status: str | None = None,
        direction: str | None = None,
        interest_level: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        organization_id: UUID | None = None,
    ) -> tuple[list[Call], int]:
        query = select(Call).join(Campaign, Call.campaign_id == Campaign.id)

        if organization_id:
            query = query.where(Campaign.organization_id == organization_id)

        if campaign_id:
            query = query.where(Call.campaign_id == campaign_id)

        if customer_id:
            query = query.where(Call.customer_id == customer_id)

        if status:
            query = query.where(Call.status == status)

        if direction:
            query = query.where(Call.direction == direction)

        if interest_level:
            query = query.where(Call.interest_level == interest_level)

        if date_from:
            query = query.where(Call.created_at >= date_from)

        if date_to:
            query = query.where(Call.created_at <= date_to)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Apply sorting and pagination
        query = query.order_by(Call.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        calls = result.scalars().all()

        return list(calls), total

    async def update(self, call_id: UUID, data: CallUpdate) -> Call | None:
        call = await self.get_by_id(call_id)
        if not call:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(call, key, value)

        await self.db.commit()
        await self.db.refresh(call)
        return call

    async def get_next_queued_call(self, campaign_id: UUID) -> Call | None:
        """Get the next call to process for a campaign"""
        result = await self.db.execute(
            select(Call)
            .where(
                and_(
                    Call.campaign_id == campaign_id,
                    Call.status == CallStatus.QUEUED,
                )
            )
            .order_by(Call.queued_at.asc())
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        return result.scalar_one_or_none()

    async def initiate_call(self, call_id: UUID) -> bool:
        """Initiate an outbound call via Twilio"""
        call = await self.get_by_id(call_id)
        if not call:
            return False

        try:
            # Update status to initiating
            call.status = CallStatus.INITIATING
            call.initiated_at = datetime.utcnow()
            await self.db.commit()

            # Get Twilio config from campaign integrations
            from app.models.enums import IntegrationType
            from app.models.integration import Integration

            integration = await self.db.scalar(select(Integration).where(and_(
                Integration.organization_id == call.campaign.organization_id,
                Integration.type == IntegrationType.TWILIO,
                Integration.is_active.is_(True),
                or_(Integration.campaign_id == call.campaign_id, Integration.campaign_id.is_(None)),
            )).order_by((Integration.campaign_id == call.campaign_id).desc()).limit(1))

            if not integration:
                raise ValueError("No active Twilio integration for this campaign")

            import json
            config = integration.config
            if isinstance(config, str): config = json.loads(config)
            from_number = config.get("phone_number")
            campaign_twilio = TwilioService(account_sid=config.get("account_sid"), auth_token=decrypt_secret(config.get("auth_token", "")), phone_number=from_number)
            if not isinstance(from_number, str) or not from_number:
                raise ValueError("Twilio integration is missing its phone number")

            call_sid = await campaign_twilio.make_call(
                to_number=call.to_number,
                from_number=from_number,
                campaign_id=str(call.campaign_id),
                call_id=str(call.id),
            )

            if call_sid:
                call.call_sid = call_sid
                call.status = CallStatus.RINGING
                await self.db.commit()
                return True
            else:
                call.status = CallStatus.FAILED
                call.failure_reason = "Failed to initiate call via Twilio"
                await self.db.commit()
                return False

        except Exception as e:
            call.status = CallStatus.FAILED
            call.failure_reason = str(e)
            await self.db.commit()
            return False

    async def handle_twilio_status(self, call_sid: str, status: str, duration: str | None = None) -> Call | None:
        """Handle Twilio status callback"""
        call = await self.db.scalar(select(Call).where(Call.call_sid == call_sid))
        if not call:
            return None

        old_status = call.status

        if status == "ringing":
            call.status = CallStatus.RINGING
        elif status == "in-progress":
            call.status = CallStatus.IN_PROGRESS
            if not call.answered_at:
                call.answered_at = datetime.utcnow()
        elif status == "completed":
            call.status = CallStatus.COMPLETED
            call.ended_at = datetime.utcnow()
            if call.answered_at:
                call.duration = int((call.ended_at - call.answered_at).total_seconds())
            if duration:
                call.billable_duration = int(duration)
            call.disposition = "COMPLETED"
        elif status == "busy":
            call.status = CallStatus.BUSY
            call.ended_at = datetime.utcnow()
            call.disposition = "BUSY"
        elif status == "no-answer":
            call.status = CallStatus.NO_ANSWER
            call.ended_at = datetime.utcnow()
            call.disposition = "NO_ANSWER"
        elif status == "failed":
            call.status = CallStatus.FAILED
            call.ended_at = datetime.utcnow()
            call.disposition = "FAILED"
        elif status == "canceled":
            call.status = CallStatus.CANCELLED
            call.ended_at = datetime.utcnow()
            call.disposition = "CANCELLED"

        await self.db.commit()

        # If call completed, trigger post-call automation
        if old_status != CallStatus.COMPLETED and call.status == CallStatus.COMPLETED:
            await self._trigger_post_call_automation(call)

        return call

    async def handle_recording(self, call_sid: str, recording_sid: str, recording_url: str, duration: str) -> CallRecording | None:
        """Handle recording callback"""
        call = await self.db.scalar(select(Call).where(Call.call_sid == call_sid))
        if not call:
            return None

        call.recording_sid = recording_sid
        call.recording_url = recording_url
        await self.db.commit()

        # Create recording record
        recording = CallRecording(
            call_id=call.id,
            url=recording_url,
            provider="twilio",
            provider_id=recording_sid,
            format="mp3",
            duration=float(duration),
            size_bytes=0,  # Would be fetched from Twilio
            channels=1,
            sample_rate=8000,
        )
        self.db.add(recording)
        await self.db.commit()
        await self.db.refresh(recording)

        return recording

    async def handle_transcription(self, call_sid: str, transcription_sid: str, transcription_text: str) -> CallTranscript | None:
        """Handle transcription callback"""
        call = await self.db.scalar(select(Call).where(Call.call_sid == call_sid))
        if not call:
            return None

        call.transcript_text = transcription_text
        call.transcript_url = f"https://api.twilio.com/.../Transcriptions/{transcription_sid}"
        await self.db.commit()

        # Create transcript record
        transcript = CallTranscript(
            call_id=call.id,
            full_text=transcription_text,
            segments=[],  # Would be parsed from detailed transcription
            language=call.campaign.language if call.campaign else "en-IN",
            word_count=len(transcription_text.split()),
            duration=call.duration or 0,
        )
        self.db.add(transcript)
        await self.db.commit()
        await self.db.refresh(transcript)

        return transcript

    async def _trigger_post_call_automation(self, call: Call) -> None:
        """Trigger post-call automation workflows"""
        from app.models.automation_log import AutomationLog
        from app.services.ai_agent_service import AIAgentService
        from app.services.callback_service import CallbackService
        from app.services.google_sheets_service import GoogleSheetsService
        from app.services.notification_service import NotificationService
        from app.services.suppression_service import SuppressionService

        # AI Analysis of call
        ai_service = AIAgentService()
        analysis = await ai_service.analyze_call(call)

        # Update call with analysis
        call.interest_level = analysis.get("interest_level", InterestLevel.UNKNOWN)
        call.customer_intent = analysis.get("customer_intent")
        call.objections = analysis.get("objections", [])
        call.questions_asked = analysis.get("questions_asked", [])
        call.summary = analysis.get("summary")
        call.sentiment = analysis.get("sentiment")
        call.requires_human_followup = analysis.get("requires_human_followup", False)
        call.human_followup_reason = analysis.get("human_followup_reason")

        # Update customer status based on interest
        customer = call.customer
        if call.interest_level == InterestLevel.HOT:
            customer.status = "HOT_LEAD"
            customer.interest_level = InterestLevel.HOT
        elif call.interest_level == InterestLevel.WARM:
            customer.status = "WARM_LEAD"
            customer.interest_level = InterestLevel.WARM
        elif call.interest_level == InterestLevel.COLD:
            customer.status = "COLD_LEAD"
            customer.interest_level = InterestLevel.COLD

        customer.last_call_at = call.ended_at
        customer.last_call_status = call.status
        customer.last_call_duration = call.duration
        customer.call_attempts += 1

        # Check for callback request
        if analysis.get("callback_requested"):
            callback_service = CallbackService(self.db)
            callback_date = analysis.get("callback_date")
            if callback_date:
                await callback_service.create(CallbackCreate(
                    campaign_id=call.campaign_id,
                    customer_id=call.customer_id,
                    source_call_id=call.id,
                    scheduled_at=callback_date,
                    scheduled_timezone=customer.timezone,
                    customer_notes=analysis.get("callback_notes"),
                    ai_notes=analysis.get("callback_ai_notes"),
                ))

        # Check for opt-out
        if analysis.get("opt_out_requested"):
            suppression_service = SuppressionService(self.db)
            await suppression_service.add_to_suppression(
                phone=customer.phone,
                reason="OPT_OUT",
                organization_id=call.campaign.organization_id,
                customer_id=customer.id,
            )
            customer.status = "OPTED_OUT"
            customer.do_not_call = True
            customer.opted_out_at = datetime.utcnow()
            customer.opt_out_reason = analysis.get("opt_out_reason")

        # Update campaign stats
        campaign = call.campaign
        if call.status == CallStatus.COMPLETED:
            campaign.completed_calls += 1
            if call.interest_level in [InterestLevel.HOT, InterestLevel.WARM]:
                campaign.interested_count += 1
        else:
            campaign.failed_calls += 1

        # Google Sheets sync
        if campaign.sheets_sync_enabled and campaign.sheets_auto_sync:
            sheets_service = GoogleSheetsService(self.db)
            await sheets_service.sync_call(call)

        # Create automation log
        automation_log = AutomationLog(
            campaign_id=call.campaign_id,
            trigger_type="CALL_COMPLETED",
            trigger_data={"call_id": str(call.id), "status": call.status.value},
            action_type="UPDATE_SHEETS" if campaign.sheets_sync_enabled else "NONE",
            action_data={},
            status="COMPLETED",
            completed_at=datetime.utcnow(),
        )
        self.db.add(automation_log)

        # Send notifications
        if call.interest_level == InterestLevel.HOT:
            notification_service = NotificationService(self.db)
            await notification_service.create_hot_lead_notification(call)

        await self.db.commit()

    async def retry_failed_calls(self, campaign_id: UUID, max_retries: int = 3) -> int:
        """Retry failed calls that haven't exceeded max retries"""
        from app.models.campaign_customer import CampaignCustomer

        # Get calls that failed and can be retried
        failed_calls = await self.db.execute(
            select(Call).where(
                and_(
                    Call.campaign_id == campaign_id,
                    Call.status.in_([CallStatus.FAILED, CallStatus.NO_ANSWER, CallStatus.BUSY]),
                )
            )
        )
        calls = failed_calls.scalars().all()

        retried = 0
        for call in calls:
            # Check if customer has exceeded max attempts
            cc = await self.db.scalar(
                select(CampaignCustomer).where(
                    and_(
                        CampaignCustomer.campaign_id == campaign_id,
                        CampaignCustomer.customer_id == call.customer_id,
                    )
                )
            )
            if cc and cc.called_at and (datetime.utcnow() - cc.called_at).days < 1:
                # Already called today, skip
                continue

            # Create new call for retry
            new_call = Call(
                campaign_id=campaign_id,
                customer_id=call.customer_id,
                direction=CallDirection.OUTBOUND,
                status=CallStatus.QUEUED,
                from_number=call.from_number,
                to_number=call.to_number,
                queued_at=datetime.utcnow(),
            )
            self.db.add(new_call)
            retried += 1

        await self.db.commit()
        return retried

    async def get_live_calls(self, campaign_id: UUID) -> builtins.list[Call]:
        """Get currently active calls for a campaign"""
        result = await self.db.execute(
            select(Call)
            .where(
                and_(
                    Call.campaign_id == campaign_id,
                    Call.status.in_([CallStatus.INITIATING, CallStatus.RINGING, CallStatus.IN_PROGRESS]),
                )
            )
            .order_by(Call.initiated_at.asc())
        )
        return list(result.scalars().all())