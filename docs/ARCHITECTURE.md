# Architecture

## The dependency rule

```
presentation ─┐
              ├──▶ application ──▶ domain
infrastructure┘
                       ▲
                   bootstrap
              (wires infrastructure + presentation
               to application, at startup only)
```

Arrows point inward. `domain` depends on nothing. `application` depends only
on `domain` (and the ports it declares). `infrastructure` and `presentation`
depend on `application`/`domain` — never on each other, and application code
never imports either of them directly. `bootstrap` is the one place that's
allowed to import a port and a concrete adapter side by side; everywhere
else, a type from `infrastructure` or `presentation.telegram` showing up
inside `domain`/`application` is a bug.

## Layers

- **`domain/`** — entities (`User`, `Film`, `QuizSession`, `WatchlistEntry`,
  `FavoriteEntry`, `ViewingHistoryEntry`, `Rating`, `Review`, `Collection`,
  `SearchHistoryEntry`), value objects (`TelegramId`, `Balance`), the domain
  error hierarchy, and **ports**: `Protocol` interfaces (`UserRepository`,
  `FilmRepository`, `FilmMetadataProvider`, `LibraryRepository`,
  `RatingRepository`, `ReviewRepository`, `CollectionRepository`,
  `SearchHistoryRepository`, `Clock`) that `application` depends on and
  `infrastructure` implements. Zero third-party imports — no aiogram, no
  SQLAlchemy, no aiohttp.
- **`application/`** — one class (or, where there's no state to inject,
  one plain function) per use case, grouped into subpackages by concern:
  `users/` (register, profile, birthday, display name),
  `films/` (`SearchFilms`, `GetFilmDetails` — live-catalog lookups, see
  below), `library/` (watchlist, favorites, viewing history),
  `ratings/`, `reviews/`, `collections/`, `search/` (recent-search
  history), `quiz/` (`advance_quiz`). Each depends only on ports, never on a
  concrete adapter — that's what makes them testable against the in-memory
  fakes in `tests/unit/fakes` with no I/O.
- **`infrastructure/`** — concrete adapters: `persistence/` (SQLAlchemy
  models + repositories + Alembic migrations), `external/kinopoisk_client.py`
  (the film-metadata provider), `clock_system.py`.
- **`presentation/telegram/`** — aiogram routers, keyboards, FSM states, and
  a DI middleware that hands each handler the use cases it needs.
- **`presentation/rest/`** — FastAPI routers, Pydantic request/response
  schemas, and a `DomainError → HTTP status` mapping. Both presentation
  packages call the *same* `application` use cases and never touch
  `infrastructure` or a repository directly.
- **`bootstrap/`** — `config.py` (settings from `.env`), `logging.py`
  (structured JSON logs), `container.py` (the channel-agnostic composition
  root), `app.py` (Telegram polling entrypoint), `rest_app.py` (the
  `uvicorn`-served ASGI entrypoint).

## Adding a new client

Telegram is not privileged — it's an adapter like any other, and the REST
API is proof: it was added without changing one line of `domain/` or
`application/`. A CLI, a Discord bot, or an MCP server is added the same way:

1. Write a new `presentation/<client>/` package that calls the existing
   `application` use cases (via `Container.use_cases`, injected however
   that client's framework does DI) and translates results into that
   client's own request/response shape.
2. Write a new `bootstrap/<client>_app.py` entrypoint (its own process),
   reusing `build_container`. If the client ever needs a channel-specific
   capability `Container` doesn't provide (e.g. something only that
   channel's SDK can do), wire that piece separately on top of the shared
   container instead of growing `Container`'s own constructor to know about
   every channel.
3. Don't touch `domain/` or `application/` unless the new client needs a
   use case that genuinely doesn't exist yet — in which case it's added
   once, in `application/`, and every client benefits.

`build_container(settings)` builds everything channel-agnostic: repositories,
the film-metadata client, the clock, and every use case. It takes no `Bot`,
no HTTP framework, nothing Telegram- or REST-specific — both the Telegram
bootstrap (`bootstrap/app.py`) and the REST bootstrap
(`presentation/rest/app.py`) call it directly.

## REST authorization

The personal-library endpoints (watchlist, favorites, ratings, reviews,
collections) have a **weak** trust model by design-so-far: a caller
identifies themselves by simply passing a `telegram_id`, the same way
`POST /users` lets anyone register any id. `ensure_owner` (in
`application/authorization.py`) stops a caller from editing *someone
else's* review or collection once a `telegram_id` is presented, but nothing
today proves the caller actually owns that id — there's no session, token,
or signature. This is a known, deliberate gap for the current stage (no
real users yet) rather than an oversight; real authentication (e.g.
Telegram's own login-widget signature verification, or a session token
issued after some login flow) is the natural next step before this API is
exposed to the public, and it slots in as a FastAPI dependency without
needing an application-layer change.

## The live film catalog

Search and film details never require anything to have been pre-loaded.
`SearchFilms` calls the live `FilmMetadataProvider` (Kinopoisk) first on
every query, `upsert`s whatever it gets back into the local `films` table,
and returns those live results — poster, description, and Kinopoisk's own
rating included. The local table is a *cache* for reference-stability
(watchlist/favorites/ratings/reviews/collections all point at a `film_id`,
so it has to keep existing after the search that first surfaced it) and a
resilience fallback (`SearchFilms` falls back to a `LIKE` search over the
cache only if the live call fails or returns nothing), not a manually
curated catalog. `GetFilmDetails` is cache-first instead — a film that's
already been searched or looked up doesn't need a second network round
trip — falling back to a live `get_by_id` lookup (and caching that too)
only for a film nobody has fetched yet.

This replaced a Phase 1 design where films only entered the system through
a manually triggered "import" action (`ImportFilmsFromProvider`, now
deleted). That design meant a user's search only ever found what had
already been imported — the opposite of what a movie-library product
needs. Removing it was a deliberate product-correctness fix, not a
refactor for its own sake.

## `UseCases` grouping

`bootstrap/container.py`'s `UseCases` is a dataclass of dataclasses —
`UseCases.users`, `.films`, `.library`, `.ratings`, `.reviews`,
`.collections`, `.search` — rather than one flat namespace. With 8 use
cases (Phase 1/2) a flat `UseCases.search_films` read fine; past 25, a flat
namespace stops being something you can scan, and the grouping is the
refactor that had to happen before adding *more* use cases, not an
afterthought. Every adapter (Telegram routers, REST routers) reads through
the group: `use_cases.library.add_to_watchlist(...)`,
`use_cases.collections.list_mine(...)`, and so on.

## Why these specific choices

- **SQLAlchemy 2.0 (async) + Alembic, SQLite by default** — the repository
  implementations talk to the ORM, never raw SQL strings. Moving to
  Postgres later is a `DATABASE_URL` change, not a rewrite.
- **A hand-rolled composition root instead of a DI framework** — at this
  scope, `dependency-injector` (or similar) buys indirection without buying
  much: `container.py` is a few explicit factory calls anyone can read
  top-to-bottom.
- **stdlib `logging` + a small JSON formatter** instead of `structlog` —
  one fewer dependency, and every future adapter (REST, CLI, …) gets
  structured logs for free from the same setup.
- **Ports as `typing.Protocol`, not ABCs** — the in-memory test fakes in
  `tests/unit/fakes/` satisfy a port structurally, with no inheritance
  ceremony.

## Testing strategy

- `tests/unit/domain/` and `tests/unit/application/` — pure logic and use
  cases against the fakes in `tests/unit/fakes/`. No I/O, runs in
  milliseconds.
- `tests/unit/infrastructure/` — adapters tested in isolation (the
  Kinopoisk client against a mocked HTTP transport via `aioresponses`).
- `tests/unit/presentation/` — pure formatting/keyboard-building logic
  (Telegram) with no aiogram dispatcher involved.
- `tests/integration/bootstrap/` and `tests/integration/persistence/` —
  the real composition root and real SQLAlchemy repositories against a
  real (temp-file) SQLite database, migrated with the actual Alembic
  revisions rather than `Base.metadata.create_all` — so a migration that
  drifted from the ORM models fails these tests too.
- `tests/integration/rest/` — the real FastAPI app (`TestClient`, which
  runs the actual ASGI lifespan) against the same kind of real, migrated
  SQLite database, covering the full HTTP request → use case → database
  round trip, ownership checks on reviews/collections, and domain-error →
  HTTP-status mapping. Every call
  into `SearchFilms`/`GetFilmDetails` here mocks the Kinopoisk HTTP
  transport via `aioresponses` — since both now call the live provider by
  design, an unmocked test would either hit the real network or fail on
  the fake token these tests use.

No test anywhere needs a real Telegram or Kinopoisk credential — CI never
touches your `.env`.
