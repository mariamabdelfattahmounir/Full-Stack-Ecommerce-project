from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.roles import CartStatus
from app.db.base_class import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cart_item import CartItem
    from app.models.user import User


class Cart(TimestampMixin, Base):
    __tablename__ = "carts"

    __table_args__ = (
        Index(
            "ix_carts_user_status",
            "user_id",
            "status",
        ),

        Index(
            "ix_carts_expires_at",
            "expires_at",
        ),

        Index(
            "ix_carts_abandoned_at",
            "abandoned_at",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[CartStatus] = mapped_column(
        Enum(CartStatus, name="cart_status_enum"),
        nullable=False,
        default=CartStatus.ACTIVE,
        index=True,
    )
    abandoned_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="carts",
    )

    items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )