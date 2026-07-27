from __future__ import annotations

from datetime import UTC, datetime

import pytest

from movielib.application.collections.add_film_to_collection import AddFilmToCollection
from movielib.application.collections.create_collection import CreateCollection
from movielib.application.collections.delete_collection import DeleteCollection
from movielib.application.collections.get_collection import GetCollection
from movielib.application.collections.list_collection_films import ListCollectionFilms
from movielib.application.collections.list_my_collections import ListMyCollections
from movielib.application.collections.remove_film_from_collection import (
    RemoveFilmFromCollection,
)
from movielib.domain.entities.film import Film
from movielib.domain.errors import (
    CollectionNotFoundError,
    DomainValidationError,
    NotAuthorizedError,
)
from movielib.domain.value_objects.telegram_id import TelegramId
from tests.unit.fakes.fake_clock import FakeClock
from tests.unit.fakes.fake_collection_repository import FakeCollectionRepository

_OWNER = TelegramId(1)
_OTHER = TelegramId(2)
_FILM_ID = 101


def _repo() -> FakeCollectionRepository:
    return FakeCollectionRepository()


async def test_create_assigns_an_id() -> None:
    collections = _repo()
    create = CreateCollection(collections, FakeClock(datetime.now(UTC)))

    collection = await create(_OWNER, "Любимые фильмы")

    assert collection.id is not None
    assert collection.name == "Любимые фильмы"


async def test_create_rejects_a_blank_name() -> None:
    collections = _repo()
    create = CreateCollection(collections, FakeClock(datetime.now(UTC)))

    with pytest.raises(DomainValidationError):
        await create(_OWNER, "   ")


async def test_list_mine_only_returns_the_requesting_users_collections() -> None:
    collections = _repo()
    create = CreateCollection(collections, FakeClock(datetime.now(UTC)))
    await create(_OWNER, "Мои")
    await create(_OTHER, "Чужие")

    mine = await ListMyCollections(collections)(_OWNER)

    assert [c.name for c in mine] == ["Мои"]


async def test_owner_can_add_and_remove_films() -> None:
    film = Film(
        id=_FILM_ID, title="Матрица", kind="movie", year=1999, description=None, poster_url=None
    )
    collections = FakeCollectionRepository(films_by_id={film.id: film})
    create = CreateCollection(collections, FakeClock(datetime.now(UTC)))
    collection = await create(_OWNER, "Мои")
    assert collection.id is not None

    await AddFilmToCollection(collections)(_OWNER, collection.id, _FILM_ID)
    assert [f.id for f in await ListCollectionFilms(collections)(collection.id)] == [_FILM_ID]

    await RemoveFilmFromCollection(collections)(_OWNER, collection.id, _FILM_ID)
    assert await ListCollectionFilms(collections)(collection.id) == []


async def test_non_owner_cannot_add_a_film() -> None:
    collections = _repo()
    create = CreateCollection(collections, FakeClock(datetime.now(UTC)))
    collection = await create(_OWNER, "Мои")
    assert collection.id is not None

    with pytest.raises(NotAuthorizedError):
        await AddFilmToCollection(collections)(_OTHER, collection.id, _FILM_ID)


async def test_non_owner_cannot_remove_a_film() -> None:
    collections = _repo()
    create = CreateCollection(collections, FakeClock(datetime.now(UTC)))
    collection = await create(_OWNER, "Мои")
    assert collection.id is not None
    await AddFilmToCollection(collections)(_OWNER, collection.id, _FILM_ID)

    with pytest.raises(NotAuthorizedError):
        await RemoveFilmFromCollection(collections)(_OTHER, collection.id, _FILM_ID)


async def test_non_owner_cannot_delete_the_collection() -> None:
    collections = _repo()
    create = CreateCollection(collections, FakeClock(datetime.now(UTC)))
    collection = await create(_OWNER, "Мои")
    assert collection.id is not None

    with pytest.raises(NotAuthorizedError):
        await DeleteCollection(collections)(_OTHER, collection.id)

    assert await GetCollection(collections)(collection.id) is not None


async def test_owner_can_delete_the_collection() -> None:
    collections = _repo()
    create = CreateCollection(collections, FakeClock(datetime.now(UTC)))
    collection = await create(_OWNER, "Мои")
    assert collection.id is not None

    await DeleteCollection(collections)(_OWNER, collection.id)

    with pytest.raises(CollectionNotFoundError):
        await GetCollection(collections)(collection.id)


async def test_mutations_on_a_missing_collection_raise_not_found() -> None:
    collections = _repo()

    with pytest.raises(CollectionNotFoundError):
        await AddFilmToCollection(collections)(_OWNER, 999, _FILM_ID)
    with pytest.raises(CollectionNotFoundError):
        await RemoveFilmFromCollection(collections)(_OWNER, 999, _FILM_ID)
    with pytest.raises(CollectionNotFoundError):
        await DeleteCollection(collections)(_OWNER, 999)
    with pytest.raises(CollectionNotFoundError):
        await ListCollectionFilms(collections)(999)
