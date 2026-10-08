"""Batch I/O safety: no input clobbering, no half-written outputs, no spreadsheet formula injection."""

import csv
import json

import pytest

from address_standardizer.batch import (
    chunk_generator,
    stream_standardize_csv,
    stream_standardize_json,
    stream_standardize_jsonl,
)

HEADER = ["street1", "city", "state", "postal_code"]


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)


def test_output_equal_to_input_is_refused_and_input_survives(tmp_path):
    path = tmp_path / "in.csv"
    _write_csv(path, [[f"{i} Main St", "Austin", "TX", "78701"] for i in range(3000)])
    before = path.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="same file"):
        stream_standardize_csv(str(path), str(path), max_workers=1)
    assert path.read_text(encoding="utf-8") == before


def test_audit_path_equal_to_output_is_refused(tmp_path):
    src = tmp_path / "in.csv"
    out = tmp_path / "out.csv"
    _write_csv(src, [["1 Main St", "Austin", "TX", "78701"]])
    with pytest.raises(ValueError, match="same file"):
        stream_standardize_csv(str(src), str(out), max_workers=1, audit_csv_path=str(out))


def test_failed_run_leaves_no_partial_output(tmp_path):
    src = tmp_path / "in.jsonl"
    out = tmp_path / "out.jsonl"
    src.write_text('{"street1": "1 Main St", "city": "Austin", "state": "TX", "postal_code": "78701"}\nnot json\n', encoding="utf-8")
    with pytest.raises(ValueError, match="line 2"):
        stream_standardize_jsonl(str(src), str(out), max_workers=1)
    assert not out.exists()
    assert not list(tmp_path.glob("*.tmp-*"))


def test_non_object_jsonl_rows_get_a_clear_error(tmp_path):
    src = tmp_path / "in.jsonl"
    src.write_text('"1 Main St"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        stream_standardize_jsonl(str(src), str(tmp_path / "o.jsonl"), max_workers=1)


def test_non_object_json_items_get_a_clear_error(tmp_path):
    src = tmp_path / "in.json"
    src.write_text(json.dumps(["1 Main St"]), encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        stream_standardize_json(str(src), str(tmp_path / "o.json"))


@pytest.mark.parametrize("size", [0, -1])
def test_chunk_size_must_be_positive(size):
    with pytest.raises(ValueError):
        list(chunk_generator(iter([{"a": 1}]), size))


def test_ragged_csv_rows_do_not_abort_the_run(tmp_path):
    src = tmp_path / "in.csv"
    out = tmp_path / "out.csv"
    src.write_text("street1,city,state,postal_code\n1 Main St,Austin,TX,78701,EXTRA\n2 Oak Ave,Austin,TX,78701\n", encoding="utf-8")
    assert stream_standardize_csv(str(src), str(out), max_workers=1) == 2
    with open(out, newline="", encoding="utf-8") as f:
        assert len(list(csv.DictReader(f))) == 2


def test_standardized_text_cells_cannot_start_a_formula(tmp_path):
    src = tmp_path / "in.csv"
    out = tmp_path / "out.csv"
    _write_csv(src, [['=cmd|"/C calc"!A0', "Austin", "TX", "78701"], ["@SUM(1+1)", "Austin", "TX", "78701"]])
    stream_standardize_csv(str(src), str(out), max_workers=1)
    with open(out, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key, value in row.items():
                if key.startswith("std_") and value:
                    assert value[0] not in "=+-@", (key, value)
