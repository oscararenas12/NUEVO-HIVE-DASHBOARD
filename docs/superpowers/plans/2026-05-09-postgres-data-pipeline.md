# Postgres Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Load SeedLive CSV reports into structured Postgres tables so we can query sales, slot performance, and trends.

**Architecture:** Replace the old JSONB-based raw_ingest models with typed tables matching each report's CSV schema. A loader module parses CSVs and inserts into Postgres with deduplication. Alembic handles migrations.

**Tech Stack:** Python 3.12, SQLAlchemy, Alembic, PostgreSQL 16, pytest

---

## File Structure

```
app/
  db/
    session.py              # Postgres connection (exists, no changes)
  models/
    __init__.py             # (exists, no changes)
    tables.py               # NEW — SQLAlchemy models: ReportLoad, DailyItemExport, SalesRollup, DetailedActivity

scraper/
  loader.py                 # NEW — CSV parsing + Postgres loading
  seedlive.py               # (exists, no changes)

alembic/
  env.py                    # MODIFY — point at new Base from tables.py
  versions/
    <new>_structured_tables.py  # NEW — auto-generated migration

tests/
  test_loader.py            # NEW — tests for parsing and loading
```

---

### Task 1: SQLAlchemy Models

**Files:**
- Create: `app/models/tables.py`
- Modify: `app/models/__init__.py`

- [ ] **Step 1: Create the models file**

```python
# app/models/tables.py
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ReportLoad(Base):
    __tablename__ = "report_loads"

    id = Column(Integer, primary_key=True)
    report_type = Column(Text, nullable=False)
    source = Column(Text, nullable=False)
    source_file = Column(Text, nullable=False)
    date_start = Column(Date)
    date_end = Column(Date)
    rows_loaded = Column(Integer, nullable=False)
    loaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class DailyItemExport(Base):
    __tablename__ = "daily_item_export"

    id = Column(Integer, primary_key=True)
    load_id = Column(Integer, ForeignKey("report_loads.id"), nullable=False)
    item_ref = Column(Text, unique=True, nullable=False)
    device = Column(Text, nullable=False)
    location = Column(Text)
    city = Column(Text)
    state = Column(Text)
    zip = Column(Text)
    item_type = Column(Text)
    item_date = Column(DateTime)
    card_number = Column(Text)
    amount = Column(Numeric)
    slot_code = Column(Text)
    slot_price = Column(Numeric)
    quantity = Column(Integer)
    settle_status = Column(Text)
    card_id = Column(Text)


class SalesRollup(Base):
    __tablename__ = "sales_rollup"

    id = Column(Integer, primary_key=True)
    load_id = Column(Integer, ForeignKey("report_loads.id"), nullable=False)
    customer = Column(Text)
    location = Column(Text)
    serial_num = Column(Text)
    city = Column(Text)
    state = Column(Text)
    trans_type = Column(Text)
    tran_count = Column(Integer)
    vend_count = Column(Integer)
    amount = Column(Numeric)
    currency_code = Column(Text)
    two_tier_pricing = Column(Numeric)
    loyalty_discount = Column(Numeric)
    purchase_discount = Column(Numeric)
    free_product_discount = Column(Numeric)


class DetailedActivity(Base):
    __tablename__ = "detailed_activity"

    id = Column(Integer, primary_key=True)
    load_id = Column(Integer, ForeignKey("report_loads.id"), nullable=False)
    currency = Column(Text)
    device = Column(Text)
    location = Column(Text)
    day = Column(Date)
    trans_type = Column(Text)
    amount = Column(Numeric)
```

- [ ] **Step 2: Verify models import cleanly**

Run: `uv run python -c "from app.models.tables import Base, ReportLoad, DailyItemExport, SalesRollup, DetailedActivity; print('OK')" `
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add app/models/tables.py
git commit -m "Add SQLAlchemy models for structured report tables"
```

---

### Task 2: Alembic Migration

**Files:**
- Modify: `alembic/env.py` (line 8 — change import from `raw_ingest` to `tables`)
- Create: `alembic/versions/<auto>_structured_tables.py` (auto-generated)

- [ ] **Step 1: Update alembic/env.py to use new models**

Change line 8 from:
```python
from app.models.raw_ingest import Base
```
to:
```python
from app.models.tables import Base
```

- [ ] **Step 2: Generate migration**

Run: `uv run alembic revision --autogenerate -m "add structured report tables"`
Expected: Output shows `Detected added table 'report_loads'`, `'daily_item_export'`, `'sales_rollup'`, `'detailed_activity'`

- [ ] **Step 3: Run migration**

Run: `uv run alembic upgrade head`
Expected: `Running upgrade ... add structured report tables`

- [ ] **Step 4: Verify tables exist**

Run: `PGPASSWORD='Toby@ux24$$' "/c/Program Files/PostgreSQL/16/bin/psql.exe" -U postgres -h localhost -d hive_dashboard -c "\dt"`
Expected: Tables `report_loads`, `daily_item_export`, `sales_rollup`, `detailed_activity` listed

- [ ] **Step 5: Commit**

```bash
git add alembic/env.py alembic/versions/
git commit -m "Add migration for structured report tables"
```

---

### Task 3: Parsing Functions

**Files:**
- Create: `scraper/loader.py` (parsing functions only — no DB code yet)
- Create: `tests/test_loader.py`

- [ ] **Step 1: Write tests for parsing helpers**

```python
# tests/test_loader.py
from scraper.loader import parse_amount, parse_slot, parse_item_date, parse_date


def test_parse_amount_with_dollar():
    assert parse_amount("$2.50") == 2.50


def test_parse_amount_without_dollar():
    assert parse_amount("2.50") == 2.50


def test_parse_amount_zero():
    assert parse_amount("$0.00") == 0.00


def test_parse_amount_empty():
    assert parse_amount("") is None


def test_parse_amount_none():
    assert parse_amount(None) is None


def test_parse_slot_normal():
    code, price = parse_slot("0B06($2.50)")
    assert code == "0B06"
    assert price == 2.50


def test_parse_slot_no_parens():
    code, price = parse_slot("0B06")
    assert code == "0B06"
    assert price is None


def test_parse_slot_empty():
    code, price = parse_slot("")
    assert code is None
    assert price is None


def test_parse_slot_none():
    code, price = parse_slot(None)
    assert code is None
    assert price is None


def test_parse_item_date():
    result = parse_item_date("05/08/2026 04:19:45 AM")
    assert result.year == 2026
    assert result.month == 5
    assert result.day == 8
    assert result.hour == 4
    assert result.minute == 19


def test_parse_item_date_empty():
    assert parse_item_date("") is None


def test_parse_date():
    result = parse_date("05/09/2026")
    assert result.year == 2026
    assert result.month == 5
    assert result.day == 9


def test_parse_date_empty():
    assert parse_date("") is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_loader.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scraper.loader'`

- [ ] **Step 3: Implement parsing functions**

```python
# scraper/loader.py
"""
SeedLive CSV Loader — parses report CSVs and loads into Postgres.
"""

import re
from datetime import datetime, date
from decimal import Decimal


def parse_amount(val: str | None) -> float | None:
    """Parse '$2.50' or '2.50' to float. Returns None for empty/None."""
    if not val or not val.strip():
        return None
    return float(val.strip().lstrip("$"))


def parse_slot(val: str | None) -> tuple[str | None, float | None]:
    """Parse '0B06($2.50)' into ('0B06', 2.50). Returns (None, None) for empty."""
    if not val or not val.strip():
        return None, None
    match = re.match(r"^([A-Za-z0-9]+)\(\$?([\d.]+)\)$", val.strip())
    if match:
        return match.group(1), float(match.group(2))
    return val.strip(), None


def parse_item_date(val: str | None) -> datetime | None:
    """Parse '05/08/2026 04:19:45 AM' to datetime."""
    if not val or not val.strip():
        return None
    return datetime.strptime(val.strip(), "%m/%d/%Y %I:%M:%S %p")


def parse_date(val: str | None) -> date | None:
    """Parse '05/09/2026' to date."""
    if not val or not val.strip():
        return None
    return datetime.strptime(val.strip(), "%m/%d/%Y").date()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_loader.py -v`
Expected: All 13 tests PASS

- [ ] **Step 5: Commit**

```bash
git add scraper/loader.py tests/test_loader.py
git commit -m "Add CSV parsing helpers with tests"
```

---

### Task 4: CSV Loading Functions

**Files:**
- Modify: `scraper/loader.py` (add loading functions)
- Modify: `tests/test_loader.py` (add loading tests)

- [ ] **Step 1: Add pytest dependency**

Run: `uv add --dev pytest`

- [ ] **Step 2: Write test for loading Daily Item Export**

Add to `tests/test_loader.py`:

```python
import os
import tempfile
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.tables import Base
from scraper.loader import load_csv


def make_test_db():
    """Create a fresh in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def write_csv(tmp_dir, filename, content):
    path = os.path.join(tmp_dir, filename)
    with open(path, "w") as f:
        f.write(content)
    return path


DAILY_ITEM_CSV = '''"Device","Item Ref #","Customer Name","Location","Address Line 1","Address Line 2","City","State","Zip","Asset #","Item Type","Item Date","Card Number","Amount","Two-Tier Pricing","Column(s)","Quantity","Orig Ref #","Fee Rate","Settle Status","Payment #","Description","Card Id"
"VK200044724","22248127354","Oscar M Arenas","Oscar M Arenas",,,"South Gate","CA","90280","TBD","CREDIT (EMV CONTACTLESS)","05/08/2026 04:19:45 AM","434256******2089","$2.50",,"0B06($2.50)",1,"","","SETTLED","","","3268435804"
"VK200044724","22248153299","Oscar M Arenas","Oscar M Arenas",,,"South Gate","CA","90280","TBD","CREDIT (EMV CONTACTLESS)","05/08/2026 04:29:13 AM","434256******2089","$2.50",,"0A06($2.50)",1,"","","SETTLED","","","3268435804"
'''

SALES_ROLLUP_CSV = '''"Customer","Region","Location","Serial #","Asset #","Make","Model","City","State","Trans Type Name","Tran Count","Vend Count","Amount","Currency Code","Two-Tier Pricing (Included in Net Revenue)","Loyalty Discount","Campaign Name","Purchase Discount","Free Product Discount"
"Oscar M Arenas",,"Oscar M Arenas","VK200044724","TBD","TBD","TO BE DETERMINED","South Gate","CA","Cash","20","20","$45.00","USD","$0.00","$0.00",,"$0.00","$0.00"
'''

DETAILED_ACTIVITY_CSV = '''"Currency","Region","Device","Device","Location","Day","Trans Type",
"United States Dollars","","VK200044724","VK200044724","Oscar M Arenas","05/09/2026","Credit (EMV Contactless)","$18.00"
'''


def test_load_daily_item_export():
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "daily_item.csv", DAILY_ITEM_CSV)
        result = load_csv(path, "daily_item_export", source="test", session_factory=Session)
        assert result["rows_loaded"] == 2
        assert result["skipped"] == 0

        with Session() as s:
            rows = s.execute(text("SELECT * FROM daily_item_export")).fetchall()
            assert len(rows) == 2
            loads = s.execute(text("SELECT * FROM report_loads")).fetchall()
            assert len(loads) == 1
            assert loads[0].report_type == "daily_item_export"


def test_load_daily_item_dedup():
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "daily_item.csv", DAILY_ITEM_CSV)
        load_csv(path, "daily_item_export", source="test", session_factory=Session)
        # Load same file again
        result = load_csv(path, "daily_item_export", source="test", session_factory=Session)
        assert result["rows_loaded"] == 0
        assert result["skipped"] == 2


def test_load_sales_rollup():
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "sales_rollup.csv", SALES_ROLLUP_CSV)
        result = load_csv(path, "sales_rollup", source="test", session_factory=Session)
        assert result["rows_loaded"] == 1


def test_load_detailed_activity():
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "activity.csv", DETAILED_ACTIVITY_CSV)
        result = load_csv(path, "detailed_activity", source="test", session_factory=Session)
        assert result["rows_loaded"] == 1


def test_load_skip_already_loaded_file():
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "sales_rollup.csv", SALES_ROLLUP_CSV)
        load_csv(path, "sales_rollup", source="test", session_factory=Session)
        result = load_csv(path, "sales_rollup", source="test", session_factory=Session)
        assert result["rows_loaded"] == 0
        assert result["skipped_file"] is True
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_loader.py::test_load_daily_item_export -v`
Expected: FAIL — `ImportError: cannot import name 'load_csv'`

- [ ] **Step 4: Implement load_csv function**

Add to `scraper/loader.py`:

```python
import csv
import os
from sqlalchemy.orm import Session as SASession
from app.models.tables import (
    Base, ReportLoad, DailyItemExport, SalesRollup, DetailedActivity,
)


def load_csv(
    filepath: str,
    report_type: str,
    source: str = "playwright",
    session_factory=None,
) -> dict:
    """
    Load a CSV file into the appropriate Postgres table.

    Returns dict with rows_loaded, skipped, skipped_file keys.
    """
    if session_factory is None:
        from app.db.session import SessionLocal
        session_factory = SessionLocal

    filename = os.path.basename(filepath)

    with session_factory() as db:
        # Check if file already loaded (for non-dedup report types)
        existing = db.query(ReportLoad).filter_by(
            source_file=filename, report_type=report_type
        ).first()

        if existing and report_type != "daily_item_export":
            return {"rows_loaded": 0, "skipped": 0, "skipped_file": True}

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if report_type == "daily_item_export":
            loaded, skipped = _load_daily_item(db, rows)
        elif report_type == "sales_rollup":
            loaded, skipped = _load_sales_rollup(db, rows), 0
        elif report_type == "detailed_activity":
            loaded, skipped = _load_detailed_activity(db, rows), 0
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        load_entry = ReportLoad(
            report_type=report_type,
            source=source,
            source_file=filename,
            rows_loaded=loaded if isinstance(loaded, int) else loaded,
        )
        db.add(load_entry)
        db.commit()

        return {
            "rows_loaded": loaded if isinstance(loaded, int) else loaded,
            "skipped": skipped,
            "skipped_file": False,
        }


def _load_daily_item(db: SASession, rows: list[dict]) -> tuple[int, int]:
    loaded = 0
    skipped = 0
    for row in rows:
        item_ref = row.get("Item Ref #", "").strip()
        if not item_ref:
            continue
        exists = db.query(DailyItemExport).filter_by(item_ref=item_ref).first()
        if exists:
            skipped += 1
            continue
        slot_code, slot_price = parse_slot(row.get("Column(s)"))
        db.add(DailyItemExport(
            load_id=0,  # Will be set after ReportLoad is created
            item_ref=item_ref,
            device=row.get("Device", "").strip(),
            location=row.get("Location", "").strip() or None,
            city=row.get("City", "").strip() or None,
            state=row.get("State", "").strip() or None,
            zip=row.get("Zip", "").strip() or None,
            item_type=row.get("Item Type", "").strip() or None,
            item_date=parse_item_date(row.get("Item Date")),
            card_number=row.get("Card Number", "").strip() or None,
            amount=parse_amount(row.get("Amount")),
            slot_code=slot_code,
            slot_price=slot_price,
            quantity=int(row["Quantity"]) if row.get("Quantity") else None,
            settle_status=row.get("Settle Status", "").strip() or None,
            card_id=row.get("Card Id", "").strip() or None,
        ))
        loaded += 1
    return loaded, skipped


def _load_sales_rollup(db: SASession, rows: list[dict]) -> int:
    loaded = 0
    for row in rows:
        db.add(SalesRollup(
            load_id=0,
            customer=row.get("Customer", "").strip() or None,
            location=row.get("Location", "").strip() or None,
            serial_num=row.get("Serial #", "").strip() or None,
            city=row.get("City", "").strip() or None,
            state=row.get("State", "").strip() or None,
            trans_type=row.get("Trans Type Name", "").strip() or None,
            tran_count=int(row["Tran Count"]) if row.get("Tran Count") else None,
            vend_count=int(row["Vend Count"]) if row.get("Vend Count") else None,
            amount=parse_amount(row.get("Amount")),
            currency_code=row.get("Currency Code", "").strip() or None,
            two_tier_pricing=parse_amount(row.get("Two-Tier Pricing (Included in Net Revenue)")),
            loyalty_discount=parse_amount(row.get("Loyalty Discount")),
            purchase_discount=parse_amount(row.get("Purchase Discount")),
            free_product_discount=parse_amount(row.get("Free Product Discount")),
        ))
        loaded += 1
    return loaded


def _load_detailed_activity(db: SASession, rows: list[dict]) -> int:
    loaded = 0
    for row in rows:
        # CSV has duplicate "Device" header — DictReader keeps last value
        # The unnamed last column is the amount
        values = list(row.values())
        amount_val = values[-1] if values else None
        db.add(DetailedActivity(
            load_id=0,
            currency=row.get("Currency", "").strip() or None,
            device=row.get("Device", "").strip() or None,
            location=row.get("Location", "").strip() or None,
            day=parse_date(row.get("Day")),
            trans_type=row.get("Trans Type", "").strip() or None,
            amount=parse_amount(amount_val),
        ))
        loaded += 1
    return loaded
```

Note: `load_id=0` is a placeholder. In the real implementation, we create the `ReportLoad` first with `rows_loaded=0`, flush to get its ID, set `load_id` on each row, then update `rows_loaded` at the end. The test uses SQLite which is more lenient. We'll fix this properly in Task 5.

- [ ] **Step 5: Run all tests**

Run: `uv run pytest tests/test_loader.py -v`
Expected: All 8 tests PASS (13 parser tests + 5 loader tests)

- [ ] **Step 6: Commit**

```bash
git add scraper/loader.py tests/test_loader.py
git commit -m "Add CSV loading with deduplication and tests"
```

---

### Task 5: Fix load_id Assignment and CLI

**Files:**
- Modify: `scraper/loader.py` (fix load_id, add CLI entry point)

- [ ] **Step 1: Fix load_csv to properly assign load_id**

Replace the `load_csv` function body to create `ReportLoad` first, use its ID, then update `rows_loaded`:

```python
def load_csv(
    filepath: str,
    report_type: str,
    source: str = "playwright",
    session_factory=None,
) -> dict:
    if session_factory is None:
        from app.db.session import SessionLocal
        session_factory = SessionLocal

    filename = os.path.basename(filepath)

    with session_factory() as db:
        existing = db.query(ReportLoad).filter_by(
            source_file=filename, report_type=report_type
        ).first()

        if existing and report_type != "daily_item_export":
            return {"rows_loaded": 0, "skipped": 0, "skipped_file": True}

        # Create load entry first to get its ID
        load_entry = ReportLoad(
            report_type=report_type,
            source=source,
            source_file=filename,
            rows_loaded=0,
        )
        db.add(load_entry)
        db.flush()
        load_id = load_entry.id

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if report_type == "daily_item_export":
            loaded, skipped = _load_daily_item(db, rows, load_id)
        elif report_type == "sales_rollup":
            loaded, skipped = _load_sales_rollup(db, rows, load_id), 0
        elif report_type == "detailed_activity":
            loaded, skipped = _load_detailed_activity(db, rows, load_id), 0
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        load_entry.rows_loaded = loaded if isinstance(loaded, int) else loaded
        db.commit()

        return {
            "rows_loaded": loaded if isinstance(loaded, int) else loaded,
            "skipped": skipped,
            "skipped_file": False,
        }
```

Update `_load_daily_item`, `_load_sales_rollup`, `_load_detailed_activity` signatures to accept `load_id` parameter and use it instead of `0`.

- [ ] **Step 2: Add CLI entry point**

Add at the bottom of `scraper/loader.py`:

```python
if __name__ == "__main__":
    import argparse
    import glob

    parser = argparse.ArgumentParser(description="Load SeedLive CSVs into Postgres")
    parser.add_argument("files", nargs="*", help="CSV files to load (default: all in scraper/downloads/)")
    parser.add_argument("--type", required=True, choices=["daily_item_export", "sales_rollup", "detailed_activity"])
    parser.add_argument("--source", default="playwright")
    args = parser.parse_args()

    files = args.files or glob.glob("scraper/downloads/*.csv")
    for f in files:
        print(f"Loading {os.path.basename(f)}...")
        result = load_csv(f, args.type, source=args.source)
        if result.get("skipped_file"):
            print(f"  Skipped (already loaded)")
        else:
            print(f"  Loaded {result['rows_loaded']} rows, skipped {result['skipped']} dupes")
```

- [ ] **Step 3: Run tests to verify nothing broke**

Run: `uv run pytest tests/test_loader.py -v`
Expected: All tests PASS

- [ ] **Step 4: Test with real data against Postgres**

Run: `uv run python -m scraper.loader --type daily_item_export "scraper/downloads/Daily Item Export for 55226937.csv"`
Expected: `Loaded 5 rows, skipped 0 dupes`

Run again: `uv run python -m scraper.loader --type daily_item_export "scraper/downloads/Daily Item Export for 55226937.csv"`
Expected: `Loaded 0 rows, skipped 5 dupes`

- [ ] **Step 5: Load all existing CSVs**

```bash
uv run python -m scraper.loader --type sales_rollup "scraper/downloads/Sales Rollup - From 04-09-2026 to 05-09-2026.csv"
uv run python -m scraper.loader --type detailed_activity "scraper/downloads/Activity - All from April 09 2026 to May 09 2026.csv"
```

- [ ] **Step 6: Verify data in Postgres**

```bash
PGPASSWORD='Toby@ux24$$' "/c/Program Files/PostgreSQL/16/bin/psql.exe" -U postgres -h localhost -d hive_dashboard -c "SELECT report_type, source_file, rows_loaded FROM report_loads;"
PGPASSWORD='Toby@ux24$$' "/c/Program Files/PostgreSQL/16/bin/psql.exe" -U postgres -h localhost -d hive_dashboard -c "SELECT device, slot_code, amount FROM daily_item_export LIMIT 5;"
```

- [ ] **Step 7: Commit**

```bash
git add scraper/loader.py tests/test_loader.py
git commit -m "Fix load_id assignment and add CLI for CSV loading"
```
