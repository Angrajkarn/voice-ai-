# CampaignCustomer model (junction table)


from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import CustomerStatus
from sqlalchemy import DateTime, ForeignKey, Index, Integer, UniqueConstraint, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class CampaignCustomer(BaseModel):
    __tablename__ = "campaign_customers"

    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[CustomerStatus] = mapped_column(SQLEnum(CustomerStatus), default=CustomerStatus.NEW, nullable=False, index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    called_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Foreign keys
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    # Relationships
    campaign: Mapped[Any] = relationship("Campaign", back_populates="campaign_customers")
    customer: Mapped[Any] = relationship("Customer", back_populates="campaign_customers")
    # Constraints
    __table_args__ = (
        UniqueConstraint('campaign_id', 'customer_id', name='uq_campaign_customer'),
        Index('ix_campaign_customers_campaign_status', 'campaign_id', 'status'),
        Index('ix_campaign_customers_customer', 'customer_id'),
    )