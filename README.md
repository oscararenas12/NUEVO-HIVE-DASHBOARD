# NUEVO-HIVE-DASHBOARD

Vending machine CRM and sales dashboard. Tracks daily sales, slot performance, inventory, and customer refunds for drink and snack vending machines.

## Quick Start

```bash
docker-compose up -d --build
```

- Frontend: http://localhost:3007
- API: http://localhost:5001
- API Docs (Swagger): http://localhost:5001/docs

## Project Structure

See [docs/STRUCTURE.md](docs/STRUCTURE.md) for full layout.

| Service | Description | Owner |
|---------|-------------|-------|
| services/client | React (TypeScript) frontend | Oscar |
| services/api | FastAPI backend | Warrsia |
| services/nginx | Reverse proxy | Shared |
| scraper/ | SeedLive data pipeline (paused) | Oscar |

## Documentation

- [STACK.md](docs/STACK.md) - Tech stack and key decisions
- [RULES.md](docs/RULES.md) - Development practices and workflow
- [STRUCTURE.md](docs/STRUCTURE.md) - File structure and ownership
- [plans/](docs/plans/) - Implementation plans
