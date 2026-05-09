"""
SeedLive CSV Loader -- parses report CSVs and loads into Postgres.

Usage:
    uv run python -m scraper.loader --type daily_item_export "path/to/file.csv"
    uv run python -m scraper.loader --type sales_rollup "path/to/file.csv"
    uv run python -m scraper.loader --type detailed_activity "path/to/file.csv"
"""

import csv
import os
import re
from datetime import datetime, date

from sqlalchemy.orm import Session as SASession

from app.models.tables import (
    ReportLoad, DailyItemExport, SalesRollup, DetailedActivity,
)


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


# ── Loading ──


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
        # Check if file already loaded (for aggregate report types)
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

        load_entry.rows_loaded = loaded
        db.commit()

        return {"rows_loaded": loaded, "skipped": skipped, "skipped_file": False}


def _load_daily_item(db: SASession, rows: list[dict], load_id: int) -> tuple[int, int]:
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
            load_id=load_id,
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


def _load_sales_rollup(db: SASession, rows: list[dict], load_id: int) -> int:
    loaded = 0
    for row in rows:
        db.add(SalesRollup(
            load_id=load_id,
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


def _load_detailed_activity(db: SASession, rows: list[dict], load_id: int) -> int:
    loaded = 0
    for row in rows:
        # The unnamed last column is the amount
        values = list(row.values())
        amount_val = values[-1] if values else None
        db.add(DetailedActivity(
            load_id=load_id,
            currency=row.get("Currency", "").strip() or None,
            device=row.get("Device", "").strip() or None,
            location=row.get("Location", "").strip() or None,
            day=parse_date(row.get("Day")),
            trans_type=row.get("Trans Type", "").strip() or None,
            amount=parse_amount(amount_val),
        ))
        loaded += 1
    return loaded


# ── Backfill ──


def load_transaction_line_item_backfill(
    filepath: str,
    source: str = "playwright_backfill",
    session_factory=None,
) -> dict:
    """
    Load a Transaction Line Item Export CSV into the daily_item_export table.

    Maps the different column names to the daily_item_export schema.
    Uses Ref Nbr as item_ref for dedup. Fields not present in Transaction
    Line Item (city, state, settle_status, etc.) are left as NULL.

    Use this for historical backfills where Daily Item Export can't pull
    custom date ranges. For daily going forward, use Daily Item Export.
    """
    if session_factory is None:
        from app.db.session import SessionLocal
        session_factory = SessionLocal

    filename = os.path.basename(filepath)

    with session_factory() as db:
        load_entry = ReportLoad(
            report_type="daily_item_export",
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

        loaded = 0
        skipped = 0
        for row in rows:
            ref = row.get("Ref Nbr", "").strip()
            if not ref:
                continue
            exists = db.query(DailyItemExport).filter_by(item_ref=ref).first()
            if exists:
                skipped += 1
                continue

            # Combine Tran Date + Tran Time into a datetime
            tran_date = row.get("Tran Date", "").strip()
            tran_time = row.get("Tran Time", "").strip()
            item_date = None
            if tran_date and tran_time:
                try:
                    item_date = datetime.strptime(f"{tran_date} {tran_time}", "%m/%d/%Y %H:%M:%S")
                except ValueError:
                    item_date = parse_date(tran_date)

            amount = float(row["Tran Amount"]) if row.get("Tran Amount") else None
            price = float(row["Line Item Price"]) if row.get("Line Item Price") else None

            db.add(DailyItemExport(
                load_id=load_id,
                item_ref=ref,
                device=row.get("Device Serial Num", "").strip(),
                item_type=row.get("Trans Type Code", "").strip() or None,
                item_date=item_date,
                card_number=row.get("Masked Card Number", "").strip() or None,
                amount=amount,
                slot_code=row.get("Item", "").strip() or None,
                slot_price=price,
                quantity=int(row["Quantity"]) if row.get("Quantity") else None,
                card_id=row.get("Card Id", "").strip() or None,
            ))
            loaded += 1

        load_entry.rows_loaded = loaded
        db.commit()

        return {"rows_loaded": loaded, "skipped": skipped}


# ── CLI ──


if __name__ == "__main__":
    import argparse
    import glob

    parser = argparse.ArgumentParser(description="Load SeedLive CSVs into Postgres")
    parser.add_argument("files", nargs="*", help="CSV files to load")
    parser.add_argument("--type", required=True,
                        choices=["daily_item_export", "sales_rollup", "detailed_activity"])
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
