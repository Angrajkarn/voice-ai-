# Campaign Service

import builtins
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from app.models.call import Call
from app.models.callback import Callback
from app.models.campaign import Campaign
from app.models.enums import CampaignStatus, CustomerStatus, IntegrationType
from app.models.integration import Integration
from app.core.config import settings
from app.models.campaign_customer import CampaignCustomer
from app.models.customer import Customer
from app.schemas.campaign import CampaignCreate, CampaignMetrics, CampaignUpdate
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class CampaignService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: CampaignCreate, owner_id: UUID, organization_id: UUID) -> Campaign:
        customer_ids = list(dict.fromkeys(data.customer_ids))
        campaign = Campaign(
            **data.model_dump(exclude={"customer_ids"}),
            owner_id=owner_id,
            organization_id=organization_id,
        )
        self.db.add(campaign)
        await self.db.flush()

        result = await self.db.execute(
            select(Customer).where(and_(
                Customer.id.in_(customer_ids),
                Customer.organization_id == organization_id,
                Customer.do_not_call.is_(False),
                Customer.status.notin_([CustomerStatus.DO_NOT_CALL, CustomerStatus.OPTED_OUT]),
            ))
        )
        customers = list(result.scalars().all())
        if len(customers) != len(customer_ids):
            raise ValueError("One or more selected customers are unavailable or marked do-not-call/opted-out.")

        for customer in customers:
            self.db.add(CampaignCustomer(
                campaign_id=campaign.id,
                customer_id=customer.id,
            ))
        campaign.total_customers = len(customers)
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def get_by_id(self, campaign_id: UUID, organization_id: UUID) -> Campaign | None:
        result = await self.db.execute(
            select(Campaign)
            .options(
                selectinload(Campaign.owner),
                selectinload(Campaign.organization),
            )
            .where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.organization_id == organization_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Campaign], int]:
        query = select(Campaign).where(Campaign.organization_id == organization_id)

        if status:
            query = query.where(Campaign.status == status)

        if search:
            query = query.where(
                or_(
                    Campaign.name.ilike(f"%{search}%"),
                    Campaign.description.ilike(f"%{search}%"),
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Apply sorting
        sort_column = getattr(Campaign, sort_by, Campaign.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        campaigns = result.scalars().all()

        return list(campaigns), total

    async def update(self, campaign_id: UUID, organization_id: UUID, data: CampaignUpdate) -> Campaign | None:
        campaign = await self.get_by_id(campaign_id, organization_id)
        if not campaign:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(campaign, key, value)

        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def delete(self, campaign_id: UUID, organization_id: UUID) -> bool:
        campaign = await self.get_by_id(campaign_id, organization_id)
        if not campaign:
            return False

        await self.db.delete(campaign)
        await self.db.commit()
        return True

    async def start(self, campaign_id: UUID, organization_id: UUID) -> Campaign | None:
        campaign = await self.get_by_id(campaign_id, organization_id)
        if not campaign:
            return None
        if campaign.status not in ["DRAFT", "READY", "PAUSED", "STOPPED"]:
            raise ValueError(f"Cannot start campaign in status: {campaign.status}")
        if len((campaign.ai_instructions or "").strip()) < 50:
            raise ValueError("AI instructions must be at least 50 characters before starting.")
        if len((campaign.opening_script or "").strip()) < 20:
            raise ValueError("Opening script must be at least 20 characters before starting.")
        if not settings.OPENAI_API_KEY:
            raise ValueError("Set OPENAI_API_KEY on the backend to enable the campaign's AI voice responses.")
        integration = await self.db.scalar(select(Integration).where(and_(
            Integration.organization_id == organization_id, Integration.type == IntegrationType.TWILIO,
            Integration.is_active.is_(True), or_(Integration.campaign_id == campaign.id, Integration.campaign_id.is_(None)),
        )).order_by((Integration.campaign_id == campaign.id).desc()).limit(1))
        config = integration.config if integration else {}
        if isinstance(config, str):
            import json
            config = json.loads(config)
        from_number = config.get("phone_number") if config else None
        if not from_number:
            raise ValueError("Connect Twilio and configure an outgoing phone number in Integrations before starting.")
        if not settings.TWILIO_WEBHOOK_BASE_URL:
            raise ValueError("Set TWILIO_WEBHOOK_BASE_URL on the backend to your public HTTPS API URL before starting calls.")
        members = await self.db.execute(select(Customer).join(CampaignCustomer, CampaignCustomer.customer_id == Customer.id).where(and_(
            CampaignCustomer.campaign_id == campaign.id, Customer.organization_id == organization_id,
            Customer.do_not_call.is_(False), Customer.status.notin_([CustomerStatus.DO_NOT_CALL, CustomerStatus.OPTED_OUT]),
        )))
        customers = list(members.scalars().all())
        if not customers:
            raise ValueError("Add at least one eligible customer to this campaign before starting.")
        existing_ids = set((await self.db.scalars(select(Call.customer_id).where(Call.campaign_id == campaign.id))).all())
        for customer in customers:
            if customer.id not in existing_ids and customer.call_attempts < customer.max_call_attempts:
                self.db.add(Call(campaign_id=campaign.id, customer_id=customer.id, from_number=from_number, to_number=customer.phone))
        campaign.total_customers = len(customers)
        campaign.status = CampaignStatus.RUNNING
        campaign.started_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def pause(self, campaign_id: UUID, organization_id: UUID) -> Campaign | None:
        campaign = await self.get_by_id(campaign_id, organization_id)
        if not campaign:
            return None

        if campaign.status != "RUNNING":
            raise ValueError(f"Cannot pause campaign in status: {campaign.status}")

        campaign.status = CampaignStatus.PAUSED
        campaign.paused_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def stop(self, campaign_id: UUID, organization_id: UUID) -> Campaign | None:
        campaign = await self.get_by_id(campaign_id, organization_id)
        if not campaign:
            return None

        if campaign.status not in ["RUNNING", "PAUSED", "READY"]:
            raise ValueError(f"Cannot stop campaign in status: {campaign.status}")

        campaign.status = CampaignStatus.STOPPED
        campaign.stopped_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(campaign)
        return campaign

    async def validate(self, campaign_id: UUID, organization_id: UUID) -> dict[str, Any]:
        campaign = await self.get_by_id(campaign_id, organization_id)
        if not campaign:
            return {"valid": False, "errors": ["Campaign not found"], "warnings": []}

        errors = []
        warnings = []

        # Check AI configuration
        if not campaign.ai_instructions or len(campaign.ai_instructions.strip()) < 50:
            errors.append("AI instructions must be at least 50 characters")

        if not campaign.opening_script or len(campaign.opening_script.strip()) < 20:
            errors.append("Opening script must be at least 20 characters")

        # Check calling configuration
        if campaign.max_calls_per_day < 1:
            errors.append("Max calls per day must be at least 1")

        if campaign.delay_between_calls < 0:
            errors.append("Delay between calls cannot be negative")

        # Check time window
        try:
            start_hour, start_min = map(int, campaign.calling_window_start.split(":"))
            end_hour, end_min = map(int, campaign.calling_window_end.split(":"))
            if start_hour * 60 + start_min >= end_hour * 60 + end_min:
                errors.append("Calling window end must be after start")
        except ValueError:
            errors.append("Invalid calling window format")

        # Check integrations
        if campaign.sheets_sync_enabled and not campaign.sheets_spreadsheet_id:
            warnings.append("Google Sheets sync enabled but no spreadsheet ID configured")

        # Check Twilio integration
        from app.models.enums import IntegrationType
        from app.models.integration import Integration
        twilio_integration = await self.db.scalar(
            select(Integration).where(
                and_(
                    Integration.organization_id == organization_id,
                    Integration.type == IntegrationType.TWILIO,
                    Integration.is_active.is_(True),
                )
            )
        )
        if not twilio_integration:
            warnings.append("No active Twilio integration found")

        # Check OpenAI integration
        openai_integration = await self.db.scalar(
            select(Integration).where(
                and_(
                    Integration.organization_id == organization_id,
                    Integration.type == IntegrationType.OPENAI,
                    Integration.is_active.is_(True),
                )
            )
        )
        if not openai_integration:
            warnings.append("No active OpenAI integration found")

        # Check customers
        customer_count = await self.db.scalar(
            select(func.count(CampaignCustomer.id)).where(
                CampaignCustomer.campaign_id == campaign_id
            )
        )
        if customer_count == 0:
            warnings.append("No customers assigned to campaign")

        campaign.total_customers = customer_count or 0

        is_valid = len(errors) == 0
        if is_valid:
            campaign.status = CampaignStatus.READY

        await self.db.commit()

        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
        }

    async def get_metrics(self, campaign_id: UUID, organization_id: UUID) -> CampaignMetrics | None:
        campaign = await self.get_by_id(campaign_id, organization_id)
        if not campaign:
            return None

        # Get call statistics
        call_stats = await self.db.execute(
            select(
                func.count(Call.id).label("total_calls"),
                func.count(Call.id).filter(Call.status == "COMPLETED").label("completed_calls"),
                func.count(Call.id).filter(Call.status.in_(["FAILED", "BUSY", "NO_ANSWER", "VOICEMAIL", "INVALID_NUMBER"])).label("failed_calls"),
                func.count(Call.id).filter(Call.status.in_(["COMPLETED", "BUSY", "NO_ANSWER", "VOICEMAIL"])).label("answered_calls"),
                func.count(Call.id).filter(Call.interest_level.in_(["HOT", "WARM"])).label("interested_count"),
                func.avg(Call.duration).filter(Call.duration.isnot(None)).label("avg_duration"),
            ).where(Call.campaign_id == campaign_id)
        )
        stats = call_stats.first()
        if stats is None:
            raise RuntimeError("Campaign call metrics query returned no row")

        # Get callback count
        callback_count = await self.db.scalar(
            select(func.count(Callback.id)).where(
                and_(
                    Callback.campaign_id == campaign_id,
                    Callback.status == "SCHEDULED",
                )
            )
        )

        # Get opt-out count
        opt_out_count = await self.db.scalar(
            select(func.count(Customer.id)).where(
                and_(
                    select(CampaignCustomer.id).where(and_(CampaignCustomer.customer_id == Customer.id, CampaignCustomer.campaign_id == campaign_id)).exists(),
                    Customer.status == "OPTED_OUT",
                )
            )
        )

        total_calls = stats.total_calls or 0
        completed_calls = stats.completed_calls or 0
        failed_calls = stats.failed_calls or 0
        answered_calls = stats.answered_calls or 0
        avg_duration = float(stats.avg_duration or 0)

        return CampaignMetrics(
            total_customers=campaign.total_customers,
            total_calls=total_calls,
            completed_calls=completed_calls,
            failed_calls=failed_calls,
            answered_calls=answered_calls,
            interested_count=stats.interested_count or 0,
            callback_count=callback_count or 0,
            opt_out_count=opt_out_count or 0,
            average_duration=round(avg_duration, 1),
            success_rate=round((completed_calls / total_calls * 100) if total_calls > 0 else 0, 2),
            answer_rate=round((answered_calls / total_calls * 100) if total_calls > 0 else 0, 2),
        )

    async def get_daily_analytics(
        self,
        campaign_id: UUID,
        organization_id: UUID,
        days: int = 30,
    ) -> builtins.list[dict[str, Any]]:
        campaign = await self.get_by_id(campaign_id, organization_id)
        if not campaign:
            return []

        start_date = datetime.utcnow() - timedelta(days=days)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # This would be a complex query in production
        # For now, return empty list
        return []