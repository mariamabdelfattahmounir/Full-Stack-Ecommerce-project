from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import logging
from app.api.deps import (
    get_db,
    require_permission,
)
from app.core.permissions import Permission
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)
from app.schemas.common import APIResponse
from app.services.category_service import (
    CategoryService,
)
from app.utils.api_response import (
    APIResponse as ResponseHandler,
)
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get(
    "",
    response_model=APIResponse[
        list[CategoryRead]
    ],
    status_code=status.HTTP_200_OK,
)
def list_categories(
    db: Session = Depends(get_db),
):
    service = CategoryService(db)

    categories = (
        service.list_categories()
    )
    logger.info(
        "Categories retrieved successfully",
        extra={
            "event": "categories_retrieved",
            "count": len(categories),
        },
    )
    return ResponseHandler.success(
        data=categories,
        message=(
            "Categories retrieved successfully"
        ),
    )


@router.get(
    "/{category_id}",
    response_model=APIResponse[
        CategoryRead
    ],
    status_code=status.HTTP_200_OK,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    service = CategoryService(db)

    category = service.get_category(
        category_id
    )
    logger.info(
        "Category retrieved successfully",
        extra={
            "event": "category_retrieved",
            "category_id": category.id,
        },
    )
    return ResponseHandler.success(
        data=category,
        message="Category retrieved successfully",
    )


@router.post(
    "",
    summary="Create category",
    description="Admin endpoint for creating product categories",
    response_model=APIResponse[
        CategoryRead
    ],
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_permission(
            Permission.CATEGORY_CREATE
        )
    ),
):
    service = CategoryService(db)

    category = service.create_category(
        payload
    )
    logger.info(
        "Category created successfully",
        extra={
            "event": "category_created",
            "category_id": category.id,
            "category_name": category.name,
        },
    )
    return ResponseHandler.success(
        data=category,
        message="Category created successfully",
    )


@router.put(
    "/{category_id}",
    summary="Update category",
    description="Admin endpoint for updating categories",
    response_model=APIResponse[
        CategoryRead
    ],
    status_code=status.HTTP_200_OK,
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_permission(
            Permission.CATEGORY_UPDATE
        )
    ),
):
    service = CategoryService(db)

    category = service.update_category(
        category_id,
        payload,
    )
    logger.info(
        "Category updated successfully",
        extra={
            "event": "category_updated",
            "category_id": category.id,
        },
    )
    return ResponseHandler.success(
        data=category,
        message="Category updated successfully",
    )


@router.delete(
    "/{category_id}",
    summary="Delete category",
    description="Admin endpoint for deleting categories",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(
        require_permission(
            Permission.CATEGORY_DELETE
        )
    ),
):
    service = CategoryService(db)

    service.delete_category(category_id)
    logger.warning(
        "Category deleted successfully",
        extra={
            "event": "category_deleted",
            "category_id": category_id,
        },
    )
    return ResponseHandler.success(
        data={"deleted": True},
        message="Category deleted successfully",
    )