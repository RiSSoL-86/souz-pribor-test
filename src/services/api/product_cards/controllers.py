from http import HTTPStatus
from typing import final

from dmr import Body, Controller, ResponseSpec, modify
from dmr.errors import ErrorModel
from dmr.plugins.pydantic import PydanticSerializer

from services.api.product_cards.schemas.request import ProductCardRequest
from services.api.product_cards.schemas.response import ProductCardResponse
from services.api.product_cards.services.generate import (
    ProductCardGenerateService,
)

LLM_ERROR_RESPONSES = [
    ResponseSpec(ErrorModel, status_code=HTTPStatus.BAD_GATEWAY),
    ResponseSpec(ErrorModel, status_code=HTTPStatus.SERVICE_UNAVAILABLE),
]


@final
class ProductCardController(Controller[PydanticSerializer]):
    """Write a product card draft and return it as JSON."""

    auth = None

    @modify(
        status_code=HTTPStatus.OK,
        tags=["Product cards"],
        extra_responses=LLM_ERROR_RESPONSES,
    )
    async def post(
        self,
        parsed_body: Body[ProductCardRequest],
    ) -> ProductCardResponse:
        """Generate the card: SEO copy, specs, queries, sales notes."""
        service = ProductCardGenerateService()
        return await service.execute(payload=parsed_body)
