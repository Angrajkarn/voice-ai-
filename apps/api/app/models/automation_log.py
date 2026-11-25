# AutomationLog model


from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class AutomationLog(BaseModel):
    __tablename__ = "automation_logs"

    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    trigger_type = Column(String(100), nullable=False)  # CALL_COMPLETED, CALLBACK_DUE, OPT_OUT, HOT_LEAD
    trigger_data: Mapped[Any] = mapped_column(JSONB, nullable=False)
    action_type = Column(String(100), nullable=False)  # UPDATE_SHEETS, SCHEDULE_CALLBACK, NOTIFY_TEAM, ADD_TO_SUPPRESSION
    action_data: Mapped[Any] = mapped_column(JSONB, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)  # PENDING, COMPLETED, FAILED
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Relationships
    campaign: Mapped[Any] = relationship("Campaign")
    # Indexes
    __table_args__ = (
        Index('ix_automation_logs_campaign_created', 'campaign_id', 'created_at'),
        Index('ix_automation_logs_trigger_status', 'trigger_type', 'status'),
    )