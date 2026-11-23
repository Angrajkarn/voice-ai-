# Analytics Service - Handles analytics and reporting

from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from uuid import UUID

from app.models.call import Call
from app.models.campaign import Campaign
from app.models.customer import Customer
from app.models.callback import Callback
from app.models.organization import Organization
from app.models.enums import CallStatus, InterestLevel, CustomerStatus, CallbackStatus
from app.schemas.analytics import CallAnalytics, CampaignAnalytics, OrganizationAnalytics, DashboardMetrics
from app.core.config import settings


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_metrics(self, organization_id: UUID) -> DashboardMetrics:
        """Get organization-wide dashboard metrics"""
        # Total customers
        total_customers = await self.db.scalar(
            select(func.count(Customer.id)).where(Customer.organization_id == organization_id)
        ) or 0

        # Call statistics
        call_stats = await self.db.execute(
            select(
                func.count(Call.id).label("total_calls"),
                func.count(Call.id).filter(Call.status == CallStatus.COMPLETED).label("completed_calls"),
                func.count(Call.id).filter(Call.status.in_([
                    CallStatus.FAILED, CallStatus.BUSY, CallStatus.NO_ANSWER,
                    CallStatus.VOICEMAIL, CallStatus.INVALID_NUMBER
                ])).label("failed_calls"),
                func.count(Call.id).filter(Call.status.in_([
                    CallStatus.COMPLETED, CallStatus.BUSY, CallStatus.NO_ANSWER, CallStatus.VOICEMAIL
                ])).label("answered_calls"),
                func.avg(Call.duration).filter(Call.duration.isnot(None)).label("avg_duration"),
            ).where(Call.campaign.has(organization_id=organization_id))
        )
        stats = call_stats.first()

        # Interest levels
        interest_stats = await self.db.execute(
            select(
                func.count(Customer.id).filter(Customer.interest_level == InterestLevel.HOT).label("hot_leads"),
                func.count(Customer.id).filter(Customer.interest_level == InterestLevel.WARM).label("warm_leads"),
                func.count(Customer.id).filter(Customer.interest_level.in_([InterestLevel.HOT, InterestLevel.WARM])).label("interested_customers"),
            ).where(Customer.organization_id == organization_id)
        )
        interest = interest_stats.first()

        # Callbacks
        callbacks_scheduled = await self.db.scalar(
            select(func.count(Callback.id))
            .where(
                and_(
                    Callback.campaign.has(organization_id=organization_id),
                    Callback.status == CallbackStatus.SCHEDULED,
                )
            )
        ) or 0

        # Opt-outs
        opt_outs = await self.db.scalar(
            select(func.count(Customer.id)).where(
                and_(
                    Customer.organization_id == organization_id,
                    Customer.status == CustomerStatus.OPTED_OUT,
                )
            )
        ) or 0

        total_calls = stats.total_calls or 0
        completed_calls = stats.completed_calls or 0
        failed_calls = stats.failed_calls or 0
        answered_calls = stats.answered_calls or 0
        avg_duration = float(stats.avg_duration or 0)

        return DashboardMetrics(
            total_customers=total_customers,
            total_calls=total_calls,
            completed_calls=completed_calls,
            failed_calls=failed_calls,
            answered_calls=answered_calls,
            interested_customers=interest.interested_customers or 0,
            hot_leads=interest.hot_leads or 0,
            callbacks_scheduled=callbacks_scheduled,
            opt_outs=opt_outs,
            average_call_duration=round(avg_duration, 1),
            call_success_rate=round((completed_calls / total_calls * 100) if total_calls > 0 else 0, 2),
            answer_rate=round((answered_calls / total_calls * 100) if total_calls > 0 else 0, 2),
            conversion_rate=round((interest.interested_customers / total_calls * 100) if total_calls > 0 else 0, 2),
        )

    async def get_campaign_analytics(
        self,
        campaign_id: UUID,
        period: str = "daily",
        days: int = 30,
    ) -> CampaignAnalytics:
        """Get campaign analytics"""
        campaign = await self.db.scalar(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        if not campaign:
            raise ValueError("Campaign not found")

        start_date = datetime.utcnow() - timedelta(days=days)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Daily call analytics
        calls = await self.db.execute(
            select(
                func.date(Call.created_at).label("date"),
                func.count(Call.id).label("total_calls"),
                func.count(Call.id).filter(Call.status == CallStatus.COMPLETED).label("completed_calls"),
                func.count(Call.id).filter(Call.status.in_([
                    CallStatus.FAILED, CallStatus.BUSY, CallStatus.NO_ANSWER,
                    CallStatus.VOICEMAIL, CallStatus.INVALID_NUMBER
                ])).label("failed_calls"),
                func.count(Call.id).filter(Call.status.in_([
                    CallStatus.COMPLETED, CallStatus.BUSY, CallStatus.NO_ANSWER, CallStatus.VOICEMAIL
                ])).label("answered_calls"),
                func.avg(Call.duration).filter(Call.duration.isnot(None)).label("avg_duration"),
                func.sum(Call.duration).filter(Call.duration.isnot(None)).label("total_duration"),
                func.count(Call.id).filter(Call.interest_level == InterestLevel.HOT).label("hot_leads"),
                func.count(Call.id).filter(Call.interest_level == InterestLevel.WARM).label("warm_leads"),
                func.count(Call.id).filter(Call.interest_level == InterestLevel.COLD).label("cold_leads"),
            )
            .where(
                and_(
                    Call.campaign_id == campaign_id,
                    Call.created_at >= start_date,
                )
            )
            .group_by(func.date(Call.created_at))
            .order_by(func.date(Call.created_at))
        )

        daily_data = []
        for row in calls:
            daily_data.append(CallAnalytics(
                date=row.date.isoformat() if isinstance(row.date, date) else str(row.date),
                total_calls=row.total_calls or 0,
                completed_calls=row.completed_calls or 0,
                failed_calls=row.failed_calls or 0,
                answered_calls=row.answered_calls or 0,
                busy_calls=0,  # Would need separate query
                no_answer_calls=0,
                voicemail_calls=0,
                average_duration=float(row.avg_duration or 0),
                total_duration=row.total_duration or 0,
                hot_leads=row.hot_leads or 0,
                warm_leads=row.warm_leads or 0,
                cold_leads=row.cold_leads or 0,
                callbacks_scheduled=0,  # Would need separate query
                opt_outs=0,
            ))

        # Callbacks
        callbacks = await self.db.execute(
            select(
                func.date(Callback.scheduled_at).label("date"),
                func.count(Callback.id).label("count"),
            )
            .where(
                and_(
                    Callback.campaign_id == campaign_id,
                    Callback.status == CallbackStatus.SCHEDULED,
                    Callback.scheduled_at >= start_date,
                )
            )
            .group_by(func.date(Callback.scheduled_at))
        )
        callback_map = {str(row.date): row.count for row in callbacks}

        # Opt-outs
        opt_outs = await self.db.execute(
            select(
                func.date(Customer.opted_out_at).label("date"),
                func.count(Customer.id).label("count"),
            )
            .where(
                and_(
                    Customer.campaigns.any(Campaign.id == campaign_id),
                    Customer.opted_out_at >= start_date,
                )
            )
            .group_by(func.date(Customer.opted_out_at))
        )
        opt_out_map = {str(row.date): row.count for row in opt_outs}

        # Merge callback and opt-out data
        for day in daily_data:
            day.callbacks_scheduled = callback_map.get(day.date, 0)
            day.opt_outs = opt_out_map.get(day.date, 0)

        # Summary
        total_calls = sum(d.total_calls for d in daily_data)
        completed_calls = sum(d.completed_calls for d in daily_data)
        answered_calls = sum(d.answered_calls for d in daily_data)
        total_interested = sum(d.hot_leads + d.warm_leads for d in daily_data)
        total_callbacks = sum(d.callbacks_scheduled for d in daily_data)
        total_opt_outs = sum(d.opt_outs for d in daily_data)
        total_duration = sum(d.total_duration for d in daily_data)
        duration_count = sum(1 for d in daily_data if d.total_duration > 0)

        return CampaignAnalytics(
            campaign_id=campaign_id,
            campaign_name=campaign.name,
            period=period,
            data=daily_data,
            summary=CampaignAnalyticsSummary(
                total_calls=total_calls,
                success_rate=round((completed_calls / total_calls * 100) if total_calls > 0 else 0, 2),
                answer_rate=round((answered_calls / total_calls * 100) if total_calls > 0 else 0, 2),
                conversion_rate=round((total_interested / total_calls * 100) if total_calls > 0 else 0, 2),
                average_duration=round(total_duration / duration_count if duration_count > 0 else 0, 1),
                total_interested=total_interested,
                total_callbacks=total_callbacks,
                total_opt_outs=total_opt_outs,
            ),
        )

    async def get_organization_analytics(
        self,
        organization_id: UUID,
        period: str = "daily",
        days: int = 30,
    ) -> OrganizationAnalytics:
        """Get organization-wide analytics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Similar to campaign analytics but across all campaigns
        calls = await self.db.execute(
            select(
                func.date(Call.created_at).label("date"),
                func.count(Call.id).label("total_calls"),
                func.count(Call.id).filter(Call.status == CallStatus.COMPLETED).label("completed_calls"),
                func.count(Call.id).filter(Call.status.in_([
                    CallStatus.FAILED, CallStatus.BUSY, CallStatus.NO_ANSWER,
                    CallStatus.VOICEMAIL, CallStatus.INVALID_NUMBER
                ])).label("failed_calls"),
                func.count(Call.id).filter(Call.status.in_([
                    CallStatus.COMPLETED, CallStatus.BUSY, CallStatus.NO_ANSWER, CallStatus.VOICEMAIL
                ])).label("answered_calls"),
                func.avg(Call.duration).filter(Call.duration.isnot(None)).label("avg_duration"),
                func.sum(Call.duration).filter(Call.duration.isnot(None)).label("total_duration"),
                func.count(Call.id).filter(Call.interest_level == InterestLevel.HOT).label("hot_leads"),
                func.count(Call.id).filter(Call.interest_level == InterestLevel.WARM).label("warm_leads"),
                func.count(Call.id).filter(Call.interest_level == InterestLevel.COLD).label("cold_leads"),
            )
            .where(
                and_(
                    Call.campaign.has(organization_id=organization_id),
                    Call.created_at >= start_date,
                )
            )
            .group_by(func.date(Call.created_at))
            .order_by(func.date(Call.created_at))
        )

        daily_data = []
        for row in calls:
            daily_data.append(CallAnalytics(
                date=row.date.isoformat() if isinstance(row.date, date) else str(row.date),
                total_calls=row.total_calls or 0,
                completed_calls=row.completed_calls or 0,
                failed_calls=row.failed_calls or 0,
                answered_calls=row.answered_calls or 0,
                busy_calls=0,
                no_answer_calls=0,
                voicemail_calls=0,
                average_duration=float(row.avg_duration or 0),
                total_duration=row.total_duration or 0,
                hot_leads=row.hot_leads or 0,
                warm_leads=row.warm_leads or 0,
                cold_leads=row.cold_leads or 0,
                callbacks_scheduled=0,
                opt_outs=0,
            ))

        # Get summary metrics
        metrics = await self.get_dashboard_metrics(organization_id)

        return OrganizationAnalytics(
            organization_id=organization_id,
            period=period,
            data=daily_data,
            summary=OrganizationAnalyticsSummary(
                total_customers=metrics.total_customers,
                total_calls=metrics.total_calls,
                completed_calls=metrics.completed_calls,
                failed_calls=metrics.failed_calls,
                answered_calls=metrics.answered_calls,
                interested_customers=metrics.interested_customers,
                hot_leads=metrics.hot_leads,
                callbacks_scheduled=metrics.callbacks_scheduled,
                opt_outs=metrics.opt_outs,
                average_call_duration=metrics.average_call_duration,
                call_success_rate=metrics.call_success_rate,
                answer_rate=metrics.answer_rate,
                conversion_rate=metrics.conversion_rate,
            ),
        )

    async def export_report(
        self,
        report_type: str,
        organization_id: UUID,
        campaign_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> bytes:
        """Export analytics report as CSV"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        if report_type == "calls":
            query = select(Call).where(Call.campaign.has(organization_id=organization_id))
            if campaign_id:
                query = query.where(Call.campaign_id == campaign_id)
            if date_from:
                query = query.where(Call.created_at >= date_from)
            if date_to:
                query = query.where(Call.created_at <= date_to)

            result = await self.db.execute(query.order_by(Call.created_at.desc()))
            calls = result.scalars().all()

            writer.writerow([
                "Call ID", "Campaign", "Customer", "Phone", "Status", "Direction",
                "Duration (s)", "Interest Level", "Customer Intent", "Objections",
                "Summary", "Recording URL", "Created At"
            ])
            for call in calls:
                writer.writerow([
                    call.id, call.campaign.name if call.campaign else "",
                    f"{call.customer.first_name} {call.customer.last_name}" if call.customer else "",
                    call.to_number, call.status.value, call.direction.value,
                    call.duration or 0, call.interest_level.value,
                    call.customer_intent or "", "; ".join(call.objections),
                    call.summary or "", call.recording_url or "",
                    call.created_at.isoformat(),
                ])

        elif report_type == "customers":
            query = select(Customer).where(Customer.organization_id == organization_id)
            if campaign_id:
                query = query.join(Customer.campaign_customers).where(
                    CampaignCustomer.campaign_id == campaign_id
                )

            result = await self.db.execute(query.order_by(Customer.created_at.desc()))
            customers = result.scalars().all()

            writer.writerow([
                "Customer ID", "First Name", "Last Name", "Email", "Phone",
                "Company", "Location", "Language", "Status", "Interest Level",
                "Call Attempts", "Last Call", "Next Callback", "Do Not Call", "Created At"
            ])
            for c in customers:
                writer.writerow([
                    c.id, c.first_name, c.last_name, c.email or "", c.phone,
                    c.company or "", c.location or "", c.language,
                    c.status.value, c.interest_level.value, c.call_attempts,
                    c.last_call_at.isoformat() if c.last_call_at else "",
                    c.next_callback_at.isoformat() if c.next_callback_at else "",
                    c.do_not_call, c.created_at.isoformat(),
                ])

        elif report_type == "campaigns":
            query = select(Campaign).where(Campaign.organization_id == organization_id)
            result = await self.db.execute(query.order_by(Campaign.created_at.desc()))
            campaigns = result.scalars().all()

            writer.writerow([
                "Campaign ID", "Name", "Status", "Total Customers", "Completed Calls",
                "Failed Calls", "Interested", "Callbacks", "Opt-outs", "Success Rate", "Created At"
            ])
            for c in campaigns:
                writer.writerow([
                    c.id, c.name, c.status.value, c.total_customers, c.completed_calls,
                    c.failed_calls, c.interested_count, c.callback_count, c.opt_out_count,
                    round((c.completed_calls / c.total_customers * 100) if c.total_customers > 0 else 0, 2),
                    c.created_at.isoformat(),
                ])

        return output.getvalue().encode("utf-8")