# Base model with common fields

import uuid

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_mixin, declared_attr


@declarative_mixin
class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


@declarative_mixin
class UUIDMixin:
    """Mixin for UUID primary key"""

    @declared_attr
    def id(cls):
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)


class BaseModel(TimestampMixin, UUIDMixin):
    """Base model combining UUID and Timestamp mixins"""
