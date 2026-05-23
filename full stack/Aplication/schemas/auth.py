from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict
from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        examples=["StrongPassword123"],
    )

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        examples=["StrongPassword123"],
    )    
    full_name: str | None = Field(default=None, max_length=255)
    model_config = ConfigDict(
        extra="forbid"
    )

class AuthResponseData(BaseModel):
    access_token: str

    refresh_token: str

    token_type: str = Field(
        default="bearer",
        examples=["bearer"],
    )

    user: UserRead