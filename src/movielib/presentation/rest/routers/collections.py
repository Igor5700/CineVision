from __future__ import annotations

from fastapi import APIRouter, Depends

from movielib.bootstrap.container import UseCases
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.rest.dependencies import get_use_cases
from movielib.presentation.rest.schemas.collection import (
    CollectionResponse,
    CreateCollectionRequest,
)
from movielib.presentation.rest.schemas.film import FilmResponse

router = APIRouter(tags=["collections"])


@router.post(
    "/users/{telegram_id}/collections", response_model=CollectionResponse, status_code=201
)
async def create_collection(
    telegram_id: int,
    body: CreateCollectionRequest,
    use_cases: UseCases = Depends(get_use_cases),
) -> CollectionResponse:
    collection = await use_cases.collections.create(
        TelegramId(telegram_id), body.name, body.description
    )
    return CollectionResponse.from_domain(collection)


@router.get("/users/{telegram_id}/collections", response_model=list[CollectionResponse])
async def list_my_collections(
    telegram_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> list[CollectionResponse]:
    collections = await use_cases.collections.list_mine(TelegramId(telegram_id))
    return [CollectionResponse.from_domain(collection) for collection in collections]


@router.delete("/users/{telegram_id}/collections/{collection_id}", status_code=204)
async def delete_collection(
    telegram_id: int, collection_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> None:
    await use_cases.collections.delete(TelegramId(telegram_id), collection_id)


@router.post("/users/{telegram_id}/collections/{collection_id}/films/{film_id}", status_code=204)
async def add_film_to_collection(
    telegram_id: int,
    collection_id: int,
    film_id: int,
    use_cases: UseCases = Depends(get_use_cases),
) -> None:
    await use_cases.collections.add_film(TelegramId(telegram_id), collection_id, film_id)


@router.delete(
    "/users/{telegram_id}/collections/{collection_id}/films/{film_id}", status_code=204
)
async def remove_film_from_collection(
    telegram_id: int,
    collection_id: int,
    film_id: int,
    use_cases: UseCases = Depends(get_use_cases),
) -> None:
    await use_cases.collections.remove_film(TelegramId(telegram_id), collection_id, film_id)


@router.get("/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> CollectionResponse:
    collection = await use_cases.collections.get(collection_id)
    return CollectionResponse.from_domain(collection)


@router.get("/collections/{collection_id}/films", response_model=list[FilmResponse])
async def list_collection_films(
    collection_id: int, use_cases: UseCases = Depends(get_use_cases)
) -> list[FilmResponse]:
    films = await use_cases.collections.list_films(collection_id)
    return [FilmResponse.from_domain(film) for film in films]
