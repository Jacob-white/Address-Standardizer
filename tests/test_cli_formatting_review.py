"""CLI csv output must neutralize spreadsheet formula injection."""

from address_standardizer.cli_formatting import _format_csv_row


def test_csv_row_neutralizes_formula_prefixes():
    row = _format_csv_row({"street1": "=HYPERLINK(\"http://x\")", "city": "+1", "state": "@SUM", "postal_code": "-2",
                           "confidence_score": 0.5})
    cells = row.split(",")
    assert cells[0].startswith("\"'=") or cells[0].startswith("'=")
    assert "'+1" in row and "'@SUM" in row and "'-2" in row
    assert row.rstrip().endswith(",")  # trailing empty key cell; score stays numeric, not quoted
    assert "0.5000" in row and "'0.5000" not in row


def test_csv_row_leaves_normal_values_alone():
    assert _format_csv_row({"street1": "100 WALL ST", "city": "NEW YORK", "state": "NY"}).startswith("100 WALL ST,,NEW YORK,NY")
