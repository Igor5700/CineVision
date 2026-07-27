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


def test_create_then_list_mine(client: TestClient) -> None:
    create = client.post("/users/420/collections", json={"name": "Мои"})
    assert create.status_code == 201
    collection_id = create.json()["id"]

    listed = client.get("/users/420/collections")
    assert [c["id"] for c in listed.json()] == [collection_id]

    fetched = client.get(f"/collections/{collection_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Мои"


def test_rejects_a_blank_name(client: TestClient) -> None:
    response = client.post("/users/421/collections", json={"name": "   "})
    assert response.status_code == 422


def test_get_unknown_collection_404s(client: TestClient) -> None:
    response = client.get("/collections/999999")
    assert response.status_code == 404


async def test_owner_can_add_and_remove_a_film(
    client: TestClient, seed_container: Container
) -> None:
    await _seed_film(seed_container)
    create = client.post("/users/422/collections", json={"name": "Мои"})
    collection_id = create.json()["id"]

    add = client.post(f"/users/422/collections/{collection_id}/films/{_FILM_ID}")
    assert add.status_code == 204
    films = client.get(f"/collections/{collection_id}/films")
    assert [f["id"] for f in films.json()] == [_FILM_ID]

    remove = client.delete(f"/users/422/collections/{collection_id}/films/{_FILM_ID}")
    assert remove.status_code == 204
    assert client.get(f"/collections/{collection_id}/films").json() == []


def test_non_owner_cannot_delete_the_collection(client: TestClient) -> None:
    create = client.post("/users/423/collections", json={"name": "Мои"})
    collection_id = create.json()["id"]

    response = client.delete(f"/users/999999/collections/{collection_id}")

    assert response.status_code == 403
    assert client.get(f"/collections/{collection_id}").status_code == 200


def test_owner_can_delete_the_collection(client: TestClient) -> None:
    create = client.post("/users/424/collections", json={"name": "Мои"})
    collection_id = create.json()["id"]

    response = client.delete(f"/users/424/collections/{collection_id}")

    assert response.status_code == 204
    assert client.get(f"/collections/{collection_id}").status_code == 404
