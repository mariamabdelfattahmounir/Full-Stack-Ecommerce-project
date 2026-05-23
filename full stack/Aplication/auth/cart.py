from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)
from app.api.deps import (
    get_current_active_user,
    get_db,
    require_permission,
)
from app.core.permissions import Permission
from app.models.user import User
from app.schemas.cart import (
    CartDetail,
    CartItemCreate,
    CartItemUpdate,
    ClearCartResponse,
)
from app.schemas.common import APIResponse
from app.services.cart_service import CartService
from app.utils.api_response import (
    APIResponse as ResponseHandler,
)

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.get(
    "",
    response_model=APIResponse[CartDetail],
    status_code=status.HTTP_200_OK,
)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.CART_MANAGE
        )
    ),
):
    service = CartService(db)

    cart = service.get_current_cart(
        current_user
    )
    logger.info(
        "Cart retrieved successfully",
        extra={
            "event": "cart_retrieved",
            "user_id": current_user.id,
        },
    )
    return ResponseHandler.success(
        data=cart,
        message="Cart retrieved successfully",
    )


@router.post(
    "/items",
    response_model=APIResponse[CartDetail],
    status_code=status.HTTP_201_CREATED,
)
def add_cart_item(
    payload: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.CART_MANAGE
        )
    ),
):
    service = CartService(db)

    cart = service.add_item(
        current_user,
        payload,
    )
    logger.info(
        "Cart item added",
        extra={
            "event": "cart_item_added",
            "user_id": current_user.id,
            "product_id": payload.product_id,
        },
    )
    return ResponseHandler.success(
        data=cart,
        message="Item added to cart successfully",
    )


@router.put(
    "/items/{cart_item_id}",
    response_model=APIResponse[CartDetail],
    status_code=status.HTTP_200_OK,
)
def update_cart_item(
    cart_item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.CART_MANAGE
        )
    ),
):
    service = CartService(db)

    cart = service.update_item(
        current_user,
        cart_item_id,
        payload,
    )
    logger.info(
        "Cart item updated",
        extra={
            "event": "cart_item_updated",
            "user_id": current_user.id,
            "cart_item_id": cart_item_id,
        },
    )
    return ResponseHandler.success(
        data=cart,
        message="Cart item updated successfully",
    )


@router.delete(
    "/items/{cart_item_id}",
    response_model=APIResponse[CartDetail],
    status_code=status.HTTP_200_OK,
)
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.CART_MANAGE
        )
    ),
):
    service = CartService(db)

    cart = service.remove_item(
        current_user,
        cart_item_id,
    )
    logger.warning(
        "Cart item removed",
        extra={
            "event": "cart_item_removed",
            "user_id": current_user.id,
            "cart_item_id": cart_item_id,
        },
    )
    return ResponseHandler.success(
        data=cart,
        message="Cart item removed successfully",
    )


@router.delete(
    "",
    response_model=APIResponse[ClearCartResponse],
    status_code=status.HTTP_200_OK,
)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            Permission.CART_MANAGE
        )
    ),
):
    service = CartService(db)

    result = service.clear_cart(
        current_user
    )
    logger.warning(
        "Cart cleared",
        extra={
            "event": "cart_cleared",
            "user_id": current_user.id,
        },
    )
    return ResponseHandler.success(
        data=result,
        message="Cart cleared successfully",
    )