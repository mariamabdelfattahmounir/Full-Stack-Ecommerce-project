from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.roles import Role


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    model_config = ConfigDict(
        extra="forbid"
    )

class UserRoleUpdate(BaseModel):
    role: Role


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None = None
    role: Role
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None = None
    role: Role