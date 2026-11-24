# User schemas

from datetime import datetime
from uuid import UUID

from app.models.enums import UserRole
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = Field(None, max_length=100)
    role: UserRole = UserRole.VIEWER
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    role: UserRole | None = None
    is_active: bool | None = None
    avatar_url: str | None = Field(None, max_length=500)


class UserResponse(UserBase):
    id: UUID
    avatar_url: str | None
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
    organization_id: UUID

    class Config:
        from_attributes = True