# Organization model

from typing import Any, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import OrganizationPlan
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class Organization(BaseModel):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    plan: Mapped[OrganizationPlan] = mapped_column(SQLEnum(OrganizationPlan), default=OrganizationPlan.FREE, nullable=False)
    plan_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Relationships
    users: Mapped[list[Any]] = relationship("User", back_populates="organization")
    customers: Mapped[list[Any]] = relationship("Customer", back_populates="organization")
    campaigns: Mapped[list[Any]] = relationship("Campaign", back_populates="organization")
    integrations: Mapped[list[Any]] = relationship("Integration", back_populates="organization")
    suppressions: Mapped[list[Any]] = relationship("SuppressionList", back_populates="organization")
    consent_records: Mapped[list[Any]] = relationship("ConsentRecord", back_populates="organization")
    audit_logs: Mapped[list[Any]] = relationship("AuditLog", foreign_keys="AuditLog.organization_id", back_populates="organization")