# CampaignCustomer model (junction table)

from sqlalchemy import Column, DateTime, ForeignKey, Enum as SQLEnum, Integer, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import CustomerStatus
import uuid


class CampaignCustomer(BaseModel):
    __tablename__ = "campaign_customers"

    priority = Column(Integer, default=0, nullable=False)
    status = Column(SQLEnum(CustomerStatus), default=CustomerStatus.NEW, nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), nullable=False)
    called_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Foreign keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_customers")
    customer = relationship("Customer", back_populates="campaign_customers")

    # Constraints
    __table_args__ = (
        UniqueConstraint('campaign_id', 'customer_id', name='uq_campaign_customer'),
        Index('ix_campaign_customers_campaign_status', 'campaign_id', 'status'),
        Index('ix_campaign_customers_customer', 'customer_id'),
    )