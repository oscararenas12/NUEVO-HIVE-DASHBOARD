# Oscar's Frontend Task Board

**Goal:** Build the React frontend with auth UI, dashboard layout, and pages — ready to connect to Warissa's backend API.

**Reference:**
- [docs/STACK.md](../STACK.md) -- tech stack decisions
- [docs/RULES.md](../RULES.md) -- dev practices (TDD, PR workflow, devlog)
- [docs/STRUCTURE.md](../STRUCTURE.md) -- file structure and ownership
- [Shadcn/ui docs](https://ui.shadcn.com/)
- [Vite docs](https://vitejs.dev/)

**Your territory:** `services/client/`

**Important:** This is a phase-based plan, not a rigid checklist. Errors and edge cases WILL come up. When they do, debug, fix, and document the decision in your devlog (docs/DEVLOG-OSCAR.md). Each phase should result in working, testable code before moving to the next.

---

## Sync points with Warissa

These are moments where you MUST coordinate before continuing:

| When | Why | What to align on |
|------|-----|-----------------|
| Before Phase 3 (Auth UI) | You need to know the exact API request/response shapes | Review Warissa's auth endpoints: POST /auth/register, POST /auth/login, GET /auth/status. Get the Pydantic models. |
| Before Phase 4 (Dashboard) | Dashboard pages will call data endpoints that don't exist yet | Agree on API contract: what endpoints will exist, what JSON shape they return. Write mock data based on this. |
| After Phase 3 (Auth UI) | End-to-end auth flow test | Together: register a user, login, verify token works, see dashboard. Both services running in Docker. |
| Before Phase 5 (Integration) | Remove mocks, connect to real API | Warissa's backend must be deployed and stable. Coordinate on CORS, API URL config, error handling patterns. |

Don't wait until you're blocked. Check in with Warissa early if you're unsure about an API shape -- better to ask now than rewrite later.

---

## How to work

1. Create a feature branch: `git checkout -b feature/<phase-name>`
2. Write tests first (TDD) -- every component, every page
3. Run tests often: `npx vitest run`
4. Commit after every completed component/file or ~400 lines -- whichever comes first
5. When phase is complete, push branch and create a PR
6. Update your devlog with decisions and reasoning
7. Wait for PR review before starting next phase

---

## Phase 1: Project Scaffold + Dev Server

**What you're building:** A working React + Vite + TypeScript app in Docker with Shadcn/ui configured. The "hello world" of the frontend -- proves the stack works.

**Files to create:**

```
services/client/
|-- Dockerfile
|-- .dockerignore
|-- index.html
|-- package.json
|-- tsconfig.json
|-- tsconfig.app.json
|-- tsconfig.node.json
|-- vite.config.ts
|-- vitest.config.ts
|-- public/
+-- src/
    |-- App.tsx
    |-- main.tsx
    |-- index.css
    |-- vite-env.d.ts
    +-- tests/
        |-- App.test.tsx
        +-- test-utils.tsx
```

**Key steps:**

- [ ] Initialize Vite project: `npm create vite@latest . -- --template react-ts`
- [ ] Install Shadcn/ui dependencies: tailwindcss, tailwind config, shadcn init
- [ ] Set up dark theme tokens from the Figma design (see STACK.md)
- [ ] Write `App.test.tsx` FIRST:
  - Test that App renders without crashing
  - Test that App displays a heading or welcome text
- [ ] Create basic `App.tsx` that passes the test
- [ ] Set up `test-utils.tsx` with custom render wrapper (for providers later)
- [ ] Set up `vitest.config.ts` with jsdom environment
- [ ] Create `Dockerfile` for dev (node:22, npm install, vite dev server)
- [ ] Create `.dockerignore` (node_modules, dist, coverage)
- [ ] Verify: `docker-compose up client` starts and page loads at localhost:3007

**You'll know this phase is done when:**
- `npx vitest run` passes
- `docker-compose up client` starts without errors
- Browser shows the app at http://localhost:3007
- Shadcn/ui components render with dark theme

**Edge cases to watch for:**
- Vite inside Docker: hot reload needs special config. Set `server.host: '0.0.0.0'` and `server.watch.usePolling: true` in vite.config.ts for Docker compatibility.
- Shadcn/ui init will ask questions -- choose New York style, dark theme, CSS variables.

---

## Phase 2: Layout + Routing

**What you're building:** Sidebar navigation, page routing, and the shared layout shell. No real data yet -- just the skeleton.

**Files to create:**

```
services/client/
+-- src/
    |-- App.tsx              # Update: add router
    |-- components/
    |   |-- Layout.tsx       # Sidebar + content area wrapper
    |   +-- NavBar.tsx       # Sidebar nav links
    |-- pages/
    |   |-- Overview.tsx     # Placeholder page
    |   |-- SlotPerformance.tsx
    |   |-- Trends.tsx
    |   +-- Login.tsx        # Placeholder (built out in Phase 3)
    +-- tests/
        |-- components/
        |   |-- Layout.test.tsx
        |   +-- NavBar.test.tsx
        +-- pages/
            +-- Overview.test.tsx
```

**Key steps:**

- [ ] Install react-router-dom
- [ ] Write `Layout.test.tsx` FIRST:
  - Test that sidebar renders with nav links
  - Test that content area renders children
- [ ] Write `NavBar.test.tsx`:
  - Test that nav links are visible (Overview, Slot Performance, Trends)
  - Test that active link is highlighted
- [ ] Create `Layout.tsx`: sidebar (260px) + scrollable content area
- [ ] Create `NavBar.tsx`: nav links with active state indicator
- [ ] Create placeholder pages (Overview, SlotPerformance, Trends, Login)
- [ ] Write `Overview.test.tsx`:
  - Test that page renders with title
- [ ] Update `App.tsx` with React Router routes:
  - `/` -> Overview (protected, later)
  - `/slots` -> SlotPerformance (protected, later)
  - `/trends` -> Trends (protected, later)
  - `/login` -> Login (public)
- [ ] Apply dark theme: bg-primary (#12121c), surface (#1c1c29), accent (#ffa600)
- [ ] Mobile responsive: sidebar collapses to hamburger menu

**You'll know this phase is done when:**
- All layout/nav tests pass
- Clicking sidebar links switches pages
- Dark theme looks right
- Mobile view shows hamburger menu

**Edge cases to watch for:**
- React Router v6 uses different syntax than v5. Make sure you're on v6.
- Test navigation with MemoryRouter in tests (not BrowserRouter).

---

## Phase 3: Auth UI (Login + Register)

**SYNC POINT: Talk to Warissa before starting this phase.**
You need the exact shape of:
- POST /auth/register request body and response
- POST /auth/login request body and response
- GET /auth/status response
- How the JWT token is returned (body vs cookie)

If Warissa's backend isn't ready yet, build against mock data and a fake API client. But agree on the contract first so you don't have to rewrite.

**Files to create/modify:**

```
services/client/
+-- src/
    |-- api/
    |   +-- auth.ts          # API client for auth endpoints
    |-- auth/
    |   |-- AuthContext.tsx   # Auth state provider (token, user, login/logout)
    |   +-- ProtectedRoute.tsx # Redirect to login if not authenticated
    |-- pages/
    |   |-- Login.tsx         # Update: real login form
    |   +-- Register.tsx      # Registration form
    +-- tests/
        |-- auth/
        |   +-- AuthContext.test.tsx
        |-- pages/
        |   |-- Login.test.tsx
        |   +-- Register.test.tsx
        +-- api/
            +-- auth.test.ts
```

**Key steps:**

- [ ] Write `Login.test.tsx` FIRST:
  - Test that login form renders email + password fields
  - Test that submit calls API with credentials
  - Test that error message shows on invalid credentials
  - Test that successful login redirects to overview
- [ ] Write `Register.test.tsx`:
  - Test that form renders username, email, password fields
  - Test that submit calls API with registration data
  - Test that duplicate email shows error
  - Test that successful register redirects to login
- [ ] Create `api/auth.ts`:
  - `login(email, password)` -- POST /auth/login
  - `register(username, email, password)` -- POST /auth/register
  - `getStatus(token)` -- GET /auth/status
  - `refresh()` -- POST /auth/refresh
  - For now, can use mock responses until backend is ready
- [ ] Create `AuthContext.tsx`:
  - Stores access token in memory (NOT localStorage)
  - Provides: user, isAuthenticated, login(), logout(), register()
  - On mount: try to refresh token silently
- [ ] Create `ProtectedRoute.tsx`:
  - Wraps routes that require auth
  - Redirects to /login if not authenticated
- [ ] Build `Login.tsx` with Shadcn/ui form components
- [ ] Build `Register.tsx` with Shadcn/ui form components
- [ ] Update `App.tsx`: wrap routes with AuthContext, protect dashboard routes
- [ ] Install and configure form handling (React Hook Form or Formik + Zod)

**You'll know this phase is done when:**
- All auth tests pass
- Login form submits and handles success/error
- Register form submits and handles success/error
- Protected routes redirect to login when not authenticated
- Successful login shows the dashboard layout

**Edge cases to watch for:**
- Token storage: access token in memory (React state), NOT localStorage. This is a security requirement.
- Refresh token: handled via httpOnly cookie by the backend. The frontend just calls POST /auth/refresh -- the browser sends the cookie automatically.
- CORS: when connecting to the real backend, you'll need to configure CORS. This is a Phase 5 (integration) concern, but be aware.

---

## Phase 4: Dashboard Pages (with mock data)

**SYNC POINT: Talk to Warissa about what data endpoints will look like.**
Agree on the API contract for dashboard data. What JSON shapes will the backend return? Build your components against that shape using mock data. When the backend is ready, you just swap the mock for the real API call.

**Files to create:**

```
services/client/
+-- src/
    |-- api/
    |   +-- dashboard.ts     # API client for dashboard endpoints (mocked initially)
    |-- components/
    |   |-- StatCard.tsx      # Revenue, vends, avg, devices cards
    |   |-- RevenueChart.tsx  # Bar chart (recharts)
    |   |-- DeviceBreakdown.tsx
    |   |-- DailySales.tsx
    |   |-- RecentTransactions.tsx
    |   |-- SlotMap.tsx       # 6x8 heatmap grid
    |   |-- SlotRankings.tsx
    |   +-- PaymentTypes.tsx
    |-- pages/
    |   |-- Overview.tsx      # Update: real components
    |   |-- SlotPerformance.tsx # Update: real components
    |   +-- Trends.tsx        # Update: real components
    +-- tests/
        +-- components/
            |-- StatCard.test.tsx
            |-- SlotMap.test.tsx
            +-- RecentTransactions.test.tsx
```

**Key steps:**

- [ ] Install recharts for charts
- [ ] Write `StatCard.test.tsx` FIRST:
  - Test renders label, value, and percent change
  - Test positive change shows green, negative shows red
- [ ] Build `StatCard.tsx` component
- [ ] Write `SlotMap.test.tsx`:
  - Test renders 6x8 grid
  - Test slot cells show code + revenue
  - Test color intensity matches revenue level
- [ ] Build `SlotMap.tsx` component
- [ ] Build remaining components (RevenueChart, DailySales, etc.) with tests
- [ ] Create `api/dashboard.ts` with mock data matching agreed API contract
- [ ] Assemble Overview page with stat cards + revenue chart + daily sales + recent transactions
- [ ] Assemble SlotPerformance page with slot map + rankings + payment types
- [ ] Assemble Trends page with weekly/monthly/hourly charts

**You'll know this phase is done when:**
- All component tests pass
- Overview page shows stat cards, charts, and tables with mock data
- SlotPerformance page shows heatmap grid and rankings
- Trends page shows time-based charts
- Everything uses dark theme with correct colors

**Edge cases to watch for:**
- Recharts needs specific data shapes. Define TypeScript interfaces for chart data early.
- Mock data should be realistic (use actual values from the SeedLive CSVs in scraper/downloads/ for reference).
- Slot map grid: drink machine and snack machine may have different grid dimensions. Check with Oscar (yourself) on actual machine layouts.

---

## Phase 5: Integration (with Warissa)

**SYNC POINT: Both services must be working independently before this phase.**
This is where frontend meets backend. Both of you work together.

**What you're doing:**
- [ ] Remove mock data, connect to real API endpoints
- [ ] Configure CORS on backend (coordinate with Warissa)
- [ ] Configure API base URL via environment variable (VITE_API_SERVICE_URL)
- [ ] Test full auth flow end-to-end: register -> login -> see dashboard -> logout
- [ ] Configure nginx to proxy /api/* to backend and /* to frontend
- [ ] Test everything running together via `docker-compose up`
- [ ] Fix any issues that come up (there will be some)
- [ ] Update devlog with integration decisions

**You'll know this phase is done when:**
- `docker-compose up` starts all 4 services (client, api, api-db, nginx)
- User can register, login, see dashboard, and logout
- All data flows from Postgres through FastAPI to React
- CI passes for both services

---

## After all phases

Once Phase 5 is complete, the frontend has:
- Working React app in Docker with dark theme
- Sidebar layout with routing
- Auth flow (login, register, protected routes, token refresh)
- Dashboard pages with real data from the API
- Tests for all components and pages
- CI passing

Next steps (planned later):
- Refund request page (public, no login)
- Refund status tracking page
- Data pipeline integration (connect scraper to backend)
