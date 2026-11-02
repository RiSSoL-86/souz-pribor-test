from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from services.api.product_cards.schemas.response import ProductCard


@final
class MarkdownRenderer:
    """Lay a product card out as Markdown for copying into a CMS."""

    def __init__(self, card: ProductCard) -> None:
        """Take the card to render."""
        self.card = card

    def render(self) -> str:
        """Return the card as one Markdown document."""
        card = self.card
        sections = [
            f"# {card.seo_title}",
            f"## SEO-описание\n\n{card.seo_description}",
            f"## Характеристики\n\n{self._specs_table()}",
            f"## Поисковые запросы\n\n{self._bullets(card.search_queries)}",
            (
                "## Для менеджера\n\n"
                "**Кому подходит:**\n\n"
                f"{self._bullets(card.commercial.audience)}\n\n"
                "**Какие задачи решает:**\n\n"
                f"{self._bullets(card.commercial.tasks)}"
            ),
        ]
        if card.missing_fields:
            sections.append(
                f"## Данных нет\n\n{self._bullets(card.missing_fields)}",
            )
        if card.needs_clarification:
            sections.append(
                "## Уточнить у поставщика\n\n"
                f"{self._bullets(card.needs_clarification)}",
            )
        if card.warnings:
            sections.append(
                f"## Не прошло автопроверку\n\n{self._bullets(card.warnings)}",
            )
        return "\n\n".join(sections) + "\n"

    def _specs_table(self) -> str:
        """Render the characteristics as a two-column table."""
        lines = ["| Характеристика | Значение |", "|---|---|"]
        for spec in self.card.specs:
            name = self._escape_cell(spec.name)
            value = self._escape_cell(spec.value)
            lines.append(f"| {name} | {value} |")
        return "\n".join(lines)

    @staticmethod
    def _bullets(items: list[str]) -> str:
        """Render a Markdown bullet list."""
        return "\n".join(f"- {item}" for item in items)

    @staticmethod
    def _escape_cell(text: str) -> str:
        """Keep a table cell on one row."""
        return text.replace("|", r"\|").replace("\n", " ")
