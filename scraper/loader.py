"""
SeedLive CSV Loader -- parses report CSVs and loads into Postgres.
"""

import re
from datetime import datetime, date


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
