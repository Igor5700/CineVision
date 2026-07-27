from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from movielib.domain.entities.review import Review


class WriteReviewRequest(BaseModel):
    text: str = Field(min_length=1, max_length=Review.MAX_LENGTH)


class ReviewResponse(BaseModel):
    telegram_id: int
    film_id: int
    text: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, review: Review) -> ReviewResponse:
        return cls(
            telegram_id=int(review.telegram_id),
            film_id=review.film_id,
            text=review.text,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )
