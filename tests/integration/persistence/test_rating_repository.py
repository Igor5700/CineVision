from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from movielib.domain.entities.rating import Rating
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.rating_repository_sqlalchemy import (
    SqlAlchemyRatingRepository,
)

_USER = TelegramId(1)
_FILM_ID = 101


@pytest.fixture()
def repo(session_factory: async_sessionmaker[AsyncSession]) -> SqlAlchemyRatingRepository:
    return SqlAlchemyRatingRepository(session_factory)


def _rating(telegram_id: TelegramId, film_id: int, score: int) -> Rating:
    return Rating(telegram_id=telegram_id, film_id=film_id, score=score, rated_at=datetime.now(UTC))


async def test_rate_then_get_mine(repo: SqlAlchemyRatingRepository) -> None:
    await repo.rate(_rating(_USER, _FILM_ID, 8))

    rating = await repo.get_my_rating(_USER, _FILM_ID)

    assert rating is not None
    assert rating.score == 8


async def test_rating_again_replaces_the_previous_score(repo: SqlAlchemyRatingRepository) -> None:
    await repo.rate(_rating(_USER, _FILM_ID, 3))
    await repo.rate(_rating(_USER, _FILM_ID, 9))

    rating = await repo.get_my_rating(_USER, _FILM_ID)

    assert rating is not None
    assert rating.score == 9
    assert len(await repo.list_my_ratings(_USER)) == 1


async def test_average_for_film_across_users(repo: SqlAlchemyRatingRepository) -> None:
    await repo.rate(_rating(TelegramId(1), _FILM_ID, 8))
    await repo.rate(_rating(TelegramId(2), _FILM_ID, 6))

    assert await repo.average_for_film(_FILM_ID) == 7.0


async def test_average_for_film_is_none_when_unrated(repo: SqlAlchemyRatingRepository) -> None:
    assert await repo.average_for_film(_FILM_ID) is None
