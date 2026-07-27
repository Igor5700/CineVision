from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_then_get_profile(client: TestClient) -> None:
    response = client.post("/users", json={"telegram_id": 100, "username": "ann"})

    assert response.status_code == 201
    body = response.json()
    assert body["telegram_id"] == 100
    assert body["username"] == "ann"
    assert body["balance"] == 0
    assert body["birthday"] is None

    profile = client.get("/users/100")
    assert profile.status_code == 200
    assert profile.json()["username"] == "ann"


def test_registering_twice_keeps_the_first_username(client: TestClient) -> None:
    client.post("/users", json={"telegram_id": 101, "username": "first"})

    response = client.post("/users", json={"telegram_id": 101, "username": "second"})

    assert response.json()["username"] == "first"


def test_get_profile_404_for_an_unknown_user(client: TestClient) -> None:
    response = client.get("/users/999999")
    assert response.status_code == 404


def test_update_display_name(client: TestClient) -> None:
    client.post("/users", json={"telegram_id": 102, "username": "ann"})

    response = client.put("/users/102/display-name", json={"display_name": "new-name"})

    assert response.status_code == 200
    assert response.json()["username"] == "new-name"


def test_update_display_name_rejects_a_blank_name(client: TestClient) -> None:
    client.post("/users", json={"telegram_id": 103, "username": "ann"})

    response = client.put("/users/103/display-name", json={"display_name": "   "})

    assert response.status_code == 422


def test_set_birthday(client: TestClient) -> None:
    client.post("/users", json={"telegram_id": 104, "username": "ann"})

    response = client.put("/users/104/birthday", json={"birthday": "15.06.1995"})

    assert response.status_code == 200
    assert response.json()["birthday"] == "1995-06-15"


def test_set_birthday_rejects_an_unparseable_date(client: TestClient) -> None:
    client.post("/users", json={"telegram_id": 105, "username": "ann"})

    response = client.put("/users/105/birthday", json={"birthday": "not-a-date"})

    assert response.status_code == 422
