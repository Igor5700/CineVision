from __future__ import annotations

from datetime import UTC, datetime

import pytest

from movielib.domain.entities.review import Review
from movielib.domain.errors import DomainValidationError
from movielib.domain.value_objects.telegram_id import TelegramId


def _review(text: str) -> Review:
    now = datetime.now(UTC)
    return Review(telegram_id=TelegramId(1), film_id=1, text=text, created_at=now, updated_at=now)


def test_accepts_non_blank_text() -> None:
    assert _review("Отличный фильм").text == "Отличный фильм"


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_rejects_blank_text(text: str) -> None:
    with pytest.raises(DomainValidationError):
        _review(text)


def test_rejects_text_over_the_max_length() -> None:
    with pytest.raises(DomainValidationError):
        _review("x" * (Review.MAX_LENGTH + 1))


def test_accepts_text_at_exactly_the_max_length() -> None:
    assert len(_review("x" * Review.MAX_LENGTH).text) == Review.MAX_LENGTH
