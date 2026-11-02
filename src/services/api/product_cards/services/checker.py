import re
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, final

from services.api.product_cards.constants import (
    BANNED_PHRASES,
    SEARCH_QUERIES_MAX_COUNT,
    SEARCH_QUERIES_MIN_COUNT,
    SEO_DESCRIPTION_MAX_LENGTH,
    SEO_DESCRIPTION_MIN_LENGTH,
    SEO_TITLE_MAX_LENGTH,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from services.api.product_cards.schemas.draft import ProductCardDraft
    from services.api.product_cards.schemas.request import ProductCardRequest


@final
class DraftChecker:
    """Find what in a model's draft breaks the card requirements."""

    number_pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"\d+(?:[.,]\d+)?",
    )
    word_pattern: ClassVar[re.Pattern[str]] = re.compile(r"[\w-]+")
    latin_pattern: ClassVar[re.Pattern[str]] = re.compile(r"[a-z]")
    cyrillic_pattern: ClassVar[re.Pattern[str]] = re.compile(r"[а-яё]")
    superscripts: ClassVar[dict[int, int]] = str.maketrans("²³", "23")

    def __init__(self, product: ProductCardRequest) -> None:
        """Remember every number the input data contains."""
        source = [
            product.name,
            product.manufacturer or "",
            product.description or "",
        ]
        for name, value in product.specs.items():
            source.extend((name, "" if value is None else str(value)))
        self.allowed_numbers = self._collect_numbers(source)
        self.source_text = " ".join(source).lower()

    def check(self, draft: ProductCardDraft) -> list[str]:
        """Return remarks on the draft; an empty list means it is fine."""
        remarks: list[str] = []

        title_length = len(draft.seo_title)
        if title_length > SEO_TITLE_MAX_LENGTH:
            remarks.append(
                f"seo_title длиной {title_length} символов, "
                f"а нужно не больше {SEO_TITLE_MAX_LENGTH}: сократи "
                f"на {title_length - SEO_TITLE_MAX_LENGTH} или больше, "
                "убрав целые слова.",
            )

        description_length = len(draft.seo_description)
        if description_length < SEO_DESCRIPTION_MIN_LENGTH:
            remarks.append(
                f"seo_description длиной {description_length} символов, "
                f"а нужно от {SEO_DESCRIPTION_MIN_LENGTH} "
                f"до {SEO_DESCRIPTION_MAX_LENGTH}: добавь не меньше "
                f"{SEO_DESCRIPTION_MIN_LENGTH - description_length + 100} "
                "символов о назначении и применении, без новых фактов.",
            )
        if description_length > SEO_DESCRIPTION_MAX_LENGTH:
            remarks.append(
                f"seo_description длиной {description_length} символов, "
                f"а нужно от {SEO_DESCRIPTION_MIN_LENGTH} "
                f"до {SEO_DESCRIPTION_MAX_LENGTH}: сократи не меньше чем на "
                f"{description_length - SEO_DESCRIPTION_MAX_LENGTH + 100} "
                "символов.",
            )

        queries = len(draft.search_queries)
        if not (
            SEARCH_QUERIES_MIN_COUNT <= queries <= SEARCH_QUERIES_MAX_COUNT
        ):
            remarks.append(
                f"В search_queries {queries} запросов, а нужно "
                f"от {SEARCH_QUERIES_MIN_COUNT} "
                f"до {SEARCH_QUERIES_MAX_COUNT}.",
            )

        texts = [draft.seo_title, draft.seo_description]
        texts.extend(draft.search_queries)
        texts.extend(draft.audience)
        texts.extend(draft.tasks)
        copy = " ".join(texts).lower()

        invented = self._collect_numbers(texts) - self.allowed_numbers
        if invented:
            numbers = sorted(format(number, "f") for number in invented)
            remarks.append(
                "В тексте есть числа, которых нет во входных данных: "
                f"{', '.join(numbers)}. Убери их или замени словами "
                "без технических значений.",
            )

        banned = [
            phrase
            for phrase in BANNED_PHRASES
            if phrase in copy and phrase not in self.source_text
        ]
        if banned:
            remarks.append(
                "В тексте есть запрещённые оценки, пояснения или "
                f"рассуждения о данных: {', '.join(banned)}. Перепиши эти "
                "предложения: только факты из данных, без выводов.",
            )

        mixed = sorted(
            {
                word
                for word in self.word_pattern.findall(copy)
                if self.latin_pattern.search(word)
                and self.cyrillic_pattern.search(word)
                and word not in self.source_text
            },
        )
        if mixed:
            remarks.append(
                f"Слова смешивают латиницу и кириллицу: {', '.join(mixed)}. "
                "Пиши названия посимвольно как во входных данных.",
            )
        return remarks

    def _collect_numbers(self, texts: Iterable[str]) -> set[Decimal]:
        """Collect numbers, so that «1,6», «1.6» and «1.60» are the same."""
        return {
            Decimal(match.replace(",", ".")).normalize()
            for text in texts
            for match in self.number_pattern.findall(
                text.translate(self.superscripts),
            )
        }
