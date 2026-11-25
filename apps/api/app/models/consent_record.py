# ConsentRecord model

from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import ConsentMethod, ConsentStatus
from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ConsentRecord(BaseModel):
    __tablename__ = "consent_records"

    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # E.164 format
    status: Mapped[ConsentStatus] = mapped_column(SQLEnum(ConsentStatus), default=ConsentStatus.PENDING, nullable=False, index=True)
    method: Mapped[ConsentMethod] = mapped_column(SQLEnum(ConsentMethod), nullable=False)
    proof_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    proof_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    # Foreign keys
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    granted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Relationships
    organization: Mapped[Any] = relationship("Organization", back_populates="consent_records")
    campaign: Mapped[Any] = relationship("Campaign")
    customer: Mapped[Any] = relationship("Customer", back_populates="consent_records")
    # Indexes
    __table_args__ = (
        Index('ix_consent_records_org_phone', 'organization_id', 'phone'),
        Index('ix_consent_records_org_status', 'organization_id', 'status'),
    )