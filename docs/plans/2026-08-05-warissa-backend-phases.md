# Warissa's Backend Task Board

**Goal:** Build the FastAPI backend service with auth, user management, and API endpoints — following TDD and the FastAPI tutorial patterns.

**Reference:**
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) -- your primary guide
- [docs/STACK.md](../STACK.md) -- tech stack decisions
- [docs/RULES.md](../RULES.md) -- dev practices (TDD, PR workflow, devlog)
- [docs/STRUCTURE.md](../STRUCTURE.md) -- file structure and ownership

**Your territory:** `services/api/`

**Important:** This is a phase-based plan, not a rigid checklist. Errors and edge cases WILL come up. When they do, debug, fix, and document the decision in your devlog (docs/DEVLOG-WARISSA.md). Each phase should result in working, testable code before moving to the next.

---

## How to work

1. Create a feature branch: `git checkout -b feature/<phase-name>`
2. Write tests first (TDD) -- every endpoint, every model
3. Run tests often: `python -m pytest src/tests -v`
4. Commit small and frequently
5. When phase is complete, push branch and create a PR
6. Update your devlog with decisions and reasoning
7. Wait for PR review before starting next phase

---

## Phase 1: Project Scaffold + Health Check

**What you're building:** A working FastAPI app in Docker that responds to a health check. This proves the entire stack works end-to-end (Python, FastAPI, Docker, Postgres, tests, CI).

**Files to create:**

```
services/api/
|-- Dockerfile
|-- requirements.txt
|-- entrypoint.sh
+-- src/
    |-- __init__.py
    |-- main.py              # FastAPI app
    |-- config.py            # Settings (DB URL, env vars)
    |-- api/
    |   |-- __init__.py
    |   +-- ping.py          # Health check endpoint
    +-- tests/
        |-- __init__.py
        |-- conftest.py      # Test fixtures (test client, test DB)
        |-- test_config.py   # Config tests
        +-- test_ping.py     # Health check tests
```

**Key steps:**

- [ ] Set up `requirements.txt` with: fastapi, uvicorn, sqlmodel, alembic, psycopg2-binary, pytest, httpx
- [ ] Create `config.py` using Pydantic Settings (see: https://fastapi.tiangolo.com/advanced/settings/)
  - DATABASE_URL from environment variable
  - TESTING flag
- [ ] Create `main.py` with FastAPI app instance
- [ ] Create `ping.py` with `GET /ping` endpoint that returns `{"status": "ok", "environment": "dev"}`
- [ ] Write `test_ping.py` FIRST (TDD):
  - Test that GET /ping returns 200
  - Test that response contains "ok" status
- [ ] Write `test_config.py`:
  - Test that config loads from environment
  - Test that TESTING flag works
- [ ] Create `conftest.py` with test client fixture using FastAPI's TestClient
- [ ] Create `Dockerfile` (Python 3.12 slim, install requirements, run uvicorn)
- [ ] Create `entrypoint.sh` (wait for DB, run migrations, start server)
- [ ] Verify: `docker-compose up api` starts and `/ping` responds

**You'll know this phase is done when:**
- `python -m pytest src/tests -v` passes locally
- `docker-compose up api` starts without errors
- `curl http://localhost:5001/ping` returns `{"status": "ok"}`
- Swagger docs visible at `http://localhost:5001/docs`

**Edge cases to watch for:**
- Docker networking: the API container needs to wait for Postgres to be ready before starting. `entrypoint.sh` handles this with a loop that checks `pg_isready`.
- Import paths: inside Docker the working directory matters. Make sure `src/` is on the Python path.

---

## Phase 2: Database + User Model

**What you're building:** SQLModel User table with Alembic migrations, running inside Docker.

**Files to create:**

```
services/api/
+-- src/
    |-- db.py                # Engine, session, create_db_and_tables
    |-- api/
    |   +-- users/
    |       |-- __init__.py
    |       |-- models.py    # User SQLModel
    |       +-- crud.py      # Create/read/update/delete functions
    +-- tests/
        |-- test_user_model.py
        +-- conftest.py      # Update: add DB session fixture
```

**Key steps:**

- [ ] Create `db.py` with SQLModel engine and session (see: https://fastapi.tiangolo.com/tutorial/sql-databases/)
  - `create_engine` with DATABASE_URL from config
  - `get_session` dependency that yields a Session
- [ ] Create `models.py` with User SQLModel:
  - id (int, primary key)
  - username (str, unique, indexed)
  - email (str, unique, indexed)
  - password_hash (str)
  - role (str: "admin" or "employee", default "employee")
  - is_active (bool, default True)
  - created_at (datetime)
- [ ] Write `test_user_model.py` FIRST:
  - Test creating a user
  - Test email uniqueness constraint
  - Test username uniqueness constraint
  - Test default role is "employee"
  - Test default is_active is True
- [ ] Create `crud.py` with functions:
  - `create_user(session, user_data)` -- returns User
  - `get_user_by_id(session, user_id)` -- returns User or None
  - `get_user_by_email(session, email)` -- returns User or None
  - `get_all_users(session)` -- returns list of Users
- [ ] Update `conftest.py`:
  - Add a test database session fixture (use SQLite in-memory for tests)
  - Override the `get_session` dependency in tests
- [ ] Set up Alembic:
  - `alembic init migrations`
  - Configure `env.py` to use SQLModel metadata
  - Generate first migration: `alembic revision --autogenerate -m "add users table"`
  - Run migration: `alembic upgrade head`

**You'll know this phase is done when:**
- All user model tests pass
- Migration runs without errors
- You can see the `user` table in Postgres (via psql or pgAdmin)

**Edge cases to watch for:**
- SQLite vs Postgres differences in testing: SQLite doesn't enforce some constraints the same way. If a test works in SQLite but fails in Postgres, you may need a Postgres test database for certain tests.
- Alembic autogenerate may not detect everything. Always review the generated migration file before running it.

---

## Phase 3: Auth Endpoints (Register + Login)

**What you're building:** Registration and login endpoints with password hashing and JWT tokens.

**Files to create/modify:**

```
services/api/
+-- src/
    |-- api/
    |   |-- auth.py          # Register + login endpoints
    |   +-- users/
    |       +-- crud.py      # Update: add password hashing
    +-- tests/
        +-- test_auth.py     # Auth endpoint tests
```

**Key steps:**

- [ ] Add to `requirements.txt`: passlib[bcrypt], pyjwt
- [ ] Write `test_auth.py` FIRST:
  - Test POST /auth/register with valid data returns 201 + user data (no password in response)
  - Test POST /auth/register with duplicate email returns 400
  - Test POST /auth/register with missing fields returns 422
  - Test POST /auth/login with valid credentials returns 200 + access token
  - Test POST /auth/login with wrong password returns 401
  - Test POST /auth/login with non-existent email returns 401
  - Test GET /auth/status with valid token returns user data
  - Test GET /auth/status without token returns 401
- [ ] Create `auth.py` endpoints:
  - `POST /auth/register` -- hash password, create user, return user (without password)
  - `POST /auth/login` -- verify password, generate JWT, return token
  - `GET /auth/status` -- decode JWT, return current user
- [ ] JWT implementation:
  - Access token: 15 min expiry, contains user_id and role
  - Use PyJWT to encode/decode
  - Secret key from config (environment variable)
- [ ] Password hashing:
  - Use passlib with bcrypt
  - Hash on register, verify on login
  - NEVER store or return plain passwords
- [ ] Register the auth router in `main.py`

**You'll know this phase is done when:**
- All auth tests pass
- You can register a user via Swagger (`/docs`)
- You can login and get a JWT token
- You can hit `/auth/status` with the token and get user info back

**Edge cases to watch for:**
- JWT secret must come from environment, not hardcoded. Use config.py.
- passlib bcrypt can be slow in tests. That's normal -- don't remove hashing in tests.
- Token expiry: make sure your tests don't depend on time-sensitive tokens. Set a long expiry in test config if needed.
- Error messages: don't reveal whether it was the email or password that was wrong on login. Just return "Invalid credentials."

---

## Phase 4: User Management Endpoints

**What you're building:** CRUD endpoints for managing users (admin-only for some operations).

**Files to create/modify:**

```
services/api/
+-- src/
    |-- api/
    |   +-- users/
    |       |-- views.py     # User endpoints
    |       +-- crud.py      # Update: add update/delete
    +-- tests/
        +-- test_users.py    # User endpoint tests
```

**Key steps:**

- [ ] Write `test_users.py` FIRST:
  - Test GET /users returns list of users (requires auth)
  - Test GET /users/:id returns single user (requires auth)
  - Test GET /users/:id with invalid id returns 404
  - Test PUT /users/:id updates user (admin only)
  - Test DELETE /users/:id deactivates user (admin only)
  - Test non-admin cannot access admin-only endpoints (returns 403)
  - Test unauthenticated requests return 401
- [ ] Create `views.py` endpoints:
  - `GET /users` -- list all users (auth required)
  - `GET /users/{user_id}` -- get single user (auth required)
  - `PUT /users/{user_id}` -- update user (admin only)
  - `DELETE /users/{user_id}` -- deactivate user (admin only)
- [ ] Add role-checking dependency:
  - Create a `get_current_user` dependency that decodes JWT and returns user
  - Create an `admin_required` dependency that checks role == "admin"
- [ ] Update `crud.py`:
  - `update_user(session, user_id, update_data)` -- returns updated User
  - `delete_user(session, user_id)` -- sets is_active to False (soft delete)
- [ ] Register users router in `main.py`

**You'll know this phase is done when:**
- All user tests pass
- Admin can manage users via Swagger
- Non-admin gets 403 on admin endpoints
- Soft delete works (user.is_active = False, not actually removed from DB)

**Edge cases to watch for:**
- Admin should not be able to delete themselves
- PUT should not allow changing role unless you're admin
- Make sure soft-deleted users can't log in (check is_active on login)

---

## Phase 5: Refresh Tokens + Logout

**What you're building:** Refresh token flow for silent re-authentication and logout.

**Files to modify:**

```
services/api/
+-- src/
    |-- api/
    |   +-- auth.py          # Add refresh + logout endpoints
    +-- tests/
        +-- test_auth.py     # Add refresh + logout tests
```

**Key steps:**

- [ ] Add refresh token tests FIRST to `test_auth.py`:
  - Test POST /auth/refresh with valid refresh token returns new access token
  - Test POST /auth/refresh with expired refresh token returns 401
  - Test POST /auth/logout clears refresh token
- [ ] Update `POST /auth/login` to return both access token and refresh token
  - Access token: 15 min expiry (in response body)
  - Refresh token: 7 day expiry (as httpOnly cookie)
- [ ] Create `POST /auth/refresh`:
  - Read refresh token from httpOnly cookie
  - Verify and decode it
  - Return new access token
- [ ] Create `POST /auth/logout`:
  - Clear the refresh token cookie

**You'll know this phase is done when:**
- Login returns access token in body + sets refresh cookie
- Refresh endpoint returns new access token
- Logout clears the cookie
- All auth tests still pass

**Edge cases to watch for:**
- httpOnly cookies won't be accessible from JavaScript (that's the point -- security)
- In tests, you need to handle cookies explicitly with the test client
- Refresh token should have a different JWT secret or prefix to prevent confusion with access tokens

---

## After all phases

Once Phase 5 is complete, the backend has:
- Working FastAPI app in Docker
- Postgres with User table and migrations
- Full auth flow (register, login, refresh, logout, status)
- User management (CRUD, admin roles)
- Tests for everything
- CI passing

Next steps (Phase 6+, planned later):
- Refund system endpoints
- Dashboard data endpoints (connect to scraper data)
- Integration with frontend (Oscar's work)
