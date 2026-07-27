from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from movielib.bootstrap.container import UseCases
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.rest.dependencies import get_use_cases
from movielib.presentation.rest.schemas.film import FilmResponse

router = APIRouter(prefix="/films", tags=["films"])


@router.get("", response_model=list[FilmResponse])
async def search_films(
    query: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
    telegram_id: int | None = Query(default=None, description="Attributes the search to a user"),
    use_cases: UseCases = Depends(get_use_cases),
) -> list[FilmResponse]:
    films = await use_cases.films.search(
        query,
        limit=limit,
        telegram_id=TelegramId(telegram_id) if telegram_id is not None else None,
    )
    return [FilmResponse.from_domain(film) for film in films]


@router.get("/{film_id}", response_model=FilmResponse)
async def get_film(film_id: int, use_cases: UseCases = Depends(get_use_cases)) -> FilmResponse:
    film = await use_cases.films.get_details(film_id)
    return FilmResponse.from_domain(film)
