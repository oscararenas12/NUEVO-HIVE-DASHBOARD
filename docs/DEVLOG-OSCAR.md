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

---

## 2026-08-21 | Oscar + Claude

### Phase 2: Layout + Routing

Added sidebar layout, page routing, and NuevoHive branding. TDD — all 13 tests written before
any component code.

Decisions and reasoning:

- **React Router v7 with nested routes.** WHY: Layout wraps dashboard pages via `<Outlet />`,
  Login sits outside the layout (no sidebar on login). Nested routes keep the sidebar persistent
  across page navigation without re-rendering it.

- **MemoryRouter in tests, BrowserRouter in app.** WHY: MemoryRouter doesn't touch the URL bar,
  so tests stay isolated. BrowserRouter in main.tsx for real navigation. Test utils wrapper
  auto-wraps every component test with MemoryRouter + configurable initialEntries.

- **Sidebar: fixed 260px, collapses on mobile.** WHY: 260px fits 3 nav links comfortably without
  wasting space. On screens < lg (1024px), sidebar slides in/out with a hamburger toggle and a
  backdrop overlay. Uses translate-x transition for smooth animation.

- **NavLink with active state via className callback.** WHY: React Router's `NavLink` gives an
  `isActive` boolean in its className function. Active link gets `bg-bg-surface text-white`,
  inactive gets `text-gray-400` with hover state. `end` prop on the "/" route prevents it from
  matching all paths.

- **Lucide icons in nav.** WHY: already installed with Shadcn/ui (lucide-react). LayoutDashboard
  for Overview, Grid3X3 for Slot Performance, TrendingUp for Trends. Consistent 16px size.

- **Logo extraction with Pillow flood fill.** WHY: the original FullLogo.jpg had a white
  background. Simple threshold-based removal also deleted the white band inside the hexagon.
  Used BFS flood fill from image edges to only remove background white, preserving the logo's
  internal white. Extracted the hexagon icon by finding the pixel-count gap between the hexagon
  and the "NUEVOHIVE" text.

- **Placeholder pages (Overview, SlotPerformance, Trends, Login).** WHY: Phase 2 is the skeleton.
  Each page just renders its heading — real content comes in Phase 4 (dashboard components with
  mock data). Login placeholder will be replaced in Phase 3 (auth UI).

Verification: `npx vitest run` passes 13 tests across 7 files. Dev server at localhost:3000
shows sidebar with logo + nav links, clicking links switches pages, mobile hamburger works.
`docker compose up client` verified in Phase 1.

---

## 2026-08-22 | Oscar + Claude

### Phase 2 polish: Apple-design refinements

Applied apple-design skill to the Phase 2 skeleton. Cosmetic-only — no behavior changes.

- **Translucent sidebar material** (`bg-sidebar` at 0.85 opacity + `backdrop-blur-xl`). WHY: gives
  the sidebar depth without being opaque. Added `--color-sidebar: rgba(18,18,28,0.85)` to `@theme`.
  Border thinned to `border-white/[0.06]`.

- **Press feedback on interactive elements** (`active:scale-[0.97]` on nav links, `active:scale-90`
  on mobile toggle buttons). WHY: apple-design §7 — tactile press feedback makes touch/click feel
  responsive.

- **Spring-like sidebar transition** (`ease-[cubic-bezier(0.25,1,0.5,1)] duration-300`). WHY: more
  natural than linear — fast open, gentle settle.

- **Mobile overlay fades** instead of popping (always in DOM, opacity transition + pointer-events
  toggle). WHY: smoother than conditional render.

- **Typography tightening**: tighter letter-spacing on h1/h2, `font-optical-sizing: auto`,
  antialiased rendering, `font-semibold` over `font-bold`. NavBar `onNavigate` prop auto-closes
  sidebar on mobile link tap.

- **Reduced-motion media query** (§14): collapses all transitions/animations to 0.01ms.

- **Page subtitles** added to Overview, SlotPerformance, Trends for context.

Verification: `npx vitest run` passes 13 tests across 7 files. Visual check confirmed.

---

## 2026-09-08 | Oscar + Claude

### Phase 3: Auth UI — login, register, protected routes

Built the full auth UI layer with TDD. 23 new tests (36 total). Warissa's backend has register,
login, status, refresh, and logout endpoints ready — no mocks needed for the API shapes.

Decisions and reasoning:

- **API client (`api/auth.ts`) uses fetch, not axios.** WHY: fetch is built-in, no extra dep.
  `credentials: 'include'` on every call so httpOnly cookies (refresh token) are sent/received
  automatically. A generic `handleResponse` function extracts `detail` from error JSON or falls back
  to a default message.

- **Access token stored in React state (AuthContext), NOT localStorage.** WHY: security requirement
  from RULES.md and the backend design. The refresh token lives in an httpOnly cookie the browser
  manages — JS never touches it.

- **Silent refresh on mount.** WHY: when a user revisits the app, `AuthProvider` tries
  `POST /auth/refresh`. If the cookie is valid, they're silently logged in without re-entering
  credentials. If it fails (no cookie, expired), `isLoading` finishes and ProtectedRoute redirects
  to `/login`.

- **ProtectedRoute wraps the Layout route group, not individual pages.** WHY: one guard for all
  dashboard pages. Login and Register sit outside the protected wrapper as public routes.

- **Login and Register are plain forms (no form library).** WHY: two fields (login) or three fields
  (register) don't warrant React Hook Form / Zod. Controlled inputs with `useState`, submit handler
  calls `useAuth().login()` or `useAuth().register()`, errors displayed from the caught exception
  message.

- **Tests mock `useAuth` at the module level** (Login/Register tests) or mock `@/api/auth` (API
  client and AuthContext tests). WHY: isolates the component under test from the network layer. API
  client tests mock `globalThis.fetch`.

Verification: `npx vitest run` passes 36 tests across 10 files.

### Security alignment with Warissa's hardening PRs

Reviewed Warissa's 3 security PRs (A: auth hardening, B: edge hardening, C: DB creds) and aligned
the frontend:

- **Password min 12 chars.** WHY: backend's `UserCreate.password` now has `min_length=12`.
  Added `minLength={12}` to Register's password input and a hint ("Must be at least 12 characters").
  Updated placeholders to 12 dots on both Login and Register.

- **Generic register error message.** WHY: backend changed from "Username or email already
  registered" to "Could not complete registration" to prevent account enumeration (SEC-005). Frontend
  `handleResponse` already propagates whatever `detail` the backend sends, so no API client change
  needed — only test assertions updated.

- **All test passwords updated to 12+ chars.** WHY: consistency with the backend policy, even though
  frontend tests mock the API. Keeps test data realistic.

Verification: `npx vitest run` passes 36 tests across 10 files.

---

## 2026-09-12 | Oscar + Claude

### Phase 4: Dashboard pages with mock data

Built all dashboard components and assembled the three pages with realistic mock data. TDD throughout
— 62 new tests (98 total). Installed recharts for charting, plus shadcn Card/Table/Badge/Tabs.

Decisions and reasoning:

- **Mock data shaped to match future API contracts.** WHY: the backend has no dashboard endpoints yet
  (Warissa's Phase 6). Designed 4 endpoint interfaces (`getOverview`, `getDevices`, `getSlots`,
  `getTrends`) based on the actual SeedLive CSV data shapes from `scraper/downloads/`. Uses real
  machine serials (VK200044724, VK200044729), real slot codes (0B06, 0A06, etc.), and all 6 observed
  payment types. When Warissa builds the endpoints, frontend just swaps mock for fetch — no component
  changes needed.

- **Mock vs fetch toggle via `VITE_API_URL`.** WHY: `api/dashboard.ts` checks if `API_BASE` is set.
  Empty string (dev without backend) returns mock data immediately. Set URL returns real fetch. Same
  pattern as the auth client — consistent, zero config for development.

- **Recharts over custom SVG.** WHY: recharts provides `BarChart`, `AreaChart`, `LineChart`, `PieChart`
  out of the box with responsive containers. All charts styled with dark theme (custom tooltip, grid,
  axis colors matching our palette). Only exception: SlotMap heatmap is custom CSS Grid because
  recharts has no heatmap component.

- **Recharts mocked in tests.** WHY: recharts renders SVG internally which is brittle in jsdom.
  Created `tests/__mocks__/recharts.tsx` that replaces chart components with `<div data-testid>`.
  Tests verify the wrapper card renders and data passes through, not SVG internals.

- **SlotMap uses CSS Grid with color interpolation.** WHY: the 6x8 heatmap grid needs per-cell
  background colors proportional to revenue/maxRevenue. CSS Grid gives precise control. Color
  interpolates from `bg-surface` (zero revenue) to accent amber (max revenue) via RGB math.

- **New theme tokens for data visualization.** WHY: added `--color-positive` (emerald), `--color-negative`
  (red), 6 chart colors for multi-series, heatmap gradient endpoints, and `--color-border-subtle`. Keeps
  all colors in the CSS `@theme` block for consistency.

- **Pages use `useState` + `useEffect`, no state library.** WHY: each page calls one or two mock API
  functions on mount. Data is static mock — no caching, refetching, or invalidation needed. TanStack
  Query can be added in Phase 5 (integration) if complexity warrants it.

Components built (9 new): StatCard, RevenueChart, DailySales, DeviceBreakdown, RecentTransactions,
SlotMap (CSS Grid heatmap), SlotRankings, PaymentTypes (donut chart), TrendCharts (4 sub-charts).

Page layouts (responsive grid):
- Overview: stat cards (4-col) → charts (2-col) → devices (1/3) + transactions (2/3)
- SlotPerformance: device tabs → slot map (3/5) + rankings (2/5) → payment donut
- Trends: weekly + monthly (2-col) → hourly + day-of-week (2-col)

Verification: `npx vitest run` passes 98 tests across 20 files. `npx tsc --noEmit` clean.
