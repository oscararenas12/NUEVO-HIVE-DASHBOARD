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
