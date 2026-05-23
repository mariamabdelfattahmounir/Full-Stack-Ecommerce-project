import logging
from collections.abc import Callable, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import (
    Settings,
    get_settings,
)
from app.core.permissions import (
    Permission,
    has_permission,
)
from app.core.roles import Role
from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.user_repository import (
    UserRepository,
)

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def get_app_settings() -> Settings:
    return get_settings()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:

    if credentials is None:
        logger.warning(
            "Token validation failed: missing authentication credentials"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
        )

    token = credentials.credentials

    try:
        payload = decode_token(token)

    except JWTError:
        logger.warning(
            "Token validation failed: invalid or expired token"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None

    subject = payload.get("sub")

    if subject is None:
        logger.warning(
            "Token validation failed: missing subject claim"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = int(subject)

    except ValueError:
        logger.warning(
            "Token validation failed: invalid subject claim",
            extra={
                "subject": subject,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        ) from None

    user = UserRepository(db).get_by_id(user_id)

    if not user:
        logger.warning(
            "Token validation failed: user not found",
            extra={
                "user_id": user_id,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    logger.info(
        "Token validation successful",
        extra={
            "user_id": user.id,
            "email": user.email,
            "role": (
                user.role.value
                if user.role
                else None
            ),
        },
    )

    return user


def get_current_active_user(
    current_user: User = Depends(
        get_current_user
    ),
) -> User:

    if not current_user.is_active:
        logger.warning(
            "Inactive user attempted to access protected resource",
            extra={
                "user_id": current_user.id,
                "email": current_user.email,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return current_user


def require_role(
    required_role: Role,
) -> Callable:

    def role_dependency(
        current_user: User = Depends(
            get_current_active_user
        ),
    ) -> User:

        if current_user.role != required_role:
            logger.warning(
                "Role authorization failed",
                extra={
                    "user_id": current_user.id,
                    "email": current_user.email,
                    "current_role": (
                        current_user.role.value
                        if current_user.role
                        else None
                    ),
                    "required_role": required_role.value,
                },
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to access this resource"
                ),
            )

        logger.info(
            "Role authorization successful",
            extra={
                "user_id": current_user.id,
                "email": current_user.email,
                "role": (
                    current_user.role.value
                    if current_user.role
                    else None
                ),
                "required_role": required_role.value,
            },
        )

        return current_user

    return role_dependency


def require_permission(
    permission: Permission,
) -> Callable:
    """
    Permission-based dependency injector.
    """

    def permission_dependency(
        current_user: User = Depends(
            get_current_active_user
        ),
    ) -> User:

        if not has_permission(
            current_user,
            permission,
        ):
            logger.warning(
                "Permission authorization failed",
                extra={
                    "user_id": current_user.id,
                    "email": current_user.email,
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
            "Permission authorization successful",
            extra={
                "user_id": current_user.id,
                "email": current_user.email,
                "permission": permission.value,
            },
        )

        return current_user

    return permission_dependency