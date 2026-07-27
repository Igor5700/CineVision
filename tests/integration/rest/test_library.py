from __future__ import annotations

from fastapi.testclient import TestClient

from movielib.bootstrap.container import Container
from movielib.domain.entities.film import Film
from movielib.infrastructure.persistence.film_repository_sqlalchemy import (
    SqlAlchemyFilmRepository,
)

_FILM_ID = 501


async def _seed_film(container: Container) -> None:
    repo = SqlAlchemyFilmRepository(container.session_factory)
    await repo.upsert_many(
        [
            Film(
                id=_FILM_ID,
                title="Матрица",
                kind="movie",
                year=1999,
                description=None,
                poster_url=None,
            )
        ]
    )


async def test_watchlist_add_list_remove(client: TestClient, seed_container: Container) -> None:
    await _seed_film(seed_container)

    add = client.post(f"/users/300/watchlist/{_FILM_ID}")
    assert add.status_code == 204

    listed = client.get("/users/300/watchlist")
    assert listed.status_code == 200
    assert [film["id"] for film in listed.json()] == [_FILM_ID]

    remove = client.delete(f"/users/300/watchlist/{_FILM_ID}")
    assert remove.status_code == 204
    assert client.get("/users/300/watchlist").json() == []


async def test_favorites_add_list_remove(client: TestClient, seed_container: Container) -> None:
    await _seed_film(seed_container)

    client.post(f"/users/301/favorites/{_FILM_ID}")
    listed = client.get("/users/301/favorites")

    assert [film["id"] for film in listed.json()] == [_FILM_ID]


async def test_mark_watched_then_list_history(
    client: TestClient, seed_container: Container
) -> None:
    await _seed_film(seed_container)

    response = client.post(f"/users/302/history/{_FILM_ID}")
    assert response.status_code == 204

    listed = client.get("/users/302/history")
    assert [film["id"] for film in listed.json()] == [_FILM_ID]


def test_watchlist_is_empty_for_a_fresh_user(client: TestClient) -> None:
    response = client.get("/users/999999/watchlist")
    assert response.status_code == 200
    assert response.json() == []


def test_recent_searches_is_empty_for_a_fresh_user(client: TestClient) -> None:
    response = client.get("/users/999999/recent-searches")
    assert response.status_code == 200
    assert response.json() == []
