from __future__ import annotations
from pydantic import model_validator
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from pydantic import StringConstraints
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from typing import Annotated
from app.core.roles import OrderStatus
from app.schemas.product import (
    ProductSummary,
)
from app.schemas.user import UserSummary


class OrderItemRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: lambda v: float(v)
        },
    )

    id: int

    product_id: int

    quantity: int = Field(
        gt=0,
        le=1000,
    )

    unit_price: Decimal = Field(
        ge=0
    )
    created_at: datetime

    updated_at: datetime


class OrderItemDetail(
    OrderItemRead
):
    product: (
        ProductSummary | None
    ) = None

    line_total: (
        Decimal | None
    ) = Field(
        default=None,
        ge=0,
    )


class OrderRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: lambda v: float(v)
        },
    )

    id: int

    user_id: int

    status: OrderStatus

    total_price: Decimal = Field(
        ge=0
    )

    shipping_address: str | None = Field(
        default=None,
        max_length=1000,
    ) 

    notes: str | None = Field(
        default=None,
        max_length=2000,
    )

    cancellation_reason: str | None = Field(
        default=None,
        max_length=1000,
    )

    created_at: datetime

    updated_at: datetime


class OrderDetail(OrderRead):
    items: list[
        OrderItemDetail
    ] = Field(default_factory=list)

    user: (
        UserSummary | None
    ) = None

    is_editable: bool = False

    is_cancellable: bool = False

    is_completed: bool = False


class OrderStatusUpdate(BaseModel):
    
    status: OrderStatus

    cancellation_reason: (
        str | None
    ) = None

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "status": "cancelled",
                "cancellation_reason":
                "Customer requested cancellation",
            }
        }
    )
    @model_validator(mode="after")
    def validate_cancellation_reason(self):

        if (
            self.status == OrderStatus.CANCELLED
            and not self.cancellation_reason
        ):
            raise ValueError(
                "Cancellation reason is required "
                "when cancelling an order"
            )

        return self

class CancelOrderRequest(
    
    BaseModel
    
):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cancellation_reason":
                "Ordered by mistake"
            }
        }
    )
    cancellation_reason: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=1000,
            strip_whitespace=True,
        )
    ]


class PlaceOrderResponse(BaseModel):

    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(v)
        },
    )

    id: int

    order_id: int

    status: OrderStatus

    total_price: Decimal = Field(
        ge=0
    )

    created_at: datetime

    message: str = "Order placed successfully"