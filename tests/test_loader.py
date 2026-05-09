import os
import tempfile

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models.tables import Base
from scraper.loader import parse_amount, parse_slot, parse_item_date, parse_date, load_csv


def make_test_db():
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


# ── Loading tests ──


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
