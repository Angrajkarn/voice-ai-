# SyncLog model


from app.models.base import BaseModel
from app.models.enums import SyncStatus
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class SyncLog(BaseModel):
    __tablename__ = "sync_logs"

    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False, index=True)

    operation = Column(String(100), nullable=False)  # SYNC_CUSTOMER, SYNC_CALL, SYNC_RECORDING
    entity_type = Column(String(100), nullable=False, index=True)  # Customer, Call, Recording
    entity_id = Column(String(100), nullable=False, index=True)
    status = Column(SQLEnum(SyncStatus), default=SyncStatus.PENDING, nullable=False, index=True)
    error = Column(Text, nullable=True)
    request_data = Column(JSONB, nullable=True)
    response_data = Column(JSONB, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    integration = relationship("Integration", back_populates="sync_logs")

    # Indexes
    __table_args__ = (
        Index('ix_sync_logs_integration_created', 'integration_id', 'created_at'),
        Index('ix_sync_logs_entity', 'entity_type', 'entity_id'),
    )