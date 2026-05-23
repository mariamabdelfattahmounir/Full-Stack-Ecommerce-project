from __future__ import annotations
from pydantic import field_validator
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import computed_field
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)
from pydantic import AliasChoices
from app.schemas.category import (
    CategorySummary,
)


class ProductBase(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    sku: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[A-Za-z0-9_-]+$",
        examples=[""],
    )

    price: Decimal = Field(
        ...,
        gt=0,
    )

    stock: int = Field(
        validation_alias=AliasChoices(
            "stock",
            "stock_quantity",
        ),
        ge=0,
        le=1_000_000,
        examples=[50],
    )

    is_active: bool = True

    category_id: int = Field(
        ...,
        gt=0,
    )
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                "Product name cannot be empty"
        )

        return cleaned
    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value: str) -> str:
        return value.strip().upper()

class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    sku: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    price: Decimal | None = Field(
        default=None,
        gt=0,
    )

    stock: int | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "stock",
            "stock_quantity",
         ),   
        ge=0,
        le=1_000_000,
    )

    is_active: bool | None = None

    category_id: int | None = Field(
        default=None,
        gt=0,
    )


class ProductRead(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
             Decimal: lambda v: float(v)
        },
    )

    id: int

    name: str

    description: str | None

    sku: str

    price: float

    stock: int

    @computed_field
    @property
    def stock_quantity(self) -> int:
        return self.stock
    
    is_active: bool

    category_id: int

    created_at: datetime

    updated_at: datetime


class ProductDetail(ProductRead):

    category: (
        CategorySummary | None
    ) = None


class ProductSummary(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    name: str

    sku: str

    price: float

    stock: int

    is_active: bool


class ProductListQuery(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )
    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    search: str | None = Field(
        default=None,
        max_length=255,
    )

    category_id: int | None = Field(
        default=None,
        gt=0,
    )

    min_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    max_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    is_active: bool | None = None

    sort_by: Literal[
        "id",
        "name",
        "price",
        "stock",
        "created_at",
        "updated_at",
    ] = "created_at"

    sort_order: Literal[
        "asc",
        "desc",
    ] = "desc"

    @model_validator(mode="after")
    def validate_price_range(
        self,
    ) -> "ProductListQuery":

        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise ValueError(
                "min_price must be less than or equal to max_price"
            )

        if self.search is not None:

            cleaned_search = (
                self.search.strip()
            )

            self.search = (
                cleaned_search or None
            )

        return self