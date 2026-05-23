from enum import Enum


class Role(str, Enum):
    """
    System roles.
    """

    ADMIN = "admin"

    CUSTOMER = "customer"


class CartStatus(str, Enum):
    """
    Shopping cart lifecycle statuses.
    """

    ACTIVE = "active"

    CHECKED_OUT = "checked_out"

    ABANDONED = "abandoned"


class OrderStatus(str, Enum):
    """
    Order lifecycle statuses.
    """

    PENDING = "pending"

    PAID = "paid"

    PROCESSING = "processing"

    SHIPPED = "shipped"

    DELIVERED = "delivered"

    CANCELLED = "cancelled"

    REFUNDED = "refunded"

    FAILED = "failed"