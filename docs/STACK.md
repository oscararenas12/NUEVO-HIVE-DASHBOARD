# Tech Stack

| Layer | Tool |
|-------|------|
| Frontend | React (TypeScript) + Vite |
| Frontend Styling | Shadcn/ui + Tailwind CSS |
| Frontend Testing | Vitest + React Testing Library |
| Backend | FastAPI + Python 3.12 |
| Backend Testing | pytest + FastAPI TestClient |
| Auth | passlib (bcrypt) + PyJWT + FastAPI Security (OAuth2) |
| Database | PostgreSQL 16 |
| ORM / Migrations | SQLModel + Alembic |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Hosting | TBD |
| Data Pipeline | Existing Playwright scraper (paused) |

## Key Decisions

- FastAPI over Flask: intern studied FastAPI tutorial, project already had FastAPI partially set up - https://fastapi.tiangolo.com/tutorial
- SQLModel over SQLAlchemy: intern focused on FastAPI tutorial which uses SQLModel
- Shadcn/ui over Chakra UI: more modern, you own the component code, built on Tailwind
- Vite: build tool for React, replaces Create React App, instant hot reload
- Vitest: frontend test runner, pairs with Vite, Jest-compatible API