# SuppressionList model

from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import SuppressionReason, SuppressionSource
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class SuppressionList(BaseModel):
    __tablename__ = "suppression_list"

    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # E.164 format
    reason: Mapped[SuppressionReason] = mapped_column(SQLEnum(SuppressionReason), nullable=False)
    source: Mapped[SuppressionSource] = mapped_column(SQLEnum(SuppressionSource), nullable=False)
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    # Foreign keys
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    added_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Relationships
    organization: Mapped[Any] = relationship("Organization", back_populates="suppressions")
    customer: Mapped[Any] = relationship("Customer", back_populates="suppressions")
    # Constraints
    __table_args__ = (
        Index('ix_suppression_list_org_phone', 'organization_id', 'phone', unique=True),
        Index('ix_suppression_list_org_active', 'organization_id', 'is_active'),
    )