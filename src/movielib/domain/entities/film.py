from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Film:
    id: int
    title: str
    kind: str
    year: int | None
    description: str | None
    poster_url: str | None
    rating: float | None = None
    genres: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)
    duration_minutes: int | None = None
    age_rating: int | None = None
    slogan: str | None = None
