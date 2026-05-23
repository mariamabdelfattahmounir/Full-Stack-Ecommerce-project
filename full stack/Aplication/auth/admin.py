from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.api.deps import get_db, require_role
from app.core.roles import Role
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.order import OrderDetail, OrderRead, OrderStatusUpdate
from app.services.order_service import OrderService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/orders", response_model=APIResponse[list[OrderRead]])
def list_all_orders(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[list[OrderRead]]:
    service = OrderService(db)
    orders = service.list_all_orders()
    return APIResponse(
        success=True,
        message="Admin orders retrieved successfully",
        data=orders,
    )


@router.get("/orders/{order_id}", response_model=APIResponse[OrderDetail])
def get_order_admin(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[OrderDetail]:
    service = OrderService(db)
    order = service.get_order_admin(order_id)
    return APIResponse(
        success=True,
        message="Admin order retrieved successfully",
        data=order,
    )


@router.put("/orders/{order_id}", response_model=APIResponse[OrderRead])
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[OrderRead]:
    service = OrderService(db)
    order = service.update_order_status(order_id, payload)
    return APIResponse(
        success=True,
        message="Order status updated successfully",
        data=order,
    )


@router.patch("/orders/{order_id}", response_model=APIResponse[OrderRead])
def patch_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
) -> APIResponse[OrderRead]:
    service = OrderService(db)
    order = service.update_order_status(order_id, payload)
    return APIResponse(
        success=True,
        message="Order status updated successfully",
        data=order,
    )

@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(Role.ADMIN)),
):
    total_products = db.query(Product).count()

    total_categories = db.query(Category).count()

    total_orders = db.query(Order).count()

    total_users = db.query(User).count()

    pending_orders = (
        db.query(Order)
        .filter(Order.status == "pending")
        .count()
    )

    revenue = (
        db.query(
            func.coalesce(
                func.sum(Order.total_price),
                0
            )
        ).scalar()
    )

    return {
        "success": True,
        "message": "Dashboard stats retrieved successfully",
        "data": {
            "total_products": total_products,
            "total_categories": total_categories,
            "total_orders": total_orders,
            "total_users": total_users,
            "pending_orders": pending_orders,
            "revenue": float(revenue),
        },
    }