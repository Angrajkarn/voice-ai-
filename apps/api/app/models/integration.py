# Integration model

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import IntegrationType, SyncStatus
import uuid


class Integration(BaseModel):
    __tablename__ = "integrations"

    type = Column(SQLEnum(IntegrationType), nullable=False)
    name = Column(String(100), nullable=False)
    config = Column(JSON, default={}, nullable=False)  # Encrypted credentials
    is_active = Column(Boolean, default=True, nullable=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_sync_status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, nullable=False)
    last_sync_error = Column(Text, nullable=True)

    # Foreign keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="integrations")
    campaign = relationship("Campaign", back_populates="integrations")
    sync_logs = relationship("SyncLog", back_populates="integration")

    # Constraints
    __table_args__ = (
        Index('ix_integrations_org_type', 'organization_id', 'type'),
        Index('ix_integrations_org_type_name', 'organization_id', 'type', 'name', unique=True),
    )