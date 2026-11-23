# AuditLog model

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import uuid


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    action = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, CALL_START, CALL_END, SYNC, EXPORT
    entity_type = Column(String(100), nullable=False, index=True)  # User, Campaign, Customer, Call, Integration
    entity_id = Column(String(100), nullable=False, index=True)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    metadata = Column(JSON, default={}, nullable=False)  # IP, user agent, etc.

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="audit_logs")
    organization = relationship("Organization", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index('ix_audit_logs_org_created', 'organization_id', 'created_at'),
        Index('ix_audit_logs_entity', 'entity_type', 'entity_id'),
        Index('ix_audit_logs_user_created', 'user_id', 'created_at'),
    )