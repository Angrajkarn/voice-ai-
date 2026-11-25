# Campaign model

from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import CampaignStatus
from sqlalchemy import (
    Boolean,

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

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    # AI Configuration
    ai_instructions: Mapped[str] = mapped_column(Text, nullable=False)
    opening_script: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_base: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    voice_id: Mapped[str] = mapped_column(String(50), default="alloy", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en-IN", nullable=False)
    supported_languages: Mapped[list[str]] = mapped_column(ARRAY(String), default=["en-IN", "hi-IN", "hinglish"], nullable=False)
    # Calling Configuration
    max_calls_per_day: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_retry_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    delay_between_calls: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    calling_window_start: Mapped[str] = mapped_column(String(5), default="09:00", nullable=False)
    calling_window_end: Mapped[str] = mapped_column(String(5), default="18:00", nullable=False)
    calling_timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    skip_weekends: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    skip_holidays: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Callback Configuration
    allow_callbacks: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    callback_window_start: Mapped[str] = mapped_column(String(5), default="09:00", nullable=False)
    callback_window_end: Mapped[str] = mapped_column(String(5), default="18:00", nullable=False)
    max_callback_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    # Google Sheets Integration
    sheets_sync_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sheets_spreadsheet_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sheets_sheet_name: Mapped[str] = mapped_column(String(100), default="Calls", nullable=False)
    sheets_auto_sync: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Status & Tracking
    status: Mapped[CampaignStatus] = mapped_column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_customers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_calls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_calls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interested_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    callback_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    opt_out_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Foreign keys
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # Relationships
    organization: Mapped[Any] = relationship("Organization", back_populates="campaigns")
    owner: Mapped[Any] = relationship("User", foreign_keys=[owner_id], back_populates="owned_campaigns")
    campaign_customers: Mapped[list[Any]] = relationship("CampaignCustomer", back_populates="campaign")
    calls: Mapped[list[Any]] = relationship("Call", back_populates="campaign")
    callbacks: Mapped[list[Any]] = relationship("Callback", back_populates="campaign")
    integrations: Mapped[list[Any]] = relationship("Integration", back_populates="campaign")
    # Indexes
    __table_args__ = (
        Index('ix_campaigns_org_status', 'organization_id', 'status'),
        Index('ix_campaigns_owner', 'owner_id'),
    )