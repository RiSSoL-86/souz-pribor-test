from typing import TYPE_CHECKING, final

from services.api.product_cards.constants import (
    MANUFACTURER_LABEL,
    NO_DATA,
    REQUIRED_SPECS,
)
from services.api.product_cards.schemas.response import SpecItem

if TYPE_CHECKING:
    from services.api.product_cards.schemas.request import ProductCardRequest


@final
class SpecsBuilder:
    """Build the specs list with values from the input only."""

    def __init__(
        self,
        product: ProductCardRequest,
        missing_specs: list[str],
    ) -> None:
        """Take the input data and the names the model found missing."""
        self.product = product
        self.missing_specs = missing_specs

    def build(self) -> list[SpecItem]:
        """Return the rows: manufacturer, input specs, then absent ones."""
        specs = [
            SpecItem(
                name=MANUFACTURER_LABEL,
                value=self._format_value(self.product.manufacturer),
            ),
        ]
        for name, value in self.product.specs.items():
            specs.append(
                SpecItem(
                    name=self._capitalize(name),
                    value=self._format_value(value),
                ),
            )

        known = {self._normalize(spec.name) for spec in specs}
        for label, synonyms in REQUIRED_SPECS.items():
            if not any(syn in name for name in known for syn in synonyms):
                specs.append(SpecItem(name=label, value=NO_DATA))
                known.add(self._normalize(label))

        required_synonyms = [
            syn for syns in REQUIRED_SPECS.values() for syn in syns
        ]
        for name in self.missing_specs:
            cleaned = name.strip().rstrip(".")
            normalized = self._normalize(cleaned)
            if (
                not cleaned
                or normalized in known
                or any(syn in normalized for syn in required_synonyms)
            ):
                continue
            specs.append(
                SpecItem(name=self._capitalize(cleaned), value=NO_DATA),
            )
            known.add(normalized)
        return specs

    @staticmethod
    def _normalize(name: str) -> str:
        """Compare names regardless of case and the letter ё."""
        return name.strip().lower().replace("ё", "е")

    @staticmethod
    def _capitalize(name: str) -> str:
        """Upper-case the first letter only, keeping units like «МПа»."""
        return name[:1].upper() + name[1:]

    @staticmethod
    def _format_value(value: str | float | None) -> str:
        """Show a value as given, or say there is none."""
        if value is None:
            return NO_DATA
        return str(value)
