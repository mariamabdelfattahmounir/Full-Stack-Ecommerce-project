from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.roles import OrderStatus
from app.db.base_class import (
    Base,
    TimestampMixin,
)

if TYPE_CHECKING:
    from app.models.order_item import OrderItem
    from app.models.user import User


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    __table_args__ = (
        Index(
            "ix_orders_user_status",
            "user_id",
            "status",
        ),

        Index(
            "ix_orders_created_at",
            "created_at",
        ),

        Index(
            "ix_orders_status_created",
            "status",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus,
            name="order_status_enum",
        ),
        nullable=False,
        default=OrderStatus.PENDING,
        index=True,
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    shipping_address: Mapped[str | None] = (
        mapped_column(
            String(500),
            nullable=True,
        )
    )

    notes: Mapped[str | None] = (
        mapped_column(
            String(1000),
            nullable=True,
        )
    )

    cancellation_reason: Mapped[
        str | None
    ] = mapped_column(
        String(1000),
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="orders",
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def is_editable(self) -> bool:
        """
        Check if order is editable.
        """

        return self.status in {
            OrderStatus.PENDING,
            OrderStatus.PAID,
        }

    @property
    def is_cancellable(self) -> bool:
        """
        Check if order can be cancelled.
        """

        return self.status in {
            OrderStatus.PENDING,
            OrderStatus.PAID,
            OrderStatus.PROCESSING,
        }

    @property
    def is_completed(self) -> bool:
        """
        Check if order is completed.
        """

        return (
            self.status
            == OrderStatus.DELIVERED
        )
