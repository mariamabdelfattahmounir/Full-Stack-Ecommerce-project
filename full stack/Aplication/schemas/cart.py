from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.roles import CartStatus
from app.schemas.product import ProductSummary


class CartItemBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime


class CartItemDetail(CartItemRead):
    product: ProductSummary | None = None
    line_total: Decimal | None = None


class CartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: CartStatus
    created_at: datetime
    updated_at: datetime


class CartDetail(CartRead):
    items: list[CartItemDetail] = Field(default_factory=list)
    total_items: int = 0
    total_amount: Decimal = Decimal("0.00")


class ClearCartResponse(BaseModel):
    cleared: bool