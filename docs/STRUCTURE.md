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
