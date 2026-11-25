# AuditLog model

from typing import Any, Optional
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    action: Mapped[str] = mapped_column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, CALL_START, CALL_END, SYNC, EXPORT
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # User, Campaign, Customer, Call, Integration
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    old_data: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    new_data: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)  # IP, user agent, etc.

    # Foreign keys
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    # Relationships
    user: Mapped[Any] = relationship("User", foreign_keys=[user_id], back_populates="audit_logs")
    organization: Mapped[Any] = relationship("Organization", back_populates="audit_logs")
    # Indexes
    __table_args__ = (
        Index('ix_audit_logs_org_created', 'organization_id', 'created_at'),
        Index('ix_audit_logs_entity', 'entity_type', 'entity_id'),
        Index('ix_audit_logs_user_created', 'user_id', 'created_at'),
    )
