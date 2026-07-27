from __future__ import annotations

from fastapi import APIRouter, Depends

from movielib.bootstrap.container import UseCases
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.rest.dependencies import get_use_cases
from movielib.presentation.rest.schemas.review import ReviewResponse, WriteReviewRequest

router = APIRouter(tags=["reviews"])


@router.put("/users/{telegram_id}/reviews/{film_id}", response_model=ReviewResponse)
async def write_review(
    telegram_id: int,
    film_id: int,
    body: WriteReviewRequest,
    use_cases: UseCases = Depends(get_use_cases),
) -> ReviewResponse:
    await use_cases.reviews.write(TelegramId(telegram_id), film_id, body.text)
    review = await use_cases.reviews.get_mine(TelegramId(telegram_id), film_id)
    assert review is not None
    return ReviewResponse.from_domain(review)


@router.delete("/users/{telegram_id}/reviews/{film_id}", status_code=204)
async def delete_review(
    telegram_id: int, film_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> None:
    await use_cases.reviews.delete(TelegramId(telegram_id), film_id)


@router.get("/users/{telegram_id}/reviews/{film_id}", response_model=ReviewResponse | None)
async def get_my_review(
    telegram_id: int, film_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> ReviewResponse | None:
    review = await use_cases.reviews.get_mine(TelegramId(telegram_id), film_id)
    return ReviewResponse.from_domain(review) if review is not None else None


@router.get("/films/{film_id}/reviews", response_model=list[ReviewResponse])
async def list_film_reviews(
    film_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> list[ReviewResponse]:
    reviews = await use_cases.reviews.list_for_film(film_id)
    return [ReviewResponse.from_domain(review) for review in reviews]
