# User model

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import UserRole
import uuid


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Foreign keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    owned_campaigns = relationship("Campaign", foreign_keys="Campaign.owner_id", back_populates="owner")
    assigned_calls = relationship("Call", foreign_keys="Call.agent_id", back_populates="agent")
    assigned_callbacks = relationship("Callback", foreign_keys="Callback.assignee_id", back_populates="assignee")
    notifications = relationship("Notification", foreign_keys="Notification.user_id", back_populates="user")
    audit_logs = relationship("AuditLog", foreign_keys="AuditLog.user_id", back_populates="user")