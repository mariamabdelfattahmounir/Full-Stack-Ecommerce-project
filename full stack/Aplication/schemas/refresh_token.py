from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RefreshTokenCreate(BaseModel):
    token: str
    expires_at: datetime


class RefreshTokenRead(BaseModel):
    id: int
    user_id: int
    token: str
    expires_at: datetime
    is_revoked: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"