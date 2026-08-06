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
