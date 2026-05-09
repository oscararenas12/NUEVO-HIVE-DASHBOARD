# Postgres Data Pipeline Design

## Overview

Load SeedLive report CSVs into structured Postgres tables for querying, historical analysis, and powering a future dashboard. Data arrives via Playwright scraper today, with HTTP POST push from SeedLive planned for later.

## Tables

### `report_loads` — Tracks every file loaded

| Column | Type | Purpose |
|--------|------|---------|
| `id` | serial PK | |
| `report_type` | text NOT NULL | `daily_item_export`, `sales_rollup`, `detailed_activity` |
| `source` | text NOT NULL | `playwright` or `http_post` |
| `source_file` | text NOT NULL | Original filename |
| `date_start` | date | Report date range start |
| `date_end` | date | Report date range end |
| `rows_loaded` | integer NOT NULL | How many rows were inserted |
| `loaded_at` | timestamp NOT NULL | When it was loaded (defaults to now) |

### `daily_item_export` — Per-transaction, slot-level data (primary table)

| Column | Type | Source CSV Column |
|--------|------|-------------------|
| `id` | serial PK | |
| `load_id` | integer FK → report_loads | Which file this came from |
| `item_ref` | text UNIQUE NOT NULL | `Item Ref #` — dedup key |
| `device` | text NOT NULL | `Device` |
| `location` | text | `Location` |
| `city` | text | `City` |
| `state` | text | `State` |
| `zip` | text | `Zip` |
| `item_type` | text | `Item Type` (payment method) |
| `item_date` | timestamp | `Item Date` |
| `card_number` | text | `Card Number` (masked) |
| `amount` | numeric | `Amount` (parsed from `$2.50` to `2.50`) |
| `slot_code` | text | Parsed from `Column(s)` — e.g. `0B06` |
| `slot_price` | numeric | Parsed from `Column(s)` — e.g. `2.50` |
| `quantity` | integer | `Quantity` |
| `settle_status` | text | `Settle Status` |
| `card_id` | text | `Card Id` |

### `sales_rollup` — Aggregated totals by device + payment type

| Column | Type | Source CSV Column |
|--------|------|-------------------|
| `id` | serial PK | |
| `load_id` | integer FK → report_loads | |
| `customer` | text | `Customer` |
| `location` | text | `Location` |
| `serial_num` | text | `Serial #` |
| `city` | text | `City` |
| `state` | text | `State` |
| `trans_type` | text | `Trans Type Name` |
| `tran_count` | integer | `Tran Count` |
| `vend_count` | integer | `Vend Count` |
| `amount` | numeric | `Amount` |
| `currency_code` | text | `Currency Code` |
| `two_tier_pricing` | numeric | `Two-Tier Pricing` |
| `loyalty_discount` | numeric | `Loyalty Discount` |
| `purchase_discount` | numeric | `Purchase Discount` |
| `free_product_discount` | numeric | `Free Product Discount` |

### `detailed_activity` — Daily totals by device + payment type

| Column | Type | Source CSV Column |
|--------|------|-------------------|
| `id` | serial PK | |
| `load_id` | integer FK → report_loads | |
| `currency` | text | `Currency` |
| `device` | text | `Device` |
| `location` | text | `Location` |
| `day` | date | `Day` |
| `trans_type` | text | `Trans Type` |
| `amount` | numeric | Last column (unnamed in CSV) |

## Deduplication Strategy

- **Daily Item Export**: Each transaction has a unique `item_ref`. On insert, skip rows where `item_ref` already exists. Safe to pull overlapping date ranges.
- **Sales Rollup & Detailed Activity**: No unique row ID. Tracked by `load_id` — don't reload the same file. Checked via `source_file` in `report_loads`.

## Data Loading Flow

1. `seedlive.py` pulls a report CSV to `scraper/downloads/`
2. `loader.py` reads the CSV
3. Checks `report_loads.source_file` — skip if already loaded
4. Parses values:
   - `$2.50` → `2.50` (strip dollar sign, cast to numeric)
   - `0B06($2.50)` → `slot_code = "0B06"`, `slot_price = 2.50`
   - `05/08/2026 04:19:45 AM` → timestamp
   - `05/09/2026` → date
5. For Daily Item Export: skip individual rows where `item_ref` already exists
6. Inserts rows into the appropriate table
7. Creates a `report_loads` entry with `rows_loaded` count
8. Returns count of rows inserted

## Source Tracking

Every row has a `load_id` FK back to `report_loads`. The `source` column distinguishes:
- `playwright` — current scraper approach
- `http_post` — future SeedLive push transport

If the HTTP POST data format differs from the Playwright CSVs, we adjust columns via Alembic migration. The schema and loading logic are the same either way.

## File Structure

```
scraper/
  seedlive.py          # Pulls reports from SeedLive (exists)
  loader.py            # Parses CSVs, loads into Postgres (new)
  downloads/           # CSVs land here

app/
  db/
    session.py         # Postgres connection (exists)
  models/
    tables.py          # SQLAlchemy models for the 4 tables (new, replaces raw_ingest.py)

alembic/               # Database migrations (exists)
```

## What This Enables

- **Quick lookups**: `SELECT * FROM daily_item_export WHERE device = 'VK200044724' AND item_date > '2026-05-01'`
- **Trend analysis**: `SELECT day, SUM(amount) FROM detailed_activity GROUP BY day ORDER BY day`
- **Slot analytics**: `SELECT slot_code, COUNT(*), SUM(amount) FROM daily_item_export GROUP BY slot_code`
- **Dashboard**: All tables are query-ready for a future UI
