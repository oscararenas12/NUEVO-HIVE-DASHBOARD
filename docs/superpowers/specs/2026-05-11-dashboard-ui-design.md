# Dashboard UI Design

## Overview

A responsive web dashboard for vending machine operators to monitor sales, slot performance, and trends. Built with React frontend and FastAPI backend. Dark theme with sidebar navigation. Designed for both desktop and mobile.

## Tech Stack

- **Frontend**: React (with TypeScript), CSS modules or styled-components
- **Backend**: FastAPI (existing) serving JSON API endpoints
- **Charts**: Recharts (React-native charting library)
- **Auth**: OAuth2 with refresh tokens (FastAPI built-in security)
- **Testing**: pytest (API), React Testing Library + Vitest (UI), TDD approach

## Design Reference

Figma file: `https://www.figma.com/design/dlqyTUKwR76UoZWKUDZD3p/NuevoHiveDashBoard`

Frames: Login, Overview, Slot Performance, Trends

## Design Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `bg-primary` | `#12121c` | Page background |
| `surface` | `#1c1c29` | Cards, sidebar |
| `surface-2` | `#242433` | Active states, inputs |
| `border` | `#2e2e3d` | Card borders, dividers |
| `accent` | `#ffa600` | Primary accent (amber) |
| `text-primary` | `#f2f2f7` | Primary text |
| `text-secondary` | `#8c8c9e` | Labels, secondary text |
| `text-muted` | `#616173` | Muted text, placeholders |
| `green` | `#33d687` | Positive values, settled status |
| `red` | `#f55461` | Negative values, fees |
| `blue` | `#548cff` | Revenue charts, device 1 |
| `teal` | `#33c7c2` | Daily sales, device 2 |
| `purple` | `#9966f2` | Hour of day charts |

## Pages

### Login

- Centered card on dark background
- Email + password fields
- "Sign In" button (amber)
- "Forgot password?" link
- On success: receives access token (short-lived, 15 min) + refresh token (longer, 7 days)
- Access token stored in memory (not localStorage — more secure)
- Refresh token stored as httpOnly cookie (can't be stolen by JavaScript)
- Redirects to Overview after login
- When access token expires, refresh token silently gets a new one
- When refresh token expires, user is redirected to login

### Layout (Shared)

- **Sidebar** (260px, left): Hive logo, nav links (Overview, Slot Performance, Trends), user info at bottom
- **Content area** (remaining width): Scrollable, padded
- **Mobile**: Sidebar collapses to hamburger menu
- Active nav item has amber left bar indicator + highlighted background

### Overview

**Header**: Page title + date filter pills (7D, 30D, 90D, YTD, All)

**Stat cards** (4 across):
- Total Revenue (with % change)
- Total Vends (with % change)
- Avg Per Vend (with % change)
- Devices Online (count)

**Revenue Over Time**: Blue bar chart showing daily/weekly revenue

**Revenue by Device**: Two devices with revenue, percentage, and colored bars (blue/teal)

**Daily Sales**: Last 7 days, teal horizontal bars with dollar amount and vend count

**Payments Received**: EFT deposit table — Period, Gross, Fees (red), Net (green)

**Recent Transactions**: Table with Device, Slot (amber), Amount, Payment type, Date & Time, Status (green "Settled")

### Slot Performance

**Device selector**: Pill tabs (All Devices, VK200044724, VK200044729)

**Slot Map**: 6x8 grid (rows A-F, cols 0-7) representing machine face. Each cell shows slot code + revenue. Color intensity = revenue (Hot/Warm/Cool/Dead). Legend below.

**Slot Rankings**: Table — Rank, Slot (amber), Vends, Revenue, Avg price. Top 3 highlighted.

**Payment Types**: Compact horizontal stacked bar with legend (EMV Contactless, Apple Pay, Cash, Google Pay, Other). Uses blue/teal/green/purple colors.

### Trends

**Period selector**: Weekly/Monthly toggle pills

**Weekly Revenue**: Blue vertical bar chart by week

**Sales by Day of Week**: Teal horizontal bars (Mon-Sun)

**Sales by Hour of Day**: Purple vertical bars (0:00-23:00)

**Month over Month**: Green horizontal bars (Jan-May+)

## API Endpoints

All endpoints return JSON. Protected by OAuth2 bearer token (except login/refresh).

### Auth
- `POST /api/auth/login` — email + password, returns access token (15 min) + sets refresh token cookie (7 days)
- `POST /api/auth/refresh` — uses refresh token cookie, returns new access token
- `POST /api/auth/logout` — clears refresh token cookie
- `GET /api/auth/me` — returns current user info (requires access token)

### Overview
- `GET /api/overview/stats?period=all` — total revenue, vends, avg, device count. `period` param: `7d`, `30d`, `90d`, `ytd`, `all`
- `GET /api/overview/revenue-chart?period=all` — daily/weekly revenue data points
- `GET /api/overview/device-breakdown?period=all` — revenue per device
- `GET /api/overview/daily-sales` — last 7 days revenue + vend count per day
- `GET /api/overview/payments` — recent EFT payments (gross, fees, net)
- `GET /api/overview/recent-transactions?limit=10` — latest transactions

### Slot Performance
- `GET /api/slots/heatmap?device=all` — revenue per slot code, for the slot map
- `GET /api/slots/rankings?device=all&limit=12` — slots ranked by revenue
- `GET /api/slots/payment-types?device=all` — revenue breakdown by payment type

### Trends
- `GET /api/trends/weekly-revenue` — revenue per week
- `GET /api/trends/day-of-week` — average revenue by day of week
- `GET /api/trends/hour-of-day` — average revenue by hour
- `GET /api/trends/monthly` — revenue per month

## Testing Strategy (TDD)

### API Tests (pytest)
Every API endpoint gets a test that verifies:
- Correct data shape returned
- Correct values from test data
- Period/device filtering works
- Auth required (401 without token)

### UI Component Tests (React Testing Library + Vitest)
- **Stat cards**: render correct values from API data
- **Charts**: render with correct data props
- **Tables**: render correct rows, columns, formatting
- **Navigation**: sidebar links switch views
- **Login**: form submits, error displays, redirect on success
- **Date filters**: clicking a pill updates the data
- **Device selector**: switching device filters slot data

### Integration Tests
- Login flow: submit credentials, receive token, redirect to dashboard
- Data flow: API returns data, UI renders it correctly
- Filter flow: changing period/device updates all components

## Data Flow

```
Postgres (daily_item_export, sales_rollup, detailed_activity)
    |
    v
FastAPI endpoints (query, aggregate, return JSON)
    |
    v
React components (fetch, render charts/tables)
```

- API endpoints query the existing Postgres tables directly
- No new tables needed for sales views — computed from `daily_item_export` + `sales_rollup` + `detailed_activity`
- **Payments data**: Requires pulling payment reports from SeedLive and loading into a new `payments` table before the Payments Received UI section works. This is a prerequisite step (add report type to `seedlive.py`, create table, load data) — to be done before building the payments UI component

## File Structure

```
frontend/
  src/
    components/
      Layout/           # Sidebar, header, responsive wrapper
      Login/             # Login page
      Overview/          # Stat cards, charts, tables
      SlotPerformance/   # Slot map, rankings, payment types
      Trends/            # Weekly, daily, hourly, monthly charts
      shared/            # Reusable card, table, chart components
    api/                 # API client functions
    auth/                # Auth context, token management
    App.tsx
    main.tsx

app/
  api/
    auth.py             # Login, JWT, user endpoints
    overview.py         # Overview data endpoints
    slots.py            # Slot performance endpoints
    trends.py           # Trends data endpoints
  main.py               # FastAPI app (updated with new routers)
```

## Flexibility for Future Updates

- **New views**: Add a nav item to sidebar + new route + new API endpoint
- **New devices**: Everything filters by device — adding devices just means more data
- **Today's Sales (HTTP POST)**: When push pipeline is ready, add a "Today" view that queries the most recent data
- **User permissions**: Auth system supports roles — add a `role` field to users table when needed
- **New charts/metrics**: Each chart is an independent component backed by its own API endpoint — add without touching existing ones
- **Mobile app**: API is REST JSON — any client can consume it
