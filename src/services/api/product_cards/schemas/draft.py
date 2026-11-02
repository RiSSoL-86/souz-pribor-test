from typing import final

from pydantic import BaseModel, Field


@final
class ProductCardDraft(BaseModel):
    """What the model writes. It holds no characteristic values at all."""

    seo_title: str = Field(description="SEO-заголовок, не длиннее 70 символов")
    seo_description: str = Field(
        description="SEO-описание, 800–1200 символов с пробелами",
    )
    search_queries: list[str] = Field(description="3–5 поисковых запросов")
    audience: list[str] = Field(description="Кому подходит прибор")
    tasks: list[str] = Field(description="Какие задачи решает прибор")
    missing_specs: list[str] = Field(
        description=(
            "Названия важных для этого типа прибора характеристик, "
            "которых нет во входных данных"
        ),
    )
    data_issues: list[str] = Field(
        description="Противоречия и неясности во входных данных",
    )
