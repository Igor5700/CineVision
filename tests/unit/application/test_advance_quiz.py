from __future__ import annotations

import pytest

from movielib.application.quiz.advance_quiz import advance_quiz
from movielib.domain.entities.quiz import QUIZ_QUESTIONS, QuizSession
from movielib.domain.errors import QuizAlreadyCompleteError
from movielib.domain.value_objects.telegram_id import TelegramId


def test_returns_the_next_question_until_the_last_one() -> None:
    session = QuizSession(telegram_id=TelegramId(1))

    result = advance_quiz(session, QUIZ_QUESTIONS[0].options[0].code)

    assert not result.is_complete
    assert result.next_question == QUIZ_QUESTIONS[1]
    assert result.summary_lines is None


def test_returns_a_summary_after_the_final_question() -> None:
    session = QuizSession(telegram_id=TelegramId(1))
    for question in QUIZ_QUESTIONS[:-1]:
        advance_quiz(session, question.options[0].code)

    result = advance_quiz(session, QUIZ_QUESTIONS[-1].options[1].code)

    assert result.is_complete
    assert result.next_question is None
    assert result.summary_lines == [q.options[0].label for q in QUIZ_QUESTIONS[:-1]] + [
        QUIZ_QUESTIONS[-1].options[1].label
    ]


def test_raises_once_the_quiz_is_already_complete() -> None:
    session = QuizSession(telegram_id=TelegramId(1))
    for question in QUIZ_QUESTIONS:
        advance_quiz(session, question.options[0].code)

    with pytest.raises(QuizAlreadyCompleteError):
        advance_quiz(session, QUIZ_QUESTIONS[0].options[0].code)
