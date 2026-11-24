# Customer model

from app.models.base import BaseModel
from app.models.enums import CustomerStatus, InterestLevel
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship


class Customer(BaseModel):
    __tablename__ = "customers"

    external_id = Column(String(100), nullable=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=False, index=True)  # E.164 format
    phone_raw = Column(String(50), nullable=True)
    company = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    language = Column(String(10), default="en-IN", nullable=False)
    timezone = Column(String(50), default="Asia/Kolkata", nullable=False)
    tags = Column(ARRAY(String), default=[], nullable=False)
    custom_fields = Column(JSON, default={}, nullable=False)

    status = Column(SQLEnum(CustomerStatus), default=CustomerStatus.NEW, nullable=False, index=True)
    interest_level = Column(SQLEnum(InterestLevel), default=InterestLevel.UNKNOWN, nullable=False, index=True)
    call_attempts = Column(Integer, default=0, nullable=False)
    max_call_attempts = Column(Integer, default=3, nullable=False)
    last_call_at = Column(DateTime(timezone=True), nullable=True)
    next_callback_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_call_status = Column(SQLEnum('call_status_enum', name='call_status_enum', create_type=False), nullable=True)
    last_call_duration = Column(Integer, nullable=True)
    final_disposition = Column(String(200), nullable=True)
    do_not_call = Column(Boolean, default=False, nullable=False)
    opted_out_at = Column(DateTime(timezone=True), nullable=True)
    opt_out_reason = Column(String(500), nullable=True)

    # Foreign keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="customers")
    campaign_customers = relationship("CampaignCustomer", back_populates="customer")
    calls = relationship("Call", back_populates="customer")
    callbacks = relationship("Callback", back_populates="customer")
    consent_records = relationship("ConsentRecord", back_populates="customer")
    suppressions = relationship("SuppressionList", back_populates="customer")

    # Composite indexes
    __table_args__ = (
        Index('ix_customers_org_phone', 'organization_id', 'phone', unique=True),
        Index('ix_customers_org_status', 'organization_id', 'status'),
        Index('ix_customers_org_interest', 'organization_id', 'interest_level'),
        Index('ix_customers_org_callback', 'organization_id', 'next_callback_at'),
    )