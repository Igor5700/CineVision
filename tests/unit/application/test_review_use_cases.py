from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from movielib.application.reviews.delete_review import DeleteReview
from movielib.application.reviews.get_my_review import GetMyReview
from movielib.application.reviews.list_film_reviews import ListFilmReviews
from movielib.application.reviews.write_review import WriteReview
from movielib.domain.errors import DomainValidationError
from movielib.domain.value_objects.telegram_id import TelegramId
from tests.unit.fakes.fake_clock import FakeClock
from tests.unit.fakes.fake_review_repository import FakeReviewRepository

_USER = TelegramId(1)
_FILM_ID = 101


async def test_write_then_get_mine() -> None:
    reviews = FakeReviewRepository()
    write = WriteReview(reviews, FakeClock(datetime.now(UTC)))

    await write(_USER, _FILM_ID, "Отличный фильм")

    review = await GetMyReview(reviews)(_USER, _FILM_ID)
    assert review is not None
    assert review.text == "Отличный фильм"


async def test_writing_again_replaces_the_text_and_keeps_the_original_created_at() -> None:
    reviews = FakeReviewRepository()
    first_write_at = datetime.now(UTC)
    write = WriteReview(reviews, FakeClock(first_write_at))
    await write(_USER, _FILM_ID, "Первая версия")

    second_write_at = first_write_at + timedelta(days=1)
    write_again = WriteReview(reviews, FakeClock(second_write_at))
    await write_again(_USER, _FILM_ID, "Вторая версия")

    review = await GetMyReview(reviews)(_USER, _FILM_ID)
    assert review is not None
    assert review.text == "Вторая версия"
    assert review.created_at == first_write_at
    assert review.updated_at == second_write_at


async def test_rejects_blank_text() -> None:
    reviews = FakeReviewRepository()
    write = WriteReview(reviews, FakeClock(datetime.now(UTC)))

    with pytest.raises(DomainValidationError):
        await write(_USER, _FILM_ID, "   ")


async def test_delete_removes_the_review() -> None:
    reviews = FakeReviewRepository()
    write = WriteReview(reviews, FakeClock(datetime.now(UTC)))
    await write(_USER, _FILM_ID, "Текст")

    await DeleteReview(reviews)(_USER, _FILM_ID)

    assert await GetMyReview(reviews)(_USER, _FILM_ID) is None


async def test_list_for_film_only_returns_reviews_for_that_film() -> None:
    reviews = FakeReviewRepository()
    clock = FakeClock(datetime.now(UTC))
    await WriteReview(reviews, clock)(_USER, _FILM_ID, "Про этот фильм")
    await WriteReview(reviews, clock)(_USER, 999, "Про другой фильм")

    results = await ListFilmReviews(reviews)(_FILM_ID)

    assert [review.film_id for review in results] == [_FILM_ID]
