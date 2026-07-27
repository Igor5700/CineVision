from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher

from movielib.bootstrap.config import get_settings
from movielib.bootstrap.container import Container, build_container
from movielib.bootstrap.logging import configure_logging
from movielib.presentation.telegram.middlewares.di_middleware import ContainerMiddleware
from movielib.presentation.telegram.routers import library, personal_library, profile, quiz, start

logger = logging.getLogger(__name__)


def build_dispatcher(container: Container) -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.update.middleware(ContainerMiddleware(container))
    dispatcher.include_router(start.router)
    dispatcher.include_router(profile.router)
    dispatcher.include_router(library.router)
    dispatcher.include_router(personal_library.router)
    dispatcher.include_router(quiz.router)
    return dispatcher


async def run() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    bot = Bot(token=settings.bot_token)
    container = build_container(settings)
    dispatcher = build_dispatcher(container)

    try:
        logger.info("Starting polling")
        await dispatcher.start_polling(bot)
    finally:
        await container.engine.dispose()
        await bot.session.close()
