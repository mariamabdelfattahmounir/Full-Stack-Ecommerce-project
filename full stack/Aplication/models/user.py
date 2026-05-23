from sqlalchemy import Index
from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.roles import Role
from app.db.base_class import (
    Base,
    TimestampMixin,
)

from app.models.refresh_token import RefreshToken
from app.models.cart import Cart
from app.models.order import Order
class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email_role", "email", "role"),
    )
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    role: Mapped[Role] = mapped_column(
        Enum(Role, name="role_enum"),
        nullable=False,
        default=Role.CUSTOMER,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    carts: Mapped[list["Cart"]] = relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    def __repr__(self) -> str:
        return (
            f"<User id={self.id} "
            f"email='{self.email}' "
            f"role='{self.role.value}'>"
        )