# Callback model

from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import CallbackStatus
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Callback(BaseModel):
    __tablename__ = "callbacks"

    status: Mapped[CallbackStatus] = mapped_column(SQLEnum(CallbackStatus), default=CallbackStatus.SCHEDULED, nullable=False, index=True)
    # Scheduling
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    scheduled_timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Source
    source_call_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="SET NULL"), nullable=True)
    customer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Assignment
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # Result
    result_call_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # Relationships
    campaign: Mapped[Any] = relationship("Campaign", back_populates="callbacks")
    customer: Mapped[Any] = relationship("Customer", back_populates="callbacks")
    assignee: Mapped[Any] = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_callbacks")
    source_call: Mapped[Any] = relationship("Call", foreign_keys=[source_call_id], back_populates="callbacks")
    result_call: Mapped[Any] = relationship("Call", foreign_keys=[result_call_id])
    # Indexes
    __table_args__ = (
        Index('ix_callbacks_campaign_status_scheduled', 'campaign_id', 'status', 'scheduled_at'),
        Index('ix_callbacks_customer_status', 'customer_id', 'status'),
        Index('ix_callbacks_assignee_status', 'assignee_id', 'status'),
    )