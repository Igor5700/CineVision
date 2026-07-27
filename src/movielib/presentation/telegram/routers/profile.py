from __future__ import annotations

import html

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from movielib.bootstrap.container import UseCases
from movielib.domain.errors import DomainValidationError, InvalidBirthdayFormatError
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.telegram.formatters import SUPPORT_TEXT, format_profile
from movielib.presentation.telegram.guards import require_message, require_user_id
from movielib.presentation.telegram.keyboards import inline, reply
from movielib.presentation.telegram.states import Profile

router = Router(name="profile")


@router.message(F.text == reply.PROFILE_BUTTON)
async def show_profile(message: types.Message, state: FSMContext, use_cases: UseCases) -> None:
    await state.clear()
    telegram_id = TelegramId(require_user_id(message))
    user = await use_cases.users.get_profile(telegram_id)
    watchlist = await use_cases.library.list_watchlist(telegram_id)
    favorites = await use_cases.library.list_favorites(telegram_id)
    watched_count = await use_cases.library.count_watched(telegram_id)
    ratings = await use_cases.ratings.list_mine(telegram_id)
    collections = await use_cases.collections.list_mine(telegram_id)

    text = format_profile(
        user,
        watchlist_count=len(watchlist),
        favorites_count=len(favorites),
        watched_count=watched_count,
        ratings_count=len(ratings),
        collections_count=len(collections),
    )
    await message.answer(text=text, reply_markup=inline.profile_kb, parse_mode="HTML")


@router.message(F.text == reply.SUPPORT_BUTTON)
async def support(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text=SUPPORT_TEXT)


@router.callback_query(F.data == "edit_name")
async def edit_name_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await require_message(callback).answer(text="Введите новое отображаемое имя:")
    await state.set_state(Profile.editing_display_name)


@router.message(Profile.editing_display_name)
async def edit_name_process(message: types.Message, state: FSMContext, use_cases: UseCases) -> None:
    await state.clear()
    new_name = message.text or ""
    try:
        await use_cases.users.update_display_name(TelegramId(require_user_id(message)), new_name)
    except DomainValidationError:
        await message.answer(text="Имя не может быть пустым.")
        return
    await message.answer(
        text=f"Имя обновлено: <b>{html.escape(new_name.strip())}</b>", parse_mode="HTML"
    )


@router.callback_query(F.data == "set_birthday")
async def set_birthday_start(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await require_message(callback).answer(
        text=(
            "Укажите дату рождения в формате <code>ДД.ММ.ГГГГ</code>, "
            "например <code>15.06.1995</code>."
        ),
        parse_mode="HTML",
    )
    await state.set_state(Profile.setting_birthday)


@router.message(Profile.setting_birthday)
async def set_birthday_process(
    message: types.Message, state: FSMContext, use_cases: UseCases
) -> None:
    raw_birthday = message.text or ""
    try:
        birthday = await use_cases.users.set_birthday(
            TelegramId(require_user_id(message)), raw_birthday
        )
    except InvalidBirthdayFormatError:
        await message.answer(
            text=(
                "Не получилось распознать дату. Формат: <code>ДД.ММ.ГГГГ</code>, "
                "например <code>15.06.1995</code>."
            ),
            parse_mode="HTML",
        )
        return
    await state.clear()
    formatted = birthday.strftime("%d.%m.%Y")
    await message.answer(text=f"Дата рождения сохранена: <b>{formatted}</b>", parse_mode="HTML")
