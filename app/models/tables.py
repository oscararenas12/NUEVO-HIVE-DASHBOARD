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
