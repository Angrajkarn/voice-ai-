# Callback model

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import CallbackStatus
import uuid


class Callback(BaseModel):
    __tablename__ = "callbacks"

    status = Column(SQLEnum(CallbackStatus), default=CallbackStatus.SCHEDULED, nullable=False, index=True)

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    scheduled_timezone = Column(String(50), default="Asia/Kolkata", nullable=False)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    reminder_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Source
    source_call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id", ondelete="SET NULL"), nullable=True)
    customer_notes = Column(Text, nullable=True)
    ai_notes = Column(Text, nullable=True)

    # Assignment
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Result
    result_call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    outcome = Column(String(500), nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="callbacks")
    customer = relationship("Customer", back_populates="callbacks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_callbacks")
    source_call = relationship("Call", foreign_keys=[source_call_id], back_populates="callbacks")
    result_call = relationship("Call", foreign_keys=[result_call_id])

    # Indexes
    __table_args__ = (
        Index('ix_callbacks_campaign_status_scheduled', 'campaign_id', 'status', 'scheduled_at'),
        Index('ix_callbacks_customer_status', 'customer_id', 'status'),
        Index('ix_callbacks_assignee_status', 'assignee_id', 'status'),
    )