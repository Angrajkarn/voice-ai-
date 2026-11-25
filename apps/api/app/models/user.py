# User model

from typing import Any, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import UserRole
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Foreign keys
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    # Relationships
    organization: Mapped[Any] = relationship("Organization", back_populates="users")
    owned_campaigns: Mapped[list[Any]] = relationship("Campaign", foreign_keys="Campaign.owner_id", back_populates="owner")
    assigned_calls: Mapped[list[Any]] = relationship("Call", foreign_keys="Call.agent_id", back_populates="agent")
    assigned_callbacks: Mapped[list[Any]] = relationship("Callback", foreign_keys="Callback.assignee_id", back_populates="assignee")
    notifications: Mapped[list[Any]] = relationship("Notification", foreign_keys="Notification.user_id", back_populates="user")
    audit_logs: Mapped[list[Any]] = relationship("AuditLog", foreign_keys="AuditLog.user_id", back_populates="user")