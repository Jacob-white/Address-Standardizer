"""
Unit tests for CLI piped input, table and csv format options, and batch mapping/jsonl options.
"""

import sys
import io
import json
import csv
from unittest.mock import patch
from address_standardizer.cli import main


class TestCLIPipedAndFormats:
    def test_cli_parse_format_table(self, capsys):
        test_args = ["address-standardizer", "parse", "100 Wall Street, Suite 400, New York, NY 10005", "--format", "table"]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert "Street 1" in lines[0]
        assert "100 WALL ST" in lines[2]
        assert "STE 400" in lines[2]
        assert "NEW YORK" in lines[2]
        assert "10005" in lines[2]

    def test_cli_parse_format_csv(self, capsys):
        test_args = ["address-standardizer", "parse", "100 Wall Street, Suite 400, New York, NY 10005", "--format", "csv"]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert lines[0].startswith("street1,street2,city,state,postal_code")
        assert "100 WALL ST,STE 400,NEW YORK,NY,10005,USA,standardized" in lines[1]

    def test_cli_parse_dash_from_stdin(self, capsys):
        fake_stdin = io.StringIO("200 Park Avenue, Suite 1200, New York, NY 10166\n")
        test_args = ["address-standardizer", "parse", "-", "--format", "csv"]
        with patch.object(sys, "argv", test_args), patch.object(sys, "stdin", fake_stdin):
            main()

        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert lines[0].startswith("street1,street2")
        assert "200 PARK AVE,STE 1200,NEW YORK,NY,10166" in lines[1]

    def test_cli_top_level_piped_stdin_table(self, capsys):
        fake_stdin = io.StringIO("350 5th Ave, New York, NY 10118\nPSC 1004 BOX 500, APO, AE 09724\n")
        test_args = ["address-standardizer", "--format", "table"]
        with patch.object(sys, "argv", test_args), patch.object(sys, "stdin", fake_stdin):
            main()

        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert "Street 1" in lines[0]
        assert "350 5TH AVE" in lines[2]
        assert "PSC 1004 BOX 500" in lines[3]

    def test_cli_top_level_piped_stdin_json(self, capsys):
        fake_stdin = io.StringIO("100 Wall St, New York, NY 10005\n")
        test_args = ["address-standardizer"]
        with patch.object(sys, "argv", test_args), patch.object(sys, "stdin", fake_stdin):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out.strip())
        assert data["street1"] == "100 WALL ST"
        assert data["city"] == "NEW YORK"

    def test_cli_batch_jsonl_auto_detection(self, tmp_path, capsys):
        input_file = tmp_path / "addresses.jsonl"
        output_file = tmp_path / "output.jsonl"

        with open(input_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({"street1": "100 Wall St", "city": "New York", "state": "NY", "postal_code": "10005"}) + "\n")

        test_args = [
            "address-standardizer",
            "batch",
            str(input_file),
            str(output_file),
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        assert "Standardized 1 record(s)" in captured.out

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
            assert data["std_street1"] == "100 WALL ST"

    def test_cli_batch_with_mapping_flag(self, tmp_path, capsys):
        input_file = tmp_path / "custom.csv"
        output_file = tmp_path / "custom_out.csv"

        with open(input_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["full_street", "town", "st_code", "zip_num"])
            writer.writerow(["350 Fifth Ave", "New York", "NY", "10118"])

        mapping_str = '{"full_street": "street1", "town": "city", "st_code": "state", "zip_num": "postal_code"}'
        test_args = [
            "address-standardizer",
            "batch",
            str(input_file),
            str(output_file),
            "--mapping", mapping_str,
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        assert "Standardized 1 record(s)" in captured.out

        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row["std_street1"] == "350 5TH AVE"
            assert row["std_city"] == "NEW YORK"

    def test_cli_batch_with_mapping_file(self, tmp_path, capsys):
        input_file = tmp_path / "file_input.csv"
        output_file = tmp_path / "file_output.csv"
        map_file = tmp_path / "schema.json"

        with open(input_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["addr_line", "city_col", "state_col", "zip_col"])
            writer.writerow(["200 Park Ave", "New York", "NY", "10166"])

        with open(map_file, "w", encoding="utf-8") as f:
            json.dump({"addr_line": "street1", "city_col": "city", "state_col": "state", "zip_col": "postal_code"}, f)

        test_args = [
            "address-standardizer",
            "batch",
            str(input_file),
            str(output_file),
            "--mapping", str(map_file),
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        assert "Standardized 1 record(s)" in captured.out

        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row["std_street1"] == "200 PARK AVE"
