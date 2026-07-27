from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

PROFILE_BUTTON = "Личный кабинет"
LIBRARY_BUTTON = "Библиотека"
QUIZ_BUTTON = "Тест предпочтений"
SUPPORT_BUTTON = "Поддержка"

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=PROFILE_BUTTON), KeyboardButton(text=LIBRARY_BUTTON)],
        [KeyboardButton(text=QUIZ_BUTTON), KeyboardButton(text=SUPPORT_BUTTON)],
    ],
    resize_keyboard=True,
)
