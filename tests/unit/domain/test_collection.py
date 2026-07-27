from __future__ import annotations

from datetime import UTC, datetime

import pytest

from movielib.domain.entities.collection import Collection
from movielib.domain.errors import DomainValidationError
from movielib.domain.value_objects.telegram_id import TelegramId


def _collection(name: str) -> Collection:
    return Collection(
        id=None,
        telegram_id=TelegramId(1),
        name=name,
        description=None,
        created_at=datetime.now(UTC),
    )


def test_accepts_a_non_blank_name() -> None:
    assert _collection("Любимые фильмы").name == "Любимые фильмы"


@pytest.mark.parametrize("name", ["", "   "])
def test_rejects_a_blank_name(name: str) -> None:
    with pytest.raises(DomainValidationError):
        _collection(name)
