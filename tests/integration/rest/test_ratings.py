from __future__ import annotations

from fastapi.testclient import TestClient

_FILM_ID = 501


def test_rate_then_get_mine(client: TestClient) -> None:
    response = client.put(f"/users/400/ratings/{_FILM_ID}", json={"score": 8})
    assert response.status_code == 200
    assert response.json()["score"] == 8

    mine = client.get(f"/users/400/ratings/{_FILM_ID}")
    assert mine.status_code == 200
    assert mine.json()["score"] == 8


def test_rejects_a_score_out_of_range(client: TestClient) -> None:
    response = client.put(f"/users/401/ratings/{_FILM_ID}", json={"score": 11})
    assert response.status_code == 422


def test_get_mine_is_null_when_unrated(client: TestClient) -> None:
    response = client.get(f"/users/999999/ratings/{_FILM_ID}")
    assert response.status_code == 200
    assert response.json() is None


def test_average_rating(client: TestClient) -> None:
    client.put(f"/users/402/ratings/{_FILM_ID}", json={"score": 8})
    client.put(f"/users/403/ratings/{_FILM_ID}", json={"score": 6})

    response = client.get(f"/films/{_FILM_ID}/rating")

    assert response.status_code == 200
    assert response.json() == {"film_id": _FILM_ID, "average": 7.0}


def test_average_rating_is_null_when_unrated(client: TestClient) -> None:
    response = client.get("/films/999999/rating")
    assert response.status_code == 200
    assert response.json()["average"] is None
