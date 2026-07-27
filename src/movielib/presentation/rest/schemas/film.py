from __future__ import annotations

from pydantic import BaseModel

from movielib.domain.entities.film import Film


class FilmResponse(BaseModel):
    id: int
    title: str
    kind: str
    year: int | None
    description: str | None
    poster_url: str | None
    rating: float | None
    genres: list[str]
    countries: list[str]
    duration_minutes: int | None
    age_rating: int | None
    slogan: str | None

    @classmethod
    def from_domain(cls, film: Film) -> FilmResponse:
        return cls(
            id=film.id,
            title=film.title,
            kind=film.kind,
            year=film.year,
            description=film.description,
            poster_url=film.poster_url,
            rating=film.rating,
            genres=film.genres,
            countries=film.countries,
            duration_minutes=film.duration_minutes,
            age_rating=film.age_rating,
            slogan=film.slogan,
        )
