from __future__ import annotations

from dataclasses import dataclass

from movielib.domain.entities.quiz import (
    QUIZ_QUESTIONS,
    QuizQuestion,
    QuizSession,
    resolve_answer_label,
)


@dataclass(frozen=True, slots=True)
class QuizStepResult:
    is_complete: bool
    next_question: QuizQuestion | None
    summary_lines: list[str] | None


def advance_quiz(session: QuizSession, option_code: str) -> QuizStepResult:
    session.record_answer(option_code)
    if session.is_complete():
        summary = [
            resolve_answer_label(answer.question_index, answer.option_code)
            for answer in session.answers
        ]
        return QuizStepResult(is_complete=True, next_question=None, summary_lines=summary)
    return QuizStepResult(
        is_complete=False,
        next_question=QUIZ_QUESTIONS[session.next_question_index],
        summary_lines=None,
    )
