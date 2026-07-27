from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.review import Review
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.review_repository_sqlalchemy import (
    SqlAlchemyReviewRepository,
)

_USER = TelegramId(1)
_FILM_ID = 101


@pytest.fixture()
def repo(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemyReviewRepository:
    return SqlAlchemyReviewRepository(session_factory)


def _review(telegram_id: TelegramId, film_id: int, text: str) -> Review:
    now = datetime.now(UTC)
    return Review(
        telegram_id=telegram_id, film_id=film_id, text=text, created_at=now, updated_at=now
    )


async def test_upsert_then_get(repo: SqlAlchemyReviewRepository) -> None:
    await repo.upsert(_review(_USER, _FILM_ID, "Отлично"))

    review = await repo.get(_USER, _FILM_ID)

    assert review is not None
    assert review.text == "Отлично"


async def test_upsert_again_replaces_the_text(repo: SqlAlchemyReviewRepository) -> None:
    await repo.upsert(_review(_USER, _FILM_ID, "Первая версия"))
    await repo.upsert(_review(_USER, _FILM_ID, "Вторая версия"))

    review = await repo.get(_USER, _FILM_ID)

    assert review is not None
    assert review.text == "Вторая версия"


async def test_delete_removes_the_review(repo: SqlAlchemyReviewRepository) -> None:
    await repo.upsert(_review(_USER, _FILM_ID, "Текст"))

    await repo.delete(_USER, _FILM_ID)

    assert await repo.get(_USER, _FILM_ID) is None


async def test_list_for_film_only_returns_matching_reviews(
    repo: SqlAlchemyReviewRepository,
) -> None:
    await repo.upsert(_review(_USER, _FILM_ID, "Про этот фильм"))
    await repo.upsert(_review(_USER, 999, "Про другой фильм"))

    results = await repo.list_for_film(_FILM_ID)

    assert [r.film_id for r in results] == [_FILM_ID]
