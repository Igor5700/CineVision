# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./
COPY public ./public

RUN pip install .

RUN useradd --create-home --shell /bin/bash movielib \
    && mkdir -p /app/data \
    && chown -R movielib:movielib /app
USER movielib

# A single-instance deployment: migrating on every start is simplest and
# safe here. A multi-replica deployment should run `alembic upgrade head`
# as its own one-off job instead, so N replicas don't race the migration.
CMD ["sh", "-c", "alembic upgrade head && python -m movielib"]
