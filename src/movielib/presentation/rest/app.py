from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from movielib.bootstrap.config import Settings, get_settings
from movielib.bootstrap.container import build_container
from movielib.presentation.rest.errors import register_error_handlers
from movielib.presentation.rest.routers import (
    collections,
    films,
    library,
    quiz,
    ratings,
    reviews,
    users,
)


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.container = build_container(resolved_settings)
        try:
            yield
        finally:
            await app.state.container.engine.dispose()

    app = FastAPI(
        title="movielib REST API",
        description=(
            "A REST adapter over the same application use cases the Telegram bot "
            "uses — the concrete proof the core doesn't know Telegram exists."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    register_error_handlers(app)
    app.include_router(users.router)
    app.include_router(films.router)
    app.include_router(library.router)
    app.include_router(ratings.router)
    app.include_router(reviews.router)
    app.include_router(collections.router)
    app.include_router(quiz.router)
    return app
