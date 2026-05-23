from decimal import Decimal
import logging
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    require_permission,
)
from app.core.permissions import Permission
from app.models.user import User
from app.schemas.common import (
    APIResponse,
    PaginatedData,
)
from app.schemas.product import (
    ProductCreate,
    ProductDetail,
    ProductListQuery,
    ProductRead,
    ProductUpdate,
)
from app.services.product_service import (
    ProductService,
)
from app.utils.api_response import (
    APIResponse as ResponseHandler,
)
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get(
    "",
    summary="List products",
    description="Retrieve products with filtering, searching, sorting, and pagination",
    response_model=APIResponse[
        PaginatedData[ProductDetail]
    ],
    status_code=status.HTTP_200_OK,
)
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    search: str | None = Query(default=None),
    category_id: int | None = Query(
        default=None,
        gt=0,
    ),
    min_price: Decimal | None = Query(
        default=None,
        ge=0,
    ),
    max_price: Decimal | None = Query(
        default=None,
        ge=0,
    ),
    is_active: bool | None = Query(
        default=None,
    ),
    sort_by: str = Query(
        default="created_at",
        pattern="^(id|name|price|stock|created_at|updated_at)$"
    ),
    sort_order: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
    ),
    db: Session = Depends(get_db),
):
    query = ProductListQuery(
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = ProductService(db)

    data = service.list_products(query)
    logger.info(
        "Products retrieved successfully",
        extra={
            "event": "products_retrieved",
            "count": len(data.items),
            "page": page,
            "page_size": page_size,
        },
    )

    return ResponseHandler.success(
        data=data,
        message="Products retrieved successfully",
    )


@router.get(
    "/{product_id}",
    response_model=APIResponse[
        ProductDetail
    ],
    status_code=status.HTTP_200_OK,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    service = ProductService(db)

    product = service.get_product(
        product_id
    )
    logger.info(
        "Product retrieved successfully",
        extra={
            "event": "product_retrieved",
            "product_id": product.id,
        },
    )
    return ResponseHandler.success(
        data=product,
        message="Product retrieved successfully",
    )

@router.post(
    "",
    summary="Create product",
    description="Admin endpoint for creating a new product",
    response_model=APIResponse[
        ProductRead
    ],
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_permission(
            Permission.PRODUCT_CREATE
        )
    ),
):
    service = ProductService(db)

    product = service.create_product(
        payload
    )
    logger.info(
        "Product created successfully",
        extra={
            "event": "product_created",
            "product_id": product.id,
            "sku": product.sku,
        },
    )
    return ResponseHandler.success(
        data=product,
        message="Product created successfully",
    )


@router.put(
    "/{product_id}",
    summary="Update product",
    description="Admin endpoint for updating product information",
    response_model=APIResponse[
        ProductRead
    ],
    status_code=status.HTTP_200_OK,
)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_permission(
            Permission.PRODUCT_UPDATE
        )
    ),
):
    service = ProductService(db)

    product = service.update_product(
        product_id,
        payload,
    )
    logger.info(
        "Product updated successfully",
        extra={
            "event": "product_updated",
            "product_id": product.id,
        },
    )
    return ResponseHandler.success(
        data=product,
        message="Product updated successfully",
    )


@router.delete(
    "/{product_id}",
    summary="Delete product",
    description="Admin endpoint for deleting a product",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_permission(
            Permission.PRODUCT_DELETE
        )
    ),
):
    logger.info(
        "Product deleted successfully",
        extra={
            "event": "product_deleted",
            "product_id": product_id,
        },
    )    
    service = ProductService(db)

    service.delete_product(product_id)

    return ResponseHandler.success(
        data={"deleted": True},
        message="Product deleted successfully",
    )