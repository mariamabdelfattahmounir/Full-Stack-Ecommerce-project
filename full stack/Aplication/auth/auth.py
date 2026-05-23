from fastapi import (
    APIRouter,
    Depends,
    Request,
    status,
)
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.api.deps import get_db
from app.middlewares.rate_limit import limiter
from app.schemas.auth import (
    AuthResponseData,
    LoginRequest,
    RegisterRequest,
)
from app.schemas.common import APIResponse
from app.schemas.refresh_token import (
    RefreshTokenResponse,
)
from app.schemas.user import UserRead
from app.services.auth_service import (
    AuthService,
)
from app.utils.api_response import (
    APIResponse as ResponseHandler,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)
settings = get_settings()

@router.post(
    "/register",
    summary="Register new user",
    description="Create a new customer account",
    response_model=APIResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: Request,
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register new user account.
    """

    service = AuthService(db)

    user = service.register(payload)

    return ResponseHandler.success(
        data=user,
        message="User registered successfully",
    )


@router.post(
    "/login",
    summary="User login",
    description="Authenticate user and generate JWT access and refresh tokens",
    response_model=APIResponse[
        AuthResponseData
    ],
    status_code=status.HTTP_200_OK,
)
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and generate tokens.
    """

    service = AuthService(db)

    auth_data = service.login(payload)

    return ResponseHandler.success(
        data=auth_data,
        message="Login successful",
    )


@router.post(
    "/refresh",
    summary="Refresh access token",
    description="Generate a new access token using a valid refresh token",
    response_model=APIResponse[
        RefreshTokenResponse
    ],
    status_code=status.HTTP_200_OK,
)
def refresh_access_token(
    request: Request,
    refresh_token: str,
    db: Session = Depends(get_db),
):
    """
    Generate new access token
    using refresh token.
    """

    service = AuthService(db)

    tokens = (
        service.refresh_access_token(
            refresh_token
        )
    )

    return ResponseHandler.success(
        data=tokens,
        message=(
            "Access token refreshed successfully"
        ),
    )


@router.post(
    "/logout",
    summary="Logout user",
    description="Revoke refresh token and logout authenticated user",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
)
def logout(
    request: Request,
    refresh_token: str,
    db: Session = Depends(get_db),
):
    """
    Logout user and revoke refresh token.
    """

    service = AuthService(db)

    service.logout(refresh_token)

    return ResponseHandler.success(
        data={
            "logged_out": True,
        },
        message="Logout successful",
    )
if settings.app_env != "test":

    register = limiter.limit("3/minute")(register)

    login = limiter.limit("5/minute")(login)

    refresh_access_token = limiter.limit("10/minute")(refresh_access_token)

    logout = limiter.limit("10/minute")(logout)