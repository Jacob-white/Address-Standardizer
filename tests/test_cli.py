"""
Tests for Command-Line Interface (CLI).
=======================================
"""

import sys
import json
import csv
import pytest
from unittest.mock import patch
from address_standardizer.cli import main


class TestCLI:
    def test_cli_parse_single_address(self, capsys):
        test_args = ["address-standardizer", "parse", "100 Wall Street, Suite 400, New York, NY 10005"]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["street1"] == "100 WALL ST"
        assert data["street2"] == "STE 400"
        assert data["city"] == "NEW YORK"
        assert data["state"] == "NY"
        assert data["postal_code"] == "10005"
        assert data["country"] == "USA"
        assert data["normalized_address_key"] == "100 WALL ST|STE 400|NEW YORK|NY|10005|USA"
        assert data["building_key"] == "100 WALL ST||NEW YORK|NY|10005|USA"

    def test_cli_batch_csv(self, tmp_path, capsys):
        input_file = tmp_path / "input.csv"
        output_file = tmp_path / "output.csv"

        with open(input_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "street1", "city", "state", "postal_code", "country"])
            writer.writerow(["1", "200 Park Avenue, Suite 1200", "New York", "NY", "10166", "USA"])
            writer.writerow(["2", "500 North Michigan Ave, Fl 14", "Chicago", "IL", "60611", "USA"])

        test_args = [
            "address-standardizer",
            "batch",
            str(input_file),
            str(output_file),
        ]
        with patch.object(sys, "argv", test_args):
            main()

        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["std_street1"] == "200 PARK AVE"
            assert rows[0]["std_street2"] == "STE 1200"
            assert rows[0]["std_city"] == "NEW YORK"
            assert rows[0]["std_state"] == "NY"
            assert rows[0]["normalized_address_key"] == "200 PARK AVE|STE 1200|NEW YORK|NY|10166|USA"
            assert rows[1]["std_street1"] == "500 N MICHIGAN AVE"
            assert rows[1]["std_street2"] == "FL 14"
            assert rows[1]["std_city"] == "CHICAGO"
            assert rows[1]["std_state"] == "IL"

    def test_cli_shorthand_invocation(self, capsys):
        test_args = ["address-standardizer", "350 5th Ave, New York, NY 10118"]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["street1"] == "350 5TH AVE"
        assert data["city"] == "NEW YORK"
        assert data["state"] == "NY"
        assert data["postal_code"] == "10118"

