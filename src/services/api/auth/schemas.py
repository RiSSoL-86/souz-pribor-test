from typing import Annotated, final

from pydantic import EmailStr, Field

from services.api.common.schemas import CamelCaseModel


@final
class SignUpRequest(CamelCaseModel):
    """Describe a user registration request."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


@final
class SignUpResponse(CamelCaseModel):
    """Return the newly registered user."""

    id: int
    email: EmailStr


@final
class SignInRequest(CamelCaseModel):
    """Describe a user sign-in request."""

    email: EmailStr
    password: Annotated[str, Field(min_length=1, max_length=128)]


class TokenPairResponse(CamelCaseModel):
    """Describe a JWT access and refresh token pair."""

    email: EmailStr
    access_token: str
    refresh_token: str


@final
class AuthResponse(TokenPairResponse):
    """Return tokens after sign-in."""


@final
class RefreshRequest(CamelCaseModel):
    """Describe a refresh-token request."""

    refresh_token: str


@final
class RefreshResponse(TokenPairResponse):
    """Return a renewed JWT token pair."""
