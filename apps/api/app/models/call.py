# Call model


from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import CallDirection, CallStatus, InterestLevel, SyncStatus
from sqlalchemy import (
    Boolean,

    DateTime,
    func,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship


class Call(BaseModel):
    __tablename__ = "calls"

    call_sid: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    direction: Mapped[CallDirection] = mapped_column(SQLEnum(CallDirection), default=CallDirection.OUTBOUND, nullable=False)
    status: Mapped[CallStatus] = mapped_column(SQLEnum(CallStatus), default=CallStatus.QUEUED, nullable=False, index=True)
    # Participants
    from_number: Mapped[str] = mapped_column(String(20), nullable=False)
    to_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    # Timing
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    initiated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    billable_duration = Column(Integer, nullable=True)  # seconds

    # Results
    disposition: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hangup_source = Column(String(50), nullable=True)  # customer, ai, system, network

    # AI Analysis
    interest_level: Mapped[InterestLevel] = mapped_column(SQLEnum(InterestLevel), default=InterestLevel.UNKNOWN, nullable=False)
    customer_intent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    objections: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[], nullable=False)
    questions_asked: Mapped[list[str]] = mapped_column(ARRAY(Text), default=[], nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sentiment = Column(String(20), nullable=True)  # positive, neutral, negative
    requires_human_followup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    human_followup_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Recording & Transcript
    recording_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    recording_sid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    transcript_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    transcript_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript_segments: Mapped[list[Any]] = mapped_column(JSONB, default=list, nullable=False)
    # Google Sheets Sync
    sheets_synced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sheets_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sheets_sync_status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, nullable=False)
    sheets_sync_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sheets_row_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # Foreign keys
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # Relationships
    campaign: Mapped[Any] = relationship("Campaign", back_populates="calls")
    customer: Mapped[Any] = relationship("Customer", back_populates="calls")
    agent: Mapped[Any] = relationship("User", foreign_keys=[agent_id], back_populates="assigned_calls")
    transcript: Mapped[Any] = relationship("CallTranscript", back_populates="call", uselist=False)
    recording: Mapped[Any] = relationship("CallRecording", back_populates="call", uselist=False)
    callbacks: Mapped[list[Any]] = relationship("Callback", back_populates="source_call", foreign_keys="Callback.source_call_id")
    # Indexes
    __table_args__ = (
        Index('ix_calls_campaign_status', 'campaign_id', 'status'),
        Index('ix_calls_customer_status', 'customer_id', 'status'),
        Index('ix_calls_campaign_created', 'campaign_id', 'created_at'),
        Index('ix_calls_to_number', 'to_number'),
        Index('ix_calls_sheets_sync', 'sheets_sync_status'),
    )