# Customer model

from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import CustomerStatus, InterestLevel
from sqlalchemy import (
    Boolean,

    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship


class Customer(BaseModel):
    __tablename__ = "customers"

    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone = Column(String(20), nullable=False, index=True)  # E.164 format
    phone_raw: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en-IN", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=[], nullable=False)
    custom_fields: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[CustomerStatus] = mapped_column(SQLEnum(CustomerStatus), default=CustomerStatus.NEW, nullable=False, index=True)
    interest_level: Mapped[InterestLevel] = mapped_column(SQLEnum(InterestLevel), default=InterestLevel.UNKNOWN, nullable=False, index=True)
    call_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_call_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    last_call_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_callback_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_call_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_call_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    final_disposition: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    do_not_call: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    opted_out_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    opt_out_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # Foreign keys
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    # Relationships
    organization: Mapped[Any] = relationship("Organization", back_populates="customers")
    campaign_customers: Mapped[list[Any]] = relationship("CampaignCustomer", back_populates="customer")
    calls: Mapped[list[Any]] = relationship("Call", back_populates="customer")
    callbacks: Mapped[list[Any]] = relationship("Callback", back_populates="customer")
    consent_records: Mapped[list[Any]] = relationship("ConsentRecord", back_populates="customer")
    suppressions: Mapped[list[Any]] = relationship("SuppressionList", back_populates="customer")
    # Composite indexes
    __table_args__ = (
        Index('ix_customers_org_phone', 'organization_id', 'phone', unique=True),
        Index('ix_customers_org_status', 'organization_id', 'status'),
        Index('ix_customers_org_interest', 'organization_id', 'interest_level'),
        Index('ix_customers_org_callback', 'organization_id', 'next_callback_at'),
    )