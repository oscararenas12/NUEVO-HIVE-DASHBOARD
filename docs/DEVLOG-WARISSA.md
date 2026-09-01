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

---

## 2026-08-22 | Warissa + Claude

### Phase 3: Auth endpoints -- register, login, status (feature/phase-3-auth)

Added authentication: `POST /auth/register`, `POST /auth/login`, `GET /auth/status` with bcrypt
password hashing and JWT access tokens. Single branch (no A/B split) because **no migration was
needed** -- the Phase 2 `User` model already had `password_hash`, `role`, and `is_active`, so this
phase is pure app code.

Decisions and reasoning:

- **Login takes a JSON body `{email, password}`** (not the OAuth2 form). WHY: it's a clean JSON API
  that matches Oscar's planned `login(email, password)` frontend call and needs no
  `python-multipart`. We still use Bearer JWTs for `/auth/status` via `OAuth2PasswordBearer`, so
  Swagger's Authorize button still works. This is the cross-team contract Oscar's Auth UI builds
  against: register -> 201 `UserRead` (no password); login -> 200 `{access_token, token_type:
  "bearer"}`; status -> 200 `UserRead`; bad creds/unknown email -> 401 "Invalid credentials".

- **Hashing + JWT live in their own `src/api/security.py`**, not in `crud.py`. WHY: single
  responsibility and easy to unit-test; keeps `auth.py` to just endpoints. `security.py` holds the
  passlib `CryptContext`, `create_access_token`/decode, and the `get_current_user` dependency. Minor
  deviation from the plan's literal "add hashing to crud.py", noted here.

- **JWT secret from config with a dev default (`JWT_SECRET_KEY`), env-overridable.** WHY: mirrors
  Phase 1's safe-default approach so tests/CI run with no setup. It MUST be overridden in production
  (Phase 6). Made the dev default >=32 bytes after PyJWT warned that a 20-byte HS256 key is below the
  recommended length.

- **Pinned `bcrypt>=4.0,<4.1`.** WHY: passlib 1.7.4 reads `bcrypt.__about__.__version__`, which
  bcrypt >=4.1 removed -- the pin avoids that break. Installed bcrypt 4.0.1.

- **No secret ever leaves the API.** `response_model=UserRead` on register/status and a `UserCreate`
  input schema guarantee `password_hash` is never returned and can't be set by the client. Register
  catches `IntegrityError` (duplicate username/email) and returns 400 after a rollback.

Implementation notes / issues:
- Circular-import avoidance: `security.py` imports `crud`, so `crud.authenticate_user` imports
  `verify_password` locally inside the function rather than at module top.
- Two remaining test warnings are cosmetic and not worth fixing now: the Starlette/httpx TestClient
  deprecation (seen since Phase 1) and passlib importing the stdlib `crypt` module (deprecated,
  removed in Python 3.13 -- fine on our pinned Python 3.12; revisit if we bump Python).

Verification: `pytest src/tests -v` against `localhost:5436/hive_test` -> 27 passed (10 new auth
tests + the prior 17). Tests confirm register hides the password, duplicate email/username -> 400,
missing fields -> 422, login returns a bearer token, wrong/unknown credentials -> 401, and
`/auth/status` accepts a valid Bearer token while rejecting missing/malformed ones. Alembic
untouched (no schema change).

---

## 2026-08-24 | Warissa + Claude

### Phase 4: User-management endpoints + admin roles (feature/phase-4-user-management)

Added `/users` endpoints: list + read for any authenticated user, update + deactivate for admins.
Like Phase 3, **no migration** -- reuses the existing `role` and `is_active` columns -- so a single
branch of pure app code.

Decisions and reasoning:

- **`admin_required` dependency layered on `get_current_user`.** WHY: `get_current_user` already
  handles the 401 (missing/invalid token) and loads the active user, so `admin_required` just adds
  the role check (403 if not admin). Composing the two gives the correct 401-vs-403 split for free:
  no token -> 401, valid non-admin -> 403.

- **PUT and DELETE are admin-only; GET list/read need any authenticated user.** WHY: matches the
  spec's access model. Consequence/limitation: employees can't edit their own profile in this phase
  -- self-service edits can come later.

- **DELETE is a soft delete** (`is_active = False`), returning 200 + the updated `UserRead` (shows
  `is_active:false`) instead of 204. WHY: soft delete preserves history/foreign keys, and returning
  the record makes the outcome visible and easy to test.

- **Admins can't deactivate themselves** (self -> 400) and **deactivated users can't log in.** WHY:
  spec edge cases -- prevent an admin locking the system out of itself, and make deactivation
  actually revoke access. The login guard went into `crud.authenticate_user` (returns None if not
  active), which `login` already maps to 401. `get_current_user` also already rejected inactive
  users, so an existing token stops working once the account is deactivated.

- **`UserUpdate` uses `role: Literal["admin","employee"]`.** WHY: an invalid role becomes a clean
  422 at validation time rather than silently writing a bad value (the DB column has no constraint).
  Only provided fields are applied (`model_dump(exclude_unset=True)`). Duplicate username/email on
  update is caught as `IntegrityError` -> 400. Password change is out of scope this phase.

Verification: `pytest src/tests -v` against `localhost:5436/hive_test` -> 40 passed (13 new
user-mgmt tests + the prior 27). Tests cover auth-required listing, 404 on unknown ids, admin-only
403s for employees, self-deactivation 400, and that a soft-deleted user can no longer log in.
Admin users in tests are inserted directly via the session fixture (register only creates
employees). Alembic untouched.

---

## 2026-08-25 | Warissa + Claude

### Phase 5: Refresh tokens + logout (feature/phase-5-refresh-logout)

The last backend auth phase. Access tokens live 15 minutes; without a refresh flow the user is
silently logged out that often. Added a 7-day refresh token (httpOnly cookie), `POST /auth/refresh`
(mint a new access token from the cookie), and `POST /auth/logout` (clear it). Branched off a `main`
that already had Phase 4 (PR #10 merged just before), so no coordination merge was needed. No
migration -- tokens are stateless JWTs.

Decisions and reasoning:

- **Token kinds separated by a `type` claim (`"access"` vs `"refresh"`), not a second secret.**
  WHY: the plan warned that an access and refresh token must not be interchangeable. A `type` claim
  validated at decode achieves that with one secret and less config. `get_current_user` now requires
  `type == "access"` and `/auth/refresh` requires `type == "refresh"`, so a refresh token can't be
  used as a Bearer access token and vice versa (both tested).

- **Refresh token delivered as an httpOnly cookie**, scoped to `path=/auth`, `samesite=lax`,
  `max_age`=7 days, and **`secure` only when `environment == "production"`**. WHY: httpOnly keeps the
  long-lived token out of reach of JS (XSS protection) -- the access token stays in the response body
  for the SPA to hold in memory. `secure=False` in dev/test is required so the http TestClient
  actually receives and returns the cookie; production flips it on. Scoping to `/auth` means the
  cookie is only sent to auth routes.

- **No refresh-token rotation** yet: `/auth/refresh` returns a new access token and leaves the
  refresh cookie in place. WHY: matches the spec and keeps it simple; rotation + reuse-detection is a
  future hardening.

- **`logout` returns 200 `{"message": "logged out"}`** and deletes the cookie (must pass the same
  `path=/auth` to clear it). Login's response body is unchanged, so all Phase 3 auth tests still hold.

Known follow-up (frontend integration, with Oscar): a cross-origin SPA calling `/auth/refresh` will
likely need `samesite=none` + `secure=true` + CORS `allow_credentials`. Deferred to the integration
phase -- noted so it isn't a surprise.

Verification: `pytest src/tests -v` against `localhost:5436/hive_test` -> 47 passed (7 new + the
prior 40). New tests cover: login sets an httpOnly refresh cookie; refresh returns a new access
token; missing/expired/wrong-type refresh -> 401; logout clears the cookie and blocks a subsequent
refresh; a refresh token rejected as a Bearer access token. Expired-token test mints a JWT with a
past `exp` and sets it via the test client's cookie jar. Alembic untouched.

---

## 2026-09-01 | Warissa + Claude

### Security remediation PR-A: auth & input hardening (feature/sec-auth-hardening)

First of three grouped PRs remediating the pre-Phase-6 audit (see
`docs/plans/2026-08-28-pre-phase-6-context.md`). PR-A covers SEC-001/002/003/005/006. No migration.

Decisions and reasoning:

- **SEC-001 — reject the default JWT secret in production.** WHY: the dev default is committed and
  public; if a prod deploy forgot `JWT_SECRET_KEY`, anyone could forge admin tokens. Added a
  pydantic `model_validator(mode="after")` on `Settings`: if `environment == "production"` and the
  secret equals the `DEV_JWT_SECRET` constant, it raises → the app fails fast at startup
  (`get_settings()` runs at import). Dev/test (default `environment=dev`) are unaffected.

- **SEC-002/003 — input validation.** WHY: previously any password (even empty) and any string as
  email were accepted. `UserCreate.password` now uses `Field(min_length=12)` and `email` uses
  `EmailStr` (added the `email-validator` dep); `UserUpdate.email` too. Bad input → 422 automatically.
  The `User` table column stays `str` (only the input schemas validate). Existing test fixtures were
  bumped to >=12-char passwords.

- **SEC-005 — reduce account enumeration.** WHY: login was faster for a non-existent email (it
  returned before running bcrypt), a timing side-channel. `authenticate_user` now always runs a
  bcrypt verify -- against a cached dummy hash when the user is missing/inactive -- so timing is
  even. Register's duplicate error is now generic ("Could not complete registration") so it doesn't
  say which field collided. KNOWN residual: register still returns 400 vs 201, so the status code
  alone can confirm an account exists; fully closing that needs a "return 201 + notify by email"
  flow (a feature, deferred). The login timing channel -- the more attackable one -- is closed.

- **SEC-006 — /users is now fully admin-only.** WHY: RULES.md gives employees "scoped access", but
  `GET /users` and `GET /users/{id}` only required being logged in, exposing the whole roster (and
  who's admin) to any employee. Both now depend on `admin_required` (PUT/DELETE already did).
  Employees get their own data from `GET /auth/status`. Chose full admin-only over self-or-admin for
  simplicity; tests updated so employees get 403 and admins 200/404.

Verification: `pytest src/tests -v` against `localhost:5436/hive_test` -> 54 passed (5 new/changed
behaviors + the prior 49). Confirmed: prod+default-secret raises; <12-char password and invalid
email -> 422; employee -> 403 on /users list/get, admin -> 200/404. Rate limiting, CORS/headers, and
DB-cred env-ization are PR-B and PR-C.
