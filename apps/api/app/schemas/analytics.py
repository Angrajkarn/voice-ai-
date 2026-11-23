# Analytics schemas

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID


class CallAnalytics(BaseModel):
    date: date
    total_calls: int
    completed_calls: int
    failed_calls: int
    answered_calls: int
    busy_calls: int
    no_answer_calls: int
    voicemail_calls: int
    average_duration: float
    total_duration: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    callbacks_scheduled: int
    opt_outs: int


class CampaignAnalytics(BaseModel):
    campaign_id: UUID
    campaign_name: str
    period: str
    data: List[CallAnalytics]
    summary: "CampaignAnalyticsSummary"


class CampaignAnalyticsSummary(BaseModel):
    total_calls: int
    success_rate: float
    answer_rate: float
    conversion_rate: float
    average_duration: float
    total_interested: int
    total_callbacks: int
    total_opt_outs: int


class OrganizationAnalytics(BaseModel):
    organization_id: UUID
    period: str
    data: List[CallAnalytics]
    summary: "OrganizationAnalyticsSummary"


class OrganizationAnalyticsSummary(BaseModel):
    total_customers: int
    total_calls: int
    completed_calls: int
    failed_calls: int
    answered_calls: int
    interested_customers: int
    hot_leads: int
    callbacks_scheduled: int
    opt_outs: int
    average_call_duration: float
    call_success_rate: float
    answer_rate: float
    conversion_rate: float


class DashboardMetrics(BaseModel):
    total_customers: int
    total_calls: int
    completed_calls: int
    failed_calls: int
    answered_calls: int
    interested_customers: int
    hot_leads: int
    callbacks_scheduled: int
    opt_outs: int
    average_call_duration: float
    call_success_rate: float
    answer_rate: float
    conversion_rate: float


class AnalyticsExportRequest(BaseModel):
    type: str = Field(..., pattern=r'^(campaign|organization|calls|customers|callbacks)$')
    campaign_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    format: str = Field(default="csv", pattern=r'^(csv|xlsx)$')