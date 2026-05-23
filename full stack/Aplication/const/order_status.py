from app.core.roles import (
    OrderStatus,
)


FINAL_ORDER_STATUSES = {
    OrderStatus.CANCELLED,
    OrderStatus.REFUNDED,
    OrderStatus.FAILED,
}


SUCCESS_ORDER_STATUSES = {
    OrderStatus.DELIVERED,
}


ACTIVE_ORDER_STATUSES = {
    OrderStatus.PENDING,
    OrderStatus.PAID,
    OrderStatus.PROCESSING,
    OrderStatus.SHIPPED,
}


CANCELLABLE_ORDER_STATUSES = {
    OrderStatus.PENDING,
    OrderStatus.PAID,
    OrderStatus.PROCESSING,
}


REFUNDABLE_ORDER_STATUSES = {
    OrderStatus.DELIVERED,
}


ORDER_STATUS_TRANSITIONS = {

    OrderStatus.PENDING: {
        OrderStatus.PAID,
        OrderStatus.CANCELLED,
        OrderStatus.FAILED,
    },

    OrderStatus.PAID: {
        OrderStatus.PROCESSING,
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED,
    },

    OrderStatus.PROCESSING: {
        OrderStatus.SHIPPED,
        OrderStatus.CANCELLED,
    },

    OrderStatus.SHIPPED: {
        OrderStatus.DELIVERED,
    },

    OrderStatus.DELIVERED: {
        OrderStatus.REFUNDED,
    },

    OrderStatus.CANCELLED: set(),

    OrderStatus.REFUNDED: set(),

    OrderStatus.FAILED: set(),
}
