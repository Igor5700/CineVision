from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio

from movielib.bootstrap.config import Settings
from movielib.bootstrap.container import Container, build_container
from movielib.domain.entities.film import Film
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.infrastructure.persistence.film_repository_sqlalchemy import (
    SqlAlchemyFilmRepository,
)


@pytest_asyncio.fixture()
async def container(sqlite_url: str) -> AsyncIterator[Container]:
    settings = Settings(
        bot_token="123456:AAEfake-token-for-tests-only",
        films_api_token="token",
        database_url=sqlite_url,
    )
    built = build_container(settings)
    try:
        yield built
    finally:
        await built.engine.dispose()


async def test_wires_every_use_case_group(container: Container) -> None:
    use_cases = container.use_cases

    assert use_cases.users.register is not None
    assert use_cases.users.get_profile is not None
    assert use_cases.users.set_birthday is not None
    assert use_cases.users.update_display_name is not None
    assert use_cases.films.search is not None
    assert use_cases.films.get_details is not None
    assert use_cases.library.add_to_watchlist is not None
    assert use_cases.library.remove_from_watchlist is not None
    assert use_cases.library.list_watchlist is not None
    assert use_cases.library.add_favorite is not None
    assert use_cases.library.remove_favorite is not None
    assert use_cases.library.list_favorites is not None
    assert use_cases.library.mark_watched is not None
    assert use_cases.library.list_history is not None
    assert use_cases.ratings.rate is not None
    assert use_cases.ratings.get_mine is not None
    assert use_cases.ratings.list_mine is not None
    assert use_cases.ratings.get_average is not None
    assert use_cases.reviews.write is not None
    assert use_cases.reviews.delete is not None
    assert use_cases.reviews.get_mine is not None
    assert use_cases.reviews.list_for_film is not None
    assert use_cases.collections.create is not None
    assert use_cases.collections.delete is not None
    assert use_cases.collections.list_mine is not None
    assert use_cases.collections.get is not None
    assert use_cases.collections.add_film is not None
    assert use_cases.collections.remove_film is not None
    assert use_cases.collections.list_films is not None
    assert use_cases.search.list_recent is not None


async def test_register_then_get_profile_round_trips_through_the_real_stack(
    container: Container,
) -> None:
    telegram_id = TelegramId(42)
    await container.use_cases.users.register(telegram_id, "ann")

    profile = await container.use_cases.users.get_profile(telegram_id)

    assert profile.username == "ann"


async def _seed_film(container: Container, film_id: int) -> None:
    repo = SqlAlchemyFilmRepository(container.session_factory)
    await repo.upsert_many(
        [
            Film(
                id=film_id,
                title=f"Film {film_id}",
                kind="movie",
                year=2020,
                description=None,
                poster_url=None,
            )
        ]
    )


async def test_watchlist_round_trips_through_the_real_stack(container: Container) -> None:
    telegram_id = TelegramId(8)
    await _seed_film(container, 501)

    await container.use_cases.library.add_to_watchlist(telegram_id, 501)
    before = await container.use_cases.library.list_watchlist(telegram_id)
    await container.use_cases.library.remove_from_watchlist(telegram_id, 501)
    after = await container.use_cases.library.list_watchlist(telegram_id)

    assert [film.id for film in before] == [501]
    assert after == []


async def test_collection_round_trips_through_the_real_stack(container: Container) -> None:
    telegram_id = TelegramId(9)
    await _seed_film(container, 501)

    collection = await container.use_cases.collections.create(telegram_id, "Избранное")
    assert collection.id is not None
    await container.use_cases.collections.add_film(telegram_id, collection.id, 501)

    films = await container.use_cases.collections.list_films(collection.id)

    assert [film.id for film in films] == [501]
