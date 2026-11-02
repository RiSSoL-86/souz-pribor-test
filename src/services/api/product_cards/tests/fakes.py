from typing import override

from pydantic import BaseModel

from services.api.product_cards.schemas.draft import ProductCardDraft
from services.llm.base import BaseLLMClient

VALID_DESCRIPTION = "\n\n".join(["Описание прибора. " * 14 + "Итог."] * 4)


def make_draft(  # noqa: PLR0913
    seo_title: str = "Манометр показывающий DM 02 Манотомь",
    seo_description: str = VALID_DESCRIPTION,
    search_queries: list[str] | None = None,
    audience: list[str] | None = None,
    tasks: list[str] | None = None,
    missing_specs: list[str] | None = None,
    data_issues: list[str] | None = None,
) -> ProductCardDraft:
    """Build a draft that passes every check unless told otherwise."""
    return ProductCardDraft(
        seo_title=seo_title,
        seo_description=seo_description,
        search_queries=(
            search_queries
            if search_queries is not None
            else [
                "манометр dm 02",
                "манометр манотомь",
                "манометр показывающий купить",
            ]
        ),
        audience=(
            audience
            if audience is not None
            else ["котельные", "тепловые пункты"]
        ),
        tasks=(
            tasks
            if tasks is not None
            else ["контроль давления в системах отопления"]
        ),
        missing_specs=missing_specs if missing_specs is not None else [],
        data_issues=data_issues if data_issues is not None else [],
    )


class FakeLLM(BaseLLMClient):
    """Hand out prepared answers in turn and remember the prompts."""

    def __init__(self, answers: list[ProductCardDraft | Exception]) -> None:
        """Take the answers (or errors) to give, one per call."""
        self.answers = list(answers)
        self.prompts: list[str] = []

    @override
    async def parse[T: BaseModel](
        self,
        instructions: str,
        prompt: str,
        output_type: type[T],
    ) -> T:
        """Return the next prepared answer."""
        self.prompts.append(prompt)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        assert isinstance(answer, output_type)
        return answer
