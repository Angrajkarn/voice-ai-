# Integration model


from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import IntegrationType, SyncStatus
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class Integration(BaseModel):
    __tablename__ = "integrations"

    type: Mapped[IntegrationType] = mapped_column(SQLEnum(IntegrationType), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)  # Encrypted credentials
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, nullable=False)
    last_sync_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Foreign keys
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    # Relationships
    organization: Mapped[Any] = relationship("Organization", back_populates="integrations")
    campaign: Mapped[Any] = relationship("Campaign", back_populates="integrations")
    sync_logs: Mapped[list[Any]] = relationship("SyncLog", back_populates="integration")
    # Constraints
    __table_args__ = (
        Index('ix_integrations_org_type', 'organization_id', 'type'),
        Index('ix_integrations_org_type_name', 'organization_id', 'type', 'name', unique=True),
    )