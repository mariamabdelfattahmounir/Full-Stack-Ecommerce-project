from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.orm import Session
import logging
from app.api.deps import (
    get_current_active_user,
    get_db,
    require_permission,
)
from app.core.permissions import (
    Permission,
)
from app.core.roles import (
    OrderStatus,
)
from app.models.user import User
from app.schemas.common import (
    APIResponse,
)
from app.schemas.order import (
    CancelOrderRequest,
    OrderDetail,
    OrderRead,
    OrderStatusUpdate,
    PlaceOrderResponse,
)
from app.services.order_service import (
    OrderService,
)
from app.utils.api_response import (
    APIResponse as ResponseHandler,
)
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={
        401: {
            "description": "Unauthorized"
        },
        403: {
            "description": "Forbidden"
        },
    },
)





@router.post(
    "/checkout",
    summary="Place order",
    description="Customer endpoint for placing orders",
    response_model=APIResponse[
        PlaceOrderResponse
    ],
    status_code=status.HTTP_201_CREATED,
    responses={
    201: {
        "description": "Order created successfully"
    },
    400: {
        "description": "Invalid order request"
    },
    401: {
        "description": "Unauthorized"
    },
},
)
def checkout(
    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    service = OrderService(db)

    result = service.checkout(
        current_user
    )
 #   logger.info(
  #      "Order placed successfully",
   #     extra={
    #        "event": "order_created",
     #       "user_id": current_user.id,
      #      "order_id": result.id,
       # },
    #)
    return ResponseHandler.success(
        data=result,
        message="Order placed successfully",
    )


@router.get(
    "",
    summary="List user orders",
    description="Retrieve paginated orders for the authenticated user",
    response_model=APIResponse[
        list[OrderRead]
    ],
    status_code=status.HTTP_200_OK,
)
def list_my_orders(
    status_filter: (
        OrderStatus | None
    ) = Query(default=None),

    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip",
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return",
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_active_user
    ),
):
   
    service = OrderService(db)

    orders = service.list_my_orders(
        current_user=current_user,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
    )
    logger.info(
    "User orders retrieved successfully",
    extra={
        "event": "user_orders_retrieved",
        "user_id": current_user.id,
        "count": len(orders),
        },
    )
    return ResponseHandler.success(
        data=orders,
        message="Orders retrieved successfully",
    )



@router.get(
    "/admin/all",
    summary="List all orders",
    description="Admin endpoint for retrieving all orders",
    response_model=APIResponse[
        list[OrderRead]
    ],
    status_code=status.HTTP_200_OK,
)
def list_all_orders_admin(
    status_filter: (
        OrderStatus | None
    ) = Query(default=None),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip",
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return",
    ),
    db: Session = Depends(get_db),

    _: User = Depends(
        require_permission(
            Permission.ORDER_READ
        )
    ),
):
    service = OrderService(db)

    orders = service.list_all_orders(
        status_filter=status_filter,
        skip=skip,
        limit=limit,
    )
    logger.info(
        "Admin retrieved all orders",
        extra={
            "event": "admin_orders_retrieved",
            "count": len(orders),
        },
    )
    return ResponseHandler.success(
        data=orders,
        message=(
            "All orders retrieved successfully"
        ),
    )


@router.get(
    "/admin/{order_id}",
    response_model=APIResponse[
        OrderDetail
    ],
    summary="Get any order",
    description="Admin endpoint for retrieving any order details",
    status_code=status.HTTP_200_OK,
)
def get_order_admin(
    order_id: int,

    db: Session = Depends(get_db),

    _: User = Depends(
        require_permission(
            Permission.ORDER_READ
        )
    ),
):
    service = OrderService(db)

    order = service.get_order_admin(
        order_id
    )
    logger.info(
        "Admin retrieved order",
        extra={
            "event": "admin_order_retrieved",
            "order_id": order.id,
        },
    )
    return ResponseHandler.success(
        data=order,
        message="Order retrieved successfully",
    )


@router.put(
    "/admin/{order_id}/status",
    summary="Update order status",
    description="Admin endpoint for updating order status",
    response_model=APIResponse[
        OrderRead
    ],
    status_code=status.HTTP_200_OK,
)
def update_order_status_admin(
    order_id: int,

    payload: OrderStatusUpdate,

    db: Session = Depends(get_db),

    _: User = Depends(
        require_permission(
            Permission.ORDER_UPDATE
        )
    ),
):
    service = OrderService(db)

    order = service.update_order_status(
        order_id,
        payload,
    )
    logger.info(
        "Order status updated successfully",
        extra={
            "event": "order_status_updated",
            "order_id": order.id,
            "new_status": order.status.value,
        },
    )
    return ResponseHandler.success(
        data=order,
        message=(
            "Order status updated successfully"
        ),
    )
@router.get(
    "/{order_id}",
    response_model=APIResponse[
        OrderDetail
    ],
    summary="Get order details",
    description="Retrieve details for a specific user order",
    status_code=status.HTTP_200_OK,
)
def get_my_order(
    order_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    logger.info(
        "Get my order endpoint called",
        extra={
            "event": "get_my_order_endpoint_called",
            "order_id": order_id,
            "user_id": current_user.id,
        },
    )    
    service = OrderService(db)

    order = service.get_my_order(
        current_user,
        order_id,
    )

    return ResponseHandler.success(
        data=order,
        message="Order retrieved successfully",
    )

@router.post(
    "/{order_id}/cancel",
    summary="Cancel order",
    description="Cancel an order if it is still cancellable",
    response_model=APIResponse[
        OrderRead
    ],
    status_code=status.HTTP_200_OK,
)
def cancel_order(
    order_id: int,

    payload: CancelOrderRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_active_user
    ),
):
    service = OrderService(db)

    order = service.cancel_order(
        current_user=current_user,
        order_id=order_id,
        cancellation_reason=(
            payload.cancellation_reason
        ),
    )
    logger.warning(
        "Order cancelled",
        extra={
            "event": "order_cancelled",
            "order_id": order.id,
            "user_id": current_user.id,
        },
    )
    return ResponseHandler.success(
        data=order,
        message="Order cancelled successfully",
    )

@router.post(
    "",
    response_model=APIResponse[PlaceOrderResponse],
    status_code=status.HTTP_201_CREATED,
)
def place_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return checkout(db, current_user)
