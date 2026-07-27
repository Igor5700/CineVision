from __future__ import annotations

from fastapi import APIRouter, Depends

from movielib.bootstrap.container import UseCases
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.rest.dependencies import get_use_cases
from movielib.presentation.rest.schemas.rating import (
    AverageRatingResponse,
    RateFilmRequest,
    RatingResponse,
)

router = APIRouter(tags=["ratings"])


@router.put("/users/{telegram_id}/ratings/{film_id}", response_model=RatingResponse)
async def rate_film(
    telegram_id: int,
    film_id: int,
    body: RateFilmRequest,
    use_cases: UseCases = Depends(get_use_cases),
) -> RatingResponse:
    await use_cases.ratings.rate(TelegramId(telegram_id), film_id, body.score)
    rating = await use_cases.ratings.get_mine(TelegramId(telegram_id), film_id)
    assert rating is not None
    return RatingResponse.from_domain(rating)


@router.get("/users/{telegram_id}/ratings/{film_id}", response_model=RatingResponse | None)
async def get_my_rating(
    telegram_id: int, film_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> RatingResponse | None:
    rating = await use_cases.ratings.get_mine(TelegramId(telegram_id), film_id)
    return RatingResponse.from_domain(rating) if rating is not None else None


@router.get("/users/{telegram_id}/ratings", response_model=list[RatingResponse])
async def list_my_ratings(
    telegram_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> list[RatingResponse]:
    ratings = await use_cases.ratings.list_mine(TelegramId(telegram_id))
    return [RatingResponse.from_domain(rating) for rating in ratings]


@router.get("/films/{film_id}/rating", response_model=AverageRatingResponse)
async def get_average_rating(
    film_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> AverageRatingResponse:
    average = await use_cases.ratings.get_average(film_id)
    return AverageRatingResponse(film_id=film_id, average=average)
