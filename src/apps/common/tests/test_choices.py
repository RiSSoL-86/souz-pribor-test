from apps.common.choices import Language


def test_language_values_are_stable() -> None:
    """Expose stable numeric values for persisted language choices."""
    assert Language.values == [0, 1]
    assert Language.names == ["RUSSIAN", "ENGLISH"]


def test_language_labels_are_readable() -> None:
    """Expose translated human-readable language labels."""
    assert [str(choice.label) for choice in Language] == [
        "russian",
        "english",
    ]
