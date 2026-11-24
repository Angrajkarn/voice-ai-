# Organization schemas

from datetime import datetime
from typing import Any
from uuid import UUID

from app.models.enums import OrganizationPlan
from pydantic import BaseModel, Field


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z0-9-]+$')
    logo_url: str | None = Field(None, max_length=500)


class OrganizationCreate(OrganizationBase):
    plan: OrganizationPlan = OrganizationPlan.FREE
    settings: dict[str, Any] = {}


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    logo_url: str | None = Field(None, max_length=500)
    plan: OrganizationPlan | None = None
    plan_expires_at: datetime | None = None
    settings: dict[str, Any] | None = None
    is_active: bool | None = None


class OrganizationResponse(OrganizationBase):
    id: UUID
    plan: OrganizationPlan
    plan_expires_at: datetime | None
    settings: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True