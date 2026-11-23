# ConsentRecord model

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import ConsentStatus, ConsentMethod
import uuid


class ConsentRecord(BaseModel):
    __tablename__ = "consent_records"

    phone = Column(String(20), nullable=False, index=True)  # E.164 format
    status = Column(SQLEnum(ConsentStatus), default=ConsentStatus.PENDING, nullable=False, index=True)
    method = Column(SQLEnum(ConsentMethod), nullable=False)
    proof_url = Column(String(500), nullable=True)
    proof_expires_at = Column(DateTime(timezone=True), nullable=True)

    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)

    # Foreign keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    granted_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="consent_records")
    campaign = relationship("Campaign")
    customer = relationship("Customer", back_populates="consent_records")

    # Indexes
    __table_args__ = (
        Index('ix_consent_records_org_phone', 'organization_id', 'phone'),
        Index('ix_consent_records_org_status', 'organization_id', 'status'),
    )