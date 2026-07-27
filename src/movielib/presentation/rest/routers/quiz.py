from __future__ import annotations

from fastapi import APIRouter

from movielib.application.quiz.advance_quiz import advance_quiz
from movielib.domain.entities.quiz import QUIZ_QUESTIONS, QuizSession
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.rest.schemas.quiz import (
    QuizAnswerSchema,
    QuizQuestionSchema,
    QuizStepRequest,
    QuizStepResponse,
)

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/first-question", response_model=QuizQuestionSchema)
async def first_question() -> QuizQuestionSchema:
    return QuizQuestionSchema.from_domain(1, len(QUIZ_QUESTIONS), QUIZ_QUESTIONS[0])


@router.post("/steps", response_model=QuizStepResponse)
async def advance(body: QuizStepRequest) -> QuizStepResponse:
    session = QuizSession(
        telegram_id=TelegramId(body.telegram_id),
        answers=[answer.to_domain() for answer in body.answers],
    )
    result = advance_quiz(session, body.option_code)

    next_question = None
    if result.next_question is not None:
        next_question = QuizQuestionSchema.from_domain(
            session.next_question_index + 1, len(QUIZ_QUESTIONS), result.next_question
        )

    return QuizStepResponse(
        is_complete=result.is_complete,
        answers=[QuizAnswerSchema.from_domain(answer) for answer in session.answers],
        next_question=next_question,
        summary=result.summary_lines,
    )
