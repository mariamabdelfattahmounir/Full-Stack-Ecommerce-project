from enum import Enum
import logging
logger = logging.getLogger(__name__)
from fastapi import HTTPException, status

from app.core.roles import Role
from app.models.user import User


class Permission(str, Enum):
    """
    System permissions.

    Granular permission-based RBAC system.
    """

    # Products
    PRODUCT_CREATE = "product:create"
    PRODUCT_READ = "product:read"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"

    # Categories
    CATEGORY_CREATE = "category:create"
    CATEGORY_READ = "category:read"
    CATEGORY_UPDATE = "category:update"
    CATEGORY_DELETE = "category:delete"

    # Orders
    ORDER_CREATE = "order:create"
    ORDER_READ = "order:read"
    ORDER_UPDATE = "order:update"
    ORDER_DELETE = "order:delete"

    # Cart
    CART_MANAGE = "cart:manage"

    # Users
    USER_READ = "user:read"
    USER_UPDATE = "user:update"

    # Admin
    ADMIN_ACCESS = "admin:access"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        # Products
        Permission.PRODUCT_CREATE,
        Permission.PRODUCT_READ,
        Permission.PRODUCT_UPDATE,
        Permission.PRODUCT_DELETE,

        # Categories
        Permission.CATEGORY_CREATE,
        Permission.CATEGORY_READ,
        Permission.CATEGORY_UPDATE,
        Permission.CATEGORY_DELETE,

        # Orders
        Permission.ORDER_CREATE,
        Permission.ORDER_READ,
        Permission.ORDER_UPDATE,
        Permission.ORDER_DELETE,

        # Cart
        Permission.CART_MANAGE,

        # Users
        Permission.USER_READ,
        Permission.USER_UPDATE,

        # Admin
        Permission.ADMIN_ACCESS,
    },

    Role.CUSTOMER: {
        # Products
        Permission.PRODUCT_READ,

        # Categories
        Permission.CATEGORY_READ,

        # Orders
        Permission.ORDER_CREATE,
        Permission.ORDER_READ,

        # Cart
        Permission.CART_MANAGE,

        # Users
        Permission.USER_READ,
    },
}

def has_permission(
    user: User,
    permission: Permission,
) -> bool:
    """
    Check if user has permission.
    """

    if not user.role:

        logger.warning(
            "Permission check failed: user has no role",
            extra={
                "event": "permission_check_failed",
                "user_id": user.id,
                "permission": permission.value,
            },
        )

        return False

    role_permissions = ROLE_PERMISSIONS.get(
        user.role,
        set(),
    )

    has_access = (
        permission in role_permissions
    )

    logger.info(
        "Permission check executed",
        extra={
            "event": "permission_checked",
            "user_id": user.id,
            "role": user.role.value,
            "permission": permission.value,
            "granted": has_access,
        },
    )

    return has_access

def require_permission(
    permission: Permission,
):
    """
    Dependency injector for permission checks.

    Example:
        Depends(
            require_permission(
                Permission.PRODUCT_DELETE
            )
        )
    """

    def permission_checker(
        current_user: User,
    ) -> User:

        if not has_permission(
            current_user,
            permission,
        ):

            logger.warning(
                "Permission denied",
                extra={
                    "event": "permission_denied",
                    "user_id": current_user.id,
                    "role": (
                        current_user.role.value
                        if current_user.role
                        else None
                    ),
                    "permission": permission.value,
                },
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to perform this action"
                ),
            )

        logger.info(
            "Permission granted",
            extra={
                "event": "permission_granted",
                "user_id": current_user.id,
                "role": current_user.role.value,
                "permission": permission.value,
            },
        )

        return current_user

    return permission_checker