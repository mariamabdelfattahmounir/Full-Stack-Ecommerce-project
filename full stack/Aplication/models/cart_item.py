from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.product import Product


class CartItem(TimestampMixin, Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="cart_items_quantity_positive"),
        UniqueConstraint("cart_id", "product_id", name="uq_cart_items_cart_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(nullable=False, default=1)

    cart: Mapped["Cart"] = relationship(
        "Cart",
        back_populates="items",
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="cart_items",
    )