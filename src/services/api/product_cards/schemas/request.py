from typing import TYPE_CHECKING, final

from pydantic import ConfigDict, Field, field_validator

from services.api.common.schemas import CamelCaseModel

if TYPE_CHECKING:
    from pydantic.config import JsonDict

PRODUCT_EXAMPLE: JsonDict = {
    "name": "Манометр показывающий DM 02",
    "manufacturer": "Манотомь",
    "specs": {
        "диапазон измерений": "0–1,6 МПа",
        "класс точности": "1,5",
        "присоединение": "G1/2",
        "диаметр корпуса": "100 мм",
    },
    "description": (
        "Прибор предназначен для измерения избыточного давления "
        "неагрессивных к медным сплавам жидкостей, газов и паров."
    ),
}


@final
class ProductCardRequest(CamelCaseModel):
    """Raw data about a measuring instrument, as the supplier gave it."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={"examples": [PRODUCT_EXAMPLE]},
    )

    name: str = Field(min_length=1, max_length=300)
    manufacturer: str | None = Field(default=None, max_length=300)
    specs: dict[str, str | int | float | None] = Field(
        default_factory=dict,
        max_length=100,
    )
    description: str | None = Field(default=None, max_length=20_000)

    @field_validator("manufacturer", "description", mode="before")
    @classmethod
    def blank_to_none(cls, value: object) -> object:
        """Treat an empty or whitespace-only string as a missing value."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("specs", mode="after")
    @classmethod
    def clean_specs(
        cls,
        specs: dict[str, str | int | float | None],
    ) -> dict[str, str | int | float | None]:
        """Drop unnamed specs and trim the names and values that remain."""
        cleaned: dict[str, str | int | float | None] = {}
        for key, value in specs.items():
            if not key.strip():
                continue
            if isinstance(value, str):
                cleaned[key.strip()] = value.strip() or None
            else:
                cleaned[key.strip()] = value
        return cleaned
