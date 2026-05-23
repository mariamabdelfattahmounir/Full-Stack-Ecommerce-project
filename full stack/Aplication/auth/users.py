from fastapi import APIRouter, Depends, status

from app.api.deps import (
    require_permission,
)
from app.core.permissions import Permission
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.user import UserRead
from app.utils.api_response import (
    APIResponse as ResponseHandler,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=APIResponse[UserRead],
    status_code=status.HTTP_200_OK,
)
def get_me(
    current_user: User = Depends(
        require_permission(
            Permission.USER_READ
        )
    ),
):
    return ResponseHandler.success(
        data=UserRead.model_validate(
            current_user
        ),
        message=(
            "Current user retrieved successfully"
        ),
    )