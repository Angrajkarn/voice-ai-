# SyncLog model


from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import SyncStatus
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class SyncLog(BaseModel):
    __tablename__ = "sync_logs"

    integration_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False, index=True)
    operation: Mapped[str] = mapped_column(String(100), nullable=False)  # SYNC_CUSTOMER, SYNC_CALL, SYNC_RECORDING
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Customer, Call, Recording
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, nullable=False, index=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_data: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    response_data: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Relationships
    integration: Mapped[Any] = relationship("Integration", back_populates="sync_logs")
    # Indexes
    __table_args__ = (
        Index('ix_sync_logs_integration_created', 'integration_id', 'created_at'),
        Index('ix_sync_logs_entity', 'entity_type', 'entity_id'),
    )