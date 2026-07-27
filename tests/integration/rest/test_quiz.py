from __future__ import annotations

from fastapi.testclient import TestClient

from movielib.domain.entities.quiz import QUIZ_QUESTIONS


def test_first_question(client: TestClient) -> None:
    response = client.get("/quiz/first-question")

    assert response.status_code == 200
    body = response.json()
    assert body["index"] == 1
    assert body["total"] == len(QUIZ_QUESTIONS)
    assert body["prompt"] == QUIZ_QUESTIONS[0].prompt


def test_full_quiz_progression_is_stateless_and_client_held(client: TestClient) -> None:
    answers: list[dict[str, object]] = []
    for question in QUIZ_QUESTIONS[:-1]:
        response = client.post(
            "/quiz/steps",
            json={"telegram_id": 1, "answers": answers, "option_code": question.options[0].code},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_complete"] is False
        assert body["summary"] is None
        answers = body["answers"]

    last_question = QUIZ_QUESTIONS[-1]
    response = client.post(
        "/quiz/steps",
        json={
            "telegram_id": 1,
            "answers": answers,
            "option_code": last_question.options[1].code,
        },
    )

    body = response.json()
    assert body["is_complete"] is True
    assert body["next_question"] is None
    assert len(body["summary"]) == len(QUIZ_QUESTIONS)


def test_an_invalid_option_code_surfaces_as_a_422_once_the_quiz_completes(
    client: TestClient,
) -> None:
    answers: list[dict[str, object]] = []
    for question in QUIZ_QUESTIONS[:-1]:
        response = client.post(
            "/quiz/steps",
            json={"telegram_id": 1, "answers": answers, "option_code": question.options[0].code},
        )
        answers = response.json()["answers"]

    response = client.post(
        "/quiz/steps",
        json={"telegram_id": 1, "answers": answers, "option_code": "not-a-real-option"},
    )

    assert response.status_code == 422
