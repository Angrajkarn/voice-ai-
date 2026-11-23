# Call model

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import CallStatus, CallDirection, InterestLevel, SyncStatus
import uuid


class Call(BaseModel):
    __tablename__ = "calls"

    call_sid = Column(String(50), unique=True, nullable=True, index=True)
    direction = Column(SQLEnum(CallDirection), default=CallDirection.OUTBOUND, nullable=False)
    status = Column(SQLEnum(CallStatus), default=CallStatus.QUEUED, nullable=False, index=True)

    # Participants
    from_number = Column(String(20), nullable=False)
    to_number = Column(String(20), nullable=False, index=True)

    # Timing
    queued_at = Column(DateTime(timezone=True), nullable=False)
    initiated_at = Column(DateTime(timezone=True), nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    billable_duration = Column(Integer, nullable=True)  # seconds

    # Results
    disposition = Column(String(50), nullable=True)
    failure_reason = Column(Text, nullable=True)
    hangup_source = Column(String(50), nullable=True)  # customer, ai, system, network

    # AI Analysis
    interest_level = Column(SQLEnum(InterestLevel), default=InterestLevel.UNKNOWN, nullable=False)
    customer_intent = Column(Text, nullable=True)
    objections = Column(ARRAY(Text), default=[], nullable=False)
    questions_asked = Column(ARRAY(Text), default=[], nullable=False)
    summary = Column(Text, nullable=True)
    sentiment = Column(String(20), nullable=True)  # positive, neutral, negative
    requires_human_followup = Column(Boolean, default=False, nullable=False)
    human_followup_reason = Column(Text, nullable=True)

    # Recording & Transcript
    recording_url = Column(String(500), nullable=True)
    recording_sid = Column(String(50), nullable=True)
    transcript_url = Column(String(500), nullable=True)
    transcript_text = Column(Text, nullable=True)
    transcript_segments = Column(JSON, default=[], nullable=False)

    # Google Sheets Sync
    sheets_synced = Column(Boolean, default=False, nullable=False)
    sheets_sync_at = Column(DateTime(timezone=True), nullable=True)
    sheets_sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, nullable=False)
    sheets_sync_error = Column(Text, nullable=True)
    sheets_row_index = Column(Integer, nullable=True)

    # Foreign keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="calls")
    customer = relationship("Customer", back_populates="calls")
    agent = relationship("User", foreign_keys=[agent_id], back_populates="assigned_calls")
    transcript = relationship("CallTranscript", back_populates="call", uselist=False)
    recording = relationship("CallRecording", back_populates="call", uselist=False)
    callbacks = relationship("Callback", back_populates="source_call")

    # Indexes
    __table_args__ = (
        Index('ix_calls_campaign_status', 'campaign_id', 'status'),
        Index('ix_calls_customer_status', 'customer_id', 'status'),
        Index('ix_calls_campaign_created', 'campaign_id', 'created_at'),
        Index('ix_calls_to_number', 'to_number'),
        Index('ix_calls_sheets_sync', 'sheets_sync_status'),
    )