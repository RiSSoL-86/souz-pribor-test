import logging
from typing import TYPE_CHECKING, final, override

from django.conf import settings

from services.api.common.services.base import BaseService
from services.api.product_cards.constants import (
    NO_DATA,
    SEARCH_QUERIES_MAX_COUNT,
)
from services.api.product_cards.exceptions import (
    NotEnoughProductDataError,
    to_api_error,
)
from services.api.product_cards.prompts import SYSTEM_PROMPT, build_prompt
from services.api.product_cards.schemas.draft import ProductCardDraft
from services.api.product_cards.schemas.response import (
    CommercialBlock,
    ProductCard,
    ProductCardResponse,
)
from services.api.product_cards.services.checker import DraftChecker
from services.api.product_cards.services.markdown import MarkdownRenderer
from services.api.product_cards.services.specs import SpecsBuilder
from services.llm import LLMBackend
from services.llm.exceptions import LLMError

if TYPE_CHECKING:
    from services.api.product_cards.schemas.request import ProductCardRequest
    from services.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


@final
class ProductCardGenerateService(BaseService):
    """Write a product card draft from the raw data of an instrument."""

    @override
    async def execute(
        self,
        payload: ProductCardRequest,
    ) -> ProductCardResponse:
        """Have the model write the copy, check it, and lay out the card."""
        if not payload.specs and not payload.description:
            raise NotEnoughProductDataError

        try:
            llm = LLMBackend.get_client()
            draft, remarks = await self._write_draft(llm, payload)
        except LLMError as e:
            logger.warning(f"Product card generation failed: {e!r}")
            raise to_api_error(e) from e

        card = self._assemble(payload, draft, remarks)
        return ProductCardResponse(
            seo_title=card.seo_title,
            seo_description=card.seo_description,
            specs=card.specs,
            search_queries=card.search_queries,
            commercial=card.commercial,
            missing_fields=card.missing_fields,
            needs_clarification=card.needs_clarification,
            warnings=card.warnings,
            markdown=MarkdownRenderer(card=card).render(),
        )

    async def _write_draft(
        self,
        llm: BaseLLMClient,
        payload: ProductCardRequest,
    ) -> tuple[ProductCardDraft, list[str]]:
        """Ask the LLM for a draft until it passes the checks."""
        checker = DraftChecker(product=payload)
        best: tuple[ProductCardDraft, list[str]] | None = None
        draft: ProductCardDraft | None = None
        remarks: list[str] = []

        max_attempts = settings.PRODUCT_CARD_MAX_ATTEMPTS  # type: ignore[misc]
        for attempt in range(1, max_attempts + 1):
            try:
                draft = await llm.parse(
                    instructions=SYSTEM_PROMPT,
                    prompt=build_prompt(
                        product=payload,
                        previous=draft,
                        remarks=remarks,
                    ),
                    output_type=ProductCardDraft,
                )
            except LLMError as e:
                if best is None:
                    raise
                logger.warning(f"Product card retry {attempt} failed: {e!r}")
                break
            draft = self._tidy(draft)
            remarks = checker.check(draft)
            logger.info(
                f"Product card draft, attempt {attempt}: "
                f"{len(remarks)} remarks",
            )
            if best is None or len(remarks) < len(best[1]):
                best = (draft, remarks)
            if not remarks:
                break

        assert best is not None  # noqa: S101
        return best

    @classmethod
    def _tidy(cls, draft: ProductCardDraft) -> ProductCardDraft:
        """Strip the text, drop empty and repeated items, cap the queries."""

        return draft.model_copy(
            update={
                "seo_title": draft.seo_title.strip(),
                "seo_description": draft.seo_description.strip(),
                "search_queries": cls._unique(
                    [query.lower() for query in draft.search_queries],
                )[:SEARCH_QUERIES_MAX_COUNT],
                "audience": cls._unique(draft.audience),
                "tasks": cls._unique(draft.tasks),
                "missing_specs": cls._unique(draft.missing_specs),
                "data_issues": cls._unique(draft.data_issues),
            },
        )

    @staticmethod
    def _unique(items: list[str]) -> list[str]:
        """Keep the first of each item, in the given order."""
        seen: dict[str, str] = {}
        for item in items:
            cleaned = item.strip()
            if cleaned and cleaned.lower() not in seen:
                seen[cleaned.lower()] = cleaned
        return list(seen.values())

    @staticmethod
    def _assemble(
        payload: ProductCardRequest,
        draft: ProductCardDraft,
        remarks: list[str],
    ) -> ProductCard:
        """Join the model's copy with the characteristics from the input."""
        specs = SpecsBuilder(
            product=payload,
            missing_specs=draft.missing_specs,
        ).build()
        missing_fields = [spec.name for spec in specs if spec.value == NO_DATA]
        if payload.description is None:
            missing_fields.append("Описание (description)")
        if not payload.specs:
            missing_fields.append("Характеристики (specs)")

        return ProductCard(
            seo_title=draft.seo_title,
            seo_description=draft.seo_description,
            specs=specs,
            search_queries=draft.search_queries,
            commercial=CommercialBlock(
                audience=draft.audience,
                tasks=draft.tasks,
            ),
            missing_fields=missing_fields,
            needs_clarification=draft.data_issues,
            warnings=remarks,
        )
