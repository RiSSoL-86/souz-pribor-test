from services.api.product_cards.constants import NO_DATA
from services.api.product_cards.schemas.request import ProductCardRequest
from services.api.product_cards.schemas.response import SpecItem
from services.api.product_cards.services.specs import SpecsBuilder


def test_values_are_taken_from_input_only() -> None:
    """Copy the input values and mark absent required specs."""
    product = ProductCardRequest(
        name="Датчик давления",
        manufacturer="ОВЕН",
        specs={"диапазон измерений": "0…1,6 МПа", "класс точности": ""},
    )

    specs = SpecsBuilder(product=product, missing_specs=[]).build()

    assert specs == [
        SpecItem(name="Производитель", value="ОВЕН"),
        SpecItem(name="Диапазон измерений", value="0…1,6 МПа"),
        SpecItem(name="Класс точности", value=NO_DATA),
    ]


def test_missing_manufacturer_and_required_specs() -> None:
    """Say «данных нет» for the manufacturer and every required spec."""
    product = ProductCardRequest(name="Термометр", description="Для воды.")

    specs = SpecsBuilder(product=product, missing_specs=[]).build()

    assert specs == [
        SpecItem(name="Производитель", value=NO_DATA),
        SpecItem(name="Диапазон измерений", value=NO_DATA),
        SpecItem(name="Класс точности", value=NO_DATA),
    ]


def test_model_names_are_added_without_repeats() -> None:
    """Add the model's missing specs, skipping ones already listed."""
    product = ProductCardRequest(
        name="Манометр",
        specs={
            "Пределы измерений": "0–1 МПа",
            "Погрешность": "1,5 %",
            "присоединение": "G1/2",
        },
    )

    specs = SpecsBuilder(
        product=product,
        missing_specs=[
            "Присоединение",
            "Диапазон измеряемого давления",
            "диаметр корпуса.",
            "Диаметр корпуса",
        ],
    ).build()

    assert [spec.name for spec in specs] == [
        "Производитель",
        "Пределы измерений",
        "Погрешность",
        "Присоединение",
        "Диаметр корпуса",
    ]
    assert specs[-1].value == NO_DATA
