from typing import TYPE_CHECKING, Any

import pytest
from django.conf import settings
from django.urls import reverse

from services.api.product_cards.constants import NO_DATA
from services.api.product_cards.schemas.request import PRODUCT_EXAMPLE
from services.api.product_cards.tests.fakes import FakeLLM, make_draft
from services.llm import LLMBackend
from services.llm.exceptions import (
    LLMAccessDeniedError,
    LLMAuthenticationError,
    LLMBadResponseError,
    LLMError,
    LLMNotConfiguredError,
    LLMRateLimitError,
    LLMUnavailableError,
)

if TYPE_CHECKING:
    from django.test import Client

    from services.api.product_cards.schemas.draft import ProductCardDraft


@pytest.fixture
def use_llm(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Make the service talk to a fake model with prepared answers."""

    def install(answers: list[ProductCardDraft | Exception]) -> FakeLLM:
        """Install a fake model and return it."""
        llm = FakeLLM(answers)
        monkeypatch.setattr(LLMBackend, "get_client", lambda: llm)
        return llm

    return install


def _post(client: Client, data: Any) -> Any:
    """Send a product to the card endpoint."""
    return client.post(
        reverse("api:product_cards:generate"),
        data=data,
        content_type="application/json",
    )


def test_generates_card(client: Client, use_llm: Any) -> None:
    """Return the copy from the model and the specs from the input."""
    use_llm([make_draft(missing_specs=["Материал корпуса"])])

    response = _post(client, PRODUCT_EXAMPLE)

    assert response.status_code == 200
    body = response.json()
    assert body["seoTitle"] == "Манометр показывающий DM 02 Манотомь"
    assert {"name": "Класс точности", "value": "1,5"} in body["specs"]
    assert {"name": "Материал корпуса", "value": NO_DATA} in body["specs"]
    assert body["missingFields"] == ["Материал корпуса"]
    assert body["commercial"]["audience"] == ["котельные", "тепловые пункты"]
    assert body["warnings"] == []
    assert body["markdown"].startswith(f"# {body['seoTitle']}\n")


def test_retries_with_remarks(client: Client, use_llm: Any) -> None:
    """Show the model what was wrong and keep the fixed draft."""
    llm = use_llm(
        [
            make_draft(tasks=["давление до 25 МПа"]),
            make_draft(),
        ],
    )

    response = _post(client, PRODUCT_EXAMPLE)

    assert response.status_code == 200
    assert response.json()["warnings"] == []
    assert len(llm.prompts) == 2
    assert "<previous_draft>" in llm.prompts[1]
    assert "25" in llm.prompts[1]


def test_keeps_remarks_as_warnings(client: Client, use_llm: Any) -> None:
    """Return the best draft with its remarks once attempts run out."""
    bad = make_draft(seo_title="М" * 80)
    attempts = settings.PRODUCT_CARD_MAX_ATTEMPTS  # type: ignore[misc]
    llm = use_llm([bad] * attempts)

    response = _post(client, PRODUCT_EXAMPLE)

    assert response.status_code == 200
    assert len(llm.prompts) == attempts
    [warning] = response.json()["warnings"]
    assert "seo_title" in warning


def test_keeps_draft_when_retry_fails(client: Client, use_llm: Any) -> None:
    """Return the first draft with its remarks if a retry call fails."""
    use_llm([make_draft(seo_title="М" * 80), LLMUnavailableError()])

    response = _post(client, PRODUCT_EXAMPLE)

    assert response.status_code == 200
    [warning] = response.json()["warnings"]
    assert "seo_title" in warning


def test_reports_missing_data(client: Client, use_llm: Any) -> None:
    """Mark absent fields instead of failing on a sparse product."""
    use_llm(
        [
            make_draft(
                seo_title="Термометр биметаллический для воды",
                search_queries=["термометр", "термометр для воды", "тб-1"],
            ),
        ],
    )

    response = _post(
        client,
        {
            "name": "Термометр ТБ-1",
            "manufacturer": "  ",
            "description": "Для воды.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert {"name": "Производитель", "value": NO_DATA} in body["specs"]
    assert body["missingFields"] == [
        "Производитель",
        "Диапазон измерений",
        "Класс точности",
        "Характеристики (specs)",
    ]


def test_rejects_product_without_specs_and_description(
    client: Client,
    use_llm: Any,
) -> None:
    """Refuse to write a card from a name alone."""
    llm = use_llm([])

    response = _post(client, {"name": "Манометр", "description": " "})

    assert response.status_code == 422
    assert llm.prompts == []


@pytest.mark.parametrize(
    "data",
    [
        {"manufacturer": "Манотомь", "description": "Манометр."},
        {"name": "   ", "description": "Манометр."},
        {"name": "Манометр", "specs": ["0–1 МПа"]},
    ],
)
def test_rejects_invalid_fields(
    client: Client,
    use_llm: Any,
    data: dict[str, Any],
) -> None:
    """Validate the product before calling the model."""
    llm = use_llm([])

    response = _post(client, data)

    assert response.status_code == 400
    assert llm.prompts == []


def test_rejects_malformed_json(client: Client, use_llm: Any) -> None:
    """Reject a body that is not JSON."""
    llm = use_llm([])

    response = _post(client, '{"name": "Манометр",')

    assert response.status_code == 400
    assert llm.prompts == []


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (LLMNotConfiguredError(), 503),
        (LLMAuthenticationError(), 502),
        (LLMAccessDeniedError(), 502),
        (LLMRateLimitError(), 503),
        (LLMUnavailableError(), 503),
        (LLMBadResponseError(), 502),
    ],
)
def test_reports_llm_errors(
    client: Client,
    use_llm: Any,
    error: LLMError,
    status_code: int,
) -> None:
    """Answer with a clear error when the model call fails."""
    use_llm([error])

    response = _post(client, PRODUCT_EXAMPLE)

    assert response.status_code == status_code
    assert response.json()["detail"][0]["msg"]
