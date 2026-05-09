# Postgres Data Pipeline Design

## Overview

Load SeedLive report CSVs into structured Postgres tables for querying, historical analysis, and powering a future dashboard. Data arrives via Playwright scraper today, with HTTP POST push from SeedLive planned for later.

## Data Sources

Two SeedLive reports feed into the primary `daily_item_export` table:

| Report | Granularity | Custom Date Range? | Use Case |
|--------|------------|-------------------|----------|
| **Daily Item Export** | Per vend | No (last day only, from Report Register) | Daily ongoing data |
| **Transaction Line Item Export** | Per vend | Yes (any date range) | Historical backfills |

Both contain individual vend-level data (one row = one item sold from one slot). They map into the same `daily_item_export` table. Transaction Line Item has slightly different column names and is missing some fields (city, state, settle_status), but the core data (device, slot, amount, timestamp) is the same.

Two additional reports provide aggregated views:

| Report | Granularity | Use Case |
|--------|------------|----------|
| **Sales Rollup** | Totals by device + payment type | Quick revenue summaries |
| **Detailed Activity** | Daily totals by device + payment type | Trend analysis |

## Tables

### `report_loads` -- Tracks every file loaded

| Column | Type | Purpose |
|--------|------|---------|
| `id` | serial PK | |
| `report_type` | text NOT NULL | `daily_item_export`, `sales_rollup`, `detailed_activity` |
| `source` | text NOT NULL | `playwright`, `playwright_backfill`, or `http_post` |
| `source_file` | text NOT NULL | Original filename |
| `date_start` | date | Report date range start |
| `date_end` | date | Report date range end |
| `rows_loaded` | integer NOT NULL | How many rows were inserted |
| `loaded_at` | timestamp NOT NULL | When it was loaded (defaults to now) |

### `daily_item_export` -- Per-vend, slot-level data (primary table)

Each row is one item sold from one slot at one timestamp.

| Column | Type | Daily Item Export CSV | Transaction Line Item CSV |
|--------|------|---------------------|--------------------------|
| `id` | serial PK | | |
| `load_id` | integer FK | report_loads.id | report_loads.id |
| `item_ref` | text UNIQUE NOT NULL | `Item Ref #` | `Ref Nbr` |
| `device` | text NOT NULL | `Device` | `Device Serial Num` |
| `location` | text | `Location` | NULL |
| `city` | text | `City` | NULL |
| `state` | text | `State` | NULL |
| `zip` | text | `Zip` | NULL |
| `item_type` | text | `Item Type` (full name) | `Trans Type Code` (code only) |
| `item_date` | timestamp | `Item Date` | `Tran Date` + `Tran Time` |
| `card_number` | text | `Card Number` (masked) | `Masked Card Number` |
| `amount` | numeric | `Amount` (parsed from $) | `Tran Amount` (already numeric) |
| `slot_code` | text | Parsed from `Column(s)` | `Item` |
| `slot_price` | numeric | Parsed from `Column(s)` | `Line Item Price` |
| `quantity` | integer | `Quantity` | `Quantity` |
| `settle_status` | text | `Settle Status` | NULL |
| `card_id` | text | `Card Id` | `Card Id` |

### `sales_rollup` -- Aggregated totals by device + payment type

| Column | Type | Source CSV Column |
|--------|------|-------------------|
| `id` | serial PK | |
| `load_id` | integer FK | |
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

### `detailed_activity` -- Daily totals by device + payment type

| Column | Type | Source CSV Column |
|--------|------|-------------------|
| `id` | serial PK | |
| `load_id` | integer FK | |
| `currency` | text | `Currency` |
| `device` | text | `Device` |
| `location` | text | `Location` |
| `day` | date | `Day` |
| `trans_type` | text | `Trans Type` |
| `amount` | numeric | Last column (unnamed in CSV) |

## Deduplication Strategy

- **daily_item_export**: Each vend has a unique `item_ref` (from `Item Ref #` or `Ref Nbr`). On insert, skip rows where `item_ref` already exists. Safe to pull overlapping date ranges or load from both Daily Item Export and Transaction Line Item -- dedup handles it.
- **Sales Rollup & Detailed Activity**: No unique row ID. Tracked by `load_id` -- don't reload the same file. Checked via `source_file` in `report_loads`.

## Data Loading Flow

### Daily loading (ongoing)
1. `seedlive.py --report daily_item` pulls Daily Item Export CSV
2. `loader.py` parses and loads via `load_csv(path, "daily_item_export")`
3. Dedup on `item_ref` -- safe to re-run

### Historical backfill
1. `seedlive.py --report transaction_line_item --start MM/DD/YYYY --end MM/DD/YYYY` pulls data for any date range
2. `loader.load_transaction_line_item_backfill(path)` maps columns and loads into `daily_item_export`
3. Same `item_ref` dedup -- safe to overlap with existing data
4. Fields not in Transaction Line Item (city, state, settle_status, location) are stored as NULL

### Parsing rules
- `$2.50` -> `2.50` (strip dollar sign, cast to numeric)
- `0B06($2.50)` -> `slot_code = "0B06"`, `slot_price = 2.50`
- `05/08/2026 04:19:45 AM` -> timestamp
- `05/09/2026` -> date
- Transaction Line Item amounts are already numeric (no parsing needed)

## Source Tracking

Every row has a `load_id` FK back to `report_loads`. The `source` column distinguishes:
- `playwright` -- daily pulls via scraper
- `playwright_backfill` -- historical backfills via Transaction Line Item
- `http_post` -- future SeedLive push transport

If the HTTP POST data format differs from the Playwright CSVs, we adjust columns via Alembic migration. The schema and loading logic are the same either way.

## File Structure

```
scraper/
  seedlive.py          # Pulls reports from SeedLive
  loader.py            # Parses CSVs, loads into Postgres
    - load_csv()                              # Load Daily Item / Sales Rollup / Detailed Activity
    - load_transaction_line_item_backfill()    # Backfill historical data
  explore_filters.py   # Maps SeedLive form fields for reference
  downloads/           # CSVs land here

app/
  db/
    session.py         # Postgres connection
  models/
    tables.py          # SQLAlchemy models for the 4 tables

alembic/               # Database migrations
tests/
  test_loader.py       # 27 tests covering parsing, loading, dedup, backfill
```

## What This Enables

- **Quick lookups**: `SELECT * FROM daily_item_export WHERE device = 'VK200044724' AND item_date > '2026-05-01'`
- **Trend analysis**: `SELECT item_date::date as day, SUM(amount) FROM daily_item_export GROUP BY day ORDER BY day`
- **Slot analytics**: `SELECT slot_code, COUNT(*), SUM(amount) FROM daily_item_export GROUP BY slot_code ORDER BY SUM(amount) DESC`
- **Dashboard**: All tables are query-ready for a future UI
