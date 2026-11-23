# Organization schemas

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.enums import OrganizationPlan


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z0-9-]+$')
    logo_url: Optional[str] = Field(None, max_length=500)


class OrganizationCreate(OrganizationBase):
    plan: OrganizationPlan = OrganizationPlan.FREE
    settings: Dict[str, Any] = {}


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    logo_url: Optional[str] = Field(None, max_length=500)
    plan: Optional[OrganizationPlan] = None
    plan_expires_at: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    id: UUID
    plan: OrganizationPlan
    plan_expires_at: Optional[datetime]
    settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True