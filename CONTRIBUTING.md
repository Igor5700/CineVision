# Contributing

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate        # .venv/bin/activate on macOS/Linux
pip install -e ".[dev]"
cp .env.example .env           # fill in BOT_TOKEN, FILMS_API_TOKEN
alembic upgrade head
```

## Before sending a change

```bash
pytest              # unit tests (fakes) + integration tests (real SQLite)
ruff check .        # lint
mypy src            # type-check
```

All three must be clean. None of this needs real Telegram/Kinopoisk
credentials — tests run entirely against fakes, mocked HTTP, and a
temporary SQLite database, so CI never needs your secrets and you never
need to touch your `.env` to run the suite.

## Where does my change go?

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full picture.
The short version:

- New business rule, independent of any delivery mechanism? → `domain/`
  (entities, value objects) or `application/` (a use case).
- New way to store/fetch/call something? → `infrastructure/`, behind a
  port declared in `domain/ports/`.
- New Telegram command/button/flow for something that already has a use
  case? → `presentation/telegram/`.
- A brand new client (REST, CLI, Discord, …)? → a new `presentation/<client>/`
  package calling the existing `application` use cases — see
  "Adding a new client" in `docs/ARCHITECTURE.md`.

If you find yourself importing `aiogram`, `sqlalchemy`, or `aiohttp` inside
`domain/` or `application/`, stop — that dependency belongs in
`infrastructure/` or `presentation/`, reached through a port.

## Style

- Ruff (`ruff check .`) is the source of truth for import order and lint
  rules; `ruff format` isn't wired in yet, so match the surrounding code's
  formatting by eye.
- Type hints are mandatory; `mypy src` runs in `strict` mode.
- Prefer a fake in `tests/unit/fakes/` and a fast unit test over a real
  database/HTTP call, unless the test's whole point is exercising that
  real integration.

## Commits & PRs

Keep commits focused and describe the *why*, not just the *what* — the
diff already shows what changed. Make sure `pytest`, `ruff check .`, and
`mypy src` all pass before opening a PR; CI runs the same three checks.
