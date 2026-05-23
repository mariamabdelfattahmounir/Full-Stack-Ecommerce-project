import logging
logger = logging.getLogger(__name__)
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from typing import (
    Any,
    Dict,
    Optional,
)

from jose import (
    JWTError,
    jwt,
)
from passlib.context import (
    CryptContext,
)

from app.core.config import (
    get_settings,
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def get_password_hash(
    password: str,
) -> str:

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def _build_token_payload(
    *,
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    additional_claims: (
        Optional[Dict[str, Any]]
    ) = None,
) -> Dict[str, Any]:

    now = datetime.now(
        timezone.utc
    )

    payload: Dict[str, Any] = {

        "sub": subject,

        "type": token_type,

        "iat": int(
            now.timestamp()
        ),

        "exp": int(
            (
                now
                + expires_delta
            ).timestamp()
        ),
    }

    if additional_claims:
        payload.update(
            additional_claims
        )

    return payload


def _create_token(
    *,
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    additional_claims: (
        Optional[Dict[str, Any]]
    ) = None,
) -> str:

    settings = get_settings()

    payload = (
        _build_token_payload(
            subject=subject,
            token_type=token_type,
            expires_delta=expires_delta,
            additional_claims=(
                additional_claims
            ),
        )
    )

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=(
            settings.jwt_algorithm
        ),
    )


def create_access_token(
    subject: str,
    additional_claims: (
        Optional[Dict[str, Any]]
    ) = None,
) -> str:

    settings = get_settings()

    token = _create_token(
        subject=subject,
        token_type=(
            ACCESS_TOKEN_TYPE
        ),
        expires_delta=timedelta(
            minutes=(
                settings
                .jwt_access_token_expire_minutes
            )
        ),
        additional_claims=(
            additional_claims
        ),
    )

    logger.info(
        "Access token generated",
        extra={
            "event": "access_token_generated",
            "subject": subject,
        },
    )

    return token

def create_refresh_token(
    subject: str,
    additional_claims: (
        Optional[Dict[str, Any]]
    ) = None,
) -> str:

    settings = get_settings()

    token = _create_token(
        subject=subject,
        token_type=(
            REFRESH_TOKEN_TYPE
        ),
        expires_delta=timedelta(
            days=7
        ),
        additional_claims=(
            additional_claims
        ),
    )

    logger.info(
        "Refresh token generated",
        extra={
            "event": "refresh_token_generated",
            "subject": subject,
        },
    )

    return token

def decode_token(
    token: str,
) -> dict[str, Any]:

    settings = get_settings()

    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[
            settings.jwt_algorithm
        ],
    )


def get_token_payload(
    token: str,
) -> dict[str, Any]:

    try:

        payload = decode_token(token)

        logger.info(
            "Token validated successfully",
            extra={
                "event": "token_validated",
                "subject": payload.get("sub"),
                "token_type": payload.get("type"),
            },
        )

        return payload

    except JWTError as exc:

        logger.warning(
            "Invalid token validation attempt",
            extra={
                "event": "invalid_token",
                "error": str(exc),
            },
        )

        raise JWTError(
            "Invalid token"
        ) from exc

def is_token_valid(
    token: str,
) -> bool:

    try:

        payload = (
            decode_token(token)
        )

        is_valid = (
            payload.get("type")
            == ACCESS_TOKEN_TYPE
        )

        if is_valid:
            logger.info(
                "Access token is valid",
                extra={
                    "event": "access_token_valid",
                    "subject": payload.get("sub"),
                },
            )

        return is_valid

    except JWTError as exc:

        logger.warning(
            "Invalid access token",
            extra={
                "event": "invalid_access_token",
                "error": str(exc),
            },
        )

        return False

def is_refresh_token_valid(
    token: str,
) -> bool:

    try:

        payload = (
            decode_token(token)
        )

        is_valid = (
            payload.get("type")
            == REFRESH_TOKEN_TYPE
        )

        if is_valid:
            logger.info(
                "Refresh token is valid",
                extra={
                    "event": "refresh_token_valid",
                    "subject": payload.get("sub"),
                },
            )

        return is_valid

    except JWTError as exc:

        logger.warning(
            "Invalid refresh token",
            extra={
                "event": "invalid_refresh_token",
                "error": str(exc),
            },
        )

        return False