from __future__ import annotations

from datetime import UTC, datetime

import pytest

from movielib.application.ratings.get_average_rating import GetAverageRating
from movielib.application.ratings.get_my_rating import GetMyRating
from movielib.application.ratings.list_my_ratings import ListMyRatings
from movielib.application.ratings.rate_film import RateFilm
from movielib.domain.errors import InvalidRatingScoreError
from movielib.domain.value_objects.telegram_id import TelegramId
from tests.unit.fakes.fake_clock import FakeClock
from tests.unit.fakes.fake_rating_repository import FakeRatingRepository

_USER = TelegramId(1)
_FILM_ID = 101


async def test_rate_then_get_mine() -> None:
    ratings = FakeRatingRepository()
    rate = RateFilm(ratings, FakeClock(datetime.now(UTC)))

    await rate(_USER, _FILM_ID, 8)

    rating = await GetMyRating(ratings)(_USER, _FILM_ID)
    assert rating is not None
    assert rating.score == 8


async def test_rating_the_same_film_again_replaces_the_previous_score() -> None:
    ratings = FakeRatingRepository()
    rate = RateFilm(ratings, FakeClock(datetime.now(UTC)))

    await rate(_USER, _FILM_ID, 3)
    await rate(_USER, _FILM_ID, 9)

    rating = await GetMyRating(ratings)(_USER, _FILM_ID)
    assert rating is not None
    assert rating.score == 9
    assert len(await ListMyRatings(ratings)(_USER)) == 1


async def test_rejects_an_out_of_range_score() -> None:
    ratings = FakeRatingRepository()
    rate = RateFilm(ratings, FakeClock(datetime.now(UTC)))

    with pytest.raises(InvalidRatingScoreError):
        await rate(_USER, _FILM_ID, 11)


async def test_get_my_rating_is_none_when_unrated() -> None:
    ratings = FakeRatingRepository()

    assert await GetMyRating(ratings)(_USER, _FILM_ID) is None


async def test_get_average_rating_across_users() -> None:
    ratings = FakeRatingRepository()
    rate = RateFilm(ratings, FakeClock(datetime.now(UTC)))
    await rate(TelegramId(1), _FILM_ID, 8)
    await rate(TelegramId(2), _FILM_ID, 6)

    average = await GetAverageRating(ratings)(_FILM_ID)

    assert average == 7.0


async def test_get_average_rating_is_none_when_nobody_has_rated() -> None:
    ratings = FakeRatingRepository()

    assert await GetAverageRating(ratings)(_FILM_ID) is None
