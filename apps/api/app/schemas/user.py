# User schemas

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.VIEWER
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserResponse(UserBase):
    id: UUID
    avatar_url: Optional[str]
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    organization_id: UUID

    class Config:
        from_attributes = True