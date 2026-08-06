# Project Structure

```
NUEVO-HIVE-DASHBOARD/
|-- .gitignore
|-- .github/
|   +-- workflows/
|       +-- main.yml
|-- docker-compose.yml
|-- README.md
|-- docs/
|   |-- STACK.md              # Tech stack decisions
|   |-- RULES.md              # Dev practices and workflow
|   |-- STRUCTURE.md          # This file
|   |-- DEVLOG-OSCAR.md       # Oscar's decision log
|   |-- DEVLOG-WARRSIA.md     # Warrsia's decision log
|   +-- plans/                # Implementation plans
|-- scraper/                  # Data pipeline (paused)
|   |-- seedlive.py           # Pulls reports from SeedLive
|   |-- loader.py             # CSV parsing/loading (broken imports, will fix later)
|   |-- explore_filters.py    # Maps SeedLive form fields
|   |-- downloads/            # Downloaded CSVs (gitignored)
|   +-- screenshots/          # Reference screenshots (gitignored)
+-- services/
    |-- client/               # React frontend (Oscar)
    |   |-- Dockerfile
    |   |-- package.json
    |   |-- vite.config.ts
    |   |-- vitest.config.ts
    |   +-- src/
    |       |-- App.tsx
    |       |-- main.tsx
    |       |-- components/
    |       |-- pages/
    |       |-- api/
    |       |-- auth/
    |       +-- tests/
    |-- nginx/                # Reverse proxy
    |   +-- default.conf
    +-- api/                  # FastAPI backend (Warrsia)
        |-- Dockerfile
        |-- requirements.txt
        |-- entrypoint.sh
        +-- src/
            |-- __init__.py
            |-- main.py
            |-- config.py
            |-- api/
            |   |-- __init__.py
            |   |-- auth.py
            |   |-- ping.py
            |   +-- users/
            |       |-- __init__.py
            |       |-- crud.py
            |       |-- models.py
            |       +-- views.py
            |-- db/
            |   |-- Dockerfile
            |   +-- create.sql
            +-- tests/
                |-- __init__.py
                |-- conftest.py
                |-- test_auth.py
                |-- test_config.py
                |-- test_ping.py
                +-- test_users.py
```

## Ownership

| Area | Owner | Description |
|------|-------|-------------|
| services/client/ | Oscar | React frontend, UI, routing |
| services/api/ | Warrsia | FastAPI backend, models, auth, API |
| services/nginx/ | Together | Reverse proxy config |
| scraper/ | Oscar | Data pipeline (paused) |
| docs/ | Both | Shared knowledge base |
| docker-compose.yml | Together | Container orchestration |
| .github/workflows/ | Together | CI/CD pipeline |

## Task Division

### Oscar (Owner)
- services/client/ -- React frontend, UI components, pages, routing
- scraper/ -- SeedLive data pipeline (paused, will resume later)
- Frontend testing (Vitest + React Testing Library)

### Warrsia (Intern)
- services/api/ -- FastAPI backend, SQLModel models, auth, API endpoints
- services/api/src/db/ -- Database setup, migrations
- Backend testing (pytest + FastAPI TestClient)
- Reference: https://fastapi.tiangolo.com/tutorial/

### Together
- services/nginx/ -- Reverse proxy config
- docker-compose.yml -- Container orchestration
- .github/workflows/ -- CI/CD pipeline
- Hosting setup and deployment
- docs/ -- Shared knowledge base

## Build Phases

| Phase | What | Who | Depends On |
|-------|------|-----|------------|
| 1. Foundation | Clean repo, project structure, docs, CI/CD | Together | -- |
| 2. Backend | FastAPI app, SQLModel, auth (signup/login/JWT), user roles, ping | Warrsia | Phase 1 |
| 3. Frontend | Vite + React setup, Shadcn/ui, login page, dashboard layout, routing | Oscar | Phase 1 |
| 4. Integration | Connect frontend to backend, auth flow end-to-end | Together | Phase 2 + 3 |
| 5. Features | Refunds, dashboard views, data pipeline integration | Split | Phase 4 |
| 6. Deploy | Docker production build, hosting, CI/CD finalize | Together | Phase 5 |

Phase 2 and 3 run in parallel -- that's the point of the split.
