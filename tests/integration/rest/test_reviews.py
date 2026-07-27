from __future__ import annotations

from fastapi.testclient import TestClient

_FILM_ID = 501


def test_write_then_get_mine(client: TestClient) -> None:
    response = client.put(f"/users/410/reviews/{_FILM_ID}", json={"text": "Отлично"})
    assert response.status_code == 200
    assert response.json()["text"] == "Отлично"

    mine = client.get(f"/users/410/reviews/{_FILM_ID}")
    assert mine.status_code == 200
    assert mine.json()["text"] == "Отлично"


def test_rejects_blank_text(client: TestClient) -> None:
    response = client.put(f"/users/411/reviews/{_FILM_ID}", json={"text": "   "})
    assert response.status_code == 422


def test_delete_removes_the_review(client: TestClient) -> None:
    client.put(f"/users/412/reviews/{_FILM_ID}", json={"text": "Текст"})

    delete = client.delete(f"/users/412/reviews/{_FILM_ID}")
    assert delete.status_code == 204

    mine = client.get(f"/users/412/reviews/{_FILM_ID}")
    assert mine.json() is None


def test_list_for_film(client: TestClient) -> None:
    client.put(f"/users/413/reviews/{_FILM_ID}", json={"text": "Про этот фильм"})

    response = client.get(f"/films/{_FILM_ID}/reviews")

    assert response.status_code == 200
    assert [r["text"] for r in response.json()] == ["Про этот фильм"]
