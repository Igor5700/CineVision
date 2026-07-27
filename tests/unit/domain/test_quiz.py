import pytest

from movielib.domain.entities.quiz import QUIZ_QUESTIONS, QuizSession, resolve_answer_label
from movielib.domain.errors import DomainValidationError, QuizAlreadyCompleteError
from movielib.domain.value_objects.telegram_id import TelegramId


def _new_session() -> QuizSession:
    return QuizSession(telegram_id=TelegramId(1))


def _answer_everything(session: QuizSession) -> None:
    for _ in range(len(QUIZ_QUESTIONS)):
        session.record_answer(QUIZ_QUESTIONS[session.next_question_index].options[0].code)


def test_quiz_session_tracks_progress() -> None:
    session = _new_session()
    assert session.next_question_index == 0
    assert not session.is_complete()

    _answer_everything(session)

    assert session.is_complete()
    assert len(session.answers) == len(QUIZ_QUESTIONS)


def test_quiz_session_rejects_extra_answers() -> None:
    session = _new_session()
    _answer_everything(session)

    with pytest.raises(QuizAlreadyCompleteError):
        session.record_answer(QUIZ_QUESTIONS[0].options[0].code)


def test_resolve_answer_label_looks_up_within_its_own_question() -> None:
    first_question = QUIZ_QUESTIONS[0]
    label = resolve_answer_label(0, first_question.options[0].code)
    assert label == first_question.options[0].label


def test_resolve_answer_label_rejects_unknown_code() -> None:
    with pytest.raises(DomainValidationError):
        resolve_answer_label(0, "not-a-real-option")
