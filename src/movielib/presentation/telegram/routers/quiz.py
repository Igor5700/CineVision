from __future__ import annotations

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from movielib.application.quiz.advance_quiz import advance_quiz
from movielib.domain.entities.quiz import QUIZ_QUESTIONS, QuizSession
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.telegram.formatters import format_quiz_question, format_quiz_summary
from movielib.presentation.telegram.guards import require_data, require_message, require_user_id
from movielib.presentation.telegram.keyboards import inline, reply
from movielib.presentation.telegram.states import Quiz

router = Router(name="quiz")

_SESSION_KEY = "quiz_session"


@router.message(F.text == reply.QUIZ_BUTTON)
async def start_quiz(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    session = QuizSession(telegram_id=TelegramId(require_user_id(message)))
    await state.set_state(Quiz.in_progress)
    await state.update_data({_SESSION_KEY: session})

    question = QUIZ_QUESTIONS[0]
    await message.answer(
        text=format_quiz_question(1, len(QUIZ_QUESTIONS), question.prompt),
        reply_markup=inline.quiz_question_kb(question),
        parse_mode="HTML",
    )


@router.callback_query(Quiz.in_progress, F.data.startswith("quiz:"))
async def answer_quiz(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    message = require_message(callback)
    option_code = require_data(callback).split(":", 1)[1]

    data = await state.get_data()
    session: QuizSession = data[_SESSION_KEY]
    result = advance_quiz(session, option_code)

    if result.is_complete:
        await state.clear()
        assert result.summary_lines is not None
        await message.edit_text(
            text=format_quiz_summary(result.summary_lines), parse_mode="HTML"
        )
        return

    await state.update_data({_SESSION_KEY: session})
    assert result.next_question is not None
    await message.edit_text(
        text=format_quiz_question(
            session.next_question_index + 1, len(QUIZ_QUESTIONS), result.next_question.prompt
        ),
        reply_markup=inline.quiz_question_kb(result.next_question),
        parse_mode="HTML",
    )
