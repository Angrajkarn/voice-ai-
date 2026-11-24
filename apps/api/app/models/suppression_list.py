# SuppressionList model

from app.models.base import BaseModel
from app.models.enums import SuppressionReason, SuppressionSource
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class SuppressionList(BaseModel):
    __tablename__ = "suppression_list"

    phone = Column(String(20), nullable=False, index=True)  # E.164 format
    reason = Column(SQLEnum(SuppressionReason), nullable=False)
    source = Column(SQLEnum(SuppressionSource), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)

    # Foreign keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)

    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    added_by = Column(String(100), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="suppressions")
    customer = relationship("Customer", back_populates="suppressions")

    # Constraints
    __table_args__ = (
        Index('ix_suppression_list_org_phone', 'organization_id', 'phone', unique=True),
        Index('ix_suppression_list_org_active', 'organization_id', 'is_active'),
    )