# AutomationLog model

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import uuid


class AutomationLog(BaseModel):
    __tablename__ = "automation_logs"

    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)

    trigger_type = Column(String(100), nullable=False)  # CALL_COMPLETED, CALLBACK_DUE, OPT_OUT, HOT_LEAD
    trigger_data = Column(JSON, nullable=False)
    action_type = Column(String(100), nullable=False)  # UPDATE_SHEETS, SCHEDULE_CALLBACK, NOTIFY_TEAM, ADD_TO_SUPPRESSION
    action_data = Column(JSON, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)  # PENDING, COMPLETED, FAILED
    error = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    campaign = relationship("Campaign")

    # Indexes
    __table_args__ = (
        Index('ix_automation_logs_campaign_created', 'campaign_id', 'created_at'),
        Index('ix_automation_logs_trigger_status', 'trigger_type', 'status'),
    )