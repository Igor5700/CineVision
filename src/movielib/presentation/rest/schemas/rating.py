from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from movielib.domain.entities.rating import Rating


class RateFilmRequest(BaseModel):
    score: int = Field(ge=1, le=10)


class RatingResponse(BaseModel):
    film_id: int
    score: int
    rated_at: datetime

    @classmethod
    def from_domain(cls, rating: Rating) -> RatingResponse:
        return cls(film_id=rating.film_id, score=rating.score, rated_at=rating.rated_at)


class AverageRatingResponse(BaseModel):
    film_id: int
    average: float | None
