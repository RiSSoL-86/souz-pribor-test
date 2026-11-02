from http import HTTPStatus
from typing import final, override

from dmr import Body, Controller, ResponseSpec, modify
from dmr.errors import ErrorModel
from dmr.plugins.pydantic import PydanticSerializer
from dmr.security import AuthenticatedHttpRequest
from dmr.security.jwt.views import (
    ObtainTokensAsyncController,
    ObtainTokensPayload,
    RefreshTokenAsyncController,
)

from apps.users.models import User
from services.api.auth.schemas import (
    AuthResponse,
    RefreshRequest,
    RefreshResponse,
    SignInRequest,
    SignUpRequest,
    SignUpResponse,
)
from services.api.auth.services.signup import SignUpService
from services.api.auth.services.token import TokenService


@final
class SignUpController(Controller[PydanticSerializer]):
    """Register new users."""

    auth = None

    @modify(
        status_code=HTTPStatus.CREATED,
        tags=["Auth"],
        extra_responses=[
            ResponseSpec(ErrorModel, status_code=HTTPStatus.CONFLICT),
        ],
    )
    async def post(self, parsed_body: Body[SignUpRequest]) -> SignUpResponse:
        """Register a user from email and password."""
        service = SignUpService()
        user = await service.execute(payload=parsed_body)
        return SignUpResponse.model_validate(obj=user)


@final
class SignInController(
    ObtainTokensAsyncController[
        PydanticSerializer,
        SignInRequest,  # type: ignore[type-var]
        AuthResponse,
    ],
):
    """Issue tokens for valid user credentials."""

    request: AuthenticatedHttpRequest[User]
    auth = None

    @modify(
        status_code=HTTPStatus.OK,
        tags=["Auth"],
        extra_responses=[
            ResponseSpec(ErrorModel, status_code=HTTPStatus.UNAUTHORIZED),
        ],
    )
    @override
    async def post(self, parsed_body: Body[SignInRequest]) -> AuthResponse:
        """Authenticate a user and return a token pair."""
        return await self.login(parsed_body)

    @override
    async def convert_auth_payload(
        self,
        payload: SignInRequest,
    ) -> ObtainTokensPayload:
        """Convert the API payload to Django authentication credentials."""
        return {
            "username": str(payload.email),
            "password": payload.password,
        }

    @override
    async def make_api_response(self) -> AuthResponse:
        """Return a new access and refresh token pair."""
        service = TokenService()
        email, access_token, refresh_token = await service.execute(
            user=self.request.user,
        )
        return AuthResponse(
            email=email,
            access_token=access_token,
            refresh_token=refresh_token,
        )


@final
class RefreshController(
    RefreshTokenAsyncController[
        PydanticSerializer,
        RefreshRequest,  # type: ignore[type-var]
        RefreshResponse,
    ],
):
    """Refresh authentication tokens."""

    request: AuthenticatedHttpRequest[User]
    auth = None

    @modify(
        status_code=HTTPStatus.OK,
        tags=["Auth"],
        extra_responses=[
            ResponseSpec(ErrorModel, status_code=HTTPStatus.UNAUTHORIZED),
        ],
    )
    @override
    async def post(
        self,
        parsed_body: Body[RefreshRequest],
    ) -> RefreshResponse:
        """Validate a refresh token and return a new token pair."""
        return await self.refresh(parsed_body)

    @override
    async def convert_refresh_payload(self, payload: RefreshRequest) -> str:
        """Extract the refresh token from the API payload."""
        return payload.refresh_token

    @override
    async def make_api_response(self) -> RefreshResponse:
        """Return a renewed access and refresh token pair."""
        service = TokenService()
        email, access_token, refresh_token = await service.execute(
            user=self.request.user,
        )
        return RefreshResponse(
            email=email,
            access_token=access_token,
            refresh_token=refresh_token,
        )
