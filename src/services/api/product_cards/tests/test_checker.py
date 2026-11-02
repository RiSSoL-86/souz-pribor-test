from services.api.product_cards.schemas.request import ProductCardRequest
from services.api.product_cards.services.checker import DraftChecker
from services.api.product_cards.tests.fakes import (
    VALID_DESCRIPTION,
    make_draft,
)

PRODUCT = ProductCardRequest(
    name="Манометр показывающий DM 02",
    manufacturer="Манотомь",
    specs={"диапазон измерений": "0–1,6 МПа", "диаметр корпуса": "100 мм"},
    description="Измеряет избыточное давление.",
)


def test_valid_draft_has_no_remarks() -> None:
    """Pass a draft that meets every requirement."""
    assert len(VALID_DESCRIPTION) in range(800, 1201)
    assert DraftChecker(product=PRODUCT).check(make_draft()) == []


def test_numbers_from_input_are_allowed() -> None:
    """Accept numbers the input has, in any decimal notation."""
    draft = make_draft(
        seo_title="Манометр DM 02 на 1.6 МПа, корпус 100 мм",
        search_queries=["манометр 0-1,6 мпа", "манометр 100", "dm 02"],
    )

    assert DraftChecker(product=PRODUCT).check(draft) == []


def test_invented_numbers_are_reported() -> None:
    """Flag numbers that appear nowhere in the input."""
    draft = make_draft(tasks=["работа при температуре до 120 °C"])

    remarks = DraftChecker(product=PRODUCT).check(draft)

    assert len(remarks) == 1
    assert "120" in remarks[0]


def test_lengths_and_counts_are_reported() -> None:
    """Report a long title, a short description and too few queries."""
    draft = make_draft(
        seo_title="М" * 71,
        seo_description="Коротко.",
        search_queries=["манометр"],
    )

    remarks = DraftChecker(product=PRODUCT).check(draft)

    assert len(remarks) == 3
    assert "seo_title" in remarks[0]
    assert "seo_description" in remarks[1]
    assert "search_queries" in remarks[2]


def test_superscript_units_match_plain_digits() -> None:
    """Treat «м³» in the input and «м3» in the copy as the same number."""
    product = PRODUCT.model_copy(update={"specs": {"расход": "60 м³/ч"}})
    draft = make_draft(search_queries=["расходомер 60 м3/ч", "dm 02", "dm"])

    assert DraftChecker(product=product).check(draft) == []


def test_banned_phrases_are_reported() -> None:
    """Flag evaluative phrases the input does not use."""
    draft = make_draft(tasks=["надёжное измерение давления"])

    remarks = DraftChecker(product=PRODUCT).check(draft)

    assert len(remarks) == 1
    assert "надёжн" in remarks[0]


def test_mixed_script_words_are_reported() -> None:
    """Flag a model name typed with Latin and Cyrillic letters mixed."""
    draft = make_draft(search_queries=["манометр dм 02", "dm 02", "dm"])

    remarks = DraftChecker(product=PRODUCT).check(draft)

    assert len(remarks) == 1
    assert "dм" in remarks[0]
