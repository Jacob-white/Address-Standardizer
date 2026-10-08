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

    def test_cli_parse_with_confidence_and_audit(self, capsys):
        test_args = [
            "address-standardizer",
            "parse",
            "1209 North Orange St, Wilmington, DE 19801",
            "--confidence",
            "--audit",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "confidence_score" in data
        assert "routing_tier" in data
        assert "failure_reason_codes" in data
        assert "audit_record" in data
        assert data["is_registered_agent_hub"] is True

    def test_cli_parse_with_audit_on_clean_address(self, capsys):
        test_args = [
            "address-standardizer",
            "parse",
            "100 Wall Street, New York, NY 10005",
            "--audit",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "audit_record" in data
        assert data["audit_record"]["normalized_address_key"] == "100 WALL ST||NEW YORK|NY|10005|USA"

    def test_cli_parse_with_cascade(self, capsys):
        test_args = [
            "address-standardizer",
            "parse",
            "100 Wall Street, New York, NY 10005",
            "--cascade",
            "--no-cache",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "latitude" in data
        assert "longitude" in data
        assert "geocode_precision" in data
        assert "cascade_source" in data

    def test_cli_batch_with_confidence_and_audit_csv(self, tmp_path, capsys):
        input_csv = tmp_path / "in_batch_conf.csv"
        output_csv = tmp_path / "out_batch_conf.csv"
        audit_csv = tmp_path / "out_batch_audit.csv"

        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "street1", "street2", "city", "state", "postal_code", "country"])
            w.writerow(["1", "1209 North Orange St", "Ste 400", "Wilmington", "DE", "19801", "USA"])

        test_args = [
            "address-standardizer",
            "batch",
            str(input_csv),
            str(output_csv),
            "--confidence",
            "--audit-csv", str(audit_csv),
            "--no-cache",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        assert output_csv.exists()
        assert audit_csv.exists()

        with open(output_csv, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            row = next(r)
            assert "confidence_score" in row
            assert "routing_tier" in row

        with open(audit_csv, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            row = next(r)
            assert "audit_id" in row
            assert "is_registered_agent_hub" in row

    def test_cli_audit_subcommand(self, capsys):
        # 1. Clear audit ledger
        with patch.object(sys, "argv", ["address-standardizer", "audit", "--clear"]):
            main()
        captured = capsys.readouterr()
        assert "Audit ledger cleared." in captured.out

        # Standardize an address that generates an audit record
        test_parse_args = ["address-standardizer", "parse", "1209 North Orange St, Wilmington, DE 19801", "--audit"]
        with patch.object(sys, "argv", test_parse_args):
            main()
        capsys.readouterr()

        # 2. List as JSON
        with patch.object(sys, "argv", ["address-standardizer", "audit", "--list", "--export", "json"]):
            main()
        captured_json = capsys.readouterr()
        recs = json.loads(captured_json.out)
        assert len(recs) >= 1
        assert recs[0]["is_registered_agent_hub"] is True

        # 3. List as SQL
        with patch.object(sys, "argv", ["address-standardizer", "audit", "--export", "sql"]):
            main()
        captured_sql = capsys.readouterr()
        assert "INSERT INTO address_stewardship_audit_ledger" in captured_sql.out

        # 4. List as dict/plain summary
        with patch.object(sys, "argv", ["address-standardizer", "audit", "--list", "--export", "dict", "--status", "PENDING"]):
            main()
        captured_dict = capsys.readouterr()
        assert "Audit ledger contains" in captured_dict.out

    def test_cli_cache_subcommand(self, capsys):
        # Check stats
        with patch.object(sys, "argv", ["address-standardizer", "cache", "--stats"]):
            main()
        captured = capsys.readouterr()
        stats = json.loads(captured.out)
        assert "l1" in stats
        assert "l2" in stats

        # Clear cache
        with patch.object(sys, "argv", ["address-standardizer", "cache", "--clear"]):
            main()
        captured_clear = capsys.readouterr()
        assert "Cache cleared." in captured_clear.out

    def test_cli_autocomplete_subcommand(self, capsys):
        # 1. Text format output with secondary unit prompt
        with patch.object(sys, "argv", ["address-standardizer", "autocomplete", "100 Wall"]):
            main()
        captured = capsys.readouterr()
        assert "100 WALL ST" in captured.out
        assert "Secondary Unit Required" in captured.out

        # 2. JSON format output
        with patch.object(sys, "argv", ["address-standardizer", "autocomplete", "100 Wall", "--format", "json", "--limit", "2"]):
            main()
        captured_json = capsys.readouterr()
        sugs = json.loads(captured_json.out)
        assert len(sugs) <= 2
        assert sugs[0]["street1"] == "100 WALL ST"
        assert sugs[0]["secondary_prompt_required"] is True

        # 3. State filter
        with patch.object(sys, "argv", ["address-standardizer", "autocomplete", "1209", "--state", "DE", "--format", "json"]):
            main()
        captured_state = capsys.readouterr()
        sugs_de = json.loads(captured_state.out)
        assert len(sugs_de) >= 1
        assert sugs_de[0]["state"] == "DE"

        # 4. No suggestions found
        with patch.object(sys, "argv", ["address-standardizer", "autocomplete", "Nonexistent12345"]):
            main()
        captured_empty = capsys.readouterr()
        assert "No suggestions found." in captured_empty.out

    def test_cli_parse_format_text(self, capsys):
        test_args = ["address-standardizer", "parse", "100 Wall Street, Suite 400, New York, NY 10005", "--format", "text"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "STANDARDIZED ADDRESS" in captured.out
        assert "Street 1:              100 WALL ST" in captured.out
        assert "Street 2:              STE 400" in captured.out
        assert "City:                  NEW YORK" in captured.out
        assert "State:                 NY" in captured.out
        assert "Postal Code:           10005" in captured.out
        assert "Country:               USA (ISO3: USA)" in captured.out
        assert "Address Key:           100 WALL ST|STE 400|NEW YORK|NY|10005|USA" in captured.out

    def test_cli_parse_format_text_with_details(self, capsys):
        test_args = [
            "address-standardizer",
            "parse",
            "100 Wall Street, New York, NY 10005",
            "--format", "text",
            "--enable-geocoding",
            "--confidence",
        ]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "STANDARDIZED ADDRESS" in captured.out
        assert "Coordinates:" in captured.out
        assert "Confidence Score:" in captured.out

    def test_cli_parse_with_enable_geocoding(self, capsys):
        test_args = ["address-standardizer", "parse", "100 Wall Street, Suite 400, New York, NY 10005", "--enable-geocoding"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["street1"] == "100 WALL ST"
        assert "latitude" in data
        assert "longitude" in data
        assert data["latitude"] == 40.7061
        assert data["longitude"] == -74.0060
        assert data["spatial_precision"] == "CONFIRMED_ROOFTOP"
        assert "spatial_result" in data

    def test_cli_parse_with_custom_spatial_db(self, tmp_path, capsys):
        from address_standardizer.spatial import SpatialEngine
        db_path = tmp_path / "custom_spatial.db"
        engine = SpatialEngine(db_path=str(db_path), seed=True)
        engine.close()

        test_args = [
            "address-standardizer", "parse", "100 Wall Street, Suite 400, New York, NY 10005",
            "--enable-geocoding", "--spatial-db", str(db_path)
        ]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["latitude"] == 40.7061

    def test_cli_parse_international_extended_fields_text_and_json(self, capsys):
        test_args = [
            "address-standardizer", "parse",
            "--street1", "Flat 2, The Mansions, 15 High Street",
            "--street2", "Headingley",
            "--city", "Leeds",
            "--zip", "LS6 2AA",
            "--country", "United Kingdom",
            "--format", "text",
        ]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "STANDARDIZED ADDRESS" in captured.out
        assert "ISO3: GBR" in captured.out

    def test_cli_batch_with_enable_geocoding(self, tmp_path):
        input_file = tmp_path / "input_spatial.csv"
        output_file = tmp_path / "output_spatial.csv"

        with open(input_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "street1", "city", "state", "postal_code", "country"])
            writer.writerow(["1", "100 Wall Street", "New York", "NY", "10005", "USA"])

        test_args = [
            "address-standardizer", "batch",
            str(input_file), str(output_file),
            "--enable-geocoding",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            assert rows[0]["latitude"] != ""
            assert rows[0]["spatial_precision"] != ""
            assert rows[0]["spatial_source"] != ""

    def test_cli_batch_with_include_intl(self, tmp_path):
        input_file = tmp_path / "input_intl.csv"
        output_file = tmp_path / "output_intl.csv"

        with open(input_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "street1", "city", "state", "postal_code", "country"])
            writer.writerow(["1", "25 Bank Street", "London", "", "E14 5JP", "GBR"])

        test_args = [
            "address-standardizer", "batch",
            str(input_file), str(output_file),
            "--include-intl",
        ]
        with patch.object(sys, "argv", test_args):
            main()

        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            assert "std_dependent_locality" in rows[0]
            assert "std_building_name" in rows[0]
            assert rows[0]["std_country_iso3"] == "GBR"

    def test_cli_benchmark_domestic_text(self, capsys):
        test_args = ["address-standardizer", "benchmark", "--dataset", "domestic", "--iterations", "1", "--format", "text"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "ADDRESS STANDARDIZER PRODUCTION BENCHMARK REPORT" in captured.out
        assert "DOMESTIC GOLDEN DATASET ACCURACY" in captured.out
        assert "ENTERPRISE ARCHITECTURE SLA VALIDATION STATUS" in captured.out
        assert "PASS" in captured.out

    def test_cli_benchmark_multinational_json(self, capsys):
        test_args = ["address-standardizer", "benchmark", "--dataset", "multi_national", "--iterations", "1", "--format", "json"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "performance" in data
        assert "accuracy" in data
        assert "accuracy_multinational" in data
        assert data["accuracy"]["overall_accuracy_pct"] >= 99.5

    def test_cli_benchmark_all(self, capsys):
        test_args = ["address-standardizer", "benchmark", "--dataset", "all", "--iterations", "1"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "DOMESTIC GOLDEN DATASET ACCURACY" in captured.out
        assert "MULTINATIONAL GOLDEN DATASET ACCURACY" in captured.out
        assert "PASS" in captured.out

    def test_cli_benchmark_custom_dataset(self, tmp_path, capsys):
        custom_file = tmp_path / "custom_golden.json"
        record = [{
            "test_id": "CUSTOM-01",
            "category": "standard_clean",
            "raw_input": {"street1": "100 Wall St", "city": "New York", "state": "NY", "postal_code": "10005", "country": "USA"},
            "expected_output": {
                "street1": "100 WALL ST", "street2": "", "city": "NEW YORK", "state": "NY", "postal_code": "10005",
                "country": "USA", "normalized_address_key": "100 WALL ST||NEW YORK|NY|10005|USA",
                "building_key": "100 WALL ST||NEW YORK|NY|10005|USA", "phonetic_key": "100|W400|10005",
                "is_registered_agent_hub": False
            }
        }]
        with open(custom_file, "w", encoding="utf-8") as f:
            json.dump(record, f)

        test_args = ["address-standardizer", "benchmark", "--dataset", str(custom_file), "--iterations", "1"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "GOLDEN DATASET ACCURACY" in captured.out

    def test_cli_benchmark_import_fallback(self, capsys):
        import builtins
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "benchmarks.run_benchmarks":
                raise ImportError("Mocked import error")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            test_args = ["address-standardizer", "benchmark", "--dataset", "domestic", "--iterations", "1", "--format", "json"]
            with patch.object(sys, "argv", test_args):
                main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "performance" in data

    def test_cli_spatial_lookup_by_address(self, capsys):
        test_args = ["address-standardizer", "spatial", "lookup", "100 Wall St, New York, NY 10005"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 1
        assert data[0]["latitude"] == 40.7061
        assert data[0]["longitude"] == -74.0060

    def test_cli_spatial_lookup_by_explicit_address_text(self, capsys):
        test_args = ["address-standardizer", "spatial", "lookup", "--address", "100 Wall St, New York, NY 10005", "--format", "text"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "SPATIAL RESOLUTION RESULT" in captured.out
        assert "Status:                CONFIRMED_ROOFTOP" in captured.out
        assert "40.7061" in captured.out

    def test_cli_spatial_lookup_by_coordinates_radius(self, capsys):
        test_args = ["address-standardizer", "spatial", "lookup", "--lat", "40.7061", "--lon", "-74.0060", "--radius", "500"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) >= 1
        assert data[0]["latitude"] == 40.7061

    def test_cli_spatial_lookup_by_coordinates_radius_text(self, capsys):
        test_args = ["address-standardizer", "spatial", "lookup", "--lat", "40.7061", "--lon", "-74.0060", "--radius", "500", "--format", "text"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "Found" in captured.out
        assert "within 500.0m" in captured.out

    def test_cli_spatial_lookup_by_bounding_box(self, capsys):
        test_args = [
            "address-standardizer", "spatial", "lookup",
            "--min-lat", "40.70", "--min-lon", "-74.01",
            "--max-lat", "40.71", "--max-lon", "-74.00"
        ]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) >= 1
        assert data[0]["latitude"] == 40.7061

    def test_cli_spatial_lookup_by_bounding_box_text(self, capsys):
        test_args = [
            "address-standardizer", "spatial", "lookup",
            "--min-lat", "40.70", "--min-lon", "-74.01",
            "--max-lat", "40.71", "--max-lon", "-74.00",
            "--format", "text"
        ]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "Found" in captured.out
        assert "in bounding box" in captured.out

    def test_cli_spatial_lookup_by_bbox_argument(self, capsys):
        test_args = [
            "address-standardizer", "spatial", "lookup",
            "--bbox", "-74.01,40.70,-74.00,40.71"
        ]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) >= 1

    def test_cli_spatial_lookup_by_bbox_argument_text(self, capsys):
        test_args = [
            "address-standardizer", "spatial", "lookup",
            "--bbox", "-74.01,40.70,-74.00,40.71",
            "--format", "text"
        ]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "in bounding box" in captured.out

    def test_cli_spatial_lookup_invalid_bbox_error(self):
        test_args = ["address-standardizer", "spatial", "lookup", "--bbox", "-74.01,40.70"]
        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 2

    def test_cli_spatial_lookup_no_query_error(self):
        test_args = ["address-standardizer", "spatial", "lookup"]
        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 2

    def test_cli_spatial_info_text_and_json(self, capsys):
        # 1. Text format
        with patch.object(sys, "argv", ["address-standardizer", "spatial", "info", "--format", "text"]):
            main()
        captured_text = capsys.readouterr()
        assert "SPATIAL DATABASE DIAGNOSTICS & INDEX STATISTICS" in captured_text.out
        assert "Indexed Spatial Points:" in captured_text.out
        assert "R*Tree Index Enabled:      True" in captured_text.out

        # 2. JSON format
        with patch.object(sys, "argv", ["address-standardizer", "spatial", "info", "--format", "json"]):
            main()
        captured_json = capsys.readouterr()
        data = json.loads(captured_json.out)
        assert data["total_spatial_points"] >= 5
        assert data["rtree_index_enabled"] is True

    def test_cli_spatial_stats_alias(self, capsys):
        with patch.object(sys, "argv", ["address-standardizer", "spatial", "stats", "--format", "json"]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "total_spatial_points" in data

    def test_cli_spatial_custom_db(self, tmp_path, capsys):
        from address_standardizer.spatial import SpatialEngine
        db_path = tmp_path / "custom_spatial_info.db"
        engine = SpatialEngine(db_path=str(db_path), seed=True)
        engine.close()

        with patch.object(sys, "argv", ["address-standardizer", "spatial", "info", "--spatial-db", str(db_path), "--format", "json"]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["database_path"] == str(db_path)

    def test_cli_spatial_no_action_prints_help(self):
        with patch.object(sys, "argv", ["address-standardizer", "spatial"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1

    def test_cli_shorthand_invocation_benchmark_spatial_not_intercepted(self, capsys):
        # Invoking benchmark with iterations=1 should run benchmark, not treat "benchmark" as street1
        with patch.object(sys, "argv", ["address-standardizer", "benchmark", "--iterations", "1", "--format", "json"]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        # Should be benchmark output, not StandardizedAddress dict
        assert "performance" in data
        assert "street1" not in data

    def test_cli_parse_format_text_with_cascade(self, capsys):
        test_args = ["address-standardizer", "parse", "100 Wall St, New York, NY 10005", "--cascade", "--format", "text"]
        with patch.object(sys, "argv", test_args):
            main()
        captured = capsys.readouterr()
        assert "Coordinates:" in captured.out
        assert "Stage" in captured.out

    def test_cli_benchmark_import_failure_raises(self):
        import builtins
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "benchmarks.run_benchmarks":
                raise ImportError("Mocked import error")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            with patch("importlib.util.spec_from_file_location", return_value=None):
                test_args = ["address-standardizer", "benchmark"]
                with patch.object(sys, "argv", test_args):
                    with pytest.raises(ImportError) as exc:
                        main()
                    assert "Cannot load benchmarks from" in str(exc.value)

    def test_cli_spatial_lookup_bbox_non_numeric_error(self):
        test_args = ["address-standardizer", "spatial", "lookup", "--bbox", "invalid,coords,not,numbers"]
        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 2



def test_serve_subcommand_dispatches_to_uvicorn(monkeypatch):
    """`serve` must be a known subcommand, not swallowed by the shorthand-address path."""
    import sys
    import types
    from unittest.mock import MagicMock

    from address_standardizer import cli

    run = MagicMock()
    monkeypatch.setitem(sys.modules, "uvicorn", types.SimpleNamespace(run=run))
    monkeypatch.setattr(sys, "argv", ["address-standardizer", "serve", "--port", "9999"])
    cli.main()
    run.assert_called_once()
    assert run.call_args.kwargs["port"] == 9999


def test_every_registered_handler_is_a_known_subcommand():
    from address_standardizer import cli

    assert set(cli._COMMAND_HANDLERS) >= {"parse", "batch", "serve", "spatial", "validate-postal"}


def test_handlers_work_without_main_state(capsys):
    """Handlers no longer depend on a global filled in by main()."""
    from argparse import Namespace

    import pytest

    from address_standardizer import cli

    with pytest.raises(SystemExit) as exc:
        cli._cmd_spatial(Namespace(spatial_action=None))
    assert exc.value.code == 1
