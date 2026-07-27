from __future__ import annotations

from fastapi import APIRouter, Depends

from movielib.bootstrap.container import UseCases
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.rest.dependencies import get_use_cases
from movielib.presentation.rest.schemas.film import FilmResponse

router = APIRouter(prefix="/users/{telegram_id}", tags=["library"])


@router.post("/watchlist/{film_id}", status_code=204)
async def add_to_watchlist(
    telegram_id: int, film_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> None:
    await use_cases.library.add_to_watchlist(TelegramId(telegram_id), film_id)


@router.delete("/watchlist/{film_id}", status_code=204)
async def remove_from_watchlist(
    telegram_id: int, film_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> None:
    await use_cases.library.remove_from_watchlist(TelegramId(telegram_id), film_id)


@router.get("/watchlist", response_model=list[FilmResponse])
async def list_watchlist(
    telegram_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> list[FilmResponse]:
    films = await use_cases.library.list_watchlist(TelegramId(telegram_id))
    return [FilmResponse.from_domain(film) for film in films]


@router.post("/favorites/{film_id}", status_code=204)
async def add_favorite(
    telegram_id: int, film_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> None:
    await use_cases.library.add_favorite(TelegramId(telegram_id), film_id)


@router.delete("/favorites/{film_id}", status_code=204)
async def remove_favorite(
    telegram_id: int, film_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> None:
    await use_cases.library.remove_favorite(TelegramId(telegram_id), film_id)


@router.get("/favorites", response_model=list[FilmResponse])
async def list_favorites(
    telegram_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> list[FilmResponse]:
    films = await use_cases.library.list_favorites(TelegramId(telegram_id))
    return [FilmResponse.from_domain(film) for film in films]


@router.post("/history/{film_id}", status_code=204)
async def mark_watched(
    telegram_id: int, film_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> None:
    await use_cases.library.mark_watched(TelegramId(telegram_id), film_id)


@router.get("/history", response_model=list[FilmResponse])
async def list_history(
    telegram_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> list[FilmResponse]:
    films = await use_cases.library.list_history(TelegramId(telegram_id))
    return [FilmResponse.from_domain(film) for film in films]


@router.get("/recent-searches", response_model=list[str])
async def list_recent_searches(
    telegram_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> list[str]:
    return await use_cases.search.list_recent(TelegramId(telegram_id))
