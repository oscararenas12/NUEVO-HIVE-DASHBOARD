# Oscar's Development Log

Format: Date | Who (human/agent) | Decision + Reasoning

---

## 2026-07-28 | Oscar + Claude

### Project foundation and cleanup

Cleaned the repo and established the project structure. Key decisions:

- Switched from Flask to FastAPI: intern studied the FastAPI tutorial extensively, and the project already had FastAPI partially set up. Less migration work.
- Switched from SQLAlchemy to SQLModel: follows the FastAPI tutorial the intern studied. Same ORM underneath, cleaner syntax.
- Chose Shadcn/ui over Chakra UI: more modern, we own the component code, built on Tailwind CSS.
- Kept scraper/ as-is but paused: loader.py has broken imports (references removed app/ modules). Will fix when backend is rebuilt.
- Split repo into services/client (Oscar) and services/api (Warissa) for clear ownership.
- Created docs/ as shared knowledge base with devlogs, rules, and plans.
- All plans must be saved to docs/plans/ before implementation begins.
- Warissa (intern) uses default Claude -- no superpowers skills. Oscar uses Claude with superpowers plugin. Both agents should read docs/ for shared context.
- RULES.md is a draft -- Oscar will refine and add more rules before development begins. Check for updates after every pull.

---

## 2026-08-21 | Oscar + Claude

### Review of Warissa's backend work (Phases 1-2)

Pulled and reviewed all of Warissa's merged changes before starting frontend work. She completed
Phase 1 (A+B) and Phase 2 (A+B) across four branches:

- Phase 1A: FastAPI scaffold, pydantic-settings config, /ping endpoint, 7 tests
- Phase 1B: Dockerfile (python:3.12-slim), entrypoint.sh with pg_isready wait loop
- Phase 2A: User SQLModel, CRUD functions, 10 new tests against real Postgres (SAVEPOINT isolation)
- Phase 2B: Alembic migrations, auto-upgrade in entrypoint, reviewed migration file

Quality assessment: solid TDD discipline, thorough devlog entries, good architectural decisions
(real Postgres in tests, "users" table name to dodge reserved word, server_default for created_at).
No issues found. Backend ready for Phase 3 (auth).

### Phase 1: Frontend scaffold (React + Vite + TypeScript)

Decisions and reasoning:

- **Vite 8 + React 19 + TypeScript 6.** WHY: `npm create vite@latest` pulled the current stable
  versions. React 19 is production-ready; TypeScript 6 is the latest with erasable syntax support.

- **Tailwind CSS v4 (not v3).** WHY: v4 is the current major and uses CSS-native `@theme` blocks
  instead of a JS config file. Cleaner setup with `@tailwindcss/vite` plugin. Shadcn/ui supports v4.

- **Shadcn/ui style: base-nova (not New York).** WHY: `npx shadcn init` defaulted to base-nova,
  which uses @base-ui/react primitives. This is their latest recommended style. Components use
  headless primitives with Tailwind styling.

- **Dark theme tokens in `@theme` block.** WHY: the dashboard is dark-first (bg-primary #12121c,
  surface #1c1c29, accent #ffa600). Defined as CSS custom properties in Tailwind v4's `@theme`
  so they're available as utility classes (`bg-bg-primary`, `text-accent`).

- **`import.meta.dirname` instead of `__dirname`.** WHY: Vite 8 warns that `__dirname` is
  unsupported in native config loading. `import.meta.dirname` is the ESM equivalent.

- **Shadcn path aliases: `src/` in components.json, `@/` in tsconfig.** WHY: shadcn v4 resolves
  file paths literally from the aliases, so `@/components` creates a literal `@/` directory.
  Using `src/components` places files correctly. The `@` alias in tsconfig/vite resolves imports
  at build time. Generated components need a one-line import fix (`src/` → `@/`).

- **Vitest with jsdom, globals enabled.** WHY: jsdom simulates the DOM for React component tests.
  Globals (`describe`, `it`, `expect`) avoid importing from vitest in every test file.

- **Docker dev server config: host 0.0.0.0, usePolling.** WHY: Docker containers need 0.0.0.0
  to expose the server outside the container. usePolling is required for file watching through
  Docker bind mounts on Windows.

Verification: `npx vitest run` passes 2 tests (App renders, heading visible). Vite dev server
starts and serves at localhost:3007. Docker Desktop not running during this session — Dockerfile
verified structurally but not built yet. Will test with `docker compose up client` next session.
