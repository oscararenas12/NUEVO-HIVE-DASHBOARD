import os
import tempfile

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models.tables import Base
from scraper.loader import parse_amount, parse_slot, parse_item_date, parse_date, load_csv, load_transaction_line_item_backfill


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


# ── Data integrity tests ──


def test_daily_item_parsed_values():
    """Verify parsed values land correctly in the DB, not just row counts."""
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "daily_item.csv", DAILY_ITEM_CSV)
        load_csv(path, "daily_item_export", source="test", session_factory=Session)

        with Session() as s:
            row = s.execute(
                text("SELECT * FROM daily_item_export WHERE item_ref = '22248127354'")
            ).fetchone()
            assert row.device == "VK200044724"
            assert row.location == "Oscar M Arenas"
            assert row.city == "South Gate"
            assert row.state == "CA"
            assert row.zip == "90280"
            assert row.item_type == "CREDIT (EMV CONTACTLESS)"
            assert float(row.amount) == 2.50
            assert row.slot_code == "0B06"
            assert float(row.slot_price) == 2.50
            assert row.quantity == 1
            assert row.settle_status == "SETTLED"
            assert row.card_id == "3268435804"
            assert "2026" in str(row.item_date)
            assert "05" in str(row.item_date) or "5" in str(row.item_date)


def test_sales_rollup_parsed_values():
    """Verify sales rollup amounts and counts parse correctly."""
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "sr.csv", SALES_ROLLUP_CSV)
        load_csv(path, "sales_rollup", source="test", session_factory=Session)

        with Session() as s:
            row = s.execute(text("SELECT * FROM sales_rollup")).fetchone()
            assert row.serial_num == "VK200044724"
            assert row.trans_type == "Cash"
            assert row.tran_count == 20
            assert row.vend_count == 20
            assert float(row.amount) == 45.00
            assert row.currency_code == "USD"
            assert float(row.two_tier_pricing) == 0.00


def test_detailed_activity_parsed_values():
    """Verify detailed activity date and amount parse correctly."""
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "da.csv", DETAILED_ACTIVITY_CSV)
        load_csv(path, "detailed_activity", source="test", session_factory=Session)

        with Session() as s:
            row = s.execute(text("SELECT * FROM detailed_activity")).fetchone()
            assert row.device == "VK200044724"
            assert row.trans_type == "Credit (EMV Contactless)"
            assert float(row.amount) == 18.00
            assert "2026" in str(row.day)
            assert "05-09" in str(row.day) or "5/9" in str(row.day)


def test_report_loads_tracks_source():
    """Verify report_loads records source correctly."""
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "daily_item.csv", DAILY_ITEM_CSV)
        load_csv(path, "daily_item_export", source="playwright", session_factory=Session)

        with Session() as s:
            load = s.execute(text("SELECT * FROM report_loads")).fetchone()
            assert load.source == "playwright"
            assert load.source_file == "daily_item.csv"
            assert load.report_type == "daily_item_export"
            assert load.rows_loaded == 2


def test_daily_item_dedup_across_files():
    """Dedup works when same transactions appear in different files."""
    Session = make_test_db()
    file1 = '''"Device","Item Ref #","Customer Name","Location","Address Line 1","Address Line 2","City","State","Zip","Asset #","Item Type","Item Date","Card Number","Amount","Two-Tier Pricing","Column(s)","Quantity","Orig Ref #","Fee Rate","Settle Status","Payment #","Description","Card Id"
"VK200044724","11111","Oscar M Arenas","Oscar M Arenas",,,"South Gate","CA","90280","TBD","CASH","05/07/2026 10:00:00 AM","","$2.00",,"0A01($2.00)",1,"","","SETTLED","","",""
"VK200044724","22222","Oscar M Arenas","Oscar M Arenas",,,"South Gate","CA","90280","TBD","CASH","05/08/2026 10:00:00 AM","","$3.00",,"0A02($3.00)",1,"","","SETTLED","","",""
'''
    file2 = '''"Device","Item Ref #","Customer Name","Location","Address Line 1","Address Line 2","City","State","Zip","Asset #","Item Type","Item Date","Card Number","Amount","Two-Tier Pricing","Column(s)","Quantity","Orig Ref #","Fee Rate","Settle Status","Payment #","Description","Card Id"
"VK200044724","22222","Oscar M Arenas","Oscar M Arenas",,,"South Gate","CA","90280","TBD","CASH","05/08/2026 10:00:00 AM","","$3.00",,"0A02($3.00)",1,"","","SETTLED","","",""
"VK200044724","33333","Oscar M Arenas","Oscar M Arenas",,,"South Gate","CA","90280","TBD","CASH","05/09/2026 10:00:00 AM","","$4.00",,"0A03($4.00)",1,"","","SETTLED","","",""
'''
    with tempfile.TemporaryDirectory() as tmp:
        path1 = write_csv(tmp, "export_day1.csv", file1)
        path2 = write_csv(tmp, "export_day2.csv", file2)

        r1 = load_csv(path1, "daily_item_export", source="test", session_factory=Session)
        assert r1["rows_loaded"] == 2

        r2 = load_csv(path2, "daily_item_export", source="test", session_factory=Session)
        assert r2["rows_loaded"] == 1  # only 33333 is new
        assert r2["skipped"] == 1      # 22222 already exists

        with Session() as s:
            total = s.execute(text("SELECT COUNT(*) FROM daily_item_export")).scalar()
            assert total == 3


def test_load_unknown_report_type():
    """Unknown report type raises ValueError."""
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "test.csv", DAILY_ITEM_CSV)
        try:
            load_csv(path, "nonexistent_type", source="test", session_factory=Session)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unknown report type" in str(e)


# ── Transaction Line Item backfill tests ──

TRANSACTION_LINE_ITEM_CSV = '''"Device Serial Num","Ref Nbr","Trans Type Code","Masked Card Number","Tran Amount","Item","Line Item Price","Line Item MDB Number","Quantity","Tran Date","Tran Time","Line Item Description","Card Id"
"VK200044724","22093419881","R","481582******2942","3","0D07","3","3335","1","04/09/2026","09:41:04","0D07","2814844442"
"VK200044724","22093561737","R","434256******8579","2","0D03","2","3331","1","04/09/2026","09:58:42","0D03","3182735164"
"VK200044729","22093564628","R","434256******8579","2.5","0B06","2.5","2822","1","04/10/2026","09:59:11","0B06","3182735164"
'''


def test_backfill_loads_into_daily_item_export():
    """Transaction Line Item rows map into daily_item_export table."""
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "tli.csv", TRANSACTION_LINE_ITEM_CSV)
        result = load_transaction_line_item_backfill(path, session_factory=Session)
        assert result["rows_loaded"] == 3
        assert result["skipped"] == 0


def test_backfill_parsed_values():
    """Verify backfill maps columns correctly to daily_item_export."""
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(tmp, "tli.csv", TRANSACTION_LINE_ITEM_CSV)
        load_transaction_line_item_backfill(path, session_factory=Session)

        with Session() as s:
            row = s.execute(
                text("SELECT * FROM daily_item_export WHERE item_ref = '22093419881'")
            ).fetchone()
            assert row.device == "VK200044724"
            assert row.slot_code == "0D07"
            assert float(row.slot_price) == 3.0
            assert float(row.amount) == 3.0
            assert row.card_number == "481582******2942"
            assert row.card_id == "2814844442"
            assert row.quantity == 1
            assert "2026" in str(row.item_date)
            # Fields not in Transaction Line Item should be None
            assert row.city is None
            assert row.state is None
            assert row.settle_status is None


def test_backfill_dedup_against_existing():
    """Backfill skips transactions already loaded via Daily Item Export."""
    Session = make_test_db()
    with tempfile.TemporaryDirectory() as tmp:
        # First load some via Daily Item Export
        daily_csv = '''"Device","Item Ref #","Customer Name","Location","Address Line 1","Address Line 2","City","State","Zip","Asset #","Item Type","Item Date","Card Number","Amount","Two-Tier Pricing","Column(s)","Quantity","Orig Ref #","Fee Rate","Settle Status","Payment #","Description","Card Id"
"VK200044724","22093419881","Oscar M Arenas","Oscar M Arenas",,,"South Gate","CA","90280","TBD","CREDIT (EMV CONTACTLESS)","04/09/2026 09:41:04 AM","481582******2942","$3.00",,"0D07($3.00)",1,"","","SETTLED","","","2814844442"
'''
        path1 = write_csv(tmp, "daily.csv", daily_csv)
        load_csv(path1, "daily_item_export", source="test", session_factory=Session)

        # Now backfill with Transaction Line Item that overlaps
        path2 = write_csv(tmp, "tli.csv", TRANSACTION_LINE_ITEM_CSV)
        result = load_transaction_line_item_backfill(path2, session_factory=Session)
        assert result["rows_loaded"] == 2  # 22093561737 and 22093564628
        assert result["skipped"] == 1      # 22093419881 already exists

        with Session() as s:
            total = s.execute(text("SELECT COUNT(*) FROM daily_item_export")).scalar()
            assert total == 3
