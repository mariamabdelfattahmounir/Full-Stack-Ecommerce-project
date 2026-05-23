from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic import field_validator

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str | None = None
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                "Category name cannot be empty"
            )

        return cleaned.title()

class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    model_config = ConfigDict(
        extra="forbid"
    )

class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CategorySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str