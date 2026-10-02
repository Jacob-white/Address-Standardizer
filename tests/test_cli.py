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

    def test_cli_parse_multiword_positional_address(self, capsys):
        test_args = ["address-standardizer", "parse", "100", "Wall", "Street,", "New", "York,", "NY", "10005"]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["street1"] == "100 WALL ST"
        assert data["city"] == "NEW YORK"
        assert data["state"] == "NY"
        assert data["postal_code"] == "10005"

    def test_cli_parse_structured_options(self, capsys):
        test_args = [
            "address-standardizer",
            "parse",
            "--street1", "200 Park Avenue",
            "--street2", "Suite 1200",
            "--city", "New York",
            "--state", "NY",
            "--zip", "10166",
            "--country", "USA",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["street1"] == "200 PARK AVE"
        assert data["street2"] == "STE 1200"
        assert data["city"] == "NEW YORK"
        assert data["state"] == "NY"
        assert data["postal_code"] == "10166"

    def test_cli_parse_with_geocode(self, capsys):
        test_args = ["address-standardizer", "parse", "100 Wall Street, New York, NY 10005", "--geocode"]
        mock_geo_result = {
            "1": {
                "latitude": 40.7061,
                "longitude": -74.0060,
                "precision": "rooftop",
            }
        }
        with patch.object(sys, "argv", test_args):
            with patch("address_standardizer.cli.CensusGeocoder.geocode_batch", return_value=mock_geo_result):
                main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["street1"] == "100 WALL ST"
        assert data["latitude"] == 40.7061
        assert data["longitude"] == -74.0060
        assert data["geocode_precision"] == "rooftop"

    def test_cli_batch_csv(self, tmp_path, capsys):
        input_file = tmp_path / "input.csv"
        output_file = tmp_path / "output.csv"

        with open(input_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "street1", "street2", "city", "state", "postal_code", "country"])
            writer.writerow(["1", "200 Park Avenue", "Suite 1200", "New York", "NY", "10166", "USA"])
            writer.writerow(["2", "500 North Michigan Ave", "Fl 14", "Chicago", "IL", "60611", "USA"])

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

    def test_cli_batch_csv_custom_columns(self, tmp_path, capsys):
        input_file = tmp_path / "custom_input.csv"
        output_file = tmp_path / "custom_output.csv"

        with open(input_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "addr_line1", "addr_line2", "town", "region", "zip_code", "nation"])
            writer.writerow(["1", "100 Main Street", "Suite 500", "Denver", "CO", "80202", "USA"])

        test_args = [
            "address-standardizer",
            "batch",
            str(input_file),
            str(output_file),
            "--street-col", "addr_line1",
            "--street2-col", "addr_line2",
            "--city-col", "town",
            "--state-col", "region",
            "--zip-col", "zip_code",
            "--country-col", "nation",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["std_street1"] == "100 MAIN ST"
            assert rows[0]["std_street2"] == "STE 500"
            assert rows[0]["std_city"] == "DENVER"
            assert rows[0]["std_state"] == "CO"

    def test_cli_batch_csv_with_geocode(self, tmp_path, capsys):
        input_file = tmp_path / "input_geo.csv"
        output_file = tmp_path / "output_geo.csv"

        with open(input_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "street1", "city", "state", "postal_code", "country"])
            writer.writerow(["1", "100 Wall Street", "New York", "NY", "10005", "USA"])
            writer.writerow(["2", "Unmatched Street", "Nowhere", "ZZ", "00000", "USA"])

        mock_geo_result = {
            "0": {
                "latitude": 40.7061,
                "longitude": -74.0060,
                "precision": "rooftop",
            }
        }

        test_args = [
            "address-standardizer",
            "batch",
            str(input_file),
            str(output_file),
            "--geocode",
        ]
        with patch.object(sys, "argv", test_args):
            with patch("address_standardizer.cli.CensusGeocoder.geocode_batch", return_value=mock_geo_result):
                main()

        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["latitude"] == "40.7061"
            assert rows[0]["longitude"] == "-74.006"
            assert rows[0]["geocode_precision"] == "rooftop"
            assert rows[1]["latitude"] == ""
            assert rows[1]["longitude"] == ""

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

    def test_cli_no_args_prints_help_and_exits(self, capsys):
        test_args = ["address-standardizer"]
        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_cli_module_main_invocation(self, capsys):
        import runpy
        test_args = ["address-standardizer", "100 Wall St, New York, NY 10005"]
        sys.modules.pop("address_standardizer.cli", None)
        with patch.object(sys, "argv", test_args):
            runpy.run_module("address_standardizer.cli", run_name="__main__")
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["street1"] == "100 WALL ST"

    def test_cli_unknown_flag_exits_2(self):
        """Verify that unknown option flags starting with '-' exit with code 2 rather than parsing as addresses."""
        test_args = ["address-standardizer", "--unknown-flag"]
        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_cli_help_flags(self, capsys):
        """Verify that -h and --help print usage and exit with 0."""
        for flag in ["-h", "--help"]:
            with patch.object(sys, "argv", ["address-standardizer", flag]):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                captured = capsys.readouterr()
                assert "usage:" in captured.out.lower() or "address-standardizer" in captured.out.lower()

    def test_cli_parse_international_address(self, capsys):
        """Verify CLI parse subcommand handles international addresses."""
        test_args = [
            "address-standardizer",
            "parse",
            "--street1", "25 Bank Street",
            "--city", "London",
            "--zip", "E14 5JP",
            "--country", "United Kingdom",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["street1"] == "25 BANK ST"
        assert data["city"] == "LONDON"
        assert data["country"] == "GBR"
        assert data["is_us"] is False

