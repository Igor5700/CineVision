from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from pathlib import Path

from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from PIL import Image

from movielib.bootstrap.container import UseCases
from movielib.domain.value_objects.telegram_id import TelegramId
from movielib.presentation.telegram.formatters import CONTACT_TEXT, WELCOME_TEXT
from movielib.presentation.telegram.guards import require_from_user
from movielib.presentation.telegram.keyboards.reply import main_menu_kb

router = Router(name="start")

# Relative to the process's working directory — the same assumption
# `DATABASE_URL=sqlite+aiosqlite:///data/movielib.db` already makes, so the
# bot is expected to run from the repo root (or /app in the Docker image,
# which COPYs public/ there too).
_LOGO_PATH = Path("public/CINEVISION_logo.png")

# Telegram rejects a photo once width + height exceeds 10000 — the source
# asset is 10123x6052, well past that. Resized once, in memory, rather than
# overwriting the original file on disk.
_MAX_TELEGRAM_PHOTO_SIDE = 1280


@lru_cache(maxsize=1)
def _logo_bytes() -> bytes:
    with Image.open(_LOGO_PATH) as image:
        image.thumbnail((_MAX_TELEGRAM_PHOTO_SIDE, _MAX_TELEGRAM_PHOTO_SIDE))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext, use_cases: UseCases) -> None:
    await state.clear()
    from_user = require_from_user(message)
    await use_cases.users.register(TelegramId(from_user.id), from_user.username)
    await message.answer_photo(
        photo=types.BufferedInputFile(_logo_bytes(), filename="CINEVISION_logo.png"),
        caption=WELCOME_TEXT,
        reply_markup=main_menu_kb,
    )


@router.message(Command("contacts"))
async def contacts(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text=CONTACT_TEXT)
