# Pre-Phase-6 Engineering Context

**Purpose:** A single reference capturing where the codebase stands before Phase 6, the
**intentional** design decisions and known tradeoffs, so future engineers (and reviewers) don't
mistake deliberate choices for defects. This is documentation only — no code changed to produce it.

**Snapshot:** backend Phases 1–5 complete (Phase 5 on `feature/phase-5-refresh-logout`, pending
merge; Phases 1–4 merged to `main`). Frontend (Oscar) Phases 1–2 complete and merged. Full auth +
user-management backend; frontend is layout/routing skeleton only.

---

## Backend (`services/api`) — completed

| Phase | What | Status |
|------|------|--------|
| 1 | FastAPI scaffold, pydantic-settings config, `/ping`, Dockerfile, `entrypoint.sh` (pg_isready wait) | merged |
| 2 | `User` SQLModel (`users` table), CRUD, Alembic migration, auto-`upgrade` on start | merged |
| 3 | Auth: `POST /auth/register`, `POST /auth/login`, `GET /auth/status` (bcrypt + JWT) | merged |
| 4 | User management: `GET/PUT/DELETE /users`, `admin_required`, soft delete | merged |
| 5 | Refresh tokens + logout: `POST /auth/refresh`, `POST /auth/logout`, httpOnly cookie | pending PR |

**Test suite:** 47 pytest tests against a real Postgres test DB (`hive_test`) with per-test
SAVEPOINT rollback isolation. TDD throughout (failing test first).

### Auth/authorization model (as designed)
- **Access token:** JWT (HS256), 15-min expiry, claims `sub` (user id), `role`, `type:"access"`.
  Returned in the login response body; the SPA is expected to hold it in memory (not localStorage).
- **Refresh token:** JWT, 7-day expiry, `type:"refresh"`, delivered as an **httpOnly** cookie
  scoped to `path=/auth`, `samesite=lax`. `POST /auth/refresh` reads the cookie and issues a new
  access token. Logout clears the cookie.
- **Token separation:** access vs refresh tokens are non-interchangeable — `get_current_user`
  requires `type=="access"`, `/auth/refresh` requires `type=="refresh"`.
- **Authorization is server-side:** `get_current_user` (active user) and `admin_required` (role
  check → 403) dependencies gate every protected route. No UI-only gating.

## Frontend (`services/client`) — completed
- React 19 + Vite + TS + Tailwind v4 + base-ui (shadcn base-nova). Dark-first theme
  (`bg-primary #12121c`, surface `#1c1c29`, accent `#ffa600`).
- Sidebar layout (260px, mobile hamburger + backdrop), React Router v7 nested routes, NavBar with
  active state, brand logo. 13 Vitest tests.

---

## INTENTIONAL behaviors — do NOT flag as bugs

These are deliberate and documented; a reviewer should treat them as context (still fine to note
production-hardening items, but they are not defects):

1. **Dashboard pages are placeholders.** `Overview.tsx`, `SlotPerformance.tsx`, `Trends.tsx`,
   `Login.tsx` intentionally render only a heading. Real content/charts arrive in the frontend's
   Phase 4; the real Login/auth UI is the frontend's Phase 3 (not built yet).
2. **No frontend↔backend wiring yet.** There is no API client, AuthContext, or protected-route
   logic in the client. That's the integration phase, deliberately not started.
3. **`register` only creates employees.** Role isn't accepted at registration; the first admin is
   bootstrapped by promoting a row in the DB (`UPDATE users SET role='admin' ...`). A dedicated
   admin-provisioning path is future work.
4. **No refresh-token rotation / server-side revocation.** Tokens are stateless JWTs; `logout`
   clears the cookie but an already-issued access token stays valid until its 15-min expiry. This
   is a known, accepted tradeoff for now (rotation + denylist are future hardening).
5. **`PUT /users/{id}` is admin-only.** Employees cannot self-edit their profile this phase.
6. **Soft delete** — `DELETE /users/{id}` sets `is_active=False` (row is kept, not removed);
   deactivated users are rejected at login and by `get_current_user`.
7. **Cookie `secure` is enabled only when `environment == "production"`.** Off in dev/test so the
   http TestClient/local stack receive the cookie. Production must run with `ENVIRONMENT=production`.

## KNOWN gaps / deferred to later phases (not yet implemented — by design)
- **CORS is not configured** on the API. Deferred to frontend integration (the SPA and API run on
  different origins: client `:3007`/nginx, api `:5001`). Cross-origin refresh will also need
  `samesite=none` + `secure=true` at that point.
- **No rate limiting / brute-force protection** on `/auth/login`.
- **JWT secret uses a dev default** (`config.py` `jwt_secret_key`) — clearly labeled
  "change-me-in-production", read from `JWT_SECRET_KEY`. Must be overridden in deployment.
- **DB credentials** are the compose dev defaults (`postgres/postgres`) — dev only; production
  must inject real secrets via env.
- **nginx** reverse proxy is a `.gitkeep` placeholder (routing not wired).
- **Scraper** (`scraper/`) is paused; `loader.py` has known broken imports (old `app.*` modules) —
  to be fixed when the pipeline resumes (Phase 6+).

## Next (Phase 6+, planned, not started)
Refund system endpoints, dashboard data endpoints (connect scraper → Postgres → API), and full
frontend↔backend integration (CORS, auth flow, real dashboard data).

---

## Pre-Phase-6 Audit (2026-08-28)

An independent, audit-only quality review was run before Phase 6 using **two fresh-context review
subagents** (each isolated, no shared findings, strictly read-only — no edits/installs/commits).
Both performed **static review only**: their environment had no `node_modules`, Python deps, or
Postgres test DB, so pytest/Vitest/tsc/oxlint were not executed (confirm via CI).

- **Subagent 1 — Security review** (Senior Application Security Engineer). Traced auth/authorization,
  token/cookie handling, DB access, and config end-to-end.
  Outcome: **0 Critical, 1 High, 1 Medium, 9 Low → FIX BEFORE PRODUCTION.**
- **Subagent 2 — Bug / quality review** (Senior SWE / QA). Traced implemented backend flows and the
  frontend skeleton.
  Outcome: **0 Blocker/High/Medium, 2 Low → SAFE FOR NEXT PHASE WITH MINOR FIXES.**

**Consolidated recommendation: PROCEED WITH P1 ITEMS TRACKED** — no P0/blocker; nothing gates Phase 6
development. The High + Mediums are **production-deployment prerequisites**, not dev blockers.

Findings (full detail lives in the audit report; IDs preserved here for tracking):
- **SEC-001 (High):** hardcoded dev `JWT_SECRET_KEY` default → forgeable tokens if deployed unset.
  Fix: fail-fast startup guard in production.
- **SEC-004 (Medium):** no rate limiting / brute-force protection on `/auth/login`.
- **SEC-002/003/005 (Low):** no password policy; `email` is plain `str` (not `EmailStr`); user
  enumeration via register errors + login timing.
- **SEC-006 (Low):** any authenticated employee can list all users (intended today — confirm vs
  RULES.md "scoped access").
- **SEC-007 (Low):** cookie `secure` + `/docs` gated on `environment` (defaults to `dev`).
- **SEC-008 (Low):** CSRF hardening needed once CORS + `samesite=none` land.
- **SEC-009 (Low):** no CORS middleware / security headers (deferred to integration).
- **SEC-010 (Low):** committed **dev** DB creds in compose (`postgres/postgres`) — ensure not reused.
- **SEC-011 (Low):** scraper `loader.py` unguarded numeric parsing + broken imports (paused module).
- **BUG-001 (Low):** mobile sidebar toggle buttons lack an accessible name (`Layout.tsx`).
- **BUG-002 (Low):** `ui/button.tsx` references shadcn theme tokens not defined in `@theme`
  (latent — component currently unused).

Both reviewers independently confirmed the core is sound: **server-side** authorization
(`admin_required` re-reads role from DB), JWT access/refresh **type separation**, bcrypt hashing,
`UserRead` never leaking `password_hash`, ORM-only queries (no SQL injection), and **no secrets
committed** to source. Remediation of the above is tracked separately and is **not** addressed on
this docs branch.
