from typing import final

from pydantic import Field

from services.api.common.schemas import CamelCaseModel


@final
class SpecItem(CamelCaseModel):
    """One row of the characteristics table."""

    name: str
    value: str


@final
class CommercialBlock(CamelCaseModel):
    """Notes for the sales manager."""

    audience: list[str]
    tasks: list[str]


class ProductCard(CamelCaseModel):
    """Draft product card for the content manager."""

    seo_title: str
    seo_description: str
    specs: list[SpecItem]
    search_queries: list[str]
    commercial: CommercialBlock
    missing_fields: list[str] = Field(
        description="Чего нет во входных данных: отмечено «данных нет»",
    )
    needs_clarification: list[str] = Field(
        description="Что стоит уточнить у поставщика",
    )
    warnings: list[str] = Field(
        description="Что не прошло автоматическую проверку текста",
    )


@final
class ProductCardResponse(ProductCard):
    """Draft product card along with its Markdown copy."""

    markdown: str = Field(description="Та же карточка в Markdown")
