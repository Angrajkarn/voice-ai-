# Organization model

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import OrganizationPlan
import uuid


class Organization(BaseModel):
    __tablename__ = "organizations"

    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    logo_url = Column(String(500), nullable=True)
    plan = Column(SQLEnum(OrganizationPlan), default=OrganizationPlan.FREE, nullable=False)
    plan_expires_at = Column(DateTime(timezone=True), nullable=True)
    settings = Column(JSON, default={}, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization")
    customers = relationship("Customer", back_populates="organization")
    campaigns = relationship("Campaign", back_populates="organization")
    integrations = relationship("Integration", back_populates="organization")
    suppressions = relationship("SuppressionList", back_populates="organization")
    consent_records = relationship("ConsentRecord", back_populates="organization")
    audit_logs = relationship("AuditLog", foreign_keys="AuditLog.organization_id", back_populates="organization")