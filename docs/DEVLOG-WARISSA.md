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
