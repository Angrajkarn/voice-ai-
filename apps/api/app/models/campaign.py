# Campaign model

from app.models.base import BaseModel
from app.models.enums import CampaignStatus
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship


class Campaign(BaseModel):
    __tablename__ = "campaigns"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    purpose = Column(Text, nullable=False)

    # AI Configuration
    ai_instructions = Column(Text, nullable=False)
    opening_script = Column(Text, nullable=False)
    knowledge_base = Column(Text, nullable=True)
    voice_id = Column(String(50), default="alloy", nullable=False)
    language = Column(String(10), default="en-IN", nullable=False)
    supported_languages = Column(ARRAY(String), default=["en-IN", "hi-IN", "hinglish"], nullable=False)

    # Calling Configuration
    max_calls_per_day = Column(Integer, default=100, nullable=False)
    max_retry_attempts = Column(Integer, default=3, nullable=False)
    delay_between_calls = Column(Integer, default=30, nullable=False)
    calling_window_start = Column(String(5), default="09:00", nullable=False)
    calling_window_end = Column(String(5), default="18:00", nullable=False)
    calling_timezone = Column(String(50), default="Asia/Kolkata", nullable=False)
    skip_weekends = Column(Boolean, default=True, nullable=False)
    skip_holidays = Column(Boolean, default=False, nullable=False)

    # Callback Configuration
    allow_callbacks = Column(Boolean, default=True, nullable=False)
    callback_window_start = Column(String(5), default="09:00", nullable=False)
    callback_window_end = Column(String(5), default="18:00", nullable=False)
    max_callback_days = Column(Integer, default=7, nullable=False)

    # Google Sheets Integration
    sheets_sync_enabled = Column(Boolean, default=False, nullable=False)
    sheets_spreadsheet_id = Column(String(100), nullable=True)
    sheets_sheet_name = Column(String(100), default="Calls", nullable=False)
    sheets_auto_sync = Column(Boolean, default=True, nullable=False)

    # Status & Tracking
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    paused_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    stopped_at = Column(DateTime(timezone=True), nullable=True)
    total_customers = Column(Integer, default=0, nullable=False)
    completed_calls = Column(Integer, default=0, nullable=False)
    failed_calls = Column(Integer, default=0, nullable=False)
    interested_count = Column(Integer, default=0, nullable=False)
    callback_count = Column(Integer, default=0, nullable=False)
    opt_out_count = Column(Integer, default=0, nullable=False)

    # Foreign keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="campaigns")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_campaigns")
    campaign_customers = relationship("CampaignCustomer", back_populates="campaign")
    calls = relationship("Call", back_populates="campaign")
    callbacks = relationship("Callback", back_populates="campaign")
    integrations = relationship("Integration", back_populates="campaign")

    # Indexes
    __table_args__ = (
        Index('ix_campaigns_org_status', 'organization_id', 'status'),
        Index('ix_campaigns_owner', 'owner_id'),
    )