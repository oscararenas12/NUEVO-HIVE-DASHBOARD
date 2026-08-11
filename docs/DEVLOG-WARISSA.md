# Warissa's Development Log

Format: Date | Who (human/agent) | Decision + Reasoning

---

Welcome! This is your decision log. After every significant change, write an entry explaining WHY you made the decisions you did. Check this file and DEVLOG-OSCAR.md after every pull from main.

Read docs/RULES.md, docs/STACK.md, and docs/STRUCTURE.md to get up to speed on the project.

---

## 2026-08-06 | Warissa + Claude

### Phase 1, Branch A: FastAPI scaffold + /ping health check

Split Phase 1 into two branches. Branch A (`feature/phase-1-app`) is the app code +
tests that run locally and turn CI green; Branch B (`feature/phase-1-docker`) will add
the Dockerfile and entrypoint. This keeps the TDD core reviewable on its own, separate
from container infra.

Decisions and reasoning:

- **Config env vars (`config.py`).** `DATABASE_URL` gets a *safe default* matching
  docker-compose (`postgresql://postgres:postgres@api-db:5432/hive_dev`), plus an
  optional `DATABASE_TEST_URL` and a `TESTING` flag; `active_database_url` picks the
  test URL only when testing. WHY: our three sources disagreed — compose and the plan
  use `DATABASE_URL`, but CI (`.github/workflows/main.yml`) only sets
  `DATABASE_TEST_URL`. A required-with-no-default field would crash CI and refuse to
  boot the container. The default satisfies compose, the plan, and CI at once.

- **/ping returns `{"status": "ok", "environment": <from config>}`.** WHY: the plan
  stated the shape two ways (`{"status":"ok","environment":"dev"}` vs bare
  `{"status":"ok"}`). Chose the richer one because reading `environment` from config
  lightly smoke-tests the settings layer, which is the whole point of Phase 1. The test
  asserts `status == "ok"` and that `environment` is present (not pinned to "dev") so it
  stays honest across dev/test/CI.

- **Pydantic v2 + `pydantic-settings`.** WHY: in Pydantic v2 `BaseSettings` moved to the
  separate `pydantic-settings` package. SQLModel is also on Pydantic v2, so this keeps
  one Pydantic major across the stack.

Edge case hit (as the plan warned): the config tests were initially not hermetic —
pydantic-settings fills any field you *don't* pass from the process environment, so under
CI (where `DATABASE_TEST_URL` is set) the "falls back to primary" test wrongly picked up
the ambient test URL. Fixed with an autouse fixture that clears the DB env vars, making
the config tests deterministic regardless of environment. Verified by running the suite
both with a clean env and with a simulated CI env — 7/7 pass in both.

Note: a cosmetic `StarletteDeprecationWarning` (httpx vs httpx2 in TestClient) shows up;
it's a warning only, tests pass. Will revisit if it becomes an error on a future bump.

---

## 2026-08-07 | Warissa + Claude

### Phase 1, Branch B: containerize the API (Dockerfile + entrypoint)

Added the container half of Phase 1 on `feature/phase-1-docker`: `services/api/Dockerfile`
and `services/api/entrypoint.sh`. The app from Branch A was unchanged.

Decisions and reasoning:

- **Base image: `python:3.12-slim`.** WHY: matches the Python 3.12 in STACK.md and keeps the
  image small; psycopg2-binary ships as a wheel so no compiler/build tools are needed.

- **Install `postgresql-client` in the image.** WHY: the entrypoint's DB-wait loop uses
  `pg_isready`, which comes from that package. It's the readiness check the Phase 1 plan
  called for.

- **Entrypoint waits for Postgres before starting the API.** WHY: compose `depends_on` only
  controls start *order*, not readiness — the API would otherwise race ahead of the DB. The
  script loops on `pg_isready -h api-db -p 5432 -U postgres` (host/port/user overridable via
  env) until it succeeds, then starts the server.

- **Uvicorn listens on container port `5000`; compose maps it to host `5001`.** WHY: the
  existing `docker-compose.yml` maps `5001:5000`, so the server must bind `--host 0.0.0.0
  --port 5000`. From the host it's reached at `:5001` (matches the README/Swagger URLs).

- **`--reload` for now.** WHY: compose bind-mounts `./services/api:/usr/src/app`, so live
  code edits should hot-reload during development. A production/multi-stage image is a Phase 6
  concern. Used the `exec` form so uvicorn becomes PID 1 and receives container signals.

- **Alembic migrations intentionally omitted.** WHY: the Phase 1 plan text mentioned running
  migrations in the entrypoint, but Alembic config and migrations don't exist until Phase 2 —
  calling `alembic upgrade head` now would crash the container on startup. Left a comment in
  the script noting Phase 2 adds it. Kept Branch B strictly to container infra.

- **`docker-compose.yml` did NOT need changes.** WHY: its `api` service already had the right
  build context, `Dockerfile` reference, bind mount, `5001:5000` mapping, `DATABASE_URL`, and
  `depends_on: api-db`. Adding a DB healthcheck would be redundant with the entrypoint wait, so
  I left compose alone. (Cosmetic aside: compose warns that the top-level `version:` key is
  obsolete — noted, but out of scope for Branch B.)

Verification (Docker Desktop running): image built successfully; `api` and `api-db` containers
started; logs showed `Waiting for Postgres at api-db:5432... -> Postgres is ready.` then
uvicorn on `0.0.0.0:5000` with the WatchFiles reloader. `GET /ping` returned
`{"status":"ok","environment":"dev"}` (200), `/docs` served the Swagger UI (200), and
`/openapi.json` exposed the `Nuevo Hive API` schema with the `/ping` path. All 7 Branch A
tests passed inside the container (`docker compose exec api python -m pytest src/tests`).
Containers were torn down cleanly afterward with `docker compose down`.

---

## 2026-08-08 | Warissa + Claude

### Phase 2, Branch A: User model + DB session + CRUD (feature/phase-2-models)

Built the data layer that gives the API a persistent `users` table, tested against a real
Postgres database. No Alembic and no endpoints yet -- migrations are Branch B, endpoints are
Phase 3. Split Phase 2 the same way as Phase 1: Branch A = model/data logic + tests (turns CI
green on its own), Branch B = schema/migration infra (needs Docker + Postgres to verify).

Decisions and reasoning:

- **Table named `users`, not `user`.** WHY: `user` is a reserved word in Postgres (`SELECT
  user` returns the current role). SQLAlchemy would auto-quote it, but anything outside the
  ORM (psql, raw SQL, hand-edited migrations) would have to remember the quotes -- a latent
  foot-gun with no upside. Set `__tablename__ = "users"` explicitly; the Python class stays
  the singular `User`.

- **Test against real PostgreSQL, not SQLite in-memory.** WHY: our Phase 1 config + CI were
  already built around a Postgres test DB (`DATABASE_TEST_URL`, `active_database_url`), and CI
  already spins up Postgres 16. Testing on the real engine avoids the class of bug where
  SQLite passes but Postgres fails (types, constraints, `server_default`). Cost: tests now
  need a running Postgres. `conftest.py` reads `DATABASE_TEST_URL` (CI provides it; locally we
  created a dedicated `hive_test` DB in the api-db container and export the 5436 URL).

- **Per-test isolation via transaction rollback (commit-safe SAVEPOINT).** WHY: unlike a fresh
  in-memory SQLite, a persistent Postgres DB keeps rows between tests. Because our
  `create_user` commits, a plain outer-transaction rollback isn't enough -- so `conftest.py`
  uses the SQLAlchemy "join an external transaction" recipe: bind the session to a connection
  with an open transaction, run inside a SAVEPOINT, and restart the SAVEPOINT after each commit
  via an `after_transaction_end` listener. Teardown rolls back the outer transaction, leaving
  the DB pristine. This resolved cleanly, including the uniqueness tests that raise
  `IntegrityError` -- no TRUNCATE fallback needed.

- **`created_at`: database-side, timezone-aware.** WHY: `Column(DateTime(timezone=True),
  server_default=func.now())` means every row's timestamp comes from one source (the DB
  clock), not from whichever app/container happens to insert it. Consequence: the value isn't
  populated on the Python object until commit + `session.refresh()`, so `create_user` refreshes
  before returning and the test asserts `created_at` after that.

- **Function-based CRUD (`crud.py`), not a repository class.** WHY: it's the lightweight
  version of the repository pattern -- one place that owns user reads/writes so endpoints never
  touch the DB directly -- and it matches the plan and the FastAPI tutorial the project follows.

Side effect noted: the Phase 1 `/ping` tests now pull in the `session` fixture transitively
(via the `client` fixture), so they need Postgres up too. True in CI and locally; the endpoint
behavior is unchanged.

Verification: `pytest src/tests -v` against `localhost:5436/hive_test` -> 17 passed (10 new
user tests + the 7 Phase 1 tests). Isolation confirmed by `test_get_all_users` expecting
exactly 2 rows passing. Alembic migrations, the entrypoint auto-`upgrade`, and verifying the
real `users` table in Postgres are Branch B.

---

## 2026-08-11 | Warissa + Claude

### Phase 2, Branch B: Alembic migrations + auto-migrate on startup (feature/phase-2-migrations)

Added schema version control. Branch A's tests build tables with
`SQLModel.metadata.create_all()`, but nothing created the `users` table in the real Postgres.
Branch B makes a reviewed Alembic migration the source of truth and runs it automatically when
the container starts.

Decisions and reasoning:

- **Alembic URL comes from `get_settings().database_url` (env-overridable), set in `env.py`.**
  WHY: migrations must always target the real database, never the test DB, and the URL
  shouldn't be hardcoded in `alembic.ini` (it ships in the image). `env.py` calls
  `config.set_main_option("sqlalchemy.url", get_settings().database_url)` and points
  `target_metadata` at `SQLModel.metadata` after importing the `User` model so its table is
  registered.

- **Added `import sqlmodel` to `migrations/script.py.mako`.** WHY: SQLModel columns render as
  `sqlmodel.sql.sqltypes.AutoString(...)` in autogenerated migrations, but Alembic does not add
  the `import sqlmodel` line -- so `alembic upgrade` would crash with a NameError. Fixing the
  template once means every future migration imports it. Confirmed the generated file
  (`b97569d66aa5_add_users_table.py`) includes the import.

- **Reviewed the autogenerated migration rather than trusting it blindly.** WHY: autogenerate
  can miss things. Confirmed it creates `users` with all seven columns, unique indexes on
  `username` and `email`, and `created_at` as `DateTime(timezone=True)` with
  `server_default=sa.text('now()')` -- i.e. it correctly captured the DB-side, timezone-aware
  default from Branch A.

- **Entrypoint runs `alembic upgrade head` after the Postgres wait, before uvicorn.** WHY: the
  schema should be current before the app serves traffic. `set -e` means a failed migration
  aborts startup rather than serving on a half-built schema. It's idempotent -- on a DB already
  at head it's a no-op. The Dockerfile now also COPYs `alembic.ini` and `migrations/` so the
  standalone image can migrate (dev already has them via the bind mount).

- **Did NOT touch CI (kept anti-drift manual for now).** WHY: CI still runs `pytest`
  (create_all). Adding an `alembic upgrade` + `check` step is a shared-ownership change to
  `.github/workflows`; deferring it keeps Branch B container-scoped. Ran `alembic check`
  manually instead -> "No new upgrade operations detected" (no model/migration drift).

Issue encountered -- in-container pytest and the test DB URL: running
`docker compose exec api python -m pytest` failed with `OperationalError` (13 errors). Cause:
`DATABASE_TEST_URL` isn't set inside the container, so `conftest.py` fell back to its local
default `localhost:5436/hive_test` -- but 5436 is the *host* port mapping; inside the container
the DB is at `api-db:5432`. This is NOT a code defect: the runtime image never runs the test
suite (it runs uvicorn), and a production image shouldn't carry test-DB config. Fixed as a
verification-only override -- re-ran with
`-e DATABASE_TEST_URL=postgresql://postgres:postgres@api-db:5432/hive_test` -> 17 passed. No
files changed.

Verification: built the image; reset `hive_dev` (dropped `users` + `alembic_version`) to prove
a from-scratch build; `docker compose up` logs showed `Postgres is ready. -> Running database
migrations... -> Running upgrade -> b97569d66aa5, add users table -> Uvicorn running`. `psql \d
users` showed the table with both unique indexes and `created_at timestamptz default now()`;
`alembic_version` = `b97569d66aa5`. `/ping` and `/docs` returned 200; in-container pytest passed
17 with the test-URL override. Stack torn down with `docker compose down` (Postgres volume
preserved).
