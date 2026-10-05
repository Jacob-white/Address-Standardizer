"""Tests for CLI International Enhancements.
========================================
Covers international address parsing with UPU formatting, country flags,
the validate-postal subcommand, piped streams, and shorthand invocations.
"""

import csv
import io
import json
import sys
from unittest.mock import patch

from address_standardizer.cli import main


class TestCLIInternational:
    """Test suite for international CLI capabilities."""

    def test_cli_parse_format_upu_us(self, capsys):
        test_args = [
            "address-standardizer",
            "parse",
            "100 Wall St, New York, NY 10005",
            "--format",
            "upu",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        out = captured.out.strip()
        assert "100 WALL ST" in out
        assert "NEW YORK, NY 10005" in out
        assert "UNITED STATES" in out

    def test_cli_parse_format_upu_uk(self, capsys):
        test_args = [
            "address-standardizer",
            "parse",
            "10 Downing St, London SW1A 2AA, UK",
            "--format",
            "upu",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        out = captured.out.strip()
        assert "10 DOWNING ST" in out
        assert "LONDON SW1A 2AA" in out
        assert "UNITED KINGDOM" in out

    def test_cli_parse_format_upu_japan(self, capsys):
        test_args = [
            "address-standardizer",
            "parse",
            "1-1 Chiyoda, Chiyoda-ku, Tokyo 100-8111",
            "--country",
            "JPN",
            "--format",
            "upu",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        out = captured.out.strip()
        assert "〒100-8111" in out
        assert "TOKYO" in out
        assert "JAPAN" in out

    def test_cli_parse_with_country_flags(self, capsys):
        # Test long --country
        test_args = [
            "address-standardizer",
            "parse",
            "Pariser Platz 1, 10117 Berlin",
            "--country",
            "DEU",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["country"] == "DEU"
        assert data["postal_code"] == "10117"
        assert data["city"] == "BERLIN"

        # Test short -c
        test_args_short = [
            "address-standardizer",
            "parse",
            "10 Avenue des Champs-Élysées, 75008 Paris",
            "-c",
            "FRA",
        ]
        with patch.object(sys, "argv", test_args_short):
            main()

        captured_short = capsys.readouterr()
        data_short = json.loads(captured_short.out)
        assert data_short["country"] == "FRA"
        assert data_short["postal_code"] == "75008"

    def test_cli_validate_postal_valid(self, capsys):
        # US ZIP
        with patch.object(sys, "argv", ["address-standardizer", "validate-postal", "10005", "-c", "USA"]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["is_valid"] is True
        assert data["country"] == "USA"
        assert data["postal_code"] == "10005"
        assert data["formatted_code"] == "10005"
        assert data["is_non_postal_country"] is False

        # UK Postcode
        with patch.object(sys, "argv", ["address-standardizer", "validate-postal", "SW1A 1AA", "-c", "GBR"]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["is_valid"] is True
        assert data["country"] == "GBR"
        assert data["formatted_code"] == "SW1A 1AA"

        # Japan Postcode
        with patch.object(sys, "argv", ["address-standardizer", "validate-postal", "100-0001", "-c", "JPN"]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["is_valid"] is True
        assert data["country"] == "JPN"
        assert data["formatted_code"] == "100-0001"

    def test_cli_validate_postal_invalid(self, capsys):
        # Letters in numeric US ZIP
        with patch.object(sys, "argv", ["address-standardizer", "validate-postal", "ABCDE", "-c", "USA"]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["is_valid"] is False
        assert data["country"] == "USA"
        assert "illegal" in data["reason"].lower() or "invalid" in data["reason"].lower()

        # Invalid length
        with patch.object(sys, "argv", ["address-standardizer", "validate-postal", "123", "-c", "USA"]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["is_valid"] is False
        assert "short" in data["reason"].lower()

    def test_cli_validate_postal_non_postal_country(self, capsys):
        # United Arab Emirates (ARE) - non-postal country
        with patch.object(sys, "argv", ["address-standardizer", "validate-postal", "", "-c", "ARE"]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["is_valid"] is True
        assert data["country"] == "ARE"
        assert data["is_non_postal_country"] is True
        assert "non-postal" in data["reason"].lower()

        # Qatar (QAT) - non-postal country
        with patch.object(sys, "argv", ["address-standardizer", "validate-postal", "00000", "-c", "QAT"]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["is_valid"] is True
        assert data["country"] == "QAT"
        assert data["is_non_postal_country"] is True

    def test_cli_validate_postal_text_extraction(self, capsys):
        # Extraction from address text
        with patch.object(
            sys,
            "argv",
            ["address-standardizer", "validate-postal", "10 Downing St, London SW1A 2AA, UK"],
        ):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["is_valid"] is True
        assert data["country"] == "GBR"
        assert data["formatted_code"] == "SW1A 2AA"

    def test_cli_validate_postal_formats(self, capsys):
        # Text format
        with patch.object(
            sys,
            "argv",
            ["address-standardizer", "validate-postal", "10005", "-c", "USA", "--format", "text"],
        ):
            main()
        captured = capsys.readouterr()
        assert "POSTAL CODE VALIDATION" in captured.out
        assert "Validity:              True" in captured.out
        assert "Country:               USA" in captured.out

        # Table format
        with patch.object(
            sys,
            "argv",
            ["address-standardizer", "validate-postal", "10005", "-c", "USA", "--format", "table"],
        ):
            main()
        captured = capsys.readouterr()
        assert "Postal Code" in captured.out
        assert "Country" in captured.out
        assert "10005" in captured.out
        assert "True" in captured.out

    def test_cli_piped_format_upu(self, capsys):
        fake_stdin = io.StringIO("10 Downing St, London SW1A 2AA, UK\n100 Wall St, New York, NY 10005\n")
        with patch("sys.stdin", fake_stdin):
            with patch.object(sys, "argv", ["address-standardizer", "--format", "upu"]):
                main()

        captured = capsys.readouterr()
        out = captured.out
        assert "10 DOWNING ST" in out
        assert "UNITED KINGDOM" in out
        assert "100 WALL ST" in out
        assert "UNITED STATES" in out

    def test_cli_piped_validate_postal(self, capsys):
        fake_stdin = io.StringIO("10005\nSW1A 1AA\n")
        with patch("sys.stdin", fake_stdin):
            with patch.object(sys, "argv", ["address-standardizer", "validate-postal", "-c", "GBR"]):
                main()

        captured = capsys.readouterr()
        lines = [line.strip() for line in captured.out.strip().split("\n") if line.strip()]
        assert len(lines) == 2
        d1 = json.loads(lines[0])
        d2 = json.loads(lines[1])
        assert d1["country"] == "GBR"
        assert d1["is_valid"] is False
        assert d2["is_valid"] is True
        assert d2["country"] == "GBR"
        assert d2["formatted_code"] == "SW1A 1AA"

    def test_cli_shorthand_with_country(self, capsys):
        test_args = [
            "address-standardizer",
            "--country",
            "JPN",
            "1-1 Chiyoda, Chiyoda-ku, Tokyo 100-8111",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["country"] == "JPN"
        assert data["city"] == "CHIYODA-KU"
        assert data["postal_code"] == "100-8111"

        # Short flag -c
        test_args_short = [
            "address-standardizer",
            "-c",
            "JPN",
            "1-1 Chiyoda, Chiyoda-ku, Tokyo 100-8111",
        ]
        with patch.object(sys, "argv", test_args_short):
            main()

        captured_short = capsys.readouterr()
        data_short = json.loads(captured_short.out)
        assert data_short["country"] == "JPN"

    def test_cli_shorthand_with_country_and_upu(self, capsys):
        test_args = [
            "address-standardizer",
            "-c",
            "JPN",
            "--format",
            "upu",
            "1-1 Chiyoda, Chiyoda-ku, Tokyo 100-8111",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        out = captured.out.strip()
        assert "〒100-8111" in out
        assert "TOKYO" in out
        assert "JAPAN" in out

    def test_cli_batch_csv_with_country(self, tmp_path, capsys):
        input_file = tmp_path / "intl_input.csv"
        output_file = tmp_path / "intl_output.csv"

        with open(input_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "street1", "street2", "city", "state", "postal_code"])
            writer.writerow(["1", "1-1 Chiyoda", "", "Chiyoda-ku", "Tokyo", "100-8111"])

        test_args = [
            "address-standardizer",
            "batch",
            str(input_file),
            str(output_file),
            "-c",
            "JPN",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["std_country"] == "JPN"
            assert rows[0]["std_postal_code"] == "100-8111"
