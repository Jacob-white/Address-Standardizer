"""
Unit and integration tests for JSONL and JSON streaming batch processing and schema mapping.
"""

import json
import csv
from address_standardizer.batch import (
    stream_standardize_jsonl,
    stream_standardize_json,
    stream_standardize_csv,
    resolve_column_mappings,
)


class TestBatchStreamingJSONL:
    def test_resolve_column_mappings(self):
        # Source to target
        m1 = {"my_street": "street1", "my_zip": "postal_code"}
        s1, s2, c, st, z, co = resolve_column_mappings(m1)
        assert s1 == "my_street"
        assert z == "my_zip"
        assert c == "city"

        # Target to source
        m2 = {"street1": "addr", "postal_code": "zipcode"}
        s1, s2, c, st, z, co = resolve_column_mappings(m2)
        assert s1 == "addr"
        assert z == "zipcode"

    def test_stream_standardize_jsonl(self, tmp_path):
        input_file = tmp_path / "input.jsonl"
        output_file = tmp_path / "output.jsonl"

        rows = [
            {"street1": "100 Wall Street", "street2": "Suite 400", "city": "New York", "state": "NY", "postal_code": "10005"},
            {"street1": "200 Park Avenue", "street2": "Ste 1200", "city": "New York", "state": "NY", "postal_code": "10166"},
            {"street1": "PSC 1004 BOX 500", "street2": "", "city": "APO", "state": "AE", "postal_code": "09724"},
        ]
        with open(input_file, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")

        count = stream_standardize_jsonl(
            input_path=str(input_file),
            output_path=str(output_file),
            chunk_size=2,
            max_workers=1,
            include_confidence=True,
        )
        assert count == 3

        with open(output_file, "r", encoding="utf-8") as f:
            out_rows = [json.loads(line) for line in f]

        assert len(out_rows) == 3
        assert out_rows[0]["std_street1"] == "100 WALL ST"
        assert out_rows[0]["std_street2"] == "STE 400"
        assert out_rows[0]["address_status"] == "standardized"
        assert "confidence_score" in out_rows[0]

        assert out_rows[1]["std_street1"] == "200 PARK AVE"
        assert out_rows[2]["std_street1"] == "PSC 1004 BOX 500"
        assert out_rows[2]["std_city"] == "APO"

    def test_stream_standardize_jsonl_with_mapping(self, tmp_path):
        input_file = tmp_path / "input_mapped.jsonl"
        output_file = tmp_path / "output_mapped.jsonl"

        rows = [
            {"addr": "350 5th Ave", "town": "New York", "region": "NY", "post": "10118"},
        ]
        with open(input_file, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")

        mapping = {"addr": "street1", "town": "city", "region": "state", "post": "postal_code"}
        count = stream_standardize_jsonl(
            input_path=str(input_file),
            output_path=str(output_file),
            mapping=mapping,
            max_workers=1,
        )
        assert count == 1

        with open(output_file, "r", encoding="utf-8") as f:
            out_row = json.loads(f.readline())

        assert out_row["std_street1"] == "350 5TH AVE"
        assert out_row["std_city"] == "NEW YORK"
        assert out_row["std_state"] == "NY"
        assert out_row["std_postal_code"] == "10118"

    def test_stream_standardize_json_array(self, tmp_path):
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.json"

        rows = [
            {"street1": "100 Wall Street", "city": "New York", "state": "NY", "postal_code": "10005"},
        ]
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(rows, f)

        count = stream_standardize_json(
            input_path=str(input_file),
            output_path=str(output_file),
            max_workers=1,
        )
        assert count == 1

        with open(output_file, "r", encoding="utf-8") as f:
            out_rows = json.load(f)

        assert len(out_rows) == 1
        assert out_rows[0]["std_street1"] == "100 WALL ST"

    def test_stream_standardize_csv_with_mapping(self, tmp_path):
        input_file = tmp_path / "input_map.csv"
        output_file = tmp_path / "output_map.csv"

        with open(input_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["line1", "locality", "reg", "zip_code"])
            writer.writerow(["200 Park Ave", "New York", "NY", "10166"])

        mapping = {"line1": "street1", "locality": "city", "reg": "state", "zip_code": "postal_code"}
        count = stream_standardize_csv(
            input_path=str(input_file),
            output_path=str(output_file),
            mapping=mapping,
            max_workers=1,
        )
        assert count == 1

        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            row = next(reader)
            assert row["std_street1"] == "200 PARK AVE"
            assert row["std_city"] == "NEW YORK"
